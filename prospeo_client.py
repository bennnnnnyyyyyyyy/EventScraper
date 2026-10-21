"""
prospeo_client.py
Prospeo.io Person Search wrapper.
Docs: https://prospeo.io/api-docs
Endpoint: POST https://api.prospeo.io/search-person
"""

import time
import requests
from config import PROSPEO_API_KEY, PERSON_TITLES, PEOPLE_PER_DOMAIN

BASE = "https://api.prospeo.io"
_TITLE_KEYWORDS = {t.lower() for t in PERSON_TITLES}


def _title_match(title: str) -> bool:
    if not title:
        return False
    t = title.lower()
    return any(kw in t for kw in _TITLE_KEYWORDS)


def find_people(domain: str) -> list[dict]:
    """
    Search people by company domain using Prospeo's Search Person API.
    Returns normalized dicts with: id, name, title, email, linkedin_url
    """
    headers = {
        "X-KEY": PROSPEO_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "filters": {
            "person_search": {
                "company_domain": domain,
            }
        },
        "page": 1,
    }

    for attempt in range(3):
        try:
            r = requests.post(f"{BASE}/search-person", headers=headers, json=payload, timeout=30)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 10))
                print(f"  [prospeo rate-limit] waiting {wait}s ...")
                time.sleep(wait)
                continue
            if r.status_code == 400:
                # Prospeo returns 400 with {"error": true, "error_code": "NO_RESULTS"} when no contacts match
                return []
            r.raise_for_status()
            data = r.json()
            break
        except requests.RequestException as e:
            if attempt == 2:
                raise
            print(f"  [prospeo retry {attempt + 1}] {e}")
            time.sleep(3)

    raw_people = data.get("response", {}).get("people", []) or data.get("people", []) or []
    people = []

    for p in raw_people:
        title = p.get("job_title", "") or p.get("title", "")
        if not _title_match(title):
            continue

        name = p.get("full_name") or f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
        email = p.get("email", "") or ""
        linkedin = p.get("linkedin_url", "") or p.get("linkedin", "") or ""
        pid = p.get("id") or email or linkedin

        people.append({
            "id": pid,
            "name": name,
            "title": title,
            "email": email,
            "linkedin_url": linkedin,
        })
        if len(people) >= PEOPLE_PER_DOMAIN:
            break

    return people
