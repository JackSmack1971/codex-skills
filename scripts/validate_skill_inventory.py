"""Verify that docs/skill-inventory.md covers skills/ exactly once."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "skill-inventory.md"
HEADER = "| Name | Purpose | Primary trigger / use case | Maturity | Implementation depth | Evaluation level | Provenance | Overlapping / adjacent skills |"


def main() -> int:
    directories = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
    rows = []
    for line in INVENTORY.read_text(encoding="utf-8").splitlines():
        if line.startswith("| `"):
            fields = [field.strip() for field in line.strip().strip("|").split("|")]
            if len(fields) != 8 or not fields[0].endswith("`"):
                print(f"invalid inventory row: {line}", file=sys.stderr)
                return 1
            rows.append(fields[0][1:-1])
    names = set(rows)
    if HEADER not in INVENTORY.read_text(encoding="utf-8"):
        print("inventory header is missing", file=sys.stderr)
        return 1
    if len(rows) != len(names):
        print("inventory contains duplicate skill names", file=sys.stderr)
        return 1
    if names != directories:
        print(f"missing: {sorted(directories - names)}", file=sys.stderr)
        print(f"extra: {sorted(names - directories)}", file=sys.stderr)
        return 1
    print(f"filesystem skill count: {len(directories)}")
    print(f"inventory skill count: {len(rows)}")
    print("skill inventory matches filesystem: yes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
