# Code Conventions

## Project Structure

```
KnowledgeLM/
├── src/
│   └── knowledgelm/
│       ├── app.py
│       ├── config.py
│       ├── core/
│       ├── data/
│       └── utils/
├── .context/
└── pyproject.toml
```

## Naming

| Element | Pattern | Example |
|---------|---------|---------|
| Constants | `UPPER_SNAKE_CASE` | `CREDIT_RATING_FOLDER` |
| Functions | `snake_case` | `download_announcements()` |
| Download folders | `snake_case` | `investor_presentations/` |

## Patterns

### Category Configuration
Categories defined declaratively in `DOWNLOAD_CATEGORIES` dict:
```python
"transcripts": {
    "enabled_arg": "download_transcripts",
    "filter": lambda item: ...,
    "label": "transcript"
}
```

### Streamlit Session State
All persistent data stored in `st.session_state`:
```python
if "data" not in st.session_state:
    st.session_state.data = None
```

### Error Handling
- Use `logging` module (not `print()`)
- Catch specific exceptions (`requests.RequestException`, `ValueError`)
- Fail gracefully in UI (show error message but don't crash)

### Logging & Output
- **No `print()`**: All output must go through `logger`.
- **Third-Party Noise**: Use `log_utils.redirect_stdout_to_logger` for libraries that print to stdout (e.g., `nse`).
- **Silence Warnings**: Explicitly suppress expected non-critical warnings (e.g., `InsecureRequestWarning` for specific legacy sites).

## UI Components

## Scraping & Automation

- **Browser Automation**: Use Selenium (headless Chrome) when:
  - Content is dynamically rendered via JS (e.g., PDF viewers).
  - High-fidelity artifact generation (PDF) is required from HTML.
- **Direct Downloads**: Prefer `requests` for static files (PDFs, CSVs) for efficiency.
- **Resilience**: Always verify file integrity (size, content type) after download.


- `st.columns()` for layout
- `st.expander()` for collapsible sections
- `st.spinner()` for loading feedback
- Checkboxes for category toggles

## Testing

> [!CAUTION]
> No automated tests exist. Manual testing via Streamlit UI.
