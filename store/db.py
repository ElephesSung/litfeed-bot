
import sqlite3, json, hashlib
from datetime import datetime
from typing import Dict

DB_PATH = "litfeed.sqlite"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS items(
      id TEXT PRIMARY KEY,
      title TEXT, journal TEXT, published TEXT,
      doi TEXT, url TEXT, source TEXT, raw_json TEXT,
      created_at TEXT
    )""")
    conn.commit(); conn.close()

def _hash(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def make_uid(item: Dict) -> str:
    # priority: DOI > arXiv/bioRxiv IDs via uid_hint containing them > fallback hash
    if item.get("doi"):
        return item["doi"].lower().strip()
    if item.get("uid_hint"):
        return _hash(item["uid_hint"])
    s = (item.get("title","")+item.get("journal","")+item.get("published","")).strip()
    return _hash(s or item.get("url","fallback"))

def seen(uid: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT 1 FROM items WHERE id=?", (uid,))
    row = cur.fetchone(); conn.close()
    return row is not None

def persist(uid: str, item: Dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""INSERT OR IGNORE INTO items
      (id,title,journal,published,doi,url,source,raw_json,created_at)
      VALUES (?,?,?,?,?,?,?,?,?)""",      (uid, item.get("title"), item.get("journal"), item.get("published"),
       item.get("doi"), item.get("url"), item.get("source"),
       json.dumps(item, ensure_ascii=False), datetime.utcnow().isoformat()))
    conn.commit(); conn.close()
