import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from nse import NSE

from knowledgelm.utils.log_utils import redirect_stdout_to_logger

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
        with redirect_stdout_to_logger(logger):
            self.nse = NSE(str(download_folder))

    def get_announcements(
        self, symbol: str, from_date: datetime, to_date: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch announcements from NSE."""
        try:
            with redirect_stdout_to_logger(logger):
                return self.nse.announcements(symbol=symbol, from_date=from_date, to_date=to_date)
        except Exception as e:
            logger.error(f"Error fetching announcements for {symbol}: {e}")
            return []

    def get_annual_reports(self, symbol: str) -> Dict[str, Any]:
        """Fetch annual reports metadata."""
        try:
            with redirect_stdout_to_logger(logger):
                return self.nse.annual_reports(symbol)
        except Exception as e:
            logger.error(f"Error fetching annual reports for {symbol}: {e}")
            return {}

    def download_document(self, url: str, destination_folder: Path) -> bool:
        """Download a document using the NSE library's downloader.

        Note: The underlying library might not be secure or robust.
        Long term, we should replace this with our own requests call.
        """
        try:
            with redirect_stdout_to_logger(logger):
                self.nse.download_document(url, destination_folder)
            return True
        except Exception as e:
            logger.error(f"Error downloading document {url}: {e}")
            return False

    def download_and_extract(self, url: str, destination_folder: Path) -> bool:
        """Download a document, extracting it if it is a ZIP archive.

        Delegates to the NSE library's download_document, which natively
        handles ZIP extraction.

        Args:
            url: URL of the document to download.
            destination_folder: Folder to save/extract the file into.

        Returns:
            True if download succeeded.
        """
        try:
            with redirect_stdout_to_logger(logger):
                self.nse.download_document(url, destination_folder)
            return True
        except Exception as e:
            logger.error(f"Error downloading document {url}: {e}")
            return False

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
        try:
            with redirect_stdout_to_logger(logger):
                response = self.nse._req(url, params=params if params else None)
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching issue documents from {api_path}: {e}")
            return []

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
            with redirect_stdout_to_logger(logger):
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
            with redirect_stdout_to_logger(logger):
                # equityQuote returns a dict for valid symbols
                # and raises an exception (often KeyError 'priceInfo') for invalid ones
                quote = self.nse.equityQuote(symbol)
                return bool(quote)
        except Exception:
            # Any error during quote fetch implies invalid symbol or network issue.
            # treating as invalid for safety.
            return False
