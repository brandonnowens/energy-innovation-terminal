"""Email transmission and bulk campaign dispatch service via Gmail SMTP."""

import os
import smtplib
import ssl
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy.orm import Session

from app.config import settings
from app.models.contact import Contact
from app.models.admin_email import (
    AdminEmailCampaign, AdminEmailLog, ContactEmailThread, ContactEmailMessage
)


def interpolate_template(template_str: str, contact: Contact, extra_vars: Optional[Dict[str, Any]] = None) -> str:
    """Replace template variables like {{name}}, {{institution}}, {{technology_area}} with contact values."""
    if not template_str:
        return ""
        
    first_name = contact.name_first or (contact.name_display.split()[0] if contact.name_display else "")
    last_name = contact.name_last or (contact.name_display.split()[-1] if contact.name_display and len(contact.name_display.split()) > 1 else "")
    institution = contact.institution_name or (contact.organization.name if contact.organization else "your institution")
    tech_area = contact.technology_area or "Clean Energy Innovation"
    title = contact.title or "Innovator"
    sector = contact.sector or "Energy & Climate Tech"
    funding_fmt = f"${(contact.total_funding / 1e6):.1f}M" if contact.total_funding and contact.total_funding >= 1e6 else (f"${contact.total_funding:,.0f}" if contact.total_funding else "$0")
    
    replacements = {
        "{{name}}": contact.name_display or "Innovator",
        "{name}": contact.name_display or "Innovator",
        "{{first_name}}": first_name or "Colleague",
        "{first_name}": first_name or "Colleague",
        "{{last_name}}": last_name or "",
        "{last_name}": last_name or "",
        "{{institution}}": institution,
        "{institution}": institution,
        "{{organization}}": institution,
        "{organization}": institution,
        "{{technology_area}}": tech_area,
        "{technology_area}": tech_area,
        "{{tech_area}}": tech_area,
        "{tech_area}": tech_area,
        "{{sector}}": sector,
        "{sector}": sector,
        "{{title}}": title,
        "{title}": title,
        "{{awards_count}}": str(contact.awards_count or 0),
        "{awards_count}": str(contact.awards_count or 0),
        "{{total_funding}}": funding_fmt,
        "{total_funding}": funding_fmt,
        "{{app_link}}": "https://terminal.aixenergy.io",
        "{app_link}": "https://terminal.aixenergy.io",
        "{{app_name}}": "Energy Innovation Terminal",
        "{app_name}": "Energy Innovation Terminal",
    }
    
    if extra_vars:
        for k, v in extra_vars.items():
            replacements[f"{{{{{k}}}}}" if not k.startswith("{{") else k] = str(v)
            replacements[f"{{{k}}}" if not k.startswith("{") else k] = str(v)
            
    result = template_str
    for tag, val in replacements.items():
        result = result.replace(tag, val)
        
    return result


