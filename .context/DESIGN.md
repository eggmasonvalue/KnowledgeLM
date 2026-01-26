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

## [done] Agent-First Design (v3.0)

- **Standardized Skill**: `SKILL.md` compliant with [Agent Skills](https://agentskills.io) standard.
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


---

## [idea] Future Enhancements

- BSE support
- Export to structured formats (CSV, Excel)
- Configurable alert filters
- Progress bars for bulk downloads
