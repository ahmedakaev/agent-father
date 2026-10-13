# Agent Father

Agent Father builds other agents. Say "I need an agent for accounting" or "make an assistant for the sales team": Father asks a few questions, collects the sources the work is based on, shows the agent's plan, and after your "yes" builds a ready package — instructions, workflows, knowledge files, templates, tests and an installation guide.

Version: 1.0.1

## What it does

- **Create an agent for a role** — "Create an agent for the HR department: hiring, dismissals, vacations".
- **Improve an existing agent** — "Improve the accounting agent: add invoice checking".
- **Build a team (department)** — "Build a marketing department": several agents plus a lead that splits multi-step work between them.
- **Build an agent from your documents** — "Make an agent from this folder": Father reads regulations, templates and examples and builds the agent on them.
- **Check and package an agent** — "Check the agent in agents/hr-assistant".

Every agent follows one standard (`references/standard.md`):
- works in Claude, Codex, Cursor and other tools that support Agent Skills;
- works in ChatGPT and other chats through a portable version;
- answers in the language you write in and produces files in the format you ask for (Word, Excel, PowerPoint, PDF…);
- rests on sources: your documents, examples and official sites;
- never invents numbers or facts;
- never sends, pays or signs anything without human confirmation;
- connects to mail, CRM and other systems only through MCP, read-only by default;
- independence you choose: from advice only to doing safe routine actions by itself from a list you approve;
- remembers decisions and preferences between conversations (memory file you control);
- can run on a schedule (every morning, every Monday) and leave a report;
- ships with tests.

## What it does not do

- It does not do the agent's job itself: if you need an act drafted, Father builds an agent that drafts acts.
- It does not connect mail, ERP or CRM: an administrator does that, following the agent's README.
- It does not remove safety rules from agents, even on request.

## Installation

**Claude (web or desktop app)**
1. Open Settings → the skills section (Capabilities → Skills). Menu names may differ slightly.
2. Click "Upload skill" and select `agent-father.zip`.
3. If the section is missing, turn on Code execution or ask your administrator to allow skills.

**Claude Code**
Copy the `agent-father` folder to `~/.claude/skills/`.

**Codex and other tools that support Agent Skills**
Copy the `agent-father` folder to `.agents/skills/` inside your working folder. For Cursor use `.cursor/skills/`.

**ChatGPT and other chats without skills**
1. Create a project or a custom GPT.
2. Paste the text of `portable/INSTRUCTIONS.md` into the instructions field.
3. Upload the files from `portable/knowledge/` and `portable/assets/` as project files.

In this mode Father delivers the agent's files as text, one by one — save them into a folder as it tells you.

Father works best where the AI can create files and run Python (Claude Code, Claude with code execution, Codex): there it validates and packages the agent itself.

## First run

Type: "I need an agent for the HR department".

What should happen:
1. Father says which mode it is working in.
2. It asks up to 4 questions, each with a suggested default.
3. It asks for the documents and examples the work is based on.
4. It shows a short plan of the agent and asks for your approval.

## Making it yours

- **Roles and work types:** Father knows ~60 roles (`references/roles.md`) built from 13 work types (`references/archetypes/`) covering office, finance, legal, HR, sales, marketing, product, IT and operations. Add a role as a row in the catalog; add a work type as a new archetype file.
- **Your branding:** edit the templates in `assets/templates/` (e.g. the README).
- **Standard changes:** bump `standard` in the manifests so it is clear which version each agent was built with.

## Limitations

- Father does not know the current rates, deadlines and forms in your country unless you give it sources or it can check official sites. Anything unconfirmed is marked `TODO: verify` and must be filled by a specialist before the agent goes to clients.

## Version history

See `manifest.yaml` → `changelog`.
