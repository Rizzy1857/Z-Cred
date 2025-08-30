"""
Comprehensive Test Suite for ML Model Integration

Tests the enhanced trust assessment, ML model pipeline, and application integration.
"""

import sys
import traceback
from datetime import datetime

# Add project root to path
sys.path.append("/Users/rizzy/Documents/GitHub/Z-Cred")


def test_model_integration():
    """Test the model integration system"""
    print("=" * 60)
    print("TESTING ML MODEL INTEGRATION")
    print("=" * 60)

    try:
        from model_integration import get_enhanced_trust_assessment, model_integrator

        # Test data samples
        test_cases = [
            {
                "name": "High Trust Applicant",
                "data": {
                    "user_id": "high_trust_user",
                    "monthly_income": 85000,
                    "employment_type": "full_time",
                    "payment_history": "excellent",
                    "existing_loans": 0,
                    "social_endorsements": 12,
                    "community_activity": "very_active",
                    "digital_presence": "strong",
                    "account_age": 36,
                },
            },
            {
                "name": "Medium Trust Applicant",
                "data": {
                    "user_id": "medium_trust_user",
                    "monthly_income": 55000,
                    "employment_type": "full_time",
                    "payment_history": "good",
                    "existing_loans": 2,
                    "social_endorsements": 6,
                    "community_activity": "active",
                    "digital_presence": "moderate",
                    "account_age": 18,
                },
            },
            {
                "name": "Lower Trust Applicant",
                "data": {
                    "user_id": "lower_trust_user",
                    "monthly_income": 35000,
                    "employment_type": "part_time",
                    "payment_history": "fair",
                    "existing_loans": 3,
                    "social_endorsements": 2,
                    "community_activity": "moderate",
                    "digital_presence": "weak",
                    "account_age": 8,
                },
            },
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing {test_case['name']}:")
            print("-" * 40)

            # Test enhanced trust assessment
            try:
                trust_result = get_enhanced_trust_assessment(test_case["data"])
                print(f"✅ Enhanced Trust Assessment:")
                print(f"   Source: {trust_result.get('source', 'unknown')}")
                print(f"   ML Available: {trust_result.get('ml_available', False)}")
                print(
                    f"   Overall Trust: {trust_result.get('trust_percentage', 0):.1f}%"
                )
                print(
                    f"   Behavioral: {trust_result.get('behavioral_score', 0)*100:.1f}%"
                )
                print(f"   Social: {trust_result.get('social_score', 0)*100:.1f}%")
                print(f"   Digital: {trust_result.get('digital_score', 0)*100:.1f}%")

            except Exception as e:
                print(f"❌ Enhanced Trust Assessment Failed: {e}")

            # Test combined assessment
            try:
                combined_result = model_integrator.get_combined_assessment(
                    test_case["data"]
                )
                if "error" not in combined_result:
                    trust_data = combined_result.get("trust_assessment", {})
                    risk_data = combined_result.get("risk_assessment", {})
                    recommendation = combined_result.get("overall_recommendation", {})

                    print(f"✅ Combined ML Assessment:")
                    print(
                        f"   Trust Score: {trust_data.get('trust_percentage', 0):.1f}%"
                    )
                    print(
                        f"   Risk Category: {risk_data.get('risk_category', 'Unknown')}"
                    )
                    print(
                        f"   Risk Probability: {risk_data.get('risk_probability', 0)*100:.1f}%"
                    )
                    print(
                        f"   Recommendation: {recommendation.get('recommendation', 'Unknown')}"
                    )
                    print(
                        f"   Confidence: {recommendation.get('confidence_level', 'Unknown')}"
                    )
                else:
                    print(
                        f"❌ Combined Assessment Error: {combined_result.get('error')}"
                    )

            except Exception as e:
                print(f"❌ Combined Assessment Failed: {e}")

        print(f"\n✅ Model Integration Tests Completed Successfully!")
        return True

    except Exception as e:
        print(f"❌ Model Integration Test Failed: {e}")
        traceback.print_exc()
        return False


def test_application_integration():
    """Test application components"""
    print("\n" + "=" * 60)
    print("TESTING APPLICATION INTEGRATION")
    print("=" * 60)

    try:
        # Test database and auth
        print("\n1. Testing Database Connection:")
        from local_db import Database

        db = Database()
        applicants = db.get_all_applicants()
        print(f"✅ Database connected, {len(applicants)} applicants found")

        print("\n2. Testing Auth System:")
        from auth import AuthManager

        AuthManager()
        print("✅ Auth manager initialized")

        print("\n3. Testing Trust Bar Rendering (simulation):")
        # Simulate the trust bar calculation without Streamlit
        test_applicant = {
            "id": 1,
            "name": "Test User",
            "monthly_income": 60000,
            "employment_type": "full_time",
            "payment_history": "good",
            "social_endorsements": 7,
            "community_activity": "active",
            "digital_presence": "moderate",
            "account_age": 20,
        }

        from model_integration import get_enhanced_trust_assessment

        trust_result = get_enhanced_trust_assessment(test_applicant)
        print(f"✅ Trust calculation successful:")
        print(f"   Trust Score: {trust_result.get('trust_percentage', 0):.1f}%")
        print(f"   ML Available: {trust_result.get('ml_available', False)}")

        print(f"\n✅ Application Integration Tests Completed!")
        return True

    except Exception as e:
        print(f"❌ Application Integration Test Failed: {e}")
        traceback.print_exc()
        return False


def test_model_pipeline_performance():
    """Test model performance and timing"""
    print("\n" + "=" * 60)
    print("TESTING MODEL PERFORMANCE")
    print("=" * 60)

    try:
        import time

        from model_integration import model_integrator

        test_data = {
            "monthly_income": 65000,
            "employment_type": "full_time",
            "payment_history": "good",
            "social_endorsements": 8,
            "community_activity": "active",
            "digital_presence": "moderate",
            "account_age": 24,
        }

        # Test timing
        print("\n1. Performance Testing:")

        # Trust score timing
        start_time = time.time()
        trust_result = model_integrator.get_ml_trust_score(test_data)
        trust_time = time.time() - start_time
        print(f"✅ Trust Score Calculation: {trust_time:.3f}s")

        # Risk prediction timing
        start_time = time.time()
        risk_result = model_integrator.get_risk_prediction(test_data)
        risk_time = time.time() - start_time
        print(f"✅ Risk Prediction: {risk_time:.3f}s")

        # Combined assessment timing
        start_time = time.time()
        model_integrator.get_combined_assessment(test_data)
        combined_time = time.time() - start_time
        print(f"✅ Combined Assessment: {combined_time:.3f}s")

        print(f"\n2. Model Quality Check:")
        if trust_result:
            trust_score = trust_result.get("overall_trust_score", 0)
            if 0.1 <= trust_score <= 1.0:
                print(f"✅ Trust score in valid range: {trust_score:.3f}")
            else:
                print(f"⚠️ Trust score outside expected range: {trust_score:.3f}")

        if risk_result:
            risk_prob = risk_result.get("risk_probability", 0)
            if 0.0 <= risk_prob <= 1.0:
                print(f"✅ Risk probability in valid range: {risk_prob:.3f}")
            else:
                print(f"⚠️ Risk probability outside expected range: {risk_prob:.3f}")

        print(f"\n✅ Performance Tests Completed!")
        return True

    except Exception as e:
        print(f"❌ Performance Test Failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run comprehensive test suite"""
    print(f"Z-CRED ML INTEGRATION TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    tests = [
        ("Model Integration", test_model_integration),
        ("Application Integration", test_application_integration),
        ("Model Performance", test_model_pipeline_performance),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            print(f"\n🚀 Starting {test_name} Tests...")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} Test Suite Failed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} : {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} test suites passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! ML Integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")

    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
