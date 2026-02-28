"""Configuration settings for KnowledgeLM."""

# --- Folder Names ---
RESIGNATIONS_FOLDER = "resignations"
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
        "label": "analyst call transcript",
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
    # XBRL-based categories
    "personnel": {
        "enabled_arg": "download_personnel",
        "label": "personnel change",
        "is_xbrl": True,
        "xbrl_cat": "Change in Personnel",
        "output_keys": ["broadcastDateTime", "xbrl_data"],
    },
    "key_announcements": {
        "enabled_arg": "download_key_announcements",
        "label": "key announcement",
        "is_xbrl": True,
        "xbrl_cat": "Key announcements",
        "output_keys": ["subOfAnn", "broadcastDateTime", "xbrl_data"],
    },
    # "board_outcome": {
    #     "enabled_arg": "download_board_outcome",
    #     "label": "board meeting outcome",
    #     "is_xbrl": True,
    #     "xbrl_cat": "Board Meeting Outcome",
    # },
    "shm": {
        "enabled_arg": "download_shm",
        "label": "shareholder meeting",
        "is_xbrl": True,
        "xbrl_cat": "Shareholder Meetings",
        "output_keys": ["eventType", "broadcastDateTime", "ixbrl", "local_pdf_path"],
    },
}

# --- Issue Documents Config ---
ISSUE_DOCS_FOLDER = "share_issuance_docs"

ISSUE_DOCS_CONFIG = {
    "offer_documents": {
        "label": "Offer Documents (IPO)",
        "api_path": "/corporates/offerdocs",
        "api_params": {"index": "equities"},
        # "attachment_fields": ["drhpAttach", "rhpAttach", "fpAttach"],
        "attachment_fields": ["fpAttach"],
        "subfolder": "Offer Documents (IPO)",
        "symbol_reliable": False,
    },
    "rights_issue": {
        "label": "Rights Issue",
        "api_path": "/corporates/offerdocs/rights",
        "api_params": {"index": "equities"},
        "attachment_fields": ["draftAttch", "finalAttach"],
        "subfolder": "Rights Issue",
        "symbol_reliable": True,
    },
    "qip_offer": {
        "label": "QIP Offer",
        "api_path": "/corporates/offerdocs/rights",
        "api_params": {"index": "qip"},
        "attachment_fields": ["attachFile"],
        "subfolder": "QIP Offer",
        "symbol_reliable": False,
    },
    "info_memorandum": {
        "label": "Information Memorandum",
        "api_path": "/corporates/offerdocs/arrangementscheme/infomemo",
        "api_params": {},
        "attachment_fields": ["date_attachmnt"],
        "subfolder": "Information Memorandum",
        "symbol_reliable": False,
    },
    "scheme_document": {
        "label": "Scheme of Arrangement",
        "api_path": "/corporates/offerdocs/arrangementscheme",
        "api_params": {},
        "attachment_fields": ["date_attachmnt"],
        "subfolder": "Scheme of Arrangement",
        "symbol_reliable": False,
    },
}

# --- Screener.in Scraper Config ---
SCREENER_BASE_URL = "https://www.screener.in/company/{symbol}/"
SCREENER_TIMEOUT = 15
SCREENER_DOCS_SELECTOR = "div.documents.credit-ratings"
SCREENER_LINKS_SELECTOR = "ul.list-links a[href]"
