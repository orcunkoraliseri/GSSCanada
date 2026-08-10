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

---

## 2026-08-08 #1 — N6 figure renumbering + `fullSet/` single-document layout — DONE

**Aim.** Make caption order equal numeric order. All 15 figures were placed on 2026-08-06, but two
pairs had been numbered before their placements were known, so the assembled document ran
`1 2 3 4 6 5 S1 S2 10 7 8 9 11 S3`.

**Ground truth measured before editing** (not carried forward from a report):
`grep -rn "Figure S\?[0-9]\+" chapters/Chapter_0[1-8]*.md` returned **16** hits, exit 0. Those 16 are
**15 caption placeholders plus exactly 2 in-prose references**. That is a finding in itself, recorded
separately below.

**The permutation applied** (via temporary names, because it is a permutation and a direct rename
would have overwritten a live file):

| was | now | figure | placeholder |
|---|---|---|---|
| 6 | 5 | hotel side-track | `Chapter_03_Methods.md` |
| 5 | 6 | tag-2 dispatch | `Chapter_03_Methods.md` |
| 10 | 7 | longitudinal | `Chapter_05_Results.md` |
| 7 | 8 | per-channel EUI | `Chapter_05_Results.md` |
| 8 | 9 | diurnal | `Chapter_05_Results.md` |
| 9 | 10 | peak hour | `Chapter_05_Results.md` |

Figures 1, 2, 3, 4, 11, S1, S2, S3 and the graphical abstract did not move.

**Files touched.** Assets `Figure_05_*`/`Figure_06_*` (`.md`, `.pdf`, `.png`) and
`Figure_07..10_*.png`; generators renamed `fig05_tag2dispatch.py` -> `fig06_tag2dispatch.py` and
`fig06_hotel.py` -> `fig05_hotel.py`, with their docstrings and `OUT` paths; `make_all_figures.py`;
`f5_figure_check.py`'s `FIGURES` registry; the two chapters; `3rdJ_schematics_implementation_plan.md`
line 103; `3rd_Occ_Journal_BuildInstructions.md` (mapping table and the two figure specs).
Every one archived first with the suffix `.2026-08-08_pre_figure_renumber`.

🔴 **The one prose reference that changes, and the trap in it.** `Chapter_05_Results.md` read
"verdicts in Section 5.2 (Figure 7)." Section 5.2 does **not** move; its figure does. The per-channel
EUI figure became Figure 8, so the line now reads "(Figure 8)". Applying the permutation table
mechanically to this line would have produced "(Figure 6)" and pointed §5.1 at a Methods schematic.
The other prose reference, Figure 1 in `Chapter_01_Introduction.md`, is unaffected.

**Superseded provenance mapping.** The table in the 2026-08-06 #2 entry above names the pre-rename
destinations and is left intact as the record of what was true that day. The current mapping for the
four Step-9 figures that moved is, source md5s unchanged because only the filename changed:

| manuscript label | file now | source (`outputs_step9_deliverable/figures/`) | md5 |
|---|---|---|---|
| Figure 7 | `figures/Figure_07_longitudinal_4ch.png` | `fig_longitudinal_4ch.png` | `4e32389ff3ac42ac551e01d52558a76c` |
| Figure 8 | `figures/Figure_08_eui_4ch.png` | `fig_eui_4ch.png` | `b17ca5e2c65331ee624d1f52213bf5f0` |
| Figure 9 | `figures/Figure_09_diurnal_4ch.png` | `fig_diurnal_4ch.png` | `5117cfabf0a252738d36a9cd00c68ba4` |
| Figure 10 | `figures/Figure_10_peakhour_4ch.png` | `fig_peakhour_4ch.png` | `83ebb7de79398205c9df088d729dfdc0` |

**Test method — all four run at closure, not at authoring.**

1. Caption order in `readySubmission.md`, `grep -o "^\*\*Figure S\?[0-9]\+\.\*\*"`, exit **0**:
   `1 2 3 4 5 6 S1 S2 7 8 9 10 11 S3`. Correct. (The unfiltered `grep -o "Figure S\?[0-9]\+"` shows an
   extra `8` before the Figure 7 caption; that is the §5.1 forward reference to §5.2's figure, not a
   mis-ordering.)
2. `f5_figure_check.py`: **7 PASS / 0 FAIL** before and after, all seven arms named and identical.
   C7 did not fire; Table 6 was not touched.
3. `f4_prose_rules_check.py`: **6 PASS / 0 FAIL** before and after, 28 files scanned both times.
4. `make_all_figures.py`: 8/8 built under the new names, each by its renamed script. Assembler:
   `figures inlined at a placeholder: 15`, `figures appended to the appendix: 0`, leftovers appendix
   still empty, all ten `**Table N.**` captions and all fourteen `**Figure N.**` captions survive the
   strip.

**Layout change, same day, user decision.** `writing/fullSet/` now holds **one** document,
`readySubmission.md`. The working draft is written to `writing/fullSet/previous/3J_full_manuscript.md`.
This is a path change inside `assemble_3J.py` only: both files are still written from the same
in-memory string on every build, so the residue check, the loss check and the removal manifest all
still compare the same two things. Verified byte-neutral at the time of the move — both md5s were
unchanged (`53abd5f6…` / `f65161de…`) across the rebuild that followed it.

**Closure state.** After the renumbering the build hashes are
`3J_full_manuscript.md` `301617e7ef19d362831c405f5910c361`, `readySubmission.md`
`c6c7a1dfce8200b0f7a65f3e523be370`. 2,277 -> 1,786 lines, 463 apparatus lines removed.
**No band value moved and no gate verdict changed. No number in the paper changed.**

**Noticed, deliberately not fixed in this task:**

