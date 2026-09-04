from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_skill_packages import package_errors, validate


class StandaloneSkillPackageTests(unittest.TestCase):
    def make_package(self, body: str, resources: tuple[str, ...] = ()) -> Path:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))
        package = root / "example"
        package.mkdir()
        (package / "SKILL.md").write_text(
            f"---\nname: example\ndescription: Example.\n---\n\n{body}\n", encoding="utf-8"
        )
        for relative in resources:
            path = package / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("resource\n", encoding="utf-8")
        return package

    def test_repository_packages_are_standalone(self) -> None:
        self.assertEqual(validate(), [])

    def test_missing_and_escaping_resources_fail(self) -> None:
        package = self.make_package("[missing](references/nope.md)\n[escape](../outside.md)")
        errors = package_errors(package)
        self.assertTrue(any("missing linked resource" in error for error in errors))
        self.assertTrue(any("link escapes package" in error for error in errors))

    def test_hard_coded_install_root_fails(self) -> None:
        package = self.make_package("Run `python .agents/skills/example/scripts/check.py`.")
        self.assertTrue(any("hard-codes a skill installation root" in error for error in package_errors(package)))

    def test_bundled_resource_passes(self) -> None:
        package = self.make_package("Read [policy](references/policy.md).", ("references/policy.md",))
        self.assertEqual(package_errors(package), [])


if __name__ == "__main__":
    unittest.main()
