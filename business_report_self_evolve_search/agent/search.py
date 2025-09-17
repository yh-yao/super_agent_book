import os
import requests


def google_search_func(query: str, num: int = 3):
    """Search the web using Google Custom Search API."""
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    
    if not api_key or not cse_id:
        raise ValueError("Missing GOOGLE_API_KEY or GOOGLE_CSE_ID")
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"q": query, "key": api_key, "cx": cse_id, "num": num}
    
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    
    items = data.get("items", []) or []
    return [
        {
            "title": it.get("title", ""),
            "snippet": it.get("snippet", ""),
            "link": it.get("link", "")
        }
        for it in items
    ]


google_search_tool = {
    "type": "function",
    "function": {
        "name": "google_search_func",
        "description": (
            "Search the web using Google Custom Search API and "
            "return top results (title, snippet, link)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string."
                },
                "num": {
                    "type": "integer",
                    "description": "Number of results to return (1-10).",
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        }
    }
}
