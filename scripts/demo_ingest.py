r"""Small helper to run the ingestion pipeline locally and save processed output.

Run this from the repo root inside the repo venv:

  .\.venv\Scripts\python.exe scripts\demo_ingest.py

It will load `data/mock_inbox.json`, run categorization and action extraction
using the current prompts and the LLM client (or the mock fallback), and write
`data/processed_emails.json` so the UI can pick it up.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path when this script is run directly from scripts/
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.storage import load_emails, load_prompts, save_processed
from backend.agent import categorize_email, extract_action_items
import json


def main():
    emails = load_emails()
    prompts = load_prompts()
    processed = {}
    for e in emails:
        category = categorize_email(e, prompts)
        actions = extract_action_items(e, prompts)
        processed[e.id] = {
            "email_id": e.id,
            "category": category,
            "action_items": actions,
            "summary": None,
        }

    out_path = Path("data") / "processed_emails.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2)

    print(f"Processed {len(processed)} emails and wrote {out_path}")


if __name__ == "__main__":
    main()
