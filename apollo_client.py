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
    Returns a list of raw person dicts.
    """
    payload = {
        "q_organization_domains_list": [domain],
        "person_titles": PERSON_TITLES,
        "person_locations": PERSON_LOCATIONS,
        "per_page": PEOPLE_PER_DOMAIN,
        "page": 1,
    }
    data = _post("mixed_people/search", payload)
    return data.get("people", [])


def enrich_email(person_id: str) -> str | None:
    """
    Run an email enrichment call for a single Apollo person ID.
    Costs 1 export credit per call — only use when you need the email.
    Returns email string or None.
    """
    data = _post("people/match", {"id": person_id, "reveal_personal_emails": False})
    person = data.get("person", {})
    return person.get("email") or None
