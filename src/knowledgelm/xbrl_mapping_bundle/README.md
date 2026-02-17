# NSE XBRL Mapping Bundle

This directory contains the tools and data required to translate cryptic NSE XBRL keys (e.g., `Rec60EventTypeAcquistion`) into human-readable labels (e.g., `Acquisition`).

## Contents

- **`xbrl_labels.json`**: The generated JSON file containing key-value mappings. This is used by the application to parse XBRL filings.
- **`generate_mappings.js`**: A Node.js script that extracts these mappings from the source JavaScript files.
- **`Ann-xbrl.js`**: Source file from NSE website containing mapping logic.
- **`Ann-format.js`**: Source file from NSE website containing field definitions.

## How to Update

If NSE updates their mapping logic or if you encounter missing keys:

1.  **Download Latest JS Files**:
    - Download `https://www.nseindia.com/dist/js/components/corporate-filing/Ann-xbrl.js` and save it to this directory as `Ann-xbrl.js`.
    - Download `https://www.nseindia.com/dist/js/components/corporate-filing/announcementXBRL-format.js` and save it to this directory as `Ann-format.js`.

2.  **Run Extraction Script**:
    ```bash
    node generate_mappings.js
    ```
    This will regenerate `xbrl_labels.json` in the current directory.

3.  **Verify**:
    Check the end of `xbrl_labels.json` to see if new keys have been added.

## Strategy

The `generate_mappings.js` script uses a **Context-Aware Parsing** strategy to extract mappings directly from the rendering logic in `Ann-xbrl.js`:

1.  **Context Detection**: It scans `Ann-xbrl.js` line-by-line, identifying `containerId` blocks (e.g., `Rec30DetailsAmalagationMerge`) to understand the context of keys.
2.  **Direct Extraction**: Inside these blocks, it parser:
    - `addRowToTable` calls: Extracts direct key-label pairs used in table rows.
    - `tableColumnData` definitions: Extracts column headers defined in local variables.
3.  **Global Fallback**: It still parses global variables like `keyMapping` and `selectkeyMapping` from both `Ann-xbrl.js` and `Ann-format.js` to catch generic keys.
4.  **Suffix Stripping**: It automatically handles NSE's practice of suffixing keys (e.g., mapping `nameTrgtEntity_Rec...` to `nameTrgtEntity`) ensures robust matching against raw XBRL data.
5.  **Collision Detection**: The script actively checks for keys that are mapped to multiple different labels and logs warnings to the console (e.g., `[COLLISION] Key '...' has conflicting labels`). It prioritizes the first valid label found.
