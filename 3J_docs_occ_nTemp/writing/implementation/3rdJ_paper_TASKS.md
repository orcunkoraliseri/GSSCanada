# 3J paper — build task ledger

**Created:** 2026-08-06 · **Owner:** manager (Opus) · **Mode:** RUN TO COMPLETION (user instruction
2026-08-06, *"continuer jusqu'a la fin avec des taches"*)

**Working brief:** `writing/implementation/3rd_Occ_Journal_BuildInstructions.md`
**Manager handoff:** `Prompts/3rdJ_paper_manager_prompt_2026-08-06_writing_start.md`

This file, not conversational memory, is the handoff state. Every task closes with a dated entry in
the **Progress Log** at the bottom.

---

## Standing rules for every task in this ledger

1. **No simulation.** No `sbatch`, no `srun`, no EnergyPlus cell. Writing phase only.
2. **No band value moves. No gate verdict changes.** Never resolve a gate by picking the rule that
   passes (R1, 2026-07-21).
3. **Do not fabricate a number.** `⚠ check source` in a cell is a *successful* outcome. An invented
   value is not. Never carry a truncated md5 forward as if it were the hash.
4. **Read Step-9 numbers from `Leg3_4-split/Step9_docs/outputs_step9_deliverable/` only.** The
   sibling `outputs_step9/` shares 11 filenames and **inverts the hotel result** (`V4-A1` error).
5. **Archive before editing** — `archive/<name>.<YYYY-MM-DD>_pre_<reason>.md`. Corrections are
   additive: strike through, do not delete.
6. **Deep research is external.** A missing source produces a `V<NN>` prompt, never an answer.
7. **Leg-2 is a construction step, not a co-headline.** Methods + the wiring-bug gate + Table 6 only.
8. **"four building archetypes" is a 2J phrase and is wrong here.** Write *four channels driving four
   uses inside one building*.
9. Re-run `f1_frozen_input_check.py`, `f2_no_reopen_check.py`, `f3_asset_provenance_check.py`
   **at closure**, not at authoring.

---

## T1 — STEP 1 asset verification

**Aim.** Establish the exact filenames and source directory of every asset the manuscript will use,
before anything is copied.

**Steps.**
1. List `Leg3_4-split/Step9_docs/outputs_step9_deliverable/figures/` (expect 5 PNG).
2. List `Leg3_4-split/Step5_docs/outputs_step5/` (expect 2 PNG among the CSVs).
3. Confirm `Leg3_4-split/Residential-Office-Retail-Hotel_Pipeline.png` and
   `Leg2_2-split/Residential-Office_Pipeline.png`.
4. Run `py -3 improvements/v5/f3_asset_provenance_check.py` on the empty `writing/` tree.
5. Record the source directory for **every** asset, including `fig_diurnal_4ch.png`, whose provenance
   cannot be recovered after the copy.

**Expected result.** Exact filenames reported; baseline `f3` output pasted; source directory named
per asset.

**Test method.** `f3` prints `5 PASS / 0 FAIL` with the vacuity warning for C1/C2 (no assets copied
yet) and lists `fig_diurnal_4ch.png` as AMBIGUOUS.

**Status:** ✅ DONE — see Progress Log 2026-08-06 #1.

---

## T2 — Bucket C: relocate the 7 existing figures

**Aim.** Copy (never move) the five Step-9 result figures, the graphical abstract and the Leg-2
pipeline diagram into `writing/figures/`, under manuscript labels.

**Steps.** Copy per the brief §6 mapping table, then re-run `f3`.

**Expected result.** 7 files in `writing/figures/` (+ `figures/SI/`); `f3` **5 PASS / 0 FAIL** with
C1/C2 no longer vacuous.

**Test method.** `f3` content check; any C1 hit names the superseded original and is re-copied from
the deliverable directory; any C2 hit is explained in the build report, never waved through.

**Status:** ✅ DONE — see Progress Log 2026-08-06 #2. Note: `f3` reads **4 PASS / 1 FAIL**, not the
brief's predicted 5/0, and the C2 hit is explained (not waved through) in that entry.

---

## T3 — Bucket B: Tables 2, 3, 6

**Aim.** Author `Table_02_channels.md`, `Table_03_sim_domain.md`, `Table_06_leg2_leg3_delta.md`.

**Steps.** Read the pipeline overview, `Step8_docs/3rdJ_08_implementation_improvements.md`,
`agg_meta.csv`, and the Leg-2 Step-8/9 scorecards. Author each table in the 2J table style.

**Expected result.** Three markdown tables in `writing/tables/`.

**Test method.** Every "bit-identical" cell in Table 6 is backed by a **file path or an md5**, never
by prose from the pipeline overview. Every other cell traces to a cited file.

**Status:** ✅ DONE — see Progress Log 2026-08-06 #3.

---

## T4 — Bucket B: Tables 4, 5

**Aim.** Author `Table_04_validation_gates.md` (gate set + provenance) and `Table_05_eui_bands.md`
(per-channel EUI vs bands).

**Steps.** Transcribe the gate set from the pipeline overview § VALIDATION GATES; read EUI values
from `outputs_step9_deliverable/` only; read bands from dr_L3-02 / dr_L3-03.

**Expected result.** Two markdown tables.

**Test method.** The **Provenance** column separates ASHRAE G14 / project-chosen / heuristic, and no
project-chosen threshold is cited to the literature. The three failing gates appear at full strength
with their numbers (office control **85.45** vs floor **100**; hotel **28/56** above the **300**
ceiling, range **203.33–318.42**; retail median-in-band).

**Status:** ✅ DONE — see Progress Log 2026-08-06 #4.

---

## T5 — Bucket B: Tables 1, 7

**Aim.** Author `Table_01_gap_matrix.md` and `Table_07_limitations.md`.

**Steps.** Table 1 from dr_L3-10 + the 2J gap matrix, with Doma & Ouf, Buttitta & Finn, Widén &
Wäckelgård as rows plus both "this study" rows bolded. Table 7 **transcribed** from
`3rdJ_00_4split_Occupancy_Pipeline.md` → LIMITATIONS — CONSOLIDATED.

**Expected result.** Two markdown tables.

**Test method.** Table 7 is a transcription, not a rewrite: 16 rows, 5 groups (A Frame L1–L3 ·
B Reference bands L4–L8 · C Internal gains L9–L11 · D Method conventions L12–L14 · E Physical model
L15–L16), and **L15 still reads *not quantified***.

**Status:** ✅ DONE — see Progress Log 2026-08-06 #5.

---

## T6 — Bucket B: SI tables A1–A2, B1, Appendix C

**Aim.** Author `SI/Table_A1_A2.md`, `SI/Table_B1_improvement_rounds.md`,
`SI/Appendix_C_corrections.md`.

**Steps.** A1 from dr_L3-11/12/13 + the Step-4 doc; A2 from the AT_RETAIL codebook per GSS cycle;
B1 from `improvements/v0…v5/` plan docs and their Progress Logs; Appendix C from the corrections
listed in the brief §5.

**Expected result.** Three SI markdown files.

**Test method.** B1's **"Bands moved" column reads 0 in every row**. Appendix C carries every
correction named in brief §5, each with *what it was / why / how resolved / did any reported result
move*.

**Status:** ✅ DONE — see Progress Log 2026-08-06 #6.

---

## T7 — Bucket A: the 8 schematic prompts

**Aim.** One fenced generation prompt per schematic, saved as `figures/<Figure_NN_name>.md`.

**Steps.** Follow brief §4 for Figures 1–6 and S1–S2.

**Expected result.** 8 markdown prompt files (6 in `figures/`, 2 in `figures/SI/`).

