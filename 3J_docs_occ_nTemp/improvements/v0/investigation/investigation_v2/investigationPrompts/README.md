# investigationPrompts — independent replication of the backward audit

Two prompts for two **external** models, each asked to perform the same backward audit of the Leg-3
pipeline that was performed here on 2026-08-03/04 — **blind to that audit, and blind to each other.**

Opened 2026-08-04. The reason is stated plainly in the audit's own self-assessment: ten of its twelve
falsifiers have not been run, so most of it is argued rather than measured. A second and third pair of
eyes, working from the same artefacts but without the first auditor's framing, is the cheapest
available test of whether that framing missed anything.

| File | For | Emphasis |
|---|---|---|
| `PROMPT_codex_backward_audit.md` | **Codex** | **Code and artefacts** — read the `.py`, re-derive logged numbers from the data, parse the IDFs, interrogate the validators as programs |
| `PROMPT_gemini_backward_audit.md` | **Gemini** | **Claims and provenance** — build a register of every load-bearing claim in the design docs, trace each to its source, sweep for cross-document contradiction |
| `REPORT_codex_backward_audit.md` | *(produced by Codex)* | findings numbered **C-1, C-2, …** |
| `REPORT_gemini_backward_audit.md` | *(produced by Gemini)* | findings numbered **G-1, G-2, …** |

Both prompts share the same entry point — `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md` and its
`_Overview.md` — the same standard of evidence, and the same deliverable structure. Only the starting
axis differs, so that the two sweeps overlap as little as possible.

## The blindness protocol, and why it is a whitelist

Both prompts open with a **whitelist**: inside `improvements/investigation/`, the only file the auditor
may open is its own prompt. Everything else under that path — the prior audit, this README, the folder
README, `deepResearch Prompts/`, and the other auditor's prompt and report — is off-limits.

A whitelist rather than a blacklist because the prompts *live inside the folder they must not read*, and
a blacklist with an exception is exactly the kind of rule a model talks itself out of.

Two files outside that folder are partially contaminated, because the 2026-08-04 session wrote the prior
audit's findings into them: `improvements/3rdJ_L3_improvements_step9.md` (`§0.21.4 Q2`, `Q8a`, `Q8b`) and
`improvements/3rdJ_L3_step9_READER_GUIDE.md` (`§1.4` rows `Q2`/`Q8a`/`Q8b`, `§2` rows 20–21). Both
prompts name those passages and give a `grep` that locates them. Both files are otherwise legitimate and
should be read.

Each report must open with a filled-in **blindness declaration**. A declared contamination is
recoverable; an undeclared one silently invalidates the comparison — which is why both prompts say
explicitly that admitting it is better than hiding it.

## What to do with the two reports

Do **not** merge them into the audit on arrival. The comparison is the result:

1. **Agreement across all three** on a finding neither of the others could have copied → the finding is
   established about as well as desk work can establish it.
2. **Something in C or G that the audit missed** → the reason this was run. Add it with its own number
   and credit the source.
3. **Something the audit claims that neither C nor G reproduces** → not refutation, but it downgrades
   confidence, and it identifies exactly which claims most need their falsifier run.
4. **Disagreement on a value** → one of the three read the wrong artefact. Settle it from the artefact,
   never by majority.

Keep `C-` and `G-` numbering separate from the audit's `B-` numbering permanently. Renumbering into one
series would destroy the provenance that makes the three-way comparison worth anything.

## Constraints given to both

Read-only. No cluster jobs, no EnergyPlus runs, no retraining. `Leg2_2-split/` is frozen. Every finding
carries a **falsifier** — the one cheap measurement that would kill it — and `path:line` citations.
Findings that weaken the papers, including the already-submitted 2J manuscript, are to be reported
plainly rather than softened.
