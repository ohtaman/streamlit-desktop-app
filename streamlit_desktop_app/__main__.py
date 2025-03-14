"""Entry point module for the Streamlit Desktop App package.

This module serves as the main entry point when the package is run directly
using python -m streamlit_desktop_app. It demonstrates basic usage by running
the included example application.

The example can be run in two ways:
1. As a module:
   ```bash
   python -m streamlit_desktop_app
   ```

2. After installation, via the console script:
   ```bash
   streamlit-desktop-app run example.py
   ```

This provides users with a quick way to see the package in action and
understand its basic functionality.
"""

import os
from streamlit_desktop_app.core import start_desktop_app


def main():
    """Launch the example Streamlit application in desktop mode.

    This function:
    1. Locates the example.py script included with the package
    2. Launches it as a desktop application using start_desktop_app
    3. Configures basic window properties like title

    The example application demonstrates core features and serves
    as a template for creating custom applications.
    """
    # Get the path to the example script
    script_path = os.path.join(os.path.dirname(__file__), "example.py")

    # Start the Streamlit desktop app with the example script
    start_desktop_app(script_path, title="My Streamlit Desktop App")


if __name__ == "__main__":
    main()
