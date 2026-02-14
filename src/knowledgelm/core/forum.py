"""Module for fetching ValuePickr forum threads and generating PDFs."""

import base64
import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.print_page_options import PrintOptions

logger = logging.getLogger(__name__)


class ForumClient:
    """Client for interacting with the ValuePickr (Discourse) JSON API."""

    BASE_URL = "https://forum.valuepickr.com"

    def __init__(self):
        """Initialize the forum client."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            }
        )

    def parse_topic_url(self, url: str) -> Tuple[str, int]:
        """Extract slug and topic ID from a URL.

        Args:
            url: The forum topic URL.

        Returns:
            Tuple of (slug, topic_id).

        Raises:
            ValueError: If the URL format is invalid.
        """
        # Match patterns like:
        # https://forum.valuepickr.com/t/security-and-intelligence-services/20319
        # https://forum.valuepickr.com/t/security-and-intelligence-services/20319/123
        match = re.search(r"/t/([^/]+)/(\d+)", url)
        if not match:
            raise ValueError(
                f"Invalid ValuePickr URL: {url}. Expected format: "
                "https://forum.valuepickr.com/t/slug/topic_id"
            )
        return match.group(1), int(match.group(2))

    def fetch_topic_data(self, slug: str, topic_id: int) -> Dict[str, Any]:
        """Fetch the initial topic metadata and post stream.

        Args:
            slug: The topic slug.
            topic_id: The topic ID.

        Returns:
            Dictionary containing the full topic data (same structure as JSON response).
        """
        url = f"{self.BASE_URL}/t/{slug}/{topic_id}.json"
        logger.info(f"Fetching topic metadata from {url}")

        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def fetch_posts_batch(self, topic_id: int, post_ids: List[int]) -> List[Dict[str, Any]]:
        """Fetch a batch of posts by their IDs.

        Args:
            topic_id: The topic ID.
            post_ids: List of post IDs to fetch.

        Returns:
            List of post objects.
        """
        url = f"{self.BASE_URL}/t/{topic_id}/posts.json"

        # Construct query parameters: post_ids[]=1&post_ids[]=2...
        params = [("post_ids[]", pid) for pid in post_ids]

        logger.debug(f"Fetching batch of {len(post_ids)} posts")
        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get("post_stream", {}).get("posts", [])

    def get_full_thread(self, url: str) -> Dict[str, Any]:
        """Download the entire thread including all posts.

        Args:
            url: The forum topic URL.

        Returns:
            Dictionary with 'title', 'id', and list of 'posts'.
        """
        slug, topic_id = self.parse_topic_url(url)

        # 1. Fetch initial data to get the full stream of post IDs
        initial_data = self.fetch_topic_data(slug, topic_id)
        post_stream = initial_data.get("post_stream", {})
        all_post_ids = post_stream.get("stream", [])

        if not all_post_ids:
            logger.warning("No post IDs found in stream.")
            return {"title": initial_data.get("title"), "id": topic_id, "posts": []}

        logger.info(f"Found {len(all_post_ids)} posts in thread '{initial_data.get('title')}'")

        # 2. Identify which posts we already have
        # The initial response usually contains the first chunk of posts (e.g., 20)
        initial_posts = post_stream.get("posts", [])
        fetched_ids = {p["id"] for p in initial_posts}

        # 3. Batch fetch the missing posts
        missing_ids = [pid for pid in all_post_ids if pid not in fetched_ids]

        all_posts = initial_posts[:]

        # Discourse allows fetching posts in batches
        BATCH_SIZE = 200  # Discourse usually allows larger batches for ID lookups

        for i in range(0, len(missing_ids), BATCH_SIZE):
            batch = missing_ids[i : i + BATCH_SIZE]
            logger.info(
                f"Fetching posts {i + 1} to {min(i + BATCH_SIZE, len(missing_ids))} "
                f"of {len(missing_ids)} remaining..."
            )

            try:
                new_posts = self.fetch_posts_batch(topic_id, batch)
                all_posts.extend(new_posts)
                # Be nice to the server
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Failed to fetch batch starting at index {i}: {e}")

        # Sort posts by creation date to ensure correct order
        all_posts.sort(key=lambda x: x.get("created_at", ""))

        return {
            "title": initial_data.get("title"),
            "id": topic_id,
            "posts": all_posts,
            "slug": slug,
            "details": initial_data.get("details", {}),
        }



class PDFGenerator:
    """Generates a clean PDF from forum thread data using Headless Chrome."""

    BASE_CSS = """
    @page {
        size: A4;
        margin: 20mm;
    }
    body {
        font-family: Georgia, "Times New Roman", Times, serif;
        line-height: 1.6;
        color: #1a1a1a;
        font-size: 16px;
    }
    h1 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
            Helvetica, Arial, sans-serif;
        font-size: 28px;
        color: #2c3e50;
        border-bottom: 2px solid #eee;
        padding-bottom: 10px;
        margin-bottom: 30px;
    }
    .post {
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 1px solid #eee;
        page-break-inside: avoid;
    }
    .post-header {
        margin-bottom: 15px;
        color: #7f8c8d;
        font-size: 12px;
        font-weight: 500;
    }
    .post-content {
        font-size: 14px;
    }
    .post-content img {
        max-width: 100%;
        height: auto;
        margin: 10px 0;
        border: 1px solid #eee;
        border-radius: 4px;
    }
    blockquote {
        border-left: 4px solid #ddd;
        margin: 0;
        padding-left: 15px;
        color: #666;
    }
    code {
        background: #f4f4f4;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: monospace;
    }
    pre {
        background: #f4f4f4;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
    }
    """

    def generate_thread_pdf(self, thread_data: Dict[str, Any], output_path: Path):
        """Generate a PDF file from the thread data.

        Args:
            thread_data: The dictionary returned by ForumClient.get_full_thread.
            output_path: Path to save the PDF.
        """
        title = thread_data.get("title", "ValuePickr Thread")
        posts = thread_data.get("posts", [])

        html_content = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<meta charset='utf-8'>",
            f"<title>{title}</title>",
            "<style>",
            self.BASE_CSS,
            "</style>",
            "</head>",
            "<body>",
            f"<h1>{title}</h1>",
            "<div class='thread-container'>",
        ]

        for post in posts:
            if post.get("hidden"):
                continue

            created_at = post.get("created_at", "")
            try:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                date_str = dt.strftime("%B %d, %Y at %I:%M %p")
            except ValueError:
                date_str = created_at

            content = post.get("cooked", "")

            post_html = f"""
            <div class='post'>
                <div class='post-header'>
                    {date_str}
                </div>
                <div class='post-content'>
                    {content}
                </div>
            </div>
            """
            html_content.append(post_html)

        html_content.append("</div></body></html>")

        full_html = "\n".join(html_content)

        logger.debug("Generating PDF using Headless Chrome...")

        # Write HTML to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        ) as f:
            f.write(full_html)
            temp_html_path = f.name

        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

            service_args = {"log_output": subprocess.DEVNULL}
            chromedriver_path = (
                os.environ.get("CHROMEDRIVER_PATH") or shutil.which("chromedriver")
            )
            if chromedriver_path:
                logger.debug(f"Using system ChromeDriver at {chromedriver_path}")
                service_args["executable_path"] = chromedriver_path
            else:
                logger.debug("System ChromeDriver not found, relying on Selenium Manager")

            service = Service(**service_args)
            if os.name == "nt":
                service.creation_flags = subprocess.CREATE_NO_WINDOW

            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.debug(f"Rendering {temp_html_path} via Selenium...")
            driver.get(f"file:///{temp_html_path}")

            # Use specific print options for A4
            print_options = PrintOptions()
            print_options.background = True

            pdf_base64 = driver.print_page(print_options)

            # Handle potential return types (string vs object)
            if hasattr(pdf_base64, "data"):
                encoded_data = pdf_base64.data
            else:
                encoded_data = pdf_base64

            pdf_data = base64.b64decode(encoded_data)

            with open(output_path, "wb") as f:
                f.write(pdf_data)

            logger.info(f"Successfully generated PDF: {output_path}")

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
        finally:
            if driver:
                driver.quit()
            # Clean up temp file
            try:
                os.unlink(temp_html_path)
            except Exception:
                pass


class ReferenceExtractor:
    """Extracts external references from forum thread data."""

    def extract_references(self, thread_data: Dict[str, Any]) -> str:
        """Extract external links and format as markdown.

        Args:
            thread_data: The dictionary returned by ForumClient.get_full_thread.

        Returns:
            Markdown string containing the references.
        """
        title = thread_data.get("title", "ValuePickr Thread")
        slug = thread_data.get("slug", "thread")
        details = thread_data.get("details", {})
        links = details.get("links", [])

        md_lines = [f"# References for {title}", ""]

        if not links:
            # Fallback to HTML parsing if no links found in details
            # return self._extract_references_from_html(thread_data)
            return f"# References for {title}\n\nNo external references found in this thread."

        # Group links by post number
        links_by_post = {}
        for link in links:
            # Skip internal links if flagged
            if link.get("internal") or link.get("reflection"):
                continue

            # Additional check for valuepickr domain just in case
            if "forum.valuepickr.com" in link.get("url", ""):
                continue

            post_num = link.get("post_number")
            if post_num is None:
                post_num = 0  # Global links?

            if post_num not in links_by_post:
                links_by_post[post_num] = []
            links_by_post[post_num].append(link)

        if not links_by_post:
            return f"# References for {title}\n\nNo external references found in this thread."

        # Sort by post number
        sorted_post_nums = sorted(links_by_post.keys())

        for post_num in sorted_post_nums:
            post_links = links_by_post[post_num]

            # Find the post date if possible
            post = next(
                (p for p in thread_data.get("posts", []) if p.get("post_number") == post_num), None
            )
            date_str = ""
            if post:
                created_at = post.get("created_at", "")
                try:
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    date_str = dt.strftime("%b %d, %Y")
                except ValueError:
                    date_str = created_at

            post_url = f"https://forum.valuepickr.com/t/{slug}/{thread_data.get('id')}/{post_num}"

            header = f"## Post #{post_num}"
            if date_str:
                header += f" ({date_str})"

            md_lines.append(header)
            md_lines.append(f"[View Post]({post_url})")
            md_lines.append("")

            for link in post_links:
                url = link.get("url")
                title = link.get("title") or url
                clicks = link.get("clicks", 0)

                # Sanitize title
                title = title.replace("\n", " ")
                if len(title) > 100:
                    title = title[:100] + "..."

                line = f"- [{title}]({url})"
                if clicks > 0:
                    line += f" (Clicks: {clicks})"
                md_lines.append(line)

            md_lines.append("")

        return "\n".join(md_lines)

    def _extract_references_from_html(self, thread_data: Dict[str, Any]) -> str:
        """Legacy method: Extract external links by parsing HTML content.

        Note: This is computationally expensive and less reliable than using
        the 'links' array from topic details. Use only as a fallback.
        """
        title = thread_data.get("title", "ValuePickr Thread")
        posts = thread_data.get("posts", [])
        slug = thread_data.get("slug", "thread")

        md_lines = [f"# References for {title}", ""]
        has_refs = False

        for post in posts:
            if post.get("hidden"):
                continue

            content = post.get("cooked", "")
            if not content:
                continue

            soup = BeautifulSoup(content, "html.parser")
            links = soup.find_all("a", href=True)

            external_links = []
            seen_urls = set()

            for link in links:
                href = link["href"]
                text = link.get_text().strip()

                if (
                    not href
                    or href.startswith("#")
                    or href.startswith("/")
                    or "forum.valuepickr.com" in href
                    or href in seen_urls
                ):
                    continue

                if not href.startswith("http"):
                    continue

                seen_urls.add(href)
                external_links.append((text, href))

            if external_links:
                has_refs = True
                created_at = post.get("created_at", "")
                try:
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    date_str = dt.strftime("%b %d, %Y")
                except ValueError:
                    date_str = created_at

                post_num = post.get("post_number")
                post_url = (
                    f"https://forum.valuepickr.com/t/{slug}/{thread_data.get('id')}/{post_num}"
                )

                md_lines.append(f"## Post #{post_num} ({date_str})")
                md_lines.append(f"[View Post]({post_url})")
                md_lines.append("")

                for text, href in external_links:
                    display_text = text if text else "Link"
                    display_text = (
                        (display_text[:100] + "...") if len(display_text) > 100 else display_text
                    )
                    display_text = display_text.replace("\n", " ")
                    md_lines.append(f"- [{display_text}]({href})")

                md_lines.append("")

        if not has_refs:
            return f"# References for {title}\n\nNo external references found in this thread."

        return "\n".join(md_lines)
