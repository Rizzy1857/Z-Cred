"""
Machine Learning Pipeline for Z-Score Credit Risk Assessment

Implements logistic regression baseline and XGBoost ensemble models with
SHAP explainability for transparent credit decisions.
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


class TrustScoreCalculator:
    """Calculate trust scores from alternative data"""
    
    @staticmethod
    def calculate_behavioral_score(payment_history: Dict, income_stability: float) -> float:
        """Calculate behavioral trust component"""
        if not payment_history:
            return 0.1
        
        # Payment punctuality (0-40 points)
        on_time_ratio = payment_history.get('on_time_payments', 0) / max(payment_history.get('total_payments', 1), 1)
        punctuality_score = min(on_time_ratio * 0.4, 0.4)
        
        # Income stability (0-30 points)
        stability_score = min(income_stability * 0.3, 0.3)
        
        # Transaction consistency (0-30 points)
        avg_amount = payment_history.get('average_amount', 0)
        consistency_score = min((avg_amount / 10000) * 0.3, 0.3) if avg_amount > 0 else 0.1
        
        return punctuality_score + stability_score + consistency_score
    
    @staticmethod
    def calculate_social_score(social_proof: Dict, community_rating: float) -> float:
        """Calculate social trust component"""
        if not social_proof:
            return 0.1
        
        # Community endorsements (0-40 points)
        endorsements = social_proof.get('endorsements', 0)
        endorsement_score = min(endorsements * 0.08, 0.4)
        
        # Community rating (0-35 points)
        rating_score = min((community_rating / 5.0) * 0.35, 0.35)
        
        # Group participation (0-25 points)
        participation = social_proof.get('group_participation_score', 0)
        participation_score = min(participation * 0.25, 0.25)
        
        return endorsement_score + rating_score + participation_score
    
    @staticmethod
    def calculate_digital_score(digital_data: Dict, device_stability: float) -> float:
        """Calculate digital trust component"""
        if not digital_data:
            return 0.1
        
        # Digital transaction patterns (0-35 points)
        transaction_score = min(digital_data.get('transaction_regularity', 0) * 0.35, 0.35)
        
        # Device and connectivity stability (0-30 points)
        stability_score = min(device_stability * 0.3, 0.3)
        
        # Digital literacy indicators (0-35 points)
        literacy_score = min(digital_data.get('digital_literacy_score', 0) * 0.35, 0.35)
        
        return transaction_score + stability_score + literacy_score


class CreditRiskModel:
    """Main ML model for credit risk assessment"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.logistic_model = LogisticRegression(random_state=42)
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.is_trained = False
        self.feature_names = []
        self.shap_explainer = None
    
    def create_features(self, applicant_data: Dict) -> np.ndarray:
        """Create feature vector from applicant data"""
        features = []
        
        # Basic demographic features
        features.append(applicant_data.get('age', 30) / 100.0)  # Normalized age
        features.append(1 if applicant_data.get('gender') == 'Female' else 0)  # Gender
        features.append(applicant_data.get('monthly_income', 15000) / 100000.0)  # Normalized income
        
        # Trust score components
        features.append(applicant_data.get('behavioral_score', 0.2))
        features.append(applicant_data.get('social_score', 0.2))
        features.append(applicant_data.get('digital_score', 0.2))
        features.append(applicant_data.get('overall_trust_score', 0.2))
        
        # Alternative data features
        payment_history = json.loads(applicant_data.get('utility_payment_history', '{}')) if isinstance(applicant_data.get('utility_payment_history'), str) else applicant_data.get('utility_payment_history', {})
        features.append(payment_history.get('on_time_ratio', 0.5))
        features.append(payment_history.get('average_amount', 1000) / 10000.0)
        
        social_proof = json.loads(applicant_data.get('social_proof_data', '{}')) if isinstance(applicant_data.get('social_proof_data'), str) else applicant_data.get('social_proof_data', {})
        features.append(social_proof.get('community_rating', 3.0) / 5.0)
        features.append(social_proof.get('endorsements', 0) / 10.0)
        
        digital_data = json.loads(applicant_data.get('digital_footprint', '{}')) if isinstance(applicant_data.get('digital_footprint'), str) else applicant_data.get('digital_footprint', {})
        features.append(digital_data.get('transaction_regularity', 0.5))
        features.append(digital_data.get('device_stability', 0.7))
        
        # Gamification features
        features.append(applicant_data.get('z_credits', 0) / 1000.0)  # Normalized credits
        
        self.feature_names = [
            'age_normalized', 'gender_female', 'income_normalized',
            'behavioral_score', 'social_score', 'digital_score', 'overall_trust_score',
            'payment_on_time_ratio', 'payment_avg_amount', 'community_rating',
            'social_endorsements', 'transaction_regularity', 'device_stability',
            'z_credits_normalized'
        ]
        
        return np.array(features).reshape(1, -1)
    
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
    
    def train(self, X: Optional[np.ndarray] = None, y: Optional[np.ndarray] = None):
        """Train both logistic regression and XGBoost models"""
        if X is None or y is None:
            print("Generating synthetic training data...")
            X, y = self.generate_synthetic_data(1000)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train logistic regression
        print("Training Logistic Regression model...")
        self.logistic_model.fit(X_train_scaled, y_train)
        
        # Train XGBoost
        print("Training XGBoost model...")
        self.xgb_model.fit(X_train, y_train)
        
        # Initialize SHAP explainer
        self.shap_explainer = shap.Explainer(self.xgb_model)
        
        # Evaluate models
        self._evaluate_models(X_test_scaled, X_test, y_test)
        
        self.is_trained = True
        print("Model training completed!")
    
    def _evaluate_models(self, X_test_scaled: np.ndarray, X_test: np.ndarray, y_test: np.ndarray):
        """Evaluate model performance"""
        # Logistic Regression evaluation
        lr_pred = self.logistic_model.predict(X_test_scaled)
        lr_pred_proba = self.logistic_model.predict_proba(X_test_scaled)[:, 1]
        
        print(f"\nLogistic Regression Performance:")
        print(f"Accuracy: {accuracy_score(y_test, lr_pred):.3f}")
        print(f"Precision: {precision_score(y_test, lr_pred):.3f}")
        print(f"Recall: {recall_score(y_test, lr_pred):.3f}")
        print(f"F1-Score: {f1_score(y_test, lr_pred):.3f}")
        print(f"AUC-ROC: {roc_auc_score(y_test, lr_pred_proba):.3f}")
        
        # XGBoost evaluation
        xgb_pred = self.xgb_model.predict(X_test)
        xgb_pred_proba = self.xgb_model.predict_proba(X_test)[:, 1]
        
        print(f"\nXGBoost Performance:")
        print(f"Accuracy: {accuracy_score(y_test, xgb_pred):.3f}")
        print(f"Precision: {precision_score(y_test, xgb_pred):.3f}")
        print(f"Recall: {recall_score(y_test, xgb_pred):.3f}")
        print(f"F1-Score: {f1_score(y_test, xgb_pred):.3f}")
        print(f"AUC-ROC: {roc_auc_score(y_test, xgb_pred_proba):.3f}")
    
    def predict(self, applicant_data: Dict) -> Dict:
        """Make prediction for a single applicant"""
        if not self.is_trained:
            self.train()  # Train with synthetic data if not already trained
        
        # Create features
        features = self.create_features(applicant_data)
        features_scaled = self.scaler.transform(features)
        
        # XGBoost predictions (primary model)
        xgb_pred_proba = self.xgb_model.predict_proba(features)[0]
        xgb_prediction = self.xgb_model.predict(features)[0]
        
        # Logistic regression predictions (backup)
        lr_pred_proba = self.logistic_model.predict_proba(features_scaled)[0]
        lr_prediction = self.logistic_model.predict(features_scaled)[0]
        
        # Risk categorization
        risk_score = xgb_pred_proba[1]  # Probability of being a good borrower
        if risk_score >= 0.7:
            risk_category = "Low Risk"
        elif risk_score >= 0.4:
            risk_category = "Medium Risk"
        else:
            risk_category = "High Risk"
        
        return {
            'prediction': int(xgb_prediction),
            'risk_probability': float(1 - risk_score),  # Probability of default
            'confidence_score': float(risk_score),
            'risk_category': risk_category,
            'model_scores': {
                'xgboost': float(risk_score),
                'logistic_regression': float(lr_pred_proba[1])
            },
            'features_used': len(self.feature_names)
        }
    
    def explain_prediction(self, applicant_data: Dict) -> Dict:
        """Generate SHAP explanation for prediction"""
        if not self.is_trained or self.shap_explainer is None:
            return {'error': 'Model not trained or SHAP explainer not available'}
        
        features = self.create_features(applicant_data)
        
        try:
            # Generate SHAP values
            shap_values = self.shap_explainer(features)
            
            # Create explanation dictionary
            explanation = {
                'shap_values': shap_values.values[0].tolist(),
                'base_value': float(shap_values.base_values[0]),
                'feature_names': self.feature_names,
                'feature_values': features[0].tolist(),
                'feature_contributions': {}
            }
            
            # Map feature contributions
            for i, (name, shap_val, feat_val) in enumerate(
                zip(self.feature_names, shap_values.values[0], features[0])
            ):
                explanation['feature_contributions'][name] = {
                    'shap_value': float(shap_val),
                    'feature_value': float(feat_val),
                    'contribution_type': 'positive' if shap_val > 0 else 'negative'
                }
            
            return explanation
            
        except Exception as e:
            return {'error': f'SHAP explanation failed: {str(e)}'}
    
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
            
            self.shap_explainer = shap.Explainer(self.xgb_model)
            self.is_trained = True
            print("Models loaded successfully!")
            
        except Exception as e:
            print(f"Failed to load models: {e}")
            self.train()  # Fallback to training with synthetic data


