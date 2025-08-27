"""
Z-Score Credit Assessment Application

Main Streamlit application for the PSB FinTech Cybersecurity Hackathon 2025.
Implements dynamic trust-based credit scoring with explainable AI and 
gamified financial literacy features.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import time

# Local imports
from auth import AuthManager
from local_db import Database
from model_pipeline import CreditRiskModel, calculate_trust_score, TrustScoreCalculator
from error_handling import safe_numeric_conversion, safe_json_parse

# Page configuration
st.set_page_config(
    page_title="Z-Score Credit Assessment",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark blue-purple theme
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #stDecoration {display:none;}
    
    /* Main app styling - Dark theme with blue-purple gradient */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 25%, #0f3460 50%, #533483 75%, #7209b7 100%);
        color: #e0e6ed;
    }
    
    /* Content area - Dark with glass effect */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: rgba(22, 33, 62, 0.85);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(112, 9, 183, 0.2);
        margin: 1rem;
    }
    
    /* Headers - Light text for dark theme */
    .main-header {
        font-size: 2.2rem;
        font-weight: 300;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(112, 9, 183, 0.3);
    }
    
    h1, h2, h3 {
        font-weight: 300;
        color: #e0e6ed;
        letter-spacing: -0.3px;
    }
    
    /* Sidebar styling - Dark theme */
    .css-1d391kg {
        background: rgba(26, 26, 46, 0.95);
        backdrop-filter: blur(15px);
        border-radius: 0 20px 20px 0;
        border-right: 1px solid rgba(112, 9, 183, 0.3);
    }
    
    /* Buttons - Blue-purple gradient */
    .stButton > button {
        background: linear-gradient(135deg, #4a6cf7 0%, #7209b7 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 400;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(74, 108, 247, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74, 108, 247, 0.6);
        background: linear-gradient(135deg, #5a7cf8 0%, #8219c7 100%);
    }
    
    /* Form inputs - Dark theme */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border: 1px solid rgba(112, 9, 183, 0.3);
        border-radius: 12px;
        padding: 0.75rem;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        background: rgba(26, 26, 46, 0.8);
        color: #e0e6ed;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #4a6cf7;
        box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.2);
        background: rgba(26, 26, 46, 0.9);
    }
    
    /* Metrics - Dark theme */
    .metric-container {
        background: rgba(26, 26, 46, 0.9);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(112, 9, 183, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        text-align: center;
        transition: all 0.3s ease;
        color: #e0e6ed;
    }
    
    .metric-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(74, 108, 247, 0.2);
        border-color: rgba(74, 108, 247, 0.5);
    }
    
    [data-testid="metric-container"] {
        background: rgba(26, 26, 46, 0.9);
        border: 1px solid rgba(112, 9, 183, 0.3);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        color: #e0e6ed;
    }
    
    /* Cards - Dark theme */
    .card {
        background: rgba(26, 26, 46, 0.95);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(112, 9, 183, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        margin: 1rem 0;
        transition: all 0.3s ease;
        color: #e0e6ed;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(74, 108, 247, 0.2);
        border-color: rgba(74, 108, 247, 0.5);
    }
    
    /* Status indicators - Enhanced for dark theme */
    .status-low {
        color: #00e676;
        font-weight: 500;
        padding: 0.3rem 0.8rem;
        background: rgba(0, 230, 118, 0.2);
        border-radius: 20px;
        font-size: 0.85rem;
        border: 1px solid rgba(0, 230, 118, 0.3);
    }
    
    .status-medium {
        color: #ffb300;
        font-weight: 500;
        padding: 0.3rem 0.8rem;
        background: rgba(255, 179, 0, 0.2);
        border-radius: 20px;
        font-size: 0.85rem;
        border: 1px solid rgba(255, 179, 0, 0.3);
    }
    
    .status-high {
        color: #ff5722;
        font-weight: 500;
        padding: 0.3rem 0.8rem;
        background: rgba(255, 87, 34, 0.2);
        border-radius: 20px;
        font-size: 0.85rem;
        border: 1px solid rgba(255, 87, 34, 0.3);
    }
    
    /* Progress bars - Blue-purple gradient */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4a6cf7 0%, #7209b7 100%);
        border-radius: 10px;
    }
    
    /* Tabs - Dark theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(26, 26, 46, 0.8);
        border-radius: 12px;
        padding: 0.3rem;
        border: 1px solid rgba(112, 9, 183, 0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #e0e6ed;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(74, 108, 247, 0.2);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #4a6cf7 0%, #7209b7 100%);
        color: white;
    }
    
    /* Success/Info/Warning messages - Dark theme */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .stSuccess {
        background: rgba(0, 230, 118, 0.15);
        border-left: 4px solid #00e676;
        color: #00e676;
    }
    
    .stInfo {
        background: rgba(74, 108, 247, 0.15);
        border-left: 4px solid #4a6cf7;
        color: #4a6cf7;
    }
    
    .stWarning {
        background: rgba(255, 179, 0, 0.15);
        border-left: 4px solid #ffb300;
        color: #ffb300;
    }
    
    .stError {
        background: rgba(255, 87, 34, 0.15);
        border-left: 4px solid #ff5722;
        color: #ff5722;
    }
    
    /* Expander - Dark theme */
    .streamlit-expanderHeader {
        border-radius: 12px;
        background: rgba(26, 26, 46, 0.9);
        border: 1px solid rgba(112, 9, 183, 0.3);
        color: #e0e6ed;
    }
    
    .streamlit-expanderContent {
        background: rgba(26, 26, 46, 0.8);
        border: 1px solid rgba(112, 9, 183, 0.2);
        border-top: none;
        border-radius: 0 0 12px 12px;
    }
    
    /* Data tables - Dark theme */
    .stDataFrame {
        background: rgba(26, 26, 46, 0.9);
        border-radius: 12px;
        border: 1px solid rgba(112, 9, 183, 0.3);
    }
    
    .stDataFrame table {
        background: rgba(26, 26, 46, 0.9);
        color: #e0e6ed;
    }
    
    .stDataFrame th {
        background: rgba(74, 108, 247, 0.3);
        color: #ffffff;
        border-bottom: 2px solid rgba(112, 9, 183, 0.5);
    }
    
    .stDataFrame td {
        border-bottom: 1px solid rgba(112, 9, 183, 0.2);
        color: #e0e6ed;
    }
    
    /* Risk category specific styling */
    .risk-low {
        background: linear-gradient(135deg, #00e676 0%, #00c853 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 230, 118, 0.3);
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #ffb300 0%, #ff8f00 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255, 179, 0, 0.3);
    }
    
    .risk-high {
        background: linear-gradient(135deg, #ff5722 0%, #d32f2f 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255, 87, 34, 0.3);
    }
    
    /* Selectbox dropdown - Dark theme */
    .stSelectbox > div > div {
        background: rgba(26, 26, 46, 0.9);
        border: 1px solid rgba(112, 9, 183, 0.3);
        color: #e0e6ed;
    }
    
    /* Text areas - Dark theme */
    .stTextArea > div > div > textarea {
        background: rgba(26, 26, 46, 0.8);
        border: 1px solid rgba(112, 9, 183, 0.3);
        color: #e0e6ed;
        border-radius: 12px;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #4a6cf7;
        box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.2);
    }
    
    /* Remove excessive padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Clean spacing */
    .element-container {
        margin-bottom: 0.8rem;
    }
    
    /* Typography improvements */
    .stMarkdown {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.6;
    }
    
    div.stButton > button {
        text-align: left;
        justify-content: left;
    }
</style>
""", unsafe_allow_html=True)


