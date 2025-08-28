"""
SHAP Explainability Dashboard Module

Provides interactive ML model explanations using SHAP (SHapley Additive exPlanations)
to help users understand why they received their trust scores and risk assessments.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional
import shap
from model_integration import model_integrator


class SHAPExplainer:
    """Handles SHAP explanations for trust scores and risk predictions"""
    
    def __init__(self):
        self.model = None
        self.explainer = None
        self.feature_names = []
        
    def get_model_and_explainer(self):
        """Initialize model and SHAP explainer if not already done"""
        if self.model is None:
            self.model = model_integrator.get_credit_model()
            # SHAP explainer is already initialized in the model
            self.explainer = self.model.shap_explainer
            self.feature_names = self.model.feature_names
        return self.model, self.explainer
    
    def get_explanation(self, applicant_data: Dict) -> Optional[Dict]:
        """Get SHAP explanation for a single applicant"""
        try:
            model, explainer = self.get_model_and_explainer()
            
            if explainer is None:
                st.warning("SHAP explainer not available. Model may need retraining.")
                return None
            
            # Use the model's built-in explanation method
            explanation = model.explain_prediction(applicant_data)
            
            if 'error' in explanation:
                st.warning(f"SHAP explanation unavailable: {explanation['error']}")
                return None
            
            # Also get the prediction for additional context
            prediction = model.predict(applicant_data)
            
            # Combine explanation with prediction data
            enhanced_explanation = {
                **explanation,
                'prediction_data': prediction
            }
                
            return enhanced_explanation
            
        except Exception as e:
            st.error(f"Error generating SHAP explanation: {e}")
            return None
    
    def create_waterfall_chart(self, explanation: Dict) -> Optional[go.Figure]:
        """Create SHAP waterfall chart showing feature contributions"""
        if not explanation:
            return None
            
        try:
            shap_values = explanation['shap_values']
            feature_names = explanation['feature_names']
            feature_values = explanation['feature_values']
            base_value = explanation['base_value']
            
            # Create waterfall data
            sorted_idx = np.argsort(np.abs(shap_values))[::-1][:10]  # Top 10 features
            
            values = []
            labels = []
            colors = []
            
            # Base value
            values.append(base_value)
            labels.append("Base Score")
            colors.append("gray")
            
            running_total = base_value
            
            for idx in sorted_idx:
                shap_val = shap_values[idx]
                feature_name = feature_names[idx]
                feature_val = feature_values[idx]
                
                values.append(shap_val)
                labels.append(f"{feature_name}<br>({feature_val:.3f})")
                colors.append("green" if shap_val > 0 else "red")
                running_total += shap_val
            
            # Final prediction
            values.append(running_total)
            labels.append("Final Score")
            colors.append("blue")
            
            # Create waterfall chart
            fig = go.Figure(go.Waterfall(
                name="SHAP Values",
                orientation="v",
                measure=["absolute"] + ["relative"] * len(sorted_idx) + ["total"],
                x=labels,
                textposition="outside",
                text=[f"{v:.3f}" for v in values],
                y=values,
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                increasing={"marker": {"color": "green"}},
                decreasing={"marker": {"color": "red"}},
                totals={"marker": {"color": "blue"}}
            ))
            
            fig.update_layout(
                title="Why did you get this score? - Feature Contributions",
                xaxis_title="Features",
                yaxis_title="Impact on Score",
                height=500,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating waterfall chart: {e}")
            return None
    
    def create_feature_importance_chart(self, explanation: Dict) -> Optional[go.Figure]:
        """Create horizontal bar chart of feature importance"""
        if not explanation:
            return None
            
        try:
            shap_values = explanation['shap_values']
            feature_names = explanation['feature_names']
            feature_values = explanation['feature_values']
            
            # Get top 10 most important features
            abs_shap = np.abs(shap_values)
            sorted_idx = np.argsort(abs_shap)[::-1][:10]
            
            top_features = [feature_names[i] for i in sorted_idx]
            top_shap = [shap_values[i] for i in sorted_idx]
            top_values = [feature_values[i] for i in sorted_idx]
            
            # Create color coding
            colors = ['green' if val > 0 else 'red' for val in top_shap]
            
            fig = go.Figure(go.Bar(
                y=top_features,
                x=top_shap,
                orientation='h',
                marker_color=colors,
                text=[f"Value: {val:.3f}" for val in top_values],
                textposition='auto',
            ))
            
            fig.update_layout(
                title="Feature Impact on Your Score",
                xaxis_title="SHAP Value (Impact on Score)",
                yaxis_title="Features",
                height=400,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating feature importance chart: {e}")
            return None
    
    def generate_plain_language_explanation(self, explanation: Dict, applicant_data: Dict) -> str:
        """Generate user-friendly explanation in plain language"""
        if not explanation:
            return "Unable to generate explanation at this time."
        
        try:
            shap_values = explanation['shap_values']
            feature_names = explanation['feature_names']
            feature_values = explanation['feature_values']
            prediction_data = explanation.get('prediction_data', {})
            
            # Get top positive and negative influences
            sorted_idx = np.argsort(np.abs(shap_values))[::-1]
            top_positive = []
            top_negative = []
            
            for idx in sorted_idx[:5]:
                if shap_values[idx] > 0:
                    top_positive.append((feature_names[idx], shap_values[idx], feature_values[idx]))
                else:
                    top_negative.append((feature_names[idx], shap_values[idx], feature_values[idx]))
            
            # Generate explanation
            risk_category = prediction_data.get('risk_category', 'Unknown')
            confidence = prediction_data.get('prediction_confidence', 0)
            
            explanation_text = f"""
