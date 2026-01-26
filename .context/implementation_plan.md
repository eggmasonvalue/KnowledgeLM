# Implementation Plan - Artifact Naming & Flattening

**Goal**: Flatten the output directory (no subfolders) and implement meaningful, temporal filenames for all downloaded artifacts.

## User Review Required
> [!IMPORTANT]
> **Breaking Change**: Files will no longer be sorted into subfolders (`transcripts/`, etc.). All files will be in the main artifact folder.
> **Breaking Change**: `NSEAdapter` will stop using the `nse` library for *downloading* and will use `requests` directly to support custom filenames.

## Proposed Naming Convention

**Format**: `{YYYY-MM-DD}_{Category}_{Symbol}_{Description}.{ext}`

- **YYYY-MM-DD**: Publication date (from announcement).
- **Category**: Short tag (e.g., `Transcript`, `Presentation`, `CreditRating`, `PressRelease`).
- **Symbol**: Ticker (e.g., `HDFCBANK`).
- **Description**: Sanitized snippet of the description (max 30 chars).

**Example**: `2024-01-26_Transcript_HDFCBANK_Q3_Earnings_Call.pdf`

## Component Changes

### 1. `src/knowledgelm/utils/file_utils.py`
- Add `generate_filename(date_str, category, symbol, description, extension) -> str`.
- Implement logic to sanitize description (remove spaces, special chars, truncate).

### 2. `src/knowledgelm/data/nse_adapter.py`
- **Refactor**: Remove reliance on `self.nse.download_document` (which lacks filename control).
- **New Method**: `download_file(url, output_path)`.
- Use `requests` with standard headers.

### 3. `src/knowledgelm/data/screener_adapter.py`
- Update `download_credit_ratings_from_screener` to accept a naming template or callback? 
- *Challenge*: Screener scraping might not easily provide a date for every link. 
- *Solution*: For Screener (all-time), we might lack exact dates. We will use `CreditRating_{Symbol}_{DocName}.pdf`. If we can parse date from link text, great; otherwise, skip date or use download date (not ideal). 
- *Refinement*: `service.py` calls this. We might need to handle renaming *after* download or pass a generator. Since Screener downloads multiple files, we'll let it handle naming internally but following the convention as best as possible.

### 4. `src/knowledgelm/core/service.py`
- Remove subfolder creation.
- Iterate through announcements:
    - Extract date from `item['an_dt']`.
    - Generate target filename using `file_utils`.
    - Call `nse_adapter.download_file(url, target_path)`.

### 5. `src/knowledgelm/app.py`
- Update "Download" buttons to use the new service method or direct download with new naming.

## Verification
- Run app, fetch `HDFCBANK`.
- Download Transcript.
- Verify file is in root artifact folder and named `202X-XX-XX_Transcript_HDFCBANK_....pdf`.
