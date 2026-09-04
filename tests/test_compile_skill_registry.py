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

    def test_deterministic_only_command_cannot_claim_behavioral_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "skills").mkdir()
            (root / "docs").mkdir()
            record = {
                "name": "one",
                "path": "skills/one/SKILL.md",
                "classification": "Specialized",
                "primary_trigger": "Test one.",
                "provenance": "unknown",
            }
            skill = root / "skills/one"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: one\ndescription: Canonical runtime description.\n---\n",
                encoding="utf-8",
            )
            (root / "skills/catalog.json").write_text(json.dumps({"skills": [record]}), encoding="utf-8")
            (root / "docs/evaluation-inventory.json").write_text(json.dumps({"skills": {"one": {
                "level": "automated-behavioral",
                "evidence": "none",
                "command": "python scripts/run_core_evaluation.py --deterministic-only",
            }}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "deterministic-only execution"):
                compile_registry(root)

    def test_runtime_frontmatter_description_is_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills/one"
            skill.mkdir(parents=True)
            (root / "docs").mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: one\ndescription: Runtime routing description.\n---\n",
                encoding="utf-8",
            )
            record = {
                "name": "one", "path": "skills/one/SKILL.md",
                "classification": "Specialized", "primary_trigger": "Test one.",
                "provenance": "unknown",
            }
            (root / "skills/catalog.json").write_text(json.dumps({"skills": [record]}), encoding="utf-8")
            (root / "docs/evaluation-inventory.json").write_text(json.dumps({"skills": {"one": {
                "level": "none", "evidence": "none", "command": "none",
            }}}), encoding="utf-8")
            registry = compile_registry(root)
            self.assertEqual(registry["skills"][0]["description"], "Runtime routing description.")


if __name__ == "__main__":
    unittest.main()
