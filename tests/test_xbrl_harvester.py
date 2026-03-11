from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from knowledgelm.core.xbrl_harvester import NSEXBRLHarvester
from knowledgelm.data.nse_adapter import NSEAdapter

@pytest.fixture
def mock_adapter():
    """Mock NSEAdapter."""
    adapter = MagicMock(spec=NSEAdapter)
    adapter.nse = MagicMock()
    adapter.nse.base_url = "http://test.nse.com"
    return adapter

@pytest.fixture
def harvester(mock_adapter):
    """NSEXBRLHarvester instance with mocked adapter."""
    return NSEXBRLHarvester(nse_adapter=mock_adapter)

def test_init_with_adapter(mock_adapter):
    """Test initialization with a provided NSEAdapter."""
    harvester = NSEXBRLHarvester(nse_adapter=mock_adapter)
    assert harvester.adapter == mock_adapter


@patch("knowledgelm.core.xbrl_harvester.NSEAdapter")
@patch("knowledgelm.core.xbrl_harvester.tempfile.gettempdir")
def test_init_without_adapter(mock_gettempdir, mock_adapter_class):
    """Test initialization without providing an NSEAdapter."""
    mock_gettempdir.return_value = "/tmp"
    harvester = NSEXBRLHarvester()
    mock_adapter_class.assert_called_once_with(Path("/tmp"))
    assert harvester.adapter == mock_adapter_class.return_value


def test_get_announcements_by_type_success(harvester, mock_adapter):
    """Test successful announcement fetching."""
    mock_adapter.fetch_json.return_value = [{"appId": "123", "attachment": "http://test.com"}]
    result = harvester.get_announcements_by_type("SYMBOL", "Reg30", "01-01-2023", "31-01-2023")

    assert result == [{"appId": "123", "attachment": "http://test.com"}]
    mock_adapter.fetch_json.assert_called_once_with(
        "http://test.nse.com/XBRL-announcements",
        {"index": "equities", "symbol": "SYMBOL", "type": "Reg30", "from_date": "01-01-2023", "to_date": "31-01-2023"}
    )


def test_get_announcements_by_type_empty(harvester, mock_adapter):
    """Test announcement fetching with no results."""
    mock_adapter.fetch_json.return_value = None
    result = harvester.get_announcements_by_type("SYMBOL", "Reg30")

    assert result == []


def test_fallback_internal_api_success(harvester, mock_adapter):
    """Test successful internal API fallback."""
    expected_data = {"fact1": "value1"}
    mock_adapter.fetch_json.return_value = expected_data
    result = harvester._fallback_internal_api("app123", "Reg30")

    assert result == expected_data
    mock_adapter.fetch_json.assert_called_with(
        "http://test.nse.com/XBRL-announcements",
        {"type": "Reg30", "appId": "app123"}
    )


def test_fallback_internal_api_failure(harvester, mock_adapter):
    """Test internal API fallback failure."""
    mock_adapter.fetch_json.return_value = None
    result = harvester._fallback_internal_api("app123", "Reg30")

    assert result == {}


def test_parse_xbrl_no_url(harvester, mock_adapter):
    """Test parse_xbrl with no URL, triggering fallback."""
    expected_data = {"fallback": "data"}
    mock_adapter.fetch_json.return_value = expected_data
    result = harvester.parse_xbrl(None, "Reg30", app_id="app123")

    assert result == expected_data


def test_parse_xbrl_download_fail(harvester, mock_adapter):
    """Test parse_xbrl when download fails, triggering fallback."""
    mock_adapter.download_and_extract.return_value = False
    expected_data = {"fallback": "data"}
    mock_adapter.fetch_json.return_value = expected_data
    result = harvester.parse_xbrl("http://test.com/xbrl.zip", "Reg30", app_id="app123")

    assert result == expected_data


@patch("knowledgelm.core.xbrl_harvester.time.sleep")
@patch("knowledgelm.core.xbrl_harvester.NSEXBRLHarvester.parse_xbrl")
@patch("knowledgelm.core.xbrl_harvester.NSEXBRLHarvester.get_announcements_by_type")
def test_harvest_xbrl_success(mock_get_ann, mock_parse, mock_sleep, harvester):
    """Test successful harvest_xbrl path."""
    mock_get_ann.return_value = [{"appId": "123", "attachment": "http://test.com"}]
    mock_parse.return_value = {"fact": "value"}

    # Test with specific type
    result = harvester.harvest_xbrl("SYMBOL", types=["Reg30"])

    assert "Reg30" in result
    assert result["Reg30"][0]["xbrl_data"] == {"fact": "value"}
    mock_get_ann.assert_called_with("SYMBOL", "Reg30", None, None)
    mock_sleep.assert_called_once_with(0.2)


@patch("knowledgelm.core.xbrl_harvester.NSEXBRLHarvester.get_announcements_by_type")
def test_harvest_xbrl_no_announcements(mock_get_ann, harvester):
    """Test harvest_xbrl when no announcements are found."""
    mock_get_ann.return_value = []
    result = harvester.harvest_xbrl("SYMBOL", types=["Reg30"])

    assert result == {}


def test_harvest_xbrl_invalid_types(harvester):
    """Test harvest_xbrl with invalid types."""
    result = harvester.harvest_xbrl("SYMBOL", types=["InvalidType"])
    assert result == {}


@patch("knowledgelm.core.xbrl_harvester.Path.rglob")
def test_parse_xbrl_no_xml(mock_rglob, harvester, mock_adapter):
    """Test parse_xbrl when no XML files are found, triggering fallback."""
    mock_adapter.download_and_extract.return_value = True
    mock_rglob.return_value = []
    expected_data = {"fallback": "data"}
    mock_adapter.fetch_json.return_value = expected_data
    result = harvester.parse_xbrl("http://test.com/xbrl.zip", "Reg30", app_id="app123")

    assert result == expected_data


@patch("knowledgelm.core.xbrl_harvester.parse_xbrl_file")
@patch("knowledgelm.core.xbrl_harvester.Path.rglob")
def test_parse_xbrl_success(mock_rglob, mock_parse_file, harvester, mock_adapter):
    """Test successful parse_xbrl path."""
    mock_adapter.download_and_extract.return_value = True
    mock_xml = MagicMock(spec=Path)
    mock_xml.name = "actual_instance.xml"
    mock_xml.relative_to.return_value = Path("actual_instance.xml")
    mock_rglob.return_value = [mock_xml]

    expected_data = {"fact": "value"}
    mock_parse_file.return_value = expected_data

    result = harvester.parse_xbrl("http://test.com/xbrl.zip", "Reg30")

    assert result == expected_data
    mock_parse_file.assert_called_once_with(mock_xml)


def test_parse_xbrl_exception_triggers_fallback(harvester, mock_adapter):
    """Test parse_xbrl catches exceptions and triggers fallback."""
    mock_adapter.download_and_extract.side_effect = Exception("Crash")
    expected_data = {"fallback": "data"}
    mock_adapter.fetch_json.return_value = expected_data
    result = harvester.parse_xbrl("http://test.com/xbrl.zip", "Reg30", app_id="app123")

    assert result == expected_data


def test_get_announcements_by_type_unexpected_format(harvester, mock_adapter):
    """Test announcement fetching with unexpected response format."""
    mock_adapter.fetch_json.return_value = {"error": "some error"}
    result = harvester.get_announcements_by_type("SYMBOL", "Reg30")

    assert result == []
