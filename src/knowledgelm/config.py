"""Configuration settings for KnowledgeLM."""

# --- Folder Names ---
RESIGNATIONS_FOLDER = "resignations"
UPDATES_FOLDER = "updates"
PRESS_RELEASES_FOLDER = "press_releases"
CREDIT_RATING_FOLDER = "credit_rating"
ANNUAL_REPORTS_FOLDER = "annual_reports"
TRANSCRIPTS_FOLDER = "transcripts"
INVESTOR_PRESENTATIONS_FOLDER = "investor_presentations"
RELATED_PARTY_TXNS_FOLDER = "related_party_txns"

# --- Constants ---
ANNOUNCEMENTS_JSON_TEMPLATE = "{symbol}_announcements.json"

FILE_EXTENSIONS = {"pdf": ".pdf", "html": ".html", "htm": ".htm"}

# --- Download Categories ---
# Each category has a label, an enabled_arg (for UI/Service mapping), and a filter function.
# The filter function logic will be moved to the service/adapter layer, here we define keys.

DOWNLOAD_CATEGORIES_CONFIG = {
    "transcripts": {
        "enabled_arg": "download_transcripts",
        "label": "transcript",
    },
    "investor_presentations": {
        "enabled_arg": "download_investor_presentations",
        "label": "investor presentation",
    },
    "press_releases": {
        "enabled_arg": "download_press_releases",
        "label": "press release",
    },
    "credit_rating": {
        "enabled_arg": "download_credit_rating",
        "label": "credit rating",
    },
    "related_party_txns": {
        "enabled_arg": "download_related_party_txns",
        "label": "related party transaction",
    },
    "annual_reports": {
        "enabled_arg": "download_annual_reports",
        "label": "annual report",
    },
}

# --- Screener.in Scraper Config ---
SCREENER_BASE_URL = "https://www.screener.in/company/{symbol}/"
SCREENER_TIMEOUT = 15
SCREENER_DOCS_SELECTOR = "div.documents.credit-ratings"
SCREENER_LINKS_SELECTOR = "ul.list-links a[href]"
