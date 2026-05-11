---
name: dk-batch
description: Dev-kernel pipeline — stage executor. Executes approved stages from status.yaml in series. Spawns dk-orchestrator sub-agents per stage with adaptive retry/halt gates. Handles crash recovery by reading stage completion status.
argument-hint: "{initiative-name}"
---

<CRITICAL-ACTIONS>
1. Verify `tmp/initiatives/{name}/progress.review` reads `review-finalized` before executing.
2. Execute the /dk-orchestrator skill using the Skill tool when spawning stage agents.
3. Protect your context window. Delegate ALL implementation to sub-agents.
4. When a stage agent returns, ALWAYS continue immediately — update status, notify, launch next stage.
</CRITICAL-ACTIONS>

---

# Crash Recovery

Uses `status.yaml` itself — completed stages have `status: done`. On startup, find the first stage without `status: done` and resume from there.

---

# Step 1 — Launch Stage Orchestrator

<STAGE-AGENT-PROMPT>
1. Execute the /dk-orchestrator skill using the Skill tool.
2. Read `CLAUDE.md` if it exists for project rules.
3. Read `tmp/initiatives/{name}/status.yaml` for stage structure and tickets.
4. For each domain referenced in your tickets, read its spec at `tmp/initiatives/{name}/specs/{domain-slug}.md`.
5. When spawning sub-agents, include:
   - Explicit skill invocation instructions (skills don't auto-inherit)
   - `CLAUDE.md` reading instruction
   - Project spec reading instructions
6. Begin stage {stage_id}.
</STAGE-AGENT-PROMPT>

Launch with the Agent tool (do NOT use `run_in_background`).

---

# Step 2 — Evaluate Outcome (Adaptive Gate)

After each stage returns:
- **Clean / minor** → proceed to Step 3.
- **Recoverable** (type errors, clear fixes) → retry once with targeted guidance. Second failure → catastrophic.
- **Catastrophic** → notify user, mark stage `blocked`, halt.

---

# Step 3 — Update status.yaml

```yaml
    status: done                # or "blocked"
    completed: "<YYYY-MM-DD>"
    commit: "<short SHA>"
    validation: "tmp/validations/<batch-id>-v<N>/ — <CLEAN|FINDINGS>"
```

---

# Step 4 — Repeat or Finalize

- More stages → back to Step 1.
- All done → run final validation, report summary.
