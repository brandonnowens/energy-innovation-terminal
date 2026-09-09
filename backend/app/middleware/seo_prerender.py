"""SEO Crawler Pre-rendering & Structured JSON-LD Middleware.

Intercepts search engine crawlers and social share bots (Googlebot, PerplexityBot,
Twitterbot, LinkedInBot, etc.) to serve semantic HTML snapshots with high-CTR
meta tags, Open Graph cards, and Schema.org JSON-LD structured data.
"""

import json
import html
import re
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from app.database import SessionLocal
from app.models.opportunity import Opportunity
from app.models.recipient import Recipient
from app.models.technology import Technology
from app.models.organization import Organization
from app.models.policy import RegulatoryProceeding

# Recognized Search & Social Bot User-Agents
BOT_USER_AGENTS = [
    "googlebot", "bingbot", "yandexbot", "baiduspider", "duckduckbot",
    "slurp", "twitterbot", "facebookexternalhit", "linkedinbot", "embedly",
    "quora link preview", "showyoubot", "outbrain", "pinterest/0.",
    "slackbot", "vkshare", "w3c_validator", "whatsapp", "flipboard",
    "tumblr", "bitlybot", "skypeuripreview", "nuzzel", "discordbot",
    "google-structured-data-testing-tool", "perplexitybot", "chatgpt-user",
    "claudebot", "applebot", "ia_archiver"
]

BASE_URL = "https://terminal.aixenergy.io"


def is_bot(user_agent: Optional[str]) -> bool:
    """Check if incoming request is from a search crawler or social bot."""
    if not user_agent:
        return False
    ua_lower = user_agent.lower()
    return any(bot in ua_lower for bot in BOT_USER_AGENTS)


def escape(val: Optional[str]) -> str:
    """Escape text for HTML attributes and content."""
    if not val:
        return ""
    return html.escape(str(val))


class SeoPrerenderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only process GET requests from recognized bots
        if request.method != "GET":
            return await call_next(request)
            
        user_agent = request.headers.get("user-agent", "")
        if not is_bot(user_agent):
            return await call_next(request)
            
        path = request.url.path
        
        # Don't intercept API or static asset paths
        if path.startswith("/api/") or path.startswith("/assets/") or "." in path.split("/")[-1]:
            return await call_next(request)
            
        # 1. Opportunity Details (/opportunities/:id)
        opp_match = re.match(r'^/opportunities/(\d+)', path)
        if opp_match:
            opp_id = int(opp_match.group(1))
            html_content = self.render_opportunity_seo(opp_id)
            if html_content:
                return HTMLResponse(content=html_content, status_code=200)
                
        # 2. Recipient Dossier (/recipients/:id)
        rec_match = re.match(r'^/recipients/(\d+)', path)
        if rec_match:
            rec_id = int(rec_match.group(1))
            html_content = self.render_recipient_seo(rec_id)
            if html_content:
                return HTMLResponse(content=html_content, status_code=200)
                
        # 3. Technology Hub (/technologies/:slug)
        tech_match = re.match(r'^/technologies/([a-zA-Z0-9_-]+)', path)
        if tech_match:
            tech_slug = tech_match.group(1)
            html_content = self.render_technology_seo(tech_slug)
            if html_content:
                return HTMLResponse(content=html_content, status_code=200)
                
        # Fall back to normal pipeline
        return await call_next(request)

    def render_opportunity_seo(self, opp_id: int) -> Optional[str]:
        db = SessionLocal()
        try:
            opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
            if not opp:
                return None
                
            title = f"{opp.name} | {opp.agency or 'Public Energy Grant'} - Energy Innovation Terminal"
            desc = (opp.short_description or opp.name)[:280]
            if opp.total_funding:
                funding_str = f" Total Funding: ${opp.total_funding:,.0f}."
            else:
                funding_str = ""
            if opp.due_date_display:
                due_str = f" Deadline: {opp.due_date_display}."
            else:
                due_str = ""
            full_desc = f"{desc}{funding_str}{due_str} Explore eligibility, RFP guidelines, and past awardees on Energy Innovation Terminal."
            
            canonical_url = f"{BASE_URL}/opportunities/{opp.id}"
            og_image = f"{BASE_URL}/api/seo/og-image/opportunity/{opp.id}.svg"
            
            # JSON-LD Schema
            schema = {
                "@context": "https://schema.org",
                "@type": "GovernmentService",
                "name": opp.name,
                "serviceType": "MonetaryGrant",
                "provider": {
                    "@type": "GovernmentOrganization",
                    "name": opp.agency or "Public Energy Agency"
                },
                "offers": {
                    "@type": "Offer",
                    "price": str(opp.total_funding or 0),
                    "priceCurrency": "USD",
                    "validThrough": opp.close_date.isoformat() if opp.close_date else None
                },
                "description": opp.short_description or opp.name,
                "url": canonical_url
            }
            
            return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{escape(title)}</title>
    <meta name="description" content="{escape(full_desc)}">
    <link rel="canonical" href="{canonical_url}">
    
    <!-- Open Graph / Facebook / LinkedIn -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:title" content="{escape(opp.name)}">
    <meta property="og:description" content="{escape(full_desc)}">
    <meta property="og:image" content="{og_image}">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="{canonical_url}">
    <meta name="twitter:title" content="{escape(opp.name)}">
    <meta name="twitter:description" content="{escape(full_desc)}">
    <meta name="twitter:image" content="{og_image}">
    
    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
    {json.dumps(schema, indent=2)}
    </script>
