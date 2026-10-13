# Create a team (department)

Purpose: turn "make a marketing department" into several agents that work together, plus a lead agent, packaged as one team.

## Inputs
- Required: the department or the outcome the team delivers.
- Optional: existing agents to include, sources, samples.

## Steps

1. **Interview the department**, following `references/interview.md` with these changes:
   - Round 1 asks about the department's outcomes and the roles in it, not one role's tasks.
   - Look up each role in `references/roles.md`.
   - Ask for sources once for the whole team; sort them into shared (company, brand, glossary) and role-specific.
   — check: you can name 2–5 members, each with 2–5 workflows.

2. **Propose the team** in the user's language, max ~20 lines:
   - members: name, role, archetypes, tasks (one line each);
   - the lead and 2–3 example requests that need several members, with who does which step;
   - shared knowledge files;
   - red lines common to the team.
   More than 5 members → suggest splitting into two teams.
   — check: explicit approval. Without it, stop.

3. **Write specs**: one `spec.yaml` per member (create-agent step 4), plus the lead's spec (archetype `coordinator`, workflow `run-team-task`).

4. **Scaffold**: `python3 scripts/father.py scaffold <name> --out <agents-dir>` for each member and the lead. Create `teams/<team-name>/` with `team.yaml`, `shared/`, `README.md` (standard §12).

5. **Build members** exactly as in create-agent step 6. Each member must work alone. In each member's SKILL.md Resources, list the shared files as `references/knowledge/shared-<file>.md`.

6. **Build the lead**:
   - Routing table: request types → `run-team-task` for multi-step work; single-role requests → name the member skill to use.
   - Workflow file `run-team-task.md`: (1) split the request into steps; (2) assign each step to a member and say so in one line; (3) for each step follow that member's skill — via a subagent if the platform supports it, otherwise in the same conversation; (4) pass results using `Task / Inputs used / Result / Open questions`; (5) check the assembled result against the original request; (6) present one answer with who did what.
   - Knowledge: `team-roster.md` — members, what each does, example handoffs.
   - Red lines: baseline + every member's red lines still apply to every step.

7. **Shared knowledge**: write files in `teams/<team-name>/shared/` (standard §5).

8. **Validate and package**: `python3 scripts/father.py package-team teams/<team-name>`. It validates every member, copies shared knowledge into each, packages each member and builds one team zip.
   — check: 0 errors for every member.

9. **Hand off**: team zip path; install all members and the lead together (README); first multi-step request to try; shared and CLIENT sections to fill.

## Output
`agents/<member>/` for every member and the lead, `teams/<team-name>/`, and `dist/<team-name>-<version>.zip`.

## Before handing over
- [ ] Each member validates and works alone.
- [ ] The lead's routing covers every member.
- [ ] Shared knowledge exists once and is listed in every member.
- [ ] Team README explains installing all agents together.

## Without scripts
Build each member as in create-agent "Without scripts". Copy each shared file into every member's `references/knowledge/` with the `shared-` prefix. Zip all member folders together with the team README.
