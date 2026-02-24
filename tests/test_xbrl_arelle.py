import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import json

from knowledgelm.core.xbrl_harvester import NSEXBRLHarvester
from knowledgelm.core.taxonomy_manager import TaxonomyManager

@pytest.fixture
def mock_taxonomy_manager():
    with patch('knowledgelm.core.taxonomy_manager.TaxonomyManager') as MockTM:
        tm_instance = MockTM.return_value
        # Default behavior: return a dummy path
        tm_instance.get_taxonomy_dir.return_value = Path("/tmp/mock_taxonomy")
        tm_instance._has_xsd.return_value = True
        yield tm_instance

@pytest.fixture
def harvester(mock_taxonomy_manager):
    with patch('knowledgelm.core.xbrl_harvester.TaxonomyManager', return_value=mock_taxonomy_manager):
        return NSEXBRLHarvester()

def test_init(harvester):
    assert harvester.base_url == "https://www.nseindia.com/api"
    assert harvester.session is not None

def test_get_announcements_by_type_success(harvester):
    # Mock the session.get response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"appId": "123", "attachment": "http://example.com/file.xml"}]

    harvester.session.get = MagicMock(return_value=mock_response)

    result = harvester.get_announcements_by_type("INFY", "Reg30")
    assert len(result) == 1
    assert result[0]["appId"] == "123"

def test_parse_xbrl_no_url(harvester):
    assert harvester.parse_xbrl(None, "Reg30") == {}
    assert harvester.parse_xbrl("", "Reg30") == {}

@patch('knowledgelm.core.xbrl_harvester.Cntlr')
def test_parse_xbrl_arelle_success(mock_cntlr_cls, harvester):
    # Mock Arelle Controller and ModelXbrl
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
    fact2.concept.label.return_value = None # Should fallback to QName or verbose

    mock_model_xbrl.facts = [fact1, fact2]

    # Mock download
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_content = MagicMock(return_value=[b"<xml>content</xml>"])
    mock_response.content = b"<xml>content</xml>"
    harvester.session.get = MagicMock(return_value=mock_response)

    # Run
    result = harvester.parse_xbrl("http://example.com/file.xml", "Reg30")

    assert result["Label 1"] == "Value1"
    # Logic for fact2 label fallback depends on implementation details
    assert "ns:Concept2" in result or result.get("ns:Concept2") == "Value2"

def test_fallback_internal_api(harvester):
    # Mock fallback internal API response
    app_id = "12345"
    type_code = "Reg30"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"RawKey": "RawValue"}

    harvester.session.get = MagicMock(return_value=mock_response)

    result = harvester._fallback_internal_api(app_id, type_code)

    assert result == {"RawKey": "RawValue"}

    # Check if correct URL was called
    harvester.session.get.assert_called_with(
        "https://www.nseindia.com/api/XBRL-announcements",
        params={"type": type_code, "appId": app_id},
        timeout=10
    )
