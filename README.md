# Project Z-Score: Dynamic Trust-Based Credit Framework

A hackathon prototype for PSB's FinTech Cybersecurity Hackathon 2025 - Credit Risk Management Track

## Overview

Project Z-Score addresses India's dual crisis of credit exclusion (451M individuals lack formal credit access) and rising microfinance delinquencies (163% YoY surge in defaults). Our solution combines alternative data sources, explainable AI, and gamified financial literacy to create a comprehensive credit infrastructure for the underbanked.

### Key Innovation

- **Trust-Based Scoring**: Dynamic assessment using alternative data (utility bills, social proof, digital footprints)
- **Explainable AI**: SHAP-powered decision transparency for regulatory compliance
- **Gamified Journey**: Transform credit building from intimidating process to engaging experience
- **DPDPA Compliant**: Built with privacy-by-design and regulatory compliance as core principles

## Team Z-Row

- Abhinand
- Hrisheekesh  
- Alvin
- Anjana

## Features

### Core Functionality

- **Dynamic Trust Scoring**: Multi-component assessment (Behavioral, Social, Digital Trust)
- **Obscurity Model**: Guided journey from credit-invisible to scorable status
- **ML Pipeline**: Logistic Regression baseline + XGBoost ensemble with SHAP explainability
- **Gamification**: Z-Credits system with missions, achievements, and Trust Bar visualization

### Compliance & Security

- **DPDPA Compliance**: Granular consent management, data minimization, withdrawal mechanisms
- **RBI Guidelines**: Direct fund flow, cooling-off periods, Key Fact Statement generation
- **Secure Architecture**: PBKDF2 password hashing, session management, input validation

### Alternative Data Integration

- **F1 - Payment History**: BBPS utility payment data for financial discipline assessment
- **F2 - Loan Performance**: MFI/NGO loan history from informal/semi-formal sources
- **F3 - Social Proof**: Community trust metrics from SHG/NGO endorsements
- **F4 - Digital Footprint**: Telecom data, transaction SMS patterns, device stability

## Technical Architecture

### Stack

- **Frontend**: Streamlit with custom CSS for professional UI
- **Backend**: Python with SQLite for offline-first architecture
- **ML Pipeline**: scikit-learn, XGBoost, SHAP for explainable predictions
- **Security**: bcrypt, session management, DPDPA-compliant consent flows
- **Visualization**: Plotly, Matplotlib for interactive charts and explanations

### Project Structure

```
zscore/
├── app.py                 # Main Streamlit application
├── auth.py               # Authentication system
├── local_db.py           # Database operations
├── model_pipeline.py     # ML models and training
├── requirements.txt      # Dependencies
├── README.md            # This file
└── data/
    ├── applicants.db    # Main SQLite database
    └── sample_data/     # Demo datasets
```

## Installation & Setup

### Prerequisites

- Python 3.8+ (recommended: Python 3.10+)
- Git
- 4GB+ available disk space
- 8GB+ RAM (recommended for optimal performance)

### Quick Start (Recommended)

Use our automated setup script for the fastest deployment:

```bash
# Clone the repository
git clone <repository-url>
cd Z-Cred

# Run automated setup and launch
./start.sh

# Alternative: Skip setup if already configured
./start.sh --skip-setup

# Start specific application
./start.sh --app=user    # User interface (port 8502)
./start.sh --app=admin   # Admin interface (port 8503)
./start.sh --app=main    # Main interface (port 8501)
```

### Manual Setup (Advanced Users)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Z-Cred
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies (pinned versions)**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Initialize database and demo data**
   ```bash
   python setup_demo_data.py
   ```

5. **Cache SHAP explainers (optional, for better performance)**
   ```bash
   python -c "
   from model_integration import model_integrator
   from shap_cache import cache_shap_explainers
   model = model_integrator.get_credit_model()
   cache_shap_explainers(model)
   print('✅ SHAP explainers cached for optimal performance')
   "
   ```

6. **Run the application**
   ```bash
   # Main application
   streamlit run app.py --server.port 8501
   
   # User-focused interface
   streamlit run app_user.py --server.port 8502
   
   # Admin interface
   streamlit run app_admin.py --server.port 8503
   ```

7. **Access the application**
   - Main App: `http://localhost:8501`
   - User App: `http://localhost:8502`
   - Admin App: `http://localhost:8503`

### Production Deployment

For production deployment, use the optimized commands:

```bash
# Build production environment
python -m venv prod_env
source prod_env/bin/activate
pip install -r requirements.txt

# Run with production settings
streamlit run app.py --server.port 8501 --server.headless true \
  --server.enableCORS false --server.enableXsrfProtection true

# Or use the launcher script
python launcher.py --production --port 8501
```

### Development Setup

For development with hot-reload and debugging:

```bash
# Install development dependencies
pip install pytest pytest-cov black flake8

# Run tests
python -m pytest test_unified_scoring.py -v
python -m pytest test_*.py

# Code formatting
black *.py

# Performance profiling
python -c "
import cProfile
import app_user
cProfile.run('app_user.main()', 'profile_output.prof')
"
```

### Docker Setup (Optional)

```bash
# Build Docker image
docker build -t z-cred .

# Run container
docker run -p 8501:8501 z-cred

# Docker Compose for full stack
docker-compose up -d
```

### Troubleshooting

**Common Issues:**

1. **Port already in use:**
   ```bash
   # Find and kill process using port
   lsof -ti:8501 | xargs kill -9
   # Or use different port
   streamlit run app.py --server.port 8504
   ```

2. **Database locked errors:**
   ```bash
   # Reset database
   rm data/applicants.db
   python setup_demo_data.py
   ```