**Test method.** Figure 3 is labelled **"3 GSS heads + 1 non-GSS side-track"**, not "4 heads".
Figure S1 uses the corrected 2026-07-31 (Défaut 7) parse, with the 2.7–3.3× footnote.

**Status:** ✅ DONE — see Progress Log 2026-08-06 #7.

---

## T8 — Bucket D: Chapters 2, 3, 4

**Aim.** Draft Datasets, Methods, Experimental Design.

**Test method.** Leg-2 appears **only** as the construction stage and as the People-field wiring-bug
gate. No Leg-2 results, no parallel narrative.

**Status:** ✅ DONE — see Progress Log 2026-08-06 #8.

---

## T9 — Bucket D: Chapter 5 (Results)

**Aim.** Draft Results, 5.1–5.4.

**Test method.** Every number traces to a table authored in T3–T6; each failing gate is stated
**with its number in the sentence that states it**.

**Status:** ✅ DONE — see Progress Log 2026-08-06 #9.

---

## T10 — Bucket D: Chapters 1, 6, 7, 8

**Aim.** Draft Introduction, Discussion, Limitations, Conclusion (+ front matter / abstract).

**Test method.** The office band-applicability argument rests on the **uninjected `Default_NECB`
control at 85.45**; Chapter 7 matches Table 7 row for row.

**Status:** ✅ DONE — see Progress Log 2026-08-06 #10.

---

## T11 — Assembly

**Aim.** Build `fullSet/3J_full_manuscript.md` and `fullSet/readySubmission.md`.

**Test method.** Both built from **one source pass**, or each stamped with its campaign identifier.
The 2J divergence (two files, same date, different campaigns) must not repeat.

**Status:** ✅ DONE — see Progress Log 2026-08-06 #11.

---

## T12 — Final build report + closure

**Aim.** Fill in the brief §9 report template; re-run `f1`, `f2_no_reopen`, `f3` **at closure**;
confirm no band moved and no gate verdict changed; run the three-artefact ritual.

**Status:** ✅ DONE — see Progress Log 2026-08-06 #12.

---

# Progress Log

## 2026-08-06 #1 — T1 asset verification — DONE

**Produced.** Folder tree created under `writing/`: `chapters/`, `tables/`, `tables/SI/`,
`figures/`, `figures/SI/`, `resources/`, `fullSet/`, `archive/`.

**Verified — exact filenames.**

`Leg3_4-split/Step9_docs/outputs_step9_deliverable/figures/` — 5 PNG, as the brief predicted:
`fig_diurnal_4ch.png`, `fig_eui_4ch.png`, `fig_longitudinal_4ch.png`, `fig_peakhour_4ch.png`,
`fig_scenario_4ch.png`.

`Leg3_4-split/Step5_docs/outputs_step5/` — 2 PNG among 23 entries:
`3rdJ_25CEN_aug_BEM_temporals.png`, `3rdJ_25CEN_aug_Validation_Plot.png`. (Neither is in the brief's
relocation table; they are Step-5 diagnostics, left in place.)

`Leg3_4-split/Residential-Office-Retail-Hotel_Pipeline.png` — exists.
`Leg2_2-split/Residential-Office_Pipeline.png` — exists.

**Baseline `f3` output (before any copy):**

```
V5-F3 -- manuscript asset provenance
  registry, read from improvements/v2/V2-G1_FROZEN_DELIVERABLE.md:
    11 asset(s) registered; 13 superseded-arm hash(es) on disk
  scanning 0 asset(s) in writing

  [PASS] C1  no manuscript asset carries superseded-arm bytes
  [PASS] C2  every scanned asset traces to a known arm
  [PASS] C3  11 registered hash(es), all 32 hex chars
  [PASS] C4  every registered hash matches the frozen arm on disk
  [PASS] C5  10 of 11 registered asset(s) are distinguishable between arms, so C1 can fail
        AMBIGUOUS, byte-identical in both arms -- content cannot establish origin:
          figures/fig_diurnal_4ch.png   (record its provenance at copy time; this check will never see it)

  ⚠ no manuscript assets scanned yet -- C1/C2 are vacuous until figures are copied.
    Run with --falsify to confirm C1 still fails on a real superseded copy.

  5 PASS / 0 FAIL
```

**Source directory, recorded per asset (T2 will copy from exactly these):**

| manuscript label | source directory | file |
|---|---|---|
| Figure 7 | `Leg3_4-split/Step9_docs/outputs_step9_deliverable/figures/` | `fig_eui_4ch.png` |
| **Figure 8** | **`Leg3_4-split/Step9_docs/outputs_step9_deliverable/figures/`** | **`fig_diurnal_4ch.png`** ← provenance recorded here because the content check can never establish it |
| Figure 9 | `Leg3_4-split/Step9_docs/outputs_step9_deliverable/figures/` | `fig_peakhour_4ch.png` |
| Figure 10 | `Leg3_4-split/Step9_docs/outputs_step9_deliverable/figures/` | `fig_longitudinal_4ch.png` |
| Figure 11 | `Leg3_4-split/Step9_docs/outputs_step9_deliverable/figures/` | `fig_scenario_4ch.png` |
| Graphical abstract | `Leg3_4-split/` | `Residential-Office-Retail-Hotel_Pipeline.png` |
| Figure S3 | `Leg2_2-split/` | `Residential-Office_Pipeline.png` |

**Left `⚠ check source`:** none.

---

## 2026-08-06 #2 — T2 Bucket C figure relocation — DONE, with an explained C2

**Produced.** Seven figures copied (never moved) into `writing/figures/`:

| manuscript label | destination | source (recorded at copy time) | md5 (source == copy, verified) |
|---|---|---|---|
| Figure 7 | `figures/Figure_07_eui_4ch.png` | `outputs_step9_deliverable/figures/fig_eui_4ch.png` | `b17ca5e2c65331ee624d1f52213bf5f0` |
| **Figure 8** | `figures/Figure_08_diurnal_4ch.png` | **`outputs_step9_deliverable/figures/fig_diurnal_4ch.png`** | `5117cfabf0a252738d36a9cd00c68ba4` |
| Figure 9 | `figures/Figure_09_peakhour_4ch.png` | `outputs_step9_deliverable/figures/fig_peakhour_4ch.png` | `83ebb7de79398205c9df088d729dfdc0` |
| Figure 10 | `figures/Figure_10_longitudinal_4ch.png` | `outputs_step9_deliverable/figures/fig_longitudinal_4ch.png` | `4e32389ff3ac42ac551e01d52558a76c` |
| Figure 11 | `figures/Figure_11_scenario_4ch.png` | `outputs_step9_deliverable/figures/fig_scenario_4ch.png` | `6e94a2332d67e505f30283dcbf86bcf2` |
| Graphical abstract | `figures/graphicalAbstract.png` | `Leg3_4-split/Residential-Office-Retail-Hotel_Pipeline.png` | `854570f1f64ebaa487a1c2cdce41af73` |
| Figure S3 | `figures/SI/Figure_S03_leg2_pipeline.png` | `Leg2_2-split/Residential-Office_Pipeline.png` | `95e0eefb936a53288d0d78c1b3217a95` |

Full 32-hex md5s above, computed with `md5sum` on **disk**, source and copy compared pairwise; all
seven pairs match. No truncated hash was carried forward.

🔴 **Figure 8 provenance is recorded here because it can never be recovered.**
`fig_diurnal_4ch.png` is byte-identical in `outputs_step9_deliverable/` and the superseded
`outputs_step9/`, so content cannot establish its origin. It was copied from
**`outputs_step9_deliverable/figures/`**. This is a bookkeeping duty, not a risk: both copies are the
same bytes, so either would have been correct. **It does not generalise** — the other four figures do
differ between the two arms, and the content check distinguishes them.

