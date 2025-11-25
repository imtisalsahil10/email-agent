import os
import json
import logging
from typing import Optional

# Prefer the official OpenAI SDK if available; import lazily to allow running without a key
try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional import
    OpenAI = None

log = logging.getLogger(__name__)


def _build_client() -> Optional[object]:
    """Create an OpenAI client from the OPENAI_API_KEY environment variable.

    If OPENAI_API_KEY is not set or the OpenAI SDK isn't available the function
    returns None and callers should fall back to the builtin mock responder.
    """
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        log.debug("OPENAI_API_KEY not found in environment; using mock LLM output")
        return None
    if OpenAI is None:
        log.warning("OpenAI SDK not installed even though OPENAI_API_KEY is set; continuing without network LLM")
        return None
    return OpenAI(api_key=key)


def _mock_response(system_prompt: str, user_prompt: str) -> str:
    """Return a deterministic fallback response for offline/demo mode.

    This simple mock tries to guess the expected JSON formats used by the app
    for categorization, action extraction and reply drafting.
    """
    # Combine prompts to make decisions
    combined = (system_prompt + "\n" + user_prompt).lower()

    # categorization -> look for keywords
    if "categorize" in system_prompt.lower() or "category" in combined:
        if "prize" in combined or "click here" in combined or "reward" in combined:
            return json.dumps({"category": "Spam"})
        if "newsletter" in combined or "top stories" in combined:
            return json.dumps({"category": "Newsletter"})
        if "final report" in combined or "prepare slides" in combined or "meeting" in combined:
            return json.dumps({"category": "To-Do"})
        return json.dumps({"category": "Important"})

    # action item extraction -> return a list of tasks
    if "extract" in system_prompt.lower() or "action" in combined:
        items = []
        if "final report" in combined:
            items.append({"task": "Write final report", "deadline": "2025-11-21"})
        if "prepare slides" in combined or "slides" in combined:
            items.append({"task": "Prepare slides for review meeting", "deadline": "2025-11-24"})
        if "claim your reward" in combined or "you won" in combined:
            items.append({"task": "Check spam link", "deadline": None})
        return json.dumps(items)

    # auto-reply -> return the JSON with subject/body/suggested_followups
    if "draft" in system_prompt.lower() or "draft" in combined or "reply" in combined:
        subj = "Re: " + (user_prompt.splitlines()[0].replace("Original email subject:", "").strip() or "")
        body = (
            "Thanks for reaching out. I can help with this — could you share a bit more detail or an agenda?"
        )
        suggested = ["Follow up in 3 days if no response", "Confirm meeting agenda"]
        return json.dumps({"subject": subj, "body": body, "suggested_followups": suggested})

    # fallback generic answer
    return "I'm an offline assistant (mock mode) — no LLM API key configured."


def run_llm(system_prompt: str, user_prompt: str) -> str:
    """Runs a chat completion with a system + user prompt.

    Behavior:
      - If OPENAI_API_KEY is set and openai.OpenAI is importable, uses the network client.
      - Otherwise, returns a safe offline mock response (useful for demos/tests).

    The function never raises due to missing configuration — it returns a helpful
    string that the caller can display or parse.
    """
    client = _build_client()
    if client is None:
        log.info("Using mock LLM response (no API key).")
        return _mock_response(system_prompt, user_prompt)

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
        )
        return response.choices[0].message.content
    except Exception as exc:  # pragma: no cover - network call
        log.exception("LLM call failed, falling back to mock response: %s", exc)
        return _mock_response(system_prompt, user_prompt)
