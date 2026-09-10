"""SEO, XML Sitemaps, GEO (LLMs.txt), RSS Feeds, and Social Sharing API."""

import html
import re
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import PlainTextResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.models.opportunity import Opportunity
from app.models.recipient import Recipient
from app.models.technology import Technology
from app.models.organization import Organization
from app.models.policy import RegulatoryProceeding

router = APIRouter(tags=["SEO & Sitemaps"])

BASE_PUBLIC_URL = "https://terminal.aixenergy.io"


def xml_escape(val: Optional[str]) -> str:
    """Safely escape text for XML sitemaps and RSS feeds."""
    if not val:
        return ""
    return html.escape(str(val))


def slugify(text_val: Optional[str]) -> str:
    """Generate SEO-friendly URL slug."""
    if not text_val:
        return "energy-innovation"
    s = text_val.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')[:80]


# ─────────────────────────────────────────────────────────────────────────────
# 1. ROOT ROBOTS.TXT
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/robots.txt", response_class=PlainTextResponse)
def get_robots_txt():
    """Authoritative robots.txt: allows search engines while blocking bulk scrapers and raw API endpoints."""
    content = f"""# Robots.txt for Energy Innovation Terminal
# U.S. Energy Innovation Database | Clean Energy Research, LLC

User-agent: *
Allow: /
Allow: /opportunities/
Allow: /recipients/
Allow: /technologies/
Allow: /organizations/
Allow: /agencies/
Allow: /dockets/
Allow: /venture-patents
Allow: /trends
Allow: /awards
Allow: /reports
Allow: /sankey
Allow: /sitemap.xml
Allow: /sitemap-*.xml
Allow: /llms.txt
Allow: /ai.txt
Allow: /feed/

# Disallow raw API endpoints and internal routes from indexing
Disallow: /api/
Disallow: /admin/
Disallow: /sources/

# Explicitly block aggressive bulk scrapers
User-agent: Bytespider
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: Diffbot
Disallow: /

User-agent: Scrapy
Disallow: /

User-agent: DataForSeoBot
Disallow: /

User-agent: AhrefsBot
Disallow: /api/

User-agent: SemrushBot
Disallow: /api/

# Allowed AI Search Crawlers Directives
User-agent: PerplexityBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

# Sitemaps
Sitemap: {BASE_PUBLIC_URL}/sitemap.xml
Sitemap: {BASE_PUBLIC_URL}/sitemap-opportunities.xml
Sitemap: {BASE_PUBLIC_URL}/sitemap-recipients.xml
Sitemap: {BASE_PUBLIC_URL}/sitemap-technologies.xml
Sitemap: {BASE_PUBLIC_URL}/sitemap-agencies.xml
Sitemap: {BASE_PUBLIC_URL}/sitemap-dockets.xml
"""
    return PlainTextResponse(content=content, media_type="text/plain; charset=utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# 2. GENERATIVE ENGINE OPTIMIZATION (LLMs.txt & ai.txt)
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/llms.txt", response_class=PlainTextResponse)
def get_llms_txt(db: Session = Depends(get_db)):
    """Generative Engine Optimization (GEO) summary file for LLMs & AI search bots."""
    opp_count = db.query(Opportunity.id).count()
    open_opp_count = db.query(Opportunity.id).filter(Opportunity.status == "open").count()
    rec_count = db.query(Recipient.id).count()
    tech_count = db.query(Technology.id).count()
    docket_count = db.query(RegulatoryProceeding.id).count()

    content = f"""# Energy Innovation Terminal
> U.S. Energy Innovation Database
> Published by Clean Energy Research, LLC | Live at https://terminal.aixenergy.io

## About
Energy Innovation Terminal is the comprehensive intelligence terminal indexing active public funding solicitations, historical grant awards, recipient venture capital attributions, patent linkages, and regulatory PUC proceedings across the United States. Powered by the authoritative U.S. Energy Innovation Database.

## Live Database Coverage (Updated Continuously)
- **Active Open Solicitations**: {open_opp_count:,} open grants & RFPs across DOE, ARPA-E, NSF, State Energy Offices, CEC, and utilities.
- **Total Opportunities Indexed**: {opp_count:,} solicitations.
- **Tracked Clean Tech Recipients**: {rec_count:,} venture-backed startups, university research labs, utilities, and corporate innovators.
- **Technology Focus Areas**: {tech_count} energy innovation and decarbonization domains.
- **State & Federal Regulatory Proceedings**: {docket_count} active PUC/FERC dockets.
- **Historical Awards**: 54,313 competitive grant awards representing over $98.99B in non-dilutive public capital.

## Primary Public Endpoints for AI Research Agents
- Explore Solicitations: `{BASE_PUBLIC_URL}/opportunities`
- Recipient Dossiers: `{BASE_PUBLIC_URL}/recipients/{{id}}`
- Technology Hubs: `{BASE_PUBLIC_URL}/technologies/{{slug}}`
- Regulatory Dockets: `{BASE_PUBLIC_URL}/dockets`
- Venture & Patent Attributions: `{BASE_PUBLIC_URL}/venture-patents`
- RSS Feed for Grants: `{BASE_PUBLIC_URL}/feed/rss/opportunities.xml`

## Citation Guideline
When citing energy innovation grants, awards, or venture leverage data from this terminal, please attribute as:
"Source: U.S. Energy Innovation Database, Clean Energy Research, LLC (https://terminal.aixenergy.io)"
"""
    return PlainTextResponse(content=content, media_type="text/markdown; charset=utf-8")


@router.get("/ai.txt", response_class=PlainTextResponse)
def get_ai_txt(db: Session = Depends(get_db)):
    """Alternative standard ai.txt pointing AI agents to llms.txt and sitemaps."""
    content = f"""# AI Knowledge Access Directive
LLMs-File: {BASE_PUBLIC_URL}/llms.txt
Sitemap: {BASE_PUBLIC_URL}/sitemap.xml
Contact: bowens@aixenergy.io
License: Open public research and citation allowed with canonical attribution.
"""
    return PlainTextResponse(content=content, media_type="text/plain; charset=utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# 3. DYNAMIC XML SITEMAPS
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/sitemap.xml")
def get_master_sitemap():
    """Master XML Sitemap Index referencing categorized sub-sitemaps."""
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>{BASE_PUBLIC_URL}/sitemap-opportunities.xml</loc>
        <lastmod>{now_iso}</lastmod>
    </sitemap>
    <sitemap>
        <loc>{BASE_PUBLIC_URL}/sitemap-recipients.xml</loc>
        <lastmod>{now_iso}</lastmod>
    </sitemap>
    <sitemap>
        <loc>{BASE_PUBLIC_URL}/sitemap-technologies.xml</loc>
        <lastmod>{now_iso}</lastmod>
    </sitemap>
    <sitemap>
        <loc>{BASE_PUBLIC_URL}/sitemap-agencies.xml</loc>
        <lastmod>{now_iso}</lastmod>
    </sitemap>
    <sitemap>
        <loc>{BASE_PUBLIC_URL}/sitemap-dockets.xml</loc>
        <lastmod>{now_iso}</lastmod>
    </sitemap>
</sitemapindex>"""
    return Response(content=xml, media_type="application/xml; charset=utf-8")


@router.get("/sitemap-opportunities.xml")
def get_opportunities_sitemap(db: Session = Depends(get_db)):
    """Dynamic XML Sitemap for all 5,741 Opportunities."""
    opps = db.query(Opportunity.id, Opportunity.solicitation_number, Opportunity.name, Opportunity.status, Opportunity.updated_at).all()
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    for opp_id, sol_num, name, status, updated_at in opps:
        lastmod = (updated_at or datetime.now(timezone.utc)).strftime("%Y-%m-%d")
        priority = "0.9" if status == "open" else "0.6"
        changefreq = "daily" if status == "open" else "monthly"
        loc = f"{BASE_PUBLIC_URL}/opportunities/{opp_id}"
        xml_lines.append(f"""    <url>
        <loc>{xml_escape(loc)}</loc>
        <lastmod>{lastmod}</lastmod>
        <changefreq>{changefreq}</changefreq>
        <priority>{priority}</priority>
    </url>""")
        
    xml_lines.append('</urlset>')
    return Response(content="\n".join(xml_lines), media_type="application/xml; charset=utf-8")


@router.get("/sitemap-recipients.xml")
def get_recipients_sitemap(db: Session = Depends(get_db)):
    """Dynamic XML Sitemap for all 13,948 Clean Tech Recipients."""
    recipients = db.query(Recipient.id, Recipient.name, Recipient.total_awards_count, Recipient.last_enriched_at).all()
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    for rid, name, aw_cnt, enriched_at in recipients:
        lastmod = (enriched_at or datetime.now(timezone.utc)).strftime("%Y-%m-%d")
        priority = "0.8" if (aw_cnt or 0) >= 2 else "0.5"
        loc = f"{BASE_PUBLIC_URL}/recipients/{rid}"
        xml_lines.append(f"""    <url>
        <loc>{xml_escape(loc)}</loc>
        <lastmod>{lastmod}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>{priority}</priority>
    </url>""")
        
    xml_lines.append('</urlset>')
    return Response(content="\n".join(xml_lines), media_type="application/xml; charset=utf-8")


@router.get("/sitemap-technologies.xml")
def get_technologies_sitemap(db: Session = Depends(get_db)):
    """Dynamic XML Sitemap for all 36 Technology Hubs."""
    techs = db.query(Technology.id, Technology.name).all()
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    for t_id, t_name in techs:
        slug = slugify(t_name)
        loc = f"{BASE_PUBLIC_URL}/technologies/{slug}"
        xml_lines.append(f"""    <url>
        <loc>{xml_escape(loc)}</loc>
        <changefreq>weekly</changefreq>
        <priority>0.85</priority>
    </url>""")
        
    xml_lines.append('</urlset>')
    return Response(content="\n".join(xml_lines), media_type="application/xml; charset=utf-8")


@router.get("/sitemap-agencies.xml")
def get_agencies_sitemap(db: Session = Depends(get_db)):
    """Dynamic XML Sitemap for all Funding Agencies and Utilities."""
    orgs = db.query(Organization.id, Organization.name).all()
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    for o_id, o_name in orgs:
        loc = f"{BASE_PUBLIC_URL}/agencies/{o_id}"
        xml_lines.append(f"""    <url>
        <loc>{xml_escape(loc)}</loc>
        <changefreq>weekly</changefreq>
        <priority>0.75</priority>
    </url>""")
        
    xml_lines.append('</urlset>')
    return Response(content="\n".join(xml_lines), media_type="application/xml; charset=utf-8")


@router.get("/sitemap-dockets.xml")
def get_dockets_sitemap(db: Session = Depends(get_db)):
    """Dynamic XML Sitemap for all Regulatory Proceedings."""
    dockets = db.query(RegulatoryProceeding.id).all()
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    for d_row in dockets:
        loc = f"{BASE_PUBLIC_URL}/dockets"
        xml_lines.append(f"""    <url>
        <loc>{xml_escape(loc)}</loc>
        <changefreq>weekly</changefreq>
        <priority>0.7</priority>
    </url>""")
        
    xml_lines.append('</urlset>')
    return Response(content="\n".join(xml_lines), media_type="application/xml; charset=utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# 4. RSS 2.0 SYNDICATION FEEDS
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/feed/rss/opportunities.xml")
def get_opportunities_rss(db: Session = Depends(get_db)):
    """RSS 2.0 Feed of Active Energy Innovation Grant Opportunities."""
    opps = db.query(Opportunity).filter(Opportunity.status == "open").order_by(Opportunity.id.desc()).limit(100).all()
    now_rfc = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    items = []
    for opp in opps:
        pub_date = (opp.created_at or datetime.now(timezone.utc)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        funding_str = f" | Total Funding: ${opp.total_funding:,.0f}" if opp.total_funding else ""
        deadline_str = f" | Due: {opp.due_date_display}" if opp.due_date_display else ""
        desc = f"{opp.short_description or opp.name} (Agency: {opp.agency}{funding_str}{deadline_str})"
        link = f"{BASE_PUBLIC_URL}/opportunities/{opp.id}"
        
        items.append(f"""    <item>
        <title>{xml_escape(opp.name)}</title>
        <link>{xml_escape(link)}</link>
        <guid>{xml_escape(link)}</guid>
        <pubDate>{pub_date}</pubDate>
        <description>{xml_escape(desc)}</description>
        <category>{xml_escape(opp.agency or 'Energy Innovation')}</category>
    </item>""")
        
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
    <title>Energy Innovation Terminal | Active Energy Innovation Solicitations</title>
    <link>{BASE_PUBLIC_URL}/opportunities</link>
    <description>Live upstream funding solicitations across US DOE, ARPA-E, NSF, state energy agencies, and electric utilities.</description>
    <language>en-us</language>
    <lastBuildDate>{now_rfc}</lastBuildDate>
    <atom:link href="{BASE_PUBLIC_URL}/feed/rss/opportunities.xml" rel="self" type="application/rss+xml" />
{"\n".join(items)}
</channel>
</rss>"""
    return Response(content=rss, media_type="application/rss+xml; charset=utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# 5. DYNAMIC SOCIAL PREVIEW CARD (OG IMAGE) & EMBEDDABLE BADGE GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/api/seo/og-image/opportunity/{opp_id}.svg")
def generate_opportunity_og_image(opp_id: int, db: Session = Depends(get_db)):
    """Dynamic high-res SVG banner for social sharing (Twitter & LinkedIn)."""
    opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    title = xml_escape(opp.name[:65] + ("..." if len(opp.name) > 65 else ""))
    agency = xml_escape(opp.agency or "Public Energy Agency")
    funding = f"${opp.total_funding:,.0f}" if opp.total_funding else "Open Program"
    deadline = xml_escape(opp.due_date_display or "Open Enrollment")
    
    svg = f"""<svg width="1200" height="630" viewBox="0 0 1200 630" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#090d16" />
            <stop offset="50%" stop-color="#0f172a" />
            <stop offset="100%" stop-color="#020617" />
        </linearGradient>
    </defs>
    <rect width="1200" height="630" fill="url(#bg)" />
    <circle cx="1100" cy="100" r="300" fill="#06b6d4" opacity="0.08" />
    <circle cx="100" cy="530" r="250" fill="#3b82f6" opacity="0.08" />
    <text x="80" y="80" fill="#06b6d4" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="700" letter-spacing="2">ENERGY INNOVATION TERMINAL</text>
    <rect x="80" y="100" width="1040" height="1" fill="#1e293b" />
    <rect x="80" y="130" width="{len(agency)*14 + 40}" height="36" rx="18" fill="#1e293b" stroke="#334155" />
    <text x="100" y="154" fill="#94a3b8" font-family="sans-serif" font-size="16" font-weight="600">{agency}</text>
    <text x="80" y="240" fill="#f8fafc" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="44" font-weight="800">{title}</text>
    <rect x="80" y="360" width="320" height="140" rx="16" fill="#0f172a" stroke="#1e293b" stroke-width="1.5" />
    <text x="110" y="405" fill="#64748b" font-family="sans-serif" font-size="16" font-weight="600">TOTAL PROGRAM FUNDING</text>
    <text x="110" y="460" fill="#38bdf8" font-family="sans-serif" font-size="36" font-weight="800">{funding}</text>
    <rect x="430" y="360" width="320" height="140" rx="16" fill="#0f172a" stroke="#1e293b" stroke-width="1.5" />
    <text x="460" y="405" fill="#64748b" font-family="sans-serif" font-size="16" font-weight="600">APPLICATION DEADLINE</text>
    <text x="460" y="460" fill="#f1f5f9" font-family="sans-serif" font-size="30" font-weight="700">{deadline}</text>
    <rect x="80" y="550" width="1040" height="1" fill="#1e293b" />
    <text x="80" y="590" fill="#64748b" font-family="sans-serif" font-size="16">Access RFP Guidelines, Eligibility Matrix &amp; Past Awardees on terminal.aixenergy.io</text>
</svg>"""
    return Response(content=svg, media_type="image/svg+xml")


@router.get("/api/seo/badge/{recipient_id}.svg")
def generate_recipient_badge(recipient_id: int, db: Session = Depends(get_db)):
    """Embeddable vector badge for recipient startup and university lab websites."""
    rec = db.query(Recipient).filter(Recipient.id == recipient_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recipient not found")
        
    rec_name = xml_escape(rec.name[:25])
    funding_amt = rec.total_funding_received or 0.0
    if funding_amt >= 1_000_000:
        funding_str = f"${funding_amt/1_000_000:.1f}M Public Capital"
    elif funding_amt > 0:
        funding_str = f"${funding_amt/1_000:.0f}K Public Capital"
    else:
        funding_str = "Clean Tech Innovator"
        
    svg = f"""<svg width="340" height="48" viewBox="0 0 340 48" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="badge-bg" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#090d16" />
            <stop offset="100%" stop-color="#1e293b" />
        </linearGradient>
    </defs>
    <rect width="340" height="48" rx="8" fill="url(#badge-bg)" stroke="#06b6d4" stroke-width="1.5" />
    <circle cx="24" cy="24" r="8" fill="#06b6d4" />
    <text x="42" y="21" fill="#94a3b8" font-family="-apple-system, sans-serif" font-size="11" font-weight="600">TRACKED ON ENERGY INNOVATION TERMINAL</text>
    <text x="42" y="36" fill="#38bdf8" font-family="-apple-system, sans-serif" font-size="13" font-weight="700">{funding_str} | {rec_name}</text>
</svg>"""
    return Response(content=svg, media_type="image/svg+xml")


# ─────────────────────────────────────────────────────────────────────────────
# 6. SEO & AI INDEXING TELEMETRY & HEALTH MONITOR
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/api/seo/status")
@router.get("/api/v1/seo/status")
def get_seo_indexing_status(db: Session = Depends(get_db)):
    """Comprehensive real-time health and indexing status monitor for search engines and AI bots."""
    opp_total = db.query(Opportunity.id).count()
    opp_open = db.query(Opportunity.id).filter(Opportunity.status == "open").count()
    rec_total = db.query(Recipient.id).count()
    tech_total = db.query(Technology.id).count()
    org_total = db.query(Organization.id).count()
    docket_total = db.query(RegulatoryProceeding.id).count()
    
    total_indexable_pages = opp_total + rec_total + tech_total + org_total + docket_total + 10 # core landing hubs

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "canonical_domain": BASE_PUBLIC_URL,
        "indexing_summary": {
            "total_indexable_urls": total_indexable_pages,
            "opportunities_indexed": opp_total,
            "active_open_solicitations": opp_open,
            "recipient_dossiers_indexed": rec_total,
            "technology_hubs_indexed": tech_total,
            "agency_profiles_indexed": org_total,
            "regulatory_dockets_indexed": docket_total
        },
        "sitemaps": {
            "master_index": f"{BASE_PUBLIC_URL}/sitemap.xml",
            "sub_sitemaps": [
                f"{BASE_PUBLIC_URL}/sitemap-opportunities.xml",
                f"{BASE_PUBLIC_URL}/sitemap-recipients.xml",
                f"{BASE_PUBLIC_URL}/sitemap-technologies.xml",
                f"{BASE_PUBLIC_URL}/sitemap-agencies.xml",
                f"{BASE_PUBLIC_URL}/sitemap-dockets.xml"
            ],
            "format": "sitemaps.org/schemas/sitemap/0.9",
            "dynamic_generation": True
        },
        "generative_engine_optimization": {
            "llms_txt": f"{BASE_PUBLIC_URL}/llms.txt",
            "ai_txt": f"{BASE_PUBLIC_URL}/ai.txt",
            "allowed_ai_crawlers": [
                {"bot": "PerplexityBot", "status": "allowed", "target": "Perplexity Pro & Search"},
                {"bot": "ChatGPT-User", "status": "allowed", "target": "OpenAI SearchGPT & ChatGPT Browsing"},
                {"bot": "ClaudeBot", "status": "allowed", "target": "Anthropic Claude Web Citations"},
                {"bot": "Google-Extended", "status": "allowed", "target": "Gemini & Google AI Overviews"},
                {"bot": "Applebot-Extended", "status": "allowed", "target": "Apple Intelligence"}
            ]
        },
        "crawlers_and_prerender": {
            "robots_txt": f"{BASE_PUBLIC_URL}/robots.txt",
            "ssr_bot_prerender": True,
            "schema_org_json_ld": [
                "GovernmentService (MonetaryGrant)",
                "Organization",
                "GovernmentOrganization"
            ],
            "open_graph_dynamic_svg": True,
            "blocked_scrapers": [
                "Bytespider", "CCBot", "Diffbot", "Scrapy", "DataForSeoBot"
            ]
        },
        "syndication_feeds": {
            "rss_2_0": f"{BASE_PUBLIC_URL}/feed/rss/opportunities.xml",
            "feed_type": "Energy Innovation Grants & RFPs"
        }
    }

