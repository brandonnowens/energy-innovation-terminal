"""Base adapter class for data ingestion."""

import hashlib
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class BaseAdapter(ABC):
    """Base class for all ingestion adapters."""

    source_name: str = "unknown"
    source_url: str = ""
    source_type: str = "api"
    authority_rank: int = 5

    def __init__(self):
        self._client: Optional[httpx.Client] = None
        self._last_request_time: float = 0

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=30.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "NYSERDA-Innovation-Navigator/1.0 (Public Data Research Tool)"
                },
            )
        return self._client

    def _rate_limit(self):
        """Respect rate limits between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < settings.request_delay_seconds:
            time.sleep(settings.request_delay_seconds - elapsed)
        self._last_request_time = time.time()

    def fetch_url(self, url: str, **kwargs) -> httpx.Response:
        """Fetch a URL with rate limiting."""
        self._rate_limit()
        logger.info(f"[{self.source_name}] Fetching: {url}")
        response = self.client.get(url, **kwargs)
        response.raise_for_status()
        return response

    def fetch_json(self, url: str, **kwargs) -> dict | list:
        """Fetch JSON from a URL."""
        response = self.fetch_url(url, **kwargs)
        return response.json()

    @staticmethod
    def compute_hash(content: str | bytes) -> str:
        """Compute SHA-256 hash of content."""
        if isinstance(content, str):
            content = content.encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)

    @abstractmethod
    def ingest(self, db) -> dict:
        """Run ingestion. Returns stats dict with keys: added, updated, unchanged, errors."""
        ...

    def close(self):
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
