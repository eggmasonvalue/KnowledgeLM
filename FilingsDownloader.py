from datetime import datetime
from pathlib import Path
from nse import NSE
from typing import Dict, Any, Tuple, List

DOWNLOAD_CATEGORIES = {
    "transcripts": {
        "enabled_arg": "download_transcripts",
        "filter": lambda item: (
            item.get("desc", "").strip().lower() == "analysts/institutional investor meet/con. call updates"
            and "attchmntText" in item
            and "transcript" in item["attchmntText"].lower()
            and "attchmntFile" in item
            and item["attchmntFile"]
        ),
        "label": "transcript"
    },
    "investor_presentations": {
        "enabled_arg": "download_investor_presentations",
        "filter": lambda item: (
            item.get("desc", "").strip().lower() == "investor presentation"
            and "attchmntFile" in item
            and item["attchmntFile"]
        ),
        "label": "investor presentation"
    },
    "press_releases": {
        "enabled_arg": "download_press_releases",
        "filter": lambda item: (
            item.get("desc", "").strip().lower() in ["press release", "press release (revised)"]
            and "attchmntFile" in item
            and item["attchmntFile"]
        ),
        "label": "press release"
    },
    # Add more categories here as needed
}

def download_announcements(
    symbol: str,
    from_date: str,
    to_date: str = datetime.today().strftime("%Y-%m-%d"),
    download_folder: str = "artifacts",
    download_transcripts: bool = True,
    download_investor_presentations: bool = True,
    download_press_releases: bool = True,
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Download announcements for a symbol between from_date and to_date.
    Dates should be in 'YYYY-MM-DD' format.
    Optionally download files by category.
    Returns:
        data: List of announcement dicts
        category_counts: Dict of category label to count
    """
    # Ensure artifacts folder exists
    Path(download_folder).mkdir(parents=True, exist_ok=True)
    nse = NSE(download_folder)
    from_dt = datetime.strptime(from_date, "%Y-%m-%d")
    to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    data = nse.announcements(symbol=symbol, from_date=from_dt, to_date=to_dt)
    
    # Download files by category using lookup table
    args = {
        "download_transcripts": download_transcripts,
        "download_investor_presentations": download_investor_presentations,
        "download_press_releases": download_press_releases,
    }
    category_counts = {}
    for cat, meta in DOWNLOAD_CATEGORIES.items():
        if args.get(meta["enabled_arg"], False):
            cat_folder = Path(download_folder) / cat
            cat_folder.mkdir(parents=True, exist_ok=True)
            count = 0
            for item in data:
                if meta["filter"](item):
                    url = item["attchmntFile"]
                    try:
                        print(f"Downloading {meta['label']}: {url} -> {cat_folder}")
                        nse.download_document(url, cat_folder)
                        count += 1
                    except Exception as e:
                        print(f"Failed to download {url}: {e}")
            category_counts[meta["label"]] = count

    # Display counts
    for label, count in category_counts.items():
        print(f"{label.capitalize()}s downloaded: {count}")

    return data, category_counts

# Example usage:
if __name__ == "__main__":
    symbol = "HDFCBANK"
    from_date = "2024-01-01"
    # Choose what to download
    announcements, counts = download_announcements(
        symbol, from_date,
        download_transcripts=True,
        download_investor_presentations=True,
        download_press_releases=True
    )
    # print(announcements)