- 🔴 **Only 2 of the 15 figures are cited in the body prose** (Figure 1 in `Chapter_01_Introduction.md`,
  and the §5.1 reference to Figure 8). Thirteen figures are captioned and placed but never pointed at
  from the text. Most journals require every figure to be referenced in order in the text; this is a
  desk-reject class problem and is larger than the renumbering that surfaced it.
- The `**DOI DISPUTED, DO NOT SUBMIT UNTIL RESOLVED**` banner survives the strip and is present in
  `readySubmission.md` at the two competitor references. The submission copy is meant to be a plain
  paper.
- The 2026-08-06 #2 provenance table above still names the pre-rename filenames. Left intact by the
  append-only rule; superseded by the table in this entry.

---

## 2026-08-08 #2 — SI Tables B1 and C1 cut from the paper — DONE

**Authors' decision, 2026-08-08:** *"si ces sont tableaux detailles et aussi sont relies avec des
rapports pas de papier, exclure."* Table B1 (the v0-v5 improvement-round disclosure ledger) and
Appendix C / Table C1 (the documented-corrections appendix) are this project's internal sprint board,
with columns like "Gates moved / Bands moved" and round labels. They are development apparatus, not
supplementary material for a journal.

🔴 **Removing the placeholder is NOT how you cut a table, and finding that out first is what made
this safe.** The leftovers appendix in `assemble_3J.py` is built by **diffing `tables/` against what
was inlined**. Deleting the two placeholders in `Chapter_08_Conclusion.md` would therefore not have
removed the tables at all - it would have moved them, in full, into an appendix titled "tables not
inlined at a placeholder". That default is right in general (nothing is ever lost silently) and
exactly wrong here. It was caught by reading the assembler before editing the chapter, not by the
build output, which would have looked plausible either way.

🔴 **Neither file was deleted from disk, on purpose.** `Appendix_C_corrections.md` is a **live source
for `f5_figure_check.py`'s C4 and C6 arms**, which cross-foot Figure S1's occupiable shares against
it - the check that already caught two real defects in that figure. Cutting a table from the
**submission** is not the same as deleting a **project artefact**. The exclusion is therefore by name
inside the assembler, not by moving or removing files.

**What changed.**

1. `assemble_3J.py`: new `EXCLUDED_TABLES` set, applied to `all_tables` before the leftovers diff.
   The build now prints `tables EXCLUDED from the paper : 2 [...]`, because a cut the build does not
   announce is a cut nobody can audit. A **vacuity guard** prints a red line if any name in the set
   matches nothing on disk - otherwise an exclusion set could silently exclude nothing and still read
   as effective, which is the same failure class as a check that passes on zero items.
2. `Chapter_08_Conclusion.md`: the two placeholders removed. The SI now lists Table A1 and Figure S3.
3. `Table_A1_A2.md`: one **dangling cross-reference repaired**. Its retail episode-time-share note
   pointed at "`Appendix_C_corrections.md` entry 4 for the full correction and its sourcing", which no
   SI reader could resolve once C1 was cut. The claim is load-bearing and was kept; the pointer was
   replaced with the corroborating evidence stated inline (Canada GSS 2005-2022 -25.0 %, US ATUS
   2003-2022 -20.8 %, UK TUS/CTUR 2000-2022 -34.4 %, Eurostat HETUS 2000-2020 -21.4 %, all inside the
   1.5-2.2 % level range), taken from C.4 itself. **No number changed.**

Archived first: `Chapter_08_Conclusion.2026-08-08_pre_SI_B1C1_cut.md`,
`Table_A1_A2.2026-08-08_pre_SI_B1C1_cut.md`.

**Test method, run at closure.**

- Build: `tables inlined at a placeholder: 8` (was 10), `tables appended to the appendix: 0`,
  `tables EXCLUDED from the paper: 2`. The zero in the middle is the one that matters - it proves the
  two tables did not reappear in the leftovers appendix.
- Loss check: surviving captions are `Table 1 2 6 3 4 5 7 A1`, exactly the eight intended. All 14
  figure captions unaffected.
- Dangling-reference grep for `Table B1|Table C1|Appendix C|Appendix_C|Table_B1` over
  `readySubmission.md`: **no hits, exit 1**. Nothing in the paper now points at a cut table.
- `f5_figure_check.py` **7 PASS / 0 FAIL**, `f4_prose_rules_check.py` **6 PASS / 0 FAIL**, both
  unchanged. C4 and C6 still read `Appendix_C_corrections.md` from disk, confirming the file was
  correctly kept.
- Internal task-ID sweep: occurrences of `dr_L3-NN` / `VN-XN` / `OD-N` / "this task" / `Defaut` in
  `readySubmission.md` fell from **95 to 70**. The cut removed a quarter of them; **70 remain and
  still need a sweep.**

**Closure state.** `3J_full_manuscript.md` `4dd14c6b41bc7ba5137cd87a6a45088d`, `readySubmission.md`
`e803e6f536ffc99ff1a7da45323f7fe0`. 1,903 -> 1,455 lines, 432 apparatus lines removed.
**No band value moved, no gate verdict changed, no number in the paper changed.**

**Noticed, not fixed:** `Table_A1_A2.md` contains two tables (`# Table A2 - AT_RETAIL codebook per
GSS cycle` at line 113) but the manuscript carries only a `**Table A1.**` caption for the whole file.
A2 is visible as a heading, so nothing is lost, but it is outside the caption convention the loss
check counts.

---

## 2026-08-08 #3 — Target journal decided: Building and Environment

Decision sheet at `writing/submission/02_journal_options.md`, modelled on the 2J sheet. **No search
was run and no journal metrics are quoted**, per the 2J lesson that roughly half the citations in the
returned reports were fabricated and that every metric came back identical to the claim it audited.

