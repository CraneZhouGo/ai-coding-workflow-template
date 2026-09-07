from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".claude/scripts/workflow-runtime.mjs"
sys.path.insert(0, str(ROOT / "scripts"))

from build_distribution import build  # noqa: E402
from evaluate_routing import (  # noqa: E402
    classify_intent,
    classify_specialized_gates,
    classify_task_type,
    evaluate,
    route,
    route_decision,
    route_mode,
)


EXPECTED_RUNTIME = {
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
FAST_FACTS = {
    "requested_change": True,
    "maintenance_only": True,
    "clear_acceptance": True,
    "localized_change": True,
    "consumers_known": True,
    "no_boundary_change": True,
    "easy_rollback": True,
    "direct_validation": True,
    "no_design_tradeoff": True,
}


def run_runtime(
    command: str,
    *arguments: str,
    payload: dict | None = None,
    cwd: Path = ROOT,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["node", str(RUNTIME), command, *arguments],
        cwd=cwd,
        input=json.dumps(payload, ensure_ascii=False) if payload is not None else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check and result.returncode != 0:
        raise AssertionError(result.stderr)
    return result


def initialize_state(
    root: Path,
    state_path: Path,
    *,
    facts: dict,
    change_id: str,
    profile_ready: bool = True,
) -> dict:
    result = run_runtime(
        "init-state",
        "--root",
        str(root),
        "--output",
        str(state_path),
        payload={
            "facts": facts,
            "profile_ready": profile_ready,
            "change_id": change_id,
            "requirement": "行为测试",
        },
        cwd=root,
    )
    return json.loads(result.stdout)


def transition(root: Path, state_path: Path, target: str, evidence: str | None = None) -> dict:
    arguments = ["--root", str(root), "--state", str(state_path), "--to", target]
    if evidence is not None:
        arguments.extend(["--evidence", evidence])
    result = run_runtime("transition", *arguments, cwd=root)
    return json.loads(result.stdout)


class DistributionTests(unittest.TestCase):
    def test_distribution_version(self) -> None:
        manifest = json.loads((ROOT / "distribution-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "3.3.0-deterministic-composable")

    def test_distribution_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.zip"
            second = Path(directory) / "second.zip"
            build(first)
            build(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_distribution_contains_only_runtime(self) -> None:
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
        facts = {"requested_diagnosis": True, "bug_or_failure": True}
        self.assertEqual(classify_intent(facts), "diagnose-only")
        self.assertEqual(classify_task_type(facts), "bug")
        self.assertIsNone(route_mode(facts))

    def test_task_type_is_independent_from_risk_mode(self) -> None:
        facts = {"requested_change": True, "bug_or_failure": True, "schema_migration": True}
        self.assertEqual(classify_task_type(facts), "bug")
        self.assertEqual(route_mode(facts), "governed")

    def test_specialized_gates_are_composable_and_ordered(self) -> None:
        facts = {"release_gate": True, "data_gate": True, "observability_gate": True}
        self.assertEqual(classify_specialized_gates(facts), ["data", "release", "observability"])

    def test_feature_never_uses_fast(self) -> None:
        facts = {**FAST_FACTS, "maintenance_only": False, "feature_or_behavior": True}
        self.assertEqual(route_decision(facts)["route"]["mode"], "standard")

    def test_unconfigured_profile_disables_fast(self) -> None:
        self.assertEqual(route_decision(FAST_FACTS, profile_ready=False)["route"]["mode"], "standard")

    def test_route_fingerprint_is_stable(self) -> None:
        first = route_decision(FAST_FACTS)
        second = route_decision(dict(reversed(list(FAST_FACTS.items()))))
        self.assertEqual(first["route_fingerprint"], second["route_fingerprint"])

    def test_governed_trigger_overrides_fast_shape(self) -> None:
        self.assertEqual(route({**FAST_FACTS, "schema_migration": True}), "governed")

    def test_case_ids_are_unique(self) -> None:
        cases = json.loads((ROOT / "evals/routing-cases.json").read_text(encoding="utf-8"))
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))


class RuntimeBehaviorTests(unittest.TestCase):
    def test_compose_has_mode_specific_human_gates_and_feature_brainstorming(self) -> None:
        feature = run_runtime(
            "compose",
            payload={"facts": {**FAST_FACTS, "maintenance_only": False, "feature_or_behavior": True}, "profile_ready": True},
        )
        standard_nodes = json.loads(feature.stdout)["nodes"]
        self.assertIn("M-FE1", [item["id"] for item in standard_nodes])
        self.assertEqual([item["id"] for item in standard_nodes if item["human_gate"]], ["S-HG1"])

        governed = run_runtime(
            "compose",
            payload={"facts": {"requested_change": True, "schema_migration": True}, "profile_ready": True},
        )
        governed_nodes = json.loads(governed.stdout)["nodes"]
        self.assertEqual([item["id"] for item in governed_nodes if item["human_gate"]], ["S-HG1", "G-HG1"])

        fast = run_runtime("compose", payload={"facts": FAST_FACTS, "profile_ready": True})
        self.assertFalse(any(item["human_gate"] for item in json.loads(fast.stdout)["nodes"]))

    def test_state_machine_rejects_skips_and_requires_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = root / ".claude/workflow-runs/test/workflow-state.json"
            state = initialize_state(root, state_path, facts=FAST_FACTS, change_id="fast-test")
            self.assertEqual(state["current_node"], "C1")

            skipped = run_runtime(
                "transition", "--root", str(root), "--state", str(state_path), "--to", "done", check=False, cwd=root
            )
            self.assertNotEqual(skipped.returncode, 0)
            self.assertIn("非法状态转换", skipped.stderr)

            transition(root, state_path, "in_progress")
            missing = run_runtime(
                "transition", "--root", str(root), "--state", str(state_path), "--to", "done", check=False, cwd=root
            )
            self.assertNotEqual(missing.returncode, 0)
            state = transition(root, state_path, "done", "已确认请求与边界")
            self.assertEqual(state["current_node"], "C2")

            state["workflow_hash"] = "0" * 64
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            tampered = run_runtime("validate-state", "--state", str(state_path), check=False, cwd=root)
            self.assertNotEqual(tampered.returncode, 0)
            self.assertIn("workflow_hash", tampered.stdout)

    def test_hooks_block_early_edit_and_stop_but_allow_implementation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = root / ".claude/workflow-runs/test/workflow-state.json"
            initialize_state(root, state_path, facts=FAST_FACTS, change_id="fast-hook")

            edit = run_runtime(
                "hook", "pre-tool-use", "--root", str(root),
                payload={"tool_input": {"file_path": str(root / "src/app.py")}}, cwd=root,
            )
            self.assertEqual(json.loads(edit.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")
            stop = run_runtime("hook", "stop", "--root", str(root), payload={"stop_hook_active": False}, cwd=root)
            self.assertEqual(json.loads(stop.stdout)["decision"], "block")

            state = json.loads(state_path.read_text(encoding="utf-8"))
            for item in state["nodes"]:
                if item["id"] == "C5":
                    break
                item["status"] = "done"
                item["evidence"] = ["测试迁移证据"]
            state["current_node"] = "C5"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            allowed = run_runtime(
                "hook", "pre-tool-use", "--root", str(root),
                payload={"tool_input": {"file_path": str(root / "src/app.py")}}, cwd=root,
            )
            self.assertEqual(allowed.stdout, "")

    def test_install_hooks_is_idempotent_and_preserves_settings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".claude/hooks").mkdir(parents=True)
            shutil.copy2(ROOT / ".claude/hooks/workflow-hooks.json", root / ".claude/hooks/workflow-hooks.json")
            shutil.copy2(ROOT / ".claude/project-profile.yaml", root / ".claude/project-profile.yaml")
            (root / ".claude/settings.json").write_text('{"permissions":{"allow":["Read"]}}', encoding="utf-8")

            first = json.loads(run_runtime("install-hooks", "--root", str(root), cwd=root).stdout)
            second = json.loads(run_runtime("install-hooks", "--root", str(root), cwd=root).stdout)
            settings = json.loads((root / ".claude/settings.json").read_text(encoding="utf-8"))
            profile = (root / ".claude/project-profile.yaml").read_text(encoding="utf-8")
            self.assertEqual(first["added"], 4)
            self.assertEqual(second["added"], 0)
            self.assertEqual(settings["permissions"], {"allow": ["Read"]})
            self.assertIn("hooks_installed: true", profile)

    def test_fast_upgrade_migrates_one_state_and_initializes_governed_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_state = root / ".claude/workflow-runs/fast/workflow-state.json"
            initialize_state(root, old_state, facts=FAST_FACTS, change_id="fast")
            for node_id in ("C1", "C2"):
                transition(root, old_state, "in_progress")
                transition(root, old_state, "done", f"完成 {node_id}")

            new_state = root / "openspec/changes/risk-found/workflow-state.json"
            rerouted = json.loads(run_runtime(
                "reroute", "--root", str(root), "--state", str(old_state),
                "--checkpoint", "post-exploration", "--reason", "发现 schema migration",
                "--output", str(new_state),
                payload={
                    "facts": {"schema_migration": True},
                    "profile_ready": True,
                    "change_id": "risk-found",
                },
                cwd=root,
            ).stdout)
            self.assertFalse(old_state.exists())
            self.assertTrue(new_state.exists())
            self.assertEqual(rerouted["route"]["current_mode"], "governed")
            self.assertEqual(rerouted["spec_review"]["diff_type"], "uncommitted")
            self.assertEqual(rerouted["code_review"]["diff_type"], "since-base")
            self.assertEqual(rerouted["archive_status"], "pending")

    def test_archive_completion_requires_archived_path_and_approved_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            active = root / "openspec/changes/finalize/workflow-state.json"
            initialize_state(
                root, active,
                facts={"requested_change": True, "maintenance_only": True},
                change_id="finalize",
            )
            state = json.loads(active.read_text(encoding="utf-8"))
            for item in state["nodes"]:
                if item["id"] == "C7":
                    item["status"] = "pending"
                    item["evidence"] = []
                else:
                    item["status"] = "done"
                    item["evidence"] = [f"完成 {item['id']}"]
            state["current_node"] = "C7"
            state["archive_status"] = "ready"
            state["spec_review"] = {
                "status": "approved",
                "diff_type": "uncommitted",
                "expected_paths": ["openspec/changes/finalize/proposal.md"],
                "displayed_paths": ["openspec/changes/finalize/proposal.md"],
                "artifact_hashes": [],
                "reviewed_at": "2026-01-01T00:00:00Z",
                "evidence": "approved",
            }
            active.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

            too_early = run_runtime(
                "archive-complete", "--state", str(active), "--evidence", "archive ok", check=False, cwd=root
            )
            self.assertNotEqual(too_early.returncode, 0)
            archived = root / "openspec/changes/archive/2026-01-01-finalize/workflow-state.json"
            archived.parent.mkdir(parents=True)
            shutil.move(active, archived)
            completed = json.loads(run_runtime(
                "archive-complete", "--state", str(archived), "--evidence", "openspec archive --yes 成功", cwd=root
            ).stdout)
            self.assertEqual(completed["status"], "completed")
            self.assertEqual(completed["archive_status"], "completed")

    def test_spec_review_checks_changed_paths_and_detects_hash_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git = ["git", "-c", "core.excludesFile="]
            subprocess.run([*git, "init"], cwd=root, check=True, capture_output=True)
            subprocess.run([*git, "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run([*git, "config", "user.name", "Workflow Test"], cwd=root, check=True)
            (root / "README.md").write_text("baseline\n", encoding="utf-8")
            subprocess.run([*git, "add", "README.md"], cwd=root, check=True)
            subprocess.run([*git, "commit", "-m", "baseline"], cwd=root, check=True, capture_output=True)

            change_dir = root / "openspec/changes/fix-order"
            change_dir.mkdir(parents=True)
            (change_dir / "proposal.md").write_text("# proposal\n", encoding="utf-8")
            state_path = change_dir / "workflow-state.json"
            initialize_state(
                root, state_path,
                facts={"requested_change": True, "bug_or_failure": True},
                change_id="fix-order",
            )

            while True:
                state = json.loads(state_path.read_text(encoding="utf-8"))
                if state["current_node"] == "S-DF1":
                    break
                current = state["current_node"]
                transition(root, state_path, "in_progress")
                transition(root, state_path, "done", f"完成 {current}")

            captured = json.loads(run_runtime(
                "capture-spec-diff", "--root", str(root), "--state", str(state_path), cwd=root
            ).stdout)
            expected = captured["spec_review"]["expected_paths"]
            self.assertEqual(expected, sorted(expected))
            self.assertTrue(all(path.startswith("openspec/changes/fix-order/") for path in expected))

            mismatch = run_runtime(
                "review", "--state", str(state_path), "--type", "spec", "--decision", "approved",
                "--diff-type", "uncommitted", "--displayed-paths", "openspec/changes/fix-order/proposal.md",
                check=False, cwd=root,
            )
            self.assertNotEqual(mismatch.returncode, 0)

            reviewed = json.loads(run_runtime(
                "review", "--state", str(state_path), "--type", "spec", "--decision", "approved",
                "--diff-type", "uncommitted", "--displayed-paths", ",".join(expected),
                "--evidence", "Plannotator approved", cwd=root,
            ).stdout)
            self.assertEqual(reviewed["current_node"], "C5")

            (change_dir / "proposal.md").write_text("# changed after review\n", encoding="utf-8")
            drift = run_runtime(
                "transition", "--root", str(root), "--state", str(state_path), "--to", "in_progress",
                check=False, cwd=root,
            )
            self.assertNotEqual(drift.returncode, 0)
            stale = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(stale["spec_review"]["status"], "stale")
            self.assertEqual(stale["current_node"], "S-DF1")


class WorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.playbook = (ROOT / ".claude/skills/workflow-router/PLAYBOOKS.md").read_text(encoding="utf-8")

    def test_tool_adapters_and_review_views_are_explicit(self) -> None:
        for term in (
            "M-FE1 REQUIRED — superpowers:brainstorming",
            "/opsx:apply <change-id>",
            "终端命令 `openspec apply` 不存在",
            "/plannotator-review",
            "uncommitted",
            "since-base",
            "禁止创建额外 Review Packet",
        ):
            self.assertIn(term, self.playbook)

    def test_completion_order_does_not_mark_completed_before_archive(self) -> None:
        self.assertIn("archive_status ready", self.playbook)
        self.assertIn("runtime `archive-complete` → status completed", self.playbook)
        self.assertNotIn("state completed → archive", self.playbook)

    def test_route_card_is_not_an_approval_gate(self) -> None:
        constitution = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        profile = (ROOT / ".claude/project-profile.yaml").read_text(encoding="utf-8")
        self.assertIn("不得在 Route Card 后询问", constitution)
        self.assertIn("internal_steps_require_confirmation: false", profile)

    def test_json_state_and_selective_agents_are_documented(self) -> None:
        self.assertIn("workflow-state.json", self.playbook)
        self.assertIn('\"schema_version\": 2', self.playbook)
        self.assertIn("## Selective specialist policy", self.playbook)


if __name__ == "__main__":
    unittest.main()
