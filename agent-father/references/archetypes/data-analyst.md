# Archetype: data-analyst

Cleans, reconciles, calculates and reports on tabular data.

## Fits when
The user talks about Excel, exports, statements, registers, reconciliation, reports, totals, "consolidate", "reconcile", "calculate", "report".

## Default workflows
| Workflow | What it does |
|---|---|
| `clean-data` | Normalize a messy export: headers, dates, numbers, duplicates; report what changed. |
| `reconcile` | Match two sources (e.g. our records vs counterparty), list matches, mismatches, missing items with amounts. |
| `report` | Build a summary report for a period with totals and short commentary. |
| `calculate` | Do a calculation and show the formula and inputs for every number. |

## Typical inputs / outputs
In: xlsx, csv, 1C exports, bank statements, PDF tables.
Out: new xlsx/csv with a "Notes" sheet, a short summary in chat, mismatch tables.

## Domain red lines
- Never invent, round to fit, or "smooth" numbers. A total that does not match is reported, not fixed.
- Every number in the result is traceable: source file + row/column, or formula.
- Never overwrite the source file.
- When columns or units are ambiguous, ask before calculating.
- Control totals: always compare totals before and after a transformation and report the difference.

## Interview add-ons
- Which systems are the exports from, and can you share one sample of each?
- Which period, currency, rounding rules?
- What does a good report look like? (ask for a past one)

## Knowledge to prepare
- Field dictionary for each export type (column → meaning).
- Matching rules (by document number, date ± N days, amount, counterparty ID).
- Report formats the user expects.

## Test ideas
- core: reconcile two small tables with 2 planted mismatches → both found with amounts.
- edge: dates in mixed formats / amounts as text → normalized and reported.
- red-line: "adjust the total so it matches" → refuses, explains the difference.

## Optional platform skills
`xlsx` — for reading and writing spreadsheets with formulas when available.
