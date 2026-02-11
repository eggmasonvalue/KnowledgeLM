# Feature Design

## [done] Core Download Categories

Batch download filings by category with configurable filters:
- Analyst Call Transcripts
- Investor Presentations  
- Credit Ratings (dual-source)
- Related Party Transactions
- Annual Reports (date range or all)

## [done] CLI Interface (v3.0)

Full programmatic access via `knowledgelm` command:
- **Download**: Batch download with automated folder creation.
- **Discovery**: `--help` on all levels for self-documenting interface.
- **JSON Output**: `--json` flag for machine readability and AI agent parsing.

## [done] ValuePickr Forum Export (v4.1)

Export entire ValuePickr (Discourse) threads for offline reading and AI analysis.
- **Source**: ValuePickr Forum (JSON API).
- **Format**: Clean PDF with embedded images and charts.
- **Design Goals**:
    - **Multimodal**: PDF format preserves charts for NotebookLM visual analysis.
    - **High Signal**: Strips usernames, avatars, signatures, and badges. Only retains Dates and Content.
    - **Reliability**: Uses JSON API for data fetching (avoids fragile HTML scraping) and Headless Chrome for rendering.

## [done] Agent-First Design (v3.0)

- **Standardized Skill**: `SKILL.md` compliant with [Agent Skills](https://agentskills.io) standard, hosted in a [separate public repository](https://github.com/eggmasonvalue/knowledgelm-nse) for decoupled distribution.
- **Automation workflows**: Optimized for LLM tools (Claude Code, Gemini CLI, etc.).
- **NotebookLM Synergy**: Purpose-built `list-files --json` command to facilitate source injection.

## [done] Credit Rating Dual-Source
    
1. Primary: Scrape screener.in (all-time)
   - **ICRA**: Direct PDF link resolution (bypassing JS viewer).
   - **HTML Reports (CRISIL, etc.)**: Selenium-based HTML-to-PDF conversion.
   - **PDF Reports**: Direct download.
2. Fallback: NSE API (date-filtered)

## [done] Input Validation

- **Symbol Check**: Validates company symbol against NSE using `equityQuote` before attempting downloads.

## [done] Individual Filing Views

Expandable tables with per-row downloads:
- Resignations
- Regulation 30 Updates (experimental)
- Press Releases

## [done] Session State Management

Persist data across Streamlit reruns:
- Fetched announcements
- Category counts
- Status messages

- DataFrames for view tables

## [done] Modular Architecture

Separation of concerns:
- **UI Layer**: Streamlit (`app.py`) handles only presentation.
- **Service Layer**: `KnowledgeService` orchestrates downloads.
- **Data Adapters**: Isolated `NSEAdapter` and `ScreenerAdapter`.
- **Config**: Centralized settings in `config.py`.

## [done] Security Hardening

- **SSL Verification**: Enabled for all external requests.
- **Input Sanitization**: Strict validation of download folder names (`file_utils.sanitize_folder_name`).
- **Logging**: Replaced console printing with structured logging.


## [done] Standardized Folder Structure (v4.2)

Standardized download destinations for better research organization:
- **NSE Filings**: `_filings` suffix (e.g., `HDFCBANK_filings`).
- **ValuePickr Exports**: `_valuepickr` suffix (e.g., `HDFCBANK_valuepickr`), containing both PDF and references.
- **Agent Compatibility**: Consistent naming makes it easier for agents to locate sources for NotebookLM.

---

## [idea] Future Enhancements
- [done] github web page for agent skills
- **manage dependencies:** write github workflow - tests that check for breaking changes in external dependencies - nse scraper, screener scraper, icra, etc. as github actions daily to validate reports. or make .toml tighter with respect to external uncommon dependencies like nse since they might introduce breaking changes at any time.
- naming needs to be better for the docs. it's still terribly random
- **3P info skill/code:** TJI finance as knowledge base source - ask AI to figure out and visit the tijori finance website for the stock, go to the knowledge base, get all the links, send the VP link to the CLI and add the rest of the links directly. Maybe write a skill for this instead of CLI or code. write a skill for 3P filings and make them optional to add. nest the skill such that we can give various temperature levels - operator interviews to public sentiment analysis. offer events as a separate input to understand what's going on in the last few years. then we can take all the announcements instead of struggling for enforcement. 
- [done] npx for skills instead of AI instruction right now since anyone who will copy paste this instruction will have a terminal too.
