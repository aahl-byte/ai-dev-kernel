---
name: dk-review
description: Dev-kernel pipeline — plan reviewer. Conversational review session for a planned initiative. Presents the execution plan, deferred work, and open questions. Lets the user modify scope, reorder stages, and approve for execution.
argument-hint: "{initiative-name}"
---

<CRITICAL-ACTIONS>
1. This is a CONVERSATIONAL skill. You review the plan WITH the user.
2. You MUST read status.yaml, deferred.yaml, and questions.md before starting.
3. You MUST NOT mark the review as finalized until the user explicitly approves.
4. Write/update `tmp/initiatives/{name}/progress.review` after state changes.
</CRITICAL-ACTIONS>

---

# Step 1 — Initialize

1. Read `tmp/initiatives/{name}/progress.review` if it exists.
   - `in-review` → Resume the review session.
   - `review-finalized` → Tell user review is complete, suggest running `/dk`.
   - `cancelled` → Tell user it was cancelled.
2. Read: `status.yaml`, `deferred.yaml` (if exists), `questions.md` (if exists), `design.md`.
3. Write `in-review` to `progress.review`.

---

# Step 2 — Present the Plan

Translate the YAML into a readable summary:
1. **Overview** — name, total tickets, stages, estimated effort
2. **Stage breakdown** — for each: name, tickets, effort, risk, key tickets, dependencies
3. **Deferred work** — how many, grouped by reason, what unblocks them
4. **Open questions** — blocking first, then clarification

End with: "Take your time. You can ask me to explain any ticket, reorder stages, add/remove tickets, or resolve questions. When satisfied, tell me to approve."

---

# Step 3 — Review Session

Free-form conversation. Handle:

- **"Explain ticket X"** — read ticket + domain spec, explain in plain language
- **"Move/reorder"** — edit status.yaml, recalculate dependencies
- **"Remove/add tickets"** — edit status.yaml, update counts
- **"Change scope"** — split/merge stages, renumber
- **"Resolve question"** — record answer, update tickets if needed
- **"Move deferred to active"** — copy from deferred.yaml to status.yaml
- **"What if we skip X?"** — analyze dependency impact

After modifications, validate status.yaml structure.

---

# Step 4 — Finalize

When the user approves:
1. Validate status.yaml one final time.
2. Write `review-finalized` to `progress.review`.
3. Tell user: "Plan approved. Run `/dk` to begin execution."

---

# Cancellation

If user wants to cancel:
1. Confirm.
2. Write `cancelled` to `progress.review`.
3. Tell user the initiative is cancelled and files remain for reference.
