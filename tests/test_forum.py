import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, ANY
from knowledgelm.core.forum import ForumClient, PDFGenerator, ReferenceExtractor

# --- ForumClient Tests ---

def test_parse_topic_url():
    """Test URL parsing for topic slug and ID."""
    client = ForumClient()
    slug, topic_id = client.parse_topic_url("https://forum.valuepickr.com/t/some-company/12345")
    assert slug == "some-company"
    assert topic_id == 12345

    slug, topic_id = client.parse_topic_url("https://forum.valuepickr.com/t/some-company/12345/999")
    assert slug == "some-company"
    assert topic_id == 12345

def test_parse_topic_url_invalid():
    """Test invalid URL parsing."""
    client = ForumClient()
    with pytest.raises(ValueError):
        client.parse_topic_url("https://example.com/invalid")

def test_fetch_topic_data(mock_requests):
    """Test fetching topic metadata."""
    mock_get, mock_session = mock_requests
    client = ForumClient()

    # Configure session mock
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"title": "Test Topic", "id": 123}
    mock_session.get.return_value = response_mock

    data = client.fetch_topic_data("slug", 123)

    assert data == {"title": "Test Topic", "id": 123}
    mock_session.get.assert_called_with("https://forum.valuepickr.com/t/slug/123.json")

def test_fetch_posts_batch(mock_requests):
    """Test fetching a batch of posts."""
    mock_get, mock_session = mock_requests
    client = ForumClient()

    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"post_stream": {"posts": [{"id": 1}, {"id": 2}]}}
    mock_session.get.return_value = response_mock

    posts = client.fetch_posts_batch(123, [1, 2])

    assert len(posts) == 2
    assert posts[0]["id"] == 1
    mock_session.get.assert_called()

def test_get_full_thread(mock_requests):
    """Test downloading the full thread."""
    mock_get, mock_session = mock_requests
    client = ForumClient()

    # Sequence of calls:
    # 1. fetch_topic_data -> returns stream with IDs [1, 2, 3] and initial posts [1]
    # 2. fetch_posts_batch -> fetches missing [2, 3]

    topic_resp = MagicMock()
    topic_resp.json.return_value = {
        "title": "Topic",
        "id": 123,
        "details": {},
        "post_stream": {
            "stream": [1, 2, 3],
            "posts": [{"id": 1, "created_at": "2023-01-01T10:00:00Z"}]
        }
    }

    batch_resp = MagicMock()
    batch_resp.json.return_value = {
        "post_stream": {
            "posts": [
                {"id": 2, "created_at": "2023-01-01T11:00:00Z"},
                {"id": 3, "created_at": "2023-01-01T12:00:00Z"}
            ]
        }
    }

    mock_session.get.side_effect = [topic_resp, batch_resp]

    thread = client.get_full_thread("https://forum.valuepickr.com/t/slug/123")

    assert len(thread["posts"]) == 3
    assert thread["posts"][0]["id"] == 1
    assert thread["posts"][2]["id"] == 3

# --- PDFGenerator Tests ---

def test_generate_thread_pdf(mock_selenium_driver):
    """Test PDF generation using Selenium."""
    mock_chrome, mock_driver = mock_selenium_driver
    generator = PDFGenerator()

    thread_data = {
        "title": "Test Thread",
        "posts": [
            {"cooked": "<p>Post 1</p>", "created_at": "2023-01-01T10:00:00Z"},
            {"cooked": "<p>Post 2</p>", "created_at": "2023-01-01T11:00:00Z"}
        ]
    }

    # Mock driver.print_page returning base64 object with data attribute or string
    # print_page usually returns a PrintPageResponse object where .data is the base64 string
    mock_print_resp = MagicMock()
    mock_print_resp.data = "dGVzdA==" # "test"
    mock_driver.print_page.return_value = mock_print_resp

    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        generator.generate_thread_pdf(thread_data, Path("/tmp/out.pdf"))

        mock_driver.get.assert_called()
        assert "file:///" in mock_driver.get.call_args[0][0]
        mock_driver.print_page.assert_called()
        mock_open.assert_called()

# --- ReferenceExtractor Tests ---

def test_extract_references():
    """Test extraction of references from thread data."""
    extractor = ReferenceExtractor()

    thread_data = {
        "title": "Thread",
        "slug": "slug",
        "id": 123,
        "details": {
            "links": [
                {"url": "http://external.com/1", "title": "Ext 1", "post_number": 1, "clicks": 5},
                {"url": "https://forum.valuepickr.com/internal", "internal": True, "post_number": 1},
                {"url": "http://external.com/2", "title": "Ext 2", "post_number": 2}
            ]
        },
        "posts": [
            {"post_number": 1, "created_at": "2023-01-01T10:00:00Z"},
            {"post_number": 2, "created_at": "2023-01-01T11:00:00Z"}
        ]
    }

    md = extractor.extract_references(thread_data)

    assert "# References for Thread" in md
    assert "## Post #1" in md
    assert "[Ext 1](http://external.com/1)" in md
    assert "Clicks: 5" in md
    assert "## Post #2" in md
    assert "[Ext 2](http://external.com/2)" in md

    # Internal link should be skipped
    assert "internal" not in md.lower()

def test_extract_references_empty():
    """Test extraction when no references exist."""
    extractor = ReferenceExtractor()
    thread_data = {"title": "Thread", "details": {"links": []}}

    md = extractor.extract_references(thread_data)
    assert "No external references found" in md
