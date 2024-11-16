from streamlit_desktop_app.core import start_desktop_app
import os


def main():
    # Get the path to the example script
    script_path = os.path.join(os.path.dirname(__file__), "example.py")

    # Start the Streamlit desktop app with the example script
    start_desktop_app(script_path, title="My Streamlit Desktop App")


if __name__ == "__main__":
    main()
