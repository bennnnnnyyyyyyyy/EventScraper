"""
hunter_client.py
Hunter.io Domain Search wrapper.
Free plan: 25 searches/month.  Each find_people() call = 1 search credit.
Docs: https://hunter.io/api-documentation/v2#domain-search
"""

import time
import requests
from config import HUNTER_API_KEY, PERSON_TITLES, PEOPLE_PER_DOMAIN

BASE = "https://api.hunter.io/v2"

# Hunter returns seniority/department but not exact titles.
# We match against PERSON_TITLES ourselves after fetching.
_TITLE_KEYWORDS = {t.lower() for t in PERSON_TITLES}


def _title_match(title: str) -> bool:
    """True if any PERSON_TITLES keyword appears in the contact's title."""
    if not title:
        return False
    t = title.lower()
    return any(kw in t for kw in _TITLE_KEYWORDS)


def find_people(domain: str) -> list[dict]:
    """
    Call Hunter Domain Search for `domain`.
    Returns a list of normalised person dicts with the same keys
    that apollo_client.find_people() returns:
        id, name, title, email, linkedin_url
    """
    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY,
        "limit": PEOPLE_PER_DOMAIN * 2,   # fetch more, then filter by title
        "type": "personal",               # only individual addresses
    }

    for attempt in range(3):
        try:
            r = requests.get(f"{BASE}/domain-search", params=params, timeout=30)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 10))
                print(f"  [hunter rate-limit] waiting {wait}s ...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            break
        except requests.RequestException as e:
            if attempt == 2:
                raise
            print(f"  [hunter retry {attempt + 1}] {e}")
            time.sleep(3)

    emails = r.json().get("data", {}).get("emails", [])

    people = []
    for e in emails:
        title = e.get("position", "")
        if not _title_match(title):
            continue

        first = e.get("first_name", "")
        last  = e.get("last_name", "")
        name  = f"{first} {last}".strip() or e.get("value", "")

        people.append({
            "id":           e.get("value", ""),   # use email as ID for dedup
            "name":         name,
            "title":        title,
            "email":        e.get("value", ""),
            "linkedin_url": e.get("linkedin", "") or "",
        })
        if len(people) >= PEOPLE_PER_DOMAIN:
            break

    return people