## 🎯 Your Credit Assessment Explanation

**Assessment Result:** {risk_category} 
**Confidence Level:** {confidence:.1%}

### 🟢 What Helped Your Score:
"""
            
            for i, (feature, impact, value) in enumerate(top_positive[:3], 1):
                explanation_text += f"{i}. **{self._humanize_feature_name(feature)}**: {self._explain_feature_impact(feature, impact, value, positive=True)}\n"
            
            if top_negative:
                explanation_text += "\n### 🔴 What Lowered Your Score:\n"
                for i, (feature, impact, value) in enumerate(top_negative[:3], 1):
                    explanation_text += f"{i}. **{self._humanize_feature_name(feature)}**: {self._explain_feature_impact(feature, impact, value, positive=False)}\n"
            
            explanation_text += "\n### 💡 How to Improve Your Score:\n"
            explanation_text += self._generate_improvement_suggestions(top_negative, applicant_data)
            
            return explanation_text
            
        except Exception as e:
            return f"Error generating explanation: {e}"
    
    def _humanize_feature_name(self, feature_name: str) -> str:
        """Convert technical feature names to user-friendly names"""
        name_mapping = {
            'monthly_income': 'Monthly Income',
            'employment_type': 'Employment Status', 
            'existing_loans': 'Existing Loans',
            'account_age': 'Account History',
            'behavioral_score': 'Payment Behavior',
            'social_score': 'Community Trust',
            'digital_score': 'Digital Presence',
            'overall_trust_score': 'Overall Trust Level'
        }
        return name_mapping.get(feature_name, feature_name.replace('_', ' ').title())
    
    def _explain_feature_impact(self, feature: str, impact: float, value: float, positive: bool) -> str:
        """Generate specific explanation for feature impact"""
        if feature == 'monthly_income':
            return f"Your income of ₹{value:,.0f} {'strengthens' if positive else 'weakens'} your credit profile"
        elif feature == 'account_age':
            return f"Your {value:.0f}-month account history {'shows stability' if positive else 'is relatively short'}"
        elif feature == 'existing_loans':
            return f"Having {value:.0f} existing loans {'shows manageable debt' if positive else 'indicates high debt burden'}"
        elif 'score' in feature:
            return f"Your {value:.1%} score in this area {'demonstrates strong performance' if positive else 'has room for improvement'}"
        else:
            return f"This factor {'positively contributes' if positive else 'negatively impacts'} your assessment"
    
    def _generate_improvement_suggestions(self, negative_factors: List, applicant_data: Dict) -> str:
        """Generate personalized improvement suggestions"""
        suggestions = []
        
        for feature, impact, value in negative_factors[:3]:
            if feature == 'monthly_income':
                suggestions.append("• Consider documenting additional income sources or part-time work")
            elif feature == 'account_age':
                suggestions.append("• Continue building your financial history - time helps!")
            elif feature == 'existing_loans':
                suggestions.append("• Focus on paying down existing debt to improve your debt-to-income ratio")
            elif 'behavioral' in feature:
                suggestions.append("• Maintain consistent payment patterns and avoid late payments")
            elif 'social' in feature:
                suggestions.append("• Engage more with community financial programs and peer networks")
            elif 'digital' in feature:
                suggestions.append("• Increase your digital financial activity and maintain regular transactions")
        
        if not suggestions:
            suggestions.append("• Continue your current positive financial behaviors!")
            suggestions.append("• Consider applying for a small loan to build payment history")
        
        return "\n".join(suggestions)


def render_shap_explainability_dashboard(applicant_data: Dict):
    """Main function to render the SHAP explainability dashboard"""
    st.markdown("## 🔍 **AI Decision Explanation Dashboard**")
    st.markdown("Understanding how AI reached your credit assessment")
    st.markdown("---")
    
    # Initialize explainer
    explainer = SHAPExplainer()
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Visual Explanation", "📈 Feature Analysis", "💬 Plain Language"])
    
    with tab1:
        st.subheader("🎯 Why Did You Get This Score?")
        
        with st.spinner("Generating AI explanation..."):
            explanation = explainer.get_explanation(applicant_data)
        
        if explanation:
            # Show waterfall chart
            waterfall_fig = explainer.create_waterfall_chart(explanation)
            if waterfall_fig:
                st.plotly_chart(waterfall_fig, use_container_width=True)
                
                st.info("""
                **How to read this chart:**
                - Green bars show factors that **improved** your score
                - Red bars show factors that **lowered** your score  
                - The height shows how much each factor contributed
                - The final bar shows your overall predicted score
                """)
            else:
                st.error("Unable to generate explanation chart")
        else:
            st.error("Unable to generate AI explanation")
    
    with tab2:
        st.subheader("📈 Feature Impact Analysis")
        
        if explanation:
            # Show feature importance chart
            importance_fig = explainer.create_feature_importance_chart(explanation)
            if importance_fig:
                st.plotly_chart(importance_fig, use_container_width=True)
                
                # Show prediction details
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    prediction_data = explanation.get('prediction_data', {})
                    risk_category = prediction_data.get('risk_category', 'Unknown')
                    st.metric("Risk Category", risk_category)
                
                with col2:
                    confidence = prediction_data.get('prediction_confidence', 0)
                    st.metric("AI Confidence", f"{confidence:.1%}")
                
                with col3:
                    risk_prob = prediction_data.get('risk_probability', 0)
                    st.metric("Risk Probability", f"{risk_prob:.1%}")
    
    with tab3:
        st.subheader("💬 Personalized Explanation")
        
        if explanation:
            # Generate and display plain language explanation
            plain_explanation = explainer.generate_plain_language_explanation(explanation, applicant_data)
            st.markdown(plain_explanation)
            
            # Add interactive Q&A
            st.markdown("---")
            st.subheader("❓ Common Questions")
            
            with st.expander("Why is AI transparency important?"):
                st.write("""
                AI transparency helps you understand and trust the credit assessment process. 
                By knowing which factors influence your score, you can make informed decisions 
                about improving your financial profile.
                """)
            
            with st.expander("How accurate are these explanations?"):
                st.write("""
                These explanations are generated using SHAP (SHapley Additive exPlanations), 
                a state-of-the-art method for explaining AI decisions. The values show the 
                actual mathematical contribution of each factor to your final score.
                """)
            
            with st.expander("Can I improve my score?"):
                st.write("""
                Yes! The improvement suggestions above are personalized based on your current 
                profile. Focus on the areas where you can make the biggest positive impact.
                """)
        else:
            st.error("Unable to generate explanation")
    
    # Add model performance info
    st.markdown("---")
    st.markdown("### 🔧 Model Information")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Algorithm**: XGBoost + Logistic Regression Ensemble")
    with col2:
        st.info("**Explanation Method**: SHAP (SHapley Additive exPlanations)")


# Global function for easy import
def show_ai_explanations(applicant_data: Dict):
    """Easy-to-use function for showing AI explanations"""
    render_shap_explainability_dashboard(applicant_data)
