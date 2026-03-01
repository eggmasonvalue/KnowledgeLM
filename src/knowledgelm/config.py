"""Configuration settings for KnowledgeLM."""

# --- Folder configuration moved directly into categories below ---

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
        "folder_name": "transcripts",
        "shorthand": "Transcript",
    },
    "investor_presentations": {
        "enabled_arg": "download_investor_presentations",
        "label": "investor presentation",
        "folder_name": "investor_presentations",
        "shorthand": "Presentation",
    },
    "press_releases": {
        "enabled_arg": "download_press_releases",
        "label": "press release",
        "folder_name": "press_releases",
        "shorthand": "PR",
    },
    "credit_rating": {
        "enabled_arg": "download_credit_rating",
        "label": "credit rating",
        "folder_name": "credit_rating",
        "shorthand": "CR",
    },
    "related_party_txns": {
        "enabled_arg": "download_related_party_txns",
        "label": "related party transaction",
        "folder_name": "related_party_txns",
        "shorthand": "RPT",
    },
    "annual_reports": {
        "enabled_arg": "download_annual_reports",
        "label": "annual report",
        "folder_name": "annual_reports",
        "shorthand": "AR",
    },
    "issue_documents": {
        "enabled_arg": "download_issue_documents",
        "label": "issue document",
        "folder_name": "share_issuance_docs",
        "shorthand": "IssueDoc",
    },
    # XBRL-based categories
    "personnel": {
        "enabled_arg": "download_personnel",
        "label": "personnel change",
        "folder_name": "personnel",
        "shorthand": "Personnel",
        "is_xbrl": True,
        "xbrl_cat": "Change in Personnel",
        "output_keys": ["broadcastDateTime", "xbrl_data"],
    },
    "key_announcements": {
        "enabled_arg": "download_key_announcements",
        "label": "key announcement",
        "folder_name": "key_announcements",
        "shorthand": "KeyAnn",
        "is_xbrl": True,
        "xbrl_cat": "Key announcements",
        "output_keys": ["subOfAnn", "broadcastDateTime", "xbrl_data"],
    },
    "shm": {
        "enabled_arg": "download_shm",
        "label": "shareholder meeting",
        "folder_name": "shareholder_meetings",
        "shorthand": "SHM",
        "is_xbrl": True,
        "xbrl_cat": "Shareholder Meetings",
        "output_keys": ["eventType", "broadcastDateTime", "ixbrl", "local_pdf_path"],
    },
}

# --- Issue Documents Config ---
ISSUE_DOCS_CONFIG = {
    "offer_documents": {
        "label": "Offer Documents (IPO)",
        "api_path": "/corporates/offerdocs",
        "api_params": {"index": "equities"},
        "attachment_fields": ["fpAttach"],
        "subfolder": "Offer Documents (IPO)",
        "shorthand": "OfferDoc",
        "symbol_reliable": False,
    },
    "rights_issue": {
        "label": "Rights Issue",
        "api_path": "/corporates/offerdocs/rights",
        "api_params": {"index": "equities"},
        "attachment_fields": ["draftAttch", "finalAttach"],
        "subfolder": "Rights Issue",
        "shorthand": "Rights",
        "symbol_reliable": True,
    },
    "qip_offer": {
        "label": "QIP Offer",
        "api_path": "/corporates/offerdocs/rights",
        "api_params": {"index": "qip"},
        "attachment_fields": ["attachFile"],
        "subfolder": "QIP Offer",
        "shorthand": "QIP",
        "symbol_reliable": False,
    },
    "info_memorandum": {
        "label": "Information Memorandum",
        "api_path": "/corporates/offerdocs/arrangementscheme/infomemo",
        "api_params": {},
        "attachment_fields": ["date_attachmnt"],
        "subfolder": "Information Memorandum",
        "shorthand": "InfoMemo",
        "symbol_reliable": False,
    },
    "scheme_document": {
        "label": "Scheme of Arrangement",
        "api_path": "/corporates/offerdocs/arrangementscheme",
        "api_params": {},
        "attachment_fields": ["date_attachmnt"],
        "subfolder": "Scheme of Arrangement",
        "shorthand": "SchemeDoc",
        "symbol_reliable": False,
    },
}

# --- Screener.in Scraper Config ---
SCREENER_BASE_URL = "https://www.screener.in/company/{symbol}/"
SCREENER_TIMEOUT = 15
SCREENER_DOCS_SELECTOR = "div.documents.credit-ratings"
SCREENER_LINKS_SELECTOR = "ul.list-links a[href]"
