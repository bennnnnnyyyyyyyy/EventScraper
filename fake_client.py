"""
fake_client.py
Zero-credit test provider.  Returns hardcoded people for every domain so
you can verify the full pipeline (dedup, sheet writes, dry-run) without
spending any API credits or signing up for anything.

Usage:
    python scraper.py --provider fake --dry-run
"""

import datetime

_FAKE_PEOPLE = [
    {
        "id":           "fake-001",
        "name":         "Amira Hassan",
        "title":        "Head of Retail",
        "email":        "amira.hassan@example.com",
        "linkedin_url": "https://linkedin.com/in/amira-hassan-fake",
    },
    {
        "id":           "fake-002",
        "name":         "Khaled Mansour",
        "title":        "Procurement Manager",
        "email":        "khaled.mansour@example.com",
        "linkedin_url": "https://linkedin.com/in/khaled-mansour-fake",
    },
    {
        "id":           "fake-003",
        "name":         "Sara Fouad",
        "title":        "Category Manager",
        "email":        "sara.fouad@example.com",
        "linkedin_url": "",   # intentionally blank to test blank-key dedup
    },
]


def find_people(domain: str) -> list[dict]:
    """Returns the same 3 fake contacts for every domain."""
    # Suffix email with domain so rows stay unique across companies
    result = []
    for i, p in enumerate(_FAKE_PEOPLE):
        result.append({
            **p,
            "id":    f"fake-{domain}-{i:03d}",
            "email": f"test{i}@{domain}",
        })
    return result
