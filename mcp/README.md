# MCP Demo (Python)

This is a **teaching-grade** implementation of the **Model Context Protocol (MCP)** using the official Python SDK.
It contains:

- A **FastMCP** server exposing a few tools and resources
- A **tiny local client** that speaks MCP over STDIO using LSP-like `Content-Length` framing
- No hardcoded secrets; config via environment variables when needed

## Quick Start

```bash
# 1) Create a virtualenv
python -m venv .venv && source .venv/bin/activate

# 2) Install
pip install -e .

# 3) Run the server (foreground)
mcp-demo-server
```

In a second terminal (with the same venv), run the demo client which spawns the server for you and calls tools over MCP:

```bash
python client/demo_client.py
```

You should see:
- Protocol `initialize` handshake
- Tool listing
- Successful tool calls to `add`, `search_http`, and `read_file`

## What’s inside

- `src/mcp_demo/server.py` — FastMCP server exposing:
  - `add(a, b)` — numeric addition
  - `search_http(query)` — performs an HTTP GET to DuckDuckGo Lite and returns the top result titles/links
  - `read_file(path)` — reads files under the repo’s `sample_data` folder (safe base dir), prevents path traversal
  - A sample **resource**: `sample://hello.txt`

- `client/demo_client.py` — minimal JSON-RPC client that:
  - launches the server as a subprocess over STDIO
  - sends `initialize` with protocol version
  - lists tools via `tools/list`
  - calls tools via `tools/call`

## Notes

- Uses **official MCP SDK** (`mcp` on PyPI) and FastMCP helpers.
- Transport is **STDIO with Content-Length** framing (LSP style), as per the current MCP spec.
- This project avoids hardcoding external tokens/secrets. The HTTP tool uses public endpoints only.

## Security

- The file tool is **sandboxed** to `sample_data/` and rejects paths outside it.
- The HTTP tool uses a fixed allowlist (DuckDuckGo Lite) to avoid arbitrary SSRF.
- For production-grade security guidance, see MCP’s official spec and recent security writeups.
