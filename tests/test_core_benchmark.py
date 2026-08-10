import json
import unittest
from pathlib import Path

from scripts.run_core_benchmark import MANIFEST, core_skills, run_deterministic


class CoreBenchmarkTests(unittest.TestCase):
    def test_manifest_covers_core_skills_and_case_kinds(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        result = run_deterministic(data)
        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertEqual(result["skills"], len(core_skills()))
        self.assertEqual(result["cases"], 69)

    def test_reported_implicit_mode_is_unavailable(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(data["modes"]["implicit_selection"]["status"], "unavailable")
        self.assertEqual(data["modes"]["implicit_selection"]["measurement"], "unreported")


if __name__ == "__main__":
    unittest.main()
