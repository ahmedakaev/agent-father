# Father — agent factory

Instructions for any AI assistant working in this repository.

## Layout

- `agent-father/` — the Father skill: builds agents through an interview. Its `SKILL.md` is the entry point; `references/standard.md` is the Agent Standard every agent follows.
- `agents/<name>/` — agents built with Father (source of truth).
- `teams/<name>/` — teams: `team.yaml`, shared knowledge, README (standard §12).
- `dist/` — build output from `father.py package`. Never edit by hand; not committed.
- `.claude/skills/`, `.agents/skills/` — symlinks so Claude Code and Codex discover Father in this repo.

## Creating or changing an agent

Read `agent-father/SKILL.md` and follow it. New agents go to `agents/<name>/`, packages to `dist/`.

```bash
python3 agent-father/scripts/father.py scaffold <name> --title "<title>" --out agents
python3 agent-father/scripts/father.py validate agents/<name>
python3 agent-father/scripts/father.py package agents/<name>
```

## Changing Father itself

- Keep `references/standard.md`, `assets/templates/` and `scripts/father.py` consistent: a rule in the standard that can be checked belongs in the validator.
- After a change, validate Father and every agent:
  ```bash
  python3 agent-father/scripts/father.py validate agent-father
  for a in agents/*/; do python3 agent-father/scripts/father.py validate "$a"; done
  ```
- Bump `agent-father/manifest.yaml` and `SKILL.md` metadata versions together and add a changelog entry. If the standard changes in a way that breaks existing agents, bump `standard` and note what agents must change.
- Model instructions are in English; anything end users read is in their language (the language the user works in).
