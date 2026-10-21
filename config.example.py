# ── config.py ────────────────────────────────────────────────────────────────
# Edit these values before running. Never commit this file with real keys.

CREDIT_LIMIT = 150  # hard stop — scraper exits when this many API calls are made

import os
# Credentials (environment variables override these defaults)
APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY", "")
HUNTER_API_KEY = os.environ.get("HUNTER_API_KEY", "YOUR_HUNTER_KEY_HERE")
SNOV_CLIENT_ID = os.environ.get("SNOV_CLIENT_ID", "YOUR_SNOV_CLIENT_ID_HERE")
SNOV_CLIENT_SECRET = os.environ.get("SNOV_CLIENT_SECRET", "YOUR_SNOV_SECRET_HERE")
PROSPEO_API_KEY = os.environ.get("PROSPEO_API_KEY", "YOUR_PROSPEO_KEY_HERE")

# Export Destination
CSV_FILE = "Egypt_Retail_Summit_2026_Prospects.csv"

# Google Sheets (optional)
SHEET_NAME = "Egypt Retail Summit 2026 - Prospects"
SERVICE_ACCOUNT_FILE = "service_account.json"

# Apollo people search filters
PERSON_TITLES = [
    "CEO", "Managing Director", "General Manager",
    "Chief Commercial Officer", "CCO",
    "Head of Retail", "Retail Director",
    "Procurement Manager", "Purchasing Manager",
    "Category Manager", "Buying Manager",
    "Supply Chain Director", "Commercial Director",
    "Marketing Director", "Business Development",
]
PERSON_LOCATIONS = ["Egypt"]   # Apollo location filter
PEOPLE_PER_DOMAIN = 5          # max contacts pulled per company (keeps credit spend low)

# Known companies from the event page (name → domain).
# Add more as you find them from Facebook/LinkedIn posts.
SEED_COMPANIES = {
    "Spinneys Egypt":        "spinneys-egypt.com",
    "Carrefour Egypt":       "carrefouregypt.com",
    "Metro Markets":         "metro-markets.com",
    "Lulu Hypermarket":      "luluhypermarket.com",
    "BIM Egypt":             "bim.com.tr",
    "Al Othaim":             "othaim.com.sa",
    "Panda Retail":          "pandamart.com.sa",
    "Oscar Grand Stores":    "oscarstores.com",
    "Exception Market":      "exceptionmarket.com",
    "Sarai Market":          "saraimarket.com",
    "Royal House":           "royalhouse-eg.com",
    "Al Mahlawi":            "almahlawi.com",
}
