from __future__ import annotations

import os
import re
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import httpx
from mcp.server.fastmcp import FastMCP

# ---- Configure a safe base for file access ----
BASE_DIR = Path(__file__).resolve().parent.parent.parent / "sample_data"
BASE_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_FILE = BASE_DIR / "hello.txt"
if not SAMPLE_FILE.exists():
    SAMPLE_FILE.write_text("Hello from MCP sample resource!\n", encoding="utf-8")

mcp = FastMCP("mcp-demo")

# ---------- Tools ----------

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b

DDG_LITE = "https://duckduckgo.com/lite/"
ALLOWED_HOSTS = {"duckduckgo.com"}

@mcp.tool()
def search_http(query: str) -> List[Dict[str, str]]:
    """
    Perform a very simple web search using DuckDuckGo Lite and return a small list of results.
    This is purposely conservative in what it fetches and parses.
    """
    url = f"{DDG_LITE}?q={httpx.QueryParams({'q': query})['q']}"
    host = httpx.URL(url).host
    if host not in ALLOWED_HOSTS:
        raise ValueError("Host not allowed")

    with httpx.Client(timeout=10.0, headers={"User-Agent": "mcp-demo/0.1"}) as client:
        r = client.get(url)
        r.raise_for_status()
        # Parse a few <a> lines as "results"
        links = re.findall(r'<a href="(https?://[^"]+)"[^>]*>([^<]+)</a>', r.text)[:5]
        return [{"title": title, "url": href} for href, title in links]

def _safe_join(base: Path, relative: str) -> Path:
    p = (base / relative).resolve()
    if not str(p).startswith(str(base.resolve())):
        raise ValueError("Path traversal detected")
    return p

@mcp.tool()
def read_file(path: str) -> str:
    """
    Read a UTF-8 text file relative to the sandboxed sample_data directory.
    Example: path='hello.txt'
    """
    p = _safe_join(BASE_DIR, path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"{p} not found")
    return p.read_text(encoding="utf-8")


# ---------- Resources ----------

@mcp.resource("sample://hello.txt")
def sample_text_resource() -> Tuple[str, bytes]:
    """
    A simple resource exposed by the server.
    Returns: (MIME type, bytes)
    """
    data = SAMPLE_FILE.read_bytes()
    return "text/plain; charset=utf-8", data


def main() -> None:
    # Run server over stdio
    mcp.run()

if __name__ == "__main__":
    main()
