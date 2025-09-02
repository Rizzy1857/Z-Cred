#!/usr/bin/env python3
"""
Test SHAP in Streamlit context
"""

import sys
import os
sys.path.append('/Users/rizzy/Documents/GitHub/Z-Cred')
sys.path.append('/Users/rizzy/Documents/GitHub/Z-Cred/src')

import streamlit as st
from database.local_db import Database
from scripts.shap_dashboard import show_ai_explanations

def main():
    st.title("SHAP Debug Test")
    
    # Get database record
    db = Database()
    applicants = db.get_all_applicants()
    
    if not applicants:
        st.error("No applicants found!")
        return
        
    applicant = applicants[0]
    
    st.write("Testing show_ai_explanations with database record:")
    st.json(applicant)
    
    st.write("---")
    
    # Test the function that's causing issues
    show_ai_explanations(applicant)

if __name__ == "__main__":
    main()
