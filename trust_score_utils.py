"""
Trust Score Utilities - Unified scoring system for consistent display

Ensures consistent trust score calculation and display across the application.
"""

from model_pipeline import calculate_trust_score
from typing import Dict, Any

def get_unified_trust_scores(applicant_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get unified trust scores with consistent calculation
    
    Args:
        applicant_data: User/applicant data dictionary
        
    Returns:
        Dictionary with consistent trust scores and percentages
    """
    try:
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
        
        return unified_scores
        
    except Exception as e:
        print(f"Error in trust score calculation: {e}")
        # Fallback to stored values or defaults
        return {
            'behavioral_score': applicant_data.get('behavioral_score', 0.5),
            'social_score': applicant_data.get('social_score', 0.5),
            'digital_score': applicant_data.get('digital_score', 0.5),
            'overall_trust_score': applicant_data.get('overall_trust_score', 0.5),
            'trust_percentage': applicant_data.get('overall_trust_score', 0.5) * 100,
            'behavioral_percentage': applicant_data.get('behavioral_score', 0.5) * 100,
            'social_percentage': applicant_data.get('social_score', 0.5) * 100,
            'digital_percentage': applicant_data.get('digital_score', 0.5) * 100
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
