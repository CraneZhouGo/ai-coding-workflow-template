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
CODEX_PLUGIN_ROOT = ROOT / "plugins/ai-coding-workflow"
CODEX_PLUGIN_FILES = {
    ".codex-plugin/plugin.json",
    "plugin.json",
    "hooks/hooks.json",
    "scripts/setup-check.mjs",
    "scripts/workflow-runtime.mjs",
    "assets/project-profile.yaml",
    "assets/workflow-state.schema.json",
    "skills/ai-coding-workflow/SKILL.md",
    "skills/ai-coding-workflow/agents/openai.yaml",
    "skills/ai-coding-workflow/references/ROUTING.md",
    "skills/ai-coding-workflow/references/PLAYBOOKS.md",
    "skills/ai-coding-workflow-setup/SKILL.md",
    "skills/ai-coding-workflow-setup/agents/openai.yaml",
}


def validate_files(errors: list[str]) -> None:
    required = RUNTIME_FILES | {
        ".agents/plugins/marketplace.json",
        "codex-distribution-manifest.json",
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
    required |= {f"plugins/ai-coding-workflow/{path}" for path in CODEX_PLUGIN_FILES}
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
    parsed: dict[str, object] = {}
    for relative in (
        "codex-distribution-manifest.json",
        "distribution-manifest.json",
        "evals/routing-cases.json",
        ".claude/workflow-state.schema.json",
        ".claude/hooks/workflow-hooks.json",
        ".agents/plugins/marketplace.json",
        "plugins/ai-coding-workflow/plugin.json",
        "plugins/ai-coding-workflow/.codex-plugin/plugin.json",
        "plugins/ai-coding-workflow/hooks/hooks.json",
        "plugins/ai-coding-workflow/assets/workflow-state.schema.json",
    ):
        try:
            parsed[relative] = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON {relative}: {exc}")

    hook_fragment = parsed.get(".claude/hooks/workflow-hooks.json", {})
    hook_events = set(hook_fragment.get("hooks", {})) if isinstance(hook_fragment, dict) else set()
    if hook_events != {"SessionStart", "PreToolUse", "Stop"}:
        errors.append("hook fragment must contain SessionStart, optional PreToolUse, and Stop only")

    codex_hooks = parsed.get("plugins/ai-coding-workflow/hooks/hooks.json", {})
    codex_hook_events = set(codex_hooks.get("hooks", {})) if isinstance(codex_hooks, dict) else set()
    if codex_hook_events != {"SessionStart", "PreToolUse", "Stop"}:
        errors.append("Codex hooks must contain SessionStart, PreToolUse, and Stop only")

    portable = parsed.get("plugins/ai-coding-workflow/plugin.json", {})
    compatibility = parsed.get("plugins/ai-coding-workflow/.codex-plugin/plugin.json", {})
    versions: dict[str, object] = {}
    for manifest_name, manifest in (("portable", portable), ("compatibility", compatibility)):
        if not isinstance(manifest, dict) or manifest.get("name") != "ai-coding-workflow":
            errors.append(f"Codex {manifest_name} manifest has invalid plugin name")
        versions[manifest_name] = manifest.get("version") if isinstance(manifest, dict) else None
    if versions.get("portable") != versions.get("compatibility"):
        errors.append("Codex portable and compatibility manifest versions must match")
    version = versions.get("portable")
    if not isinstance(version, str) or re.fullmatch(
        r"3\.3\.0(?:\+codex\.\d{14})?", version
    ) is None:
        errors.append("Codex plugin version must be 3.3.0 or a generated cachebuster version")

    marketplace = parsed.get(".agents/plugins/marketplace.json", {})
    entries = marketplace.get("plugins", []) if isinstance(marketplace, dict) else []
    if marketplace.get("name") != "ai-coding-workflow" or not any(
        entry.get("name") == "ai-coding-workflow"
        and entry.get("source", {}).get("path") == "./plugins/ai-coding-workflow"
        for entry in entries
        if isinstance(entry, dict)
    ):
        errors.append("repo marketplace must publish ai-coding-workflow from ./plugins/ai-coding-workflow")

    checked = subprocess.run(
        ["node", "--check", str(ROOT / ".claude/scripts/workflow-runtime.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if checked.returncode != 0:
        errors.append(f"invalid workflow runtime JavaScript: {checked.stderr.strip()}")
    codex_checked = subprocess.run(
        ["node", "--check", str(CODEX_PLUGIN_ROOT / "scripts/workflow-runtime.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if codex_checked.returncode != 0:
        errors.append(f"invalid Codex workflow runtime JavaScript: {codex_checked.stderr.strip()}")
    setup_checked = subprocess.run(
        ["node", "--check", str(CODEX_PLUGIN_ROOT / "scripts/setup-check.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if setup_checked.returncode != 0:
        errors.append(f"invalid Codex setup checker JavaScript: {setup_checked.stderr.strip()}")
    if (CODEX_PLUGIN_ROOT / "scripts/workflow-runtime.mjs").read_bytes() != (
        ROOT / ".claude/scripts/workflow-runtime.mjs"
    ).read_bytes():
        errors.append("Claude and Codex runtime copies must stay byte-identical")


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
        "SessionStart",
        "PreToolUse",
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
        "hook_profile",
        "resume_incomplete",
    ):
        if re.search(rf"^\s*{re.escape(key)}\s*:", profile, re.MULTILINE) is None:
            errors.append(f"project profile missing key: {key}")

    codex_skill = (CODEX_PLUGIN_ROOT / "skills/ai-coding-workflow/SKILL.md").read_text(encoding="utf-8")
    codex_playbooks = (
        CODEX_PLUGIN_ROOT / "skills/ai-coding-workflow/references/PLAYBOOKS.md"
    ).read_text(encoding="utf-8")
    codex_routing = (
        CODEX_PLUGIN_ROOT / "skills/ai-coding-workflow/references/ROUTING.md"
    ).read_text(encoding="utf-8")
    codex_contract = "\n".join((codex_skill, codex_playbooks, codex_routing))
    for term in (
        "$openspec-propose",
        "$openspec-apply-change",
        "$plannotator-review",
        ".codex/ai-coding-workflow/project-profile.yaml",
        "--host codex",
        "Route Card 不是批准 Gate",
        "$ai-coding-workflow-setup",
        "plannotator review --git",
    ):
        if term not in codex_contract:
            errors.append(f"Codex workflow missing required host contract: {term}")
    for stale in ("/opsx:apply", "/opsx:propose", "/plannotator-review", ".claude/project-profile.yaml"):
        if stale in codex_contract:
            errors.append(f"Codex workflow contains Claude-specific invocation: {stale}")

    codex_profile = (CODEX_PLUGIN_ROOT / "assets/project-profile.yaml").read_text(encoding="utf-8")
    for term in (
        ".codex/ai-coding-workflow/workflow-state.schema.json",
        'hook_profile: "default"',
        'status: "unchecked"',
        'hooks_trust: "manual"',
        "node_supported: false",
    ):
        if term not in codex_profile:
            errors.append(f"Codex project profile missing host setting: {term}")

    setup_skill = (
        CODEX_PLUGIN_ROOT / "skills/ai-coding-workflow-setup/SKILL.md"
    ).read_text(encoding="utf-8")
    for term in (
        "一次性授权",
        "superpowers-plugin",
        "openspec init --tools codex",
        "--write-profile --require-ready",
        "不得重复安装",
        "20.19.0",
        "https://plannotator.ai/install.ps1",
    ):
        if term not in setup_skill:
            errors.append(f"Codex setup skill missing required contract: {term}")


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


def validate_archive_contents(
    errors: list[str], archive_path: Path | None, included: set[str], base: Path
) -> None:
    if archive_path is None:
        return
    if not archive_path.exists():
        errors.append(f"archive does not exist: {archive_path}")
        return
    with ZipFile(archive_path) as archive:
        actual = {name for name in archive.namelist() if not name.endswith("/")}
        expected: set[str] = set()
        for entry in included:
            path = base / entry
            if path.is_file():
                expected.add(path.relative_to(base).as_posix())
            elif path.is_dir():
                expected.update(item.relative_to(base).as_posix() for item in path.rglob("*") if item.is_file())
        if actual != expected:
            errors.append(f"archive content does not match deterministic manifest: {archive_path.name}")
        for name in actual & expected:
            if archive.read(name) != (base / name).read_bytes():
                errors.append(f"archive has stale content: {name}")


def validate_manifest(
    errors: list[str], archive_path: Path | None, codex_archive_path: Path | None
) -> None:
    manifest = json.loads((ROOT / "distribution-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("version") != "3.3.0-deterministic-composable":
        errors.append("distribution version must be 3.3.0-deterministic-composable")
    included = set(manifest.get("include", []))
    if included != RUNTIME_FILES:
        errors.append("distribution must contain exactly the declared V3.3 runtime files")
    if any(path.startswith(("scripts/", "tests/", "evals/")) for path in included):
        errors.append("business distribution must not include maintainer tooling")

    validate_archive_contents(errors, archive_path, included, ROOT)

    codex_manifest = json.loads((ROOT / "codex-distribution-manifest.json").read_text(encoding="utf-8"))
    if codex_manifest.get("version") != "3.3.0-codex":
        errors.append("Codex distribution version must be 3.3.0-codex")
    codex_included = set(codex_manifest.get("include", []))
    declared_files: set[str] = set()
    for entry in codex_included:
        path = CODEX_PLUGIN_ROOT / entry
        if path.is_file():
            declared_files.add(path.relative_to(CODEX_PLUGIN_ROOT).as_posix())
        elif path.is_dir():
            declared_files.update(
                item.relative_to(CODEX_PLUGIN_ROOT).as_posix() for item in path.rglob("*") if item.is_file()
            )
    if declared_files != CODEX_PLUGIN_FILES:
        errors.append("Codex distribution must contain exactly the declared plugin runtime files")
    validate_archive_contents(errors, codex_archive_path, codex_included, CODEX_PLUGIN_ROOT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--codex-archive", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    validate_files(errors)
    validate_json_and_javascript(errors)
    validate_content(errors)
    validate_references(errors)
    validate_manifest(errors, args.archive, args.codex_archive)
    if errors:
        print("workflow validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("V3.3 deterministic composable workflow validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
