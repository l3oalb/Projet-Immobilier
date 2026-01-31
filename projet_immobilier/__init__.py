"""
Projet Immobilier - Système d'analyse du marché immobilier français
"""

__version__ = "0.1.0"

# Exports principaux pour faciliter les imports
from .jina_web_scraper import get_latest_ads_content
from .extract_with_gen_ai import extract_with_ai
from .decision import verifier_opportunite
from .get_coord_API import get_coordinates
from .get_additionals_informations import get_environment_info

__all__ = [
    "get_latest_ads_content",
    "extract_with_ai",
    "verifier_opportunite",
    "get_coordinates",
    "get_environment_info",
]