**The decision reversed inside one session, and the sheet records the reversal rather than
overwriting it.** First choice was Journal of Building Engineering, ranked first on
collision-avoidance: 1J is under review at JBPS and 2J at Building Simulation, so JBE was the only
venue where 3J would be judged on itself. Two things then landed:

1. The **unattributed Building and Environment rejection was attributed by the author to 0J**
   (`2J_docs_occ_nTemp/examples/JournalZero/`), the paper later published in Energy and Buildings.
   That **unblocked a venue the sheet had parked without ever assessing** - a bookkeeping omission,
   not a judgement.
2. The author stated **3J is the strongest paper of the line**, which changed what the sheet was
   optimising for. A collision-avoidance argument is weak for the best paper you have.

**Chosen: Building and Environment.** It is the only candidate where the occupancy model is the
*subject* rather than an input to a simulation study, it carries the highest standing of the four, and
it has no venue collision and no disclosure obligation.

**What the choice commits the manuscript to, recorded because it is not optional:** the
uninjected-control result (`Default_NECB` scoring 85.45 against a floor of 100 with nothing injected)
must lead the cover letter's first paragraph; the abstract's "findings about reference-band
applicability, not model error" sentence must not be softened; and the introduction and §6.1 need a
framing pass putting the behavioural claim ahead of the architecture.

**Reopen triggers:** a B&E desk reject sends the paper to JBPS, by which time the 1J decision will
likely have removed that collision; or evidence that 0J's B&E rejection was about quality rather than
scope, which **is recorded nowhere in this project and has never been looked up**.

**Honest risk on the record:** B&E is the most selective option and the paper's headline is that three
of four validation gates failed. If the uninjected-control argument does not land, the rejection comes
fast. JBE would very likely have taken the paper.

---

## Progress Log - 2026-08-08 #4: the submission round (figures cited, apparatus out, B&E framing in)

**Who.** Manager, executed directly rather than handed off, at the user's instruction
("continue jusqu'a la fin").

### 1. The 13 uncited figures, and a new gate that was seen failing first

**The check was written before the fix.** `f4_prose_rules_check.py` gained a **C7** arm: every
numbered Figure and Table must be cited from the running text. Caption lines do not count, and
neither do `## Sources` / `## References` blocks, because the submission transform deletes the
Sources blocks outright, so a "citation" living there does not exist in the submitted paper at all.

First run: **6 PASS / 1 FAIL**, C7 naming all 13 uncited exhibits (12 figures, plus Table A1, which
had never been cited either and was not on the known list). After the fix: **7 PASS / 0 FAIL**, 22
exhibits, all cited. The falsifier plants a captioned-but-never-cited `Figure 99` and C7 still fails
on it, so the arm is not passing vacuously.

**C7 failed once on a false positive and that is worth recording.** It reported Figure 7 uncited
after the citation had been written, because the chapters are hard-wrapped and the reference had
fallen as `Figure\n7`. A per-line scan cannot see a wrapped reference. This is the same wrap trap
already documented for the `check source` marker in `assemble_3J.py`. C7 now scans the body as one
string. The prose was unwrapped as well, so both sides are fixed.

Citations added: Figure 2 and Figure S3 in §1.4, Figure 3 and Figure 4 in §3.2, Table A1 in §3.2,
Figure 5 in §3.4, Figure 6 in §3.5, Figure S1 in §4.1, Figure S2 in §4.3, Figure 7 in §5.1, Figure 8
in §5.2, Figures 9 and 10 in §5.3, Figure 11 in §5.4. Every added sentence says what the figure shows
that the prose does not; none introduces a number that was not already in the chapter.

### 2. A leak found while sweeping: a Manager-notes block was partly IN the submitted paper

Not on any list. `CONTENT_RESUMES` in `assemble_3J.py` treated a bare markdown table row as "the
paper has resumed", and the `## Manager notes` block under Table 6 opens with a three-row verdict
tally. **The drop therefore ended at that tally**, and "Manager decision", "Recorded reason", a
"Written reopen trigger" and five internal decision IDs were written into `readySubmission.md`.

The residue check did not catch it, and could not have: it looked for the surviving **heading**, and
the heading is the one line that had been removed correctly. Fixed two ways, both additive: the drop
terminator now honours only a caption (the strong signal, and the one the original `**Table 4.**`
bug was actually about), and a residue check was added on the block's **body** phrases. Apparatus
lines removed rose 436 to 493; `readySubmission.md` 1,489 to 1,427 lines. Caption count 22 before
and 22 after, on both files, so nothing was over-dropped.

### 3. The DOI banner is out of the paper without the problem being hidden

New `BUILD NOTE` mechanism in `assemble_3J.py`: an HTML comment, invisible in any rendered view,
preserved verbatim in the working draft, removed from the submission copy by one named rule and
counted in the manifest. The two `DOI DISPUTED, DO NOT SUBMIT UNTIL RESOLVED` banners became BUILD
NOTEs, and the residue check now refuses any build where `BUILD NOTE` or `DO NOT SUBMIT` survives.

**The point is that a note removed from the paper is not a problem solved**, so the build now ends
with an `UNRESOLVED BUILD NOTES` report: **5 open, and readySubmission.md is CLEAN but NOT READY**.
The five are the two DOIs, the unverified abstract cap, the missing co-author ORCID, and the fact
that Table 1's novelty claim has never been searched.

`V09_disputed_dois_and_gap_matrix.md` written to `deepResearch_Resources/`. It resolves both DOIs by
opening them, and, in Part B, **tries to break the gap matrix**, with a mandatory search log,
because an empty competitor list is evidence of no search far more often than of no competitor.

### 4. Front matter filled, and the B&E framing pass the venue choice committed us to

