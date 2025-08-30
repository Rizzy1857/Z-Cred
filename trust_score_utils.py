"""
Trust Score Utilities - Unified scoring system for consistent display

Ensures consistent trust score calculation and display across the application.
Enhanced with caching for optimal performance.
"""

from src.models.model_pipeline import calculate_trust_score
from typing import Dict, Any
import hashlib
import json
import time

# Global cache for trust scores
_trust_score_cache = {}
_cache_timestamps = {}
_cache_ttl = 300  # 5 minutes TTL

def _get_cache_key(applicant_data: Dict[str, Any]) -> str:
    """Generate cache key from applicant data"""
    # Create a normalized version of the data for consistent caching
    cache_data = {
        'age': applicant_data.get('age', 25),
        'income': applicant_data.get('income', applicant_data.get('monthly_income', 30000)),
        'employment_length': applicant_data.get('employment_length', 2),
        'debt_to_income': applicant_data.get('debt_to_income', 0.3),
        'credit_utilization': applicant_data.get('credit_utilization', 0.4),
        'payment_history_score': applicant_data.get('payment_history_score', 80),
        'account_diversity': applicant_data.get('account_diversity', 2),
        'savings_rate': applicant_data.get('savings_rate', 0.15),
        'education_level': applicant_data.get('education_level', 'Bachelor')
    }
    
    # Create hash from normalized data
    data_str = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(data_str.encode()).hexdigest()

def _is_cache_valid(cache_key: str) -> bool:
    """Check if cache entry is still valid"""
    if cache_key not in _cache_timestamps:
        return False
    
    return (time.time() - _cache_timestamps[cache_key]) < _cache_ttl

def _get_cached_scores(cache_key: str) -> Dict[str, Any] | None:
    """Get scores from cache if valid"""
    if cache_key in _trust_score_cache and _is_cache_valid(cache_key):
        return _trust_score_cache[cache_key].copy()
    return None

def _cache_scores(cache_key: str, scores: Dict[str, Any]) -> None:
    """Cache the computed scores"""
    _trust_score_cache[cache_key] = scores.copy()
    _cache_timestamps[cache_key] = time.time()

def get_unified_trust_scores(applicant_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get unified trust scores with consistent calculation and caching
    
    Args:
        applicant_data: User/applicant data dictionary
        
    Returns:
        Dictionary with consistent trust scores and percentages
    """
    try:
        # Check cache first
        cache_key = _get_cache_key(applicant_data)
        cached_scores = _get_cached_scores(cache_key)
        
        if cached_scores is not None:
            return cached_scores
        
        # Prepare data for trust score calculation
        calc_data = {
            'age': applicant_data.get('age', 25),
            'income': applicant_data.get('income', applicant_data.get('monthly_income', 30000)),
            'employment_length': applicant_data.get('employment_length', 2),
            'debt_to_income': applicant_data.get('debt_to_income', 0.3),
            'credit_utilization': applicant_data.get('credit_utilization', 0.4),
            'payment_history_score': applicant_data.get('payment_history_score', 80),
            'account_diversity': applicant_data.get('account_diversity', 2),
            'savings_rate': applicant_data.get('savings_rate', 0.15),
            'education_level': applicant_data.get('education_level', 'Bachelor')
        }
        
        # Calculate trust scores using the actual ML pipeline
        trust_result = calculate_trust_score(calc_data)
        
        # Ensure consistent format
        unified_scores = {
            'behavioral_score': trust_result.get('behavioral_score', 0.5),
            'social_score': trust_result.get('social_score', 0.5),
            'digital_score': trust_result.get('digital_score', 0.5),
            'overall_trust_score': trust_result.get('overall_trust_score', 0.5),
            'trust_percentage': trust_result.get('trust_percentage', 50.0),
            'behavioral_percentage': trust_result.get('behavioral_score', 0.5) * 100,
            'social_percentage': trust_result.get('social_score', 0.5) * 100,
            'digital_percentage': trust_result.get('digital_score', 0.5) * 100
        }
        
        # Cache the results
        _cache_scores(cache_key, unified_scores)
        
        return unified_scores
        
    except Exception as e:
        print(f"Error in unified trust scoring: {e}")
        # Return fallback scores
        return {
            'behavioral_score': 0.5,
            'social_score': 0.5,
            'digital_score': 0.5,
            'overall_trust_score': 0.5,
            'trust_percentage': 50.0,
            'behavioral_percentage': 50.0,
            'social_percentage': 50.0,
            'digital_percentage': 50.0
        }

def clear_trust_score_cache():
    """Clear the trust score cache"""
    _trust_score_cache.clear()
    _cache_timestamps.clear()
    print("🗑️ Trust score cache cleared")

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    valid_entries = sum(1 for key in _trust_score_cache.keys() if _is_cache_valid(key))
    return {
        'total_entries': len(_trust_score_cache),
        'valid_entries': valid_entries,
        'cache_hit_ratio': valid_entries / max(len(_trust_score_cache), 1),
        'cache_ttl_seconds': _cache_ttl
    }

def get_trust_level(trust_percentage: float) -> int:
    """
    Get consistent trust level based on percentage
    
    Args:
        trust_percentage: Trust score as percentage (0-100)
        
    Returns:
        Trust level (1-5)
    """
    return min(int(trust_percentage // 20) + 1, 5)

def get_level_description(level: int) -> str:
    """
    Get description for trust level
    
    Args:
        level: Trust level (1-5)
        
    Returns:
        Level description
    """
    descriptions = {
        1: "Building Trust",
        2: "Growing Foundation", 
        3: "Steady Progress",
        4: "Strong Credit",
        5: "Credit Elite"
    }
    return descriptions.get(level, "Unknown Level")

def get_next_milestone(trust_percentage: float, current_level: int) -> float:
    """
    Calculate points needed for next milestone
    
    Args:
        trust_percentage: Current trust percentage
        current_level: Current trust level
        
    Returns:
        Points needed for next level
    """
    if current_level >= 5:
        return 0  # Already at max level
    
    next_level_threshold = current_level * 20
    return max(0, next_level_threshold - trust_percentage)

def format_trust_display(unified_scores: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format scores for consistent display
    
    Args:
        unified_scores: Unified trust scores dictionary
        
    Returns:
        Formatted display data
    """
    trust_percentage = unified_scores['trust_percentage']
    level = get_trust_level(trust_percentage)
    
    return {
        'trust_percentage': trust_percentage,
        'trust_score_decimal': unified_scores['overall_trust_score'],
        'level': level,
        'level_description': get_level_description(level),
        'next_milestone': get_next_milestone(trust_percentage, level),
        'behavioral_percentage': unified_scores['behavioral_percentage'],
        'social_percentage': unified_scores['social_percentage'],
        'digital_percentage': unified_scores['digital_percentage'],
        'credit_eligible': trust_percentage >= 70,
        'level_up_available': trust_percentage >= level * 20
    }
