# Z-Score Logic and Calculations

## Core Mathematical Framework

### Trust Score Calculation

The Z-Score framework uses a **balanced composite scoring system** across three equal dimensions:

```
Trust_Score = (Behavioral_Trust + Social_Trust + Digital_Trust) / 3

Where:
- Equal weighting: 33.33% each component
- All components normalized to 0-1.0 scale
- Final score converted to percentage (0-100%)
```

### Component Calculations

#### 1. Behavioral Trust (33.33% weight)
**Primary Data Source**: F1 (Payment History) + F2 (Income Stability)

**Note**: The enhanced scoring formula below represents the improved logic design. Current implementation uses a simplified version for stability during demo phase.

```python
def calculate_behavioral_score(applicant_data):
    """
    Enhanced behavioral scoring with proper weight distribution:
    - Base Score (40%): Income-relative assessment
    - Consistency Score (30%): Payment reliability
    - Type Score (15%): Payment behavior patterns  
    - Reliability Score (15%): Employment/income stability
    """
    
    # 1. BASE SCORE (40% weight) - Income relative scoring
    monthly_income = applicant_data.get('monthly_income', 30000)
    income_relative_score = min(monthly_income / 100000, 1.0)  # Normalized to median income
    base_score = income_relative_score * 0.4
    
    # 2. CONSISTENCY SCORE (30% weight) - Payment consistency factor
    payment_history = applicant_data.get('utility_payment_history', {})
    on_time_ratio = payment_history.get('on_time_ratio', 0.5)
    consistency_factor = on_time_ratio  # Direct 0-1.0 mapping
    consistency_score = consistency_factor * 0.3
    
    # 3. TYPE SCORE (15% weight) - Payment type hierarchy
    payment_types = payment_history.get('payment_types', [])
    
    # Payment type scoring hierarchy (higher value = better creditworthiness indicator)
    type_weights = {
        'electricity_bill': 0.3,     # Basic utility - lower predictive value
        'water_bill': 0.3,           # Basic utility - lower predictive value  
        'gas_bill': 0.35,            # Utility - moderate predictive value
        'phone_bill': 0.4,           # Communication - moderate predictive value
        'internet_bill': 0.45,       # Digital engagement - moderate predictive value
        'rent_payment': 0.7,         # Housing - high predictive value
        'loan_emi': 0.9,             # Credit obligation - highest predictive value
        'credit_card': 0.85,         # Credit behavior - very high predictive value
        'insurance_premium': 0.6,    # Financial planning - good predictive value
        'school_fees': 0.5           # Education investment - moderate predictive value
    }
    
    # Calculate weighted type score based on payment mix
    if payment_types:
        type_scores = [type_weights.get(ptype.lower(), 0.2) for ptype in payment_types]
        avg_type_score = sum(type_scores) / len(type_scores)
    else:
        avg_type_score = 0.3  # Default for basic utility payments
    
    type_score = avg_type_score * 0.15
    
    # 4. RELIABILITY SCORE (15% weight) - Employment/income stability
    employment_tenure = applicant_data.get('employment_tenure_months', 12)
    reliability_factor = min(employment_tenure / 24, 1.0)  # 24 months = full reliability
    reliability_score = reliability_factor * 0.15
    
    # Combine all components (totals 100%)
    total_score = base_score + consistency_score + type_score + reliability_score
    return max(0.1, min(1.0, total_score))  # Ensure score between 0.1-1.0
```

**Key Assumptions**:

- **Base Score (40%)**: Income-relative capacity drives primary creditworthiness assessment
- **Consistency Score (30%)**: Payment reliability is the strongest behavioral predictor  
- **Type Score (15%)**: Payment type hierarchy - EMI/credit > rent > utilities in predictive value
- **Reliability Score (15%)**: Employment stability provides foundational risk assessment

**Enhanced Logic**:
- Payment type scoring recognizes that EMI/loan payments are stronger creditworthiness indicators than utility bills
- Payment type mix assessment rewards users with diverse, higher-value payment obligations
- Four-component structure provides balanced assessment across different risk dimensions
- Income-relative base scoring ensures fair assessment across different economic segments

