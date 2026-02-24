import io
import logging
import os
import shutil
import zipfile
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# Map of major XBRL announcement types and their corresponding Taxonomy URLs
TAXONOMY_URL_MAP = {
    "Reg30": "https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Taxonomy_Regulation_30_Restructuring.zip",
    "announcements": "https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Taxonomy_Changes_In_Management.zip",
    "outcome": "https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Taxonomy_Announcements_Pertaining_To_Outcome_Of_Board_Meeting_0.zip",
    "fundRaising": "https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Taxonomy%20-%20Alteration%20of%20Capital%20and%20Fund%20Raising.zip",
    "agr": "https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Taxonomy%20-%20Announcement%20for%20Agreements.zip",
    "award": "https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Taxonomy_Awarding_Or_Bagging_Or_Receiving_Of_Orders_Or_Contracts.zip",
    "annFraud": "https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Taxonomy%20-%20Announcement%20for%20Fraud%20or%20Default.zip",
    "cdr": "https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Taxonomy%20-%20Corporate%20Debt%20Restructuring.zip",
    "shm": "https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Taxonomy%20-%20Notice%20of%20Shareholders%20Meeting.zip",
    "CIRP": "https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Taxonomy_Corporate_Insolvency_Resolution_Process.zip",
    "annOts": "https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Taxonomy%20-One%20Time%20Settlement%20and%20RestructuringLoansOrBorrowings.zip",
}


class TaxonomyManager:
    """Manages downloading and caching of NSE XBRL Taxonomies."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the taxonomy manager.

        Args:
            cache_dir: Directory to store cached taxonomies. Defaults to .taxonomies/ in project root.
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Default to .taxonomies in project root
            self.cache_dir = Path(os.getcwd()) / ".taxonomies"

        if not self.cache_dir.exists():
            try:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                logger.error(f"Failed to create cache directory {self.cache_dir}: {e}")

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_taxonomy_dir(self, type_code: str) -> Optional[Path]:
        """Get the directory path for a specific taxonomy type.

        This method checks if the taxonomy is already cached. If not, it attempts to download
        and extract it.

        Args:
            type_code: The XBRL announcement type code (e.g., 'Reg30', 'fundRaising')

        Returns:
            Path object to the directory containing the extracted taxonomy files,
            or None if the type is unknown or download fails.
        """
        if type_code not in TAXONOMY_URL_MAP:
            logger.warning(f"No taxonomy URL mapped for type: {type_code}")
            return None

        target_dir = self.cache_dir / type_code

        # Check if already exists and is not empty
        if target_dir.exists() and any(target_dir.iterdir()):
            return target_dir

        return self._download_and_extract(type_code, target_dir)

    def _download_and_extract(self, type_code: str, target_dir: Path) -> Optional[Path]:
        """Download and extract the taxonomy zip file."""
        url = TAXONOMY_URL_MAP[type_code]
        logger.info(f"Downloading taxonomy for {type_code} from {url}...")

        try:
            response = requests.get(url, headers=self.headers, stream=True, timeout=60)
            if response.status_code != 200:
                logger.error(
                    f"Failed to download taxonomy for {type_code}: Status {response.status_code}"
                )
                return None

            # Use BytesIO to handle zip in memory before extraction
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                # Create directory only if download and zip load successful
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                target_dir.mkdir(parents=True, exist_ok=True)

                logger.info(f"Extracting taxonomy for {type_code} to {target_dir}...")
                zip_ref.extractall(target_dir)

            # After extraction, we might want to flatten the structure if it's nested deep,
            # but Arelle is generally good at finding things if we point to the right place.
            # However, for robustness, checking for .xsd files is good.
            if not self._has_xsd(target_dir):
                logger.warning(
                    f"Taxonomy for {type_code} extracted but NO .xsd files found. Arelle might struggle."
                )

            return target_dir

        except Exception as e:
            logger.error(f"Error managing taxonomy for {type_code}: {e}")
            # Clean up partial extraction
            if target_dir.exists():
                shutil.rmtree(target_dir)
            return None

    def _has_xsd(self, path: Path) -> bool:
        """Check recursively if directory contains any .xsd files."""
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".xsd"):
                    return True
        return False
