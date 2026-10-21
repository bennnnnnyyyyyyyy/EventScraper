"""
snov_client.py
Snov.io Prospects by Domain wrapper using the official v2 async task workflow.
Returns prospects with job title, name, and LinkedIn URL.
"""

import time
import requests
from config import SNOV_CLIENT_ID, SNOV_CLIENT_SECRET, PEOPLE_PER_DOMAIN, PERSON_TITLES

BASE = "https://api.snov.io/v2"
_TITLE_KEYWORDS = {t.lower() for t in PERSON_TITLES}


def _get_access_token() -> str:
    r = requests.post(
        "https://api.snov.io/v1/oauth/access_token",
        json={
            "grant_type": "client_credentials",
            "client_id": SNOV_CLIENT_ID,
            "client_secret": SNOV_CLIENT_SECRET,
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def _title_match(title: str) -> bool:
    if not title:
        return False
    t = title.lower()
    return any(kw in t for kw in _TITLE_KEYWORDS)


def find_people(domain: str) -> list[dict]:
    """
    Search prospects by domain on Snov.io via v2 prospects/start -> poll result.
    Returns normalized dicts with: id, name, title, email, linkedin_url
    """
    token = _get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # 1. Start prospects task
    start_payload = {"domain": domain}
    start_resp = requests.post(
        f"{BASE}/domain-search/prospects/start",
        headers=headers,
        json=start_payload,
        timeout=30,
    )
    start_resp.raise_for_status()
    task_data = start_resp.json()
    task_hash = task_data.get("meta", {}).get("task_hash") or task_data.get("task_hash")

    if not task_hash:
        return []

    # 2. Poll for results (up to 15 seconds)
    result_data = None
    for _ in range(5):
        time.sleep(3)
        poll_resp = requests.get(
            f"{BASE}/domain-search/prospects/result/{task_hash}",
            headers=headers,
            timeout=30,
        )
        if poll_resp.status_code == 200:
            res_json = poll_resp.json()
            status = res_json.get("status", "").lower()
            if status in ("completed", "done", "success"):
                result_data = res_json
                break
            elif status in ("failed", "error"):
                break

    if not result_data:
        return []

    raw_prospects = result_data.get("data", [])
    people = []

    for c in raw_prospects:
        title = c.get("position", "") or ""
        if not _title_match(title):
            continue

        first = c.get("first_name", "") or ""
        last = c.get("last_name", "") or ""
        name = f"{first} {last}".strip()
        linkedin = c.get("source_page", "") or ""

        people.append({
            "id": linkedin or name,
            "name": name,
            "title": title,
            "email": "",
            "linkedin_url": linkedin,
        })
        if len(people) >= PEOPLE_PER_DOMAIN:
            break

    return people
