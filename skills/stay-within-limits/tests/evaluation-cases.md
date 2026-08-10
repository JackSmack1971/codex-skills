# Manual evaluation cases (not automated tests)

1. **Normal:** Given usage data between waves, continue only while the next bounded wave fits.
2. **Negative:** Given no usage signal, pause and report the limit is unverified.
3. **Boundary:** Given a near-cap reading, defer the next expensive wave after safe local cleanup.
