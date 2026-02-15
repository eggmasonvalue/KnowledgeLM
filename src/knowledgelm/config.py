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
    "issue_documents": {
        "enabled_arg": "download_issue_documents",
        "label": "issue document",
    },
}

# --- Issue Documents Config ---
ISSUE_DOCS_FOLDER = "issue_documents"

ISSUE_DOCS_CONFIG = {
    "offer_documents": {
        "label": "Offer Documents (IPO)",
        "api_path": "/corporates/offerdocs",
        "api_params": {"index": "equities"},
        # "attachment_fields": ["drhpAttach", "rhpAttach", "fpAttach"],
        "attachment_fields": ["fpAttach"],
        "subfolder": "offer_documents",
        "symbol_reliable": False,
    },
    "rights_issue": {
        "label": "Rights Issue",
        "api_path": "/corporates/offerdocs/rights",
        "api_params": {"index": "equities"},
        "attachment_fields": ["draftAttch", "finalAttach"],
        "subfolder": "rights_issue",
        "symbol_reliable": True,
    },
    "qip_offer": {
        "label": "QIP Offer",
        "api_path": "/corporates/offerdocs/rights",
        "api_params": {"index": "qip"},
        "attachment_fields": ["attachFile"],
        "subfolder": "qip_offer",
        "symbol_reliable": False,
    },
    "info_memorandum": {
        "label": "Information Memorandum",
        "api_path": "/corporates/offerdocs/arrangementscheme/infomemo",
        "api_params": {},
        "attachment_fields": ["date_attachmnt"],
        "subfolder": "info_memorandum",
        "symbol_reliable": False,
    },
    "scheme_document": {
        "label": "Scheme of Arrangement",
        "api_path": "/corporates/offerdocs/arrangementscheme",
        "api_params": {},
        "attachment_fields": ["date_attachmnt"],
        "subfolder": "scheme_document",
        "symbol_reliable": False,
    },
}

# --- Screener.in Scraper Config ---
SCREENER_BASE_URL = "https://www.screener.in/company/{symbol}/"
SCREENER_TIMEOUT = 15
SCREENER_DOCS_SELECTOR = "div.documents.credit-ratings"
SCREENER_LINKS_SELECTOR = "ul.list-links a[href]"