def build_funding_alert_email_html(
    opportunity_name: str,
    solicitation_number: str,
    agency_name: str,
    match_score_pct: int,
    total_funding: Optional[float],
    max_per_award: Optional[float],
    cost_share_pct: Optional[float],
    deadline_str: Optional[str],
    days_remaining: Optional[int],
    tech_areas: List[str],
    eligibility_summary: str,
    app_base_url: str = "https://terminal.aixenergy.io",
    opp_id: Optional[int] = None,
) -> str:
    """Construct a high-signal, publication-grade HTML financial terminal alert email."""
    funding_fmt = f"${(total_funding / 1e6):.1f}M Pool" if total_funding and total_funding >= 1e6 else (f"${total_funding:,.0f}" if total_funding else "Funding Varies")
    award_max_fmt = f"Up to ${(max_per_award / 1e6):.1f}M / Award" if max_per_award and max_per_award >= 1e6 else (f"${max_per_award:,.0f} Max" if max_per_award else "Competitive Max")
    cost_share_fmt = f"{cost_share_pct:.0f}% Mandatory Cost-Share" if cost_share_pct and cost_share_pct > 0 else "0% Non-Federal Match (100% Grant)"
    deadline_badge = f"{days_remaining} Days Remaining ({deadline_str or 'Approaching'})" if days_remaining is not None else (deadline_str or "Rolling / Open")
    urgency_color = "#dc2626" if days_remaining and days_remaining <= 30 else "#0284c7"
    
    tags_html = "".join([f"<span style='display:inline-block; background-color:#f1f5f9; color:#334155; font-size:11px; font-weight:600; padding:3px 8px; border-radius:4px; margin-right:6px; margin-bottom:6px; border:1px solid #e2e8f0;'>{t}</span>" for t in (tech_areas or ["Clean Energy Innovation"])])
    opp_url = f"{app_base_url}/opportunities/{opp_id}" if opp_id else f"{app_base_url}/opportunities"
    proposal_url = f"{app_base_url}/proposals"

    return f"""
    <div style="background-color:#ffffff; border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.05); font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <!-- Header Banner -->
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); padding:20px 24px; color:#ffffff;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="background-color:rgba(0, 229, 255, 0.15); color:#00e5ff; border:1px solid rgba(0, 229, 255, 0.4); font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; padding:3px 10px; border-radius:12px;">
                    ⚡ High-Priority Funding Alert
                </span>
                <span style="background-color:#059669; color:#ffffff; font-size:12px; font-weight:800; padding:4px 10px; border-radius:8px;">
                    {match_score_pct}% Match Compatibility
                </span>
            </div>
            <h2 style="margin:8px 0 4px 0; font-size:18px; font-weight:800; color:#ffffff; line-height:1.3;">{opportunity_name}</h2>
            <div style="font-size:12.5px; color:#94a3b8; font-weight:500;">
                {agency_name} · Solicitation <strong>{solicitation_number}</strong>
            </div>
        </div>

        <!-- Metric Grid -->
        <div style="padding:20px 24px; background-color:#f8fafc; border-bottom:1px solid #e2e8f0;">
            <table style="width:100%; border-collapse:collapse;">
                <tr>
                    <td style="width:33%; padding:8px; vertical-align:top;">
                        <div style="font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase;">Total Program Pool</div>
                        <div style="font-size:16px; font-weight:800; color:#0f172a; margin-top:2px;">{funding_fmt}</div>
                    </td>
                    <td style="width:33%; padding:8px; vertical-align:top; border-left:1px solid #e2e8f0;">
                        <div style="font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase;">Award Ceiling</div>
                        <div style="font-size:16px; font-weight:800; color:#059669; margin-top:2px;">{award_max_fmt}</div>
                    </td>
                    <td style="width:33%; padding:8px; vertical-align:top; border-left:1px solid #e2e8f0;">
                        <div style="font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase;">Cost-Share Rule</div>
                        <div style="font-size:14px; font-weight:700; color:#475569; margin-top:2px;">{cost_share_fmt}</div>
                    </td>
                </tr>
            </table>
        </div>

        <!-- Scope & Eligibility Body -->
        <div style="padding:24px;">
            <div style="margin-bottom:16px;">
                <div style="font-size:11.5px; font-weight:700; color:#475569; text-transform:uppercase; margin-bottom:8px;">Target Technology Sectors</div>
                <div>{tags_html}</div>
            </div>

            <div style="background-color:#eff6ff; border-left:4px solid #3b82f6; padding:12px 16px; border-radius:0 8px 8px 0; margin-bottom:20px;">
                <div style="font-size:11px; font-weight:800; color:#1e40af; text-transform:uppercase; margin-bottom:4px;">Eligibility & Scope Verification</div>
                <div style="font-size:13px; color:#1e293b; line-height:1.5;">{eligibility_summary}</div>
            </div>

            <div style="margin-bottom:24px; display:flex; align-items:center; justify-content:space-between; padding:12px 16px; background-color:#f1f5f9; border-radius:8px;">
                <span style="font-size:12px; font-weight:600; color:#475569;">Submission Deadline:</span>
                <span style="font-size:12.5px; font-weight:800; color:{urgency_color};">{deadline_badge}</span>
            </div>

            <!-- Action CTAs -->
            <div style="display:flex; gap:12px; flex-wrap:wrap;">
                <a href="{opp_url}" style="flex:1; min-width:180px; text-align:center; background:linear-gradient(to right, #059669, #0284c7); color:#ffffff; font-weight:700; font-size:13px; padding:12px 20px; border-radius:8px; text-decoration:none; box-shadow:0 2px 6px rgba(2,132,199,0.25);">
                    View Full Solicitation & Rules →
                </a>
                <a href="{proposal_url}" style="flex:1; min-width:180px; text-align:center; background-color:#0f172a; color:#ffffff; font-weight:700; font-size:13px; padding:12px 20px; border-radius:8px; text-decoration:none;">
                    Draft Proposal with AI Copilot
                </a>
            </div>
        </div>
    </div>
    """


