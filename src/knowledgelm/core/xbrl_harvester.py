import logging
import os
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from nse_xbrl_parser import parse_xbrl_file

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
        if nse_adapter:
            self.adapter = nse_adapter
        else:
            # Default to a temp path if no adapter provided (fallback behavior)
            logger.warning("No NSEAdapter provided to Harvester. Creating default one.")
            self.adapter = NSEAdapter(Path(tempfile.gettempdir()))
            # Default to a temp path if no adapter provided (fallback behavior)
            logger.warning("No NSEAdapter provided to Harvester. Creating default one.")
            self.adapter = NSEAdapter(Path(tempfile.gettempdir()))

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
        """Fetch parsed details from NSE's internal XBRL API."""
        logger.warning(f"!!! SWITCHING TO INTERNAL API FALLBACK for {app_id} ({announcement_type}) !!!")
        url = f"{self.adapter.nse.base_url}/XBRL-announcements"
        params = {"type": announcement_type, "appId": app_id}

        result = self.adapter.fetch_json(url, params)
        if result:
            logger.info(f"Fallback successful for {app_id}.")
            return result
        logger.error(f"Fallback failed for {app_id}.")
        return {}

    def _find_schema_ref(self, xbrl_content: bytes) -> Optional[str]:
        """Find the schemaRef href inside the XBRL instance document.

        Uses robust XML-aware searching to handle namespaces and different
        formatting of the schemaRef element.

        Args:
            xbrl_content: Raw bytes content of the XBRL file.

        Returns:
            The href string (e.g., 'in-capmkt-ent-2023-12-31.xsd') if found, else None.
        """
        try:
            # We use a simple XML-aware search for the schemaRef tag
            # to be more robust than regex but faster than full LXML/playwright.
            import xml.etree.ElementTree as ET
            from io import BytesIO

            # Standard namespaces often used in XBRL
            # link:schemaRef is what we're looking for
            tree = ET.parse(BytesIO(xbrl_content))
            root = tree.getroot()

            # Find any tag ending in 'schemaRef' (to handle varying prefix namespaces)
            for elem in root.iter():
                if elem.tag.endswith("schemaRef"):
                    # Attributes can also be namespaced, e.g., {http://www.w3.org/1999/xlink}href
                    # We check for any attribute that ends with 'href'
                    href = None
                    for attr_key, attr_val in elem.attrib.items():
                        if attr_key.endswith("href") or attr_key == "href":
                            href = attr_val
                            break
                    if href:
                        return href

        except Exception as e:
            logger.debug(f"XML parsing for schemaRef failed: {e}. Falling back to regex.")
            # Fallback to regex if XML is malformed or parser fails
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

        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)

            # 1. Download XBRL filing using Adapter
            try:
                # We use download_and_extract which ensures complete extraction of ZIPs
                if not self.adapter.download_and_extract(xbrl_url, temp_dir):
                    logger.error(f"Adapter failed to download/extract XBRL filing: {xbrl_url}")
                    if app_id:
                        return self._fallback_internal_api(app_id, announcement_type)
                    return {}

                # 2. Find the actual XBRL instance (.xml)
                downloaded_xmls = []
                for ext in ["*.xml", "*.XML"]:
                    downloaded_xmls.extend(list(temp_dir.rglob(ext)))
                
                if not downloaded_xmls:
                    logger.error(f"No XBRL XML found in extracted content: {xbrl_url}")
                    if app_id:
                        return self._fallback_internal_api(app_id, announcement_type)
                    return {}

                logger.info(f"Found {len(downloaded_xmls)} XML file(s) in download.")

                actual_file_path = None
                for xml_file in downloaded_xmls:
                    name = xml_file.name.lower()
                    if not any(x in name for x in ["-pre", "-def", "-lab", "-cal", ".xsd", "schema", "taxonomy"]):
                        actual_file_path = xml_file
                        break
                
                if not actual_file_path:
                    actual_file_path = downloaded_xmls[0]

                logger.info(f"Using XBRL instance: {actual_file_path.relative_to(temp_dir)}")

                # Use the new standalone parser package!
                # All taxonomy and Arelle logic is safely abstracted there
                logger.info("Passing instance to nse-xbrl-parser...")
                parsed_data = parse_xbrl_file(actual_file_path)
                logger.info(f"Successfully parsed {len(parsed_data)} facts from XBRL.")
                
                return parsed_data

            except Exception as e:
                logger.error(f"Error processing XBRL filing via parser package: {e}")
                if app_id:
                    return self._fallback_internal_api(app_id, announcement_type)
                return {}

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
