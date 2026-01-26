# KnowledgeLM Overview

A CLI and Streamlit web app for batch downloading NSE company announcements by category, designed as a research companion for NotebookLM. Includes an agent skill for use with AI coding assistants.

## Problem Solved

- **Batch downloads**: NSE lacks bulk download/multi-category selection
- **Filtering**: Both NSE and BSE have confusing phantom categories
- **AI Integration**: No easy way to programmatically feed filings to research tools

## Core Features

- **CLI** (`knowledgelm`): Batch download with `--json` output for automation
- **Agent Skill**: Works with Claude Code, Gemini CLI, Codex, and other LLMs
- Download announcements by category (Transcripts, Investor Presentations, Credit Ratings, Related Party Transactions, Annual Reports)
- View/download individual filings via Streamlit UI (Resignations, Reg 30 Updates, Press Releases)
- Credit ratings: Primary source (screener.in, all-time) with NSE fallback (date-filtered)
- **NotebookLM Integration**: Skill includes workflow for adding downloads as notebook sources

## Tech Stack

| Layer | Technology |
|-------|------------|
| CLI | Click |
| Frontend | Streamlit |
| Data | pandas, requests |
| NSE API | `nse` library |
| Web scraping | BeautifulSoup, Selenium |
| Agent Skill | [Agent Skills](https://agentskills.io) standard |

## Dependencies

- Python 3.12+
- click, streamlit, pandas, nse, requests
- selenium, webdriver-manager (credit ratings)
- beautifulsoup4 (web scraping)

## How to Run

```bash
# Install
uv sync  # or pip install .

# CLI
knowledgelm download HDFCBANK --from 2023-01-01 --to 2025-01-26

# Web UI
streamlit run src/knowledgelm/app.py
```
