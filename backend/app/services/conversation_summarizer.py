"""AI and structured dialogue summarization engine for contact email correspondence."""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.config import settings
from app.models.admin_email import ContactEmailThread, ContactEmailMessage

logger = logging.getLogger("ConversationSummarizer")

SUMMARY_PROMPT_TEMPLATE = """You are the Executive Communications Director for Energy Innovation Terminal.
Analyze this email correspondence thread between Brandon Owens (Founder & Lead Principal) and an external clean tech stakeholder ({contact_name} at {contact_org}).

=== EMAIL THREAD CORRESPONDENCE ===
{formatted_conversation}

=== INSTRUCTIONS ===
1. Synthesize a concise 2-3 sentence executive summary of the conversation state and stakeholder intent.
2. Classify stakeholder sentiment: "positive", "warm", "neutral", "skeptical", or "negative".
3. Classify thread status: "pending_reply", "replied", "interested", "meeting_scheduled", "joined", or "opted_out".
4. Extract 2-3 concise bullet takeaways.
5. Prescribe a concrete, actionable next step for Brandon Owens.
6. Draft a polished, polite, and authoritative email reply from Brandon Owens addressing their points.

Return ONLY a valid JSON object strictly matching this schema:
{{
  "summary": "<2-3 sentence executive synthesis of conversation state>",
  "sentiment": "positive",
  "status": "replied",
  "key_takeaways": ["<Bullet takeaway 1>", "<Bullet takeaway 2>"],
  "next_action": "<Concrete recommended action for Brandon Owens>",
  "suggested_reply_draft": "<Polished email draft text>"
}}
"""


def _run_llm_summarization(formatted_conversation: str, contact_name: str, contact_org: str) -> Optional[Dict[str, Any]]:
    """Invokes OpenAI, Gemini, or Anthropic to summarize email correspondence."""
    openai_key = getattr(settings, "openai_api_key", None) or os.environ.get("OPENAI_API_KEY")
    gemini_key = getattr(settings, "gemini_api_key", None) or os.environ.get("GEMINI_API_KEY")
    anthropic_key = getattr(settings, "anthropic_api_key", None) or os.environ.get("ANTHROPIC_API_KEY")

    if not (openai_key or gemini_key or anthropic_key):
        return None

    prompt = SUMMARY_PROMPT_TEMPLATE.format(
        contact_name=contact_name or "Stakeholder",
        contact_org=contact_org or "Partner Organization",
        formatted_conversation=formatted_conversation
    )

    # 1. Try OpenAI
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key, timeout=25.0, max_retries=2)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are the Executive Communications Director for Energy Innovation Terminal. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1000,
            )
            parsed = json.loads(resp.choices[0].message.content or "{}")
            if parsed.get("summary") and parsed.get("key_takeaways"):
                parsed["summarized_by"] = "OpenAI GPT-4o-mini"
                return parsed
        except Exception as e:
            logger.warning(f"OpenAI conversation summarization failed: {e}")

    # 2. Try Gemini
    if gemini_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                )
            )
            parsed = json.loads(response.text or "{}")
            if parsed.get("summary") and parsed.get("key_takeaways"):
                parsed["summarized_by"] = "Google Gemini 2.5 Flash"
                return parsed
        except Exception as e:
            logger.warning(f"Gemini conversation summarization failed: {e}")

    return None