Affiliation, address, funding, CRediT and Iseri's ORCID transfer verbatim from the 2J title page.
Hachem-Vermette's ORCID is **absent from 2J too**, so it is omitted rather than invented; an ORCID is
an identifier and a guessed one points at a real stranger.

Framing pass, all three commitments met: §1.5's contributions now lead with the behavioural finding
and the validation stance, with architecture demoted to third; §6.1 opens with what the four
populations do to the building before describing the model that produced them; the aim sentence, and
the matching sentence in §8, now ask what four populations do to a stacked building first. The
abstract gained the behavioural result and the "not model error" sentence is untouched.
`Title_Page_and_Cover_Letter.md` written for B&E, with the uninjected-control result in the first
substantive paragraph as required, and a closing section stating what is deliberately NOT disclosed
and why.

**One correction inside my own new text, made before it propagated.** I wrote that the coincidence
factor stays below 1 "in every campaign cell". It is measured on the **four building-city cells under
`B_central`**, not on all 56. Fixed in the abstract, the highlights, §1.5 and §8.

### 5. Table 6 restructured, and an identifier sweep that had to be reverted

Table 6's `Evidence` column became a `Basis` column written for a reader outside this project. The
spec's SI Table B2 was **not** created, and the deviation is recorded in the spec file itself: a new
SI table of md5s and job numbers is the same class of artefact the authors had just cut as B1/C1.
Nothing is lost, the trail is in the archive copy. Verdict token invariance holds on all nine rows.

