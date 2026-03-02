import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from knowledgelm.utils.file_utils import get_download_path, sanitize_folder_name
from knowledgelm.utils.log_utils import StreamToLogger, redirect_output_to_logger


def test_sanitize_folder_name_valid():
    """Test sanitization with valid folder names."""
    assert sanitize_folder_name("valid_name") == "valid_name"
    assert sanitize_folder_name("valid name") == "valid name"
    assert sanitize_folder_name("valid-name") == "valid-name"
    assert sanitize_folder_name("valid_name_123") == "valid_name_123"


def test_sanitize_folder_name_empty():
    """Test sanitization with empty or whitespace-only names."""
    with pytest.raises(ValueError, match="Folder name cannot be empty"):
        sanitize_folder_name("")

    with pytest.raises(ValueError, match="Folder name cannot be empty"):
        sanitize_folder_name("   ")


def test_sanitize_folder_name_path_traversal():
    """Test sanitization with path traversal attempts."""
    with pytest.raises(ValueError, match="Folder name cannot contain path separators or '..'"):
        sanitize_folder_name("../parent")

    with pytest.raises(ValueError, match="Folder name cannot contain path separators or '..'"):
        sanitize_folder_name("parent/child")

    with pytest.raises(ValueError, match="Folder name cannot contain path separators or '..'"):
        sanitize_folder_name("parent\\child")


def test_sanitize_folder_name_invalid_chars():
    """Test sanitization with invalid characters."""
    # Should strip invalid chars but keep valid ones
    assert sanitize_folder_name("invalid<name>") == "invalidname"
    assert sanitize_folder_name("invalid:name") == "invalidname"
    assert sanitize_folder_name('invalid"name') == "invalidname"
    assert sanitize_folder_name("invalid|name") == "invalidname"
    assert sanitize_folder_name("invalid?name") == "invalidname"
    assert sanitize_folder_name("invalid*name") == "invalidname"


def test_sanitize_folder_name_becomes_empty():
    """Test sanitization resulting in empty string."""
    with pytest.raises(ValueError, match="Folder name resulted in empty string"):
        sanitize_folder_name('<>:"|?*')


def test_get_download_path():
    """Test get_download_path combines paths correctly."""
    base = "/tmp"
    folder = "test_folder"
    expected = Path("/tmp/test_folder")
    assert get_download_path(base, folder) == expected


def test_get_download_path_sanitizes():
    """Test get_download_path sanitizes the folder name."""
    base = "/tmp"
    folder = "test<folder>"
    expected = Path("/tmp/testfolder")
    assert get_download_path(base, folder) == expected


def test_stream_to_logger_write():
    """Test StreamToLogger writes and buffers correctly."""
    mock_logger = MagicMock()
    stream = StreamToLogger(mock_logger, level=logging.INFO)

    # Write a line with a newline
    stream.write("Hello\n")
    mock_logger.log.assert_called_once_with(logging.INFO, "Hello")
    mock_logger.log.reset_mock()

    # Write multiple lines
    stream.write("Line 1\nLine 2\n")
    assert mock_logger.log.call_count == 2
    mock_logger.log.assert_any_call(logging.INFO, "Line 1")
    mock_logger.log.assert_any_call(logging.INFO, "Line 2")
    mock_logger.log.reset_mock()

    # Write without a newline, shouldn't log yet
    stream.write("Partial")
    mock_logger.log.assert_not_called()

    # Complete the line
    stream.write(" line\n")
    mock_logger.log.assert_called_once_with(logging.INFO, "Partial line")


def test_stream_to_logger_flush():
    """Test StreamToLogger flush writes the buffer."""
    mock_logger = MagicMock()
    stream = StreamToLogger(mock_logger, level=logging.DEBUG)

    # Write without a newline
    stream.write("Buffered data")
    mock_logger.log.assert_not_called()

    # Flush should log the buffered data
    stream.flush()
    mock_logger.log.assert_called_once_with(logging.DEBUG, "Buffered data")
    assert stream.linebuf == ""


def test_stream_to_logger_custom_level():
    """Test StreamToLogger respects the severity level."""
    mock_logger = MagicMock()
    stream = StreamToLogger(mock_logger, level=logging.ERROR)

    stream.write("An error occurred\n")
    mock_logger.log.assert_called_once_with(logging.ERROR, "An error occurred")


def test_redirect_output_to_logger_happy_path():
    """Test redirect_output_to_logger intercepts stdout and stderr."""
    mock_logger = MagicMock()
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    with redirect_output_to_logger(mock_logger, level=logging.WARNING):
        # stdout and stderr should be instances of StreamToLogger
        assert isinstance(sys.stdout, StreamToLogger)
        assert isinstance(sys.stderr, StreamToLogger)

        # Write to stdout
        sys.stdout.write("stdout message\n")
        # Write to stderr
        sys.stderr.write("stderr message\n")

    # Outside the context, stdout and stderr should be restored
    assert sys.stdout is original_stdout
    assert sys.stderr is original_stderr

    # Both messages should have been logged
    assert mock_logger.log.call_count == 2
    mock_logger.log.assert_any_call(logging.WARNING, "stdout message")
    mock_logger.log.assert_any_call(logging.WARNING, "stderr message")


def test_redirect_output_to_logger_exception():
    """Test redirect_output_to_logger restores streams even on exception."""
    mock_logger = MagicMock()
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    class TestException(Exception):
        pass

    try:
        with redirect_output_to_logger(mock_logger, level=logging.INFO):
            sys.stdout.write("pre-exception stdout")
            sys.stderr.write("pre-exception stderr")
            raise TestException("Test error")
    except TestException:
        pass

    # Outside the context, stdout and stderr should be restored
    assert sys.stdout is original_stdout
    assert sys.stderr is original_stderr

    # The un-flushed buffers should be logged by finally block flush()
    assert mock_logger.log.call_count == 2
    mock_logger.log.assert_any_call(logging.INFO, "pre-exception stdout")
    mock_logger.log.assert_any_call(logging.INFO, "pre-exception stderr")
