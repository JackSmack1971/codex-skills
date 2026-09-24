from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any, Iterable

from common import SCHEMA_FINDING, append_jsonl, load_jsonl, read_json, utc_now


def finding_id(kind: str, key: str) -> str:
    return "F-" + hashlib.sha256(f"{kind}\0{key}".encode()).hexdigest()[:12].upper()


def load_events(data_root: Path, *, include_ambient: bool = False) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    roots = [data_root / "raw"]
    if include_ambient:
        roots.append(data_root / "ambient")
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.jsonl")):
            events.extend(load_jsonl(path))
    return events


def confidence_from_support(support: int, *, base: float = 0.55, step: float = 0.1, cap: float = 0.95) -> float:
    return round(min(cap, base + max(0, support - 1) * step), 2)


def status(confidence: float, support: int, min_support: int, supported_confidence: float) -> str:
    return "supported" if support >= min_support and confidence >= supported_confidence else "candidate"


def build_finding(
    kind: str,
    key: str,
    run_ids: Iterable[str],
    observation: str,
    effect: str | None,
    hypothesis: str | None,
    proposed: str,
    *,
    min_support: int,
    supported_confidence: float,
    confidence: float | None = None,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    runs = sorted(set(run_ids))
    conf = confidence if confidence is not None else confidence_from_support(len(runs))
    return {
        "schema": SCHEMA_FINDING,
        "finding_id": finding_id(kind, key),
        "finding_type": kind,
        "status": status(conf, len(runs), min_support, supported_confidence),
        "confidence": conf,
        "support_count": len(runs),
        "run_ids": runs,
        "observation": observation,
        "effect": effect,
        "hypothesis": hypothesis,
        "proposed_change_class": proposed,
        "requires_review": True,
        "metrics": metrics or {},
        "generated_at": utc_now(),
    }


def analyze(events: list[dict[str, Any]], *, allowed: set[str], min_support: int, supported_confidence: float) -> list[dict[str, Any]]:
    usable = [e for e in events if e.get("attribution") in allowed]
    runs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in usable:
        run_id = event.get("run_id")
        if isinstance(run_id, str):
            runs[run_id].append(event)

    findings: list[dict[str, Any]] = []

    failure_runs: dict[str, set[str]] = defaultdict(set)
    for e in usable:
        failure = e.get("failure_class")
        if isinstance(failure, str) and failure:
            failure_runs[failure].add(str(e.get("run_id")))
    for failure, run_ids in sorted(failure_runs.items()):
        findings.append(build_finding(
            "repeated_failure",
            failure,
            run_ids,
            f"Failure class `{failure}` recurred in {len(run_ids)} attributable run(s).",
            "Repeated failures can indicate a missing precondition, fragile branch, or unstable verification path.",
            "Confirm whether the failure is caused by the skill rather than repository/environment variance before changing instructions.",
            "runtime_check" if "precondition" in failure or "environment" in failure else "eval",
            min_support=min_support,
            supported_confidence=supported_confidence,
        ))

    thrash_runs: dict[str, set[str]] = defaultdict(set)
    thrash_counts: Counter[str] = Counter()
    for run_id, items in runs.items():
        hashes = [
            e.get("evidence", {}).get("command_sha256")
            for e in items
            if isinstance(e.get("evidence"), dict) and e.get("evidence", {}).get("command_sha256")
        ]
        counts = Counter(hashes)
        for command_hash, count in counts.items():
            if count >= 2:
                thrash_runs[str(command_hash)].add(run_id)
                thrash_counts[str(command_hash)] += count
        if any((isinstance(e.get("retry_count"), int) and e["retry_count"] > 0) or e.get("event") == "retry" for e in items):
            thrash_runs["retry_signal"].add(run_id)
    for key, run_ids in sorted(thrash_runs.items()):
        findings.append(build_finding(
            "retry_or_command_thrashing",
            key,
            run_ids,
            f"Repeated command/retry behavior appeared in {len(run_ids)} attributable run(s).",
            "Repeated operations increase latency/cost and can signal ambiguous instructions or missing readiness checks.",
            "Determine whether repetition was required by the task before encoding a maximum-repeat invariant.",
            "eval",
            min_support=min_support,
            supported_confidence=supported_confidence,
            confidence=confidence_from_support(len(run_ids), base=0.55),
            metrics={"observed_repetitions": thrash_counts.get(key)},
        ))

    verification_failures: dict[str, set[str]] = defaultdict(set)
    for e in usable:
        if e.get("event") == "verification" and e.get("outcome") == "failure":
            key = str(e.get("phase") or e.get("failure_class") or "verification")
            verification_failures[key].add(str(e.get("run_id")))
    for key, run_ids in sorted(verification_failures.items()):
        findings.append(build_finding(
            "verification_failure",
            key,
            run_ids,
            f"Verification phase `{key}` failed in {len(run_ids)} attributable run(s).",
            "A workflow that reaches verification but fails may have an implementation defect or an under-specified completion criterion.",
            "Use the failing verification artifact to decide whether the durable fix belongs in runtime logic, the skill, or an eval.",
            "eval",
            min_support=min_support,
            supported_confidence=supported_confidence,
            confidence=confidence_from_support(len(run_ids), base=0.6),
        ))

    correction_runs: set[str] = set()
    for e in usable:
        if e.get("event") == "user.correction":
            correction_runs.add(str(e.get("run_id")))
    if correction_runs:
        findings.append(build_finding(
            "user_correction",
            "explicit_user_correction",
            correction_runs,
            f"Explicit user correction was recorded in {len(correction_runs)} attributable run(s).",
            "User corrections are high-value negative signals but may be task-specific.",
            "Review the correction context manually and convert only durable behavior into an eval.",
            "eval",
            min_support=min_support,
            supported_confidence=supported_confidence,
            confidence=min(0.95, 0.75 + 0.05 * len(correction_runs)),
        ))

    incomplete_runs = []
    for run_id, items in runs.items():
        if any(e.get("event") == "run.started" for e in items) and not any(e.get("event") == "run.finished" for e in items):
            incomplete_runs.append(run_id)
    if incomplete_runs:
        findings.append(build_finding(
            "telemetry_incomplete_run",
            "missing_run_finished",
            incomplete_runs,
            f"{len(incomplete_runs)} telemetry run(s) started without a matching `run.finished` event.",
            "Incomplete runs weaken causal analysis and may hide failures.",
            "Treat this as an observability defect before interpreting target-skill quality.",
            "observability",
            min_support=min_support,
            supported_confidence=supported_confidence,
            confidence=confidence_from_support(len(incomplete_runs), base=0.7),
        ))

    # Summary-level latency candidate, only when explicit durations exist on finished runs.
    durations: list[tuple[str, float]] = []
    for run_id, items in runs.items():
        finish = next((e for e in reversed(items) if e.get("event") == "run.finished" and isinstance(e.get("duration_ms"), (int, float))), None)
        if finish is not None:
            durations.append((run_id, float(finish["duration_ms"])))
    if len(durations) >= max(3, min_support):
        values = [x[1] for x in durations]
        med = median(values)
        high = [(run_id, value) for run_id, value in durations if value > med * 2 and value - med > 1000]
        if len(high) >= min_support:
            findings.append(build_finding(
                "latency_outlier_cluster",
                "run_duration_gt_2x_median",
                [x[0] for x in high],
                f"{len(high)} run(s) exceeded twice the observed median duration ({med:.0f} ms).",
                "Persistent latency outliers can indicate retry loops or expensive workflow branches.",
                "Correlate outliers with decision and operation events before changing the skill.",
                "eval",
                min_support=min_support,
                supported_confidence=supported_confidence,
                confidence=confidence_from_support(len(high), base=0.55),
                metrics={"median_duration_ms": med, "outlier_durations_ms": [x[1] for x in high]},
            ))

    findings.sort(key=lambda f: (-f["confidence"], f["finding_type"], f["finding_id"]))
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze normalized skill telemetry and write evidence-backed findings.")
    parser.add_argument("sidecar", type=Path)
    parser.add_argument("--data-root", type=Path, help="Runtime data root; defaults to the sidecar directory.")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--min-support", type=int)
    parser.add_argument("--supported-confidence", type=float)
    parser.add_argument("--include-ambient", action="store_true")
    args = parser.parse_args()

    sidecar = args.sidecar.resolve()
    config = read_json(sidecar / "config.json")
    analysis_cfg = config.get("analysis", {}) if isinstance(config, dict) else {}
    min_support = args.min_support or int(analysis_cfg.get("min_support", 2))
    supported_confidence = args.supported_confidence or float(analysis_cfg.get("supported_confidence", 0.65))
    allowed = set(analysis_cfg.get("include_attribution", ["semantic", "confirmed"]))
    if args.include_ambient:
        allowed.add("ambient")
    data_root = (args.data_root or sidecar).resolve()
    events = load_events(data_root, include_ambient=args.include_ambient)
    findings = analyze(events, allowed=allowed, min_support=min_support, supported_confidence=supported_confidence)

    out = args.out or sidecar / "derived" / "findings.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("", encoding="utf-8")
    for finding in findings:
        append_jsonl(out, finding)

    summary = {
        "events_total": len(events),
        "events_used": sum(1 for e in events if e.get("attribution") in allowed),
        "allowed_attribution": sorted(allowed),
        "findings": len(findings),
        "supported": sum(1 for f in findings if f["status"] == "supported"),
        "output": str(out),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
