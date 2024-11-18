import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import tempfile
import shutil
from streamlit_desktop_app.build import (
    extract_imports,
    parse_streamlit_options,
    build_executable,
)


class TestBuildScript(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test scripts
        self.temp_dir = tempfile.mkdtemp()
        self.script_path = os.path.join(self.temp_dir, "test_script.py")
        with open(self.script_path, "w") as f:
            f.write(
                "import os\n"
                "import sys\n"
                "from streamlit import st\n"
                "import pandas as pd\n"
            )

        # Create a dummy icon file
        self.icon_path = os.path.join(self.temp_dir, "icon.ico")
        with open(self.icon_path, "w") as f:
            f.write("")

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)

    def test_extract_imports(self):
        # Test extracting imports from a script
        imports = extract_imports(self.script_path)
        self.assertSetEqual(set(imports), {"os", "sys", "streamlit", "pandas"})

    def test_parse_streamlit_options_from_list(self):
        # Test parsing Streamlit options from a list
        options = parse_streamlit_options(
            ["--theme.base=dark", "--server.headless", "false"]
        )
        self.assertEqual(options, {"theme.base": "dark", "server.headless": "false"})

    def test_parse_streamlit_options_from_dict(self):
        # Test parsing Streamlit options from a dictionary
        options = parse_streamlit_options({"theme.base": "dark", "server.headless": "false"})
        self.assertEqual(options, {"theme.base": "dark", "server.headless": "false"})

    def test_parse_streamlit_options_empty(self):
        # Test parsing empty options
        self.assertIsNone(parse_streamlit_options(None))
        self.assertIsNone(parse_streamlit_options([]))

    @patch("streamlit_desktop_app.build.PyInstaller.__main__.run")
    @patch("streamlit_desktop_app.build.extract_imports", return_value=["os", "sys", "streamlit", "pandas"])
    def test_build_executable_raw(self, mock_extract_imports, mock_pyinstaller_run):
        # Test building an executable with a raw script
        build_executable(
            script_path=self.script_path,
            name="TestApp",
            script_type="raw",
            raw_script_path=None,
            icon=self.icon_path,
            pyinstaller_options=["--onefile"],
            streamlit_options=["--theme.base=dark"],
        )

        # Ensure PyInstaller's run method is called with the correct arguments
        mock_pyinstaller_run.assert_called_once()
        args = mock_pyinstaller_run.call_args[0][0]
        self.assertIn("--onefile", args)
        self.assertIn("--name", args)
        self.assertIn("TestApp", args)
        self.assertIn("--add-data", args)
        self.assertIn(f"{self.script_path}:.", args)

    @patch("streamlit_desktop_app.build.PyInstaller.__main__.run")
    def test_build_executable_wrapped(self, mock_pyinstaller_run):
        # Test building an executable with a wrapped script
        wrapped_script = os.path.join(self.temp_dir, "wrapped_script.py")
        with open(wrapped_script, "w") as f:
            f.write("print('Wrapped script running')")

        build_executable(
            script_path=wrapped_script,
            name="TestApp",
            script_type="wrapped",
            raw_script_path=self.script_path,
            icon=self.icon_path,
            pyinstaller_options=["--noconfirm"],
            streamlit_options=None,
        )

        # Ensure PyInstaller's run method is called with the correct arguments
        mock_pyinstaller_run.assert_called_once()
        args = mock_pyinstaller_run.call_args[0][0]
        self.assertIn("--noconfirm", args)
        self.assertIn("--name", args)
        self.assertIn("TestApp", args)
        self.assertIn("--add-data", args)
        self.assertIn(f"{wrapped_script}:.", args)

    @patch("streamlit_desktop_app.build.os.path.exists", return_value=False)
    def test_missing_script(self, mock_exists):
        # Test behavior when the script file is missing
        with self.assertRaises(SystemExit) as cm:
            build_executable(
                script_path="missing_script.py",
                name="TestApp",
                script_type="raw",
                icon=None,
                pyinstaller_options=None,
                streamlit_options=None,
            )
        self.assertEqual(str(cm.exception), "Error: The script 'missing_script.py' does not exist.")

    def test_invalid_script_type(self):
        # Test behavior with an invalid script type
        with self.assertRaises(SystemExit) as cm:
            build_executable(
                script_path=self.script_path,
                name="TestApp",
                script_type="invalid",
                icon=None,
                pyinstaller_options=None,
                streamlit_options=None,
            )
        self.assertEqual(str(cm.exception), "Error: Invalid script type 'invalid'. Use 'raw' or 'wrapped'.")

    def test_missing_raw_script_path(self):
        # Test behavior when raw script path is missing for wrapped scripts
        wrapped_script = os.path.join(self.temp_dir, "wrapped_script.py")
        with open(wrapped_script, "w") as f:
            f.write("print('Wrapped script running')")

        with self.assertRaises(SystemExit) as cm:
            build_executable(
                script_path=wrapped_script,
                name="TestApp",
                script_type="wrapped",
                raw_script_path=None,
                icon=None,
                pyinstaller_options=None,
                streamlit_options=None,
            )
        self.assertEqual(str(cm.exception), "Error: --raw-script-path must be provided for wrapped scripts.")


if __name__ == "__main__":
    unittest.main()
