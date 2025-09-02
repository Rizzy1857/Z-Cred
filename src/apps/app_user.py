"""
Z-Score User Application - Gamified Credit Journey

User-focused Streamlit application with advanced gamification features
for building trust scores and credit readiness.
"""

import os
import random
import sys
import time

# Add project root to path for imports FIRST
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from src.core.auth import AuthManager
from src.database.local_db import Database
from src.models.model_integration import get_enhanced_trust_assessment
from src.models.model_pipeline import CreditRiskModel
from trust_score_utils import format_trust_display, get_unified_trust_scores

# Import SHAP dashboard for AI explanations
from scripts.shap_dashboard import show_ai_explanations

# Page configuration
st.set_page_config(
    page_title="Z-Score: Your Credit Journey",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Modern dark theme with perfect text contrast
st.markdown(
    """
<style>
    /* Modern Dark Theme - Complete Reset */
    :root {
        --primary: #6366f1;
        --secondary: #8b5cf6;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary: #334155;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --border: #475569;
        --shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    /* Global Application Styles */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%) !important;
        background-attachment: fixed !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    .main .block-container {
        padding: 2rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
        background: transparent !important;
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
    }

    h1 {
        font-size: 3rem !important;
        background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
    }

    p, span, div, label {
        color: var(--text-secondary) !important;
    }

    /* Mission Cards */
    .mission-card {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        padding: 1.5rem !important;
        border-radius: 16px !important;
        box-shadow: var(--shadow) !important;
        margin: 1rem 0 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .mission-card h3, .mission-card h4 {
        color: var(--text-primary) !important;
        margin-bottom: 0.5rem !important;
    }

    .mission-card p, .mission-card span {
        color: var(--text-secondary) !important;
    }

    .mission-card::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 4px !important;
        background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
    }

    .mission-card:hover {
        background: var(--bg-secondary) !important;
        transform: translateY(-4px) !important;
        box-shadow: 0 16px 48px rgba(99, 102, 241, 0.2) !important;
        border-color: var(--primary) !important;
    }

    .mission-completed {
        background: rgba(16, 185, 129, 0.1) !important;
        border-color: var(--success) !important;
    }

    .mission-completed::before {
        background: var(--success) !important;
    }

    /* Achievement Cards */
    .achievement-card {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        padding: 1.2rem !important;
        border-radius: 12px !important;
        box-shadow: var(--shadow) !important;
        margin: 0.8rem 0 !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
    }

    .achievement-card h4, .achievement-card h3 {
        color: #2d3748 !important;
        margin: 0.5rem 0 !important;
        font-weight: 700 !important;
    }

    .achievement-card p {
        color: #4a5568 !important;
        font-weight: 500 !important;
    }

    .achievement-card:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 12px 32px rgba(99, 102, 241, 0.2) !important;
        background: var(--bg-secondary) !important;
    }

    /* Analytics Cards */
    .analytics-card {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        padding: 2rem !important;
        border-radius: 20px !important;
        box-shadow: var(--shadow) !important;
        margin: 1.5rem 0 !important;
        transition: all 0.3s ease !important;
    }

    .analytics-card h2, .analytics-card h3 {
        color: var(--text-primary) !important;
    }

    .analytics-card p, .analytics-card span {
        color: var(--text-secondary) !important;
    }

    /* Metric Cards */
    .metric-container {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        padding: 1.5rem !important;
        border-radius: 16px !important;
        text-align: center !important;
        box-shadow: var(--shadow) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .metric-container::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 3px !important;
        background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
    }

    .metric-container:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px rgba(99, 102, 241, 0.2) !important;
        background: var(--bg-secondary) !important;
    }

    .metric-container h3 {
        color: var(--text-muted) !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    .metric-container h2 {
        color: var(--text-primary) !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        margin: 0.5rem 0 !important;
    }

    .metric-container p {
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        margin: 0 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 0.5rem 2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent), var(--primary)) !important;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.3) !important;
    }

    /* Form Elements */
    .stSelectbox, .stNumberInput, .stTextInput {
        background: var(--bg-tertiary) !important;
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
    }

    .stSelectbox > div > div {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
    }

    /* Enhanced Metrics */
    .stMetric {
        background: var(--bg-tertiary) !important;
        padding: 1rem !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        box-shadow: var(--shadow) !important;
        transition: all 0.3s ease !important;
    }

    .stMetric:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 24px rgba(99, 102, 241, 0.2) !important;
    }

    /* Progress Bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
        border-radius: 10px !important;
    }

    /* Sidebar */
    .css-1d391kg {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }

    /* Info Cards */
    .stAlert {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }

    /* Tables */
    .stDataFrame {
        background: var(--bg-tertiary) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
    }

    /* Mission difficulty indicators */
    .mission-easy { border-left: 4px solid var(--success) !important; }
    .mission-medium { border-left: 4px solid var(--warning) !important; }
    .mission-hard { border-left: 4px solid var(--error) !important; }

    /* Animation utilities */
    .fade-in {
        animation: fadeIn 0.6s ease-in !important;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px !important;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-secondary) !important;
        border-radius: 10px !important;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        border-radius: 10px !important;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--secondary), var(--accent)) !important;
    }

    /* Hide Streamlit elements */
    footer, #MainMenu, .stToolbar {
        visibility: hidden !important;
    }

    /* Mobile Responsive Enhancements */
    @media screen and (max-width: 768px) {
        .main .block-container {
            padding: 1rem !important;
            margin: 0.5rem !important;
        }

        h1 {
            font-size: 2rem !important;
            margin-bottom: 1rem !important;
        }

        .mission-card, .achievement-card, .metric-container, .analytics-card {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }

        .metric-container h2 {
            font-size: 1.5rem !important;
        }

        .stButton > button {
            width: 100% !important;
            margin: 0.5rem 0 !important;
        }

        /* Mobile-friendly columns */
        .stColumns > div {
            min-width: 100% !important;
            margin-bottom: 1rem !important;
        }

        /* Touch-friendly interactions */
        .mission-card:hover, .achievement-card:hover {
            transform: translateY(-2px) !important;
        }
    }

    @media screen and (max-width: 480px) {
        .main .block-container {
            padding: 0.5rem !important;
            margin: 0.25rem !important;
        }

        h1 {
            font-size: 1.5rem !important;
        }

        .mission-card, .achievement-card, .metric-container {
            padding: 0.75rem !important;
            border-radius: 8px !important;
        }

        .metric-container h2 {
            font-size: 1.25rem !important;
        }

        .metric-container h3 {
            font-size: 0.75rem !important;
        }
    }

    /* Progressive Web App enhancements */
    @media (display-mode: standalone) {
        .stApp {
            padding-top: env(safe-area-inset-top) !important;
            padding-bottom: env(safe-area-inset-bottom) !important;
        }
    }

    /* Mission Cards */
    .mission-card {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(102, 126, 234, 0.2) !important;
        padding: 1.5rem !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
        margin: 1rem 0 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
        color: #1a202c !important;
    }

    .mission-card * {
        color: #1a202c !important;
    }

    .mission-card h3, .mission-card h4, .mission-card p, .mission-card span, .mission-card div {
        color: #1a202c !important;
    }

    .mission-card::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 4px !important;
        background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
    }

    .mission-card:hover {
        background: rgba(255, 255, 255, 1) !important;
        transform: translateY(-4px) !important;
        box-shadow: 0 16px 48px rgba(102, 126, 234, 0.3) !important;
        border-color: var(--primary) !important;
    }

    .mission-completed {
        background: rgba(248, 255, 248, 0.95) !important;
        border-color: #48bb78 !important;
    }

    .mission-completed * {
        color: #1a202c !important;
    }

    .mission-completed::before {
        background: linear-gradient(90deg, var(--success), #38a169) !important;
    }

    /* Achievement Cards */
    .achievement-card {
        background: rgba(255, 255, 255, 0.98) !important;
        border: 2px solid rgba(102, 126, 234, 0.2) !important;
        padding: 1.2rem !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
        margin: 0.8rem 0 !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
        color: #1a202c !important;
    }

    .achievement-card * {
        color: #1a202c !important;
        font-weight: 500 !important;
    }

    .achievement-card h3, .achievement-card h4 {
        color: #2d3748 !important;
        font-weight: 700 !important;
    }

    .achievement-card p {
        color: #4a5568 !important;
        font-weight: 500 !important;
    }

    .achievement-card:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.3) !important;
        background: rgba(255, 255, 255, 1) !important;
    }

    /* Analytics Cards */
    .analytics-card {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(102, 126, 234, 0.2) !important;
        padding: 2rem !important;
        border-radius: 20px !important;
        backdrop-filter: blur(15px) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
        margin: 1.5rem 0 !important;
        transition: all 0.3s ease !important;
        color: #1a202c !important;
    }

    .analytics-card * {
        color: #1a202c !important;
    }

    /* Metric Cards */
    .metric-container {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(102, 126, 234, 0.2) !important;
        padding: 1.5rem !important;
        border-radius: 16px !important;
        text-align: center !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
        color: #1a202c !important;
    }

    .metric-container * {
        color: #1a202c !important;
    }

    .metric-container::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 3px !important;
        background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
    }

    .metric-container:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.3) !important;
        background: rgba(255, 255, 255, 1) !important;
    }

    .metric-container h3 {
        color: #1a202c !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    .metric-container h2 {
        color: #1a202c !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        margin: 0.5rem 0 !important;
    }

    .metric-container p {
        color: #1a202c !important;
        font-size: 0.8rem !important;
        opacity: 0.8 !important;
        margin: 0 !important;
    }

    /* Enhanced Metrics */
    .stMetric {
        background: var(--card) !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        border: 2px solid var(--border) !important;
        box-shadow: var(--shadow) !important;
        transition: all 0.3s ease !important;
    }

    .stMetric:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.3) !important;
    }

    /* Progress Bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
        border-radius: 10px !important;
    }

    .stProgress > div > div > div {
        background: rgba(128, 90, 213, 0.2) !important;
        border-radius: 10px !important;
    }

    /* Data Frames */
    .stDataFrame {
        background: var(--card) !important;
        border-radius: 12px !important;
        border: 2px solid var(--border) !important;
        overflow: hidden !important;
    }

    /* Sidebar */
    .css-1d391kg, .css-1cypcdb, .css-17eq0hr {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 2px solid var(--border) !important;
    }

    /* Tabs */
    .stTabs > div > div > div > div {
        background: var(--card) !important;
        border-radius: 12px !important;
        border: 2px solid var(--border) !important;
        color: var(--text) !important;
    }

    /* Status Colors */
    .status-success { color: var(--success) !important; }
    .status-warning { color: var(--warning) !important; }
    .status-danger { color: var(--danger) !important; }
    .status-primary { color: var(--primary) !important; }

    /* Animations */
    .pulse {
        animation: pulse 2s infinite !important;
    }

    .bounce {
        animation: bounce 1s infinite !important;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }

    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-5px); }
        60% { transform: translateY(-3px); }
    }

    footer, #MainMenu, .stToolbar { visibility: hidden !important; }

</style>
""",
    unsafe_allow_html=True,
)


class ZScoreUserApp:
    """User-focused application with enhanced gamification"""

    def __init__(self):
        self.auth = AuthManager()
        self.db = Database()
        self.model = CreditRiskModel()

        # Initialize session state for gamification
        if "user_level" not in st.session_state:
            st.session_state.user_level = 1
        if "z_credits" not in st.session_state:
            st.session_state.z_credits = 0
        if "completed_missions" not in st.session_state:
            st.session_state.completed_missions = set()
        if "achievements" not in st.session_state:
            st.session_state.achievements = []
        if "current_applicant" not in st.session_state:
            st.session_state.current_applicant = None

    def get_user_applicant_profile(self, user_id: int):
        """Get applicant profile for a user"""
        applicants = self.db.get_all_applicants()
        for applicant in applicants:
            if applicant.get("user_id") == user_id:
                return applicant
        return None

    def show_user_login_form(self):
        """Display user-specific login form with only user demo credentials"""
        # Clean welcome header
        st.markdown(
            """
        <div style="text-align: center; padding: 3rem 2rem;">
            <h1 style="font-size: 3rem; font-weight: 300; color: #2c3e50; margin-bottom: 1rem;">
                Z-Score User
            </h1>
            <h3 style="font-weight: 300; color: #7f8c8d; margin-bottom: 2rem;">
                Credit Building Journey
            </h3>
            <p style="font-size: 1.1rem; color: #95a5a6; max-width: 600px; margin: 0 auto 2rem;">
                Transform your financial future with gamified credit building missions.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Center login/signup options
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### Get Started")

            # Cleaner tabs
            tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

            with tab1:
                # Clean login form
                with st.form("login_form", clear_on_submit=False):
                    st.markdown("#### Welcome Back")

                    username = st.text_input(
                        "Username", placeholder="Enter your username"
                    )
                    password = st.text_input(
                        "Password", type="password", placeholder="Enter your password"
                    )

                    if st.form_submit_button("Sign In", use_container_width=True):
                        if username and password:
                            if self.auth.login(username, password):
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Invalid username or password")
                        else:
                            st.warning("Please enter both username and password")

                # Demo credentials - USER ONLY
                with st.expander("Demo Access"):
                    st.markdown(
                        """
                    **Demo User Login:**
                    Username: `demo_user`
                    Password: `user123`
                    Role: Credit Applicant

                    *Demo account for testing the credit building journey*
                    """
                    )

            with tab2:
                self.auth.show_signup_form()

    def require_user_auth(self):
        """Require authentication with user-specific login form"""
        if not self.auth.is_authenticated():
            self.show_user_login_form()
            return False
        return True

    def run(self):
        """Main application runner"""
        if not self.require_user_auth():
            return

        # Ensure only applicants can access
        current_user = self.auth.get_current_user()
        if not current_user or current_user["role"] != "applicant":
            st.error(
                "This is the user application. Please use the admin version for administrative access."
            )
            st.info("Contact your administrator for proper access.")
            return

        # Get user's applicant profile
        applicant = self.get_user_applicant_profile(current_user["id"])
        if not applicant:
            st.error("No applicant profile found. Please contact support.")
            return

        st.session_state.current_applicant = applicant

        # Check if profile is complete (needs real data, not placeholder)
        phone = applicant.get("phone", "")
        if not phone or phone.startswith("pending_") or not applicant.get("age"):
            self.show_profile_completion(applicant)
            return

        # Show main user interface
        self.show_user_interface(applicant)

    def show_profile_completion(self, applicant):
        """Gamified profile completion"""
        st.markdown(
            '<h1 class="game-header"> Welcome to Your Credit Journey!</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<h2 class="level-header">Level 1: Complete Your Profile</h2>',
            unsafe_allow_html=True,
        )

        # Progress indicator
        st.progress(0.1)
        st.markdown("**Quest Progress:** Profile Setup (10% Complete)")

        with st.form("profile_completion"):
            st.markdown("###  Your Character Sheet")

            col1, col2 = st.columns(2)

            with col1:
                phone = st.text_input(" Phone Number*", placeholder="+91-XXXXXXXXXX")
                age = st.number_input(" Age*", min_value=18, max_value=80, value=25)
                gender = st.selectbox(" Gender*", ["Male", "Female", "Other"])
                location = st.text_input(" Location*", placeholder="City, State")

            with col2:
                occupation = st.text_input(
                    " Occupation*", placeholder="Your profession"
                )
                monthly_income = st.number_input(
                    " Monthly Income (₹)*", min_value=0, value=15000
                )
                education = st.selectbox(
                    " Education",
                    ["High School", "Graduate", "Post Graduate", "Professional"],
                )
                marital_status = st.selectbox(
                    " Marital Status", ["Single", "Married", "Divorced", "Widowed"]
                )

            st.markdown("###  Your Credit Goals")
            credit_purpose = st.multiselect(
                "What's your mission?",
                [
                    "Business expansion ",
                    "Education ",
                    "Home improvement ",
                    "Medical expenses ",
                    "Vehicle purchase ",
                    "Working capital ",
                    "Emergency fund ",
                    "Other ",
                ],
            )

            submit_profile = st.form_submit_button(
                " Start My Credit Journey!", use_container_width=True
            )

            if submit_profile:
                if (
                    phone
                    and age
                    and gender
                    and location
                    and occupation
                    and monthly_income
                ):
                    # Update applicant profile using the new method
                    current_user = self.auth.get_current_user()
                    if current_user:
                        profile_data = {
                            'name': applicant.get('name', current_user['username']),  # Keep existing name or use username
                            'phone': phone,
                            'email': applicant.get('email'),
                            'age': age,
                            'gender': gender,
                            'location': location,
                            'occupation': occupation,
                            'monthly_income': monthly_income
                        }
                        
                        success = self.db.update_applicant_profile(current_user['id'], profile_data)
                        
                        if success:
                            # Award completion bonus
                            st.balloons()
                            st.success(" Profile Complete! +50 Z-Credits earned!")
                            if "z_credits" not in st.session_state:
                                st.session_state.z_credits = 0
                            st.session_state.z_credits += 50
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Failed to update profile. Please try again.")
                    else:
                        st.error("Authentication error. Please log in again.")
                else:
                    st.error(
                        "Please fill all required fields to continue your journey!"
                    )

    def show_user_interface(self, applicant):
        """Main user interface with enhanced gamification"""
        # Get unified trust scores for consistent display
        unified_scores = get_unified_trust_scores(applicant)
        display_data = format_trust_display(unified_scores)

        # Sidebar navigation
        with st.sidebar:
            st.markdown(f"###  Welcome, {applicant['name']}!")

            # User stats with unified scores
            st.markdown("####  Your Stats")
            st.metric(" Trust Score", f"{display_data['trust_percentage']:.1f}%")
            st.metric(
                " Level",
                f"{display_data['level']}/5 - {display_data['level_description']}",
            )
            st.metric(" Z-Credits", st.session_state.z_credits)

            # Navigation
            st.markdown("---")
            selected_tab = st.radio(
                "Navigation",
                [
                    " Dashboard",
                    " Trust Builder",
                    " Missions",
                    " Achievements",
                    " AI Insights",
                    " My Analytics",
                    " Profile",
                ],
                index=0,
                key="navigation_radio",
            )

            # Quick actions
            st.markdown("---")
            st.markdown("####  Quick Actions")
            if st.button(" Refresh Score", use_container_width=True):
                st.rerun()

            if st.button(" Logout", use_container_width=True):
                self.auth.logout()
                st.session_state.clear()
                st.rerun()

        # Main content based on selected tab
        if selected_tab == " Dashboard":
            self.show_dashboard(applicant)
        elif selected_tab == " Trust Builder":
            self.show_trust_builder(applicant)
        elif selected_tab == " Missions":
            self.show_missions(applicant)
        elif selected_tab == " Achievements":
            self.show_achievements(applicant)
        elif selected_tab == " AI Insights":
            self.show_ai_insights(applicant)
        elif selected_tab == " My Analytics":
            self.show_personal_analytics(applicant)
        elif selected_tab == " Profile":
            self.show_profile(applicant)

    def show_dashboard(self, applicant):
        """User dashboard with gamified elements"""
        st.markdown(
            '<h1 class="game-header"> Your Credit Journey Dashboard</h1>',
            unsafe_allow_html=True,
        )

        # Get unified trust scores for consistent display
        unified_scores = get_unified_trust_scores(applicant)
        display_data = format_trust_display(unified_scores)

        # Trust score overview with animation
        trust_percentage = display_data["trust_percentage"]
        level = display_data["level"]

        # Level progression
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown(
                f'<h2 class="level-header"> Level {level} - {display_data["level_description"]}</h2>',
                unsafe_allow_html=True,
            )

            # Animated progress bar
            progress_value = min(trust_percentage / 100, 1.0)
            st.progress(progress_value)

            if trust_percentage >= 70:
                st.success(" **CREDIT READY!** You can apply for loans!")
            else:
                next_milestone = (
                    ((level * 20) - trust_percentage)
                    if level * 20 > trust_percentage
                    else (20 - (trust_percentage % 20))
                )
                st.info(
                    f" Next milestone: {next_milestone:.1f}% to Level {level + 1}"
                )

        # Key metrics with enhanced cards
        st.markdown('<div style="margin: 2rem 0;">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
            <div class="metric-container">
                <h3> Trust Score</h3>
                <h2 style="color: var(--primary)">{trust_percentage:.1f}%</h2>
                <p>+{random.randint(1, 5)}% this week</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
            <div class="metric-container">
                <h3> Credit Level</h3>
                <h2 style="color: var(--success)">{level}/5</h2>
                <p>{"Level up available!" if trust_percentage >= level * 20 else f"Next: {((level * 20) - trust_percentage):.0f}% to go"}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
            <div class="metric-container">
                <h3> Z-Credits</h3>
                <h2 style="color: var(--accent)">{st.session_state.z_credits}</h2>
                <p>+{random.randint(10, 50)} earned today</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col4:
            completed_count = len(st.session_state.completed_missions)
            st.markdown(
                f"""
            <div class="metric-container">
                <h3> Missions</h3>
                <h2 style="color: var(--warning)">{completed_count}/8</h2>
                <p>{8 - completed_count} missions remaining</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Recent achievements with enhanced cards
        if st.session_state.achievements:
            st.markdown(
                '<h2 style="color: var(--primary); margin: 2rem 0 1rem 0;"> Recent Achievements</h2>',
                unsafe_allow_html=True,
            )

            achievement_cols = st.columns(
                min(len(st.session_state.achievements[-3:]), 3)
            )
            for i, achievement in enumerate(st.session_state.achievements[-3:]):
                with achievement_cols[i]:
                    st.markdown(
                        f"""
                    <div class="achievement-card" style="background: rgba(16, 185, 129, 0.1); border-color: #10b981; text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;"></div>
                        <h4 style="color: #f8fafc; margin: 0;">{achievement}</h4>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

        # Quick mission suggestions with enhanced cards
        st.markdown(
            '<h2 style="color: var(--primary); margin: 2rem 0 1rem 0;"> Recommended Next Steps</h2>',
            unsafe_allow_html=True,
        )

        suggestions = [
            (
                " Take Financial Quiz",
                "Boost Behavioral Trust by 15%",
                "quiz",
                "#48bb78",
            ),
            (
                " Verify Payment History",
                "Increase Social Trust by 20%",
                "payment",
                "#805ad5",
            ),
            (
                " Get Community Endorsement",
                "Enhance Social Trust by 25%",
                "social",
                "#ed8936",
            ),
            (
                " Connect Bank Account",
                "Maximize Digital Trust by 30%",
                "banking",
                "#9f7aea",
            ),
        ]

        suggestion_cols = st.columns(2)
        for i, (title, benefit, mission_type, color) in enumerate(suggestions[:2]):
            if mission_type not in st.session_state.completed_missions:
                with suggestion_cols[i]:
                    st.markdown(
                        f"""
                    <div class="mission-card" style="border-left: 4px solid {color};">
                        <h3 style="color: {color}; margin-bottom: 0.5rem;">{title}</h3>
                        <p style="color: #cbd5e1; margin-bottom: 1rem;">{benefit}</p>
                        <div style="background: rgba(99, 102, 241, 0.1); padding: 0.5rem 1rem; border-radius: 20px; text-align: center;">
                            <span style="color: #6366f1; font-weight: 600;"> Quick Win Available!</span>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        f"Start {title.split(' ')[1]} Mission",
                        key=f"start_{mission_type}",
                        use_container_width=True,
                        type="primary",
                    ):
                        st.session_state.selected_mission = mission_type
                        st.rerun()

        # Trust score breakdown
        self.show_trust_breakdown(applicant)

    def show_trust_builder(self, applicant):
        """Interactive trust score builder"""
        st.markdown(
            '<h1 class="game-header"> Trust Score Builder</h1>',
            unsafe_allow_html=True,
        )

        # Enhanced trust bar
        self.render_enhanced_trust_bar(applicant)

        # Component analysis
        st.markdown("###  Trust Components Deep Dive")

        tabs = st.tabs([" Behavioral", " Social", " Digital"])

        with tabs[0]:
            self.show_behavioral_analysis(applicant)

        with tabs[1]:
            self.show_social_analysis(applicant)

        with tabs[2]:
            self.show_digital_analysis(applicant)

    def show_missions(self, applicant):
        """Interactive missions with gamification"""
        st.markdown(
            '<h1 class="game-header"> Credit Building Missions</h1>',
            unsafe_allow_html=True,
        )

        # Mission categories
        mission_categories = {
            " Learning Missions": [
                {
                    "id": "quiz_basic",
                    "title": "Financial Basics Quiz",
                    "description": "Master the fundamentals of personal finance and credit",
                    "reward": "+15% Trust Score, 50 Z-Credits",
                    "difficulty": "Beginner",
                    "time": "10 minutes",
                    "type": "quiz",
                },
                {
                    "id": "quiz_advanced",
                    "title": "Advanced Credit Concepts",
                    "description": "Deep dive into credit scoring and financial planning",
                    "reward": "+20% Trust Score, 75 Z-Credits",
                    "difficulty": "Advanced",
                    "time": "15 minutes",
                    "type": "quiz",
                },
            ],
            " Verification Missions": [
                {
                    "id": "payment_history",
                    "title": "Payment History Verification",
                    "description": "Submit proof of consistent payment records",
                    "reward": "+20% Trust Score, 100 Z-Credits",
                    "difficulty": "Easy",
                    "time": "5 minutes",
                    "type": "upload",
                },
                {
                    "id": "income_verification",
                    "title": "Income Documentation",
                    "description": "Verify your income sources and stability",
                    "reward": "+25% Trust Score, 125 Z-Credits",
                    "difficulty": "Medium",
                    "time": "10 minutes",
                    "type": "upload",
                },
            ],
            " Social Missions": [
                {
                    "id": "community_endorsement",
                    "title": "Community Leader Endorsement",
                    "description": "Get endorsed by a recognized community member",
                    "reward": "+25% Trust Score, 150 Z-Credits",
                    "difficulty": "Medium",
                    "time": "1 day",
                    "type": "social",
                },
                {
                    "id": "peer_references",
                    "title": "Peer References",
                    "description": "Collect references from trusted community peers",
                    "reward": "+15% Trust Score, 100 Z-Credits",
                    "difficulty": "Easy",
                    "time": "30 minutes",
                    "type": "social",
                },
            ],
        }

        for category, missions in mission_categories.items():
            st.markdown(
                f'<h2 style="color: var(--primary); margin: 2rem 0 1rem 0;">{category}</h2>',
                unsafe_allow_html=True,
            )

            # Create grid layout for missions
            cols = st.columns(2)

            for i, mission in enumerate(missions):
                with cols[i % 2]:
                    # Determine mission status
                    is_completed = mission["id"] in st.session_state.completed_missions
                    card_class = (
                        "mission-card mission-completed"
                        if is_completed
                        else "mission-card"
                    )

                    # Difficulty color mapping
                    difficulty_colors = {
                        "Beginner": "#48bb78",
                        "Easy": "#38a169",
                        "Medium": "#ed8936",
                        "Advanced": "#e53e3e",
                        "Expert": "#9f1239",
                    }
                    diff_color = difficulty_colors.get(mission["difficulty"], "#64748b")

                    st.markdown(
                        f"""
                    <div class="{card_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <h3 style="margin: 0; color: var(--primary); font-size: 1.3rem;">
                                {"" if is_completed else ""} {mission['title']}
                            </h3>
                            <div style="background: {diff_color}; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                                {mission['difficulty']}
                            </div>
                        </div>

                        <p style="color: var(--text); margin-bottom: 1.5rem; line-height: 1.5;">
                            {mission['description']}
                        </p>

                        <div style="background: rgba(128, 90, 213, 0.1); border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span style="color: var(--primary); font-weight: 600;"> Reward:</span>
                                <span style="color: var(--text); font-weight: 500;">{mission['reward']}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: var(--primary); font-weight: 600;">⏱ Time:</span>
                                <span style="color: var(--text); font-weight: 500;">{mission['time']}</span>
                            </div>
                        </div>

                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="color: var(--text); font-size: 0.9rem;">
                                 Level {self.get_mission_level_requirement(mission)} Required
                            </div>
                            <div>
                                {" Mission Complete!" if is_completed else ""}
                            </div>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    # Action button
                    if is_completed:
                        st.success(" Mission Completed!", icon="")
                    else:
                        if st.button(
                            " Start Mission",
                            key=f"mission_{mission['id']}",
                            use_container_width=True,
                            type="primary",
                        ):
                            self.start_mission(mission, applicant)

                    st.markdown("<br>", unsafe_allow_html=True)

    def start_mission(self, mission, applicant):
        """Start a specific mission"""
        st.markdown(f"###  Starting: {mission['title']}")

        if mission["type"] == "quiz":
            self.show_quiz_mission(mission, applicant)
        elif mission["type"] == "upload":
            self.show_upload_mission(mission, applicant)
        elif mission["type"] == "social":
            self.show_social_mission(mission, applicant)

    def show_quiz_mission(self, mission, applicant):
        """Interactive quiz mission"""
        st.markdown('<div class="quiz-container">', unsafe_allow_html=True)

        # Sample quiz questions
        questions = [
            {
                "question": "What is a good credit utilization ratio?",
                "options": ["Above 90%", "30% or below", "50-70%", "It doesn't matter"],
                "correct": 1,
                "explanation": "Keeping credit utilization below 30% shows responsible credit management.",
            },
            {
                "question": "How often should you check your credit score?",
                "options": [
                    "Never",
                    "Once a year",
                    "Monthly",
                    "Only when applying for loans",
                ],
                "correct": 2,
                "explanation": "Regular monthly monitoring helps catch errors and track improvements.",
            },
            {
                "question": "What builds credit history fastest?",
                "options": [
                    "Multiple credit cards",
                    "Consistent on-time payments",
                    "High income",
                    "Expensive purchases",
                ],
                "correct": 1,
                "explanation": "Payment history is the most important factor in credit scoring.",
            },
        ]

        # Quiz interface
        correct_answers = 0

        for i, q in enumerate(questions):
            st.markdown(
                f'<div class="quiz-question">Question {i + 1}: {q["question"]}</div>',
                unsafe_allow_html=True,
            )

            answer = st.radio(
                "Select your answer:", q["options"], key=f"q_{i}_{mission['id']}"
            )

            if st.button(f"Submit Answer {i + 1}", key=f"submit_{i}_{mission['id']}"):
                if q["options"].index(answer) == q["correct"]:
                    st.success(f" Correct! {q['explanation']}")
                    correct_answers += 1
                else:
                    st.error(f" Incorrect. {q['explanation']}")

        # Quiz completion
        if st.button("Complete Quiz", key=f"complete_{mission['id']}"):
            score = (correct_answers / len(questions)) * 100

            if score >= 70:
                self.complete_mission(mission, applicant)
                st.success(f" Quiz Passed! Score: {score:.0f}%")
            else:
                st.warning(f" Study more! Score: {score:.0f}% (70% needed to pass)")

        st.markdown("</div>", unsafe_allow_html=True)

    def show_upload_mission(self, mission, applicant):
        """File upload mission"""
        st.markdown("###  Document Upload")

        uploaded_file = st.file_uploader(
            f"Upload documents for: {mission['title']}",
            type=["pdf", "jpg", "png", "jpeg"],
            help="Upload clear photos or scans of your documents",
        )

        if uploaded_file:
            st.success(" Document uploaded successfully!")

            if st.button("Verify & Complete Mission"):
                # Simulate verification process
                with st.spinner("Verifying document..."):
                    time.sleep(3)

                self.complete_mission(mission, applicant)
                st.success(" Document verified and mission completed!")

    def show_social_mission(self, mission, applicant):
        """Social verification mission"""
        st.markdown("###  Social Verification")

        with st.form(f"social_form_{mission['id']}"):
            st.markdown(f"**Mission:** {mission['title']}")

            if mission["id"] == "community_endorsement":
                endorser_name = st.text_input("Endorser Name*")
                endorser_role = st.text_input("Endorser Role/Position*")
                endorser_contact = st.text_input("Endorser Contact*")
                relationship = st.text_area("How do you know this person?*")

                submit = st.form_submit_button("Submit for Verification")

                if submit and all(
                    [endorser_name, endorser_role, endorser_contact, relationship]
                ):
                    with st.spinner("Submitting for verification..."):
                        time.sleep(2)

                    st.success(" Endorsement submitted! Verification pending.")
                    # For demo purposes, auto-complete after short delay
                    time.sleep(3)
                    self.complete_mission(mission, applicant)

            elif mission["id"] == "peer_references":
                ref1_name = st.text_input("Reference 1 Name*")
                ref1_contact = st.text_input("Reference 1 Contact*")
                ref2_name = st.text_input("Reference 2 Name*")
                ref2_contact = st.text_input("Reference 2 Contact*")

                submit = st.form_submit_button("Submit References")

                if submit and all([ref1_name, ref1_contact, ref2_name, ref2_contact]):
                    self.complete_mission(mission, applicant)

    def complete_mission(self, mission, applicant):
        """Complete a mission and award rewards"""
        # Add to completed missions
        st.session_state.completed_missions.add(mission["id"])

        # Award Z-Credits
        if "Z-Credits" in mission["reward"]:
            credits = int(mission["reward"].split(" ")[-2])
            st.session_state.z_credits += credits

        # Update trust score (simplified for demo)
        if "+15%" in mission["reward"]:
            trust_boost = 0.15
        elif "+20%" in mission["reward"]:
            trust_boost = 0.20
        elif "+25%" in mission["reward"]:
            trust_boost = 0.25
        else:
            trust_boost = 0.10

        # Update database
        current_trust = applicant.get("overall_trust_score", 0)
        new_trust = min(current_trust + trust_boost, 1.0)

        behavioral = applicant.get("behavioral_score", 0) + (trust_boost * 0.5)
        social = applicant.get("social_score", 0) + (trust_boost * 0.3)
        digital = applicant.get("digital_score", 0) + (trust_boost * 0.2)

        self.db.update_trust_score(applicant["id"], behavioral, social, digital)

        # Add achievement
        achievement = f" {mission['title']} Master"
        if achievement not in st.session_state.achievements:
            st.session_state.achievements.append(achievement)

        # Celebration
        st.balloons()
        st.success(f" Mission Completed! {mission['reward']}")

        # Check for level up
        new_level = min(int((new_trust * 100) // 20) + 1, 5)
        if new_level > st.session_state.user_level:
            st.session_state.user_level = new_level
            st.success(f" LEVEL UP! You're now Level {new_level}!")

        time.sleep(2)
        st.rerun()

    def show_achievements(self, applicant):
        """Display user achievements"""
        st.markdown(
            '<h1 class="game-header"> Your Achievements</h1>', unsafe_allow_html=True
        )

        # Achievement categories
        categories = {
            " Trust Building": [
                (
                    "Newcomer",
                    "Complete profile setup",
                    "profile" in st.session_state.completed_missions,
                ),
                (
                    "Trust Builder",
                    "Reach 30% trust score",
                    applicant.get("overall_trust_score", 0) >= 0.3,
                ),
                (
                    "Credit Ready",
                    "Reach 70% trust score",
                    applicant.get("overall_trust_score", 0) >= 0.7,
                ),
                (
                    "Trust Master",
                    "Reach 90% trust score",
                    applicant.get("overall_trust_score", 0) >= 0.9,
                ),
            ],
            " Mission Master": [
                (
                    "First Steps",
                    "Complete first mission",
                    len(st.session_state.completed_missions) >= 1,
                ),
                (
                    "Mission Runner",
                    "Complete 3 missions",
                    len(st.session_state.completed_missions) >= 3,
                ),
                (
                    "Mission Expert",
                    "Complete 5 missions",
                    len(st.session_state.completed_missions) >= 5,
                ),
                (
                    "Mission Legend",
                    "Complete all missions",
                    len(st.session_state.completed_missions) >= 8,
                ),
            ],
            " Credit Collector": [
                (
                    "First Earnings",
                    "Earn 50 Z-Credits",
                    st.session_state.z_credits >= 50,
                ),
                (
                    "Credit Builder",
                    "Earn 200 Z-Credits",
                    st.session_state.z_credits >= 200,
                ),
                (
                    "Credit Rich",
                    "Earn 500 Z-Credits",
                    st.session_state.z_credits >= 500,
                ),
                (
                    "Credit Millionaire",
                    "Earn 1000 Z-Credits",
                    st.session_state.z_credits >= 1000,
                ),
            ],
        }

        for category, achievements in categories.items():
            st.markdown(
                f'<h2 style="color: var(--primary); margin: 2rem 0 1rem 0;">{category}</h2>',
                unsafe_allow_html=True,
            )

            cols = st.columns(2)
            for i, (title, description, achieved) in enumerate(achievements):
                with cols[i % 2]:
                    if achieved:
                        # Achieved badge
                        st.markdown(
                            f"""
                        <div class="achievement-card" style="background: linear-gradient(145deg, rgba(72, 187, 120, 0.2), rgba(72, 187, 120, 0.1)); border-color: var(--success);">
                            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                                <div style="background: var(--success); color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-size: 1.5rem;">
                                    ✅
                                </div>
                                <div>
                                    <h3 style="margin: 0; color: #2d3748; font-size: 1.2rem; font-weight: 700;">{title}</h3>
                                    <p style="margin: 0; color: #4a5568; font-size: 0.9rem; font-weight: 500;">{description}</p>
                                </div>
                            </div>
                            <div style="background: rgba(72, 187, 120, 0.2); padding: 0.5rem 1rem; border-radius: 20px; text-align: center;">
                                <span style="color: #2d3748; font-weight: 700; font-size: 0.9rem;"> ACHIEVEMENT UNLOCKED!</span>
                            </div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
                    else:
                        # Locked badge
                        st.markdown(
                            f"""
                        <div class="achievement-card" style="opacity: 0.8; border-color: var(--border);">
                            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                                <div style="background: #64748b; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-size: 1.5rem;">
                                    🔒
                                </div>
                                <div>
                                    <h3 style="margin: 0; color: #2d3748; font-size: 1.2rem; font-weight: 600;">{title}</h3>
                                    <p style="margin: 0; color: #4a5568; font-size: 0.9rem; font-weight: 500;">{description}</p>
                                </div>
                            </div>
                            <div style="background: rgba(100, 116, 139, 0.15); padding: 0.5rem 1rem; border-radius: 20px; text-align: center;">
                                <span style="color: #2d3748; font-weight: 700; font-size: 0.9rem;"> KEEP WORKING!</span>
                            </div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                    st.markdown("<br>", unsafe_allow_html=True)

    def show_ai_insights(self, applicant):
        """AI explanations and insights"""
        st.markdown(
            '<h1 class="game-header"> AI Credit Insights</h1>', unsafe_allow_html=True
        )

        # Show SHAP explanations
        try:
            show_ai_explanations(applicant)
        except Exception as e:
            st.error(f"AI insights temporarily unavailable: {str(e)}")

            # Fallback insights with unified scoring
            unified_scores = get_unified_trust_scores(applicant)
            display_data = format_trust_display(unified_scores)

            st.markdown("###  Basic Credit Analysis")

            trust_percentage = display_data["trust_percentage"]

            if display_data["credit_eligible"]:
                st.success(
                    " **Credit Ready!** Your profile shows strong creditworthiness."
                )
            elif trust_percentage >= 50:
                st.info(" **Building Trust** - You're on the right track!")
            else:
                st.warning(
                    " **Early Stage** - Complete more missions to boost your score."
                )

            # Improvement suggestions
            st.markdown("###  Personalized Recommendations")

            suggestions = [
                "Complete financial literacy quizzes to demonstrate knowledge",
                "Verify payment history to show reliability",
                "Get community endorsements to build social trust",
                "Connect bank account for comprehensive analysis",
            ]

            for suggestion in suggestions:
                st.markdown(f"• {suggestion}")

    def show_profile(self, applicant):
        """User profile management"""
        st.markdown(
            '<h1 class="game-header"> Your Profile</h1>', unsafe_allow_html=True
        )

        # Profile overview
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("###  Profile Stats")
            st.metric(
                " Trust Score",
                f"{applicant.get('overall_trust_score', 0) * 100:.1f}%",
            )
            st.metric(
                " Level",
                f"{min(int((applicant.get('overall_trust_score', 0) * 100) // 20) + 1, 5)}/5",
            )
            st.metric(" Z-Credits", st.session_state.z_credits)
            st.metric(
                " Missions Completed", f"{len(st.session_state.completed_missions)}/8"
            )

        with col2:
            st.markdown("###  Personal Information")
            st.write(f"**Name:** {applicant.get('name', 'N/A')}")
            st.write(f"**Phone:** {applicant.get('phone', 'N/A')}")
            st.write(f"**Location:** {applicant.get('location', 'N/A')}")
            st.write(f"**Occupation:** {applicant.get('occupation', 'N/A')}")
            st.write(f"**Monthly Income:** ₹{applicant.get('monthly_income', 0):,}")

        # Edit profile
        st.markdown("---")
        if st.button(" Edit Profile"):
            self.show_profile_edit(applicant)

    def show_profile_edit(self, applicant):
        """Profile editing interface"""
        st.markdown("###  Edit Your Profile")

        with st.form("edit_profile"):
            phone = st.text_input("Phone", value=applicant.get("phone", ""))
            location = st.text_input("Location", value=applicant.get("location", ""))
            occupation = st.text_input(
                "Occupation", value=applicant.get("occupation", "")
            )
            monthly_income = st.number_input(
                "Monthly Income", value=applicant.get("monthly_income", 0)
            )

            if st.form_submit_button(" Save Changes"):
                # Update database
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        UPDATE applicants SET
                            phone = ?, location = ?, occupation = ?, monthly_income = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """,
                        (phone, location, occupation, monthly_income, applicant["id"]),
                    )

                    conn.commit()

                st.success(" Profile updated successfully!")
                time.sleep(1)
                st.rerun()

    def render_enhanced_trust_bar(self, applicant):
        """Enhanced animated trust bar with unified scoring"""
        # Get unified trust scores for consistency
        unified_scores = get_unified_trust_scores(applicant)
        display_data = format_trust_display(unified_scores)

        behavioral_score = display_data["behavioral_percentage"]
        social_score = display_data["social_percentage"]
        digital_score = display_data["digital_percentage"]
        overall_trust = display_data["trust_percentage"]

        # Enhanced trust bar display
        st.markdown('<div class="trust-bar-container">', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown(f"###  Overall Trust Score: {overall_trust:.1f}%")
            progress_value = min(overall_trust / 100, 1.0)
            st.progress(progress_value)

            if overall_trust >= 70:
                st.success(" **CREDIT ELIGIBLE** - Ready for loan applications!")
            else:
                needed = 70 - overall_trust
                st.info(f" **{needed:.1f}% more** needed for credit eligibility")

        # Component breakdown
        st.markdown("###  Trust Components")

        comp_col1, comp_col2, comp_col3 = st.columns(3)

        with comp_col1:
            st.metric(" Behavioral", f"{behavioral_score:.0f}%")
            st.progress(min(behavioral_score / 100, 1.0))

        with comp_col2:
            st.metric(" Social", f"{social_score:.0f}%")
            st.progress(min(social_score / 100, 1.0))

        with comp_col3:
            st.metric(" Digital", f"{digital_score:.0f}%")
            st.progress(min(digital_score / 100, 1.0))

        st.markdown("</div>", unsafe_allow_html=True)

    def show_trust_breakdown(self, applicant):
        """Detailed trust score breakdown"""
        st.markdown("###  Trust Score Breakdown")

        # Create visualization
        try:
            trust_result = get_enhanced_trust_assessment(applicant)

            behavioral = trust_result.get("behavioral_score", 0.5) * 100
            social = trust_result.get("social_score", 0.5) * 100
            digital = trust_result.get("digital_score", 0.5) * 100

            # Create pie chart
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=[" Behavioral", " Social", " Digital"],
                        values=[behavioral, social, digital],
                        hole=0.3,
                        marker_colors=["#FF6B6B", "#4ECDC4", "#45B7D1"],
                    )
                ]
            )

            fig.update_layout(
                title="Trust Score Components",
                showlegend=True,
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Visualization error: {str(e)}")

    def show_behavioral_analysis(self, applicant):
        """Behavioral trust analysis"""
        st.markdown("####  Behavioral Trust Analysis")

        behavioral_score = applicant.get("behavioral_score", 0) * 100

        factors = [
            ("Payment Consistency", 85, "Strong track record of timely payments"),
            ("Financial Discipline", 70, "Good budgeting and expense management"),
            ("Credit Usage", 60, "Moderate utilization of available credit"),
            ("Savings Behavior", 75, "Regular savings pattern observed"),
        ]

        for factor, score, description in factors:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**{factor}:** {description}")
                st.progress(score / 100)
            with col2:
                st.metric("Score", f"{score}%")

    def show_social_analysis(self, applicant):
        """Social trust analysis"""
        st.markdown("####  Social Trust Analysis")

        social_score = applicant.get("social_score", 0) * 100

        factors = [
            ("Community Standing", 80, "Active community member"),
            ("Professional Network", 65, "Good professional connections"),
            ("References", 70, "Positive peer references"),
            ("Social Verification", 75, "Verified social presence"),
        ]

        for factor, score, description in factors:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**{factor}:** {description}")
                st.progress(score / 100)
            with col2:
                st.metric("Score", f"{score}%")

    def show_digital_analysis(self, applicant):
        """Digital trust analysis"""
        st.markdown("####  Digital Trust Analysis")

        digital_score = applicant.get("digital_score", 0) * 100

        factors = [
            ("Digital Footprint", 70, "Established online presence"),
            ("Transaction History", 80, "Consistent digital transactions"),
            ("Account Security", 85, "Strong security practices"),
            ("Digital Engagement", 65, "Active digital participation"),
        ]

        for factor, score, description in factors:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**{factor}:** {description}")
                st.progress(score / 100)
            with col2:
                st.metric("Score", f"{score}%")

    def get_mission_level_requirement(self, mission):
        """Get level requirement for mission"""
        difficulty_levels = {
            "Beginner": 1,
            "Easy": 1,
            "Medium": 2,
            "Advanced": 3,
            "Expert": 4,
        }
        return difficulty_levels.get(mission.get("difficulty", "Beginner"), 1)

    def show_personal_analytics(self, applicant):
        """Personal analytics and insights dashboard"""
        st.markdown(
            '<h1 class="game-header"> Your Personal Analytics Hub</h1>',
            unsafe_allow_html=True,
        )

        # Get unified trust scores for consistency
        unified_scores = get_unified_trust_scores(applicant)
        display_data = format_trust_display(unified_scores)

        # Personal KPIs Overview
        with st.container():
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)

            trust_percentage = display_data["trust_percentage"]

            with col1:
                st.markdown(
                    """
                <div class="metric-container">
                    <h3> Progress This Month</h3>
                    <h2 style="color: var(--success)">+15.2%</h2>
                    <p>Credit score improvement</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col2:
                percentile = min(
                    95, max(5, trust_percentage + np.random.uniform(-10, 20))
                )
                st.markdown(
                    f"""
                <div class="metric-container">
                    <h3> Peer Ranking</h3>
                    <h2 style="color: var(--primary)">Top {100 - percentile:.0f}%</h2>
                    <p>Better than {percentile:.0f}% of users</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col3:
                streak = np.random.randint(5, 30)
                st.markdown(
                    f"""
                <div class="metric-container">
                    <h3> Active Streak</h3>
                    <h2 style="color: var(--warning)">{streak} days</h2>
                    <p>Consistent engagement</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col4:
                savings_rate = np.random.uniform(12, 25)
                st.markdown(
                    f"""
                <div class="metric-container">
                    <h3> Savings Rate</h3>
                    <h2 style="color: var(--accent)">{savings_rate:.1f}%</h2>
                    <p>Of monthly income</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Personal Analytics Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                " Progress Tracking",
                " Goal Achievement",
                " Behavioral Insights",
                " Performance Analysis",
                " Predictions & Tips",
            ]
        )

        with tab1:
            self.show_progress_tracking(applicant)

        with tab2:
            self.show_goal_achievement(applicant)

        with tab3:
            self.show_behavioral_insights(applicant)

        with tab4:
            self.show_performance_analysis(applicant)

        with tab5:
            self.show_predictions_tips(applicant)

    def show_progress_tracking(self, applicant):
        """Personal progress tracking analytics"""
        col1, col2 = st.columns(2)

        with col1:
            # Credit score progression
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
            scores = [620, 635, 648, 665, 682, 695, 708, 720]
            targets = [650, 660, 670, 680, 690, 700, 710, 720]

            fig_progress = go.Figure()

            fig_progress.add_trace(
                go.Scatter(
                    x=months,
                    y=scores,
                    mode="lines+markers",
                    name="Your Score",
                    line=dict(color="#10b981", width=4),
                    marker=dict(size=8),
                )
            )

            fig_progress.add_trace(
                go.Scatter(
                    x=months,
                    y=targets,
                    mode="lines",
                    name="Target Score",
                    line=dict(color="#8b5cf6", width=2, dash="dash"),
                )
            )

            fig_progress.update_layout(
                title=" Your Credit Score Journey",
                xaxis_title="Month",
                yaxis_title="Credit Score",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=400,
            )

            st.plotly_chart(fig_progress, use_container_width=True)

        with col2:
            # Personal milestones achieved
            milestones = [
                {"name": "First 600+", "date": "2024-02-15", "score": 605},
                {"name": "Reached 650", "date": "2024-04-20", "score": 652},
                {"name": "Hit 700!", "date": "2024-07-10", "score": 705},
                {"name": "Credit Ready", "date": "2024-08-25", "score": 720},
            ]

            st.markdown("###  Your Milestones")

            for milestone in milestones:
                with st.container():
                    col_icon, col_info = st.columns([1, 4])
                    with col_icon:
                        st.markdown("")
                    with col_info:
                        st.markdown(f"**{milestone['name']}**")
                        st.caption(f"{milestone['date']} • Score: {milestone['score']}")

        # Weekly progress breakdown
        st.markdown("###  Weekly Progress Breakdown")

        categories = [
            "Payment History",
            "Credit Utilization",
            "Account Age",
            "Credit Mix",
            "New Credit",
        ]
        current_week = [85, 72, 90, 65, 78]
        last_week = [80, 68, 88, 63, 75]

        fig_weekly = go.Figure()

        fig_weekly.add_trace(
            go.Bar(
                name="This Week",
                x=categories,
                y=current_week,
                marker_color="#10b981",
                opacity=0.8,
            )
        )

        fig_weekly.add_trace(
            go.Bar(
                name="Last Week",
                x=categories,
                y=last_week,
                marker_color="#64748b",
                opacity=0.6,
            )
        )

        fig_weekly.update_layout(
            title="Weekly Credit Factor Performance",
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=400,
        )

        st.plotly_chart(fig_weekly, use_container_width=True)

    def show_goal_achievement(self, applicant):
        """Goal tracking and achievement analytics"""
        st.markdown("###  Your Financial Goals")

        # Goal progress cards
        goals = [
            {
                "name": "Emergency Fund",
                "target": 10000,
                "current": 7500,
                "deadline": "2024-12-31",
                "icon": "",
            },
            {
                "name": "Credit Score 750+",
                "target": 750,
                "current": 720,
                "deadline": "2024-11-30",
                "icon": "",
            },
            {
                "name": "Debt Reduction",
                "target": 5000,
                "current": 3200,
                "deadline": "2025-03-31",
                "icon": "",
            },
        ]

        for goal in goals:
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])

                with col1:
                    st.markdown(f"<h2>{goal['icon']}</h2>", unsafe_allow_html=True)

                with col2:
                    progress = goal["current"] / goal["target"]
                    st.markdown(f"**{goal['name']}**")
                    st.progress(progress)

                    if goal["name"] == "Debt Reduction":
                        remaining = goal["target"] - goal["current"]
                        st.caption(
                            f"${remaining:,} reduced of ${goal['target']:,} target"
                        )
                    else:
                        st.caption(
                            f"${goal['current']:,} of ${goal['target']:,} target"
                        )

                with col3:
                    st.metric("Progress", f"{progress:.1%}")
                    days_left = np.random.randint(30, 120)
                    st.caption(f"{days_left} days left")

        # Goal achievement timeline
        col1, col2 = st.columns(2)

        with col1:
            # Monthly savings vs goal
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
            actual_savings = [800, 950, 750, 1200, 1100, 850, 1300, 1150]
            target_savings = [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]

            fig_savings = go.Figure()

            fig_savings.add_trace(
                go.Bar(
                    name="Actual Savings",
                    x=months,
                    y=actual_savings,
                    marker_color=[
                        "#10b981" if actual >= target else "#f59e0b"
                        for actual, target in zip(actual_savings, target_savings)
                    ],
                )
            )

            fig_savings.add_trace(
                go.Scatter(
                    name="Monthly Goal",
                    x=months,
                    y=target_savings,
                    mode="lines",
                    line=dict(color="#ef4444", width=3, dash="dash"),
                )
            )

            fig_savings.update_layout(
                title="Monthly Savings vs Goal",
                yaxis_title="Amount ($)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=400,
            )

            st.plotly_chart(fig_savings, use_container_width=True)

        with col2:
            # Goal completion forecast
            goal_names = ["Emergency Fund", "Credit Score", "Debt Reduction"]
            completion_probability = [85, 92, 73]

            fig_forecast = go.Figure(
                go.Bar(
                    x=goal_names,
                    y=completion_probability,
                    marker_color=[
                        "#10b981" if p > 80 else "#f59e0b" if p > 60 else "#ef4444"
                        for p in completion_probability
                    ],
                    text=[f"{p}%" for p in completion_probability],
                    textposition="auto",
                )
            )

            fig_forecast.update_layout(
                title="Goal Completion Probability",
                yaxis_title="Probability (%)",
                yaxis=dict(range=[0, 100]),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=400,
            )

            st.plotly_chart(fig_forecast, use_container_width=True)

    def show_behavioral_insights(self, applicant):
        """Behavioral pattern analysis"""
        st.markdown("###  Your Financial Behavior Insights")

        # Spending pattern analysis
        col1, col2 = st.columns(2)

        with col1:
            # Spending by category
            categories = [
                "Housing",
                "Food",
                "Transportation",
                "Entertainment",
                "Savings",
                "Other",
            ]
            amounts = [1200, 400, 300, 250, 1000, 200]

            fig_spending = go.Figure(
                data=[
                    go.Pie(
                        labels=categories,
                        values=amounts,
                        hole=0.4,
                        marker_colors=[
                            "#ef4444",
                            "#f59e0b",
                            "#10b981",
                            "#8b5cf6",
                            "#06b6d4",
                            "#64748b",
                        ],
                    )
                ]
            )

            fig_spending.update_layout(
                title="Monthly Spending Breakdown",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=400,
            )

            st.plotly_chart(fig_spending, use_container_width=True)

        with col2:
            # Financial habits score
            habits = [
                "Budgeting",
                "Regular Savings",
                "Bill Payment",
                "Investment",
                "Emergency Planning",
            ]
            scores = [85, 92, 98, 65, 78]

            fig_habits = go.Figure(
                go.Bar(
                    y=habits,
                    x=scores,
                    orientation="h",
                    marker_color=[
                        "#10b981" if s > 80 else "#f59e0b" if s > 60 else "#ef4444"
                        for s in scores
                    ],
                    text=[f"{s}%" for s in scores],
                    textposition="inside",
                )
            )

            fig_habits.update_layout(
                title="Financial Habits Assessment",
                xaxis_title="Score (%)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=400,
            )

            st.plotly_chart(fig_habits, use_container_width=True)

        # Behavioral insights cards
        st.markdown("###  Behavioral Insights")

        insights = [
            {
                "title": " Payment Timing",
                "insight": "You consistently pay bills 3-5 days early",
                "impact": "Excellent for credit score (+15 points)",
                "color": "success",
            },
            {
                "title": " Spending Pattern",
                "insight": "Weekend spending is 40% higher than weekdays",
                "impact": "Consider weekend budget limits",
                "color": "warning",
            },
            {
                "title": " Digital Behavior",
                "insight": "You check your credit score weekly",
                "impact": "Great monitoring habit (+10 points)",
                "color": "success",
            },
            {
                "title": " Goal Alignment",
                "insight": "Spending aligns well with stated goals",
                "impact": "On track for 85% goal completion",
                "color": "success",
            },
        ]

        col1, col2 = st.columns(2)

        for i, insight in enumerate(insights):
            with col1 if i % 2 == 0 else col2:
                if insight["color"] == "success":
                    st.success(
                        f"**{insight['title']}**\n\n{insight['insight']}\n\n*Impact: {insight['impact']}*"
                    )
                elif insight["color"] == "warning":
                    st.warning(
                        f"**{insight['title']}**\n\n{insight['insight']}\n\n*Suggestion: {insight['impact']}*"
                    )
                else:
                    st.info(
                        f"**{insight['title']}**\n\n{insight['insight']}\n\n*Note: {insight['impact']}*"
                    )

    def show_performance_analysis(self, applicant):
        """Performance analysis and comparisons"""
        st.markdown("###  Your Performance Analysis")

        # Performance vs peers
        col1, col2 = st.columns(2)

        with col1:
            # Peer comparison radar chart
            categories = [
                "Credit Score",
                "Savings Rate",
                "Payment History",
                "Debt Management",
                "Financial Goals",
            ]
            your_scores = [85, 78, 95, 72, 88]
            peer_average = [70, 65, 80, 68, 75]

            fig_radar = go.Figure()

            fig_radar.add_trace(
                go.Scatterpolar(
                    r=your_scores + [your_scores[0]],
                    theta=categories + [categories[0]],
                    fill="toself",
                    name="Your Performance",
                    line_color="#10b981",
                )
            )

            fig_radar.add_trace(
                go.Scatterpolar(
                    r=peer_average + [peer_average[0]],
                    theta=categories + [categories[0]],
                    fill="toself",
                    name="Peer Average",
                    line_color="#64748b",
                    opacity=0.6,
                )
            )

            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title="Performance vs Peers",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=400,
            )

            st.plotly_chart(fig_radar, use_container_width=True)

        with col2:
            # Monthly performance trends
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
            performance_score = [72, 75, 78, 82, 85, 83, 87, 89]

            fig_trend = go.Figure()

            fig_trend.add_trace(
                go.Scatter(
                    x=months,
                    y=performance_score,
                    mode="lines+markers",
                    name="Overall Performance",
                    line=dict(color="#3b82f6", width=3),
                    fill="tonexty",
                )
            )

            # Add trend line
            z = np.polyfit(range(len(months)), performance_score, 1)
            p = np.poly1d(z)
            fig_trend.add_trace(
                go.Scatter(
                    x=months,
                    y=p(range(len(months))),
                    mode="lines",
                    name="Trend",
                    line=dict(color="#f59e0b", width=2, dash="dash"),
                )
            )

            fig_trend.update_layout(
                title="Monthly Performance Trend",
                yaxis_title="Performance Score",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=400,
            )

            st.plotly_chart(fig_trend, use_container_width=True)

        # Performance achievements
        st.markdown("###  Recent Achievements")

        achievements = [
            {
                "icon": "",
                "title": "Credit Score Champion",
                "description": "Reached 720+ credit score",
                "date": "2024-08-25",
            },
            {
                "icon": "",
                "title": "Savings Streak",
                "description": "6 months of consistent savings",
                "date": "2024-08-20",
            },
            {
                "icon": "",
                "title": "Quick Payer",
                "description": "Never missed a payment this year",
                "date": "2024-08-15",
            },
            {
                "icon": "",
                "title": "Goal Crusher",
                "description": "Exceeded monthly savings goal 3x",
                "date": "2024-08-10",
            },
        ]

        col1, col2 = st.columns(2)

        for i, achievement in enumerate(achievements):
            with col1 if i % 2 == 0 else col2:
                with st.container():
                    col_icon, col_info = st.columns([1, 4])
                    with col_icon:
                        st.markdown(
                            f"<h2>{achievement['icon']}</h2>", unsafe_allow_html=True
                        )
                    with col_info:
                        st.markdown(f"**{achievement['title']}**")
                        st.write(achievement["description"])
                        st.caption(achievement["date"])

    def show_predictions_tips(self, applicant):
        """Predictive insights and personalized tips"""
        st.markdown("###  Your Financial Predictions & Tips")

        # Predictive insights
        col1, col2 = st.columns(2)

        with col1:
            # Credit score prediction
            months_ahead = ["Current", "1 Month", "3 Months", "6 Months", "12 Months"]
            predicted_scores = [720, 735, 748, 765, 780]
            confidence = [100, 85, 75, 65, 55]

            fig_prediction = go.Figure()

            fig_prediction.add_trace(
                go.Scatter(
                    x=months_ahead,
                    y=predicted_scores,
                    mode="lines+markers",
                    name="Predicted Score",
                    line=dict(color="#8b5cf6", width=3),
                    marker=dict(size=8),
                )
            )

            # Add confidence intervals
            upper_bound = [
                score + (10 * (1 - conf / 100))
                for score, conf in zip(predicted_scores, confidence)
            ]
            lower_bound = [
                score - (10 * (1 - conf / 100))
                for score, conf in zip(predicted_scores, confidence)
            ]

            fig_prediction.add_trace(
                go.Scatter(
                    x=months_ahead + months_ahead[::-1],
                    y=upper_bound + lower_bound[::-1],
                    fill="toself",
                    fillcolor="rgba(139, 92, 246, 0.2)",
                    line=dict(color="rgba(255,255,255,0)"),
                    name="Confidence Range",
                )
            )

            fig_prediction.update_layout(
                title="Credit Score Prediction",
                yaxis_title="Credit Score",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=400,
            )

            st.plotly_chart(fig_prediction, use_container_width=True)

        with col2:
            # Financial health forecast
            metrics = ["Credit Score", "Savings Rate", "Debt Ratio", "Emergency Fund"]
            current_status = [85, 78, 65, 72]
            six_month_forecast = [92, 85, 55, 88]

            fig_health = go.Figure()

            fig_health.add_trace(
                go.Bar(
                    name="Current",
                    x=metrics,
                    y=current_status,
                    marker_color="#06b6d4",
                    opacity=0.7,
                )
            )

            fig_health.add_trace(
                go.Bar(
                    name="6 Month Forecast",
                    x=metrics,
                    y=six_month_forecast,
                    marker_color="#10b981",
                    opacity=0.9,
                )
            )

            fig_health.update_layout(
                title="Financial Health Forecast",
                yaxis_title="Health Score (%)",
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=400,
            )

            st.plotly_chart(fig_health, use_container_width=True)

        # Personalized recommendations
        st.markdown("###  Personalized Recommendations")

        recommendations = [
            {
                "priority": " High Impact",
                "action": "Pay down credit card balance by $500",
                "benefit": "Could increase credit score by 15-20 points",
                "timeline": "1-2 months",
                "difficulty": "Medium",
            },
            {
                "priority": " Quick Win",
                "action": "Set up autopay for all bills",
                "benefit": "Ensure 100% on-time payment history",
                "timeline": "1 day",
                "difficulty": "Easy",
            },
            {
                "priority": " Long-term",
                "action": "Open a savings account for emergency fund",
                "benefit": "Build financial stability foundation",
                "timeline": "3-6 months",
                "difficulty": "Easy",
            },
            {
                "priority": " Strategic",
                "action": "Diversify credit mix with installment loan",
                "benefit": "Improve credit score by 5-10 points",
                "timeline": "6-12 months",
                "difficulty": "Hard",
            },
        ]

        for rec in recommendations:
            with st.expander(f"{rec['priority']} - {rec['action']}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"**Benefit:** {rec['benefit']}")

                with col2:
                    st.markdown(f"**Timeline:** {rec['timeline']}")

                with col3:
                    difficulty_color = {"Easy": "", "Medium": "", "Hard": ""}
                    st.markdown(
                        f"**Difficulty:** {difficulty_color[rec['difficulty']]} {rec['difficulty']}"
                    )

        # Weekly tip
        st.markdown("###  This Week's Pro Tip")
        st.info(
            """
        ** Smart Tip: Use the 'Debt Avalanche' Method**

        Focus on paying off your highest interest rate debt first while making minimum payments on others.
        This strategy can save you hundreds in interest and improve your credit score faster.

        *Your current highest rate: Credit Card at 18.9% APR*
        """
        )


def main():
    """Main application entry point"""
    app = ZScoreUserApp()
    app.run()


if __name__ == "__main__":
    main()
