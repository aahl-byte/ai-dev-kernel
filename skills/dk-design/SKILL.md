---
name: dk-design
description: Dev-kernel pipeline — deep-dive designer. Runs a focused design session on a single area identified by dk-vision. Explores UX, behaviors, edge cases, and interactions through conversational brainstorming. Includes a sub-agent review gate for completeness and cross-alignment checking.
argument-hint: "{initiative-name} {area-slug}"
---

<CRITICAL-ACTIONS>
1. This is a CONVERSATIONAL skill. You brainstorm WITH the user — do not delegate the conversation.
2. You MUST read the vision doc and dive tracker before starting.
3. You MUST read any previously completed dives for cross-alignment context.
4. The review gate (sub-agent) is mandatory — do not skip it.
5. You MUST update the dive tracker when the dive is complete.
6. If the deep dive reveals the vision needs revision, flag it in the tracker.
</CRITICAL-ACTIONS>

---

# Overview

dk-design runs a focused, deep brainstorming session on a single area within an initiative. You already know the big picture (from the vision). Now you're working out the specifics of one area with the user.

```
Read context (vision + tracker + prior dives)
  → Deep Dive Session (conversational)
  → Draft the dive document
  → Review Gate (sub-agent)
  → Iterate with user if needed
  → Finalize + update tracker
```

---

# Step 1 — Initialize

1. Parse arguments: expect `{name}` and `{area-slug}`.
   - If missing, list initiatives in `tmp/initiatives/` and ask.
2. Read `tmp/initiatives/{name}/dive-tracker.yaml` — verify the area exists and needs a dive.
3. Read `tmp/initiatives/{name}/vision.md`.
4. Read ALL existing dive documents in `tmp/initiatives/{name}/dives/`.
5. If project specs exist, read relevant ones for codebase context.

---

# Step 2 — Set Context

Ground the conversation:
1. Summarize what the vision says about this area
2. Note interactions with other areas
3. Note relevant decisions from completed dives
4. State the goal: "We need to design {area} in enough detail that implementation can proceed without ambiguity."

---

# Step 3 — Deep Dive Session

Adapt exploration to the area type:

## For UX/UI Areas
- **User Flows** — entry points, happy path, exit points
- **Interactions & Feedback** — visual feedback, states, animations
- **Edge Cases & Error States** — failures, extreme data, accessibility
- **Visual Hierarchy & Layout** — importance, responsiveness

## For Data/Logic Areas
- **Behaviors & Rules** — core behaviors, invariants, state changes
- **Data Flow** — sources, transformations, caching
- **Failure Modes** — what can go wrong, recovery paths
- **Performance & Scale** — requirements, volumes, concurrency

## For Integration Areas
- **Contracts** — API surface, inputs/outputs, guarantees
- **Dependencies** — what depends on what, coupling strategy
- **Failure & Fallback** — unavailability, degraded mode, retry

## Conversation Guidelines
- Go deep on what matters, skim what doesn't.
- Probe surface-level answers: "What happens when...?"
- When the user is stuck, offer 2-3 options to react to.
- Connect decisions back to the vision.
- Track decisions as you go — summarize after each aspect.
- Flag contradictions with the vision or other dives immediately.

---

# Step 4 — Draft the Dive Document

Write to: `tmp/initiatives/{name}/dives/{area-slug}.md`

```markdown
# Deep Dive: {Area Name}

Initiative: {name}
Date: YYYY-MM-DD

## Summary
{2-3 sentences}

## Key Decisions

### {Decision Title}
**Decision:** {what}
**Rationale:** {why}
**Alternatives considered:** {brief}

## Behaviors
- {behavior 1: specific, testable}

## User Flows (if UX area)
### Flow: {Name}
1. {step}

## Edge Cases & Error States
- {case}: {handling}

## Interactions with Other Areas
- {area}: {how}

## Risks & Open Questions
- {item}

## Vision Alignment
{How this serves the vision. Flag any needed revisions.}
```

---

# Step 5 — Review Gate

Spawn a **single general-purpose sub-agent**:

<REVIEW-GATE-AGENT-PROMPT>
1. Read `tmp/initiatives/{name}/vision.md`.
2. Read `tmp/initiatives/{name}/dives/{area-slug}.md` (the dive being reviewed).
3. Read ALL OTHER dive documents for cross-alignment.
4. If project specs exist, read relevant architecture specs.

Evaluate for:
- **Completeness** — all vision items covered? decisions documented? edge cases addressed?
- **Alignment** — consistent with vision and other dives? matches architecture?
- **Clarity** — implementable without clarifying questions? testable behaviors?

Write to: `tmp/initiatives/{name}/dives/{area-slug}-review.md`

```markdown
# Review: {Area Name}

## Verdict: {Complete | Minor Gaps | Significant Gaps}

## Completeness
## Alignment
## Clarity
## Recommendations
```
</REVIEW-GATE-AGENT-PROMPT>

---

# Step 6 — Iterate

Present review findings to the user:
- **Complete**: Confirm and finalize.
- **Minor Gaps**: List findings, ask if user wants to address them.
- **Significant Gaps**: Work through them conversationally.

No need to re-run the review gate after iteration.

---

# Step 7 — Finalize

1. Update `dive-tracker.yaml`: set area depth to `complete`, add vision revisions if flagged.
2. Delete the review file.
3. Tell user: dive complete, remaining areas, or "all done — run `/dk` to consolidate."
