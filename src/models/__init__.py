"""
Machine Learning Models and Scoring

Model pipeline, trust scoring, SHAP explanations, and caching.
"""

from .model_integration import ModelIntegrator, model_integrator
from .model_pipeline import calculate_trust_score, CreditRiskModel, TrustScoreCalculator
from .trust_score_utils import get_unified_trust_scores, format_trust_display, clear_trust_score_cache, get_cache_stats
from .shap_cache import SHAPCache

__all__ = [
    'ModelIntegrator',
    'model_integrator', 
    'calculate_trust_score',
    'CreditRiskModel',
    'TrustScoreCalculator',
    'get_unified_trust_scores',
    'format_trust_display',
    'clear_trust_score_cache',
    'get_cache_stats',
    'SHAPCache'
]
