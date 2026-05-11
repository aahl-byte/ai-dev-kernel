# ai-dev-kernel

Project infrastructure, agent orchestration, and architecture design for Claude Code.

Takes a vague idea through to implemented code via a pipeline of specialized, context-isolated skills — each handling one phase of the lifecycle.

## What it does

```
/dk (type this — the router handles the rest)
  │
  ├── dk-vision    — conversational vision exploration with the user
  ├── dk-design    — focused deep-dive sessions per area
  ├── dk-plan      — automated domain-driven implementation planning
  ├── dk-review    — conversational plan review and approval
  └── dk-batch     — automated serial stage execution
```

**Key ideas:**
- One entry point (`/dk`) — the router reads file-based state and invokes the right skill
- Conversational phases get fresh terminal sessions for clean context
- Automated phases delegate to sub-agents
- Crash recovery via progress markers — resume where you left off across sessions
- Spec system for maintaining living architecture documentation

## Install

```bash
git clone https://github.com/aahl-byte/ai-dev-kernel.git /tmp/ai-dev-kernel
/tmp/ai-dev-kernel/init.sh /path/to/your/project
rm -rf /tmp/ai-dev-kernel
```

Or from within your project directory:

```bash
git clone https://github.com/aahl-byte/ai-dev-kernel.git /tmp/ai-dev-kernel
/tmp/ai-dev-kernel/init.sh .
```

### What gets installed

| Location | Contents |
|----------|----------|
| `.claude/skills/dk*/` | Pipeline skills (router, vision, design, plan, review, batch, orchestrator, validate) |
| `.claude/skills/manage-specs/` | Spec maintenance skill |
| `scripts/dk/launch.ts` | Fresh terminal launcher (macOS: Terminal.app, iTerm2, WezTerm) |
| `scripts/dk/validate.py` | status.yaml schema validator |
| `scripts/dk/ntfy.js` | Push notifications via ntfy.sh (set `NTFY_TOPIC` env var) |
| `scripts/spec-tree.py` | Spec tree viewer |
| `specs/` | Pipeline specs + scaffolded ARCHITECTURE.md and INTENT.md |

### Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Node.js / tsx (for launch script)
- Python 3 (for spec-tree)

## Usage

After installing, start Claude Code in your project and type:

```
/dk
```

The router will ask what you want to build and guide you through the pipeline.

### Pipeline phases

| Phase | Skill | Mode | What happens |
|-------|-------|------|-------------|
| Vision | dk-vision | Conversational | Explores the big picture — goal, scope, areas |
| Design | dk-design | Conversational | Deep-dives each area that needs detail |
| Plan | dk-plan | Automated | Breaks design into staged implementation tickets |
| Review | dk-review | Conversational | You review, modify, and approve the plan |
| Execute | dk-batch | Automated | Implements stages one at a time |

### Resuming

Just type `/dk` again. The router reads state from `tmp/initiatives/` and picks up where you left off — even across sessions.

### Fresh terminals

When transitioning between conversational phases, the router opens a new terminal with a clean Claude session. This prevents context window pollution from long conversations.

Requires `bun dk:launch` (added to package.json during init).

## Specs

The spec system maintains living documentation of your project's architecture. Two roots:

- `INTENT.md` — what the project is and why (product philosophy)
- `ARCHITECTURE.md` — how it works (technical overview, parent of all technical specs)

Run `python3 scripts/spec-tree.py` (or `bun specs:list` if configured) to view the tree.

Use `/manage-specs` to audit and update specs after code changes.

## Customization

After installing, you'll want to customize:

1. **`specs/INTENT.md`** — Your project's purpose and philosophy
2. **`specs/ARCHITECTURE.md`** — Your project's technical architecture
3. **`dk-plan` triage rules** — Add project-specific deferral signals (what work should be flagged for manual handling)
4. **`dk-validate` domains** — Configure validation domains to match your project's architecture
5. **`dk-orchestrator` conventions** — Add your project's type-check command, commit conventions, etc.

## File structure

```
tmp/initiatives/{name}/
├── vision.md              # Vision document
├── dive-tracker.yaml      # State machine
├── design.md              # Consolidated design
├── dives/{area}.md        # Deep dive documents
├── classification.md      # Domain classification
├── designs/{domain}.md    # Domain designs (with Review + Verdict)
├── specs/{domain}.md      # Condensed implementation specs
├── status.yaml            # Execution plan
├── deferred.yaml          # Deferred tickets
├── questions.md           # Open questions
├── progress.plan          # Planning progress marker
└── progress.review        # Review progress marker
```

## License

MIT
