# KnowledgeLM

A CLI and web app to batch download NSE company announcements by category.  
Intended as a companion for NotebookLM and other research tools.

## Features

- **CLI**: Batch download filings with `knowledgelm download SYMBOL --from DATE --to DATE`
- **Web UI**: Streamlit app for interactive downloads
- Download announcements by category: Transcripts, Investor Presentations, Credit Ratings, Related Party Transactions, Annual Reports
- **AI Agent Skill**: Works with Claude Code, Gemini CLI, Codex, and other LLM agents
- **NotebookLM Integration**: Easily add downloaded files as sources to NotebookLM notebooks

## Quick Start (CLI)

```bash
# Install
uv tool install knowledgelm

# Download all categories for a company
knowledgelm download HDFCBANK --from 2023-01-01 --to 2025-01-26

# Download specific categories
knowledgelm download INFY --from 2020-01-01 --to 2025-01-26 --categories transcripts,credit_rating

# List available categories
knowledgelm list-categories

# List downloaded files (for NotebookLM integration)
knowledgelm list-files ./HDFCBANK_knowledgeLM --json
```

## AI Agent Skill Installation

KnowledgeLM includes an agent skill for use with Claude Code, Gemini CLI, Codex, or any LLM that supports the [Agent Skills](https://agentskills.io) standard.

**To install the skill, give this prompt to your AI agent:**

> Install the knowledgelm-nse skill by copying the `.agent/skills/knowledgelm-nse/` directory (including all bundled resources) from the knowledgelm repository to your skills directory. The skill enables batch downloading of NSE India company filings and integration with NotebookLM.

The agent will locate the skill directory and install it to the appropriate location for your environment.

## Web UI Usage

1. Run the Streamlit app:
   ```bash
   streamlit run src/knowledgelm/app.py
   ```

2. Enter the company symbol, start date, and end date.
3. Choose the download folder.
4. Select download categories and/or which filings to display.
5. Click "Fetch Filings" to download.

**Note on Credit Ratings:** The app tries the primary source first (all available ratings). If unavailable, the fallback only fetches ratings within your date range.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended)

Using uv:

```bash
uv sync
```

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov

# Format code
ruff format src/ tests/
```