def summarize_conversation_thread(db: Session, thread_id: int) -> Dict[str, Any]:
    """Analyze messages in a correspondence thread and synthesize executive summary, sentiment, and status."""
    thread = db.query(ContactEmailThread).filter_by(id=thread_id).first()
    if not thread:
        return {"status": "error", "message": f"Thread {thread_id} not found"}
        
    messages = db.query(ContactEmailMessage).filter_by(thread_id=thread.id).order_by(ContactEmailMessage.sent_at.asc()).all()
    if not messages:
        return {"status": "ok", "message": "No messages to summarize"}
        
    inbound_msgs = [m for m in messages if m.direction == "inbound"]
    outbound_msgs = [m for m in messages if m.direction == "outbound"]
    last_msg = messages[-1]

    # Format transcript for LLM
    formatted_msgs = []
    for m in messages:
        dir_lbl = "Brandon Owens (Admin)" if m.direction == "outbound" else f"{thread.contact_name or 'Stakeholder'} (Contact)"
        date_str = m.sent_at.strftime("%b %d, %Y %I:%M %p") if m.sent_at else "Recently"
        body = (m.body_text or m.snippet or "").strip()
        formatted_msgs.append(f"[{date_str}] {dir_lbl}:\nSubject: {m.subject or 'No Subject'}\n{body}")
    
    formatted_conversation = "\n\n---\n\n".join(formatted_msgs)

    # Attempt Live LLM Summarization first
    contact_org = getattr(thread, "institution_name", None) or "Clean Tech Entity"
    llm_result = _run_llm_summarization(
        formatted_conversation=formatted_conversation,
        contact_name=thread.contact_name or "Stakeholder",
        contact_org=contact_org
    )

    if llm_result:
        thread.conversation_summary = llm_result.get("summary")
        thread.key_takeaways = llm_result.get("key_takeaways", [])
        thread.next_action = llm_result.get("next_action")
        thread.sentiment = llm_result.get("sentiment", "neutral")
        if thread.status not in ["joined", "opted_out"]:
            thread.status = llm_result.get("status", thread.status)
        db.commit()

        return {
            "thread_id": thread.id,
            "summary": thread.conversation_summary,
            "status": thread.status,
            "sentiment": thread.sentiment,
            "next_action": thread.next_action,
            "takeaways": thread.key_takeaways,
            "suggested_reply_draft": llm_result.get("suggested_reply_draft"),
            "summarized_by": llm_result.get("summarized_by", "Live LLM")
        }

    # Deterministic extractive fallback synthesis
    summary_parts = []
    takeaways = []
    sentiment = "neutral"
    detected_status = thread.status
    
    if outbound_msgs:
        first_outbound = outbound_msgs[0]
        outbound_date_str = first_outbound.sent_at.strftime("%b %d, %Y") if first_outbound.sent_at else "recently"
        summary_parts.append(f"Admin outreach sent on {outbound_date_str} regarding '{first_outbound.subject}'.")
        takeaways.append(f"Initiated contact via subject: '{first_outbound.subject}'")
        
    if inbound_msgs:
        last_inbound = inbound_msgs[-1]
        inbound_date_str = last_inbound.sent_at.strftime("%b %d, %Y") if last_inbound.sent_at else "recently"
        snippet = last_inbound.snippet or last_inbound.body_text[:120]
        lower_body = (last_inbound.body_text or "").lower()
        
        positive_keywords = ["interested", "happy to", "sounds great", "would love", "let's connect", "call", "zoom", "schedule", "meet", "discuss", "partner", "teaming", "joined", "signed up", "thanks for reaching out"]
        meeting_keywords = ["calendar", "schedule", "availability", "time to talk", "zoom", "teams", "tuesday", "wednesday", "thursday", "friday", "monday", "am", "pm"]
        unsubscribe_keywords = ["unsubscribe", "remove", "do not contact", "stop emailing", "wrong person", "no longer with"]
        
        if any(kw in lower_body for kw in unsubscribe_keywords):
            sentiment = "negative"
            detected_status = "opted_out"
            next_action = "Opted out. Do not send further automated campaigns."
            summary_parts.append(f"Contact responded on {inbound_date_str} requesting removal or no contact.")
            takeaways.append("Contact requested removal from future outreach.")
        elif any(kw in lower_body for kw in meeting_keywords) and any(kw in lower_body for kw in positive_keywords):
            sentiment = "positive"
            detected_status = "meeting_scheduled"
            next_action = "Coordinate meeting details and send calendar invitation."
            summary_parts.append(f"Contact responded positively on {inbound_date_str} seeking to schedule a discussion: \"{snippet}\"")
            takeaways.append("Contact expressed active interest in scheduling introductory meeting.")
        elif any(kw in lower_body for kw in positive_keywords):
            sentiment = "warm"
            detected_status = "interested"
            next_action = "Follow up with application onboarding link and teaming specifics."
            summary_parts.append(f"Contact responded on {inbound_date_str} with positive engagement: \"{snippet}\"")
            takeaways.append("Contact is receptive to collaboration and platform adoption.")
        else:
            sentiment = "neutral"
            detected_status = "replied"
            next_action = "Review incoming reply and respond with relevant context."
            summary_parts.append(f"Contact replied on {inbound_date_str}: \"{snippet}\"")
            takeaways.append(f"Received reply from {last_inbound.from_name or thread.contact_name}.")
    else:
        # Outbound only with no response yet
        days_since_contact = (datetime.utcnow() - (last_msg.sent_at or datetime.utcnow())).days
        if days_since_contact > 14:
            detected_status = "pending_reply"
            next_action = "Consider sending 2nd follow-up reminder with updated solicitation highlights."
            summary_parts.append(f"No response received after {days_since_contact} days.")
            takeaways.append("Awaiting initial response to platform invitation.")
        elif days_since_contact > 5:
            detected_status = "pending_reply"
            next_action = "Awaiting reply. Follow-up window active."
            summary_parts.append("Initial outreach sent; follow-up window currently active.")
            takeaways.append("Pending reply.")
        else:
            detected_status = "pending_reply"
            next_action = "Recent outreach sent. Monitor inbox for response."
            summary_parts.append("Recent outreach sent.")
            takeaways.append("Outreach pending review by contact.")
            
    full_summary = " ".join(summary_parts)
    
    # Save back to thread
    thread.conversation_summary = full_summary
    thread.key_takeaways = takeaways
    thread.next_action = next_action
    thread.sentiment = sentiment
    if thread.status not in ["joined", "opted_out"]:
        thread.status = detected_status
        
    db.commit()
    
    return {
        "thread_id": thread.id,
        "summary": full_summary,
        "status": thread.status,
        "sentiment": sentiment,
        "next_action": next_action,
        "takeaways": takeaways,
        "suggested_reply_draft": f"Hi {thread.contact_name or 'there'},\n\nThank you for your response regarding our clean energy funding intelligence platform. I'd be glad to discuss how our data can support your upcoming grant and innovation initiatives.\n\nBest regards,\nBrandon Owens",
        "summarized_by": "Deterministic House Engine (Offline)"
    }

