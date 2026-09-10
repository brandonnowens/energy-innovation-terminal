"""System Administration Email Hub, Gmail Linkage & Contact Correspondence API."""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.contact import Contact
from app.models.admin_email import (
    AdminEmailCampaign, AdminEmailLog, ContactEmailThread, ContactEmailMessage
)
from app.core.membership import require_role
from app.services.email_service import (
    send_single_email, test_gmail_smtp_connection, dispatch_campaign_to_contacts, interpolate_template
)
from app.services.imap_sync_service import (
    test_gmail_imap_connection, sync_gmail_correspondence
)
from app.services.conversation_summarizer import summarize_conversation_thread

router = APIRouter(prefix="/admin/email", tags=["Admin Email Hub"])


# ----------------------------------------------------------------------
# Schemas
# ----------------------------------------------------------------------

class SendEmailPayload(BaseModel):
    name: str = Field(..., description="Campaign or message name")
    template_type: str = Field("application_invitation", description="Type of email template")
    subject: str = Field(..., description="Email subject line with optional {{tags}}")
    body_text: str = Field(..., description="Plain text email body with optional {{tags}}")
    body_html: Optional[str] = Field(None, description="Optional HTML body")
    footer_text: Optional[str] = Field(None, description="Custom footer or disclaimer")
    recipient_mode: str = Field("ids", description="'ids', 'all', or 'filter'")
    contact_ids: Optional[List[int]] = Field(default_factory=list, description="Specific contact IDs to target")
    filter_criteria: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Filter parameters if mode is 'filter'")


class QuickReplyPayload(BaseModel):
    subject: str
    body_text: str
    body_html: Optional[str] = None
    footer_text: Optional[str] = None


class ThreadStatusUpdatePayload(BaseModel):
    status: str = Field(..., description="new thread status: pending_reply, replied, interested, meeting_scheduled, joined, opted_out, closed")
    next_action: Optional[str] = None
    notes: Optional[str] = None


# ----------------------------------------------------------------------
# Diagnostics & System Status
# ----------------------------------------------------------------------

