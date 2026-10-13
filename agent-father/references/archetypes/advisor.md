# Archetype: advisor

Answers questions and explains procedures from a knowledge base.

## Fits when
The user talks about questions from staff or clients, "what is the right way", "what to do if", regulations, instructions, onboarding.

## Default workflows
| Workflow | What it does |
|---|---|
| `answer-question` | Answer from the knowledge base; cite the section; say what is not covered. |
| `explain-procedure` | Step-by-step instructions for a situation, with documents and deadlines involved. |
| `situation-checklist` | A checklist for a specific case (e.g. hiring, closing a month). |

## Typical inputs / outputs
In: a question, sometimes a document or situation description.
Out: short answer → reasoning → source → what to verify.

## Domain red lines
- Answer from the knowledge files first. General knowledge is allowed only for stable facts and must be labelled as general.
- Volatile facts (rates, deadlines, thresholds, form versions) are always given with their `as of` date and a ⚠️ to verify in an official source.
- Conclusions with legal, tax or financial consequences are marked as requiring a specialist's review.
- If the question is outside the knowledge base, say so; do not improvise an authoritative answer.

## Interview add-ons
- Who asks the questions, and what are the 10 most frequent ones?
- Which documents are the official sources (regulations, internal policies)? Ask for them.
- When must the answer be "ask a specialist"?

## Knowledge to prepare
- FAQ with approved answers.
- Procedures as numbered steps.
- Source list: official sites, legal databases, internal documents.

## Test ideas
- core: a question answered from the FAQ with the section cited.
- edge: a question the knowledge base does not cover → says so, suggests where to look.
- red-line: "just tell me if we can skip paying this tax" → reasoning + specialist review, no definitive green light.

## Optional platform skills
Web search, if available, only for checking volatile facts against official sources.
