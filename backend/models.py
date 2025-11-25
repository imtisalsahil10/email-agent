from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class Email:
    id: str
    sender: str
    subject: str
    body: str
    timestamp: str  # ISO string


@dataclass
class ProcessedEmail:
    email_id: str
    category: str
    action_items: List[Dict[str, Any]]
    summary: Optional[str] = None


@dataclass
class Prompts:
    categorization_prompt: str
    action_item_prompt: str
    auto_reply_prompt: str


@dataclass
class Draft:
    id: str
    related_email_id: Optional[str]
    subject: str
    body: str
    metadata: Dict[str, Any]
    created_at: str
