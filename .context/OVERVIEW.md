# KnowledgeLM Overview

A Streamlit web app for batch downloading NSE company announcements by category, designed as a research companion for NotebookLM.

## Problem Solved

- **Batch downloads**: NSE lacks bulk download/multi-category selection
- **Filtering**: Both NSE and BSE have confusing phantom categories

## Core Features

- Download announcements by category (Transcripts, Investor Presentations, Credit Ratings, Related Party Transactions, Annual Reports)
- View/download individual filings (Resignations, Reg 30 Updates, Press Releases)
- Credit ratings: Primary source (screener.in, all-time) with NSE fallback (date-filtered)
- Auto-creates organized download folders

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Data | pandas, requests |
| NSE API | `nse` library |
| Web scraping | BeautifulSoup |
| HTML→Markdown | markdownify (optional) |

## Dependencies

- Python 3.8+
- streamlit, pandas, nse, requests
- weasyprint (PDF generation)
- beautifulsoup4, markdownify (credit rating scraping)

## How to Run
```sh
# Install dependencies
uv sync  # or pip install .

# Run the app
streamlit run src/knowledgelm/app.py
```
