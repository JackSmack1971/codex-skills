# Manual evaluation cases (not automated tests)

1. **Normal:** Given a reproducible test failure, trace the failing data flow and identify root cause before proposing a fix.
2. **Negative:** Given a plausible symptom patch with no reproduction, reject it as unverified and continue investigation.
3. **Boundary:** Given an active outage or security exposure, permit only reversible containment while preserving RCA work.
