import logging
import multiprocessing
import requests
import socket
import sys
import time
from typing import Optional, Dict

import webview
from streamlit.web import cli as stcli

logger = logging.getLogger(__name__)

class StreamlitAppError(Exception):
    """Base exception class for Streamlit Desktop App errors."""
    pass

class NetworkError(StreamlitAppError):
    """Raised when network-related operations fail."""
    pass

class PortBindingError(StreamlitAppError):
    """Raised when port binding operations fail."""
    pass

class ProcessError(StreamlitAppError):
    """Raised when process management operations fail."""
    pass

def find_free_port(max_attempts: int = 3) -> int:
    """Find an available port on the system.
    
    Args:
        max_attempts: Maximum number of attempts to find a free port.
        
    Returns:
        int: Available port number.
        
    Raises:
        PortBindingError: If unable to find a free port after max attempts.
    """
    for attempt in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", 0))
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                return s.getsockname()[1]
        except socket.error as e:
            logger.warning(f"Port binding attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_attempts - 1:
                raise PortBindingError(f"Failed to find a free port after {max_attempts} attempts: {str(e)}")
            time.sleep(0.1)


def run_streamlit(script_path: str, options: Dict[str, str]) -> None:
    """Run the Streamlit app with specified options in a subprocess.

    Args:
        script_path: Path to the Streamlit script.
        options: Dictionary of Streamlit options, including port and headless settings.
        
    Raises:
        ProcessError: If Streamlit process fails to start.
    """
    try:
        args = ["streamlit", "run", script_path]
        args.extend([f"--{key}={value}" for key, value in options.items()])
        sys.argv = args
        stcli.main()
    except Exception as e:
        raise ProcessError(f"Failed to start Streamlit process: {str(e)}")


def wait_for_server(port: int, timeout: int = 10, retry_interval: float = 0.1, max_retries: int = 3) -> None:
    """Wait for the Streamlit server to start with retry mechanism.

    Args:
        port: Port number where the server is expected to run.
        timeout: Maximum time to wait for the server to start.
        retry_interval: Time to wait between retries.
        max_retries: Maximum number of retry attempts for connection errors.

    Raises:
        TimeoutError: If server fails to start within timeout period.
        NetworkError: If server fails to start after retries.
    """
    start_time = time.time()
    url = f"http://localhost:{port}"
    retry_count = 0
    
    while True:
        try:
            requests.get(url)
            logger.info(f"Successfully connected to Streamlit server on port {port}")
            break
        except requests.ConnectionError as e:
            retry_count += 1
            if retry_count > max_retries:
                raise NetworkError(f"Failed to connect to Streamlit server after {max_retries} retries: {str(e)}")
            
            current_time = time.time()
            if current_time - start_time > timeout:
                raise TimeoutError(f"Streamlit server did not start within {timeout} seconds")
            
            logger.warning(f"Connection attempt {retry_count} failed, retrying in {retry_interval} seconds")
            time.sleep(retry_interval)
        except requests.RequestException as e:
            raise NetworkError(f"Unexpected error while connecting to Streamlit server: {str(e)}")


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

    Raises:
        StreamlitAppError: Base exception for all app-related errors.
        NetworkError: If server connection fails.
        PortBindingError: If port binding fails.
        ProcessError: If process management fails.
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
            logger.warning(
                f"Option '{opt}' is overridden by the application and will be ignored."
            )

    try:
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
            # Ensure the Streamlit process is terminated gracefully
            if streamlit_process.is_alive():
                logger.info("Terminating Streamlit process...")
                streamlit_process.terminate()
                streamlit_process.join()  # Single join call without timeout
            
            logger.info("Streamlit process terminated successfully")
            
    except Exception as e:
        logger.error(f"Fatal error in desktop app: {str(e)}")
        raise StreamlitAppError(f"Desktop app failed to start: {str(e)}") from e
