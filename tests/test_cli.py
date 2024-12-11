import pytest
from unittest.mock import patch
from streamlit_desktop_app.cli import main


@pytest.fixture
def mock_build_executable():
    """Mock the build_executable function in the build module."""
    with patch("streamlit_desktop_app.cli.build_executable") as mock:
        yield mock


@pytest.mark.parametrize(
    "args, expected_call",
    [
        (
            ["streamlit-desktop-app", "build", "tests/example.py", "--name", "MyApp"],
            {"script_path": "tests/example.py", "name": "MyApp", "icon": None, "pyinstaller_options": [], "streamlit_options": []},
        ),
        (
            ["streamlit-desktop-app", "build", "tests/example.py", "--name", "MyApp", "--icon", "app_icon.ico"],
            {"script_path": "tests/example.py", "name": "MyApp", "icon": "app_icon.ico", "pyinstaller_options": [], "streamlit_options": []},
        ),
        (
            [
                "streamlit-desktop-app",
                "build",
                "tests/example.py",
                "--name",
                "MyApp",
                "--pyinstaller-options",
                "--onefile",
                "--noconfirm",
                "--streamlit-options",
                "--theme.base=dark",
            ],
            {"script_path": "tests/example.py", "name": "MyApp", "icon": None, "pyinstaller_options": ["--onefile", "--noconfirm"], "streamlit_options": ["--theme.base=dark"]},
        ),
    ],
)
def test_build_command(mock_build_executable, args, expected_call):
    """Test the 'build' subcommand with various argument combinations."""
    with patch("sys.argv", args):
        main()
    mock_build_executable.assert_called_once_with(**expected_call)


def test_missing_required_arguments():
    """Test missing required arguments for the 'build' subcommand."""
    args = ["streamlit-desktop-app", "build", "--name", "MyApp"]
    with patch("sys.argv", args):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 2  # argparse exits with code 2 for missing arguments


def test_invalid_command():
    """Test an invalid command for the CLI."""
    args = ["streamlit-desktop-app", "invalid_command"]
    with patch("sys.argv", args):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 2  # argparse exits with code 2 for invalid commands
