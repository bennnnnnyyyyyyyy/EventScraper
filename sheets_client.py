"""
sheets_client.py
Read / write to a Google Sheet via gspread + service account.
"""

import gspread
from config import SHEET_NAME, SERVICE_ACCOUNT_FILE
import config

HEADER = [
    "Company", "Domain", "Source",
    "Name", "Title", "Email", "LinkedIn URL",
    "Apollo ID", "Date Added",
]


def _open_sheet() -> gspread.Worksheet:
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    spreadsheet_id = getattr(config, "SPREADSHEET_ID", "")
    if spreadsheet_id:
        sh = gc.open_by_key(spreadsheet_id)
    else:
        try:
            sh = gc.open(SHEET_NAME)
        except Exception:
            sh = gc.open_by_key("1LNG9nhDE62LKBya4pD9NsUagJwcmK0_sxspS4LsY5iE")
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
        for val in (row[6], row[5], row[7]):  # linkedin, email, id
            v = val.strip().lower().rstrip("/")
            if v:
                keys.add(v)
    return keys


def append_rows(ws: gspread.Worksheet, rows: list[list]) -> None:
    if rows:
        ws.append_rows(rows, value_input_option="RAW")  # RAW prevents formula injection


def open_and_prepare() -> gspread.Worksheet:
    ws = _open_sheet()
    ensure_header(ws)
    return ws
