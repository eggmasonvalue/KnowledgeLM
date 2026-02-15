"""Core service logic for KnowledgeLM."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from knowledgelm.config import (
    ANNUAL_REPORTS_FOLDER,
    DOWNLOAD_CATEGORIES_CONFIG,
    ISSUE_DOCS_CONFIG,
    ISSUE_DOCS_FOLDER,
)
from knowledgelm.data.nse_adapter import NSEAdapter
from knowledgelm.data.screener_adapter import download_credit_ratings_from_screener
from knowledgelm.utils.file_utils import get_download_path

logger = logging.getLogger(__name__)


class KnowledgeService:
    """Service class to handle orchestration of fetching and downloading."""

    def __init__(self, base_download_path: str):
        """Initialize the service.

        Args:
            base_download_path: The root directory where specific symbol folders will be created.
                NOTE: This is NOT the symbol folder itself, but usually CWD.
                The actual download folder is determined per request or config.
                However, for this app structure, the UI passes the specific folder name.
        """
        self.base_path = Path(base_download_path)

    def process_request(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        folder_name: str,
        options: Dict[str, bool],
        annual_reports_all_mode: bool = False,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """Process the user request to fetch and download filings.

        Args:
            symbol: Stock symbol.
            from_date: Start date.
            to_date: End date.
            folder_name: Name of the folder to create (will be sanitized).
            options: Dictionary mapping config keys (e.g., 'download_transcripts') to booleans.
            annual_reports_all_mode: If True, download all ARs ignoring date range.

        Returns:
            Tuple of (announcements_list, category_counts_dict)
        """
        # 1. Setup Folder
        # Assuming the service is initialized with a base path (like CWD),
        # get_download_path sanitizes and joins.
        try:
            download_dir = get_download_path(str(self.base_path), folder_name)
            download_dir.mkdir(parents=True, exist_ok=True)
        except ValueError as e:
            logger.error(f"Invalid folder name: {e}")
            raise

        nse_adapter = NSEAdapter(download_dir)

        # 1.5 Validate Symbol
        if not nse_adapter.validate_symbol(symbol):
            raise ValueError(f"Symbol '{symbol}' is invalid or not found on NSE.")

        # 2. Fetch Announcements
        announcements = nse_adapter.get_announcements(symbol, from_date, to_date)

        category_counts = {}

        # 3. Process Categories
        for cat_key, config in DOWNLOAD_CATEGORIES_CONFIG.items():
            if not options.get(config["enabled_arg"], False):
                continue

            label = config["label"]

            # Special Case: Annual Reports
            if cat_key == "annual_reports":
                count = self._process_annual_reports(
                    symbol, nse_adapter, download_dir, from_date, to_date, annual_reports_all_mode
                )
                category_counts[label] = count
                continue

            # Special Case: Credit Ratings
            if cat_key == "credit_rating":
                count = self._process_credit_ratings(
                    symbol, announcements, nse_adapter, download_dir
                )
                category_counts[label] = count
                continue

            # Special Case: Issue Documents
            if cat_key == "issue_documents":
                issue_counts = self._process_issue_documents(symbol, nse_adapter, download_dir)
                category_counts.update(issue_counts)
                continue

            # Standard Categories - apply filter and download matching items

            cat_folder = download_dir / cat_key
            cat_folder.mkdir(parents=True, exist_ok=True)

            count = 0
            for item in announcements:
                if self._matches_filter(cat_key, item):
                    url = item.get("attchmntFile")
                    if url:
                        if nse_adapter.download_document(url, cat_folder):
                            count += 1
            category_counts[label] = count

        return announcements, category_counts

    def _matches_filter(self, category: str, item: Dict[str, Any]) -> bool:
        """Check if an item matches the category filter."""
        desc = str(item.get("desc", "")).strip().lower()
        attortext = str(item.get("attchmntText", "")).lower()
        has_file = bool(item.get("attchmntFile"))

        if not has_file:
            return False

        if category == "transcripts":
            return (
                desc == "analysts/institutional investor meet/con. call updates"
                and "transcript" in attortext
            )
        elif category == "investor_presentations":
            return desc == "investor presentation"
        elif category == "press_releases":
            return desc in ["press release", "press release (revised)"]
        elif category == "credit_rating":
            return desc == "credit rating"
        elif category == "related_party_txns":
            return desc in ["related party transaction", "related party transactions"]

        return False

    def _process_annual_reports(
        self,
        symbol: str,
        adapter: NSEAdapter,
        root_dir: Path,
        from_date: datetime,
        to_date: datetime,
        all_mode: bool,
    ) -> int:
        ar_folder = root_dir / ANNUAL_REPORTS_FOLDER
        ar_folder.mkdir(parents=True, exist_ok=True)
        count = 0

        ar_data = adapter.get_annual_reports(symbol)
        # ar_data is {year: [docs...]} or similar structure based on legacy code

        if not ar_data:
            return 0

        for year, docs in ar_data.items():
            for doc in docs:
                to_yr = doc.get("toYr")
                url = (
                    doc.get("fileName")
                    or doc.get("url")
                    or doc.get("fileUrl")
                    or doc.get("documentUrl")
                )
                if not url or not to_yr:
                    continue

                try:
                    yr = int(str(to_yr).strip())
                except ValueError:
                    continue

                if not all_mode:
                    if yr < from_date.year or yr > to_date.year:
                        continue

                if adapter.download_document(url, ar_folder):
                    count += 1
        return count

    def _process_credit_ratings(
        self, symbol: str, announcements: List[Dict[str, Any]], adapter: NSEAdapter, root_dir: Path
    ) -> int:
        # 1. Try Screener (Primary)
        cat_folder = root_dir / "credit_rating"  # Matches config constant value
        cat_folder.mkdir(parents=True, exist_ok=True)

        primary_count = download_credit_ratings_from_screener(symbol, root_dir)
        if primary_count > 0:
            return primary_count

        # 2. Fallback to NSE announcements
        count = 0
        downloaded_files = set(f.name for f in cat_folder.glob("*"))

        for item in announcements:
            if self._matches_filter("credit_rating", item):
                url = item.get("attchmntFile")
                if not url:
                    continue
                filename = url.split("/")[-1]
                if filename in downloaded_files:
                    continue

                if adapter.download_document(url, cat_folder):
                    count += 1
                    downloaded_files.add(filename)
        return count

    def _process_issue_documents(
        self,
        symbol: str,
        adapter: NSEAdapter,
        root_dir: Path,
    ) -> Dict[str, int]:
        """Fetch and download all issue documents for a company.

        Iterates over all issue document types (offer docs for rights and QIP issues,
        info memo, scheme of arrangement docs), fetches each API endpoint, filters for
        the given symbol, and downloads all available attachments.

        Args:
            symbol: Stock symbol (e.g., 'HDFCBANK').
            adapter: Initialized NSEAdapter with active session.
            root_dir: Root download directory for this symbol.

        Returns:
            Dict mapping document type labels to download counts.
        """
        issue_dir = root_dir / ISSUE_DOCS_FOLDER
        issue_dir.mkdir(parents=True, exist_ok=True)

        # Resolve company name for endpoints where symbol is unreliable
        company_name = adapter.get_company_name(symbol)
        logger.info(f"Resolved company name for {symbol}: '{company_name}'")

        counts: Dict[str, int] = {}

        for doc_type, config in ISSUE_DOCS_CONFIG.items():
            label = config["label"]
            api_path = config["api_path"]
            api_params = config["api_params"]
            attachment_fields = config["attachment_fields"]
            subfolder = config["subfolder"]
            symbol_reliable = config["symbol_reliable"]

            # Fetch all documents from this endpoint
            documents = adapter.get_issue_documents(api_path, api_params)
            if not documents:
                logger.info(f"No {label} records returned from API")
                counts[label] = 0
                continue

            # Filter for matching records
            matching = []
            if symbol_reliable:
                # Match on symbol field directly
                matching = [
                    doc
                    for doc in documents
                    if str(doc.get("symbol", "")).strip().upper() == symbol.upper()
                ]
            else:
                # Match on company name (primary method for offer docs & info memo)
                if company_name:
                    company_lower = company_name.strip().lower()
                    matching = [
                        doc
                        for doc in documents
                        if company_lower in str(doc.get("company", "")).strip().lower()
                        or str(doc.get("company", "")).strip().lower() in company_lower
                    ]

            if not matching:
                logger.info(f"No {label} found for {symbol}")
                counts[label] = 0
                continue

            # Download attachments
            doc_folder = issue_dir / subfolder
            doc_folder.mkdir(parents=True, exist_ok=True)

            count = 0
            for doc in matching:
                for field in attachment_fields:
                    url = str(doc.get(field, "") or "").strip()
                    if not url or url == "-" or url == "null":
                        continue

                    if adapter.download_and_extract(url, doc_folder):
                        count += 1

            counts[label] = count
            logger.info(f"Downloaded {count} {label} file(s) for {symbol}")

        return counts
