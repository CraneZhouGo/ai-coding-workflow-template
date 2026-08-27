#!/usr/bin/env python3
"""校验 V3.2.1 可组合运行时及内容可复现的发行包。"""

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
        "docs/design/v3-composable.md",
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
        "docs/design/v3-adaptive.md",
    )
    for relative in obsolete_files:
        if (ROOT / relative).exists():
            errors.append(f"obsolete component remains: {relative}")

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
        "V3.2.1 Composable",
        "Intent → Task Type → Risk Mode → Specialized Gates → Ordered Execution",
        "Core Spine + Task Method + Risk Safeguards + Specialized Gates",
        "Fast",
        "Standard",
        "Governed",
        "Superpowers",
        "OpenSpec",
        "Plannotator",
        "Route Card",
        "workflow-state.yaml",
        "feature",
        "bug",
        "refactor",
        "upgrade-config",
        "migration-infrastructure",
        "maintenance",
        "data",
        "security",
        "contract",
        "infrastructure",
        "release",
        "observability",
        "Integration Adapter Contract",
        "返回父 Router",
        "/opsx:apply <change-id>",
        "openspec-apply-change",
        "openspec instructions apply --change <change-id> --json",
        "Change Review Packet",
        "tool_input.plan",
        "SHA-256",
    )
    for term in required_terms:
        if term not in runtime:
            errors.append(f"runtime missing required Composable term: {term}")

    stale_terms = (
        "V2.2 Balanced",
        "V3.1 Adaptive",
        "score: n/33",
        "tasks.jsonl",
        "metrics-schema",
        "S1 REQUIRED — superpowers:brainstorming",
        "Standard state machine",
        "workspace-and-openspec:apply",
        "S-EX1 REQUIRED — superpowers:executing-plans",
    )
    for term in stale_terms:
        if term in runtime:
            errors.append(f"runtime contains stale fixed-workflow term: {term}")

    routing = (ROOT / ".claude/skills/workflow-router/ROUTING.md").read_text(encoding="utf-8")
    for rule in ("any trigger is enough", "every condition must hold", "the default"):
        if rule not in routing:
            errors.append(f"routing decision rule missing: {rule}")

    playbooks = (ROOT / ".claude/skills/workflow-router/PLAYBOOKS.md").read_text(encoding="utf-8")
    core_nodes = [f"C{index} REQUIRED" for index in range(1, 8)]
    positions = [playbooks.find(node) for node in core_nodes]
    for node, position in zip(core_nodes, positions):
        if position < 0:
            errors.append(f"Core Spine node missing: {node}")
    if all(position >= 0 for position in positions) and positions != sorted(positions):
        errors.append("Core Spine nodes are not in execution order")

    for node in (
        "M-FE1 REQUIRED — superpowers:brainstorming",
        "M-BU1 REQUIRED — superpowers:systematic-debugging",
        "M-BU3 REQUIRED — failing-regression-test",
        "M-RE1 REQUIRED — behavior-baseline",
        "M-UP1 REQUIRED — changelog-release-note-analysis",
        "M-MI1 REQUIRED — impact-and-rollback-plan",
        "M-MA1 REQUIRED — focused-exploration",
        "S-HG1 HUMAN GATE — plannotator-plan-review",
        "S-RP1 REQUIRED — complete-change-review-packet",
        "S-IM1 REQUIRED — openspec-implementation-entry",
        "G-HG1 HUMAN GATE — plannotator-code-review",
    ):
        if node not in playbooks:
            errors.append(f"composable orchestration node missing: {node}")

    if "Standard：只有 1 个预定人工 Gate" not in playbooks:
        errors.append("Standard must declare exactly one planned human gate")
    standard = playbooks.split("### Standard safeguards", 1)[-1].split("### Governed safeguards", 1)[0]
    if standard.count("HUMAN GATE") != 1:
        errors.append("Standard safeguards must contain exactly one HUMAN GATE")

    state_terms = (
        "schema_version: 1",
        "current_node:",
        "status: active",
        "pending | in_progress | done | N/A | blocked",
        "done 节点不重复",
        "openspec validate <change-id>",
        "plan_review.status",
        "sha256:",
        "status completed → `openspec archive <change-id>`",
    )
    for term in state_terms:
        if term not in playbooks:
            errors.append(f"durable state contract missing: {term}")

    profile = (ROOT / ".claude/project-profile.yaml").read_text(encoding="utf-8")
    if re.search(r"^version:\s*3\.2\.1\s*$", profile, re.MULTILINE) is None:
        errors.append("project profile version must be 3.2.1")
    for key in (
        "allow_fast_mode",
        "openspec_from",
        "plannotator_plan_review_from",
        "plannotator_code_review_from",
        "persist_from",
        "file_name",
        "resume_incomplete",
        "rollback",
        "observability",
        "deployment_strategy",
        "public_contract_locations",
        "route_requires_confirmation",
        "internal_steps_require_confirmation",
        "openspec_lifecycle_authorized",
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
    if manifest.get("version") != "3.2.1-composable":
        errors.append("distribution version must be 3.2.1-composable")
    included = set(manifest.get("include", []))
    if included != RUNTIME_FILES:
        errors.append("distribution must contain exactly the six Composable runtime files")
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
            errors.append("archive content does not match Composable manifest")
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
    print("V3.2.1 Composable workflow validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
