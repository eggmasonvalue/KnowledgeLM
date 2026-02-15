import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch
from knowledgelm.core.service import KnowledgeService

# Helper for dates
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2023, 1, 31)

def test_service_init():
    """Test service initialization."""
    service = KnowledgeService("/base")
    assert service.base_path == Path("/base")

@patch("knowledgelm.core.service.get_download_path")
def test_process_request_invalid_folder(mock_get_path):
    """Test handling of invalid folder name."""
    mock_get_path.side_effect = ValueError("Invalid folder")
    service = KnowledgeService("/tmp")

    with pytest.raises(ValueError, match="Invalid folder"):
        service.process_request(
            "SYMBOL", START_DATE, END_DATE, "invalid/folder", {}
        )

@patch("knowledgelm.core.service.NSEAdapter")
def test_process_request_invalid_symbol(mock_adapter_cls):
    """Test handling of invalid symbol."""
    mock_adapter = mock_adapter_cls.return_value
    mock_adapter.validate_symbol.return_value = False

    service = KnowledgeService("/tmp")

    with pytest.raises(ValueError, match="Symbol 'INVALID' is invalid"):
        service.process_request(
            "INVALID", START_DATE, END_DATE, "folder", {}
        )

@patch("knowledgelm.core.service.NSEAdapter")
def test_process_request_success(mock_adapter_cls):
    """Test successful request processing."""
    mock_adapter = mock_adapter_cls.return_value
    mock_adapter.validate_symbol.return_value = True
    mock_adapter.get_announcements.return_value = [
        {
            "desc": "investor presentation",
            "attchmntFile": "http://example.com/pres.pdf",
            "attchmntText": ""
        }
    ]
    mock_adapter.download_document.return_value = True

    service = KnowledgeService("/tmp")
    options = {"download_investor_presentations": True}

    announcements, counts = service.process_request(
        "SYMBOL", START_DATE, END_DATE, "folder", options
    )

    assert counts["investor presentation"] == 1
    mock_adapter.download_document.assert_called_once()

    # Check folder creation logic was called (implicitly by checking if download_document was called with correct path)
    # mock_adapter initialized with sanitized folder path
    mock_adapter_cls.assert_called()

@patch("knowledgelm.core.service.NSEAdapter")
def test_process_annual_reports(mock_adapter_cls):
    """Test annual reports processing."""
    mock_adapter = mock_adapter_cls.return_value
    mock_adapter.validate_symbol.return_value = True
    mock_adapter.get_announcements.return_value = []

    # Mock get_annual_reports
    mock_adapter.get_annual_reports.return_value = {
        "2023": [{"url": "http://example.com/ar.pdf", "toYr": "2023"}]
    }
    mock_adapter.download_document.return_value = True

    service = KnowledgeService("/tmp")
    options = {"download_annual_reports": True}

    # Test with date range match
    announcements, counts = service.process_request(
        "SYMBOL", datetime(2023, 1, 1), datetime(2023, 12, 31), "folder", options
    )
    assert counts["annual report"] == 1

    # Test with date range mismatch
    mock_adapter.download_document.reset_mock()
    announcements, counts = service.process_request(
        "SYMBOL", datetime(2020, 1, 1), datetime(2020, 12, 31), "folder", options
    )
    assert counts["annual report"] == 0

    # Test with all_mode
    mock_adapter.download_document.reset_mock()
    announcements, counts = service.process_request(
        "SYMBOL", datetime(2020, 1, 1), datetime(2020, 12, 31), "folder", options,
        annual_reports_all_mode=True
    )
    assert counts["annual report"] == 1

@patch("knowledgelm.core.service.NSEAdapter")
@patch("knowledgelm.core.service.download_credit_ratings_from_screener")
def test_process_credit_ratings_screener_success(mock_screener_dl, mock_adapter_cls):
    """Test credit ratings using Screener (primary source)."""
    mock_adapter = mock_adapter_cls.return_value
    mock_adapter.validate_symbol.return_value = True
    mock_adapter.get_announcements.return_value = []

    mock_screener_dl.return_value = 5 # Downloaded 5 from screener

    service = KnowledgeService("/tmp")
    options = {"download_credit_rating": True}

    announcements, counts = service.process_request(
        "SYMBOL", START_DATE, END_DATE, "folder", options
    )

    assert counts["credit rating"] == 5
    mock_screener_dl.assert_called_once()
    mock_adapter.download_document.assert_not_called()

