# Pull-request merge policy

Use squash merging for pull requests targeting `main`. Each pull request
should represent one focused issue or atomic change, and its squash commit
should have a concise imperative subject. Reviewers should confirm the linked
issue, verification, scope, and security impact before merge.

Merge commits and rebase merges are disabled to keep the default branch linear
and the release history easy to audit. GitHub automatically deletes merged
head branches; protected branches remain available when required by policy.
