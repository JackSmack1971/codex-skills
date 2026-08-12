import json
import tempfile
import unittest
from pathlib import Path

from evals.codex.graders.runtime import classify_runtime, selected_skill
from scripts.run_codex_evaluation import deterministic_checks


class CodexEvaluationTests(unittest.TestCase):
    def test_deterministic_cases_pass(self):
        self.assertTrue(all(case["status"] == "PASS" for case in deterministic_checks()))

    def test_selection_requires_runtime_evidence(self):
        self.assertEqual(selected_skill([{"type": "agent_message", "text": "I used testing-qa"}]), "UNKNOWN")
        self.assertEqual(selected_skill([{"type": "skill_loaded", "name": "testing-qa"}]), "testing-qa")

    def test_result_classification(self):
        self.assertEqual(classify_runtime([]), "UNAVAILABLE")
        self.assertEqual(classify_runtime([{"type": "turn.completed"}]), "PASS")
        self.assertEqual(classify_runtime([{"type": "error"}]), "FAIL")

    def test_authored_fixture_locations_and_results_ignore(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "evals/codex/tasks/runtime-cases.json").is_file())
        self.assertTrue((root / "evals/codex/expected_invariants/runtime.json").is_file())
        self.assertIn("evals/codex/results/*", (root / ".gitignore").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
