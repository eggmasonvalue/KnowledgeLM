import streamlit as st
from datetime import date
from typing import Dict, Any, Tuple
from FilingsDownloader import download_announcements

st.title("NSE Company Wiki Downloader")

symbol = st.text_input("Symbol", value="HDFCBANK")
from_date = st.date_input("From Date", value=date(2024, 1, 1))
to_date = st.date_input("To Date", value=date.today())

st.markdown("**Select what to download:**")
download_transcripts = st.checkbox("Transcripts", value=True)
download_investor_presentations = st.checkbox("Investor Presentations", value=True)
download_press_releases = st.checkbox("Press Releases", value=True)

download_folder = st.text_input("Download Folder", value="artifacts")

if st.button("Download"):
    with st.spinner("Downloading..."):
        data, category_counts = download_announcements(
            symbol=symbol,
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=to_date.strftime("%Y-%m-%d"),
            download_folder=download_folder,
            download_transcripts=download_transcripts,
            download_investor_presentations=download_investor_presentations,
            download_press_releases=download_press_releases,
        )
    st.write(f"Parsed {len(data)} announcements and downloaded relevant docs. Check the '{download_folder}' folder.")
    st.subheader("Downloaded files by category:")
    for label, count in category_counts.items():
        st.markdown(f"**{label.capitalize()}s:** <b>{count}</b>", unsafe_allow_html=True)
