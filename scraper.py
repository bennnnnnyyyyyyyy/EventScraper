"""
scraper.py  --  Egypt Retail Summit 2026 prospect scraper
──────────────────────────────────────────────────────────
Usage:
    python scraper.py                              # write to CSV using Hunter
    python scraper.py --provider hunter            # write to CSV using Hunter.io
    python scraper.py --provider snov              # write to CSV using Snov.io
    python scraper.py --provider fake --dry-run    # 0-cost local test run
    python scraper.py --output sheets              # write to Google Sheet

Providers:
    hunter : Hunter.io domain-search API (default)
    prospeo: Prospeo.io search-person API
    snov   : Snov.io async domain-emails API
    apollo : Apollo.io mixed_people api_search
    fake   : Local mock data (0 credits)
"""

import argparse
import datetime
import sys
from config import SEED_COMPANIES, CREDIT_LIMIT, CSV_FILE

credits_used = 0


def get_provider_function(provider: str):
    if provider == "prospeo":
        import prospeo_client
        return prospeo_client.find_people
    elif provider == "hunter":
        import hunter_client
        return hunter_client.find_people
    elif provider == "snov":
        import snov_client
        return snov_client.find_people
    elif provider == "apollo":
        import apollo_client
        return apollo_client.find_people
    elif provider == "fake":
        import fake_client
        return fake_client.find_people
    else:
        raise ValueError(f"Unknown provider: {provider}")


def get_storage_module(output_format: str):
    if output_format == "csv":
        import csv_client
        return csv_client
    elif output_format == "sheets":
        import sheets_client
        return sheets_client
    else:
        raise ValueError(f"Unknown output format: {output_format}")


def check_credits() -> None:
    """Raise if we've hit the limit before making another call."""
    if credits_used >= CREDIT_LIMIT:
        print(f"\n[CREDIT LIMIT] Reached {CREDIT_LIMIT} credits. Stopping.")
        sys.exit(0)


def person_to_row(company: str, domain: str, person: dict, provider: str) -> list:
    source_label = f"Event Seed ({provider.capitalize()})"
    return [
        company,
        domain,
        source_label,
        person.get("name", ""),
        person.get("title", ""),
        person.get("email", ""),
        person.get("linkedin_url", ""),
        person.get("id", ""),
        datetime.date.today().isoformat(),
    ]


def dedup_keys(row: list) -> set[str]:
    """Return all non-empty identifiers for a row, lowercased and stripped."""
    return {
        v.strip().lower().rstrip("/")
        for v in (row[6], row[5], row[7])
        if len(row) > 7 and v and v.strip()
    }


def run(provider: str, output: str, dry_run: bool) -> None:
    global credits_used

    find_people = get_provider_function(provider)
    storage = get_storage_module(output)

    if dry_run:
        print(f"[DRY RUN] Provider: {provider.upper()}. Output: {output.upper()}. Nothing will be saved.\n")
        existing = set()
        handle = None
    else:
        handle = storage.open_and_prepare()
        existing = storage.get_existing_keys(handle)
        target_name = CSV_FILE if output == "csv" else "Google Sheet"
        print(f"Destination: {target_name} ({len(existing)} existing records found).")

    print(f"Active Provider: {provider.upper()}")
    if provider != "fake":
        print(f"Credit limit   : {CREDIT_LIMIT}\n")
    else:
        print("Mock mode      : No credits will be spent.\n")

    new_rows: list[list] = []

    for company, domain in SEED_COMPANIES.items():
        if provider != "fake":
            check_credits()
            print(f"-> {company} ({domain})  [credits used: {credits_used}/{CREDIT_LIMIT}]")
        else:
            print(f"-> {company} ({domain})  [MOCK]")

        try:
            people = find_people(domain)
            if provider != "fake":
                credits_used += 1          # one search call = one credit
        except Exception as e:
            print(f"  ERROR: {e}")
            if provider != "fake":
                credits_used += 1          # count failed call too
            continue

        if not people:
            print(f"  No results from {provider.capitalize()}.")
            continue

        added = 0
        for p in people:
            row = person_to_row(company, domain, p, provider)
            keys = dedup_keys(row)
            if keys & existing:
                continue
            existing |= keys
            new_rows.append(row)
            added += 1
            if dry_run:
                email_display = row[5] or "(no email)"
                print(f"  [{added}] {row[3]} | {row[4]} | {email_display} | {row[6]}")

        if not dry_run:
            print(f"  {added} new contacts queued.")

    print(f"\n{'-'*50}")
    if provider != "fake":
        print(f"Credits used : {credits_used}/{CREDIT_LIMIT}")
    print(f"New rows     : {len(new_rows)}")

    if dry_run or not new_rows:
        return

    dest_desc = CSV_FILE if output == "csv" else "Google Sheet"
    print(f"Saving to {dest_desc} ...")
    storage.append_rows(handle, new_rows)
    print(f"Done [OK] -> Saved {len(new_rows)} prospects to {dest_desc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Egypt Retail Summit 2026 prospect scraper")
    parser.add_argument("--provider", choices=["hunter", "prospeo", "snov", "apollo", "fake"],
                        default="hunter", help="Data provider to use (default: hunter)")
    parser.add_argument("--output", choices=["csv", "sheets"],
                        default="csv", help="Destination storage (default: csv)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print results without writing to storage")
    args = parser.parse_args()

    try:
        run(provider=args.provider, output=args.output, dry_run=args.dry_run)
    except KeyboardInterrupt:
        print(f"\nAborted. Credits used so far: {credits_used}")
        sys.exit(0)
