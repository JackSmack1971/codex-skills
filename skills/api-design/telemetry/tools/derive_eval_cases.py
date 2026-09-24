from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from common import SCHEMA_EVAL, append_jsonl, load_jsonl, utc_now


def eval_id(finding_id: str) -> str:
    return "E-" + hashlib.sha256(finding_id.encode()).hexdigest()[:12].upper()


def convert(f: dict[str, Any], *, min_confidence: float, supported_only: bool) -> dict[str, Any] | None:
    if supported_only and f.get("status") != "supported":
        return None
    confidence = f.get("confidence")
    if not isinstance(confidence, (int, float)) or confidence < min_confidence:
        return None

    kind = str(f.get("finding_type") or "unknown")
    fid = str(f.get("finding_id") or "unknown")
    check: dict[str, Any]
    eval_kind = "hybrid"
    expected = "The target skill should avoid recurrence of the evidence-backed failure while preserving valid behavior."

    if kind == "retry_or_command_thrashing":
        eval_kind = "deterministic"
        expected = "Equivalent command/retry work should not repeat without new evidence or an explicit recovery reason."
        check = {"metric": "max_repeated_command_hash_per_run", "operator": "<=", "value": 1, "note": "Review legitimate retry workflows before promotion."}
    elif kind == "verification_failure":
        eval_kind = "deterministic"
        expected = "Required verification should complete successfully for representative fixtures."
        check = {"event": "verification", "expected_outcome": "success", "phase": f.get("metrics", {}).get("phase")}
    elif kind == "repeated_failure":
        eval_kind = "hybrid"
        expected = "Representative runs should not reproduce the recurring failure class after the proposed remediation."
        check = {"metric": "failure_class_occurrences", "failure_finding": fid, "operator": "==", "value": 0}
    elif kind == "user_correction":
        eval_kind = "rubric"
        expected = "The behavior that triggered the explicit user correction should be prevented without overfitting to one prompt."
        check = {"rubric_required": True, "note": "Manual review of correction context is mandatory before promotion."}
    elif kind == "latency_outlier_cluster":
        eval_kind = "hybrid"
        expected = "The remediated workflow should not regress completion quality while materially reducing the identified outlier path."
        check = {"metric": "duration_distribution", "comparison": "candidate_vs_baseline", "note": "Use representative samples; do not gate on a single duration."}
    elif kind == "telemetry_incomplete_run":
        eval_kind = "deterministic"
        expected = "Every telemetry run start should have a terminal run event or an explicit interrupted state."
        check = {"metric": "started_without_terminal", "operator": "==", "value": 0}
    else:
        check = {"rubric_required": True}

    return {
        "schema": SCHEMA_EVAL,
        "eval_id": eval_id(fid),
        "source_finding_id": fid,
        "title": f"Regression candidate for {kind.replace('_', ' ')}",
        "kind": eval_kind,
        "expected_behavior": expected,
        "check": check,
        "source_run_ids": f.get("run_ids", []),
        "source_confidence": confidence,
        "promotion_status": "candidate",
        "requires_review": True,
        "generated_at": utc_now(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert evidence-backed findings into review-required eval candidates.")
    parser.add_argument("findings", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--min-confidence", type=float, default=0.6)
    parser.add_argument("--supported-only", action="store_true")
    args = parser.parse_args()

    findings = load_jsonl(args.findings.resolve())
    candidates = [c for f in findings if (c := convert(f, min_confidence=args.min_confidence, supported_only=args.supported_only))]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("", encoding="utf-8")
    for candidate in candidates:
        append_jsonl(args.out, candidate)
    print(json.dumps({"findings": len(findings), "eval_candidates": len(candidates), "output": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()
