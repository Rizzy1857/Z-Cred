#!/usr/bin/env python3
"""
Debug SHAP data flow - inspect actual database record vs. expected format
"""

import sys
import os
sys.path.append('/Users/rizzy/Documents/GitHub/Z-Cred')
sys.path.append('/Users/rizzy/Documents/GitHub/Z-Cred/src')

from database.local_db import Database
from scripts.shap_dashboard import SHAPExplainer
import json

def debug_data_flow():
    """Debug the complete data flow from database to SHAP"""
    
    # Initialize database
    db = Database()
    
    # Get actual applicant data from database
    applicants = db.get_all_applicants()
    
    if not applicants:
        print("No applicants found in database!")
        return
    
    # Use first applicant
    applicant = applicants[0]
    
    print("=== DATABASE RECORD ===")
    print("Raw applicant data from database:")
    for key, value in applicant.items():
        print(f"  {key}: {value} ({type(value)})")
    
    print("\n=== SHAP EXPLAINER TEST ===")
    
    # Initialize SHAP explainer
    shap_explainer = SHAPExplainer()
    
    # Test SHAP explanation
    try:
        result = shap_explainer.get_explanation(applicant)
        print(f"SHAP Result: {result}")
        print("Type:", type(result))
        if isinstance(result, dict):
            print("Keys:", list(result.keys()))
    except Exception as e:
        print(f"SHAP Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== DATA PREPARATION TEST ===")
    
    # Test the _prepare_applicant_data method directly
    try:
        prepared_data = shap_explainer._prepare_applicant_data(applicant)
        print(f"Prepared data: {prepared_data}")
        print("Type:", type(prepared_data))
        if isinstance(prepared_data, dict):
            print("Keys:", list(prepared_data.keys()))
            for key, value in prepared_data.items():
                print(f"  {key}: {value} ({type(value)})")
    except Exception as e:
        print(f"Data preparation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_data_flow()
