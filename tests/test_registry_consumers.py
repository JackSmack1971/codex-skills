from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_core_benchmark import core_skills
from scripts.run_core_evaluation import core_skill_names


class RegistryConsumerTests(unittest.TestCase):
    def test_core_consumers_use_registry_not_markdown_formatting(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "docs/skill-state.json").write_text(json.dumps({
                "skills": [
                    {"name": "core-one", "classification": "Core"},
                    {"name": "special-one", "classification": "Specialized"},
                ]
            }), encoding="utf-8")
            (root / "docs/skill-inventory.md").write_text("not a Markdown table", encoding="utf-8")

            self.assertEqual(core_skills(root), {"core-one"})
            self.assertEqual(core_skill_names(root), {"core-one"})


if __name__ == "__main__":
    unittest.main()
