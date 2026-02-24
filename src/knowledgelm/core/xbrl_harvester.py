import logging
import os
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from arelle import Cntlr

from knowledgelm.core.taxonomy_manager import TaxonomyManager
from knowledgelm.data.nse_adapter import NSEAdapter

logger = logging.getLogger(__name__)

# Map of major XBRL announcement types
XBRL_TYPES = {
    "Reg30": "Restructuring (Reg 30)",
    "announcements": "Change in Personnel",
    "outcome": "Board Meeting Outcomes",
    "fundRaising": "Issuance of Securities",
    "agr": "Agreements/Contracts",
    "award": "Orders & Contracts",
    "annFraud": "Fraud/Default",
    "cdr": "Corporate Debt Restructuring",
    "shm": "Shareholder Meetings",
    "CIRP": "Insolvency (IBC)",
    "annOts": "One Time Settlement",
}

# New logical grouping for UI and CLI
XBRL_CATEGORIES = {
    "Change in Personnel": ["announcements"],
    "Key announcements": [
        "Reg30",
        "fundRaising",
        "agr",
        "award",
        "annFraud",
        "cdr",
        "CIRP",
        "annOts",
    ],
    "Board Meeting Outcome": ["outcome"],
    "Shareholder Meetings": ["shm"],
}


