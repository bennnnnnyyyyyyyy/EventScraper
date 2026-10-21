# Agent Instructions — BD26-EVENT (EventScraper)

This repository contains the prospecting and enrichment pipeline for **Egypt Retail Summit 2026 (`BD26-EVENT`)**. It extracts key retail decision-makers (procurement, buying, category, supply chain, commercial executives) across public event seed companies, enriches them through multi-provider APIs (Hunter.io, Snov.io, Prospeo.io, Apollo.io), and synchronizes them directly into a local CSV and Google Sheets via Google Apps Script.

---

## 1. Multi-Agent & Team Collaboration

- **Collaborators**: Ben, Antigravity, Claude, Codex.
- **Shared Standards**:
  - Always keep code modular and provider-agnostic. All providers must implement `find_people(domain) -> list[dict]`.
  - Maintain synchronization between local configurations, `config.py`, and the Apps Script webhook.
  - Never commit real API keys or sensitive customer credentials to public repositories.

---

## 2. Architecture & File Boundaries

| Component | Path | Responsibility |
|---|---|---|
| **Central Config** | [`config.py`](file:///c:/Users/ben.arthur/Desktop/EventScraper/config.py) | API keys, seed company registry, credit limits, target titles |
| **Main Orchestrator** | [`scraper.py`](file:///c:/Users/ben.arthur/Desktop/EventScraper/scraper.py) | CLI orchestrator supporting `--provider` and `--output` |
| **CSV Storage** | [`csv_client.py`](file:///c:/Users/ben.arthur/Desktop/EventScraper/csv_client.py) | Append-only CSV storage with deduplication |
| **Sheets Storage** | [`sheets_client.py`](file:///c:/Users/ben.arthur/Desktop/EventScraper/sheets_client.py) | Google Sheets integration (Service Account or Webhook) |
| **Apps Script Code** | [`appscript/Code.js`](file:///c:/Users/ben.arthur/Desktop/EventScraper/appscript/Code.js) | Server-side Google Sheets deduplication & webhook handler |
| **Apps Script Config** | [`appscript/appsscript.json`](file:///c:/Users/ben.arthur/Desktop/EventScraper/appscript/appsscript.json) | Web app execution and deployment manifest |
| **Admin GUI** | [`admin.html`](file:///c:/Users/ben.arthur/Desktop/EventScraper/admin.html) / [`gui_server.py`](file:///c:/Users/ben.arthur/Desktop/EventScraper/gui_server.py) | Interactive GUI Admin Board for API keys, settings, and runs |

---

## 3. Safety & Implementation Rules

- **Surgical Changes**: State assumptions before coding; touch only files strictly relevant to the request.
- **Credit Guards**: Respect `CREDIT_LIMIT = 200` and conservative batches (`PEOPLE_PER_DOMAIN = 5`) to prevent runaway API spend.
- **Strict Deduplication**: Deduplicate on `LinkedIn URL -> Email -> Contact ID`. Never add empty strings to dedup sets to prevent false collision drops.
- **No Automated Browser Testing**: Never activate automatic browser test subagents without explicit request. Always provide the URL and ask the user to verify manually.

---

## 4. Google Sheets & Clasp Execution Rules

- **Connected Sheet**: [BD26-EVENT Sheet](https://docs.google.com/spreadsheets/d/1LNG9nhDE62LKBya4pD9NsUagJwcmK0_sxspS4LsY5iE/edit)
- **Web App URL**: `https://script.google.com/macros/s/AKfycbyWi3FM_2OKlCoZDlVuBKO-OHzIWF8Xl2d0Q7srCkUN_2C2_OsyZ1zMHJv-DTpWsT6O/exec`
- **Clasp Commands**: You must use absolute paths to Node and Clasp:
  ```powershell
  & "C:\Users\ben.arthur\node-v24.14.1-win-x64\node.exe" `
    "C:\Users\ben.arthur\node-v24.14.1-win-x64\node_modules\@google\clasp\build\src\index.js" `
    [command] [args]
  ```
- **Clasp Login**: Always include `--no-localhost`:
  ```powershell
  & "C:\Users\ben.arthur\node-v24.14.1-win-x64\node.exe" `
    "C:\Users\ben.arthur\node-v24.14.1-win-x64\node_modules\@google\clasp\build\src\index.js" `
    login --no-localhost
  ```

---

## 5. Environment & Execution Constraints

- **Shell**: Use PowerShell ONLY. `cmd` and `cmd /c` are not supported.
- **Python Path**: `C:\Users\ben.arthur\AppData\Local\Programs\Python\Python313\python.exe`
- **Privileges**: No Admin/Sudo access available.
