# 3J paper — manager handoff, 2026-08-06 (**writing phase STARTS; v4 is CLOSED**)

**Paste this whole file as the first message of a fresh session.**

---

## 0. Who you are

You are the **manager (Opus)** for the **3rd journal paper (3J)**. The pipeline work is finished; this
is a **writing** phase. Plan, decide, write prompts for employee sessions, and review. Do not execute
long mechanical builds yourself — hand those to a Sonnet/Haiku employee with a written task doc.

**First read `CLAUDE.md` and `memory/MEMORY.md`.** Reply in **English** even though the user writes
French. Casual, ≤100 words unless detail is asked for.

---

## 1. Read first, in this order

1. **`3J_docs_occ_nTemp/writing/implementation/3rd_Occ_Journal_BuildInstructions.md`** — the build
   brief. Buckets A (8 schematics) / B (10 tables) / C (7 figure relocations) / D (9 chapters), the
   folder convention, the hard rules, and the final report template. **This is the working document.**
2. `3J_docs_occ_nTemp/PAPER_SERIES.md` — one table: what 1st / 2nd / 3rd mean.
3. `3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` — the pipeline, the
   gate set, the key design decisions, and the pointer to the consolidated limitations.
4. `3J_docs_occ_nTemp/improvements/v2/V2-G1_FROZEN_DELIVERABLE.md` — the arm the paper reports.
5. `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md` — the 2nd paper, **for form**, and for the
   only 2J numbers that may be cited.

---

## 2. Scope — settled by the user, do not relitigate

**The paper is Leg-3, the 4-split:** four occupancy channels — residential `AT_HOME`, office
`AT_WORK`, retail `AT_RETAIL` (the one new GSS channel), hotel (non-GSS, from provincial tourism
statistics) — driving four uses inside the PNNL **Tall** and **SuperTall** mixed-use towers, Montréal
6A and Calgary 7A. **56 cells.**

🔴 **Leg-2 (2-split) is a STEP toward Leg-3, not a co-headline.** The user's own call, 2026-08-06:
*"est une etape pour construire Leg-3."* It belongs in **Methods** — the stage the three-head model
grew from, and the source of the People-field wiring-bug gate — plus the additive-ledger table.
**No results section. No parallel narrative. No billing in the abstract.**

🔴 **"four building archetypes" is a 2J phrase and is wrong here.** 2J had SingleDetached /
OtherDwelling / MidRise / HighRise. Leg-3 has **four channels × two towers × two cities**. Write
*four channels driving four uses inside one building*.

### Which project is which

| role | path | for what |
|---|---|---|
| **the project** | `3J_docs_occ_nTemp/` | all content, all numbers, all figures |
| **reference** | `2J_docs_occ_nTemp/` | **form only** — structure, table style, prose conventions. Read-only |
| **reference** | `eSim_writing/methodology/` | 1st-journal methodology notes. Read-only |

---

## 3. What is already done

- `writing/implementation/3rd_Occ_Journal_BuildInstructions.md` — written.
- `PAPER_SERIES.md` — written.
- The **two-directory hazard is resolved** (§5).
- **v4 is closed:** 7 done · 2 withdrawn · 2 blocked of 11. Nothing is owed by the user on that ledger.

**Nothing has been drafted yet.** No figure copied, no table authored, no chapter written. The next
action is STEP 1 of the brief (asset verification), then Buckets A–D.

---

## 4. Two hazards that change what the manuscript may claim

### 4.1 🔴 Three EUI gates are FAILING and stay failing

From the consolidated limitations (sixteen items, five groups, fifteen carrying a number):

- **Office (L4)** — the **uninjected `Default_NECB` control** scores **85.45** against a floor of
  **100**. A gate no untreated control can pass measures the band, not the model. Two explanatory
  mechanisms were tested and **both refuted, 56/56 cells.**
- **Hotel (L5)** — `S9-EUI-hotel` FAILs **28/56**, every failure **above the 300 ceiling**, every one
  on **`Tall`**; range **203.33–318.42**.
- **Retail (L7)** — median-in-band rule, not all-cells; the gate was turning on **0.15 % of its floor**.

**These are written up as band-applicability findings, at full strength.** Do not widen a band,
re-basis a metric, or select the rule that passes. That is a standing project rule (R1, 2026-07-21)
and it is the most defensible material in the paper.

### 4.2 🔴 The 2J numbers changed on 2026-08-06

`V4-B4` recomputed all 6,000 runs behind 2J's Table 5. Corrected residential EUI:
**SingleDetached 115 · OtherDwelling 100 · MidRise 108 · HighRise 78 kWh/m²·yr**, and **all four now
sit below** their NRCan SHEU bands — three of four verdicts changed.

