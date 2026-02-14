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
