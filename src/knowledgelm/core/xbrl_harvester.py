import os
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pathlib import Path

from knowledgelm.utils.log_utils import redirect_stdout_to_logger

logger = logging.getLogger(__name__)

# Map of major XBRL announcement types
# Map each type code to a description
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
    """Harvester for NSE XBRL filings via internal API."""

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
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
        })
        
        # Load XBRL Labels Mapping
        self.label_map = {}
        try:
            # Assuming JSON is in src/knowledgelm/xbrl_mapping_bundle/xbrl_labels.json relative to this file
            current_dir = Path(__file__).parent
            # this file is in src/knowledgelm/core/xbrl_harvester.py
            # we want src/knowledgelm/xbrl_mapping_bundle/xbrl_labels.json
            mapping_path = current_dir.parent / "xbrl_mapping_bundle" / "xbrl_labels.json"
            if mapping_path.exists():
                with open(mapping_path, "r", encoding="utf-8") as f:
                    self.label_map = json.load(f)
                logger.info(f"Loaded {len(self.label_map)} XBRL labels.")
            else:
                logger.warning(f"XBRL mapping file not found at {mapping_path}")
        except Exception as e:
            logger.error(f"Failed to load XBRL labels: {e}")

        # Initial visit to set cookies
        try:
            with redirect_stdout_to_logger(logger):
                self.session.get("https://www.nseindia.com", timeout=10)
        except Exception as e:
            logger.warning(f"Failed to initialize session cookies: {e}")

    def _apply_mapping(self, data: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
        """Recursively map keys in the data structure using label_map."""
        if isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                # Map key if exists, else keep original
                new_key = self.label_map.get(k, k)
                new_dict[new_key] = self._apply_mapping(v)
            return new_dict
        elif isinstance(data, list):
            return [self._apply_mapping(item) for item in data]
        else:
            return data

    def get_announcements_by_type(
        self, 
        symbol: str, 
        announcement_type: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch announcement list for a symbol and type.

        Args:
            symbol: NSE Symbol (e.g., 'TATAMOTORS')
            announcement_type: One of the keys in XBRL_TYPES
            start_date: Start date in 'dd-MM-yyyy' format (e.g., '01-01-2024')
            end_date: End date in 'dd-MM-yyyy' format

        Returns:
            List of announcement dictionaries containing the 'appId'
        """
        url = f"{self.base_url}/XBRL-announcements"
        params = {
            "index": "equities",
            "symbol": symbol,
            "type": announcement_type
        }
        
        if start_date:
            params["from_date"] = start_date
        if end_date:
            params["to_date"] = end_date
        
        try:
            with redirect_stdout_to_logger(logger):
                response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # The API returns a list of objects
                return data
            elif response.status_code == 401:
                logger.info("Session expired, refreshing cookies...")
                # Refresh session if unauthorized
                with redirect_stdout_to_logger(logger):
                    self.session.get("https://www.nseindia.com", timeout=10)
                    response = self.session.get(url, params=params, timeout=10)
                return response.json()
                
            logger.error(f"Error fetching list for {announcement_type}: {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Exception fetching list: {e}")
            return []

    def get_xbrl_details(self, app_id: str, announcement_type: str) -> Dict[str, Any]:
        """Fetch the detailed parsed JSON for a specific filing.

        Args:
            app_id: The unique ID of the announcement
            announcement_type: The type category (needed for the API call)

        Returns:
            Dictionary containing the parsed XBRL data with mapped labels
        """
        url = f"{self.base_url}/XBRL-announcements"
        params = {
            "type": announcement_type,
            "appId": app_id
        }
        
        try:
            with redirect_stdout_to_logger(logger):
                response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                raw_data = response.json()
                return self._apply_mapping(raw_data)
            logger.error(f"Error fetching details for {app_id}: {response.status_code}")
            return {}
        except Exception as e:
            logger.error(f"Exception fetching details: {e}")
            return {}

    def harvest_xbrl(
        self, 
        symbol: str, 
        types: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
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
            # Filter main dict by requested keys that exist
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
                
            logger.info(f"Found {len(announcements)} filings for {description}. Fetching details...")
            type_details = []
            
            for announcement in announcements:
                # The ID is typically in 'id' field, but inspection shows 'appId'
                api_id = announcement.get('appId') 
                if not api_id:
                    continue
                    
                details = self.get_xbrl_details(str(api_id), type_code)
                if details:
                    # Merge metadata from the list view into the details
                    full_record = {**announcement, "xbrl_data": details}
                    type_details.append(full_record)
                
                # Be nice to the server
                time.sleep(0.2)
            
            if type_details:
                results[type_code] = type_details
                
        return results

def test_harvest(symbol: str = "NRBBEARING"):
    """Run a test harvest for a symbol."""
    # Configure logging to stdout for the test run
    logging.basicConfig(level=logging.INFO)
    
    harvester = NSEXBRLHarvester()
    
    # Test specific type and date
    print(f"Testing harvest for {symbol} (Reg30, Jan 2026)...")
    data = harvester.harvest_xbrl(
        symbol, 
        types=["Reg30"], 
        start_date="20-01-2026", 
        end_date="30-01-2026"
    )
    
    # Save to a file for inspection
    output_file = f"{symbol}_xbrl_dump.json"
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"\nSaved harvest data to {output_file}")
    
    # Print summary
    for type_code, items in data.items():
        print(f"{type_code}: {len(items)} records")

if __name__ == "__main__":
    test_harvest()
