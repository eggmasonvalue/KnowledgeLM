from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

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

    # Invalid domain
    with pytest.raises(ValueError, match="Invalid ValuePickr URL domain"):
        client.parse_topic_url("https://example.com/t/slug/123")

    # Invalid scheme
    with pytest.raises(ValueError, match="Invalid ValuePickr URL scheme"):
        client.parse_topic_url("ftp://forum.valuepickr.com/t/slug/123")

    # Missing scheme
    with pytest.raises(ValueError, match="Invalid ValuePickr URL scheme"):
        client.parse_topic_url("forum.valuepickr.com/t/slug/123")

    # Invalid path format (missing ID)
    with pytest.raises(ValueError, match="Invalid ValuePickr URL path"):
        client.parse_topic_url("https://forum.valuepickr.com/t/slug")

    # Invalid path format (wrong prefix)
    with pytest.raises(ValueError, match="Invalid ValuePickr URL path"):
        client.parse_topic_url("https://forum.valuepickr.com/topic/slug/123")

    # Path traversal / malicious path
    with pytest.raises(ValueError, match="Invalid ValuePickr URL path"):
        client.parse_topic_url("https://forum.valuepickr.com/t/../../etc/passwd/123")

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

def test_pdf_generator_driver_not_found():
    """Test PDF generation when ChromeDriver is not found."""
    # We need to unset CHROMEDRIVER_PATH env var and make shutil.which return None
    with patch.dict("os.environ", {}, clear=True), \
         patch("shutil.which", return_value=None), \
         patch("knowledgelm.core.forum.webdriver.Chrome") as mock_chrome:

        generator = PDFGenerator()
        thread_data = {"title": "Test", "posts": []}

        # Should rely on Selenium Manager (Service default)
        # We just want to ensure no exception is raised during Service creation if we don't pass executable_path

        with patch("knowledgelm.core.forum.Service") as mock_service:
            # We also mock print_page to avoid actual execution
            mock_driver = mock_chrome.return_value
            mock_print_resp = MagicMock()
            mock_print_resp.data = "dGVzdA=="
            mock_driver.print_page.return_value = mock_print_resp

            with patch("builtins.open", new_callable=MagicMock):
                generator.generate_thread_pdf(thread_data, Path("out.pdf"))

            # Verify Service was called without executable_path
            call_args = mock_service.call_args[1]
            assert "executable_path" not in call_args

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

def test_extract_references_legacy():
    """Test fallback extraction from HTML content."""
    extractor = ReferenceExtractor()

    # Simulate data without 'links' in details
    thread_data = {
        "title": "Thread",
        "slug": "slug",
        "id": 123,
        "details": {},
        "posts": [
            {
                "post_number": 1,
                "created_at": "2023-01-01T10:00:00Z",
                "cooked": '<p>Check <a href="http://external.com/1">Link 1</a></p>',
            },
            {
                "post_number": 2,
                "created_at": "2023-01-01T11:00:00Z",
                "cooked": '<p>Internal <a href="https://forum.valuepickr.com/t/1">Internal</a></p>',
            },
        ],
    }

    # Create mock BeautifulSoup objects
    # Post 1
    mock_link1 = MagicMock()
    mock_link1.__getitem__.side_effect = lambda key: {"href": "http://external.com/1"}[key]
    mock_link1.get_text.return_value = "Link 1"

    mock_soup1 = MagicMock()
    mock_soup1.find_all.return_value = [mock_link1]

    # Post 2
    mock_link2 = MagicMock()
    mock_link2.__getitem__.side_effect = lambda key: {"href": "https://forum.valuepickr.com/t/1"}[
        key
    ]
    mock_link2.get_text.return_value = "Internal"

    mock_soup2 = MagicMock()
    mock_soup2.find_all.return_value = [mock_link2]

    with patch("knowledgelm.core.forum.BeautifulSoup") as mock_bs:
        mock_bs.side_effect = [mock_soup1, mock_soup2]

        # So we must call the legacy method directly to test it.
        md = extractor._extract_references_from_html(thread_data)

    assert "Link 1" in md
    assert "http://external.com/1" in md
    assert "Internal" not in md  # Should be skipped


