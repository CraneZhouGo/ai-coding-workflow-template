#!/usr/bin/env python3
"""Run the routing policy's maintainer calibration cases.

This evaluator is intentionally excluded from the business distribution. It
protects the template policy from accidental drift; the coding agent still
routes from repository evidence rather than asking users to fill a form.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOVERNED_FACTS = {
    "critical_semantics_changed",
    "incompatible_public_contract",
    "coordinated_release",
    "schema_migration",
    "data_backfill",
    "global_security_or_infrastructure",
    "no_credible_rollback",
    "cross_repo_release_ordering",
    "unbounded_impact",
    "critical_validation_unavailable",
}
FAST_FACTS = {
    "clear_acceptance",
    "localized_change",
    "consumers_known",
    "no_boundary_change",
    "easy_rollback",
    "direct_validation",
    "no_design_tradeoff",
}


def route(facts: dict[str, bool]) -> str:
    if any(facts.get(name, False) for name in GOVERNED_FACTS):
        return "governed"
    if all(facts.get(name, False) for name in FAST_FACTS):
        return "fast"
    return "standard"


def evaluate(path: Path) -> list[str]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    failures: list[str] = []
    for case in cases:
        actual = route(case["facts"])
        if actual != case["expected_mode"]:
            failures.append(f"{case['id']}: expected {case['expected_mode']}, got {actual}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=ROOT / "evals/routing-cases.json")
    args = parser.parse_args()
    failures = evaluate(args.cases)
    if failures:
        print("routing evaluation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    count = len(json.loads(args.cases.read_text(encoding="utf-8")))
    print(f"routing evaluation passed: {count} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
