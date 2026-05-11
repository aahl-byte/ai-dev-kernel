---
name: dk-vision
description: Dev-kernel pipeline — vision architect. Builds an overarching vision for large initiatives through conversational exploration with the user. Identifies areas needing detailed design, tracks deep-dive progress, and consolidates everything into a design file for dk-plan. Called by the /dk router.
argument-hint: "[goal description or existing initiative name to resume]"
---

<CRITICAL-ACTIONS>
1. This is a CONVERSATIONAL skill. You explore the vision WITH the user through dialogue.
2. Check for existing progress before starting fresh — read `tmp/initiatives/*/dive-tracker.yaml` if resuming.
3. You MUST write the vision doc and dive tracker to disk so dk-design can read them.
4. You MUST NOT proceed to consolidation until ALL deep-dive areas are marked `complete` in the tracker.
5. Sub-agents CANNOT interact with the user. All user-facing dialogue happens in YOUR context.
</CRITICAL-ACTIONS>

---

# Overview

dk-vision sits at the start of the pipeline. It takes a large, potentially vague goal and through structured conversation with the user, produces:

1. A **vision document** — the north star for the initiative
2. A **dive tracker** — structured state tracking for deep-dive progress
3. A **design file** — the final consolidated output that feeds into dk-plan

```
User's idea/goal
  |
  v
Phase 1: Vision Exploration (conversational)
  -> vision.md + dive-tracker.yaml
  |
  v
Phase 2: Deep Dives (user runs /dk-design per area)
  -> dives/{area-slug}.md (per area)
  |
  v
Phase 3: Consolidation (cross-alignment + final design)
  -> design.md (input for dk-plan)
```

---

# File Structure

All files live in `tmp/initiatives/{name}/`:

```
tmp/initiatives/{name}/
├── vision.md              # The overarching vision document
├── dive-tracker.yaml      # Structured progress tracking
├── design.md              # Final consolidated design (Phase 3 output)
└── dives/
    ├── {area-slug}.md     # Deep dive documents (written by dk-design)
    └── ...
```

## Dive Tracker Schema

```yaml
initiative_name: "{name}"
status: "exploring" | "diving" | "consolidating" | "ready"
vision_file: "tmp/initiatives/{name}/vision.md"
design_file: "tmp/initiatives/{name}/design.md"
updated: "YYYY-MM-DD"

areas:
  - slug: "area-slug"
    name: "Area Name"
    summary: "One-line description of what this area covers"
    depth: "vision-level" | "needs-dive" | "complete" | "needs-revision"
    dive_file: "tmp/initiatives/{name}/dives/area-slug.md"

vision_revisions:
  - area: "area-slug"
    flag: "Description of what needs to change in the vision"
    status: "pending" | "applied"
```

---

# Phase 1 — Vision Exploration

This phase is a structured conversation. You are not delegating — you are thinking WITH the user.

## Step 1 — Initialize

1. Derive `{name}` from the user's argument: slugify it (lowercase, hyphens, no special chars).
2. Check if `tmp/initiatives/{name}/dive-tracker.yaml` exists.
   - **If resuming:** Read the tracker and vision doc. Determine the current state:
     - `exploring` → Continue the vision conversation (Step 2)
     - `diving` → Show dive progress and tell the user which areas still need dives (skip to Handoff)
     - `consolidating` → Continue consolidation (skip to Phase 3)
     - `ready` → The design file is already produced. Tell the user and suggest running /dk.
   - **If new:** Proceed to Step 2.
3. If project specs exist (`specs/` directory), read them for context.

## Step 2 — Explore the Vision

Your goal is to build a complete mental model of what the user wants to achieve. This is NOT brainstorming solutions — it's understanding the problem space and desired outcomes.

Guide the conversation through these layers:

**Layer 1 — The Goal**
- What are we building / changing / fixing?
- Why now? What's the trigger?
- Who benefits and how?

**Layer 2 — Scope & Boundaries**
- What's explicitly in scope?
- What's explicitly OUT of scope?
- Are there hard constraints? (Timeline, tech, team, budget)
- Are there non-negotiable requirements?

**Layer 3 — Current State**
- What exists today that's relevant?
- What's working well that we shouldn't break?
- What's the pain that's driving this?

