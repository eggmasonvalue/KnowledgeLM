import sys
from unittest.mock import MagicMock
import pytest

# --- Mock external dependencies before imports ---

# Mock 'nse' library (not installed)
mock_nse_module = MagicMock()
sys.modules["nse"] = mock_nse_module

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
