"""Utility functions for file handling and sanitization."""

import datetime
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


def format_iso_date(date_str: str) -> str:
    """Parse various date formats and return YYYY-MM-DD or YYYY."""
    if not date_str:
        return "UnknownDate"
    
    # Try parsing common formats
    formats = [
        "%d-%b-%Y %H:%M:%S",  # General announcements: "17-Jan-2026 17:36:35"
        "%d-%b-%Y %H:%M",
        "%d-%b-%Y",
        "%d_%b_%Y",  # Screener credit rating
        "%Y",        # Annual reports target year
    ]
    
    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(date_str, fmt)
            if fmt == "%Y":
                return dt.strftime("%Y") 
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
            
    # Screener specific edge case like "4_Jul_from_icra"
    if "_from_" in date_str:
        clean_date = date_str.split("_from_")[0] # "4_Jul"
        return clean_date.replace("_", "-")

    safe_str = re.sub(r'[\\/*?:"<>|]', "", str(date_str))
    return safe_str.replace(" ", "_")


def generate_standard_filename(temporal_str: str, shorthand: str) -> str:
    """Generate filename base based on temporal info and shorthand.
    
    Args:
        temporal_str: The extracted date string to parse.
        shorthand: The shorthand for the category (e.g., 'AR', 'Transcript').
        
    Returns:
        The standardized filename prefix like '2024_AR'.
    """
    iso_date = format_iso_date(temporal_str)
    
    return f"{iso_date}_{shorthand}"

