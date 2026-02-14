import pytest
from pathlib import Path
from knowledgelm.utils.file_utils import sanitize_folder_name, get_download_path

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
    assert sanitize_folder_name("invalid\"name") == "invalidname"
    assert sanitize_folder_name("invalid|name") == "invalidname"
    assert sanitize_folder_name("invalid?name") == "invalidname"
    assert sanitize_folder_name("invalid*name") == "invalidname"

def test_sanitize_folder_name_becomes_empty():
    """Test sanitization resulting in empty string."""
    with pytest.raises(ValueError, match="Folder name resulted in empty string"):
        sanitize_folder_name("<>:\"|?*")

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
