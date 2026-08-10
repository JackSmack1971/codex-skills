import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FrontDoorRoutingTests(unittest.TestCase):
    def test_explicit_specialists_override_front_door(self):
        catalog = json.loads((ROOT / "skills/catalog.json").read_text(encoding="utf-8"))
        doors = catalog["front_doors"]
        skills = {record["name"] for record in catalog["skills"]}
        cases = json.loads((ROOT / "tests/front-door-routing-cases.json").read_text(encoding="utf-8"))["cases"]
        self.assertEqual(len(cases), 8)
        for case in cases:
            self.assertIn(case["front_door"], doors)
            self.assertIn(case["expected_skill"], skills)
            self.assertIn(case["expected_skill"], doors[case["front_door"]]["skills"])


if __name__ == "__main__":
    unittest.main()
