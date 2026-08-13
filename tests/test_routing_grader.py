import unittest

from evals.codex.graders.routing import grade_routing


def case(**overrides):
    value = {
        "case_id": "fixture",
        "expected_primary_skill": "testing-qa",
        "acceptable_alternative_skills": [],
        "forbidden_skills": [],
    }
    value.update(overrides)
    return value


class RoutingGraderTests(unittest.TestCase):
    def test_correct_selection(self):
        result = grade_routing(case(), [{"type": "skill_selected", "name": "testing-qa"}])
        self.assertEqual(result["primary_selection_verdict"], "PASS")
        self.assertEqual(result["routing_verdict"], "PASS")

    def test_wrong_neighboring_skill(self):
        result = grade_routing(case(), [{"type": "skill_loaded", "name": "test-driven-development"}])
        self.assertEqual(result["primary_selection_verdict"], "FAIL")

    def test_forbidden_skill_activation(self):
        result = grade_routing(case(forbidden_skills=["pr-review"]), [{"type": "skill_loaded", "name": "pr-review"}])
        self.assertEqual(result["forbidden_activation_verdict"], "FAIL")
        self.assertEqual(result["routing_verdict"], "FAIL")

    def test_acceptable_alternative(self):
        result = grade_routing(case(acceptable_alternative_skills=["improve"]), [{"type": "skill_loaded", "name": "improve"}])
        self.assertEqual(result["primary_selection_verdict"], "ACCEPTED")
        self.assertEqual(result["acceptable_alternative_handling"], "ACCEPTED")

    def test_multi_skill_composition_is_allowed(self):
        result = grade_routing(case(), [
            {"type": "skill_loaded", "name": "testing-qa"},
            {"type": "skill_loaded", "name": "feature-implementation"},
        ])
        self.assertEqual(result["actual_selected_skills"], ["testing-qa", "feature-implementation"])
        self.assertEqual(result["routing_verdict"], "PASS")

    def test_expected_composition_sequence(self):
        result = grade_routing(
            case(expected_skill_sequence=["testing-qa", "feature-implementation"]),
            [
                {"type": "skill_loaded", "name": "testing-qa"},
                {"type": "skill_loaded", "name": "feature-implementation"},
            ],
        )
        self.assertEqual(result["expected_composition_sequence_verdict"], "PASS")

    def test_missing_telemetry_is_unknown_and_health_is_separate(self):
        result = grade_routing(case(), [{"type": "turn.completed", "text": "I used testing-qa"}])
        self.assertEqual(result["primary_selection_verdict"], "UNKNOWN")
        self.assertEqual(result["runtime_health"], "PASS")
        self.assertEqual(result["routing_verdict"], "UNKNOWN")

    def test_runtime_failure_does_not_imply_routing(self):
        result = grade_routing(case(), [{"type": "error", "message": "failed"}])
        self.assertEqual(result["runtime_health"], "FAIL")
        self.assertEqual(result["primary_selection_verdict"], "UNKNOWN")

    def test_malformed_events_are_structured(self):
        result = grade_routing(case(), [{"type": "skill_loaded", "name": None}])
        self.assertIn("malformed_event", result["reason_codes"])
        self.assertEqual(result["primary_selection_verdict"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
