# Create an agent

Purpose: turn "I need an agent for X" into a validated, packaged agent.

## Inputs
- Required: the role or department the agent is for.
- Optional: samples (documents, exports, messages), company templates, rules, target platform.

## Steps

1. **Detect mode** — can you create files? can you run Python? Files + Python → files mode with `scripts/father.py`. Files without Python → files mode, run the checklist by hand. No files → chat mode (`references/chat-mode.md`).
   — check: you told the user in one line which mode you are in.

2. **Interview** — look up the role in `references/roles.md`, then follow `references/interview.md`. Pick archetypes and read their files in `references/archetypes/`.
   — check: you can fill every field in `spec.yaml` or have listed it as an assumption.

3. **Sources** — collect what the agent's expertise will rest on, following `references/interview.md` → "Sources". Record each source in the spec's `sources` list (name, type, date or version, where it came from).
   - User documents (regulations, policies, templates, real examples) come first; summarize them into knowledge files in step 6, citing the document name.
   - If the platform has web search: check volatile facts on official sites only (government, regulators, standard bodies); record the URL and the date checked.
   - What remains unconfirmed becomes `TODO: verify` and is listed in the spec summary.
   — check: every knowledge topic in the spec has at least one source or is listed as unconfirmed.

4. **Spec** — fill `assets/templates/spec.yaml`. Show the summary described in `references/interview.md` → "Showing the spec".
   — check: the user explicitly approved. Without approval, stop here.

5. **Scaffold** — `python3 scripts/father.py scaffold <agent-name> --out <agents-dir>`. Default `<agents-dir>`: `agents/` next to the Father folder if it exists, otherwise the current directory. Save the approved spec as `<agent>/spec.yaml`.
   — check: the tree from `references/standard.md` §1 exists.

6. **Build** — fill files in this order; delete every `FATHER:FILL` marker as you go:
   1. `references/workflows/*.md` — one per spec workflow, format from `assets/templates/workflow.md` and standard §4.
   2. `references/knowledge/*.md` — from `assets/templates/knowledge.md`, standard §5. Every fact cites its source from the spec; volatile facts dated and sourced, or `TODO: verify`.
   3. `assets/` — format-neutral templates (Markdown/CSV), if the workflows need them.
   4. `scripts/` — only if a step is deterministic, repetitive and error-prone by hand. Otherwise leave `scripts/` empty.
   5. `SKILL.md` — standard §3. Routing table must list every workflow file; Resources must list every knowledge file, asset and script.
   6. `tests/cases.yaml` + `tests/fixtures/` — standard §10; build small realistic fixtures with planted issues.
   7. `README.md` — from the template.
   8. `manifest.yaml` — standard §11.
   — check: no file still contains `FATHER:FILL`.

7. **Validate** — `python3 scripts/father.py validate <agent-dir>`. Fix all errors; fix warnings unless you can say why they are fine. Then go through `references/checklist.md`.
   — check: validator reports 0 errors; every checklist item is yes or explained.

8. **Dry run** — take two cases from `tests/cases.yaml` (one core, the red-line one). Read the agent's SKILL.md and the workflow it routes to as if you were that agent, and produce the answer. Compare with `expect`. Fix the agent's files if it would fail.
   — check: both cases pass.

9. **Package** — `python3 scripts/father.py package <agent-dir> --out <dist-dir>` (default `dist/` next to `<agents-dir>`).
   — check: the command printed the artifact paths.

10. **Hand off** — in the user's language, 5–8 lines:
   - what the agent does (one line),
   - where the package is,
   - how to install: point to the README section for their platform,
   - which test case to try first,
   - what to add to `references/knowledge/` to make it truly theirs (the `CLIENT` sections),
   - what you assumed,
   - which sources the knowledge rests on and what is still `TODO: verify`.

## Output
A folder `<agents-dir>/<agent-name>/` and a package in `<dist-dir>/<agent-name>-<version>/` plus `.zip`.

## Before handing over
- [ ] Spec approved by the user.
- [ ] Validator: 0 errors.
- [ ] Dry run: core and red-line cases pass.
- [ ] No invented volatile facts; every knowledge fact has a source.
- [ ] README explains installation for every platform in the spec.

## Without scripts
Create the tree from standard §1 by hand, copying templates from `assets/templates/`. Validate with `references/checklist.md` plus these checks: name matches folder; description ≤ 1024 chars with "Use when"; all links in SKILL.md resolve; ≥ 5 test cases incl. edge and red-line; no `FATHER:FILL` or `{{` left outside `assets/`. Package by zipping `SKILL.md`, `references/`, `assets/`, `scripts/` into `<agent-name>.zip`; for chat tools, give the user SKILL.md body as instructions and the reference files as uploads.
