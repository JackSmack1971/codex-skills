"""Run the repository's deterministic, offline skill-quality gate."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILLS = "skills"
EVALUATION_INVENTORY = "docs/evaluation-inventory.json"
FRESHNESS_REGISTRY = "docs/skill-freshness.json"
EVALUATION_LEVELS = {"none", "manual-prose", "deterministic-validator", "automated-behavioral"}
QUALITY_DIMENSIONS = ["trigger", "inputs", "workflow", "output", "failure-stop", "security", "evaluation", "runtime-claims", "references"]
PROVENANCE_STATUSES = {"original", "adapted", "vendored", "unknown"}
SUPPORTED_FRONTMATTER = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
PORTABLE_PATH = re.compile(r"(?:[A-Za-z]:[\\/]Users[\\/][A-Za-z0-9._-]+|/(?:Users|home)/[A-Za-z0-9._-]+)")
SECRET = re.compile(r"(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)", re.I)


def frontmatter(text: str) -> tuple[dict[str, str], str | None]:
    if not text.startswith("---\n"):
        return {}, "missing opening delimiter"
    lines = text.splitlines()
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return {}, "missing closing delimiter"
    values: dict[str, str] = {}
    block_key: str | None = None
    block: list[str] = []
    for line in lines[1:end]:
        if block_key:
            if line.startswith((" ", "\t")) or not line.strip():
                block.append(line.strip())
                continue
            values[block_key] = " ".join(part for part in block if part)
            block_key = None
            block = []
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line or line[:1].isspace():
            return {}, f"invalid frontmatter line: {line}"
        key, value = line.split(":", 1)
        value = value.strip()
        if value in {">", ">-", "|", "|-"}:
            block_key = key.strip()
            continue
        values[key.strip()] = value.strip("'\"")
    if block_key:
        values[block_key] = " ".join(part for part in block if part)
    return values, None


def local_links(text: str) -> list[str]:
    links = []
    for raw in LINK.findall(text):
        target = raw.strip().split("#", 1)[0].strip("<>")
        if target and ("/" in target or "." in Path(target).name) and not re.match(r"(?:[a-z]+:)?//|mailto:", target, re.I) and not target.startswith("#"):
            links.append(target)
    return links


def referenced_paths(text: str) -> list[str]:
    paths: set[str] = set()
    for code in re.findall(r"`([^`]+)`", text):
        if "://" in code:
            continue
        command = code.strip()
        if command.startswith(("scripts/", "references/", "resources/", "assets/", "tests/", "templates/")):
            paths.update(re.findall(r"(?:scripts|references|resources|assets|tests|templates)/[A-Za-z0-9._/-]+", command))
    return sorted(paths)


def schema_errors(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    checks = {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool), "boolean": isinstance(value, bool),
    }
    if expected and not checks.get(expected, True):
        return [f"{path}: expected {expected}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value is not in enum")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0): errors.append(f"{path}: too short")
        if schema.get("pattern") and not re.search(schema["pattern"], value): errors.append(f"{path}: pattern mismatch")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0): errors.append(f"{path}: too few items")
        if isinstance(schema.get("items"), dict):
            for i, item in enumerate(value): errors.extend(schema_errors(item, schema["items"], f"{path}[{i}]"))
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value: errors.append(f"{path}: missing {key}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            errors.extend(f"{path}.{key}: unknown property" for key in value if key not in props)
        for key, child in props.items():
            if key in value: errors.extend(schema_errors(value[key], child, f"{path}.{key}"))
    return errors


def validate_freshness(root: Path, actual: set[str]) -> list[str]:
    errors: list[str] = []
    path = root / FRESHNESS_REGISTRY
    if not path.is_file():
        return [f"{FRESHNESS_REGISTRY}: missing"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{FRESHNESS_REGISTRY}: invalid JSON: {exc}"]
    if not isinstance(data, dict) or data.get("version") != 1:
        return [f"{FRESHNESS_REGISTRY}: version 1 metadata required"]
    errors.extend(_validate_freshness_date(FRESHNESS_REGISTRY, data.get("last_updated"), "last_updated"))
    records = data.get("skills")
    exemptions = data.get("exemptions")
    if not isinstance(records, dict) or not isinstance(exemptions, dict):
        return [f"{FRESHNESS_REGISTRY}: skills and exemptions must be objects"]
    if set(records) & set(exemptions):
        errors.append(f"{FRESHNESS_REGISTRY}: a skill cannot be both sensitive and exempt")
    if set(records) | set(exemptions) != actual:
        errors.append(f"{FRESHNESS_REGISTRY}: coverage does not match skill directories")
    if (set(records) | set(exemptions)) - actual:
        errors.append(f"{FRESHNESS_REGISTRY}: unknown skill record")
    for name, metadata in records.items():
        prefix = f"{FRESHNESS_REGISTRY}: {name}"
        if not isinstance(metadata, dict):
            errors.append(f"{prefix}: metadata must be an object")
            continue
        required = {"status", "technology", "checked_version", "last_verified", "runtime_detection_required", "verification", "references"}
        if set(metadata) != required:
            errors.append(f"{prefix}: sensitive metadata keys mismatch")
            continue
        if metadata.get("status") != "version-sensitive":
            errors.append(f"{prefix}: status must be version-sensitive")
        if not isinstance(metadata.get("technology"), list) or not metadata["technology"] or not all(isinstance(item, str) and item for item in metadata["technology"]):
            errors.append(f"{prefix}: technology must be a non-empty string list")
        if not isinstance(metadata.get("checked_version"), str) or not metadata["checked_version"]:
            errors.append(f"{prefix}: checked_version is required")
        if not isinstance(metadata.get("verification"), str) or not metadata["verification"]:
            errors.append(f"{prefix}: verification is required")
        if not isinstance(metadata.get("runtime_detection_required"), bool):
            errors.append(f"{prefix}: runtime_detection_required must be boolean")
        errors.extend(_validate_freshness_date(prefix, metadata.get("last_verified")))
        errors.extend(_validate_freshness_references(root, prefix, metadata.get("references")))
    for name, metadata in exemptions.items():
        prefix = f"{FRESHNESS_REGISTRY}: {name}"
        if not isinstance(metadata, dict) or set(metadata) != {"status", "exemption", "references"}:
            errors.append(f"{prefix}: exemption metadata keys mismatch")
            continue
        if metadata.get("status") != "exempt":
            errors.append(f"{prefix}: status must be exempt")
        if not isinstance(metadata.get("exemption"), str) or not metadata["exemption"]:
            errors.append(f"{prefix}: exemption is required")
        errors.extend(_validate_freshness_references(root, prefix, metadata.get("references")))
    return errors


def _validate_freshness_date(prefix: str, value: Any, field: str = "last_verified") -> list[str]:
    if not isinstance(value, str):
        return [f"{prefix}: {field} must be ISO date"]
    try:
        checked = date.fromisoformat(value)
    except ValueError:
        return [f"{prefix}: {field} must be ISO date"]
    return [f"{prefix}: {field} cannot be in the future"] if checked > date.today() else []


def _validate_freshness_references(root: Path, prefix: str, value: Any) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        return [f"{prefix}: references must be a non-empty string list"]
    errors = []
    for reference in value:
        target = (root / reference).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{prefix}: reference escapes repository: {reference}")
        else:
            if not target.is_file():
                errors.append(f"{prefix}: missing reference: {reference}")
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    skills_root = root / SKILLS
    skill_dirs = sorted(p for p in skills_root.iterdir() if p.is_dir()) if skills_root.is_dir() else []
    records: list[dict[str, Any]] = []
    catalog = skills_root / "catalog.json"
    if catalog.is_file():
        try:
            data = json.loads(catalog.read_text(encoding="utf-8"))
            records = data.get("skills", []) if isinstance(data, dict) else []
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"skills/catalog.json: invalid JSON: {exc}")
    else:
        errors.append("skills/catalog.json: missing")

    evaluation_path = root / EVALUATION_INVENTORY
    evaluation: dict[str, Any] = {}
    if not evaluation_path.is_file():
        errors.append(f"{EVALUATION_INVENTORY}: missing")
    else:
        try:
            evaluation_data = json.loads(evaluation_path.read_text(encoding="utf-8"))
            if evaluation_data.get("version") != 1 or evaluation_data.get("levels") != ["none", "manual-prose", "deterministic-validator", "automated-behavioral"]:
                errors.append(f"{EVALUATION_INVENTORY}: invalid rubric metadata")
            evaluation = evaluation_data.get("skills", {})
            if not isinstance(evaluation, dict):
                errors.append(f"{EVALUATION_INVENTORY}: skills must be an object")
                evaluation = {}
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{EVALUATION_INVENTORY}: invalid JSON: {exc}")
    names: list[str] = []
    for skill in skill_dirs:
        path = skill / "SKILL.md"
        if not path.is_file():
            errors.append(f"{skill.relative_to(root).as_posix()}: SKILL.md missing")
            continue
        try: text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{path.relative_to(root).as_posix()}: unreadable: {exc}")
            continue
        meta, issue = frontmatter(text)
        rel = path.relative_to(root).as_posix()
        if issue: errors.append(f"{rel}: {issue}")
        unknown = sorted(set(meta) - SUPPORTED_FRONTMATTER)
        if unknown: errors.append(f"{rel}: unsupported frontmatter: {', '.join(unknown)}")
        name = meta.get("name", "")
        if not name or not KEBAB.fullmatch(name): errors.append(f"{rel}: name must be lowercase kebab-case")
        if name != skill.name: errors.append(f"{rel}: name does not match directory {skill.name}")
        if not meta.get("description"): errors.append(f"{rel}: description is required")
        names.append(name)
        for md in [path, *sorted(skill.rglob("*.md"))]:
            try: md_text = md.read_text(encoding="utf-8")
            except OSError as exc:
                errors.append(f"{md.relative_to(root).as_posix()}: unreadable: {exc}")
                continue
            for link in local_links(md_text):
                target = (md.parent / link).resolve()
                try: target.relative_to(skill.resolve())
                except ValueError: errors.append(f"{md.relative_to(root).as_posix()}: reference escapes skill: {link}"); continue
                if not target.exists(): errors.append(f"{md.relative_to(root).as_posix()}: missing reference: {link}")
            for reference in referenced_paths(md_text):
                target = (skill / reference.rstrip(".,:;`\"'\""))
                if not target.exists(): errors.append(f"{md.relative_to(root).as_posix()}: missing referenced file: {reference}")
            if PORTABLE_PATH.search(md_text): errors.append(f"{md.relative_to(root).as_posix()}: machine-specific absolute path")
            if SECRET.search(md_text): errors.append(f"{md.relative_to(root).as_posix()}: secret-like value")
    if len(names) != len(set(names)): errors.append("skill frontmatter names are not unique")

    actual = {skill.name for skill in skill_dirs}
    errors.extend(validate_freshness(root, actual))
    if set(evaluation) != actual:
        errors.append(f"{EVALUATION_INVENTORY}: skill coverage does not match directories")
    for name, metadata in evaluation.items():
        if not isinstance(metadata, dict) or set(metadata) != {"level", "evidence", "command"}:
            errors.append(f"{EVALUATION_INVENTORY}: {name}: metadata must contain level, evidence, command")
            continue
        level = metadata.get("level")
        evidence = metadata.get("evidence")
        command = metadata.get("command")
        if level not in EVALUATION_LEVELS:
            errors.append(f"{EVALUATION_INVENTORY}: {name}: invalid evaluation level")
        if not isinstance(evidence, str) or not isinstance(command, str) or not evidence or not command:
            errors.append(f"{EVALUATION_INVENTORY}: {name}: evidence and command are required strings")
        if evidence != "none" and not (root / evidence).is_file():
            errors.append(f"{EVALUATION_INVENTORY}: {name}: missing evidence {evidence}")
        cases = root / f"skills/{name}/tests/evaluation-cases.md"
        if cases.is_file():
            case_text = cases.read_text(encoding="utf-8")
            if "not automated tests" not in case_text.lower():
                errors.append(f"{cases.relative_to(root).as_posix()}: must identify prose cases as non-automated")
            if len(re.findall(r"^\s*\d+\.\s", case_text, re.M)) < 3:
                errors.append(f"{cases.relative_to(root).as_posix()}: requires at least 3 scenarios")

    inventory_text = (root / "docs/skill-inventory.md").read_text(encoding="utf-8") if (root / "docs/skill-inventory.md").is_file() else ""
    inventory_rows: dict[str, list[str]] = {}
    for line in inventory_text.splitlines():
        if line.startswith("| `"):
            fields = [field.strip() for field in line.strip().strip("|").split("|")]
            if len(fields) != 8:
                errors.append("docs/skill-inventory.md: inventory rows must have 8 columns")
                continue
            name = fields[0].strip("`")
            status = fields[6].split(";", 1)[0].strip()
            inventory_rows[name] = fields
            if status not in PROVENANCE_STATUSES:
                errors.append(f"docs/skill-inventory.md: {name}: invalid provenance status {status}")
            evidence_link = re.search(rf"\]\([^)]*skills/{re.escape(name)}/", inventory_text)
            if status in {"adapted", "vendored"} and not evidence_link:
                errors.append(f"docs/skill-inventory.md: {name}: provenance evidence link is required")
    if set(inventory_rows) != actual:
        errors.append("docs/skill-inventory.md: provenance inventory coverage does not match directories")
    readme = root / "README.md"
    if root == ROOT and (not readme.is_file() or "## Provenance, licensing, and support boundaries" not in readme.read_text(encoding="utf-8")):
        errors.append("README.md: root provenance/licensing section is missing")
    core = set()
    for line in inventory_text.splitlines():
        fields = [field.strip() for field in line.strip().strip("|").split("|")]
        if len(fields) >= 4 and fields[0].startswith("`") and fields[3] == "Core":
            core.add(fields[0].strip("`"))
    for name in sorted(core):
        metadata = evaluation.get(name, {})
        skill_text = (root / f"skills/{name}/SKILL.md").read_text(encoding="utf-8") if (root / f"skills/{name}/SKILL.md").is_file() else ""
        contract_match = re.search(r"^## Minimum contract\n(?P<body>.*?)(?=^## |\Z)", skill_text, re.M | re.S)
        if not contract_match:
            errors.append(f"Core skill {name}: minimum contract is missing from SKILL.md")
            contract = ""
        else:
            contract = contract_match.group("body")
            trigger_count = len(re.findall(r"^[- ]+\*\*Trigger and exclusion:\*\*", contract, re.M))
            if trigger_count != 1:
                errors.append(f"Core skill {name}: minimum contract must contain exactly one Trigger and exclusion declaration")
            malformed = [line for line in contract.splitlines() if line and line[0].isspace() and line.lstrip().startswith("-")]
            if malformed:
                errors.append(f"Core skill {name}: minimum contract has malformed leading whitespace on a bullet")
            if any(line and not line.startswith("- ") and re.match(r"\s*\*\*[A-Za-z/-]+:\*\*", line) for line in contract.splitlines()):
                errors.append(f"Core skill {name}: minimum contract labels must use Markdown list bullets")
        labels = {
            "trigger": r"\*\*Trigger and exclusion:\*\*",
            "inputs": r"\*\*Inputs:\*\*",
            "workflow": r"\*\*Bounded workflow:\*\*",
            "output": r"\*\*Output:\*\*",
            "failure-stop": r"\*\*Failure/stop:\*\*",
            "security": r"\*\*Security:\*\*",
            "evaluation": r"\*\*Evaluation:\*\*",
            "runtime-claims": r"\*\*Runtime claims:\*\*",
            "references": r"\*\*References:\*\*",
        }
        for dimension, pattern in labels.items():
            if dimension in {"inputs", "failure-stop", "security", "evaluation", "runtime-claims", "references"}:
                present = re.search(pattern, contract) or re.search(r"^[- ]+\*\*Shared baseline:\*\*", contract, re.M)
            else:
                present = re.search(pattern, contract)
            if not present:
                errors.append(f"Core skill {name}: missing quality dimension {dimension}")
        if metadata.get("level") == "none":
            errors.append(f"Core skill {name}: evaluation level cannot be none")
        cases = root / f"skills/{name}/tests/evaluation-cases.md"
        if not cases.is_file():
            errors.append(f"Core skill {name}: evaluation cases missing")
        else:
            case_text = cases.read_text(encoding="utf-8")
            count = len(re.findall(r"^\s*\d+\.\s", case_text, re.M))
            if count < 3 or not all(re.search(rf"^\s*\d+\.\s+\*\*{kind}:\*\*", case_text, re.M) for kind in ("Normal", "Negative", "Boundary")):
                errors.append(f"Core skill {name}: fewer than 3 evaluation cases")
        artifact_groups = [record.get("validation_artifacts", []) for record in records if isinstance(record, dict) and record.get("name") == name]
        has_helper = any("/scripts/" in artifact or artifact.endswith(".py") for group in artifact_groups for artifact in group)
        if has_helper and metadata.get("level") not in {"deterministic-validator", "automated-behavioral"}:
            errors.append(f"Core skill {name}: executable helper requires deterministic or automated evaluation evidence")

    quality_path = root / "docs/core-quality.json"
    if not quality_path.is_file():
        errors.append("docs/core-quality.json: missing")
    else:
        try:
            quality = json.loads(quality_path.read_text(encoding="utf-8"))
            dimensions = QUALITY_DIMENSIONS
            if quality.get("version") != 1 or quality.get("dimensions") != dimensions:
                errors.append("docs/core-quality.json: invalid dimensions")
            if set(quality.get("skills", {})) != core:
                errors.append("docs/core-quality.json: Core skill coverage does not match inventory")
            for name, declared in quality.get("skills", {}).items():
                if declared != dimensions:
                    errors.append(f"docs/core-quality.json: {name}: incomplete quality declaration")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"docs/core-quality.json: invalid JSON: {exc}")
    behavioral_path = root / "benchmarks/core/behavioral-cases.json"
    if not behavioral_path.is_file():
        errors.append("benchmarks/core/behavioral-cases.json: missing")
    else:
        try:
            behavioral = json.loads(behavioral_path.read_text(encoding="utf-8"))
            by_skill: dict[str, list[dict[str, Any]]] = {}
            overlap_groups = {
                "review-agent-vs-pr-review": {"review-agent", "pr-review"},
                "feature-implementation-vs-vertical-slice": {"feature-implementation", "vertical-slice"},
                "feature-implementation-vs-test-driven-development": {"feature-implementation", "test-driven-development"},
                "testing-qa-vs-test-driven-development": {"testing-qa", "test-driven-development"},
                "skill-auditor-vs-context-doctor-vs-improve": {"skill-auditor", "context-doctor", "improve"},
                "git-workflow-vs-git-commit-vs-using-git-worktrees": {"git-workflow", "git-commit", "using-git-worktrees"},
                "skill-creator-vs-context7-skill-wizard-vs-plugin-creator": {"skill-creator", "context7-skill-wizard", "plugin-creator"},
            }
            for case in behavioral.get("cases", []):
                if isinstance(case, dict):
                    by_skill.setdefault(case.get("skill_name"), []).append(case)
            if not core.issubset(by_skill):
                errors.append(f"benchmarks/core/behavioral-cases.json: missing Core skills {sorted(core - set(by_skill))}")
            for name in sorted(core):
                cases_for_skill = by_skill.get(name, [])
                if len(cases_for_skill) < 6:
                    errors.append(f"Core skill {name}: behavioral corpus requires at least 6 cases")
                for polarity in ("positive", "negative", "ambiguous"):
                    if sum(case.get("polarity") == polarity for case in cases_for_skill) < 2:
                        errors.append(f"Core skill {name}: behavioral corpus requires 2 {polarity} cases")
                if any(not case.get("expected_required_behaviors") for case in cases_for_skill):
                    errors.append(f"Core skill {name}: every behavioral case needs a required behavior")
                if any(case.get("polarity") == "negative" and not case.get("forbidden_behaviors") for case in cases_for_skill):
                    errors.append(f"Core skill {name}: negative behavioral cases need forbidden behavior")
            for group, expected in overlap_groups.items():
                overlap_actual = {case.get("skill_name") for case in behavioral.get("cases", []) if case.get("overlap_group") == group}
                if overlap_actual != expected:
                    errors.append(f"{group}: behavioral overlap coverage mismatch")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"benchmarks/core/behavioral-cases.json: invalid JSON: {exc}")
    catalog_names = [r.get("name") for r in records if isinstance(r, dict)]
    if len(catalog_names) != len(set(catalog_names)): errors.append("catalog skill names are not unique")
    if set(catalog_names) != actual: errors.append("canonical catalog does not exactly match skill directories")
    for record in records:
        if not isinstance(record, dict): errors.append("catalog record must be an object"); continue
        name = record.get("name", "<unknown>")
        expected = f"skills/{name}/SKILL.md"
        if record.get("path") != expected: errors.append(f"{name}: catalog path must be {expected}")
        for artifact in record.get("validation_artifacts", []):
            candidate = root / artifact
            if Path(artifact).is_absolute() or not candidate.is_file(): errors.append(f"{name}: missing validation artifact {artifact}")
        level = record.get("capability_level")
        if level not in {"prompt-only", "evaluated", "script-backed", "tested"}: errors.append(f"{name}: invalid capability level")
        if level in {"evaluated", "tested"} and not ((root / f"skills/{name}/VERIFICATION.md").is_file() or (root / f"skills/{name}/tests").is_dir()):
            errors.append(f"{name}: {level} skill lacks evaluation/test metadata")

    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts: continue
        try: compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (OSError, SyntaxError) as exc: errors.append(f"{path.relative_to(root).as_posix()}: Python compile failure: {exc}")
    for path in sorted(root.rglob("*.json")):
        try: json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc: errors.append(f"{path.relative_to(root).as_posix()}: invalid JSON: {exc}")
    for schema in sorted(skills_root.rglob("*.schema.json")):
        try: schema_data = json.loads(schema.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): continue
        for fixture in sorted(schema.parent.glob("*example*.json")):
            try: fixture_data = json.loads(fixture.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError): continue
            values = fixture_data.get("findings", []) if schema_data.get("title") == "Repository Hygiene Finding" and isinstance(fixture_data, dict) else [fixture_data]
            for value in values:
                errors.extend(f"{fixture.relative_to(root).as_posix()}: {item}" for item in schema_errors(value, schema_data))

    if (root / ".git").exists():
        tracked = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=False).stdout.decode(errors="replace").split("\0")
        sensitive = re.compile(r"(?:^|/)(?:\.env(?:\..*)?|.*\.(?:pem|key|p12|sqlite|db|log|pyc|pyo)|__pycache__)(?:/|$)", re.I)
        errors.extend(f"tracked sensitive/runtime artifact: {name}" for name in tracked if name and sensitive.search(name))
        if subprocess.run(["git", "grep", "-nI", "-E", r"[[:blank:]]+$", "HEAD", "--"], cwd=root, capture_output=True, check=False).returncode == 0:
            errors.append("committed trailing whitespace")
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    root = Path(argv[0]).resolve() if argv else ROOT
    errors = validate(root)
    if root == ROOT:
        for label, script in (("catalog", "validate_catalog.py"), ("inventory", "validate_skill_inventory.py")):
            result = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, capture_output=True, text=True, check=False)
            if result.returncode: errors.append(f"{label} validator failed: {result.stdout.strip()} {result.stderr.strip()}".strip())
    if errors:
        print("\n".join(errors)); print("REPOSITORY_VALIDATION_FAILED"); return 1
    print(f"SKILLS_VALIDATED={len(list((root / SKILLS).glob('*/SKILL.md')))}")
    if root == ROOT:
        core = set()
        for line in (root / "docs/skill-inventory.md").read_text(encoding="utf-8").splitlines():
            fields = [field.strip() for field in line.strip().strip("|").split("|")]
            if len(fields) >= 4 and fields[0].startswith("`") and fields[3] == "Core":
                core.add(fields[0].strip("`"))
        evaluation = json.loads((root / EVALUATION_INVENTORY).read_text(encoding="utf-8"))["skills"]
        statuses = {}
        for line in (root / "docs/skill-inventory.md").read_text(encoding="utf-8").splitlines():
            if line.startswith("| `"):
                fields = [field.strip() for field in line.strip().strip("|").split("|")]
                if len(fields) == 8:
                    statuses[fields[0].strip("`")] = fields[6].split(";", 1)[0].strip()
        print("PROVENANCE COUNTS")
        for status in ("original", "adapted", "vendored", "unknown"):
            print(f"{status}={sum(value == status for value in statuses.values())}")
        print("REMAINING UNKNOWN")
        for name in sorted(name for name, status in statuses.items() if status == "unknown"):
            print(name)
        freshness_path = root / FRESHNESS_REGISTRY
        if freshness_path.is_file():
            freshness = json.loads(freshness_path.read_text(encoding="utf-8"))
            print("SKILL FRESHNESS")
            actual = {path.parent.name for path in root.joinpath(SKILLS).glob("*/SKILL.md")}
            for name in sorted(actual):
                record = freshness.get("skills", {}).get(name) or freshness.get("exemptions", {}).get(name)
                print(f"{name} | {record.get('status', 'UNKNOWN')} | {record.get('last_verified', 'n/a')}")
        print("CORE EVALUATION MATRIX")
        print("skill | trigger | inputs | workflow | output | failure-stop | security | evaluation | runtime-claims | references | evidence")
        for name in sorted(core):
            metadata = evaluation[name]
            print(f"{name} | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | {metadata['level']}: {metadata['evidence']}")
    print("REPOSITORY_VALIDATION_OK"); return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
