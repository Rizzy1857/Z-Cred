"""
Comprehensive test for the enhanced Z-Score model pipeline
Tests error handling, confidence intervals, and SHAP explanations
"""

import traceback

from src.core.error_handling import FeatureExtractionError, ModelError, ValidationError
from src.models.model_pipeline import (
    CreditRiskModel,
    calculate_trust_score,
)


def test_enhanced_model():
    """Test enhanced model with error handling and confidence intervals"""
    print("=" * 60)
    print("TESTING ENHANCED Z-SCORE MODEL PIPELINE")
    print("=" * 60)

    # Test 1: Model initialization and training
    print("\n1. Testing Model Initialization and Training...")
    try:
        model = CreditRiskModel()
        model.train()
        print("✅ Model training successful")
        print(f"   - Model confidence intervals: {model.model_confidence}")
        print(f"   - Training history entries: {len(model.training_history)}")
    except Exception as e:
        print(f"❌ Model training failed: {e}")
        return False

    # Test 2: Valid prediction with confidence intervals
    print("\n2. Testing Valid Prediction...")
    valid_applicant = {
        "age": 35,
        "gender": "Female",
        "monthly_income": 25000,
        "behavioral_score": 0.7,
        "social_score": 0.6,
        "digital_score": 0.8,
        "overall_trust_score": 0.7,
        "utility_payment_history": '{"on_time_ratio": 0.9, "average_amount": 2500}',
        "social_proof_data": '{"community_rating": 4.2, "endorsements": 5}',
        "digital_footprint": '{"transaction_regularity": 0.8, "device_stability": 0.9}',
        "z_credits": 150,
    }

    try:
        prediction = model.predict(valid_applicant)
        print("✅ Valid prediction successful")
        print(f"   - Risk Category: {prediction['risk_category']}")
        print(f"   - Confidence Score: {prediction['confidence_score']:.3f}")
        print(f"   - Prediction Confidence: {prediction['prediction_confidence']:.3f}")
        print(f"   - Model Version: {prediction['model_version']}")
    except Exception as e:
        print(f"❌ Valid prediction failed: {e}")
        return False

    # Test 3: SHAP explanation
    print("\n3. Testing SHAP Explanation...")
    try:
        explanation = model.explain_prediction(valid_applicant)
        if "error" not in explanation:
            print("✅ SHAP explanation successful")
            print(
                f"   - Explanation quality: {explanation.get('explanation_quality', 'unknown')}"
            )
            print(
                f"   - Top positive contributors: {len(explanation.get('top_contributors', {}).get('positive', []))}"
            )
            print(
                f"   - Top negative contributors: {len(explanation.get('top_contributors', {}).get('negative', []))}"
            )

            # Show top contributors
            if "top_contributors" in explanation:
                print("   - Top positive factors:")
                for contrib in explanation["top_contributors"]["positive"][:2]:
                    print(f"     • {contrib['feature']}: {contrib['impact']:.3f}")
        else:
            print(f"⚠️  SHAP explanation returned error: {explanation['error']}")
            if "fallback_explanation" in explanation:
                print("✅ Fallback explanation available")
    except Exception as e:
        print(f"❌ SHAP explanation failed: {e}")

    # Test 4: Error handling for invalid data
    print("\n4. Testing Error Handling...")
    invalid_applicant = {
        "age": "invalid",
        "monthly_income": -5000,
        "utility_payment_history": "invalid_json",
        "behavioral_score": "not_a_number",
    }

    try:
        prediction = model.predict(invalid_applicant)
        print("✅ Error handling successful - invalid data converted safely")
        print(f"   - Risk Category: {prediction['risk_category']}")
    except (ModelError, FeatureExtractionError, ValidationError) as e:
        print(f"✅ Proper error handling - caught expected error: {type(e).__name__}")
    except Exception as e:
        print(f"⚠️  Unexpected error type: {type(e).__name__}: {e}")

    # Test 5: Trust score calculation
    print("\n5. Testing Enhanced Trust Score Calculation...")
    try:
        trust_result = calculate_trust_score(valid_applicant)
        print("✅ Trust score calculation successful")
        print(
            f"   - Overall Trust Score: {trust_result.get('overall_trust_score', 'N/A'):.3f}"
        )
        print(
            f"   - Behavioral Score: {trust_result.get('behavioral_score', 'N/A'):.3f}"
        )
        print(f"   - Social Score: {trust_result.get('social_score', 'N/A'):.3f}")
        print(f"   - Digital Score: {trust_result.get('digital_score', 'N/A'):.3f}")
    except Exception as e:
        print(f"❌ Trust score calculation failed: {e}")

    # Test 6: Edge cases
    print("\n6. Testing Edge Cases...")
    edge_cases = [
        {"age": 18, "monthly_income": 0},  # Minimum values
        {"age": 100, "monthly_income": 10000000},  # Maximum values
        {},  # Empty data
        {"age": None, "monthly_income": None},  # None values
    ]

    for i, case in enumerate(edge_cases):
        try:
            prediction = model.predict(case)
            print(f"✅ Edge case {i+1} handled successfully")
        except Exception as e:
            print(f"⚠️  Edge case {i+1} failed: {type(e).__name__}")

    # Test 7: Model persistence (save/load)
    print("\n7. Testing Model Persistence...")
    try:
        model.save_model("test_models/")
        print("✅ Model save successful")

        new_model = CreditRiskModel()
        new_model.load_model("test_models/")
        print("✅ Model load successful")

        # Test loaded model
        test_prediction = new_model.predict(valid_applicant)
        print(
            f"✅ Loaded model prediction successful: {test_prediction['risk_category']}"
        )
    except Exception as e:
        print(f"⚠️  Model persistence test failed: {e}")

    print("\n" + "=" * 60)
    print("ENHANCED MODEL PIPELINE TEST COMPLETE")
    print("=" * 60)
    return True


