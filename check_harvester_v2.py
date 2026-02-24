from knowledgelm.core.xbrl_harvester import NSEXBRLHarvester
from knowledgelm.data.nse_adapter import NSEAdapter
from pathlib import Path
import json
import logging
import tempfile

# Configure logging to see info
logging.basicConfig(level=logging.INFO)

def check():
    # Use real NSEAdapter with a temp dir
    # Note: In real app, this should be a persistent dir for caching
    temp_download_dir = Path(tempfile.gettempdir()) / "knowledgelm_test"
    temp_download_dir.mkdir(exist_ok=True)

    adapter = NSEAdapter(temp_download_dir)
    harvester = NSEXBRLHarvester(adapter)

    # 1. Test Reg30 (Expected: Fallback to Internal API)
    print("\n--- Testing Reg30 (NRBBEARING) ---")
    data_reg30 = harvester.harvest_xbrl(
        "NRBBEARING",
        types=["Reg30"],
        start_date="01-01-2026",
        end_date="30-01-2026"
    )
    # Check sample
    if "Reg30" in data_reg30 and data_reg30["Reg30"]:
        item = data_reg30["Reg30"][0]
        print(f"Found item. Data keys: {list(item.get('xbrl_data', {}).keys())[:5]}")
        # Validate we got data (internal API keys are usually verbose like 'NSESymbol', 'NameOfTheCompany')
        assert item.get('xbrl_data'), "Reg30 data should not be empty (Fallback failed)"
    else:
        print("No Reg30 data found.")

    # 2. Test fundRaising (Expected: Arelle Parsing)
    print("\n--- Testing fundRaising (INFY) ---")
    data_infy = harvester.harvest_xbrl(
        "INFY",
        types=["fundRaising"],
        start_date="01-01-2026",
        end_date="30-01-2026"
    )
    if "fundRaising" in data_infy and data_infy["fundRaising"]:
        item = data_infy["fundRaising"][0]
        # Check for human readable keys
        keys = list(item.get('xbrl_data', {}).keys())
        print(f"Found item. Data keys: {keys[:5]}")
        has_human_readable = any(" " in k for k in keys)
        assert has_human_readable, "fundRaising should have human readable keys from Arelle"
    else:
        print("No fundRaising data found.")

if __name__ == "__main__":
    check()
