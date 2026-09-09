"""Award repository for querying awards and precedents."""

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc

from app.models.award import Award
from app.repositories.base import BaseRepository


class AwardRepository(BaseRepository[Award]):
    """Repository for querying historical grant awards and recipient precedents."""

    def __init__(self, db: Session):
        super().__init__(Award, db)

    def search_awards(
        self,
        query: Optional[str] = None,
        query_text: Optional[str] = None,
        agency: Optional[str] = None,
        recipient_name: Optional[str] = None,
        state: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Award], int]:
        """Search grant awards with server-side pagination, returning (items, total)."""
        q = self.db.query(Award)

        search_term = query or query_text
        if search_term and search_term.strip():
            term = f"%{search_term.strip()}%"
            q = q.filter(
                or_(
                    Award.project_title.ilike(term),
                    Award.recipient_name.ilike(term),
                    Award.pi_name.ilike(term),
                    Award.project_abstract.ilike(term),
                )
            )

        if agency and agency.strip() and agency.lower() != "all":
            q = q.filter(Award.agency.ilike(f"%{agency.strip()}%"))

        if recipient_name and recipient_name.strip():
            q = q.filter(Award.recipient_name.ilike(f"%{recipient_name.strip()}%"))

        if state and state.strip() and state.lower() != "all":
            q = q.filter(Award.recipient_state.ilike(state.strip()))

        eff_min_year = min_year if min_year is not None else year_min
        if eff_min_year is not None:
            q = q.filter(Award.year >= eff_min_year)

        eff_max_year = max_year if max_year is not None else year_max
        if eff_max_year is not None:
            q = q.filter(Award.year <= eff_max_year)

        total = q.count()

        eff_offset = offset if offset is not None else ((page - 1) * page_size)
        eff_limit = limit if limit is not None else page_size

        items = (
            q.order_by(desc(Award.award_amount))
            .offset(eff_offset)
            .limit(eff_limit)
            .all()
        )

        return items, total

    def get_by_opportunity_id(self, opportunity_id: int, limit: int = 20) -> List[Award]:
        """Fetch awards associated with an opportunity."""
        return (
            self.db.query(Award)
            .filter(Award.opportunity_id == opportunity_id)
            .order_by(desc(Award.award_amount))
            .limit(limit)
            .all()
        )

    def get_by_solicitation_number(self, solicitation_number: str, limit: int = 20) -> List[Award]:
        """Fetch awards referencing a solicitation number."""
        clean = solicitation_number.strip()
        return (
            self.db.query(Award)
            .filter(
                or_(
                    Award.solicitation_number == clean,
                    Award.solicitation_number.ilike(f"%{clean}%")
                )
            )
            .order_by(desc(Award.award_amount))
            .limit(limit)
            .all()
        )
