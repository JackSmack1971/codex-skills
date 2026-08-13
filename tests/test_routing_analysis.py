import json
import unittest
from pathlib import Path

from scripts.analyze_routing_results import analyze, markdown_report


ROOT = Path(__file__).resolve().parents[1]


class RoutingAnalysisTests(unittest.TestCase):
    def test_synthetic_metrics_and_metadata(self):
        artifact = json.loads((ROOT / "tests/fixtures/routing-results-synthetic.json").read_text())
        report = analyze([artifact])
        self.assertEqual(report["metadata"]["runtime_versions"], ["codex-test-1"])
        self.assertEqual(report["metrics"]["primary_selection_accuracy"], {"count": 3, "total": 7, "rate": 3 / 7})
        self.assertEqual(report["metrics"]["unknown_rate"], {"count": 1, "total": 9, "rate": 1 / 9})
        self.assertEqual(report["metrics"]["unavailable_rate"], {"count": 1, "total": 9, "rate": 1 / 9})
        self.assertEqual(report["metrics"]["acceptable_alternative_rate"]["count"], 1)
        self.assertEqual(report["metrics"]["forbidden_skill_activation_rate"]["count"], 1)
        self.assertEqual(report["confusions"]["feature-implementation"]["vertical-slice"], 3)
        self.assertEqual(report["counterfactual_groups"]["pass_rate"], {"count": 0, "total": 1, "rate": 0.0})

    def test_markdown_is_deterministic_and_has_sample_counts(self):
        artifact = json.loads((ROOT / "tests/fixtures/routing-results-synthetic.json").read_text())
        output = markdown_report(analyze([artifact]))
        self.assertIn("Primary-selection accuracy: 3/7 (42.9%)", output)
        self.assertIn("feature-implementation -> vertical-slice: 3/4 (75.0%)", output)
        self.assertIn("UNKNOWN rate: 1/9", output)


if __name__ == "__main__":
    unittest.main()
