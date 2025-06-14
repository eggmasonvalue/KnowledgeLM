# NSE Company Wiki Downloader

A Streamlit app to download and organize NSE company announcements and attachments.

## Value Proposition
This is intended to be used as a companion to tools like NotebookLM to supplement fundamental analysis of NSE-listed companies
NSE doesn't have limits on the from and to date ranges(unlike BSE) but it lacks the option to batch download documents

## Features

- Download announcements and attachments by category (Transcripts, Investor Presentations, Credit Rating, Related Party Transactions).
- Display and download attachments for Resignations/Cessations, Updates (with Regulation 30), and Press Releases in collapsible windows.
- "Download all" and per-filing download options for each window

## Usage

1. Enter the symbol, from date, and to date.
2. Choose download categories and/or which windows to display.
3. Click "Get Announcements" to fetch and process data.
4. Use the collapsible windows to view and download relevant attachments.

## Requirements

- Python 3.8+
- streamlit
- pandas
- requests

## How to Run

```sh
streamlit run app.py
```
