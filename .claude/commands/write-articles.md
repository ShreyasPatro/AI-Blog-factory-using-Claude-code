---
description: Write all articles in a cluster, using parallel worktrees if more than 3 articles.
argument-hint: "<run_id>"
---

The user wants all articles for run **$ARGUMENTS** to be written. This is a long-running operation.

Steps:

1. Read `runs/$ARGUMENTS/content-architect/output.json` to get the article list.
2. Check `chroma_kb_stats` to verify the KB has been populated with research facts. If total_facts is suspiciously low (<50 for a fresh topic), warn the user and ask whether to proceed without research.
3. For each article in the plan:
   a. Spawn the **lead-writer** subagent with `article_slug` and `run_id`.
   b. After it returns, spawn **fact-verifier** with the article path.
   c. Spawn **brand-auditor** with the article path.
   d. Read both scores. If `fact_check_score < 0.85` OR `brand_score < 7.0` OR `readability < 55` OR `flagged_count > 3`:
      - Spawn **rewriter**.
      - Re-run fact-verifier and brand-auditor.
      - Maximum 2 quality-loop iterations per article.
   e. After loop exit, spawn **meta-tagger** to finalize meta + schema.
4. Print a final summary table: slug, words, scores (fact/brand/readability), iterations, status.

## Parallelism note

If the article count is greater than 3, you should suggest to the user:

  "This cluster has N articles. To run them in parallel via git worktrees, exit this session
   and run: python scripts/parallel_writers.py $ARGUMENTS"

Do not auto-spawn worktrees from within a session — that's a separate orchestration mode handled by the Python orchestrator. From within this Claude Code session, run them sequentially.