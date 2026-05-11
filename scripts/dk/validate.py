#!/usr/bin/env python3
"""Validate a status.yaml file against the DK_TEMPLATE schema.

Usage:
  python3 scripts/dk/validate.py tmp/initiatives/my-project/status.yaml
  python3 scripts/dk/validate.py tmp/initiatives/my-project/status.yaml --verbose

Exit codes:
  0 = all checks pass
  1 = validation errors found
  2 = file not found or unparseable
"""

import sys
import re
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip3 install pyyaml")
    sys.exit(2)

# --- Schema constants ---

VALID_STATUSES = {"pending", "in_progress", "done", "blocked"}
VALID_EFFORTS = {"S", "M", "L"}
VALID_RISKS = {"low", "medium", "high"}

REQUIRED_TOP = {"name", "total_tickets", "stages"}
REQUIRED_STAGE = {"id", "name", "description", "priority", "effort", "risk", "tickets"}
REQUIRED_TICKET = {"id", "title", "effort", "key_files", "notes"}

TICKET_ID_RE = re.compile(r"^\d+\.\d+$")


def validate(path: str, verbose: bool = False) -> list[str]:
    """Return a list of error strings. Empty list = valid."""
    errors: list[str] = []
    warnings: list[str] = []

    filepath = Path(path)
    if not filepath.exists():
        return [f"File not found: {path}"]

    try:
        data = yaml.safe_load(filepath.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(data, dict):
        return ["Top-level value is not a mapping"]

    # --- Top-level fields ---
    for field in REQUIRED_TOP:
        if field not in data:
            errors.append(f"Missing top-level field: {field}")

    stages = data.get("stages")
    if not isinstance(stages, list):
        errors.append("'stages' is not a list")
        return errors

    # --- Stage-level validation ---
    stage_ids: set[str] = set()
    total_tickets = 0

    for i, stage in enumerate(stages):
        prefix = f"stages[{i}]"
        if not isinstance(stage, dict):
            errors.append(f"{prefix}: not a mapping")
            continue

        for field in REQUIRED_STAGE:
            if field not in stage:
                errors.append(f"{prefix}: missing field '{field}'")

        sid = stage.get("id", f"<unnamed-{i}>")
        prefix = f"{sid}"

        if sid in stage_ids:
            errors.append(f"{prefix}: duplicate stage id")
        stage_ids.add(sid)

        # Status enum (optional — only present after execution)
        if "status" in stage and stage["status"] not in VALID_STATUSES:
            errors.append(f"{prefix}: invalid status '{stage['status']}'")

        # Risk enum
        if "risk" in stage and stage["risk"] not in VALID_RISKS:
            errors.append(f"{prefix}: invalid risk '{stage['risk']}'")

        # depends_on references
        deps = stage.get("depends_on", [])
        if isinstance(deps, list):
            pass  # validated below after all stages collected

        # --- Ticket-level validation ---
        tickets = stage.get("tickets")
        if not isinstance(tickets, list):
            errors.append(f"{prefix}: 'tickets' is not a list")
            continue

        if len(tickets) > 10:
            warnings.append(f"{prefix}: {len(tickets)} tickets (guideline: ≤10)")

        total_tickets += len(tickets)
        ticket_ids: set[str] = set()

        for j, ticket in enumerate(tickets):
            tprefix = f"{prefix}/{ticket.get('id', f'ticket-{j}')}"
            if not isinstance(ticket, dict):
                errors.append(f"{tprefix}: not a mapping")
                continue

            for field in REQUIRED_TICKET:
                if field not in ticket:
                    errors.append(f"{tprefix}: missing field '{field}'")

            tid = ticket.get("id")
            if tid:
                tid_str = str(tid)
                if tid_str in ticket_ids:
                    errors.append(f"{tprefix}: duplicate ticket id")
                ticket_ids.add(tid_str)

                if not TICKET_ID_RE.match(tid_str):
                    warnings.append(f"{tprefix}: id '{tid}' doesn't match #.# format")

            # Effort enum
            if "effort" in ticket and ticket["effort"] not in VALID_EFFORTS:
                errors.append(f"{tprefix}: invalid effort '{ticket['effort']}'")

            # key_files should be a list
            kf = ticket.get("key_files")
            if kf is not None and not isinstance(kf, list):
                errors.append(f"{tprefix}: key_files is not a list")

            # notes should be a non-empty string
            notes = ticket.get("notes")
            if notes is not None and (not isinstance(notes, str) or len(notes.strip()) == 0):
                warnings.append(f"{tprefix}: notes is empty")

    # --- Cross-stage dependency validation ---
    for stage in stages:
        sid = stage.get("id", "?")
        for dep in stage.get("depends_on", []) or []:
            if dep not in stage_ids:
                errors.append(f"{sid}: depends_on references unknown stage '{dep}'")

    # --- Ticket count ---
    declared = data.get("total_tickets")
    if declared is not None and declared != total_tickets:
        errors.append(f"total_tickets mismatch: header says {declared}, counted {total_tickets}")

    # --- Output ---
    if verbose:
        print(f"Initiative: {data.get('name', '?')}")
        print(f"Stages: {len(stages)}")
        print(f"Tickets: {total_tickets} (declared: {declared})")
        for stage in stages:
            sid = stage.get("id", "?")
            tcount = len(stage.get("tickets", []))
            print(f"  {sid}: {stage.get('name', '?')} — {tcount} tickets [{stage.get('risk', '?')}]")
        print()

    if warnings and verbose:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")
        print()

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/dk/validate.py <path-to-status.yaml> [--verbose]")
        sys.exit(2)

    path = sys.argv[1]
    verbose = "--verbose" in sys.argv

    errors = validate(path, verbose=verbose)

    if errors:
        print(f"FAIL — {len(errors)} error(s):")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print("PASS — all checks passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
