# Manual evaluation cases (not automated tests)

1. **Normal:** Given a web endpoint, identify validation, authentication, authorization, secrets, and safe output handling.
2. **Negative:** Given a proposed `eval`, unsafe redirect, or disabled CSRF control, reject the insecure shortcut.
3. **Boundary:** Given an untrusted file path or webhook, require canonicalization/signature checks and bounded errors.
