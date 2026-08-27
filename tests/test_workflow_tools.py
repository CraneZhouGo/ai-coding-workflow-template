from __future__ import annotations

import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import workflow_report  # noqa: E402
from build_distribution import build  # noqa: E402
from record_workflow_metric import validate_record  # noqa: E402


class WorkflowReportTests(unittest.TestCase):
    def test_report_calculates_upgrade_and_known_defect_rates(self) -> None:
        records = [
            {
                "outcome": "completed",
                "initial_tier": "R1",
                "final_tier": "R2",
                "dimensions": {"business": 2},
                "semantic_red_flags": [],
                "duration_minutes": 20,
                "human_wait_minutes": 5,
                "rework": True,
                "capability_degradations": [{"capability": "plan_review"}],
                "code_review_findings": {"critical": 0, "high": 0, "medium": 1, "low": 0},
                "escaped_defect": False,
            },
            {
                "outcome": "completed",
                "initial_tier": "R2",
                "final_tier": "R2",
                "dimensions": {"business": 1},
                "semantic_red_flags": [],
                "duration_minutes": 40,
                "human_wait_minutes": 10,
                "rework": False,
                "capability_degradations": [],
                "code_review_findings": {"critical": 0, "high": 0, "medium": 0, "low": 1},
                "escaped_defect": True,
            },
        ]
        report = workflow_report.summarize(records, minimum_samples=20)
        self.assertIn("upgrade rate: 50% (1/2)", report)
        self.assertIn("escaped defect rate: 50% (1/2)", report)
        self.assertIn("insufficient sample for tuning: 2/20", report)

    def test_metric_record_validation_rejects_incomplete_record(self) -> None:
        errors = validate_record({"schema_version": 1})
        self.assertTrue(any(error.startswith("missing required field:") for error in errors))

    def test_metric_record_validation_accepts_v2_1_record(self) -> None:
        record = {
            "schema_version": 1,
            "timestamp": "2026-08-27T12:00:00+08:00",
            "task_id": "task-1",
            "task_summary": "example",
            "outcome": "completed",
            "initial_tier": "R2",
            "final_tier": "R2",
            "initial_score": 8,
            "final_score": 8,
            "dimensions": {
                "scope": 1, "business": 1, "code_impact": 1,
                "architecture": 1, "data": 0, "infrastructure": 0,
                "runtime_risk": 1,
            },
            "semantic_red_flags": [],
            "required_gates": [],
            "delivery_profile": {
                "agents": "1", "worktrees": "none",
                "rollout": "none", "ownership": "single",
            },
            "capability_degradations": [],
            "changed_files": 1,
            "changed_modules": 1,
            "tests": [{"command": "test", "result": "passed"}],
            "plan_review_rounds": 1,
            "code_review_findings": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "rework": False,
            "duration_minutes": 10,
            "human_wait_minutes": 0,
            "escaped_defect": None,
        }
        self.assertEqual(validate_record(record), [])


class DistributionTests(unittest.TestCase):
    def test_distribution_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.zip"
            second = Path(directory) / "second.zip"
            build(first)
            build(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_extracted_distribution_validates_in_runtime_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "template.zip"
            extracted = Path(directory) / "extracted"
            build(archive)
            with ZipFile(archive) as package:
                package.extractall(extracted)
            result = subprocess.run(
                [sys.executable, "scripts/validate_workflow.py"],
                cwd=extracted,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
