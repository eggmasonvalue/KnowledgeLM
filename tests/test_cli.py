import pytest
import json
import logging
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from knowledgelm.cli import main

def test_download_help():
    """Test help message for download command."""
    runner = CliRunner()
    result = runner.invoke(main, ["download", "--help"])
    assert result.exit_code == 0
    assert "Download company filings" in result.output

@patch("knowledgelm.cli.KnowledgeService")
def test_download_success(mock_service_cls):
    """Test successful download command execution."""
    mock_service = mock_service_cls.return_value
    mock_service.process_request.return_value = ([], {"transcript": 1})

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["download", "SYMBOL", "--from", "2023-01-01", "--to", "2023-01-31"])

        assert result.exit_code == 0

        # Output goes to log file
        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "Downloaded filings for SYMBOL" in content
        assert "transcript: 1 files" in content

        mock_service.process_request.assert_called()

@patch("knowledgelm.cli.KnowledgeService")
def test_download_json(mock_service_cls):
    """Test JSON output for download command."""
    mock_service = mock_service_cls.return_value
    mock_service.process_request.return_value = ([], {"transcript": 1})

    runner = CliRunner()
    # JSON output goes to stdout (click.echo)
    result = runner.invoke(main, ["download", "SYMBOL", "--from", "2023-01-01", "--to", "2023-01-31", "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["success"] is True
    assert data["downloads"]["transcript"] == 1

@patch("knowledgelm.cli.KnowledgeService")
def test_download_invalid_date(mock_service_cls):
    """Test invalid date format."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["download", "SYMBOL", "--from", "invalid", "--to", "2023-01-31"])

        assert result.exit_code != 0

        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "Invalid date format" in content

@patch("knowledgelm.cli.KnowledgeService")
def test_download_invalid_category(mock_service_cls):
    """Test invalid category input."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["download", "SYMBOL", "--from", "2023-01-01", "--to", "2023-01-31", "--categories", "invalid"])

        assert result.exit_code != 0

        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "Invalid categories" in content

def test_list_categories():
    """Test listing categories."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["list-categories"])
        assert result.exit_code == 0

        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "Available categories:" in content
        assert "transcripts" in content

def test_list_categories_json():
    """Test listing categories as JSON."""
    runner = CliRunner()
    result = runner.invoke(main, ["list-categories", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "transcripts" in data

def test_list_files():
    """Test listing files in a directory."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        p = Path("test_dir")
        p.mkdir()
        (p / "file1.pdf").touch()
        (p / "file2.txt").touch()

        result = runner.invoke(main, ["list-files", str(p)])
        assert result.exit_code == 0

        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "file1.pdf" in content
        assert "file2.txt" in content

def test_list_files_json():
    """Test listing files as JSON."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        p = Path("test_dir")
        p.mkdir()
        (p / "file1.pdf").touch()

        result = runner.invoke(main, ["list-files", str(p), "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["file_count"] == 1
        assert data["files"][0]["name"] == "file1.pdf"

@patch("knowledgelm.cli.ForumClient")
@patch("knowledgelm.cli.PDFGenerator")
@patch("knowledgelm.cli.ReferenceExtractor")
def test_forum_command(mock_extractor_cls, mock_generator_cls, mock_client_cls):
    """Test forum command."""
    mock_client = mock_client_cls.return_value
    mock_client.get_full_thread.return_value = {"title": "Test", "posts": []}
    mock_client.parse_topic_url.return_value = ("slug", 123)

    mock_generator = mock_generator_cls.return_value
    mock_extractor = mock_extractor_cls.return_value
    mock_extractor.extract_references.return_value = "# References"

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["forum", "http://url", "--symbol", "SYM"])
        assert result.exit_code == 0

        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "Successfully saved thread" in content

        mock_client.get_full_thread.assert_called_with("http://url")
        mock_generator.generate_thread_pdf.assert_called()

@patch("knowledgelm.cli.ForumClient")
def test_forum_command_error(mock_client_cls):
    """Test forum command error handling."""
    mock_client = mock_client_cls.return_value
    mock_client.get_full_thread.side_effect = Exception("Fetch error")

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["forum", "http://url"])
        assert result.exit_code != 0

        log_file = Path("knowledgelm.log")
        assert log_file.exists()
        content = log_file.read_text()
        assert "Failed to download forum thread" in content
