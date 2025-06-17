import streamlit as st
from datetime import date
from FilingsDownloader import download_announcements
import pandas as pd
from pathlib import Path
from nse import NSE

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
download_folder = st.text_input(
    "Download Folder",
    value=f"{symbol}_artifacts",
    help="The folder will be created in the current directory if it does not exist."
)

# --- Download Options ---
st.header("Download Categories")
col_dl1, col_dl2, col_dl3 = st.columns(3)
with col_dl1:
    download_transcripts = st.checkbox("Analyst Call Transcripts")
    download_credit_rating = st.checkbox("Credit Ratings")
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
            key="annual_report_mode_radio"
        )
        annual_reports_download_all = ar_mode == "All"

# --- View/Filter Options ---
st.header("Show/Download Individual Filings")
col_v1, col_v2, col_v3 = st.columns(3)
with col_v1:
    show_resignations = st.checkbox("Resignations")
with col_v2:
    show_updates = st.checkbox(
        "Regulation 30 Updates",
        help="Experimental. Does not cover all update filings"
    )
with col_v3:
    show_press_releases = st.checkbox(
        "Press Releases"
    )    
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
if "nse_instance" not in st.session_state:
    st.session_state.nse_instance = None

# --- Main Action Button ---
st.markdown("---")
if st.button("Fetch Filings"):
    with st.spinner("Downloading and processing filings..."):
        data, category_counts = download_announcements(
            symbol=symbol,
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=to_date.strftime("%Y-%m-%d"),
            download_folder=download_folder,
            download_transcripts=download_transcripts,
            download_investor_presentations=download_investor_presentations,
            download_press_releases=False,  # handled as window
            download_credit_rating=download_credit_rating,
            download_related_party_txns=download_related_party_txns,
            download_annual_reports=download_annual_reports,
            annual_reports_download_all=annual_reports_download_all,
        )
        st.session_state.data = data
        st.session_state.category_counts = category_counts
        st.session_state.nse_instance = NSE(download_folder)
        st.session_state.status_msgs = []
        st.session_state.resignation_df = None
        st.session_state.updates_df = None
        st.session_state.press_releases_df = None

        st.session_state.status_msgs.append(
            f"Fetched {len(data)} filings. Saved to '{download_folder}'."
        )
        if category_counts:
            summary = ", ".join(
                f"{count} {label if count == 1 else label + 's'}"
                for label, count in category_counts.items()
                if count > 0
            )
            if summary:
                st.session_state.status_msgs.append(f"Downloaded: {summary}")

        if show_resignations:
            resignation_records = [
                {
                    "Announcement Date": item.get("an_dt", ""),
                    "Description": item.get("attchmntText", ""),
                    "Attachment File": item.get("attchmntFile", ""),
                }
                for item in data
                if str(item.get("desc", "")).strip().lower() in ["cessation", "resignation"]
            ]
            resignation_df = pd.DataFrame(resignation_records)
            st.session_state.resignation_df = resignation_df
            st.session_state.status_msgs.append(
                f"{len(resignation_df)} resignations found."
            )
        else:
            st.session_state.resignation_df = None

        if show_updates:
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
            updates_df = pd.DataFrame(updates_records)
            st.session_state.updates_df = updates_df
            st.session_state.status_msgs.append(
                f"{len(updates_df)} Regulation 30 updates found."
            )
        else:
            st.session_state.updates_df = None

        if show_press_releases:
            press_release_records = [
                {
                    "Announcement Date": item.get("an_dt", ""),
                    "Description": item.get("attchmntText", ""),
                    "Attachment File": item.get("attchmntFile", ""),
                }
                for item in data
                if str(item.get("desc", "")).strip().lower() in ["press release", "press release (revised)"]
            ]
            press_releases_df = pd.DataFrame(press_release_records)
            st.session_state.press_releases_df = press_releases_df
            st.session_state.status_msgs.append(
                f"{len(press_releases_df)} press releases found."
            )
        else:
            st.session_state.press_releases_df = None

# --- Resignation Table with Download Buttons ---
if show_resignations and st.session_state.resignation_df is not None and not st.session_state.resignation_df.empty:
    with st.expander("Resignations", expanded=False):
        resignation_df = st.session_state.resignation_df
        nse_instance = st.session_state.nse_instance or NSE(download_folder)

        if st.button("Download All Resignation Attachments"):
            count = 0
            for idx, row in resignation_df.iterrows():
                url = row["Attachment File"]
                if url and url != "-":
                    try:
                        dest_folder = Path(download_folder) / "resignations"
                        dest_folder.mkdir(parents=True, exist_ok=True)
                        nse_instance.download_document(url, dest_folder)
                        count += 1
                    except Exception as e:
                        st.session_state.status_msgs.append(f"Error downloading {url}: {e}")
            st.session_state.status_msgs.append(f"Downloaded {count} resignation attachments.")
            st.rerun()

        for idx, row in resignation_df.iterrows():
            col1, col2, col3 = st.columns([2, 5, 2])
            with col1:
                st.write(row["Announcement Date"])
            with col2:
                st.write(row["Description"])
            with col3:
                url = row["Attachment File"]
                if url and url != "-":
                    download_key = f"download_resignation_{idx}"
                    if st.button("Download", key=download_key):
                        try:
                            dest_folder = Path(download_folder) / "resignations"
                            dest_folder.mkdir(parents=True, exist_ok=True)
                            result = nse_instance.download_document(url, dest_folder)
                            st.session_state.status_msgs.append(f"Downloaded to {result}")
                            st.rerun()
                        except Exception as e:
                            st.session_state.status_msgs.append(f"Error: {e}")
                            st.rerun()
                else:
                    st.write("-")