- Any 3J sentence citing 2J magnitudes **must use these values.**
- Source of truth: `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md`. **Not** the archived
  pre-`V4-B4` copies, and **not** `writing/sharingCHV/2ndOcc_Journal.docx`, which still carries the
  stale table.
- Leg-3 was **verified immune** (it reads hourly meters, not the tabular summary). Worth one sentence
  in Limitations as a reproducibility point.

---

## 5. The two-directory hazard — RESOLVED, here is the short version

`Leg3_4-split/Step9_docs/` holds two siblings sharing **11 filenames**:

| | |
|---|---|
| ✅ **`outputs_step9_deliverable/`** | frozen 2026-08-06 00:05 — **canonical, everything comes from here** |
| ⚠️ `outputs_step9/` | 2026-07-31 — superseded; reading it is the `V4-A1` error (hotel **inverts**, and **both directories report "28 of 56"**) |

**`outputs_step9/` must not be deleted or renamed** — it holds 8 files that exist nowhere else,
including the three `finding9_verify/` IDFs and the **uninjected control** behind the office finding.

**Three mechanisms handle it. Use them; do not re-derive the comparison.**

1. `_PROVENANCE.md` in **both** directories — the full collision table with md5s.
2. `improvements/v2/V2-G1_FROZEN_DELIVERABLE.md` § *Step-9 deliverable assets* — md5 of every
   canonical figure and table.
3. **`improvements/v5/f3_asset_provenance_check.py`** — verifies copied assets **by content**, so it
   still works after a file is renamed to `Figure_07_eui_4ch.png`. Run it after any figure copy.
   Live **5 PASS / 0 FAIL**; `--falsify` fails C1 on a real superseded copy.

> ℹ️ **`fig_diurnal_4ch.png` is byte-identical in both directories — this is a non-issue, not a risk.**
> Both copies are the same bytes, so either is correct and there is nothing to decide. The checker
> labels it `AMBIGUOUS` only to say *it cannot report where a copy came from*. **Do not present this to
> the user as a problem** — that framing already caused one round of confusion. Just note the source
> directory when copying it, and never generalise from it to the other four figures, which do differ.

---

## 6. Standing rules — in force

- **🔴🔴 NEVER run `srun`, any python, or any computation on the Speed login node. ALWAYS `sbatch`.**
  Flagged three times; one more = account suspension. Every submission requests `-t 7-00:00:00`.
- **Speed, as amended 2026-08-06 by the user:** `ssh`/`scp` to **fetch** a file is permitted;
  `sbatch`, `srun`, simulation campaigns and bare `python` on the login node remain **forbidden**.
  *"Blocked because the file is on Speed"* is not a valid status. **Reachability is not availability** —
  the user grants scope; do not infer it. **One Speed stream at a time** (a second concurrent transfer
  gives `scp rc=255`).
- **This is a writing phase: zero simulation cells.** No campaign, no EnergyPlus run.
- **No band value moves. No gate verdict is changed.** Never resolve a gate by picking the rule that
  passes (R1, 2026-07-21). A correct input is never withheld because it deepens a FAIL.
- **Do not fabricate a number.** `⚠ check source` in a cell is a successful outcome. Read every value
  from the cited artefact — including hashes: **never carry a truncated md5 forward as if it were the
  hash** (this happened on 2026-08-06 and its own checker caught it).
- **Archive the predecessor** (`archive/<name>.<date>_pre_<reason>.md`) before editing anything.
  Corrections are **additive** — strike through, do not delete.
- **Re-run the checks at closure, not at authoring.** `f1_frozen_input_check.py` was green at 14:59
  and red by 16:15 on 2026-08-06 because code written afterwards was code it never saw.
- **Deep research is EXTERNAL.** Never spawn research agents or verify citations yourself. The
  deliverable is a `V<NN>` prompt in `deepResearch_Resources/`; the user runs it in Gemini
  Antigravity. All five rounds so far returned at least one fabricated number.
- **Never count lines with PowerShell** (`Measure-Object -Line` miscounts — use `wc -l`).
  `py -3` is the only working Python invocation in this shell.
- **Every closure runs the three-artefact ritual in the same response, unprompted:** the plan's
  Progress Log, this manager prompt, and the board republished at its fixed URL —
  <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213> — plus memory. Every decision
  carries a **recorded reason** and a **written reopen trigger**.

---

## 7. Two items still sitting with the user (from v4, not blocking the writing)

1. **Sign-off** on the single interpretive sentence in the rewritten §5.2 of `readySubmission.md` —
   that a current-code NECB-2017 / NBC-9.36 envelope should sit below survey averages of the existing
   stock. It is a judgement, not a measurement.
2. **Decision** on `2J_docs_occ_nTemp/writing/sharingCHV/2ndOcc_Journal.docx`, which still carries the
   old table as "Table 4". Regenerating it from the corrected `.md` is the safe route; it was left
   alone on purpose (fragile XML, and it is the copy that gets shared).

