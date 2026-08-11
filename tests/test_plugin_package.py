import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_plugin_package import validate


class PluginPackageValidationTests(unittest.TestCase):
    def test_repository_package_is_valid(self):
        self.assertEqual(validate(), [])

    def test_manifest_path_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".codex-plugin").mkdir()
            (root / ".agents/plugins").mkdir(parents=True)
            (root / "skills/example").mkdir(parents=True)
            (root / "skills/example/SKILL.md").write_text("---\nname: example\ndescription: x\n---\n", encoding="utf-8")
            (root / ".codex-plugin/plugin.json").write_text(json.dumps({
                "name": "example",
                "version": "0.1.0",
                "description": "x",
                "skills": "./../outside",
            }), encoding="utf-8")
            errors = validate(root)
            self.assertTrue(any("skills" in error and "must resolve" in error for error in errors))

    def test_marketplace_source_escape_or_wrong_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".codex-plugin").mkdir()
            (root / ".agents/plugins").mkdir(parents=True)
            (root / "skills/example").mkdir(parents=True)
            (root / "skills/example/SKILL.md").write_text("---\nname: example\ndescription: x\n---\n", encoding="utf-8")
            (root / ".codex-plugin/plugin.json").write_text(json.dumps({
                "name": "example", "version": "0.1.0", "description": "x", "skills": "./skills/"
            }), encoding="utf-8")
            (root / ".agents/plugins/marketplace.json").write_text(json.dumps({
                "name": "test", "interface": {"displayName": "Test"}, "plugins": [{
                    "name": "example", "source": {"source": "local", "path": "../../outside"},
                    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                    "category": "Productivity"
                }]
            }), encoding="utf-8")
            errors = validate(root)
            self.assertTrue(any("source" in error for error in errors))
            self.assertTrue(any("source.path" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
