# Z-Cred Application Launch Guide

## 🚀 Quick Start

The Z-Cred application has been fully configured and is ready to run! Here are the different ways to launch the applications:

### Method 1: Using the Main Launcher (Recommended)

```bash
# Start the main launcher (opens in browser)
./run.sh main
# or
python main.py --app main
```

The main launcher will open at: **http://localhost:8501**

From the launcher, you can:
- Click "Launch User App" to start the user interface
- Click "Launch Admin App" to start the admin interface

### Method 2: Direct App Launch

```bash
# Launch User Application directly
./run.sh user
# or
python main.py --app user

# Launch Admin Application directly  
./run.sh admin
# or
python main.py --app admin
```

### Method 3: Manual Streamlit Commands

```bash
# User App (Credit building and assessment)
streamlit run src/apps/app_user.py --server.port 8502

# Admin App (Analytics and management)  
streamlit run src/apps/app_admin.py --server.port 8503

# Main Launcher
streamlit run src/apps/app.py --server.port 8501
```

## 🔧 Additional Commands

```bash
# Run health check
python main.py --health

# Run test suite
python main.py --test
./run.sh test

# Setup demo data
python main.py --setup
./run.sh setup

# Show version info
python main.py --version
```

## 🌐 Application URLs

When running, the applications will be available at:

- **Main Launcher**: http://localhost:8501
- **User App**: http://localhost:8502  
- **Admin App**: http://localhost:8503

## 🛠️ Troubleshooting

### If apps fail to launch from the launcher:

1. **Check if ports are free**:
   ```bash
   lsof -i :8501 -i :8502 -i :8503
   ```

2. **Kill any existing Streamlit processes**:
   ```bash
   pkill -f "streamlit run"
   ```

3. **Test individual app launches**:
   ```bash
   python test_launcher.py
   ```

### If you get import errors:

1. **Ensure virtual environment is activated**:
   ```bash
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run health check**:
   ```bash
   python main.py --health
   ```

## 🎯 Application Features

### User App (Port 8502)
- Credit score assessment
- Gamified credit building journey
- Personal financial insights
- Interactive AI explanations

### Admin App (Port 8503)  
- User management dashboard
- System analytics
- Model performance monitoring
- Administrative controls

### Main Launcher (Port 8501)
- Central application hub
- Easy navigation between apps
- System status overview

## ✅ Verification

Run this command to verify everything is working:

```bash
./run.sh test
```

This will run the complete test suite and confirm all components are functioning properly.

---

🎉 **Your Z-Cred application is now ready to use!**

Start with: `./run.sh main` or `python main.py --app main`
