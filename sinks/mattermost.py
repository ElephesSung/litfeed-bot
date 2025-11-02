
import os, requests
from typing import List, Dict, Any

def _env_sub(value: str) -> str:
    if value and value.startswith("${") and value.endswith("}"):
        key = value[2:-1]
        return os.getenv(key, "")
    return value

def post_cards(config: Dict[str, Any], cards: List[str]) -> None:
    mm = config.get("mattermost", {})
    webhook = _env_sub(mm.get("webhook_url", ""))
    if not webhook:
        raise RuntimeError("Mattermost webhook_url is not set (or env substitution failed).")

    text = "\n\n".join(cards)
    payload = {
        "text": text,
        "username": mm.get("username","LitFeedBot"),
        "icon_emoji": mm.get("icon_emoji",":books:")
    }
    r = requests.post(webhook, json=payload, timeout=25)
    r.raise_for_status()
