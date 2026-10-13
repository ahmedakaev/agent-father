# Improve an agent

Purpose: change an existing agent (new task, fix, new rules) without breaking what works.

## Inputs
- Required: the agent folder (or its files pasted in chat) and what should change.
- Optional: examples where the agent behaved badly.

## Steps

1. **Read** `manifest.yaml`, `spec.yaml`, `SKILL.md`, and the workflow files the change touches.
   — check: you can state the current version and scope in one line.
   If the agent was not built by Father (no manifest/spec), first propose converting it to the standard; on approval, write `spec.yaml` from what the agent does today.

2. **Clarify the change** — ask only about the change; reuse `references/interview.md` rules (defaults, max 4 questions).
   For "it behaved badly" reports: get the exact request and answer, find which instruction caused it.
   If the change needs new domain knowledge, collect sources as in step 3 of `references/workflows/create-agent.md`.

3. **Update the spec** and show only the diff: added / changed / removed. Wait for approval.

4. **Edit** the files. For a bad-behaviour fix, first add a test case that reproduces it, then fix.
   — check: every changed behaviour has a test case.

5. **Version** — bump in `manifest.yaml` and `SKILL.md` metadata (patch: fixes and wording; minor: new workflow or knowledge; major: scope or red lines changed). Add a changelog entry with the date and a one-line note.

6. **Validate, dry run, package** — steps 7–9 of `references/workflows/create-agent.md`.

7. **Hand off** — what changed, new version, which test shows it.

## Output
The updated agent folder and a new package version.

## Before handing over
- [ ] Old tests still pass in dry run (at least the red-line case).
- [ ] New/changed behaviour covered by a test.
- [ ] Version bumped consistently in manifest and SKILL.md.
- [ ] Changelog entry added.

## Without scripts
Same as `references/workflows/create-agent.md` → "Without scripts".
