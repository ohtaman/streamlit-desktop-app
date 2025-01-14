"""Build module for creating standalone executables from Streamlit applications.

This module provides functionality to package Streamlit applications into
standalone executables using PyInstaller. It handles all the complexity of:
- Analyzing Python script dependencies
- Managing Streamlit configuration options
- Creating a wrapper script for the application
- Configuring PyInstaller for proper packaging

The main entry point is the build_executable function, which orchestrates
the entire build process.

Example:
    ```python
    from streamlit_desktop_app.build import build_executable

    # Basic usage
    build_executable(
        script_path='app.py',
        name='MyApp',
        icon='icon.ico'
    )

    # With additional options
    build_executable(
        script_path='app.py',
        name='MyApp',
        icon='icon.ico',
        pyinstaller_options=['--onefile', '--clean'],
        streamlit_options=['--theme.primaryColor', '#F63366']
    )
    ```
"""

import ast
import os
import sys
import tempfile
from typing import Optional, Dict, List, Union
import PyInstaller.__main__


def extract_imports(script_path: str) -> List[str]:
    """
    Extract a list of imported modules from a Python script.

    This function analyzes the AST (Abstract Syntax Tree) of a Python script
    to identify all `import` and `from ... import ...` statements, returning 
    a list of fully qualified module names.

    Args:
        script_path (str): Path to the Python script to analyze.

    Returns:
        List[str]: A list of imported module names, including top-level and submodules.
    """
    # Read and parse the script
    with open(script_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=script_path)

    imports = set()

    # Traverse the AST to find import statements
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # Handle `import module` or `import module as alias`
            for module in node.names:
                imports.add(module.name)  # Only add the module name
        elif isinstance(node, ast.ImportFrom):
            # Handle `from module import name` or `from module import name as alias`
            if node.module:
                for alias in node.names:
                    # Add the fully qualified module name
                    imports.add(f"{node.module}.{alias.name}")

    # Return a sorted list of unique imports
    return sorted(imports)


def parse_streamlit_options(
    options: Optional[Union[List[str], Dict[str, str]]],
) -> Optional[Dict[str, str]]:
    """Parse and normalize Streamlit configuration options.

    This function converts Streamlit options from either command-line style
    arguments or a dictionary into a normalized dictionary format. It handles
    both flag-style options and key-value pairs.

    Args:
        options: Either a list of command-line style arguments
            (e.g., ["--theme.base", "dark", "--server.headless"]) or
            a dictionary of options (e.g., {"theme.base": "dark"}).

    Returns:
        Optional[Dict[str, str]]: A dictionary of normalized options where:
            - Keys are option names without leading dashes
            - Values are the corresponding option values
            - Flag-style options are set to "true"
            Returns None if no options are provided.

    Examples:
        >>> parse_streamlit_options(["--theme.base", "dark"])
        {"theme.base": "dark"}
        
        >>> parse_streamlit_options(["--server.headless"])
        {"server.headless": "true"}
        
        >>> parse_streamlit_options({"theme.base": "dark"})
        {"theme.base": "dark"}
    """
    if not options:
        return None

    if isinstance(options, dict):
        # If already a dictionary, return as is
        return options

    options_dict = {}
    current_key = None

    for token in options:
        if token.startswith("--"):
            # Strip the leading '--' and prepare for a new key
            if "=" in token:
                key, value = token.lstrip("-").split("=", 1)
                options_dict[key] = value
            else:
                current_key = token.lstrip("-")
                options_dict[current_key] = "true"  # Assume flag is True unless overridden
        else:
            # This token is the value for the last key
            if current_key:
                options_dict[current_key] = token
                current_key = None  # Reset after value assignment

    return options_dict


def build_executable(
    script_path: str,
    name: str,
    icon: Optional[str] = None,
    pyinstaller_options: Optional[List[str]] = None,
    streamlit_options: Optional[list[str]] = None,
):
    """Build a standalone executable from a Streamlit application.

    This function packages a Streamlit application into a standalone executable
    using PyInstaller. It handles all necessary setup including:
    - Creating a wrapper script that launches the Streamlit application
    - Configuring PyInstaller with appropriate options
    - Managing dependencies and resources
    - Handling platform-specific requirements

    Args:
        script_path: Path to the Streamlit application script. Must be a valid
            Python file containing a Streamlit application.
        name: Name for the output executable. This will be the name of the
            final application.
        icon: Optional path to an icon file (.ico) to use for the executable.
            If not provided, the default PyInstaller icon will be used.
        pyinstaller_options: Optional list of additional PyInstaller command-line
            options. These will be passed directly to PyInstaller.
        streamlit_options: Optional list of Streamlit configuration options.
            These will be applied when the application starts.

    Raises:
        SystemExit: If the specified script_path does not exist.
        PyInstaller.exceptions.ExecCommandFailed: If PyInstaller encounters
            an error during the build process.

    Example:
        ```python
        # Basic usage
        build_executable('app.py', 'MyApp')

        # With custom icon and options
        build_executable(
            script_path='app.py',
            name='MyApp',
            icon='app.ico',
            pyinstaller_options=['--onefile', '--clean'],
            streamlit_options=['--theme.primaryColor', '#F63366']
        )
        ```
    """
    if not os.path.exists(script_path):
        sys.exit(f"Error: The script '{script_path}' does not exist.")

    script_path = os.path.abspath(script_path)
    if icon:
        icon = os.path.abspath(icon)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as wrapper:
        wrapper_path = wrapper.name
        wrapper_content = f"""
import os
import sys

from streamlit_desktop_app import start_desktop_app
import streamlit_desktop_app


# To avoid font cache generation
if "MPLCONFIGDIR" in os.environ:
    del(os.environ["MPLCONFIGDIR"])


def get_script_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "{os.path.basename(script_path)}")
    else:
        return os.path.join(os.path.dirname(sys.executable), "{os.path.basename(script_path)}")


if __name__ == "__main__":
    if '_PYI_SPLASH_IPC' in os.environ:
        import pyi_splash
        pyi_splash.close()
    start_desktop_app(get_script_path(), title="{name}", options={parse_streamlit_options(streamlit_options)})
"""
        wrapper.write(wrapper_content.encode())


    args = [
        "--name",
        name,
        "--paths",
        ".",
        "--collect-all",
        "streamlit",
        "--copy-metadata",
        "streamlit",
        "--add-data",
        f"{script_path}:.",  # Add the script as a data file
    ]

    if icon:
        args.extend(["-i", icon])

    for pkg in extract_imports(script_path):
        args.extend(["--hidden-import", pkg])

    if pyinstaller_options:
        args.extend(pyinstaller_options)

    args.append(wrapper_path)

    PyInstaller.__main__.run(args)

    os.remove(wrapper_path)