**Critical Limitation**: Payment behavior correlation with credit risk varies across economic conditions and cultural contexts.

#### Income Stability Calculation

Income stability is a key component of behavioral trust, calculated using multiple data sources:

```python
def calculate_income_stability(applicant_data):
    """
    Calculate income stability score from 0.0 to 1.0 based on:
    - Employment consistency
    - Income variance
    - Income growth trend
    - Income source diversification
    """
    
    # 1. Employment History Stability (0-0.4)
    employment_tenure = applicant_data.get("employment_tenure_months", 0)
    job_changes = applicant_data.get("job_changes_last_2_years", 0)
    
    # Longer tenure = more stable (max 24 months for full score)
    tenure_score = min(employment_tenure / 24, 1.0) * 0.25
    
    # Fewer job changes = more stable (0 changes = full score)
    stability_score = max(0, (2 - job_changes) / 2) * 0.15
    
    employment_stability = tenure_score + stability_score
    
    # 2. Income Variance Analysis (0-0.3)
    monthly_incomes = applicant_data.get("monthly_income_history", [])
    if len(monthly_incomes) >= 3:
        income_variance = np.std(monthly_incomes) / np.mean(monthly_incomes)
        # Lower variance = more stable (inverse relationship)
        variance_score = max(0, 1 - income_variance) * 0.3
    else:
        variance_score = 0.15  # Default for insufficient data
    
    # 3. Income Growth Trend (0-0.2)
    if len(monthly_incomes) >= 6:
        # Calculate 6-month trend
        recent_avg = np.mean(monthly_incomes[-3:])
        earlier_avg = np.mean(monthly_incomes[-6:-3])
        growth_rate = (recent_avg - earlier_avg) / earlier_avg
        
        # Positive growth gets higher score
        growth_score = min(max(growth_rate, -0.2), 0.2) / 0.2 * 0.1 + 0.1
    else:
        growth_score = 0.1  # Neutral for insufficient data
    
    # 4. Income Source Diversification (0-0.1)
    income_sources = applicant_data.get("income_sources", [])
    diversification_score = min(len(income_sources) / 3, 1.0) * 0.1
    
    # Total income stability score
    total_stability = (
        employment_stability +     # 0-0.4
        variance_score +          # 0-0.3  
        growth_score +            # 0-0.2
        diversification_score     # 0-0.1
    )
    
    return min(max(total_stability, 0.0), 1.0)
```

**Income Stability Data Sources:**
- **Employment Records**: Job tenure, employer changes, employment type
- **Income History**: 6+ months of income data for variance analysis
- **Growth Patterns**: Income trends over time
- **Source Diversification**: Multiple income streams reduce risk

**Scoring Breakdown:**
- **Employment Stability (40%)**: Longer tenure + fewer job changes = higher score
- **Income Variance (30%)**: Consistent monthly income = higher score
- **Growth Trend (20%)**: Positive income growth = higher score  
- **Diversification (10%)**: Multiple income sources = higher score

#### 2. Social Trust (33.33% weight)  
**Primary Data Source**: F3 (Social Proof from community endorsements)

```python
def calculate_social_score(social_proof, community_rating):
    # Community rating (0-0.5)
    rating_score = min((community_rating / 5.0) * 0.5, 0.5)
    
    # Social endorsements (0-0.25)
    endorsements = social_proof.get("endorsements", 0)
    endorsement_score = min((endorsements / 10.0) * 0.25, 0.25)
    
    # Network strength (0-0.25)
    network_size = social_proof.get("network_size", 0)
    network_score = min((network_size / 50.0) * 0.25, 0.25)
    
    return max(0.1, min(1.0, rating_score + endorsement_score + network_score))
```

**Key Assumptions**:
- Community endorsements correlate with individual creditworthiness
- Social capital translates to financial reliability
- Network strength indicates support system

**Critical Limitation**: Social proof requires community integration and may not work for mobile populations.

#### 3. Digital Trust (33.33% weight)
**Primary Data Source**: F4 (Digital Footprint - telecom, transaction, device data)

