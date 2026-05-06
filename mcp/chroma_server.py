"""
ChromaDB exposed as an MCP server for Claude Code.

Tools:
  - chroma_search_facts: semantic search over ingested facts
  - chroma_search_articles: find similar already-written articles (for dedup)
  - chroma_kb_stats: counts and categories in the KB

This wraps your existing db/chroma_ops.py — no duplicate logic.

Run pattern: configured in .claude/settings.json as a stdio MCP server.
The Claude Code CLI starts it automatically when subagents need it.
"""

import json
from typing import Any
from claude_agent_sdk import tool, create_sdk_mcp_server

# Reuse your existing ChromaDB code
from db.chroma_ops import search_facts, search_articles, get_client, ef


@tool(
    "chroma_search_facts",
    "Semantic search over Canvas Homes' verified fact knowledge base. "
    "Returns top-k facts most relevant to the query, each with source citation, "
    "category (property|rental|legal|finance|lifestyle|infrastructure), "
    "location (Bangalore locality if applicable), and confidence score. "
    "Use BEFORE writing any factual claim — prefer KB facts over WebSearch.",
    {"query": str, "top_k": int, "category_filter": str, "location_filter": str},
)
async def chroma_search_facts(args: dict[str, Any]) -> dict[str, Any]:
    where_filter = {}
    if args.get("category_filter"):
        where_filter["category"] = args["category_filter"]
    if args.get("location_filter"):
        where_filter["location"] = args["location_filter"]

    results = search_facts(
        query=args["query"],
        top_k=args.get("top_k", 10),
        where_filter=where_filter or None,
    )

    payload = {
        "query": args["query"],
        "results_count": len(results),
        "facts": [
            {
                "id": r["id"],
                "text": r["text"],
                "category": r.get("metadata", {}).get("category", ""),
                "location": r.get("metadata", {}).get("location", ""),
                "source": r.get("metadata", {}).get("source_id", ""),
                "relevance": round(1 - r.get("distance", 1.0), 3),
            }
            for r in results
        ],
    }
    return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}]}


@tool(
    "chroma_search_articles",
    "Find existing Canvas Homes articles similar to a topic or query. "
    "Use to detect duplication before writing a new article, or to find related articles for internal linking.",
    {"query": str, "top_k": int},
)
async def chroma_search_articles(args: dict[str, Any]) -> dict[str, Any]:
    results = search_articles(query=args["query"], top_k=args.get("top_k", 5))
    payload = {
        "query": args["query"],
        "results_count": len(results),
        "articles": [
            {
                "id": r["id"],
                "preview": r["text"][:200],
                "title": r.get("metadata", {}).get("title", ""),
                "slug": r.get("metadata", {}).get("slug", ""),
                "similarity": round(1 - r.get("distance", 1.0), 3),
            }
            for r in results
        ],
    }
    return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}]}


@tool(
    "chroma_kb_stats",
    "Return summary statistics of the Canvas Homes knowledge base — total facts, "
    "facts per category, facts per location. Useful before starting a cluster build "
    "to know how much research coverage already exists.",
    {},
)
async def chroma_kb_stats(args: dict[str, Any]) -> dict[str, Any]:
    client = get_client()
    facts_col = client.get_collection("facts", embedding_function=ef)
    articles_col = client.get_collection("articles", embedding_function=ef)

    stats = {
        "total_facts": facts_col.count(),
        "total_articles": articles_col.count(),
    }

    # Sample to count categories/locations (Chroma doesn't have GROUP BY)
    if facts_col.count() > 0:
        sample_size = min(facts_col.count(), 1000)
        sample = facts_col.get(limit=sample_size)
        categories = {}
        locations = {}
        for meta in sample.get("metadatas", []) or []:
            cat = meta.get("category", "unknown")
            loc = meta.get("location", "")
            categories[cat] = categories.get(cat, 0) + 1
            if loc:
                locations[loc] = locations.get(loc, 0) + 1
        stats["categories"] = dict(sorted(categories.items(), key=lambda x: -x[1]))
        stats["top_locations"] = dict(sorted(locations.items(), key=lambda x: -x[1])[:15])

    return {"content": [{"type": "text", "text": json.dumps(stats, indent=2)}]}


# Expose the server
canvas_chroma_server = create_sdk_mcp_server(
    name="canvas-chroma",
    version="1.0.0",
    tools=[chroma_search_facts, chroma_search_articles, chroma_kb_stats],
)


if __name__ == "__main__":
    print("ChromaDB MCP server defined. Used by Claude Code via .claude/settings.json.")