</head>
<body style="font-family: sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #1e293b;">
    <header>
        <p style="color: #0284c7; font-weight: bold; font-size: 14px; letter-spacing: 1px;">ENERGY INNOVATION TERMINAL</p>
        <h1 style="font-size: 32px; color: #0f172a;">{escape(opp.name)}</h1>
        <p><strong>Agency:</strong> {escape(opp.agency or 'Public Agency')} | <strong>Solicitation Number:</strong> {escape(opp.solicitation_number or 'N/A')}</p>
        <p><strong>Total Funding:</strong> {funding_str or 'Open Solicitation'} | <strong>Status:</strong> {escape(opp.status)} | <strong>Deadline:</strong> {escape(opp.due_date_display or 'Open Enrollment')}</p>
    </header>
    <main>
        <h2>Program Description</h2>
        <p>{escape(opp.short_description or opp.name)}</p>
        <p><a href="{canonical_url}" style="background: #0284c7; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; display: inline-block;">View Live Opportunity Details &amp; Past Awardees</a></p>
    </main>
</body>
</html>"""
        finally:
            db.close()

    def render_recipient_seo(self, rec_id: int) -> Optional[str]:
        db = SessionLocal()
        try:
            rec = db.query(Recipient).filter(Recipient.id == rec_id).first()
            if not rec:
                return None
                
            title = f"{rec.name} Funding History, DOE Grants & Awards | Energy Innovation Terminal"
            tech = rec.primary_technology or "Clean Energy"
            funding_str = f"${rec.total_funding_received:,.0f}" if rec.total_funding_received else "$0"
            desc = f"Comprehensive public grant and funding track record for {rec.name}. Tracked with {funding_str} across {rec.total_awards_count or 0} competitive awards in {tech}. Explore patent linkages and venture attributions."
            canonical_url = f"{BASE_URL}/recipients/{rec.id}"
            badge_image = f"{BASE_URL}/api/seo/badge/{rec.id}.svg"
            
            schema = {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": rec.name,
                "description": rec.description,
                "url": rec.website_url or canonical_url,
                "knowsAbout": [tech, rec.sector or "Clean Energy"]
            }
            
            return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{escape(title)}</title>
    <meta name="description" content="{escape(desc)}">
    <link rel="canonical" href="{canonical_url}">
    <meta property="og:title" content="{escape(title)}">
    <meta property="og:description" content="{escape(desc)}">
    <meta property="og:image" content="{badge_image}">
    <script type="application/ld+json">
    {json.dumps(schema, indent=2)}
    </script>
</head>
<body style="font-family: sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; line-height: 1.6;">
    <h1>{escape(rec.name)} - Clean Energy Grant Funding Dossier</h1>
    <p><strong>Primary Technology:</strong> {escape(tech)} | <strong>HQ:</strong> {escape(rec.headquarters_city)}, {escape(rec.headquarters_state)}</p>
    <p><strong>Total Public Funding:</strong> {funding_str} across {rec.total_awards_count or 0} award(s)</p>
    <p>{escape(rec.description)}</p>
    <p><a href="{canonical_url}">View full awards ledger, venture rounds &amp; patent linkages</a></p>
</body>
</html>"""
        finally:
            db.close()

    def render_technology_seo(self, tech_slug: str) -> Optional[str]:
        db = SessionLocal()
        try:
            techs = db.query(Technology).all()
            matched = None
            for t in techs:
                s = re.sub(r'[^a-z0-9]+', '-', t.name.lower()).strip('-')
                if s == tech_slug or tech_slug in s:
                    matched = t
                    break
            if not matched:
                return None
                
            title = f"{matched.name} Public Funding, Grants & Solicitations 2026 | Energy Innovation Terminal"
            desc = f"Directory of active federal and state clean energy grants, RFPs, venture attributions, and awards for {matched.name}."
            canonical_url = f"{BASE_URL}/technologies/{tech_slug}"
            
            return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{escape(title)}</title>
    <meta name="description" content="{escape(desc)}">
    <link rel="canonical" href="{canonical_url}">
</head>
<body style="font-family: sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px;">
    <h1>{escape(matched.name)} Clean Energy Grants &amp; Solicitations</h1>
    <p>{escape(desc)}</p>
    <p><a href="{canonical_url}">Explore open solicitations, top funded innovators, and regulatory dockets</a></p>
</body>
</html>"""
        finally:
            db.close()
