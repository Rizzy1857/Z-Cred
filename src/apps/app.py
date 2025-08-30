"""
Z-Score Application Launcher
"""

import streamlit as st
import subprocess
import os
import time
import socket
import signal
import webbrowser
from typing import Optional, Tuple

# Page configuration
st.set_page_config(
    page_title="Z-Score Launcher",
    page_icon="⚡",
    layout="centered"
)

def _is_port_free(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        s.close()
        return True
    except OSError:
        return False


def _find_free_port(preferred: int) -> int:
    if _is_port_free(preferred):
        return preferred
    # find any free port
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def launch_app(app_name: str, preferred_port: Optional[int] = None) -> Tuple[bool, str, Optional[subprocess.Popen]]:
    """Launch the specified application and return (success, url, process).

    Uses the workspace venv python if available to run streamlit deterministically.
    """
    try:
        current_dir = os.getcwd()

        # map apps to script names with correct paths
        if app_name == "user":
            script = os.path.join("src", "apps", "app_user.py")
            preferred = preferred_port or 8503
        elif app_name == "admin":
            script = os.path.join("src", "apps", "app_admin.py")
            preferred = preferred_port or 8504
        else:
            return False, "Invalid app name", None

        port = _find_free_port(preferred)
        app_url = f"http://localhost:{port}"

        # prefer workspace venv python executable
        venv_python = os.path.join(current_dir, ".venv", "bin", "python")
        python_exec = venv_python if os.path.exists(venv_python) else "python"

        cmd = [python_exec, "-m", "streamlit", "run", os.path.join(current_dir, script), "--server.port", str(port)]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if os.name != 'nt' else None
        )

        # Wait briefly for server to start
        time.sleep(2)

        # Try to open browser programmatically (best-effort)
        try:
            webbrowser.open(app_url)
        except Exception:
            pass

        return True, app_url, process

    except Exception as e:
        return False, str(e), None

# Purple theme CSS for Z-Score launcher
st.markdown("""
<style>
    :root {
        --bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --card: rgba(255, 255, 255, 0.9);
        --text: #2d3748;
        --text-light: #4a5568;
        --primary: #805ad5;
        --accent: #9f7aea;
    }

    body, .stApp, .main {
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
    }

    .main .block-container {
        background: var(--card) !important;
        padding: 1.5rem 2rem !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.15) !important;
        max-width: 1000px;
        margin: 1.2rem auto !important;
        backdrop-filter: blur(10px);
    }

    h1, h2, h3 { color: var(--text) !important; text-align: left; }

    .app-card { 
        background: rgba(255, 255, 255, 0.7) !important; 
        border: 1px solid rgba(128, 90, 213, 0.2) !important; 
        padding: 1rem !important; 
        border-radius: 8px !important;
        backdrop-filter: blur(5px);
    }

    .stButton > button {
        background: var(--primary) !important;
        color: #fff !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: var(--accent) !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(128, 90, 213, 0.3);
    }

    footer, #MainMenu, .stToolbar { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

def main():
    """Main launcher interface"""
    
    st.markdown("# Z-Score Platform")
    st.markdown("### Select Application")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="app-card">
            <h3>User Application</h3>
            <p>Credit building and assessment</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch User App", key="user_app", use_container_width=True):
            with st.spinner("Starting User App..."):
                success, result, proc = launch_app("user")
                if success:
                    st.success("User App launched!")
                    # Use link button to open in new tab
                    st.link_button("🚀 Open User App", result, use_container_width=True)
                    st.info(f"URL: {result}")
                else:
                    st.error(f"Launch failed: {result}")
                    st.code("streamlit run app_user.py", language="bash")
    
    with col2:
        st.markdown("""
        <div class="app-card">
            <h3>Admin Application</h3>
            <p>Analytics and management</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch Admin App", key="admin_app", use_container_width=True):
            with st.spinner("Starting Admin App..."):
                success, result, proc = launch_app("admin")
                if success:
                    st.success("Admin App launched!")
                    # Use link button to open in new tab
                    st.link_button("🚀 Open Admin App", result, use_container_width=True)
                    st.info(f"URL: {result}")
                else:
                    st.error(f"Launch failed: {result}")
                    st.code("streamlit run app_admin.py", language="bash")

if __name__ == "__main__":
    main()
