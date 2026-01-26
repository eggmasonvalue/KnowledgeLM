---
name: knowledgelm-nse
description: >
  Batch download NSE India company filings (transcripts, investor presentations,
  credit ratings, annual reports) and optionally add them to NotebookLM.
  Use when user asks to download company announcements, filings, or investor
  documents from NSE India, or wants to create a research notebook with Indian
  stock materials.
---

# KnowledgeLM NSE

Batch download company filings from NSE India and integrate with NotebookLM.

## Prerequisites

1. Install the package:
   ```bash
   pip install knowledgelm
   ```

2. Verify installation:
   ```bash
   knowledgelm --help
   ```

## Command Discovery

**Always run `--help` to discover current options:**

```bash
knowledgelm --help                    # List all commands
knowledgelm download --help           # Download options
knowledgelm list-categories --help    # Category listing options
knowledgelm list-files --help         # File listing options
```

## Core Workflow

### 1. Determine Date Range

If user provides no date range, **ask for clarification**. Accept:
- Explicit dates: "from 2023-01-01 to 2025-01-26"
- Relative durations: "last 2 years", "past 5 years"
- Approximate: "few years" → interpret as ~3 years

Convert to YYYY-MM-DD format for the CLI.

### 2. Download Filings

```bash
knowledgelm download SYMBOL --from YYYY-MM-DD --to YYYY-MM-DD
```

**Options** (run `knowledgelm download --help` for current list):
- `--categories`: Comma-separated list or "all"
- `--output`: Custom output directory
- `--annual-reports-all`: Ignore date range for annual reports
- `--json`: Output as JSON for parsing

**Output**: Files saved to `./{SYMBOL}_knowledgeLM/` with category subfolders.

### 3. List Downloaded Files

```bash
knowledgelm list-files ./SYMBOL_knowledgeLM --json
```

Returns JSON with all file paths (excluding `.pkl` cookies).

## NotebookLM Integration

After downloading, optionally add files to NotebookLM:

### Check for notebooklm skill

If `notebooklm --help` fails, the skill is not installed. Guide user:
"The notebooklm-py package is required. Install with: `pip install notebooklm-py`"

### Create notebook and add sources

1. Get file list:
   ```bash
   knowledgelm list-files ./SYMBOL_knowledgeLM --json
   ```

2. Create notebook:
   ```bash
   notebooklm create "SYMBOL_knowledgeLM"
   ```

3. Add each file as source (loop through files from step 1):
   ```bash
   notebooklm source add "/path/to/file.pdf"
   ```

**Exclude**: Files with `.pkl` extension (cookie files).

## Error Handling

- **Invalid symbol**: CLI returns error JSON with `"success": false`
- **Network issues**: Retry once after 5 seconds
- **Selenium required**: Credit ratings may need Chrome; warn user if missing

## Categories

Run `knowledgelm list-categories` to see current list. Typical categories:
- `transcripts`: Earnings call transcripts
- `investor_presentations`: Investor day presentations
- `credit_rating`: Credit rating reports (requires Selenium)
- `annual_reports`: Annual reports
- `related_party_txns`: Related party transaction disclosures
- `press_releases`: Press releases
