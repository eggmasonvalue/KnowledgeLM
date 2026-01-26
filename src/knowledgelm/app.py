"""Streamlit UI for batch downloading NSE company announcements."""

import logging
from datetime import date

import pandas as pd
import streamlit as st
from nse import NSE  # Kept for direct download reuse in UI if needed, or better replaced by service

from knowledgelm.config import (
    DOWNLOAD_CATEGORIES_CONFIG,
    PRESS_RELEASES_FOLDER,
    RESIGNATIONS_FOLDER,
    UPDATES_FOLDER,
)
from knowledgelm.core.service import KnowledgeService
from knowledgelm.utils.file_utils import get_download_path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Constants ---
DOWNLOAD_KEY_PREFIX = {
    "resignations": "download_resignation_",
    "updates": "download_update_",
    "press_releases": "download_press_release_",
}

# --- Session State Initialization ---
if "data" not in st.session_state:
    st.session_state.data = None
if "category_counts" not in st.session_state:
    st.session_state.category_counts = None
if "status_msgs" not in st.session_state:
    st.session_state.status_msgs = []
if "resignation_df" not in st.session_state:
    st.session_state.resignation_df = None
if "updates_df" not in st.session_state:
    st.session_state.updates_df = None
if "press_releases_df" not in st.session_state:
    st.session_state.press_releases_df = None
# We no longer rely on a global 'nse_instance' in session state

st.title("KnowledgeLM")
st.caption("A notebookLM companion for NSE company research")

# --- Input Section: Symbol and Date Range ---
st.header("Select Company and Date Range")
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    symbol = st.text_input("Company Symbol", value="HDFCBANK")
with col2:
    from_date = st.date_input("Start Date", value=date(2024, 1, 1))
with col3:
    to_date = st.date_input("End Date", value=date.today())

# --- Download Folder ---
folder_name_input = st.text_input(
    "Artifacts Folder Name",
    value=f"{symbol}_artifacts",
    help="Name of the folder to create. Do NOT include paths (e.g., 'C:\\'). Valid chars only.",
)

# --- Download Options ---
st.header("Download Categories")
col_dl1, col_dl2, col_dl3 = st.columns(3)


# Helper to access config keys
def get_config_key(cat):
    """Get the enabled_arg key for a category from config."""
    return DOWNLOAD_CATEGORIES_CONFIG[cat]["enabled_arg"]


with col_dl1:
    download_transcripts = st.checkbox("Analyst Call Transcripts")
    download_credit_rating = st.checkbox(
        "Credit Ratings",
        help="Primary source: Screener.in. Fallback: NSE Filings.",
    )
with col_dl2:
    download_investor_presentations = st.checkbox("Investor Presentations")
    download_related_party_txns = st.checkbox("Related Party Transactions")
with col_dl3:
    download_annual_reports = st.checkbox("Download Annual Reports", value=False)
    annual_reports_download_all = False
    if download_annual_reports:
        ar_mode = st.radio(
            "Annual Report Download Mode",
            options=["Within Date Range", "All"],
            horizontal=True,
            index=0,
            key="annual_report_mode_radio",
        )
        annual_reports_download_all = ar_mode == "All"

# --- View/Filter Options ---
st.header("Show/Download Individual Filings")
col_v1, col_v2, col_v3 = st.columns(3)
with col_v1:
    show_resignations = st.checkbox("Resignations")
with col_v2:
    show_updates = st.checkbox(
        "Regulation 30 Updates", help="Experimental. Does not cover all update filings"
    )
with col_v3:
    show_press_releases = st.checkbox("Press Releases")

