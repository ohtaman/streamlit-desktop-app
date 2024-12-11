import argparse


from streamlit_desktop_app.build import build_executable


def build_command(args: argparse.Namespace):
    """
    Handle the 'build' subcommand.
    Parse additional options and delegate to the build_executable function.
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
    """
    Add the 'build' subcommand parser.

    Args:
        subparsers: The subparsers action to which the 'build' parser will be added.
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
    parser = argparse.ArgumentParser(
        description="Streamlit Desktop App CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_build_parser(subparsers)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
