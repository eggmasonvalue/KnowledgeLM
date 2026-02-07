# Changelog

## [Unreleased]

## [4.0.0] - 2026-02-08

### Breaking Changes
- **Skill Location**: Moved agent skill from `src/knowledgelm/data/SKILL.md` to `.agent/skills/knowledgelm-nse/SKILL.md` following skill-creator best practices for directory-based structure with bundled resources

### Features
- **Self-Upgradeable Skill**: Skill can now self-upgrade by downloading latest version from GitHub raw URL
- **Bundled Resources**: Added `references/` directory with NotebookLM audio overview prompt template for fundamental analysis
- **Enhanced NotebookLM Integration**: 
  - Comprehensive version management for both notebooklm-py package and skill
  - Uses `uv tool upgrade` for package updates
  - Always runs `notebooklm skill install` to ensure skill is current
  - Handles browser extras conditionally for first-time authentication
  - Vendor-agnostic approach for different AI agent skills directories
- **Package Upgrade**: Added `uv tool upgrade knowledgelm` to Installation section

### Documentation
- **Skill Improvements**: Streamlined skill to be principle-based rather than task-like, emphasizing `--help` discovery over prescriptive commands
- **Architecture Updates**: Updated `.context/ARCHITECTURE.md` to reflect new `.agent/` directory structure with separate "Agent Resources" subgraph in mermaid diagram
- **Changelog Updates**: Updated skill path references throughout `.context/` artifacts

### Cleanup
- Removed legacy pip artifacts (root `__pycache__`, committed `.coverage`, and `nse_cookies_requests.pkl`)
- Updated documentation and agent skill to prefer `uv` over `pip`

## [3.0.0] - 2026-01-26

### Features
- **CLI Interface**: New `knowledgelm` CLI with commands:
  - `download SYMBOL --from DATE --to DATE`: Batch download filings
  - `list-categories`: Show available filing types
  - `list-files DIRECTORY --json`: List downloaded files for NotebookLM integration
- **AI Agent Skill**: Bundled `SKILL.md` at `.agent/skills/knowledgelm-nse/SKILL.md` following [Agent Skills](https://agentskills.io) open standard
- **NotebookLM Integration**: Skill includes workflow for adding downloads to NotebookLM notebooks via notebooklm-py

### Architecture
- **CLI-First Design**: All operations accessible via CLI with `--help` discovery and `--json` output for agent parsing
- **Skill Maintenance**: SKILL.md uses `--help` discovery instead of hardcoded commands (reduces sync burden)

### Dependencies
- Added `click>=8.1.0` for CLI

### Documentation
- Updated README with CLI usage, agent skill installation prompt (LLM-agnostic)


## [2.0.0] - 2026-01-26

### Security
- **SSL Verification**: Enabled SSL verification for Screener.in requests to prevent MitM attacks.
- **Input Sanitization**: Implemented `sanitize_folder_name` to prevent path traversal vulnerabilities in download folders.

### Architecture
- **Modular Design**: Split monolithic `filings_downloader.py` into:
  - `core/service.py`: Business logic and orchestration.
  - `data/nse_adapter.py`: Wrapper for NSE library.
  - `data/screener_adapter.py`: Secure scraper for Screener.in.
  - `utils/file_utils.py`: Shared utilities.
  - `config.py`: Centralized configuration.
- **UI Decoupling**: Refactored `app.py` to delegate logic to `KnowledgeService`.
- **Validation**: Added early-exit symbol validation using `nse.equityQuote()` to prevent invalid API calls.
- **Cleanup**: Removed intermediate `{symbol}_announcements.json` dump from output folder (data is ephemeral/in-memory).

### Features
- **Selenium Support**: Integrated `selenium` and `webdriver-manager` for headless Chrome operations to handle dynamic content.
- **Robust Scraper**: Added fallback logic to handle various content types (PDF vs HTML) from Screener.in.
- **Direct PDF Resolution**: implemented direct resolution for ICRA reports to bypass viewers.
- **High-Fidelity HTML Conversion**: Replaced `markdownify` with Selenium-based "Print to PDF" for better report quality.

### Documentation
- **Walkthrough**: Added a browser recording demonstrating app functionalities to `README.md`.
- **Assets**: Created `assets/` directory for media files.
- **Context Artifacts**: Added `.context/` documentation artifacts (DESIGN, ARCHITECTURE, CHANGELOG).

### Improvements
- **Logging**: Redirected library logs (NSE, Selenium) to application logger and reduced noise.
- **Project Structure**: Adopted `src/` layout.
- **Dependency Management**: Migrated to `pyproject.toml` and `uv`.
- **Code Quality**: Added `tests/` directory, configured `ruff`, and applied Google-style docstrings.

### Fixed
- **Empty ICRA Reports**: Resolved by bypassing JS viewers.
- **Missing Dependencies**: Added `beautifulsoup4`, `markdownify`, `requests`.
- **Duplicate Imports**: Cleaned up `FilingsDownloader.py` (now refactored).

---

## Initial Release

### Features
- Batch download NSE announcements by category
- Credit rating dual-source (screener.in primary, NSE fallback)
- Individual filing views (Resignations, Reg 30, Press Releases)
- Annual report download (date range or all)
- Streamlit UI with status feedback
