"""Adapter for the NSE library."""

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