@router.get("/status")
def get_admin_email_status(
    admin_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Get system admin email configuration status, telemetry, and unread counts."""
    total_contacts = db.query(func.count(Contact.id)).scalar() or 0
    contacts_with_email = db.query(func.count(Contact.id)).filter(Contact.email.isnot(None), Contact.email != "").scalar() or 0
    total_campaigns = db.query(func.count(AdminEmailCampaign.id)).scalar() or 0
    total_threads = db.query(func.count(ContactEmailThread.id)).scalar() or 0
    unread_inbound = db.query(func.sum(ContactEmailThread.unread_inbound_count)).scalar() or 0
    active_conversations = db.query(func.count(ContactEmailThread.id)).filter(ContactEmailThread.status.in_(["replied", "interested", "meeting_scheduled"])).scalar() or 0

    return {
        "admin_email": settings.admin_gmail_user,
        "admin_name": settings.admin_primary_name,
        "display_name": settings.admin_email_display_name,
        "smtp_host": settings.admin_smtp_host,
        "smtp_port": settings.admin_smtp_port,
        "imap_host": settings.admin_imap_host,
        "imap_port": settings.admin_imap_port,
        "default_footer": settings.admin_email_default_footer,
        "telemetry": {
            "total_contacts_in_directory": total_contacts,
            "contacts_with_direct_email": contacts_with_email,
            "total_campaigns_dispatched": total_campaigns,
            "tracked_threads": total_threads,
            "unread_inbound_messages": unread_inbound,
            "active_engaged_conversations": active_conversations,
        },
        "account_info": {
            "primary_admin": "Brandon Owens (bowens@aixenergy.io)",
            "service_provider": "Google Workspace / Gmail",
            "protocol": "SMTP (Port 587 STARTTLS) & IMAP (Port 993 SSL)"
        }
    }


@router.post("/test-connection")
def test_connection(admin_user: User = Depends(require_role(["admin"]))):
    """Run live diagnostic handshake against Gmail SMTP and IMAP endpoints."""
    smtp_ok, smtp_msg = test_gmail_smtp_connection()
    imap_ok, imap_msg = test_gmail_imap_connection()
    
    return {
        "smtp": {
            "success": smtp_ok,
            "message": smtp_msg,
            "host": f"{settings.admin_smtp_host}:{settings.admin_smtp_port}",
            "user": settings.admin_gmail_user
        },
        "imap": {
            "success": imap_ok,
            "message": imap_msg,
            "host": f"{settings.admin_imap_host}:{settings.admin_imap_port}",
            "user": settings.admin_gmail_user
        },
        "all_healthy": smtp_ok and imap_ok,
        "timestamp": datetime.utcnow().isoformat()
    }


# ----------------------------------------------------------------------
# Email Templates
# ----------------------------------------------------------------------

@router.get("/templates")
def get_email_templates(admin_user: User = Depends(require_role(["admin"]))):
    """Pre-built high-converting clean energy outreach and application invitation templates."""
    return {
        "templates": [
            {
                "id": "application_invitation",
                "name": "🚀 Official Invitation to Join Energy Innovation Terminal",
                "category": "invitation",
                "default_subject": "Invitation: Access the National Clean Energy Innovation Intelligence Terminal — {{name}}",
                "default_body": """Dear {{first_name}},

I am reaching out directly as the Founder & Lead Principal of the Energy Innovation Terminal. We have indexed your pioneering research, grant awards, and technology portfolio in {{technology_area}} at {{institution}}.

I would like to personally invite you and your team to join the Energy Innovation Terminal (https://terminal.aixenergy.io).

The platform provides comprehensive upstream intelligence across federal and state funding ecosystems (DOE, ARPA-E, CEC, MassCEC, NSF, and NYSERDA), including:
• Multi-Agency Grant & Solicitation Match Engine
• Complete Federal & State Award Ledger & Geospatial Map
• Consortia Teaming Partner & Principal Investigator Directory
• 9-Dimensional Lineage & Patent Citation Linkage Matrix
• AI Executive Grant Dossier & Win-Rate Benchmarks

As an active leader in {{sector}}, your profile and track record are already featured in our verified national directory. We would be delighted to grant you full researcher access.

You can explore your indexed profile and active solicitations here:
👉 https://terminal.aixenergy.io

Please let me know if you have any questions or if you would welcome a brief 10-minute walkthrough of our intelligence tools.

Warm regards,

Brandon N. Owens
Clean Energy Research, LLC | Energy Innovation Terminal
bowens@aixenergy.io""",
            },
            {
                "id": "consortium_teaming",
                "name": "🤝 Clean Energy Grant Consortia & Teaming Inquiry",
                "category": "teaming",
                "default_subject": "Consortium Teaming & Grant Collaboration: {{technology_area}} — Attn: {{name}}",
                "default_body": """Dear {{name}},

I hope this message finds you well.

I am contacting you regarding your ongoing innovation leadership in {{technology_area}} at {{institution}}. We are currently structuring multi-disciplinary consortia for upcoming non-dilutive federal (DOE/ARPA-E) and state clean energy funding opportunities.

Given your funded track record ({{awards_count}} projects totaling {{total_funding}}), we see strong alignment for potential teaming, prime/subcontracting, or advisory roles on upcoming grant submissions.

Would you be open to a brief 15-minute introductory discussion next week to explore mutual alignment?

Best regards,

Brandon N. Owens
Clean Energy Research, LLC | Energy Innovation Terminal
bowens@aixenergy.io""",
            },
            {
                "id": "tech_due_diligence",
                "name": "🔬 Technology Track Record & Commercialization Due Diligence",
                "category": "diligence",
                "default_subject": "Technology Advancement & Commercialization Inquiry: {{technology_area}} — {{name}}",
                "default_body": """Dear {{name}},

Our team is currently evaluating commercialization trajectories, intellectual property advancements, and market deployment readiness across the {{technology_area}} sector.

We reviewed your public research awards and project milestones at {{institution}} in our national innovation database. We were deeply impressed by your team's technical achievements.

We would welcome the opportunity to connect regarding your commercial roadmap and upcoming deployment demonstration pilots.

Looking forward to connecting.

Sincerely,

Brandon N. Owens
Clean Energy Research, LLC | Energy Innovation Terminal
bowens@aixenergy.io""",
            },
            {
                "id": "custom",
                "name": "✍️ Custom Direct Message / General Announcement",
                "category": "custom",
                "default_subject": "Clean Energy Innovation Update — {{institution}}",
                "default_body": """Dear {{first_name}},

I hope you are having a productive week.

I am reaching out regarding clean energy technology developments and funding programs in {{technology_area}}.

[Insert your personalized message here]

Best regards,

Brandon N. Owens
Clean Energy Research, LLC | Energy Innovation Terminal
bowens@aixenergy.io""",
            }
        ]
    }


# ----------------------------------------------------------------------
# Campaign Dispatch & Single Email
# ----------------------------------------------------------------------

@router.post("/send")
async def send_email_campaign(
    payload_json: str = Form(..., description="JSON-encoded SendEmailPayload"),
    files: List[UploadFile] = File(None, description="Optional uploaded file attachments"),
    admin_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Send an email message (single or bulk) with variable replacements and optional file attachments.
    Saves campaign, individual delivery logs, and updates contact correspondence threads.
    """
    try:
        data_dict = json.loads(payload_json)
        req = SendEmailPayload(**data_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload JSON: {str(e)}")
        
    # Process uploaded files into in-memory attachment dicts
    attachment_objects = []
    attachments_meta = []
    
    if files:
        for file in files:
            if file.filename:
                content = await file.read()
                attachment_objects.append({
                    "filename": file.filename,
                    "content_bytes": content,
                    "content_type": file.content_type or "application/octet-stream"
                })
                attachments_meta.append({
                    "filename": file.filename,
                    "size": len(content),
                    "content_type": file.content_type or "application/octet-stream"
                })
                
    # Determine target contact IDs
    target_ids = []
    if req.recipient_mode == "ids":
        target_ids = req.contact_ids or []
    elif req.recipient_mode == "all":
        contacts = db.query(Contact.id).filter(Contact.email.isnot(None), Contact.email != "").all()
        target_ids = [c[0] for c in contacts]
    elif req.recipient_mode == "filter":
        query = db.query(Contact.id).filter(Contact.email.isnot(None), Contact.email != "")
        filters = req.filter_criteria or {}
        
        if filters.get("category"):
            cat = filters["category"]
            if cat == "funder_officers":
                query = query.filter(Contact.role_type == "program_officer")
            elif cat == "domain_experts":
                query = query.filter(Contact.role_type.in_(["pi", "technical_expert"]))
            elif cat == "institutional_gateways":
                query = query.filter(Contact.role_type == "institutional_gateway")
            elif cat == "utilities":
                query = query.filter(Contact.role_type == "utility_lead")
        if filters.get("role_type") and filters["role_type"] != "all":
            query = query.filter(Contact.role_type == filters["role_type"])
        if filters.get("technology") and filters["technology"] != "all":
            query = query.filter(Contact.technology_area.ilike(f"%{filters['technology']}%"))
        if filters.get("sector") and filters["sector"] != "all":
            query = query.filter(Contact.sector.ilike(f"%{filters['sector']}%"))
        if filters.get("state") and filters["state"] != "all":
            query = query.filter(Contact.state.ilike(filters["state"].strip()))
        if filters.get("deliverable_only"):
            query = query.filter(Contact.email_deliverable == True)
            
        target_ids = [c[0] for c in query.all()]
        
    if not target_ids:
        raise HTTPException(status_code=400, detail="No valid recipient contacts selected or matched by filter criteria.")
        
    # Create Campaign record
    campaign = AdminEmailCampaign(
        user_id=admin_user.id,
        name=req.name.strip(),
        template_type=req.template_type,
        subject=req.subject.strip(),
        body_text=req.body_text.strip(),
        body_html=req.body_html.strip() if req.body_html else None,
        footer_text=req.footer_text.strip() if req.footer_text else settings.admin_email_default_footer,
        attachments_json=attachments_meta,
        target_criteria_json={"mode": req.recipient_mode, "filters": req.filter_criteria or {}, "count": len(target_ids)},
        total_recipients=len(target_ids),
        status="draft",
        created_at=datetime.utcnow()
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    # Execute campaign dispatch
    result = dispatch_campaign_to_contacts(
        db=db,
        campaign_id=campaign.id,
        contact_ids=target_ids,
        subject_template=req.subject,
        body_text_template=req.body_text,
        body_html_template=req.body_html,
        footer_text=req.footer_text,
        attachments=attachment_objects,
        user_id=admin_user.id
    )
    
    return {
        "status": "ok",
        "message": f"Dispatched campaign '{campaign.name}' to {result['sent']} contacts ({result['failed']} failed).",
        "campaign": campaign.to_dict(),
        "result": result
    }


# ----------------------------------------------------------------------
# Campaign History
# ----------------------------------------------------------------------

@router.get("/campaigns")
def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """List past admin email outreach campaigns."""
    query = db.query(AdminEmailCampaign).order_by(desc(AdminEmailCampaign.created_at))
    total = query.count()
    campaigns = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [c.to_dict() for c in campaigns]
    }


@router.get("/campaigns/{campaign_id}")
def get_campaign_detail(
    campaign_id: int,
    admin_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Get full campaign details and individual recipient delivery logs."""
    campaign = db.query(AdminEmailCampaign).filter_by(id=campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    logs = db.query(AdminEmailLog).filter_by(campaign_id=campaign.id).order_by(desc(AdminEmailLog.created_at)).all()
    
    return {
        "campaign": campaign.to_dict(),
        "logs": [l.to_dict() for l in logs]
    }


# ----------------------------------------------------------------------
# Inbox Synchronization & Correspondence Tracker
# ----------------------------------------------------------------------

@router.post("/sync")
def trigger_gmail_sync(
    days_lookback: int = Query(30, ge=1, le=180),
    admin_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Trigger live IMAP sync with Gmail to fetch sent emails and inbound replies from contacts."""
    res = sync_gmail_correspondence(db, days_lookback=days_lookback)
    return res


@router.get("/threads")
def list_correspondence_threads(
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    technology: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    admin_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """List all contact email correspondence threads with AI summaries and sentiment."""
    query = db.query(ContactEmailThread)
    
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                ContactEmailThread.contact_name.ilike(term),
                ContactEmailThread.contact_email.ilike(term),
                ContactEmailThread.institution_name.ilike(term),
                ContactEmailThread.technology_area.ilike(term),
                ContactEmailThread.conversation_summary.ilike(term)
            )
        )
        
    if status_filter and status_filter != "all":
        query = query.filter(ContactEmailThread.status == status_filter)
        
    if technology and technology != "all":
        query = query.filter(ContactEmailThread.technology_area.ilike(f"%{technology}%"))
        
    query = query.order_by(desc(ContactEmailThread.last_activity_at))
    total = query.count()
    threads = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
        "items": [t.to_dict() for t in threads]
    }


@router.get("/threads/{thread_id}")
def get_thread_detail(
    thread_id: int,
    admin_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Get full chronological email stream and AI executive summary for a thread."""
    thread = db.query(ContactEmailThread).filter_by(id=thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
        
    messages = db.query(ContactEmailMessage).filter_by(thread_id=thread.id).order_by(ContactEmailMessage.sent_at.asc()).all()
    
    # Mark unread messages as read
    for m in messages:
        if not m.is_read:
            m.is_read = True
    thread.unread_inbound_count = 0
    db.commit()
    
    contact = db.query(Contact).filter_by(id=thread.contact_id).first()
    
    return {
        "thread": thread.to_dict(),
        "contact": {
            "id": contact.id if contact else None,
            "name_display": contact.name_display if contact else thread.contact_name,
            "title": contact.title if contact else None,
            "institution_name": contact.institution_name if contact else thread.institution_name,
            "technology_area": contact.technology_area if contact else thread.technology_area,
            "email": contact.email if contact else thread.contact_email,
            "total_funding": contact.total_funding if contact else 0,
            "awards_count": contact.awards_count if contact else 0,
            "city": contact.city if contact else None,
            "state": contact.state if contact else None,
        } if contact else None,
        "messages": [m.to_dict() for m in messages]
    }


@router.get("/contact/{contact_id}/history")
def get_contact_correspondence_history(
    contact_id: int,
    admin_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Get complete correspondence history and AI summary specifically for a given contact."""
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
        
    thread = db.query(ContactEmailThread).filter_by(contact_id=contact.id).first()
    if not thread:
        return {
            "contact_id": contact_id,
            "has_thread": False,
            "status": "no_outreach",
            "messages": [],
            "summary": "No outreach or correspondences recorded yet with this contact."
        }
        
    messages = db.query(ContactEmailMessage).filter_by(thread_id=thread.id).order_by(ContactEmailMessage.sent_at.asc()).all()
    
    return {
        "contact_id": contact_id,
        "has_thread": True,
        "thread": thread.to_dict(),
        "messages": [m.to_dict() for m in messages]
    }


@router.post("/threads/{thread_id}/reply")
def quick_reply_to_thread(
    thread_id: int,
    payload: QuickReplyPayload,
    admin_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Send a quick reply to an existing contact correspondence thread."""
    thread = db.query(ContactEmailThread).filter_by(id=thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
        
    contact = db.query(Contact).filter_by(id=thread.contact_id).first()
    if not contact or not contact.email:
        raise HTTPException(status_code=400, detail="Contact has no valid email address")
        
    footer = payload.footer_text or settings.admin_email_default_footer
    
    success, status_msg, msg_id = send_single_email(
        to_email=contact.email.strip(),
        to_name=contact.name_display,
        subject=payload.subject.strip(),
        body_text=payload.body_text.strip(),
        body_html=payload.body_html.strip() if payload.body_html else None,
        footer_text=footer,
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to send reply: {status_msg}")
        
    now = datetime.utcnow()
    new_msg = ContactEmailMessage(
        thread_id=thread.id,
        contact_id=contact.id,
        message_id=msg_id,
        direction="outbound",
        from_email=settings.admin_gmail_user,
        from_name=settings.admin_email_display_name,
        to_email=contact.email.strip(),
        to_name=contact.name_display,
        subject=payload.subject.strip(),
        snippet=(payload.body_text[:180] + "...") if len(payload.body_text) > 180 else payload.body_text,
        body_text=payload.body_text.strip(),
        body_html=payload.body_html.strip() if payload.body_html else None,
        has_attachments=False,
        is_read=True,
        sent_at=now,
        synced_at=now,
        summary=f"Admin reply sent regarding {payload.subject}"
    )
    db.add(new_msg)
    
    thread.total_messages += 1
    thread.outbound_count += 1
    thread.last_contacted_at = now
    thread.last_activity_at = now
    db.commit()
    
    # Re-summarize
    summarize_conversation_thread(db, thread.id)
    
    return {
        "status": "ok",
        "message": "Reply sent successfully",
        "message_id": msg_id,
        "thread": thread.to_dict()
    }


@router.post("/threads/{thread_id}/status")
def update_thread_status(
    thread_id: int,
    payload: ThreadStatusUpdatePayload,
    admin_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Manually update thread status, next actions, and notes."""
    thread = db.query(ContactEmailThread).filter_by(id=thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
        
    thread.status = payload.status
    if payload.next_action:
        thread.next_action = payload.next_action.strip()
        
    db.commit()
    db.refresh(thread)
    
    return {
        "status": "ok",
        "thread": thread.to_dict()
    }


@router.post("/threads/{thread_id}/summarize")
def force_summarize_thread(
    thread_id: int,
    admin_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Trigger re-summarization of a conversation thread."""
    res = summarize_conversation_thread(db, thread_id)
    return res


@router.post("/threads/{thread_id}/draft-reply")
def draft_reply_for_thread(
    thread_id: int,
    admin_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Generate an authentic contextual email reply draft for a contact thread using LLM reasoning."""
    thread = db.query(ContactEmailThread).filter_by(id=thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
        
    summary_res = summarize_conversation_thread(db, thread_id)
    contact = db.query(Contact).filter_by(id=thread.contact_id).first() if thread.contact_id else None
    
    suggested_draft = summary_res.get("suggested_reply_draft") or (
        f"Hi {thread.contact_name or 'there'},\n\n"
        f"Thank you for reaching out regarding our clean energy funding intelligence platform. "
        f"I would be glad to coordinate a brief discussion to share our data on active opportunities and historical awards in your sector.\n\n"
        f"Best regards,\nBrandon Owens\nFounder & Lead Principal | Energy Innovation Terminal"
    )

    last_inbound = db.query(ContactEmailMessage).filter(
        ContactEmailMessage.thread_id == thread.id,
        ContactEmailMessage.direction == "inbound"
    ).order_by(ContactEmailMessage.sent_at.desc()).first()

    reply_subject = f"Re: {last_inbound.subject}" if (last_inbound and last_inbound.subject and not last_inbound.subject.lower().startswith("re:")) else (last_inbound.subject if last_inbound else "Re: Clean Energy Funding Intelligence")

    return {
        "status": "ok",
        "thread_id": thread.id,
        "contact_name": thread.contact_name,
        "contact_email": thread.contact_email,
        "subject": reply_subject,
        "body_text": suggested_draft,
        "sentiment": summary_res.get("sentiment", "neutral"),
        "summarized_by": summary_res.get("summarized_by", "AI Assistant")
    }

