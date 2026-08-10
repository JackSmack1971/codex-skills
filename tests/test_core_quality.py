import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_repository import validate


class CoreQualityTests(unittest.TestCase):
    def test_core_contract_requires_each_dimension(self):
        root = Path(tempfile.mkdtemp())
        (root / "skills" / "one" / "tests").mkdir(parents=True)
        (root / "skills" / "one" / "SKILL.md").write_text("---\nname: one\ndescription: test\n---\n## Minimum contract\n- **Trigger and exclusion:** x\n", encoding="utf-8")
        (root / "skills" / "one" / "tests" / "evaluation-cases.md").write_text("# Manual evaluation cases (not automated tests)\n\n1. **Normal:** ok\n2. **Negative:** ok\n3. **Boundary:** ok\n", encoding="utf-8")
        (root / "skills" / "catalog.json").write_text(json.dumps({"skills": [{"name": "one", "path": "skills/one/SKILL.md", "capability_level": "prompt-only", "validation_artifacts": []}]}), encoding="utf-8")
        (root / "docs").mkdir()
        (root / "docs" / "evaluation-inventory.json").write_text(json.dumps({"version": 1, "levels": ["none", "manual-prose", "deterministic-validator", "automated-behavioral"], "skills": {"one": {"level": "manual-prose", "evidence": "skills/one/tests/evaluation-cases.md", "command": "manual review"}}}), encoding="utf-8")
        (root / "docs" / "skill-inventory.md").write_text("| Name | Purpose | Primary trigger / use case | Maturity |\n|---|---|---|---|\n| `one` | x | x | Core |\n", encoding="utf-8")
        (root / "docs" / "core-quality.json").write_text(json.dumps({"version": 1, "dimensions": ["trigger", "inputs", "workflow", "output", "failure-stop", "security", "evaluation", "runtime-claims", "references"], "skills": {"one": ["trigger", "inputs", "workflow", "output", "failure-stop", "security", "evaluation", "runtime-claims", "references"]}}), encoding="utf-8")
        errors = validate(root)
        self.assertTrue(any("missing quality dimension inputs" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
