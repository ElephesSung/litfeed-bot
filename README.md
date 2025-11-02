
# LitFeed Bot

A simple, reliable bot to fetch the **latest articles** from multiple scholarly sources (Crossref, PubMed, arXiv, bioRxiv/medRxiv, RSS feeds), generate **structured summaries** with **Google Gemini**, and post **digest cards to Mattermost**. Runs on a schedule via **GitHub Actions**, **cron**, or **Airflow**.

> No scraping of Google Scholar. Only official/public APIs and RSS feeds.

---

## Features

- **Sources**: Crossref (by ISSN or keyword), PubMed (keywords), arXiv (keywords), bioRxiv/medRxiv (date-window API), plus journal **RSS** feeds.
- **Smart de-duplication**: DOI > arXiv ID > title+journal hash.
- **Structured summaries**: One-liner TL;DR, Methods, Findings, Limitations, Audience — as JSON then rendered to Markdown.
- **Robustness**: Backoff/retries, per-source errors don’t break the run.
- **Simple persistence**: SQLite to avoid reposting the same items.
- **Flexible scheduling**: GitHub Actions, cron, or Airflow (DAG provided).
- **One-file config**: `config.yaml` controls sources, lookback window, language, and Mattermost channel.

---

## Quick Start (Local)

1) **Clone and set up**

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# open .env and add your GOOGLE_API_KEY and MM_WEBHOOK_URL
```

2) **Configure** `config.yaml`  
   - Add your journals (ISSNs & RSS), keywords, and toggles for sources.
   - Defaults will already work with demo settings.

3) **Run once**

```bash
python main.py --dry-run   # prints the cards instead of posting
python main.py             # posts to Mattermost via the webhook
```

> On first run, a `litfeed.sqlite` database is created to remember posted items.

---

## GitHub Actions (scheduled)

1) Commit this repo to GitHub.
2) Add **Actions secrets** in your repository settings:
   - `GOOGLE_API_KEY` – your Gemini API key
   - `MM_WEBHOOK_URL` – the Mattermost incoming webhook URL
3) The workflow in `.github/workflows/schedule.yml` runs every day at 08:00 UTC by default. Adjust as needed.

---

## Airflow (optional)

A DAG is provided at `deploy/airflow/dag_litfeed.py`. Set `REPO` to your path and ensure your virtual environment is available on the worker(s).

---

## Configuration

**`config.yaml`**

- `lookback_days`: how many days back to search each run.
- `max_per_source`: per-source cap for performance/sanity.
- `language`: summary language, defaults to English (`"en"`).
- `sources`: enable/disable: `crossref`, `pubmed`, `arxiv`, `biorxiv`, `rss`.
- `journals`: list of `name`, `issn`, and `rss` (all optional).
- `keywords`: simple OR query list, used by Crossref/PubMed/arXiv.
- `mattermost.webhook_url`: you can place `${MM_WEBHOOK_URL}` to read from environment instead of hardcoding.

---

## How it works

1. Fetch recent items per enabled source within `lookback_days`.
2. Normalise metadata and compute a stable unique ID.
3. Skip items that are already in SQLite (`litfeed.sqlite`).
4. Call **Gemini** to obtain **JSON** summaries with consistent fields.
5. Render Markdown cards & post to Mattermost in manageable batches.

---

## Notes & Limits

- **Crossref & PubMed rate limits** exist. We use short timeouts and retry with backoff.
- **bioRxiv/medRxiv**: uses their public API by date window.
- **arXiv**: public ATOM feed (via API). Avoid excessive polling.
- If the LLM call fails, we still post **fallback cards** with links and basic metadata.

---

## Troubleshooting

- Nothing posted? Try `--dry-run` first and inspect console output.
- Check `.env` is loaded and `GOOGLE_API_KEY` / `MM_WEBHOOK_URL` are set.
- Increase `lookback_days` if you expect more items.
- For journals without ISSNs in Crossref, use RSS as a reliable alternative.

---

## License

MIT — see `LICENSE`.
