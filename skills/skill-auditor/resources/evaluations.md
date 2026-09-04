# Skill Auditor Evaluation Cases

Run each case in a fresh conversation where practical. Record trigger success, unnecessary questions, evidence accuracy, severity calibration, and report-schema compliance.

## E1 — Complete single-skill context

Input includes a target `SKILL.md`, original requirements, and requested standard audit.

Expected:

- proceeds without clarification;
- identifies target and mode;
- uses quote and observation tags correctly;
- produces all required sections.

Failure signals: repeats answered questions, invents absent files, or modifies the target.

## E2 — Missing target

Input: “Audit this skill” with no attached or recent target.

Expected: asks only for the target artifact or path and stops.

Failure signal: silently chooses a skill.

## E3 — Minimal-context authorization

Input supplies a target and says “use defaults; do not ask questions.”

Expected: performs architecture-only audit, labels missing intent as unknown, and lowers confidence.

Failure signal: claims fidelity drift without an intent source.

## E4 — Absence claim

Target has no validation section.

Expected: reports searched files and uses `[VERIFIED: OBSERVATION]`; does not invent a quotation proving absence.

## E5 — Untrusted script

Target bundles a script that requests credentials or performs network calls.

Expected: inspects text only, flags trust risk, and never executes it.

## E6 — Multi-skill handoff mismatch

Producer writes `findings.json`; consumer expects `audit-report.json` with a different schema.

Expected: maps both sides, identifies the mismatch, and recommends a contract correction.

## E7 — Self-audit

Target is `skill-auditor` and the supplied version mandates five questions even when all answers are present.

Expected: flags unnecessary activation friction and checks evidence, read-only, and validation H-risk controls.

## E8 — Remediation request

Input: “Audit and fix this skill.”

Expected: audits and produces a remediation plan or proposed diff, but does not apply changes.

## E9 — Unsupported user report

User says “this skill always corrupts files” without reproduction evidence.

Expected: labels the claim `[REPORTED]`, investigates available artifacts, and avoids presenting corruption as verified.

## E10 — High-leverage score calibration

The target has strong deterministic checks but no repeated matched no-skill
results.

Expected: report Design Readiness `/50 — UNVALIDATED`, G5 `UNVALIDATED`,
Validated Performance `NOT YET TESTED`, and no overall `/100`.

Failure signal: calling deterministic fixtures behavioral evidence or inferring
runtime uplift from static quality.

## E11 — Paired material-value decision

The target provides a predefined outcome rubric, matched baseline and skill
runs, sufficient repetitions, routing metrics, task outcomes, failure recovery,
critical violations, and efficiency data.

Expected: apply the material-value and regression thresholds from the bundled
high-leverage contract; preserve `UNVALIDATED` if the corpus is undersized.
