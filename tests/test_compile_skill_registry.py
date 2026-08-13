from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.compile_skill_registry import compile_registry, inventory_text, render


class SkillRegistryCompilerTests(unittest.TestCase):
    def test_committed_views_are_current(self) -> None:
        root = Path(__file__).resolve().parents[1]
        inventory, state = render(root)
        self.assertEqual(inventory, (root / "docs/skill-inventory.md").read_text(encoding="utf-8"))
        self.assertEqual(state, (root / "docs/skill-state.json").read_text(encoding="utf-8"))

    def test_catalog_and_evaluation_must_have_exact_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "skills").mkdir()
            (root / "docs").mkdir()
            (root / "skills/catalog.json").write_text(json.dumps({"skills": [{"name": "one"}]}), encoding="utf-8")
            (root / "docs/evaluation-inventory.json").write_text(json.dumps({"skills": {}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "coverage differ"):
                compile_registry(root)


if __name__ == "__main__":
    unittest.main()
