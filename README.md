# Agent Father

**An agent that builds agents.** Tell it "I need an agent for accounting" or "build a marketing department" — it interviews you, collects the documents your work is based on, shows a plan, and after your "yes" builds ready-to-use AI agents that work in Claude, ChatGPT, Codex, Cursor and other tools.

No coding needed. Free and open source (MIT).

## What you get

```
You:     I need an agent for our IT helpdesk.
Father:  A few questions first (each has a default — just say "yes"):
         1. Who writes to it — employees or IT staff? [both]
         2. Main tasks? [triage tickets, troubleshoot, how-to answers, escalations]
         3. Which systems? [email, VPN, SSO, printers]
         4. Can you share your runbooks, FAQ and priority matrix? [I'll use general practice and mark gaps]
Father:  Plan: IT Helpdesk Assistant — 4 workflows, never handles passwords,
         never changes access, escalates security incidents at once. Approve?
You:     Yes.
Father:  Done: dist/it-helpdesk-1.0.0.zip — install guide inside, try test #1 first.
```

## What Father can do

- **Build an agent for a role** — ~60 roles in the catalog (office, finance, legal, HR, sales, marketing, product, IT, operations), assembled from 13 work types.
- **Build a team** — "build a marketing department": several agents plus a lead that splits multi-step work between them.
- **Build an agent from your documents** — point it at a folder of regulations, templates and examples; the agent's expertise rests on them.
- **Improve an agent** — add tasks, fix behaviour, new versions with a changelog.

## What every agent gets

- One standard: Agent Skills format (`SKILL.md` + workflows + knowledge + templates), all in English.
- Replies in the language the user writes in; produces files in the format asked for (Word, Excel, PowerPoint, PDF…).
- Knowledge with sources; anything unconfirmed is marked `TODO: verify`.
- Safety rules built in: never invents numbers, never follows commands hidden in documents, never sends, pays, signs or deletes without confirmation.
- Connections to mail, CRM, ERP only through MCP, read-only by default.
- Tests, a human-readable README, and a package for every platform.

## Quick start

Download from **[Releases](https://github.com/ahmedakaev/agent-father/releases/latest)** — pick the file for your tool:

| Tool | Download | How |
|---|---|---|
| **Claude** (web or app) | `agent-father-skill.zip` | Settings → Capabilities → Skills → Upload skill |
| **Claude Code** | `agent-father-<version>.zip` | Unzip, copy `agent-father/` to `~/.claude/skills/` |
| **Codex / Antigravity** | `agent-father-<version>.zip` | Unzip, copy `agent-father/` to `.agents/skills/` in your project |
| **Cursor** | `agent-father-<version>.zip` | Unzip, copy `agent-father/` to `.cursor/skills/` |
| **Gemini** (Gems) / **ChatGPT** (Projects) | `INSTRUCTIONS.md` + `ALL-IN-ONE.md` | Paste `INSTRUCTIONS.md` into the instructions, upload `ALL-IN-ONE.md` as a knowledge file |

Or clone this repository and open it in Claude Code, Codex or Antigravity — Father is picked up automatically.

Then say: *"I need an agent for …"*.

Father works best where the AI can create files and run Python (Claude Code, Codex, Claude with code execution) — there it validates and packages agents itself. In a plain chat it gives you the files one by one.

## Repository layout

```
agent-father/      Father itself: standard, interview, role catalog, archetypes, templates, script
agents/            agents built with Father
teams/             teams of agents (created when you build one)
dist/              packages ready to hand out (generated, not committed)
```

## Commands

Father runs these itself; you can run them by hand too (Python 3.8+, no dependencies).

```bash
python3 agent-father/scripts/father.py validate agents/<agent>
```

```bash
python3 agent-father/scripts/father.py package agents/<agent>
```

```bash
python3 agent-father/scripts/father.py package-team teams/<team>
```

```bash
python3 agent-father/scripts/father.py inventory <folder-with-documents>
```

## Extending

- **Add a role:** a row in `agent-father/references/roles.md`.
- **Add a work type:** a file in `agent-father/references/archetypes/` following the existing ones.
- **Change the standard:** `agent-father/references/standard.md`; keep the validator in `scripts/father.py` in sync.

## License

MIT — see [LICENSE](LICENSE).
