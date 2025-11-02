
import os, sys, argparse, yaml
from typing import Dict, List
from importlib import import_module

from store.db import init_db, make_uid, seen, persist
from summarizers.gemini import GeminiSummariser
from utils.text import render_cards
from sinks.mattermost import post_cards

SOURCES = [
    "sources.crossref",
    "sources.pubmed",
    "sources.arxiv",
    "sources.biorxiv",
    "sources.rss",
]

def load_config(path: str="config.yaml") -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def env_sub_inplace(cfg: Dict):
    # basic ${VAR} env substitution
    if isinstance(cfg, dict):
        for k,v in list(cfg.items()):
            if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
                envk = v[2:-1]
                cfg[k] = os.getenv(envk, "")
            else:
                env_sub_inplace(v)
    elif isinstance(cfg, list):
        for i in range(len(cfg)):
            env_sub_inplace(cfg[i])

def collect(config: Dict, max_per_source: int=None) -> List[Dict]:
    items: List[Dict] = []
    for path in SOURCES:
        try:
            src = import_module(path)
            fetched = src.fetch(config) or []
            if max_per_source:
                fetched = fetched[:max_per_source]
            items.extend(fetched)
        except Exception as e:
            print(f"[WARN] Source {path} failed:", e)
    return items

def dedupe_and_store(raw_items: List[Dict]) -> List[Dict]:
    new_items: List[Dict] = []
    init_db()
    for it in raw_items:
        uid = make_uid(it)
        it["id"] = uid
        if seen(uid):
            continue
        persist(uid, it)
        new_items.append(it)
    return new_items

def main():
    p = argparse.ArgumentParser(description="Fetch, summarise, and post literature digests.")
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--dry-run", action="store_true", help="Print cards instead of posting.")
    p.add_argument("--limit", type=int, default=None, help="Cap items per source (override config).")
    args = p.parse_args()

    config = load_config(args.config)
    env_sub_inplace(config)

    raw_items = collect(config, max_per_source=args.limit or config.get("max_per_source", 20))
    new_items = dedupe_and_store(raw_items)

    if not new_items:
        print("No new items to summarise/post.")
        return 0

    summariser = GeminiSummariser(config)
    enriched = summariser.summarise(new_items)
    cards = render_cards(enriched)

    if args.dry_run:
        print("\n\n--- DRY RUN OUTPUT ---\n\n")
        for c in cards:
            print(c)
            print("\n---\n")
        return 0

    post_cards(config, cards)
    print(f"Posted {len(cards)} card(s) to Mattermost.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
