# Streamlit Desktop App

Easily run your Streamlit apps in a desktop window with `pywebview`. This package makes it simple to turn any Streamlit app into a standalone desktop application with a native window, providing a desktop-like experience for your web-based app.

## Features

- **Desktop Application Feel**: Turn your Streamlit app into a desktop application with a native window.
- **No Browser Required**: Use `pywebview` to create a streamlined experience, without needing to open a separate web browser.
- **Simple Integration**: Just a few lines of code to launch your Streamlit app in a desktop window.
- **Customizable**: Customize the title, size, and configuration of your desktop window.

## Installation

You can install `streamlit_desktop_app` via **pip** or **Poetry**:

### Using pip

```bash
pip install streamlit_desktop_app
```

### Using Poetry

```bash
poetry add streamlit_desktop_app
```

## Quick Start

Here is how you can quickly get started:

### Example Streamlit App

Create an example Streamlit app file named `example.py`:

```python
import streamlit as st

st.title("Streamlit Desktop App Example")
st.write("This is a simple example running in a desktop window!")
st.button("Click me!")
```

### Running as a Desktop App

To run the `example.py` app as a desktop application, use the following code:

```python
from streamlit_desktop_app import start_desktop_app

start_desktop_app("example.py", title="My Streamlit Desktop App")
```

This will open your Streamlit app in a native desktop window without requiring a web browser.

## CLI Usage

You can also run the package directly from the command line to launch the default example app:

```bash
python -m streamlit_desktop_app
```

This will use the built-in example app to demonstrate how `streamlit_desktop_app` works.

## API Reference

```python
start_desktop_app(script_path, title="Streamlit Desktop App", width=800, height=600, options=None)
```

- **`script_path`** (str): Path to the Streamlit script to be run.
- **`title`** (str): Title of the desktop window (default: "Streamlit Desktop App").
- **`width`** (int): Width of the desktop window (default: 800).
- **`height`** (int): Height of the desktop window (default: 600).
- **`options`** (dict): Additional Streamlit options (e.g., `server.enableCORS`).

```python
run_streamlit(script_path, options)
```

- **`script_path`** (str): Path to the Streamlit script to be run.
- **`options`** (dict): Dictionary of Streamlit configuration options, such as port and headless settings.

This function allows you to start Streamlit in a background process.

## Requirements

- **Python 3.8+**
- **Streamlit**: The core framework for building the app (`pip install streamlit`).
- **PyWebview**: For creating a desktop window (`pip install pywebview`).
- **Requests**: For checking the server status (`pip install requests`).

All required packages will be installed automatically when using `pip` or `Poetry`.

## Contributing

Contributions are welcome! If you have suggestions or feature requests, feel free to open an issue or submit a pull request.

### Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/ohtaman/streamlit-desktop-app.git
   ```

2. Install dependencies with Poetry:

   ```bash
   poetry install
   ```

3. Make your changes and ensure tests pass.

## License

This project is licensed under the Apache License Ver. 2.0. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- [Streamlit](https://streamlit.io/) for making data apps easy to create.
- [PyWebview](https://github.com/r0x0r/pywebview) for enabling seamless desktop integration.

## Contact

If you have any questions or issues, feel free to reach out via [GitHub Issues](https://github.com/ohtaman/streamlit-desktop-app/issues).

