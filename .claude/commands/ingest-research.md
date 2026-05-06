---
description: Ingest a Perplexity research document into the knowledge base.
argument-hint: "<filepath> <topic>"
---

The human has run Perplexity and wants to ingest the output. Arguments: $ARGUMENTS

Steps:
1. Parse $ARGUMENTS into filepath and topic. If unclear, ask.
2. Find the active run_id (most recent in runs/ unless stated).
3. Delegate to the **ingestor** subagent with: filepath, topic, run_id.
4. After ingestion completes, run the chroma_kb_stats MCP tool to confirm fact counts increased.
5. Print a summary: "Ingested N facts into the knowledge base. KB now has M total facts. Ready for /write-articles.