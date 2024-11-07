import webview
import socket
import subprocess
import sys
import time
from typing import Optional, Dict
import requests


def find_free_port() -> int:
    """Find an available port on the system."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def run_streamlit(script_path: str, options: Dict[str, str]) -> subprocess.Popen:
    """Run the Streamlit app with specified options in a subprocess.

    Args:
        script_path: Path to the Streamlit script.
        options: Dictionary of Streamlit options, including port and headless settings.

    Returns:
        A Popen object representing the Streamlit server process.
    """
    args = [sys.executable, "-m", "streamlit.web.cli", "run", script_path]
    args.extend([f"--{key}={value}" for key, value in options.items()])
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def wait_for_server(port: int, timeout: int = 10) -> None:
    """Wait for the Streamlit server to start.

    Args:
        port: Port number where the server is expected to run.
        timeout: Maximum time to wait for the server to start.
    """
    start_time = time.time()
    url = f"http://localhost:{port}"
    while True:
        try:
            requests.get(url)
            break
        except requests.ConnectionError:
            if time.time() - start_time > timeout:
                raise TimeoutError("Streamlit server did not start in time.")
            time.sleep(0.1)


def start_desktop_app(
    script_path: str,
    title: str = "Streamlit Desktop App",
    width: int = 800,
    height: int = 600,
    options: Optional[Dict[str, str]] = None
) -> None:
    """Start the Streamlit app as a desktop app using pywebview.

    Args:
        script_path: Path to the Streamlit script.
        title: Title of the desktop window.
        width: Width of the desktop window.
        height: Height of the desktop window.
        options: Dictionary of additional Streamlit options.
    """
    if options is None:
        options = {}
    port = find_free_port()
    options["server.port"] = str(port)
    options["server.headless"] = "true"

    # Launch Streamlit in a background process
    streamlit_process = run_streamlit(script_path, options)

    try:
        # Wait for the Streamlit server to start
        wait_for_server(port)

        # Start pywebview with the Streamlit server URL
        window = webview.create_window(title, f"http://localhost:{port}", width=width, height=height)
        webview.start()
    finally:
        # Ensure the Streamlit process is terminated
        streamlit_process.terminate()
        streamlit_process.wait()
