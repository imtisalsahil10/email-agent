"""Storage helpers for the application.

This file provides JSON-backed storage helpers the app expects. The functions
are intentionally minimal – they read and write small JSON files under the
``data/`` directory so the repository remains simple to run without a db.
"""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import uuid

from .models import Email, ProcessedEmail, Prompts, Draft

DATA_DIR = Path("data")

def load_emails() -> List[Email]:
    with open(DATA_DIR / "mock_inbox.json", "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Email(**e) for e in raw]

def load_prompts() -> Prompts:
    path = DATA_DIR / "prompts.json"
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # Support two schema shapes:
    # 1) Simple dict with top-level keys (legacy): { categorization_prompt, action_item_prompt, auto_reply_prompt }
    # 2) Structured schema with templates array (newer): { templates: [ {id/type/template}, ... ] }
    if isinstance(raw, dict) and "templates" in raw and isinstance(raw["templates"], list):
        # Map template types to expected prompt fields
        mapping = {
            "categorization": None,
            "action_item": None,
            "reply": None,
            "chat": None,
        }
        for t in raw["templates"]:
            ttype = t.get("type")
            if ttype == "categorization":
                mapping["categorization"] = t.get("template")
            elif ttype in ("action_item", "action_item_extraction"):
                mapping["action_item"] = t.get("template")
            elif ttype in ("reply", "auto_reply", "auto_reply_draft"):
                mapping["reply"] = t.get("template")

        return Prompts(
            categorization_prompt=mapping.get("categorization") or "",
            action_item_prompt=mapping.get("action_item") or "",
            auto_reply_prompt=mapping.get("reply") or "",
        )

    # fallback to previous simple schema
    return Prompts(**raw)

def save_prompts(prompts: Prompts):
    with open(DATA_DIR / "prompts.json", "w", encoding="utf-8") as f:
        json.dump(prompts.__dict__, f, indent=2)

def load_processed() -> Dict[str, ProcessedEmail]:
    path = DATA_DIR / "processed_emails.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {k: ProcessedEmail(**v) for k, v in raw.items()}

def save_processed(data: Dict[str, ProcessedEmail]):
    serializable = {k: v.__dict__ for k, v in data.items()}
    with open(DATA_DIR / "processed_emails.json", "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)

def load_drafts() -> List[Draft]:
    path = DATA_DIR / "drafts.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Draft(**d) for d in raw]

def save_drafts(drafts: List[Draft]):
    with open(DATA_DIR / "drafts.json", "w", encoding="utf-8") as f:
        json.dump([d.__dict__ for d in drafts], f, indent=2)

def add_draft(related_email_id, subject, body, metadata):
    drafts = load_drafts()
    new_draft = Draft(
        id=str(uuid.uuid4()),
        related_email_id=related_email_id,
        subject=subject,
        body=body,
        metadata=metadata,
        created_at=datetime.utcnow().isoformat()
    )
    drafts.append(new_draft)
    save_drafts(drafts)
    return new_draft
