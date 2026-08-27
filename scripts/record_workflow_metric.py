#!/usr/bin/env python3
"""Validate and append one workflow metric record to JSONL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / ".claude/skills/workflow-router/v2/metrics-schema.json"
DIMENSIONS = {
    "scope", "business", "code_impact", "architecture",
    "data", "infrastructure", "runtime_risk",
}
TIERS = {"R1", "R2", "R3", "R4"}


def validate_record(record: object) -> list[str]:
    if not isinstance(record, dict):
        return ["record must be a JSON object"]
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = [f"missing required field: {key}" for key in schema["required"] if key not in record]
    if errors:
        return errors
    if record["schema_version"] != 1:
        errors.append("schema_version must be 1")
    for field in ("timestamp", "task_id", "task_summary"):
        if not isinstance(record[field], str) or not record[field].strip():
            errors.append(f"{field} must be a non-empty string")
    if record["outcome"] not in {"completed", "blocked"}:
        errors.append("outcome must be completed or blocked")
    for field in ("initial_tier", "final_tier"):
        if record[field] not in TIERS:
            errors.append(f"{field} must be R1, R2, R3 or R4")
    for field in ("initial_score", "final_score"):
        value = record[field]
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 36:
            errors.append(f"{field} must be an integer in 0..36")
    dimensions = record["dimensions"]
    if not isinstance(dimensions, dict) or set(dimensions) != DIMENSIONS:
        errors.append("dimensions must contain exactly the 7 v2.1 dimensions")
    elif any(not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 3 for value in dimensions.values()):
        errors.append("dimension values must be integers in 0..3")
    for field in ("semantic_red_flags", "required_gates", "capability_degradations", "tests"):
        if not isinstance(record[field], list):
            errors.append(f"{field} must be an array")
    delivery = record["delivery_profile"]
    expected_delivery = {"agents", "worktrees", "rollout", "ownership"}
    if not isinstance(delivery, dict) or set(delivery) != expected_delivery:
        errors.append("delivery_profile must contain agents, worktrees, rollout and ownership")
    else:
        allowed_delivery = {
            "agents": {"1", "2+"},
            "worktrees": {"none", "optional", "required"},
            "rollout": {"none", "standard", "coordinated"},
            "ownership": {"single", "multi-team"},
        }
        for field, allowed in allowed_delivery.items():
            if delivery[field] not in allowed:
                errors.append(f"delivery_profile.{field} has an invalid value")
    for field in ("changed_files", "changed_modules", "plan_review_rounds", "duration_minutes", "human_wait_minutes"):
        value = record[field]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"{field} must be a non-negative integer")
    if not isinstance(record["rework"], bool):
        errors.append("rework must be boolean")
    findings = record["code_review_findings"]
    finding_keys = {"critical", "high", "medium", "low"}
    if not isinstance(findings, dict) or set(findings) != finding_keys:
        errors.append("code_review_findings must contain critical, high, medium and low")
    elif any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in findings.values()):
        errors.append("code_review_findings values must be non-negative integers")
    if not (isinstance(record["escaped_defect"], bool) or record["escaped_defect"] is None):
        errors.append("escaped_defect must be true, false or null")
    return errors


def append_record(record: dict, metrics_path: Path) -> None:
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", type=Path, help="JSON file; omit to read one object from stdin")
    parser.add_argument("--metrics", type=Path, default=Path(".claude/workflow-metrics/tasks.jsonl"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        if args.record:
            record = json.loads(args.record.read_text(encoding="utf-8"))
        else:
            record = json.load(sys.stdin)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"unable to read metric record: {exc}", file=sys.stderr)
        return 1
    errors = validate_record(record)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    if args.dry_run:
        print("metric record is valid")
    else:
        append_record(record, args.metrics)
        print(f"appended metric record to {args.metrics}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
