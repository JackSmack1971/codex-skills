import unittest

from scripts.compare_routing_baseline import compare, create_baseline


def artifact(version, rows):
    return {"result": {"version": version, "codex_version": "codex-1", "cases": rows}}


def row(case_id, expected, actual, *, forbidden=False, group=None, core=False):
    return {
        "case_id": case_id,
        "expected_primary_skill": expected,
        "actual_selected_skills": [actual] if actual else [],
        "selection_telemetry": bool(actual),
        "primary_selection_verdict": "PASS" if actual == expected else "FAIL",
        "forbidden_activation_verdict": "FAIL" if forbidden else "PASS",
        "routing_verdict": "PASS" if actual == expected and not forbidden else "FAIL",
        "runtime_health": "OK",
        "case_kind": "counterfactual" if group else "positive",
        "group_id": group,
        "source": "benchmarks/core/behavioral-cases.json" if core else "tests/skill-routing-cases.json",
    }


class RoutingBaselineTests(unittest.TestCase):
    def test_compare_reports_deltas_edges_groups_versions_and_policy(self):
        baseline = create_baseline([artifact("runtime-1", [
            row("a", "alpha", "alpha", core=True),
            row("b", "alpha", "alpha", core=True),
            row("cf", "alpha", "alpha", group="alpha-v-beta"),
        ])])
        candidate = create_baseline([artifact("runtime-2", [
            row("a", "alpha", "beta", forbidden=True, core=True),
            row("b", "alpha", "alpha", core=True),
            row("cf", "alpha", "beta", group="alpha-v-beta"),
        ])])
        report = compare(baseline, candidate, {"protected_core_max_accuracy_regression": 0.0})
        self.assertAlmostEqual(report["per_skill_accuracy_delta"]["alpha"]["delta"], -2 / 3)
        self.assertEqual(report["new_confusion_edges"], ["alpha->beta"])
        self.assertEqual(report["forbidden_activation_regressions"], ["a"])
        self.assertEqual(report["counterfactual_regressions"], ["alpha-v-beta"])
        self.assertTrue(report["runtime_comparison"]["material_version_change"])
        self.assertEqual(report["policy"]["status"], "FAIL")

    def test_unknown_and_unavailable_are_counted_with_samples(self):
        baseline = create_baseline([artifact("runtime-1", [row("a", "alpha", "alpha"), row("b", "alpha", "alpha")])])
        unavailable = row("b", "alpha", None)
        unavailable["runtime_health"] = "UNAVAILABLE"
        candidate = create_baseline([artifact("runtime-1", [row("a", "alpha", None), unavailable])])
        report = compare(baseline, candidate)
        self.assertEqual(report["unknown_delta"]["candidate"], {"count": 1, "total": 2, "rate": 0.5})
        self.assertEqual(report["unavailable_delta"]["candidate"], {"count": 1, "total": 2, "rate": 0.5})


if __name__ == "__main__":
    unittest.main()
