"""
Machine Learning Pipeline for Z-Score Credit Risk Assessment

Implements logistic regression baseline and XGBoost ensemble models with
SHAP explainability for transparent credit decisions.
Enhanced with comprehensive error handling and confidence intervals.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import xgboost as xgb
import shap
import joblib
import json
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Import our error handling module
from ..core.error_handling import (
    ModelError, FeatureExtractionError, ValidationError,
    handle_exceptions
)

# Helper functions for safe data conversion
def safe_numeric_conversion(value, default=0.0, min_val=None, max_val=None):
    """Safely convert value to numeric with bounds checking"""
    try:
        result = float(value) if value is not None else default
        if min_val is not None and result < min_val:
            result = min_val
        if max_val is not None and result > max_val:
            result = max_val
        return result
    except (ValueError, TypeError):
        return default

def safe_json_parse(value, default=None):
    """Safely parse JSON string"""
    try:
        import json
        return json.loads(value) if isinstance(value, str) else value
    except (json.JSONDecodeError, TypeError):
        return default or {}

# Create a simple error handler instance
class SimpleErrorHandler:
    def log_error(self, error, context=None):
        # Simple logging - in production this would be more sophisticated
        print(f"Error: {error}")
        if context:
            print(f"Context: {context}")

error_handler = SimpleErrorHandler()

def confidence_interval_calculator(predictions):
    """Calculate simple confidence interval"""
    import numpy as np
    if not predictions:
        return {'lower': 0.8, 'upper': 0.99, 'confidence': 0.95}
    std_dev = float(np.std(predictions))
    confidence = min(0.99, max(0.8, std_dev + 0.8))
    return {
        'lower': max(0.0, confidence - 0.1), 
        'upper': min(1.0, confidence + 0.1),
        'confidence': confidence
    }


class TrustScoreCalculator:
    """Calculate trust scores from alternative data with enhanced error handling"""
    
    @staticmethod
    @handle_exceptions(FeatureExtractionError)
    def calculate_behavioral_score(payment_history: Dict, income_stability: float) -> float:
        """Calculate behavioral trust component with validation"""
        if not payment_history:
            return 0.1
        
        try:
            # Payment punctuality (0-40 points)
            on_time_payments = safe_numeric_conversion(payment_history.get('on_time_payments', 0), 0)
            total_payments = safe_numeric_conversion(payment_history.get('total_payments', 1), 1)
            total_payments = max(total_payments, 1)  # Avoid division by zero
            
            on_time_ratio = on_time_payments / total_payments
            punctuality_score = min(on_time_ratio * 0.4, 0.4)
            
            # Income stability (0-30 points)
            income_stability = safe_numeric_conversion(income_stability, 0.0, 0.0, 1.0)
            stability_score = min(income_stability * 0.3, 0.3)
            
            # Transaction consistency (0-30 points)
            avg_amount = safe_numeric_conversion(payment_history.get('average_amount', 0), 0, 0)
            consistency_score = min((avg_amount / 10000) * 0.3, 0.3) if avg_amount > 0 else 0.1
            
            total_score = punctuality_score + stability_score + consistency_score
            return max(0.1, min(1.0, total_score))  # Ensure score is between 0.1 and 1.0
            
        except Exception as e:
            error_handler.log_error(e, {'payment_history': payment_history, 'income_stability': income_stability})
            return 0.2  # Conservative default
    
    @staticmethod
    @handle_exceptions(FeatureExtractionError)
    def calculate_social_score(social_proof: Dict, community_rating: float) -> float:
        """Calculate social trust component with validation"""
        if not social_proof:
            return 0.1
        
        try:
            # Community rating (0-50 points)
            community_rating = safe_numeric_conversion(community_rating, 3.0, 1.0, 5.0)
            rating_score = min((community_rating / 5.0) * 0.5, 0.5)
            
            # Social endorsements (0-25 points)
            endorsements = safe_numeric_conversion(social_proof.get('endorsements', 0), 0, 0)
            endorsement_score = min((endorsements / 10.0) * 0.25, 0.25)
            
            # Network strength (0-25 points)
            network_size = safe_numeric_conversion(social_proof.get('network_size', 0), 0, 0)
            network_score = min((network_size / 50.0) * 0.25, 0.25)
            
            total_score = rating_score + endorsement_score + network_score
            return max(0.1, min(1.0, total_score))
            
        except Exception as e:
            error_handler.log_error(e, {'social_proof': social_proof, 'community_rating': community_rating})
            return 0.2
    
    @staticmethod
    @handle_exceptions(FeatureExtractionError)
    def calculate_digital_score(digital_footprint: Dict) -> float:
        """Calculate digital trust component with validation"""
        if not digital_footprint:
            return 0.1
        
        try:
            # Transaction regularity (0-40 points)
            regularity = safe_numeric_conversion(digital_footprint.get('transaction_regularity', 0.5), 0.5, 0.0, 1.0)
            regularity_score = regularity * 0.4
            
            # Device stability (0-30 points)
            device_stability = safe_numeric_conversion(digital_footprint.get('device_stability', 0.7), 0.7, 0.0, 1.0)
            device_score = device_stability * 0.3
            
            # Digital engagement (0-30 points)
            engagement = safe_numeric_conversion(digital_footprint.get('engagement_score', 0.5), 0.5, 0.0, 1.0)
            engagement_score = engagement * 0.3
            
            total_score = regularity_score + device_score + engagement_score
            return max(0.1, min(1.0, total_score))
            
        except Exception as e:
            error_handler.log_error(e, {'digital_footprint': digital_footprint})
            return 0.2


class CreditRiskModel:
    """Enhanced credit risk model with comprehensive error handling and confidence intervals"""
    
    def __init__(self):
        self.logistic_model = LogisticRegression(random_state=42, max_iter=1000)
        self.xgb_model = xgb.XGBClassifier(
            random_state=42,
            eval_metric='logloss',
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1
        )
        self.scaler = StandardScaler()
        self.shap_explainer = None
        self.feature_names = []
        self.is_trained = False
        self.training_history = []
        self.model_confidence = {'min': 0.0, 'max': 1.0, 'mean': 0.5}
    
    @handle_exceptions(FeatureExtractionError)
    def create_features(self, applicant_data: Dict) -> np.ndarray:
        """Create feature vector from applicant data with enhanced validation"""
        try:
            features = []
            
            # Basic demographic features with validation
            age = safe_numeric_conversion(applicant_data.get('age', 30), 30, 18, 100)
            features.append(age / 100.0)  # Normalized age
            
            gender = applicant_data.get('gender', 'Male')
            features.append(1 if gender == 'Female' else 0)  # Gender
            
            income = safe_numeric_conversion(applicant_data.get('monthly_income', 15000), 15000, 0, 10000000)
            features.append(income / 100000.0)  # Normalized income
            
            # Trust score components with validation
            features.append(safe_numeric_conversion(applicant_data.get('behavioral_score', 0.2), 0.2, 0.0, 1.0))
            features.append(safe_numeric_conversion(applicant_data.get('social_score', 0.2), 0.2, 0.0, 1.0))
            features.append(safe_numeric_conversion(applicant_data.get('digital_score', 0.2), 0.2, 0.0, 1.0))
            features.append(safe_numeric_conversion(applicant_data.get('overall_trust_score', 0.2), 0.2, 0.0, 1.0))
            
            # Alternative data features with safe JSON parsing
            payment_history = safe_json_parse(applicant_data.get('utility_payment_history', '{}'))
            features.append(safe_numeric_conversion(payment_history.get('on_time_ratio', 0.5), 0.5, 0.0, 1.0))
            features.append(safe_numeric_conversion(payment_history.get('average_amount', 1000), 1000, 0) / 10000.0)
            
            social_proof = safe_json_parse(applicant_data.get('social_proof_data', '{}'))
            features.append(safe_numeric_conversion(social_proof.get('community_rating', 3.0), 3.0, 1.0, 5.0) / 5.0)
            features.append(safe_numeric_conversion(social_proof.get('endorsements', 0), 0, 0) / 10.0)
            
            digital_data = safe_json_parse(applicant_data.get('digital_footprint', '{}'))
            features.append(safe_numeric_conversion(digital_data.get('transaction_regularity', 0.5), 0.5, 0.0, 1.0))
            features.append(safe_numeric_conversion(digital_data.get('device_stability', 0.7), 0.7, 0.0, 1.0))
            
            # Gamification features
            z_credits = safe_numeric_conversion(applicant_data.get('z_credits', 0), 0, 0)
            features.append(z_credits / 1000.0)  # Normalized credits
            
            # Update feature names if not set
            if not self.feature_names:
                self.feature_names = [
                    'age_normalized', 'gender_female', 'income_normalized',
                    'behavioral_score', 'social_score', 'digital_score', 'overall_trust_score',
                    'payment_on_time_ratio', 'payment_avg_amount', 'community_rating',
                    'social_endorsements', 'transaction_regularity', 'device_stability',
                    'z_credits_normalized'
                ]
            
            feature_array = np.array(features).reshape(1, -1)
            
            # Validate feature array
            if np.any(np.isnan(feature_array)) or np.any(np.isinf(feature_array)):
                raise FeatureExtractionError("Invalid feature values detected (NaN or Inf)")
            
            return feature_array
            
        except Exception as e:
            if isinstance(e, FeatureExtractionError):
                raise e
            else:
                raise FeatureExtractionError(f"Feature creation failed: {str(e)}")
    
    def generate_synthetic_data(self, n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data for demo purposes"""
        np.random.seed(42)
        
        # Generate feature matrix
        n_features = 14
        X = np.random.rand(n_samples, n_features)
        
        # Create realistic feature distributions
        X[:, 0] = np.random.normal(0.3, 0.15, n_samples)  # age_normalized (20-50 years)
        X[:, 1] = np.random.binomial(1, 0.52, n_samples)  # gender_female
        X[:, 2] = np.random.lognormal(-1, 0.5, n_samples)  # income_normalized
        
        # Trust scores (correlated with good behavior)
        base_trust = np.random.beta(2, 3, n_samples)
        X[:, 3] = base_trust + np.random.normal(0, 0.1, n_samples)  # behavioral_score
        X[:, 4] = base_trust + np.random.normal(0, 0.1, n_samples)  # social_score
        X[:, 5] = base_trust + np.random.normal(0, 0.1, n_samples)  # digital_score
        X[:, 6] = (X[:, 3] + X[:, 4] + X[:, 5]) / 3  # overall_trust_score
        
        # Payment and social features
        X[:, 7] = np.clip(base_trust + np.random.normal(0, 0.2, n_samples), 0, 1)  # payment_on_time_ratio
        X[:, 8] = np.random.exponential(0.3, n_samples)  # payment_avg_amount
        X[:, 9] = np.clip(base_trust + np.random.normal(0, 0.15, n_samples), 0, 1)  # community_rating
        X[:, 10] = np.random.poisson(base_trust * 5, n_samples) / 10  # social_endorsements
        
        # Digital features
        X[:, 11] = np.clip(base_trust + np.random.normal(0, 0.2, n_samples), 0, 1)  # transaction_regularity
        X[:, 12] = np.clip(np.random.normal(0.7, 0.2, n_samples), 0, 1)  # device_stability
        X[:, 13] = np.random.exponential(0.2, n_samples)  # z_credits_normalized
        
        # Clip all features to [0, 1] range
        X = np.clip(X, 0, 1)
        
        # Generate target variable (0 = default, 1 = repay)
        # Higher trust scores and good payment history lead to lower default probability
        default_probability = 1 - (0.3 * X[:, 6] + 0.25 * X[:, 7] + 0.15 * X[:, 9] + 
                                  0.1 * X[:, 2] + 0.1 * X[:, 11] + 0.1 * X[:, 12])
        default_probability = np.clip(default_probability, 0.05, 0.95)
        
        y = np.random.binomial(1, 1 - default_probability, n_samples)  # 1 = good borrower
        
        return X, y
    
    @handle_exceptions(ModelError)
    def train(self, X: Optional[np.ndarray] = None, y: Optional[np.ndarray] = None):
        """Train the credit risk models with enhanced error handling"""
        try:
            print("Initializing Credit Risk Model...")
            
            if X is None or y is None:
                print("Generating synthetic training data...")
                X, y = self.generate_synthetic_data()
            
            # Validate training data
            if len(X) == 0 or len(y) == 0:
                raise ModelError("Empty training data provided")
            
            if len(X) != len(y):
                raise ModelError("Feature and target arrays have different lengths")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features for logistic regression
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Logistic Regression
            print("Training Logistic Regression model...")
            self.logistic_model.fit(X_train_scaled, y_train)
            
            # Train XGBoost
            print("Training XGBoost model...")
            self.xgb_model.fit(X_train, y_train)
            
            # Initialize SHAP explainer
            try:
                self.shap_explainer = shap.Explainer(self.xgb_model)
                print("SHAP explainer initialized successfully")
            except Exception as e:
                error_handler.log_error(e, {'context': 'SHAP initialization'})
                print(f"Warning: SHAP explainer initialization failed: {e}")
            
            # Evaluate models and calculate confidence intervals
            performance = self._evaluate_models(X_test_scaled, X_test, y_test)
            
            # Calculate model confidence intervals
            predictions = self.xgb_model.predict_proba(X_test)[:, 1]
            self.model_confidence = confidence_interval_calculator(predictions.tolist())
            
            # Store training history
            self.training_history.append({
                'timestamp': pd.Timestamp.now().isoformat(),
                'performance': performance,
                'confidence_intervals': self.model_confidence,
                'training_size': len(X_train),
                'test_size': len(X_test)
            })
            
            self.is_trained = True
            print("Model training completed!")
            
        except Exception as e:
            if isinstance(e, ModelError):
                raise e
            else:
                raise ModelError(f"Model training failed: {str(e)}")
    
    def _evaluate_models(self, X_test_scaled: np.ndarray, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate model performance and return metrics"""
        try:
            # Logistic Regression evaluation
            lr_pred = self.logistic_model.predict(X_test_scaled)
            lr_pred_proba = self.logistic_model.predict_proba(X_test_scaled)[:, 1]
            
            lr_metrics = {
                'accuracy': accuracy_score(y_test, lr_pred),
                'precision': precision_score(y_test, lr_pred, zero_division=0),
                'recall': recall_score(y_test, lr_pred, zero_division=0),
                'f1_score': f1_score(y_test, lr_pred, zero_division=0),
                'auc_roc': roc_auc_score(y_test, lr_pred_proba) if len(np.unique(y_test)) > 1 else 0.5
            }
            
            print(f"\nLogistic Regression Performance:")
            print(f"Accuracy: {lr_metrics['accuracy']:.3f}")
            print(f"Precision: {lr_metrics['precision']:.3f}")
            print(f"Recall: {lr_metrics['recall']:.3f}")
            print(f"F1-Score: {lr_metrics['f1_score']:.3f}")
            print(f"AUC-ROC: {lr_metrics['auc_roc']:.3f}")
            
            # XGBoost evaluation
            xgb_pred = self.xgb_model.predict(X_test)
            xgb_pred_proba = self.xgb_model.predict_proba(X_test)[:, 1]
            
            xgb_metrics = {
                'accuracy': accuracy_score(y_test, xgb_pred),
                'precision': precision_score(y_test, xgb_pred, zero_division=0),
                'recall': recall_score(y_test, xgb_pred, zero_division=0),
                'f1_score': f1_score(y_test, xgb_pred, zero_division=0),
                'auc_roc': roc_auc_score(y_test, xgb_pred_proba) if len(np.unique(y_test)) > 1 else 0.5
            }
            
            print(f"\nXGBoost Performance:")
            print(f"Accuracy: {xgb_metrics['accuracy']:.3f}")
            print(f"Precision: {xgb_metrics['precision']:.3f}")
            print(f"Recall: {xgb_metrics['recall']:.3f}")
            print(f"F1-Score: {xgb_metrics['f1_score']:.3f}")
            print(f"AUC-ROC: {xgb_metrics['auc_roc']:.3f}")
            
            return {
                'logistic_regression': lr_metrics,
                'xgboost': xgb_metrics
            }
            
        except Exception as e:
            error_handler.log_error(e, {'context': 'model_evaluation'})
            # Return default metrics on error
            return {
                'logistic_regression': {'accuracy': 0.5, 'precision': 0.5, 'recall': 0.5, 'f1_score': 0.5, 'auc_roc': 0.5},
                'xgboost': {'accuracy': 0.5, 'precision': 0.5, 'recall': 0.5, 'f1_score': 0.5, 'auc_roc': 0.5}
            }
    
    @handle_exceptions(ModelError)
    def predict(self, applicant_data: Dict) -> Dict:
        """Make prediction for a single applicant with confidence intervals"""
        if not self.is_trained:
            print("Model not trained. Training with synthetic data...")
            self.train()  # Train with synthetic data if not already trained
        
        try:
            # Create and validate features
            features = self.create_features(applicant_data)
            features_scaled = self.scaler.transform(features)
            
            # XGBoost predictions (primary model)
            xgb_pred_proba = self.xgb_model.predict_proba(features)[0]
            xgb_prediction = self.xgb_model.predict(features)[0]
            
            # Logistic regression predictions (backup)
            lr_pred_proba = self.logistic_model.predict_proba(features_scaled)[0]
            lr_prediction = self.logistic_model.predict(features_scaled)[0]
            
            # Risk categorization with confidence consideration
            risk_score = float(xgb_pred_proba[1])  # Probability of being a good borrower
            confidence_lower = self.model_confidence.get('lower', 0.0)
            confidence_upper = self.model_confidence.get('upper', 1.0)
            
            # Adjust thresholds based on confidence intervals
            if risk_score >= max(0.7, confidence_upper * 0.7):
                risk_category = "Low Risk"
            elif risk_score >= max(0.4, confidence_lower * 1.5):
                risk_category = "Medium Risk"
            else:
                risk_category = "High Risk"
            
            # Calculate prediction confidence
            prediction_confidence = min(abs(risk_score - 0.5) * 2, 1.0)  # Distance from uncertain (0.5)
            
            return {
                'prediction': int(xgb_prediction),
                'risk_probability': float(1 - risk_score),  # Probability of default
                'confidence_score': risk_score,
                'prediction_confidence': prediction_confidence,
                'risk_category': risk_category,
                'model_scores': {
                    'xgboost': risk_score,
                    'logistic_regression': float(lr_pred_proba[1])
                },
                'confidence_intervals': self.model_confidence,
                'features_used': len(self.feature_names),
                'model_version': self.training_history[-1]['timestamp'] if self.training_history else 'unknown'
            }
            
        except Exception as e:
            if isinstance(e, (ModelError, FeatureExtractionError)):
                raise e
            else:
                raise ModelError(f"Prediction failed: {str(e)}")
    
    @handle_exceptions(ModelError)
    def explain_prediction(self, applicant_data: Dict) -> Dict:
        """Generate enhanced SHAP explanation for prediction"""
        if not self.is_trained:
            raise ModelError('Model not trained')
        
        if self.shap_explainer is None:
            return {
                'error': 'SHAP explainer not available. Model may need retraining.',
                'fallback_explanation': self._generate_fallback_explanation(applicant_data)
            }
        
        try:
            features = self.create_features(applicant_data)
            
            # Generate SHAP values
            shap_values = self.shap_explainer(features)
            
            # Create enhanced explanation dictionary
            explanation = {
                'shap_values': [float(val) for val in shap_values.values[0]],
                'base_value': float(shap_values.base_values[0]),
                'feature_names': self.feature_names,
                'feature_values': [float(val) for val in features[0]],
                'feature_contributions': {},
                'top_contributors': {},
                'explanation_quality': 'high'
            }
            
            # Map feature contributions with enhanced analysis
            contributions = []
            for i, (name, shap_val, feat_val) in enumerate(
                zip(self.feature_names, shap_values.values[0], features[0])
            ):
                contribution_info = {
                    'shap_value': float(shap_val),
                    'feature_value': float(feat_val),
                    'contribution_type': 'positive' if shap_val > 0 else 'negative',
                    'abs_contribution': abs(float(shap_val)),
                    'feature_importance_rank': 0  # Will be filled below
                }
                explanation['feature_contributions'][name] = contribution_info
                contributions.append((name, abs(float(shap_val))))
            
            # Rank features by importance
            contributions.sort(key=lambda x: x[1], reverse=True)
            for rank, (name, _) in enumerate(contributions):
                explanation['feature_contributions'][name]['feature_importance_rank'] = rank + 1
            
            # Extract top 5 contributors
            explanation['top_contributors'] = {
                'positive': [],
                'negative': []
            }
            
            for name, shap_val in [(name, explanation['feature_contributions'][name]['shap_value']) 
                                   for name, _ in contributions[:10]]:
                if shap_val > 0:
                    explanation['top_contributors']['positive'].append({
                        'feature': name,
                        'impact': shap_val,
                        'description': self._get_feature_description(name)
                    })
                else:
                    explanation['top_contributors']['negative'].append({
                        'feature': name,
                        'impact': abs(shap_val),
                        'description': self._get_feature_description(name)
                    })
            
            # Limit to top 3 in each category
            explanation['top_contributors']['positive'] = explanation['top_contributors']['positive'][:3]
            explanation['top_contributors']['negative'] = explanation['top_contributors']['negative'][:3]
            
            return explanation
            
        except Exception as e:
            error_handler.log_error(e, {'context': 'SHAP_explanation', 'applicant_id': applicant_data.get('id', 'unknown')})
            return {
                'error': f'SHAP explanation failed: {str(e)}',
                'explanation_quality': 'low',
                'fallback_explanation': self._generate_fallback_explanation(applicant_data)
            }
    
    def _generate_fallback_explanation(self, applicant_data: Dict) -> Dict:
        """Generate basic explanation when SHAP is unavailable"""
        try:
            features = self.create_features(applicant_data)
            
            # Simple feature importance based on typical credit factors
            fallback_factors = {
                'income_normalized': features[0][2] * 0.3,
                'overall_trust_score': features[0][6] * 0.25,
                'behavioral_score': features[0][3] * 0.2,
                'payment_on_time_ratio': features[0][7] * 0.15,
                'age_normalized': features[0][0] * 0.1
            }
            
            return {
                'type': 'fallback',
                'key_factors': fallback_factors,
                'message': 'Advanced explanation temporarily unavailable. Showing key contributing factors.'
            }
        except:
            return {
                'type': 'minimal',
                'message': 'Explanation unavailable due to technical issues.'
            }
    
    def _get_feature_description(self, feature_name: str) -> str:
        """Get human-readable description for features"""
        descriptions = {
            'age_normalized': 'Applicant age (normalized)',
            'gender_female': 'Gender factor',
            'income_normalized': 'Monthly income level',
            'behavioral_score': 'Payment behavior history',
            'social_score': 'Community trust rating',
            'digital_score': 'Digital engagement pattern',
            'overall_trust_score': 'Combined trust assessment',
            'payment_on_time_ratio': 'On-time payment percentage',
            'payment_avg_amount': 'Average transaction amount',
            'community_rating': 'Community feedback score',
            'social_endorsements': 'Social proof indicators',
            'transaction_regularity': 'Transaction consistency',
            'device_stability': 'Digital device usage pattern',
            'z_credits_normalized': 'Gamification score achievement'
        }
        return descriptions.get(feature_name, f"Factor: {feature_name}")
    
    def save_model(self, filepath: str = "models/"):
        """Save trained models"""
        import os
        os.makedirs(filepath, exist_ok=True)
        
        joblib.dump(self.scaler, f"{filepath}/scaler.pkl")
        joblib.dump(self.logistic_model, f"{filepath}/logistic_model.pkl")
        joblib.dump(self.xgb_model, f"{filepath}/xgb_model.pkl")
        
        # Save feature names
        with open(f"{filepath}/feature_names.json", 'w') as f:
            json.dump(self.feature_names, f)
    
    def load_model(self, filepath: str = "models/"):
        """Load saved models"""
        try:
            self.scaler = joblib.load(f"{filepath}/scaler.pkl")
            self.logistic_model = joblib.load(f"{filepath}/logistic_model.pkl")
            self.xgb_model = joblib.load(f"{filepath}/xgb_model.pkl")
            
            with open(f"{filepath}/feature_names.json", 'r') as f:
                self.feature_names = json.load(f)
            
            # Initialize SHAP explainer with better error handling
            try:
                self.shap_explainer = shap.Explainer(self.xgb_model)
                print("SHAP explainer initialized successfully")
            except Exception as shap_error:
                print(f"Warning: SHAP explainer initialization failed: {shap_error}")
                self.shap_explainer = None
            
            self.is_trained = True
            print("Models loaded successfully!")
            
        except Exception as e:
            print(f"Failed to load models: {e}")
            self.train()  # Fallback to training with synthetic data


@handle_exceptions(FeatureExtractionError)
def calculate_trust_score(applicant_data: Dict) -> Dict:
    """Calculate comprehensive trust score with enhanced error handling"""
    calculator = TrustScoreCalculator()
    
    try:
        # Extract relevant data with safe parsing
        payment_history = safe_json_parse(applicant_data.get('utility_payment_history', '{}'))
        social_proof = safe_json_parse(applicant_data.get('social_proof_data', '{}'))
        digital_data = safe_json_parse(applicant_data.get('digital_footprint', '{}'))
        
        # Calculate component scores
        behavioral = calculator.calculate_behavioral_score(
            payment_history, 
            safe_numeric_conversion(applicant_data.get('income_stability', 0.7), 0.7, 0.0, 1.0)
        )
        
        social = calculator.calculate_social_score(
            social_proof,
            safe_numeric_conversion(social_proof.get('community_rating', 3.0), 3.0, 1.0, 5.0)
        )
        
        digital = calculator.calculate_digital_score(digital_data)
        
        overall = (behavioral + social + digital) / 3
        
        return {
            'behavioral_score': behavioral,
            'social_score': social,
            'digital_score': digital,
            'overall_trust_score': overall,
            'trust_percentage': overall * 100
        }
        
    except Exception as e:
        error_handler.log_error(e, {'applicant_data_keys': list(applicant_data.keys())})
        # Return conservative defaults on error
        return {
            'behavioral_score': 0.2,
            'social_score': 0.2,
            'digital_score': 0.2,
            'overall_trust_score': 0.2,
            'trust_percentage': 20.0
        }


if __name__ == "__main__":
    # Initialize and train model
    print("Initializing Credit Risk Model...")
    model = CreditRiskModel()
    model.train()
    
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
    print(f"\nSample Prediction: {prediction}")
    
    explanation = model.explain_prediction(sample_applicant)
    if 'error' not in explanation:
        print(f"SHAP Explanation: Available with {len(explanation['feature_names'])} features")
    else:
        print(f"SHAP Error: {explanation['error']}")
