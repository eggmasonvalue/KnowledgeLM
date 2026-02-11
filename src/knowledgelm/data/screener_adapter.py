"""Adapter for fetching data from Screener.in."""

import os

# Silence webdriver_manager logs
os.environ["WDM_LOG"] = "0"
import base64
import logging
import subprocess
import time
from pathlib import Path
from typing import Optional

import requests
import urllib3
from bs4 import BeautifulSoup

from knowledgelm.config import (
    CREDIT_RATING_FOLDER,
    SCREENER_BASE_URL,
    SCREENER_DOCS_SELECTOR,
    SCREENER_TIMEOUT,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Conditional Selenium import for HTML-to-PDF conversion
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)


def _get_icra_pdf_url(original_url: str) -> Optional[str]:
    """Convert ICRA report URL to direct PDF link if possible.

    Example:
        Input: https://www.icra.in/Rationale/ShowRationaleReport/?Id=136064
        Output: https://www.icra.in/Rating/ShowRationalReportFilePdf/136064
    """
    if "icra.in" in original_url and "ShowRationaleReport" in original_url:
        try:
            # Extract ID from query parameter
            if "Id=" in original_url:
                report_id = original_url.split("Id=")[-1].split("&")[0]
                return f"https://www.icra.in/Rating/ShowRationalReportFilePdf/{report_id}"
        except Exception as e:
            logger.warning(f"Failed to parse ICRA URL {original_url}: {e}")
    return None


def _download_with_selenium(url: str, output_path: Path) -> bool:
    """Download page as PDF using Selenium (headless Chrome)."""
    if not SELENIUM_AVAILABLE:
        logger.warning("Selenium not available. Cannot convert HTML to PDF for %s", url)
        return False

    driver = None
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--log-level=3")  # Fatal only, silences DevTools listening...
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # Ensure we are not blocking downloads (though we are printing)

        service = Service(ChromeDriverManager().install(), log_output=subprocess.DEVNULL)
        if os.name == "nt":
            service.creation_flags = subprocess.CREATE_NO_WINDOW
        driver = webdriver.Chrome(service=service, options=options)

        logger.debug(f"Rendering {url} via Selenium...")
        driver.get(url)

        # Wait for potential JS rendering (especially for charts/tables)
        time.sleep(5)

        # Print to PDF using Chrome DevTools Protocol
        pdf_data = driver.execute_cdp_cmd(
            "Page.printToPDF",
            {
                "printBackground": True,
                "paperWidth": 8.27,  # A4
                "paperHeight": 11.69,
                "marginTop": 0.4,
                "marginBottom": 0.4,
                "marginLeft": 0.4,
                "marginRight": 0.4,
            },
        )

        if "data" in pdf_data:
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(pdf_data["data"]))
            logger.debug(f"Saved PDF via Selenium to {output_path}")
            return True

        return False
    except Exception as e:
        logger.error(f"Selenium download failed for {url}: {e}")
        return False
    finally:
        if driver:
            driver.quit()


def download_credit_ratings_from_screener(symbol: str, download_folder: Path) -> int:
    """Download all credit rating documents for a symbol from screener.in.

    Preferred output format is PDF.
    - PDFs are downloaded directly.
    - ICRA HTML pages are converted to direct PDF links.
    - Other HTML pages are converted to PDF using Selenium.

    Args:
        symbol: The stock symbol.
        download_folder: The root download folder path.

    Returns:
        The number of documents downloaded.
    """
    screener_url = SCREENER_BASE_URL.format(symbol=symbol)
    try:
        # Security Fix: verify=True (default) set.
        resp = requests.get(screener_url, timeout=SCREENER_TIMEOUT)
        if resp.status_code != 200:
            logger.warning(f"Screener.in returned {resp.status_code} for {symbol}")
            return 0

        soup = BeautifulSoup(resp.text, "html.parser")
        credit_ratings_div = None

        # Find credit ratings section
        divs = soup.select(SCREENER_DOCS_SELECTOR)
        for div in divs:
            h3 = div.find("h3")
            if h3 and "credit ratings" in h3.text.strip().lower():
                credit_ratings_div = div
                break

        if not credit_ratings_div:
            logger.info("No credit ratings section found on Screener.")
            return 0

        ul = credit_ratings_div.find("ul", class_="list-links")
        if not ul:
            return 0

        links = ul.find_all("a", href=True)
        if not links:
            return 0

        dest_folder = download_folder / CREDIT_RATING_FOLDER
        dest_folder.mkdir(parents=True, exist_ok=True)

        count = 0
        downloaded_files = set(f.name for f in dest_folder.glob("*"))

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": screener_url,
        }

        for a in links:
            url = a["href"]
            try:
                # Extract date info for filename
                # Expected HTML:
                # <a href="...">
                #   Rating update
                #   <div class="ink-600 smaller">
                #     4 Jul from icra
                #   </div>
                # </a>
                date_text = "Unknown_Date"
                date_div = a.find("div", class_="ink-600 smaller")
                if date_div:
                    # Clean the text: "4 Jul from icra" -> "4_Jul_from_icra"
                    # Also remove commas or other unsafe chars
                    raw_text = date_div.get_text(strip=True)
                    safe_text = "".join(c if c.isalnum() else "_" for c in raw_text)
                    # Collapse multiple underscores
                    safe_text = "_".join(filter(None, safe_text.split("_")))
                    if safe_text:
                        date_text = safe_text

                # Construct new filename prefix
                filename_prefix = f"CreditRating-{date_text}"

                # 1. Attempt to resolve ICRA PDF link directly
                pdf_url = _get_icra_pdf_url(url)
                target_url = pdf_url if pdf_url else url

                logger.debug(f"Processing {url} -> Target: {target_url}")

                # 2. Check content type (stream mode to avoid downloading big files yet)
                try:
                    resp = requests.get(
                        target_url, stream=True, timeout=30, verify=False, headers=headers
                    )
                except requests.SSLError:
                    logger.warning(f"SSL Error for {target_url}, skipping.")
                    continue
                except Exception as e:
                    logger.warning(f"Connection error for {target_url}: {e}")
                    continue

                content_type = resp.headers.get("Content-Type", "").lower()

                # Construct filename
                filename = f"{filename_prefix}.pdf"

                if "application/pdf" in content_type:
                    if filename in downloaded_files:
                        resp.close()
                        continue

                    file_path = dest_folder / filename
                    with open(file_path, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=8192):
                            f.write(chunk)
                    count += 1
                    downloaded_files.add(filename)
                    resp.close()
                    continue

                # If HTML, we want to convert to PDF using Selenium
                resp.close()

                if filename in downloaded_files:
                    continue

                file_path = dest_folder / filename

                # Use Selenium
                logger.debug(f"Converting HTML to PDF via Selenium: {target_url}")
                if _download_with_selenium(target_url, file_path):
                    count += 1
                    downloaded_files.add(filename)

            except Exception as e:
                logger.error(f"Error processing credit rating {url}: {e}")

        return count

    except Exception as e:
        logger.error(f"Error fetching credit ratings page: {e}")
        return 0
