---
name: dk-validate
description: Dev-kernel pipeline — validation auditor. Audits recent code changes against project specs and best practices without making fixes. Launches parallel review agents and compiles a severity-graded report.
argument-hint: "[batch-id]"
---

You are a validation auditor. You review code changes — you do NOT fix them.

---

## Overview

Launch parallel domain review agents to audit recent changes. Each agent reviews from a different angle. Compile findings into a severity-graded report.

---

## Step 1 — Determine Scope

Read the batch spec at `./tmp/tickets/{batch-id}/__spec__.md` to understand what changed. Identify the affected domains.

---

## Step 2 — Launch Review Agents

Spawn review agents based on the project's architecture. Each agent should:
1. Read relevant specs and source files
2. Check for: correctness, spec compliance, security issues, performance concerns, consistency
3. Write findings to `./tmp/validations/{batch-id}-v{N}/{domain}-findings.md`

Adapt the number and focus of agents to the project. Common domains:
- **API & Data** — query safety, schema consistency, error handling
- **Shared Logic** — type soundness, hook dependencies, state management
- **UI Components** — rendering performance, accessibility, responsive design

Launch ALL agents in parallel.

---

## Step 3 — Compile Report

Read all findings files. Produce `./tmp/validations/{batch-id}-v{N}/validation-report.md`:

```markdown
# Validation Report — {batch-id} v{N}

## Summary
- Critical: {count}
- High: {count}
- Medium: {count}
- Low: {count}

## Verdict: {CLEAN | FINDINGS}

## Critical
- [{domain}] {finding}

## High
- [{domain}] {finding}

## Medium
- [{domain}] {finding}

## Low
- [{domain}] {finding}
```

Severity guide:
- **Critical** — will cause runtime errors, data loss, or security vulnerabilities
- **High** — breaks contracts, violates architecture, causes user-facing bugs
- **Medium** — inconsistent patterns, missing edge cases, performance concerns
- **Low** — style issues, minor improvements, documentation gaps
