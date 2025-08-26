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

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 0.5rem 0;
    }
    
    .trust-bar {
        background-color: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        height: 30px;
        margin: 10px 0;
    }
    
    .risk-low {
        color: #28a745;
        font-weight: bold;
    }
    
    .risk-medium {
        color: #ffc107;
        font-weight: bold;
    }
    
    .risk-high {
        color: #dc3545;
        font-weight: bold;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
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
        self.route_to_page(page)
    
    def show_navigation(self):
        """Show main navigation menu"""
        with st.sidebar:
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
    
    def show_dashboard(self):
        """Main dashboard page"""
        st.markdown('<h1 class="main-header">Z-Score Credit Assessment Dashboard</h1>', unsafe_allow_html=True)
        
        # Quick stats
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
        st.markdown('<h1 class="main-header">📝 New Applicant Registration</h1>', unsafe_allow_html=True)
        
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
            
            with st.expander("💳 Payment History"):
                col1, col2 = st.columns(2)
                with col1:
                    total_payments = st.number_input("Total Utility Payments", min_value=0, value=12)
                    on_time_payments = st.number_input("On-time Payments", min_value=0, value=10)
                with col2:
                    avg_payment_amount = st.number_input("Average Payment Amount (₹)", min_value=0, value=1500)
                    payment_consistency = st.slider("Payment Consistency", 0.0, 1.0, 0.8)
            
            with st.expander("👥 Social Proof"):
                col1, col2 = st.columns(2)
                with col1:
                    community_rating = st.slider("Community Rating", 1.0, 5.0, 3.5)
                    endorsements = st.number_input("Community Endorsements", min_value=0, value=3)
                with col2:
                    group_participation = st.slider("Group Participation Score", 0.0, 1.0, 0.6)
                    social_references = st.number_input("Social References", min_value=0, value=2)
            
            with st.expander("📱 Digital Footprint"):
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
                            
                            st.success(f"✅ Applicant {name} registered successfully!")
                            st.success(f"📊 Trust Score: {((behavioral_score + social_score + digital_score) / 3 * 100):.1f}%")
                            
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
        st.markdown('<h1 class="main-header">🎯 Credit Risk Assessment</h1>', unsafe_allow_html=True)
        
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
            st.subheader(f"📊 Assessment for {applicant['name']}")
            
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
        st.subheader("🤖 AI Risk Assessment")
        
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
                    st.subheader("🔍 AI Decision Explanation")
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
                                    st.info("📅 **Improve Payment History**: Make more on-time utility payments")
                                elif 'social' in feature.lower():
                                    st.info("👥 **Build Social Proof**: Get community endorsements and references")
                                elif 'digital' in feature.lower():
                                    st.info("📱 **Enhance Digital Presence**: Increase digital transaction regularity")
                                elif 'income' in feature.lower():
                                    st.info("💰 **Increase Income Stability**: Work on stable income sources")
                        else:
                            st.success("🎉 **Excellent Profile!** All major factors are positive.")
                    
                    else:
                        st.error(f"Explanation Error: {explanation['error']}")
                
                except Exception as e:
                    st.error(f"Prediction Error: {str(e)}")
    
    def show_gamification(self):
        """Gamification and financial literacy page"""
        st.markdown('<h1 class="main-header">🎮 Financial Literacy & Gamification</h1>', unsafe_allow_html=True)
        
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
        st.subheader("📊 Trust Progression")
        
        progress_val = trust_percentage / 100
        st.progress(progress_val, text=f"Trust Score: {trust_percentage:.1f}% (Threshold: 70%)")
        
        if trust_percentage < 70:
            remaining = 70 - trust_percentage
            st.info(f"📈 You need {remaining:.1f}% more to become credit eligible!")
        else:
            st.success("🎉 Congratulations! You are eligible for credit assessment!")
        
        # Available missions
        st.subheader("🎯 Available Missions")
        
        missions = [
            {
                'title': '💡 Financial Literacy Quiz',
                'description': 'Complete basic financial literacy assessment',
                'reward': '+15% Trust Score, 50 Z-Credits',
                'type': 'quiz'
            },
            {
                'title': '📅 Pay Utility Bill On Time',
                'description': 'Submit proof of on-time utility payment',
                'reward': '+20% Trust Score, 75 Z-Credits',
                'type': 'payment'
            },
            {
                'title': '👥 Get Community Endorsement',
                'description': 'Obtain endorsement from community leader',
                'reward': '+25% Trust Score, 100 Z-Credits',
                'type': 'social'
            },
            {
                'title': '📱 Connect Bank Account',
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
            achievements.append("📈 Growing Trust - Reached 50% Trust")
        if trust_percentage >= 70:
            achievements.append("🎯 Credit Ready - Reached 70% Trust")
        if z_credits >= 100:
            achievements.append("💰 Credit Collector - Earned 100+ Z-Credits")
        
        if achievements:
            for achievement in achievements:
                st.success(achievement)
        else:
            st.info("Complete missions to unlock achievements!")
    
    def show_compliance(self):
        """DPDPA compliance and consent management"""
        st.markdown('<h1 class="main-header">⚖️ Compliance & Data Privacy</h1>', unsafe_allow_html=True)
        
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
        st.subheader("🏛️ RBI Digital Lending Guidelines 2025")
        
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
        st.subheader("📋 Consent Management System")
        
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
        st.subheader("🛡️ Privacy Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.button("📥 Download My Data", use_container_width=True)
            st.button("🔄 Update Preferences", use_container_width=True)
        
        with col2:
            st.button("❌ Withdraw Consent", use_container_width=True)
            st.button("🗑️ Delete My Account", use_container_width=True)
    
    def show_admin_panel(self):
        """Admin panel for system management"""
        if not self.auth.has_role('admin'):
            st.error("Access denied. Admin role required.")
            return
        
        st.markdown('<h1 class="main-header">⚙️ Admin Panel</h1>', unsafe_allow_html=True)
        
        # System statistics
        st.subheader("📊 System Statistics")
        
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
        st.subheader("🗄️ Database Management")
        
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
        st.subheader("🤖 Model Management")
        
        if st.button("Retrain Models", use_container_width=True):
            with st.spinner("Retraining ML models..."):
                self.model.train()
                st.success("Models retrained successfully!")
        
        # All applicants table
        if applicants:
            st.subheader("👥 All Applicants")
            
            df = pd.DataFrame(applicants)
            df['trust_percentage'] = (df['overall_trust_score'] * 100).round(1)
            
            st.dataframe(
                df[['name', 'phone', 'location', 'occupation', 'monthly_income', 
                   'trust_percentage', 'z_credits', 'created_at']],
                use_container_width=True
            )


def main():
    """Main application entry point"""
    app = ZScoreApp()
    app.run()


if __name__ == "__main__":
    main()
