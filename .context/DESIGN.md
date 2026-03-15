# Feature Design

## [done] Core Download Categories

Batch download filings by category with configurable filters:
- Analyst Call Transcripts
- Investor Presentations
- Credit Ratings (Screener.in sole source)
- Related Party Transactions
- Annual Reports (date range or all)

## [done] CLI Interface (v3.0)

Full programmatic access via `knowledgelm`
- **CLI**: Click-based command interface (`fetch nse`, `fetch vp`, `list-datasets`) designed strictly for LLM Agents.
- **Categories**: `issue_documents` and XBRL categories (`personnel`, `key_announcements`, `shm`) exist as valid target datasets for the `fetch nse` command.
- **JSON Output**: All CLI commands output pure JSON format for agent parsing without terminal noise.

## [done] ValuePickr Forum Export (v4.1)

Export entire ValuePickr (Discourse) threads for offline reading and AI analysis.
- **Source**: ValuePickr Forum (JSON API).
- **Format**: Clean PDF with embedded images and charts.
- **Interfaces**: Available via universal CLI (`knowledgelm fetch vp`) and Streamlit WebUI (checkbox).
- **Design Goals**:
    - **Multimodal**: PDF format preserves charts for NotebookLM visual analysis.
    - **High Signal**: Strips usernames, avatars, signatures, and badges. Only retains Dates and Content.
    - **Reliability**: Uses JSON API for data fetching (avoids fragile HTML scraping) and Headless Chrome for rendering.

## [done] Agent-First Design (v4.2.1)

- **Standardized Skill**: `SKILL.md` compliant with [Agent Skills](https://agentskills.io) standard, hosted in a [separate public repository](https://github.com/eggmasonvalue/knowledgelm-nse) for decoupled distribution.
- **Context Preservation**: Strictly silent execution (no `stdout`/`stderr` noise) to prevent LLM context window pollution.
- **Automation workflows**: Optimized for LLM tools (Claude Code, Gemini CLI, etc.) with structured JSON results.
- **Unified Actions**: The CLI exposes a simple `fetch nse` and `fetch vp` verb/noun structure to lower cognitive load for LLM models.

## [done] Credit Rating (Screener.in)

1. Primary: Scrape screener.in (all-time)
   - **ICRA**: Direct PDF link resolution (bypassing JS viewer).
   - **HTML Reports (CRISIL, etc.)**: Selenium-based HTML-to-PDF conversion.
   - **PDF Reports**: Direct download.

## [done] Input Validation

- **Symbol Check**: Validates company symbol against NSE using `equityQuote` before attempting downloads.

## [done] Individual Filing Views (v5.1)

Expandable tables with per-row downloads:
- Change in Personnel (via XBRL)
- Key announcements (via XBRL)
<!-- - Board Meeting Outcome (via XBRL) -->
- Shareholder Meetings (via XBRL)
- Press Releases (legacy filter)
- Regulation 30 Updates (legacy filter)

## [done] PDF to Markdown Converter (v5.0.0)

A standalone `convert` command handles offline PDF-to-Markdown conversion using `markitdown`.

- **Explicit Post-Processing**: Conversion is inherently decoupled from the `fetch` command.
- **Why**: Performance tuning against real NSE data (like HDFCBANK Annual Reports) showed conversion times of over **2 minutes per file** (1.8+ million characters). Running this during default fetches would trigger massive latency blocking and cause LLM Agents to timeout natively.
- **Agent Strategy**: Agents should `fetch` rapidly, evaluate filenames from the JSON result, and then strategically execute `convert file` or `convert dir` strictly on high-yield targets.
- **Zero-Trust Validation**: Implements aggressive input validation on target paths to handle LLM hallucinations (e.g. attempting to convert missing files, non-PDF files, or directories that don't exist).

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
- **NSE Filings**: `_sources` suffix (e.g., `HDFCBANK_sources`).
- **ValuePickr Exports**: `_valuepickr` suffix (e.g., `HDFCBANK_valuepickr`), containing both PDF and references.
- **Agent Compatibility**: Consistent naming makes it easier for agents to locate sources for NotebookLM.

## [done] Issue Documents (v5.0)

Download company share issue documents from NSE corporate filings:
- **Document Types**: Offer Documents (IPO), Rights Issue, QIP Offer, Information Memorandum, Scheme of Arrangement.
- **Category**: `issue_documents` within the existing `fetch nse --datasets` argument — no date range dependency.
- **API**: 5 NSE endpoints under `/api/corporates/offerdocs/...`, fetched via the `nse` library's session.
- **Matching**: Symbol-based for Rights, QIP, Schemes; company-name-based (via `equityMetaInfo`) for Offer Docs and Info Memo where symbol fields are unreliable.
- **ZIP Handling**: Delegated to the `nse` library's native `download_document` which auto-extracts ZIPs.
- **Output**: `{SYMBOL}_sources/share_issuance_docs/{type}/` subfolder structure.

## [done] Resignations Query CLI (v5.0)

Standalone `knowledgelm resignations` command for querying board-level resignations (Replaced by `personnel` datatset in `fetch nse`).

---

## [done] XBRL Harvester Refactor (v5.1.1)

Overhaul of the XBRL processing pipeline to use native parsing:
- **Arelle Integration**: Replaced legacy `xbrl_labels.json` mapping with the `arelle` library for parsing raw XBRL XML filings.
- **Dynamic Mapping**: Labels are now resolved directly from official NSE taxonomy schemas, ensuring accuracy and handling updates automatically.
- **Taxonomy Management**: New `TaxonomyManager` handles downloading, extracting (manual unzip for robustness), and caching of massive taxonomy ZIPs in `.taxonomies/`.
- **Robust Fallback**: Implements a safety net for taxonomies with missing/broken schemas (e.g., Reg30). If Arelle parsing fails, the system automatically degrades to using NSE's internal API to fetch raw parsed data, ensuring availability.
- **Dependency Reuse**: All network traffic is consolidated through `NSEAdapter` for consistent session handling.

---

## [idea] Future Enhancements
- **manage dependencies:** write github workflow - tests that check for breaking changes in external dependencies - nse scraper, screener scraper, icra, etc. as github actions daily to validate reports. or make .toml tighter with respect to external uncommon dependencies like nse since they might introduce breaking changes at any time.
- naming needs to be better for the docs. it's still terribly random
- **3P info skill/code:** TJI finance as knowledge base source - ask AI to figure out and visit the tijori finance website for the stock, go to the knowledge base, get all the links, send the VP link to the CLI and add the rest of the links directly. Maybe write a skill for this instead of CLI or code. write a skill for 3P filings and make them optional to add. nest the skill such that we can give various temperature levels - operator interviews to public sentiment analysis. offer events as a separate input to understand what's going on in the last few years. then we can take all the announcements instead of struggling for enforcement.
- **RPT upgrade** - replace RPT with RPT XBRL along with integrated filing-financials/governance with selective fields exposed

## Pending Fixes
- cli docstrings as well as organisation are terrible. need fixes
- provide markdown option in CLI that uses the library to iterate through all the .pdfs and convert to .md
- performance audit
- security audit, especially input validation