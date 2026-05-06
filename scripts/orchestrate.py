"""
Run the full Canvas Homes pipeline from Python, no interactive CC session.
Used for production / CI / scheduled runs.

Usage: python scripts/orchestrate.py "HSR Layout"
"""

import sys
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def run_pipeline(topic: str):
    options = ClaudeAgentOptions(
        cwd=".",                       # project root
        setting_sources=["project"],   # picks up .claude/agents, .claude/skills, mcp servers
        permission_mode="acceptEdits", # auto-approve file edits during the run
        max_turns=200,                 # enough for 10 agents × 11 articles
    )

    prompt = f"""Build a complete content cluster for the Bangalore topic: "{topic}".

Run the pipeline:
1. trend-scout, competitor-spy, keyword-mapper (Layer 1)
2. AUTO-APPROVE the gate (this is non-interactive). Print the Layer 1 summary first.
3. content-architect, faq-architect (Layer 2)
4. For every article: lead-writer → fact-verifier → brand-auditor → (rewriter if needed, max 2 iterations) → meta-tagger
5. Print final summary.

Use a fresh run_id. Write all artifacts to runs/<run_id>/. Write final articles to output/clusters/<slug>/."""

    async for message in query(prompt=prompt, options=options):
        # Print streaming progress
        if hasattr(message, "content"):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text, end="", flush=True)
        elif hasattr(message, "result"):
            print(f"\n\n=== FINAL ===\n{message.result}")


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "HSR Layout"
    asyncio.run(run_pipeline(topic))
    