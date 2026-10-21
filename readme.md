# EventScraper — BD26-EVENT

Multi-provider B2B prospecting pipeline for the **Egypt Retail Summit 2026**.

Scrapes retail decision-makers (CEO, Procurement, Category, Supply Chain) from 12 seed companies across Hunter.io, Snov.io, Prospeo.io, and Apollo.io. Deduplicates and exports to local CSV or Google Sheets.

---

## Quick Start

### 1. Clone & install
```powershell
git clone https://github.com/bennnnnnyyyyyyyy/EventScraper.git
cd EventScraper
pip install requests
```

### 2. Configure your API keys
```powershell
cp config.example.py config.py
# Open config.py and fill in your keys
```

### 3. Launch the Admin Board (GUI)
```powershell
python gui_server.py
```
Open **http://localhost:8080** — manage keys, run providers, view captured prospects.

### 4. Or run via CLI
```powershell
python scraper.py --provider hunter    # Hunter.io
python scraper.py --provider snov      # Snov.io (best free-tier yield for MENA)
python scraper.py --provider prospeo   # Prospeo.io
python scraper.py --provider apollo    # Apollo.io (best MENA coverage overall)
python scraper.py --provider fake      # 0-cost mock run
python scraper.py --provider snov --dry-run   # Preview without saving
```

---

## Provider Yield (Live Run — Oct 2026)

| Provider | Free Credits Used | New Contacts | Notes |
|---|---|---|---|
| Hunter.io | 12 | 0 | Egyptian domains not indexed |
| Prospeo.io | 12 | 0 | MENA retail not in index |
| Snov.io | 12 | **17** | ✅ Spinneys, Carrefour, Metro, Lulu, BIM |
| Apollo.io | TBD | TBD | Best MENA + title filter |

---

## Project Structure

| File | Purpose |
|---|---|
| `config.py` | API keys, seed companies, credit limit *(gitignored)* |
| `config.example.py` | Safe template to share with collaborators |
| `scraper.py` | CLI orchestrator |
| `csv_client.py` | Local CSV export with deduplication |
| `sheets_client.py` | Google Sheets integration |
| `gui_server.py` | Admin Board HTTP server |
| `admin.html` | Admin Board UI |
| `hunter_client.py` | Hunter.io adapter |
| `snov_client.py` | Snov.io async adapter |
| `prospeo_client.py` | Prospeo.io adapter |
| `apollo_client.py` | Apollo.io adapter |
| `appscript/` | Google Apps Script webhook & manifest |

---

## Security

- `config.py` is in `.gitignore` — never committed
- All JSON credential files are gitignored
- Credit limit hard-capped at `150` in `config.py`


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
