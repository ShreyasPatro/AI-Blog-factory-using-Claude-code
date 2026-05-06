---
description: Kick off a new content cluster build for a Bangalore topic.
argument-hint: "topic name (e.g. 'HSR Layout')"
---

Start a new content cluster build for the topic: **$ARGUMENTS**

Steps you must perform:

1. Generate a unique run_id of the form `run-YYYYMMDD-HHMMSS-<short-uuid>` and a topic slug (lowercase-hyphenated). Tell me both.
2. Create directories: `runs/<run_id>/`, `output/clusters/<topic-slug>/`.
3. Delegate to the **trend-scout** subagent with the topic and run_id. Wait for completion.
4. Delegate to the **competitor-spy** subagent. Wait.
5. Delegate to the **keyword-mapper** subagent. Wait.
6. **STOP** at the human approval gate. Print a summary of what was produced (number of PAA questions, number of keyword groups, top 3 AEO opportunities) and tell me to type `/approve-gate <run_id>` to continue or describe changes if I want adjustments.

Do not proceed past step 6 without explicit user approval.