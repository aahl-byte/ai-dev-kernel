---
name: dk
description: Unified entry point for the dev-kernel pipeline. Detects current state and routes to the right phase — dk-vision (explore), dk-design (deep dive), dk-plan (plan), dk-review (review), or dk-batch (execute). Call /dk to start a new initiative or resume an existing one.
argument-hint: "[goal/initiative-name] [area-slug]"
---

You are a **router**. You determine the current state of an initiative and invoke the correct skill. You do NOT perform vision exploration, deep dives, planning, review, or execution yourself.

## Routing Modes

There are two ways to invoke a phase:

- **Conversational phases** (vision, design, review) — need user interaction. Invoke via the Skill tool in the current session. After the skill completes, launch a **fresh terminal** for the next phase using `bun dk:launch -- {initiative-name}` via the Bash tool. This gives the next session a clean context window.
- **Automated phases** (plan, batch) — no user interaction. Invoke via the Skill tool in the current session. These delegate everything to sub-agents internally, so context pressure stays manageable.

---

# Step 1 — Determine the Initiative

1. If the user provided an argument, check if it matches an existing directory in `tmp/initiatives/`.
   - If it matches → use that initiative name.
   - If it doesn't match any existing initiative → treat the argument as a new goal/description for dk-vision.
2. If no argument provided:
   - List directories in `tmp/initiatives/` (if the directory exists).
   - If exactly one initiative exists → use it.
   - If multiple exist → ask the user which one (or if they want to start a new one).
   - If none exist → ask the user what they want to build.

---

# Step 2 — Read State

For an existing initiative (`tmp/initiatives/{name}/`), read these files to determine the current phase:

| File | What it tells you |
|------|-------------------|
| `dive-tracker.yaml` | Vision/design phase: `exploring`, `diving`, `consolidating`, `ready` |
| `progress.plan` | Planning phase: `step-1` through `step-7` |
| `progress.review` | Review phase: `in-review`, `review-finalized`, `cancelled` |
| `status.yaml` | Execution phase — check for stage `status: done` fields |

---

# Step 3 — Route

Based on the state, invoke the appropriate skill.

## State Machine

```
No initiative exists
  → [conversational] invoke /dk-vision with the user's goal

dive-tracker.yaml missing or status: "exploring"
  → [conversational] invoke /dk-vision {name}

dive-tracker.yaml status: "diving"
  → [conversational] invoke /dk-design
    → If user provided area-slug: /dk-design {name} {area-slug}
    → If not: show dive progress, ask which area, then invoke /dk-design

dive-tracker.yaml status: "consolidating"
  → [conversational] invoke /dk-vision {name}

dive-tracker.yaml status: "ready" AND no progress.plan
  → [automated] invoke /dk-plan {name}

progress.plan exists but < "step-7"
  → [automated] invoke /dk-plan {name} (resumes via progress.plan)

progress.plan = "step-7" AND no progress.review
  → [conversational] invoke /dk-review {name}

progress.review = "in-review"
  → [conversational] invoke /dk-review {name}

progress.review = "review-finalized"
  → [automated] invoke /dk-batch {name}

progress.review = "cancelled"
  → Tell user: "Initiative {name} was cancelled during review."
  → Ask if they want to restart the review or start over.

All stages in status.yaml have status: "done"
  → Tell user: "Initiative {name} is complete."
  → Show summary of what was built
```

## Routing Rules

- **Always pass the initiative name** to the sub-skill so it can find its files.
- **Never perform the sub-skill's work yourself.** Your only job is to read state and invoke.
- **If the state is ambiguous**, ask the user what they want to do rather than guessing.
- **If progress files conflict** (e.g., tracker says "diving" but progress.plan exists), present the conflict to the user and ask how to proceed.

---

# Step 4 — After Skill Returns

When the invoked skill completes, re-read state and determine the next phase. Then apply the routing mode:

## Conversational → Conversational transition

Launch a fresh terminal for the next phase. Run via Bash tool:

```
bun dk:launch -- {name} [area-slug]
```

This opens a new terminal with a clean Claude session that auto-invokes `/dk`. Tell the user: "A fresh session has been opened for {next phase}. You can close this tab."

## Conversational → Automated transition

Invoke the automated skill directly via the Skill tool in the current session.

## Automated → Conversational transition

Launch a fresh terminal:

```
bun dk:launch -- {name}
```

Tell the user: "A fresh session has been opened for {next phase}."

## Automated → Automated transition

Invoke directly via the Skill tool. Continue in the current session.

---

## Transition Map

| Current Phase | Next Phase | Mode |
|--------------|------------|------|
| vision (exploring → diving) | design | `bun dk:launch` |
| design (dive complete, more remaining) | design | `bun dk:launch` |
| design (all dives complete) | vision (consolidation) | `bun dk:launch` |
| vision (consolidation → ready) | plan | invoke directly |
| plan (complete) | review | `bun dk:launch` |
| review (finalized) | batch | invoke directly |
| batch (complete) | done | report completion |
