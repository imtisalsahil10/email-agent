import runpy
from pathlib import Path
import json

from backend import storage


def test_demo_ingest_writes_processed(tmp_path, monkeypatch):
    # Ensure we're executing in the repo root
    repo_root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(repo_root)

    out_path = repo_root / "data" / "processed_emails.json"
    if out_path.exists():
        out_path.unlink()

    # Run the demo_ingest script which should create processed_emails.json
    runpy.run_path("scripts/demo_ingest.py", run_name="__main__")

    assert out_path.exists(), "processed_emails.json should be created"

    with out_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    emails = storage.load_emails()
    # processed_emails.json should have same number of emails processed as inbox length
    assert isinstance(data, dict)
    assert len(data) == len(emails)
