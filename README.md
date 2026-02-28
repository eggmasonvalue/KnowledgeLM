# KnowledgeLM 🧠

[![Version](https://img.shields.io/badge/version-4.2.1-blue.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Built with uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://docs.astral.sh/uv/)

A research companion for **NotebookLM** that automates the collection of NSE company filings. Designed to be operated by AI agents (Claude Code, Gemini CLI, etc.).

## 🚀 Instant Setup (AI Agents)

Install the [knowledgelm-nse](https://github.com/eggmasonvalue/knowledgelm-nse) agent skill using

> `npx skills add eggmasonvalue/knowledgelm-nse`


This skill allows your AI agent to batch download investor materials (transcripts, presentations, credit ratings, annual reports) for Indian publicly listed companies and integrate them into NotebookLM for deep fundamental analysis.

---

## ✨ Features

- **Agent-First**: Optimized for LLMs with standardized [Agent Skill](.agent/skills/knowledgelm-nse/SKILL.md), and silent execution (primary output is JSON) to preserve the context window.
- **Batch Downloads**: NSE lacks bulk extraction; KnowledgeLM fetches filings by category in seconds.
- **Granular XBRL Parsing**: Extracts fine-grained facts (Personnel Changes, Board Outcomes, Shareholder Meetings) into clean JSON using our standalone, highly optimized `nse-xbrl-parser` offline resolution engine.
- **Issue Documents**: IPO prospectus, rights offers, QIP placements, information memoranda, and scheme documents — unified across 5 NSE endpoints with inconsistent schemas, unreliable metadata, and mixed archive formats so you don't have to be.
- **NotebookLM Synergy**: Purpose-built commands to facilitate source injection and bundled prompt templates for audio overviews.
- **Credit Rating Dual-Source**: Primary extraction from Screener.in (high-fidelity PDF conversion) with NSE API fallback.
- **ValuePickr Forum Export**: Export entire forum threads to clean, research-ready PDFs with reference extraction.
- **Interactive UI**: Browse and download individual filings (Resignations, Press Releases, etc.) via Streamlit.

### 🐧 ARM / Linux Setup (Termux, Raspberry Pi, Android AVF)

On ARM Linux devices, official Selenium Manager binaries are unavailable. You must manually install `chromedriver` using your system's package manager.

```bash
# Example (Debian/Ubuntu/Termux):
sudo apt install chromium-driver  # Package names vary (e.g. chromium, chromium-chromedriver, etc.)
```

**Requirement**: Ensure `chromedriver` is available in your `$PATH`. The tool will automatically detect and use it.

## ️ Manual Installation & Usage

If you prefer to use the tool directly from your terminal:

### CLI Usage

```bash
# Install (requires uv)
uv tool install knowledgelm

# Download filings
knowledgelm download HDFCBANK --from 2024-01-01 --to 2025-01-26

# Download issue documents (IPO, rights, QIP, schemes)
knowledgelm download SWIGGY --from 2020-01-01 --to 2025-12-31 --categories issue_documents

# Export forum thread
knowledgelm forum "https://forum.valuepickr.com/t/hdfc-bank-limited/123" --symbol HDFCBANK
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
