import pytest
import sys
from unittest.mock import MagicMock
from pathlib import Path
from datetime import datetime
from knowledgelm.data.nse_adapter import NSEAdapter

# Access the mock module we set up in conftest.py
mock_nse_module = sys.modules["nse"]

def test_init(mock_nse):
    """Test initialization of NSEAdapter."""
    path = Path("foo")
    adapter = NSEAdapter(path)
    mock_nse_module.NSE.assert_called_with("foo")

def test_get_announcements_success(mock_nse):
    """Test successful retrieval of announcements."""
    adapter = NSEAdapter(Path("foo"))

    expected_data = [{"desc": "test", "attchmntFile": "http://example.com/file.pdf"}]
    mock_nse.announcements.return_value = expected_data

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 2)

    result = adapter.get_announcements("SYMBOL", start_date, end_date)

    assert result == expected_data
    mock_nse.announcements.assert_called_once_with(
        symbol="SYMBOL",
        from_date=start_date,
        to_date=end_date
    )

def test_get_announcements_error(mock_nse):
    """Test error handling when fetching announcements."""
    adapter = NSEAdapter(Path("foo"))
    mock_nse.announcements.side_effect = Exception("Network error")

    result = adapter.get_announcements("SYMBOL", datetime(2023, 1, 1), datetime(2023, 1, 2))

    assert result == []

def test_get_annual_reports_success(mock_nse):
    """Test successful retrieval of annual reports."""
    adapter = NSEAdapter(Path("foo"))
    expected_data = {"2023": [{"url": "http://example.com/ar.pdf"}]}
    mock_nse.annual_reports.return_value = expected_data

    result = adapter.get_annual_reports("SYMBOL")
    assert result == expected_data
    mock_nse.annual_reports.assert_called_once_with("SYMBOL")

def test_get_annual_reports_error(mock_nse):
    """Test error handling when fetching annual reports."""
    adapter = NSEAdapter(Path("foo"))
    mock_nse.annual_reports.side_effect = Exception("Network error")

    result = adapter.get_annual_reports("SYMBOL")
    assert result == {}

def test_download_document_success(mock_nse):
    """Test successful document download."""
    adapter = NSEAdapter(Path("foo"))
    url = "http://example.com/doc.pdf"
    dest = Path("bar")

    result = adapter.download_document(url, dest)

    assert result is True
    mock_nse.download_document.assert_called_once_with(url, dest)

def test_download_document_error(mock_nse):
    """Test error handling during document download."""
    adapter = NSEAdapter(Path("foo"))
    mock_nse.download_document.side_effect = Exception("Download failed")

    result = adapter.download_document("http://example.com/doc.pdf", Path("bar"))

    assert result is False

def test_validate_symbol_valid(mock_nse):
    """Test validation of a valid symbol."""
    adapter = NSEAdapter(Path("foo"))
    mock_nse.equityQuote.return_value = {"priceInfo": {}}

    assert adapter.validate_symbol("VALID") is True
    mock_nse.equityQuote.assert_called_once_with("VALID")

def test_validate_symbol_invalid_exception(mock_nse):
    """Test validation of an invalid symbol (exception raised)."""
    adapter = NSEAdapter(Path("foo"))
    mock_nse.equityQuote.side_effect = Exception("Invalid symbol")

    assert adapter.validate_symbol("INVALID") is False

def test_validate_symbol_invalid_empty(mock_nse):
    """Test validation of an invalid symbol (empty response)."""
    adapter = NSEAdapter(Path("foo"))
    mock_nse.equityQuote.return_value = {}

    assert adapter.validate_symbol("INVALID") is False

def test_download_and_extract_success(mock_nse):
    """Test successful download and extraction."""
    adapter = NSEAdapter(Path("foo"))
    url = "http://example.com/doc.zip"
    dest = Path("bar")

    result = adapter.download_and_extract(url, dest)

    assert result is True
    mock_nse.download_document.assert_called_once_with(url, dest)

def test_download_and_extract_error(mock_nse):
    """Test error handling during download and extraction."""
    adapter = NSEAdapter(Path("foo"))
    mock_nse.download_document.side_effect = Exception("Download failed")

    result = adapter.download_and_extract("http://example.com/doc.zip", Path("bar"))

    assert result is False

def test_get_issue_documents_success(mock_nse):
    """Test successful retrieval of issue documents."""
    adapter = NSEAdapter(Path("foo"))
    expected_data = [{"symbol": "SYMBOL"}]

    # Mock the internal _req method of nse instance
    mock_response = MagicMock()
    mock_response.json.return_value = expected_data
    mock_nse._req.return_value = mock_response
    mock_nse.base_url = "http://base.url"

    result = adapter.get_issue_documents("/api/path", {"param": "val"})

    assert result == expected_data
    mock_nse._req.assert_called_with("http://base.url/api/path", params={"param": "val"})

def test_get_issue_documents_error(mock_nse):
    """Test error handling when fetching issue documents."""
    adapter = NSEAdapter(Path("foo"))
    mock_nse._req.side_effect = Exception("Network error")
    mock_nse.base_url = "http://base.url"

    result = adapter.get_issue_documents("/api/path", {})

    assert result == []

def test_get_company_name_success(mock_nse):
    """Test successful retrieval of company name."""
    adapter = NSEAdapter(Path("foo"))
    mock_nse.equityMetaInfo.return_value = {"companyName": "Test Company Ltd"}

    result = adapter.get_company_name("SYMBOL")

    assert result == "Test Company Ltd"
    mock_nse.equityMetaInfo.assert_called_with("SYMBOL")

def test_get_company_name_error(mock_nse):
    """Test error handling when fetching company name."""
    adapter = NSEAdapter(Path("foo"))
    mock_nse.equityMetaInfo.side_effect = Exception("Network error")

    result = adapter.get_company_name("SYMBOL")

    assert result == ""
