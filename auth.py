"""
Authentication system for Z-Score Credit Assessment Application

Handles user authentication, session management, and role-based access control
with security features for production deployment.
"""

import streamlit as st
import bcrypt
import time
from typing import Optional, Dict
from local_db import Database


class AuthManager:
    """Manages authentication and session state"""
    
    def __init__(self):
        self.db = Database()
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'user_role' not in st.session_state:
            st.session_state.user_role = None
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate user login"""
        if not username or not password:
            return False
        
        user = self.db.authenticate_user(username, password)
        if user:
            st.session_state.authenticated = True
            st.session_state.user = user
            st.session_state.user_role = user['role']
            return True
        
        return False
    
    def logout(self):
        """Logout current user"""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.user_role = None
        st.rerun()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current authenticated user"""
        return st.session_state.get('user')
    
    def has_role(self, required_role: str) -> bool:
        """Check if current user has required role"""
        if not self.is_authenticated():
            return False
        
        user_role = st.session_state.get('user_role')
        if user_role == 'admin':
            return True  # Admin has all permissions
        
        return user_role == required_role
    
    def require_auth(self):
        """Decorator-like function to require authentication"""
        if not self.is_authenticated():
            self.show_login_form()
            return False
        return True
    
    def require_role(self, required_role: str):
        """Require specific role for access"""
        if not self.require_auth():
            return False
        
        if not self.has_role(required_role):
            st.error(f"Access denied. Required role: {required_role}")
            return False
        
        return True
    
    def show_login_form(self):
        """Display clean minimalistic login/signup interface"""
        # Clean welcome header
        st.markdown("""
        <div style="text-align: center; padding: 3rem 2rem;">
            <h1 style="font-size: 3rem; font-weight: 300; color: #2c3e50; margin-bottom: 1rem;">
                ⚡ Z-Score
            </h1>
            <h3 style="font-weight: 300; color: #7f8c8d; margin-bottom: 2rem;">
                Dynamic Trust-Based Credit Assessment
            </h3>
            <p style="font-size: 1.1rem; color: #95a5a6; max-width: 600px; margin: 0 auto 2rem;">
                Transform your financial future with AI-powered credit scoring that goes beyond traditional metrics. 
                Experience transparent, inclusive, and gamified financial assessment.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Center login/signup options
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Get Started")
            
            # Cleaner tabs
            tab1, tab2 = st.tabs(["🔑 Sign In", "✨ Sign Up"])
            
            with tab1:
                # Clean login form
                with st.form("login_form", clear_on_submit=False):
                    st.markdown("#### Welcome Back")
                    
                    username = st.text_input("Username", placeholder="Enter your username")
                    password = st.text_input("Password", type="password", placeholder="Enter your password")
                    
                    if st.form_submit_button("🔑 Sign In", use_container_width=True):
                        if username and password:
                            if self.login(username, password):
                                st.success("✅ Login successful!")
                                st.rerun()
                            else:
                                st.error("❌ Invalid username or password")
                        else:
                            st.warning("⚠️ Please enter both username and password")
                
                # Demo credentials in clean format
                with st.expander("🔓 Demo Access"):
                    st.markdown("""
                    **Default Admin Login:**  
                    Username: `admin`  
                    Password: `admin123`
                    
                    *Demo app for PSB FinTech Hackathon 2025*
                    """)
            
            with tab2:
                self.show_signup_form()
    
    def show_user_info(self):
        """Display current user information in sidebar"""
        if self.is_authenticated():
            user = self.get_current_user()
            if user:
                with st.sidebar:
                    # Clean user info
                    st.markdown("---")
                    st.markdown(f"**👤 {user['username']}**")
                    st.caption(f"Role: {user['role'].title()}")
                    
                    if st.button("🚪 Sign Out", use_container_width=True):
                        self.logout()
    
    def show_signup_form(self):
        """Display clean user registration form"""
        with st.form("signup_form", clear_on_submit=False):
            st.markdown("#### Create Your Account")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username", placeholder="Choose a unique username")
                new_password = st.text_input("Password", type="password", placeholder="Create secure password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            with col2:
                account_type = st.selectbox("I am a:", ["Credit Applicant", "System Admin"], 
                                          help="Choose your role")
                full_name = st.text_input("Full Name", placeholder="Enter your full name")
                email = st.text_input("Email (optional)", placeholder="your.email@example.com")
            
            # Convert account type
            account_role = "applicant" if account_type == "Credit Applicant" else "admin"
            
            # Terms and consent
            st.markdown("---")
            terms_accepted = st.checkbox("✅ I accept the Terms & Privacy Policy", help="Required for account creation")
            
            if account_role == "applicant":
                data_consent = st.checkbox("✅ I consent to credit assessment data processing", 
                                         help="Required for credit scoring functionality")
            else:
                data_consent = True
            
            # Submit button
            if st.form_submit_button("Create Account", use_container_width=True):
                # Clean validation
                if not new_username or not new_password or not full_name:
                    st.error("Please fill in all required fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif not terms_accepted:
                    st.error("Please accept Terms & Privacy Policy")
                elif account_role == "applicant" and not data_consent:
                    st.error("Credit assessment consent required for applicants")
                else:
                    # Create account
                    success = create_user(new_username, new_password, account_role)
                    if success:
                        st.success("Account created successfully!")
                        st.info("👉 Switch to Sign In tab to access your account.")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Account creation failed. Username may already exist.")


def create_user(username: str, password: str, role: str = 'user') -> bool:
    """Create new user account"""
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        """, (username, password_hash.decode('utf-8'), role))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False


def check_password_strength(password: str) -> Dict[str, bool]:
    """Check password strength"""
    checks = {
        'length': len(password) >= 8,
        'uppercase': any(c.isupper() for c in password),
        'lowercase': any(c.islower() for c in password),
        'digit': any(c.isdigit() for c in password),
        'special': any(c in '!@#$%^&*(),.?":{}|<>' for c in password)
    }
    return checks


def show_password_requirements():
    """Display password requirements"""
    st.info("""
    **Password Requirements:**
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """)


# Authentication decorator for Streamlit pages
def require_authentication(func):
    """Decorator to require authentication for Streamlit pages"""
    def wrapper(*args, **kwargs):
        auth = AuthManager()
        if auth.require_auth():
            return func(*args, **kwargs)
        return None
    return wrapper


def require_admin_role(func):
    """Decorator to require admin role for Streamlit pages"""
    def wrapper(*args, **kwargs):
        auth = AuthManager()
        if auth.require_role('admin'):
            return func(*args, **kwargs)
        return None
    return wrapper


if __name__ == "__main__":
    # Test authentication
    auth = AuthManager()
    print("Authentication system initialized!")
