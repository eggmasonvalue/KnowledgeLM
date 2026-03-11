"""Adapter module for interacting with the NSE library and data endpoints."""

import io
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from nse import NSE

from knowledgelm.utils.log_utils import redirect_output_to_logger

logger = logging.getLogger(__name__)


class NSEAdapter:
    """Wrapper around the NSE library to isolate dependencies."""

    def __init__(self, download_folder: Path):
        """Initialize the NSE adapter.

        Args:
            download_folder: Path where documents will be downloaded.
        """
        self.download_folder = download_folder
        # Suppress initial print if any
        with redirect_output_to_logger(logger):
            self.nse = NSE(str(download_folder), server=True)

    def get_announcements(
        self, symbol: str, from_date: datetime, to_date: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch announcements from NSE for a specific symbol and date range.

        Args:
            symbol: Stock symbol.
            from_date: Start date for the announcements fetch.
            to_date: End date for the announcements fetch.

        Returns:
            A list of announcement dictionaries from the NSE response.
        """
        logger.info(
            f"Fetching announcements for {symbol} ({from_date} to {to_date})..."
        )
        try:
            with redirect_output_to_logger(logger):
                return self.nse.announcements(symbol=symbol, from_date=from_date, to_date=to_date)
        except Exception as e:
            logger.error(f"Error fetching announcements for {symbol}: {e}")
            return []

    def get_annual_reports(self, symbol: str) -> Dict[str, Any]:
        """Fetch annual reports metadata from NSE.

        Args:
            symbol: Stock symbol.

        Returns:
            A dictionary containing annual report metadata, typically grouped by year.
        """
        logger.info(f"Fetching annual reports for {symbol}...")
        try:
            with redirect_output_to_logger(logger):
                return self.nse.annual_reports(symbol)
        except Exception as e:
            logger.error(f"Error fetching annual reports for {symbol}: {e}")
            return {}

    def download_and_extract(self, url: str, destination_folder: Path, file_name: Optional[str] = None) -> bool:
        """Download a document, extracting all contents if it is a ZIP archive.

        This uses the internal NSE session (_req) for authentication but performs
        its own robust extraction to bypass the library's selective extraction.

        Args:
            url: URL of the document to download.
            destination_folder: Folder to save/extract the file into.
            file_name: Optional override for the saved filename.
            
        Returns:
            True if download succeeded.
        """
        logger.info(f"Downloading and extracting: {url}")
        try:
            # Ensure we have an absolute Path object and it exists
            dest_path = Path(destination_folder).absolute()
            dest_path.mkdir(parents=True, exist_ok=True)

            with redirect_output_to_logger(logger):
                response = self.nse._req(url)

            if response.status_code != 200:
                logger.error(f"Failed to fetch {url}: Status {response.status_code}")
                return False

            original_filename = url.split("?")[0].split("/")[-1]
            if not original_filename:
                original_filename = "document_data"

            # 1. Handle ZIP mirroring
            if original_filename.lower().endswith(".zip") or original_filename.lower().endswith(".gz"):
                try:
                    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                        self._safe_extract(z, dest_path)
                    return True
                except zipfile.BadZipFile:
                    logger.warning(f"File from {url} claimed to be ZIP but is not. Saving raw.")

            # 2. Handle Direct File
            output_filename = file_name if file_name else original_filename
            output_full_path = dest_path / output_filename
            with open(output_full_path, "wb") as f:
                f.write(response.content)
            return True

        except Exception as e:
            logger.error(f"Error during robust download/extract of {url}: {e}")
            return False

    def _safe_extract(self, zf: zipfile.ZipFile, extract_path: Path):
        """Safely extract ZIP members to prevent Zip Slip (path traversal)."""
        resolved_extract_path = extract_path.resolve()
        for member in zf.infolist():
            # Calculate the absolute target path for the member
            target_path = (resolved_extract_path / member.filename).resolve()
            # Ensure the target path is still within the extraction directory
            if not target_path.is_relative_to(resolved_extract_path):
                logger.warning(f"Skipping malicious ZIP member: {member.filename}")
                continue
            zf.extract(member, resolved_extract_path)

    def get_issue_documents(self, api_path: str, params: Dict[str, str]) -> List[Dict[str, Any]]:
        """Fetch issue documents from an NSE corporate filings endpoint.

        Uses the NSE library's internal _req method to reuse the session's
        cookies, headers, and throttling.

        Args:
            api_path: API path suffix (e.g., '/corporates/offerdocs').
            params: Query parameters for the request.

        Returns:
            List of document records from the API.
        """
        url = f"{self.nse.base_url}{api_path}"
        logger.info(f"Fetching issue documents from {api_path}...")
        try:
            with redirect_output_to_logger(logger):
                response = self.nse._req(url, params=params if params else None)
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching issue documents from {api_path}: {e}")
            return []

    def fetch_json(self, url: str, params: Optional[Dict[str, str]] = None) -> Any:
        """Make a generic GET request to an NSE URL and return JSON.

        Reuses the internal NSE session for consistent headers and cookies.

        Args:
            url: Full URL or path.
            params: Query parameters.

        Returns:
            Parsed JSON content, or None on failure.
        """
        try:
            with redirect_output_to_logger(logger):
                response = self.nse._req(url, params=params)
                # Check status code? _req usually returns response object
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"fetch_json failed for {url}: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching JSON from {url}: {e}")
            return None

    def get_company_name(self, symbol: str) -> str:
        """Resolve a stock symbol to its full company name.

        Used for matching on endpoints where the symbol field is unreliable
        (Offer Documents, Information Memorandum).

        Args:
            symbol: The company stock symbol (e.g., 'HDFCBANK').

        Returns:
            The full company name, or empty string if resolution fails.
        """
        try:
            with redirect_output_to_logger(logger):
                meta = self.nse.equityMetaInfo(symbol)
                return meta.get("companyName", "")
        except Exception as e:
            logger.error(f"Error resolving company name for {symbol}: {e}")
            return ""

    def validate_symbol(self, symbol: str) -> bool:
        """Check if a symbol is valid using equityQuote.

        Args:
            symbol: The company stock symbol (e.g., 'INFY').

        Returns:
            True if the symbol exists/provides a quote, False otherwise.
        """
        try:
            with redirect_output_to_logger(logger):
                # equityQuote returns a dict for valid symbols
                # and raises an exception (often KeyError 'priceInfo') for invalid ones
                quote = self.nse.equityQuote(symbol)
                return bool(quote)
        except Exception:
            # Any error during quote fetch implies invalid symbol or network issue.
            # treating as invalid for safety.
            return False
