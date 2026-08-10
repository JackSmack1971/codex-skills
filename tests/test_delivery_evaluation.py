import unittest

from scripts.run_delivery_evaluation import FIXTURES, checks_for


class DeliveryEvaluationTests(unittest.TestCase):
    def test_all_target_fixtures_pass_skill_specific_checks(self):
        import json

        data = json.loads(FIXTURES.read_text(encoding="utf-8"))
        self.assertEqual(len(data["cases"]), 7)
        for case in data["cases"]:
            self.assertTrue(all(passed for _, passed in checks_for(case["skill"], case["artifact"])))

    def test_skill_specific_invariant_fails_when_artifact_is_invalid(self):
        import copy
        import json

        case = json.loads(FIXTURES.read_text(encoding="utf-8"))["cases"][0]
        artifact = copy.deepcopy(case["artifact"])
        artifact["solution_design"] = "invented feature"
        self.assertFalse(all(passed for _, passed in checks_for(case["skill"], artifact)))


if __name__ == "__main__":
    unittest.main()
