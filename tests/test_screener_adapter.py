import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, ANY
from knowledgelm.data.screener_adapter import (
    _get_icra_pdf_url,
    download_credit_ratings_from_screener,
    _download_with_selenium
)

def test_get_icra_pdf_url():
    """Test ICRA URL conversion."""
    url = "https://www.icra.in/Rationale/ShowRationaleReport/?Id=136064"
    expected = "https://www.icra.in/Rating/ShowRationalReportFilePdf/136064"
    assert _get_icra_pdf_url(url) == expected

    # Test with extra params
    url_extra = "https://www.icra.in/Rationale/ShowRationaleReport/?Id=136064&foo=bar"
    assert _get_icra_pdf_url(url_extra) == expected

    # Test invalid URL
    assert _get_icra_pdf_url("http://google.com") is None

def test_download_credit_ratings_network_error(mock_requests):
    """Test handling of network error when fetching screener page."""
    mock_get, _ = mock_requests
    mock_get.return_value.status_code = 404

    count = download_credit_ratings_from_screener("SYMBOL", Path("tmp"))
    assert count == 0

def test_download_credit_ratings_no_section(mock_requests):
    """Test when credit ratings section is missing."""
    mock_get, _ = mock_requests
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "<html><body><h1>No Ratings</h1></body></html>"

    count = download_credit_ratings_from_screener("SYMBOL", Path("tmp"))
    assert count == 0

@patch("builtins.open")
def test_download_credit_ratings_pdf(mock_open, mock_requests):
    """Test downloading a PDF rating directly."""
    # We need to configure the mocks to match the behavior of requests.get
    # Since we are using the fixture mock_requests which patches requests.get
    # mock_get is the mock object for requests.get
    mock_get, _ = mock_requests

    # Mock main page response
    html_content = """
    <html>
        <body>
            <div class="documents credit-ratings">
                <h3>Credit Ratings</h3>
                <ul class="list-links">
                    <li>
                        <a href="http://example.com/rating.pdf">
                            Rating update
                            <div class="ink-600 smaller">4 Jul from icra</div>
                        </a>
                    </li>
                </ul>
            </div>
        </body>
    </html>
    """

    # Configure mock_get to return different responses based on call count or args
    # But since we use same mock for all calls, we can use side_effect

    main_page_resp = MagicMock()
    main_page_resp.status_code = 200
    main_page_resp.text = html_content

    pdf_resp = MagicMock()
    pdf_resp.status_code = 200
    pdf_resp.headers = {"Content-Type": "application/pdf"}
    pdf_resp.iter_content = lambda chunk_size: [b"pdf_data"]

    mock_get.side_effect = [main_page_resp, pdf_resp]

    # Mock file writing
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    count = download_credit_ratings_from_screener("SYMBOL", Path("/tmp"))

    assert count == 1
    # Verify file was written
    mock_open.assert_called() # Check arguments if needed
    # Path should include sanitized date: 4_Jul_from_icra
    args, _ = mock_open.call_args
    assert "CreditRating-4_Jul_from_icra.pdf" in str(args[0])

@patch("builtins.open")
@patch("knowledgelm.data.screener_adapter._download_with_selenium")
def test_download_credit_ratings_html_fallback(mock_selenium_download, mock_open, mock_requests):
    """Test fallback to Selenium when content is HTML."""
    mock_get, _ = mock_requests

    html_content = """
    <html>
        <body>
            <div class="documents credit-ratings">
                <h3>Credit Ratings</h3>
                <ul class="list-links">
                    <li>
                        <a href="http://example.com/rating.html">Rating</a>
                    </li>
                </ul>
            </div>
        </body>
    </html>
    """

    main_page_resp = MagicMock()
    main_page_resp.status_code = 200
    main_page_resp.text = html_content

    html_doc_resp = MagicMock()
    html_doc_resp.status_code = 200
    html_doc_resp.headers = {"Content-Type": "text/html"}

    mock_get.side_effect = [main_page_resp, html_doc_resp]

    mock_selenium_download.return_value = True

    count = download_credit_ratings_from_screener("SYMBOL", Path("/tmp"))

    assert count == 1
    mock_selenium_download.assert_called_once()
    args, _ = mock_selenium_download.call_args
    assert args[0] == "http://example.com/rating.html"

def test_download_with_selenium_success(mock_selenium_driver, monkeypatch):
    """Test _download_with_selenium success."""
    # We need to ensure SELENIUM_AVAILABLE is True.
    # It is determined at import time. Since we mocked selenium in sys.modules before import,
    # it should be True.

    # We also need to patch open to avoid writing to disk
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_chrome, mock_driver = mock_selenium_driver

        # Mock execute_cdp_cmd to return data
        mock_driver.execute_cdp_cmd.return_value = {"data": "dGVzdA=="}

        # We need to call the function directly
        result = _download_with_selenium("http://example.com", Path("/tmp/output.pdf"))

        assert result is True
        mock_driver.get.assert_called_with("http://example.com")
        mock_driver.execute_cdp_cmd.assert_called_with("Page.printToPDF", ANY)
        mock_driver.quit.assert_called_once()

def test_download_with_selenium_failure(mock_selenium_driver):
    """Test _download_with_selenium failure."""
    mock_chrome, mock_driver = mock_selenium_driver
    mock_driver.get.side_effect = Exception("Selenium error")

    result = _download_with_selenium("http://example.com", Path("/tmp/output.pdf"))

    assert result is False
    mock_driver.quit.assert_called_once()
