"""Program repository for querying funding programs and portfolios."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc

from app.models.program import Program
from app.repositories.base import BaseRepository


class ProgramRepository(BaseRepository[Program]):
    """Repository for querying funding programs, portfolio thrusts, and multi-year initiatives."""

    def __init__(self, db: Session):
        super().__init__(Program, db)

    def search_programs(
        self,
        query_text: Optional[str] = None,
        program_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Program]:
        """Search innovation programs."""
        q = self.db.query(Program)

        if query_text and query_text.strip():
            term = f"%{query_text.strip()}%"
            q = q.filter(
                or_(
                    Program.name.ilike(term),
                    Program.description.ilike(term),
                )
            )

        if program_type and program_type.strip():
            q = q.filter(Program.program_type.ilike(f"%{program_type.strip()}%"))

        return q.order_by(Program.name.asc()).limit(limit).all()
