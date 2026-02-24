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

    This class orchestrates the retrieval and parsing of XBRL filings. It leverages
    `NSEAdapter` for robust network interactions (mimicking browser behavior) and
    `arelle` for parsing the raw XBRL XML files using official NSE taxonomies.

    Attributes:
        adapter (NSEAdapter): The adapter instance used for network requests.
        taxonomy_manager (TaxonomyManager): Manager for handling taxonomy downloading and caching.
    """

    def __init__(self, nse_adapter: Optional[NSEAdapter] = None):
        """Initialize the harvester.

        Args:
            nse_adapter: An existing `NSEAdapter` instance. If `None`, a default instance
                configured with a temporary directory will be created. In production, it is
                recommended to inject a configured adapter.
        """
        if nse_adapter:
            self.adapter = nse_adapter
        else:
            # Default to a temp path if no adapter provided (fallback behavior)
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
        """Fetch a list of XBRL announcements for a symbol and type.

        Uses the NSE internal API `/api/XBRL-announcements` to retrieve metadata about filings.

        Args:
            symbol: The NSE stock symbol (e.g., 'TATAMOTORS').
            announcement_type: The specific XBRL type code (e.g., 'Reg30').
            start_date: Start date for filtering in 'dd-MM-yyyy' format.
            end_date: End date for filtering in 'dd-MM-yyyy' format.

        Returns:
            A list of dictionaries, where each dictionary represents an announcement
            and contains metadata such as 'appId' and 'attachment'. Returns an empty list on failure.
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
            logger.warning(f"Unexpected response format for {announcement_type}: {type(result)}")
        return []

    def _fallback_internal_api(self, app_id: str, announcement_type: str) -> Dict[str, Any]:
        """Fetch parsed details from NSE's internal XBRL API.

        This method acts as a fallback when Arelle parsing fails (e.g., due to missing schemas
        in the taxonomy package). It hits the NSE endpoint that returns pre-parsed JSON.
        Note that the keys in this JSON are internal technical keys and not always human-readable.

        Args:
            app_id: The unique application ID of the filing.
            announcement_type: The filing type code.

        Returns:
            A dictionary containing the raw parsed data from the NSE internal API, or an empty dict on failure.
        """
        logger.warning(f"Using fallback Internal API for {app_id} ({announcement_type})...")
        url = f"{self.adapter.nse.base_url}/XBRL-announcements"
        params = {"type": announcement_type, "appId": app_id}

        result = self.adapter.fetch_json(url, params)
        if result:
            return result
        return {}

    def _find_schema_ref(self, xbrl_content: bytes) -> Optional[str]:
        """Extract the schemaRef href from XBRL content using regex.

        Helper method to identify which XSD schema the XBRL instance refers to.

        Args:
            xbrl_content: Raw bytes content of the XBRL file.

        Returns:
            The href string (e.g., 'in-capmkt-ent-2023-12-31.xsd') if found, else None.
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
        """Download and parse an XBRL filing using Arelle.

        Downloads the XBRL XML file and attempts to parse it using the cached taxonomy
        for the given type. It handles complex relative path resolution by setting up
        a temporary environment where the XML file acts as a sibling to the schema.

        If parsing fails (e.g., due to missing schemas in the taxonomy), it attempts to
        use the fallback internal API if `app_id` is provided.

        Args:
            xbrl_url: URL to the raw XBRL XML filing.
            announcement_type: The filing type code (e.g., 'fundRaising').
            app_id: Optional App ID used for the fallback mechanism if parsing fails.

        Returns:
            A dictionary of parsed facts, where keys are human-readable labels (if resolvable)
            or QNames, and values are the fact values. Returns empty dict on total failure.
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
            # Use 'logToBuffer' to prevent Arelle from spamming stdout
            cntlr = Cntlr.Cntlr(logFileName="logToBuffer")
            cntlr.modelManager.validate = True

            model_xbrl = None
            try:
                # Load the model
                # This performs validation and schema loading
                model_xbrl = cntlr.modelManager.load(str(final_xbrl_path))
            except Exception as e:
                logger.error(f"Arelle failed to load XBRL: {e}")
                if cntlr:
                    cntlr.close()
                if app_id:
                    return self._fallback_internal_api(app_id, announcement_type)
                return {}

            # Check for critical failures (None or no facts)
            # 0 facts typically indicates schema loading failure where instance was invalid against empty schema
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

                # Attempt to get human-readable label
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
        """Harvest and parse XBRL data for a given symbol.

        Iterates through the requested announcement types, fetches filings within the date range,
        and parses them into a structured format.

        Args:
            symbol: The NSE stock symbol (e.g., 'RELIANCE').
            types: Optional list of XBRL type codes to fetch (e.g., ['Reg30']).
                   If None, fetches all supported types defined in `XBRL_TYPES`.
            start_date: Start date for filtering in 'dd-MM-yyyy' format.
            end_date: End date for filtering in 'dd-MM-yyyy' format.

        Returns:
            A dictionary where keys are the type codes (e.g., 'Reg30') and values are lists
            of dictionaries, each representing a parsed filing with metadata and 'xbrl_data'.
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
