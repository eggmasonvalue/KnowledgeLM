# Architecture

## Module Structure

```mermaid
graph TD
    subgraph Entry["Entry Points"]
        CLI[src/knowledgelm/cli.py<br/>Click CLI]
        APP[src/knowledgelm/app.py<br/>Streamlit UI]
    end
    
    subgraph Logic["Core Logic"]
        SRV[src/knowledgelm/core/service.py]
    end
    
    subgraph Data["Data Layer"]
        NSE_ADPT[src/knowledgelm/data/nse_adapter.py]
        SCR_ADPT[src/knowledgelm/data/screener_adapter.py]
    end
    
    subgraph Agent["Agent Resources"]
        SKILL[.agent/skills/knowledgelm-nse/SKILL.md<br/>Agent Skill]
    end
    
    subgraph Utils["Utilities"]
        CONF[src/knowledgelm/config.py]
        F_UTIL[src/knowledgelm/utils/file_utils.py]
    end
    
    subgraph External["External Sources"]
        NSE_LIB[NSE API<br/>nse library]
        SCR_WEB[screener.in<br/>Credit Ratings]
        NLMPY[notebooklm-py<br/>Optional Integration]
    end
    
    CLI --> SRV
    APP --> SRV
    SRV --> NSE_ADPT
    SRV --> SCR_ADPT
    SRV --> F_UTIL
    NSE_ADPT --> NSE_LIB
    SCR_ADPT --> SCR_WEB
    CLI .-> SKILL
    SKILL .-> NLMPY
    APP ..-> CONF
    SRV ..-> CONF
```

## Project Structure

```
KnowledgeLM/
├── src/
│   └── knowledgelm/
│       ├── __init__.py
│       ├── cli.py                # Click CLI (v3.0)
│       ├── app.py                # Streamlit UI
│       ├── config.py             # Configuration
│       ├── core/
│       │   └── service.py        # Orchestration Logic
│       ├── data/
│       │   ├── nse_adapter.py    # NSE Library Wrapper
│       │   └── screener_adapter.py # Screener Scraper
│       └── utils/
│           └── file_utils.py     # Sanitization & paths
├── tests/
│   └── test_placeholder.py
├── .agent/
│   └── skills/
│       └── knowledgelm-nse/
│           └── SKILL.md          # Agent Skill (v3.0)
├── .context/
├── pyproject.toml                # uv config
└── README.md
```

## Component Responsibilities

### cli.py
- **CLI**: Click-based command interface (`download`, `list-categories`, `list-files`)
- **JSON Output**: `--json` flag for agent parsing
- **Help Discovery**: `--help` on all commands for agent self-discovery

### app.py
- **UI**: Streamlit forms for symbol, dates, category selection.
- **Display**: Renders status and download tables.
- **Validations**: Calls `KnowledgeService`.

### core/service.py
- **`KnowledgeService`**: Orchestrates fetching and downloading.
- **Filters**: Applies business logic (category filters) on fetched data.

### data/
- **`nse_adapter.py`**: Wraps the external `nse` library.
  - **Validation**: Checks symbol validity via `equityQuote`.
- **`screener_adapter.py`**: Handles scraping from Screener.in.
  - Resolves ICRA PDF links directly.
  - Uses Selenium for high-fidelity HTML-to-PDF conversion.

### .agent/skills/knowledgelm-nse/
- **`SKILL.md`**: Agent skill following [Agent Skills](https://agentskills.io) standard.
  - Instructs AI agents on CLI usage and NotebookLM integration.
  - Self-upgradeable via GitHub raw URL.

### utils/file_utils.py
- **`sanitize_folder_name`**: Prevents path traversal security issues.

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as app.py
    participant S as Service
    participant N as NSEAdapter
    participant SC as ScreenerAdapter

    U->>A: Enter symbol, dates, folder name
    A->>S: process_request()
    S->>S: sanitize_folder_name()
    
    S->>N: validate_symbol()
    alt Invalid Symbol
        N-->>S: False
        S--x A: Raise ValueError
    end

    S->>N: get_announcements()
    N-->>S: JSON data
    
    par Download Categories
        loop Each Category
             S->>N: download_document()
        end
        alt Credit Ratings
             S->>SC: download_credit_ratings()
             SC-->>S: Count
        end
    end
    
    S-->>A: data, counts
    A-->>U: Show status + updated tables
```

## Output Structure

```
{folder_name}/
├── transcripts/
├── investor_presentations/
├── credit_rating/
├── related_party_txns/
├── annual_reports/
├── resignations/      (Optional: Logical grouping in UI, physical folder relies on user download)
├── updates/           (Optional: Logical grouping in UI)
└── press_releases/    (Optional: Logical grouping in UI)
```
