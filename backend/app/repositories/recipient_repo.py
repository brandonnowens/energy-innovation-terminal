"""Recipient repository for querying research institutions and corporate grant recipients."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc

from app.models.recipient import Recipient
from app.repositories.base import BaseRepository


class RecipientRepository(BaseRepository[Recipient]):
    """Repository for querying recipients, universities, labs, and clean tech startups."""

    def __init__(self, db: Session):
        super().__init__(Recipient, db)

    def search_recipients(
        self,
        query_text: Optional[str] = None,
        recipient_type: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 50,
    ) -> List[Recipient]:
        """Search grant recipients."""
        q = self.db.query(Recipient)

        if query_text and query_text.strip():
            term = f"%{query_text.strip()}%"
            q = q.filter(
                or_(
                    Recipient.name.ilike(term),
                    Recipient.description.ilike(term),
                    Recipient.city.ilike(term),
                )
            )

        if recipient_type and recipient_type.strip():
            q = q.filter(Recipient.recipient_type == recipient_type.strip())

        if state and state.strip():
            q = q.filter(Recipient.state.ilike(state.strip()))

        return q.order_by(desc(Recipient.total_funding_received)).limit(limit).all()

    def get_by_name(self, name: str) -> Optional[Recipient]:
        """Fetch recipient by exact or fuzzy name."""
        return self.db.query(Recipient).filter(Recipient.name.ilike(name.strip())).first()
