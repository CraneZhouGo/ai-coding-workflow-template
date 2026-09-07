#!/usr/bin/env python3
"""校验 V3.3 确定性可组合运行时及可复现发行包。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = {
    ".claude/project-profile.yaml",
    ".claude/scripts/workflow-runtime.mjs",
    ".claude/workflow-state.schema.json",
    ".claude/hooks/workflow-hooks.json",
    ".claude/workflow-runs/.gitignore",
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

    for relative in (
        ".claude/commands/new-task.md",
        ".claude/commands/workflow-report.md",
        ".claude/skills/workflow-router/WORKFLOWS.md",
        "scripts/record_workflow_metric.py",
        "scripts/workflow_report.py",
        "docs/design/v3-adaptive.md",
    ):
        if (ROOT / relative).exists():
            errors.append(f"obsolete component remains: {relative}")


def validate_json_and_javascript(errors: list[str]) -> None:
    for relative in (
        "distribution-manifest.json",
        "evals/routing-cases.json",
        ".claude/workflow-state.schema.json",
        ".claude/hooks/workflow-hooks.json",
    ):
        try:
            json.loads((ROOT / relative).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON {relative}: {exc}")

    checked = subprocess.run(
        ["node", "--check", str(ROOT / ".claude/scripts/workflow-runtime.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if checked.returncode != 0:
        errors.append(f"invalid workflow runtime JavaScript: {checked.stderr.strip()}")


def validate_content(errors: list[str]) -> None:
    runtime = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in sorted(RUNTIME_FILES))
    for term in (
        "V3.3",
        "Intent → Task Type → Risk Mode → Specialized Gates → Ordered Execution",
        "Core Spine + Task Method + Risk Safeguards + Specialized Gates",
        "Fast",
        "Standard",
        "Governed",
        "Superpowers",
        "OpenSpec",
        "Plannotator",
        "route_fingerprint",
        "workflow_hash",
        "workflow-state.json",
        "planning_depth",
        "validation_scope",
        "execution_strategy",
        "M-FE1 REQUIRED — superpowers:brainstorming",
        "S-HG1 HUMAN GATE — plannotator-spec-diff-review",
        "G-HG1 HUMAN GATE — plannotator-code-diff-review",
        "/opsx:apply <change-id>",
        "openspec instructions apply --change <change-id> --json",
        "uncommitted",
        "since-base",
        "archive-complete",
        "PreToolUse",
        "PreCompact",
        "Stop",
    ):
        if term not in runtime:
            errors.append(f"runtime missing required deterministic contract: {term}")

    for term in (
        "workflow-state.yaml",
        "schema_version: 1",
        "state completed → archive",
        "V3.1 Adaptive",
        "S-RP1 REQUIRED — complete-change-review-packet",
        "P-RP4 REQUIRED — render-full-packet",
        "S-HG1 HUMAN GATE — plannotator-plan-review",
    ):
        if term in runtime:
            errors.append(f"runtime contains stale workflow contract: {term}")

    routing = (ROOT / ".claude/skills/workflow-router/ROUTING.md").read_text(encoding="utf-8")
    for rule in ("any trigger is enough", "every condition must hold", "the default"):
        if rule not in routing:
            errors.append(f"routing decision rule missing: {rule}")

    playbooks = (ROOT / ".claude/skills/workflow-router/PLAYBOOKS.md").read_text(encoding="utf-8")
    positions = [playbooks.find(f"C{index} REQUIRED") for index in range(1, 8)]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        errors.append("Core Spine C1-C7 is missing or out of order")
    standard = playbooks.split("### Standard safeguards", 1)[-1].split("### Governed safeguards", 1)[0]
    if standard.count("HUMAN GATE") != 1:
        errors.append("Standard safeguards must contain exactly one HUMAN GATE")

    profile = (ROOT / ".claude/project-profile.yaml").read_text(encoding="utf-8")
    if re.search(r"^version:\s*3\.3\.0\s*$", profile, re.MULTILINE) is None:
        errors.append("project profile version must be 3.3.0")
    for key in (
        "profile_status",
        "feature_min_mode",
        "planning_depth",
        "validation_scope",
        "isolation",
        "review_policy",
        "execution_strategy",
        "persist_from",
        "schema",
        "fast_directory",
        "hooks_installed",
        "resume_incomplete",
    ):
        if re.search(rf"^\s*{re.escape(key)}\s*:", profile, re.MULTILINE) is None:
            errors.append(f"project profile missing key: {key}")


def validate_references(errors: list[str]) -> None:
    sources = [ROOT / path for path in RUNTIME_FILES if path.endswith(".md")]
    pattern = re.compile(r"`([^`\n]+\.(?:md|yaml|json|mjs))`")
    for source in sources:
        for reference in pattern.findall(source.read_text(encoding="utf-8")):
            if "<" in reference or reference == ".claude/settings.json":
                continue
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
    if manifest.get("version") != "3.3.0-deterministic-composable":
        errors.append("distribution version must be 3.3.0-deterministic-composable")
    included = set(manifest.get("include", []))
    if included != RUNTIME_FILES:
        errors.append("distribution must contain exactly the declared V3.3 runtime files")
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
            errors.append("archive content does not match deterministic manifest")
        for name in actual & included:
            if archive.read(name) != (ROOT / name).read_bytes():
                errors.append(f"archive has stale content: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    validate_files(errors)
    validate_json_and_javascript(errors)
    validate_content(errors)
    validate_references(errors)
    validate_manifest(errors, args.archive)
    if errors:
        print("workflow validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("V3.3 deterministic composable workflow validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
