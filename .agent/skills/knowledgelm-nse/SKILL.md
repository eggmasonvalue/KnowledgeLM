---
name: knowledgelm-nse
description: >
  Batch download Indian company filings (transcripts, investor presentations,
  credit ratings, annual reports) from NSE and optionally add to NotebookLM.
  Use when user asks to: (1) Download investor materials for Indian publicly 
  listed companies, (2) Research Indian stocks/companies, (3) Create research 
  notebooks with company filings, or (4) Analyze NSE-listed company documents.
---

# KnowledgeLM NSE

Batch download Indian company filings from NSE and optionally integrate with NotebookLM.

## Installation

Check if installed: `knowledgelm --version`

If not: `uv tool install knowledgelm`

To upgrade: `uv tool upgrade knowledgelm`

## Skill Upgrade

To upgrade this skill to the latest version:

1. Download the latest skill from GitHub:
   ```
   https://raw.githubusercontent.com/eggmasonvalue/KnowledgeLM/main/.agent/skills/knowledgelm-nse/SKILL.md
   ```

2. Replace the existing `SKILL.md` in your skills directory with the downloaded version.

**Note:** The skill file location in your skills directory depends on your AI agent vendor.

## Command Discovery

**Use `--help` extensively to discover current options and flags.**

```bash
knowledgelm --help
knowledgelm download --help
knowledgelm list-files --help
```

## Core Workflow

### 1. Gather Required Information

**NSE Symbol:** If not provided, use `web_search` to find it.

**Date Range:** If not provided, ask for clarification. Accept various formats:
- Explicit: `"2023-01-01 to 2025-01-26"`, `"2023 to 2025"`, `"from 2023"`
- Relative: `"last 2 years"`
- Milestones: `"Since IPO"`, `"since <event>"` (use `web_search` to resolve dates)

Convert to `YYYY-MM-DD` for CLI.

**Categories:** Default to all categories if not specified. Use `--annual-reports-all` by default.

### 2. Download Filings

Use `knowledgelm download` with appropriate flags. Files save to `./{SYMBOL}_knowledgeLM/`.

### 3. List Files (if needed)

Use `knowledgelm list-files` with `--json` flag to get file paths (excludes `.pkl` cookies).

## NotebookLM Integration

If user wants to create a NotebookLM notebook:

### 1. Ensure Latest Package Version

Check if installed and upgrade to latest:

```bash
notebooklm --version
```

If not installed:
```bash
uv tool install notebooklm-py
```

If installed, upgrade to latest:
```bash
uv tool upgrade notebooklm-py
```

**Browser extras (for first-time setup):** If user hasn't authenticated with NotebookLM before, they need browser login support:

```bash
uv tool install --reinstall "notebooklm-py[browser]"
playwright install chromium
```

### 2. Update Skill to Latest Version

**Always run** `notebooklm skill install` to ensure skill is current:

```bash
notebooklm skill install
```

This installs/updates to the default directory (typically `~/.claude/skills/notebooklm/`).

**Important:** Do NOT delete this directory - it's used for version tracking.

### 3. Copy to Your Skills Directory (if different)

If your AI agent uses a different skills directory, copy the installed skill there. The install directory path is shown in the `skill install` output.

### 4. Create Notebook

Use the notebooklm skill to create notebook and add downloaded files as sources (exclude `.pkl` files).

**Optional - Audio Overview Generation:**

For generating audio overviews focused on fundamental analysis, use the prompt template at `references/notebooklm_audio_prompt.md` as a system prompt. This provides structured guidance for creating investor-focused audio summaries.

## Exception Handling

- **Invalid symbol:** CLI returns `"success": false` in JSON
- **Network issues:** Retry once after 5 seconds
- **Incomplete data:** May indicate newly listed company on the NSE mainboard or corporate action. Use `web_search` to verify.
