"""
Demo Data Setup for Z-Score Hackathon

Creates polished demo users with compelling stories for presentation.
"""

from local_db import Database
import json
from datetime import datetime

def setup_demo_data():
    """Setup demo users with compelling stories"""
    db = Database()
    
    # Demo User 1: Sarah - Freelancer Building Credit
    sarah_data = {
        'id': 'demo_sarah',
        'name': 'Sarah Sharma',
        'phone': '+91-9876543210',
        'email': 'sarah@freelancer.in',
        'age': 28,
        'gender': 'Female',
        'location': 'Mumbai',
        'occupation': 'Freelance Designer',
        'monthly_income': 35000,
        'income': 35000,
        'employment_length': 2,
        'debt_to_income': 0.15,
        'credit_utilization': 0.25,
        'payment_history_score': 82,
        'account_diversity': 2,
        'savings_rate': 0.20,
        'education_level': 'Bachelor',
        'behavioral_score': 0.75,
        'social_score': 0.70,
        'digital_score': 0.85,
        'overall_trust_score': 0.77,
        'story': 'Freelance designer building her first credit profile',
        'demo_stage': 'improving',
        'created_at': datetime.now().isoformat()
    }
    
    # Demo User 2: Raj - Small Business Owner
    raj_data = {
        'id': 'demo_raj',
        'name': 'Raj Patel',
        'phone': '+91-9876543211',
        'email': 'raj@smallbiz.in',
        'age': 35,
        'gender': 'Male',
        'location': 'Delhi',
        'occupation': 'Small Business Owner',
        'monthly_income': 65000,
        'income': 65000,
        'employment_length': 8,
        'debt_to_income': 0.40,
        'credit_utilization': 0.60,
        'payment_history_score': 78,
        'account_diversity': 4,
        'savings_rate': 0.15,
        'education_level': 'Bachelor',
        'behavioral_score': 0.80,
        'social_score': 0.75,
        'digital_score': 0.70,
        'overall_trust_score': 0.75,
        'story': 'Small business owner seeking growth capital',
        'demo_stage': 'established',
        'created_at': datetime.now().isoformat()
    }
    
    # Demo User 3: Priya - Student Starting Journey
    priya_data = {
        'id': 'demo_priya',
        'name': 'Priya Singh',
        'phone': '+91-9876543212',
        'email': 'priya@student.in',
        'age': 22,
        'gender': 'Female',
        'location': 'Bangalore',
        'occupation': 'Student',
        'monthly_income': 12000,
        'income': 12000,
        'employment_length': 0,
        'debt_to_income': 0.05,
        'credit_utilization': 0.15,
        'payment_history_score': 95,
        'account_diversity': 1,
        'savings_rate': 0.30,
        'education_level': 'Pursuing Masters',
        'behavioral_score': 0.65,
        'social_score': 0.80,
        'digital_score': 0.90,
        'overall_trust_score': 0.78,
        'story': 'Student building first credit profile',
        'demo_stage': 'beginning',
        'created_at': datetime.now().isoformat()
    }
    
    # Store demo users
    demo_users = [sarah_data, raj_data, priya_data]
    
    for user in demo_users:
        try:
            # Store in database
            applicant_id = db.create_applicant(user)
            if applicant_id:
                print(f"✅ Created demo user: {user['name']} ({user['story']})")
            else:
                print(f"⚠️ User {user['name']} may already exist")
        except Exception as e:
            print(f"⚠️ Error creating {user['name']}: {e}")
    
    print(f"🎯 Demo data setup complete! {len(demo_users)} users ready for presentation.")
    return demo_users

def get_demo_credentials():
    """Get demo login credentials"""
    return {
        'sarah': {
            'email': 'sarah@freelancer.in',
            'password': 'demo123',
            'story': 'Freelance designer building her first credit profile'
        },
        'raj': {
            'email': 'raj@smallbiz.in', 
            'password': 'demo123',
            'story': 'Small business owner seeking growth capital'
        },
        'priya': {
            'email': 'priya@student.in',
            'password': 'demo123', 
            'story': 'Student building first credit profile'
        }
    }

if __name__ == "__main__":
    print("🎬 Setting up Z-Score Demo Data...")
    users = setup_demo_data()
    
    print("\n📋 Demo Credentials:")
    creds = get_demo_credentials()
    for name, info in creds.items():
        print(f"👤 {name.title()}: {info['email']} / {info['password']}")
        print(f"   Story: {info['story']}")
    
    print("\n🎯 Ready for hackathon demo!")
