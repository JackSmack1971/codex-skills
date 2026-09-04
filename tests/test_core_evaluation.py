import unittest
from unittest.mock import patch

from scripts.run_core_evaluation import CASES, evaluate_assertions, load_cases, run_case, skill_condition_prompt, summarize_paired, validate_suite


class CoreEvaluationTests(unittest.TestCase):
    def test_fixture_matches_behavioral_schema_contract(self):
        data = load_cases()
        self.assertEqual(validate_suite(data), [])
        self.assertEqual(len({case["case_id"] for case in data["cases"]}), len(data["cases"]))
        self.assertTrue(CASES.is_file())

    def test_assertions_report_required_and_forbidden_evidence_without_body(self):
        case = {
            "expected_required_behaviors": [{"type": "required_heading", "value": "Acceptance criteria"}],
            "forbidden_behaviors": [{"type": "forbidden_text", "value": "secret"}],
        }
        result = evaluate_assertions(case, "# Acceptance criteria\n- one\n", 0)
        self.assertEqual(result["status"], "pass")
        self.assertNotIn("output", result)
        self.assertEqual([check["category"] for check in result["checks"]], ["required", "forbidden"])

    def test_missing_codex_is_unavailable_not_failure(self):
        case = load_cases()["cases"][0]
        with patch("scripts.run_core_evaluation.codex_bin", return_value=None):
            result = run_case(case, "explicit")
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["mode"], "explicit")

    def test_skill_condition_injects_exact_package_with_digest(self):
        case = load_cases()["cases"][0]
        prompt, digest = skill_condition_prompt(case)
        self.assertIn("<skill-instructions>", prompt)
        self.assertIn(case["prompt"], prompt)
        self.assertEqual(len(digest), 64)

    def test_validator_exit_code_assertion_runs_declared_command(self):
        case = {
            "expected_required_behaviors": [{"type": "validator_exit_code", "value": 0, "command": ["python", "-c", "pass"]}],
            "forbidden_behaviors": [],
        }
        self.assertEqual(evaluate_assertions(case, "", 0)["status"], "pass")

    def test_invalid_case_is_rejected(self):
        data = {"schema_version": 1, "artifact_policy": "metadata-only", "cases": [{"case_id": "x"}]}
        self.assertTrue(validate_suite(data))

    def test_paired_summary_reports_material_uplift_as_exploratory(self):
        runtime = []
        for index in range(10):
            checks = [{"category": "forbidden", "passed": True}]
            runtime.append({
                "case_id": f"case-{index % 3}",
                "explicit_invocation": {"status": "pass", "response_chars": 80, "assertions": {"checks": checks}},
                "baseline": {"status": "fail" if index < 3 else "pass", "response_chars": 100, "assertions": {"checks": checks}},
            })
        summary = summarize_paired(runtime)
        self.assertFalse(summary["adequate_evidence"])
        self.assertTrue(summary["adequate_exploratory_evidence"])
        self.assertEqual(summary["g5_status"], "UNVALIDATED")
        self.assertEqual(summary["decision"], "EXPLORATORY_RETAIN_SIGNAL")
        self.assertAlmostEqual(summary["task_success_uplift_pp"], 30.0)

    def test_paired_summary_marks_no_uplift_as_exploratory_only(self):
        checks = [{"category": "forbidden", "passed": True}]
        runtime = [{
            "case_id": f"case-{index % 3}",
            "explicit_invocation": {"status": "pass", "response_chars": 100, "assertions": {"checks": checks}},
            "baseline": {"status": "pass", "response_chars": 100, "assertions": {"checks": checks}},
        } for index in range(10)]
        self.assertEqual(summarize_paired(runtime)["decision"], "EXPLORATORY_COMPRESS_SIGNAL")

    def test_paired_summary_is_inconclusive_when_runtime_is_unavailable(self):
        runtime = [{
            "case_id": "case-1",
            "explicit_invocation": {"status": "unavailable"},
            "baseline": {"status": "unavailable"},
        }]
        self.assertEqual(summarize_paired(runtime)["decision"], "INCONCLUSIVE")


if __name__ == "__main__":
    unittest.main()
