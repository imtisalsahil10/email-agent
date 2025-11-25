import json
import streamlit as st

from backend.storage import (
    load_emails, load_prompts, save_prompts,
    load_processed, save_processed,
    load_drafts, add_draft
)
from backend.agent import (
    categorize_email, extract_action_items,
    chat_about_email, draft_reply
)
from backend.models import Prompts, ProcessedEmail

st.set_page_config(page_title="Email Productivity Agent", layout="wide")

st.title("📧 Prompt-Driven Email Productivity Agent")

# Visible debug banner (timezone-aware) to help identify which source file is running in Streamlit
try:
    from datetime import datetime, timezone
    st.markdown(f"**DEBUG:** running `app.py` — modified at {datetime.now(timezone.utc).isoformat()} (UTC)")
except Exception:
    st.markdown("**DEBUG:** running `app.py`")

# Small landing dashboard / hero area so the app doesn't look empty when you open it:
with st.container():
    st.markdown("---")
    left, right = st.columns([2, 1])
    with left:
        st.header("Email Agent — Inbox at a glance")
        st.write("Use the Prompt Brain in the sidebar to edit and experiment with prompts. Click `Ingest / Re-process Inbox` to apply the prompts to all messages.")
        st.write("Features: categorization, action-item extraction, draft generation, and an email agent chat. Drafts are always saved and never sent.")
    with right:
        # a small stats card
        st.subheader("Quick stats")
        try:
            total = len(load_emails())
            processed_count = len(load_processed())
            drafts_count = len(load_drafts())
        except Exception:
            total, processed_count, drafts_count = 0, 0, 0

        st.metric("Inbox total", total)
        st.metric("Processed", processed_count)
        st.metric("Drafts", drafts_count)
    st.markdown("---")

# Sidebar: Prompt Brain
st.sidebar.header("🧠 Prompt Brain")
prompts = load_prompts()

cat_prompt = st.sidebar.text_area("Categorization Prompt", prompts.categorization_prompt, height=150)
action_prompt = st.sidebar.text_area("Action Item Prompt", prompts.action_item_prompt, height=150)
auto_prompt = st.sidebar.text_area("Auto-Reply Draft Prompt", prompts.auto_reply_prompt, height=150)

if st.sidebar.button("Save Prompts"):
    new_prompts = Prompts(
        categorization_prompt=cat_prompt,
        action_item_prompt=action_prompt,
        auto_reply_prompt=auto_prompt
    )
    save_prompts(new_prompts)
    st.sidebar.success("Prompts saved!")

# Main layout
col_inbox, col_detail = st.columns([1, 2])

emails = load_emails()
processed = load_processed()
prompts = load_prompts()  # reload after save

with col_inbox:
    st.subheader("📥 Inbox")

    # Search/filter and selection helpers
    query = st.text_input("Search subjects or senders", value="")

    # build display labels for selection
    display_items = [f"{e.id} — {e.subject} ({e.sender})" for e in emails]
    filtered = [e for e in emails if query.lower() in e.subject.lower() or query.lower() in e.sender.lower()]

    all_ids = [e.id for e in filtered]
    selected_ids = st.multiselect("Select one or more emails (multi-select)", all_ids, default=[all_ids[0]] if all_ids else [])

    col_btns = st.columns([1, 1])
    with col_btns[0]:
        if st.button("Process Selected"):
            if not selected_ids:
                st.warning("Select at least one email to process.")
            else:
                progress = st.progress(0)
                new_processed = processed.copy()
                for i, eid in enumerate(selected_ids, start=1):
                    e = next(x for x in emails if x.id == eid)
                    category = categorize_email(e, prompts)
                    actions = extract_action_items(e, prompts)
                    new_processed[e.id] = ProcessedEmail(
                        email_id=e.id,
                        category=category,
                        action_items=actions,
                        summary=None
                    )
                    progress.progress(int(i / len(selected_ids) * 100))
                save_processed(new_processed)
                processed = new_processed
                st.success(f"Processed {len(selected_ids)} email(s)")

    with col_btns[1]:
        if st.button("Ingest / Re-process Inbox"):
            new_processed = processed.copy()
            progress = st.progress(0)
            for i, e in enumerate(emails, start=1):
                category = categorize_email(e, prompts)
                actions = extract_action_items(e, prompts)
                new_processed[e.id] = ProcessedEmail(
                    email_id=e.id,
                    category=category,
                    action_items=actions,
                    summary=None
                )
                progress.progress(int(i / len(emails) * 100))
            save_processed(new_processed)
            processed = new_processed
            st.success("Inbox processed using current prompts!")

    # Show a compact visual list
    st.markdown("### Email List")
    # We'll map id->email for quick lookup
    id_to_email = {e.id: e for e in emails}

    # Use a radio if single-selection preferred; default to the first selected_id or first email
    default_single = selected_ids[0] if selected_ids else (emails[0].id if emails else None)
    selected_id = st.radio("Choose an email to view details", options=[e.id for e in emails], index=[e.id for e in emails].index(default_single) if default_single else 0) if emails else None
    selected_email = id_to_email[selected_id] if selected_id else None

    for e in emails:
        cat = processed.get(e.id).category if e.id in processed else "Not processed"
        st.write(f"**[{cat}]** {e.subject}")
        st.caption(f"{e.sender} • {e.timestamp}")

