from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_distribution import build  # noqa: E402
from evaluate_routing import evaluate, route  # noqa: E402


EXPECTED_RUNTIME = {
    ".claude/project-profile.yaml",
    ".claude/skills/new-task/SKILL.md",
    ".claude/skills/workflow-router/SKILL.md",
    ".claude/skills/workflow-router/ROUTING.md",
    ".claude/skills/workflow-router/PLAYBOOKS.md",
    "CLAUDE.md",
}


class DistributionTests(unittest.TestCase):
    def test_distribution_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.zip"
            second = Path(directory) / "second.zip"
            build(first)
            build(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_distribution_contains_only_adaptive_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "template.zip"
            build(archive)
            with ZipFile(archive) as package:
                actual = {name for name in package.namelist() if not name.endswith("/")}
            self.assertEqual(actual, EXPECTED_RUNTIME)


class RoutingPolicyTests(unittest.TestCase):
    def test_calibration_cases(self) -> None:
        failures = evaluate(ROOT / "evals/routing-cases.json")
        self.assertEqual(failures, [])

    def test_governed_trigger_overrides_fast_shape(self) -> None:
        facts = {
            "clear_acceptance": True,
            "localized_change": True,
            "consumers_known": True,
            "no_boundary_change": True,
            "easy_rollback": True,
            "direct_validation": True,
            "no_design_tradeoff": True,
            "schema_migration": True,
        }
        self.assertEqual(route(facts), "governed")

    def test_missing_fast_evidence_defaults_to_standard(self) -> None:
        self.assertEqual(route({"clear_acceptance": True}), "standard")

    def test_case_ids_are_unique(self) -> None:
        cases = json.loads((ROOT / "evals/routing-cases.json").read_text(encoding="utf-8"))
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
