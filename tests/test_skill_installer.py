import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "skill-installer" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location("skill_installer", SCRIPT_DIR / "install-skill-from-github.py")
installer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = installer
SPEC.loader.exec_module(installer)


class SkillInstallerTests(unittest.TestCase):
    def test_default_destination_uses_isolated_home(self):
        with tempfile.TemporaryDirectory() as home, mock.patch.dict(
            os.environ, {"HOME": home, "CODEX_HOME": str(Path(home) / "legacy")}
        ):
            self.assertEqual(installer._default_dest(), str(Path(home) / ".agents" / "skills"))

    def test_explicit_destination_still_works_without_network(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "repo" / "demo"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text("---\nname: demo\ndescription: Demo\n---\n", encoding="utf-8")
            destination = root / "chosen"
            with mock.patch.object(installer, "_prepare_repo", return_value=str(root / "repo")):
                result = installer.main(
                    ["--repo", "owner/repo", "--path", "demo", "--dest", str(destination)]
                )
            self.assertEqual(result, 0)
            self.assertTrue((destination / "demo" / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
