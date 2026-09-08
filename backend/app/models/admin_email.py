"""Admin Email, Campaign Management, and Contact Correspondence Tracking models."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class AdminEmailCampaign(Base):
    """Outreach and group email campaign dispatched by System Admin."""
    __tablename__ = "admin_email_campaigns"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(300), nullable=False)
    template_type = Column(String(100), default="application_invitation")  # application_invitation, teaming, tech_inquiry, general_announcement, custom
    subject = Column(String(500), nullable=False)
    body_text = Column(Text, nullable=False)
    body_html = Column(Text, nullable=True)
    footer_text = Column(Text, nullable=True)
    
    # Attachments metadata: list of dicts [{"filename": "...", "size": 1234, "content_type": "...", "path": "..."}]
    attachments_json = Column(JSON, default=list, nullable=True)
    
    # Audience & Filters applied
    target_criteria_json = Column(JSON, default=dict, nullable=True)
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # Status: draft, sending, completed, partial_failure, failed
    status = Column(String(50), default="draft", index=True)
    error_summary = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    logs = relationship("AdminEmailLog", back_populates="campaign", cascade="all, delete-orphan")
    messages = relationship("ContactEmailMessage", back_populates="campaign")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "template_type": self.template_type,
            "subject": self.subject,
            "body_text": self.body_text,
            "body_html": self.body_html,
            "footer_text": self.footer_text,
            "attachments": self.attachments_json or [],
            "target_criteria": self.target_criteria_json or {},
            "total_recipients": self.total_recipients,
            "sent_count": self.sent_count,
            "failed_count": self.failed_count,
            "status": self.status,
            "error_summary": self.error_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class AdminEmailLog(Base):
    """Detailed audit delivery record for each recipient in a campaign."""
    __tablename__ = "admin_email_logs"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("admin_email_campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    recipient_name = Column(String(300), nullable=False)
    recipient_email = Column(String(300), nullable=False, index=True)
    institution_name = Column(String(500), nullable=True)
    
    # Delivery status: queued, sent, failed
    status = Column(String(50), default="queued", index=True)
    error_message = Column(Text, nullable=True)
    smtp_response = Column(String(500), nullable=True)
    message_id = Column(String(300), nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    campaign = relationship("AdminEmailCampaign", back_populates="logs")
    contact = relationship("Contact")

    def to_dict(self):
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "contact_id": self.contact_id,
            "recipient_name": self.recipient_name,
            "recipient_email": self.recipient_email,
            "institution_name": self.institution_name,
            "status": self.status,
            "error_message": self.error_message,
            "message_id": self.message_id,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ContactEmailThread(Base):
    """Tracks ongoing correspondence conversation and AI dialogue summary per contact."""
    __tablename__ = "contact_email_threads"

    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    contact_email = Column(String(300), nullable=False, index=True)
    contact_name = Column(String(400), nullable=False)
    institution_name = Column(String(500), nullable=True)
    technology_area = Column(String(200), nullable=True)
    
    # Thread status: 'no_outreach', 'pending_reply', 'replied', 'interested', 'meeting_scheduled', 'joined', 'opted_out', 'closed'
    status = Column(String(50), default="pending_reply", index=True)
    
    # Aggregated metrics
    total_messages = Column(Integer, default=0)
    outbound_count = Column(Integer, default=0)
    inbound_count = Column(Integer, default=0)
    unread_inbound_count = Column(Integer, default=0)
    
    # Timestamps
    first_contacted_at = Column(DateTime, nullable=True)
    last_contacted_at = Column(DateTime, nullable=True)
    last_inbound_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # AI Conversation Summary & Action Items
    conversation_summary = Column(Text, nullable=True)
    key_takeaways = Column(JSON, default=list, nullable=True)
    next_action = Column(String(500), nullable=True)
    sentiment = Column(String(50), default="neutral")  # positive, neutral, warm, unresponsive, negative
    
    # Relationships
    contact = relationship("Contact")
    messages = relationship("ContactEmailMessage", back_populates="thread", cascade="all, delete-orphan", order_by="ContactEmailMessage.sent_at.asc()")

    def to_dict(self):
        return {
            "id": self.id,
            "contact_id": self.contact_id,
            "contact_email": self.contact_email,
            "contact_name": self.contact_name,
            "institution_name": self.institution_name,
            "technology_area": self.technology_area,
            "status": self.status,
            "total_messages": self.total_messages,
            "outbound_count": self.outbound_count,
            "inbound_count": self.inbound_count,
            "unread_inbound_count": self.unread_inbound_count,
            "first_contacted_at": self.first_contacted_at.isoformat() if self.first_contacted_at else None,
            "last_contacted_at": self.last_contacted_at.isoformat() if self.last_contacted_at else None,
            "last_inbound_at": self.last_inbound_at.isoformat() if self.last_inbound_at else None,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "conversation_summary": self.conversation_summary,
            "key_takeaways": self.key_takeaways or [],
            "next_action": self.next_action,
            "sentiment": self.sentiment,
        }


class ContactEmailMessage(Base):
    """Individual inbound or outbound email within a correspondence thread."""
    __tablename__ = "contact_email_messages"

    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey("contact_email_threads.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("admin_email_campaigns.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # RFC 822 Message-ID or IMAP UID to prevent duplicates
    message_id = Column(String(300), nullable=True, unique=True, index=True)
    in_reply_to = Column(String(300), nullable=True)
    
    # Direction: 'outbound' (Brandon -> Contact), 'inbound' (Contact -> Brandon)
    direction = Column(String(20), nullable=False, index=True)
    
    from_email = Column(String(300), nullable=False)
    from_name = Column(String(300), nullable=True)
    to_email = Column(String(300), nullable=False)
    to_name = Column(String(300), nullable=True)
    
    subject = Column(String(500), nullable=False)
    snippet = Column(String(500), nullable=True)
    body_text = Column(Text, nullable=False)
    body_html = Column(Text, nullable=True)
    
    # Attachments: [{"filename": "...", "size": 1234, "content_type": "...", "path": "..."}]
    has_attachments = Column(Boolean, default=False)
    attachments_json = Column(JSON, default=list, nullable=True)
    
    # Reading / sync status
    is_read = Column(Boolean, default=True)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    synced_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # AI message synopsis
    summary = Column(String(500), nullable=True)

    thread = relationship("ContactEmailThread", back_populates="messages")
    contact = relationship("Contact")
    campaign = relationship("AdminEmailCampaign", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "contact_id": self.contact_id,
            "campaign_id": self.campaign_id,
            "message_id": self.message_id,
            "direction": self.direction,
            "from_email": self.from_email,
            "from_name": self.from_name,
            "to_email": self.to_email,
            "to_name": self.to_name,
            "subject": self.subject,
            "snippet": self.snippet,
            "body_text": self.body_text,
            "body_html": self.body_html,
            "has_attachments": self.has_attachments,
            "attachments": self.attachments_json or [],
            "is_read": self.is_read,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
            "summary": self.summary,
        }


Index("ix_admin_email_thread_status", ContactEmailThread.status, ContactEmailThread.last_activity_at)
Index("ix_admin_email_msg_thread_date", ContactEmailMessage.thread_id, ContactEmailMessage.sent_at)
