"""
Model Integration Module

Provides seamless integration between the application data structure
and the ML model pipeline, handling data format transformation and
fallback mechanisms. Enhanced with SHAP caching for optimal performance.
"""

import json
from typing import Any, Dict, Optional

from .model_pipeline import CreditRiskModel, TrustScoreCalculator, calculate_trust_score


class ModelIntegrator:
    """Integrates application data with ML model pipeline"""

    def __init__(self):
        self.credit_model = None
        self.trust_calculator = TrustScoreCalculator()
        self._shap_cache_initialized = False

    def get_credit_model(self):
        """Lazy initialization of credit model with training if needed"""
        if self.credit_model is None:
            self.credit_model = CreditRiskModel()

            # Try to load saved models first
            try:
                self.credit_model.load_model("test_models/")
                print("✅ Loaded pre-trained models successfully")
            except Exception as e:
                print(f"⚠️ Could not load saved models ({e}), training new model...")
                # Train the model if loading fails
                self.credit_model.train()
                # Save the trained model
                try:
                    self.credit_model.save_model("test_models/")
                    print("✅ Trained model saved successfully")
                except Exception as save_error:
                    print(f"⚠️ Could not save model: {save_error}")

            # Initialize SHAP cache after model is loaded
            self._initialize_shap_cache()

        return self.credit_model

    def _initialize_shap_cache(self):
        """Initialize SHAP cache for faster explanations"""
        if self._shap_cache_initialized:
            return

        try:
            from .shap_cache import cache_shap_explainers

            print("🚀 Initializing SHAP cache for faster explanations...")
            cache_shap_explainers(self.credit_model)
            self._shap_cache_initialized = True
            print("✅ SHAP cache initialized successfully")
        except Exception as e:
            print(f"⚠️ SHAP cache initialization failed: {e}")
            print("   Continuing without cache - explanations may be slower")

    def get_shap_explanation(
        self, features: Dict[str, Any], model_type: str = "xgboost"
    ) -> Optional[Dict]:
        """
        Get SHAP explanation for predictions with caching

        Args:
            features: Feature dictionary for explanation
            model_type: Type of model to explain ('xgboost' or 'logistic')

        Returns:
            Dictionary with SHAP values and explanation data
        """
        try:
            import numpy as np

            from .shap_cache import get_cached_shap_values

            # Ensure model is loaded
            model = self.get_credit_model()

            # Prepare features for SHAP
            feature_names = list(features.keys())
            feature_values = np.array([list(features.values())])

            # Get model for explanation
            if model_type == "xgboost" and hasattr(model, "xgb_model"):
                target_model = model.xgb_model
            elif model_type == "logistic" and hasattr(model, "logistic_model"):
                target_model = model.logistic_model
            else:
                print(f"⚠️ Model type {model_type} not available")
                return None

            # Get cached SHAP values
            shap_values = get_cached_shap_values(
                target_model, feature_values, model_type, feature_names
            )

            if shap_values is not None:
                return {
                    "shap_values": (
                        shap_values[0] if len(shap_values.shape) > 1 else shap_values
                    ),
                    "feature_names": feature_names,
                    "feature_values": feature_values[0],
                    "model_type": model_type,
                    "base_value": (
                        getattr(shap_values, "base_values", [0])[0]
                        if hasattr(shap_values, "base_values")
                        else 0
                    ),
                }

        except Exception as e:
            print(f"❌ Error generating SHAP explanation: {e}")

        return None

    def transform_applicant_data(self, applicant_data: Dict) -> Dict:
        """Transform application data format to model expected format"""
        try:
            # Create payment history structure
            payment_history = {
                "on_time_payments": self._get_payment_ratio(applicant_data),
                "average_amount": float(applicant_data.get("monthly_income", 50000))
                * 0.1,
                "payment_consistency": self._get_payment_consistency(applicant_data),
            }

            # Create social proof structure
            social_proof = {
                "endorsements": int(applicant_data.get("social_endorsements", 0)),
                "network_size": self._estimate_network_size(applicant_data),
                "community_rating": self._get_community_rating(applicant_data),
            }

            # Create digital footprint structure
            digital_footprint = {
                "transaction_frequency": self._get_transaction_frequency(
                    applicant_data
                ),
                "online_activity": applicant_data.get("digital_presence", "moderate"),
                "account_age": int(applicant_data.get("account_age", 12)),
                "digital_stability": self._get_digital_stability(applicant_data),
            }

            return {
                # Model pipeline expected format
                "utility_payment_history": json.dumps(payment_history),
                "social_proof_data": json.dumps(social_proof),
                "digital_footprint": json.dumps(digital_footprint),
                "income_stability": self._calculate_income_stability(applicant_data),
                # Additional model features
                "monthly_income": float(applicant_data.get("monthly_income", 50000)),
                "employment_type": applicant_data.get("employment_type", "full_time"),
                "existing_loans": int(applicant_data.get("existing_loans", 0)),
                "account_age": int(applicant_data.get("account_age", 12)),
                # Pass through other fields
                **{
                    k: v
                    for k, v in applicant_data.items()
                    if k
                    not in [
                        "utility_payment_history",
                        "social_proof_data",
                        "digital_footprint",
                    ]
                },
            }

        except Exception as e:
            print(f"Error transforming applicant data: {e}")
            return applicant_data

    def _get_payment_ratio(self, data: Dict) -> float:
        """Calculate payment history ratio from application data"""
        payment_history = data.get("payment_history", "good")
        if payment_history == "excellent":
            return 0.95
        elif payment_history == "good":
            return 0.85
        elif payment_history == "fair":
            return 0.70
        else:
            return 0.50

    def _get_payment_consistency(self, data: Dict) -> float:
        """Estimate payment consistency"""
        employment = data.get("employment_type", "full_time")
        if employment == "full_time":
            return 0.9
        elif employment == "part_time":
            return 0.7
        else:
            return 0.6

    def _estimate_network_size(self, data: Dict) -> int:
        """Estimate network size from activity"""
        activity = data.get("community_activity", "moderate")
        endorsements = int(data.get("social_endorsements", 0))

        base_network = endorsements * 3  # Rough multiplier

        if activity == "very_active":
            return base_network + 30
        elif activity == "active":
            return base_network + 20
        elif activity == "moderate":
            return base_network + 10
        else:
            return base_network + 5

    def _get_community_rating(self, data: Dict) -> float:
        """Convert community activity to rating"""
        activity = data.get("community_activity", "moderate")
        endorsements = int(data.get("social_endorsements", 0))

        # Base rating from endorsements
        base_rating = min(3.0 + (endorsements * 0.1), 4.5)

        # Adjust for activity level
        if activity == "very_active":
            return min(base_rating + 0.5, 5.0)
        elif activity == "active":
            return min(base_rating + 0.3, 5.0)
        elif activity == "moderate":
            return base_rating
        else:
            return max(base_rating - 0.3, 2.0)

    def _get_transaction_frequency(self, data: Dict) -> str:
        """Estimate transaction frequency"""
        income = float(data.get("monthly_income", 50000))
        if income > 80000:
            return "high"
        elif income > 40000:
            return "regular"
        else:
            return "low"

    def _get_digital_stability(self, data: Dict) -> float:
        """Calculate digital stability score"""
        presence = data.get("digital_presence", "moderate")
        age = int(data.get("account_age", 12))

        base_score = min(age / 24.0, 1.0)  # Normalize by 2 years

        if presence == "strong":
            return min(base_score + 0.2, 1.0)
        elif presence == "moderate":
            return base_score
        else:
            return max(base_score - 0.2, 0.3)

    def _calculate_income_stability(self, data: Dict) -> float:
        """Calculate income stability score"""
        employment = data.get("employment_type", "full_time")
        income = float(data.get("monthly_income", 50000))

        # Base stability from employment type
        if employment == "full_time":
            base_stability = 0.8
        elif employment == "part_time":
            base_stability = 0.6
        elif employment == "contract":
            base_stability = 0.7
        else:
            base_stability = 0.5

        # Adjust for income level (higher income = more stability)
        income_factor = min(income / 100000, 1.2)  # Cap at 120%

        return min(base_stability * income_factor, 1.0)

    def get_ml_trust_score(self, applicant_data: Dict) -> Optional[Dict]:
        """Get trust score using ML model pipeline"""
        try:
            transformed_data = self.transform_applicant_data(applicant_data)
            return calculate_trust_score(transformed_data)
        except Exception as e:
            print(f"ML trust score calculation failed: {e}")
            return None

    def get_risk_prediction(self, applicant_data: Dict) -> Optional[Dict]:
        """Get risk prediction using credit model"""
        try:
            model = self.get_credit_model()
            transformed_data = self.transform_applicant_data(applicant_data)
            return model.predict(transformed_data)
        except Exception as e:
            print(f"Risk prediction failed: {e}")
            return None

    def get_combined_assessment(self, applicant_data: Dict) -> Dict:
        """Get both trust score and risk prediction"""
        try:
            transformed_data = self.transform_applicant_data(applicant_data)

            # Get trust scores
            trust_result = calculate_trust_score(transformed_data)

            # Get risk prediction
            model = self.get_credit_model()
            risk_result = model.predict(transformed_data)

            # Combine results
            return {
                "trust_assessment": trust_result,
                "risk_assessment": risk_result,
                "overall_recommendation": self._generate_recommendation(
                    trust_result, risk_result
                ),
                "data_transformation_successful": True,
            }

        except Exception as e:
            print(f"Combined assessment failed: {e}")
            return {"error": str(e), "data_transformation_successful": False}

    def _generate_recommendation(self, trust_result: Dict, risk_result: Dict) -> Dict:
        """Generate overall recommendation based on trust and risk"""
        try:
            trust_score = trust_result.get("overall_trust_score", 0.5)
            risk_category = risk_result.get("risk_category", "High Risk")
            confidence = risk_result.get("prediction_confidence", 0.5)

            # Simple recommendation logic
            if trust_score > 0.7 and risk_category == "Low Risk":
                recommendation = "Highly Recommended"
                confidence_level = "High"
            elif trust_score > 0.5 and risk_category in ["Low Risk", "Medium Risk"]:
                recommendation = "Recommended"
                confidence_level = "Medium" if confidence > 0.6 else "Low"
            elif trust_score > 0.3:
                recommendation = "Consider with Conditions"
                confidence_level = "Low"
            else:
                recommendation = "Not Recommended"
                confidence_level = "High"

            return {
                "recommendation": recommendation,
                "confidence_level": confidence_level,
                "trust_weight": trust_score,
                "risk_weight": 1 - risk_result.get("risk_probability", 0.5),
            }

        except Exception as e:
            return {"recommendation": "Unable to Generate", "error": str(e)}


