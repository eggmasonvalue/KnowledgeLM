"""Streamlit UI for batch downloading NSE company announcements."""

import logging
from datetime import date
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from knowledgelm.config import (
    DOWNLOAD_CATEGORIES_CONFIG,
)
from knowledgelm.core.forum import ForumClient, PDFGenerator, ReferenceExtractor
from knowledgelm.core.service import KnowledgeService
from knowledgelm.utils.text_utils import pluralize


# Configure logging — route to file, keep terminal clean
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="knowledgelm.log",
    filemode="a",
)

# --- Constants ---
# --- Session State Initialization ---
if "data" not in st.session_state:
    st.session_state.data = None
if "category_counts" not in st.session_state:
    st.session_state.category_counts = None
if "scroll_to_results" not in st.session_state:
    st.session_state.scroll_to_results = False
if "status_msgs" not in st.session_state:
    st.session_state.status_msgs = []
# We no longer rely on a global 'nse_instance' in session state

st.title("KnowledgeLM")
st.caption("A notebookLM companion for NSE company research")

# --- Search and Output Card ---
with st.container(border=True):
    st.subheader("Search and Output Settings")
    col_h1, col_h2, col_h3, col_h4 = st.columns([1.5, 1, 1, 2.5])
    with col_h1:
        symbol = st.text_input("Symbol", value="HDFCBANK")
    with col_h2:
        from_date = st.date_input("Start Date", value=date(2024, 1, 1))
    with col_h3:
        to_date = st.date_input("End Date", value=date.today())
    with col_h4:
        folder_name_input = st.text_input(
            "Output Folder",
            value=f"{symbol}_sources",
            help="Name of the folder to create. Do NOT include paths (e.g., 'C:\\').",
        )

# --- Filing Category Selection Card ---
with st.container(border=True):
    st.subheader("Select Filing Categories")
    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        dl_transcripts = st.checkbox("Analyst call transcripts", value=True)
        dl_investor_pres = st.checkbox("Investor presentations", value=True)
        dl_annual_reports = st.checkbox("Annual reports", value=True)
        # Annual Report sub-option - flat layout for perfect alignment
        dl_annual_reports_all = st.checkbox(
            "All ARs (Ignore Range)",
            value=False,
            disabled=not dl_annual_reports
        )
        annual_reports_download_all = dl_annual_reports_all if dl_annual_reports else False

    with col_c2:
        dl_press_releases = st.checkbox("Press releases", value=True)
        dl_credit_ratings = st.checkbox("Credit ratings", value=False)
        dl_related_party = st.checkbox("Related party transactions", value=False)
        dl_issue_docs = st.checkbox(
            "Issue documents",
            value=False,
            help="IPO, Rights, QIP offer docs, info memoranda, scheme of arrangement docs.",
        )

    with col_c3:
        # XBRL-based categories grouped logically on the right
        dl_personnel = st.checkbox("Change in Personnel", value=True)
        dl_key_ann = st.checkbox("Key announcements", value=True)
        # dl_board_outcome = st.checkbox("Board Meeting Outcomes", value=True)
        dl_shm = st.checkbox("Shareholder Meetings", value=True)

    st.write("")
    dl_forum = st.checkbox("ValuePickr Thread", value=False)
    forum_url = ""
    if dl_forum:
        forum_url = st.text_input("Thread URL", placeholder="https://forum.valuepickr.com/t/.../1234")

# --- Main Action Button ---
st.write("") # Spacer
if st.button("Download", type="primary", use_container_width=False):
    st.session_state.status_msgs = []
    st.session_state.scroll_to_results = False

    # Validation
    try:
        service = KnowledgeService(".")

        with st.spinner("Downloading and processing filings..."):
            options = {
                "download_transcripts": dl_transcripts,
                "download_investor_presentations": dl_investor_pres,
                "download_press_releases": dl_press_releases,
                "download_credit_rating": dl_credit_ratings,
                "download_related_party_txns": dl_related_party,
                "download_annual_reports": dl_annual_reports,
                "download_issue_documents": dl_issue_docs,
                "download_personnel": dl_personnel,
                "download_key_announcements": dl_key_ann,
                # "download_board_outcome": dl_board_outcome,
                "download_shm": dl_shm,
            }

            data, category_counts = service.process_request(
                symbol=symbol,
                from_date=from_date,
                to_date=to_date,
                folder_name=folder_name_input,
                options=options,
                annual_reports_all_mode=annual_reports_download_all,
            )

            if dl_forum and forum_url:
                client = ForumClient()
                thread_data = client.get_full_thread(forum_url)

                output_dir = Path.cwd() / folder_name_input / "forum_valuepickr"
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "forum_thread.pdf"

                generator = PDFGenerator()
                generator.generate_thread_pdf(thread_data, output_path)

                ref_extractor = ReferenceExtractor()
                ref_content = ref_extractor.extract_references(thread_data)
                ref_path = output_dir / "forum_links.md"
                with open(ref_path, "w", encoding="utf-8") as f:
                    f.write(ref_content)

                category_counts["ValuePickr Thread"] = 1

            st.session_state.data = data
            st.session_state.category_counts = category_counts

            # constructing detailed status summary
            processed_counts = []

            for cat_key, config in DOWNLOAD_CATEGORIES_CONFIG.items():
                label = config["label"]
                count = category_counts.get(label, 0)
                if count > 0:
                    processed_counts.append(f"• {count} {pluralize(label, count)}")


            if category_counts.get("ValuePickr Thread", 0) > 0:
                processed_counts.append("• 1 ValuePickr Thread")

            summary_header = f"Successfully processed **{symbol}** filings in `{folder_name_input}`."
            if processed_counts:
                summary_body = f"{summary_header}\n\n" + "\n\n".join(processed_counts)
            else:
                summary_body = summary_header

            st.session_state.scroll_to_results = True

            # Anchor div for results scroll
            st.markdown('<div id="results-anchor"></div>', unsafe_allow_html=True)
            st.success(summary_body)

            # Smooth scroll to results area
            if st.session_state.scroll_to_results:
                components.html(
                    """
                    <script>
                        var resultsElement = window.parent.document.getElementById('results-anchor');
                        if (resultsElement) {
                            resultsElement.scrollIntoView({behavior: 'smooth'});
                        }
                    </script>
                    """,
                    height=0,
                )
                st.session_state.scroll_to_results = False

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# --- Status Window ---
if st.session_state.status_msgs:
    try:
        with st.expander("Status", expanded=True):
            for msg in st.session_state.status_msgs:
                st.markdown(msg, unsafe_allow_html=True)
    except Exception:
        pass