@patch("knowledgelm.core.service.NSEAdapter")
@patch("knowledgelm.core.service.download_credit_ratings_from_screener")
def test_process_credit_ratings_fallback(mock_screener_dl, mock_adapter_cls):
    """Test credit ratings fallback to NSE."""
    mock_adapter = mock_adapter_cls.return_value
    mock_adapter.validate_symbol.return_value = True
    mock_adapter.get_announcements.return_value = [
        {
            "desc": "credit rating",
            "attchmntFile": "http://example.com/rating.pdf",
            "attchmntText": ""
        }
    ]
    mock_adapter.download_document.return_value = True

    mock_screener_dl.return_value = 0 # Screener failed or empty

    service = KnowledgeService("/tmp")
    options = {"download_credit_rating": True}

    announcements, counts = service.process_request(
        "SYMBOL", START_DATE, END_DATE, "folder", options
    )

    assert counts["credit rating"] == 1
    mock_screener_dl.assert_called_once()
    mock_adapter.download_document.assert_called_once()

@patch("knowledgelm.core.service.NSEAdapter")
@patch("knowledgelm.core.service.download_credit_ratings_from_screener")
def test_process_credit_ratings_existing_file(mock_screener_dl, mock_adapter_cls):
    """Test credit ratings fallback skips existing files."""
    mock_adapter = mock_adapter_cls.return_value
    mock_adapter.validate_symbol.return_value = True
    mock_adapter.get_announcements.return_value = [
        {
            "desc": "credit rating",
            "attchmntFile": "http://example.com/rating.pdf",
            "attchmntText": ""
        }
    ]
    mock_screener_dl.return_value = 0

    service = KnowledgeService("/tmp")
    options = {"download_credit_rating": True}

    # Simulate existing file
    with patch("pathlib.Path.glob") as mock_glob:
        mock_glob.return_value = [Path("rating.pdf")]
        announcements, counts = service.process_request(
            "SYMBOL", START_DATE, END_DATE, "folder", options
        )

    assert counts["credit rating"] == 0
    mock_adapter.download_document.assert_not_called()

@patch("knowledgelm.core.service.NSEAdapter")
def test_process_issue_documents(mock_adapter_cls):
    """Test issue documents processing."""
    mock_adapter = mock_adapter_cls.return_value
    mock_adapter.validate_symbol.return_value = True
    mock_adapter.get_announcements.return_value = []

    # Mock issue documents response
    mock_adapter.get_issue_documents.return_value = [
        {
            "symbol": "SYMBOL",
            "company": "Symbol Ltd",
            "fpAttach": "http://example.com/doc.zip", # for offer_documents
            "finalAttach": "http://example.com/doc.zip", # for rights_issue
            "attachFile": "http://example.com/doc.zip", # for qip_offer
            "date_attachmnt": "http://example.com/doc.zip", # for info_memorandum, scheme_document
        }
    ]
    mock_adapter.get_company_name.return_value = "Symbol Ltd"
    mock_adapter.download_and_extract.return_value = True

    service = KnowledgeService("/tmp")
    options = {"download_issue_documents": True}

    # We need to ensure ISSUE_DOCS_CONFIG is iterated.
    # Since we can't easily patch the imported constant in the function execution context without complex patching,
    # we rely on the actual config and mock the adapter's response to match one of the keys.
    # The config iterates over several types. We just need one to return data.

    announcements, counts = service.process_request(
        "SYMBOL", START_DATE, END_DATE, "folder", options
    )

    # We expect at least one successful download from the mocked response
    # Checks if any key in counts > 0
    assert any(val > 0 for val in counts.values())
    mock_adapter.get_issue_documents.assert_called()
    mock_adapter.download_and_extract.assert_called()

def test_matches_filter():
    """Test category filtering logic."""
    service = KnowledgeService("/tmp")

    # Transcripts
    item = {
        "desc": "analysts/institutional investor meet/con. call updates",
        "attchmntText": "earnings call transcript",
        "attchmntFile": "file"
    }
    assert service._matches_filter("transcripts", item)

    # Investor Presentation
    item = {"desc": "investor presentation", "attchmntFile": "file"}
    assert service._matches_filter("investor_presentations", item)

    # Press Release
    item = {"desc": "press release", "attchmntFile": "file"}
    assert service._matches_filter("press_releases", item)

    # Credit Rating
    item = {"desc": "credit rating", "attchmntFile": "file"}
    assert service._matches_filter("credit_rating", item)

    # Related Party
    item = {"desc": "related party transaction", "attchmntFile": "file"}
    assert service._matches_filter("related_party_txns", item)

    # No file
    item = {"desc": "investor presentation"}
    assert not service._matches_filter("investor_presentations", item)

    # Mismatch
    item = {"desc": "other", "attchmntFile": "file"}
    assert not service._matches_filter("investor_presentations", item)

