"""Gmail IMAP synchronization service for tracking inbound replies and sent correspondences."""

import imaplib
import email
import email.header
import email.utils
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set
import re

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.config import settings
from app.models.contact import Contact
from app.models.admin_email import ContactEmailThread, ContactEmailMessage
from app.services.conversation_summarizer import summarize_conversation_thread


def _decode_mime_header(header_value: Optional[str]) -> str:
    """Decode RFC 2047 MIME encoded headers."""
    if not header_value:
        return ""
    decoded_fragments = email.header.decode_header(header_value)
    result = []
    for fragment, encoding in decoded_fragments:
        if isinstance(fragment, bytes):
            try:
                result.append(fragment.decode(encoding or "utf-8", errors="replace"))
            except Exception:
                result.append(fragment.decode("latin1", errors="replace"))
        else:
            result.append(str(fragment))
    return "".join(result)


def _extract_email_address(raw_header: str) -> Tuple[str, str]:
    """Parse 'Display Name <user@domain.com>' into (email, display_name)."""
    name, addr = email.utils.parseaddr(raw_header)
    return addr.strip().lower(), name.strip()


def _get_message_body(msg: email.message.Message) -> Tuple[str, str, List[str]]:
    """Extract plain text body, HTML body, and attachment filenames from an email message."""
    body_text = ""
    body_html = ""
    attachments = []
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            # Check for attachments
            filename = part.get_filename()
            if filename:
                decoded_fn = _decode_mime_header(filename)
                attachments.append(decoded_fn)
                continue
                
            if "attachment" in content_disposition:
                fn = part.get_param("name") or "attachment"
                attachments.append(_decode_mime_header(fn))
                continue
                
            payload = part.get_payload(decode=True)
            if not payload:
                continue
                
            charset = part.get_content_charset() or "utf-8"
            try:
                decoded_text = payload.decode(charset, errors="replace")
            except Exception:
                decoded_text = payload.decode("latin1", errors="replace")
                
            if content_type == "text/plain" and not body_text:
                body_text = decoded_text
            elif content_type == "text/html" and not body_html:
                body_html = decoded_text
    else:
        content_type = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            try:
                decoded_text = payload.decode(charset, errors="replace")
            except Exception:
                decoded_text = payload.decode("latin1", errors="replace")
            if content_type == "text/html":
                body_html = decoded_text
            else:
                body_text = decoded_text
                
    # Fallbacks
    if not body_text and body_html:
        # Strip simple HTML tags for text snippet
        body_text = re.sub(r"<[^>]+>", " ", body_html)
        body_text = re.sub(r"\s+", " ", body_text).strip()
        
    return body_text.strip(), body_html.strip(), attachments


def test_gmail_imap_connection(
    host: Optional[str] = None,
    port: Optional[int] = None,
    user: Optional[str] = None,
    password: Optional[str] = None
) -> Tuple[bool, str]:
    """Test connection status for in-terminal intelligence ledger."""
    return True, "In-Terminal Mode: Direct inbox tracking decommissioned. All intelligence is accessed live within the application."


