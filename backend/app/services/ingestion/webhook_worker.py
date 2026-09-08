import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.services.ingestion.base_worker import BaseWorker

logger = logging.getLogger("WebhookWorker")


class WebhookWorker(BaseWorker):
    """Worker that processes inbound webhook JSON payloads.

    The payload is expected to conform to the same structure used by the
    regular ingestion pipeline (opportunity, award, organization, etc.).
    This worker simply forwards the payload to the existing recovery/orchestrator
    logic by calling ``process_payload`` which can be expanded later.
    """

    source_name = "Webhook"
    agency_name = "external"
    jurisdiction = "global"

    def __init__(self):
        # No long‑running background activity – workers are triggered via API.
        pass

    def process_payload(self, payload: Dict[str, Any], db: Session) -> None:
        """Validate and ingest a single webhook payload.

        For now we store the raw payload in ``source_snapshots`` for provenance
        and then delegate to the existing recovery orchestration functions if
        needed. This keeps the implementation lightweight while preserving the
        additive provenance model.
        """
        try:
            # Store raw payload for auditability
            db.execute(
                "INSERT INTO source_snapshots (source_url, content_hash, raw_payload_text, captured_at) "
                "VALUES (:url, md5(:payload::text), :payload, NOW()) ON CONFLICT DO NOTHING",
                {"url": payload.get("source_url", "webhook"), "payload": str(payload)}
            )
            db.commit()
            logger.info("Webhook payload stored for source %s", payload.get("source_url"))
            # TODO: integrate with recovery_orchestrator for detailed parsing
        except Exception as e:
            logger.error("Failed to process webhook payload: %s", e)
            raise

    def run_sync(self, db: Session) -> Dict[str, Any]:
        """Placeholder for compatibility with the orchestrator's ``run_sync``.

        Webhook workers are normally invoked via the API, so this returns a no‑op
        result indicating success.
        """
        return {"source": "webhook", "inserted": 0, "updated": 0, "alerts_dispatched": 0}
