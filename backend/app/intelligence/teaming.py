"""
Canonical Consortia & Teaming Intelligence Module.

Leverages the 13,720 recipient entities and 34,974 verified PI contacts
to automatically assemble optimal multi-party consortia stacks for major solicitations.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.engine.teaming_engine import generate_teaming_stack

logger = logging.getLogger("CanonicalTeaming")


def assemble_consortium_stack(
    db: Session,
    opportunity_id: Optional[int] = None,
    technology_area: Optional[str] = None,
    state_scope: Optional[str] = None,
    lead_company_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Assembles a recommended multi-stakeholder teaming consortia for an opportunity or technology area.
    
    Returns structured recommendations across standard roles:
    - Tier-1 Academic Research Anchor (University lab with verified grant precedent)
    - Utility / Commercial Host Demonstration Partner
    - National Lab / Research Center Partner
    - Small Business Innovation Lead / Specialized Subcontractor
    Includes tailored outreach email copy and verified PI citations.
    """
    try:
        stack = generate_teaming_stack(
            db=db,
            opp_id=opportunity_id,
            technology_area=technology_area,
            state_scope=state_scope,
            lead_company_name=lead_company_name
        )
        if "consortia_roles" not in stack:
            stack["consortia_roles"] = stack.get("recommended_partners", [])
        return stack
    except Exception as e:
        logger.error(f"Error generating consortia stack: {e}")
        return {
            "opportunity_id": opportunity_id,
            "technology_area": technology_area or "Clean Energy",
            "consortia_roles": [
                {
                    "role_title": "Academic Research Anchor",
                    "recommended_partners": [],
                    "outreach_template": "Inquiry regarding potential teaming for Clean Energy solicitation."
                },
                {
                    "role_title": "Utility / Host Demonstration Partner",
                    "recommended_partners": [],
                    "outreach_template": "Host demonstration partnership inquiry."
                }
            ],
            "status": "partial_fallback",
            "message": str(e)
        }
