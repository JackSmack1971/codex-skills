import unittest
from unittest.mock import patch

from scripts.run_core_evaluation import CASES, evaluate_assertions, load_cases, run_case, validate_suite


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

    def test_missing_codex_is_unavailable_not_failure(self):
        case = load_cases()["cases"][0]
        with patch("scripts.run_core_evaluation.codex_bin", return_value=None):
            result = run_case(case, "explicit")
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["mode"], "explicit")

    def test_validator_exit_code_assertion_runs_declared_command(self):
        case = {
            "expected_required_behaviors": [{"type": "validator_exit_code", "value": 0, "command": ["python", "-c", "pass"]}],
            "forbidden_behaviors": [],
        }
        self.assertEqual(evaluate_assertions(case, "", 0)["status"], "pass")

    def test_invalid_case_is_rejected(self):
        data = {"schema_version": 1, "artifact_policy": "metadata-only", "cases": [{"case_id": "x"}]}
        self.assertTrue(validate_suite(data))


if __name__ == "__main__":
    unittest.main()
