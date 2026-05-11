---
name: manage-specs
description: Audit and maintain spec files in specs/. Use when source files have changed and specs may be stale, when creating new specs, or when the spec tree needs restructuring.
argument-hint: "[tag or 'create' or blank for full audit]"
---

# Manage Specs

You are a spec maintenance agent.

## Spec Tree Structure

The spec tree has two roots:

- **`INTENT.md`** (`parent: null`) — product philosophy, the "what and why". Standalone.
- **`ARCHITECTURE.md`** (`parent: null`) — technical overview, the "how". Parent of all technical specs.

All technical specs should be children of ARCHITECTURE.md or its descendants.

## Default Behavior (Full Audit)

When invoked without arguments:

1. List the current spec tree (scan `specs/` for frontmatter)
2. Find recently changed source files via `git log`
3. For each spec, check if its `sources` files have been modified more recently
4. Read stale specs and their changed source files
5. Update spec content and frontmatter
6. Commit changes

## Creating New Specs

1. Choose the right parent
2. Scaffold with proper frontmatter
3. Write an `intent` field (1-5 sentences)
4. Populate content from source files
5. Update the parent's `children` field
6. Commit

## Frontmatter Schema

```yaml
---
title: <string, required>
summary: <string, required — one sentence>
intent: <string, required — 1-5 sentences: why does this exist?>
parent: <filename or null>
children: <list of filenames, may be empty>
sources: <list of source file paths/globs>
tags: <list of tags>
context: <string, optional — cross-spec coordination notes>
---
```

## Rules

1. **Max 400 lines per spec** — split into children if exceeding
2. **Single-topic ownership** — one spec owns each topic, cross-reference others
3. **No mirroring source code** — reference paths, describe contracts
4. **Bidirectional parent/children** — must be consistent
5. **Tags are lowercase, hyphenated**
6. **Intent required** on all detail specs
7. **Filenames: SCREAMING_SNAKE_CASE.md**

## What Specs Should Contain

- Design intent and "why" decisions
- Contracts between components
- Constraints (security, performance, compatibility)
- Non-obvious behavior and gotchas

## What Specs Should NOT Contain

- Implementation details obvious from code
- Copy-pasted type definitions
- Line-by-line walkthroughs
- Speculative/planned features
