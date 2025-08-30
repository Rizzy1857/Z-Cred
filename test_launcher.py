#!/usr/bin/env python3
"""
Test script to verify the launcher functionality
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def test_app_launch(app_name, port):
    """Test launching an app and check if it starts successfully"""
    print(f"\n🧪 Testing {app_name} app launch on port {port}...")
    
    # Get the correct python executable
    project_root = Path(__file__).parent
    venv_python = project_root / ".venv" / "bin" / "python"
    python_exec = str(venv_python) if venv_python.exists() else "python"
    
    # Build the command
    script_path = project_root / "src" / "apps" / f"app_{app_name}.py"
    cmd = [
        python_exec, "-m", "streamlit", "run", 
        str(script_path), 
        "--server.port", str(port),
        "--server.headless", "true"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(project_root)
        )
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"✅ {app_name} app started successfully on port {port}")
            
            # Try to get some output
            try:
                stdout, stderr = process.communicate(timeout=2)
                if "You can now view your Streamlit app" in stdout:
                    print("✅ App server confirmed running")
                if stderr:
                    print(f"⚠️  Stderr: {stderr[:200]}...")
            except subprocess.TimeoutExpired:
                print("✅ App is running (no immediate errors)")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ {app_name} app failed to start")
            print(f"Return code: {process.returncode}")
            if stdout:
                print(f"Stdout: {stdout}")
            if stderr:
                print(f"Stderr: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception testing {app_name} app: {e}")
        return False

def main():
    print("🚀 Z-Cred App Launch Test")
    print("=" * 40)
    
    # Test user app
    user_success = test_app_launch("user", 8502)
    
    # Test admin app
    admin_success = test_app_launch("admin", 8503)
    
    print("\n📊 Test Summary:")
    print(f"User App:  {'✅ PASS' if user_success else '❌ FAIL'}")
    print(f"Admin App: {'✅ PASS' if admin_success else '❌ FAIL'}")
    
    if user_success and admin_success:
        print("\n🎉 All apps can launch successfully!")
        print("The launcher should work properly now.")
    else:
        print("\n⚠️  Some apps failed to launch. Check the errors above.")
    
    return 0 if (user_success and admin_success) else 1

if __name__ == "__main__":
    sys.exit(main())
