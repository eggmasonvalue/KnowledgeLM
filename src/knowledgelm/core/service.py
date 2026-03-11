"""Core service logic for KnowledgeLM."""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

from knowledgelm.config import (
    DATE_FORMAT_DMY_DASH,
    DATE_FORMAT_DMY_HM,
    DATE_FORMAT_DMY_HMS,
    DEFAULT_FILE_EXT,
    DOWNLOAD_CATEGORIES_CONFIG,
    FILTER_ANALYST_MEET,
    FILTER_CREDIT_RATING,
    FILTER_INVESTOR_PRESENTATION,
    FILTER_PRESS_RELEASE,
    FILTER_RELATED_PARTY_TXNS,
    ISSUE_DOCS_CONFIG,
)
from knowledgelm.core.xbrl_harvester import XBRL_CATEGORIES, NSEXBRLHarvester
from knowledgelm.data.nse_adapter import NSEAdapter
from knowledgelm.data.screener_adapter import download_credit_ratings_from_screener
from knowledgelm.utils.file_utils import generate_standard_filename, get_download_path

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
        # Initialize an NSEAdapter that uses the base_path as its working directory
        self.nse_adapter = NSEAdapter(self.base_path)

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
        logger.info(f"Starting processing request for {symbol} ({from_date} - {to_date})")

        # 1. Setup Folder
        # Assuming the service is initialized with a base path (like CWD),
        # get_download_path sanitizes and joins.
        try:
            download_dir = get_download_path(str(self.base_path), folder_name)
            download_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Output directory: {download_dir}")
        except ValueError as e:
            logger.error(f"Invalid folder name: {e}")
            raise

        nse_adapter = NSEAdapter(download_dir)

        # 1.5 Validate Symbol
        if not nse_adapter.validate_symbol(symbol):
            raise ValueError(f"Symbol '{symbol}' is invalid or not found on NSE.")

        # 2. Lazy Fetch Announcements
        _cached_announcements = None

        def get_general_announcements() -> List[Dict[str, Any]]:
            nonlocal _cached_announcements
            if _cached_announcements is None:
                _cached_announcements = nse_adapter.get_announcements(symbol, from_date, to_date)
                logger.info(f"Fetched {len(_cached_announcements)} total announcements.")
            return _cached_announcements

        category_counts = {}

        # 3. Process Categories
        for cat_key, config in DOWNLOAD_CATEGORIES_CONFIG.items():
            if not options.get(config["enabled_arg"], False):
                continue

            label = config["label"]
            logger.info(f"Processing category: {label}")

            # Special Case: Annual Reports
            if cat_key == "annual_reports":
                count = self._process_annual_reports(
                    symbol, nse_adapter, download_dir, from_date, to_date, annual_reports_all_mode
                )
                category_counts[label] = count
                logger.info(f"Completed {label}: {count} items.")
                continue

            # Special Case: Credit Ratings
            if cat_key == "credit_rating":
                count = self._process_credit_ratings(
                    symbol, get_general_announcements, nse_adapter, download_dir
                )
                category_counts[label] = count
                logger.info(f"Completed {label}: {count} items.")
                continue

            # Special Case: Issue Documents
            if cat_key == "issue_documents":
                issue_counts = self._process_issue_documents(symbol, nse_adapter, download_dir)
                category_counts.update(issue_counts)
                # logging handled inside _process_issue_documents per sub-type
                continue

            # Special Case: XBRL Categories
            if config.get("is_xbrl"):
                count = self._process_xbrl_category(
                    symbol,
                    cat_key,
                    config["xbrl_cat"],
                    download_dir,
                    from_date,
                    to_date,
                    nse_adapter,
                )
                category_counts[label] = count
                logger.info(f"Completed {label}: {count} items.")
                continue

            # Standard Categories - apply filter and download matching items

            cat_folder = download_dir / config.get("folder_name", cat_key)
            cat_folder.mkdir(parents=True, exist_ok=True)

            count = 0
            for item in get_general_announcements():
                if self._matches_filter(cat_key, item):
                    url = item.get("attchmntFile")
                    if url:
                        ext = Path(url.split("?")[0]).suffix or DEFAULT_FILE_EXT
                        dt_str = item.get("an_dt", "")
                        shorthand = config.get("shorthand", cat_key)
                        file_name = f"{generate_standard_filename(dt_str, shorthand)}{ext}"
                        if nse_adapter.download_and_extract(url, cat_folder, file_name):
                            count += 1
            category_counts[label] = count
            logger.info(f"Completed {label}: {count} items.")

        logger.info(f"Processing request for {symbol} complete.")
        return _cached_announcements or [], category_counts

    def _matches_filter(self, category: str, item: Dict[str, Any]) -> bool:
        """Check if an item matches the category filter."""
        desc = str(item.get("desc", "")).strip().lower()
        attortext = str(item.get("attchmntText", "")).lower()
        has_file = bool(item.get("attchmntFile"))

        if not has_file:
            return False

        if category == "transcripts":
            return desc == FILTER_ANALYST_MEET and "transcript" in attortext
        elif category == "investor_presentations":
            return desc == FILTER_INVESTOR_PRESENTATION
        elif category == "press_releases":
            return desc in FILTER_PRESS_RELEASE
        elif category == "credit_rating":
            return desc == FILTER_CREDIT_RATING
        elif category == "related_party_txns":
            return desc in FILTER_RELATED_PARTY_TXNS

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
        """Fetch and download annual reports for the given symbol.

        Filters reports based on the provided date range unless `all_mode` is True.

        Args:
            symbol: Stock symbol.
            adapter: Initialized NSEAdapter instance.
            root_dir: Root download directory for this symbol.
            from_date: Start date for filtering.
            to_date: End date for filtering.
            all_mode: If True, downloads all available reports ignoring the date range.

        Returns:
            The number of annual reports downloaded.
        """
        ar_config = DOWNLOAD_CATEGORIES_CONFIG.get("annual_reports", {})
        folder_name = ar_config.get("folder_name", "annual_reports")
        shorthand = ar_config.get("shorthand", "AR")
        ar_folder = root_dir / folder_name
        ar_folder.mkdir(parents=True, exist_ok=True)
        count = 0

        logger.info("Fetching annual reports metadata...")
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

                logger.info(f"Downloading Annual Report for {yr}...")
                ext = Path(url.split("?")[0]).suffix or DEFAULT_FILE_EXT
                file_name = f"{generate_standard_filename(str(yr), shorthand)}{ext}"
                if adapter.download_and_extract(url, ar_folder, file_name):
                    count += 1
        return count

    def _process_credit_ratings(
        self, symbol: str, get_announcements_func: callable, adapter: NSEAdapter, root_dir: Path
    ) -> int:
        """Fetch and download credit ratings from Screener.in.

        Screener.in is used as the sole source for credit ratings as it provides
        high-fidelity PDF conversion and historical records.

        Args:
            symbol: Stock symbol.
            get_announcements_func: Callable to get general announcements (unused,
                kept for signature compatibility).
            adapter: Initialized NSEAdapter.
            root_dir: Root download directory.

        Returns:
            Number of documents downloaded.
        """
        # 1. Try Screener (Sole Source)
        cat_folder = root_dir / "credit_rating"  # Matches config constant value
        cat_folder.mkdir(parents=True, exist_ok=True)

        primary_count = download_credit_ratings_from_screener(symbol, root_dir)
        return primary_count

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
        issue_cat_config = DOWNLOAD_CATEGORIES_CONFIG.get("issue_documents", {})
        issue_folder_name = issue_cat_config.get("folder_name", "share_issuance_docs")
        issue_dir = root_dir / issue_folder_name
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
            company_lower = company_name.strip().lower() if company_name else ""
            matching = []

            for doc in documents:
                doc_symbol = str(doc.get("symbol", "")).strip().upper()
                doc_company = str(doc.get("company", "")).strip().lower()

                if symbol_reliable:
                    if doc_symbol == symbol.upper():
                        matching.append(doc)
                elif company_lower:
                    # Tightened matching: Ensure company name is a significant part of the record
                    # or matches exactly to prevent "Bank of India" matching "State Bank of India"
                    if company_lower == doc_company or (
                        len(company_lower) > 5 and company_lower in doc_company
                    ):
                        matching.append(doc)

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
                    # Robust check for invalid placeholders and trailing dashes
                    if not url or url.lower() in ["-", "null", "nan"] or url.endswith("/-"):
                        continue

                    # Attempt to extract some temporal info from doc (e.g. fileDate, date_attachmnt)
                    temporal = str(doc.get("fileDate", doc.get("date_attachmnt", "")))
                    ext = Path(url.split("?")[0]).suffix or DEFAULT_FILE_EXT
                    shorthand = config.get("shorthand", "IssueDoc")
                    file_name = f"{generate_standard_filename(temporal, shorthand)}{ext}"

                    if adapter.download_and_extract(url, doc_folder, file_name):
                        count += 1

            counts[label] = count
            logger.info(f"Downloaded {count} {label} file(s) for {symbol}")

        return counts

    def _process_xbrl_category(
        self,
        symbol: str,
        cat_key: str,
        xbrl_cat: str,
        download_dir: Path,
        from_date: datetime,
        to_date: datetime,
        adapter: NSEAdapter,
    ) -> int:
        """Fetch XBRL data and save it as a JSON file in the category folder."""
        records = self.get_xbrl_data(symbol, xbrl_cat, from_date, to_date)
        if not records:
            return 0

        # Special processing for Shareholder Meetings (SHM) to extract resolutions
        if cat_key == "shm":
            self._enrich_shm_records(records, symbol, adapter, download_dir)

        # Filter output fields based on configuration
        output_keys = DOWNLOAD_CATEGORIES_CONFIG.get(cat_key, {}).get("output_keys")
        if output_keys:
            records = [{k: r[k] for k in output_keys if k in r} for r in records]

        # Save to JSON
        import json

        if cat_key == "personnel":
            output_file = download_dir / "personnel_changes.json"
        elif cat_key == "key_announcements":
            output_file = download_dir / "key_announcements.json"
        elif cat_key == "shm":
            shm_dir = download_dir / "shareholder_meetings"
            shm_dir.mkdir(parents=True, exist_ok=True)
            output_file = shm_dir / "shm_details.json"
        else:
            output_file = download_dir / f"{cat_key}_details.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

        return len(records)

    def _enrich_shm_records(
        self, records: List[Dict], symbol: str, adapter: NSEAdapter, download_dir: Path
    ):
        """Enrich Shareholder Meeting (SHM) records with resolution details from PDF notices.

        Fetches general announcements around the broadcast date of the SHM XBRL record
        to find the corresponding PDF notice. Evaluates candidates based on their description
        and stores the path to the downloaded PDF in the record.

        Args:
            records: List of parsed SHM XBRL records to enrich.
            symbol: Stock symbol.
            adapter: Initialized NSEAdapter for fetching announcements and documents.
            download_dir: Root download directory for this symbol.
        """
        # We need general announcements to find the PDF.
        # Since we have a list of records, we can determine the date range needed.
        if not records:
            return

        try:
            dates = []
            for r in records:
                dt_str = r.get("broadcastDateTime")
                if dt_str:
                    try:
                        dt = datetime.strptime(dt_str, DATE_FORMAT_DMY_HMS)
                        dates.append(dt)
                    except ValueError:
                        pass

            if not dates:
                return

            min_date = min(dates)
            max_date = max(dates)

            # Pad by a few days to find matching general announcements
            search_start = min_date - timedelta(days=5)
            search_end = max_date + timedelta(days=5)

            logger.info(
                f"Fetching general announcements for SHM PDF matching "
                f"({search_start} to {search_end})..."
            )
            # Use a fresh fetch to ensure we have the data
            general_anns = adapter.get_announcements(symbol, search_start, search_end)

        except Exception as e:
            logger.error(f"Failed to fetch general announcements for enrichment: {e}")
            return

        # Pre-parse general announcements dates for matching
        parsed_anns = []
        for g_ann in general_anns:
            g_dt_str = g_ann.get("an_dt", "")
            if not g_dt_str:
                continue
            try:
                g_dt = datetime.strptime(g_dt_str, DATE_FORMAT_DMY_HMS)
                parsed_anns.append((g_ann, g_dt))
            except ValueError:
                continue

        for record in records:
            # Check if it's a Notice
            sub_ann = record.get("subOfAnn", "")
            if "Notice" not in sub_ann:
                continue

            logger.info(f"Processing SHM Notice: {sub_ann}")

            # Find matching PDF
            xbrl_dt_str = record.get("broadcastDateTime")
            if not xbrl_dt_str:
                continue

            try:
                xbrl_dt = datetime.strptime(xbrl_dt_str, DATE_FORMAT_DMY_HMS)
            except ValueError:
                continue

            target_pdf_url = None

            # Look for match in general_anns
            candidates = []
            for g_ann, g_dt in parsed_anns:
                # Date Match: +/- 2 days
                diff = abs((g_dt - xbrl_dt).days)
                if diff <= 2:
                    candidates.append(g_ann)

            # Filter candidates to find the best PDF match
            best_candidate = None

            for cand in candidates:
                url = cand.get("attchmntFile", "")
                if not url or not url.lower().endswith(DEFAULT_FILE_EXT):
                    continue

                desc = cand.get("desc", "").lower()
                text = cand.get("attchmntText", "").lower()

                # Exclusions
                if "advertisement" in desc or "newspaper" in desc:
                    continue

                # Scoring
                score = 0
                if "notice" in desc:
                    score += 2
                if "notice" in text:
                    score += 1
                if "shareholder" in desc:
                    score += 1
                if "postal ballot" in text:
                    score += 3

                # Check for "Ad" in filename as a negative signal (e.g. PostalBallotAd.pdf)
                if f"ad{DEFAULT_FILE_EXT}" in url.lower() or "_ad" in url.lower():
                    score -= 5

                if score > 0:
                    # If we don't have a candidate yet, or this one is better
                    if best_candidate is None or score > best_candidate[0]:
                        best_candidate = (score, url)

            if best_candidate:
                target_pdf_url = best_candidate[1]
                logger.info(f"Found matching PDF: {target_pdf_url}")

                shm_config = DOWNLOAD_CATEGORIES_CONFIG.get("shm", {})
                shorthand = shm_config.get("shorthand", "SHM")

                # Download to shm folder instead of temp
                shm_folder = shm_config.get("folder_name", "shareholder_meetings")
                shm_dir = download_dir / shm_folder / "shm_notices"
                shm_dir.mkdir(parents=True, exist_ok=True)

                ext = Path(target_pdf_url.split("?")[0]).suffix or DEFAULT_FILE_EXT
                file_name = f"{generate_standard_filename(xbrl_dt_str, shorthand)}{ext}"

                if adapter.download_and_extract(target_pdf_url, shm_dir, file_name):
                    # The file was saved as file_name
                    pdf_path = shm_dir / file_name

                    if pdf_path.exists():
                        try:
                            # record["pdf_url"] = target_pdf_url
                            record["local_pdf_path"] = str(pdf_path.absolute())
                        except Exception as e:
                            logger.error(f"Failed to process PDF: {e}")
                    else:
                        logger.error("Downloaded PDF not found.")
            else:
                logger.warning(f"No matching PDF found for SHM Notice dated {xbrl_dt}")

    def get_xbrl_data(
        self,
        symbol: str,
        category: str,
        from_date: datetime,
        to_date: datetime,
    ) -> List[Dict[str, Any]]:
        """Fetch and group XBRL data for a specific category.

        Args:
            symbol: Stock symbol.
            category: One of the keys in XBRL_CATEGORIES.
            from_date: Start date.
            to_date: End date.

        Returns:
            List of flattened XBRL records for the requested category.
        """
        if category not in XBRL_CATEGORIES:
            logger.warning(f"Unknown XBRL category: {category}")
            return []

        harvester = NSEXBRLHarvester(nse_adapter=self.nse_adapter)
        types = XBRL_CATEGORIES[category]

        # Convert datetime to dd-mm-yyyy for the harvester
        start_str = from_date.strftime(DATE_FORMAT_DMY_DASH)
        end_str = to_date.strftime(DATE_FORMAT_DMY_DASH)

        raw_results = harvester.harvest_xbrl(
            symbol=symbol,
            types=types,
            start_date=start_str,
            end_date=end_str,
        )

        # Flatten the dictionary results into a single list
        flattened = []
        for type_code, records in raw_results.items():
            for record in records:
                # Add category info to each record
                record["xbrl_category"] = category
                record["xbrl_type_code"] = type_code
                flattened.append(record)

        # Sort by date descending if possible
        try:
            flattened.sort(
                key=lambda x: datetime.strptime(x.get("an_dt", ""), DATE_FORMAT_DMY_HM),
                reverse=True,
            )
        except Exception:
            pass

        return flattened
