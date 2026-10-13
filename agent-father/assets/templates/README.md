# {{title}}

<!-- FATHER:FILL 2–3 sentences: what the agent does and for whom. -->

Version: {{version}}<!-- FATHER:FILL publisher line if any: " · Publisher: ..." -->

## What it does

<!-- FATHER:FILL one line per workflow, each with an example request -->

## What it does not do

<!-- FATHER:FILL list + where to go instead -->

## Installation

The agent follows the open Agent Skills standard and works across AI tools. Pick yours.

**Claude (web or desktop app)**
1. Open Settings → the skills section (Capabilities → Skills). Menu names may differ slightly.
2. Click "Upload skill" and select `{{name}}.zip`.
3. If the section is missing, turn on Code execution or ask your administrator to allow skills.

**Claude Code**
Copy the `{{name}}` folder from the archive to `~/.claude/skills/` (just for you) or to `.claude/skills/` inside a project (for the team).

**Codex and other tools that support Agent Skills**
Copy the `{{name}}` folder to `.agents/skills/` inside your working folder. For Cursor use `.cursor/skills/`.

**ChatGPT and tools without skill support**
1. Create a project (or a custom GPT).
2. Paste the text of `portable/INSTRUCTIONS.md` into the instructions field.
3. Upload all files from `portable/knowledge/` (and `portable/assets/`, if present) as project files.

In this mode the agent works without scripts, following its text instructions only.

## Connections

<!-- FATHER:FILL for each connector in manifest.yaml: what it gives the agent, access level (read / drafts / write with confirmation), what the agent does without it. The administrator connects an MCP server for your system. If there are no connectors, delete this section. -->

## Independence and memory

<!-- FATHER:FILL autonomy level in plain words; for level 3 — the list of actions it does by itself, with limits, and what always needs your "yes"; how to see what it did ("what did you do?") and how to turn it off. Memory: where it is kept, what it remembers, how to view or clear it. Delete parts that do not apply. -->

## Scheduled tasks

<!-- FATHER:FILL for each schedule in manifest.yaml: what runs, when, what it does alone, where the report goes. How to set up: Claude Code / Claude — scheduled tasks; ChatGPT — Tasks; other tools — their scheduler or cron, with the prompt "Run scheduled task <id> of {{name}}". Delete this section if there are no schedules. -->

## First run

Check that the agent works on a ready-made example:

<!-- FATHER:FILL one case from tests/cases.yaml: what to upload, what to type, what should happen -->

More checks are in `tests/cases.yaml`.

## Making it yours

<!-- FATHER:FILL which files in references/knowledge/ to fill with your own data (CLIENT sections) and why -->

## Limitations

- The agent prepares drafts and calculations; it never sends, signs or pays anything by itself.
- Values that change over time (rates, deadlines, forms) are marked ⚠️ — check them against an official source.
<!-- FATHER:FILL domain-specific limitations -->

## Version history

See `manifest.yaml` → `changelog`.
