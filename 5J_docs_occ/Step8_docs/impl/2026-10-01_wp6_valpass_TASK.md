# 5J Step 8 part D: validation pass on the draft (task doc for a fresh employee)

Written 2026-10-01 by the 5J manager. Parent: `Step8_docs/5thJ_08_writing.md`; gates: `Step8_docs/5thJ_08_writing_val.md`.
State file you keep: `Step8_docs/impl/2026-10-01_wp6_valpass.md` (ledger, decisions, WHAT I DID NOT VERIFY; same form as
`Step8_docs/impl/2026-10-01_wp6_fig5.md`).

## 🔴 Rules (binding)
* UK licence: never open any UK diary file, UK episodes, UK manifests, any file pooling UK rows, or any output built from them.
  You need NONE of them: this task reads only the text files named below. No folder-wide or repo-wide search, no wildcard that
  could match a UK file: name every file in full.
* Compute: the author allowed half of the desktop (<=10 CPUs). This is a text job: run it locally with `py -3.13`, one process.
* Do not edit the manuscript. You report; the manager fixes.
* Never create files other than the three named under Outputs.
* No web access at all (CLAUDE.md: citation and DOI checks are external, done by the author). AMENDED 2026-10-01 by the manager after launch; message sent to the employee.

## Inputs (all under `C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/`)
* The draft: `writing/5J_manuscript_draft.md`.
* Number sources (frozen outputs and checked ledgers):
  `Step8_docs/impl/2026-10-01_wp6_draft.md`, `Step8_docs/impl/2026-10-01_wp6_s38.md`, `Step8_docs/impl/2026-10-01_wp6_s38_text.md`,
  `Step6_docs/outputs_step6/RESULTS.md`, `Step7_docs/outputs_step7/district_check_summary.md`, `Step7_docs/outputs_step7/speed.md`,
  `Step7_docs/outputs_step7/district_spread.csv`, `Step7_docs/impl/2026-10-01_wp5_district.md`,
  `Step5_docs/outputs_step5/winner.md`, `Step5_docs/outputs_step5/models.md`, `Step5_docs/outputs_step5/step5_rules.md`,
  `Step4_docs/outputs_step4/perturbations.md`, `Step2_docs/outputs_step2/campaign_design.md`.
  If a named file does not exist, say so in the state file; do not search for it.

## What the checker does (one script, `tools/5thJ_valpass.py`), one section per gate
1. **1.1 numbers.** Extract every number from the draft body (title to the end of Section 6, plus Appendix A, Table and figure
   captions; skip References, DOIs, years inside citations, section and figure numbers, list numbering). For each number,
   look for it in the source pool: exact text, or with thousands separators removed, or a source number that rounds to it at
   the shown decimals, or that source number /1000 (kWh to MWh) or x100 (fraction to %). Print every UNMATCHED number with
   its line number and sentence. Unmatched is not wrong: it is a list for the manager.
2. **1.2 verdict counts.** Print every "x of y" count and every sentence that holds pass / fail / not evaluable, with line
   number, next to the RESULTS.md line that holds the same count (or "no source line").
3. **1.3 and 1.4.** Print every hit of: first, to our knowledge, novel, for the first time, no previous, nobody, never been,
   and of the three not-claimed phrases (first building energy surrogate, first hourly residential stock surrogate, first to
   score a surrogate on differences), case-insensitive.
4. **2.1 and 2.2 citations.** Every in-text citation has a reference entry and every entry is cited (print both lists of
   orphans). List every DOI in References as text (no lookup); gate 2.2 is left to the external check.
5. **2.3 licence credits.** Print the sentences that credit INE, ISTAT and the UK Data Service. Find the required wording in
   `5thJ_00_Occupancy_Surrogate_Pipeline.md` (named file; search inside it only) and print it next to them.
6. **3.1 tool names** outside the section headed "Declaration of generative AI": Claude, Anthropic, Gemini, Google DeepMind,
   GPT, ChatGPT, OpenAI, Copilot, LLM, language model, Sonnet, Opus.
7. **3.2 meta and process notes** in prose and captions: not comparable, stated here, see above, placeholder, TBD, TODO, `[`
   (any bracket slot), FINDING, 5J, G5J, WP, B4, Step 1-8, manager, employee, ledger, sbatch, Speed cluster, job, our earlier
   draft, previous version, as decided.
8. **3.3** every hit of failure / failed / fails / failing, with line, marked GATE (a verdict word about a gate or a test) or
   PROSE (anything else). Your marking is a suggestion; the manager decides.
9. **3.4 figures.** Every `![Figure N](path)` path exists under `writing/`, and a script for it exists in `figures/scripts/`
   (name each script you matched). Figure 1 is expected to be missing (author-made drawing); report it, do not fail on it.
10. **4.1 data statement.** Print the Data availability section and every file or data set it promises; flag any mention of
    UK-derived outputs, weights or schedules as released.

## Planted faults (must be seen firing)
Copy the draft to a temporary file in your scratchpad (never into the repo) and plant: one "Claude" in a figure caption, one
"to our knowledge" in Section 1, one "failure" in a Limitations sentence, one fake number "7,777 kWh" in Section 3.2, one in-text
citation "(Smith et al., 2019)" with no reference entry, one "[TBD]" slot. Run the checker on the clean draft and on the planted
copy and print, per section, the hit count clean vs planted. Every plant must raise its section count by at least one.

## Exit code (print its meaning at the end)
0 = ran, every plant fired; 1 = a plant did not fire; 2 = could not run (missing input, exception). Hits on the clean draft do
NOT change the exit code: they are the report.

## Outputs
* `tools/5thJ_valpass.py` (the checker).
* `Step8_docs/impl/2026-10-01_wp6_valpass.md` (state file: run time from `date`, md5 of the draft read, counts per section,
  the full hit lists, plant table, exit code, WHAT I DID NOT VERIFY).
* The full printed log saved as `Step8_docs/impl/2026-10-01_wp6_valpass_log.txt`.

## Done means
The checker ran on the clean and planted copies, every plant fired, the state file lists every hit, and you did not edit the
draft.
