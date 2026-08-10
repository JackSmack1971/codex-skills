# Manual evaluation cases (not automated tests)

1. **Normal:** Given an OAuth webhook integration, ground behavior in current provider documentation and verify signatures.
2. **Negative:** Given untrusted callback data, reject processing without validation, replay protection, and authorization.
3. **Boundary:** Given provider timeout or duplicate delivery, specify retries, idempotency, and recovery.
