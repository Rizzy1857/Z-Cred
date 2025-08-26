#!/usr/bin/env python3
"""
Z-Score System Test Script

Validates all major components before demo presentation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """Test database operations"""
    print("🗄️ Testing database...")
    try:
        from local_db import Database
        db = Database()
        
        # Test applicant creation
        test_applicant = {
            'name': 'Test User',
            'phone': '+91-9999999999',
            'email': 'test@example.com',
            'age': 30,
            'gender': 'Male',
            'location': 'Test City',
            'occupation': 'Test Job',
            'monthly_income': 25000
        }
        
        applicant_id = db.create_applicant(test_applicant)
        if applicant_id:
            print("   ✅ Database operations working")
            
            # Test trust score update
            db.update_trust_score(applicant_id, 0.5, 0.6, 0.4)
            print("   ✅ Trust score updates working")
            
            # Test consent logging
            db.log_consent(applicant_id, 'test_consent', 'testing', True)
            print("   ✅ Consent logging working")
            
            return True
        else:
            print("   ❌ Database creation failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def test_authentication():
    """Test authentication system"""
    print("🔐 Testing authentication...")
    try:
        from auth import AuthManager
        auth = AuthManager()
        
        # Test authentication (should fail with wrong credentials)
        result = auth.db.authenticate_user("test_user", "wrong_password")
        if result is None:
            print("   ✅ Authentication rejection working")
        
        # Test with admin credentials
        result = auth.db.authenticate_user("admin", "admin123")
        if result:
            print("   ✅ Admin authentication working")
            return True
        else:
            print("   ❌ Admin authentication failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Authentication test failed: {e}")
        return False

def test_ml_pipeline():
    """Test ML pipeline"""
    print("🤖 Testing ML pipeline...")
    try:
        from model_pipeline import CreditRiskModel, calculate_trust_score
        
        # Test model initialization
        model = CreditRiskModel()
        print("   ✅ Model initialization working")
        
        # Test trust score calculation
        sample_data = {
            'utility_payment_history': '{"on_time_payments": 10, "total_payments": 12}',
            'social_proof_data': '{"community_rating": 4.0, "endorsements": 5}',
            'digital_footprint': '{"device_stability": 0.8, "transaction_regularity": 0.7}'
        }
        
        trust_scores = calculate_trust_score(sample_data)
        if trust_scores and 'overall_trust_score' in trust_scores:
            print("   ✅ Trust score calculation working")
        
        # Test model training (quick synthetic data)
        model.train()
        print("   ✅ Model training working")
        
        # Test prediction
        sample_applicant = {
            'age': 28,
            'gender': 'Female',
            'monthly_income': 15000,
            'behavioral_score': 0.65,
            'social_score': 0.60,
            'digital_score': 0.55,
            'overall_trust_score': 0.60,
            'z_credits': 150
        }
        
        prediction = model.predict(sample_applicant)
        if prediction and 'risk_category' in prediction:
            print("   ✅ ML prediction working")
            return True
        else:
            print("   ❌ ML prediction failed")
            return False
            
    except Exception as e:
        print(f"   ❌ ML pipeline test failed: {e}")
        return False

def test_streamlit_imports():
    """Test Streamlit application imports"""
    print("🌐 Testing Streamlit imports...")
    try:
        from app import ZScoreApp
        app = ZScoreApp()
        print("   ✅ Streamlit app imports working")
        return True
        
    except Exception as e:
        print(f"   ❌ Streamlit import test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Z-Score System Component Tests")
    print("=" * 50)
    
    tests = [
        test_database,
        test_authentication,
        test_ml_pipeline,
        test_streamlit_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All systems ready for demo!")
        print("\n🚀 To start the application, run:")
        print("   ./run.sh")
        print("   or")
        print("   streamlit run app.py")
        print("\n🔐 Default login: admin / admin123")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
