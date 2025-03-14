import logging
import multiprocessing
import requests
import socket
import sys
import time
from typing import Optional, Dict

import webview
from streamlit.web import cli as stcli


def find_free_port() -> int:
    """Find an available port on the system.

    This function creates a temporary socket, binds it to an available port,
    and returns that port number. The socket is configured with REUSEADDR
    to ensure the port can be immediately reused.

    Returns:
        int: An available port number that can be used for binding.

    Raises:
        socket.error: If there is an error creating or binding the socket.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def run_streamlit(script_path: str, options: Dict[str, str]) -> None:
    """Run the Streamlit app with specified options in a subprocess.

    This function configures and launches a Streamlit application using the provided
    script and options. It modifies sys.argv to pass the options to Streamlit's CLI.

    Args:
        script_path: Path to the Streamlit script to run. Should be a valid Python
            file that contains a Streamlit application.
        options: Dictionary of Streamlit configuration options. Each key-value pair
            will be converted to a command-line argument in the format --key=value.
            Common options include 'server.port', 'server.address', etc.

    Example:
        >>> options = {
        ...     'server.port': '8501',
        ...     'server.address': 'localhost'
        ... }
        >>> run_streamlit('app.py', options)
    """
    args = ["streamlit", "run", script_path]
    args.extend([f"--{key}={value}" for key, value in options.items()])
    sys.argv = args
    stcli.main()


def wait_for_server(port: int, timeout: int = 10) -> None:
    """Wait for the Streamlit server to start and become responsive.

    This function repeatedly attempts to connect to the Streamlit server
    until it succeeds or times out. It uses HTTP GET requests to check
    if the server is accepting connections.

    Args:
        port: Port number where the server is expected to run. Should be
            a valid port number between 1 and 65535.
        timeout: Maximum time in seconds to wait for the server to start.
            Defaults to 10 seconds.

    Raises:
        TimeoutError: If the server does not become responsive within the
            specified timeout period.
        requests.ConnectionError: If there are network connectivity issues.

    Example:
        >>> try:
        ...     wait_for_server(8501, timeout=15)
        ... except TimeoutError:
        ...     print("Server failed to start")
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
    """Start the Streamlit app as a desktop application using pywebview.

    This function creates a desktop window that runs a Streamlit application.
    It handles the complete lifecycle of both the Streamlit server and the
    desktop window, including proper cleanup when the window is closed.

    Args:
        script_path: Path to the Streamlit script to run. Should be a valid Python
            file that contains a Streamlit application.
        title: Title of the desktop window. Defaults to "Streamlit Desktop App".
        width: Width of the desktop window in pixels. Defaults to 1024.
        height: Height of the desktop window in pixels. Defaults to 768.
        options: Optional dictionary of additional Streamlit configuration options.
            Note that certain options (server.address, server.port, server.headless,
            global.developmentMode) will be overridden by the application.

    Raises:
        FileNotFoundError: If the specified script_path does not exist.
        TimeoutError: If the Streamlit server fails to start within the timeout period.
        RuntimeError: If there are issues with the webview window creation or
            Streamlit process management.

    Example:
        >>> # Basic usage
        >>> start_desktop_app('app.py')
        >>>
        >>> # Custom window size and title
        >>> start_desktop_app(
        ...     'app.py',
        ...     title='My Streamlit App',
        ...     width=1200,
        ...     height=800
        ... )
        >>>
        >>> # With additional Streamlit options
        >>> start_desktop_app(
        ...     'app.py',
        ...     options={
        ...         'theme.primaryColor': '#F63366',
        ...         'theme.backgroundColor': '#FFFFFF'
        ...     }
        ... )
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
            logging.warning(
                f"Option '{opt}' is overridden by the application and will be ignored."
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
