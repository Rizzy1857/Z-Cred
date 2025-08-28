# Z-Score Logic and Calculations

## Core Mathematical Framework

### Trust Score Calculation

The Z-Score framework uses a weighted composite scoring system across three dimensions:

```
Trust_Score = w₁ × Behavioral_Trust + w₂ × Social_Trust + w₃ × Digital_Trust

Where:
- w₁ = 0.5 (Behavioral weight - highest priority)
- w₂ = 0.3 (Social weight - community validation)  
- w₃ = 0.2 (Digital weight - stability indicators)
- All components normalized to 0-100 scale
```

### Component Calculations

#### 1. Behavioral Trust (50% weight)
**Primary Data Source**: F1 (Payment History) + F2 (Loan Performance)

```python
def calculate_behavioral_trust(payment_data, loan_data):
    # Payment consistency score (0-50)
    payment_score = (
        on_time_payments / total_payments * 30 +
        payment_frequency_regularity * 20
    )
    
    # Loan performance score (0-50)
    if loan_data.exists():
        loan_score = (
            successful_repayments / total_loans * 30 +
            (1 - default_rate) * 20
        )
    else:
        loan_score = 25  # Neutral for new-to-credit
    
    return min(100, payment_score + loan_score)
```

**Key Assumptions**:
- On-time utility payments predict loan repayment behavior
- Payment regularity indicates financial discipline
- Past loan performance is strongest predictor of future performance

**Critical Limitation**: This assumes correlation between utility payments and loan repayment, which may vary significantly across economic conditions and individual circumstances.

#### 2. Social Trust (30% weight)
**Primary Data Source**: F3 (Social Proof from SHG/NGO endorsements)

```python
def calculate_social_trust(endorsements, community_data):
    # Endorsement strength (0-40)
    endorsement_score = min(40, len(endorsements) * 8)
    
    # Community standing (0-30)
    standing_score = (
        years_in_community / 5 * 15 +
        leadership_roles * 10 +
        group_participation_rate * 5
    )
    
    # Penalty for joint liability defaults (0-30)
    jlg_penalty = group_default_history * -10
    
    return max(0, min(100, endorsement_score + standing_score + jlg_penalty))
```

**Key Assumptions**:
- Community endorsements correlate with individual creditworthiness
- Social capital translates to financial reliability
- Group dynamics provide meaningful risk signals

**Critical Limitation**: Social proof can be manipulated, and community standing may not reflect individual financial capacity or intent.

#### 3. Digital Trust (20% weight)
**Primary Data Source**: F4 (Digital Footprint - telecom, SMS, device data)

```python
def calculate_digital_trust(telecom_data, sms_data, device_data):
    # Stability indicators (0-40)
    stability_score = (
        min(device_tenure_months / 24, 1) * 15 +
        location_consistency_score * 15 +
        sim_tenure_years / 3 * 10
    )
    
    # Financial behavior signals (0-40)
    behavior_score = (
        regular_recharge_pattern * 20 +
        transaction_sms_frequency / 30 * 20
    )
    
    # Digital sophistication (0-20)
    sophistication_score = (
        app_usage_diversity * 10 +
        digital_payment_adoption * 10
    )
    
    return min(100, stability_score + behavior_score + sophistication_score)
```

**Key Assumptions**:
- Device stability indicates personal stability
- Regular recharge patterns show financial planning ability
- Digital transaction frequency correlates with financial activity

**Critical Limitation**: Digital behavior may reflect economic necessity rather than creditworthiness. Urban/rural digital divides could create systemic bias.

### Obscurity Index Calculation

Measures data sufficiency for reliable scoring:

```python
def calculate_obscurity_index(applicant_data):
    data_points = {
        'payment_history': min(len(payment_records) / 12, 1.0),  # 12 months ideal
        'loan_history': 1.0 if loan_records else 0.3,  # Heavily weighted
        'social_proof': min(len(endorsements) / 3, 1.0),  # 3 endorsements ideal
        'digital_footprint': min(digital_data_points / 10, 1.0)  # 10 signals ideal
    }
    
    # Weighted average with minimum thresholds
    obscurity = 100 * (1 - sum(
        weight * min(score, threshold) 
        for (score, weight, threshold) in data_points.items()
    ))
    
    return max(0, min(100, obscurity))
```

