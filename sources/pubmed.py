
import requests
from typing import List, Dict, Any

def fetch(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not config.get("sources", {}).get("pubmed", False):
        return []
    if not config.get("keywords"):
        return []

    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    max_rows = config.get("max_per_source", 20)

    query = " OR ".join([f'("{kw}")' for kw in config.get("keywords", [])])
    results = []
    try:
        es = requests.get(base + "esearch.fcgi", params={
            "db":"pubmed","term":query,"retmode":"json","retmax":max_rows,
            "sort":"pub+date"
        }, timeout=20).json()
        ids = es.get("esearchresult",{}).get("idlist",[])
        if not ids: return results
        sm = requests.get(base + "esummary.fcgi", params={"db":"pubmed","id":",".join(ids),"retmode":"json"}, timeout=20).json()
        for k,v in sm.get("result",{}).items():
            if k=="uids": continue
            title = v.get("title")
            journal = v.get("fulljournalname") or v.get("source")
            date_str = v.get("pubdate") or v.get("epubdate") or v.get("sortpubdate","")
            url = f"https://pubmed.ncbi.nlm.nih.gov/{k}/"
            results.append({
                "uid_hint": "PMID:"+k,
                "title": title,
                "journal": journal,
                "published": date_str,
                "doi": v.get("elocationid","").replace("doi: ","") if v.get("elocationid") else None,
                "url": url, "source": "pubmed", "raw": v
            })
    except Exception as e:
        print("PubMed error:", e)
    return results