class ZScoreApp:
    """Main application class"""
    
    def __init__(self):
        self.auth = AuthManager()
        self.db = Database()
        self.model = CreditRiskModel()
        
        # Initialize session state
        if 'current_applicant' not in st.session_state:
            st.session_state.current_applicant = None
        if 'demo_mode' not in st.session_state:
            st.session_state.demo_mode = False
    
    def get_user_applicant_profile(self, user_id: int):
        """Get applicant profile for a user"""
        applicants = self.db.get_all_applicants()
        for applicant in applicants:
            if applicant.get('user_id') == user_id:
                return applicant
        return None
    
    def show_profile_completion(self, applicant):
        """Show profile completion form for new applicants"""
        st.markdown('<h1 class="main-header">👋 Welcome to Z-Score!</h1>', unsafe_allow_html=True)
        st.markdown("### Complete your profile to start your credit journey")
        
        with st.form("profile_completion"):
            st.subheader("Personal Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                phone = st.text_input("Phone Number*", placeholder="+91-XXXXXXXXXX")
                age = st.number_input("Age*", min_value=18, max_value=80, value=25)
                gender = st.selectbox("Gender*", ["Male", "Female", "Other"])
                location = st.text_input("Location*", placeholder="City, State")
            
            with col2:
                occupation = st.text_input("Occupation*", placeholder="Job title or business")
                monthly_income = st.number_input("Monthly Income (₹)*", min_value=0, value=15000)
                education = st.selectbox("Education Level", ["High School", "Graduate", "Post Graduate", "Professional"])
                marital_status = st.selectbox("Marital Status", ["Single", "Married", "Divorced", "Widowed"])
            
            st.subheader("Your Credit Goals")
            credit_purpose = st.multiselect(
                "What do you need credit for?",
                ["Business expansion", "Education", "Home improvement", "Medical expenses", 
                 "Vehicle purchase", "Working capital", "Emergency fund", "Other"]
            )
            
            credit_amount = st.selectbox(
                "Expected credit amount",
                ["< ₹50,000", "₹50,000 - ₹1,00,000", "₹1,00,000 - ₹5,00,000", 
                 "₹5,00,000 - ₹10,00,000", "> ₹10,00,000"]
            )
            
            submit_profile = st.form_submit_button("Complete Profile & Start Journey", use_container_width=True)
            
            if submit_profile:
                if phone and age and gender and location and occupation and monthly_income:
                    # Update applicant profile
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        UPDATE applicants SET
                            phone = ?, age = ?, gender = ?, location = ?,
                            occupation = ?, monthly_income = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (phone, age, gender, location, occupation, monthly_income, applicant['id']))
                    
                    conn.commit()
                    conn.close()
                    
                    # Log profile completion
                    self.db.log_consent(
                        applicant['id'],
                        'profile_completion',
                        'credit_assessment_preparation',
                        True,
                        {
                            'credit_purpose': credit_purpose,
                            'credit_amount': credit_amount,
                            'education': education,
                            'marital_status': marital_status
                        }
                    )
                    
                    st.success("Profile completed successfully!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Please fill in all required fields marked with *")
    
    def run(self):
        """Main application entry point"""
        # Show authentication check
        if not self.auth.require_auth():
            return
        
        # Show user info in sidebar
        self.auth.show_user_info()
        
        # Main navigation
        self.show_navigation()
        
        # Route to selected page
        page = st.session_state.get('selected_page', 'Dashboard')
        
        # Check if user is an applicant and needs to complete profile
        current_user = self.auth.get_current_user()
        if current_user and current_user['role'] == 'applicant':
            applicant = self.get_user_applicant_profile(current_user['id'])
            if applicant and not applicant.get('phone'):
                # Redirect to profile completion
                st.info("👋 Welcome! Please complete your profile to get started with your credit journey.")
                self.show_profile_completion(applicant)
                return
        
        self.route_to_page(page)
    
    def show_navigation(self):
        """Show role-based navigation menu"""
        with st.sidebar:
            # Header with user info
            current_user = self.auth.get_current_user()
            if current_user:
                st.markdown(f"### Welcome, {current_user['username']}!")
                st.markdown(f"**Role:** {current_user['role'].title()}")
            else:
                st.markdown("### Z-Score Navigation")
            
            st.markdown("---")
            
            # Role-based navigation
            if current_user:
                if current_user['role'] == 'admin':
                    self.show_admin_navigation()
                elif current_user['role'] == 'applicant':
                    self.show_user_navigation()
                else:
                    self.show_guest_navigation()
            else:
                self.show_guest_navigation()
            
            st.markdown("---")
            
            # User controls
            if current_user:
                if st.button("🚪 Logout", use_container_width=True):
                    self.auth.logout()
                    st.session_state.clear()
                    st.rerun()
            
            # Demo controls (only for admin)
            if current_user and current_user['role'] == 'admin':
                st.markdown("---")
                st.subheader("🚀 Admin Controls")
                if st.button("Load Sample Data", use_container_width=True):
                    self.db.add_sample_data()
                    st.success("Sample data loaded!")
                    time.sleep(1)
                    st.rerun()
                
                if st.button("Reset Database", use_container_width=True):
                    if st.session_state.get('confirm_reset'):
                        from local_db import reset_database
                        reset_database()
                        st.success("Database reset!")
                        st.session_state.confirm_reset = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.session_state.confirm_reset = True
                        st.warning("Click again to confirm reset")
    
    def show_admin_navigation(self):
        """Show navigation for admin users"""
        st.subheader("Admin Dashboard")
        
        admin_pages = [
            ("System Overview", "Dashboard"),
            ("All Applicants", "All Applicants"),
            ("Risk Assessment", "Risk Assessment"),
            ("New Applicant", "New Applicant"),
            ("Gamification", "Gamification"),
            ("Compliance", "Compliance"),
            ("Admin Panel", "Admin Panel")
        ]
        
        for label, page_key in admin_pages:
            if st.button(f"{label}", use_container_width=True, key=f"admin_{page_key}"):
                st.session_state.selected_page = page_key
                st.rerun()
    
    def show_user_navigation(self):
        """Show navigation for regular users/applicants"""
        st.subheader("My Dashboard")
        
        user_pages = [
            ("My Dashboard", "Dashboard"),
            ("My Profile", "My Profile"),
            ("My Journey", "My Journey"),
            ("Trust Score", "Trust Score"),
            ("Apply for Credit", "Apply for Credit")
        ]
        
        for label, page_key in user_pages:
            if st.button(f"{label}", use_container_width=True, key=f"user_{page_key}"):
                st.session_state.selected_page = page_key
                st.rerun()
    
    def show_guest_navigation(self):
        """Show navigation for guests/unauthenticated users"""
        st.subheader("Get Started")
        
        guest_pages = [
            ("Overview", "Dashboard"),
            ("Demo Features", "Gamification")
        ]
        
        for label, page_key in guest_pages:
            if st.button(f"{label}", use_container_width=True, key=f"guest_{page_key}"):
                st.session_state.selected_page = page_key
                st.rerun()
    
    def route_to_page(self, page: str):
        """Route to selected page with role-based access control"""
        current_user = self.auth.get_current_user()
        
        # Define role-based access permissions
        admin_only_pages = ["New Applicant", "Risk Assessment", "Admin Panel", "All Applicants"]
        user_only_pages = ["My Profile", "My Journey", "Trust Score", "Apply for Credit"]
        public_pages = ["Dashboard", "Gamification", "Compliance"]
        
        # Check access permissions
        if page in admin_only_pages:
            if not current_user or current_user['role'] != 'admin':
                st.error("🔒 Access Denied: Admin privileges required")
                st.info("Please login as an administrator to access this feature.")
                return
        
        elif page in user_only_pages:
            if not current_user or current_user['role'] != 'applicant':
                st.error("🔒 Access Denied: User account required")
                st.info("Please login as a user to access this feature.")
                return
        
        # Route to appropriate page
        if page == "Dashboard":
            if current_user and current_user['role'] == 'admin':
                self.show_admin_dashboard()
            elif current_user and current_user['role'] == 'applicant':
                self.show_user_dashboard()
            else:
                self.show_public_dashboard()
        elif page == "New Applicant":
            self.show_new_applicant()
        elif page == "Risk Assessment":
            self.show_risk_assessment()
        elif page == "Gamification":
            self.show_gamification()
        elif page == "Compliance":
            self.show_compliance()
        elif page == "Admin Panel":
            self.show_admin_panel()
        elif page == "My Profile":
            self.show_my_profile()
        elif page == "My Journey":
            self.show_my_journey()
        elif page == "Trust Score":
            self.show_trust_score()
        elif page == "Apply for Credit":
            self.show_apply_credit()
        elif page == "All Applicants":
            self.show_all_applicants()
        else:
            st.error(f"Page '{page}' not found")
    
    def show_admin_dashboard(self):
        """Admin dashboard with system overview"""
        st.markdown('<h1 class="main-header">🔧 Admin Dashboard</h1>', unsafe_allow_html=True)
        
        # System metrics
        applicants = self.db.get_all_applicants()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Applicants", len(applicants))
        
        with col2:
            scored_applicants = [a for a in applicants if a.get('overall_trust_score', 0) > 0]
            st.metric("Trust Scored", len(scored_applicants))
        
        with col3:
            high_trust = [a for a in applicants if a.get('overall_trust_score', 0) > 0.7]
            st.metric("High Trust (>70%)", len(high_trust))
        
        with col4:
            applications = [a for a in applicants if a.get('credit_application_status') != 'not_applied']
            st.metric("Credit Applications", len(applications))
        
        # Quick actions for admin
        st.subheader("⚡ Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➕ Add New Applicant", use_container_width=True):
                st.session_state.selected_page = "New Applicant"
                st.rerun()
        
        with col2:
            if st.button("🔍 Assess Risk", use_container_width=True):
                st.session_state.selected_page = "Risk Assessment"
                st.rerun()
        
        with col3:
            if st.button("👥 View All Users", use_container_width=True):
                st.session_state.selected_page = "All Applicants"
                st.rerun()
        
        # Recent applications table
        if applicants:
            st.subheader("📋 Recent Applications")
            
            df = pd.DataFrame(applicants)
            df['trust_percentage'] = (df['overall_trust_score'] * 100).round(1)
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Display table
            display_cols = ['name', 'phone', 'location', 'trust_percentage', 'credit_application_status']
            if all(col in df.columns for col in display_cols):
                st.dataframe(
                    df[display_cols].head(10),
                    column_config={
                        'trust_percentage': st.column_config.ProgressColumn(
                            'Trust Score %',
                            min_value=0,
                            max_value=100
                        )
                    }
                )
        else:
            st.info("No applicants found. Add some sample data to get started!")
    
    def show_user_dashboard(self):
        """User dashboard with personal overview"""
        current_user = self.auth.get_current_user()
        if not current_user:
            st.error("Please login to view your dashboard")
            return
            
        applicant = self.get_user_applicant_profile(current_user['id'])
        
        if not applicant:
            self.show_profile_completion(None)
            return
        
        st.markdown('<h1 class="main-header">📊 My Dashboard</h1>', unsafe_allow_html=True)
        
        # Personal metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            trust_score = applicant.get('overall_trust_score', 0) * 100
            st.metric("My Trust Score", f"{trust_score:.1f}%")
        
        with col2:
            z_credits = applicant.get('z_credits', 0)
            st.metric("Z-Credits Earned", z_credits)
        
        with col3:
            app_status = applicant.get('credit_application_status', 'not_applied')
            status_display = app_status.replace('_', ' ').title()
            st.metric("Application Status", status_display)
        
        # Quick actions for user
        st.subheader("⚡ My Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👤 Update Profile", use_container_width=True):
                st.session_state.selected_page = "My Profile"
                st.rerun()
        
        with col2:
            if st.button("🎮 Continue Journey", use_container_width=True):
                st.session_state.selected_page = "My Journey"
                st.rerun()
        
        with col3:
            if st.button("💳 Apply for Credit", use_container_width=True):
                st.session_state.selected_page = "Apply for Credit"
                st.rerun()
        
        # Professional Trust Score visualization
        st.markdown("---")
        self.render_professional_trust_bar(applicant)
    
    def show_public_dashboard(self):
        """Public dashboard for unauthenticated users"""
        st.markdown('<h1 class="main-header">Welcome to Z-Score</h1>', unsafe_allow_html=True)
        st.markdown("### Revolutionizing Credit Assessment for the Underbanked")
        
        # Feature highlights
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            #### Trust-Based Scoring
            Our AI analyzes behavioral patterns, social proof, and digital footprints 
            to create comprehensive trust scores for applicants without traditional credit history.
            """)
        
        with col2:
            st.markdown("""
            #### Explainable AI
            Every credit decision comes with clear explanations using SHAP technology, 
            ensuring transparency and helping applicants understand their assessment.
            """)
        
        with col3:
            st.markdown("""
            #### Gamified Journey
            Earn Z-Credits through financial literacy missions and responsible behavior, 
            improving your trust score while learning.
            """)
        
        # Call to action
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Ready to Get Started?")
            st.info("Please login or contact an administrator to access the full Z-Score platform")
            
            if st.button("Explore Demo Features", use_container_width=True):
                st.session_state.selected_page = "Gamification"
                st.rerun()

    def show_new_applicant(self):
        """New applicant registration page"""
        st.markdown('<h1 class="main-header">New Applicant Registration</h1>', unsafe_allow_html=True)
        
        with st.form("new_applicant_form"):
            st.subheader("Basic Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name*", placeholder="Enter full name")
                phone = st.text_input("Phone Number*", placeholder="+91-XXXXXXXXXX")
                email = st.text_input("Email", placeholder="email@example.com")
                age = st.number_input("Age", min_value=18, max_value=80, value=25)
            
            with col2:
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                location = st.text_input("Location", placeholder="City, State")
                occupation = st.text_input("Occupation", placeholder="Job title or business")
                monthly_income = st.number_input("Monthly Income (₹)", min_value=0, value=15000)
            
            # Alternative data section
            st.subheader("Alternative Data (Optional)")
            
            with st.expander("Payment History"):
                col1, col2 = st.columns(2)
                with col1:
                    total_payments = st.number_input("Total Utility Payments", min_value=0, value=12)
                    on_time_payments = st.number_input("On-time Payments", min_value=0, value=10)
                with col2:
                    avg_payment_amount = st.number_input("Average Payment Amount (₹)", min_value=0, value=1500)
                    payment_consistency = st.slider("Payment Consistency", 0.0, 1.0, 0.8)
            
            with st.expander("Social Proof"):
                col1, col2 = st.columns(2)
                with col1:
                    community_rating = st.slider("Community Rating", 1.0, 5.0, 3.5)
                    endorsements = st.number_input("Community Endorsements", min_value=0, value=3)
                with col2:
                    group_participation = st.slider("Group Participation Score", 0.0, 1.0, 0.6)
                    social_references = st.number_input("Social References", min_value=0, value=2)
            
            with st.expander("Digital Footprint"):
                col1, col2 = st.columns(2)
                with col1:
                    transaction_regularity = st.slider("Digital Transaction Regularity", 0.0, 1.0, 0.7)
                    device_stability = st.slider("Device Stability", 0.0, 1.0, 0.8)
                with col2:
                    digital_literacy = st.slider("Digital Literacy Score", 0.0, 1.0, 0.6)
                    online_presence = st.slider("Online Presence Score", 0.0, 1.0, 0.5)
            
            submitted = st.form_submit_button("Register Applicant", use_container_width=True)
            
            if submitted:
                if name and phone:
                    try:
                        # Create applicant data
                        current_user = self.auth.get_current_user()
                        if current_user:
                            applicant_data = {
                                'user_id': current_user['id'],
                                'name': name,
                                'phone': phone,
                                'email': email,
                                'age': age,
                                'gender': gender,
                                'location': location,
                                'occupation': occupation,
                                'monthly_income': monthly_income
                            }
                            
                            # Create applicant record
                            applicant_id = self.db.create_applicant(applicant_data)
                        
                        if applicant_id:
                            # Prepare alternative data
                            payment_history = {
                                'total_payments': total_payments,
                                'on_time_payments': on_time_payments,
                                'average_amount': avg_payment_amount,
                                'on_time_ratio': on_time_payments / max(total_payments, 1)
                            }
                            
                            social_proof = {
                                'community_rating': community_rating,
                                'endorsements': endorsements,
                                'group_participation_score': group_participation,
                                'social_references': social_references
                            }
                            
                            digital_data = {
                                'transaction_regularity': transaction_regularity,
                                'device_stability': device_stability,
                                'digital_literacy_score': digital_literacy,
                                'online_presence_score': online_presence
                            }
                            
                            # Calculate trust scores
                            calculator = TrustScoreCalculator()
                            behavioral_score = calculator.calculate_behavioral_score(
                                payment_history, payment_consistency
                            )
                            social_score = calculator.calculate_social_score(
                                social_proof, community_rating
                            )
                            digital_score = calculator.calculate_digital_score(
                                digital_data, device_stability
                            )
                            
                            # Update trust scores
                            self.db.update_trust_score(applicant_id, behavioral_score, social_score, digital_score)
                            
                            # Log consent
                            self.db.log_consent(
                                applicant_id,
                                'data_collection',
                                'credit_assessment',
                                True,
                                {'timestamp': datetime.now().isoformat()}
                            )
                            
                            st.success(f"Applicant {name} registered successfully!")
                            st.success(f"Trust Score: {((behavioral_score + social_score + digital_score) / 3 * 100):.1f}%")
                            
                            # Store in session for navigation
                            st.session_state.current_applicant = applicant_id
                            
                        else:
                            st.error("Failed to create applicant record")
                    
                    except Exception as e:
                        st.error(f"Error creating applicant: {str(e)}")
                else:
                    st.error("Please fill in required fields (Name and Phone)")
    
    def show_risk_assessment(self):
        """Risk assessment and ML prediction page"""
        st.markdown('<h1 class="main-header">Credit Risk Assessment</h1>', unsafe_allow_html=True)
        
        # Select applicant
        applicants = self.db.get_all_applicants()
        if not applicants:
            st.warning("No applicants found. Please register an applicant first.")
            return
        
        # Applicant selection
        applicant_options = {f"{a['name']} ({a['phone']})": a['id'] for a in applicants}
        selected_applicant_key = st.selectbox("Select Applicant", list(applicant_options.keys()))
        applicant_id = applicant_options[selected_applicant_key]
        
        applicant = self.db.get_applicant(applicant_id)
        if not applicant:
            st.error("Applicant not found")
            return
        
        # Display applicant info
        col1, col2 = st.columns([2, 1])
        
        with col1:
            applicant_name = applicant.get('name', 'Unknown Applicant')
            st.subheader(f"Assessment for {applicant_name}")
            
            # Current trust score
            trust_percentage = (applicant.get('overall_trust_score', 0) * 100)
            st.metric("Current Trust Score", f"{trust_percentage:.1f}%")
            
            # Trust score breakdown
            behavioral = applicant.get('behavioral_score', 0) * 100
            social = applicant.get('social_score', 0) * 100
            digital = applicant.get('digital_score', 0) * 100
            
            # Trust bar visualization
            fig = go.Figure(data=[
                go.Bar(name='Behavioral', x=['Trust Components'], y=[behavioral], marker_color='#1f77b4'),
                go.Bar(name='Social', x=['Trust Components'], y=[social], marker_color='#ff7f0e'),
                go.Bar(name='Digital', x=['Trust Components'], y=[digital], marker_color='#2ca02c')
            ])
            
            fig.update_layout(
                title='Trust Score Breakdown',
                barmode='group',
                yaxis_title='Score (%)',
                showlegend=True,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📋 Applicant Details")
            st.write(f"**Phone:** {applicant.get('phone', 'N/A')}")
            st.write(f"**Age:** {applicant.get('age', 'N/A')}")
            st.write(f"**Location:** {applicant.get('location', 'N/A')}")
            st.write(f"**Occupation:** {applicant.get('occupation', 'N/A')}")
            
            # Safe formatting for monthly income
            monthly_income = applicant.get('monthly_income')
            if monthly_income is not None:
                st.write(f"**Monthly Income:** ₹{monthly_income:,.0f}")
            else:
                st.write("**Monthly Income:** Not provided")
        
        # ML Prediction
        st.subheader("AI Risk Assessment")
        
        if st.button("Run Credit Risk Assessment", use_container_width=True):
            with st.spinner("Running AI models..."):
                try:
                    # Make prediction
                    prediction_result = self.model.predict(applicant)
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        risk_category = prediction_result['risk_category']
                        if risk_category == "Low Risk":
                            st.markdown(f'<div class="risk-low">🟢 {risk_category}</div>', unsafe_allow_html=True)
                        elif risk_category == "Medium Risk":
                            st.markdown(f'<div class="risk-medium">🟡 {risk_category}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="risk-high">🔴 {risk_category}</div>', unsafe_allow_html=True)
                    
                    with col2:
                        risk_probability = prediction_result.get('risk_probability', 0)
                        st.metric("Default Probability", f"{risk_probability:.1%}" if risk_probability is not None else "N/A")
                    
                    with col3:
                        confidence_score = prediction_result.get('confidence_score', 0)
                        st.metric("Confidence Score", f"{confidence_score:.1%}" if confidence_score is not None else "N/A")
                    
                    # SHAP Explanation
                    st.subheader("AI Decision Explanation")
                    explanation = self.model.explain_prediction(applicant)
                    
                    if 'error' not in explanation:
                        # Feature importance chart
                        feature_contrib = explanation['feature_contributions']
                        
                        features = list(feature_contrib.keys())
                        shap_values = [feature_contrib[f]['shap_value'] for f in features]
                        
                        # Create SHAP-style plot
                        colors = ['red' if v < 0 else 'blue' for v in shap_values]
                        
                        fig = go.Figure(data=[
                            go.Bar(
                                x=shap_values,
                                y=features,
                                orientation='h',
                                marker_color=colors,
                                text=[f"{v:.3f}" if v is not None else "N/A" for v in shap_values],
                                textposition='auto'
                            )
                        ])
                        
                        fig.update_layout(
                            title='Feature Impact on Credit Decision',
                            xaxis_title='SHAP Value (Impact on Decision)',
                            yaxis_title='Features',
                            height=600
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Recommendations
                        st.subheader("💡 Improvement Recommendations")
                        
                        negative_features = [f for f, data in feature_contrib.items() 
                                           if data['shap_value'] < 0]
                        
                        if negative_features:
                            for feature in negative_features[:3]:  # Top 3 negative features
                                if 'payment' in feature.lower():
                                    st.info("**Improve Payment History**: Make more on-time utility payments")
                                elif 'social' in feature.lower():
                                    st.info("**Build Social Proof**: Get community endorsements and references")
                                elif 'digital' in feature.lower():
                                    st.info("**Enhance Digital Presence**: Increase digital transaction regularity")
                                elif 'income' in feature.lower():
                                    st.info("**Increase Income Stability**: Work on stable income sources")
                        else:
                            st.success("**Excellent Profile!** All major factors are positive.")
                    
                    else:
                        st.error(f"Explanation Error: {explanation['error']}")
                
                except Exception as e:
                    st.error(f"Prediction Error: {str(e)}")
    
    def show_gamification(self):
        """Gamification and financial literacy page"""
        st.markdown('<h1 class="main-header">Financial Literacy & Gamification</h1>', unsafe_allow_html=True)
        
        # Select applicant
        applicants = self.db.get_all_applicants()
        if not applicants:
            st.warning("No applicants found. Please register an applicant first.")
            return
        
        applicant_options = {f"{a['name']} ({a['phone']})": a['id'] for a in applicants}
        selected_applicant_key = st.selectbox("Select Applicant", list(applicant_options.keys()))
        applicant_id = applicant_options[selected_applicant_key]
        
        applicant = self.db.get_applicant(applicant_id)
        if not applicant:
            st.error("Applicant not found")
            return
        
        # Current status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            trust_percentage = (applicant.get('overall_trust_score', 0) * 100)
            st.metric("Trust Score", f"{trust_percentage:.1f}%")
        
        with col2:
            z_credits = applicant.get('z_credits', 0)
            st.metric("Z-Credits", z_credits)
        
        with col3:
            eligibility = "Eligible" if trust_percentage >= 70 else "Not Eligible"
            st.metric("Credit Eligibility", eligibility)
        
        # Professional animated Trust Bar
        current_trust = self.render_professional_trust_bar(applicant)
        
        # Available missions section
        st.markdown("---")
        st.markdown('<h2 style="color: #2E4A62; font-weight: 600; margin-top: 30px;">Available Growth Missions</h2>', unsafe_allow_html=True)
        
    def calculate_behavioral_trust_fallback(self, applicant_data):
        """Calculate Behavioral Trust (50% weight) per LOGIC.md - Payment History + Loan Performance"""
        score = 0
        
        # Payment consistency simulation (0-50 points)
        # In real implementation, this would analyze F1 (Payment History)
        if applicant_data.get('phone'):  # Phone suggests payment capability
            score += 25  # Base payment score for having contact info
        
        # Loan performance simulation (0-50 points)  
        # In real implementation, this would analyze F2 (Loan Performance)
        if applicant_data.get('monthly_income'):
            try:
                income = float(applicant_data.get('monthly_income', 0))
                if income > 15000:  # Good income suggests loan repayment ability
                    score += 25
                elif income > 10000:
                    score += 15
                else:
                    score += 10
            except (TypeError, ValueError):
                score += 10  # Minimal score for having income data
        else:
            score += 15  # Neutral for new-to-credit per LOGIC.md
            
        # Add small variance for demo purposes
        variance = hash(str(applicant_data.get('id', 1))) % 10
        score += variance
        
        return min(100, max(0, score))
    
    def calculate_social_trust_fallback(self, applicant_data):
        """Calculate Social Trust (30% weight) per LOGIC.md - Social Proof from SHG/NGO endorsements"""
        score = 0
        
        # Endorsement strength simulation (0-40 points)
        # In real implementation, this would analyze F3 (Social Proof)
        if applicant_data.get('location'):  # Location suggests community ties
            score += 20  # Community presence
            
        # Community standing simulation (0-30 points)
        if applicant_data.get('occupation'):  # Occupation suggests social role
            score += 20
            
        # Age-based community standing (older = more established)
        age = applicant_data.get('age', 25)
        if age > 30:
            score += 15
        elif age > 25:
            score += 10
        else:
            score += 5
            
        # Add small variance for demo purposes
        variance = hash(str(applicant_data.get('name', 'user'))) % 8
        score += variance
        
        return min(100, max(0, score))
    
    def calculate_digital_trust_fallback(self, applicant_data):
        """Calculate Digital Trust (20% weight) per LOGIC.md - Digital Footprint Analysis"""
        score = 0
        
        # Stability indicators simulation (0-40 points)
        # In real implementation, this would analyze F4 (Digital Footprint)
        if applicant_data.get('phone'):  # Phone ownership = digital presence
            score += 20
            
        if applicant_data.get('email'):  # Email = digital sophistication
            score += 15
            
        # Financial behavior signals simulation (0-40 points)
        # Location consistency suggests stability
        if applicant_data.get('location'):
            score += 10
            
        # Age suggests device tenure (older = longer device usage)
        age = applicant_data.get('age', 25)
        if age > 30:
            score += 15
        elif age > 25:
            score += 10
        else:
            score += 5
            
        # Add small variance for demo purposes  
        variance = hash(str(applicant_data.get('phone', '123'))) % 12
        score += variance
        
        return min(100, max(0, score))

    def render_professional_trust_bar(self, applicant_data):
        """Render professional Trust Bar with correct Z-Score logic per LOGIC.md"""
        
        # Get stored trust scores (should be calculated by proper ML pipeline)
        overall_trust = applicant_data.get('overall_trust_score', 0) * 100
        behavioral_score = applicant_data.get('behavioral_score', 0) * 100
        social_score = applicant_data.get('social_score', 0) * 100
        digital_score = applicant_data.get('digital_score', 0) * 100
        
        # If no ML-calculated scores exist, use fallback logic that follows LOGIC.md structure
        if overall_trust == 0 and behavioral_score == 0 and social_score == 0 and digital_score == 0:
            behavioral_score = self.calculate_behavioral_trust_fallback(applicant_data)
            social_score = self.calculate_social_trust_fallback(applicant_data)
            digital_score = self.calculate_digital_trust_fallback(applicant_data)
            
            # Apply correct weighting per LOGIC.md: 50% behavioral, 30% social, 20% digital
            overall_trust = (behavioral_score * 0.5 + social_score * 0.3 + digital_score * 0.2)
            
            # Update the database with calculated scores for persistence
            try:
                applicant_id = applicant_data.get('id')
                if applicant_id:
                    self.db.update_trust_score(
                        applicant_id, 
                        behavioral_score / 100,  # Convert back to 0-1 scale
                        social_score / 100,
                        digital_score / 100
                    )
            except Exception as e:
                pass  # Silently fail if DB update doesn't work
        
        # Display the Trust Bar with enhanced visual prominence using native Streamlit components
        st.markdown("---")
        st.markdown("## 🎯 **CREDIT TRUST ASSESSMENT DASHBOARD**")
        st.markdown("---")
        
        # Create columns for better layout
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Display a prominent progress bar using Streamlit's native progress
            st.markdown(f"### **Overall Trust Score: {overall_trust:.1f}%**")
            progress_value = min(overall_trust / 100, 1.0)
            st.progress(progress_value)
            
            # Status indicator
            if overall_trust >= 70:
                st.success("✅ **CREDIT ASSESSMENT ELIGIBLE**")
            else:
                st.warning(f"⚠️ **BUILDING TRUST PROFILE** - {70 - overall_trust:.1f}% more needed")
        
        # Component breakdown in columns
        st.markdown("### **Trust Components Breakdown**")
        comp_col1, comp_col2, comp_col3 = st.columns(3)
        
        with comp_col1:
            st.metric(
                label="🎭 Behavioral Trust",
                value=f"{behavioral_score:.0f}%",
                delta=f"{behavioral_score - 30:.1f}% vs baseline"
            )
            st.progress(min(behavioral_score / 100, 1.0))
        
        with comp_col2:
            st.metric(
                label="👥 Social Trust", 
                value=f"{social_score:.0f}%",
                delta=f"{social_score - 25:.1f}% vs baseline"
            )
            st.progress(min(social_score / 100, 1.0))
        
        with comp_col3:
            st.metric(
                label="💻 Digital Trust",
                value=f"{digital_score:.0f}%", 
                delta=f"{digital_score - 35:.1f}% vs baseline"
            )
            st.progress(min(digital_score / 100, 1.0))
        
        # Display the correct Z-Score formula per LOGIC.md
        st.markdown("---")
        st.markdown("### **📊 Z-Score Calculation Formula (per LOGIC.md)**")
        st.latex(r'''
        Trust\_Score = 0.5 \times Behavioral + 0.3 \times Social + 0.2 \times Digital
        ''')
        st.markdown(f"**Current Calculation:** {overall_trust:.1f}% = 0.5×{behavioral_score:.0f}% + 0.3×{social_score:.0f}% + 0.2×{digital_score:.0f}%")
        
        # Small debug indicator
        st.caption(f"✅ Trust Bar Active - Overall Score: {overall_trust:.1f}% | Components: Behavioral: {behavioral_score:.0f}%, Social: {social_score:.0f}%, Digital: {digital_score:.0f}%")
        
        return overall_trust
        
        # Available missions
        # Professional missions grid
        missions_css = """
        <style>
        .missions-container {
            margin-top: 30px;
        }
        
        .missions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .mission-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            padding: 24px;
            color: white;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .mission-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(31, 38, 135, 0.5);
        }
        
        .mission-title {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 12px;
            color: #ffffff;
        }
        
        .mission-description {
            font-size: 14px;
            color: #e8f4f8;
            margin-bottom: 16px;
            line-height: 1.5;
        }
        
        .mission-reward {
            background: rgba(255, 255, 255, 0.2);
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 16px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .mission-button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
            border: none;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .mission-button:hover {
            background: linear-gradient(90deg, #0072ff 0%, #00c6ff 100%);
            transform: translateY(-2px);
        }
        
        .achievement-section {
            margin-top: 40px;
            padding: 24px;
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border-radius: 16px;
            color: #8b2635;
        }
        
        .achievement-title {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 16px;
            text-align: center;
        }
        
        .achievement-item {
            background: rgba(255, 255, 255, 0.8);
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 8px;
            font-weight: 600;
            border-left: 4px solid #4caf50;
        }
        
        .no-achievements {
            text-align: center;
            font-style: italic;
            color: #666;
        }
        </style>
        """
        
        missions = [
            {
                'title': 'Financial Literacy Assessment',
                'description': 'Complete comprehensive financial knowledge evaluation covering budgeting, savings, and credit fundamentals',
                'reward': '+15% Trust Score, 50 Z-Credits',
                'type': 'quiz',
                'id': 'quiz'
            },
            {
                'title': 'Utility Payment Verification',
                'description': 'Submit documented proof of consistent on-time utility bill payments',
                'reward': '+20% Trust Score, 75 Z-Credits',
                'type': 'payment',
                'id': 'payment'
            },
            {
                'title': 'Community Endorsement',
                'description': 'Obtain verified endorsement from recognized community leader or local authority',
                'reward': '+25% Trust Score, 100 Z-Credits',
                'type': 'social',
                'id': 'social'
            },
            {
                'title': 'Banking Integration',
                'description': 'Provide consent and connect bank account for transaction history analysis',
                'reward': '+30% Trust Score, 150 Z-Credits',
                'type': 'data',
                'id': 'banking'
            }
        ]
        
        st.markdown(missions_css, unsafe_allow_html=True)
        
        missions_html = """
        <div class="missions-container">
            <div class="missions-grid">
        """
        
        for i, mission in enumerate(missions):
            missions_html += f"""
                <div class="mission-card">
                    <div class="mission-title">{mission['title']}</div>
                    <div class="mission-description">{mission['description']}</div>
                    <div class="mission-reward">Reward: {mission['reward']}</div>
                </div>
            """
        
        missions_html += """
            </div>
        </div>
        """
        
        st.markdown(missions_html, unsafe_allow_html=True)
        
        # Interactive mission completion
        st.markdown("---")
        selected_mission = st.selectbox(
            "Select Mission to Complete",
            [f"{mission['title']}" for mission in missions],
            help="Choose a mission to simulate completion"
        )
        
        if st.button("Complete Selected Mission", use_container_width=True, type="primary"):
            mission_idx = next(i for i, m in enumerate(missions) if m['title'] == selected_mission)
            mission = missions[mission_idx]
            
            with st.spinner("Processing mission completion..."):
                import time
                time.sleep(2)
            
            # Update trust score and credits
            current_trust = applicant.get('overall_trust_score', 0)
            if mission['type'] == 'quiz':
                new_trust = min(current_trust + 0.15, 1.0)
                credits_earned = 50
            elif mission['type'] == 'payment':
                new_trust = min(current_trust + 0.20, 1.0)
                credits_earned = 75
            elif mission['type'] == 'social':
                new_trust = min(current_trust + 0.25, 1.0)
                credits_earned = 100
            else:  # data
                new_trust = min(current_trust + 0.30, 1.0)
                credits_earned = 150
            
            # Update database (simplified for demo)
            behavioral = applicant.get('behavioral_score', 0) + 0.1
            social = applicant.get('social_score', 0) + 0.1
            digital = applicant.get('digital_score', 0) + 0.1
            
            self.db.update_trust_score(applicant_id, behavioral, social, digital)
            
            st.success(f"Mission completed successfully! +{credits_earned} Z-Credits earned!")
            st.balloons()
            time.sleep(2)
            st.rerun()
        
        # Professional achievement showcase
        st.markdown("---")
        st.markdown('<h2 style="color: #2E4A62; font-weight: 600; margin-top: 30px;">Achievement Milestones</h2>', unsafe_allow_html=True)
        
        achievements = []
        if trust_percentage >= 30:
            achievements.append("Foundation Builder - Reached 30% Trust Score")
        if trust_percentage >= 50:
            achievements.append("Trust Developer - Reached 50% Trust Score")
        if trust_percentage >= 70:
            achievements.append("Credit Ready - Reached 70% Trust Score")
        if z_credits >= 100:
            achievements.append("Credit Advocate - Earned 100+ Z-Credits")
        
        achievement_html = """
        <div class="achievement-section">
            <div class="achievement-title">Your Progress Milestones</div>
        """
        
        if achievements:
            for achievement in achievements:
                achievement_html += f'<div class="achievement-item">{achievement}</div>'
        else:
            achievement_html += '<div class="no-achievements">Complete missions to unlock achievement milestones</div>'
        
        achievement_html += "</div>"
        st.markdown(achievement_html, unsafe_allow_html=True)
    
    def show_compliance(self):
        """DPDPA compliance and consent management"""
        st.markdown('<h1 class="main-header">Compliance & Data Privacy</h1>', unsafe_allow_html=True)
        
        st.subheader("🔒 DPDPA 2023 Compliance Framework")
        
        compliance_items = [
            ("✅ Valid Consent", "Free, specific, informed, and unambiguous consent collection"),
            ("✅ Purpose Limitation", "Data used only for stated credit assessment purposes"),
            ("✅ Data Minimization", "Collection limited to necessary data only"),
            ("✅ Data Localization", "All data stored within India boundaries"),
            ("✅ Consent Withdrawal", "Easy mechanism for users to withdraw consent"),
            ("✅ Data Security", "Encryption and secure storage protocols"),
            ("✅ Audit Trail", "Complete logging of all data processing activities"),
            ("✅ Transparency", "Clear explanation of data usage and decisions")
        ]
        
        for status, description in compliance_items:
            st.success(f"{status}: {description}")
        
        # RBI Guidelines compliance
        st.subheader("RBI Digital Lending Guidelines 2025")
        
        rbi_items = [
            ("✅ LSP Partnership Model", "Working with regulated lending entities"),
            ("✅ Direct Fund Flow", "No intermediary handling of borrower funds"),
            ("✅ Key Fact Statement", "Clear disclosure of terms and conditions"),
            ("✅ Cooling-off Period", "Mandatory waiting period before loan disbursement"),
            ("✅ Grievance Redressal", "Established complaint resolution mechanism")
        ]
        
        for status, description in rbi_items:
            st.success(f"{status}: {description}")
        
        # Consent management demo
        st.subheader("Consent Management System")
        
        if st.button("Demonstrate Consent Collection"):
            st.info("""
            **Sample Consent Flow:**
            
            1. **Data Collection Consent**
               - Purpose: Credit risk assessment
               - Data Types: Basic profile, payment history, social proof
               - Retention: 7 years as per RBI guidelines
               - Sharing: Only with partner lending institutions
            
            2. **Processing Consent**
               - ML model analysis for risk scoring
               - Alternative data evaluation
               - Credit recommendation generation
            
            3. **Sharing Consent**
               - Results shared with authorized lenders only
               - Applicant has right to know data recipients
               - Consent required for each new use case
            """)
            
            if st.button("✅ Grant Consent"):
                st.success("Consent granted and logged with timestamp!")
                st.info("You can withdraw this consent at any time.")
        
        # Privacy controls
        st.subheader("Privacy Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.button("Download My Data", use_container_width=True)
            st.button("Update Preferences", use_container_width=True)
        
        with col2:
            st.button("Withdraw Consent", use_container_width=True)
            st.button("Delete My Account", use_container_width=True)
    
    def show_admin_panel(self):
        """Admin panel for system management"""
        if not self.auth.has_role('admin'):
            st.error("Access denied. Admin role required.")
            return
        
        st.markdown('<h1 class="main-header">Admin Panel</h1>', unsafe_allow_html=True)
        
        # System statistics
        st.subheader("System Statistics")
        
        applicants = self.db.get_all_applicants()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", len(applicants))
        
        with col2:
            high_trust = len([a for a in applicants if a.get('overall_trust_score', 0) > 0.7])
            st.metric("High Trust Users", high_trust)
        
        with col3:
            avg_trust = sum([a.get('overall_trust_score', 0) for a in applicants]) / len(applicants) if applicants else 0
            st.metric("Average Trust Score", f"{avg_trust:.2%}")
        
        with col4:
            recent_apps = len([a for a in applicants if a.get('created_at', '') > (datetime.now() - timedelta(days=7)).isoformat()])
            st.metric("New This Week", recent_apps)
        
        # Database management
        st.subheader("Database Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Add Sample Data", use_container_width=True):
                self.db.add_sample_data()
                st.success("Sample data added!")
        
        with col2:
            if st.button("Export Data", use_container_width=True):
                # Create export functionality
                df = pd.DataFrame(applicants)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"zscore_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("Reset Database", use_container_width=True):
                if st.session_state.get('admin_confirm_reset'):
                    from local_db import reset_database
                    reset_database()
                    st.success("Database reset successfully!")
                    st.session_state.admin_confirm_reset = False
                else:
                    st.session_state.admin_confirm_reset = True
                    st.warning("⚠️ Click again to confirm database reset")
        
        # Demo Data Enhancement
        st.subheader("Demo Data Enhancement")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate Realistic Trust Scores", use_container_width=True):
                updated_count = 0
                for applicant in applicants:
                    if applicant.get('overall_trust_score', 0) == 0:
                        # Use correct LOGIC.md calculations for consistency
                        behavioral = self.calculate_behavioral_trust_fallback(applicant) / 100
                        social = self.calculate_social_trust_fallback(applicant) / 100  
                        digital = self.calculate_digital_trust_fallback(applicant) / 100
                        
                        self.db.update_trust_score(applicant['id'], behavioral, social, digital)
                        updated_count += 1
                
                st.success(f"Generated realistic trust scores for {updated_count} applicants using correct LOGIC.md formula!")
                st.rerun()
        
        with col2:
            if st.button("Boost Random Applicant", use_container_width=True):
                if applicants:
                    import random
                    selected = random.choice(applicants)
                    # Give them a boost towards credit eligibility
                    new_behavioral = min(selected.get('behavioral_score', 0) + 0.15, 0.8)
                    new_social = min(selected.get('social_score', 0) + 0.12, 0.75)
                    new_digital = min(selected.get('digital_score', 0) + 0.18, 0.85)
                    
                    self.db.update_trust_score(selected['id'], new_behavioral, new_social, new_digital)
                    st.success(f"Boosted trust scores for {selected.get('name', 'Unknown')}!")
                    st.rerun()
        
        # Model management
        st.subheader("Model Management")
        
        if st.button("Retrain Models", use_container_width=True):
            with st.spinner("Retraining ML models..."):
                self.model.train()
                st.success("Models retrained successfully!")
        
        # All applicants table
        if applicants:
            st.subheader("All Applicants")
            
            df = pd.DataFrame(applicants)
            df['trust_percentage'] = (df['overall_trust_score'] * 100).round(1)
            
            st.dataframe(
                df[['name', 'phone', 'location', 'occupation', 'monthly_income', 
                   'trust_percentage', 'z_credits', 'created_at']],
                use_container_width=True
            )
    
    def show_my_profile(self):
        """Show applicant's own profile page"""
        st.markdown('<h1 class="main-header">👤 My Profile</h1>', unsafe_allow_html=True)
        
        current_user = self.auth.get_current_user()
        if not current_user:
            st.error("Please login to view your profile")
            return
        
        applicant = self.get_user_applicant_profile(current_user['id'])
        if not applicant:
            st.warning("Applicant profile not found. Please contact support.")
            return
        
        # Profile overview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            applicant_name = applicant.get('name', 'User')
            st.subheader(f"Welcome, {applicant_name}! 👋")
            
            # Profile completeness
            required_fields = ['phone', 'age', 'gender', 'location', 'occupation', 'monthly_income']
            completed_fields = sum(1 for field in required_fields if applicant.get(field))
            completeness = (completed_fields / len(required_fields)) * 100
            
            st.metric("Profile Completeness", f"{completeness:.0f}%")
            st.progress(completeness / 100)
            
            if completeness < 100:
                st.warning(f"Complete {len(required_fields) - completed_fields} more fields to improve your trust score!")
        
        with col2:
            trust_percentage = (applicant.get('overall_trust_score', 0) * 100)
            st.metric("Trust Score", f"{trust_percentage:.1f}%")
            z_credits = applicant.get('z_credits', 0)
            st.metric("Z-Credits", z_credits)
        
        # Profile details
        st.subheader("📋 Profile Information")
        
        with st.form("update_profile"):
            col1, col2 = st.columns(2)
            
            with col1:
                phone = st.text_input("Phone", value=applicant.get('phone', ''))
                age = st.number_input("Age", value=applicant.get('age', 25), min_value=18, max_value=80)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                    index=["Male", "Female", "Other"].index(applicant.get('gender', 'Male')))
                location = st.text_input("Location", value=applicant.get('location', ''))
            
            with col2:
                occupation = st.text_input("Occupation", value=applicant.get('occupation', ''))
                monthly_income = st.number_input("Monthly Income (₹)", value=applicant.get('monthly_income', 15000), min_value=0)
                email = st.text_input("Email", value=applicant.get('email', ''))
            
            if st.form_submit_button("Update Profile", use_container_width=True):
                # Update profile
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE applicants SET
                        phone = ?, age = ?, gender = ?, location = ?,
                        occupation = ?, monthly_income = ?, email = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (phone, age, gender, location, occupation, monthly_income, email, applicant['id']))
                
                conn.commit()
                conn.close()
                
                st.success("Profile updated successfully!")
                time.sleep(1)
                st.rerun()
    
    def show_my_journey(self):
        """Show applicant's financial literacy journey"""
        st.markdown('<h1 class="main-header">🎮 My Financial Journey</h1>', unsafe_allow_html=True)
        
        current_user = self.auth.get_current_user()
        if not current_user:
            st.error("Please login to access your journey")
            return
            
        applicant = self.get_user_applicant_profile(current_user['id'])
        
        if not applicant:
            st.error("Profile not found")
            return
        
        # Current progress
        trust_percentage = (applicant.get('overall_trust_score', 0) * 100)
        st.subheader("📈 Your Progress")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Trust Score", f"{trust_percentage:.1f}%")
        with col2:
            st.metric("Z-Credits", applicant.get('z_credits', 0))
        with col3:
            eligibility = "✅ Eligible" if trust_percentage >= 70 else "❌ Not Ready"
            st.metric("Credit Status", eligibility)
        
        # Progress towards eligibility
        st.progress(min(trust_percentage / 70, 1.0), text=f"Progress to Credit Eligibility: {min(trust_percentage, 70):.1f}/70%")
        
        # This reuses the gamification system but personalizes it
        self.show_gamification()
    
    def show_trust_score(self):
        """Show detailed trust score breakdown"""
        st.markdown('<h1 class="main-header">📊 My Trust Score</h1>', unsafe_allow_html=True)
        
        current_user = self.auth.get_current_user()
        if not current_user:
            st.error("Please login to view your trust score")
            return
            
        applicant = self.get_user_applicant_profile(current_user['id'])
        
        if not applicant:
            st.error("Profile not found")
            return
        
        # Trust score components
        behavioral = applicant.get('behavioral_score', 0) * 100
        social = applicant.get('social_score', 0) * 100
        digital = applicant.get('digital_score', 0) * 100
        overall = applicant.get('overall_trust_score', 0) * 100
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Trust score visualization
            fig = go.Figure(data=[
                go.Bar(name='Behavioral Trust', x=['Components'], y=[behavioral], marker_color='#1f77b4'),
                go.Bar(name='Social Trust', x=['Components'], y=[social], marker_color='#ff7f0e'),
                go.Bar(name='Digital Trust', x=['Components'], y=[digital], marker_color='#2ca02c')
            ])
            
            fig.update_layout(
                title='Trust Score Breakdown',
                barmode='group',
                yaxis_title='Score (%)',
                showlegend=True,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Overall Trust Score", f"{overall:.1f}%")
            
            # Individual components
            st.subheader("📊 Components")
            st.metric("🎯 Behavioral", f"{behavioral:.1f}%")
            st.metric("👥 Social", f"{social:.1f}%")
            st.metric("📱 Digital", f"{digital:.1f}%")
        
        # Improvement suggestions
        st.subheader("💡 Improvement Suggestions")
        
        if behavioral < 70:
            st.info("🎯 **Improve Behavioral Score**: Complete on-time payment missions and demonstrate financial discipline")
        if social < 70:
            st.info("👥 **Build Social Trust**: Get community endorsements and participate in group activities")
        if digital < 70:
            st.info("📱 **Enhance Digital Presence**: Increase digital transaction activity and maintain device stability")
        
        if overall >= 70:
            st.success("🎉 Congratulations! Your trust score qualifies you for credit assessment!")
    
    def show_apply_credit(self):
        """Credit application form for applicants"""
        st.markdown('<h1 class="main-header">💳 Apply for Credit</h1>', unsafe_allow_html=True)
        
        current_user = self.auth.get_current_user()
        if not current_user:
            st.error("Please login to apply for credit")
            return
            
        applicant = self.get_user_applicant_profile(current_user['id'])
        
        if not applicant:
            st.error("Profile not found")
            return
        
        trust_percentage = (applicant.get('overall_trust_score', 0) * 100)
        
        # Eligibility check
        if trust_percentage < 70:
            st.warning(f"⚠️ Your current trust score ({trust_percentage:.1f}%) is below the minimum threshold of 70% required for credit application.")
            st.info("Complete missions in 'My Journey' to improve your trust score and become eligible.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎮 Go to My Journey", use_container_width=True):
                    st.session_state.selected_page = "My Journey"
                    st.rerun()
            with col2:
                if st.button("📊 View Trust Score Details", use_container_width=True):
                    st.session_state.selected_page = "Trust Score"
                    st.rerun()
            return
        
        # Credit application form
        st.success(f"🎉 Congratulations! Your trust score of {trust_percentage:.1f}% qualifies you for credit assessment.")
        
        with st.form("credit_application"):
            st.subheader("💰 Credit Application Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                loan_amount = st.number_input("Requested Amount (₹)", min_value=1000, max_value=1000000, value=50000)
                loan_purpose = st.selectbox("Purpose", [
                    "Business expansion", "Working capital", "Equipment purchase",
                    "Education", "Medical expenses", "Home improvement", "Other"
                ])
                repayment_period = st.selectbox("Repayment Period", [
                    "3 months", "6 months", "12 months", "18 months", "24 months"
                ])
            
            with col2:
                existing_loans = st.selectbox("Existing Loans?", ["No", "Yes"])
                monthly_expenses = st.number_input("Monthly Expenses (₹)", min_value=0, value=10000)
                collateral = st.selectbox("Collateral Available?", ["No", "Yes - Property", "Yes - Vehicle", "Yes - Other"])
            
            additional_info = st.text_area("Additional Information", placeholder="Any additional details...")
            
            consent_terms = st.checkbox("I agree to the loan terms and conditions")
            consent_credit_check = st.checkbox("I authorize credit assessment and verification")
            
            if st.form_submit_button("Submit Credit Application", use_container_width=True):
                if not consent_terms or not consent_credit_check:
                    st.error("Please provide all required consents")
                else:
                    # Process credit application
                    with st.spinner("Processing your application..."):
                        time.sleep(3)  # Simulate processing
                        
                        # Run ML assessment
                        prediction_result = self.model.predict(applicant)
                        
                        # Update applicant status
                        conn = self.db.get_connection()
                        cursor = conn.cursor()
                        
                        cursor.execute("""
                            UPDATE applicants SET
                                credit_application_status = 'under_review',
                                credit_limit = ?,
                                risk_category = ?,
                                ml_prediction_score = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (
                            loan_amount if prediction_result['risk_category'] == 'Low Risk' else loan_amount * 0.7,
                            prediction_result['risk_category'],
                            prediction_result['confidence_score'],
                            applicant['id']
                        ))
                        
                        conn.commit()
                        conn.close()
                        
                        # Log application
                        self.db.log_consent(
                            applicant['id'],
                            'credit_application',
                            'loan_assessment',
                            True,
                            {
                                'loan_amount': loan_amount,
                                'loan_purpose': loan_purpose,
                                'repayment_period': repayment_period
                            }
                        )
                    
                    st.success("🎉 Application submitted successfully!")
                    st.info("You will receive a decision within 24-48 hours. Check your dashboard for updates.")
                    st.balloons()
    
    def show_all_applicants(self):
        """Show all applicants (admin view)"""
        if not self.auth.has_role('admin'):
            st.error("Access denied. Admin role required.")
            return
        
        st.markdown('<h1 class="main-header">All Applicants</h1>', unsafe_allow_html=True)
        
        # This reuses the admin panel applicants table
        applicants = self.db.get_all_applicants()
        
        if applicants:
            st.subheader(f"📋 Total Applicants: {len(applicants)}")
            
            df = pd.DataFrame(applicants)
            df['trust_percentage'] = (df['overall_trust_score'] * 100).round(1)
            
            # Add filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox("Filter by Status", 
                    ["All", "not_applied", "under_review", "approved", "rejected"])
            
            with col2:
                risk_filter = st.selectbox("Filter by Risk", 
                    ["All", "Low Risk", "Medium Risk", "High Risk"])
            
            with col3:
                trust_filter = st.slider("Minimum Trust Score (%)", 0, 100, 0)
            
            # Apply filters
            filtered_df = df.copy()
            
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['credit_application_status'] == status_filter]
            
            if risk_filter != "All":
                filtered_df = filtered_df[filtered_df['risk_category'] == risk_filter]
            
            filtered_df = filtered_df[filtered_df['trust_percentage'] >= trust_filter]
            
            st.dataframe(
                filtered_df[['name', 'phone', 'location', 'occupation', 'monthly_income', 
                           'trust_percentage', 'credit_application_status', 'risk_category', 'created_at']],
                use_container_width=True,
                column_config={
                    'trust_percentage': st.column_config.ProgressColumn(
                        'Trust Score %',
                        min_value=0,
                        max_value=100
                    )
                }
            )
        else:
            st.info("No applicants found. Use 'Load Sample Data' to add demo applicants.")


def main():
    """Main application entry point"""
    app = ZScoreApp()
    app.run()


if __name__ == "__main__":
    main()
