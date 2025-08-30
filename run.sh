#!/bin/bash
# Z-Cred Application Launcher Script

echo "🚀 Z-Cred Dynamic Trust-Based Credit Framework"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Virtual environment found"
    source .venv/bin/activate
fi

# Run health check
echo ""
echo "🏥 Running health check..."
python main.py --health

echo ""
echo "Available commands:"
echo "  ./start.sh user     - Launch User Application (port 8502)"
echo "  ./start.sh admin    - Launch Admin Application (port 8503)"
echo "  ./start.sh main     - Launch Main Launcher (port 8501)"
echo "  ./start.sh test     - Run test suite"
echo "  ./start.sh setup    - Setup demo data"
echo ""

# Check command line argument
if [ "$1" = "user" ]; then
    echo "🚀 Starting User Application..."
    python main.py --app user
elif [ "$1" = "admin" ]; then
    echo "🚀 Starting Admin Application..."
    python main.py --app admin
elif [ "$1" = "main" ]; then
    echo "🚀 Starting Main Launcher..."
    python main.py --app main
elif [ "$1" = "test" ]; then
    echo "🧪 Running tests..."
    python main.py --test
elif [ "$1" = "setup" ]; then
    echo "🔧 Setting up demo data..."
    python main.py --setup
else
    echo "⚡ Starting Main Launcher by default..."
    echo "   Access at: http://localhost:8501"
    python main.py --app main
fi