# --- Updates Table ---
if show_updates and st.session_state.updates_df is not None and not st.session_state.updates_df.empty:
    with st.expander("Regulation 30 Updates", expanded=False):
        updates_df = st.session_state.updates_df
        nse_instance = st.session_state.nse_instance or NSE(download_folder)

        if st.button("Download All Update Attachments"):
            count = 0
            for idx, row in updates_df.iterrows():
                url = row["Attachment File"]
                if url and url != "-":
                    try:
                        dest_folder = Path(download_folder) / "updates"
                        dest_folder.mkdir(parents=True, exist_ok=True)
                        nse_instance.download_document(url, dest_folder)
                        count += 1
                    except Exception as e:
                        st.session_state.status_msgs.append(f"Error downloading {url}: {e}")
            st.session_state.status_msgs.append(f"Downloaded {count} update attachments.")
            st.rerun()

        for idx, row in updates_df.iterrows():
            col1, col2, col3 = st.columns([2, 5, 2])
            with col1:
                st.write(row["Announcement Date"])
            with col2:
                st.write(row["Description"])
            with col3:
                url = row["Attachment File"]
                if url and url != "-":
                    download_key = f"download_update_{idx}"
                    if st.button("Download", key=download_key):
                        try:
                            dest_folder = Path(download_folder) / "updates"
                            dest_folder.mkdir(parents=True, exist_ok=True)
                            result = nse_instance.download_document(url, dest_folder)
                            st.session_state.status_msgs.append(f"Downloaded to {result}")
                            st.rerun()
                        except Exception as e:
                            st.session_state.status_msgs.append(f"Error: {e}")
                            st.rerun()
                else:
                    st.write("-")

# --- Press Releases Table ---
if show_press_releases and st.session_state.press_releases_df is not None and not st.session_state.press_releases_df.empty:
    with st.expander("Press Releases", expanded=False):
        press_releases_df = st.session_state.press_releases_df
        nse_instance = st.session_state.nse_instance or NSE(download_folder)

        if st.button("Download All Press Release Attachments"):
            count = 0
            for idx, row in press_releases_df.iterrows():
                url = row["Attachment File"]
                if url and url != "-":
                    try:
                        dest_folder = Path(download_folder) / "press_releases"
                        dest_folder.mkdir(parents=True, exist_ok=True)
                        nse_instance.download_document(url, dest_folder)
                        count += 1
                    except Exception as e:
                        st.session_state.status_msgs.append(f"Error downloading {url}: {e}")
            st.session_state.status_msgs.append(f"Downloaded {count} press release attachments.")
            st.rerun()

        for idx, row in press_releases_df.iterrows():
            col1, col2, col3 = st.columns([2, 5, 2])
            with col1:
                st.write(row["Announcement Date"])
            with col2:
                st.write(row["Description"])
            with col3:
                url = row["Attachment File"]
                if url and url != "-":
                    download_key = f"download_press_release_{idx}"
                    if st.button("Download", key=download_key):
                        try:
                            dest_folder = Path(download_folder) / "press_releases"
                            dest_folder.mkdir(parents=True, exist_ok=True)
                            result = nse_instance.download_document(url, dest_folder)
                            st.session_state.status_msgs.append(f"Downloaded to {result}")
                            st.rerun()
                        except Exception as e:
                            st.session_state.status_msgs.append(f"Error: {e}")
                            st.rerun()
                else:
                    st.write("-")

# --- Status Window ---
if st.session_state.status_msgs:
    try:
        with st.expander("Status", expanded=True):
            for msg in st.session_state.status_msgs:
                st.markdown(msg, unsafe_allow_html=True)
    except Exception:
        for msg in st.session_state.status_msgs:
            st.markdown(msg, unsafe_allow_html=True)
    except Exception:
        for msg in st.session_state.status_msgs:
            st.markdown(msg, unsafe_allow_html=True)
            if st.button("Download", key=download_key):
                try:
                    dest_folder = Path(download_folder) / "press_releases"
                    dest_folder.mkdir(parents=True, exist_ok=True)
                    result = nse_instance.download_document(url, dest_folder)
                    st.session_state.status_msgs.append(f"Downloaded to {result}")
                    st.rerun()
                except Exception as e:
                    st.session_state.status_msgs.append(f"Error: {e}")
                    st.rerun()
            else:
                st.write("-")

