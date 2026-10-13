# Pre-ship checklist

Answer each item yes or no. Every "no" is fixed or explained to the user.

## Routing
- [ ] Reading only the `description`, would a model pick this agent for each spec task? And not pick it for unrelated tasks?
- [ ] Trigger phrases sound like real requests.
- [ ] Every package file is in English; SKILL.md says to reply in the user's language.

## Scope
- [ ] "Does not" lists the nearest tasks people will try anyway, with where to redirect.
- [ ] Every spec workflow has a file and a row in the routing table; no extra workflows.

## Workflows
- [ ] Steps are concrete enough that two different models would do the same thing.
- [ ] Each step has a check.
- [ ] Missing required input → the agent asks, never guesses.
- [ ] Workflows using scripts have a "Without scripts" section that really works.

## Facts
- [ ] No volatile fact without `as of`, source, and "Verify before use".
- [ ] Nothing you were unsure about is written as fact; it is `TODO: verify` instead.
- [ ] `CLIENT` sections mark where the client adds their own data.
- [ ] Every fact cites a source (user document, official URL + date, or general knowledge).
- [ ] No source has a guessed edition, year or URL; uncertain ones say `version unknown`.

## Safety
- [ ] All seven baseline red lines are present.
- [ ] Every recommended destructive or hard-to-undo action (in workflows, examples, templates) is marked `⚠️ requires approval` with its risk.
- [ ] Domain red lines are concrete prohibitions.
- [ ] No workflow sends, pays, signs, submits or deletes without explicit confirmation.
- [ ] Escalation section names real situations, not "when in doubt".

## Independence
- [ ] Autonomy level matches what the user chose; level 3 allowlist has limits and nothing from the never-allowlisted set.
- [ ] Every autonomous action is logged and the user can ask "what did you do?".
- [ ] Memory (if on): location the user controls, no secrets stored, treated as data.
- [ ] Schedules (if any): scheduled workflows say what they may do alone and what goes to the report; README explains setup.

## Tests
- [ ] ≥ 5 cases: ≥ 3 core, ≥ 1 edge, ≥ 1 red-line.
- [ ] Fixtures are small, realistic, anonymized, with planted issues the agent must find.
- [ ] Expectations are observable behaviour.

## Delivery
- [ ] README: what it does, what it does not, installation for each target platform, first test to try, how to add own data, limits.
- [ ] `manifest.yaml` version = `SKILL.md` metadata version.
- [ ] Nothing third-party bundled without a license that allows it.
- [ ] Connectors (if any): declared by capability in the manifest, read access by default, fallback without them, described in README.