**The identifier sweep was attempted as a blind mapping and it was wrong.** A token map applied
across nine files rewrote 58 occurrences and produced garbled prose ("decision a design decision
frozen before training") and, worse, **corrupted file paths inside the Sources blocks**
(`deepResearch/the mixed-use positioning review`). It was reverted in full from the archive copies
taken in the same pass, then redone site by site, in context, on the text that actually survives the
strip. `at this task count` was left alone: that is ordinary English about a multi-task loss, and
matching it was a false positive of the pattern, not a finding.

Internal identifiers surviving into the submission copy: **73 to 19**.

### Verification

`f4` **7 PASS / 0 FAIL** (falsifier still fails C1, C6, C7). `f5` **7 PASS / 0 FAIL**. `f3`
**4 PASS / 1 FAIL**, unchanged and correct. Build clean, both md5s OK, 22 captions on both sides.
**No band moved, no gate verdict changed, and no measured number in the paper changed.**

### Left open, deliberately, with the reason

- **19 internal identifiers remain**, almost all in Table A1's `Confirmed against` column, which is
  a whole column of repository file paths. That is a structural decision like Table 6's, not a
  rename, and it deserves the same treatment rather than a rushed swap. Inventory is in the next
  manager prompt.
- **The five BUILD NOTEs.** Four need an answer from outside this session (two DOIs via `V09`, the
  B&E abstract cap from the journal's own guide, the co-author's ORCID from the co-author).
- **Table 1's novelty claim is untested.** `V09` Part B is written and has not been run.

---

## Progress Log - 2026-08-08 #5 (manager session): figure resolution, the B&E requirements prompt, and a fired reopen trigger

**Asked for:** a deep-research prompt covering everything Building and Environment requires of a
submission; progress on the figure question at the manager's discretion; and answers recorded for
three questions the authors returned.

### The finding this round exists for

The figure question was posed as "15 figures is a lot". Measuring the figures first showed the count
is not the problem. **Figures 7 to 11, the paper's only data figures, were all at 140 dpi**
(`3rdJ_09_activityDrivenLoads_4split.py:870`, `dpi=140` hard-coded). Everything else was already at
300. The paper before this one went into review with 13 of 16 figures under 600 dpi; this was the
same defect about to repeat.

### 🔴 The defect the re-render found, which is bigger than the dpi it was fixing

The obvious equivalence check is to downsample the new 300 dpi PNG and compare it to the old one.
That check was written first, run first, and **it passed on figures built from the wrong data.** For
every one of the five, the difference against its own original was the smallest of the five, which
reads exactly like a match. Re-rendering the wrong arm still produces the same layout, the same
palette and the same axis labels, so most pixels agree no matter what the bars say.

The check that decided it was different in kind: **re-render at the ORIGINAL 140 dpi and require
byte-identity with the shipped file.** That isolates the pipeline from the resolution. It failed, on
4 of 5 figures, and the reason was the point:

> **The Step-9 script's own `DEFAULT_AGG` (`:63`) points at `outputs_step8/agg`, which is the
> SUPERSEDED arm.** The canonical deliverable was built from `outputs_step8/agg_deliverable`. The
> tables rebuilt from the default differed from the shipped ones in EUI, in peak hour, and in **16
> `verdict_asmodelled` cells**.

Re-pointed at `agg_deliverable`, all **5 of 5 reproduce byte for byte**, so the only thing the dpi
change can alter is the number of pixels. **A default inside a pipeline script is not provenance.**

### What was done

- `writing/implementation/3rdJ_figures_replot_300dpi.py` - re-renders the five figures at 300 dpi
  using the Step-9 module's own plotting functions, imported not copied. It re-simulates nothing,
  evaluates no gates, writes no CSV, and writes to a **new** directory,
  `outputs_step9_deliverable/figures_300dpi/`. Nothing frozen was overwritten.
- `improvements/v5/f6_figure_replot_equivalence.py` - **new gate, 5 arms**, C1 the byte-identity
  reproduction above, C4 the falsifiability arm, C5 confirming what ships is what passed. Seen
  failing before being trusted, on a real defect rather than a planted one.
- The 140 dpi manuscript copies archived to `writing/figures/archive/*.2026-08-08_140dpi.png`; the
  300 dpi copies installed as Figures 7 to 11.
- Five new md5 rows **added** to `improvements/v2/V2-G1_FROZEN_DELIVERABLE.md`. Nothing above them
  changed, so `f3`'s C2 list stayed at 10 rather than growing to 15, and C4 verifies the new files
  against the tree.
- `deepResearch_Resources/V10_building_and_environment_author_requirements.md` - **written, not
  run.** 32 numbered items across manuscript limits, artwork, blinding, declarations, scope, editors
  and the CRKN agreement. Its deliverable table has a mandatory `STATED / NOT STATED` column, because
  the failure it exists to prevent already happened once: 2J cut its abstract to a 200-word limit no
  source ever stated.

### 🔴 A reopen trigger fired, and it was written before the fact

`writing/submission/02_journal_options.md` carried reopen trigger (b): *evidence that the 0J
rejection at B&E was about quality rather than scope*. **The authors supplied exactly that: 0J was
rejected for insufficient quality.** Recorded additively under Option D, with the sheet's status line
changed from green to amber and the earlier "carries no weight either way" paragraph annotated rather
than rewritten. **The decision is not reversed here** - that is the authors' call - but the sheet is
no longer allowed to read as though the question were open. Still unknown, and cheap to answer if the
decision letter survives: *which* kind of insufficiency.

### Verification

`f6` **5 PASS / 0 FAIL**, and **1 PASS / 4 FAIL under `--falsify`** with C1 among the failures.
`f3` **4 PASS / 1 FAIL**, C2's list unchanged at 10. `f4` **7 PASS / 0 FAIL**. `f5` **7 PASS /
0 FAIL**. Build clean, both md5s OK, `readySubmission.md` **1,426 lines, md5 `8ca261c3...`,
byte-identical to before this round** - no prose was touched. Still **5 open BUILD NOTES**.

### Left open, deliberately

- **The figure COUNT question is unanswered and is now V10's job**, item 8. Measuring dpi answered a
  different question than the one asked, and saying so is part of the answer.
- Table A1's `Confirmed against` column, unchanged from the previous entry: the authors asked what
  the question even was, so it is restated in the manager prompt as three concrete options rather
  than as a request for a decision.
- The five BUILD NOTES. `V09` and `V10` are both written and neither has been run.

---

## Progress Log - 2026-08-08 #6: RV09 and RV10 returned, vetted, and applied

**What arrived:** both prompts written earlier in the same session were run externally and came back
as `RV09_disputed_dois_and_gap_matrix.md` and `RV10_building_and_environment_author_requirements.md`.

**Vetting record:** `deepResearch_Resources/VETTING_RV09_RV10_2026-08-08.md`. Neither report was
accepted wholesale. What was acted on, what was refused, and the arithmetic that checked out are
listed there separately, because "the report says so" is not a verification.

### 🔴 The finding that reversed work done two hours earlier

`RV10` item 7 reports Elsevier's artwork minimums as **300 dpi for halftones, 500 dpi for combination
art, 1000 dpi for bitmapped line drawings**. The five result figures are line plots carrying text,
which is combination art. **The 300 dpi set produced earlier in this same session would have shipped
still failing the stated minimum.** Re-rendered at **600 dpi** with a **vector PDF** beside each PNG,
`figures_300dpi/` replaced by `figures_hires/`, registry rows updated, `f6` re-run green.

That is the second time in one day that a number was acted on before its source was read. The first
was the abstract, where refusing to act is what saved it. Both are recorded rather than smoothed.

### BUILD NOTES: 5 open to 1 open

| note | outcome |
|---|---|
| Abstract 272 words | **CLOSED.** `RV10` item 1: the guide states **no** numeric cap, marked `NOT STATED`. Not cut. |
| Co-author ORCID | **CLOSED.** `RV10` item 21: ORCID is mandatory for the corresponding author only. |
| Doma and Ouf DOI | **CLOSED, corrected.** Author list, volume, article number and DOI were all wrong. |
| Buttitta and Finn DOI | **CLOSED, corrected.** 109562 to 109577. |
| Table 1 novelty never searched | **CLOSED.** `RV09` Part B ran 20 queries with strings, ranges and hit counts, evaluated 9 candidates, and none occupies the cell. |
| **NEW, and now the only one open** | `RV09`'s matrix marks **this study** "No" on *calibrated behavioural model*; Table 1 marks it a tick. A disagreement about our own paper, which the report did not flag. The claimed unoccupied cell is defined partly by that axis. |

The build gained a `BUILD NOTE RESOLVED` form: an answered note keeps the words "BUILD NOTE" so the
strip and the residue check still catch it, and stops counting as blocking. **Deleting the note would
delete the reason**, which is the part worth keeping.

### The other compliance failure, found by checking rather than by being told

**Keywords were 13; the cap is 6.** Cut to 6, and every dropped term was verified to still appear in
the manuscript text before it was dropped, with where it survives recorded in the note. Highlights
were checked at the same time against the 85-character cap: 5 bullets, longest 80. Compliant already.

### Refused, and why

- **The CRKN 100 percent APC waiver is NOT acted on.** `RV10` says B&E is covered and Section D says
  to select Gold at $0. That is the same shape of claim that was wrong for 2J and Springer. It blocks
  nothing, because the subscription route is free, but ticking Gold is an irreversible commitment
  against a **$3,690** list APC. Confirm on Concordia Library's own page first.
- **Item 29 is incomplete, not clear.** The prompt asked for the subject editors and a Concordia
  conflict flag. `RV10` named two Editors-in-Chief and stopped. An unlisted board is not an empty
  board, and this author line already found one such conflict at another venue.
- **`RV09` reference 5 fails its own check**: it states one Yamaguchi title and reports a different
  one as the Crossref return. That is the closest competitor row in the matrix. Not relied on.

### Verification

`f3` **4 PASS / 1 FAIL** (unchanged, correct) · `f4` **7 PASS / 0 FAIL** · `f5` **7 PASS / 0 FAIL** ·
`f6` **5 PASS / 0 FAIL** and C1 still fails under `--falsify`. Build clean, both md5s OK.
`readySubmission.md` **1,426 lines**. Every shipped figure is now **300 dpi with a vector PDF** or
**600 dpi with a vector PDF**; nothing is below 300. **No band moved, no gate verdict changed, and no
measured number in the paper changed.**

---

## Progress Log - 2026-08-09 #1: the three authorial decisions taken, the last RV09/RV10 note closed, and the submission .docx built

The three items the previous handoff parked as "the authors' call" were put to the authors and answered
in one pass. All three were executed the same session. The build went to **zero open BUILD NOTES for
the first time**, and then a new defect was found in the package and it is back to one. That sequence
is the entry, not an embarrassment in it.

### The three decisions, as answered

1. **Venue: Building and Environment RECONFIRMED.** Reopen trigger (b) had fired on 2026-08-08 (0J was
   rejected there for insufficient quality, not scope). The trigger was put back in front of the
   authors with the bar restated, and the venue was chosen again. `02_journal_options.md` returns to
   green with a `RECONFIRMED BY THE AUTHORS - 2026-08-09` block, and the three commitments under "My
   recommendation" are now recorded as **binding** rather than advisory, which is what the amber block
   said reconfirmation would cost.
2. **The calibrated-behavioural-model axis: keep the tick, define the axis.**
3. **Table A1's `Confirmed against` column: option (c)** - keep it, retitle it, declare the convention.

### The fact that actually settled the calibration dispute, and it was in RV09 all along

`RV09` marks THIS STUDY **No** on *calibrated behavioural model* while `Table_01_gap_matrix.md` marks
it with a tick, and the report never flagged the disagreement. Reading the column instead of the cell
settles it: **RV09 marks all TEN rows of its own matrix "No" on that axis**, including Widen and
Wackelgard and Yamaguchi, which it separately certifies as time-use-survey-driven, and its own
parenthetical for this study is "gate-tested control" - a statement about validation, not a denial
that the model is fit to microdata.

**A column with zero variance across ten studies cannot un-tick this study specifically.** It is a
different axis under the same name. It was recorded and not adopted.

Two further things fell out of looking at the column rather than the cell:

- **The novelty claim never rested on that axis at all.** It rests on four - time-use-survey-driven,
  multi-channel, forecast to a future year, mixed-use single building - and the BUILD NOTE's premise
  ("the unoccupied cell is defined partly by that axis") was simply wrong.
- 🔴 **One of those four load-bearing axes was not a column in Table 1.** The matrix scored seven axes
  and *time-use-survey-driven* was not among them, so the table did not show the axis the claim most
  depends on. It has been added. The matrix is now eight axes, and §1.2's "six positioning axes" (which
  was already wrong against a seven-axis table) and the caption's "Seven-column" are corrected to
  eight.

