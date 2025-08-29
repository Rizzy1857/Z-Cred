#!/usr/bin/env python3
"""
Z-Cred Application Entry Point

Main launcher for the Z-Cred Dynamic Trust-Based Credit Framework.
Provides multiple application interfaces with optimized performance.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Also add project root for direct imports
sys.path.insert(0, str(project_root))

def health_check():
    """Perform system health check"""
    print("🔍 Checking system components...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required directories
    required_dirs = ["src", "tests", "scripts", "data"]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ Directory: {dir_name}/")
        else:
            print(f"❌ Missing directory: {dir_name}/")
    
    # Check key application files
    key_files = [
        "src/apps/app.py",
        "src/apps/app_user.py", 
        "src/apps/app_admin.py",
        "requirements.txt"
    ]
    
    for file_path in key_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ File: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
    
    # Check if virtual environment is active
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment active")
    else:
        print("⚠️  Virtual environment not detected")
    
    # Check database
    db_path = project_root / "data" / "applicants.db"
    if db_path.exists():
        print(f"✅ Database: {db_path}")
    else:
        print(f"⚠️  Database not found: {db_path}")
    
    print("🏥 Health check complete!")

def main():
    """Main application launcher"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Z-Cred Dynamic Trust-Based Credit Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --app user     # Launch user interface (port 8502)
  python main.py --app admin    # Launch admin interface (port 8503)
  python main.py --app main     # Launch main interface (port 8501)
  python main.py --setup        # Run setup and initialization
  python main.py --test         # Run test suite
  python main.py --profile      # Run performance profiling
  python main.py --app user --port 9000  # Custom port
        """
    )
    
    parser.add_argument(
        "--app", 
        choices=["user", "admin", "main"],
        default="main",
        help="Application interface to launch (default: main)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to run the application on (overrides defaults)"
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run setup and database initialization"
    )
    
    parser.add_argument(
        "--test",
        action="store_true", 
        help="Run the test suite"
    )
    
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Run performance profiling"
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information"
    )
    
    parser.add_argument(
        "--health",
        action="store_true",
        help="Run system health check"
    )
    
    args = parser.parse_args()
    
    if args.version:
        print("Z-Cred Dynamic Trust-Based Credit Framework")
        print("Version: 1.0.0")
        print("Build: Hackathon Demo")
        print("Repository: https://github.com/Rizzy1857/Z-Cred")
        return
    
    if args.health:
        print("🏥 Running Z-Cred health check...")
        health_check()
        return
    
    if args.setup:
        print("🔧 Running Z-Cred setup...")
        from scripts.setup_demo_data import setup_demo_data
        setup_demo_data()
        return
    
    if args.test:
        print("🧪 Running Z-Cred test suite...")
        # Change to tests directory and run tests
        test_script = project_root / "tests" / "test_unified_scoring.py"
        import subprocess
        result = subprocess.run([
            sys.executable, str(test_script)
        ], cwd=str(project_root), capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Tests failed:\n{result.stderr}")
            sys.exit(1)
        else:
            print("✅ All tests passed!")
        return
    
    if args.profile:
        print("📊 Running Z-Cred performance profiling...")
        # Run profiling script
        profile_script = project_root / "scripts" / "performance_profiler.py"
        import subprocess
        result = subprocess.run([
            sys.executable, str(profile_script)
        ], cwd=str(project_root))
        return
    
    # Launch the selected application
    app_ports = {
        "main": args.port or 8501,
        "user": args.port or 8502, 
        "admin": args.port or 8503
    }
    
    port = app_ports[args.app]
    
    # Determine the correct app file path
    if args.app == "main":
        app_file = src_path / "apps" / "app.py"
    else:
        app_file = src_path / "apps" / f"app_{args.app}.py"
    
    # Check if the app file exists
    if not app_file.exists():
        print(f"❌ Application file not found: {app_file}")
        sys.exit(1)
    
    print(f"🚀 Launching Z-Cred {args.app} interface on port {port}")
    print(f"📱 Access at: http://localhost:{port}")
    print(f"📄 Running: {app_file}")
    
    # Use streamlit run command
    import subprocess
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(app_file), "--server.port", str(port)
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Z-Cred application stopped")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
