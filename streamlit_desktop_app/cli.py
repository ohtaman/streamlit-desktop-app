"""Command Line Interface for Streamlit Desktop App.

This module provides the command-line interface for building standalone
desktop applications from Streamlit scripts. It supports various configuration
options for both PyInstaller and Streamlit.

Usage:
    streamlit-desktop-app build app.py --name MyApp [options]

Options:
    --name              Name of the output executable (required)
    --icon             Path to the icon file for the executable
    --pyinstaller-options  Additional PyInstaller options
    --streamlit-options    Additional Streamlit configuration options

Examples:
    # Basic usage
    streamlit-desktop-app build app.py --name MyApp

    # With custom icon
    streamlit-desktop-app build app.py --name MyApp --icon icon.ico

    # With PyInstaller options
    streamlit-desktop-app build app.py --name MyApp --pyinstaller-options --onefile --clean

    # With Streamlit options
    streamlit-desktop-app build app.py --name MyApp --streamlit-options --theme.primaryColor=#F63366
"""

import argparse
from streamlit_desktop_app.build import build_executable


def build_command(args: argparse.Namespace):
    """Handle the 'build' subcommand by processing arguments and building the executable.

    This function processes the command-line arguments for the 'build' subcommand,
    separates PyInstaller and Streamlit options, and delegates to the build_executable
    function to create the standalone application.

    Args:
        args: Namespace object containing the parsed command-line arguments including:
            - script: Path to the Streamlit script
            - name: Name of the output executable
            - icon: Optional path to the icon file
            - pyinstaller_options: Additional PyInstaller command-line options
            - streamlit_options: Additional Streamlit configuration options

    Example:
        When called via CLI:
        ```bash
        streamlit-desktop-app build app.py --name MyApp --icon app.ico \\
            --pyinstaller-options --onefile --clean \\
            --streamlit-options --theme.primaryColor=#F63366
        ```
    """

    pyinstaller_options = []
    streamlit_options = []

    if args.pyinstaller_options:
        if "--streamlit-options" in args.pyinstaller_options:
            split_index = args.pyinstaller_options.index("--streamlit-options")
            pyinstaller_options = args.pyinstaller_options[:split_index]
            streamlit_options = args.pyinstaller_options[split_index + 1 :]
        else:
            pyinstaller_options = args.pyinstaller_options

    if args.streamlit_options:
        if "--pyinstaller-options" in args.streamlit_options:
            split_index = args.streamlit_options.index("--pyinstaller-options")
            streamlit_options = args.streamlit_options[:split_index]
            pyinstaller_options = args.streamlit_options[split_index + 1 :]
        else:
            streamlit_options = args.streamlit_options

    build_executable(
        script_path=args.script,
        name=args.name,
        icon=args.icon,
        pyinstaller_options=pyinstaller_options,
        streamlit_options=streamlit_options,
    )


def add_build_parser(subparsers: argparse._SubParsersAction):
    """Add the 'build' subcommand parser to the main parser.

    This function configures the argument parser for the 'build' subcommand,
    defining all available options and their help text.

    Args:
        subparsers: The subparsers action object to which the build parser
            will be added. This allows the CLI to handle multiple subcommands.

    The build subcommand supports the following arguments:
        - script: (Required) Path to the Streamlit script to package
        - --name: (Required) Name of the output executable
        - --icon: (Optional) Path to the icon file for the executable
        - --pyinstaller-options: (Optional) Additional PyInstaller arguments
        - --streamlit-options: (Optional) Additional Streamlit CLI options
    """
    build_parser = subparsers.add_parser(
        "build", help="Build a standalone executable for your Streamlit desktop app."
    )
    build_parser.add_argument("script", help="Path to the Streamlit script to be packaged.")
    build_parser.add_argument("--name", required=True, help="Name of the output executable.")
    build_parser.add_argument("--icon", help="Path to the icon file for the executable.")
    build_parser.add_argument(
        "--pyinstaller-options",
        nargs=argparse.REMAINDER,
        help="Additional arguments to pass to PyInstaller."
    )
    build_parser.add_argument(
        "--streamlit-options",
        nargs=argparse.REMAINDER,
        help="Additional Streamlit CLI options."
    )
    build_parser.set_defaults(func=build_command)


def main():
    """Main entry point for the Streamlit Desktop App CLI.

    This function sets up the argument parser, processes command-line arguments,
    and executes the appropriate subcommand. Currently supports the 'build'
    subcommand for creating standalone executables.

    Example:
        ```python
        if __name__ == "__main__":
            main()
        ```
    """
    parser = argparse.ArgumentParser(
        description="Streamlit Desktop App CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_build_parser(subparsers)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
