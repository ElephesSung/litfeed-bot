
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any

def fetch(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not config.get("sources", {}).get("crossref", False):
        return []

    base = "https://api.crossref.org/works"
    lookback_days = config.get("lookback_days", 3)
    lookback = (datetime.utcnow() - timedelta(days=lookback_days)).date().isoformat()
    max_rows = config.get("max_per_source", 20)

    results = []
    params_list = []

    # by ISSN (journals)
    for j in config.get("journals", []):
        for issn in j.get("issn", []):
            params_list.append({"filter": f"from-pub-date:{lookback},issn:{issn}", "sort": "published", "order": "desc"})

    # by keywords
    for kw in config.get("keywords", []):
        params_list.append({"query": kw, "filter": f"from-pub-date:{lookback}", "sort":"published", "order":"desc"})

    for params in params_list:
        try:
            r = requests.get(base, params={**params, "rows": max_rows}, timeout=20)
            r.raise_for_status()
            payload = r.json().get("message", {}).get("items", [])
            for w in payload:
                title = " ".join(w.get("title") or []) or "(no title)"
                doi = w.get("DOI")
                url = w.get("URL") or (f"https://doi.org/{doi}" if doi else None)
                journal = (w.get("container-title") or [""])[0]
                pub = w.get("published-print") or w.get("published-online") or {}
                date_parts = pub.get("date-parts", [[]])
                date_str = "-".join(map(str, date_parts[0])) if date_parts and date_parts[0] else w.get("created",{}).get("date-time","")
                results.append({
                    "uid_hint": doi or (title + journal + (date_str or "")),
                    "title": title,
                    "journal": journal,
                    "published": date_str,
                    "doi": doi,
                    "url": url,
                    "source": "crossref",
                    "raw": w,
                })
        except Exception as e:
            print("Crossref error:", e)
    return results
