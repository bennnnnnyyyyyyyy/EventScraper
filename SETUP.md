# Egypt Retail Summit 2026 – Prospect Pipeline

## Multi-Provider Support & Test Setup

All providers share the exact same `find_people(domain)` interface and output schema. You can switch or test any provider with a single CLI flag.

| Provider | Flag | Free Tier / Trial | API Details |
|---|---|---|---|
| **Fake Mock** | `--provider fake` | Unlimited (0 cost) | No API key required; tests pipeline and deduplication logic instantly |
| **Apollo.io** | `--provider apollo` | Free plan available | `POST /v1/mixed_people/search` (default) |
| **Hunter.io** | `--provider hunter` | 25 searches/mo | `GET /v2/domain-search` with client-side title filter |
| **Snov.io** | `--provider snov` | 50 credits/mo | Official v2 async task: `POST /v2/domain-search/domain-emails/start` + polling |
| **Prospeo.io** | `--provider prospeo` | 75-100 credits/mo | `POST /search-person` with `X-KEY` auth header |

---

## Quick Test Run Commands

### 1. Instant 0-Credit Simulation (No setup required)
```powershell
& "C:\Users\ben.arthur\AppData\Local\Programs\Python\Python313\python.exe" scraper.py --provider fake --dry-run
```

### 2. Apollo.io Test
```powershell
$env:APOLLO_API_KEY = "your_apollo_key"
& "C:\Users\ben.arthur\AppData\Local\Programs\Python\Python313\python.exe" scraper.py --provider apollo --dry-run
```

### 3. Hunter.io Test
```powershell
$env:HUNTER_API_KEY = "your_hunter_key"
& "C:\Users\ben.arthur\AppData\Local\Programs\Python\Python313\python.exe" scraper.py --provider hunter --dry-run
```

### 4. Snov.io Test
```powershell
$env:SNOV_CLIENT_ID = "your_client_id"
$env:SNOV_CLIENT_SECRET = "your_client_secret"
& "C:\Users\ben.arthur\AppData\Local\Programs\Python\Python313\python.exe" scraper.py --provider snov --dry-run
```

### 5. Prospeo.io Test
```powershell
$env:PROSPEO_API_KEY = "your_prospeo_key"
& "C:\Users\ben.arthur\AppData\Local\Programs\Python\Python313\python.exe" scraper.py --provider prospeo --dry-run
```

---

## Live Run (Writes to Google Sheet)

Remove the `--dry-run` flag once you're satisfied with the dry run output:

```powershell
& "C:\Users\ben.arthur\AppData\Local\Programs\Python\Python313\python.exe" scraper.py --provider [apollo|hunter|snov|prospeo]
```
