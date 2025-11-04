# Devotional Agent - Telex A2A Compatible

This monolithic FastAPI app exposes a single A2A endpoint `/a2a` (JSON-RPC style) that Telex can call to run devotional workflows.

## Features
- Pick a random verse from a local SQLite Bible (`bible.db`).
- Use OpenAI to generate a structured devotional (title, scripture_ref, scripture_text, reflection, application, prayer).
- Archive generated devotionals into `devotionals.db`.
- Single `/a2a` endpoint that supports methods:
  - `pick_verse` — optional params: `{ "topic": "faith" }`
  - `generate_devotional` — params: `{ "reference": "John 3:16", "text": "For God so loved..." }`
  - `run_devotional_workflow` — params: `{ "topic": "faith", "tone": "encouraging", "archive": true }`

## Quickstart
1. Copy your `bible.db` into `./data/bible.db`. The app expects a `verses` table with columns `(id, book, chapter, verse, text)`.
2. Create `.env` from `.env.sample` and set:
   - `OPENAI_API_KEY`
   - `A2A_API_KEY` (Telex should send this value in `X-API-KEY` header)
   - `BIBLE_DB` and `ARCHIVE_DB` if you want custom paths
3. Install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
4. Run:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Example A2A Request (Telex)
POST `/a2a` with header `X-API-KEY: <A2A_API_KEY>`
Body (JSON-RPC):
```json
{
  "jsonrpc": "2.0",
  "id": "dev-001",
  "method": "run_devotional_workflow",
  "params": {"topic": "faith", "tone": "encouraging", "archive": true}
}
```

Expected response:
```json
{
  "jsonrpc": "2.0",
  "id": "dev-001",
  "result": {
    "title": "...",
    "scripture_ref": "...",
    "scripture_text": "...",
    "reflection": "...",
    "application": "...",
    "prayer": "...",
    "_archived_id": 1
  }
}
```