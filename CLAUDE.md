# Canvas Homes Content Pipeline

You are running a hub-spoke content factory for canvas-homes.com, a Bangalore real estate platform. Output is SEO + AEO-optimized markdown articles competing with MagicBricks and NoBroker.

## Architecture

- 10 specialized subagents in `.claude/agents/` — delegate, don't do their work yourself
- SerpAPI is exposed via the `canvas-serp` MCP server (tools: `mcp__canvas-serp__serp_search`, `mcp__canvas-serp__google_autocomplete`)
- Each run has a `run_id` and writes per-stage artifacts to `runs/<run_id>/<agent>/`
- Final articles land in `output/clusters/<topic-slug>/`

## Hard rules

1. ALWAYS delegate to the correct subagent. Don't do trend-scout's work yourself.
2. Brand voice is non-negotiable. Writers and auditors must load the canvas-brand skill.
3. The human approval gate after Layer 1 is mandatory — STOP and ask. Do not auto-approve.
4. Quality loop: max 2 rewrite iterations per article. Then accept and move on.
5. Never make up statistics. Either cite a source from research, use WebSearch, or say "as of <date>, market estimates suggest...".
6. URL format for internal links is `/<slug>` (no trailing slash, no .html). Base URL is `https://canvas-homes.com/`.

## File conventions

- Article frontmatter must include: title, slug, type, meta_title, meta_description, keywords, last_updated.
- All JSON outputs use snake_case keys.
- Slugs: lowercase, hyphenated, no special chars, max 80 chars.

## When in doubt

Run `/status` to see where the current pipeline is. Read run.json files in `runs/`.