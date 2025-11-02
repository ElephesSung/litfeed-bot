
import os, json, time
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

def _env_or_placeholder(value: str) -> str:
    # support ${VAR} indirection in YAML
    if value and value.startswith("${") and value.endswith("}"):
        key = value[2:-1]
        return os.getenv(key, "")
    return value

class GeminiSummariser:
    def __init__(self, config: Dict[str, Any]) -> None:
        use_vertex = config.get("gemini", {}).get("use_vertex", False)
        self.model_name = config.get("gemini", {}).get("model", "gemini-2.0-flash")
        self.language = config.get("language", "en")
        self.use_vertex = use_vertex
        self.client = None
        if use_vertex:
            # You can switch to Vertex AI SDK here if needed.
            raise NotImplementedError("Vertex AI client wiring not implemented in this minimal build.")
        else:
            import google.generativeai as genai
            api_key_env = config.get("gemini", {}).get("api_key_env", "GOOGLE_API_KEY")
            api_key = os.getenv(api_key_env)
            if not api_key:
                raise RuntimeError(f"Missing {api_key_env} environment variable for Gemini API key.")
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model_name)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type(Exception))
    def _summarise_one(self, item: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
You are an experienced scholarly editor. Write a concise, structured summary in {self.language}.
Return **JSON only** with fields:
- title
- venue
- published
- link
- tldr            (one sentence)
- methods         (2-4 bullet points)
- findings        (2-4 bullet points)
- limitations     (1-3 bullet points)
- who_should_read (1-2 sentences)

If details are unavailable, keep the fields and set "unknown" or direct readers to the link.

Article info:
Title: {item.get('title')}
Journal/Venue: {item.get('journal')}
Published: {item.get('published')}
Link: {item.get('url')}
Possible DOI: {item.get('doi')}
"""
        try:
            resp = self.client.generate_content(
                prompt,
                generation_config={"response_mime_type":"application/json"}
            )
            js = json.loads(resp.text)
            return {**item, "summary": js}
        except Exception as e:
            # Fallback
            return {**item, "summary": {
                "title": item.get("title"),
                "venue": item.get("journal"),
                "published": item.get("published"),
                "link": item.get("url"),
                "tldr": "(LLM summary unavailable; please read the original)",
                "methods": [], "findings": [], "limitations": [], "who_should_read": ""
            }}

    def summarise(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out = []
        for it in items:
            out.append(self._summarise_one(it))
            time.sleep(0.2)  # be gentle
        return out
