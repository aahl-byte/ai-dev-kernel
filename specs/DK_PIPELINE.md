---
title: Dev-Kernel Pipeline
summary: End-to-end AI orchestration pipeline — conversational vision exploration, deep-dive design sessions, implementation planning, human review, and serial stage execution via specialized skills routed through /dk.
intent: >
  Large initiatives spanning many files and domains cannot be designed or
  implemented reliably in a single agent session. The dev-kernel pipeline
  addresses this with isolated skills: dk (router), dk-vision (vision building),
  dk-design (deep dives), dk-plan (implementation planning), dk-review (plan
  review), dk-batch (execution), and dk-orchestrator (per-stage tickets).
  File-based state enables crash recovery and cross-session handoff.
parent: ARCHITECTURE.md
children:
  - DK_TEMPLATE.md
sources:
  - .claude/skills/dk/**
  - .claude/skills/dk-vision/**
  - .claude/skills/dk-design/**
  - .claude/skills/dk-plan/**
  - .claude/skills/dk-review/**
  - .claude/skills/dk-batch/**
  - .claude/skills/dk-orchestrator/**
tags:
  - pipeline
  - orchestration
  - process
  - ai-agents
context: >
  DK_TEMPLATE.md defines the status.yaml schema. The /dk router is the only
  skill users invoke directly. Fresh terminals (bun dk:launch) isolate context
  between conversational phases.
---

# Dev-Kernel Pipeline

> End-to-end AI orchestration — from vague idea to implemented code through specialized, context-isolated skills.

---

## Overview

```
/dk (router — reads state, invokes the right skill)
  │
  ├── dk-vision (conversational — builds vision with user)
  │     → vision.md + dive-tracker.yaml
  │
  ├── dk-design (conversational — deep dives per area)
  │     → dives/{area-slug}.md
  │
  ├── dk-vision again (consolidation)
  │     → design.md
  │
  ├── dk-plan (automated — domain-driven planning)
  │     → status.yaml + deferred.yaml + questions.md
  │
  ├── dk-review (conversational — plan review with user)
  │     → approved status.yaml
  │
  └── dk-batch (automated — serial stage execution)
        → stages via dk-orchestrator
```

**Principles:**
- Conversational skills interact with the user; automated skills delegate to sub-agents.
- All state is file-based — crash recovery works via progress markers on disk.
- Each skill has isolated context — no skill carries another's prompt weight.
- Fresh terminals (`bun dk:launch`) give conversational phases clean context windows.

---

## Router (`/dk`)

| State | Action |
|-------|--------|
| No initiative | → `/dk-vision` (new) |
| Tracker: `exploring` | → `/dk-vision` (resume) |
| Tracker: `diving` | → `/dk-design` (ask which area) |
| Tracker: `consolidating` | → `/dk-vision` (consolidation) |
| Tracker: `ready`, no progress.plan | → `/dk-plan` |
| progress.plan < step-7 | → `/dk-plan` (resume) |
| progress.plan = step-7, no review | → `/dk-review` |
| progress.review = in-review | → `/dk-review` (resume) |
| progress.review = review-finalized | → `/dk-batch` |
| All stages done | → report completion |

---

## Phase Details

### Vision (`dk-vision`)
Conversational. Five layers: goal, scope, current state, behaviors, area identification. Produces vision.md + dive-tracker.yaml. After all dives complete, consolidates into design.md.

### Design (`dk-design`)
Conversational. Deep-dives one area. Adapts to type (UX, data/logic, integration). Mandatory review gate. Flags vision revisions.

### Plan (`dk-plan`)
Automated. 7-step pipeline: classify → architect → review → revise → assemble → triage → notify. Produces status.yaml with staged tickets.

### Review (`dk-review`)
Conversational. Presents plan, allows modifications, requires explicit approval.

### Batch (`dk-batch`)
Automated. Executes stages serially via dk-orchestrator. Adaptive retry/halt gates.

---

## Crash Recovery

| File | Values |
|------|--------|
| `dive-tracker.yaml` | `exploring`, `diving`, `consolidating`, `ready` |
| `progress.plan` | `step-1` through `step-7` |
| `progress.review` | `in-review`, `review-finalized`, `cancelled` |
| `status.yaml` stages | `done`, `blocked` |

---

## Directory Layout

```
tmp/initiatives/{name}/
├── vision.md
├── dive-tracker.yaml
├── design.md
├── cross-alignment-report.md
├── dives/{area-slug}.md
├── classification.md
├── designs/{domain-slug}.md
├── specs/{domain-slug}.md
├── status.yaml
├── deferred.yaml
├── questions.md
├── progress.plan
└── progress.review
```
