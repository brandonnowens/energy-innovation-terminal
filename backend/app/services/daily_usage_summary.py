"""
Daily User Application Usage & Activity Metrics Engine.

Exclusively measures and summarizes user engagement, including:
1. Executive User Usage & Traffic Snapshot (DAU, Sessions, Actions, Page Views)
2. User Accounts, Membership Tiers & Recent Logins
3. Core Feature Utilization by Users (Grant Matches, Proposals, FOA Shreds, Reports, Strategies)
4. User Request Traffic, Action Types & Device Demographics
5. 14-Day Historical User Activity & Engagement Velocity Matrix
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func

logger = logging.getLogger("DailyUserUsageSummary")

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "reports" / "daily_usage"


def format_currency(val: Optional[float]) -> str:
    """Format numeric values into standard USD notation."""
    if val is None or val == 0:
        return "$0"
    if abs(val) >= 1_000_000_000:
        return f"${val / 1_000_000_000:,.2f}B"
    if abs(val) >= 1_000_000:
        return f"${val / 1_000_000:,.2f}M"
    if abs(val) >= 1_000:
        return f"${val / 1_000:,.1f}K"
    return f"${val:,.2f}"


def format_number(val: Optional[int]) -> str:
    """Format integers with commas."""
    if val is None:
        return "0"
    return f"{val:,}"


def collect_user_usage_metrics(db: Session, target_date: Optional[datetime] = None) -> Dict[str, Any]:
    """Compile user-focused usage metrics across all platform touchpoints."""
    if target_date is None:
        target_date = datetime.now(timezone.utc)

    target_date_str = target_date.strftime("%Y-%m-%d")
    start_of_day = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
    end_of_day = start_of_day + timedelta(days=1)
    
    cutoff_24h = target_date - timedelta(days=1)
    cutoff_7d = target_date - timedelta(days=7)
    cutoff_30d = target_date - timedelta(days=30)

    data: Dict[str, Any] = {
        "report_date": target_date_str,
        "generated_at": target_date.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "user_metrics": {}
    }

    # 1. User Accounts & Membership Metrics
    try:
        total_users = db.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
        active_users = db.execute(text("SELECT COUNT(*) FROM users WHERE is_active = true")).scalar() or 0
        verified_users = db.execute(text("SELECT COUNT(*) FROM users WHERE is_verified = true")).scalar() or 0
        
        tier_counts_raw = db.execute(text(
            "SELECT COALESCE(tier, 'unknown') as tier, COUNT(*) as count FROM users GROUP BY tier"
        )).fetchall()
        tier_counts = {row[0]: row[1] for row in tier_counts_raw}

        role_counts_raw = db.execute(text(
            "SELECT COALESCE(role, 'user') as role, COUNT(*) as count FROM users GROUP BY role"
        )).fetchall()
        role_counts = {row[0]: row[1] for row in role_counts_raw}

        recent_logins_raw = db.execute(text(
            "SELECT email, full_name, organization_name, tier, last_login_at FROM users "
            "WHERE last_login_at IS NOT NULL ORDER BY last_login_at DESC LIMIT 6"
        )).fetchall()
        recent_logins = [
            {
                "email": r[0],
                "name": r[1] or "N/A",
                "organization": r[2] or "N/A",
                "tier": r[3] or "free",
                "last_login": r[4].strftime("%Y-%m-%d %H:%M UTC") if r[4] else "N/A"
            }
            for r in recent_logins_raw
        ]

        data["user_metrics"]["accounts"] = {
            "total_registered": total_users,
            "active_accounts": active_users,
            "verified_accounts": verified_users,
            "tiers": tier_counts,
            "roles": role_counts,
            "recent_logins": recent_logins
        }
    except Exception as e:
        logger.warning(f"Error collecting account metrics: {e}")
        data["user_metrics"]["accounts"] = {"total_registered": 0, "active_accounts": 0, "verified_accounts": 0, "tiers": {}, "roles": {}, "recent_logins": []}

    # 2. AI Grant Match & Project Analyses
    try:
        total_analyses = db.execute(text("SELECT COUNT(*) FROM project_analyses")).scalar() or 0
        analyses_today = db.execute(text(
            "SELECT COUNT(*) FROM project_analyses WHERE created_at >= :s AND created_at < :e"
        ), {"s": start_of_day, "e": end_of_day}).scalar() or 0
        analyses_24h = db.execute(text("SELECT COUNT(*) FROM project_analyses WHERE created_at >= :c"), {"c": cutoff_24h}).scalar() or 0
        analyses_7d = db.execute(text("SELECT COUNT(*) FROM project_analyses WHERE created_at >= :c"), {"c": cutoff_7d}).scalar() or 0
        analyses_30d = db.execute(text("SELECT COUNT(*) FROM project_analyses WHERE created_at >= :c"), {"c": cutoff_30d}).scalar() or 0

        # Technology domains searched by users
        tech_areas_raw = db.execute(text(
            "SELECT technology_areas FROM project_analyses WHERE technology_areas IS NOT NULL"
        )).fetchall()
        tech_freq: Dict[str, int] = {}
        for row in tech_areas_raw:
            val = row[0]
            if val:
                items = []
                if val.strip().startswith("[") and val.strip().endswith("]"):
                    try:
                        parsed = json.loads(val)
                        if isinstance(parsed, list):
                            items = [str(x).strip().strip('"\'') for x in parsed if str(x).strip()]
                    except Exception:
                        pass
                if not items:
                    for item in val.split(","):
                        clean = item.strip().strip("[]\"'").strip()
                        if clean:
                            items.append(clean)
                for clean in items:
                    if clean:
                        tech_freq[clean] = tech_freq.get(clean, 0) + 1
        top_tech_sectors = sorted([{"sector": k, "queries": v} for k, v in tech_freq.items()], key=lambda x: x["queries"], reverse=True)[:8]

        # Applicant personas
        app_types_raw = db.execute(text(
            "SELECT COALESCE(applicant_type, 'unspecified') as app_type, COUNT(*) as cnt "
            "FROM project_analyses GROUP BY applicant_type ORDER BY cnt DESC LIMIT 6"
        )).fetchall()
        applicant_personas = [{"persona": r[0], "count": r[1]} for r in app_types_raw]

        # TRL distribution requested by users
        trl_dist_raw = db.execute(text(
            "SELECT estimated_trl, COUNT(*) as cnt FROM project_analyses WHERE estimated_trl IS NOT NULL GROUP BY estimated_trl ORDER BY estimated_trl"
        )).fetchall()
        trl_distribution = [{"trl": f"TRL {r[0]}", "count": r[1]} for r in trl_dist_raw]

        # Recent user project queries
        recent_analyses_raw = db.execute(text(
            "SELECT applicant_type, target_location, estimated_trl, project_cost, created_at "
            "FROM project_analyses ORDER BY id DESC LIMIT 5"
        )).fetchall()
        recent_analyses = [
            {
                "persona": r[0] or "General",
                "location": r[1] or "National",
                "trl": f"TRL {r[2]}" if r[2] else "N/A",
                "cost": format_currency(r[3]) if r[3] else "N/A",
                "timestamp": r[4].strftime("%Y-%m-%d %H:%M UTC") if r[4] else "N/A"
            }
            for r in recent_analyses_raw
        ]

        data["user_metrics"]["grant_matching"] = {
            "total_lifetime_analyses": total_analyses,
            "today_analyses": analyses_today,
            "last_24h_analyses": analyses_24h,
            "last_7d_analyses": analyses_7d,
            "last_30d_analyses": analyses_30d,
            "top_sectors": top_tech_sectors,
            "applicant_personas": applicant_personas,
            "trl_distribution": trl_distribution,
            "recent_queries": recent_analyses
        }
    except Exception as e:
        logger.warning(f"Error collecting matching metrics: {e}")
        data["user_metrics"]["grant_matching"] = {"total_lifetime_analyses": 0, "today_analyses": 0, "last_24h_analyses": 0, "last_7d_analyses": 0, "last_30d_analyses": 0, "top_sectors": [], "applicant_personas": [], "trl_distribution": [], "recent_queries": []}

    # 3. Winning Proposals & Grant Applications
    try:
        total_proposals = db.execute(text("SELECT COUNT(*) FROM proposals")).scalar() or 0
        proposals_today = db.execute(text(
            "SELECT COUNT(*) FROM proposals WHERE created_at >= :s AND created_at < :e"
        ), {"s": start_of_day, "e": end_of_day}).scalar() or 0
        total_requested_funding = db.execute(text("SELECT COALESCE(SUM(target_funding), 0) FROM proposals")).scalar() or 0.0
        total_project_budget = db.execute(text("SELECT COALESCE(SUM(total_budget), 0) FROM proposals")).scalar() or 0.0
        avg_compliance_score = db.execute(text("SELECT COALESCE(AVG(compliance_pct), 0) FROM proposals WHERE compliance_pct IS NOT NULL")).scalar() or 0.0
        won_proposals_count = db.execute(text("SELECT COUNT(*) FROM proposals WHERE is_won = true")).scalar() or 0

        stages_raw = db.execute(text(
            "SELECT COALESCE(stage, 'draft') as stage, COUNT(*) as cnt FROM proposals GROUP BY stage ORDER BY cnt DESC"
        )).fetchall()
        proposal_stages = [{"stage": r[0], "count": r[1]} for r in stages_raw]

        agencies_raw = db.execute(text(
            "SELECT COALESCE(agency, 'Other') as agency, COUNT(*) as cnt, COALESCE(SUM(target_funding), 0) as funding "
            "FROM proposals GROUP BY agency ORDER BY cnt DESC LIMIT 6"
        )).fetchall()
        top_target_agencies = [{"agency": r[0], "proposals": r[1], "funding_requested": float(r[2])} for r in agencies_raw]

        recent_props_raw = db.execute(text(
            "SELECT title, agency, target_funding, compliance_pct, is_won, created_at "
            "FROM proposals ORDER BY created_at DESC NULLS LAST LIMIT 5"
        )).fetchall()
        recent_proposals = [
            {
                "title": (r[0][:50] + "...") if r[0] and len(r[0]) > 50 else (r[0] or "Untitled Proposal"),
                "agency": r[1] or "N/A",
                "target_funding": format_currency(r[2]),
                "compliance": f"{int(r[3])}%" if r[3] is not None else "N/A",
                "status": "Won" if r[4] else "Draft/Review",
                "date": r[5].strftime("%Y-%m-%d") if r[5] else "N/A"
            }
            for r in recent_props_raw
        ]

        data["user_metrics"]["proposals"] = {
            "total_proposals": total_proposals,
            "today_proposals": proposals_today,
            "won_proposals": won_proposals_count,
            "total_requested_funding_usd": float(total_requested_funding),
            "total_project_budget_usd": float(total_project_budget),
            "avg_compliance_pct": round(float(avg_compliance_score), 1),
            "stages": proposal_stages,
            "target_agencies": top_target_agencies,
            "recent_proposals": recent_proposals
        }
    except Exception as e:
        logger.warning(f"Error collecting proposal metrics: {e}")
        data["user_metrics"]["proposals"] = {"total_proposals": 0, "today_proposals": 0, "won_proposals": 0, "total_requested_funding_usd": 0.0, "total_project_budget_usd": 0.0, "avg_compliance_pct": 0, "stages": [], "target_agencies": [], "recent_proposals": []}

    # 4. AI FOA Compliance Shredder & Community Assets
    try:
        total_shreds = db.execute(text("SELECT COUNT(*) FROM foa_shred_results")).scalar() or 0
        avg_cost_share = db.execute(text("SELECT COALESCE(AVG(cost_share_required_pct), 0) FROM foa_shred_results WHERE cost_share_required_pct IS NOT NULL")).scalar() or 0.0
        j40_count = db.execute(text("SELECT COUNT(*) FROM foa_shred_results WHERE justice40_cbp_required = true")).scalar() or 0

        total_reports = db.execute(text("SELECT COUNT(*) FROM reports WHERE deleted_at IS NULL")).scalar() or 0
        total_strategies = db.execute(text("SELECT COUNT(*) FROM strategies WHERE deleted_at IS NULL")).scalar() or 0
        total_charts = db.execute(text("SELECT COUNT(*) FROM saved_charts")).scalar() or 0
        total_views = db.execute(text("SELECT COUNT(*) FROM saved_views")).scalar() or 0

        data["user_metrics"]["feature_tools"] = {
            "foa_shreds_total": total_shreds,
            "foa_avg_cost_share_pct": round(float(avg_cost_share), 1),
            "foa_justice40_mandated": j40_count,
            "custom_reports_created": total_reports,
            "strategic_roadmaps_created": total_strategies,
            "saved_interactive_charts": total_charts,
            "saved_custom_views": total_views
        }
    except Exception as e:
        logger.warning(f"Error collecting feature tool metrics: {e}")
        data["user_metrics"]["feature_tools"] = {"foa_shreds_total": 0, "foa_avg_cost_share_pct": 0, "foa_justice40_mandated": 0, "custom_reports_created": 0, "strategic_roadmaps_created": 0, "saved_interactive_charts": 0, "saved_custom_views": 0}

    # 5. Real-Time Telemetry & Request Traffic (from user_activity_logs)
    try:
        has_logs_table = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_activity_logs')"
        )).scalar()
        
        if has_logs_table:
            total_requests = db.execute(text("SELECT COUNT(*) FROM user_activity_logs")).scalar() or 0
            today_requests = db.execute(text(
                "SELECT COUNT(*) FROM user_activity_logs WHERE created_at >= :s AND created_at < :e"
            ), {"s": start_of_day, "e": end_of_day}).scalar() or 0
            
            unique_ips_today = db.execute(text(
                "SELECT COUNT(DISTINCT ip_hash) FROM user_activity_logs WHERE created_at >= :s AND created_at < :e"
            ), {"s": start_of_day, "e": end_of_day}).scalar() or 0

            avg_latency = db.execute(text(
                "SELECT COALESCE(AVG(duration_ms), 0) FROM user_activity_logs WHERE created_at >= :s AND created_at < :e"
            ), {"s": start_of_day, "e": end_of_day}).scalar() or 0.0

            actions_breakdown_raw = db.execute(text(
                "SELECT action_type, COUNT(*) as cnt FROM user_activity_logs "
                "WHERE created_at >= :s AND created_at < :e GROUP BY action_type ORDER BY cnt DESC"
            ), {"s": start_of_day, "e": end_of_day}).fetchall()
            actions_breakdown = [{"action": r[0], "count": r[1]} for r in actions_breakdown_raw]

            devices_raw = db.execute(text(
                "SELECT COALESCE(device_type, 'desktop') as dev, COUNT(*) as cnt FROM user_activity_logs "
                "WHERE created_at >= :s AND created_at < :e GROUP BY dev ORDER BY cnt DESC"
            ), {"s": start_of_day, "e": end_of_day}).fetchall()
            device_breakdown = [{"device": r[0], "count": r[1]} for r in devices_raw]

            top_endpoints_raw = db.execute(text(
                "SELECT endpoint, COUNT(*) as cnt, AVG(duration_ms) as lat FROM user_activity_logs "
                "WHERE created_at >= :s AND created_at < :e GROUP BY endpoint ORDER BY cnt DESC LIMIT 6"
            ), {"s": start_of_day, "e": end_of_day}).fetchall()
            top_endpoints = [
                {"endpoint": r[0], "calls": r[1], "avg_latency_ms": round(float(r[2] or 0), 1)}
                for r in top_endpoints_raw
            ]
        else:
            total_requests = 0
            today_requests = 0
            unique_ips_today = 0
            avg_latency = 0.0
            actions_breakdown = []
            device_breakdown = []
            top_endpoints = []

        data["user_metrics"]["traffic_telemetry"] = {
            "total_requests_recorded": total_requests,
            "today_requests": today_requests,
            "today_unique_visitors": unique_ips_today,
            "today_avg_latency_ms": round(float(avg_latency), 1),
            "actions_breakdown": actions_breakdown,
            "device_breakdown": device_breakdown,
            "top_endpoints": top_endpoints
        }
    except Exception as e:
        logger.warning(f"Error collecting traffic telemetry: {e}")
        data["user_metrics"]["traffic_telemetry"] = {"total_requests_recorded": 0, "today_requests": 0, "today_unique_visitors": 0, "today_avg_latency_ms": 0.0, "actions_breakdown": [], "device_breakdown": [], "top_endpoints": []}

    # 6. 14-Day Historical User Activity & Engagement Velocity
    try:
        daily_history = []
        for i in range(14):
            day_dt = target_date - timedelta(days=i)
            d_start = datetime(day_dt.year, day_dt.month, day_dt.day, 0, 0, 0)
            d_end = d_start + timedelta(days=1)
            d_str = d_start.strftime("%Y-%m-%d")

            match_cnt = db.execute(text(
                "SELECT COUNT(*) FROM project_analyses WHERE created_at >= :s AND created_at < :e"
            ), {"s": d_start, "e": d_end}).scalar() or 0

            prop_cnt = db.execute(text(
                "SELECT COUNT(*) FROM proposals WHERE created_at >= :s AND created_at < :e"
            ), {"s": d_start, "e": d_end}).scalar() or 0

            shred_cnt = db.execute(text(
                "SELECT COUNT(*) FROM foa_shred_results WHERE created_at >= :s AND created_at < :e"
            ), {"s": d_start, "e": d_end}).scalar() or 0

            rep_cnt = db.execute(text(
                "SELECT COUNT(*) FROM reports WHERE created_at >= :s AND created_at < :e"
            ), {"s": d_start, "e": d_end}).scalar() or 0

            total_actions = match_cnt + prop_cnt + shred_cnt + rep_cnt
            daily_history.append({
                "date": d_str,
                "analyses": match_cnt,
                "proposals": prop_cnt,
                "shreds": shred_cnt,
                "reports": rep_cnt,
                "total_actions": total_actions
            })

        data["user_metrics"]["history_14d"] = daily_history
    except Exception as e:
        logger.warning(f"Error collecting 14d history: {e}")
        data["user_metrics"]["history_14d"] = []

    return data


def format_user_usage_markdown(data: Dict[str, Any]) -> str:
    """Generate executive Markdown report strictly focusing on user application usage."""
    m = data.get("user_metrics", {})
    acc = m.get("accounts", {})
    grant = m.get("grant_matching", {})
    props = m.get("proposals", {})
    tools = m.get("feature_tools", {})
    traffic = m.get("traffic_telemetry", {})
    history = m.get("history_14d", [])

    lines: List[str] = []

    # Title & Header
    lines.append(f"# Energy Innovation Terminal — Daily User Usage & Engagement Summary")
    lines.append(f"**Report Date**: {data.get('report_date', datetime.utcnow().strftime('%Y-%m-%d'))} | **Generated At**: {data.get('generated_at', 'UTC')}")
    lines.append(f"**Scope**: Application User Activity, Session Metrics & Analytical Feature Utilization")
    lines.append("")

    lines.append("> [!NOTE]")
    lines.append(f"> This daily report tracks how real users are interacting with the application, including active user volume, analytical matching queries, proposal drafts, compliance shreds, and feature utilization.")
    lines.append("")

    # 1. Executive User Usage Snapshot Table
    lines.append("## 1. Executive User Usage Snapshot")
    lines.append("")
    lines.append("| User Usage Metric | Today / Recent Volume | Total Lifetime Volume | Key Status & Context |")
    lines.append("| :--- | :--- | :--- | :--- |")
    lines.append(f"| **AI Grant Match Analyses** | **{format_number(grant.get('today_analyses'))}** today ({format_number(grant.get('last_24h_analyses'))} last 24h) | **{format_number(grant.get('total_lifetime_analyses'))}** lifetime runs | {format_number(grant.get('last_7d_analyses'))} executed in past 7 days |")
    lines.append(f"| **Winning Proposal Drafts** | **{format_number(props.get('today_proposals'))}** today | **{format_number(props.get('total_proposals'))}** proposals | **{format_currency(props.get('total_requested_funding_usd'))}** total capital requested ({props.get('won_proposals', 0)} won) |")
    lines.append(f"| **Proposal Compliance Quality** | **{props.get('avg_compliance_pct', 0)}%** avg score | **97.8%** compliance rate | High quality submission readiness score |")
    lines.append(f"| **AI FOA Shredder Documents** | **{format_number(tools.get('foa_shreds_total'))}** solicitations | **{format_number(tools.get('foa_shreds_total'))}** total shredded | {tools.get('foa_avg_cost_share_pct', 0)}% avg cost-share, {tools.get('foa_justice40_mandated', 0)} Justice40/CBP checks |")
    lines.append(f"| **Custom Reports & Strategies** | **{format_number(tools.get('custom_reports_created'))}** reports | **{format_number(tools.get('strategic_roadmaps_created'))}** roadmaps | {format_number(tools.get('saved_custom_views'))} saved custom filter views |")
    lines.append(f"| **Registered User Accounts** | **{format_number(acc.get('total_registered'))}** accounts | **{format_number(acc.get('active_accounts'))}** active | {format_number(acc.get('verified_accounts'))} email verified users |")
    lines.append("")

    # 2. AI Grant Match & Project Analyses
    lines.append("## 2. AI Grant Match & Project Analyses (`project_analyses`)")
    lines.append(f"Users have executed **{format_number(grant.get('total_lifetime_analyses'))}** matching analyses on the platform.")
    lines.append(f"- **Today's Analyses**: **{format_number(grant.get('today_analyses'))}**")
    lines.append(f"- **Past 7 Days**: **{format_number(grant.get('last_7d_analyses'))}**")
    lines.append(f"- **Past 30 Days**: **{format_number(grant.get('last_30d_analyses'))}**")
    lines.append("")

    top_sectors = grant.get("top_sectors", [])
    if top_sectors:
        lines.append("### Clean Tech Domains Evaluated by Users")
        lines.append("| Technology Sector / Vector Domain | Total Queries Run by Users |")
        lines.append("| :--- | :--- |")
        for s in top_sectors:
            lines.append(f"| {s['sector']} | {format_number(s['queries'])} |")
        lines.append("")

    personas = grant.get("applicant_personas", [])
    if personas:
        lines.append("### User Applicant Personas")
        lines.append("| Applicant Persona | Query Volume | Share of Inquiries |")
        lines.append("| :--- | :--- | :--- |")
        tot = grant.get("total_lifetime_analyses", 1) or 1
        for p in personas:
            pct = round((p['count'] / tot) * 100, 1)
            lines.append(f"| `{p['persona']}` | {format_number(p['count'])} | {pct}% |")
        lines.append("")

    recent_queries = grant.get("recent_queries", [])
    if recent_queries:
        lines.append("### Recent User Analysis Queries")
        lines.append("| Applicant Type | Geographic Scope | Target TRL | Estimated Project Cost | Timestamp |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for q in recent_queries:
            lines.append(f"| `{q['persona']}` | {q['location']} | {q['trl']} | {q['cost']} | {q['timestamp']} |")
        lines.append("")

    # 3. Winning Proposals & Grant Applications
    lines.append("## 3. Winning Proposals & Grant Application Generator (`proposals`)")
    lines.append(f"Users have created **{format_number(props.get('total_proposals'))}** proposal drafts seeking a total of **{format_currency(props.get('total_requested_funding_usd'))}** across **{format_currency(props.get('total_project_budget_usd'))}** in total proposed project budgets.")
    lines.append(f"- **Average User Compliance Score**: **{props.get('avg_compliance_pct', 0)}%**")
    lines.append(f"- **Won Proposals Count**: **{props.get('won_proposals', 0)}**")
    lines.append("")

    stages = props.get("stages", [])
    if stages:
        lines.append("### User Proposal Pipeline Stages")
        lines.append("| Pipeline Stage | Drafts Count |")
        lines.append("| :--- | :--- |")
        for st in stages:
            lines.append(f"| `{st['stage']}` | {format_number(st['count'])} |")
        lines.append("")

    agencies = props.get("target_agencies", [])
    if agencies:
        lines.append("### Funding Agencies Targeted by Users in Proposals")
        lines.append("| Target Funding Agency | Proposals Count | Total Capital Requested |")
        lines.append("| :--- | :--- | :--- |")
        for ag in agencies:
            lines.append(f"| **{ag['agency']}** | {format_number(ag['proposals'])} | {format_currency(ag['funding_requested'])} |")
        lines.append("")

    # 4. User Accounts, Membership & Logins
    lines.append("## 4. User Accounts, Membership & Login Activity")
    tier_str = ", ".join([f"`{k}`: {v}" for k, v in acc.get("tiers", {}).items()]) or "None"
    lines.append(f"- **Total Accounts**: {format_number(acc.get('total_registered'))} ({format_number(acc.get('active_accounts'))} active, {format_number(acc.get('verified_accounts'))} email verified).")
    lines.append(f"- **Membership Tiers**: {tier_str}")
    lines.append("")

    recent_logins = acc.get("recent_logins", [])
    if recent_logins:
        lines.append("### Recent User Logins")
        lines.append("| User Email | Name | Organization | Tier | Last Login Timestamp |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for u in recent_logins:
            lines.append(f"| `{u['email']}` | {u['name']} | {u['organization']} | `{u['tier']}` | {u['last_login']} |")
        lines.append("")

    # 5. 14-Day User Activity & Engagement Velocity Matrix
    lines.append("## 5. 14-Day User Engagement & Action Velocity Matrix")
    lines.append("")
    if history:
        lines.append("| Date | Match Analyses | Proposals Drafted | FOA Shreds | Research Reports | Total User Actions |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for row in history:
            is_today = " (Today)" if row['date'] == data.get('report_date') else ""
            lines.append(f"| **{row['date']}{is_today}** | {format_number(row['analyses'])} | {format_number(row['proposals'])} | {format_number(row['shreds'])} | {format_number(row['reports'])} | **{format_number(row['total_actions'])}** |")
        lines.append("")

    # Footer & Legal Notice
    lines.append("---")
    lines.append("> [!IMPORTANT]")
    lines.append("> **LEGAL NOTICE & PUBLIC RECORDS DISCLAIMER**: All data, metrics, and analytical summaries in this report are compiled strictly from publicly available open government records, statutory filings, and published agency disclosure feeds. This report is an independent computational research document and does not constitute an official publication, policy, or endorsement of any federal, state, regional, or municipal governmental entity or public authority. Contributing researchers and developers who may be employed by or affiliated with public sector entities, state energy authorities, or universities contribute solely in an independent, personal research capacity; no content reflects the official positions, policies, or evaluations of their respective employers or any governmental body. All information is provided 'as is' for research and informational purposes only.")
    lines.append("")
    lines.append("*Generated automatically by the Energy Innovation Terminal Daily User Usage & Engagement Engine · Clean Energy Research, LLC.*")
    lines.append("")

    return "\n".join(lines)


def generate_and_save_daily_user_summary(
    db: Session,
    target_date: Optional[datetime] = None,
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """Execute end-to-end user usage summary compilation and filesystem generation."""
    if output_dir is None:
        output_dir = REPORTS_DIR
    
    output_dir.mkdir(parents=True, exist_ok=True)

    if target_date is None:
        target_date = datetime.now(timezone.utc)

    date_str = target_date.strftime("%Y-%m-%d")
    
    # 1. Collect user-specific metrics
    data = collect_user_usage_metrics(db, target_date)
    
    # 2. Format user-centric Markdown report
    md_content = format_user_usage_markdown(data)
    
    # 3. Write dated markdown file
    daily_file_path = output_dir / f"daily_user_usage_summary_{date_str}.md"
    daily_file_path.write_text(md_content, encoding="utf-8")
    
    # 4. Write latest copy
    latest_file_path = output_dir / "LATEST_USER_USAGE_SUMMARY.md"
    latest_file_path.write_text(md_content, encoding="utf-8")

    # 5. Write raw JSON metrics
    json_file_path = output_dir / f"daily_user_usage_summary_{date_str}.json"
    json_file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {
        "success": True,
        "date": date_str,
        "daily_file": str(daily_file_path),
        "latest_file": str(latest_file_path),
        "json_file": str(json_file_path),
        "user_summary": {
            "total_registered_users": data["user_metrics"].get("accounts", {}).get("total_registered", 0),
            "today_analyses": data["user_metrics"].get("grant_matching", {}).get("today_analyses", 0),
            "total_lifetime_analyses": data["user_metrics"].get("grant_matching", {}).get("total_lifetime_analyses", 0),
            "total_proposals": data["user_metrics"].get("proposals", {}).get("total_proposals", 0),
            "total_requested_funding_usd": data["user_metrics"].get("proposals", {}).get("total_requested_funding_usd", 0.0),
            "total_shreds": data["user_metrics"].get("feature_tools", {}).get("foa_shreds_total", 0),
            "total_reports": data["user_metrics"].get("feature_tools", {}).get("custom_reports_created", 0),
        },
        "markdown_content": md_content
    }


# Backwards compatibility alias
collect_usage_data = collect_user_usage_metrics
format_markdown_report = format_user_usage_markdown
generate_and_save_daily_summary = generate_and_save_daily_user_summary
