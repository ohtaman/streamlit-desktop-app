# Streamlit Desktop App

Easily run your Streamlit apps in a desktop window with `pywebview`. This package makes it simple to turn any Streamlit app into a standalone desktop application with a native window, providing a desktop-like experience for your web-based app.

## Features

- **Desktop Application Feel**: Turn your Streamlit app into a desktop application with a native window.
- **No Browser Required**: Use `pywebview` to create a streamlined experience, without needing to open a separate web browser.
- **Simple Integration**: Just a few lines of code to launch your Streamlit app in a desktop window.

## Installation

You can install `streamlit_desktop_app` via **pip** or **Poetry**. To use optional features like building standalone executables, you can also install additional dependencies.

### Using pip

```bash
pip install streamlit_desktop_app
```

To install with optional PyInstaller support:

```bash
pip install streamlit_desktop_app[pyinstaller]
```

### Using Poetry

```bash
poetry add streamlit_desktop_app
```

To add with optional PyInstaller support:

```bash
poetry add streamlit_desktop_app -E pyinstaller
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

- **Python >=3.8,<3.9.7 || >3.9.7,<3.13**
- **Streamlit**: The core framework for building the app (`pip install streamlit`).
- **PyWebview**: For creating a desktop window (`pip install pywebview`).
- **Requests**: For checking the server status (`pip install requests`).

All required packages will be installed automatically when using `pip` or `Poetry`.

## Building a Distributable File with PyInstaller

To create a standalone executable for your Streamlit desktop app using **PyInstaller**, you can either manually run the commands or use the built-in wrapper command provided by this framework for convenience.

### Using `streamlit-desktop-build`

The `streamlit-desktop-build` command simplifies creating standalone executables for your Streamlit desktop app. To use this command, you **must** install the library with PyInstaller support.

#### Example with PyInstaller Options

You can pass Streamlit configuration options using the `--streamlit-options` parameter. For example, the `--onefile` option packages everything into a single executable, making distribution easier:

```bash
streamlit-desktop-build --script example.py --name "MyStreamlitApp" --icon path/to/icon.ico --pyinstaller-options --onefile --noconfirm
```

#### Example with Streamlit Options

You can also pass Streamlit configuration options using the `--streamlit-options` parameter. For example, to set a dark theme:

```bash
streamlit-desktop-build --script example.py --name "MyStreamlitApp" --icon path/to/icon.ico --streamlit-options --theme.base=dark
```

### Manually Running PyInstaller

If you prefer to run PyInstaller manually, follow these steps:

1. **Install PyInstaller** (optional, for building executables):

   ```bash
   pip install streamlit_desktop_app[pyinstaller]
   ```

2. **Create a PyInstaller Spec File** (optional):
   You can customize the build process by creating a `.spec` file. This step is optional but recommended if you need more control over the build process.

3. **Run PyInstaller Manually**:

   Run the following command to create a standalone executable for your app:

   ```bash
   pyinstaller --collect-all streamlit --copy-metadata streamlit --name "MyStreamlitApp" --onefile --windowed --splash path/to/splash_image.png -i path/to/icon.ico example.py
   ```

   - **`--collect-all`**: Collects all necessary static files and resources for Streamlit to function properly.
   - **`--copy-metadata`**: Ensures the required metadata for Streamlit is included in the executable, allowing it to function as expected.
   - **`--name`**: Sets the name of the generated executable.
   - **`--onefile`**: (Optional) Packages everything into a single executable.
   - **`--windowed`**: (Optional) Prevents a terminal window from opening alongside the app.
   - **`-i`**: (Optional) Sets the icon for the executable.
   - **--splash**: (Optional) Displays a splash screen with the specified image while the application initializes.

4. **Locate the Executable**:

   After running PyInstaller, you will find the generated executable in the `dist/` directory.

5. **Run the Executable**:

   Navigate to the `dist/` directory and run the executable:

   ```bash
   ./MyStreamlitApp
   ```

This will open your Streamlit app in a native desktop window, just like when running it directly via Python.

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

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- [Streamlit](https://streamlit.io/) for making data apps easy to create.
- [PyWebview](https://github.com/r0x0r/pywebview) for enabling seamless desktop integration.
- [PyInstaller](https://www.pyinstaller.org/) for providing the tools to create standalone executables.

## Contact

If you have any questions or issues, feel free to reach out via [GitHub Issues](https://github.com/ohtaman/streamlit-desktop-app/issues).
