"""
SerpAPI as an in-process MCP server.

Why: Claude Code subagents can call MCP tools natively, with caching, retries,
and permission control built in. This replaces the direct SerpAPI calls in
trend_scout.py and competitor_spy.py.

Run as standalone: python mcp/serp_server.py  (for testing)
Used by Claude Code via .claude/settings.json mcpServers config.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Any
from claude_agent_sdk import tool, create_sdk_mcp_server
from serpapi import GoogleSearch

CACHE_DIR = Path("runs/_serp_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
SERPAPI_KEY = os.environ["SERPAPI_KEY"]


def _cache_key(params: dict) -> Path:
    h = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
    return CACHE_DIR / f"{h}.json"


@tool(
    "serp_search",
    "Search Google via SerpAPI for a given query, localized to Bangalore. "
    "Returns organic results, People Also Ask, related searches, and SERP features.",
    {"query": str, "num_results": int},
)
async def serp_search(args: dict[str, Any]) -> dict[str, Any]:
    params = {
        "engine": "google",
        "q": args["query"],
        "location": "Bangalore, Karnataka, India",
        "gl": "in",
        "hl": "en",
        "num": args.get("num_results", 10),
        "api_key": SERPAPI_KEY,
    }

    # Cache check (saves money during demo iterations)
    cache_file = _cache_key(params)
    if cache_file.exists():
        data = json.loads(cache_file.read_text())
        return {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]}

    raw = GoogleSearch(params).get_dict()
    distilled = {
        "query": args["query"],
        "organic": [
            {
                "title": r.get("title", ""),
                "link": r.get("link", ""),
                "snippet": r.get("snippet", ""),
                "domain": r.get("link", "").split("/")[2] if r.get("link", "").startswith("http") else "",
            }
            for r in raw.get("organic_results", [])[:10]
        ],
        "paa": [
            {"question": q.get("question", ""), "snippet": q.get("snippet", "")}
            for q in raw.get("related_questions", [])
        ],
        "related_searches": [r.get("query", "") for r in raw.get("related_searches", [])],
        "has_featured_snippet": bool(raw.get("answer_box")),
        "has_ai_overview": bool(raw.get("ai_overview")),
    }

    cache_file.write_text(json.dumps(distilled, indent=2))
    return {"content": [{"type": "text", "text": json.dumps(distilled, indent=2)}]}


@tool(
    "google_autocomplete",
    "Get Google autocomplete suggestions for a seed query.",
    {"seed": str},
)
async def google_autocomplete(args: dict[str, Any]) -> dict[str, Any]:
    params = {"engine": "google_autocomplete", "q": args["seed"], "gl": "in", "api_key": SERPAPI_KEY}
    cache_file = _cache_key(params)
    if cache_file.exists():
        return {"content": [{"type": "text", "text": cache_file.read_text()}]}

    raw = GoogleSearch(params).get_dict()
    suggestions = [s.get("value", "") for s in raw.get("suggestions", [])]
    payload = json.dumps({"seed": args["seed"], "suggestions": suggestions}, indent=2)
    cache_file.write_text(payload)
    return {"content": [{"type": "text", "text": payload}]}


# Expose for Claude Code to import
canvas_serp_server = create_sdk_mcp_server(
    name="canvas-serp",
    version="1.0.0",
    tools=[serp_search, google_autocomplete],
)


if __name__ == "__main__":
    print("MCP server defined. Used by Claude Code via settings.json — not run standalone.")