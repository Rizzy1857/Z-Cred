"""
Local Database Management for Z-Score Credit Assessment System

Handles SQLite database operations including user management, applicant data,
consent tracking, and compliance logging for DPDPA compliance.

Enhanced with transaction retries, proper locking, and uniqueness handling.
"""

import sqlite3
import hashlib
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable, Any
import bcrypt
from contextlib import contextmanager
import threading


class DatabaseException(Exception):
    """Custom exception for database operations"""
    pass


class TransactionRetryException(DatabaseException):
    """Exception for retryable transaction errors"""
    pass


class Database:
    """Main database class for Z-Score application with enhanced transaction handling"""
    
    def __init__(self, db_path: str = "data/applicants.db"):
        self.db_path = db_path
        self._connection_lock = threading.Lock()
        self.max_retries = 3
        self.retry_delay_base = 0.1  # Base delay in seconds
        self.initialize_database()
    
    @contextmanager
    def get_connection(self, timeout: float = 30.0):
        """Get database connection with proper timeout and lock handling"""
        with self._connection_lock:
            conn = None
            try:
                conn = sqlite3.connect(self.db_path, timeout=timeout)
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
                conn.execute("PRAGMA synchronous = NORMAL")  # Better performance
                conn.execute("PRAGMA temp_store = MEMORY")  # Faster temp operations
                conn.execute("PRAGMA cache_size = 10000")  # Larger cache
                conn.row_factory = sqlite3.Row
                yield conn
            except Exception as e:
                if conn:
                    conn.rollback()
                raise DatabaseException(f"Database connection error: {e}")
            finally:
                if conn:
                    conn.close()
    
    def execute_with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute database operation with automatic retry on transient errors
        
        Args:
            operation: Function to execute
            *args, **kwargs: Arguments to pass to the operation
            
        Returns:
            Result of the operation
            
        Raises:
            DatabaseException: On persistent failures
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
                
            except sqlite3.OperationalError as e:
                last_exception = e
                error_msg = str(e).lower()
                
                # Check if this is a retryable error
                if any(retryable in error_msg for retryable in [
                    'database is locked',
                    'database table is locked', 
                    'cannot start a transaction within a transaction',
                    'disk i/o error'
                ]):
                    if attempt < self.max_retries:
                        # Exponential backoff with jitter
                        delay = self.retry_delay_base * (2 ** attempt) + random.uniform(0, 0.1)
                        time.sleep(delay)
                        continue
                    else:
                        raise TransactionRetryException(f"Max retries exceeded: {e}")
                else:
                    # Non-retryable error
                    raise DatabaseException(f"Database operation failed: {e}")
                    
            except sqlite3.IntegrityError as e:
                # Handle uniqueness violations gracefully
                if "unique" in str(e).lower():
                    raise DatabaseException(f"Unique constraint violation: {e}")
                else:
                    raise DatabaseException(f"Integrity error: {e}")
                    
            except Exception as e:
                raise DatabaseException(f"Unexpected database error: {e}")
        
        # If we get here, all retries failed
        raise TransactionRetryException(f"All retry attempts failed. Last error: {last_exception}")
    
    @contextmanager 
    def transaction(self):
        """Context manager for database transactions with proper error handling"""
        with self.get_connection() as conn:
            try:
                conn.execute("BEGIN IMMEDIATE")  # Acquire exclusive lock immediately
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise
    
    def initialize_database(self):
        """Initialize all required database tables"""
        def _init_tables():
            with self.get_connection() as conn:
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
        
        self.execute_with_retry(_init_tables)
        
        # Create default admin user
        self.create_default_admin()
        
        # Create demo user account
        self.create_demo_user()
    
    def create_default_admin(self):
        """Create default admin user if not exists"""
        def _create_admin():
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
                if not cursor.fetchone():
                    password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, role)
                        VALUES (?, ?, ?)
                    """, ("admin", password_hash.decode('utf-8'), "admin"))
                    conn.commit()
        
        try:
            self.execute_with_retry(_create_admin)
        except DatabaseException as e:
            if "unique constraint" not in str(e).lower():
                raise  # Re-raise if it's not a uniqueness issue
    
    def create_demo_user(self):
        """Create demo user account if not exists"""
        def _create_demo():
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT id FROM users WHERE username = ?", ("demo_user",))
                if not cursor.fetchone():
                    password_hash = bcrypt.hashpw("user123".encode('utf-8'), bcrypt.gensalt())
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, role)
                        VALUES (?, ?, ?)
                    """, ("demo_user", password_hash.decode('utf-8'), "applicant"))
                    
                    # Create a demo applicant profile for this user
                    user_id = cursor.lastrowid
                    cursor.execute("""
                        INSERT INTO applicants (user_id, name, phone, email, age, gender, location, occupation, monthly_income)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        "Demo User",
                        "+91-9999999999",
                        "demo@example.com",
                        25,
                        "Other",
                        "Demo City, India",
                        "Software Developer",
                        35000.0
                    ))
                    conn.commit()
        
        try:
            self.execute_with_retry(_create_demo)
        except DatabaseException as e:
            if "unique constraint" not in str(e).lower():
                raise  # Re-raise if it's not a uniqueness issue
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        def _authenticate():
            with self.get_connection() as conn:
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
                    
                    return {
                        'id': user['id'],
                        'username': user['username'],
                        'role': user['role']
                    }
                return None
        
        return self.execute_with_retry(_authenticate)
    
    def create_applicant(self, applicant_data: Dict) -> Optional[int]:
        """Create new applicant record"""
        def _create_applicant():
            with self.get_connection() as conn:
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
                return applicant_id
        
        return self.execute_with_retry(_create_applicant)
    
    def update_applicant_profile(self, user_id: int, applicant_data: Dict) -> bool:
        """Update applicant profile data"""
        def _update_applicant():
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE applicants SET
                        name = ?,
                        phone = ?,
                        email = ?,
                        age = ?,
                        gender = ?,
                        location = ?,
                        occupation = ?,
                        monthly_income = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (
                    applicant_data['name'],
                    applicant_data['phone'],
                    applicant_data.get('email'),
                    applicant_data.get('age'),
                    applicant_data.get('gender'),
                    applicant_data.get('location'),
                    applicant_data.get('occupation'),
                    applicant_data.get('monthly_income'),
                    user_id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
        
        return self.execute_with_retry(_update_applicant)
    
    def update_trust_score(self, applicant_id: int, behavioral: float, 
                          social: float, digital: float) -> None:
        """Update trust score components"""
        overall_score = (behavioral + social + digital) / 3
        
        def _update_score():
            with self.get_connection() as conn:
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
        
        self.execute_with_retry(_update_score)
    
    def log_consent(self, applicant_id: int, consent_type: str, 
                   purpose: str, granted: bool, consent_data: Optional[Dict] = None) -> None:
        """Log consent for DPDPA compliance"""
        def _log_consent():
            with self.get_connection() as conn:
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
        
        self.execute_with_retry(_log_consent)
    
    def get_applicant(self, applicant_id: int) -> Optional[Dict]:
        """Get applicant details by ID"""
        def _get_applicant():
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM applicants WHERE id = ?", (applicant_id,))
                applicant = cursor.fetchone()
                
                if applicant:
                    return dict(applicant)
                return None
        
        return self.execute_with_retry(_get_applicant)
    
    def get_all_applicants(self) -> List[Dict]:
        """Get all applicants"""
        def _get_all():
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM applicants ORDER BY created_at DESC")
                applicants = cursor.fetchall()
                
                return [dict(applicant) for applicant in applicants]
        
        return self.execute_with_retry(_get_all)
    
    def add_sample_data(self):
        """Add scenario-based sample data for demo purposes"""
        # Use the new scenario-based demo data instead of old samples
        from scripts.setup_demo_data import setup_demo_data
        try:
            setup_demo_data()
            print(" ✅ Scenario-based demo data added successfully!")
        except Exception as e:
            print(f" ❌ Error adding scenario demo data: {e}")
            # Fallback to minimal sample data
            sample_applicants = [
                {
                    'name': 'Demo User',
                    'phone': '+91-9999999999',
                    'email': 'demo@zcred.in',
                    'age': 30,
                    'gender': 'Other',
                    'location': 'India',
                    'occupation': 'Demo Applicant',
                    'monthly_income': 25000.0
                }
            ]
            
            for applicant_data in sample_applicants:
                try:
                    applicant_id = self.create_applicant(applicant_data)
                    if applicant_id is not None:
                        # Add some trust score progression
                        self.update_trust_score(applicant_id, 0.7, 0.6, 0.8)
                        
                        # Log sample consent
                        self.log_consent(
                            applicant_id, 
                            'data_collection', 
                            'credit_assessment', 
                            True,
                            {'ip_address': '127.0.0.1', 'user_agent': 'Demo Browser'}
                        )
                except DatabaseException as e:
                    if "unique constraint" not in str(e).lower():
                        print(f" ❌ Error adding sample data: {e}")
                # Skip if already exists


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
