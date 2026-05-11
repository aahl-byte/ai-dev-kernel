#!/usr/bin/env python3
"""Print the spec tree from specs/ directory."""

import os
import re
import sys
from pathlib import Path


def parse_frontmatter(path: Path) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    text = path.read_text()
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}

    fm = {}
    for line in match.group(1).splitlines():
        # Simple key: value parsing (handles strings, lists inline)
        m = re.match(r"^(\w+):\s*(.+)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith("[") and val.endswith("]"):
                fm[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
            elif val == "null" or val == "~":
                fm[key] = None
            else:
                fm[key] = val.strip("'\"")

    # Handle multi-line lists (children, sources, tags)
    in_list = None
    items = []
    for line in match.group(1).splitlines():
        if re.match(r"^(\w+):$", line):
            if in_list and items:
                fm[in_list] = items
            in_list = re.match(r"^(\w+):$", line).group(1)
            items = []
        elif in_list and line.strip().startswith("- "):
            items.append(line.strip()[2:].strip("'\""))
        elif not line.startswith(" ") and not line.startswith("\t"):
            if in_list and items:
                fm[in_list] = items
            in_list = None
            items = []
    if in_list and items:
        fm[in_list] = items

    return fm


def build_tree(specs_dir: Path) -> None:
    """Build and print the spec tree."""
    if not specs_dir.exists():
        print("No specs/ directory found.", file=sys.stderr)
        sys.exit(1)

    specs = {}
    for f in sorted(specs_dir.glob("*.md")):
        fm = parse_frontmatter(f)
        if fm:
            specs[f.name] = fm

    if not specs:
        print("No spec files found in specs/.", file=sys.stderr)
        sys.exit(1)

    # Find roots (parent: null)
    roots = [name for name, fm in specs.items() if fm.get("parent") is None]

    # Print tree
    print("Spec Tree")
    print("=========")

    def print_node(name: str, prefix: str = "", is_last: bool = True):
        fm = specs.get(name, {})
        connector = "└── " if prefix else ""
        if prefix:
            connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{name}")

        children = fm.get("children", [])
        if isinstance(children, str):
            children = [children]

        child_prefix = prefix + ("    " if is_last or not prefix else "│   ")
        for i, child in enumerate(children):
            if child in specs:
                print_node(child, child_prefix, i == len(children) - 1)

    for i, root in enumerate(roots):
        print_node(root, "", i == len(roots) - 1)

    # Print details
    print("\nSpec Details")
    print("============")
    for name, fm in specs.items():
        print(f"\n{name}")
        for key in ["title", "summary", "intent", "parent", "children", "sources", "tags", "context"]:
            val = fm.get(key)
            if val is not None:
                if isinstance(val, list):
                    print(f"  {key}: {', '.join(val)}")
                else:
                    print(f"  {key}: {val}")


if __name__ == "__main__":
    specs_dir = Path("specs")

    if "--json" in sys.argv:
        import json
        specs = {}
        for f in sorted(specs_dir.glob("*.md")):
            fm = parse_frontmatter(f)
            if fm:
                specs[f.name] = fm
        print(json.dumps(specs, indent=2))
    else:
        build_tree(specs_dir)
