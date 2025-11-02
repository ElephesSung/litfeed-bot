
from typing import Dict, List

def render_cards(items: List[Dict]) -> List[str]:
    cards = []
    for it in items:
        s = it.get("summary", {})
        tldr = s.get("tldr") or "—"
        methods = s.get("methods") or []
        findings = s.get("findings") or []
        limitations = s.get("limitations") or []
        cards.append(
f"""**{s.get('title', it['title'])}**  
*{s.get('venue', it['journal'])}* · {s.get('published', it['published'])}  
{s.get('link', it['url'])}

**TL;DR**: {tldr}
**Methods**: {('; '.join(methods)) if methods else '—'}
**Findings**: {('; '.join(findings)) if findings else '—'}
**Limitations**: {('; '.join(limitations)) if limitations else '—'}""")
    return cards