def build_mime_message(
    from_email: str,
    from_name: str,
    to_email: str,
    to_name: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    footer_text: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
) -> MIMEMultipart:
    """Construct an RFC 5322 MIME Multipart email message."""
    msg = MIMEMultipart("mixed")
    
    from_header = f"{from_name} <{from_email}>" if from_name else from_email
    to_header = f"{to_name} <{to_email}>" if to_name else to_email
    
    msg["From"] = from_header
    msg["To"] = to_header
    msg["Subject"] = subject
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = email.utils.make_msgid(domain="aixenergy.io")
    msg["Reply-To"] = from_email
    
    # Text + HTML alternate payload container
    msg_alt = MIMEMultipart("alternative")
    
    # 1. Plain text version
    full_text = body_text or ""
    if footer_text:
        full_text += f"\n\n{footer_text}"
    msg_alt.attach(MIMEText(full_text, "plain", "utf-8"))
    
    # 2. Rich HTML version
    if body_html or body_text:
        raw_html = body_html or body_text.replace("\n", "<br>")
        footer_html = f"<div style='margin-top:24px; padding-top:16px; border-top:1px solid #e2e8f0; color:#64748b; font-size:12px; font-family:sans-serif;'>{footer_text.replace(chr(10), '<br>')}</div>" if footer_text else ""
        
        full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1e293b; background-color: #ffffff; margin: 0; padding: 16px; font-size: 14px; }}
