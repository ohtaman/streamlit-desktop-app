"""Streamlit Desktop App - Run Streamlit applications as native desktop applications.

This package provides functionality to convert Streamlit web applications into
standalone desktop applications using pywebview. It handles all the complexity
of running a Streamlit server and displaying it in a native window.

Main Features:
    - Convert any Streamlit app into a desktop application
    - Customizable window properties (title, size)
    - Automatic port management
    - Clean process handling and termination

Example:
    from streamlit_desktop_app import start_desktop_app

    # Basic usage
    start_desktop_app('your_app.py')

    # Customized window
    start_desktop_app(
        'your_app.py',
        title='My Desktop App',
        width=1200,
        height=800,
        options={'theme.primaryColor': '#F63366'}
    )
"""

from streamlit_desktop_app.core import run_streamlit, start_desktop_app
from streamlit_desktop_app._version import __version__

__all__ = ["run_streamlit", "start_desktop_app", "__version__"]