### What was done

- **`Table_01_gap_matrix.md`**: new `Time-use-survey-driven` column, scored for all five rows; a
  **`What the axes mean`** block defining *calibrated behavioural model* (parameters estimated from
  observed microdata on the modelled population, NOT agreement with a measured energy series) and
  *stock-scale*; the five previously `check source` cells settled from RV09 full-text readings with the
  fact each rests on; and three disagreements recorded rather than resolved.
- **The five `check source` cells**, settled: Doma time-series ✓ (1 h), calibrated ✗ (positioning trace,
  no behavioural model estimated from it), stock-scale ✗ (district of 221 individually modelled
  buildings); Buttitta calibrated ✓ (national TUS), activity/end-use ✗ (presence-state counts),
  stock-scale ✓ (four archetypes standing for a stock).
- **NOT adopted from RV09**, and named in Table 1's Sources so nobody re-imports them: its calibration
  column (10/10 No, cannot discriminate) and its *activity/end-use* verdict for Doma, which contradicts
  `dr_L3-10` on a cell `dr_L3-10` does state. The `dr_L3-10` verdict is kept.
- **§1.2**: the vendor name dropped from "mobile-positioning (SafeGraph) snapshots" rather than asserted
  unverified, since RV09 says Telus and `dr_L3-10` says SafeGraph and the axis verdict is identical
  either way; the four load-bearing axes named as such; "calibrated behavioural time-series" rewritten
  as "behavioural time-series whose parameters are estimated from national time-use microdata", so the
  claim states itself instead of leaning on a contested word.
- **`Table_A1_A2.md`**: `Confirmed against` retitled to **`Source in the project repository`** in all
  three sub-tables, with a paragraph above the tables declaring what the column is - internal paths,
  not expected to resolve, printed so every number is attributable to a place in the build rather than
  restated from a summary. 19 stray identifiers become a declared appendix convention.
- Four predecessors archived before editing.

### 🔴 The defect found while verifying the .docx, which is why the build is back to 1 open

`Table_A1_A2.md` carries **two** tables under two `# ` headings. `Chapter_08_Conclusion.md:13` has
**one** placeholder for the file, and `assemble_3J.py`'s `inline_table()` strips every `^# ` line. A1's
label comes from the placeholder; **A2's is deleted.** The AT_RETAIL codebook therefore ships as an
unlabelled continuation of the model card, under no number, and **no chapter cites "Table A2"
anywhere.** Verified in the built docx: "Table A1" 3 times, "Table A2" and "AT_RETAIL codebook" zero,
while A2's body ships in full (codebook rows, granularity note, excluded-channel note, episode-time
share).

**f4's C7 is structurally blind to this.** It checks that every caption it FINDS is cited in prose, so
it reports 22/22 while a 23rd exhibit rides along unnumbered - the caption was destroyed before C7 ever
saw the document. Same shape as the 2026-08-08 leak, inverted: there a heading was dropped and the body
survived as content; here a heading is dropped and the body survives as an orphan.

