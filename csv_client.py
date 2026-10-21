"""
csv_client.py
Local CSV storage with automatic header initialization and deduplication.
"""

import os
import csv
from config import CSV_FILE

HEADER = [
    "Company", "Domain", "Source",
    "Name", "Title", "Email", "LinkedIn URL",
    "Apollo ID", "Date Added",
]


def open_and_prepare() -> str:
    """Ensure CSV file exists and has headers."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)
    return CSV_FILE


def get_existing_keys(filepath: str = CSV_FILE) -> set[str]:
    """Extract unique dedup keys from existing CSV records."""
    if not os.path.exists(filepath):
        return set()

    keys = set()
    with open(filepath, mode="r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        try:
            next(reader)  # skip header
        except StopIteration:
            return keys

        for row in reader:
            if len(row) < 8:
                continue
            linkedin = row[6].strip()
            email = row[5].strip()
            apollo = row[7].strip()
            key = linkedin or email or apollo
            if key:
                keys.add(key)
    return keys


def append_rows(filepath: str, rows: list[list]) -> None:
    """Append new prospect rows to CSV."""
    if not rows:
        return
    with open(filepath, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
