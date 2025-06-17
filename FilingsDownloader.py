import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List
import json

from nse import NSE

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
    "credit_rating": {
        "enabled_arg": "download_credit_rating",
        "filter": lambda item: (
            item.get("desc", "").strip().lower() == "credit rating"
            and "attchmntFile" in item
            and item["attchmntFile"]
        ),
        "label": "credit rating"
    },
    "related_party_txns": {
        "enabled_arg": "download_related_party_txns",
        "filter": lambda item: (
            item.get("desc", "").strip().lower() in [
                "related party transaction",
                "related party transactions"
            ]
            and "attchmntFile" in item
            and item["attchmntFile"]
        ),
        "label": "related party transaction"
    },
    "annual_reports": {
        "enabled_arg": "download_annual_reports",
        "filter": None,  # handled separately
        "label": "annual report"
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
    download_credit_rating: bool = True,
    download_related_party_txns: bool = True,
    download_annual_reports: bool = False,
    annual_reports_download_all: bool = False,  # NEW
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

    # Store data into a file
    with open(Path(download_folder) / f"{symbol}_announcements.json", "w") as f:
        json.dump(data, f, default=str, indent=2)

    args = {
        "download_transcripts": download_transcripts,
        "download_investor_presentations": download_investor_presentations,
        "download_press_releases": download_press_releases,
        "download_credit_rating": download_credit_rating,
        "download_related_party_txns": download_related_party_txns,
        "download_annual_reports": download_annual_reports,  # NEW
    }
    category_counts = {}
    for cat, meta in DOWNLOAD_CATEGORIES.items():
        if cat == "annual_reports" and args.get("download_annual_reports", False):
            ar_folder = Path(download_folder) / "annual_reports"
            ar_folder.mkdir(parents=True, exist_ok=True)
            count = 0
            try:
                ar_data = nse.annual_reports(symbol)
                for year, docs in ar_data.items():
                    for doc in docs:
                        to_yr = doc.get("toYr")
                        url = doc.get("fileName") or doc.get("url") or doc.get("fileUrl") or doc.get("documentUrl")
                        if not url or not to_yr:
                            continue
                        try:
                            yr = int(str(to_yr).strip())
                        except Exception:
                            continue
                        # Download logic based on toggle
                        if not annual_reports_download_all:
                            if yr < from_dt.year or yr > to_dt.year:
                                continue
                        try:
                            nse.download_document(url, ar_folder)
                            count += 1
                        except Exception as e:
                            pass
            except Exception as e:
                print(f"Error fetching annual reports: {e}")
            category_counts[meta["label"]] = count
        elif cat != "annual_reports" and args.get(meta["enabled_arg"], False):
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
    announcements, counts = download_announcements(
        symbol, from_date,
        download_transcripts=True,
        download_investor_presentations=True,
        download_press_releases=True
    )
    # print(announcements)