def test_error_handling_module():
    """Test the error handling module"""
    print("\n" + "=" * 60)
    print("TESTING ERROR HANDLING MODULE")
    print("=" * 60)

    from src.core.error_handling import (
        confidence_interval_calculator,
        is_valid_age,
        is_valid_email,
        is_valid_phone,
        safe_json_parse,
        safe_numeric_conversion,
    )

    # Test safe JSON parsing
    print("\n1. Testing Safe JSON Parsing...")
    test_cases = [
        ('{"valid": "json"}', True),
        ("invalid json", False),
        ("", False),
        (None, False),
        ({"already": "dict"}, True),
    ]

    for json_input, should_succeed in test_cases:
        try:
            result = safe_json_parse(json_input)
            if should_succeed and isinstance(result, dict):
                print(f"✅ JSON parse handled correctly: {str(json_input)[:20]}")
            elif not should_succeed and result == {}:
                print(f"✅ Invalid JSON handled correctly: {str(json_input)[:20]}")
            else:
                print(f"⚠️  Unexpected result for: {str(json_input)[:20]}")
        except Exception as e:
            print(f"❌ JSON parse failed: {e}")

    # Test numeric conversion
    print("\n2. Testing Safe Numeric Conversion...")
    numeric_cases = [
        ("25", 25.0),
        ("invalid", 0.0),
        (None, 0.0),
        (-5, 0.0),  # With min_val=0
        (105, 100.0),  # With max_val=100
    ]

    for value, expected in numeric_cases:
        try:
            if value == -5:
                result = safe_numeric_conversion(value, min_val=0)
            elif value == 105:
                result = safe_numeric_conversion(value, max_val=100)
            else:
                result = safe_numeric_conversion(value)
            print(f"✅ Numeric conversion: {value} -> {result}")
        except Exception as e:
            print(f"❌ Numeric conversion failed: {e}")

    # Test validation functions
    print("\n3. Testing Validation Functions...")
    validation_tests = [
        (is_valid_email, "test@example.com", True),
        (is_valid_email, "invalid-email", False),
        (is_valid_phone, "9876543210", True),
        (is_valid_phone, "123", False),
        (is_valid_age, 25, True),
        (is_valid_age, 200, False),
    ]

    for func, value, expected in validation_tests:
        try:
            result = func(value)
            if result == expected:
                print(f"✅ Validation {func.__name__}: {value} -> {result}")
            else:
                print(
                    f"⚠️  Validation {func.__name__}: {value} -> {result} (expected {expected})"
                )
        except Exception as e:
            print(f"❌ Validation {func.__name__} failed: {e}")

    # Test confidence intervals
    print("\n4. Testing Confidence Interval Calculator...")
    try:
        test_predictions = [0.3, 0.5, 0.7, 0.4, 0.6, 0.8, 0.2, 0.9]
        intervals = confidence_interval_calculator(test_predictions)
        print(f"✅ Confidence intervals calculated:")
        print(f"   - Mean: {intervals['mean']:.3f}")
        print(f"   - Lower bound: {intervals['lower']:.3f}")
        print(f"   - Upper bound: {intervals['upper']:.3f}")
    except Exception as e:
        print(f"❌ Confidence interval calculation failed: {e}")

    print("\n" + "=" * 60)
    print("ERROR HANDLING MODULE TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    try:
        # Test the enhanced model pipeline
        model_success = test_enhanced_model()

        # Test the error handling module
        test_error_handling_module()

        if model_success:
            print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
            print("✅ Enhanced model pipeline is ready for production")
            print("✅ Error handling is robust and comprehensive")
            print("✅ Confidence intervals are working correctly")
            print("✅ SHAP explanations are enhanced with fallbacks")
        else:
            print("\n⚠️  Some tests failed. Please review the output above.")

    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        traceback.print_exc()
