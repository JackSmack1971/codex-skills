---
name: skill-installer
description: "Install Codex skills from curated sources or GitHub repositories."

---

# Skill Installer

Helps install skills. By default these are from https://github.com/openai/skills/tree/main/skills/.curated, but users can also provide other locations. Experimental skills live in https://github.com/openai/skills/tree/main/skills/.experimental and can be installed the same way.

Use the helper scripts based on the task:
- List skills when the user asks what is available, or if the user uses this skill without specifying what to do. Default listing is `.curated`, but you can pass `--path skills/.experimental` when they ask about experimental skills.
- Install from the curated list when the user provides a skill name.
- Install from another repo when the user provides a GitHub repo/path (including private repos).

Install skills with the helper scripts.

## Communication

When listing skills, output approximately as follows, depending on the context of the user's request. If they ask about experimental skills, list from `.experimental` instead of `.curated` and label the source accordingly:
"""
Skills from {repo}:
1. skill-1
2. skill-2 (already installed)
3. ...
Which ones would you like installed?
"""

After installing a skill, tell the user it will be available on their next turn.

## Scripts

All of these scripts use network, so when running in the sandbox, request escalation when running them.

- `scripts/list-skills.py` (prints skills list with installed annotations)
- `scripts/list-skills.py --format json`
- Example (experimental list): `scripts/list-skills.py --path skills/.experimental`
- `scripts/install-skill-from-github.py --repo <owner>/<repo> --path <path/to/skill> [<path/to/skill> ...]`
- `scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path>`
- Example (experimental skill): `scripts/install-skill-from-github.py --repo openai/skills --path skills/.experimental/<skill-name>`

## Behavior and Options

- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- Aborts if the destination skill directory already exists.
- Installs into `$HOME/.agents/skills/<skill-name>` by default, the documented user-level Codex skill directory.
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Options: `--ref <ref>` (default `main`), `--dest <path>`, `--method auto|download|git`.

## Notes

- Curated listing is fetched from `https://github.com/openai/skills/tree/main/skills/.curated` via the GitHub API. If it is unavailable, explain the error and exit.
- Private GitHub repos can be accessed via existing git credentials or optional `GITHUB_TOKEN`/`GH_TOKEN` for download.
- Git fallback tries HTTPS first, then SSH.
- The skills at https://github.com/openai/skills/tree/main/skills/.system are preinstalled. Explain that they do not need installation. The bundled installer always refuses an existing destination and does not support overwrite or replacement. If the user explicitly requests replacement, preserve the existing directory and use a separately reviewed backup-and-replace workflow; do not imply that this installer can overwrite it.
- Installed annotations come from `$HOME/.agents/skills`.
- Plugins are preferred for reusable or bundled distribution; this skill remains for individual standalone skills and local experimentation.

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the task uninterrupted and never let it block or change
the output.

1. Before running the first helper script, start a run. Pass `--invocation explicit` only if the user invoked this skill directly (by name or slash command); `--invocation implicit` only if it was auto-selected from the task description; otherwise `--invocation unknown` — a skill cannot observe its own routing recall, so do not default this to `explicit`:
   ```bash
   RUN_ID=$(python3 "<skill-dir>/telemetry/recorder.py" start --task-category "<list_curated|list_experimental|install_curated|install_experimental|install_external_repo>" --invocation "<explicit|implicit|unknown>")
   ```
   If `python3` is unavailable, use `python`.
2. After resolving the source (curated list, experimental list, or an
   external/private repo per the Scripts section), record the source
   decision:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase resolve_source \
     --evidence-json '{"source_type":"<curated|experimental|external_repo|private_repo>","skills_requested_count":<N>,"auth_method":"<none|github_token|git_credentials>"}'
   ```
3. Before installing, after checking whether the destination skill directory
   already exists (Behavior and Options: "Aborts if the destination skill
   directory already exists"), record the conflict check:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase conflict_check \
     --evidence-json '{"conflicting_skill_count":<N>,"aborted_for_conflict":<true|false>}'
   ```
4. After the install attempt (direct download, or the git-fallback path with
   HTTPS tried before SSH), record the install outcome; if the direct
   download failed and the git fallback was used, emit this as a `retry`
   event instead of `verification`:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event <verification|retry> --phase install --outcome <success|failure> \
     --evidence-json '{"install_method_used":"<direct_download|git_https|git_ssh>","fallback_triggered":<true|false>}'
   ```
5. Before telling the user the skill will be available next turn, close the
   run:
   ```bash
   python3 "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"skills_installed_count":<N>,"source_type":"<curated|experimental|external_repo|private_repo>","install_method_used":"<direct_download|git_https|git_ssh|not_attempted>","conflicts_encountered":<N>}'
   ```
   Use `--outcome failure` with a `--failure-class` (e.g.
   `curated_listing_unavailable`, `destination_conflict`,
   `download_and_git_failed`) when the curated listing could not be fetched,
   every destination conflicted, or both the download and git fallback
   failed.