**Graduation Threshold**: Obscurity < 30% (equivalent to Trust Bar > 70%)

### ML Model Integration

#### Logistic Regression (Baseline)
```python
# Feature engineering for interpretability
features = [
    'payment_consistency_ratio',
    'loan_default_history',
    'community_endorsement_count',
    'device_stability_months',
    'transaction_frequency_score'
]

# Model: P(Default) = 1 / (1 + e^-(β₀ + β₁x₁ + ... + βₙxₙ))
log_odds_default = (
    intercept +
    β₁ * payment_consistency_ratio +
    β₂ * loan_default_indicator +
    β₃ * community_endorsement_count +
    β₄ * device_stability_months +
    β₅ * transaction_frequency_score
)

probability_default = 1 / (1 + exp(-log_odds_default))
```

#### XGBoost Enhancement
```python
# Handles non-linear relationships and feature interactions
xgb_features = features + [
    'payment_amount_variance',
    'seasonal_payment_patterns',
    'social_network_risk_score',
    'digital_behavior_anomalies',
    'macro_economic_indicators'
]

# Model automatically discovers feature interactions:
# - Payment consistency × Loan amount requested
# - Community endorsements × Regional default rates
# - Digital stability × Economic stress indicators
```

### Risk Categorization Logic

```python
def categorize_risk(probability_default, trust_score, obscurity_index):
    # Multi-dimensional risk assessment
    if obscurity_index > 30:
        return "INSUFFICIENT_DATA"
    
    if probability_default < 0.05 and trust_score > 80:
        return "LOW_RISK"
    elif probability_default < 0.15 and trust_score > 60:
        return "MEDIUM_RISK"
    elif probability_default < 0.30:
        return "HIGH_RISK"
    else:
        return "VERY_HIGH_RISK"
```

### Gamification Mechanics

#### Z-Credits Earning System
```python
z_credit_actions = {
    'complete_literacy_module': 100,
    'pay_bill_on_time': 50,
    'link_bank_account': 200,
    'get_community_endorsement': 150,
    'maintain_payment_streak': lambda streak: min(streak * 10, 500)
}

def update_trust_bar(current_trust, z_credits_earned):
    # Diminishing returns to prevent gaming
    trust_increase = z_credits_earned * 0.1 * (1 - current_trust/100)
    return min(100, current_trust + trust_increase)
```

#### Mission Progression
```python
missions = {
    'beginner': {
        'pay_3_bills_on_time': {'z_credits': 200, 'trust_boost': 5},
        'complete_basic_literacy': {'z_credits': 150, 'trust_boost': 3}
    },
    'intermediate': {
        'maintain_6_month_streak': {'z_credits': 500, 'trust_boost': 10},
        'reduce_loan_utilization': {'z_credits': 300, 'trust_boost': 7}
    },
    'advanced': {
        'mentor_new_user': {'z_credits': 400, 'trust_boost': 8},
        'diversify_income_sources': {'z_credits': 600, 'trust_boost': 12}
    }
}
```

## SHAP Explainability Integration

### Local Explanations
```python
def generate_shap_explanation(model, features, prediction):
    # Calculate SHAP values for individual prediction
    shap_values = shap_explainer(features)
    
    explanation = {
        'base_value': model.expected_value,
        'prediction': prediction,
        'feature_contributions': dict(zip(feature_names, shap_values))
    }
    
    # Rank features by absolute contribution
    ranked_features = sorted(
        explanation['feature_contributions'].items(),
        key=lambda x: abs(x[1]),
        reverse=True
    )
    
    return explanation, ranked_features
```

### Global Feature Importance
```python
def calculate_global_importance(shap_values_matrix):
    # Mean absolute SHAP values across all predictions
    feature_importance = np.mean(np.abs(shap_values_matrix), axis=0)
    
    # Normalize to percentages
    importance_percentages = 100 * feature_importance / np.sum(feature_importance)
    
    return dict(zip(feature_names, importance_percentages))
```

