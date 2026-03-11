import io
import zipfile
import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# Mock external dependencies
mock_nse_module = MagicMock()
sys.modules["nse"] = mock_nse_module
sys.modules["arelle"] = MagicMock()
sys.modules["arelle.ModelXbrl"] = MagicMock()
sys.modules["arelle.ViewFileFactList"] = MagicMock()

from knowledgelm.data.nse_adapter import NSEAdapter

def test_safe_extract_prevents_path_traversal(tmp_path):
    """Test that _safe_extract prevents Zip Slip (path traversal)."""
    adapter = NSEAdapter(tmp_path / "downloads")

    extract_dir = tmp_path / "extract"
    extract_dir.mkdir()

    # Create a malicious ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        # Malicious entry 1: Parent directory traversal
        zf.writestr("../evil.txt", "malicious content")
        # Malicious entry 2: Absolute path (if allowed by zipfile)
        zf.writestr("/tmp/evil_abs.txt", "malicious content abs")
        # Valid entry
        zf.writestr("good.txt", "safe content")

    zip_buffer.seek(0)
    with zipfile.ZipFile(zip_buffer, "r") as z:
        adapter._safe_extract(z, extract_dir)

    # Verify results
    assert (extract_dir / "good.txt").exists()
    assert (extract_dir / "good.txt").read_text() == "safe content"

    # Verify that malicious files were NOT created outside or inside under the wrong name
    assert not (tmp_path / "evil.txt").exists()
    assert not (extract_dir / "../evil.txt").resolve().exists() or (extract_dir / "../evil.txt").resolve() == extract_dir / "evil.txt"

    # Note: zipfile might strip leading slashes or ../ itself depending on version,
    # but our _safe_extract should catch it regardless.
    # If it was stripped and put INSIDE extract_dir, that's technically safe but we want to be sure it's not OUTSIDE.

    evil_outside = tmp_path / "evil.txt"
    assert not evil_outside.exists()

def test_download_and_extract_uses_safe_extract(tmp_path, monkeypatch):
    """Test that download_and_extract uses the secure extraction logic."""
    adapter = NSEAdapter(tmp_path / "downloads")

    # Create a malicious ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("../evil_download.txt", "malicious download")
        zf.writestr("ok.txt", "ok")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = zip_buffer.getvalue()

    adapter.nse._req = MagicMock(return_value=mock_response)

    extract_dir = tmp_path / "extract_download"
    extract_dir.mkdir()

    url = "http://example.com/file.zip"
    result = adapter.download_and_extract(url, extract_dir)

    assert result is True
    assert (extract_dir / "ok.txt").exists()
    assert not (tmp_path / "evil_download.txt").exists()
