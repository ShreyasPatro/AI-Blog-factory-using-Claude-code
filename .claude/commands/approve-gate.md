---
description: After human review of Layer 1 outputs, proceed with planning + writing.
argument-hint: "<run_id>"
---

The user has approved Layer 1 for run **$ARGUMENTS**. Proceed:

1. Delegate to **content-architect** with the run_id. Wait.
2. Delegate to **faq-architect** with the run_id. Wait.
3. Print the article plan: titles, types, word-count targets. Then begin writing.
4. For each article in the plan:
   a. Delegate to **lead-writer** with the article slug.
   b. Delegate to **fact-verifier** with the article path.
   c. Delegate to **brand-auditor** with the article path.
   d. Read the two scores. If `fact_check_score < 0.85` OR `brand_score < 7.0` OR `readability < 55` OR `flagged_count > 3`, delegate to **rewriter**. Then re-run fact-verifier and brand-auditor. Maximum 2 quality-loop iterations per article.
   e. If still failing after 2 iterations, accept and move on (log to `runs/<run_id>/_failures.json`).
   f. Delegate to **meta-tagger** to finalize meta + schema.
5. After all articles done: print a final summary table (slug, words, scores, status) and the path to the finished cluster.