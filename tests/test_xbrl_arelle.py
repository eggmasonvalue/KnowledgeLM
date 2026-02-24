import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import json

from knowledgelm.core.xbrl_harvester import NSEXBRLHarvester
from knowledgelm.core.taxonomy_manager import TaxonomyManager
from knowledgelm.data.nse_adapter import NSEAdapter

@pytest.fixture
def mock_taxonomy_manager():
    with patch('knowledgelm.core.taxonomy_manager.TaxonomyManager') as MockTM:
        tm_instance = MockTM.return_value
        tm_instance.get_taxonomy_dir.return_value = Path("/tmp/mock_taxonomy")
        tm_instance._has_xsd.return_value = True
        yield tm_instance

@pytest.fixture
def mock_adapter():
    mock = MagicMock(spec=NSEAdapter)
    mock.nse = MagicMock()
    mock.nse.base_url = "https://www.nseindia.com/api"
    return mock

@pytest.fixture
def harvester(mock_taxonomy_manager, mock_adapter):
    # Initialize with mock adapter
    # TaxonomyManager is instantiated inside __init__, so we patch the class
    with patch('knowledgelm.core.xbrl_harvester.TaxonomyManager', return_value=mock_taxonomy_manager):
        return NSEXBRLHarvester(nse_adapter=mock_adapter)

def test_init(harvester):
    assert harvester.adapter is not None
    assert harvester.adapter.nse.base_url == "https://www.nseindia.com/api"

def test_get_announcements_by_type_success(harvester, mock_adapter):
    # Mock fetch_json response
    expected_data = [{"appId": "123", "attachment": "http://example.com/file.xml"}]
    mock_adapter.fetch_json.return_value = expected_data

    result = harvester.get_announcements_by_type("INFY", "Reg30")
    assert len(result) == 1
    assert result[0]["appId"] == "123"

    mock_adapter.fetch_json.assert_called_once()

def test_parse_xbrl_no_url(harvester):
    assert harvester.parse_xbrl(None, "Reg30") == {}
    assert harvester.parse_xbrl("", "Reg30") == {}

@patch('knowledgelm.core.xbrl_harvester.Cntlr')
def test_parse_xbrl_arelle_success(mock_cntlr_cls, harvester, mock_adapter):
    # Mock Arelle
    mock_cntlr = MagicMock()
    mock_cntlr_cls.Cntlr.return_value = mock_cntlr

    mock_model_xbrl = MagicMock()
    mock_cntlr.modelManager.load.return_value = mock_model_xbrl

    # Mock Facts
    fact1 = MagicMock()
    fact1.qname = "ns:Concept1"
    fact1.value = "Value1"
    fact1.concept.label.return_value = "Label 1"

    fact2 = MagicMock()
    fact2.qname = "ns:Concept2"
    fact2.value = "Value2"
    fact2.concept.label.return_value = None

    mock_model_xbrl.facts = [fact1, fact2]

    # Mock download_document success
    mock_adapter.download_document.return_value = True

    with patch('builtins.open', MagicMock()) as mock_open, \
         patch('knowledgelm.core.xbrl_harvester.Path.glob', return_value=[Path("/tmp/mock.xml")]), \
         patch('shutil.move') as mock_move, \
         patch('knowledgelm.core.xbrl_harvester.tempfile.TemporaryDirectory') as mock_temp:

        # Mock temp dir context manager
        mock_temp_path = Path("/tmp/mock_dir")
        mock_temp.return_value.__enter__.return_value = str(mock_temp_path)

        # Run
        result = harvester.parse_xbrl("http://example.com/file.xml", "Reg30")

        assert result["Label 1"] == "Value1"
        assert "ns:Concept2" in result or result.get("ns:Concept2") == "Value2"

def test_fallback_internal_api(harvester, mock_adapter):
    # Mock fallback internal API response
    app_id = "12345"
    type_code = "Reg30"

    expected_data = {"RawKey": "RawValue"}
    mock_adapter.fetch_json.return_value = expected_data

    result = harvester._fallback_internal_api(app_id, type_code)

    assert result == expected_data

    # Check if correct URL was called
    mock_adapter.fetch_json.assert_called_with(
        "https://www.nseindia.com/api/XBRL-announcements",
        {"type": type_code, "appId": app_id}
    )
