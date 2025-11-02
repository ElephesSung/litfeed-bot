
import feedparser
from typing import List, Dict, Any
from dateutil import parser as dtparser
from datetime import datetime, timezone, timedelta

def _within(date_str: str, days: int) -> bool:
    try:
        dt = dtparser.parse(date_str)
        return (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)) <= timedelta(days=days)
    except Exception:
        return True

def fetch(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not config.get("sources", {}).get("rss", False):
        return []

    results = []
    lookback_days = config.get("lookback_days", 3)
    for j in config.get("journals", []):
        rss = j.get("rss")
        if not rss:
            continue
        try:
            feed = feedparser.parse(rss)
            for e in feed.entries[: config.get("max_per_source", 20)]:
                title = e.title
                url = e.link
                date_str = getattr(e, "published", "") or getattr(e, "updated", "")
                if not _within(date_str, lookback_days):
                    continue
                results.append({
                    "uid_hint": "rss:"+url,
                    "title": title,
                    "journal": j.get("name",""),
                    "published": date_str,
                    "doi": None,
                    "url": url,
                    "source": "rss",
                    "raw": {"summary": getattr(e,"summary","")}
                })
        except Exception as e:
            print("RSS error:", e)
    return results
