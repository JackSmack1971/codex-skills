import json
import unittest
from pathlib import Path

from scripts.validate_routing_benchmark import validate


ROOT = Path(__file__).resolve().parents[1]


class RoutingBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "benchmarks/routing/cases.json").read_text(encoding="utf-8"))
        self.state = json.loads((ROOT / "docs/skill-state.json").read_text(encoding="utf-8"))

    def test_canonical_corpus_validates(self):
        self.assertEqual(validate(self.data, self.state, ROOT), [])

    def test_unknown_skill_is_rejected(self):
        self.data["cases"][0]["forbidden_skills"] = ["not-a-skill"]
        self.assertTrue(any("unknown skill not-a-skill" in error for error in validate(self.data, self.state, ROOT)))

    def test_counterfactual_requires_group(self):
        self.data["cases"][0]["case_kind"] = "counterfactual"
        self.data["cases"][0].pop("group_id", None)
        self.assertTrue(any("counterfactual case requires group_id" in error for error in validate(self.data, self.state, ROOT)))


if __name__ == "__main__":
    unittest.main()