# --- Main Action Button ---
st.markdown("---")
if st.button("Fetch Filings"):
    st.session_state.status_msgs = []

    # Validation
    try:
        # Use CWD for now. In a real app, this might be a user config dir.
        service = KnowledgeService(".")

        with st.spinner("Downloading and processing filings..."):
            options = {
                "download_transcripts": download_transcripts,
                "download_investor_presentations": download_investor_presentations,
                # PRs displayed in view, not bulk downloaded (original behavior)
                "download_press_releases": False,
                "download_credit_rating": download_credit_rating,
                "download_related_party_txns": download_related_party_txns,
                "download_annual_reports": download_annual_reports,
            }

            data, category_counts = service.process_request(
                symbol=symbol,
                from_date=from_date,
                to_date=to_date,
                folder_name=folder_name_input,
                options=options,
                annual_reports_all_mode=annual_reports_download_all,
            )

            st.session_state.data = data
            st.session_state.category_counts = category_counts

            # Re-create DataFrames for the UI Logic
            # Filter logic duplication: ideally moves to Service and returns DFs
            # For now, we keep the DF construction here to minimize UI refactor

            # Resignations
            resignation_records = [
                {
                    "Announcement Date": item.get("an_dt", ""),
                    "Description": item.get("attchmntText", ""),
                    "Attachment File": item.get("attchmntFile", ""),
                }
                for item in data
                if str(item.get("desc", "")).strip().lower() in ["cessation", "resignation"]
            ]
            st.session_state.resignation_df = pd.DataFrame(resignation_records)
            if show_resignations:
                st.session_state.status_msgs.append(
                    f"{len(st.session_state.resignation_df)} resignations found."
                )

            # Updates
            updates_records = [
                {
                    "Announcement Date": item.get("an_dt", ""),
                    "Description": item.get("attchmntText", ""),
                    "Attachment File": item.get("attchmntFile", ""),
                }
                for item in data
                if (
                    str(item.get("desc", "")).strip().lower() == "updates"
                    and "regulation 30" in str(item.get("attchmntText", "")).lower()
                )
            ]
            st.session_state.updates_df = pd.DataFrame(updates_records)
            if show_updates:
                st.session_state.status_msgs.append(
                    f"{len(st.session_state.updates_df)} Regulation 30 updates found."
                )

            # Press Releases
            press_release_records = [
                {
                    "Announcement Date": item.get("an_dt", ""),
                    "Description": item.get("attchmntText", ""),
                    "Attachment File": item.get("attchmntFile", ""),
                }
                for item in data
                if str(item.get("desc", "")).strip().lower()
                in ["press release", "press release (revised)"]
            ]
            st.session_state.press_releases_df = pd.DataFrame(press_release_records)
            if show_press_releases:
                st.session_state.status_msgs.append(
                    f"{len(st.session_state.press_releases_df)} press releases found."
                )

            # Success Message
            st.session_state.status_msgs.append(
                f"Fetched {len(data)} filings. Processed in '{folder_name_input}'."
            )

            if category_counts:
                summary_parts = []
                for label, count in category_counts.items():
                    if count > 0:
                        summary_parts.append(f"{count} {label if count == 1 else label + 's'}")
                summary = ", ".join(summary_parts)
                if summary:
                    st.session_state.status_msgs.append(f"Downloaded: {summary}")

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


# --- Helper for Download Tables ---
def render_download_table(
    df: pd.DataFrame | None,
    show_flag: bool,
    expander_title: str,
    folder_subname: str,
    key_prefix: str,
    download_root_name: str,
) -> None:
    """Render an expandable table with download buttons for filings."""
    if show_flag and df is not None and not df.empty:
        with st.expander(expander_title, expanded=False):
            # Use NSE lib directly for UI downloads (legacy compat, safe paths)

            try:
                root_path = get_download_path(".", download_root_name)
                nse_instance = NSE(str(root_path))  # The NSE lib takes the root folder string
            except Exception:
                st.error("Invalid download folder configuration.")
                return

            # Download all button
            if st.button(f"Download All {expander_title} Attachments"):
                count = 0
                for idx, row in df.iterrows():
                    url = row["Attachment File"]
                    if url and url != "-":
                        try:
                            # Construct safe subfolder path
                            dest_folder = root_path / folder_subname
                            dest_folder.mkdir(parents=True, exist_ok=True)
                            nse_instance.download_document(url, dest_folder)
                            count += 1
                        except Exception as e:
                            st.session_state.status_msgs.append(f"Error downloading {url}: {e}")
                st.session_state.status_msgs.append(
                    f"Downloaded {count} {expander_title.lower()} attachments."
                )
                st.rerun()

            # Per-row download
            for idx, row in df.iterrows():
                col1, col2, col3 = st.columns([2, 5, 2])
                with col1:
                    st.write(row["Announcement Date"])
                with col2:
                    st.write(row["Description"])
                with col3:
                    url = row["Attachment File"]
                    if url and url != "-":
                        download_key = f"{key_prefix}{idx}"
                        if st.button("Download", key=download_key):
                            try:
                                dest_folder = root_path / folder_subname
                                dest_folder.mkdir(parents=True, exist_ok=True)
                                result = nse_instance.download_document(url, dest_folder)
                                st.session_state.status_msgs.append(f"Downloaded to {result}")
                                st.rerun()
                            except Exception as e:
                                st.session_state.status_msgs.append(f"Error: {e}")
                                st.rerun()
                    else:
                        st.write("-")


# --- Render Download Tables ---
# We need to pass the current folder_name_input to these helpers so they know where to save
render_download_table(
    st.session_state.resignation_df,
    show_resignations,
    "Resignations",
    RESIGNATIONS_FOLDER,
    DOWNLOAD_KEY_PREFIX["resignations"],
    folder_name_input,
)
render_download_table(
    st.session_state.updates_df,
    show_updates,
    "Regulation 30 Updates",
    UPDATES_FOLDER,
    DOWNLOAD_KEY_PREFIX["updates"],
    folder_name_input,
)
render_download_table(
    st.session_state.press_releases_df,
    show_press_releases,
    "Press Releases",
    PRESS_RELEASES_FOLDER,
    DOWNLOAD_KEY_PREFIX["press_releases"],
    folder_name_input,
)

# --- Status Window ---
if st.session_state.status_msgs:
    try:
        with st.expander("Status", expanded=True):
            for msg in st.session_state.status_msgs:
                st.markdown(msg, unsafe_allow_html=True)
    except Exception:
        pass