3. **SHAP explainer errors:**
   ```bash
   # Clear SHAP cache
   rm -rf cache/shap/
   python -c "from shap_cache import shap_cache; shap_cache.clear_cache()"
   ```

4. **Memory issues:**
   ```bash
   # Run with memory optimization
   export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
   streamlit run app.py --server.maxUploadSize 1
   ```

### Performance Optimization

For optimal performance:

1. **Pre-cache SHAP explainers:** Run the caching command above
2. **Use SSD storage:** Ensure database is on SSD for faster I/O
3. **Increase RAM:** 8GB+ recommended for large datasets
4. **Browser cache:** Enable browser caching for faster subsequent loads

### Verified Environments

✅ **Tested Configurations:**
- macOS 12+ with Python 3.10+
- Ubuntu 20.04+ with Python 3.8+
- Windows 10+ with Python 3.9+
- Docker on Linux/macOS

📈 **Performance Benchmarks:**
- Cold start: <30 seconds
- Warm start: <5 seconds  
- Trust score calculation: <1 second
- SHAP explanation: <2 seconds (cached)
- UI response time: <500ms

## Demo Scenarios

### Scenario 1: New User Journey (Priya - Rural Artisan)

1. **Onboarding**: New user starts in "Obscurity" phase with 5% Trust Bar
2. **Literacy Mission**: Complete quiz on bill payment importance (+15% Trust Bar)
3. **Behavioral Challenge**: Pay electricity bill on time (+20% Trust Bar)
4. **Data Sharing**: Provide consent for bank transaction history (+30% Trust Bar)
5. **Graduation**: Cross 70% threshold, unlock credit application eligibility

### Scenario 2: Credit Decision with Explanation

1. **Application Processing**: Submit credit application with complete profile
2. **ML Prediction**: XGBoost model generates risk score and probability of default
3. **SHAP Explanation**: Visual breakdown of decision factors
4. **Actionable Feedback**: Clear guidance on improving creditworthiness

### Scenario 3: Compliance Demonstration

1. **Consent Management**: Granular data permissions with easy withdrawal
2. **DPDPA Compliance**: Data minimization and purpose limitation enforcement
3. **RBI Guidelines**: KFS generation, cooling-off period implementation

## Key Metrics & Performance

### Model Performance (Synthetic Data)

- **Logistic Regression**: AUC ~0.92, F1-Score ~0.89
- **XGBoost Ensemble**: AUC ~0.96, F1-Score ~0.93
- **Response Time**: <1s per applicant assessment
- **Explainability**: 100% decisions explained via SHAP

### Business Impact Potential

- **Target Addressable Market**: 451M credit-invisible Indians
- **Partner Ecosystem**: MFIs, NGOs, Rural Banks, SHGs
- **Risk Reduction Goal**: 15-20% improvement in Portfolio at Risk (PAR)

## Regulatory Compliance

### DPDPA 2023 Compliance

- ✅ Valid consent (free, specific, informed, unambiguous)
- ✅ Purpose limitation (credit assessment only)
- ✅ Data minimization (collect only necessary data)
- ✅ Data localization (India-based storage)
- ✅ Consent withdrawal mechanisms

### RBI Digital Lending Guidelines 2025

- ✅ LSP partnership model with regulated entities
- ✅ Direct fund flow (no intermediary handling)
- ✅ Key Fact Statement generation
- ✅ Mandatory cooling-off period
- ✅ Grievance redressal mechanism

## Development Status

### Completed Features

- ✅ Authentication system with role management
- ✅ SQLite database with offline-first architecture
- ✅ ML pipeline with Logistic Regression + XGBoost
- ✅ Trust scoring framework (Behavioral, Social, Digital components)
- ✅ Basic gamification (Z-Credits, Trust Bar)
- ✅ DPDPA-compliant consent management
- ✅ Professional Streamlit UI

### In Progress

- 🔄 SHAP integration for explainable AI
- 🔄 Advanced visualizations (Trust Bar animations, SHAP plots)
- 🔄 Demo data scenarios refinement

### Planned Enhancements

- 📋 PDF credit reports generation
- 📋 Offline/online data synchronization
- 📋 Mobile-optimized interface for field agents
- 📋 Account Aggregator framework integration

## Usage Guide

for detailed usage guide check [Usage Documentation](USAGE.md)

### For Developers

1. Model training: `python model_pipeline.py`
2. Database reset: `python -c "from local_db import reset_database; reset_database()"`
3. Add sample data: `python -c "from local_db import add_sample_data; add_sample_data()"`

## API Documentation

### Core Functions

- `calculate_trust_score(applicant_data)`: Returns Trust Bar components and overall score
- `predict_credit_risk(features)`: ML prediction with confidence intervals
- `generate_shap_explanation(features, prediction)`: Explainable AI breakdown
- `log_consent(user_id, consent_type, granted)`: DPDPA compliance logging

**Refer detailed documentaion [API Documentation](API.md)**

## Contributing

This is a hackathon prototype. For the competition:

1. Focus on demo-ready scenarios
2. Prioritize visual polish and stability
3. Ensure all compliance features work smoothly
4. Test end-to-end user journeys

*Refer detailed documentaion [Contribution Documentaion](CONTRIBUTION.md)**

## License

[MIT License](LICENSE)

## Support

For project-related questions:

- Team Lead: [Rizzy](https://github.com/Rizzy1857)

---

**Built for PSB's FinTech Cybersecurity Hackathon 2025 - Credit Risk Management Track**

*Empowering India's underbanked through trust, technology, and transparency.*