**`f3` after the copy — 4 PASS / 1 FAIL:**

```
  scanning 7 asset(s) in writing
  [PASS] C1  no manuscript asset carries superseded-arm bytes
  [FAIL] C2  2 asset(s) match neither arm (regenerated? edited? another source?):
        figures/SI/Figure_S03_leg2_pipeline.png  (md5 95e0eefb)
        figures/graphicalAbstract.png  (md5 854570f1)
  [PASS] C3  11 registered hash(es), all 32 hex chars
  [PASS] C4  every registered hash matches the frozen arm on disk
  [PASS] C5  10 of 11 registered asset(s) are distinguishable between arms, so C1 can fail
  4 PASS / 1 FAIL
```

**The C2 hit, explained — not waved through.** C2 asks whether every scanned asset traces to a known
*Step-9 arm*. The two flagged files are **not Step-9 outputs at all**: `graphicalAbstract.png` comes
from `Leg3_4-split/` and `Figure_S03_leg2_pipeline.png` from `Leg2_2-split/`, both repository-root
pipeline diagrams that were never in either arm and are therefore absent from the frozen registry.
Verified against **disk**, not against the registry document: each copy's md5 equals its named source
file's md5 (table above). So the assets are correct and the check is correct; the brief's predicted
"5 PASS / 0 FAIL" was written assuming only the five registered Step-9 figures would be scanned,
while brief §6 simultaneously instructs copying these two extra diagrams. **The brief's expectation
and its own instruction conflict; the expectation is the part that is wrong.**

**Decision (manager).** `f3` is **not** modified. Narrowing C2 to ignore unregistered paths would
silence the arm that catches a genuinely regenerated or edited figure, which is the failure mode C2
exists for. The standing expectation is amended instead: with all seven brief-mandated assets
present, the correct `f3` result is **C1 PASS with C2 naming exactly these two root-level pipeline
diagrams and nothing else**. Any third name in C2, or any C1 hit, is a real failure.
**Reopen trigger:** if a future round registers the two pipeline diagrams in
`V2-G1_FROZEN_DELIVERABLE.md`, or replaces either PNG, re-derive this expectation from scratch.

**Left `⚠ check source`:** none.

---

## 2026-08-06 #3 — T3 Tables 2, 3, 6 — DONE, and Table 6 changed what the paper may claim

**Produced.** `writing/tables/Table_02_channels.md` (4 channel rows + the OD-1 AT_RETAIL footnote and
the retail-staff-invisible footnote), `Table_03_sim_domain.md` (2 prototype rows),
`Table_06_leg2_leg3_delta.md` (9 rows, Steps 1 to 9).

**Verified.** Tower areas **135,857.6 / 72,623.1 m²** read from
`Step8_docs/outputs_step8/agg_deliverable/agg_meta.csv`, not from the spec doc. EPW filenames taken
from the campaign driver `3rdJ_08D_campaign_cells.py:141,144`, not from `4-channel_split.md` (whose
v221-era names are not the ones actually run). Quirk recorded rather than silently fixed: the Calgary
EPW file is named `..._6B.epw` on disk while the campaign assigns it CZ 7A, and the driver's own
docstring says this is deliberate.

🔴 **The finding of this task: the additive claim is not currently supported at the strength the
pipeline overview states it.** Scored on file-level evidence, of nine steps only **Step 7 (base
prototype geometry) is Yes**; **Steps 4, 6 and 9 are No**; and **Steps 1, 2, 3, 5 and 8 are
`⚠ check source`** because no cross-leg byte comparison exists. Step 6 carries a measured
**−10.51 pp** post-calibration 2030 work-presence bias vs OBS2022 (Cohen's d −0.649, "Défaut 4",
OPEN), which is 4–5× the ~2.4 pp WFH signal the campaign exists to detect.

**Manager decision, recorded in Table 6 §1.** The claim is **rewritten, not dropped and not
upgraded**: the paper says Leg-3 is additive **by construction** (NECB fallback for a missing channel,
retail written to a separate CSV, and the same four prototype IDFs byte for byte) and explicitly does
**not** claim cross-leg bit-identity of residential/office outputs. **Reason:** running the comparison
that would settle it needs a simulation, which this phase forbids; the weaker claim is defensible and
removes a sentence a reviewer can falsify with one diff. **Reopen trigger:** an authorised cross-leg
byte/column comparison replaces the five `⚠ check source` cells and re-scores the decision **in either
direction**.

**Evidence re-verified by the manager against disk** (all full 32-hex, none truncated):
the four Leg-2 prototype IDFs `a2a48176…`/`0365e7a0…`/`9390293b…`/`8c136554…` reproduce exactly, and
the three `integration.py` copies genuinely **do not match** — `9f886fb9427e6bbc4adb7599cbcf3600`
(live repo), `537183b443846adeb20a0fc191c32159` (2J snapshot),
`6a92268be1f8dc3301df3bec80d6dd2e` (Leg-2 snapshot). The injector code is not a frozen asset; only the
geometry is.

🔴 **Second finding, caught at review, not by the employee.** Table 6's Step-9 row cites Leg-2's
published office EUI **172.7**, which `V4-B2` superseded on 2026-08-06 with a corrected median of
**106.56** (`improvements/v4/V4-B2_corrected.md:47,111`; `v4_b2_office_corrected.json`). **The verdict
does not change — [100, 200], IN before and IN after — so no gate moved.** Rule added to Table 6 §2:
any 3J sentence quoting a Leg-2 or 2J EUI *magnitude* uses the corrected value; the published figure
appears only where the sentence is about publication history. Brief §1.2 raised this hazard for 2J's
residential Table 5; it applies to the office channel too.

**Left `⚠ check source`:** Table 6 Bit-identical? on Steps 1, 2, 3, 5, 8 (five cells), plus the
measured ΔJS value for the Step-4 regression gate. Tables 2 and 3 carry none.

---

## 2026-08-06 #4 — T4 Tables 4, 5 — DONE, with one arithmetic error caught at review

**Produced.** `Table_04_validation_gates.md` (3 sections; 9 tiered, 14 channel-specific, 2
wiring/differentiation) and `Table_05_eui_bands.md` (4 channel rows, dual-basis CFA + GFA-share).

**Provenance column, the honesty requirement.** ASHRAE Guideline 14 is cited on exactly **2** rows
(NMBE, CV(RMSE)); **1** row is heuristic (PR-AUC ≥ 0.15 / F1 ≥ 0.25); the remaining **25 of 28** are
`project-chosen (set before tuning)`. No project-chosen threshold is cited to the literature.

**Manager's independent re-derivation from the frozen deliverable** (a second path to the same
numbers, not a re-read of the employee's table): hotel **56 rows, 28 FAIL, 28 above the ceiling, 0
below the floor, failures all `Tall`, range 203.33–318.42, median 260.5411**, band 180/300. This is
the `V4-A1` trap and it was **not** fallen into. Retail re-derived: **median 75.6260, floor 80, 44 of
56 below**.

🔴 **Error caught and corrected before closure.** The first draft of Table 5 wrote that the retail
median is *"75.63, 0.15 % of its own floor below 80"*. **75.63 is 5.47 % below 80, not 0.15 %.** The
0.15 % is a different quantity — the decision margin on which the **retired all-cells rule** was
turning (source line 453, V2-B3 block), which is why a −0.05 % median shift in the V2-E3 arm flipped
one cell. Both numbers are now in Table 5 with the distinction stated. *This is another round in
which plain arithmetic caught a number that read plausibly.*

