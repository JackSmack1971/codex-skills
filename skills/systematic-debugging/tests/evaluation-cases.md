# Evaluation cases

## Root-cause and emergency-containment policy

1. **Normal bug — reject premature patching.** A non-emergency bug has a
   plausible one-line symptom patch, but no reproduction, recent-change check,
   or traced data flow. The agent must refuse to present the patch as a fix and
   continue Phase 1 before proposing a permanent change.
2. **Production outage — allow reversible containment.** A service outage is
   causing active customer impact. The agent may deploy a narrowly scoped,
   reversible **temporary mitigation** for service restoration before full RCA,
   while preserving or collecting evidence, explicitly stating that the root
   cause is unresolved, and scheduling RCA afterward.
3. **Security incident — stop exposure first.** An active vulnerability is
   exposing credentials. The agent may disable the affected endpoint or revoke
   exposed credentials as a narrowly scoped **temporary mitigation** before
   full RCA, while preserving evidence and continuing the investigation after
   exposure is stopped.
4. **Reporting — mitigation is not root-cause resolution.** After a temporary
   workaround makes symptoms disappear, the agent must not report “fixed” or
   “root cause solved”; it must identify the action as temporary and state what
   remains to investigate.

5. Confirm the skill is discovered under `.agents/skills`.
6. Run `python scripts/find_polluter.py --help`; it must work on Windows.
7. Run the helper with a missing pollution target and a glob that matches no tests; it must finish without shell errors.
8. Confirm all supporting references remain available and use the migrated helper name.
9. Confirm no Claude-specific frontmatter or `superpowers:` launcher references remain.
