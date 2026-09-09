"""Organization repository for querying funding organizations and utilities."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc

from app.models.organization import Organization
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Repository for querying funding agencies, electric utilities, and climate foundations."""

    def __init__(self, db: Session):
        super().__init__(Organization, db)

    def search_organizations(
        self,
        query_text: Optional[str] = None,
        org_type: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 100,
    ) -> List[Organization]:
        """Search funding organizations with filters."""
        q = self.db.query(Organization)

        if query_text and query_text.strip():
            term = f"%{query_text.strip()}%"
            q = q.filter(
                or_(
                    Organization.name.ilike(term),
                    Organization.acronym.ilike(term),
                    Organization.description.ilike(term),
                )
            )

        if org_type and org_type.strip():
            q = q.filter(Organization.org_type == org_type.strip())

        if state and state.strip():
            q = q.filter(Organization.state.ilike(state.strip()))

        return q.order_by(Organization.name.asc()).limit(limit).all()

    def get_by_name_or_code(self, identifier: str) -> Optional[Organization]:
        """Fetch organization by name, code, or acronym."""
        clean = identifier.strip()
        return (
            self.db.query(Organization)
            .filter(
                or_(
                    Organization.name.ilike(clean),
                    Organization.acronym.ilike(clean),
                    Organization.code.ilike(clean) if hasattr(Organization, "code") else False,
                )
            )
            .first()
        )
