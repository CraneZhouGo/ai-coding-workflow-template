#!/usr/bin/env python3
"""Validate the V3 Adaptive runtime and deterministic distribution."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = {
    ".claude/project-profile.yaml",
    ".claude/skills/new-task/SKILL.md",
    ".claude/skills/workflow-router/SKILL.md",
    ".claude/skills/workflow-router/ROUTING.md",
    ".claude/skills/workflow-router/PLAYBOOKS.md",
    "CLAUDE.md",
}


def validate_files(errors: list[str]) -> None:
    required = RUNTIME_FILES | {
        "distribution-manifest.json",
        "evals/routing-cases.json",
        "scripts/build_distribution.py",
        "scripts/evaluate_routing.py",
        "scripts/validate_workflow.py",
        "tests/test_workflow_tools.py",
        ".github/workflows/validate-workflow-template.yml",
        "docs/README.md",
        "docs/market-benchmark.md",
        "AI-Coding-Workflow-Template-详细使用说明.md",
    }
    for relative in sorted(required):
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    obsolete_files = (
        ".claude/commands/new-task.md",
        ".claude/commands/workflow-report.md",
        ".claude/skills/workflow-router/WORKFLOWS.md",
        "scripts/record_workflow_metric.py",
        "scripts/workflow_report.py",
    )
    for relative in obsolete_files:
        if (ROOT / relative).exists():
            errors.append(f"obsolete runtime component remains: {relative}")

    for relative in (
        ".claude/skills/workflow-router/gates",
        ".claude/skills/workflow-router/v2",
    ):
        path = ROOT / relative
        if path.exists() and any(item.is_file() for item in path.rglob("*")):
            errors.append(f"obsolete expanded workflow files remain under: {relative}")


def validate_content(errors: list[str]) -> None:
    runtime = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in sorted(RUNTIME_FILES))
    required_terms = (
        "V3 Adaptive", "Fast", "Standard", "Governed", "Superpowers",
        "OpenSpec", "Plannotator", "Route Card", "openspec validate",
    )
    for term in required_terms:
        if term not in runtime:
            errors.append(f"runtime missing required Adaptive term: {term}")

    stale_terms = (
        "V2.2 Balanced", "score: n/33", "0~4", "5~10", "11~20", "21~33",
        "tasks.jsonl", "metrics-schema", "workflow-report",
    )
    for term in stale_terms:
        if term in runtime:
            errors.append(f"runtime contains stale term: {term}")

    routing = (ROOT / ".claude/skills/workflow-router/ROUTING.md").read_text(encoding="utf-8")
    for rule in ("any trigger is enough", "every condition must hold", "the default"):
        if rule not in routing:
            errors.append(f"routing decision rule missing: {rule}")

    playbooks = (ROOT / ".claude/skills/workflow-router/PLAYBOOKS.md").read_text(encoding="utf-8")
    for node in ("探索与推理", "持久规格", "实现计划", "Plan Review", "实现", "验证", "Code Review", "收尾"):
        if node not in playbooks:
            errors.append(f"tool orchestration node missing: {node}")

    profile = (ROOT / ".claude/project-profile.yaml").read_text(encoding="utf-8")
    for key in (
        "allow_fast_mode", "openspec_from", "plannotator_plan_review_from",
        "plannotator_code_review_from", "rollback", "observability",
        "deployment_strategy", "public_contract_locations",
    ):
        if re.search(rf"^\s*{re.escape(key)}\s*:", profile, re.MULTILINE) is None:
            errors.append(f"project profile missing key: {key}")


def validate_references(errors: list[str]) -> None:
    sources = [ROOT / path for path in RUNTIME_FILES if path.endswith(".md")]
    pattern = re.compile(r"`([^`\n]+\.(?:md|yaml))`")
    for source in sources:
        for reference in pattern.findall(source.read_text(encoding="utf-8")):
            if reference.startswith(".claude/") or reference == "CLAUDE.md":
                target = ROOT / reference
            elif reference in {"ROUTING.md", "PLAYBOOKS.md"}:
                target = ROOT / ".claude/skills/workflow-router" / reference
            else:
                continue
            if not target.exists():
                errors.append(f"broken reference in {source.relative_to(ROOT)}: {reference}")


def validate_manifest(errors: list[str], archive_path: Path | None) -> None:
    manifest = json.loads((ROOT / "distribution-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("version") != "3.0-adaptive":
        errors.append("distribution version must be 3.0-adaptive")
    included = set(manifest.get("include", []))
    if included != RUNTIME_FILES:
        errors.append("distribution must contain exactly the six Adaptive runtime files")
    if any(path.startswith(("scripts/", "tests/", "evals/")) for path in included):
        errors.append("business distribution must not include maintainer tooling")

    if archive_path is None:
        return
    if not archive_path.exists():
        errors.append(f"archive does not exist: {archive_path}")
        return
    with ZipFile(archive_path) as archive:
        actual = {name for name in archive.namelist() if not name.endswith("/")}
        if actual != included:
            errors.append("archive content does not match Adaptive manifest")
        for name in actual & included:
            if archive.read(name) != (ROOT / name).read_bytes():
                errors.append(f"archive has stale content: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    validate_files(errors)
    validate_content(errors)
    validate_references(errors)
    validate_manifest(errors, args.archive)
    if errors:
        print("workflow validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("V3 Adaptive workflow validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
