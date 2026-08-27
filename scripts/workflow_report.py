#!/usr/bin/env python3
"""Summarize AI Coding Workflow JSONL metrics using only the Python stdlib."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean


TIERS = ("R1", "R2", "R3", "R4")


def load_records(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.exists():
        return records
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            records.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
    return records


def percentage(part: int, total: int) -> str:
    return "n/a" if total == 0 else f"{part / total:.0%} ({part}/{total})"


def summarize(records: list[dict], minimum_samples: int) -> str:
    lines = ["Workflow Report", "===============", f"total tasks: {len(records)}"]
    if not records:
        lines.extend(["no metrics records found", "insufficient sample for tuning"])
        return "\n".join(lines)

    outcomes = Counter(record.get("outcome", "unknown") for record in records)
    lines.append("outcomes: " + ", ".join(f"{key}={value}" for key, value in sorted(outcomes.items())))

    matrix = Counter((record.get("initial_tier"), record.get("final_tier")) for record in records)
    lines.append("tier matrix (initial -> final):")
    for initial in TIERS:
        cells = [f"{final}={matrix[(initial, final)]}" for final in TIERS]
        lines.append(f"  {initial}: " + ", ".join(cells))

    tier_rank = {tier: index for index, tier in enumerate(TIERS)}
    upgraded = [
        record for record in records
        if tier_rank.get(record.get("final_tier"), -1) > tier_rank.get(record.get("initial_tier"), -1)
    ]
    lines.append(f"upgrade rate: {percentage(len(upgraded), len(records))}")

    lines.append("final tier outcomes:")
    by_tier: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        by_tier[record.get("final_tier", "unknown")].append(record)
    for tier in TIERS:
        tier_records = by_tier[tier]
        if not tier_records:
            lines.append(f"  {tier}: n=0")
            continue
        duration = mean(record.get("duration_minutes", 0) for record in tier_records)
        wait = mean(record.get("human_wait_minutes", 0) for record in tier_records)
        rework = sum(bool(record.get("rework")) for record in tier_records)
        lines.append(
            f"  {tier}: n={len(tier_records)}, avg_duration={duration:.0f}m, "
            f"avg_human_wait={wait:.0f}m, rework={percentage(rework, len(tier_records))}"
        )

    high_dimensions = Counter()
    red_flags = Counter()
    for record in upgraded:
        for name, score in record.get("dimensions", {}).items():
            if isinstance(score, int) and score >= 2:
                high_dimensions[name] += 1
        red_flags.update(record.get("semantic_red_flags", []))
    lines.append("upgrade signals:")
    lines.append("  high dimensions: " + (", ".join(f"{k}={v}" for k, v in high_dimensions.most_common()) or "none"))
    lines.append("  semantic red flags: " + (", ".join(f"{k}={v}" for k, v in red_flags.most_common()) or "none"))

    degradations = Counter()
    findings = Counter()
    for record in records:
        for item in record.get("capability_degradations", []):
            degradations[str(item.get("capability", "unknown"))] += 1
        findings.update(record.get("code_review_findings", {}))
    lines.append("capability degradations: " + (", ".join(f"{k}={v}" for k, v in degradations.most_common()) or "none"))
    lines.append("code review findings: " + ", ".join(f"{key}={findings[key]}" for key in ("critical", "high", "medium", "low")))

    known_defects = [record["escaped_defect"] for record in records if record.get("escaped_defect") is not None]
    escaped = sum(bool(value) for value in known_defects)
    lines.append(f"escaped defect rate: {percentage(escaped, len(known_defects))}")

    if len(records) < minimum_samples:
        lines.append(f"insufficient sample for tuning: {len(records)}/{minimum_samples}")
    else:
        lines.append("tuning is permitted; review tier matrix, upgrade signals and escaped defects before changing thresholds")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", type=Path, default=Path(".claude/workflow-metrics/tasks.jsonl"))
    parser.add_argument("--minimum-samples", type=int, default=20)
    args = parser.parse_args()
    print(summarize(load_records(args.metrics), args.minimum_samples))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
