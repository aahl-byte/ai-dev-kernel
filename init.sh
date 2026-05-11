#!/usr/bin/env bash
set -euo pipefail

# ai-dev-kernel initializer
# Installs the dk pipeline into the current project directory.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-.}"
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo "ai-dev-kernel — installing into: $TARGET_DIR"
echo ""

# --- Skills ---
echo "Installing skills..."
mkdir -p "$TARGET_DIR/.claude/skills"
for skill_dir in "$SCRIPT_DIR/skills"/*/; do
  skill_name="$(basename "$skill_dir")"
  mkdir -p "$TARGET_DIR/.claude/skills/$skill_name"
  cp "$skill_dir/SKILL.md" "$TARGET_DIR/.claude/skills/$skill_name/SKILL.md"
  echo "  ✓ $skill_name"
done

# --- Scripts ---
echo "Installing scripts..."
mkdir -p "$TARGET_DIR/scripts/dk"
cp "$SCRIPT_DIR/scripts/dk/launch.ts" "$TARGET_DIR/scripts/dk/launch.ts"
cp "$SCRIPT_DIR/scripts/dk/validate.py" "$TARGET_DIR/scripts/dk/validate.py"
cp "$SCRIPT_DIR/scripts/spec-tree.py" "$TARGET_DIR/scripts/spec-tree.py"
echo "  ✓ scripts/dk/launch.ts"
echo "  ✓ scripts/dk/validate.py"
echo "  ✓ scripts/spec-tree.py"

# --- Specs ---
echo "Installing specs..."
mkdir -p "$TARGET_DIR/specs"
for spec_file in "$SCRIPT_DIR/specs"/*.md; do
  spec_name="$(basename "$spec_file")"
  if [ ! -f "$TARGET_DIR/specs/$spec_name" ]; then
    cp "$spec_file" "$TARGET_DIR/specs/$spec_name"
    echo "  ✓ specs/$spec_name"
  else
    echo "  ⊘ specs/$spec_name (already exists, skipped)"
  fi
done

# --- Package.json scripts ---
if [ -f "$TARGET_DIR/package.json" ]; then
  echo "Checking package.json scripts..."

  # Check if dk:launch already exists
  if ! grep -q '"dk:launch"' "$TARGET_DIR/package.json"; then
    # Use node to safely inject scripts
    node -e "
      const fs = require('fs');
      const pkg = JSON.parse(fs.readFileSync('$TARGET_DIR/package.json', 'utf8'));
      pkg.scripts = pkg.scripts || {};
      pkg.scripts['dk:launch'] = 'tsx scripts/dk/launch.ts';
      pkg.scripts['dk:validate'] = 'python3 scripts/dk/validate.py';
      pkg.scripts['specs:list'] = pkg.scripts['specs:list'] || 'python3 scripts/spec-tree.py';
      fs.writeFileSync('$TARGET_DIR/package.json', JSON.stringify(pkg, null, 2) + '\n');
    "
    echo "  ✓ Added dk:launch and specs:list to package.json"
  else
    echo "  ⊘ dk:launch already in package.json"
  fi
else
  echo "No package.json found. Add these scripts manually:"
  echo '  "dk:launch": "tsx scripts/dk/launch.ts"'
  echo '  "specs:list": "python3 scripts/spec-tree.py"'
fi

# --- Scaffold base specs if empty ---
if [ ! -f "$TARGET_DIR/specs/ARCHITECTURE.md" ]; then
  cat > "$TARGET_DIR/specs/ARCHITECTURE.md" << 'SPEC'
---
title: Architecture
summary: Technical architecture overview.
intent: >
  TODO: Describe what this project is and how its parts fit together.
parent: null
children: []
sources: []
tags:
  - architecture
  - overview
---

# Architecture

> Technical architecture overview.

TODO: Document the high-level architecture of this project.
SPEC
  echo "  ✓ Scaffolded specs/ARCHITECTURE.md (fill in your architecture)"
fi

if [ ! -f "$TARGET_DIR/specs/INTENT.md" ]; then
  cat > "$TARGET_DIR/specs/INTENT.md" << 'SPEC'
---
title: Product Intent
summary: What this project is, why it exists, and who it's for.
intent: This document IS the intent.
parent: null
children: []
sources: []
tags:
  - intent
  - product
---

# Product Intent

> What this project is, why it exists, and who it's for.

TODO: Document your project's purpose and philosophy.
SPEC
  echo "  ✓ Scaffolded specs/INTENT.md (fill in your product intent)"
fi

# --- tmp directory ---
mkdir -p "$TARGET_DIR/tmp/initiatives"
if [ -f "$TARGET_DIR/.gitignore" ]; then
  if ! grep -q "tmp/" "$TARGET_DIR/.gitignore"; then
    echo "tmp/" >> "$TARGET_DIR/.gitignore"
    echo "  ✓ Added tmp/ to .gitignore"
  fi
fi

echo ""
echo "Done! Next steps:"
echo "  1. Fill in specs/INTENT.md and specs/ARCHITECTURE.md"
echo "  2. Run /dk to start your first initiative"
echo ""
