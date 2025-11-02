
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any

API = "https://api.biorxiv.org/details/{venue}/{start}/{end}"  # venue: biorxiv|medrxiv

def fetch(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not config.get("sources", {}).get("biorxiv", False):
        return []

    lookback_days = config.get("lookback_days", 3)
    end = datetime.utcnow().date()
    start = end - timedelta(days=lookback_days)
    results: List[Dict[str, Any]] = []

    for venue in ("biorxiv","medrxiv"):
        try:
            url = API.format(venue=venue, start=start.isoformat(), end=end.isoformat())
            r = requests.get(url, timeout=25)
            r.raise_for_status()
            data = r.json()
            for item in data.get("collection", []):
                # Expected keys: title, doi, date, link, etc.
                title = item.get("title") or "(no title)"
                doi = item.get("doi")
                date_str = item.get("date")
                link = "https://doi.org/" + doi if doi else item.get("biorxiv_url") or item.get("link")
                results.append({
                    "uid_hint": doi or (title + venue + (date_str or "")),
                    "title": title,
                    "journal": venue,
                    "published": date_str,
                    "doi": doi,
                    "url": link,
                    "source": venue,
                    "raw": item
                })
        except Exception as e:
            print("bioRxiv/medRxiv error:", e)

    return results
