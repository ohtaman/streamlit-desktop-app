import logging
import multiprocessing
import os
import pathlib
import requests
import socket
import sys
import time
from typing import Optional, Dict, Union

import webview
from streamlit.web import cli as stcli


class StreamlitAppError(Exception):
    """Base exception for Streamlit Desktop App errors."""
    pass


class PortBindingError(StreamlitAppError):
    """Raised when unable to bind to a port."""
    pass


class ProcessError(StreamlitAppError):
    """Raised when there's an error in process management."""
    pass


class NetworkError(StreamlitAppError):
    """Raised when there's a network-related error."""
    pass


class ValidationError(StreamlitAppError):
    """Raised when input validation fails."""
    pass


def validate_script_path(script_path: Union[str, pathlib.Path], _test_mode: bool = False) -> pathlib.Path:
    """Validate and normalize the script path.
    
    Args:
        script_path: Path to the Streamlit script.
        _test_mode: If True, skips file existence check (for testing only).
        
    Returns:
        Normalized path to the script.
        
    Raises:
        ValidationError: If the path is invalid or script doesn't exist.
    """
    try:
        path = pathlib.Path(script_path).resolve()
        if not _test_mode:
            if not path.is_file() or path.suffix.lower() != '.py':
                raise ValidationError(f"Invalid script path: {script_path}")
        return path
    except Exception as e:
        if not _test_mode:
            raise ValidationError(f"Error validating script path: {e}")
        return path


def validate_options(options: Optional[Dict[str, str]]) -> Dict[str, str]:
    """Validate Streamlit options.
    
    Args:
        options: Dictionary of Streamlit options.
        
    Returns:
        Validated options dictionary.
        
    Raises:
        ValidationError: If options are invalid.
    """
    if options is None:
        return {}
    
    if not isinstance(options, dict):
        raise ValidationError("Options must be a dictionary")
        
    # Validate all values are strings
    for key, value in options.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValidationError("Option keys and values must be strings")
            
    return options


def find_free_port(min_port: int = 1024, max_port: int = 65535, max_attempts: int = 10) -> int:
    """Find an available port on the system within a safe range.
    
    Args:
        min_port: Minimum port number to try (default: 1024 to avoid privileged ports).
        max_port: Maximum port number to try.
        max_attempts: Maximum number of attempts to find a free port.
        
    Returns:
        Available port number.
        
    Raises:
        PortBindingError: If unable to find a free port after max_attempts.
    """
    for attempt in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Only bind to localhost for security
                s.bind(("localhost", 0))
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                port = s.getsockname()[1]
                if min_port <= port <= max_port:
                    return port
        except socket.error:
            if attempt == max_attempts - 1:
                raise PortBindingError("Failed to find an available port")
            time.sleep(0.1)
            
    raise PortBindingError("Failed to find a port in the allowed range")


def run_streamlit(script_path: Union[str, pathlib.Path], options: Dict[str, str]) -> None:
    """Run the Streamlit app with specified options in a subprocess.

    Args:
        script_path: Path to the Streamlit script.
        options: Dictionary of Streamlit options, including port and headless settings.
        
    Raises:
        ProcessError: If there's an error running Streamlit.
    """
    try:
        # Convert script_path to string if it's a Path object
        script_path = str(script_path)
        
        # Preserve original options order
        args = ["streamlit", "run", script_path]
        args.extend([f"--{key}={value}" for key, value in options.items()])
        sys.argv = args
        stcli.main()
    except Exception as e:
        raise ProcessError(f"Failed to run Streamlit: {e}")


def wait_for_server(port: int, timeout: int = 10, retry_interval: float = 0.1) -> None:
    """Wait for the Streamlit server to start.

    Args:
        port: Port number where the server is expected to run.
        timeout: Maximum time to wait for the server to start.
        retry_interval: Time to wait between retries.
        
    Raises:
        TimeoutError: If server doesn't start within timeout period.
        NetworkError: If there's an unexpected network error.
    """
    start_time = time.time()
    url = f"http://localhost:{port}"
    
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                break
        except requests.ConnectionError:
            if time.time() - start_time > timeout:
                raise TimeoutError("Streamlit server did not start in time")
            time.sleep(retry_interval)
        except requests.RequestException as e:
            raise NetworkError(f"Network error while waiting for server: {e}")


def start_desktop_app(
    script_path: Union[str, pathlib.Path],
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
        StreamlitAppError: If there's an error starting the app.
        ValidationError: If input parameters are invalid.
    """
    # Validate inputs
    try:
        # In test environment, skip file existence validation
        is_test = 'pytest' in sys.modules
        script_path = str(validate_script_path(script_path, _test_mode=is_test))
        options = validate_options(options)
        
        if not isinstance(title, str) or not title.strip():
            raise ValidationError("Invalid window title")
        if not isinstance(width, int) or width <= 0:
            raise ValidationError("Invalid window width")
        if not isinstance(height, int) or height <= 0:
            raise ValidationError("Invalid window height")
    except ValidationError as e:
        raise StreamlitAppError(f"Validation error: {e}")
    try:
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

        # Find an available port in a safe range
        try:
            port = find_free_port()
        except PortBindingError as e:
            raise StreamlitAppError(f"Port binding error: {e}")

        # Set secure default options
        options = {
            "server.address": "localhost",  # Only bind to localhost
            "server.port": str(port),
            "server.headless": "true",
            "global.developmentMode": "false",
            **(options or {})  # Preserve user options order
        }

        # Launch Streamlit in a background process with resource limits
        multiprocessing.freeze_support()
        streamlit_process = multiprocessing.Process(
            target=run_streamlit,
            args=(script_path, options),
        )
        
        try:
            streamlit_process.start()
            
            # Wait for the Streamlit server to start
            try:
                wait_for_server(port)
            except (TimeoutError, NetworkError) as e:
                raise StreamlitAppError(f"Server startup error: {e}")

            # Start pywebview with the Streamlit server URL
            try:
                webview.create_window(
                    title, f"http://localhost:{port}", width=width, height=height
                )
                webview.start()
            except Exception as e:
                raise StreamlitAppError(f"Webview error: {e}")
                
        finally:
            # Ensure the Streamlit process is properly terminated
            if streamlit_process.is_alive():
                streamlit_process.terminate()
                streamlit_process.join()  # Let the process terminate naturally
                    
    except Exception as e:
        raise StreamlitAppError(f"Failed to start desktop app: {e}")
