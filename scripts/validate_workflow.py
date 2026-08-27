#!/usr/bin/env python3
"""Validate workflow rules, calibration cases, references and distribution content."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = {
    "scope": 1,
    "business": 1,
    "code_impact": 1,
    "architecture": 2,
    "data": 2,
    "infrastructure": 2,
    "runtime_risk": 3,
}
TIER_RANK = {"R1": 1, "R2": 2, "R3": 3, "R4": 4}
KNOWN_GATES = {
    "architecture", "data", "security", "compliance", "contract",
    "infrastructure", "delivery", "observability", "isolation",
}


def tier_from_score(score: int) -> str:
    if score <= 5:
        return "R1"
    if score <= 11:
        return "R2"
    if score <= 22:
        return "R3"
    return "R4"


def validate_required_files(errors: list[str], repository: bool) -> None:
    required = [
        "CLAUDE.md",
        ".claude/project-profile.yaml",
        ".claude/commands/new-task.md",
        ".claude/commands/workflow-report.md",
        ".claude/skills/workflow-router/SKILL.md",
        ".claude/skills/workflow-router/v2/complexity-matrix.md",
        ".claude/skills/workflow-router/v2/routing-rules.md",
        ".claude/skills/workflow-router/v2/gates.md",
        ".claude/skills/workflow-router/v2/levels.md",
        ".claude/skills/workflow-router/v2/toolcheck.md",
        ".claude/skills/workflow-router/v2/metrics.md",
        ".claude/skills/workflow-router/v2/metrics-schema.json",
        ".claude/skills/workflow-router/v2/calibration-cases.json",
        "scripts/workflow_report.py",
        "scripts/record_workflow_metric.py",
        "distribution-manifest.json",
    ]
    if repository:
        required.extend([
            "docs/README.md",
            "AI-Coding-Workflow-Template-详细使用说明.md",
            "docs/superpowers/specs/2026-08-26-ai-coding-workflow-v2-design.md",
            "scripts/build_distribution.py",
            ".github/workflows/validate-workflow-template.yml",
        ])
    required.extend(f".claude/skills/workflow-router/gates/R{tier}.md" for tier in range(1, 5))
    for relative in required:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")


def validate_calibration(errors: list[str]) -> None:
    path = ROOT / ".claude/skills/workflow-router/v2/calibration-cases.json"
    cases = json.loads(path.read_text(encoding="utf-8"))
    for case in cases:
        dimensions = case["dimensions"]
        if set(dimensions) != set(WEIGHTS):
            errors.append(f"{case['name']}: dimensions do not match v2.1 model")
            continue
        if any(not isinstance(value, int) or value < 0 or value > 3 for value in dimensions.values()):
            errors.append(f"{case['name']}: dimension outside 0..3")
            continue
        score = sum(dimensions[name] * weight for name, weight in WEIGHTS.items())
        if score != case["expected_score"]:
            errors.append(f"{case['name']}: expected score {case['expected_score']}, calculated {score}")
        baseline = tier_from_score(score)
        final_rank = max(TIER_RANK[baseline], TIER_RANK[case["red_flag_min_tier"]])
        final = next(tier for tier, rank in TIER_RANK.items() if rank == final_rank)
        if final != case["expected_tier"]:
            errors.append(f"{case['name']}: expected tier {case['expected_tier']}, calculated {final}")


def validate_consistency(errors: list[str], repository: bool) -> None:
    implementation_paths = [
        ROOT / "CLAUDE.md",
        ROOT / ".claude/skills/workflow-router/SKILL.md",
        ROOT / ".claude/skills/workflow-router/v2/complexity-matrix.md",
        ROOT / ".claude/skills/workflow-router/v2/routing-rules.md",
        ROOT / ".claude/skills/workflow-router/v2/levels.md",
    ]
    if repository:
        implementation_paths.extend([
            ROOT / "docs/README.md",
            ROOT / "AI-Coding-Workflow-Template-详细使用说明.md",
            ROOT / "docs/superpowers/specs/2026-08-26-ai-coding-workflow-v2-design.md",
        ])
    for path in implementation_paths:
        text = path.read_text(encoding="utf-8")
        if "V2.1" not in text and "v2.1" not in text:
            errors.append(f"missing V2.1 marker: {path.relative_to(ROOT)}")

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / ".claude").rglob("*.md")
    )
    required_terms = ["0~36", "required_gates", "Delivery Profile", "tasks.jsonl"]
    for term in required_terms:
        if term not in combined:
            errors.append(f"implementation does not contain required v2.1 term: {term}")
    forbidden = ["score: {n}/39", "Collaboration:     2 ×1", "tasks.md（追加）"]
    for term in forbidden:
        if term in combined:
            errors.append(f"stale v2 implementation term found: {term}")

    gate_catalog = (ROOT / ".claude/skills/workflow-router/v2/gates.md").read_text(encoding="utf-8")
    catalog_names = {
        match.group(1)
        for match in re.finditer(r"^\| `([a-z_]+)` \|", gate_catalog, re.MULTILINE)
    }
    if catalog_names != KNOWN_GATES:
        errors.append(
            "gate catalog mismatch: expected " + ", ".join(sorted(KNOWN_GATES))
            + "; found " + ", ".join(sorted(catalog_names))
        )
    routing = (ROOT / ".claude/skills/workflow-router/v2/routing-rules.md").read_text(encoding="utf-8")
    referenced_gates: set[str] = set()
    for line in routing.splitlines():
        columns = [column.strip() for column in line.split("|")]
        if len(columns) >= 5 and columns[2] in {"R3", "R4"}:
            referenced_gates.update(re.findall(r"`([a-z_]+)`", columns[3]))
    undefined = referenced_gates - catalog_names
    if undefined:
        errors.append("routing rules reference undefined gates: " + ", ".join(sorted(undefined)))

    profile = (ROOT / ".claude/project-profile.yaml").read_text(encoding="utf-8")
    for key in ("allow_r1_fast_path", "minimum_samples_for_tuning", "migration_dry_run", "rollback_strategy"):
        if re.search(rf"^\s*{re.escape(key)}\s*:", profile, re.MULTILINE) is None:
            errors.append(f"project profile missing key: {key}")


def validate_references(errors: list[str], repository: bool) -> None:
    markdown_files = [ROOT / "CLAUDE.md", *(ROOT / ".claude").rglob("*.md")]
    if repository:
        markdown_files.extend([
            ROOT / "docs/README.md",
            ROOT / "AI-Coding-Workflow-Template-详细使用说明.md",
            ROOT / "docs/superpowers/specs/2026-08-26-ai-coding-workflow-v2-design.md",
        ])
    router_root = ROOT / ".claude/skills/workflow-router"
    reference_pattern = re.compile(r"`([^`\n]+\.(?:md|json|yaml|py))`")
    for source in markdown_files:
        for raw_reference in reference_pattern.findall(source.read_text(encoding="utf-8")):
            references = [raw_reference]
            if "{n}" in raw_reference:
                references = [raw_reference.replace("{n}", str(tier)) for tier in range(1, 5)]
            for reference in references:
                if reference.startswith(".claude/") or reference.startswith("scripts/") or reference.startswith("docs/"):
                    target = ROOT / reference
                elif reference.startswith("v2/") or reference.startswith("gates/"):
                    target = router_root / reference
                elif reference == "CLAUDE.md":
                    target = ROOT / reference
                elif reference in {"metrics-schema.json", "calibration-cases.json"}:
                    target = source.parent / reference
                else:
                    continue
                if not target.exists():
                    errors.append(
                        f"broken reference in {source.relative_to(ROOT)}: {raw_reference} -> {target.relative_to(ROOT)}"
                    )


def validate_manifest(errors: list[str], archive_path: Path | None) -> None:
    manifest_path = ROOT / "distribution-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("version") != "2.1":
        errors.append("distribution manifest version must be 2.1")
    expected: set[str] = set()
    for entry in manifest["include"]:
        path = ROOT / entry
        if not path.exists():
            errors.append(f"manifest entry does not exist: {entry}")
            continue
        if path.is_file():
            expected.add(path.relative_to(ROOT).as_posix())
        else:
            expected.update(item.relative_to(ROOT).as_posix() for item in path.rglob("*") if item.is_file())
    if archive_path is not None:
        if not archive_path.exists():
            errors.append(f"archive does not exist: {archive_path}")
            return
        with ZipFile(archive_path) as archive:
            actual = {name for name in archive.namelist() if not name.endswith("/")}
            stale = sorted(
                name for name in expected & actual
                if archive.read(name) != (ROOT / name).read_bytes()
            )
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing:
            errors.append("archive missing: " + ", ".join(missing))
        if extra:
            errors.append("archive has unmanifested files: " + ", ".join(extra))
        if stale:
            errors.append("archive has stale content: " + ", ".join(stale))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--repository", action="store_true", help="also validate repository-only docs and CI files")
    args = parser.parse_args()
    errors: list[str] = []
    validate_required_files(errors, args.repository)
    if not errors:
        validate_calibration(errors)
        validate_consistency(errors, args.repository)
        validate_references(errors, args.repository)
        validate_manifest(errors, args.archive)
    if errors:
        print("workflow validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("workflow validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
