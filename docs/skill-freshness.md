# Skill freshness

`skill-freshness.json` is the machine-readable registry for guidance that can
drift with an external product, runtime, library, API, or CLI.

Each skill is classified as either `version-sensitive` or `exempt`. Sensitive
records state the technology, checked version (or why it is unspecified),
verification date, whether runtime detection is required, the required
verification action, and references. Exemptions are documented in the registry
with an explicit reason and references to the skill they cover.

When a sensitive skill is used, perform the declared runtime/version probe and
documentation lookup before treating its guidance as current. A checked date is
not a substitute for that lookup when the record requires detection.
