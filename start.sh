#!/bin/bash

# Z-Cred Application Startup Script
# Handles environment setup and application launching

set -e  # Exit on any error

echo "🚀 Starting Z-Cred Application Setup..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.8+ is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_CMD="python"
    else
        print_error "Python not found. Please install Python 3.8 or higher."
        exit 1
    fi

    # Check version
    if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_status "Python $PYTHON_VERSION detected"
}

# Setup virtual environment
setup_venv() {
    if [ ! -d ".venv" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv .venv
    else
        print_status "Virtual environment already exists"
    fi

    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source .venv/Scripts/activate
        PIP_CMD=".venv/Scripts/pip"
        PYTHON_VENV=".venv/Scripts/python"
    else
        source .venv/bin/activate
        PIP_CMD=".venv/bin/pip"
        PYTHON_VENV=".venv/bin/python"
    fi

    print_status "Virtual environment activated"
}

# Install dependencies
install_deps() {
    print_status "Installing dependencies..."
    $PIP_CMD install --upgrade pip
    $PIP_CMD install -r requirements.txt
    print_status "Dependencies installed successfully"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    $PYTHON_VENV -c "
from local_db import initialize_database
from setup_demo_data import setup_demo_data
print('Setting up database...')
initialize_database()
setup_demo_data()
print('Database initialization complete!')
"
    print_status "Database initialized with demo data"
}

# Cache SHAP explainers
cache_shap() {
    print_status "Pre-computing SHAP explainers for faster UI responses..."
    $PYTHON_VENV -c "
from model_integration import model_integrator
from shap_cache import cache_shap_explainers
print('Loading and caching SHAP explainers...')
model = model_integrator.get_credit_model()
cache_shap_explainers(model)
print('SHAP explainers cached successfully!')
"
    print_status "SHAP explainers cached"
}

# Start application
start_app() {
    APP_TYPE=${1:-"main"}
    
    case $APP_TYPE in
        "main")
            PORT=8501
            APP_FILE="app.py"
            print_status "Starting main application on port $PORT..."
            ;;
        "user")
            PORT=8502
            APP_FILE="app_user.py"
            print_status "Starting user application on port $PORT..."
            ;;
        "admin")
            PORT=8503
            APP_FILE="app_admin.py"
            print_status "Starting admin application on port $PORT..."
            ;;
        *)
            print_error "Invalid app type. Use: main, user, or admin"
            exit 1
            ;;
    esac

    # Check if port is already in use
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $PORT is already in use. Trying next available port..."
        PORT=$((PORT + 1))
    fi

    print_status "🌐 Application will be available at: http://localhost:$PORT"
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        .venv/Scripts/streamlit run $APP_FILE --server.port $PORT
    else
        .venv/bin/streamlit run $APP_FILE --server.port $PORT
    fi
}

# Main execution
main() {
    echo "════════════════════════════════════════════════════════════════"
    echo "  Z-Cred: Dynamic Trust-Based Credit Framework"
    echo "  Quick Setup & Launch Script"
    echo "════════════════════════════════════════════════════════════════"
    echo ""

    # Parse command line arguments
    SKIP_SETUP=false
    APP_TYPE="main"
    
    for arg in "$@"; do
        case $arg in
            --skip-setup)
                SKIP_SETUP=true
                shift
                ;;
            --app=*)
                APP_TYPE="${arg#*=}"
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --skip-setup     Skip environment setup (use if already configured)"
                echo "  --app=TYPE       Application type: main, user, or admin (default: main)"
                echo "  --help, -h       Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0                    # Full setup + start main app"
                echo "  $0 --skip-setup      # Skip setup, start main app"
                echo "  $0 --app=user        # Full setup + start user app"
                echo "  $0 --skip-setup --app=admin  # Skip setup, start admin app"
                exit 0
                ;;
        esac
    done

    if [ "$SKIP_SETUP" = false ]; then
        check_python
        setup_venv
        install_deps
        init_database
        
        # Only cache SHAP if not skipping setup (for performance)
        print_status "Caching SHAP explainers for optimal performance..."
        cache_shap || print_warning "SHAP caching failed, continuing without cache..."
    else
        print_status "Skipping setup steps as requested"
        # Just activate the environment
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            source .venv/Scripts/activate
        else
            source .venv/bin/activate
        fi
    fi

    echo ""
    print_status "✅ Setup complete! Starting application..."
    echo ""
    
    start_app $APP_TYPE
}

# Run main function with all arguments
main "$@"
