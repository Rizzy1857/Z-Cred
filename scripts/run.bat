@echo off
echo Starting Z-Score Credit Assessment Application...
echo PSB FinTech Cybersecurity Hackathon 2025
echo.

REM activate virtual env
call .venv\bin\activate

REM check requirements
echo Installing requirements...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Failed to install required packages.
    echo Try checking requirements.txt
    pause
    exit \b %errorlevel%
)

if not exist data\applicants.db (
    echo "Initializing database..."
    python -c "from local_db import initialize_database; initialize_database()"
)

REM start streamlit app
echo "🌐 Starting Streamlit application..."
echo "📱 Open your browser to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run app.py