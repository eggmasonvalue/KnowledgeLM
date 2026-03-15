# KnowledgeLM 🧠

[![Version](https://img.shields.io/badge/version-5.1.0-blue.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Built with uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://docs.astral.sh/uv/)

A research companion for **NotebookLM** that automates the collection of NSE company filings. Designed to be operated by AI agents (Claude Code, Gemini CLI, etc.).

## 🚀 Instant Setup (AI Agents)

Install the [knowledgelm-nse](https://github.com/eggmasonvalue/knowledgelm-nse) agent skill using:

> `npx skills add eggmasonvalue/knowledgelm-nse`

This skill allows your AI agent to batch download a comprehensive bundle of investor materials(exchange filings - .pdfs and parsed XBRLs) and valuepickr forum thread for Indian publicly listed companies and optionally integrate them into NotebookLM for deep fundamental analysis.

---

## ✨ Features

- **Agent-First**: Optimized for LLMs with a standardized [Agent Skill](.agent/skills/knowledgelm-nse/SKILL.md), and strictly formatted JSON output to `stdout` to preserve the context window.
- **Batch Downloads**: NSE lacks bulk extraction; KnowledgeLM fetches filings by category in seconds via `fetch nse`.
- **Granular XBRL Parsing**: Extracts fine-grained facts (Personnel Changes/Resignations, Board Outcomes, Shareholder Meetings) into clean JSON using our standalone, highly optimized `nse-xbrl-parser` offline resolution engine.
- **Issue Documents**: IPO prospectus, rights offers, QIP placements, information memoranda, and scheme documents — unified across 5 NSE endpoints.
- **Markdown Conversion**: Built-in `convert` commands to transform PDFs into LLM-ready Markdown.
- **NotebookLM Synergy**: Purpose-built commands to facilitate source injection and bundled prompt templates for audio overviews.
- **ValuePickr Forum Export**: Export entire forum threads to clean, research-ready PDFs with reference extraction via `fetch vp`. Besides, Valuepickr forum thread .pdfs are formatted for a distraction-free reading experience for humans.
- **Interactive UI**: Browse and download individual filings (Resignations, Press Releases, etc.) via Streamlit.

## 🐧 ARM / Linux Setup

On ARM Linux devices, official Selenium Manager binaries are unavailable. You must manually install `chromedriver` using your system's package manager.

```bash
# Example (Debian/Ubuntu/Termux):
sudo apt install chromium-driver  # Package names vary
```

**Requirement**: Ensure `chromedriver` is available in your `$PATH`.

## 🛠️ Manual Installation & Usage

### CLI Usage

```bash
# Install from PyPI
uv tool install knowledgelm --upgrade

# Fetch corporate filings (NSE)
knowledgelm fetch nse HDFCBANK --start 2024-01-01 --end 2025-01-26 --datasets transcripts,annual_reports

# Fetch personnel changes/resignations (XBRL)
knowledgelm fetch nse RELIANCE --start 2024-01-01 --end 2025-01-26 --datasets personnel

# Fetch issue documents (IPO, rights, QIP, schemes)
knowledgelm fetch nse SWIGGY --start 2020-01-01 --end 2025-12-31 --datasets issue_documents

# Export forum thread (ValuePickr)
knowledgelm fetch vp "https://forum.valuepickr.com/t/hdfc-bank-limited/123" --symbol HDFCBANK

# Convert downloaded PDFs to Markdown
knowledgelm convert dir "./HDFCBANK_sources/transcripts/"
```

### Web UI

Launch the interactive dashboard:

```bash
uv run streamlit run src/knowledgelm/app.py
```

## 📂 Project Structure

- **`.agent/`**: AI Agent resources, skills, and prompt templates.
- **`.context/`**: Living documentation (Architecture, Design, Changelog).
- **`src/`**: Core logic and Streamlit app.
- **`tests/`**: Unit and integration tests.

See [.context/ARCHITECTURE.md](.context/ARCHITECTURE.md) for detailed diagrams.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
