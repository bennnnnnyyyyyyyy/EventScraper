# EventScraper

Multi-provider retail prospect scraper and pipeline for **Egypt Retail Summit 2026 (BD26-EVENT)**.

Connects to Hunter.io, Snov.io, Prospeo.io, and Apollo.io to extract retail executives, deduplicates them, and exports directly to local CSV and Google Sheets via Google Apps Script.

## Quick Start

1. Start Admin Board:
```powershell
python gui_server.py
```
Open [http://localhost:8080](http://localhost:8080) in your browser.

2. Run from CLI:
```powershell
python scraper.py --provider hunter
python scraper.py --provider snov
python scraper.py --provider prospeo
python scraper.py --provider apollo
```
