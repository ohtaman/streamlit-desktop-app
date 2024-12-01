import multiprocessing
import webview
import socket
import sys
import time
from typing import Optional, Dict
import requests

from streamlit.web import cli as stcli


def find_free_port() -> int:
    """Find an available port on the system."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def run_streamlit(script_path: str, options: Dict[str, str]) -> None:
    """Run the Streamlit app with specified options in a subprocess.

    Args:
        script_path: Path to the Streamlit script.
        options: Dictionary of Streamlit options, including port and headless settings.
    """
    args = ["streamlit", "run", script_path]
    args.extend([f"--{key}={value}" for key, value in options.items()])
    sys.argv = args
    stcli.main()


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
    width: int = 1024,
    height: int = 768,
    options: Optional[Dict[str, str]] = None,
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

    # Check for overridden options and print warnings
    overridden_options = [
        "server.address",
        "server.port",
        "server.headless",
        "global.developmentMode",
    ]
    for opt in overridden_options:
        if opt in options:
            print(
                f"Warning: Option '{opt}' is overridden by the application and will be ignored."
            )

    port = find_free_port()
    options["server.address"] = "localhost"
    options["server.port"] = str(port)
    options["server.headless"] = "true"
    options["global.developmentMode"] = "false"

    # Launch Streamlit in a background process
    multiprocessing.freeze_support()
    streamlit_process = multiprocessing.Process(
        target=run_streamlit, args=(script_path, options)
    )
    streamlit_process.start()

    try:
        # Wait for the Streamlit server to start
        wait_for_server(port)

        # Start pywebview with the Streamlit server URL
        webview.create_window(
            title, f"http://localhost:{port}", width=width, height=height
        )
        webview.start()
    finally:
        # Ensure the Streamlit process is terminated
        streamlit_process.terminate()
        streamlit_process.join()