```python
def calculate_digital_score(digital_footprint):
    # Transaction regularity (0-0.4)
    regularity = digital_footprint.get("transaction_regularity", 0.5)
    regularity_score = regularity * 0.4
    
    # Device stability (0-0.3)
    device_stability = digital_footprint.get("device_stability", 0.7)
    device_score = device_stability * 0.3
    
    # Digital engagement (0-0.3)
    engagement = digital_footprint.get("engagement_score", 0.5)
    engagement_score = engagement * 0.3
    
    return max(0.1, min(1.0, regularity_score + device_score + engagement_score))
```

**Key Assumptions**:
- Digital behavior stability indicates personal stability
- Regular digital transactions show financial planning
- Device tenure correlates with stability

**Critical Limitation**: Digital behavior may reflect economic necessity rather than creditworthiness, and urban/rural digital divides could create bias.
        digital_payment_adoption * 10
    )
    
    return min(100, stability_score + behavior_score + sophistication_score)
```

**Key Assumptions**:
- Device stability indicates personal stability
- Regular recharge patterns show financial planning ability
- Digital transaction frequency correlates with financial activity

**Critical Limitation**: Digital behavior may reflect economic necessity rather than creditworthiness, and urban/rural digital divides could create bias.

### Overall Trust Score Integration

The final trust score combines all components with equal weighting:

```python
def calculate_trust_score(applicant_data):
    # Calculate individual components (each returns 0-1.0)
    behavioral = calculate_behavioral_score(payment_history, income_stability)
    social = calculate_social_score(social_proof, community_rating)  
    digital = calculate_digital_score(digital_footprint)
    
    # Equal weighting approach
    overall = (behavioral + social + digital) / 3
    
    return {
        "behavioral_score": behavioral,      # 0-1.0
        "social_score": social,             # 0-1.0  
        "digital_score": digital,           # 0-1.0
        "overall_trust_score": overall,     # 0-1.0
        "trust_percentage": overall * 100   # 0-100%
    }
```

**Design Rationale**: Equal weighting ensures no single dimension dominates, providing balanced assessment across different user profiles and data availability scenarios.

### ML Model Integration

The Z-Cred system uses ensemble machine learning with explainable AI:

#### Feature Engineering
```python
# 14 features used in actual model:
features = [
    'age_normalized',           # Age / 100.0
    'gender_female',            # 1 if Female, 0 if Male
    'income_normalized',        # Monthly income / 100000.0
    'behavioral_score',         # 0-1.0 from behavioral calculation
    'social_score',            # 0-1.0 from social calculation  
    'digital_score',           # 0-1.0 from digital calculation
    'overall_trust_score',     # Average of above three scores
    'payment_on_time_ratio',   # From utility payment history
    'payment_avg_amount',      # Payment to income ratio (avg_payment/monthly_income)
    'community_rating',        # Community rating / 5.0
    'social_endorsements',     # Number of endorsements / 10.0
    'transaction_regularity',  # Digital transaction patterns
    'device_stability',        # Device tenure and consistency
    'z_credits_normalized'     # Gamification credits / 1000.0
]
```

#### Logistic Regression (Baseline)

```python
# Simple linear model for interpretability
log_odds_default = (
    intercept +
    β₁ * age_normalized +
    β₂ * gender_female +
    β₃ * income_normalized +
    β₄ * behavioral_score +
    β₅ * social_score +
    β₆ * digital_score +
    β₇ * overall_trust_score +
    β₈ * payment_on_time_ratio +
    β₉ * payment_avg_amount +
    β₁₀ * community_rating +
    β₁₁ * social_endorsements +
    β₁₂ * transaction_regularity +
    β₁₃ * device_stability +
    β₁₄ * z_credits_normalized
)

probability_default = 1 / (1 + exp(-log_odds_default))
```

#### XGBoost Enhancement

```python
# Handles non-linear relationships and feature interactions
xgb_model = XGBClassifier(
    random_state=42,
    eval_metric="logloss",
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1
)

# Model automatically discovers feature interactions:
# - Age × Income interactions
# - Payment behavior × Social proof correlations  
# - Digital stability × Trust score relationships
# - Complex non-linear patterns in alternative data
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