import json
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from knowledgelm.cli import main


def test_fetch_nse_help():
    """Test help message for fetch nse command."""
    runner = CliRunner()
    result = runner.invoke(main, ["fetch", "nse", "--help"])
    assert result.exit_code == 0
    assert "Fetch Corporate Filings and XBRL" in result.output

@patch("knowledgelm.cli.KnowledgeService")
def test_fetch_nse_success(mock_service_cls):
    """Test successful fetch nse command execution."""
    mock_service = mock_service_cls.return_value
    mock_service.process_request.return_value = ([], {"transcript": 1})

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["fetch", "nse", "SYMBOL", "--start", "2023-01-01", "--end", "2023-01-31"])

        assert result.exit_code == 0
        
        # Check JSON output on stdout
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["downloads"]["transcript"] == 1

        # Check log file for human-readable output
        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "Downloaded filings for SYMBOL" in content
        assert "transcript: 1 files" in content
        assert "JSON Result:" in content

        mock_service.process_request.assert_called()

@patch("knowledgelm.cli.KnowledgeService")
def test_fetch_nse_all_datasets(mock_service_cls):
    """Test fetch nse with all datasets (default)."""
    mock_service = mock_service_cls.return_value
    mock_service.process_request.return_value = ([], {})

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["fetch", "nse", "SYMBOL", "--start", "2023-01-01", "--end", "2023-01-31", "--datasets", "all"])
        assert result.exit_code == 0

        args = mock_service.process_request.call_args[1]
        options = args["options"]
        # Ensure all options are True
        assert all(options.values())

@patch("knowledgelm.cli.KnowledgeService")
def test_fetch_nse_invalid_date(mock_service_cls):
    """Test invalid date format error."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["fetch", "nse", "SYMBOL", "--start", "invalid", "--end", "2023-01-31"])

        assert result.exit_code != 0
        
        # Check JSON error on stdout
        data = json.loads(result.output)
        assert data["success"] is False
        assert "error" in data

        # Check log file
        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "Invalid date format" in content

@patch("knowledgelm.cli.KnowledgeService")
def test_fetch_nse_invalid_dataset(mock_service_cls):
    """Test invalid dataset input error."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["fetch", "nse", "SYMBOL", "--start", "2023-01-01", "--end", "2023-01-31", "--datasets", "invalid"])

        assert result.exit_code != 0
        
        # Check JSON error on stdout
        data = json.loads(result.output)
        assert data["success"] is False
        assert "error" in data

        # Check log file
        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "Invalid datasets" in content

@patch("knowledgelm.cli.KnowledgeService")
def test_fetch_nse_unexpected_error(mock_service_cls):
    """Test unexpected error handling during fetch nse."""
    mock_service = mock_service_cls.return_value
    mock_service.process_request.side_effect = Exception("Unexpected")

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["fetch", "nse", "SYMBOL", "--start", "2023-01-01", "--end", "2023-01-31"])

        assert result.exit_code != 0
        
        # Check JSON error on stdout
        data = json.loads(result.output)
        assert data["success"] is False
        assert "error" in data

        # Check log file
        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "Unexpected error during download" in content

def test_list_datasets():
    """Test listing datasets."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["list-datasets"])
        assert result.exit_code == 0
        
        # Check JSON on stdout
        data = json.loads(result.output)
        assert "datasets" in data
        assert "transcripts" in data["datasets"]

        # Check log file
        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "Available datasets list fetched." in content
        assert "JSON Result:" in content

@patch("knowledgelm.cli.ForumClient")
@patch("knowledgelm.cli.PDFGenerator")
@patch("knowledgelm.cli.ReferenceExtractor")
def test_fetch_vp_success(mock_extractor_cls, mock_generator_cls, mock_client_cls):
    """Test fetch vp command."""
    mock_client = mock_client_cls.return_value
    mock_client.get_full_thread.return_value = {"title": "Test", "posts": []}
    mock_client.parse_topic_url.return_value = ("slug", 123)

    mock_generator = mock_generator_cls.return_value
    mock_extractor = mock_extractor_cls.return_value
    mock_extractor.extract_references.return_value = "# References"

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["fetch", "vp", "http://url", "--symbol", "SYM"])
        assert result.exit_code == 0
        
        # Check JSON on stdout
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["title"] == "Test"

        # Check log file
        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "Successfully saved thread" in content
        assert "JSON Result:" in content

        mock_client.get_full_thread.assert_called_with("http://url")
        mock_generator.generate_thread_pdf.assert_called()

@patch("knowledgelm.cli.ForumClient")
def test_fetch_vp_error(mock_client_cls):
    """Test fetch vp command error handling."""
    mock_client = mock_client_cls.return_value
    mock_client.get_full_thread.side_effect = Exception("Fetch error")

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["fetch", "vp", "http://url"])
        assert result.exit_code != 0
        
        # Check JSON on stdout
        data = json.loads(result.output)
        assert data["success"] is False
        assert "error" in data

        # Check log file
        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "Failed to download forum thread" in content
