"""Utility functions for file handling and sanitization."""

import re
from pathlib import Path


def sanitize_folder_name(name: str) -> str:
    """Sanitize a folder name to prevent path traversal and invalid characters.

    Args:
        name: The user-provided folder name.

    Returns:
        A sanitized string safe for use as a directory name.

    Raises:
        ValueError: If the name contains invalid characters or attempts path traversal.
    """
    if not name or not name.strip():
        raise ValueError("Folder name cannot be empty.")

    # Check for path separators or parent directory traversal
    if ".." in name or "/" in name or "\\" in name:
        raise ValueError("Folder name cannot contain path separators or '..'")

    # Allow alphanumeric, underscore, hyphen, space
    # Remove any other characters
    cleaned_name = re.sub(r'[<>:"/\\|?*]', "", name).strip()

    if not cleaned_name:
        raise ValueError("Folder name resulted in empty string after sanitization.")

    return cleaned_name


def get_download_path(base_dir: str, folder_name: str) -> Path:
    """Get a safe path for downloading files.

    Args:
        base_dir: The base directory (usually CWD).
        folder_name: The target subfolder name.

    Returns:
        A Path object.
    """
    safe_name = sanitize_folder_name(folder_name)
    return Path(base_dir) / safe_name
