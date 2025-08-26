# Integration Guide: Enhanced Error Handling for Z-Score App

## Quick Integration Steps for app.py

To integrate the enhanced error handling and model improvements into your Streamlit app, follow these steps:

### 1. Import Enhanced Modules

Add these imports to the top of `app.py`:

```python
# Enhanced error handling and model pipeline
from error_handling import (
    error_handler, ModelError, DatabaseError, AuthenticationError,
    ValidationError, safe_json_parse, safe_numeric_conversion,
    is_valid_email, is_valid_phone, is_valid_age, is_valid_income
)
```

### 2. Enhance Prediction Functions

Replace existing prediction calls with error-handled versions:

```python
# OLD CODE:
try:
    prediction = model.predict(applicant_data)
    explanation = model.explain_prediction(applicant_data)
except Exception as e:
    st.error(f"Prediction failed: {e}")

# NEW CODE:
try:
    prediction = model.predict(applicant_data)
    
    # Display enhanced prediction with confidence
    st.metric("Risk Category", prediction['risk_category'])
    st.metric("Confidence Score", f"{prediction['confidence_score']:.1%}")
    st.metric("Prediction Confidence", f"{prediction['prediction_confidence']:.1%}")
    
    # Show confidence intervals
    ci = prediction['confidence_intervals']
    st.write(f"Model Confidence Range: {ci['lower']:.1%} - {ci['upper']:.1%}")
    
    explanation = model.explain_prediction(applicant_data)
    if 'error' not in explanation:
        # Display enhanced SHAP explanation
        st.write("### Top Contributing Factors")
        for contrib in explanation.get('top_contributors', {}).get('positive', [])[:3]:
            st.write(f"✅ {contrib['feature']}: +{contrib['impact']:.3f}")
        for contrib in explanation.get('top_contributors', {}).get('negative', [])[:3]:
            st.write(f"❌ {contrib['feature']}: -{contrib['impact']:.3f}")
    
except (ModelError, FeatureExtractionError) as e:
    error_response = error_handler.handle_error(e)
    st.error(error_response['user_message'])
    st.info("Please check your input data and try again.")
except Exception as e:
    error_response = error_handler.handle_error(e)
    st.error(error_response['user_message'])
```

### 3. Enhance Form Validation

Replace input validation with safe conversion functions:

```python
# OLD CODE:
age = st.number_input("Age", min_value=18, max_value=100, value=30)
income = st.number_input("Monthly Income", min_value=0, value=15000)

# NEW CODE:
age_input = st.text_input("Age", value="30")
income_input = st.text_input("Monthly Income (₹)", value="15000")

# Safe conversion with validation
age = safe_numeric_conversion(age_input, default=30, min_val=18, max_val=100)
income = safe_numeric_conversion(income_input, default=15000, min_val=0, max_val=10000000)

# Validation feedback
if not is_valid_age(age):
    st.warning("Please enter a valid age between 18 and 100")
if not is_valid_income(income):
    st.warning("Please enter a valid monthly income")
```

### 4. Enhanced Database Error Handling

Wrap database operations with proper error handling:

```python
# OLD CODE:
try:
    result = self.db.create_applicant(applicant_data)
except Exception as e:
    st.error(f"Database error: {e}")

# NEW CODE:
try:
    result = self.db.create_applicant(applicant_data)
    if result:
        st.success("Applicant created successfully!")
    else:
        st.error("Failed to create applicant record")
except DatabaseError as e:
    error_response = error_handler.handle_error(e)
    st.error(error_response['user_message'])
    if st.button("Retry"):
        st.experimental_rerun()
```

### 5. Enhanced Trust Score Display

Update trust score visualization to use the enhanced calculation:

```python
# Calculate trust score with error handling
try:
    trust_result = calculate_trust_score(applicant_data)
    
    # Create enhanced trust bar visualization
    trust_score = trust_result['overall_trust_score']
    trust_percentage = trust_result['trust_percentage']
    
    # Animated progress bar (ready for animation enhancement)
    st.write("### Trust Score Breakdown")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Behavioral", f"{trust_result['behavioral_score']:.1%}")
    with col2:
        st.metric("Social", f"{trust_result['social_score']:.1%}")
    with col3:
        st.metric("Digital", f"{trust_result['digital_score']:.1%}")
    
    # Overall trust bar
    st.write(f"**Overall Trust Score: {trust_percentage:.1f}%**")
    st.progress(trust_score)
    
except (FeatureExtractionError, ValidationError) as e:
    error_response = error_handler.handle_error(e)
    st.warning(error_response['user_message'])
    # Show default trust visualization
    st.progress(0.2)
    st.write("Trust score calculation using default values")
```

### 6. Add System Health Monitoring

Add a simple health check section for admin users:

```python
def show_system_health(self):
    """Display system health and error statistics"""
    st.write("### System Health Monitor")
    
    # Check if error log exists
    try:
        import os
        if os.path.exists('logs/zscore_errors.log'):
            with open('logs/zscore_errors.log', 'r') as f:
                recent_errors = f.readlines()[-10:]  # Last 10 errors
            
            if recent_errors:
                st.warning(f"Recent errors detected: {len(recent_errors)}")
                with st.expander("View Recent Errors"):
                    for error in recent_errors:
                        st.code(error.strip())
            else:
                st.success("No recent errors detected")
        else:
            st.info("Error logging initialized")
    except Exception as e:
        st.error(f"Unable to check system health: {e}")
```

## Benefits of Integration

1. **🛡️ Robust Error Handling**: Graceful recovery from all error conditions
2. **📊 Enhanced Predictions**: Confidence intervals and uncertainty quantification
3. **🔍 Better Explanations**: Rich SHAP explanations with fallback mechanisms
4. **✅ Input Validation**: Automatic data sanitization and validation
5. **📱 User Experience**: Clear, actionable error messages
6. **🔧 Maintainability**: Centralized error handling and logging

## Next Steps

After integrating these enhancements:

1. **Test thoroughly** with various input scenarios
2. **Implement Trust Bar animation** using confidence data
3. **Add real-time monitoring** dashboard for production
4. **Create comprehensive demo** scenarios showcasing error handling

---

**Status**: Ready for integration into main Streamlit application
**Estimated Integration Time**: 30-60 minutes
**Testing Required**: Form validation, prediction flows, error scenarios
