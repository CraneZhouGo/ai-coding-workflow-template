#!/usr/bin/env python3
"""通过 V3.3 Node 运行时执行路由校准，避免维护第二套路由规则。"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".claude/scripts/workflow-runtime.mjs"


def route_decision(facts: dict[str, bool], *, profile_ready: bool = True) -> dict[str, Any]:
    """调用发行包中的唯一确定性 Router，返回完整路由结果。"""
    payload = json.dumps(
        {"facts": facts, "profile_ready": profile_ready},
        ensure_ascii=False,
    )
    result = subprocess.run(
        ["node", str(RUNTIME), "route", "--json", payload],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def classify_intent(facts: dict[str, bool]) -> str:
    """返回用户授权意图。"""
    return route_decision(facts)["route"]["intent"]


def classify_task_type(facts: dict[str, bool]) -> str | None:
    """返回任务主方法类型。"""
    return route_decision(facts)["route"]["task_type"]


def route(facts: dict[str, bool]) -> str:
    """按修改意图计算风险模式，保留维护脚本原有调用接口。"""
    change_facts = {**facts, "requested_change": True}
    return route_decision(change_facts)["route"]["mode"]


def route_mode(facts: dict[str, bool]) -> str | None:
    """仅 change 意图返回风险模式。"""
    return route_decision(facts)["route"]["mode"]


def classify_specialized_gates(facts: dict[str, bool]) -> list[str]:
    """按照稳定顺序返回专项 Gate。"""
    return route_decision(facts)["route"]["specialized_gates"]


def evaluate(path: Path) -> list[str]:
    """重放校准案例并检查同一输入的路由指纹稳定性。"""
    cases = json.loads(path.read_text(encoding="utf-8"))
    failures: list[str] = []
    for case in cases:
        result = route_decision(
            case["facts"],
            profile_ready=case.get("profile_ready", True),
        )
        actual = result["route"]
        for field in ("intent", "task_type", "mode", "specialized_gates"):
            expected_key = "expected_gates" if field == "specialized_gates" else f"expected_{field}"
            expected = case.get(expected_key, [] if field == "specialized_gates" else None)
            if actual[field] != expected:
                failures.append(
                    f"{case['id']} {field}: expected {expected!r}, got {actual[field]!r}"
                )

        replay = route_decision(
            case["facts"],
            profile_ready=case.get("profile_ready", True),
        )
        if replay["route_fingerprint"] != result["route_fingerprint"]:
            failures.append(f"{case['id']} route fingerprint is not deterministic")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=ROOT / "evals/routing-cases.json")
    args = parser.parse_args()
    failures = evaluate(args.cases)
    if failures:
        print("deterministic routing evaluation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    count = len(json.loads(args.cases.read_text(encoding="utf-8")))
    print(f"deterministic routing evaluation passed: {count} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
