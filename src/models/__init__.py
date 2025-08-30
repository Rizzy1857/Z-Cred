"""
Machine Learning Models and Scoring

Model pipeline, trust scoring, SHAP explanations, and caching.
"""

from .model_integration import ModelIntegrator, model_integrator
from .model_pipeline import CreditRiskModel, TrustScoreCalculator, calculate_trust_score
from .shap_cache import SHAPCache
from .trust_score_utils import (
    clear_trust_score_cache,
    format_trust_display,
    get_cache_stats,
    get_unified_trust_scores,
)

__all__ = [
    "ModelIntegrator",
    "model_integrator",
    "calculate_trust_score",
    "CreditRiskModel",
    "TrustScoreCalculator",
    "get_unified_trust_scores",
    "format_trust_display",
    "clear_trust_score_cache",
    "get_cache_stats",
    "SHAPCache",
]
