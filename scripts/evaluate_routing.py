#!/usr/bin/env python3
"""运行 V3.2 可组合路由器的维护校准案例。"""

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
GATE_FACTS = {
    "data": "data_gate",
    "security": "security_gate",
    "contract": "contract_gate",
    "infrastructure": "infrastructure_gate",
    "release": "release_gate",
    "observability": "observability_gate",
}


def classify_intent(facts: dict[str, bool]) -> str:
    """识别用户的授权意图；明确要求实施时，以修改意图为准。"""
    if facts.get("requested_change", False):
        return "change"
    if facts.get("requested_plan", False):
        return "plan-only"
    if facts.get("requested_diagnosis", False):
        return "diagnose-only"
    if facts.get("requested_review", False):
        return "review"
    return "explain"


def classify_task_type(facts: dict[str, bool]) -> str | None:
    """独立于风险模式，选择任务的主要方法类型。"""
    if facts.get("migration_or_infrastructure", False):
        return "migration-infrastructure"
    if facts.get("bug_or_failure", False):
        return "bug"
    if facts.get("refactor_only", False):
        return "refactor"
    if facts.get("upgrade_or_configuration", False):
        return "upgrade-config"
    if facts.get("maintenance_only", False):
        return "maintenance"
    if facts.get("feature_or_behavior", False) or facts.get("requested_change", False):
        return "feature"
    return None


def route(facts: dict[str, bool]) -> str:
    """为修改类任务选择风险模式；调用方必须先识别用户意图。"""
    if any(facts.get(name, False) for name in GOVERNED_FACTS):
        return "governed"
    if all(facts.get(name, False) for name in FAST_FACTS):
        return "fast"
    return "standard"


def route_mode(facts: dict[str, bool]) -> str | None:
    if classify_intent(facts) != "change":
        return None
    return route(facts)


def classify_specialized_gates(facts: dict[str, bool]) -> list[str]:
    """按照稳定的执行顺序返回需要启用的专项 Gate。"""
    return [gate for gate, signal in GATE_FACTS.items() if facts.get(signal, False)]


def evaluate(path: Path) -> list[str]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    failures: list[str] = []
    for case in cases:
        facts = case["facts"]
        actual = {
            "intent": classify_intent(facts),
            "task_type": classify_task_type(facts),
            "mode": route_mode(facts),
            "gates": classify_specialized_gates(facts),
        }
        for field in ("intent", "task_type", "mode", "gates"):
            expected = case.get(f"expected_{field}", [] if field == "gates" else None)
            if actual[field] != expected:
                failures.append(
                    f"{case['id']} {field}: expected {expected!r}, got {actual[field]!r}"
                )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=ROOT / "evals/routing-cases.json")
    args = parser.parse_args()
    failures = evaluate(args.cases)
    if failures:
        print("composable routing evaluation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    count = len(json.loads(args.cases.read_text(encoding="utf-8")))
    print(f"composable routing evaluation passed: {count} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
