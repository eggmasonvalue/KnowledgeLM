import sys
from unittest.mock import MagicMock

import pytest

# --- Mock external dependencies before imports ---

# Mock 'nse' library (not installed)
mock_nse_module = MagicMock()
sys.modules["nse"] = mock_nse_module

# Mock 'nse_xbrl_parser' library (not installed)
mock_nse_xbrl_parser = MagicMock()
sys.modules["nse_xbrl_parser"] = mock_nse_xbrl_parser

# Mock 'markitdown' library
mock_markitdown = MagicMock()
sys.modules["markitdown"] = mock_markitdown

# Mock 'urllib3' library
mock_urllib3 = MagicMock()
sys.modules["urllib3"] = mock_urllib3

# Mock 'requests' library
sys.modules["requests"] = MagicMock()

# Mock 'bs4' library
sys.modules["bs4"] = MagicMock()

# Mock 'selenium' library
sys.modules["selenium"] = MagicMock()
sys.modules["selenium.webdriver"] = MagicMock()
sys.modules["selenium.webdriver.chrome"] = MagicMock()
sys.modules["selenium.webdriver.chrome.options"] = MagicMock()
sys.modules["selenium.webdriver.chrome.service"] = MagicMock()
sys.modules["selenium.webdriver.common"] = MagicMock()
sys.modules["selenium.webdriver.common.print_page_options"] = MagicMock()

# Mock 'click' library
sys.modules["click"] = MagicMock()
sys.modules["click.testing"] = MagicMock()

# We have installed requests, bs4, selenium, click. So we don't need to mock them in sys.modules.

@pytest.fixture
def mock_nse(monkeypatch):
    """Mock the NSE class from the nse library."""
    mock_nse_instance = MagicMock()
    # Mock the NSE class constructor to return our instance
    mock_nse_module.NSE.return_value = mock_nse_instance
    return mock_nse_instance

@pytest.fixture
def mock_requests(monkeypatch):
    """Mock requests.get and requests.Session."""
    # Since requests is installed, we can patch it using monkeypatch
    import requests

    mock_get = MagicMock()
    monkeypatch.setattr(requests, "get", mock_get)

    mock_session = MagicMock()
    # Mock the Session class
    mock_session_cls = MagicMock(return_value=mock_session)
    monkeypatch.setattr(requests, "Session", mock_session_cls)

    return mock_get, mock_session

@pytest.fixture
def mock_selenium_driver(monkeypatch):
    """Mock Selenium WebDriver."""
    # Since selenium is installed, we can patch it using monkeypatch
    import selenium.webdriver

    mock_driver = MagicMock()
    mock_chrome = MagicMock(return_value=mock_driver)

    monkeypatch.setattr(selenium.webdriver, "Chrome", mock_chrome)

    return mock_chrome, mock_driver
