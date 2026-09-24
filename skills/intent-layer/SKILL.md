---
name: intent-layer
description: "Set up hierarchical AGENTS.md intent context for codebases."

---

# Intent Layer

Hierarchical AGENTS.md infrastructure so agents navigate codebases like senior engineers.

## Core Principle

**Only ONE root context file.** Keep `AGENTS.md` as the Codex/Open Agent instruction root. Child `AGENTS.md` files are encouraged for complex subsystems.

## Workflow

```
1. Detect state
   python scripts/intent_tools.py detect-state /path/to/project
   → Returns: none | partial | complete

2. Route
   none/partial → Initial setup (steps 3-5)
   complete     → Maintenance (step 6)

3. Measure [gate - show table first]
   python scripts/intent_tools.py analyze /path/to/project
   python scripts/intent_tools.py estimate /path/to/each/source/dir

4. Decide
   No root file  → Ask whether to add a root AGENTS.md.
   Has root file → Add Intent Layer section + child nodes if needed

5. Execute
   Use references/templates.md for structure
   Use references/node-examples.md for real-world patterns
   Validate: one root, READ-FIRST directive, <4k tokens per node

6. Maintenance mode (when state=complete)
   Ask user:
   a) Audit nodes     → Use references/capture-protocol.md for SME questions
   b) Find candidates → Re-measure tokens, suggest new nodes
   c) Both
```

## When to Create Child Nodes

| Signal | Action |
|--------|--------|
| >20k tokens in directory | Create AGENTS.md |
| Responsibility shift | Create AGENTS.md |
| Hidden contracts/invariants | Document in nearest ancestor |
| Cross-cutting concern | Place at LCA |

Do NOT create for: every directory, simple utilities, test folders (unless complex).

## Capture Questions

When documenting existing code, ask:
1. What does this area own? What's out of scope?
2. What invariants must never be violated?
3. What repeatedly confuses new engineers?
4. What patterns should always be followed?

## Resources

**Scripts:**
- `scripts/intent_tools.py detect-state` - Check Intent Layer state (none/partial/complete)
- `scripts/intent_tools.py analyze` - Find semantic boundaries
- `scripts/intent_tools.py estimate` - Measure directory complexity

**References:**
- `references/templates.md` - Root and child node templates
- `references/node-examples.md` - Real-world examples
- `references/capture-protocol.md` - SME interview protocol

## Telemetry

Record tailored run signals so improvement agents can evaluate this skill
from real usage. Resolve `<skill-dir>` as the directory containing this
loaded `SKILL.md`. Telemetry is observability only: if a `recorder.py` call
errors, proceed with the task uninterrupted and never let it block or change
the output.

1. Before Workflow step 1 (detect state), start a run. Pass `--invocation explicit` only if the user invoked this skill directly (by name or slash command); `--invocation implicit` only if it was auto-selected from the task description; otherwise `--invocation unknown` — a skill cannot observe its own routing recall, so do not default this to `explicit`:
   ```bash
   RUN_ID=$(python "<skill-dir>/telemetry/recorder.py" start --task-category "<initial_setup|maintenance>" --invocation "<explicit|implicit|unknown>")
   ```
2. After Workflow step 1-2 (detect state and route), record the routing
   decision:
   ```bash
   python "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase route \
     --evidence-json '{"detected_state":"<none|partial|complete>","route":"<initial_setup|maintenance>"}'
   ```
3. After Workflow step 4 for initial setup (decide root/child nodes), or
   after the maintenance-mode question for a complete state, record the
   planning decision:
   ```bash
   python "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event decision --phase plan \
     --evidence-json '{"child_nodes_planned":<N>,"signals_triggered":["<subset of token_threshold,responsibility_shift,hidden_contracts,cross_cutting_concern>"],"maintenance_choice":"<audit_nodes|find_candidates|both|null>"}'
   ```
4. After Workflow step 5 (execute and validate: one root, READ-FIRST
   directive, <4k tokens per node), record the validation check:
   ```bash
   python "<skill-dir>/telemetry/recorder.py" event --run-id "$RUN_ID" --event verification --phase validate --outcome <success|failure> \
     --evidence-json '{"one_root_confirmed":<true|false>,"read_first_directive_present":<true|false>,"max_node_tokens":<N>}'
   ```
5. Before returning output, close the run:
   ```bash
   python "<skill-dir>/telemetry/recorder.py" finish --run-id "$RUN_ID" --outcome success \
     --evidence-json '{"route":"<initial_setup|maintenance>","nodes_created":<N>,"max_node_tokens":<N>,"maintenance_choice":"<audit_nodes|find_candidates|both|null>"}'
   ```
   Use `--outcome failure` with a `--failure-class` when detection, routing,
   or validation could not be completed.
