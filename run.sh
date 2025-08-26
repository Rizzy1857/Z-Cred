#!/bin/bash

# Z-Score Application Launcher
# PSB FinTech Cybersecurity Hackathon 2025

echo "🚀 Starting Z-Score Credit Assessment Application..."
echo "📊 PSB FinTech Cybersecurity Hackathon 2025"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Check if database exists, if not initialize it
if [ ! -f "data/applicants.db" ]; then
    echo "🗄️ Initializing database..."
    python -c "from local_db import initialize_database; initialize_database()"
fi

# Start Streamlit application
echo "🌐 Starting Streamlit application..."
echo "📱 Open your browser to: http://localhost:8501"
echo "🔐 Default login: admin / admin123"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run app.py
