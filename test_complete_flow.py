#!/usr/bin/env python3
"""
Test the complete signup to profile completion flow
"""

import os
import sys
import time

# Add the project root directory to the path
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_complete_flow():
    """Test the complete user flow from signup to profile completion"""
    print("🚀 Testing Complete User Flow")
    print("=" * 50)
    
    try:
        from src.core.auth import create_user
        from local_db import Database
        
        # Create a unique test user
        test_username = f"flow_test_{int(time.time())}"
        test_password = "FlowTest123!"
        
        print(f"📝 Creating new user: {test_username}")
        
        # 1. Test signup creates user + basic applicant profile
        success = create_user(test_username, test_password, "applicant")
        if not success:
            print("❌ User creation failed")
            return False
            
        print("✅ User created successfully")
        
        # 2. Test authentication works
        db = Database()
        user = db.authenticate_user(test_username, test_password)
        if not user:
            print("❌ Authentication failed")
            return False
            
        print("✅ Authentication successful")
        print(f"   User ID: {user['id']}, Role: {user['role']}")
        
        # 3. Check applicant profile was created automatically
        applicants = db.get_all_applicants()
        user_applicant = None
        for applicant in applicants:
            if applicant.get("user_id") == user["id"]:
                user_applicant = applicant
                break
                
        if not user_applicant:
            print("❌ No applicant profile found")
            return False
            
        print("✅ Applicant profile found")
        print(f"   Profile ID: {user_applicant['id']}")
        print(f"   Name: {user_applicant.get('name')}")
        print(f"   Phone: {user_applicant.get('phone')}")
        print(f"   Age: {user_applicant.get('age')}")
        
        # 4. Check if profile needs completion (it should)
        phone = user_applicant.get("phone", "")
        needs_completion = not phone or phone.startswith("pending_") or not user_applicant.get("age")
        
        if needs_completion:
            print("✅ Profile correctly marked as needing completion")
        else:
            print("❌ Profile should need completion but doesn't")
            return False
        
        # 5. Test profile completion
        print("📋 Testing profile completion...")
        
        # Use unique phone number based on user ID to avoid conflicts
        unique_phone = f"+91-987654{user['id']:04d}"
        
        profile_data = {
            'name': test_username,
            'phone': unique_phone,
            'email': f'{test_username}@test.com',
            'age': 28,
            'gender': 'Male',
            'location': 'Mumbai, Maharashtra',
            'occupation': 'Software Engineer',
            'monthly_income': 75000
        }
        
        # Update using the new method
        update_success = db.update_applicant_profile(user['id'], profile_data)
        if not update_success:
            print("❌ Profile update failed")
            return False
            
        print("✅ Profile updated successfully")
        
        # 6. Verify profile completion
        updated_applicants = db.get_all_applicants()
        updated_applicant = None
        for applicant in updated_applicants:
            if applicant.get("user_id") == user["id"]:
                updated_applicant = applicant
                break
                
        if not updated_applicant:
            print("❌ Updated profile not found")
            return False
            
        # Check if profile is now complete
        phone = updated_applicant.get("phone", "")
        is_complete = phone and not phone.startswith("pending_") and updated_applicant.get("age")
        
        if is_complete:
            print("✅ Profile successfully completed")
            print(f"   Updated Phone: {updated_applicant.get('phone')}")
            print(f"   Updated Age: {updated_applicant.get('age')}")
            print(f"   Updated Occupation: {updated_applicant.get('occupation')}")
        else:
            print("❌ Profile not properly completed")
            return False
            
        print("\n🎉 Complete flow test PASSED!")
        print("\nFlow Summary:")
        print("1. ✅ User signup creates account + basic applicant profile")
        print("2. ✅ Authentication works for new users")
        print("3. ✅ Profile completion detection works")
        print("4. ✅ Profile update functionality works")
        print("5. ✅ Completed profiles are properly validated")
        
        return True
        
    except Exception as e:
        print(f"❌ Flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if test_complete_flow():
        print("\n✅ All tests passed! The signup flow is working correctly.")
        print("\n📱 To test manually:")
        print("1. Open http://localhost:8502")
        print("2. Click 'Sign Up' tab")
        print("3. Create a new account (role: Credit Applicant)")
        print("4. Login with new credentials")
        print("5. Complete the profile form")
        print("6. Verify you can access the main dashboard")
    else:
        print("\n❌ Tests failed! Check the errors above.")
        sys.exit(1)