**Layer 4 — Desired Behaviors**
- What are the critical behaviors of the finished system?
- How should users interact with it?
- What should happen in edge cases and error states?
- Are there performance / scale requirements?

**Layer 5 — Area Identification**
- Based on everything discussed, what are the natural areas/domains?
- Which areas are straightforward (can be covered at vision level)?
- Which areas have UX complexity, multiple valid approaches, or need user input to resolve?
- How do the areas interact with each other?

### Conversation guidelines

- Ask one focused question at a time.
- Reflect back what you've heard before moving to the next layer.
- When the user is uncertain, help them think through it rather than deciding for them.
- Watch for hidden assumptions.
- Don't move to area identification until you have a clear picture of the goal, scope, and desired behaviors.
- If the user provides a document or spec as input, read it first, then use the conversation to fill gaps.

## Step 3 — Document the Vision

Write to: `tmp/initiatives/{name}/vision.md`

```markdown
# Vision: {Name}

## Goal
{What we're building and why — 2-3 sentences}

## Trigger
{Why now — what prompted this initiative}

## Scope
### In Scope
- {item}

### Out of Scope
- {item}

### Constraints
- {hard constraint}

## Current State
{What exists today, what works, what's broken}

## Critical Behaviors
- {behavior 1}
- {behavior 2}

## Areas

### {Area Name} [vision-level | needs-dive]
{2-3 sentence summary}

Interactions: {how this area connects to other areas}

## Open Questions
- {question surfaced during exploration}

## Principles
{Design principles or values that should guide all subsequent work}
```

## Step 4 — Initialize the Tracker

Write to: `tmp/initiatives/{name}/dive-tracker.yaml`

Set status to `diving` if any areas need dives, or `consolidating` if all areas are vision-level.

## Step 5 — Handoff

Tell the user:
1. The vision has been documented
2. List areas that need deep dives with WHY each needs one
3. Instruct: "Run `/dk-design {name} {area-slug}` for each area, or `/dk` to be guided."
4. When all dives are complete, run `/dk {name}` to consolidate.

---

# Phase 2 — Deep Dives (External)

Handled by the user running `/dk-design`. dk-vision does NOT execute deep dives.

When the user returns mid-process:
1. Read the tracker
2. Show progress
3. If vision revisions are pending, discuss them with the user
4. Direct user to the next dive

---

# Phase 3 — Consolidation

Activates when ALL areas are either `vision-level` or `complete`.

## Step 1 — Cross-Alignment Check

Spawn a **single general-purpose sub-agent**:

<CROSS-ALIGNMENT-AGENT-PROMPT>
1. Read `tmp/initiatives/{name}/vision.md`.
2. Read ALL dive documents in `tmp/initiatives/{name}/dives/`.
3. Check for: contradictions between dives, gaps in area interactions, vision drift, missing critical behaviors, redundant solutions.

Write findings to: `tmp/initiatives/{name}/cross-alignment-report.md`

Format:
```markdown
# Cross-Alignment Report

## Verdict: {Clean | Minor Issues | Significant Conflicts}

## Contradictions
## Gaps
## Vision Drift
## Missing Behaviors
## Redundancy
## Recommendations
```
</CROSS-ALIGNMENT-AGENT-PROMPT>

## Step 2 — Resolve Findings

Present findings to the user. Discuss resolutions conversationally.

## Step 3 — Produce the Design File

Spawn a **single general-purpose sub-agent**:

<CONSOLIDATION-AGENT-PROMPT>
1. Read `tmp/initiatives/{name}/vision.md`
2. Read ALL dive documents in `tmp/initiatives/{name}/dives/`
3. Read `tmp/initiatives/{name}/cross-alignment-report.md` (if exists)
4. Produce a consolidated design document.

Write to: `tmp/initiatives/{name}/design.md`

Structure:
```markdown
# Design: {Name}

## Vision
{Condensed — goal, scope, constraints, principles}

## Critical Behaviors
{Ordered list}

## Areas

### {Area Name}
#### Key Decisions
#### Behaviors
#### Interactions
#### Risks & Edge Cases

## Cross-Cutting Concerns
## Open Questions
```

Keep it dense and decision-focused. Drop exploration history.
</CONSOLIDATION-AGENT-PROMPT>

## Step 4 — Finalize

1. Update tracker: set status to `ready`.
2. Tell user the design file is ready and suggest running `/dk` to begin planning.
