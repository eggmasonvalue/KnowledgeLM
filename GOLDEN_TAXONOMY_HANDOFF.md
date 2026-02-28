# Golden Taxonomy Engineering - Handoff Document

Welcome! You are picking up the development of **KnowledgeLM**, a CLI/Streamlit app used for batch downloading and parsing Indian company filings from the NSE (National Stock Exchange). 

We are currently on the branch `feature/golden-taxonomy`. Your exact mission is to design and implement the **Golden Taxonomy** pipeline to solve critical stability issues in our XBRL parser.

---

## 🏗️ Background: How the Parser Currently Works
We use the python `arelle` library to parse XBRL instances (XML files) published by companies on the NSE for events like Board Meetings, Personnel Changes, etc.
To parse an XBRL file into human-readable JSON, Arelle must resolve the schema (`.xsd`) and linkbase files (`-lab.xml`, `-pre.xml`) defined in the filing's `schemaRef`.

**Current Workflow:**
1. A filing is downloaded.
2. We identify its category (e.g., Shareholder Meetings) and download the specific Taxonomy ZIP from the NSE website on-the-fly and cache it in `.taxonomies/`.
3. We also download a "Master" taxonomy (Ind AS).
4. **The Global Mixer Hack:** In `xbrl_harvester.py`, we recursively copy the entire `.taxonomies` cache into a temporary directory so that Arelle has access to a "global pool" of schemas when trying to resolve dependencies.

## 🚨 The Core Problem
The current "on-demand" taxonomy resolution system is fundamentally fragile and cannot survive in a production environment:

1. **Version Drift:** An older filing from 2023 might require `in-capmkt-ent-2023-01-31.xsd`. However, the Taxonomy ZIP currently hosted on the NSE website only contains the `2024` versions. If the user hasn't magically cached the 2023 ZIP previously, Arelle will fail with a `Missing XSD` error, forcing us to fallback to unparsed, raw data keys.
2. **Cross-Category Imports:** A "Shareholder Meeting" taxonomy might rely on an underlying schema that was only bundled in the "Board Outcomes" taxonomy ZIP.
3. **Link Rot:** NSE frequently changes the URLs of these taxonomy ZIP files, breaking our hardcoded mappings in `taxonomy_manager.py`.
4. **Runtime Inefficiency:** Doing massive recursive OS-level `copytree` operations inside a temporary directory for *every single filing* is computationally expensive and slow.

---

## 🎯 The Goal: The "Golden Taxonomy" Strategy
Instead of incrementally and precariously caching ZIPs at runtime, we need to shift to a **Golden Taxonomy Archive** strategy.

We need a unified, comprehensive archive containing **all historically released NSE XBRL taxonomies** merged into a single, perfectly structured directory tree that Arelle can seamlessly transverse.

### What You Need to Build

1. **The Taxonomy Spider / Builder Script**
   - Create an offline pipeline or script (e.g., in `scripts/build_golden_taxonomy.py`) designed to spider, download, and extract all known NSE taxonomies.
   - It needs to fetch all historical versions (possibly parsing the NSE archives or utilizing an exhaustive URL list).
   - It must merge the unzipped taxonomies into a single Root Directory. It should merge them cleanly so that different version folders (like `.../2023-01-31/` and `.../2024-05-31/`) coexist happily, and core dependencies are deduplicated gracefully.

2. **Refactoring the Runtime Harvester**
   - Once the Golden Taxonomy is available (either bundled, or fetched as one large reliable release ZIP via `taxonomy_manager.py`), you must update `src/knowledgelm/core/xbrl_harvester.py`.
   - Remove the expensive temporary directory `copytree` logic.
   - Point the `arelle` controller directly to the Golden Taxonomy environment so it natively resolves any `schemaRef`.

3. **Validation**
   - Verify that both legacy (2020-2023) and modern (2024+) filings can successfully resolve their XSDs and labels against this single golden archive without hitting missing schema exceptions.

---

## 📍 Where We Are Stopping
- Current Branch: `feature/golden-taxonomy`
- Recent Commits: We just implemented the "Global Taxonomy Mixer" fallback in `xbrl_harvester.py` to stop the bleeding, and cleaned up the `NSEAdapter` to use robust ZIP extraction.
- Our Streamlit app and CLI commands (e.g., `knowledgelm download SWIGGY --categories personnel shm --from 2024-01-01 --to 2026-02-28`) work and show when the parser gracefully falls back.

**Your First Move:** Read this document, review `taxonomy_manager.py` (which currently houses the fragile static URL list), and begin designing the Golden Taxonomy builder system. Good luck!
