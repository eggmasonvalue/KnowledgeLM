# Changelog

## [Unreleased] - 2026-03-15

### Added
- **Centralized Pluralization Utility (`text_utils.py`)**: Introduced a dedicated text processing utility for consistent, professional output formatting across the CLI and UI.
- **Improved Dataset Discovery**: The `list-datasets` command now returns pluralized, user-friendly labels (e.g., "Analyst Call Transcripts") rather than raw singular labels.

### Changed
- **Premium CLI Logging**: Refactored `fetch nse` and `convert dir` log output to use dynamic pluralization (e.g., "Found 1 PDF" vs "Found 5 PDFs"), providing a more polished command-line experience.
- **Pluralization Refactor**: Consolidated local pluralization logic in `app.py` into the shared `text_utils` module for better maintainability.

### Documentation
- **Agent Skill Overhaul (`SKILL.md`)**: Rewrote the agent skill to reflect the v5.2.0 CLI interface. Replaced all deprecated commands (`download` → `fetch nse`, `forum` → `fetch vp`, `resignations` → `--datasets personnel`), added the `convert` workflow, updated all 10 dataset keys, added the CLI JSON contract section, and included the full output structure tree.

### Added
- **Unified Fetch CLI**: Completely rewrote `cli.py` to use a universal `fetch nse` and `fetch vp` verb/noun structure, removing `download`, `forum`, `personnel`, `key-announcements`, and `shareholder-meetings` as top-level commands. This drastically reduces the cognitive load for LLM Agents trying to drive the tool.
- **PDF-to-Markdown Converter (`convert`)**: Added a standalone `convert` CLI group with `file` and `dir` subcommands leveraging `markitdown` for high-quality LLM context extraction.
- **Standardized PDF Filenames**: Implemented dynamic generation of standardized filenames for downloaded PDFs across all endpoints (NSE and Screener). Files are now saved using an ISO-8601 formatted date prefix and category shorthand (e.g., `2024_AR.pdf` or `2025-01-17_Transcript.pdf`).
- **LLM-Oriented Docstrings**: Rewrote all CLI `--help` strings to focus explicitly on the JSON input/output schemas of the data extraction.
- **ValuePickr Forum Support in WebUI**: Added UI elements to `app.py` for downloading ValuePickr forum threads.
- **Configurable JSON Output**: Introduced an `output_keys` configuration option in `config.py` for XBRL categories (`personnel`, `key_announcements`, and `shm`).

### Fixed
- **Resilient Fact Extraction**: Enhanced `nse-xbrl-parser` to ensure the raw XML fallback runs even if Arelle fails to resolve the official NSE taxonomy. This prevents data loss for announcements with newly published or non-standard SEBI schemas (e.g., specific "Arrest" or "Fraud" disclosures).
- **Robust XBRL Resolution**: Updated `nse-xbrl-parser` to fix "Shadowed XSD" and "Relative Path Resolution" errors.
- **Arelle Parsing Bugs**: Resolved a critical indentation bug where Arelle was trying to parse files that had already been deleted from the temporary directory.
- **Verbose Fallbacks**: Added aggressive warning logs (`!!! SWITCHING TO INTERNAL API FALLBACK !!!`) if Arelle parsing fails.

### Changed
- **New Output Directory Structure**: Renamed the default download directory from `{SYMBOL}_filings` to `{SYMBOL}_sources`.
- **Screener Only for Credit Ratings**: Disabled the NSE announcements fallback for credit ratings. Screener.in is now the sole source.
- **Lazy Loading Announcements**: Optimized `process_request` to lazy-load the general announcements from the NSE API.
- **Human-Readable Labels**: XBRL parsing now preserves original casing and spaces from the taxonomy.

## [5.0.0] - 2026-02-15

### Features
- **Issue Documents**: New `issue_documents` category in the `download` command (deprecated in 5.1.0) for batch downloading company share issue documents from NSE.
- **Resignations CLI**: New `resignations` standalone query command (deprecated in 5.1.0 in favor of `fetch nse --datasets personnel`).

## [4.2.1] - 2026-02-14

### Documentation
- **Formalized Agent-First Design Principles**: Added strict development guidelines to `.context/OVERVIEW.md` and `.context/CONVENTIONS.md`.

### Fixes
- **Silent CLI Execution**: Refactored `cli.py` to route all informational and error messages to `knowledgelm.log` when JSON output is not requested.
- **ValuePickr PDF Generator Cleanup**: Migrated to native Selenium Manager and implemented Selenium silencing.
...