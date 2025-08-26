"""
Authentication system for Z-Score Credit Assessment Application

Handles user authentication, session management, and role-based access control
with security features for production deployment.
"""

import streamlit as st
import bcrypt
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
        """Display login form"""
        st.title("🔐 Z-Score Login")
        
        with st.form("login_form"):
            st.subheader("Authentication Required")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if self.login(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        # Show demo credentials
        with st.expander("Demo Credentials"):
            st.info("""
            **Default Admin Login:**
            - Username: admin
            - Password: admin123
            
            This is a demo application for the PSB FinTech Hackathon 2025.
            """)
    
    def show_user_info(self):
        """Display current user information in sidebar"""
        if self.is_authenticated():
            user = self.get_current_user()
            if user:
                with st.sidebar:
                    st.success(f"👤 Logged in as: **{user['username']}**")
                    st.info(f"🎭 Role: **{user['role'].title()}**")
                    
                    if st.button("🚪 Logout", use_container_width=True):
                        self.logout()


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
