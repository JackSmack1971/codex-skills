import json
import tempfile
import unittest
from pathlib import Path

from evals.codex.graders.runtime import classify_runtime, selected_skill
from scripts.run_codex_evaluation import (
    deterministic_checks,
    live_probe,
    parse_runtime_events,
    routing_command,
    serialize_routing_result,
)


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

    def test_routing_command_is_ephemeral_read_only_and_does_not_include_prompt(self):
        command = routing_command("codex")
        self.assertIn("--ephemeral", command)
        self.assertIn("--ignore-user-config", command)
        self.assertIn("read-only", command)
        self.assertEqual(command[-1], "-")

    def test_event_parser_keeps_only_structured_grading_telemetry(self):
        events = parse_runtime_events('\n'.join([
            '{"type":"skill_loaded","name":"testing-qa","text":"private response"}',
            '{"type":"turn.completed","text":"response body"}',
            'not json',
        ]))
        self.assertEqual(events, [{"type": "skill_loaded", "name": "testing-qa"}, {"type": "turn.completed"}])

    def test_unavailable_without_installed_runtime(self):
        self.assertEqual(live_probe("codex-executable-that-does-not-exist")["status"], "UNAVAILABLE")

    def test_result_serialization_is_metadata_only(self):
        case = {"case_id": "case-1", "prompt": "private prompt"}
        grading = {
            "expected_primary_skill": "testing-qa",
            "actual_selected_skills": [],
            "primary_selection_verdict": "UNKNOWN",
            "forbidden_activation_verdict": "NOT_APPLICABLE",
            "acceptable_alternative_handling": "NOT_USED",
            "expected_composition_sequence_verdict": "NOT_SPECIFIED",
            "routing_verdict": "UNKNOWN",
            "runtime_health": "PASS",
            "reason_codes": ["selection_evidence_unavailable"],
        }
        result = serialize_routing_result(case, grading, "codex 1")
        self.assertNotIn("prompt", result)
        self.assertEqual(result["implicit_routing_status"], "UNAVAILABLE")
        self.assertEqual(result["codex_version"], "codex 1")


if __name__ == "__main__":
    unittest.main()