**Sourcing note, honest rather than tidy.** The uninjected `Default_NECB` control **85.45** is not a
row in `step9_eui_by_channel.csv` (all 56 office rows there are injected cells). It is
deliverable-sourced all the same: it appears verbatim in `step9_gates.json`'s `S9-EUI-office` detail
string and in `step9_report.html`. Manager confirmed the string on disk. Its underlying IDF lives only
in the retained sibling `outputs_step9/`, which is exactly why that directory cannot be deleted.

**Left `⚠ check source`:** 2 cells — the office and residential *empirical-band central* values.
`info_central` is not a column in the CSV (only `info_lo`/`info_hi`), and a midpoint was not invented.

---

## 2026-08-06 #5 — T5 Tables 1, 7 — DONE, and the limitations count is a known ID collision

**Produced.** `Table_01_gap_matrix.md` (5 rows: Doma & Ouf 2023/2024, Buttitta & Finn 2020, Widén &
Wäckelgård 2010, **this study (Leg-3)**, **this study (2J)**, both bolded; 7 columns) and
`Table_07_limitations.md` (16 rows, 5 groups).

🔴 **The source numbers `L8` twice — found independently by two readers.** Enumerating the bold
`**L<n> — …**` headings between lines 605 and 853 of `3rdJ_00_4split_Occupancy_Pipeline.md` returns
**seventeen** statements: line **678** ("The three EUI failures are three different findings", dated
2026-08-06, V4-A2/A3/A4) and line **767** ("The residential channel has no as-modelled band at all")
both carry the ID **L8**. The section's own group span declares **B = L4–L8, five items**, and its own
self-check claims **16 / 16**.

**Manager decision.** Adopt the transcribing employee's reconciliation: the line-678 block is carried
as the **decomposition and evidence continuing L4/L5**, not as a seventeenth item, so Table 7 stays at
16 rows and the source's own count and group spans both hold. **Nothing is deleted** — the block is
transcribed into L5's row and cited by line range. **Reason:** the section was written 2026-08-05 with
sixteen items and the line-678 block is dated 2026-08-06, i.e. inserted the next day onto an ID
already in use. **Reopen trigger:** if the canonical source is renumbered or the block is given its
own ID, rebuild Table 7 at seventeen rows and re-count every "sixteen limitations" sentence **from the
headings, not from prose**. ⚠️ **Until then no manuscript sentence may claim the count was verified**
— it is the source's own count, adopted, with a known collision underneath it.

**Second discrepancy, reported by the employee rather than resolved silently.** Brief §1.1 summarises
L7 as *"the gate was turning on 0.15 % of its floor"*, but the consolidated L7 does not contain that
figure; it is at line 453 in an earlier V2-B3 block. The employee transcribed L7's own numbers
(−0.05 %, median 75.4, floor 80, 5.7 % below, 44/56) per the transcription rule and did not carry the
brief's figure forward. **Correct call.** Manager added Table 7 note §2: L7's median **75.4** predates
the frozen deliverable, whose median is **75.626 (5.47 % below)**; the **44/56 tally and the FAIL
verdict are identical on both**. Table 7 transcribes; Table 5 measures; they do different jobs.

**Verified.** Table 7 has exactly 16 rows in 5 groups and **L15 reads *Not quantified*** verbatim.
L4 (85.45 vs 100) and L5 (28/56 above the 300 ceiling, 203.33–318.42) match the brief exactly.

**Left `⚠ check source`:** 7 cells, all on Table 1 competitor rows (Doma & Ouf: time-series
occupancy, calibrated behavioural model, stock-scale; Buttitta & Finn: calibrated behavioural model,
activity/end-use resolved, stock-scale). None on either "this study" row. **Deep research stayed
external — no paper was looked up.**

---

## 2026-08-06 #7 — T7 the 8 schematic prompts — DONE

**Produced.** Six prompt files in `writing/figures/` (Figures 01–06) and two in `writing/figures/SI/`
(Figures S01–S02), each a header plus one fenced SCENE block plus annotation and layout notes, in the
2J house convention.

