import os
import requests
import socket
import sys
import unittest
from unittest.mock import patch, MagicMock, call
from streamlit_desktop_app.core import (
    find_free_port,
    run_streamlit,
    wait_for_server,
    start_desktop_app,
)


class TestCore(unittest.TestCase):
    @patch("socket.socket")
    def test_find_free_port(self, mock_socket):
        # Mock socket behavior
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        mock_socket_instance.getsockname.return_value = ("127.0.0.1", 12345)

        # Use the actual constants from the socket module
        SOL_SOCKET = socket.SOL_SOCKET
        SO_REUSEADDR = socket.SO_REUSEADDR

        port = find_free_port()
        self.assertEqual(port, 12345)
        mock_socket_instance.bind.assert_called_once()
        mock_socket_instance.setsockopt.assert_called_once_with(SOL_SOCKET, SO_REUSEADDR, 1)


    @patch("streamlit.web.cli.main")  # Mock Streamlit CLI entry point
    def test_run_streamlit(self, mock_stcli_main):
        script_path = "test_script.py"
        options = {"theme.base": "dark", "server.headless": "true"}

        # Expected arguments
        expected_argv = [
            "streamlit",
            "run",
            script_path,
            "--theme.base=dark",
            "--server.headless=true",
        ]

        # Patch sys.argv explicitly for this test
        with patch.object(sys, "argv", expected_argv):
            run_streamlit(script_path, options)
            # Validate sys.argv is correctly set during the function
            self.assertEqual(sys.argv, expected_argv)

        # Validate the CLI was called
        mock_stcli_main.assert_called_once()


    @patch("time.sleep")
    @patch("streamlit_desktop_app.core.requests.get")
    def test_wait_for_server_success(self, mock_requests_get, mock_sleep):
        # Simulate successful server start
        mock_requests_get.return_value.status_code = 200

        try:
            wait_for_server(12345)
        except TimeoutError:
            self.fail("wait_for_server raised TimeoutError unexpectedly!")
        mock_requests_get.assert_called_with("http://localhost:12345")

    @patch("time.sleep")
    @patch("streamlit_desktop_app.core.requests.get")
    def test_wait_for_server_timeout(self, mock_requests_get, mock_sleep):
        # Simulate server failing to start
        mock_requests_get.side_effect = requests.ConnectionError

        with self.assertRaises(TimeoutError):
            wait_for_server(12345, timeout=1)  # Short timeout for testing
        self.assertGreaterEqual(mock_sleep.call_count, 1)

    @patch("streamlit_desktop_app.core.webview")
    @patch("streamlit_desktop_app.core.wait_for_server")
    @patch("streamlit_desktop_app.core.multiprocessing.Process")
    @patch("streamlit_desktop_app.core.find_free_port", return_value=12345)
    def test_start_desktop_app(
        self, mock_find_free_port, mock_process, mock_wait_for_server, mock_webview
    ):
        # Mock subprocess and webview behavior
        mock_process_instance = MagicMock()
        mock_process.return_value = mock_process_instance

        script_path = os.path.join(os.path.dirname(__file__), "test_script.py")
        title = "Test App"
        options = {"theme.base": "dark"}

        start_desktop_app(
            script_path=script_path,
            title=title,
            width=800,
            height=600,
            options=options,
        )

        # Assertions for process and server behavior
        mock_find_free_port.assert_called_once()
        mock_process.assert_called_once_with(
            target=run_streamlit,
            args=(script_path, {
                "server.address": "localhost",
                "server.port": "12345",
                "server.headless": "true",
                "global.developmentMode": "false",
                "theme.base": "dark",
            }),
        )
        mock_process_instance.start.assert_called_once()
        mock_wait_for_server.assert_called_once_with(12345)

        # Assertions for webview behavior
        mock_webview.create_window.assert_called_once_with(
            title, "http://localhost:12345", width=800, height=600
        )
        mock_webview.start.assert_called_once()

        # Ensure the process is terminated
        mock_process_instance.terminate.assert_called_once()
        mock_process_instance.join.assert_called_once()


if __name__ == "__main__":
    unittest.main()
