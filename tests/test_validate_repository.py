from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_repository import validate

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_repository.py"


class RepositoryValidatorTests(unittest.TestCase):
    def make_repo(self, skills: dict[str, str]) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        records = []
        for name, body in skills.items():
            skill = root / "skills" / name
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: Test skill.\n---\n\n{body}\n",
                encoding="utf-8",
            )
            records.append({"name": name, "path": f"skills/{name}/SKILL.md", "capability_level": "prompt-only", "validation_artifacts": []})
        (root / "skills" / "catalog.json").write_text(json.dumps({"skills": records}), encoding="utf-8")
        return root

    def assert_cli_fails(self, root: Path) -> None:
        result = subprocess.run([sys.executable, str(SCRIPT), str(root)], capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_relative_reference_fails(self) -> None:
        errors = validate(self.make_repo({"one": "[missing](references/nope.md)"}))
        self.assertTrue(any("missing reference" in error for error in errors))
        self.assert_cli_fails(self.make_repo({"one": "[missing](references/nope.md)"}))

    def test_duplicate_skill_names_fail(self) -> None:
        root = self.make_repo({"one": "", "two": ""})
        (root / "skills" / "two" / "SKILL.md").write_text(
            "---\nname: one\ndescription: Test skill.\n---\n", encoding="utf-8"
        )
        errors = validate(root)
        self.assertTrue(any("frontmatter names are not unique" in error for error in errors))
        self.assert_cli_fails(root)

    def test_secret_like_value_fails(self) -> None:
        errors = validate(self.make_repo({"one": "AKIA1234567890ABCDEF"}))
        self.assertTrue(any("secret-like value" in error for error in errors))
        self.assert_cli_fails(self.make_repo({"one": "AKIA1234567890ABCDEF"}))


if __name__ == "__main__":
    unittest.main()
