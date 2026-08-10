# Verification

- The skill requires Tailwind major-version evidence before version-sensitive
  guidance and explicitly stops for unknown or conflicting evidence.
- The playbook separates Tailwind v4 CSS-first setup from Tailwind v3
  `tailwind.config`/`content`/`@tailwind` setup.
- Version-independent token, variant, responsive, dark-mode, and accessibility
  guidance is preserved.
- Evaluation fixtures cover v4, v3, and unknown/conflicting version evidence.

Run:

```text
python scripts/validate_repository.py
python -m unittest discover -s tests -v
```