Recorded as a BUILD NOTE with two options (split A2 into its own SI table and cite it from §2 or §3;
or fold it in as `### A1.6`), because which one is right is an editorial judgment about whether the
codebook is data or model. **Not patched.**

### Verification

- Build: **8 BUILD NOTEs RESOLVED, 1 open.** Between the three decisions and the A2 discovery it read
  `none. Nothing in the manuscript is waiting on an external answer.` for the first time.
- `f4` **7 PASS / 0 FAIL** · `f5` **7 PASS / 0 FAIL** · `f3` **4 PASS / 1 FAIL, unchanged and correct.**
- `check source` markers 22 to 14; readySubmission.md 1,427 to 1,467 lines; 22 captions both sides.
- **Submission .docx built and verified against the INSTALLED file, not the build output** (the 2J
  lesson, where a table column had silently vanished from the shipped docx): 22 captions, 15 images,
  15 media parts, 14 tables, zero BUILD NOTE residue, zero warning glyphs, zero `check source`, no
  campaign stamp, no `Confirmed against` column title. The single `Confirmed against` hit is Table 5's
  own prose about `_PROVENANCE.md` and is paper content.
- Package at `writing/submission/`: `3J_manuscript_submission.{md,docx}`, `figures/` (12 PNG + 11
  vector PDF, `SI/` alongside), `tables/`, and the 2J toolchain copied into `extra/build_scripts/`
  (`ref_submit.docx`, `post.py`, `submit_check.py`) so the render is reproducible here. Zero broken
  image links. **No blinded build**: review is single-anonymized (RV10 item 14).

### Left open

1. **The Table A2 label** (the one BUILD NOTE, above).
2. **Do NOT tick Gold open access** on RV10's CRKN 100 percent waiver claim. $3,690 USD, irreversible,
   same shape as the 2J/Springer claim that was wrong.
3. **The subject editors are still unlisted**, so the Concordia conflict is unanswered, not cleared.
4. **RV09 reference 5 (Yamaguchi 2017)** states one title and reports another as its Crossref return.
   It does not enter Table 1 and fails the cell on two axes under either title, so it blocks nothing
   here, but the row is unverified.
5. **The generative-AI declaration** - the authors' statement to make.
6. **Cover letter placeholders**: handling editor's name and submission date.
7. Deferred, unchanged: N7 (`f3` C2, do not relax) and N8 (`f5` C4 converse gap).

---

## Progress Log - 2026-08-09 #2: the submission .docx made to read like a paper, references consolidated, 2J cross-cited, image prompts collected

Seven changes asked for in one message, all executed against the sources and the build, none by hand
editing the built artefacts. Every one is verified against the **installed** `.docx`, not the pandoc
output.

### 1. The "Horizontal Line" shapes are gone, and they were never a style setting

Word was showing sixty objects named "Horizontal Line". They are markdown thematic breaks: pandoc
renders each `---` as a **VML rectangle** (`<v:rect>`), and Word names that shape. No style change
could have removed them, because they are not styled text - they are drawings. `strip_for_submission()`
now drops every thematic break, and the built file carries **0 `<v:rect>`** against 60 before.

The drop runs **last**, after the residue and loss checks, on purpose: the strip's own section-drop
loop uses `---` as a terminator, and the residue check tests for two rules in a row. Removing the rules
earlier would have quietly disarmed both.

Note. A second defect was written into that code comment and then **falsified by testing it**: a rule
at line 1420 sits directly under a paragraph with no blank line, which is the shape that makes a setext
heading, and the comment claimed the whole paragraph was rendering as an H2. Running that fragment
through pandoc shows a `<p>`: pandoc reads setext only from a *single-line* header, and this is a
six-line paragraph. The comment now records the wrong claim and how it was killed.

### 2. Four report-style notes removed from the paper, and none of them deleted

The four the authors quoted, plus one more found alongside them:

| Removed from the paper | Where it came from | Where it went |
|---|---|---|
| the `n/r` legend blockquote after the abstract | inserted by the assembler | no longer inserted; see below |
| `(5 bullets, each <=85 characters.)` | drafting instruction in Chapter 00 | `<!-- APPARATUS NOTE -->` |
| `Front-matter note: no result or magnitude...` | Chapter 00 | `<!-- APPARATUS NOTE -->` |
| `Differentiation targets named in this project's own positioning review...` | Table 1 | `<!-- APPARATUS NOTE -->` |
| `Carried from the two-channel construction stage; to be merged into the master bibliography` | Chapter 02 | obsolete - the merge is what this round did |
| `- (verify final citation form / status against master bibliography)` x2 | Chapter 01 references | obsolete, same reason |

The mechanism matters more than the list. Three of them became `<!-- APPARATUS NOTE ... -->` comments
rather than deletions, and `strip_for_submission()` grew **one new named rule** that removes every HTML
comment that is not already a BUILD NOTE. The working draft keeps the note in its source; the submitted
paper never sees it. **Deleting the note would have deleted the reason**, which is the same argument
that put BUILD NOTES in HTML comments in the first place.

**The `n/r` legend was solved by making the legend unnecessary**, not by deleting it. `MARK_SUB` is now
`not reported` instead of `n/r`, so the 17 substituted cells read as English and the blockquote that
declared the symbol is gone. The marker is still fully **visible**, which is the entire point of the
convention: an unfilled cell that looks filled is worse than an ugly one. Two cells in Table 5 that read
`check source (central not reported)` lost the now-redundant parenthetical.

### 3. Line spacing, double to single