with col_detail:
    st.subheader("📄 Email Details & Agent")

    if selected_email:
        st.markdown(f"**From:** {selected_email.sender}")
        st.markdown(f"**Subject:** {selected_email.subject}")
        st.markdown(f"**Time:** {selected_email.timestamp}")
        st.markdown("---")
        st.text_area("Body", selected_email.body, height=200)

        # Threaded view (emails with the same subject or same sender are shown as a thread)
        st.markdown("---")
        st.markdown("### 📎 Thread / Related messages")
        thread = [x for x in emails if (x.subject == selected_email.subject or x.sender == selected_email.sender)]
        # Sort thread by timestamp if possible
        try:
            thread = sorted(thread, key=lambda x: x.timestamp)
        except Exception:
            pass
        for t in thread:
            st.markdown(f"**{t.sender}** — {t.timestamp}")
            st.write(t.body)
            st.markdown("---")

        # Allow single-email processing from detail view
        if st.button("Process this email"):
            with st.spinner("Processing email..."):
                category = categorize_email(selected_email, prompts)
                actions = extract_action_items(selected_email, prompts)
                processed[selected_email.id] = ProcessedEmail(
                    email_id=selected_email.id,
                    category=category,
                    action_items=actions,
                    summary=None
                )
                save_processed(processed)
            st.success("Email processed!")
    else:
        st.write("No email selected")

    if selected_id in processed:
        st.markdown("**Category:** " + processed[selected_id].category)
        st.markdown("**Action Items:**")
        st.json(processed[selected_id].action_items)

    st.markdown("### 💬 Email Agent Chat")
    user_query = st.text_input("Ask the agent about this email (e.g., 'Summarize this email')")
    if st.button("Ask"):
        answer = chat_about_email(selected_email, prompts, user_query)
        st.markdown("**Agent Response:**")
        st.write(answer)

    st.markdown("### ✍️ Draft Reply")
    extra_instruction = st.text_input("Optional: Describe your tone (e.g., 'friendly and concise')")
    if st.button("Generate Reply Draft"):
        raw = draft_reply(selected_email, prompts, extra_instruction)
        try:
            data = json.loads(raw)
            draft = add_draft(
                related_email_id=selected_email.id,
                subject=data.get("subject", f"Re: {selected_email.subject}"),
                body=data.get("body", ""),
                metadata={
                    "suggested_followups": data.get("suggested_followups", []),
                    "category": processed[selected_id].category if selected_id in processed else None,
                    "action_items": processed[selected_id].action_items if selected_id in processed else []
                }
            )
            st.success("Draft generated and saved (not sent).")
            st.text_input("Draft Subject", value=draft.subject)
            st.text_area("Draft Body", value=draft.body, height=200)
            st.markdown("**Suggested follow-ups:**")
            st.json(draft.metadata.get("suggested_followups", []))
        except Exception:
            st.error("Failed to parse draft reply JSON. Check LLM output.")
            st.code(raw)