# Global integrator instance
model_integrator = ModelIntegrator()


def get_enhanced_trust_assessment(applicant_data: Dict) -> Dict:
    """
    Enhanced trust assessment that tries ML model first,
    falls back to rule-based calculation if needed
    """
    # Try ML model first
    ml_result = model_integrator.get_ml_trust_score(applicant_data)

    if ml_result and ml_result.get("overall_trust_score", 0) > 0.1:
        # ML model worked and gave reasonable results
        return {
            "source": "ml_model",
            "behavioral_score": ml_result.get("behavioral_score", 0.5),
            "social_score": ml_result.get("social_score", 0.5),
            "digital_score": ml_result.get("digital_score", 0.5),
            "overall_trust_score": ml_result.get("overall_trust_score", 0.5),
            "trust_percentage": ml_result.get("trust_percentage", 50.0),
            "ml_available": True,
        }
    else:
        # Fall back to rule-based calculation
        print("ML model unavailable, using rule-based fallback")
        calculator = TrustScoreCalculator()

        # Create dummy structures for the calculator
        payment_data = {"on_time_payments": 0.85, "average_amount": 5000}
        social_data = {
            "endorsements": applicant_data.get("social_endorsements", 5),
            "network_size": 25,
        }
        digital_data = {"transaction_frequency": "regular", "online_activity": "active"}

        behavioral = calculator.calculate_behavioral_score(payment_data, 0.8)
        social = calculator.calculate_social_score(social_data, 4.0)
        digital = calculator.calculate_digital_score(digital_data)

        overall = (behavioral * 0.5) + (social * 0.3) + (digital * 0.2)

        return {
            "source": "fallback_calculation",
            "behavioral_score": behavioral,
            "social_score": social,
            "digital_score": digital,
            "overall_trust_score": overall,
            "trust_percentage": overall * 100,
            "ml_available": False,
        }
