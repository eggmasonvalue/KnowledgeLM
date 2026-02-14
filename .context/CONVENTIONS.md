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
- **Exceptions for Failures**: Failures must be communicated via standard Python exceptions.
- **CLI Exit Codes**: CLI commands must return appropriate non-zero exit codes on failure to enable programmatic detection.
- **No Silent Crashes**: Catch specific exceptions (`requests.RequestException`, `ValueError`) but always propagate or log them for the agent to see in logs.
- **Fail gracefully in UI**: Show error messages in the Streamlit UI but don't crash the server.

### Logging & Output
- **Strict No-Print Policy**: Do not use `print()` or `sys.stdout.write()`. All diagnostic info must go to `knowledgelm.log`.
- **Zero Terminal Noise**: Standard production runs should remain silent on `stdout`/`stderr` to preserve LLM context window space.
- **Third-Party Noise**: Use `log_utils.redirect_stdout_to_logger` or devnull redirects for libraries (Selenium, nse) that print to terminal.
- **Structured Results**: Use JSON output via the CLI when requested for easy agent parsing.

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
