import os
import json

import backend.llm_client as lc


def test_run_llm_mock_categorize(monkeypatch):
    # Ensure no API key is present so _build_client returns None and mock is used
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    system = "Categorize the email into Important/Newsletter/Spam/To-Do and return JSON {\"category\": \"...\"}."
    user = "Email subject: You won a prize!!!\nEmail body: Click here to claim your reward."

    out = lc.run_llm(system, user)
    # Should be JSON from the offline mock
    data = json.loads(out)
    assert "category" in data
    assert data["category"] == "Spam"


def test_run_llm_mock_reply(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    system = "Draft a reply in JSON with subject/body/suggested_followups"
    user = "Original email subject: Meeting request\nOriginal email body: Can you meet Monday?\nUser preferences: friendly and concise"

    out = lc.run_llm(system, user)
    data = json.loads(out)
    assert "subject" in data and "body" in data
    assert data["subject"].startswith("Re:")
