"""Database repository layer for clean, centralized data access."""

from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository providing standardized query methods."""

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: Any) -> Optional[T]:
        """Fetch a single record by primary key."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def count(self) -> int:
        """Return total row count."""
        return self.db.query(func.count(self.model.id)).scalar() or 0
