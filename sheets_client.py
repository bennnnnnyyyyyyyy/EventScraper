"""
sheets_client.py
Read / write to a Google Sheet via gspread + service account.
"""

import gspread
from config import SHEET_NAME, SERVICE_ACCOUNT_FILE

HEADER = [
    "Company", "Domain", "Source",
    "Name", "Title", "Email", "LinkedIn URL",
    "Apollo ID", "Date Added",
]


def _open_sheet() -> gspread.Worksheet:
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open(SHEET_NAME)
    return sh.sheet1


def ensure_header(ws: gspread.Worksheet) -> None:
    """Write header row if sheet is empty."""
    if ws.row_count == 0 or ws.cell(1, 1).value != HEADER[0]:
        ws.insert_row(HEADER, index=1)


def get_existing_keys(ws: gspread.Worksheet) -> set[str]:
    """
    Return a set of dedup keys already in the sheet.
    Key = linkedin_url if present, else email, else apollo_id.
    """
    rows = ws.get_all_values()[1:]  # skip header
    keys = set()
    for row in rows:
        if len(row) < 8:
            continue
        linkedin = row[6].strip()
        email    = row[5].strip()
        apollo   = row[7].strip()
        key = linkedin or email or apollo
        if key:                          # never add empty string — avoids false dedup
            keys.add(key)
    return keys


def append_rows(ws: gspread.Worksheet, rows: list[list]) -> None:
    if rows:
        ws.append_rows(rows, value_input_option="USER_ENTERED")


def open_and_prepare() -> gspread.Worksheet:
    ws = _open_sheet()
    ensure_header(ws)
    return ws