**Still blocked, correctly:** `V4-C2` (needs an authorised `sbatch` validator run — not granted) and
`V4-C3` (prompt `V07_qc_hotel_occupancy_pre2019.md` is written and awaits an external run).

---

## 8. 🟢 RUN TO COMPLETION — the user's instruction, 2026-08-06

> **"continuer jusqu'a la fin avec des taches"** — work through the whole build, as tasks, to the end.

**This supersedes any earlier "ask before drafting prose".** You are authorised to run T1 → T12 below
without stopping for approval between tasks. Do not ask *"shall I continue?"* — continue.

### 8.1 First action: create the task ledger

Create **`writing/implementation/3rdJ_paper_TASKS.md`** with the twelve tasks below, each in the
project's task format — **aim · steps · expected result · test method** — and a **Progress Log**
section at the bottom. Append a dated entry to the Progress Log **as each task closes**, stating what
was produced, what was verified, and anything left `⚠ check source`. That file, not conversational
memory, is the handoff state.

### 8.2 The tasks

| ID | task | done when |
|---|---|---|
| **T1** | STEP 1 asset verification (brief §3) | exact filenames reported; `f3_asset_provenance_check.py` output pasted; source directory named for every asset, including `fig_diurnal_4ch.png` |
| **T2** | Bucket C — relocate the 7 existing figures (brief §6) | all 7 copied; `f3` re-run **5 PASS / 0 FAIL**; any C2 hit explained, not waved through |
| **T3** | Bucket B — Tables 2, 3, 6 (channels · simulation domain · Leg-2→Leg-3 delta) | authored from source; every "bit-identical" cell in T6 backed by a file or md5, never by prose |
| **T4** | Bucket B — Tables 4, 5 (validation gates · EUI vs bands) | the **Provenance column** separates ASHRAE G14 / project-chosen / heuristic; the three failing gates appear at full strength with their numbers |
| **T5** | Bucket B — Tables 1, 7 (gap matrix · the sixteen limitations) | limitations **transcribed**, not rewritten; **L15 still marked *not quantified*** |
| **T6** | Bucket B — SI tables A1–A2, B1, Appendix C | B1's "bands moved" column reads **0 in every row**; Appendix C carries every correction listed in the brief |
| **T7** | Bucket A — the 8 schematic prompts (brief §4) | one fenced prompt per figure, saved as `figures/<name>.md`; Figure 3 labelled **3 GSS heads + 1 non-GSS side-track** |
| **T8** | Bucket D — Chapters 2, 3, 4 (Datasets · Methods · Experimental Design) | Leg-2 appears **only** as the construction stage and the wiring-bug gate; no Leg-2 results |
| **T9** | Bucket D — Chapter 5 (Results) | every number traces to a table from T3–T6; the three failing gates are stated with their numbers in the sentence that states them |
| **T10** | Bucket D — Chapters 1, 6, 7, 8 (Introduction · Discussion · Limitations · Conclusion) | the office band-applicability argument rests on the **uninjected control**; Limitations matches Table 7 |
| **T11** | Assembly (brief §8) | `fullSet/3J_full_manuscript.md` + `readySubmission.md`, both built from one source **or** each stamped with its campaign identifier — the 2J divergence must not repeat |
| **T12** | Final build report (brief §9) + closure | report filled in; **all three checks re-run at closure** (`f1`, `f2_no_reopen`, `f3`); confirmation that no band moved and no gate verdict changed |

**Order is a guide, not a constraint.** T3–T6 may run in any order and are good candidates to hand to
a Sonnet employee in parallel with a written task doc each. **T8–T10 must follow T3–T6** — prose cites
tables, so the tables exist first.

### 8.3 Rules while running

- **Delegate the mechanical work.** Bulk table transcription, figure copying, and log scanning go to a
  Sonnet/Haiku employee with a written task doc — never done in the manager's own context.
  **Fresh employee session per task**, pointed at `3rdJ_paper_TASKS.md`; do not resume long threads.
- **A blocked task does not block the round.** Mark it `BLOCKED` with its reason in the ledger, finish
  every other task, and report what was left out and why. Scaling the work down is the user's call.
- **`⚠ check source` is a successful outcome.** An invented number is not. If a value cannot be found,
  leave the cell blank, flag it, and keep going.
- **Escalate to the user only for:** a genuine contradiction between two source artefacts; a number
  that would require a simulation to obtain; or anything that would move a band, a threshold, or a
  gate verdict. Everything else is yours to decide and record.
- **Run the three-artefact ritual at closure** (T12), in the same response, unprompted.

### 8.4 Report at the end

One summary: what was produced, which cells are `⚠ check source`, what is `BLOCKED` and why, the
final `f1`/`f2`/`f3` results, and the explicit confirmation that **no band value moved and no gate
verdict changed**.
