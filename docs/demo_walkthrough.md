# Demo Walkthrough & Recording Checklist — Prompt-Driven Email Productivity Agent

Purpose: a concise script and checklist you can follow to record the required 5–10 minute demo. The demo shows ingestion, prompt editing, categorization/action extraction, agent chat, and draft creation — all powered by the stored prompts.

Recording guidance
- Aim for 5–10 minutes. Record with your screen at 1080p if possible and capture clear audio narration.
- If you don't have an LLM API key or prefer reproducible outputs, the project falls back to the built-in mock LLM responses (no key required).
- Keep each step short and demonstrate the outcomes (UI + files persisted). Use the `scripts/demo_ingest.py` helper and `data/processed_emails.json` to show results.

Structure & timing (approx.)
1) Intro (20–30s)
   - Say your name and the project name (Prompt-Driven Email Productivity Agent).
   - One sentence objective: demonstrate ingestion, prompt-driven processing, chat, and draft generation.

2) Setup & Run (45–60s)
   - Show the repo tree briefly (open README or files). Mention the mock inbox and prompt templates.
   - Run the UI with the helper (PowerShell example):
     ```powershell
     # (If not already) create & activate venv then install deps
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     pip install -r requirements.txt

     # Start the app (or use run.ps1 helper)
     .\run.ps1
     ```
   - Point the audience to the Local URL printed by Streamlit and open it. Confirm the debug banner (timestamp) is visible to show it's the local app.

3) Loading and showing the Mock Inbox (60–90s)
   - Open the Prompt Brain (sidebar) and show the default prompts in `data/prompts.json` are loaded.
   - Click `Ingest / Re-process Inbox` **or** use the ingestion helper in a terminal to process all messages and save `data/processed_emails.json`.
     ```powershell
     .\.venv\Scripts\python.exe scripts\demo_ingest.py
     ```
   - Show the progress bar in the UI while processing runs. Demonstrate that each email gets a category and action-items JSON.
   - Open `data/processed_emails.json` in editor to show stored results (metadata, categories, action items).

4) Prompt-driven behavior / Editing Prompts (60–90s)
   - Edit the Categorization Prompt in the sidebar to change behavior (eg. add a new rule to classify invoices as "Important").
   - Re-run the `Ingest / Re-process Inbox` (or Process Selected) and show how the categories change based on the updated prompt.
   - Highlight that the system uses the stored prompt template to shape model output.

5) Email Agent chat (45–60s)
   - Select a processed email and use the "Ask" box to ask: "Summarize this email" or "What tasks do I need to do?"
   - Show the returned agent response (from LLM or mock). Demonstrate how the prompts are combined with the email to produce reply content.

6) Draft reply generation & safety (60–90s)
   - Select another email and click "Generate Reply Draft" with a tone instruction (e.g., "friendly and concise").
   - Show the saved draft in the UI (subject, body) and confirm the draft is persisted to `data/drafts.json` but NOT sent.
   - Optional: open `data/drafts.json` to show the draft and the metadata stored (action items and suggested follow-ups).

7) Final wrap-up (10–15s)
   - Recap what you demonstrated: ingestion, prompt editing, prompt-driven categorization/action extraction, chat, drafting, and persistence.
   - Mention where to find the code (`backend/agent.py`, `backend/llm_client.py`, `data/` folder) and how to run tests:
     ```powershell
     .\.venv\Scripts\python.exe -m pytest -q
     ```

Optional extra scenes (if you have extra time)
- Show how to use the multi-select and "Process Selected" for batch processing. Demonstrate progress indication.
- Show the threaded view (related messages) and explain how the agent uses thread context when drafting replies.

Demo checklist (pass/fail, quick capture)
- [ ] Launches locally & shows debug banner
- [ ] Demonstrates loading or running ingestion helper
- [ ] Shows categories and action items saved in `data/processed_emails.json`
- [ ] Edits a prompt and demonstrates changed behavior after reprocessing
- [ ] Uses the Email Agent chat (asks a question) and shows a relevant response
- [ ] Generates a draft and confirms it's saved in `data/drafts.json` (not sent)
- [ ] Shows multi-select batch processing + progress UI (optional but recommended)
- [ ] Notes safe mock behavior when `OPENAI_API_KEY` is not set (no real API key exposed)

Tips for a clean recording
- Keep each step short and demonstrate the exact UI element being used.
- Narrate what you're doing at each step and why (e.g., "Now I will change the categorization prompt so invoices are 'Important'").
- If the demo produces noisy or long-running network calls, use the offline mock or re-run `scripts/demo_ingest.py` to create deterministic output for recording.

Done — follow the script above for the 5–10 minute video. If you want, I can also generate a short textual voiceover script that you can read while recording.