`ref_submit.docx` carries `w:line="480"` in `docDefaults` - double. The authors asked for single. A
derived reference document `ref_submit_single.docx` sets `240` and is now what the build uses;
`ref_submit.docx` is left untouched so the 2J toolchain stays byte-identical to 2J's.

Note. Elsevier's own guidance for Building and Environment asks for double-spaced manuscripts at
submission. The authors asked for single and that is what is built; if the desk check bounces it, the
fix is one flag on the build line, not a rebuild.

### 4. All references collected at the end, as bullets - and the list grew by nine entries

The paper had **two** per-chapter reference blocks (Chapter 1 and Chapter 2) and nothing at the end.
They are now one `# References` chapter after the Conclusion and before the Supplementary material,
alphabetised, rendered as a real bulleted list in Word (`numPr`, verified in the built XML).

Chapter 08 was split into three files so the order comes out right and no file does two jobs:
`Chapter_08_Conclusion.md` (prose only), `Chapter_09_References.md` (new), `Chapter_10_Supplementary.md`
(the Table A1 and Figure S3 placeholders, moved out of Chapter 08).

**Nine sources were cited in the text with no reference entry anywhere in the paper.** They are now
entered: ASHRAE 90.1-2019, ASHRAE Guideline 14, NRCan SHEU 2019, NRCan SCIEU, and - the two that matter
- **Kurin et al. 2022 and Menon et al. 2020**, cited by name in the SI architecture table since it was
written. Statistics Canada, NECB and EnergyPlus entries were replaced with the fuller, already-vetted
forms used in the 2J submission, so the two papers now agree on their shared sources.

🔴 **Kurin and Menon are the only two references in the paper whose details have never been opened.**
Both come from the deep-research report family in which roughly half of all citations have been found
fabricated. The Kurin entry is `dr_L3-13` reference 5 minus two fields that were self-evidently
placeholders in that report and were deliberately not carried (a page range `35, 1234-1246` and an
OpenReview URL `id=e-58pB58p`). This session does not run literature searches and did not run one here.
It is an **open BUILD NOTE**, so the build reports it every time until someone opens both.

### 5. The 2J paper is now cross-cited, and it was missing from its own successor

`§1.4` describes, in detail, a single-channel residential pipeline "linked to the Census dwelling stock,
and forecast to 2030 through the COVID/work-from-home break, together with the paired stock-scale
simulation design used to isolate the behavioural signal". That is 2J's abstract almost word for word.
**2J was not in the reference list at all**, and the sentence cited the JBPS *Longitudinal Analysis*
paper and the eSim companion instead.

2J is entered as `Iseri and Hachem-Vermette (under review b)`, *From "How Much" to "When": Forecasting
the Residential Energy Load Shape from a Calibrated Behavioural Occupancy Time-Series (Canada,
2005-2030)*, Building Simulation, and cited at five sites: §1.4 (the departure point), §2.1 (the GSS
cycles), §3.6 (the SHEU anchoring), §7.F (the shared extraction defect, which is *about* 2J), and the
reference list. The JBPS entry became `under review a` so the two are distinguishable in text.

⚠ **Left for the authors, because it is a naming question and not a citation question:** §1.4 opens
"Leg-1, published as the second journal in this line (2J)", which reads as though Leg-1 and 2J are the
same paper. The citation is now correct either way; the sentence is not this session's to rewrite.

### 6. Image prompts collected at `submission/figures/Prompts_Images/`

The eight schematic prompt files are copied there, plus a **new prompt for the graphical abstract**,
which never had one, plus a `README.md` that does the part the authors will actually need: it separates
the **nine figures that can be prompted** from the **six that carry measured numbers and must not be**
(Figures 7-11 and S1 - a drawn approximation of a measured result is a fabricated figure), and it lists
the three rules any generated image has to satisfy before it can replace a figure, each of which is an
`f5` arm and each of which exists because it was wrong once.

Note. This partly reverses the 2026-08-06 decision to build the schematics as matplotlib. The README
names what that costs rather than arguing about it: `f5` arm C2 re-runs each script and compares md5, so
an image-model output makes that arm unable to fail; the vector PDF goes away; and `f3` needs its
registered md5 updated or it fails on a hash mismatch.

### Verification

- Build: **1979 to 1326 lines**, 566 apparatus lines removed, every removal named in the manifest.
  New manifest entries: `other HTML comments` **3**, `horizontal rules` **59**, `check source rewritten
  as not reported` **17**.
- **22 captions on both sides of the strip**, unchanged. The loss check is what proves the reference
  restructuring did not eat one.
- `f3` **4 PASS / 1 FAIL** (correct, unchanged, not modified) · `f4` **7 PASS / 0 FAIL**, 31 files
  scanned, 22 exhibits · `f5` **7 PASS / 0 FAIL**.
- **Installed .docx**: 22 captions, 15 images, 15 media parts, 14 tables, **0 `<v:rect>`**, 0 HTML
  comments, 0 `BUILD NOTE`, 0 `check source`, 0 warning glyphs, `docDefaults` line spacing **240**, and
  the References heading renders as `Heading1` with its entries as a numbered-bullet list.
- The paragraph at old line 1420 renders as `BodyText`, not a heading - checked in the built XML, after
  the setext claim about it was falsified.

### Left open

1. **The Table A2 label** - unchanged from entry #1, still the authors' editorial call.
2. **Kurin and Menon** - open BUILD NOTE, above.
3. **§1.4's "Leg-1 ... (2J)" wording** - above.
4. The one remaining report-like element in the paper is Table A1's `Source in the project repository`
   column, kept because the authors chose it on 2026-08-09 in entry #1. It goes on one word.
5. Unchanged: do NOT tick Gold OA on the CRKN claim · subject editors unlisted · cover-letter
   placeholders · the generative-AI declaration · N7 / N8 deferred.
