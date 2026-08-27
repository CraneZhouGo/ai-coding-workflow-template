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
from evaluate_routing import (  # noqa: E402
    classify_intent,
    classify_specialized_gates,
    classify_task_type,
    evaluate,
    route,
    route_mode,
)


EXPECTED_RUNTIME = {
    ".claude/project-profile.yaml",
    ".claude/skills/new-task/SKILL.md",
    ".claude/skills/workflow-router/SKILL.md",
    ".claude/skills/workflow-router/ROUTING.md",
    ".claude/skills/workflow-router/PLAYBOOKS.md",
    "CLAUDE.md",
}


class DistributionTests(unittest.TestCase):
    def test_distribution_version_is_patch_release(self) -> None:
        manifest = json.loads((ROOT / "distribution-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "3.2.1-composable")

    def test_distribution_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.zip"
            second = Path(directory) / "second.zip"
            build(first)
            build(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_distribution_contains_only_composable_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "template.zip"
            build(archive)
            with ZipFile(archive) as package:
                actual = {name for name in package.namelist() if not name.endswith("/")}
            self.assertEqual(actual, EXPECTED_RUNTIME)


class RoutingPolicyTests(unittest.TestCase):
    def test_calibration_cases(self) -> None:
        self.assertEqual(evaluate(ROOT / "evals/routing-cases.json"), [])

    def test_non_change_intent_has_no_mode(self) -> None:
        facts = {
            "requested_diagnosis": True,
            "bug_or_failure": True,
            "critical_semantics_changed": True,
        }
        self.assertEqual(classify_intent(facts), "diagnose-only")
        self.assertEqual(classify_task_type(facts), "bug")
        self.assertIsNone(route_mode(facts))

    def test_explicit_change_wins_over_plan_signal(self) -> None:
        facts = {"requested_change": True, "requested_plan": True}
        self.assertEqual(classify_intent(facts), "change")

    def test_task_type_is_independent_from_risk_mode(self) -> None:
        facts = {
            "requested_change": True,
            "bug_or_failure": True,
            "schema_migration": True,
        }
        self.assertEqual(classify_task_type(facts), "bug")
        self.assertEqual(route_mode(facts), "governed")

    def test_specialized_gates_are_composable_and_ordered(self) -> None:
        facts = {
            "release_gate": True,
            "data_gate": True,
            "observability_gate": True,
        }
        self.assertEqual(
            classify_specialized_gates(facts),
            ["data", "release", "observability"],
        )

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


class WorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.playbook = (ROOT / ".claude/skills/workflow-router/PLAYBOOKS.md").read_text(encoding="utf-8")

    def test_composition_formula_and_core_spine_exist(self) -> None:
        self.assertIn("Core Spine + Task Method + Risk Safeguards + Specialized Gates", self.playbook)
        nodes = [f"C{index} REQUIRED" for index in range(1, 8)]
        positions = [self.playbook.index(node) for node in nodes]
        self.assertEqual(positions, sorted(positions))

    def test_standard_feature_includes_brainstorming(self) -> None:
        example = self.playbook.split("### Standard Feature", 1)[1].split("### Standard Bug", 1)[0]
        self.assertIn("brainstorming", example)
        self.assertIn("Plan Review", example)

    def test_standard_bug_uses_debugging_before_regression_test(self) -> None:
        example = self.playbook.split("### Standard Bug", 1)[1].split("### Governed Migration", 1)[0]
        self.assertLess(example.index("systematic-debugging"), example.index("failing-regression-test"))
        self.assertLess(example.index("Plan Review"), example.index("failing-regression-test"))

    def test_governed_migration_runs_dry_run_after_plan_review(self) -> None:
        example = self.playbook.split("### Governed Migration", 1)[1].split("## Durable workflow state", 1)[0]
        self.assertLess(example.index("Plan Review"), example.index("dry-run"))

    def test_openspec_apply_uses_real_agent_entry(self) -> None:
        for term in (
            "/opsx:apply <change-id>",
            "openspec-apply-change",
            "openspec instructions apply --change <change-id> --json",
            "终端命令 `openspec apply` 不存在",
            "S-IM1 REQUIRED — openspec-implementation-entry",
        ):
            self.assertIn(term, self.playbook)
        self.assertNotIn("S-EX1 REQUIRED — superpowers:executing-plans", self.playbook)

    def test_plan_review_packet_contains_all_change_documents(self) -> None:
        for term in (
            "Change Review Packet contract",
            "openspec status --change <change-id> --json",
            "P-RP3 REQUIRED — hash-artifacts",
            "P-RP4 REQUIRED — render-full-packet",
            "tool_input.plan",
            "每个文件完整内容",
            "不得摘要或截断",
            "context-only",
            "避免 Gate 状态更新使其自失效",
        ):
            self.assertIn(term, self.playbook)

    def test_standard_packet_gate_and_apply_are_ordered(self) -> None:
        example = self.playbook.split("### Standard Feature", 1)[1].split("### Standard Bug", 1)[0]
        positions = [
            example.index("full Change Review Packet"),
            example.index("Plannotator Plan Review"),
            example.index("/opsx:apply"),
        ]
        self.assertEqual(positions, sorted(positions))

    def test_completion_validates_before_completed_and_archive(self) -> None:
        contract = self.playbook.split("## Durable workflow state contract", 1)[1]
        sequence = "`openspec validate <change-id>` → status completed → `openspec archive <change-id>`"
        self.assertIn(sequence, contract)

    def test_standard_has_one_planned_human_gate(self) -> None:
        self.assertIn("Standard：只有 1 个预定人工 Gate", self.playbook)
        safeguards = self.playbook.split("### Standard safeguards", 1)[1].split("### Governed safeguards", 1)[0]
        self.assertEqual(safeguards.count("HUMAN GATE"), 1)

    def test_state_contract_supports_resume(self) -> None:
        for term in (
            "workflow-state.yaml",
            "schema_version: 1",
            "current_node:",
            "status: active",
            "最早的 pending/in_progress/blocked REQUIRED 节点继续",
            "done 节点不重复",
            "plan_review.status",
            "sha256:",
            "status completed → `openspec archive <change-id>`",
        ):
            self.assertIn(term, self.playbook)

    def test_route_card_is_not_an_approval_gate(self) -> None:
        constitution = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        profile = (ROOT / ".claude/project-profile.yaml").read_text(encoding="utf-8")
        self.assertIn("不得在 Route Card 后询问", constitution)
        self.assertIn("internal_steps_require_confirmation: false", profile)

    def test_integration_adapter_consolidates_duplicate_gates(self) -> None:
        self.assertIn("brainstorming 默认的逐段设计批准", self.playbook)
        self.assertIn("统一合并到当前工作流唯一一次 Plannotator Plan Review", self.playbook)
        self.assertIn("只表示返回父 Router", self.playbook)


if __name__ == "__main__":
    unittest.main()