def calculate_trust_score(applicant_data: Dict) -> Dict:
    """Calculate comprehensive trust score"""
    calculator = TrustScoreCalculator()
    
    # Extract relevant data
    payment_history = json.loads(applicant_data.get('utility_payment_history', '{}')) if isinstance(applicant_data.get('utility_payment_history'), str) else applicant_data.get('utility_payment_history', {})
    social_proof = json.loads(applicant_data.get('social_proof_data', '{}')) if isinstance(applicant_data.get('social_proof_data'), str) else applicant_data.get('social_proof_data', {})
    digital_data = json.loads(applicant_data.get('digital_footprint', '{}')) if isinstance(applicant_data.get('digital_footprint'), str) else applicant_data.get('digital_footprint', {})
    
    # Calculate component scores
    behavioral = calculator.calculate_behavioral_score(
        payment_history, 
        applicant_data.get('income_stability', 0.7)
    )
    
    social = calculator.calculate_social_score(
        social_proof,
        social_proof.get('community_rating', 3.0)
    )
    
    digital = calculator.calculate_digital_score(
        digital_data,
        digital_data.get('device_stability', 0.7)
    )
    
    overall = (behavioral + social + digital) / 3
    
    return {
        'behavioral_score': behavioral,
        'social_score': social,
        'digital_score': digital,
        'overall_trust_score': overall,
        'trust_percentage': overall * 100
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
