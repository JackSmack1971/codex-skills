from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

from analyze_telemetry import load_events


def metrics(root: Path, allowed: set[str]) -> dict[str, Any]:
    events = [e for e in load_events(root) if e.get("attribution") in allowed]
    runs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in events:
        if isinstance(e.get("run_id"), str):
            runs[e["run_id"]].append(e)

    terminals = []
    failures = 0
    retries = 0
    corrections = 0
    durations: list[float] = []
    repeated_command_excess = 0
    for items in runs.values():
        terminal = next((e for e in reversed(items) if e.get("event") == "run.finished"), None)
        if terminal:
            terminals.append(terminal)
            if isinstance(terminal.get("duration_ms"), (int, float)):
                durations.append(float(terminal["duration_ms"]))
        failures += sum(1 for e in items if e.get("outcome") == "failure" or e.get("event") == "failure")
        retries += sum(1 for e in items if e.get("event") == "retry")
        retries += sum(int(e.get("retry_count") or 0) for e in items if isinstance(e.get("retry_count"), int))
        corrections += sum(1 for e in items if e.get("event") == "user.correction")
        hashes = [
            e.get("evidence", {}).get("command_sha256")
            for e in items
            if isinstance(e.get("evidence"), dict) and e.get("evidence", {}).get("command_sha256")
        ]
        for count in Counter(hashes).values():
            repeated_command_excess += max(0, count - 1)

    success = sum(1 for e in terminals if e.get("outcome") == "success")
    denom = len(terminals)
    return {
        "events": len(events),
        "runs": len(runs),
        "terminal_runs": denom,
        "success_rate": (success / denom) if denom else None,
        "failure_events_per_run": failures / len(runs) if runs else None,
        "retry_signals_per_run": retries / len(runs) if runs else None,
        "user_corrections": corrections,
        "repeated_command_excess_per_run": repeated_command_excess / len(runs) if runs else None,
        "median_duration_ms": median(durations) if durations else None,
    }


def delta(candidate: float | int | None, baseline: float | int | None) -> float | None:
    if candidate is None or baseline is None:
        return None
    return float(candidate) - float(baseline)


def gate(b: dict[str, Any], c: dict[str, Any], args: argparse.Namespace) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if min(b["terminal_runs"], c["terminal_runs"]) < args.min_terminal_runs:
        return "INCONCLUSIVE", [f"Need at least {args.min_terminal_runs} terminal runs in both samples."]

    if b["success_rate"] is not None and c["success_rate"] is not None:
        if c["success_rate"] < b["success_rate"] - args.max_success_rate_drop:
            reasons.append("candidate success rate regressed beyond threshold")
    if b["failure_events_per_run"] is not None and c["failure_events_per_run"] is not None:
        if c["failure_events_per_run"] > b["failure_events_per_run"] + args.max_failure_increase:
            reasons.append("candidate failure events per run increased beyond threshold")
    if b["repeated_command_excess_per_run"] is not None and c["repeated_command_excess_per_run"] is not None:
        if c["repeated_command_excess_per_run"] > b["repeated_command_excess_per_run"] + args.max_repeat_increase:
            reasons.append("candidate repeated-command excess increased beyond threshold")
    if c["user_corrections"] > b["user_corrections"] + args.max_correction_increase:
        reasons.append("candidate user corrections increased beyond threshold")
    return ("FAIL", reasons) if reasons else ("PASS", ["No configured regression threshold was exceeded."])


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare baseline and candidate telemetry without assuming statistical significance.")
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--allowed-attribution", default="semantic,confirmed")
    parser.add_argument("--gate", action="store_true", help="Apply explicit non-regression thresholds; otherwise decision is INCONCLUSIVE.")
    parser.add_argument("--min-terminal-runs", type=int, default=3)
    parser.add_argument("--max-success-rate-drop", type=float, default=0.0)
    parser.add_argument("--max-failure-increase", type=float, default=0.0)
    parser.add_argument("--max-repeat-increase", type=float, default=0.0)
    parser.add_argument("--max-correction-increase", type=int, default=0)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    allowed = {x.strip() for x in args.allowed_attribution.split(",") if x.strip()}
    b = metrics(args.baseline.resolve(), allowed)
    c = metrics(args.candidate.resolve(), allowed)
    decision, reasons = gate(b, c, args) if args.gate else ("INCONCLUSIVE", ["No gate requested; metrics are descriptive."])
    result = {
        "decision": decision,
        "reasons": reasons,
        "baseline": b,
        "candidate": c,
        "delta": {key: delta(c.get(key), b.get(key)) for key in sorted(set(b) | set(c)) if isinstance(b.get(key), (int, float)) or isinstance(c.get(key), (int, float))},
        "caveat": "This comparator is descriptive/non-regression oriented; it does not claim statistical significance.",
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
