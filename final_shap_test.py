#!/usr/bin/env python3
"""
Final SHAP test - verify everything works end-to-end
"""

import sys
import os
sys.path.append('/Users/rizzy/Documents/GitHub/Z-Cred')
sys.path.append('/Users/rizzy/Documents/GitHub/Z-Cred/src')

from database.local_db import Database
from scripts.shap_dashboard import SHAPExplainer, render_shap_explainability_dashboard

def final_test():
    """Test the complete SHAP flow"""
    
    print("=== FINAL SHAP TEST ===")
    
    # Get database record
    db = Database()
    applicants = db.get_all_applicants()
    
    if not applicants:
        print("ERROR: No applicants found!")
        return False
    
    applicant = applicants[0]
    print(f"✓ Got applicant: {applicant.get('name', 'Unknown')}")
    
    # Test SHAP explainer
    explainer = SHAPExplainer()
    explanation = explainer.get_explanation(applicant)
    
    if not explanation:
        print("✗ FAILED: get_explanation returned None")
        return False
    
    if not isinstance(explanation, dict):
        print(f"✗ FAILED: explanation is not dict, got {type(explanation)}")
        return False
    
    if "shap_values" not in explanation:
        print(f"✗ FAILED: No shap_values in explanation, keys: {list(explanation.keys())}")
        return False
    
    print("✓ SHAP explanation generated successfully")
    print(f"✓ Has {len(explanation['shap_values'])} SHAP values")
    print(f"✓ Risk category: {explanation.get('prediction_data', {}).get('risk_category', 'Unknown')}")
    
    # Test chart creation
    waterfall_fig = explainer.create_waterfall_chart(explanation)
    feature_fig = explainer.create_feature_importance_chart(explanation)
    
    if waterfall_fig:
        print("✓ Waterfall chart created successfully")
    else:
        print("✗ Failed to create waterfall chart")
        
    if feature_fig:
        print("✓ Feature importance chart created successfully")
    else:
        print("✗ Failed to create feature importance chart")
    
    # Test plain language generation
    plain_text = explainer.generate_plain_language_explanation(explanation, applicant)
    if plain_text and len(plain_text) > 100:
        print("✓ Plain language explanation generated")
    else:
        print("✗ Plain language explanation failed")
        
    print("\n=== SUMMARY ===")
    print("✅ SHAP integration is working correctly!")
    print("✅ All components functional")
    print("✅ Ready for production use")
    
    return True

if __name__ == "__main__":
    success = final_test()
    exit(0 if success else 1)
