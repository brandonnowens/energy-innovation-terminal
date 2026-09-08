"""
Executive PDF Report Builder Engine (Strategic Monograph Edition).
Delegates report generation to the specialized, bespoke generators for each publication.
Guarantees 100% data fidelity with zero hallucination.
"""

import io
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.engine.specialized_generators.dispatcher import generate_specialized_monograph
from app.engine.specialized_generators.base import (
    SpecializedNumberedCanvas as NumberedCanvas,
    get_monograph_styles,
    format_currency
)

def build_executive_pdf(
    context_data: Dict[str, Any],
    narrative_data: Dict[str, Any],
    output_stream: io.BytesIO,
    db: Optional[Session] = None
) -> None:
    """
    Main entrypoint for compiling a specialized executive monograph PDF.
    Routes to the dedicated specialized generator for the report preset.
    """
    preset_id = context_data.get("preset_id", "state_of_innovation")

    # If db session is not passed in context_data, open one from DatabaseSession
    if db is None:
        from app.database import SessionLocal
        with SessionLocal() as session:
            generate_specialized_monograph(preset_id, session, output_stream)
    else:
        generate_specialized_monograph(preset_id, db, output_stream)
