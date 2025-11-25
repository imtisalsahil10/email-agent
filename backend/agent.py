import json
from typing import List, Dict, Any
from .llm_client import run_llm
from .models import Email, Prompts

def categorize_email(email: Email, prompts: Prompts) -> str:
    system_prompt = prompts.categorization_prompt
    user_prompt = f"Email subject: {email.subject}\nEmail body:\n{email.body}\n"
    raw = run_llm(system_prompt, user_prompt)
    try:
        data = json.loads(raw)
        return data.get("category", "Uncategorized")
    except Exception:
        return "Uncategorized"

def extract_action_items(email: Email, prompts: Prompts) -> List[Dict[str, Any]]:
    system_prompt = prompts.action_item_prompt
    user_prompt = f"Email subject: {email.subject}\nEmail body:\n{email.body}\n"
    raw = run_llm(system_prompt, user_prompt)
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []

def chat_about_email(email: Email, prompts: Prompts, user_query: str) -> str:
    system_prompt = (
        "You are an email productivity assistant. "
        "Use the user's prompt brain instructions when relevant.\n\n"
        f"Categorization instructions:\n{prompts.categorization_prompt}\n\n"
        f"Action item instructions:\n{prompts.action_item_prompt}\n\n"
        f"Auto-reply instructions:\n{prompts.auto_reply_prompt}\n"
    )
    user_prompt = (
        f"EMAIL CONTENT:\nSubject: {email.subject}\nBody:\n{email.body}\n\n"
        f"USER QUESTION:\n{user_query}"
    )
    return run_llm(system_prompt, user_prompt)

def draft_reply(email: Email, prompts: Prompts, extra_instruction: str = "") -> str:
    system_prompt = prompts.auto_reply_prompt
    user_prompt = (
        f"Original email subject: {email.subject}\n"
        f"Original email body:\n{email.body}\n\n"
        f"User preferences: {extra_instruction}\n\n"
        "Draft a reply email with a subject and body. "
        "Respond in JSON: {\"subject\": \"...\", \"body\": \"...\", \"suggested_followups\": [\"...\"]}."
    )
    return run_llm(system_prompt, user_prompt)
