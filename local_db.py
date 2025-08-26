"""
Local Database Management for Z-Score Credit Assessment System

Handles SQLite database operations including user management, applicant data,
consent tracking, and compliance logging for DPDPA compliance.
"""

import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import bcrypt


class Database:
    """Main database class for Z-Score application"""
    
    def __init__(self, db_path: str = "data/applicants.db"):
        self.db_path = db_path
        self.initialize_database()
    
    def get_connection(self):
        """Get database connection with foreign key support"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_database(self):
        """Initialize all required database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table for authentication
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Applicants table for credit assessment
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applicants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                email TEXT,
                age INTEGER,
                gender TEXT,
                location TEXT,
                occupation TEXT,
                monthly_income REAL,
                
                -- Trust Score Components
                behavioral_score REAL DEFAULT 0.0,
                social_score REAL DEFAULT 0.0,
                digital_score REAL DEFAULT 0.0,
                overall_trust_score REAL DEFAULT 0.0,
                
                -- Alternative Data Features
                utility_payment_history TEXT, -- JSON
                mfi_loan_history TEXT, -- JSON
                social_proof_data TEXT, -- JSON
                digital_footprint TEXT, -- JSON
                
                -- Credit Application Status
                credit_application_status TEXT DEFAULT 'not_applied',
                credit_limit REAL,
                risk_category TEXT,
                ml_prediction_score REAL,
                
                -- Gamification
                z_credits INTEGER DEFAULT 0,
                missions_completed TEXT, -- JSON
                achievements TEXT, -- JSON
                
                -- Compliance
                consent_data TEXT, -- JSON
                consent_timestamp TIMESTAMP,
                data_sharing_agreements TEXT, -- JSON
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Consent tracking for DPDPA compliance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                applicant_id INTEGER NOT NULL,
                consent_type TEXT NOT NULL,
                purpose TEXT NOT NULL,
                granted BOOLEAN NOT NULL,
                consent_data TEXT, -- JSON
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                withdrawn_at TIMESTAMP,
                
                FOREIGN KEY (applicant_id) REFERENCES applicants (id)
            )
        """)
        
        # ML model predictions log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                applicant_id INTEGER NOT NULL,
                model_version TEXT NOT NULL,
                input_features TEXT, -- JSON
                prediction_score REAL,
                risk_probability REAL,
                shap_explanation TEXT, -- JSON
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (applicant_id) REFERENCES applicants (id)
            )
        """)
        
        # Gamification activities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gamification_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                applicant_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                activity_data TEXT, -- JSON
                z_credits_earned INTEGER DEFAULT 0,
                trust_score_impact REAL DEFAULT 0.0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (applicant_id) REFERENCES applicants (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Create default admin user
        self.create_default_admin()
    
    def create_default_admin(self):
        """Create default admin user if not exists"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
        if not cursor.fetchone():
            password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, ("admin", password_hash.decode('utf-8'), "admin"))
            conn.commit()
        
        conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, password_hash, role, is_active
            FROM users WHERE username = ? AND is_active = 1
        """, (username,))
        
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            # Update last login
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (user['id'],))
            conn.commit()
            conn.close()
            
            return {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        
        conn.close()
        return None
    
    def create_applicant(self, applicant_data: Dict) -> Optional[int]:
        """Create new applicant record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO applicants (
                user_id, name, phone, email, age, gender, location, 
                occupation, monthly_income
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            applicant_data.get('user_id'),
            applicant_data['name'],
            applicant_data['phone'],
            applicant_data.get('email'),
            applicant_data.get('age'),
            applicant_data.get('gender'),
            applicant_data.get('location'),
            applicant_data.get('occupation'),
            applicant_data.get('monthly_income')
        ))
        
        applicant_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return applicant_id
    
    def update_trust_score(self, applicant_id: int, behavioral: float, 
                          social: float, digital: float) -> None:
        """Update trust score components"""
        overall_score = (behavioral + social + digital) / 3
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE applicants SET
                behavioral_score = ?,
                social_score = ?,
                digital_score = ?,
                overall_trust_score = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (behavioral, social, digital, overall_score, applicant_id))
        
        conn.commit()
        conn.close()
    
    def log_consent(self, applicant_id: int, consent_type: str, 
                   purpose: str, granted: bool, consent_data: Optional[Dict] = None) -> None:
        """Log consent for DPDPA compliance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO consent_logs (
                applicant_id, consent_type, purpose, granted, consent_data
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            applicant_id, consent_type, purpose, granted,
            json.dumps(consent_data) if consent_data else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_applicant(self, applicant_id: int) -> Optional[Dict]:
        """Get applicant details by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM applicants WHERE id = ?", (applicant_id,))
        applicant = cursor.fetchone()
        conn.close()
        
        if applicant:
            return dict(applicant)
        return None
    
    def get_all_applicants(self) -> List[Dict]:
        """Get all applicants"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM applicants ORDER BY created_at DESC")
        applicants = cursor.fetchall()
        conn.close()
        
        return [dict(applicant) for applicant in applicants]
    
    def add_sample_data(self):
        """Add sample data for demo purposes"""
        sample_applicants = [
            {
                'name': 'Priya Sharma',
                'phone': '+91-9876543210',
                'email': 'priya@example.com',
                'age': 28,
                'gender': 'Female',
                'location': 'Rajasthan, India',
                'occupation': 'Handicraft Artisan',
                'monthly_income': 15000.0
            },
            {
                'name': 'Raj Kumar',
                'phone': '+91-9876543211',
                'email': 'raj@example.com',
                'age': 35,
                'gender': 'Male',
                'location': 'Punjab, India',
                'occupation': 'Small Farmer',
                'monthly_income': 20000.0
            }
        ]
        
        for applicant_data in sample_applicants:
            try:
                applicant_id = self.create_applicant(applicant_data)
                if applicant_id is not None:
                    # Add some trust score progression
                    self.update_trust_score(applicant_id, 0.3, 0.25, 0.2)
                    
                    # Log sample consent
                    self.log_consent(
                        applicant_id, 
                        'data_collection', 
                        'credit_assessment', 
                        True,
                        {'ip_address': '127.0.0.1', 'user_agent': 'Demo Browser'}
                    )
            except sqlite3.IntegrityError:
                # Skip if already exists
                pass


def initialize_database():
    """Initialize database with tables and sample data"""
    import os
    os.makedirs("data", exist_ok=True)
    db = Database()
    print("Database initialized successfully!")
    return db


def reset_database():
    """Reset database for testing"""
    import os
    if os.path.exists("data/applicants.db"):
        os.remove("data/applicants.db")
    return initialize_database()


def add_sample_data():
    """Add sample data to existing database"""
    db = Database()
    db.add_sample_data()
    print("Sample data added successfully!")


if __name__ == "__main__":
    # Initialize database if run directly
    initialize_database()