@patch("knowledgelm.core.service.NSEAdapter")
def test_process_annual_reports_empty(mock_adapter_cls):
    """Test annual reports when no data found."""
    mock_adapter = mock_adapter_cls.return_value
    mock_adapter.validate_symbol.return_value = True
    mock_adapter.get_announcements.return_value = []
    mock_adapter.get_annual_reports.return_value = {}

    service = KnowledgeService("/tmp")
    options = {"download_annual_reports": True}

    _, counts = service.process_request(
        "SYMBOL", START_DATE, END_DATE, "folder", options
    )
    assert counts["annual report"] == 0

@patch("knowledgelm.core.service.NSEAdapter")
def test_process_annual_reports_malformed(mock_adapter_cls):
    """Test annual reports with missing fields."""
    mock_adapter = mock_adapter_cls.return_value
    mock_adapter.validate_symbol.return_value = True
    mock_adapter.get_announcements.return_value = []

    # Missing url or toYr
    mock_adapter.get_annual_reports.return_value = {
        "2023": [{"toYr": "2023"}, {"url": "http://url"}]
    }

    service = KnowledgeService("/tmp")
    options = {"download_annual_reports": True}

    _, counts = service.process_request(
        "SYMBOL", START_DATE, END_DATE, "folder", options, annual_reports_all_mode=True
    )
    assert counts["annual report"] == 0

@patch("knowledgelm.core.service.NSEAdapter")
@patch("knowledgelm.core.service.download_credit_ratings_from_screener")
def test_process_credit_ratings_missing_url(mock_screener, mock_adapter_cls):
    """Test credit ratings fallback when URL is missing."""
    mock_adapter = mock_adapter_cls.return_value
    mock_adapter.validate_symbol.return_value = True
    mock_adapter.get_announcements.return_value = [
        {"desc": "credit rating"} # No attchmntFile
    ]
    mock_screener.return_value = 0

    service = KnowledgeService("/tmp")
    options = {"download_credit_rating": True}

    _, counts = service.process_request(
        "SYMBOL", START_DATE, END_DATE, "folder", options
    )
    assert counts["credit rating"] == 0

@patch("knowledgelm.core.service.NSEAdapter")
def test_process_issue_documents_empty(mock_adapter_cls):
    """Test issue documents when API returns empty or no match."""
    mock_adapter = mock_adapter_cls.return_value
    mock_adapter.validate_symbol.return_value = True
    mock_adapter.get_announcements.return_value = []

    # Case 1: Empty response
    mock_adapter.get_issue_documents.return_value = []

    service = KnowledgeService("/tmp")
    options = {"download_issue_documents": True}

    _, counts = service.process_request("SYMBOL", START_DATE, END_DATE, "folder", options)
    assert all(v == 0 for v in counts.values())

    # Case 2: No match
    mock_adapter.get_issue_documents.return_value = [{"symbol": "OTHER", "company": "Other"}]
    mock_adapter.get_company_name.return_value = "Symbol Ltd"

    _, counts = service.process_request("SYMBOL", START_DATE, END_DATE, "folder", options)
    assert all(v == 0 for v in counts.values())

@patch("knowledgelm.core.service.NSEAdapter")
def test_process_annual_reports_invalid_year(mock_adapter_cls):
    """Test annual reports with invalid year."""
    mock_adapter = mock_adapter_cls.return_value
    mock_adapter.validate_symbol.return_value = True
    mock_adapter.get_announcements.return_value = []

    mock_adapter.get_annual_reports.return_value = {
        "2023": [{"toYr": "invalid"}, {"url": "http://url"}]
    }

    service = KnowledgeService("/tmp")
    options = {"download_annual_reports": True}

    _, counts = service.process_request(
        "SYMBOL", START_DATE, END_DATE, "folder", options, annual_reports_all_mode=True
    )
    assert counts["annual report"] == 0