## Data Quality and Bias Mitigation

### Fairness Constraints
```python
def check_demographic_parity(predictions, protected_attributes):
    """Ensure similar approval rates across demographic groups"""
    groups = np.unique(protected_attributes)
    approval_rates = {}
    
    for group in groups:
        group_mask = protected_attributes == group
        group_approvals = np.mean(predictions[group_mask] < default_threshold)
        approval_rates[group] = group_approvals
    
    # Flag if approval rate difference > 10%
    max_disparity = max(approval_rates.values()) - min(approval_rates.values())
    return max_disparity < 0.1, approval_rates
```

### Data Validation Pipeline
```python
def validate_input_data(applicant_data):
    validation_rules = {
        'payment_history': lambda x: 0 <= len(x) <= 36,  # Max 3 years
        'loan_amounts': lambda x: all(amt > 0 for amt in x),
        'endorsements': lambda x: len(x) <= 10,  # Prevent spam
        'device_tenure': lambda x: 0 <= x <= 120,  # Max 10 years reasonable
    }
    
    errors = []
    for field, rule in validation_rules.items():
        if field in applicant_data and not rule(applicant_data[field]):
            errors.append(f"Invalid {field}: {applicant_data[field]}")
    
    return len(errors) == 0, errors
```

## Performance Monitoring

### Model Drift Detection
```python
def detect_model_drift(current_data, training_data, threshold=0.05):
    """Monitor for changes in data distribution"""
    from scipy import stats
    
    drift_scores = {}
    for feature in feature_names:
        # Kolmogorov-Smirnov test for distribution shift
        ks_stat, p_value = stats.ks_2samp(
            training_data[feature], 
            current_data[feature]
        )
        drift_scores[feature] = {'ks_stat': ks_stat, 'p_value': p_value}
    
    # Alert if significant drift detected
    drifted_features = [
        f for f, score in drift_scores.items() 
        if score['p_value'] < threshold
    ]
    
    return len(drifted_features) == 0, drifted_features
```

### Real-time Performance Metrics
```python
def calculate_portfolio_metrics(predictions, actuals, time_window_days=30):
    """Monitor model performance over time"""
    recent_mask = (datetime.now() - actuals.index).days <= time_window_days
    recent_predictions = predictions[recent_mask]
    recent_actuals = actuals[recent_mask]
    
    metrics = {
        'auc_score': roc_auc_score(recent_actuals, recent_predictions),
        'precision': precision_score(recent_actuals, recent_predictions > 0.5),
        'recall': recall_score(recent_actuals, recent_predictions > 0.5),
        'default_rate': np.mean(recent_actuals),
        'avg_score': np.mean(recent_predictions)
    }
    
    return metrics
```

## Critical Assumptions and Limitations

### Mathematical Assumptions
1. **Linear Additivity**: Trust components combine linearly, which may not reflect complex interactions
2. **Static Weights**: Fixed weights (50%-30%-20%) may not be optimal across all populations
3. **Normal Distribution**: Many calculations assume normally distributed features
4. **Independence**: Assumes feature independence, which rarely holds in practice

### Data Quality Assumptions
1. **Payment History**: Assumes utility payments reflect credit behavior (correlation ≠ causation)
2. **Social Proof**: Assumes community endorsements are honest and meaningful
3. **Digital Footprint**: Assumes digital behavior correlates with creditworthiness
4. **Temporal Stability**: Assumes past behavior predicts future performance

### Operational Limitations
1. **Data Freshness**: Real-time updates require continuous data feeds
2. **Gaming Prevention**: Gamification system vulnerable to manipulation
3. **Scalability**: Complex calculations may not scale to millions of users
4. **Bias Propagation**: Historical data may perpetuate existing inequalities

### Regulatory Constraints
1. **Consent Management**: Requires granular tracking of data permissions
2. **Right to Explanation**: All decisions must be explainable in simple terms
3. **Data Minimization**: Cannot collect data beyond stated purpose
4. **Accuracy Requirements**: Must maintain high precision to avoid wrongful denials

This logic framework provides the mathematical foundation for Z-Score while acknowledging the inherent limitations and assumptions that judges should evaluate critically.