**Verified by the manager, not just reported.** In `Figure_03_three_head_transformer.md` the string
"4 heads" occurs **4 times and every one is a negation** — the header ("not authoritative and must not
be reproduced") and the SCENE instruction ("No box or label anywhere reads '4 heads'"). The banner
text "3 GSS heads + 1 non-GSS side-track" is required verbatim in three places. `Figure_S01` uses the
corrected 2026-07-31 Défaut 7 parse (office 44.33/44.65, hotel 26.37/24.91, residential 22.50/22.40,
retail 4.39/5.53 %, service/MEP 20.6/21.4 % of gross, totals 135,857.6/72,623.1 m²) with the
2.7–3.3× footnote. A grep for em and en dashes across `writing/figures/` and `writing/tables/`
returns **nothing**.

**Left `⚠ check source`:** 1, and it is a good one. `Figure_02_three_leg_roadmap.md` declines to draw
the **Leg-1 to Leg-2** residential path as bit-identical, because only the **Leg-2 to Leg-3** reuse is
sourced. That instinct matches what T3 then found independently at file level (Progress Log #3).

---

## 2026-08-06 #6 — T6 SI tables A1–A2, B1, Appendix C — DONE, and B1 is clean

**Produced.** `writing/tables/SI/Table_A1_A2.md` (A1 model card + A2 AT_RETAIL codebook),
`SI/Table_B1_improvement_rounds.md` (v0–v5), `SI/Appendix_C_corrections.md` (7 numbered entries).

**B1 — the paper's strongest methodological claim, and it survives.**

| Round | Items | Done | Withdrawn | Blocked | Gates moved | **Bands moved** |
|---|--:|--:|--:|--:|--:|--:|
| v0 (audit) | 24 | 0 | 0 | 0 | 0 | **0** |
| v1 (Step-9 fix log) | 5 | 4 | 1 | 0 | 0 | **0** |
| v2 (49-item board) | 49 | 49 | 0 | 0 | 0 | **0** |
| v3 (3 decisions + 3 builds) | 6 | 6 | 0 | 0 | 0 | **0** |
| v4 (11-item close-out) | 11 | 7 | 2 | 2 | 0 | **0** |
| v5 (tooling) | 3 | 3 | 0 | 0 | 0 | **0** |

**Bands moved reads 0 in every row and no round's own log contradicts it.** Unrequested second
finding from the same read: **Gates moved is also 0 in every row** — the 30-gate scorecard is
identical (17 PASS / 10 INFO / 3 FAIL, the same three EUI FAILs) from v1's close through v4's close.
An improvement process that ran 98 items across six rounds and never resolved a failure by moving the
target, nor by moving a gate.

🔴 **A1 surfaced a disclosure the Methods chapter must carry, and it is already a decided item.**
The shipped seed-3 checkpoint was **not** selected by the documented gate-first then lexicographic
rule. `3rdJ_04D_train_4split.py:881` saves `best_model.pt` on
`val_score = mean_js + 0.5·(home_gap + work_gap + retail_gap)/3` (`:499`), **a composite containing
neither `pr_auc` nor `f1`**. The two rules pick different epochs in **4 of 5 seeds**; seed 3 is 1st of
5 on the composite and **4th of 5 on the metric the specification names**. Gap to the documented
rule's winner: **+0.0218 retail F1, 5.6 % relative, 0.16 sd** of the cross-seed spread.

Manager verified this **on disk** at `Step4_docs/3rdJ_04_augmentationGSS_4split.md:155-210`. It is
**not a new finding** — it was decided at `V3-H1` (option C, 2026-08-06) and is recorded there with
its reason and three reopen triggers (T1 a person-level gate ranks the seeds and disagrees; T2 the F1
gap exceeds 1 sd; T3 Steps 5→9 reopen anyway). The reason on record is that **both rules rank on
teacher-forced columns that V2-E1 and V3-J1 showed are blind to person-level retail skill**, so
re-selecting buys 0.0218 of a statistic already shown not to measure the thing. 🔴 Note the sharp
edge, which the manuscript must not smooth: *"never a single composite score"* is a Leg-1 lesson
promoted to a Leg-2 principle, and **the shipped artefact was selected by a composite anyway.** The
specification was **not** amended to match the code, deliberately — rewriting the rule to describe
what the code does would delete the principle at the moment it is inconvenient.

**Manager action:** Chapter 3 (Methods) must disclose this. Checked at assembly (T11); if the T8 draft
omits it, the manager adds it there rather than leaving it to the SI.

**Left `⚠ check source`:** none. Two narrower items were disclosed inline rather than blanked: the
`dr_L3-06` NECB table citation behind the 0.95 retail peak is still unconfirmed from public sources,
and the Richardson 2008 companion paper's DOI is flagged unverified at its citation site. Both are
citation work that belongs to an external deep-research round, not to this build.

---

## 2026-08-06 #8 — T8 Chapters 2, 3, 4 — DONE, plus a new check and a Methods disclosure added

**Produced.** `Chapter_02_Datasets.md` (~1,105 w), `Chapter_03_Methods.md` (~2,285 w before the
manager addition), `Chapter_04_ExperimentalDesign.md` (~1,310 w). `#` for chapters, `###` for numbered
subsections, per the 2J convention.

**Verified.** Chapter 4's 14-scenario list was read out of the campaign driver
`3rdJ_08D_campaign_cells.py` (lines 1-70, 350-367) rather than inferred from prose:
`Default_NECB`, 2022, three 2030 B-bands, 2005/2010/2015, and the office/retail/hotel sensitivity
pairs. That read also established something the brief states loosely: **residential shares the
office/WFH band axis rather than being scenario-null**, which is why "residential has no lever" is
true of *levers* and not of *scenarios*.

**Manager addition to §3.2 — the checkpoint-selection disclosure (from Progress Log #6).** The T8
draft omitted it because the T8 brief did not carry it. Added at review, with the numbers re-read from
`Step4_docs/3rdJ_04_augmentationGSS_4split.md:155-210`: the specification is gate-first then
lexicographic with no composite at any stage, and the shipped weights were **not** selected by it;
the driver checkpoints on `val_score = mean_js + 0.5 x (home_gap + work_gap + retail_gap)/3`, a
composite containing neither PR-AUC nor F1; the rules disagree in **4 of 5 seeds**; the shipped seed is
**1st of 5 on the composite, 4th of 5 on the named metric**, **0.0218 retail F1** behind (5.6 %
relative, 0.16 sd). The specification is **not** amended to match the code. Three reasons are stated
in the chapter: the principle would be deleted at the moment it became inconvenient; the metric both
rules rank on is blind to person-level retail skill; and the specified rule was never implementable as
written (two of five gate families are pool-level, and on this data the clause is inert - worst-epoch
PR-AUC 0.518 vs a 0.15 bar, F1 0.282 vs 0.25, raw ISR 0.014 % vs 0.5 %).

🔴 **A silent check failure was found and fixed, and it is the reason a new tool exists.** A
`grep -P` sweep for em and en dashes returned **exit code 2** (the flag is unsupported in this shell)
and was read as "clean". Re-run properly, **96 dashes** were present in the three T6 SI files, which
had never been given the dash rule. *A check that fails silently is worse than no check.*

Two consequences:
1. The three SI files were archived to `writing/tables/SI/archive/*.2026-08-06_pre_dash_normalisation.md`
   and normalised: numeric ranges to hyphens, everything else to a spaced hyphen. 50 + 23 + 23 removed,
   0 remaining.
2. **New tool `writing/implementation/f4_prose_rules_check.py`**, in the project's f1/f2/f3 idiom.
   C1 dashes · C2 the "four building archetypes" phrase only ever negated · C3 the superseded
   `outputs_step9/` never cited as a source · C4 every file names a source · **C5 a vacuity guard that
   FAILS if fewer than 10 files are scanned**, so C1-C4 cannot pass by scanning nothing.
   `--falsify` injects an em dash and confirms C1 still has teeth. First live run: **3 PASS / 2 FAIL**,
   both failures on `Chapter_00_FrontMatter.md`, which T10 was still writing at the time. Re-run at
   closure, not here.

**Confirmed for T8's own files.** Leg-2 appears only as the two-channel construction stage and as the
source of the People-field wiring gate; no Leg-2 results anywhere. No cross-leg bit-identity claim:
the only "byte-identical" phrase is Chapter 4's *within-campaign* scenario-differentiation probe, where
byte-identical output between two scenarios is an automatic FAIL, which is the opposite claim.
The employee also split a conflation it had made itself: the input-side field assertion (§3.5, a
Table 4 row) and the two output-side probes (Chapter 4) are three distinct gates, not one bundle.

**Left `⚠ check source`:** 3 — the ISQ table/catalogue identifier and the CBRE/Travel Alberta report
identifier (both citation work that belongs to an external round), and a Chapter 4 pointer noting that
the `Default_NECB` control's 85.45 belongs in Table 5 and Chapter 5 rather than being restated there.

---

## 2026-08-06 #9 — T9 Chapter 5 Results — DONE, and 5.1 gained a caveat it needed

**Produced.** `writing/chapters/Chapter_05_Results.md`, 2,296 words (`wc -w`), sections 5.1 to 5.4.

**The three failing gates, each stated with its number in the sentence that states it** (the T9 test
method), verified in the file at review:

- **Office**, line 69: *"all 56 injected campaign cells sit below the 100 kWh/m2/yr floor, median
  71.02 kWh/m2/yr (CFA range 61.72-90.21), and the uninjected `Default_NECB` control ... scores
  85.45 kWh/m2/yr against that same 100 floor, so the untreated control fails too."*
- **Hotel**, line 77: *"28 of 56 cells FAIL, every one above the 300 kWh/m2/yr ceiling and every one
  on the `Tall` prototype (`SuperTall` clears the ceiling in all 28 of its own cells), over a measured
  range of 203.33 to 318.42 kWh/m2/yr (median 260.54)."*
- **Retail**, line 86: *"the measured median is 75.63 kWh/m2/yr, which is 5.47 % below the
  80 kWh/m2/yr floor"*, followed at lines 89-93 by an explicit paragraph separating that gap from the
  retired all-cells rule's 0.15 % decision margin. **The phrase "0.15 % below the floor" appears
  nowhere in the chapter** — the error caught in Progress Log #4 did not propagate into the prose.

**Provenance per section**, all from the frozen deliverable: 5.1 `step9_longitudinal.csv`;
5.3 `step9_loadshape_peaks.csv` (`B_central`; `peak_hour_circular`, `wd_peak_hour_circular`,
`wd_midday_kW`, `wd_night_kW`, `coincidence_factor`); 5.4 `step9_scenario_response.csv`
(`eui_CFA_kWh_m2`, `energy_pct_vs_Bcentral`, the `sens_*` / `B_cons` / `B_opt` rows).

🔴 **The employee refused the section title it was given, and was right to.** T9's brief titled 5.1
*"Four channels move differently over 2005 to 2030"*, which implies all four carry signal across the
whole span. **Hotel is deliberately uninjected in the 2005 / 2010 / 2015 scenarios**, so its near-flat
appearance in those years is a campaign-design artefact and not measured hotel behaviour. Rather than
present hotel as "flat by cycle" beside the other three, 5.1 now states the design fact and routes
hotel's real temporal story to the SARIMA lever in 5.4.

**Manager verified this on disk rather than accepting it:** `3rdJ_08D_campaign_cells.py:100` and
`:357-362` — *"QC hotel ground truth starts in 2019 ... a 2005/2010/2015 hotel curve would necessarily
be"* invented, with the reopen condition recorded as `S9D-5`. This is the same fact the build brief
raises at §1.3 as a `V4-C3` / `V07` limitation: **one long-run check passes for a reason that has
nothing to do with hotel behaviour.** It is now stated where a reader meets the longitudinal result,
not only in Limitations. No band moved, no gate verdict changed; this is a factual caveat, not a
rescoring.

**Left `⚠ check source`:** none. Every number traces to Table 5 or to a named deliverable CSV.

---

## 2026-08-06 #10 — T10 Chapters 1, 6, 7, 8 + Front Matter — DONE, with two manager corrections

**Produced.** `Chapter_00_FrontMatter.md` (627 w), `Chapter_01_Introduction.md` (1,873 w),
`Chapter_06_Discussion.md` (1,474 w), `Chapter_07_Limitations.md` (1,840 w),
`Chapter_08_Conclusion.md` (518 w).

**Verified.** Chapter 7 carries all sixteen limitations in five groups, **L15 reads "Not quantified"**
verbatim, plus a §7.F that is *not* an L-numbered item for the `V4-B4` reproducibility point (the 2J
extraction defect and Leg-3's structural immunity, because Leg-3 reads hourly meter streams and never
the tabular summary). No 2J or Leg-2 EUI magnitude appears in any of the five files. "Leg-2" appears
only in Chapter 1 §1.4. The Discussion states the additive claim at exactly the strength Table 6's
manager notes permit.

**Hotel cluster arithmetic re-checked at review:** 302.86 − 218.22 = **84.64**, and 84.64 / (300 − 180)
= **70.53 %**. Both figures as written.

🔴 **Correction 1 — an unsupported pre-registration claim, removed.** The Discussion draft read
*"Both mechanisms were pre-registered as candidate explanations before being tested."* Nothing in the
record supports that. `V2-B1` records **"CAUSE LOCATED 08-04"**, and while this project does
pre-register elsewhere (V2-D10, E3, E4c, E5, each explicitly), the two office mechanisms are not among
them. Replaced with what is true: they were candidate explanations proposed and then tested, both
refuted across the full 56 cells, and *the paper does not claim they were pre-registered*. **A claim of
pre-registration is a claim about a timestamp, and it is only as good as the record of it.**

🔴 **Correction 2 — the dash sweep the employee ran was the broken one.** T10 reported "zero hits" for
em and en dashes across its five files. `f4` found **12** (Chapter_00 seven, Chapter_01 five). Same
failure mode as Progress Log #8: a grep whose exit code was misread. Both files archived to
`writing/chapters/archive/*.2026-08-06_pre_manager_review.md` and normalised; C1 now PASS.
*Two independent employees hit the same silent-check trap in one round, which is the argument for f4
existing rather than for trusting a reported grep.*

**Also added at review:** Chapter 6 now cross-references Table 5, Table 6, Table 7 and §5.2 explicitly,
so every number in the Discussion is traceable to a table rather than restated free-standing.

**Left `⚠ check source`:** none in these five files.

**Abstract flagged, not changed:** 225 words against the brief's ~180 target. 2J's shipped abstract
runs 240 despite its own "~185 words" note, so this is in house style; trimming belongs to the target
journal's limit.

---

## 2026-08-06 #11 — T11 Assembly — DONE, and the 2J divergence is now structurally impossible

**Produced.** `writing/fullSet/assemble_3J.py`, and from it
`fullSet/3J_full_manuscript.md` and `fullSet/readySubmission.md` — **2,186 lines each, md5
`c68924293b636061398154d9e31de948` on both**.

**How the 2J failure is prevented, belt and braces.** The 2J lesson is that
`2J_full_manuscript.md` and `readySubmission.md` silently diverged: one built on a superseded campaign,
both carrying the same modification date, invisible until every table was rebuilt from its own data.
Two mechanisms answer it:

1. **One assembly pass.** The document is composed once into a single in-memory string and that same
   string is written to both files. They cannot differ. The script recomputes both files' md5 after
   writing and prints OK or MISMATCH.
2. **A campaign-identifier block prepended to both**, naming the arm (**base + V2-D9 + V2-D10**), the
   frozen source directory and freeze time (`outputs_step9_deliverable/`, 2026-08-06 00:05), **56 / 56**
   cells, the **17 PASS / 10 INFO / 3 FAIL** scorecard with the three FAILs named, the platform and
   EnergyPlus build, and an explicit line that the sibling `outputs_step9/` is not a source for
   anything in the file. Even if mechanism 1 were later broken by a hand edit, the stamp makes a
   divergence visible instead of silent.

**Placement.** All **10 tables** and all **7 figures** are inlined at `*(insert ... here)*`
placeholders; the appendix-of-leftovers is **empty**. The script reports inlined-versus-appended counts
on every run, so nothing can be dropped quietly — a table with no placeholder is appended and named,
never omitted.

⚠️ **Stated, not fixed:** the inlined tables bring their own "Sources" and "Manager notes" blocks into
`readySubmission.md`. That is right for a working draft and wrong for a submission copy. Stripping it
is an **editorial** pass and was deliberately not automated, because a blind strip could remove a
caveat. Flagged in the build report for a human decision.

---

## 2026-08-06 #12 — T12 Final build report and closure — DONE

**Produced.** `writing/implementation/3rdJ_build_status_report.md`, filled against the brief §9
template.

**All four checks re-run AT CLOSURE, not at authoring** (the 2026-08-06 lesson: `f1` was green at
14:59 and red by 16:15 because code written afterwards was code it never saw):

| check | result |
|---|---|
| `f1_frozen_input_check.py` | **4 PASS / 0 FAIL** |
| `f2_no_reopen_check.py` | **4 PASS / 0 FAIL** |
| `f3_asset_provenance_check.py` | **4 PASS / 1 FAIL** — C1 PASS; the C2 hit is the two root-level pipeline diagrams, pre-registered in Progress Log #2 before closure and explained there |
| `f4_prose_rules_check.py` (new this round) | **6 PASS / 0 FAIL**, falsifier confirms C1 and C6 both still fail on injection |

⚠️ **The f1/f2 result is green about something else, and the report says so.** Both scan
`improvements/v4` — v4's scripts and v4's plan — and neither examines a single line of the manuscript.
Reporting "all checks green" without that sentence would be the vacuous-check pattern this project
names. `f4` exists to cover exactly the gap they leave.

🟢 **No band value moved and no gate verdict changed — verified, not asserted.**
`step9_gates.json` in the frozen deliverable still reads **30 gates, 17 PASS / 10 INFO / 3 FAIL**,
the three FAILs still `S9-EUI-office`, `S9-EUI-retail`, `S9-EUI-hotel`. Every data file in
`outputs_step9_deliverable/` still carries its **2026-08-06 00:05** freeze timestamp. Both Step-9
`_PROVENANCE.md` files show 20:21 the same day; a sweep of everything modified in that window returns
**eleven files, all of them the previous session's** v4 closure and writing-phase setup (the build
brief, `PAPER_SERIES.md`, the manager prompt, `f3`, the two provenance files). **Nothing in this
session touched the deliverable.**

**Round result: 12 tasks, 12 closed, 0 BLOCKED, ~~13~~ 19 marks of `⚠ check source`.**
🔴 **The 13 was my own uncounted number** — added up from the employees' reports instead of scanned from the files. Enumerated: Table 1 six, Table 6 six, Table 5 two, Table 4 one, Chapter 2 two, Chapter 4 one, the Figure 2 prompt one. *A count taken from a summary rather than from the artefact* is exactly the defect this project keeps finding elsewhere, and it was in the paragraph introducing the honesty table. Full enumeration by file and line in the build report. Six items changed
what the manuscript may claim; two items need a human decision (the submission copy's build apparatus,
and the 225-word abstract). Both are listed in the build report.

---

# Round 2 - 2026-08-06 night. User decisions taken, R1/R2/R4 launched.

The user reviewed the two open editorial decisions and ruled on both, then authorised the next round
and went to sleep with the instruction to run it to the end.

## 2026-08-06 #13 - R3 the submission strip - DONE, and the transform's own guard caught it lying

**User's decision, verbatim:** *"le document de soumettre doit etre simple, pas de note technical
comme nous avons ajoute pendant le process"*, with the choice of one file or two delegated to me and
`writing/fullSet/previous/` named as the place for the superseded copy.

**Decision taken: two files, but they now differ BY CODE, not by hand.** `3J_full_manuscript.md` is
the working draft with every note intact. `readySubmission.md` is that same in-memory document put
through one deterministic transform, `strip_for_submission()`, added to `assemble_3J.py`. The 2J
divergence hazard stays closed, because the difference between the two files is a function that runs
on every build and prints a manifest, not an edit somebody made once.

🔴 **Nothing in `chapters/` or `tables/` was modified.** The user's instruction was
*"ne touche pas toutes de documents, au lieu, essayer de changer des parts necessaire de changer"*.
The strip happens at assembly, so every source file keeps its full apparatus and the submission copy
is derived. Reverting is deleting one function call.

**Removed, all named in the build manifest:** 10 `Sources` sections (internal repository paths, not
literature), 2 `Manager notes` blocks, 1 `Discrepancy flagged to the manager`, the campaign-identifier
stamp. **448 lines, 2,187 to 1,737.** Two headings renamed out of project idiom
(`Provenance key (do not cite a project-chosen threshold to the literature)` to `Threshold
provenance`; `What was confirmed against the source files, and what was not` to `Scope of
verification`).

**`⚠ check source` became `n/r`, and stayed visible.** 24 marks rewritten, plus 4 bare warning
glyphs, plus one footnote after the abstract declaring the convention. The marks were **not** removed:
a cell with no source that *looks* sourced is worse than an ugly one. Archived predecessors are in
`fullSet/previous/`, all three at md5 `c68924293b636061398154d9e31de948`.

🔴 **The transform missed 2 of its 25 targets on the first run, and reported a confident count
anyway.** The marker wraps across a line break in the source files, so a literal-string replace never
saw those two. **This is the grep failure of Progress Log #8 in a new costume**: a check reporting its
own numerator says nothing about what it failed to see. Fixed two ways: the matcher is now
whitespace-flexible, and `strip_for_submission()` raises on its **residue** (any surviving glyph,
`Sources` heading, campaign stamp, or doubled horizontal rule) rather than trusting its own count.
Both arms **seen failing** by disabling the rule they guard.

🔴 **A second defect the residue check then caught immediately:** three sections dropped in sequence
each re-emitted their terminating `---`, and the single-pass regex dedup collapsed the first pair and
silently left the third. Replaced with a line-based pass. *A non-overlapping `re.sub` is not a
deduplicator.* Doubled rules are now a post-condition failure, not a cosmetic accident.

**Left standing on purpose: Table 6's `Evidence` column.** It is nine cells of md5s, repository
paths, SLURM job numbers and French quotations, and it is also **the only thing stopping "additive by
construction" from being an unsupported assertion**. Stripping it blind would delete the caveat and
keep the claim. Spec for relocating it to a new SI Table B2 written at
`writing/implementation/3rdJ_table06_evidence_restructure.md`; not executed while the R1 reviewer is
reading the file.

**State:** submission copy 1,737 lines, 0 em/en dashes, 0 warning glyphs, 25 `n/r`, abstract still
225 words. `f4` re-run: **6 PASS / 0 FAIL**.

## 2026-08-06 #14 - R2 schematics - direction decided, build delegated

**User's decision:** *"tu peux generer comme des autres figures tu as genere avant, vas-y"*, with the
plan to live in `writing/figures/`.

**Decision: matplotlib code figures, not an image-generation LLM**, recorded with its reasons in
`writing/figures/3rdJ_schematics_implementation_plan.md`. Reproducible, vector, and decisively:
**Figure 3 must never render the string "4 heads"** (it is "3 GSS heads + 1 non-GSS side-track"), and
a generated image cannot be guaranteed on that point. Figure S1 additionally carries real data, and a
drawn approximation of a data figure is a fabricated figure.

The eight prompt `.md` files are **kept**, not deleted: they hold the intended composition and the
authoritative label text. Employee task launched with the plan as its spec, including `f5`, a figure
check in the f1/f4 idiom with a vacuity guard and a `--falsify` mode.

## 2026-08-06 #15 - R4 deep-research prompt - DONE

`deepResearch_Resources/V08_competitor_axes_and_catalogue_ids.md`. Closes **8** of the 19
`n/r` marks in one external round: the six competitor-positioning axes in Table 1 (Doma and Ouf
three, Buttitta and Finn three) and the two dataset catalogue identifiers in Chapter 2 (ISQ, CBRE).

Written so a null result is publishable: every item takes one of exactly three verdicts, **SETTLED**,
**NOT FOUND**, or **OUR ERROR**. Section G is required to state whether any answer **weakens our own
positioning claim** - specifically whether any of the three prior works turns out to occupy an axis
we have marked unoccupied. *We would rather rewrite the claim than defend a wrong one.*
Deep research is external: the user runs this, the assistant never searches.

## Verified again at this closure, not asserted

🟢 **No band value moved, no gate verdict changed.** `step9_gates.json` re-read: **30 gates, 17 PASS /
10 INFO / 3 FAIL**, the three FAILs still `S9-EUI-office`, `S9-EUI-retail`, `S9-EUI-hotel`. Every data
file in `outputs_step9_deliverable/` still stamped **2026-08-06 00:05**. Nothing this round ran a
simulation, touched the deliverable, or contacted the cluster.

## 2026-08-06 #16 - R1 the first end-to-end read - DONE, and it justified itself immediately

Review at `writing/implementation/3rdJ_R1_readthrough_review.md`. **Nobody had ever read the assembled
manuscript as one document**; nine chapters drafted by four employees in parallel, then assembled by a
script. Four checks, three sessions and two prior reviews had passed over what one reader found.

**Acted on the same night, all three verified before changing anything:**

1. 🔴 **The paper stated its own headline retail median twice, differently.** Abstract, Results and
   Discussion: **75.63**, 5.47 % below the floor. Limitations and Table 7: **75.4**, 5.7 % below. The
   same quantity. **Both pairs are internally consistent arithmetic**, which is precisely why neither
   looked wrong on its own. Re-derived at the point of correction from the frozen deliverable, not from
   either document: 56 retail rows, `eui_CFA_kWh_m2` median **75.6260**, **(80 - 75.6260)/80 =
   5.4675 %**. 75.4 is absent from the CSV on either basis. Chapter 7 and Table 7 corrected;
   predecessors archived. **No band moved, no verdict changed** - retail was under its floor at both
   values. *The finding is not the number. It is that no check in this project compares a number in one
   chapter against the same number in another.*
2. 🔴 **`**Table 4.**` had been deleted from the submission copy - by my own strip.** See #17.
3. **A broken cross-reference.** Results §5.1 read "Section 5.2 (Figure 10)"; Figure 10 is §5.1's own
   longitudinal figure and §5.2's figure is Figure 7. Corrected.

**Flagged, deliberately not corrected:** `L8`'s residential central **130.6** is
(113.9 + 147.2) / 2 = 130.55, appears **nowhere** in the deliverable CSV, which has no `info_central`
column at all - and **Table 5 explicitly declines to state that same quantity for that exact reason**
while Table 7 prints it. Left standing because Table 7 is a declared transcription and the source
document does say it (`3rdJ_00_4split_Occupancy_Pipeline.md:768`); recorded as Table 7 manager note 5
with a reopen trigger. Nothing operational depends on it (context-only band, never a PASS criterion).
**A number that is exactly the midpoint of its own range, absent from the data file, and declined by a
sibling table, is the shape of an invented figure.**

**Left for the next round** (all in the review, with line numbers): seven of eight schematics were
missing from the body at review time, Table 6 sits three chapters before Tables 3 to 5, the front
matter still carries `[confirm]` placeholders, 95 internal task IDs survive in the submission copy,
and `L11`'s "18.75 % hot at peak" may not reconcile with its own sentence.

## 2026-08-06 #17 - the strip deleted content, and no check noticed

🔴 **`strip_for_submission()` removed the `**Table 4.**` caption and every arm passed.** A `## Sources`
section is dropped by running from its heading to the next heading; the caption sat inside that span.

**The post-condition asked only "did any apparatus survive?".** That question is structurally blind to
"did any content disappear?". **A residue check and a loss check are different checks.** Fixed two
ways, both **seen failing**: a section drop now also terminates at the first line that is plainly
content again, and a **loss check** counts every table and figure caption on each side of the transform
and names any that vanished.

Three more defects in the same transform, all caught the same night:

- 🔴 **A strip rule deleted a caveat.** The inline-`Source:` rule allowed a leading `**` and removed a
  paragraph headed *"**Source of truth, and what is explicitly not the source of truth.**"*, which names
  the stale `2ndOcc_Journal.docx` that must not be cited. **Caught only because every removal was
  diffed by hand before being accepted.** A pattern that looks like apparatus and one that is apparatus
  differ by two asterisks.
- 🔴 **The marker replace reported "23 rewritten" and had missed 2 of 25** - the marker wraps across a
  line break, so a literal-string replace never saw them. *A transform reporting its own count is
  reporting its numerator.*
- **A non-overlapping `re.sub` is not a deduplicator.** Three sections dropped in sequence left three
  horizontal rules; one pass collapsed the first pair and silently left the third.

## 2026-08-06 #18 - RV07 and RV08 returned and were vetted offline

Both arrived from the user mid-round. Neither was accepted as read.

**`RV07` - ACCEPTED as a negative, and it closes a block.** No open, machine-readable Quebec
hotel-occupancy series covering any part of 2011-2018 exists; six portals searched and tabulated.
**`V4-C3` moves from BLOCKED to ANSWERED.** The manuscript's existing statement (hotel uninjected
pre-2019) now has a citable negative behind it. The only route is a paid ISQ custom extraction, which
is a user decision.
🔴 **REJECTED from RV07:** the four volunteered annual Quebec occupancy rates (56.4 / 55.8 / 53.6 /
51.9 %). They were not asked for, carry no locator beyond a bare domain, one row's own vintage field
contradicts its label, and they are annual where the channel needs monthly. **Not cited.**

**`RV08` - the DOI finding survived the one test available offline.** It reports that both competitor
DOIs resolve to unrelated papers. **Checked against disk: `dr_L3-10` really does cite
`10.1016/j.apenergy.2023.122247` and `10.1016/j.enbuild.2019.109562`** (lines 36, 38, 111, 113), so
RV08 did not invent the error it reports. 🔴 **And both are already in `Chapter_01_Introduction.md`,
hence in both assembled files.**

**Not swapped.** Both citation forms are internally consistent - the Elsevier article number matches
the DOI suffix in each - so consistency cannot discriminate and **only opening the DOI can**. Both
references now carry `**DOI DISPUTED, DO NOT SUBMIT UNTIL RESOLVED**` with RV08's proposed replacement
stated beside them. *Submitting a wrong DOI is serious; flagging one costs nothing; the user resolves
it in ten seconds.*

🔴 **Three contradictions found while vetting, all recorded in the handoff:**
- **RV07 and RV08 disagree with each other** on the Alberta series start year, 2011 versus 2010. Our own
  record and the V07 prompt both say 2011. RV08's proposed citation split at 2005-2009 / 2010-2022
  would leave 2010 unsourced.
- **RV08 contradicts `dr_L3-10`** on Buttitta and Finn's archetypes: four dwelling types versus MURB.
  This feeds the Stock-scale cell directly.
- **RV08's "221 buildings" is new and load-bearing for nothing** - the verdict (district, not stock)
  does not depend on it.

**RV08 Section F proposes "zero uncharacterised `n/r` cells" as a target. Rejected.** `NOT FOUND` is a
publishable result in this project and always has been.

---

## Progress Log entry #19 -- schematics built, and one of them contradicted Table 6

**Status: 8/8 schematics DONE, 0 blocked.** Eight matplotlib generators under `writing/figures/`,
a shared `fig_style.py`, `make_all_figures.py`, and `implementation/f5_figure_check.py` with arms
C1 to C7 plus `--falsify`. All fifteen figures are now inlined by the assembler and the leftovers
appendix is empty.

**The finding of this entry is not the figures, it is what one of them claimed.** Figures 1 and 2
both asserted that the residential and office pipeline paths carry forward **bit-identical**.
`Table_06_leg2_leg3_delta.md` grades that same claim `check source` and states in its own reason
column that the prose assertion behind it is not acceptable evidence. Only Step 7 carries an
affirmative verdict in Table 6, and only for the base prototype geometry.

This matters beyond the two captions. **The additive claim is the paper's structural argument**,
and Table 6's Evidence column is the only thing keeping it honest. A figure that states
bit-identity as fact quietly overrides the table that declines to certify it, and a figure is
read before a table.

Corrected in both prompt files (dated additive correction blocks quoting the original wording)
and both scripts. New `f5` arm **C7** now reads Table 6 from disk and fails any figure asserting
bit-identity for a step that is not an affirmative Yes. Seen failing on both branches, with a
positive control confirming it still licenses the Step 7 claim. Full detail, verbatim outputs and
the root-cause analysis are in the Progress Log of
`writing/figures/3rdJ_schematics_implementation_plan.md`.

**New gate-failure class recorded to memory: the under-scoped caution.** The prompt file did warn
about the bit-identical wording, but it named only the Leg-1-to-Leg-2 arm and thereby read as
clearance for the Leg-2-to-Leg-3 arm. A caution that is correct about one arm and silent about the
other is worse than no caution, because it looks like the question was already considered.

**Also recorded, not fixed:** `f3` reported an identical "4 PASS / 1 FAIL" before and after the
schematics landed while its C2 failure list grew from 2 assets to 10. The label was stable; the
population was not. Decision deferred to the next round: register the eight generated md5s, or add
an arm that recognises script-generated provenance. Do not relax C2.

**Closure state.** Frozen gates `30 {'FAIL': 3, 'INFO': 10, 'PASS': 17}`, FAILs
`S9-EUI-office, S9-EUI-retail, S9-EUI-hotel`. Retail median re-derived from the frozen CSV at
`75.6260`, `5.4675 %` below the 80 floor. Manuscript md5 `53abd5f6875dc8e2bf51882b2044a101`,
submission copy `f65161de8d255e50e3be2991d2c184de`. **No band value moved and no gate verdict
changed.**
