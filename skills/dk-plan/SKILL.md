---
name: dk-plan
description: Dev-kernel pipeline — implementation planner. Takes a consolidated design file and produces a triaged execution plan (status.yaml) through a 7-step domain-driven design pipeline. Classifies items into domains, runs parallel architect + reviewer agents, assembles stages, and auto-triages deferrals.
argument-hint: "{initiative-name}"
---

<CRITICAL-ACTIONS>
1. You MUST receive an initiative name. Read the design file at `tmp/initiatives/{name}/design.md`.
2. Consolidation guard: read `tmp/initiatives/{name}/dive-tracker.yaml`. If it exists and `status` is NOT `ready`, HALT and tell the user to complete consolidation first.
3. Check `tmp/initiatives/{name}/progress.plan` for crash recovery. Skip completed steps.
4. Write/update `progress.plan` after EACH step completes.
</CRITICAL-ACTIONS>

---

The planner NEVER performs design or implementation directly. All steps are delegated to sub-agents that write output to disk.

Protect your context window. Your task is only to schedule and delegate. You do not ever want to receive the output of your sub-agents.

---

## Crash Recovery

```
tmp/initiatives/{name}/progress.plan -> "step-1" through "step-7"
```

---

## Pipeline

```
design.md → Step 1: Classify → Step 2: Architect → Step 3: Review → Step 4: Revise → Step 5: Assemble → Step 6: Triage → Step 7: Notify
```

---

## Step 1 — Domain Classification

Spawn a single sub-agent to classify the design into domains.

<CLASSIFIER-AGENT-PROMPT>
1. Read `CLAUDE.md` if it exists for project rules.
2. Explore the project structure to understand the codebase layout.
3. Read the design file at `tmp/initiatives/{name}/design.md`.
4. Classify every item into domains — cohesive areas of the codebase that share architecture.

For each domain:
- Assign a slug (lowercase, hyphens)
- List items with tags: [bug], [feature], [refactor], [ui-tweak]
- Note cross-domain items

Write to: `tmp/initiatives/{name}/classification.md`
</CLASSIFIER-AGENT-PROMPT>

After completion, read the classification and extract domain names/slugs.

---

## Step 2 — Domain Architects (parallel)

For each domain, spawn a sub-agent to produce a design document.

<ARCHITECT-AGENT-PROMPT>
1. Read `CLAUDE.md` if it exists for project rules.
2. Read project specs if they exist.
3. Read `tmp/initiatives/{name}/classification.md` — find your domain's items.
4. Read relevant source files for your domain.
5. For each major design decision, propose 2-3 alternatives with trade-offs. Select one with rationale.
6. Write a design document covering: decisions, rationale, cross-domain interactions, implementation sketch, risks.

Write to: `tmp/initiatives/{name}/designs/{domain-slug}.md`
</ARCHITECT-AGENT-PROMPT>

Launch ALL architect agents in parallel.

---

## Step 3 — Domain Reviewers (parallel)

For each domain, spawn a sub-agent to review.

<REVIEWER-AGENT-PROMPT>
1. Read `CLAUDE.md` if it exists.
2. Read `tmp/initiatives/{name}/designs/{domain-slug}.md`.
3. Read the same source files the architect references.
4. Check: coverage, simpler alternatives, architecture fit, edge cases, cross-domain correctness.

Append a `## Review` section to `tmp/initiatives/{name}/designs/{domain-slug}.md`.
</REVIEWER-AGENT-PROMPT>

Launch ALL reviewer agents in parallel.

---

## Step 4 — Architect Revision (parallel)

For each domain, spawn a sub-agent to address review findings.

<REVISION-AGENT-PROMPT>
1. Read `tmp/initiatives/{name}/designs/{domain-slug}.md` (includes Review section).
2. Address every finding. Append a `## Verdict` section — accept or reject each finding with rationale.

Write the complete file back.
</REVISION-AGENT-PROMPT>

Launch ALL revision agents in parallel.

---

## Step 5 — Assembly

Spawn a single sub-agent to produce status.yaml.

<ASSEMBLER-AGENT-PROMPT>
1. Read `CLAUDE.md` if it exists.
2. Read ALL design documents in `tmp/initiatives/{name}/designs/`.
3. For each domain, generate a condensed spec at `tmp/initiatives/{name}/specs/{domain-slug}.md` (~100-200 lines).
4. Produce `tmp/initiatives/{name}/status.yaml`:
   - Derive tickets from design decisions
   - Order: bugs first, refactors second, features last
   - Max 10 tickets per stage
   - Each ticket references its domain and decision
5. Validate: run `bun dk:validate -- tmp/initiatives/{name}/status.yaml --verbose`. Fix any errors.
</ASSEMBLER-AGENT-PROMPT>

---

## Step 6 — Auto-Triage & Deferral

Spawn a single sub-agent to split automatable vs. deferred work.

<TRIAGE-AGENT-PROMPT>
1. Read `tmp/initiatives/{name}/status.yaml`.
2. Read ALL design documents for context.
3. Scan for deferral signals — tickets that require manual work the agent cannot do:
   - Database migrations or schema changes
   - External system dependencies
   - Blocked prerequisites requiring human action
   - Infrastructure provisioning
4. Produce:
   - Pruned `tmp/initiatives/{name}/status.yaml` (active tickets only)
   - `tmp/initiatives/{name}/deferred.yaml` (grouped by reason)
   - `tmp/initiatives/{name}/questions.md` (open questions, categorized by urgency)
5. Validate: run `bun dk:validate -- tmp/initiatives/{name}/status.yaml --verbose`. Fix any errors.
6. Return summary: active tickets, deferred tickets, stages, questions.
</TRIAGE-AGENT-PROMPT>

---

## Step 7 — Notify and HALT

1. Update `progress.plan` to `step-7`.
2. Return summary to the router:
   - `status.yaml` — active plan ({N} tickets, {M} stages)
   - `deferred.yaml` — tickets requiring manual work
   - `questions.md` — open questions
