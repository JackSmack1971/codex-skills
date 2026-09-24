from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_EVENT = "skilltelemetry.event.v1"
SCHEMA_INSPECTION = "skilltelemetry.inspection.v1"
SCHEMA_MANIFEST = "skilltelemetry.manifest.v1"
SCHEMA_FINDING = "skilltelemetry.finding.v1"
SCHEMA_EVAL = "skilltelemetry.eval-candidate.v1"

EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "telemetry",
    ".skill-telemetry",
    "dist",
    "build",
}

TEXT_EXTENSIONS = {
    ".md", ".txt", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
    ".json", ".jsonl", ".toml", ".yaml", ".yml", ".sh", ".bash", ".ps1",
    ".bat", ".cmd", ".rs", ".go", ".java", ".kt", ".rb", ".php", ".sql",
    ".html", ".css", ".xml", ".ini", ".cfg", ".conf",
}

SECRET_KEY_RE = re.compile(
    r"(?:api[_-]?key|secret|token|password|passwd|credential|authorization|cookie|private[_-]?key)",
    re.IGNORECASE,
)
SECRET_VALUE_RES = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]+=*", re.IGNORECASE),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8", errors="replace"))


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(value, separators=(",", ":"), sort_keys=True, ensure_ascii=False) + "\n"
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(line)
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            pass


def load_jsonl(path: Path, *, max_bytes: int = 50_000_000) -> list[dict[str, Any]]:
    if path.stat().st_size > max_bytes:
        raise ValueError(f"Refusing oversized JSONL file: {path}")
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for idx, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{idx}: {exc}") from exc
            if isinstance(value, dict):
                out.append(value)
    return out


def iter_target_files(root: Path, *, max_file_bytes: int = 2_000_000) -> Iterable[Path]:
    root = root.resolve()
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in rel.parts[:-1]):
            continue
        try:
            if path.stat().st_size > max_file_bytes:
                continue
        except OSError:
            continue
        yield path


def is_probably_text(path: Path, data: bytes | None = None) -> bool:
    if path.name == "SKILL.md" or path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    if data is None:
        try:
            data = path.read_bytes()[:4096]
        except OSError:
            return False
    return b"\x00" not in data


def target_fingerprint(root: Path) -> tuple[str, list[dict[str, Any]]]:
    root = root.resolve()
    records: list[dict[str, Any]] = []
    hasher = hashlib.sha256()
    for path in iter_target_files(root):
        rel = path.relative_to(root).as_posix()
        data = path.read_bytes()
        digest = sha256_bytes(data)
        records.append({"path": rel, "bytes": len(data), "sha256": digest})
        hasher.update(rel.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(digest.encode("ascii"))
        hasher.update(b"\n")
    return hasher.hexdigest(), records


def parse_skill_frontmatter(skill_md: Path) -> dict[str, str | None]:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    result: dict[str, str | None] = {"name": None, "description": None, "version": None}
    if not text.startswith("---"):
        return result
    lines = text.splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError:
        return result
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        if key in result:
            result[key] = value.strip().strip("\"'") or None
    return result


def redact(value: Any) -> tuple[Any, int]:
    """Recursively redact values with sensitive keys/patterns."""
    count = 0
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if SECRET_KEY_RE.search(str(key)):
                out[str(key)] = "[REDACTED]"
                count += 1
            else:
                redacted, c = redact(item)
                out[str(key)] = redacted
                count += c
        return out, count
    if isinstance(value, list):
        out_list = []
        for item in value:
            redacted, c = redact(item)
            out_list.append(redacted)
            count += c
        return out_list, count
    if isinstance(value, str):
        text = value
        for pattern in SECRET_VALUE_RES:
            text, n = pattern.subn("[REDACTED]", text)
            count += n
        return text, count
    return value, count


def command_class(command: str) -> str | None:
    stripped = command.strip()
    if not stripped:
        return None
    # Conservative tokenization: no shell evaluation.
    first = re.split(r"\s+", stripped, maxsplit=1)[0]
    first = first.strip("'\"")
    return Path(first).name or None


def safe_relpath(path_text: str, cwd: str | None = None) -> str:
    try:
        path = Path(path_text)
        if not path.is_absolute():
            return path.as_posix()
        if cwd:
            base = Path(cwd).resolve()
            try:
                return path.resolve().relative_to(base).as_posix()
            except (ValueError, OSError):
                pass
        return f"abs:{sha256_text(str(path))[:16]}"
    except Exception:
        return f"path:{sha256_text(path_text)[:16]}"


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    code: str
    message: str


def require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value
