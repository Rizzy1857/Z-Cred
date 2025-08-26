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

# Page configuration
st.set_page_config(
    page_title="Z-Score Credit Assessment",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimalistic
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #stDecoration {display:none;}
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #2c3e50;
    }
    
    /* Content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        margin: 1rem;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.2rem;
        font-weight: 300;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: -0.5px;
    }
    
    h1, h2, h3 {
        font-weight: 300;
        color: #2c3e50;
        letter-spacing: -0.3px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 0 20px 20px 0;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 400;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Form inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border: 1px solid #e1e8ed;
        border-radius: 12px;
        padding: 0.75rem;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.8);
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Metrics */
    .metric-container {
        background: rgba(255, 255, 255, 0.8);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(230, 230, 230, 0.5);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(230, 230, 230, 0.5);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Cards */
    .card {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(230, 230, 230, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
    }
    
    /* Status indicators */
    .status-low {
        color: #27ae60;
        font-weight: 500;
        padding: 0.3rem 0.8rem;
        background: rgba(39, 174, 96, 0.1);
        border-radius: 20px;
        font-size: 0.85rem;
    }
    
    .status-medium {
        color: #f39c12;
        font-weight: 500;
        padding: 0.3rem 0.8rem;
        background: rgba(243, 156, 18, 0.1);
        border-radius: 20px;
        font-size: 0.85rem;
    }
    
    .status-high {
        color: #e74c3c;
        font-weight: 500;
        padding: 0.3rem 0.8rem;
        background: rgba(231, 76, 60, 0.1);
        border-radius: 20px;
        font-size: 0.85rem;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 12px;
        padding: 0.3rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 400;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Success/Info/Warning messages */
    .stSuccess, .stInfo, .stWarning {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.8);
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
            st.subheader("📋 Personal Information")
            
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
            
            st.subheader("🎯 Your Credit Goals")
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
                    
                    st.success("🎉 Profile completed successfully!")
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
        """Show main navigation menu"""
        with st.sidebar:
            # Clean header
            st.markdown("### Navigation")
            
            current_user = self.auth.get_current_user()
            is_admin = current_user and current_user['role'] == 'admin'
            is_applicant = current_user and current_user['role'] == 'applicant'
            
            # Simplified navigation
            if is_admin:
                nav_items = [
                    ("📊", "Dashboard", "Dashboard"),
                    ("👤", "New User", "New Applicant"),
                    ("🔍", "Assess Risk", "Risk Assessment"),
                    ("👥", "All Users", "All Applicants"),
                    ("⚙️", "Settings", "Admin Panel")
                ]
            elif is_applicant:
                nav_items = [
                    ("📊", "Dashboard", "Dashboard"),
                    ("👤", "My Profile", "My Profile"),
                    ("🎯", "My Journey", "My Journey"),
                    ("📈", "Trust Score", "Trust Score"),
                    ("💳", "Apply Credit", "Apply for Credit")
                ]
            else:
                nav_items = [("📊", "Dashboard", "Dashboard")]
            
            # Clean button layout
            for icon, label, page_key in nav_items:
                if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{page_key}"):
                    st.session_state.selected_page = page_key
                    st.rerun()
            
            st.markdown("---")
            st.subheader("🎯 Navigation")
            
            pages = [
                ("📊 Dashboard", "Dashboard"),
                ("👤 New Applicant", "New Applicant"),
                ("🔍 Risk Assessment", "Risk Assessment"),
                ("🎮 Gamification", "Gamification"),
                ("📋 Compliance", "Compliance"),
                ("⚙️ Admin Panel", "Admin Panel")
            ]
            
            for page_label, page_key in pages:
                if st.button(page_label, use_container_width=True):
                    st.session_state.selected_page = page_key
                    st.rerun()
            
            st.markdown("---")
            
            # Demo controls
            st.subheader("🚀 Demo Controls")
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
    
    def route_to_page(self, page: str):
        """Route to selected page"""
        if page == "Dashboard":
            self.show_dashboard()
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
    
    def show_dashboard(self):
        """Main dashboard page - minimalistic design"""
        st.markdown('<h1 class="main-header">Z-Score Dashboard</h1>', unsafe_allow_html=True)
        
        # Clean metrics row
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
        
        # Recent applications
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
        
        # Trust score distribution
        if scored_applicants:
            st.subheader("📊 Trust Score Distribution")
            
            trust_scores = [a.get('overall_trust_score', 0) * 100 for a in scored_applicants]
            
            fig = px.histogram(
                x=trust_scores,
                nbins=20,
                title="Distribution of Trust Scores",
                labels={'x': 'Trust Score (%)', 'y': 'Number of Applicants'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
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
            st.subheader(f"Assessment for {applicant['name']}")
            
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
            st.write(f"**Phone:** {applicant['phone']}")
            st.write(f"**Age:** {applicant['age']}")
            st.write(f"**Location:** {applicant['location']}")
            st.write(f"**Occupation:** {applicant['occupation']}")
            st.write(f"**Monthly Income:** ₹{applicant['monthly_income']:,.0f}")
        
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
                        st.metric("Default Probability", f"{prediction_result['risk_probability']:.1%}")
                    
                    with col3:
                        st.metric("Confidence Score", f"{prediction_result['confidence_score']:.1%}")
                    
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
                                text=[f"{v:.3f}" for v in shap_values],
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
        
        # Trust progression bar
        st.subheader("Trust Progression")
        
        progress_val = trust_percentage / 100
        st.progress(progress_val, text=f"Trust Score: {trust_percentage:.1f}% (Threshold: 70%)")
        
        if trust_percentage < 70:
            remaining = 70 - trust_percentage
            st.info(f"📈 You need {remaining:.1f}% more to become credit eligible!")
        else:
            st.success("Congratulations! You are eligible for credit assessment!")
        
        # Available missions
        st.subheader("Available Missions")
        
        missions = [
            {
                'title': 'Financial Literacy Quiz',
                'description': 'Complete basic financial literacy assessment',
                'reward': '+15% Trust Score, 50 Z-Credits',
                'type': 'quiz'
            },
            {
                'title': 'Pay Utility Bill On Time',
                'description': 'Submit proof of on-time utility payment',
                'reward': '+20% Trust Score, 75 Z-Credits',
                'type': 'payment'
            },
            {
                'title': 'Get Community Endorsement',
                'description': 'Obtain endorsement from community leader',
                'reward': '+25% Trust Score, 100 Z-Credits',
                'type': 'social'
            },
            {
                'title': 'Connect Bank Account',
                'description': 'Provide consent for bank transaction history',
                'reward': '+30% Trust Score, 150 Z-Credits',
                'type': 'data'
            }
        ]
        
        for i, mission in enumerate(missions):
            with st.expander(f"Mission {i+1}: {mission['title']}"):
                st.write(mission['description'])
                st.success(f"**Reward:** {mission['reward']}")
                
                if st.button(f"Complete Mission {i+1}", key=f"mission_{i}"):
                    # Simulate mission completion
                    with st.spinner("Processing mission..."):
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
                    
                    st.success(f"🎉 Mission completed! +{credits_earned} Z-Credits earned!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
        
        # Achievement showcase
        st.subheader("🏆 Achievements")
        
        achievements = []
        if trust_percentage >= 30:
            achievements.append("🌱 First Steps - Reached 30% Trust")
        if trust_percentage >= 50:
            achievements.append("Growing Trust - Reached 50% Trust")
        if trust_percentage >= 70:
            achievements.append("Credit Ready - Reached 70% Trust")
        if z_credits >= 100:
            achievements.append("Credit Collector - Earned 100+ Z-Credits")
        
        if achievements:
            for achievement in achievements:
                st.success(achievement)
        else:
            st.info("Complete missions to unlock achievements!")
    
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
            st.subheader(f"Welcome, {applicant['name']}! 👋")
            
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
        
        st.markdown('<h1 class="main-header">👥 All Applicants</h1>', unsafe_allow_html=True)
        
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