def test_extract_references_from_html_filtering():
    """Test filtering logic in _extract_references_from_html."""
    extractor = ReferenceExtractor()
    thread_data = {
        "title": "Thread",
        "slug": "slug",
        "id": 123,
        "posts": [
            {
                "post_number": 1,
                "cooked": "links",
            }
        ],
    }

    # Helper to create a mock link
    def create_mock_link(href, text="Link"):
        m = MagicMock()
        m.__getitem__.side_effect = lambda key: href if key == "href" else None
        m.get_text.return_value = text
        return m

    mock_links = [
        create_mock_link("http://valid.com", "Valid"),
        create_mock_link("https://valid.com", "Valid Secure"),
        create_mock_link("ftp://invalid.com", "FTP"),  # Not http
        create_mock_link("/relative", "Relative"),  # Relative
        create_mock_link("#anchor", "Anchor"),  # Anchor
        create_mock_link("https://forum.valuepickr.com/t/1", "Internal"),  # Internal
        create_mock_link("", "Empty"),  # Empty
        create_mock_link("http://valid.com", "Duplicate"),  # Duplicate URL
    ]

    mock_soup = MagicMock()
    mock_soup.find_all.return_value = mock_links

    with patch("knowledgelm.core.forum.BeautifulSoup", return_value=mock_soup):
        md = extractor._extract_references_from_html(thread_data)

    assert "Valid" in md
    assert "Valid Secure" in md
    assert "FTP" not in md
    assert "Relative" not in md
    assert "Anchor" not in md
    assert "Internal" not in md
    assert "Duplicate" not in md  # Should only see the first occurrence


def test_extract_references_from_html_sanitization():
    """Test title sanitization in _extract_references_from_html."""
    extractor = ReferenceExtractor()
    thread_data = {
        "title": "Thread",
        "slug": "slug",
        "id": 123,
        "posts": [
            {
                "post_number": 1,
                "cooked": "links",
            }
        ],
    }

    long_title = "A" * 150
    newline_title = "Title with\nNewline"

    def create_mock_link(href, text):
        m = MagicMock()
        m.__getitem__.side_effect = lambda key: href if key == "href" else None
        m.get_text.return_value = text
        return m

    mock_links = [
        create_mock_link("http://long.com", long_title),
        create_mock_link("http://newline.com", newline_title),
        create_mock_link("http://notext.com", "   "),  # Should fallback to "Link"
    ]

    mock_soup = MagicMock()
    mock_soup.find_all.return_value = mock_links

    with patch("knowledgelm.core.forum.BeautifulSoup", return_value=mock_soup):
        md = extractor._extract_references_from_html(thread_data)

    # Check truncation (100 chars + ...)
    assert "A" * 100 + "..." in md
    # Check newline replacement
    assert "Title with Newline" in md
    # Check fallback text
    assert "[Link](http://notext.com)" in md


def test_extract_references_from_html_edge_cases():
    """Test edge cases in _extract_references_from_html."""
    extractor = ReferenceExtractor()
    thread_data = {
        "title": "Thread",
        "slug": "slug",
        "id": 123,
        "posts": [
            {"post_number": 1, "hidden": True, "cooked": '<a href="http://hidden.com">Hidden</a>'},
            {"post_number": 2, "cooked": ""},  # Empty content
            {"post_number": 3},  # Missing cooked
        ],
    }

    md = extractor._extract_references_from_html(thread_data)

    assert "hidden.com" not in md
    assert "No external references found" in md


def test_extract_references_from_html_no_refs():
    """Test _extract_references_from_html when no references are found."""
    extractor = ReferenceExtractor()
    thread_data = {
        "title": "Empty Thread",
        "posts": [{"post_number": 1, "cooked": "<p>No links here</p>"}],
    }

    mock_soup = MagicMock()
    mock_soup.find_all.return_value = []

    with patch("knowledgelm.core.forum.BeautifulSoup", return_value=mock_soup):
        md = extractor._extract_references_from_html(thread_data)

    assert "No external references found" in md
    assert "Empty Thread" in md