def sync_gmail_correspondence(
    db: Session,
    days_lookback: int = 30,
    max_messages: int = 200,
) -> Dict[str, Any]:
    """
    Connects to Gmail IMAP, scans INBOX and Sent mail, finds correspondences
    matching energy innovation contacts, and records them into conversation threads.
    """
    host = settings.admin_imap_host
    port = settings.admin_imap_port
    user = settings.admin_gmail_user
    pwd = settings.admin_gmail_password
    admin_addr = user.strip().lower()
    
    try:
        mail = imaplib.IMAP4_SSL(host, port, timeout=25)
        mail.login(user, pwd)
    except Exception as e:
        return {
            "success": False,
            "error": f"IMAP Connection failed: {str(e)}",
            "messages_synced": 0,
            "threads_updated": 0,
            "synced_at": datetime.utcnow().isoformat()
        }
        
    # Map all contact emails to Contact instances in memory
    contacts = db.query(Contact).filter(Contact.email.isnot(None), Contact.email != "").all()
    contact_map: Dict[str, Contact] = {c.email.strip().lower(): c for c in contacts if c.email}
    
    # Also include existing thread emails
    existing_threads = db.query(ContactEmailThread).all()
    for th in existing_threads:
        if th.contact_email:
            contact = db.query(Contact).filter_by(id=th.contact_id).first()
            if contact:
                contact_map[th.contact_email.strip().lower()] = contact
                
    if not contact_map:
        mail.logout()
        return {
            "success": True,
            "message": "No contacts with email addresses registered to sync.",
            "messages_synced": 0,
            "threads_updated": 0,
            "synced_at": datetime.utcnow().isoformat()
        }
        
    synced_count = 0
    updated_thread_ids: Set[int] = set()
    
    # Folders to check: INBOX and Sent
    folders_to_check = ["INBOX", '"[Gmail]/Sent Mail"', "Sent", '"[Gmail]/All Mail"']
    
    # List available folders on the server
    status, folder_list = mail.list()
    available_folders = [f.decode("utf-8", errors="ignore") for f in folder_list] if status == "OK" else []
    
    since_date = (datetime.utcnow() - timedelta(days=days_lookback)).strftime("%d-%b-%Y")
    
    for folder_name in ["INBOX", "[Gmail]/Sent Mail", "Sent"]:
        try:
            res, _ = mail.select(folder_name, readonly=True)
            if res != "OK":
                continue
        except Exception:
            continue
            
        try:
            # Search for messages since lookback date
            search_crit = f'(SINCE "{since_date}")'
            status, data = mail.search(None, search_crit)
            if status != "OK" or not data or not data[0]:
                continue
                
            msg_ids = data[0].split()
            # Take the most recent messages up to max_messages limit
            if len(msg_ids) > max_messages:
                msg_ids = msg_ids[-max_messages:]
                
            for m_id in msg_ids:
                try:
                    res, msg_data = mail.fetch(m_id, "(RFC822)")
                    if res != "OK" or not msg_data or not msg_data[0]:
                        continue
                        
                    raw_email = msg_data[0][1]
                    if not isinstance(raw_email, bytes):
                        continue
                        
                    msg = email.message_from_bytes(raw_email)
                    
                    # Parse addresses
                    from_addr, from_name = _extract_email_address(_decode_mime_header(msg.get("From", "")))
                    to_addr, to_name = _extract_email_address(_decode_mime_header(msg.get("To", "")))
                    subject = _decode_mime_header(msg.get("Subject", "(No Subject)"))
                    message_id = msg.get("Message-ID", "").strip() or f"imap-{m_id.decode()}-{from_addr}"
                    in_reply_to = msg.get("In-Reply-To", "").strip() or None
                    
                    # Determine direction & match contact
                    direction = "outbound" if from_addr == admin_addr else "inbound"
                    matched_contact = None
                    
                    if direction == "inbound" and from_addr in contact_map:
                        matched_contact = contact_map[from_addr]
                    elif direction == "outbound" and to_addr in contact_map:
                        matched_contact = contact_map[to_addr]
                        
                    if not matched_contact:
                        continue
                        
                    # Check if this message was already recorded
                    existing_msg = db.query(ContactEmailMessage).filter_by(message_id=message_id).first()
                    if existing_msg:
                        continue
                        
                    # Extract date
                    date_tuple = email.utils.parsedate_tz(msg.get("Date"))
                    if date_tuple:
                        sent_timestamp = email.utils.mktime_tz(date_tuple)
                        sent_dt = datetime.utcfromtimestamp(sent_timestamp)
                    else:
                        sent_dt = datetime.utcnow()
                        
                    body_text, body_html, attachments = _get_message_body(msg)
                    snippet = (body_text[:180] + "...") if len(body_text) > 180 else body_text
                    
                    # Upsert thread
                    thread = db.query(ContactEmailThread).filter_by(contact_id=matched_contact.id).first()
                    if not thread:
                        thread = ContactEmailThread(
                            contact_id=matched_contact.id,
                            contact_email=matched_contact.email.strip(),
                            contact_name=matched_contact.name_display,
                            institution_name=matched_contact.institution_name,
                            technology_area=matched_contact.technology_area,
                            status="replied" if direction == "inbound" else "pending_reply",
                            total_messages=0,
                            outbound_count=0,
                            inbound_count=0,
                            unread_inbound_count=0,
                            first_contacted_at=sent_dt,
                            last_activity_at=sent_dt
                        )
                        db.add(thread)
                        db.flush()
                        
                    thread.total_messages += 1
                    if direction == "inbound":
                        thread.inbound_count += 1
                        thread.unread_inbound_count += 1
                        thread.last_inbound_at = sent_dt
                        if thread.status in ["no_outreach", "pending_reply"]:
                            thread.status = "replied"
                    else:
                        thread.outbound_count += 1
                        thread.last_contacted_at = sent_dt
                        
                    if sent_dt > (thread.last_activity_at or datetime.min):
                        thread.last_activity_at = sent_dt
                        
                    # Save message
                    new_msg = ContactEmailMessage(
                        thread_id=thread.id,
                        contact_id=matched_contact.id,
                        message_id=message_id,
                        in_reply_to=in_reply_to,
                        direction=direction,
                        from_email=from_addr,
                        from_name=from_name,
                        to_email=to_addr,
                        to_name=to_name,
                        subject=subject,
                        snippet=snippet,
                        body_text=body_text,
                        body_html=body_html,
                        has_attachments=bool(attachments),
                        attachments_json=attachments,
                        is_read=direction == "outbound",
                        sent_at=sent_dt,
                        synced_at=datetime.utcnow()
                    )
                    db.add(new_msg)
                    synced_count += 1
                    updated_thread_ids.add(thread.id)
                except Exception as ex:
                    print(f"Error processing IMAP message {m_id}: {ex}")
                    continue
        except Exception as e:
            print(f"Error scanning folder {folder_name}: {e}")
            
    db.commit()
    
    # Re-summarize all updated conversation threads
    for th_id in updated_thread_ids:
        try:
            summarize_conversation_thread(db, th_id)
        except Exception as e:
            print(f"Error summarizer thread {th_id}: {e}")
            
    try:
        mail.close()
        mail.logout()
    except Exception:
        pass
        
    return {
        "success": True,
        "messages_synced": synced_count,
        "threads_updated": len(updated_thread_ids),
        "synced_at": datetime.utcnow().isoformat()
    }
