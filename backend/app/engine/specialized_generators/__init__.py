"""
Specialized Report Generators Package.
"""

from .dispatcher import GENERATORS_MAP, generate_specialized_monograph
from .base import SpecializedNumberedCanvas, get_monograph_styles, format_currency

__all__ = [
    "GENERATORS_MAP",
    "generate_specialized_monograph",
    "SpecializedNumberedCanvas",
    "get_monograph_styles",
    "format_currency"
]
