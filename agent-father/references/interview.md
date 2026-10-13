# Interview

Goal: collect enough to fill `spec.yaml` without tiring the user. The user is usually not technical.

## Rules

- Speak the user's language. Plain words, no jargon ("agent", "skill" are fine; "frontmatter", "MCP" are not).
- At most 3 rounds, at most 4 questions per round.
- **Use clickable questions when the platform has them** (a structured question tool with options): one question per item, 2–4 options, your default first and marked "(recommended)", multi-select where answers combine. The user can always type their own answer. Without such a tool, number the questions so the user can answer "1 — yes, 2 — ...".
- Every question comes with your proposed default in brackets. The user may answer "use defaults" / "your call" — then use the defaults and list them under `assumptions` in the spec.
- If the first message already answers a question, do not ask it again.
- Ask for samples (a real invoice, report, letter). Personal data in samples must be anonymized before it goes into `tests/fixtures/` or `references/knowledge/`; tell the user you will do it.
- Stop interviewing as soon as the spec can be filled. A good spec with stated assumptions beats a long interview.

## Round 1 — the job

1. Who will use the agent, and how experienced are they? (e.g. accountant / business owner without an accountant / outsourcing staff serving clients)
2. Which 3–7 tasks should it take over? Ask for concrete examples: "What did you do last week that you would hand to it?"
3. What comes in and what must come out? (Excel exports, PDFs, scans, emails, questions → tables, documents, drafts, answers)

## Round 2 — context

4. Country, standards and rules that apply (laws, industry standards, internal policies).
5. Systems involved (1C, Excel, Google, mail, CRM, bank) and where the agent will run (Claude, ChatGPT, other, unknown). For each system the agent should work with directly: read only, or also write? [Default: any platform, level L1; if a system is connected — read only]
6. Templates, tone and style to follow; company name for the README. [Default: neutral business style, no company name]

## Round 3 — risks

7. What must the agent never do? Which mistakes would be expensive?
8. Which decisions must stay with a human?
9. Anything about the data it must keep confidential?

10. How independent should it be? [1 — prepares drafts, you act] Options: 0 advise only · 1 drafts · 2 acts after your "yes" · 3 does safe routine actions by itself from a list you approve (e.g. sort mail, create tasks) — payments, deletion, signing, access changes and messages to clients always need your "yes".
11. Should it remember between conversations (decisions, your preferences, what worked)? [yes, in a memory file you control]
12. Anything it should do on a schedule, e.g. every morning or every Monday? [no]

Offer archetype defaults for 7–8 so the user can confirm instead of inventing them. For level 3, propose the allowlist yourself from the workflows (with limits such as "max 50 per run", "only the Support inbox") and let the user trim it.

## Sources

Ask in round 2 or 3, always — this is what makes the agent an expert instead of a generalist:

- Which documents define how the work is done here? Laws and standards that apply, internal regulations and policies, instructions, templates. [Default: I'll use general knowledge and mark everything that needs checking]
- Can you share 2–3 real examples of good work (a report, a letter, a checked document)? Personal data will be anonymized.
- Who is the expert whose answers the agent should match (e.g. the chief accountant)? Their typical answers to frequent questions are the best knowledge source.

Explain in one line why you ask: without sources the agent will mark many facts "to verify", and its answers will be generic.

Handling:
- Files and pasted texts → summarized into `references/knowledge/`, each fact citing the document name. Never copy a whole document whose license does not allow redistribution; summarize and cite.
- Links to official sites → check them yourself if you have web search; record URL and date checked.
- No sources → proceed, but the spec summary must say how many facts remain `TODO: verify`.
- Record a source's version, edition or year only if the user gave it or you are certain; otherwise `version unknown`. A guessed edition is an invented fact.

## Choosing archetypes

| Signals in the answers | Archetype |
|---|---|
| Drafting, checking, filling documents; templates; contracts, letters, acts | `document-specialist` |
| Tables, exports, reconciliation, reports, calculations | `data-analyst` |
| Email, messengers, replies, follow-ups, meetings | `communicator` |
| Questions, explanations, procedures, "how do I…", knowledge base | `advisor` |
| Finding and comparing information, market or supplier research, briefs | `researcher` |
| Posts, articles, newsletters, descriptions, copy, editing, tone of voice | `writer` |
| Projects, tasks, deadlines, statuses, plans, meeting logistics | `coordinator` |
| Onboarding, courses, quizzes, explaining to newcomers, feedback on practice | `trainer` |
| Strategy, positioning, campaigns, roadmaps, business cases, options | `strategist` |
| Checking work against standards: review, audit, QA, compliance | `reviewer` |
| Tickets, helpdesk, customer questions, troubleshooting, escalation | `support` |
| Code, scripts, SQL, APIs, automation, bugs, infrastructure, tech docs | `engineer` |
| Design, UX/UI, layouts, brand visuals, accessibility, image prompts | `designer` |

First look up the role in `references/roles.md`: it gives the usual archetype mix, workflows, sources to ask for and extra red lines — use them as defaults in the interview. Choose one primary and up to two secondary. Read each chosen file in `archetypes/` before writing the spec: it gives default workflows, red lines, interview add-ons and test ideas. Ask the archetype add-on questions in round 2 or 3 instead of generic ones when they are more specific.

## Showing the spec

Summarize the spec for approval in the user's language, max ~15 lines:

- Name and title
- Who it is for
- Tasks (workflows), one line each
- What it will not do
- Red lines
- Level and where it runs; autonomy level (and allowlist), memory, schedules
- Sources: what the knowledge rests on; what remains `TODO: verify`
- Assumptions you made

End with a direct question: approve or change? Do not build before an explicit yes.
