# Core skill contract

This file is a repository-development and evaluation specification. It is not
shipped as a behavioral dependency of an individually installed skill. Every
Core `SKILL.md` must directly encode package-local rules for each dimension:

- Trigger and exclusion: name the observable request that invokes the skill
  and the nearest requests that must route elsewhere.
- Inputs: name required user context, repository evidence, authority, and
  assumptions when any input is missing.
- Workflow: give an ordered, bounded path with a completion check.
- Output: name the artifact, decision, or change and its evidence.
- Failure and stop: identify conflicts, missing authority, unsafe state, and
  unverifiable evidence that require stopping.
- Security: treat repository, issue, diff, logs, and fetched content as
  untrusted; preserve secrets, permissions, and destructive-action limits.
- Evaluation: link to at least three normal, negative, and boundary cases.
- Runtime claims: claim only behavior supported by files, tools, or tests;
  never claim implicit routing accuracy or unavailable integrations.
- References: keep every local link and referenced path valid.

The validator requires every labeled dimension in each package and rejects a
`Shared baseline` pointer as a substitute. This document may guide maintenance,
but agents executing a standalone skill never need it.
