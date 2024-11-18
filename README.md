# Streamlit Desktop App

Seamlessly transform your Streamlit apps into standalone desktop applications. This library enables you to run your web-based Streamlit projects in native desktop windows, providing a polished and intuitive user experience—no browser required!

---

## 🚀 Features

- **Effortless Deployment**  
  With built-in PyInstaller support, convert your Streamlit app into a standalone executable in just one command.

- **Native Desktop Experience**  
  Run your Streamlit app in a native desktop window for a true desktop-like feel.

- **Automatic Cleanup**  
  The Streamlit process ends automatically when the desktop window is closed, ensuring no lingering background processes.

---

## 📖 Quick Start

### Installation

You can install `streamlit_desktop_app` via **pip** or **Poetry**. Both options ensure an easy and smooth installation process.

#### Using pip

```bash
pip install streamlit_desktop_app
```

#### Using Poetry

```bash
poetry add streamlit_desktop_app
```

### Verify the Installation

To verify the installation, run the following command:

```bash
python -m streamlit_desktop_app
```

This will open a desktop window with a pre-built Streamlit app that includes a simple layout demonstrating the library's capabilities.

---

## 🎨 Create and Build Your App

### Step 1: Create an Example App

Start by creating a simple `example.py` file:

```python
import streamlit as st

st.title("Streamlit Desktop App Example")
st.write("This is a simple example running in a desktop window!")
st.button("Click me!")
```

### Step 2: Build Your App into an Executable

To create a standalone executable, run the following command:

```bash
streamlit-desktop-build --script example.py --name "MyStreamlitApp"
```

This command will:

1. Build your Streamlit app into an executable.
2. Place the executable in the `dist/` directory.

### Advanced Options

#### Example with PyInstaller Options

If you want more control over the build process, use the `--pyinstaller-options` parameter. For example:

```bash
streamlit-desktop-build --script example.py --name "MyStreamlitApp" --icon path/to/icon.ico --pyinstaller-options --onefile --noconfirm
```

- **`--onefile`**: Packages everything into a single executable.
- **`--noconfirm`**: Suppresses confirmation prompts during the build.

#### Example with Streamlit Options

To customize the behavior of the Streamlit app, use the `--streamlit-options` parameter. For example, to enable a dark theme:

```bash
streamlit-desktop-build --script example.py --name "MyStreamlitApp" --icon path/to/icon.ico --streamlit-options --theme.base=dark
```

---

## 🛠 Advanced: Launch Programmatically

If you prefer programmatic control, use the `start_desktop_app` function to launch your app in a desktop window:

```python
from streamlit_desktop_app import start_desktop_app

start_desktop_app("example.py", title="My Streamlit Desktop App")
```

This method is useful for:

- Embedding additional logic before launching your app.
- Development and testing.

---

## API Reference

### `start_desktop_app`

```python
start_desktop_app(script_path, title="Streamlit Desktop App", width=1024, height=768, options=None)
```

- **`script_path`** (str): Path to the Streamlit script to be run.
- **`title`** (str): Title of the desktop window (default: "Streamlit Desktop App").
- **`width`** (int): Width of the desktop window (default: 1024).
- **`height`** (int): Height of the desktop window (default: 768).
- **`options`** (dict): Additional Streamlit options (e.g., `server.enableCORS`).

---

### Manually Run PyInstaller

If you prefer manual control, use PyInstaller directly to build your app:

```bash
pyinstaller --collect-all streamlit --copy-metadata streamlit --name "MyStreamlitApp" --onefile --windowed --splash path/to/splash_image.png -i path/to/icon.ico example.py
```

- **`--collect-all`**: Includes all static files and resources required by Streamlit.
- **`--copy-metadata`**: Ensures the metadata for Streamlit is included.
- **`--onefile`**: Packages everything into a single executable.
- **`--splash`**: Displays a splash screen while the app initializes.

---

## ⚠️ Important for Windows Users

To run desktop applications on Windows, you must have the **.NET Framework** (> 4.0) installed. This is required for compatibility with `pywebview`.

---

## 🤝 Contributing

We welcome contributions! If you have suggestions or feature requests, feel free to open an issue or submit a pull request.

### Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/ohtaman/streamlit-desktop-app.git
   ```

2. Install dependencies with Poetry:

   ```bash
   poetry install
   ```

3. Run the tests to ensure everything works as expected:

   ```bash
   poetry run pytest
   ```

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🎉 Acknowledgments

- [Streamlit](https://streamlit.io/) for its powerful framework.
- [PyWebview](https://github.com/r0x0r/pywebview) for enabling seamless desktop integration.
- [PyInstaller](https://www.pyinstaller.org/) for making standalone executable creation a breeze.

---

## Contact

If you have any questions or issues, feel free to reach out via [GitHub Issues](https://github.com/ohtaman/streamlit-desktop-app/issues).