p {{ margin: 0 0 14px 0; }}
a {{ color: #0284c7; text-decoration: none; font-weight: 600; }}
a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<div style="max-width: 640px; margin: 0 auto;">
{raw_html}
{footer_html}
</div>
</body>
</html>"""
        msg_alt.attach(MIMEText(full_html, "html", "utf-8"))
        
    msg.attach(msg_alt)
    
    # 3. File Attachments
    if attachments:
        for att in attachments:
            filename = att.get("filename", "attachment")
            content_bytes = att.get("content_bytes")
            file_path = att.get("path")
            
            if file_path and os.path.isfile(file_path):
                with open(file_path, "rb") as f:
                    data = f.read()
            elif content_bytes:
                data = content_bytes
            else:
                continue
                
            part = MIMEApplication(data, Name=filename)
            part["Content-Disposition"] = f'attachment; filename="{filename}"'
            msg.attach(part)
            
    return msg


def send_single_email(
    to_email: str,
    to_name: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    footer_text: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Tuple[bool, str, Optional[str]]:
    """Record outbound correspondence in terminal database ledger without transmitting to external inboxes."""
    from_name = settings.admin_email_display_name
    from_email = username or settings.admin_gmail_user
    
    msg = build_mime_message(
        from_email=from_email,
        from_name=from_name,
        to_email=to_email,
        to_name=to_name,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        footer_text=footer_text,
        attachments=attachments,
    )
    
    msg_id = msg.get("Message-ID") or email.utils.make_msgid(domain="aixenergy.io")
    # Per system policy, outbound email transmission to user inboxes is decommissioned.
    # All correspondence, alerts, and drafts are logged in the database for in-terminal review.
    return True, "In-Terminal Mode: Correspondence recorded in terminal database. Outbound inbox email transmission is decommissioned.", msg_id


def test_gmail_smtp_connection(
    host: Optional[str] = None,
    port: Optional[int] = None,
    user: Optional[str] = None,
    password: Optional[str] = None
) -> Tuple[bool, str]:
    """Report status of in-terminal intelligence mode."""
    return True, "In-Terminal Mode Active: External email dispatching is decommissioned. All updates, alerts, and intelligence are served directly within the terminal application."


def dispatch_campaign_to_contacts(
    db: Session,
    campaign_id: int,
    contact_ids: List[int],
    subject_template: str,
    body_text_template: str,
    body_html_template: Optional[str] = None,
    footer_text: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    extra_vars: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Send campaign messages to a list of contacts and update database tracking ledger."""
    campaign = db.query(AdminEmailCampaign).filter_by(id=campaign_id).first()
    if not campaign:
        raise ValueError(f"Campaign {campaign_id} not found")
        
    campaign.status = "sending"
    campaign.started_at = datetime.utcnow()
    campaign.total_recipients = len(contact_ids)
    db.commit()
    
    contacts = db.query(Contact).filter(Contact.id.in_(contact_ids)).all()
    sent_count = 0
    failed_count = 0
    
    footer = footer_text if footer_text is not None else settings.admin_email_default_footer
    from_email = settings.admin_gmail_user
    from_name = settings.admin_email_display_name
    
    for contact in contacts:
        if not contact.email or not contact.email.strip():
            log = AdminEmailLog(
                campaign_id=campaign.id,
                contact_id=contact.id,
                recipient_name=contact.name_display,
                recipient_email="N/A",
                institution_name=contact.institution_name,
                status="failed",
                error_message="Contact has no valid email address.",
                created_at=datetime.utcnow()
            )
            db.add(log)
            failed_count += 1
            continue
            
        personalized_subject = interpolate_template(subject_template, contact, extra_vars)
        personalized_body_text = interpolate_template(body_text_template, contact, extra_vars)
        personalized_body_html = interpolate_template(body_html_template, contact, extra_vars) if body_html_template else None
        
        success, status_msg, msg_id = send_single_email(
            to_email=contact.email.strip(),
            to_name=contact.name_display,
            subject=personalized_subject,
            body_text=personalized_body_text,
            body_html=personalized_body_html,
            footer_text=footer,
            attachments=attachments,
        )
        
        now = datetime.utcnow()
        
        log = AdminEmailLog(
            campaign_id=campaign.id,
            contact_id=contact.id,
            recipient_name=contact.name_display,
            recipient_email=contact.email.strip(),
            institution_name=contact.institution_name,
            status="sent" if success else "failed",
            error_message=None if success else status_msg,
            smtp_response=status_msg if success else None,
            message_id=msg_id,
            sent_at=now if success else None,
            created_at=now
        )
        db.add(log)
        
        if success:
            sent_count += 1
            
            # Upsert Contact correspondence thread
            thread = db.query(ContactEmailThread).filter_by(contact_id=contact.id).first()
            if not thread:
                thread = ContactEmailThread(
                    contact_id=contact.id,
                    contact_email=contact.email.strip(),
                    contact_name=contact.name_display,
                    institution_name=contact.institution_name,
                    technology_area=contact.technology_area,
                    status="pending_reply",
                    total_messages=1,
                    outbound_count=1,
                    inbound_count=0,
                    first_contacted_at=now,
                    last_contacted_at=now,
                    last_activity_at=now,
                    conversation_summary=f"Sent campaign '{campaign.name}' on {now.strftime('%b %d, %Y')}.",
                    next_action="Awaiting contact reply or application signup.",
                    sentiment="neutral"
                )
                db.add(thread)
                db.flush()
            else:
                thread.total_messages += 1
                thread.outbound_count += 1
                thread.last_contacted_at = now
                thread.last_activity_at = now
                if thread.status == "no_outreach":
                    thread.status = "pending_reply"
                thread.conversation_summary = f"Sent outreach '{personalized_subject}' on {now.strftime('%b %d, %Y')}."
                
            # Log specific outbound message
            attachment_names = [a.get("filename") for a in (attachments or []) if a.get("filename")]
            msg_record = ContactEmailMessage(
                thread_id=thread.id,
                contact_id=contact.id,
                campaign_id=campaign.id,
                message_id=msg_id,
                direction="outbound",
                from_email=from_email,
                from_name=from_name,
                to_email=contact.email.strip(),
                to_name=contact.name_display,
                subject=personalized_subject,
                snippet=(personalized_body_text[:180] + "...") if len(personalized_body_text) > 180 else personalized_body_text,
                body_text=personalized_body_text,
                body_html=personalized_body_html,
                has_attachments=bool(attachments),
                attachments_json=attachment_names,
                is_read=True,
                sent_at=now,
                synced_at=now,
                summary=f"Outreach invitation sent regarding {contact.technology_area or 'Energy Innovation'}"
            )
            db.add(msg_record)
        else:
            failed_count += 1
            
    campaign.sent_count = sent_count
    campaign.failed_count = failed_count
    campaign.status = "completed" if failed_count == 0 else ("partial_failure" if sent_count > 0 else "failed")
    campaign.completed_at = datetime.utcnow()
    db.commit()
    
    return {
        "campaign_id": campaign.id,
        "total": len(contact_ids),
        "sent": sent_count,
        "failed": failed_count,
        "status": campaign.status
    }
