#!/usr/bin/env python3
"""
Test the new sign-up functionality
"""

import os
import sys

# Add the project root directory to the path
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, project_root)


def test_signup():
    """Test user registration"""
    print(" Testing Sign-up Functionality...")
    try:
        from src.core.auth import create_user
        from local_db import Database
        import time
        
        # Use timestamp to create unique username
        test_username = f"test_user_{int(time.time())}"

        # Test creating a new applicant user
        success = create_user(test_username, "TestPass123!", "applicant")
        if success:
            print("    User creation working")

            # Test authentication
            db = Database()
            user = db.authenticate_user(test_username, "TestPass123!")
            if user:
                print("    New user authentication working")
                print(f"    User details: {user}")
                
                # Check if applicant profile was created
                applicants = db.get_all_applicants()
                user_applicant = None
                for applicant in applicants:
                    if applicant.get("user_id") == user["id"]:
                        user_applicant = applicant
                        break
                
                if user_applicant:
                    print("    Applicant profile automatically created")
                    print(f"    Profile: name={user_applicant.get('name')}, phone={user_applicant.get('phone')}")
                    return True
                else:
                    print("    Applicant profile not created")
                    return False
            else:
                print("    New user authentication failed")
                return False
        else:
            print("    User creation failed")
            return False

    except Exception as e:
        print(f"    Sign-up test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run sign-up tests"""
    print(" Z-Score Sign-up System Test")
    print("=" * 40)

    if test_signup():
        print("\n Sign-up system is working correctly!")
        print("\n To test in the app:")
        print("1. Open http://localhost:8501")
        print("2. Click on 'Sign Up' tab")
        print("3. Create a new applicant account")
        print("4. Login with new credentials")
        print("5. Complete profile to start journey")
    else:
        print("\n Sign-up system needs fixing")
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
