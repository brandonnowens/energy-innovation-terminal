"""Opportunity repository for optimized data access."""

from typing import Optional, List, Dict, Any, Tuple, Union
from datetime import datetime
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, or_, and_, desc

from app.models.opportunity import Opportunity, OpportunityCategory, OpportunityRound, OpportunityContact, OpportunityDocument
from app.repositories.base import BaseRepository


class OpportunityRepository(BaseRepository[Opportunity]):
    """Repository for querying solicitations and funding opportunities."""

    def __init__(self, db: Session):
        super().__init__(Opportunity, db)

    def get_with_details(self, id: int) -> Optional[Opportunity]:
        """Fetch opportunity with loaded relationships."""
        return (
            self.db.query(Opportunity)
            .options(
                selectinload(Opportunity.rounds),
                selectinload(Opportunity.contacts),
                selectinload(Opportunity.documents),
                selectinload(Opportunity.categories),
                selectinload(Opportunity.restrictions),
            )
            .filter(Opportunity.id == id)
            .first()
        )

    def get_by_id_eager(self, id: int) -> Optional[Opportunity]:
        """Alias for get_with_details."""
        return self.get_with_details(id)

    def get_by_solicitation_number(self, sol_num: str) -> Optional[Opportunity]:
        """Fetch opportunity by its solicitation/funding number."""
        clean = sol_num.strip()
        return (
            self.db.query(Opportunity)
            .filter(
                or_(
                    Opportunity.solicitation_number == clean,
                    Opportunity.solicitation_number.ilike(f"%{clean}%")
                )
            )
            .first()
        )

    def search_opportunities(
        self,
        query: Optional[str] = None,
        query_text: Optional[str] = None,
        agency: Optional[str] = None,
        technology: Optional[str] = None,
        sector: Optional[str] = None,
        status: Optional[str] = None,
        min_funding: Optional[float] = None,
        max_funding: Optional[float] = None,
        is_historical: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Opportunity], int]:
        """Search and filter opportunities, returning (items, total)."""
        q = self.db.query(Opportunity)

        search_term = query or query_text
        if search_term and search_term.strip():
            term = f"%{search_term.strip()}%"
            q = q.filter(
                or_(
                    Opportunity.name.ilike(term),
                    Opportunity.solicitation_number.ilike(term),
                    Opportunity.description.ilike(term),
                    Opportunity.short_description.ilike(term),
                    Opportunity.agency.ilike(term),
                )
            )

        if agency and agency.strip() and agency.lower() != "all":
            q = q.filter(Opportunity.agency.ilike(f"%{agency.strip()}%"))

        if status and status.strip() and status.lower() != "all":
            q = q.filter(Opportunity.status == status.strip())

        if min_funding is not None:
            q = q.filter(Opportunity.total_funding >= min_funding)

        if max_funding is not None:
            q = q.filter(Opportunity.total_funding <= max_funding)

        if is_historical is not None:
            q = q.filter(Opportunity.is_historical == is_historical)

        if technology and technology.strip() and technology.lower() != "all":
            tech_term = f"%{technology.strip()}%"
            q = q.join(OpportunityCategory, Opportunity.id == OpportunityCategory.opportunity_id).filter(
                OpportunityCategory.category_type == "technology",
                OpportunityCategory.category_value.ilike(tech_term)
            )

        total = q.count()

        eff_offset = offset if offset is not None else ((page - 1) * page_size)
        eff_limit = limit if limit is not None else page_size

        items = (
            q.order_by(desc(Opportunity.id))
            .offset(eff_offset)
            .limit(eff_limit)
            .all()
        )

        return items, total

    def get_recent_opportunities(self, limit: int = 20) -> List[Opportunity]:
        """Fetch recently added or verified opportunities."""
        return (
            self.db.query(Opportunity)
            .order_by(desc(Opportunity.id))
            .limit(limit)
            .all()
        )