class NSEXBRLHarvester:
    """Harvester for NSE XBRL filings via internal API and Arelle parser.

    Leverages NSEAdapter for network interactions and Arelle for XBRL parsing.
    """

    def __init__(self, nse_adapter: Optional[NSEAdapter] = None):
        """Initialize the harvester.

        Args:
            nse_adapter: Existing NSEAdapter instance. If None, one will be created.
        """
        if nse_adapter:
            self.adapter = nse_adapter
        else:
            # Default to a temp path if no adapter provided (fallback behavior)
            # In production, adapter should be injected
            logger.warning("No NSEAdapter provided to Harvester. Creating default one.")
            self.adapter = NSEAdapter(Path(tempfile.gettempdir()))

        # Taxonomy Manager initialized with adapter
        self.taxonomy_manager = TaxonomyManager(self.adapter)

    def get_announcements_by_type(
        self,
        symbol: str,
        announcement_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch announcement list for a symbol and type using NSEAdapter.

        Args:
            symbol: NSE Symbol.
            announcement_type: Type code.
            start_date: DD-MM-YYYY start date.
            end_date: DD-MM-YYYY end date.

        Returns:
            List of announcement dicts.
        """
        url = f"{self.adapter.nse.base_url}/XBRL-announcements"
        params = {
            "index": "equities",
            "symbol": symbol,
            "type": announcement_type,
        }

        if start_date:
            params["from_date"] = start_date
        if end_date:
            params["to_date"] = end_date

        result = self.adapter.fetch_json(url, params)
        if result and isinstance(result, list):
            return result
        # Handle case where API returns error JSON or None
        if result:
            # Sometimes API returns dict on error?
            logger.warning(f"Unexpected response format for {announcement_type}: {type(result)}")
        return []

    def _fallback_internal_api(self, app_id: str, announcement_type: str) -> Dict[str, Any]:
        """Fetch parsed details from NSE's internal XBRL API (The "Cheat" method).

        Used when Arelle parsing fails due to missing schemas or taxonomy issues.
        Returns the raw, unmapped JSON from NSE.

        Args:
            app_id: The unique application ID of the filing.
            announcement_type: The filing type code.

        Returns:
            Dictionary containing raw parsed data from NSE internal API.
        """
        logger.warning(f"Using fallback Internal API for {app_id} ({announcement_type})...")
        url = f"{self.adapter.nse.base_url}/XBRL-announcements"
        params = {"type": announcement_type, "appId": app_id}

        result = self.adapter.fetch_json(url, params)
        if result:
            return result
        return {}

    def _find_schema_ref(self, xbrl_content: bytes) -> Optional[str]:
        """Simple helper to extract schemaRef href from XBRL content.

        Args:
            xbrl_content: Raw bytes content of the XBRL file.

        Returns:
            The href string if found, else None.
        """
        try:
            content_str = xbrl_content.decode("utf-8", errors="ignore")
            match = re.search(r'schemaRef[^>]*href=["\']([^"\']+)["\']', content_str)
            if match:
                return match.group(1)
        except Exception:
            pass
        return None

    def parse_xbrl(
        self, xbrl_url: str, announcement_type: str, app_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Download and parse XBRL using Arelle and cached taxonomies.

        If parsing fails (e.g., due to missing schemas in the taxonomy package),
        this method falls back to using the internal NSE API if `app_id` is provided.

        Args:
            xbrl_url: URL to the XBRL XML filing.
            announcement_type: The filing type code.
            app_id: Optional App ID for fallback mechanism.

        Returns:
            Dictionary of parsed facts (Label -> Value).
        """
        if not xbrl_url:
            if app_id:
                return self._fallback_internal_api(app_id, announcement_type)
            return {}

        taxonomy_dir = self.taxonomy_manager.get_taxonomy_dir(announcement_type)
        if not taxonomy_dir:
            logger.warning(f"Could not get taxonomy for {announcement_type}. Attempting fallback.")
            if app_id:
                return self._fallback_internal_api(app_id, announcement_type)
            return {}

        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            final_xbrl_path = temp_dir / "filing.xml"
            xbrl_content = b""

            # 1. Download XBRL XML using Adapter
            try:
                # Download to temp dir
                if not self.adapter.download_document(xbrl_url, temp_dir):
                    logger.error(f"Adapter failed to download XBRL: {xbrl_url}")
                    if app_id:
                        return self._fallback_internal_api(app_id, announcement_type)
                    return {}

                # Find the file (name might vary)
                downloaded_files = list(temp_dir.glob("*.xml"))
                if not downloaded_files:
                    logger.error("Downloaded file not found or not XML")
                    if app_id:
                        return self._fallback_internal_api(app_id, announcement_type)
                    return {}

                # Use the first XML file found
                actual_file_path = downloaded_files[0]

                # Read content for schema detection
                with open(actual_file_path, "rb") as f:
                    xbrl_content = f.read()

                # Rename to standard name for consistency logic below
                shutil.move(actual_file_path, final_xbrl_path)

            except Exception as e:
                logger.error(f"Error downloading/processing XBRL: {e}")
                if app_id:
                    return self._fallback_internal_api(app_id, announcement_type)
                return {}

            # 2. Find schemaRef inside the XBRL
            schema_ref = self._find_schema_ref(xbrl_content)

            # 3. Setup Taxonomy Environment
            # We copy the cached taxonomy into the temp dir to allow Arelle to resolve relative paths
            if taxonomy_dir and taxonomy_dir.exists() and schema_ref:
                found_schema_dir = None
                # Search for the specific schema file in the cached taxonomy
                for root, dirs, files in os.walk(taxonomy_dir):
                    if schema_ref in files:
                        found_schema_dir = Path(root)
                        break

                if found_schema_dir:
                    try:
                        # Copy entire taxonomy structure to temp
                        shutil.copytree(taxonomy_dir, temp_dir / "taxonomy", dirs_exist_ok=True)

                        # Find schema in the temp copy
                        temp_schema_dir = None
                        for root, dirs, files in os.walk(temp_dir / "taxonomy"):
                            if schema_ref in files:
                                temp_schema_dir = Path(root)
                                break

                        if temp_schema_dir:
                            # Move XML file to be a sibling of the schema
                            # This fixes relative path resolution for XSDs
                            new_xbrl_path = temp_schema_dir / "filing.xml"
                            shutil.move(final_xbrl_path, new_xbrl_path)
                            final_xbrl_path = new_xbrl_path
                    except Exception as e:
                        logger.warning(f"Failed to setup taxonomy environment: {e}")

            # 4. Initialize Arelle Controller
            cntlr = Cntlr.Cntlr(logFileName="logToBuffer")
            cntlr.modelManager.validate = True

            model_xbrl = None
            try:
                model_xbrl = cntlr.modelManager.load(str(final_xbrl_path))
            except Exception as e:
                logger.error(f"Arelle failed to load XBRL: {e}")
                if cntlr:
                    cntlr.close()
                if app_id:
                    return self._fallback_internal_api(app_id, announcement_type)
                return {}

            # Check for critical failures (None or no facts)
            if model_xbrl is None or len(model_xbrl.facts) == 0:
                logger.warning(
                    f"Arelle loaded model with {0 if model_xbrl is None else len(model_xbrl.facts)} facts. Switching to fallback."
                )
                if model_xbrl:
                    model_xbrl.close()
                cntlr.close()
                if app_id:
                    return self._fallback_internal_api(app_id, announcement_type)
                return {}

            parsed_data = {}
            for fact in model_xbrl.facts:
                label = str(fact.qname)

                if fact.concept is not None:
                    lbl = fact.concept.label(lang="en")
                    if lbl:
                        label = lbl
                    else:
                        lbl = fact.concept.label(
                            lang="en",
                            labelrole="http://www.xbrl.org/2003/role/verboseLabel",
                        )
                        if lbl:
                            label = lbl

                value = fact.value
                if value is None:
                    value = ""
                parsed_data[label] = value

            model_xbrl.close()
            cntlr.close()

            return parsed_data

    def harvest_xbrl(
        self,
        symbol: str,
        types: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Harvest XBRL data for a symbol.

        Args:
            symbol: NSE Symbol
            types: Optional list of specific types to fetch (e.g., ['Reg30']). Defaults to all.
            start_date: Start date 'dd-MM-yyyy'
            end_date: End date 'dd-MM-yyyy'

        Returns:
            Dictionary mapping type -> list of detailed filings
        """
        results = {}

        target_types = XBRL_TYPES
        if types:
            target_types = {k: v for k, v in XBRL_TYPES.items() if k in types}
            if not target_types:
                logger.warning(f"No valid XBRL types found in requested list: {types}")
                return {}

        logger.info(f"Harvesting XBRL data for {symbol} (Types: {list(target_types.keys())})...")

        for type_code, description in target_types.items():
            logger.info(f"Checking {description} ({type_code})...")
            announcements = self.get_announcements_by_type(symbol, type_code, start_date, end_date)

            if not announcements:
                continue

            logger.info(f"Found {len(announcements)} filings for {description}. Parsing details...")
            type_details = []

            for announcement in announcements:
                xbrl_url = announcement.get("attachment")
                app_id = announcement.get("appId")

                parsed_data = {}
                try:
                    parsed_data = self.parse_xbrl(xbrl_url, type_code, app_id=app_id)
                except Exception as e:
                    logger.error(f"Failed to parse XBRL for {xbrl_url}: {e}")
                    if app_id and not parsed_data:
                        parsed_data = self._fallback_internal_api(app_id, type_code)

                full_record = {**announcement, "xbrl_data": parsed_data}
                type_details.append(full_record)

                time.sleep(0.2)

            if type_details:
                results[type_code] = type_details

        return results
