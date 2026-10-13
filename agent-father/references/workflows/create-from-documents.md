# Create an agent from a folder of documents

Purpose: the user gives a folder (regulations, instructions, templates, examples, exports) and Father builds an agent — or a team — whose expertise rests on those documents.

## Inputs
- Required: a folder or a set of files.
- Optional: the role, if the user already knows it.

## Steps

1. **Inventory**: `python3 scripts/father.py inventory <folder>`. It lists every file with type, size and a short text preview where it can read one (txt, md, csv, docx, xlsx sheet names). For PDFs, scans and other formats, use the platform's file skills to read them.
   — check: every file appears in the inventory; unreadable files are listed as such.

2. **Classify** each file:
   | Class | Goes to |
   |---|---|
   | Rules: laws, regulations, policies, instructions | `references/knowledge/` — summarized, every fact citing file name and section |
   | Templates and forms | `assets/` — converted to format-neutral masters; original kept if the user owns it |
   | Examples of good work | knowledge (patterns, tone) and `tests/fixtures/` (anonymized) |
   | Data exports | `tests/fixtures/` samples; field dictionaries in knowledge |
   | Irrelevant, duplicates, outdated versions | skipped, listed |
   Show the classification as a table and ask the user to correct it.
   — check: user confirmed or corrected.

3. **Propose the role**: from the documents, infer what work they support, look it up in `references/roles.md`, and propose one agent (or a team via `references/workflows/create-team.md` if the documents clearly cover several roles). Ask only the interview questions the documents do not answer.

4. **Coverage table**: map each workflow to the documents it rests on. Workflows with no document → general knowledge with `TODO: verify`, or drop them. Show it with the spec.

5. **Spec, approval, build, validate, package** — create-agent steps 4–10. Knowledge files are English summaries; quote official wording verbatim only where it must not change.

## Output
The agent (or team) plus a knowledge file `sources.md` listing every source file, its date or version, and where it is used.

## Before handing over
- [ ] Every document is used, skipped with a reason, or flagged unreadable.
- [ ] Every knowledge fact cites a file and section.
- [ ] Personal data from the documents is anonymized; confidential internal documents are summarized, not copied, if the package will leave the company — ask the user.

## Without scripts
List the files yourself (name, type, size) and read them with the platform's file tools; continue from step 2.
