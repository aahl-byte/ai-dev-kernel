---
title: Status YAML Template
summary: Structure and conventions for status.yaml control files — stages, tickets, priorities, risk levels, and validation tracking.
intent: >
  When large initiatives are broken into stages and executed by AI orchestrator
  sessions, there must be a standard structure for defining stages, tickets,
  priorities, and dependencies. This template provides a canonical schema.
parent: DK_PIPELINE.md
children: []
sources: []
tags:
  - pipeline
  - template
  - schema
---

# Status YAML Template

> Canonical schema for status.yaml initiative control files.

---

## Top-Level Structure

```yaml
name: "{initiative-name}"
description: >
  {One paragraph describing the initiative}
total_tickets: {N}
estimated_effort_days: {N}
created: "YYYY-MM-DD"

stages:
  - id: "stage-1"
    name: "{Stage Name}"
    description: >
      {What this stage accomplishes}
    priority: {1-5, where 1 is highest}
    effort: "{estimated days}"
    risk: "low" | "medium" | "high"
    depends_on: []  # stage IDs this depends on
    tickets:
      - id: "1.1"
        title: "{Ticket title}"
        effort: "S" | "M" | "L"
        key_files:
          - {file path}
        notes: >
          {Implementation context. Reference domain and design decision.}
```

---

## Conventions

### Stage Ordering
1. Bugs first (foundational stability)
2. Refactors second (clean foundation)
3. Features last (build on stable code)

Within priority tiers, order by dependency.

### Ticket Sizing
- **S** — under 1 hour, single file, straightforward
- **M** — 1-4 hours, multiple files, some complexity
- **L** — 4+ hours, cross-cutting, significant complexity

### Risk Levels
- **low** — well-understood changes, minimal blast radius
- **medium** — some unknowns, moderate blast radius
- **high** — significant unknowns, wide blast radius, or critical path

### Stage Limits
- Max 10 tickets per stage
- If a domain produces more than 10, split into multiple stages

### Completion Tracking

After execution, stages gain these fields:

```yaml
    status: "done" | "blocked"
    completed: "YYYY-MM-DD"
    commit: "{short SHA}"
    validation: "tmp/validations/{batch-id}-v{N}/ — {CLEAN|FINDINGS}"
```

---

## Deferred Tickets (deferred.yaml)

Tickets removed during triage. Grouped by deferral reason:

```yaml
deferred_stages:
  - id: "deferred-{slug}"
    name: "{Descriptive Name}"
    description: >
      {Why deferred and what unblocks it}
    tickets:
      - id: "D1.1"
        title: "{title}"
        effort: "S" | "M" | "L"
        key_files: [...]
        notes: >
          {context}
        prerequisite: "{what must happen first}"
```
