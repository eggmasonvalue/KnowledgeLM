
# --- Imports ---
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List

# --- Constants ---
CREDIT_RATING_FOLDER = "credit_rating"
ANNUAL_REPORTS_FOLDER = "annual_reports"
TRANSCRIPTS_FOLDER = "transcripts"
INVESTOR_PRESENTATIONS_FOLDER = "investor_presentations"
PRESS_RELEASES_FOLDER = "press_releases"
RELATED_PARTY_TXNS_FOLDER = "related_party_txns"
FILE_EXTENSIONS = {"pdf": ".pdf", "html": ".html", "htm": ".htm"}
ANNOUNCEMENTS_JSON = "{symbol}_announcements.json"

def download_credit_ratings_from_screener(symbol: str, download_folder: str = "artifacts") -> int:
    """
    Download all credit rating documents for a symbol from screener.in.
    Returns the number of documents downloaded.
    """
    screener_url = f"https://www.screener.in/company/{symbol}/"
    try:
        resp = requests.get(screener_url, timeout=15)
        if resp.status_code != 200:
            return 0
        soup = BeautifulSoup(resp.text, "html.parser")
        credit_ratings_div = None
        divs = soup.select("div.documents.credit-ratings")
        for div in divs:
            h3 = div.find("h3")
            if h3 and "credit ratings" in h3.text.strip().lower():
                credit_ratings_div = div
                break
        if not credit_ratings_div:
            return 0
        ul = credit_ratings_div.find("ul", class_="list-links")
        if not ul:
            return 0
        links = ul.find_all("a", href=True)
        if not links:
            return 0
        dest_folder = Path(download_folder) / CREDIT_RATING_FOLDER
        dest_folder.mkdir(parents=True, exist_ok=True)
        count = 0
        downloaded_files = set(f.name for f in dest_folder.glob("*"))
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": screener_url,
        }
        for a in links:
            url = a["href"]
            try:
                resp = requests.get(url, stream=True, timeout=30, verify=False, headers=headers)
                if resp.status_code == 200:
                    filename = url.split("/")[-1]
                    # If no extension, try to guess from content-type
                    if not any(filename.endswith(ext) for ext in FILE_EXTENSIONS.values()):
                        ctype = resp.headers.get('Content-Type', '').lower()
                        for key, ext in FILE_EXTENSIONS.items():
                            if key in ctype:
                                filename += ext
                                break
                    if filename in downloaded_files:
                        continue
                    file_path = dest_folder / filename
                    with open(file_path, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=8192):
                            f.write(chunk)
                    count += 1
                    downloaded_files.add(filename)
            except Exception as e:
                print(f"Exception downloading credit rating from primary source: {e}")
        return count
    except Exception as e:
        print(f"Exception fetching credit ratings page: {e}")
        return 0
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
    annual_reports_download_all: bool = False,
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Download announcements for a symbol between from_date and to_date.
    Dates should be in 'YYYY-MM-DD' format.
    Optionally download files by category.

    Returns:
        data: List of announcement dicts
        category_counts: Dict of category label to count
    """

    # Helper: check if any download is enabled
    def any_download_enabled():
        return any([
            download_transcripts,
            download_investor_presentations,
            download_press_releases,
            download_credit_rating,
            download_related_party_txns,
            download_annual_reports
        ])

    if not any_download_enabled():
        return [], {}

    Path(download_folder).mkdir(parents=True, exist_ok=True)
    nse = NSE(download_folder)
    from_dt = datetime.strptime(from_date, "%Y-%m-%d")
    to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    data = nse.announcements(symbol=symbol, from_date=from_dt, to_date=to_dt)

    # Store data into a file
    with open(Path(download_folder) / ANNOUNCEMENTS_JSON.format(symbol=symbol), "w") as f:
        json.dump(data, f, default=str, indent=2)

    args = {
        "download_transcripts": download_transcripts,
        "download_investor_presentations": download_investor_presentations,
        "download_press_releases": download_press_releases,
        "download_credit_rating": download_credit_rating,
        "download_related_party_txns": download_related_party_txns,
        "download_annual_reports": download_annual_reports,
    }
    category_counts = {}

    def download_category_items(cat_folder, items, label, filter_func):
        cat_folder.mkdir(parents=True, exist_ok=True)
        count = 0
        for item in items:
            if filter_func(item):
                url = item["attchmntFile"]
                try:
                    nse.download_document(url, cat_folder)
                    count += 1
                except Exception as e:
                    print(f"Exception downloading {label}: {e}")
        return count

    for cat, meta in DOWNLOAD_CATEGORIES.items():
        label = meta["label"]
        if cat == "annual_reports" and args.get("download_annual_reports", False):
            ar_folder = Path(download_folder) / ANNUAL_REPORTS_FOLDER
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
                        if not annual_reports_download_all:
                            if yr < from_dt.year or yr > to_dt.year:
                                continue
                        try:
                            nse.download_document(url, ar_folder)
                            count += 1
                        except Exception as e:
                            print(f"Exception downloading annual report: {e}")
            except Exception as e:
                print(f"Exception fetching annual reports: {e}")
            category_counts[label] = count
        elif cat == "credit_rating" and args.get(meta["enabled_arg"], False):
            cat_folder = Path(download_folder) / CREDIT_RATING_FOLDER
            cat_folder.mkdir(parents=True, exist_ok=True)
            primary_count = download_credit_ratings_from_screener(symbol, download_folder)
            if primary_count > 0:
                print(f"Credit ratings downloaded from primary source: {primary_count}")
                category_counts[label] = primary_count
            else:
                downloaded_files = set(f.name for f in cat_folder.glob("*"))
                count = 0
                for item in data:
                    if meta["filter"](item):
                        url = item["attchmntFile"]
                        filename = url.split("/")[-1]
                        if filename in downloaded_files:
                            continue
                        try:
                            nse.download_document(url, cat_folder)
                            count += 1
                            downloaded_files.add(filename)
                        except Exception as e:
                            print(f"Exception downloading credit rating from secondary source: {e}")
                print(f"Credit ratings downloaded from secondary source: {count}")
                category_counts[label] = count
        elif cat != "annual_reports" and cat != "credit_rating" and args.get(meta["enabled_arg"], False):
            cat_folder = Path(download_folder) / cat
            count = download_category_items(cat_folder, data, label, meta["filter"])
            category_counts[label] = count

    # Display counts
    for label, count in category_counts.items():
        if label == "credit rating":
            continue
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
