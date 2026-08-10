from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_repository import CONTROL_PLANE_DIRECTORIES, control_plane_layout_errors, validate, validate_freshness

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

    def test_valid_freshness_registry_passes(self) -> None:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))
        skill = root / "skills" / "one"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("# One\n", encoding="utf-8")
        (root / "docs").mkdir()
        (root / "docs" / "skill-freshness.json").write_text(json.dumps({
            "version": 1,
            "last_updated": "2026-01-01",
            "skills": {},
            "exemptions": {"one": {"status": "exempt", "exemption": "local method", "references": ["skills/one/SKILL.md"]}},
        }), encoding="utf-8")
        self.assertEqual(validate_freshness(root, {"one"}), [])

    def test_freshness_registry_rejects_bad_date_and_reference(self) -> None:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))
        (root / "docs").mkdir()
        (root / "docs" / "skill-freshness.json").write_text(json.dumps({
            "version": 1,
            "last_updated": "not-a-date",
            "skills": {"one": {
                "status": "version-sensitive", "technology": ["Tool"], "checked_version": "unknown",
                "last_verified": "2026-01-01", "runtime_detection_required": True,
                "verification": "probe", "references": ["skills/one/SKILL.md"],
            }},
            "exemptions": {},
        }), encoding="utf-8")
        errors = validate_freshness(root, {"one"})
        self.assertTrue(any("last_updated" in error for error in errors))
        self.assertTrue(any("missing reference" in error for error in errors))

    def test_control_plane_directories_are_structural_not_skill_packages(self) -> None:
        root = self.make_repo({"one": ""})
        (root / "AGENTS.md").write_text("# Policy\n", encoding="utf-8")
        for relative in CONTROL_PLANE_DIRECTORIES:
            (root / relative).mkdir(parents=True, exist_ok=True)
        local_skill = root / ".agents" / "skills" / "compatibility-example"
        local_skill.mkdir()
        (local_skill / "SKILL.md").write_text("not a canonical package", encoding="utf-8")

        self.assertEqual(control_plane_layout_errors(root), [])
        errors = validate(root)
        self.assertFalse(any("compatibility-example" in error for error in errors))

    def test_control_plane_layout_reports_missing_directory(self) -> None:
        root = self.make_repo({"one": ""})
        (root / "AGENTS.md").write_text("# Policy\n", encoding="utf-8")

        errors = control_plane_layout_errors(root)

        self.assertIn(".codex/hooks: required control-plane directory missing", errors)

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

    def test_missing_provenance_status_fails(self) -> None:
        root = self.make_repo({"one": ""})
        (root / "docs").mkdir()
        (root / "docs" / "skill-inventory.md").write_text(
            "| Name | Purpose | Primary trigger / use case | Maturity | Implementation depth | Evaluation level | Provenance | Overlapping / adjacent skills |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| `one` | x | x | Specialized | prompt-only | none | missing | — |\n",
            encoding="utf-8",
        )
        errors = validate(root)
        self.assertTrue(any("invalid provenance status" in error for error in errors))

    def test_duplicate_core_trigger_declaration_fails(self) -> None:
        root = self.make_repo({"one": "## Minimum contract\n\n- **Trigger and exclusion:** one\n- **Trigger and exclusion:** two\n"})
        (root / "docs").mkdir()
        (root / "docs" / "skill-inventory.md").write_text(
            "| Name | Purpose | Primary trigger / use case | Maturity | Implementation depth | Evaluation level | Provenance | Overlapping / adjacent skills |\n"
            "|---|---|---|---|---|---|---|---|\n| `one` | x | x | Core | prompt-only | none | unknown | — |\n",
            encoding="utf-8",
        )
        errors = validate(root)
        self.assertTrue(any("exactly one Trigger and exclusion" in error for error in errors))

    def test_malformed_core_contract_bullet_fails(self) -> None:
        root = self.make_repo({"one": "## Minimum contract\n\n - **Trigger and exclusion:** one\n"})
        (root / "docs").mkdir()
        (root / "docs" / "skill-inventory.md").write_text(
            "| Name | Purpose | Primary trigger / use case | Maturity | Implementation depth | Evaluation level | Provenance | Overlapping / adjacent skills |\n"
            "|---|---|---|---|---|---|---|---|\n| `one` | x | x | Core | prompt-only | none | unknown | — |\n",
            encoding="utf-8",
        )
        errors = validate(root)
        self.assertTrue(any("malformed leading whitespace" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
