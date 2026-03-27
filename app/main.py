"""
Main Application Entry Point
Launches the Streamlit dashboard.
"""
import subprocess
import sys
import os


def main():
    """Launch the Streamlit dashboard."""
    dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.py")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", dashboard_path,
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ])


if __name__ == "__main__":
    main()
