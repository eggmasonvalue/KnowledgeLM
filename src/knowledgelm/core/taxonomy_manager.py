import logging
import os
import shutil
from pathlib import Path
from typing import Optional

from knowledgelm.data.nse_adapter import NSEAdapter

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
    """Manages downloading and caching of NSE XBRL Taxonomies.

    Uses NSEAdapter for robust downloading and caching.
    """

    def __init__(self, nse_adapter: NSEAdapter, cache_dir: Optional[Path] = None):
        """Initialize the taxonomy manager.

        Args:
            nse_adapter: Instance of NSEAdapter to handle downloads.
            cache_dir: Directory to store cached taxonomies.
                Defaults to .taxonomies/ in project root.
        """
        self.adapter = nse_adapter
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Default to .taxonomies in project root
            self.cache_dir = Path.cwd() / ".taxonomies"

        try:
            if not self.cache_dir.exists():
                self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create cache directory {self.cache_dir}: {e}")

    def get_taxonomy_dir(self, type_code: str) -> Optional[Path]:
        """Get the directory path for a specific taxonomy type.

        This method checks if the taxonomy is already cached. If not, it attempts to download
        and extract it using the NSEAdapter.

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
        """Download and extract the taxonomy zip file using NSEAdapter.

        Args:
            type_code: The taxonomy type key.
            target_dir: The directory to extract content into.

        Returns:
            Path to target_dir if successful, else None.
        """
        if type_code not in TAXONOMY_URL_MAP:
            return None

        url = TAXONOMY_URL_MAP[type_code]
        logger.info(f"Downloading taxonomy for {type_code} from {url}...")

        # Ensure parent cache dir exists (in case it was deleted externally during runtime)
        if not self.cache_dir.exists():
            try:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                logger.error(f"Failed to recreate cache directory {self.cache_dir}: {e}")
                return None

        # Create directory
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        # Use adapter to download and extract
        # download_and_extract uses nse.download_document which extracts to folder
        success = self.adapter.download_and_extract(url, target_dir)

        if success:
            if not self._has_xsd(target_dir):
                logger.warning(
                    f"Taxonomy for {type_code} extracted but NO .xsd files found. "
                    "Arelle might struggle."
                )
            return target_dir
        else:
            logger.error(f"Failed to download taxonomy for {type_code}")
            if target_dir.exists():
                shutil.rmtree(target_dir)
            return None

    def _has_xsd(self, path: Path) -> bool:
        """Check recursively if directory contains any .xsd files.

        Args:
            path: Directory to search.

        Returns:
            True if at least one .xsd file is found.
        """
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".xsd"):
                    return True
        return False
