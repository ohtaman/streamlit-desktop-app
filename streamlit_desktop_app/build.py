import argparse
import ast
import os
import sys
import tempfile
from typing import Optional, Dict, List
import PyInstaller.__main__

def extract_imports(script_path: str) -> List[str]:
    """Extract all top-level imported modules from the given script."""
    imports = set()
    
    with open(script_path, "r") as file:
        tree = ast.parse(file.read(), filename=script_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])  # Capture only the top-level module
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])  # Capture only the top-level module

    return list(imports)

def parse_streamlit_options(options: Optional[List[str]]) -> Optional[Dict[str, str]]:
    if not options:
        return None
    options_dict = {}
    for option in options:
        if '=' in option:
            key, value = option.split('=', 1)
            options_dict[key] = value
        else:
            options_dict[option] = True
    return options_dict

def build_executable(script: str, name: str, icon: Optional[str] = None, pyinstaller_options: Optional[List[str]] = None, streamlit_options: Optional[list[str]] = None):
    """
    Wrapper command to build an executable using PyInstaller.
    """
    script = os.path.abspath(script)
    if icon:
        icon = os.path.abspath(icon)

    if not os.path.exists(script):
        sys.exit(f"Error: The script '{script}' does not exist.")
    
    imports = extract_imports(script)

    if "start_desktop_app" not in open(script).read():
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp_wrapper:
            wrapper_path = tmp_wrapper.name
            wrapper_content = f"""
import os
import sys

from streamlit_desktop_app import start_desktop_app

def get_script_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "{os.path.basename(script)}")
    else:
        return os.path.join(os.path.dirname(sys.executable), "{os.path.basename(script)}")

if __name__ == "__main__":
    if hasattr(sys, 'frozen'):
        import pyi_splash
        pyi_splash.close()
    start_desktop_app(get_script_path(), title="{name}", options={parse_streamlit_options(streamlit_options)})
"""
            tmp_wrapper.write(wrapper_content.encode())

    else:
        wrapper_path = script

    args = [
        "--name", name,
        "--paths", ".",
        "--collect-all", "streamlit",
        "--copy-metadata", "streamlit",
        "--hidden-import", "streamlit-desktop-app",
        "--add-data", f"{script}:.",  # Add the script as a data file
        wrapper_path
    ]

    for pkg in imports:
        args.extend(["--hidden-import", pkg])

    if icon:
        args.extend(["-i", icon])

    if pyinstaller_options:
        args.extend(pyinstaller_options)

    PyInstaller.__main__.run(args)

    if wrapper_path != script:
        os.remove(wrapper_path)

def main():
    parser = argparse.ArgumentParser(description="Build a standalone executable for your Streamlit desktop app.")
    parser.add_argument("--script", required=True, help="Path to the Streamlit script to be packaged.")
    parser.add_argument("--name", required=True, help="Name of the output executable.")
    parser.add_argument("--icon", help="Path to the icon file for the executable.")
    parser.add_argument("--pyinstaller-options", nargs=argparse.REMAINDER, help="Additional arguments to pass to PyInstaller.")
    parser.add_argument("--streamlit-options", nargs=argparse.REMAINDER, help="Additional Streamlit CLI options.")
    args = parser.parse_args()

    pyinstaller_options = []
    streamlit_options = []

    if args.pyinstaller_options:
        if '--streamlit-options' in args.pyinstaller_options:
            split_index = args.pyinstaller_options.index('--streamlit-options')
            pyinstaller_options = args.pyinstaller_options[:split_index]
            streamlit_options = args.pyinstaller_options[split_index + 1:]
        else:
            pyinstaller_options = args.pyinstaller_options

    if args.streamlit_options:
        if '--pyinstaller-options' in args.streamlit_options:
            split_index = args.streamlit_options.index('--pyinstaller-options')
            streamlit_options = args.streamlit_options[:split_index]
            pyinstaller_options = args.streamlit_options[split_index + 1:]
        else:
            streamlit_options = args.streamlit_options

    try:
        build_executable(args.script, args.name, args.icon, pyinstaller_options, streamlit_options)
    except Exception as e:
        sys.exit(f"Build failed: {e}")

if __name__ == "__main__":
    main()
