from backend import storage


def test_load_emails_returns_list():
    emails = storage.load_emails()
    assert isinstance(emails, list)
    assert len(emails) >= 3  # we've seeded 15 sample messages in repo
    assert hasattr(emails[0], "id")


def test_load_prompts_parsing():
    prompts = storage.load_prompts()
    # Prompts dataclass should have attributes
    assert hasattr(prompts, "categorization_prompt")
    assert hasattr(prompts, "action_item_prompt")
    assert hasattr(prompts, "auto_reply_prompt")
