"""
apollo_client.py
Thin wrapper around the Apollo.io v1 API.
"""

import time
import requests
from config import APOLLO_API_KEY, PERSON_TITLES, PERSON_LOCATIONS, PEOPLE_PER_DOMAIN

BASE = "https://api.apollo.io/api/v1"
HEADERS = {
    "x-api-key": APOLLO_API_KEY,
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
}


def _post(endpoint: str, payload: dict, retries: int = 3) -> dict:
    url = f"{BASE}/{endpoint}"
    for attempt in range(retries):
        try:
            r = requests.post(url, headers=HEADERS, json=payload, timeout=30)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 10))
                print(f"  [rate-limit] waiting {wait}s ...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise
            print(f"  [retry {attempt + 1}] {e}")
            time.sleep(3)
    return {}


def find_people(domain: str) -> list[dict]:
    """
    Search Apollo for people at `domain` matching our title + location filters.
    Returns normalized dicts compatible with person_to_row.
    """
    payload = {
        "q_organization_domains": [domain],   # array, bare domain only (no https://)
        "person_titles": PERSON_TITLES,
        "person_locations": PERSON_LOCATIONS,
        "per_page": PEOPLE_PER_DOMAIN,
        "page": 1,
    }
    data = _post("mixed_people/api_search", payload)
    return [
        {
            "id": p.get("id", ""),
            "name": p.get("name") or f'{p.get("first_name", "")} {p.get("last_name", "")}'.strip(),
            "title": p.get("title", ""),
            "email": p.get("email") or "",
            "linkedin_url": p.get("linkedin_url") or "",
        }
        for p in data.get("people", [])
    ]
