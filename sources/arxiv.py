
import requests, feedparser
from typing import List, Dict, Any

def fetch(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not config.get("sources", {}).get("arxiv", False):
        return []
    if not config.get("keywords"):
        return []

    base = "http://export.arxiv.org/api/query"
    query = " OR ".join([f'all:"{kw}"' for kw in config["keywords"]])
    max_rows = config.get("max_per_source", 20)

    results = []
    try:
        r = requests.get(base, params={"search_query": query, "sortBy":"submittedDate",
                                       "sortOrder":"descending","max_results":max_rows}, timeout=20)
        feed = feedparser.parse(r.text)
        for e in feed.entries:
            title = e.title
            url = e.link
            date_str = e.published
            results.append({
                "uid_hint": "arxiv:"+e.id,
                "title": title,
                "journal": "arXiv",
                "published": date_str,
                "doi": None,
                "url": url,
                "source": "arxiv",
                "raw": {"id": e.id}
            })
    except Exception as e:
        print("arXiv error:", e)
    return results
