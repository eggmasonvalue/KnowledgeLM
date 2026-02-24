import logging
import os
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from arelle import Cntlr
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from knowledgelm.core.taxonomy_manager import TaxonomyManager
from knowledgelm.utils.log_utils import redirect_stdout_to_logger

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
    """Harvester for NSE XBRL filings via internal API and Arelle parser."""

    def __init__(self):
        """Initialize the harvester."""
        self.base_url = "https://www.nseindia.com/api"
        # We need a session to hold cookies
        self.session = requests.Session()

        # Configure retry strategy
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        # Mimic a browser
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

        # Taxonomy Manager
        self.taxonomy_manager = TaxonomyManager()

        # Initial visit to set cookies
        try:
            with redirect_stdout_to_logger(logger):
                self.session.get("https://www.nseindia.com", timeout=10)
        except Exception as e:
            logger.warning(f"Failed to initialize session cookies: {e}")

    def get_announcements_by_type(
        self,
        symbol: str,
        announcement_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch announcement list for a symbol and type."""
        url = f"{self.base_url}/XBRL-announcements"
        params = {"index": "equities", "symbol": symbol, "type": announcement_type}

        if start_date:
            params["from_date"] = start_date
        if end_date:
            params["to_date"] = end_date

        try:
            with redirect_stdout_to_logger(logger):
                response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.info("Session expired, refreshing cookies...")
                with redirect_stdout_to_logger(logger):
                    self.session.get("https://www.nseindia.com", timeout=10)
                    response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    return response.json()

            logger.error(f"Error fetching list for {announcement_type}: {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Exception fetching list: {e}")
            return []

    def _fallback_internal_api(self, app_id: str, announcement_type: str) -> Dict[str, Any]:
        """Fetch parsed details from NSE's internal XBRL API (The "Cheat" method)."""
        logger.warning(f"Using fallback Internal API for {app_id} ({announcement_type})...")
        url = f"{self.base_url}/XBRL-announcements"
        params = {"type": announcement_type, "appId": app_id}

        try:
            with redirect_stdout_to_logger(logger):
                response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                # Returns unmapped JSON directly
                return response.json()
            logger.error(f"Fallback API failed for {app_id}: {response.status_code}")
            return {}
        except Exception as e:
            logger.error(f"Exception in fallback API: {e}")
            return {}

    def _find_schema_ref(self, xbrl_content: bytes) -> Optional[str]:
        """Simple helper to extract schemaRef href from XBRL content."""
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
        """Download and parse XBRL using Arelle and cached taxonomies."""
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

            # 1. Download XBRL XML
            xbrl_content = b""
            try:
                response = self.session.get(xbrl_url, stream=True, timeout=30)
                if response.status_code != 200:
                    logger.error(f"Failed to download XBRL: {response.status_code}")
                    if app_id:
                        return self._fallback_internal_api(app_id, announcement_type)
                    return {}
                xbrl_content = response.content
            except Exception as e:
                logger.error(f"Error downloading XBRL: {e}")
                if app_id:
                    return self._fallback_internal_api(app_id, announcement_type)
                return {}

            # 2. Find schemaRef inside the XBRL
            schema_ref = self._find_schema_ref(xbrl_content)
            final_xbrl_path = temp_dir / "filing.xml"

            with open(final_xbrl_path, "wb") as f:
                f.write(xbrl_content)

            # 3. Setup Taxonomy Environment
            if taxonomy_dir and taxonomy_dir.exists() and schema_ref:
                # Find where schema is located
                found_schema_dir = None
                for root, dirs, files in os.walk(taxonomy_dir):
                    if schema_ref in files:
                        found_schema_dir = Path(root)
                        break

                if found_schema_dir:
                    try:
                        # Copy taxonomy to temp to maintain relative paths
                        shutil.copytree(taxonomy_dir, temp_dir / "taxonomy", dirs_exist_ok=True)

                        # Find schema in temp copy
                        temp_schema_dir = None
                        for root, dirs, files in os.walk(temp_dir / "taxonomy"):
                            if schema_ref in files:
                                temp_schema_dir = Path(root)
                                break

                        if temp_schema_dir:
                            # Move XML file to be a sibling of the schema
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
                            lang="en", labelrole="http://www.xbrl.org/2003/role/verboseLabel"
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
        """Harvest XBRL data for a symbol."""
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
                    # Pass app_id so fallback can be triggered internally if Arelle fails
                    parsed_data = self.parse_xbrl(xbrl_url, type_code, app_id=app_id)
                except Exception as e:
                    logger.error(f"Failed to parse XBRL for {xbrl_url}: {e}")
                    # Last ditch effort
                    if app_id and not parsed_data:
                        parsed_data = self._fallback_internal_api(app_id, type_code)

                full_record = {**announcement, "xbrl_data": parsed_data}
                type_details.append(full_record)

                time.sleep(0.2)

            if type_details:
                results[type_code] = type_details

        return results
