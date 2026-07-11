# Step-7 Improvement Notes — BEM integration: stale-report refresh, validator schema un-staling, Step-9 channel validation, deviation framing

> ## 🏁 CLOSED-OUT — 2026-07-10 (Option A executed to the end: 4/4 improvements)
>
> **All four improvements DONE.** The Step-7 validator was un-staled and both reports regenerated as
> **`_v2`** files (the two Jun-11 originals are **preserved in place**, untouched, per the user's request).
> - **Imp-1 (lineage/staleness):** Option A confirmed & executed — the BEM output files were already
>   current (Jul-9, 17-col, 2030 built from `joint_raked`); the reports + validator **code** were stale and
>   are now refreshed. No BEM recompute.
> - **Imp-2 (un-stale + regenerate):** validator schema **13 → 17 cols** (check 1.1 now PASS on the live
>   file), 2030 reference switched to `2030_synthetic_diaries_joint_raked.csv` (OD-3), 72.3% anchor kept +
>   documented vs the Step-6 76.93% (OD-2). Fresh reports **`step7_validation_report_{2022,2030}_v2.html`**
>   with a provenance banner. Predecessor validator archived (`archive/07_bemIntegrationGSS_val.20260710.py`).
> - **Imp-3 (Step-9 channels):** new **Section 4b** validates the 4 Equipment/Lighting channels (ranges,
>   diurnal shape, design-W by DTYPE) — all PASS, with figures. Previously validated nowhere.
> - **Imp-4 (figures + disposition):** per-figure captions (activity axes already by name), a
>   "Documented deviations — disposition" panel (5 deviations) + a paper-ready limitations paragraph.
> - **🔎 Real finding surfaced by the refresh (not a defect in the edits):** the canonical frame **shrank
>   144,507 → 144,465 HH (−42 HH; persons 285,419 → 285,367)** in the Jul-9 Step-5 refresh (region-tier
>   relink + joint rake + 5H exclusion). The stock `..._aug_Full_Aggregated_excl.csv` now holds **144,465
>   unique HH_ID / 285,367 person-rows** (verified read). The validator's hardcoded `N_HH=144,507` was stale
>   → updated to **144,465** (documented); the 5 count-gate FAILs it caused all cleared. Both BEM files are
>   internally consistent with 144,465 (0 partial HH, exactly 48 rows/HH).
> - **Result (re-derived from the report §7 tables, not transcribed):** **2022 = 34 PASS / 0 WARN / 0 FAIL**,
>   **2030 = 33 PASS / 0 WARN / 0 FAIL**. `_v2` reports: 7 figures each, provenance banner + Section 4b +
>   deviations panel, **0 external refs** (self-contained base64), correct build-source named per year.
>
> **Follow-up round — 2026-07-10 (post-close-out, executed this session):**
> - **① Frame propagation — INVESTIGATED (read-only audit).** No live Step-8/9 code hardcodes the frame
>   (all use `nunique()`) → **no false-FAIL risk.** The real gap is data: `BEM_Schedules_{2022,2030}.csv` are on
>   144,465 (Jul-9) but `BEM_Schedules_{2005,2010,2015}.csv` are still 144,507 (Jun-8, `GSSCanada-main/BEM_Setup/`).
>   Step-8's "all 5 cycle years share one SIM_HH_ID set" invariant breaks by ~42 HH **only if Step-8 is re-frozen**
>   without regenerating the three historical files. Existing sim outputs stay self-consistent on 144,507
>   (42/144,507 = 0.029 %, negligible under N=50). **Action deferred to next-campaign prep** (see handoff prompt).
> - **② §4b lighting "00h peak" — RESOLVED (validator label bug, not a data defect).** BEM data is correct:
>   lighting peaks at real **20h**. Since the 2026-06-08 +4 h diary→clock roll the BEM `Hour` is already clock
>   time, but the validator re-applied a stale `_clock(h)=(4+h)%24` helper that shifted the reported peak 20→0
>   (and mislabelled the §3/§4/§4b chart x-axes by +4 h). Helper removed; all three x-axes + the §4b peak now read
>   true clock hours. Data/gates unchanged; both `_v2` reports **regenerated** → §4b now **"Lighting peak at 20h
>   — PASS"**, totals still **2022 34/0/0 · 2030 33/0/0**. Predecessor → `archive/07_bemIntegrationGSS_val.20260710_pre_clockfix.py`.
> - **③ Doc alignment — DONE.** `07_bemIntegrationGSS.md` input table now names `2030_synthetic_diaries_joint_raked.csv`
>   (read via `--joint`); frame corrected 144,507→144,465 / 285,419→285,367 / 6,936,336→6,934,320 (Progress Log row added).
> - **④ File restore — DONE.** The two Jun-11 originals were found only in `previous/` (not the root); restored to
>   the `outputs_step7/` root (Jun-11 mtime intact) so originals + `_v2` coexist.
> - **⑤ Handoff prompt** for the next director session → `outputs_step7/prompt/step7_handoff_prompt.md`.
>
> **Still open (NON-BLOCKING):** propagate 144,465 to Step-8/9 **data** (regen 2005/2010/2015) before the next
> EnergyPlus campaign; doc-hygiene sweep of the remaining 144,507 prose (manuscript under `writing/`, `08_simulation.md`,
> `09_activityDrivenLoads.md`, `07_bemIntegrationGSS_val.md`, the `00_*` overviews, `main.py:69`); optional metabolic
> ×1.19/×1.5 sensitivity (Methods); decide whether `_v2` → canonical (rename). Metabolic channel un-calibrated by design.

Running log of planned/ongoing improvements to the Step-7 BEM-integration deliverable.
Companion to `outputs_step7/step7_validation_report_2022.html` and `..._2030.html`
*(both currently **stale**: internally generated 2026-06-01, describing the pre-Step-9 **13-column** BEM
schema, while the files they validate were rebuilt 2026-07-09 as **17-column** files — see the Context audit)*.
Add each improvement as a new numbered section; keep an entry in the index below. Work is tackled point by point.
Mirrors the structure of `outputs_step6/improvement/step6_improvement_notes.md`,
`outputs_step5/step5_improvement_notes.md`, and `outputs_step4/improvement_planning/step4_improvement_notes.md`.

**Created 2026-07-10** as the follow-on to the Step-4 (v7 report), Step-5 (enhanced report promoted), and
Step-6 (calibrated joint-raked report promoted canonical) refreshes of 2026-07-09/10. The user's trigger:
*"we updated Steps 4, 5 and 6 — now let's focus on Step 7; the previous documents changed a lot, so the
Step-7 validation reports probably need updating too."* **Unlike Step 6, that premise holds strongly for
Step 7:** Step 7 is exactly where the Steps 4/5 calibration (via the 2022 stock) and the Step-6 2030 forecast
both land. **Read Improvement 1 first** — it pins what is already current (the BEM output files) versus what is
stale (the two reports *and* the validator code), which reframes "update Step 7" and gates Improvements 2–4.

## Index
| # | Improvement | Status |
|---|---|---|
| 1 | **Lineage / staleness check** — what feeds Step 7, which artefacts are current vs stale, and what "update Step 7" concretely means (gating decision) | **DONE 2026-07-10** — Option A confirmed & executed; BEM outputs current (2030 = `joint_raked`); reports + validator code were stale, now refreshed. OD-5 paper note recorded |
| 2 | **Un-stale the validator + regenerate both reports** — fix the 13→17-col schema check, point the 2030 reference at the canonical `joint_raked` file, reconcile the 72.3% AT_HOME anchor, re-run both years, preserve the Jun-11 reports | **DONE 2026-07-10** — schema 13→17 (1.1 PASS), 2030 ref → joint (OD-3), 72.3% kept + documented (OD-2), **frame 144,507→144,465 fixed**, fresh **`_v2`** reports **34/0/0 · 33/0/0** + provenance banner; validator predecessor archived; originals preserved in place |
| 3 | **Validate the Step-9 internal-gain channels** — the 4 live columns (`Equipment_Fraction`, `Lighting_Fraction`, `Equip_Design_W`, `Light_Design_W`) are in the file but validated **nowhere**; add a section + gates + figures | **DONE 2026-07-10** — new **Section 4b** (4b.1-4b.5) all PASS/INFO + 24-h Equip/Light overlay & design-W-by-DTYPE figure (OD-4 = added now) |
| 4 | **Figures + paper-ready deviation disposition** — caption every figure, show activity **names** not codes, and give one coherent disposition for Step-7's documented deviations (metabolic un-calibrated · Sat/Sun pooled · 70 W/MET basis · MATCH_TIER within-HH · classic-frame regression) | **DONE 2026-07-10** — 7 captioned figures (activity axes by name), "Documented deviations — disposition" panel (5 rows) + paper-ready limitations paragraph |

---

## ✅ Master checklist — all proposed steps (all four improvements)

At-a-glance tracker for every step this doc proposes. `[x]` = done · `[ ]` = pending/decision needed.
Legend: **(DECISION)** = needs the manager/user to choose · **(DEFERRED)** = intentionally postponed.

**Improvement 1 — Lineage / staleness check (gating)**
- [x] Establish what Step 7 consumes (Step-5 2022 stock + Step-6 2030 forecast) and where the 4/5/6 calibration lands
- [x] Confirm the two reports are stale (internal Gen 2026-06-01; describe 13-col schema; no joint / no Step-9 channels)
- [x] Confirm the **BEM output files are current** — rebuilt Jul 9 (2022 20:57, 2030 21:06), 17-col
- [x] Confirm **which 2030 source the shipped `BEM_Schedules_2030.csv` reflects** → **`joint_raked`** (canonical), proven via the metabolic channel
- [x] Confirm the validator **code** is itself schema-stale (13-col `OUT_COLS`, would FAIL check 1.1 on the live 17-col file)
- [x] **(DECISION)** OD-1 — **Option A confirmed** by the user ("continue to the end") and executed
- [x] **(DECISION)** OD-2 — **keep 72.3%** (Step-2 GSS dwelling-stock scope); documented as distinct from the Step-6 person-diary 76.93%. §3.5 PASS (2022 pop 71.06%, Δ1.24 pp)
- [x] **(DECISION)** OD-3 — **yes**, 2030 reference switched to `2030_synthetic_diaries_joint_raked.csv`

**Improvement 2 — Un-stale the validator + regenerate both reports** *(the core — DONE 2026-07-10)*
- [x] check 1.1 schema 13 → 17 cols (+ `OUT_COLS_BASELINE`/`STEP9_COLS` constants) → **1.1 PASS** on the live file
- [x] 2030 reference → `2030_synthetic_diaries_joint_raked.csv` — §3 occupancy unaffected (hom30 identical); §4 metabolic now referenced correctly (2030 WE 109.6 W)
- [x] 2022 AT_HOME anchor kept at 72.3% + documented vs 76.93% (OD-2)
- [x] **Frame-size fix**: `N_HH` 144,507 → **144,465** (verified stock count) — cleared the 5 count-gate FAILs (1.2/1.3/5.2/5.4/5.5)
- [x] Re-run `07_bemIntegrationGSS_val.py` both years → **2022 34/0/0 · 2030 33/0/0**
- [x] Preserve the Jun-11 reports **in place** (user request) — new reports written as **`_v2`**; a dated copy also in `previous/`
- [x] Provenance banner on each `_v2` report (built-from source diary + 17-col + timestamp)
- [x] Archive validator predecessor → `archive/07_bemIntegrationGSS_val.20260710.py`; run-from-anywhere holds; no BAK/tmp left
- [ ] **(DEFERRED)** align `07_bemIntegrationGSS.md` input table (still lists the base diary) to say the 2030 BEM used `--joint` — doc hygiene, non-blocking

**Improvement 3 — Validate the Step-9 internal-gain channels** *(DONE 2026-07-10)*
- [x] New **Section 4b** validating `Equipment_Fraction` / `Lighting_Fraction` / `Equip_Design_W` / `Light_Design_W`
- [x] Gates: 4b.1 fractions ∈ [0,1] PASS · 4b.2 design-W ≥ 0 PASS · 4b.3 lighting evening-peak · 4b.4 equipment non-flat · 4b.5 design-W varies by DTYPE (INFO)
- [x] Figure: 24-h Equipment + Lighting overlay (WD solid / WE dashed) + mean design-W by DTYPE
- [x] **(DECISION)** OD-4 — **added now** (one report per file is cleaner for the paper)

**Improvement 4 — Figures + deviation disposition** *(DONE 2026-07-10)*
- [x] Per-figure captions (`CAPTIONS` dict; 7 figures + limitations paragraph → 8 `.caption` blocks)
- [x] Metabolic activity-share chart already labelled by **activity name** (ACT_LABELS), verified
- [x] "Documented deviations — disposition" panel (5 rows: metabolic un-calibrated · Sat/Sun pooled · 70 W/MET · MATCH_TIER within-HH · classic-frame regression)
- [x] Paper-ready Step-7 limitations paragraph (in the panel)
- [ ] **(DEFERRED)** optional metabolic conversion-factor sensitivity (×1.19 / ×1.5) — Methods-stage, not a gate

**Cross-cutting — decisions**
- [x] **(DECISION)** OD-5 (paper wiring) — recorded: Step 7 **is** the confluence where the Step-4/5 calibration (2022 stock) and the Step-6 2030 forecast enter the BEM (opposite of Step 6's parallel-branch note)
- [ ] **(FOLLOW-UP, non-blocking)** propagate the **144,465** frame to any Step-8/9 artefact still expecting 144,507

---

## Context — where Step 7 stands today

**What Step 7 is.** BEM/UBEM integration. `07_aug_to_bem.py` (OP4 + Step-9) converts the calibrated occupancy
dataset into the flat hourly-per-household schedule EnergyPlus consumes:
`BEM_Setup/BEM_Schedules_{2022,2030}.csv`. Per household it emits a Weekday and a Weekend profile of 24 hourly
values across four channels — **occupancy** (fraction home), **metabolic rate** (W/person), and the additive
**Step-9 internal gains** (`Equipment_Fraction`, `Lighting_Fraction`, `Equip_Design_W`, `Light_Design_W`) —
plus dwelling/geography attributes inherited from the Step-5 linkage. The validator
`07_bemIntegrationGSS_val.py` renders a 6-section HTML report per year:
§1 Schema · §2 Day-type coverage · §3 Occupancy calibration match · §4 Metabolic plausibility ·
§5 Attribute integrity · §6 Regression vs classic · §7 Summary.

### 🔑 The load-bearing finding (verified in code + on disk — audit 2026-07-10)

**Step 7 is exactly where the Steps 4/5/6 work lands — and its output files are already current, but the two
reports and the validator code are ~5 weeks stale.** Concretely:

1. **Step 7 → Steps 4/5/6: real and direct** (the opposite of Step 6's parallel-branch isolation). Inputs:
   - **2022 stock:** `0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_excl.csv`
     (**Jul 9 20:47**, 598 MB) — the region-tier-relinked + joint-raked + excluded population = the Step-5
     calibration carrier.
   - **2030 forecast:** the Step-6 canonical `2030_synthetic_diaries_joint_raked.csv` (**Jul 9 20:44**).

2. **The BEM output files ARE current.** `BEM_Schedules_2022.csv` (**Jul 9 20:57**, 674 MB, 17-col) and
   `BEM_Schedules_2030.csv` (**Jul 9 21:06**, 674 MB, 17-col) were both rebuilt after the upstream refresh.
   `_baseline.csv` (13-col) siblings exist for both years, same timestamps.

3. **The shipped `BEM_Schedules_2030.csv` was built with `--joint`** (the canonical joint_raked 2030
   population), **verified via the metabolic channel** — its Weekend metabolic 109.59 W matches the
   joint_raked diary (109.49 W, gap 0.10 W), NOT the base diary (99.90 W, gap 9.69 W). The occupancy channel
   cannot tell the two apart because the joint rake only touches `act30_*`, leaving `hom30_*` byte-identical
   between the base and joint files (max abs diff 0.0). ⇒ the 2030 BEM output is already consistent with the
   Step-6 canonical decision.

4. **The reports and the validator code are stale.** The reports were internally generated **2026-06-01**
   (mtime Jun 11 is a later touch, not a regeneration), describe the **13-column** pre-Step-9 schema, mention
   neither `joint` nor the Step-9 channels, and use the **72.3%** 2022 AT_HOME anchor. The validator
   `07_bemIntegrationGSS_val.py` still hardcodes a **13-entry `OUT_COLS`** (L51-52) and checks it at L154
   against the **live 17-col** `BEM_Schedules_{year}.csv` (L100) — **so rerunning it unmodified today would
   hard-FAIL check 1.1** (17 cols ≠ expected 13). It also references the **base** 2030 diary (`D2030`, L37),
   not the joint_raked file the BEM was built from.

**Consequence for the user's premise.** The user's intuition — *"the Step-7 reports need updating"* — is
**correct and stronger than for Step 6.** But the concrete action is precise: **not** a BEM-data rebuild (the
`BEM_Schedules_*.csv` files are current and canonical), but **un-staling the validator (13→17-col schema, joint
reference, anchor) and regenerating the two reports** so they describe the files that will actually feed
EnergyPlus — plus closing the gap that the Step-9 internal-gain channels are validated nowhere.

### Current shipped state (verified from the artefacts, not transcribed from a log)

| Artefact | Path | Timestamp | Headline |
|---|---|---|---|
| Report 2022 | `outputs_step7/step7_validation_report_2022.html` | internal Gen **2026-06-01 16:17:45** (mtime Jun 11) | **29 PASS / 0 / 0**, 6 figs, **13-col** schema, 72.3% anchor — **stale** |
| Report 2030 | `outputs_step7/step7_validation_report_2030.html` | internal Gen **2026-06-01 16:18:03** (mtime Jun 11) | **28 PASS / 0 / 0**, 6 figs, **13-col** schema — **stale** |
| Validator | `07_bemIntegrationGSS_val.py` | Jun 11 21:29 | 13-entry `OUT_COLS` (L51-52); would **FAIL 1.1** on live 17-col; base-diary 2030 ref (L37); 72.3% anchor (L58) |
| Pipeline | `07_aug_to_bem.py` | Jul 9 17:00 | emits 17-col + 13-col `_baseline`; `--joint` flag added Jul 9 (predecessor `archive/07_aug_to_bem.20260709.py`) |
| BEM 2022 | `BEM_Setup/BEM_Schedules_2022.csv` | **Jul 9 20:57** | 674 MB, **17-col**, current — built from the Jul-9 stock |
| BEM 2030 | `BEM_Setup/BEM_Schedules_2030.csv` | **Jul 9 21:06** | 674 MB, **17-col**, current — **built from `joint_raked`** (metabolic-verified) |
| 2022 stock (input) | `aug_pipeline/21CEN22GSS_aug_Full_Aggregated_excl.csv` | Jul 9 20:47 | Step-5 relinked+raked+excluded population |
| 2030 canonical (input) | `forecast_2030/2030_synthetic_diaries_joint_raked.csv` | Jul 9 20:44 | Step-6 canonical (hom30+act30 calibrated) |
| 2030 base (input) | `forecast_2030/2030_synthetic_diaries.csv` | Jul 9 21:07 | base forecast — the validator's current (stale) 2030 reference |

### Measured marginals (audit 2026-07-10, memory-safe employee read)

| Channel | `BEM_Schedules_2030.csv` (live) | Base diary | Joint_raked diary | Verdict |
|---|---|---|---|---|
| Occupancy WD | 78.53% | 78.44% | 78.44% (identical) | matches both (Δ≈0.09 pp) — cannot discriminate |
| Occupancy WE | 80.37% | 80.32% | 80.32% (identical) | matches both (Δ≈0.05 pp) |
| Metabolic WD | 109.70 W | 107.42 W | 109.69 W | → **joint** (Δ 0.01 vs 2.28 W) |
| Metabolic WE | 109.59 W | **99.90 W** | **109.49 W** | → **joint** (Δ 0.10 vs 9.69 W) |

The Weekend metabolic row is the decisive one and the reason a fresh validator run **must** use the joint
reference: keep the base reference and §4 would spuriously show a ~9.7 W Weekend gap against a file that is in
fact faithful to its (joint) source.

### Documented deviations already carried by Step 7 (all PASS/INFO under current gates)

| Deviation | Section | Nature | Disposition target (Imp-4) |
|---|---|---|---|
| Metabolic / activity channel **un-calibrated** | §4 / Risk Register | only `hom30` was raked; `act30 → Metabolic_Rate` rides raw J3/forecast | INFO; occupancy (dominant driver) is calibrated; document as limitation |
| **Sat/Sun pooled → Weekend** | §Deviations | integration.py is 2-day-type; loses the calibrated ~2.3 pp Sat/Sun split | Accept (consumer contract); note in paper |
| Metabolic **70 W/MET (~60 kg)** basis | §4 / Risk Register | conservative vs ASHRAE 105/70 kg 83 W/MET; scales all internal gains | **Verified** vs 2024 Adult Compendium (`07_metabolicMap_verification.md`); document basis + optional sensitivity |
| **MATCH_TIER within-HH** drift (20,397 HH) | §5.7 | per-person Step-5 label differs across an HH's two day-type blocks (`.first()`) | INFO (BEM-harmless; DTYPE/PR drift = 0) |
| **Classic-frame regression** | §6.3 | 2022 classic backup is the older 36,909-HH census frame, not the 144,507-HH ML frame | INFO (row-count "parity" not a defect) |

---

## Improvement 1 — Lineage / staleness check: what "update Step 7" concretely means

**Status:** PLANNED (audit DONE; awaiting OD-1) · **Owner:** occupancy/BEM · **Created:** 2026-07-10
**Refs:** `07_aug_to_bem.py` (`AUG`/`D2030`/`D2030_JOINT` L19-21, `--joint` L197-204, `assemble_2030` L182-193,
17-col `OUT_COLS` L27-29, `_baseline` write L227), `07_bemIntegrationGSS_val.py` (13-col `OUT_COLS` L51-52,
check 1.1 L154, `D2030` L37, `OBSERVED_2022_ATHOME` L58), `07_bemIntegrationGSS.md` (input table L27-30,
Deviations L159-173, Risk Register L222-231), `07_metabolicMap_verification.md`,
`docs_conversations/07_Investigating_Column_Discrepancy.md`

### Context
Step 7 sits **downstream** of everything that changed on Jul 9/10: the Step-5 2022 stock and the Step-6 2030
forecast both feed it. Someone already re-ran `07_aug_to_bem.py` for both years on Jul 9 (2022 20:57, 2030
21:06 with `--joint`), so the **BEM output files are current and canonical**. What did **not** happen is a
re-validation: the two reports (and the validator code behind them) are the Jun-01/Jun-11 vintage and describe
the pre-Step-9 13-column build. So "update Step 7" is a **re-validation + validator un-staling** task, not a
BEM recompute.

### Aim
Put the Step-7 dependency and staleness on the record, and rule on the concrete update: regenerate the two
reports against the current 17-col BEM files after minimally un-staling the validator — so the paper cites a
report that matches the files EnergyPlus will actually read.

### Approach (to decide — see Open Decisions)
- **Option A (recommended): un-stale the validator + regenerate both reports.** Update check 1.1 to the live
  17-col schema, point the 2030 reference at `joint_raked`, reconcile the 72.3% anchor, re-run both years,
  archive the Jun-11 reports. No BEM recompute (outputs already current). Improvements 3/4 then extend the
  fresh reports.
- **Option B: baseline-file workaround** — point the validator at the 13-col `_baseline.csv` so check 1.1
  passes unmodified. **Rejected:** it validates a file EnergyPlus does *not* consume (the live 17-col file is
  the input) and hides the Step-9 channels entirely.
- **Option C: accept the stale reports.** **Rejected:** the paper would cite a report describing a 13-col
  build that no longer exists, with a wrong 2030 metabolic reference.

### Steps
1. (DONE) Audit: confirm inputs, BEM-file currency, the `joint` provenance of BEM 2030, and the validator's
   schema staleness. Recorded in the Context above.
2. Decide OD-1/OD-2/OD-3. If A, hand off to Improvement 2.
3. Register OD-5 (paper wiring): Step 7 is the confluence of the 4/5 (stock) and 6 (forecast) calibration.

### Expected result
A one-paragraph on-record ruling: "The BEM_Schedules_{2022,2030}.csv files are current and canonical
(2030 built from joint_raked); the Step-7 reports and validator are stale and will be un-staled and
regenerated (Improvement 2); no BEM recompute is warranted."

### Test method
- BEM file mtimes + the audit's metabolic-channel discrimination (already done) confirm currency + joint
  provenance.
- Grep confirms the validator's 13-col `OUT_COLS` and base-diary 2030 reference (already done, L51-52 / L37).
- The fresh re-run (Improvement 2) is the acceptance test: it must reproduce the calibrated marginals and
  clear check 1.1 on the 17-col file.

### Risks / Open Decisions
- **OD-1:** Option A (un-stale + regenerate) vs B (baseline workaround) vs C (accept stale). Recommend **A**.
- **OD-2:** the 2022 AT_HOME anchor — keep **72.3%** (current validator) or move to the Step-2/6 **76.93%**
  observed? These differ enough to matter for §3.5; reconcile which is the correct observed 2022 figure and
  document it. *(Cross-links Step-6's AT_HOME work.)*
- **OD-3:** switch the validator's 2030 reference to `2030_synthetic_diaries_joint_raked.csv`. Recommend
  **yes** — it is what the BEM was built from; keeping the base reference mis-scores §4 metabolic by ~9.7 W WE.
- Pure decision/analysis item — no data or model change under Option A (only validator code + report HTML).

### Progress Log
- 2026-07-10 — Doc created. Read-only audit (1 Sonnet employee, memory-safe reads of the 674 MB BEM CSVs)
  established: both reports stale (internal Gen 2026-06-01, 13-col, 72.3%, no joint/no Step-9 channels);
  validator code stale (13-entry `OUT_COLS`, would FAIL 1.1 on the live 17-col file; base-diary 2030 ref);
  **BEM output files current** (Jul 9, 17-col) and **BEM 2030 built from `joint_raked`** (metabolic-channel
  proof: WE 109.59 W ≈ joint 109.49 vs base 99.90). Recommendation logged: **Option A**. Awaiting OD-1/2/3.
- 2026-07-10 — **Option A confirmed by the user ("continue to the end") and executed.** Ruling on record:
  the `BEM_Schedules_{2022,2030}.csv` files are current & canonical (2030 built from joint_raked); the
  reports + validator were stale and are now refreshed (Improvement 2); **no BEM recompute** was warranted.
  OD-5 (paper wiring) recorded: Step 7 is the confluence of the Step-4/5 (2022 stock) and Step-6 (2030
  forecast) calibration entering the BEM — state this in Methods so a reader doesn't assume Step 6's
  parallel-branch isolation applies here. Hand-off to Improvements 2–4 complete.

---

## Improvement 2 — Un-stale the validator + regenerate both reports (the core)

**Status:** PLANNED (depends on OD-1/2/3) · **Owner:** occupancy/BEM · **Created:** 2026-07-10
**Refs:** `07_bemIntegrationGSS_val.py` (§1 schema L154-156, `D2030` L37, `OBSERVED_2022_ATHOME` L58 applied
L311, `bem_path` L100, per-year select L124), `07_aug_to_bem.py` (17-col `OUT_COLS` L27-29), the Jun-11
reports in `outputs_step7/`

### Context
The validator un-staling is a prerequisite to a clean re-run: as-is it FAILs check 1.1 on the live 17-col
file, and its 2030 metabolic reference points at the base diary the BEM was *not* built from. This is the
Step-7 analogue of Step-6 Improvement 2 (validate the calibrated population, promote it canonical, add a
provenance banner, archive the predecessor) — but here it also carries a genuine **code** fix, not just a
re-run.

### Aim
Produce two fresh reports that (a) describe the live 17-col BEM files, (b) validate 2030 against its true
(joint_raked) source, (c) use the reconciled 2022 anchor, and (d) carry a provenance banner — and archive the
Jun-11 predecessors.

### Approach
1. **Schema (check 1.1):** update the validator's expected schema from the 13-entry `OUT_COLS` to the live
   17-entry `OUT_COLS` (matching `07_aug_to_bem.py` L27-29). Add an explicit note that the 13-col
   `_baseline.csv` is the pre-Step-9 variant, and (optionally) validate it as a documented secondary artefact.
2. **2030 reference (OD-3):** add a `D2030_JOINT` constant and select it for the 2030 run so §3 occupancy and
   §4 metabolic compare against the file the BEM was built from. Occupancy is unaffected (hom30 identical);
   §4 metabolic WE should move from a spurious ~9.7 W gap to ≈0.1 W.
3. **2022 anchor (OD-2):** reconcile 72.3% vs 76.93%; set the correct observed value and cite its source in
   the report.
4. **Doc hygiene:** align `07_bemIntegrationGSS.md` (input table + prerequisites) to say the 2030 BEM was
   built with `--joint` from `joint_raked`, not the base diary.
5. **Regenerate + archive:** run `07_bemIntegrationGSS_val.py` for both years; archive the Jun-11 reports to
   `previous/step7_validation_report_{2022,2030}_20260611.html`; add a provenance banner (built-from source,
   diary, timestamp) to each fresh report.

### Expected result
Two fresh reports, dated today, describing the 17-col files, 2030 validated against joint_raked, anchor
reconciled, provenance-bannered; Jun-11 predecessors archived. Gate tallies should be ≥ the previous
29/28 PASS (schema now correctly 17-col; §4 metabolic now referenced correctly).

### Test method
- Re-run reproduces the calibrated occupancy marginals (2030 WD ~78.5 / WE ~80.4; 2022 stock marginals) —
  cross-check vs the audit numbers.
- Check 1.1 passes on the live 17-col file (no schema FAIL).
- §4 metabolic WE gap vs the (joint) reference ≤ ~1 W (was ~9.7 W against the wrong base reference).
- `previous/` holds the two archived Jun-11 reports; no BAK/tmp left; validator still run-from-anywhere.
- **Verify-claims rule:** re-derive the fresh PASS tally from the report's own section tables, do not transcribe.

### Risks / Open Decisions
- Editing `07_bemIntegrationGSS_val.py` changes a **publishable-artefact generator** — make the smallest
  change (schema list + a 2030-reference constant + the anchor), preserve every existing gate/threshold, and
  archive the predecessor script (`archive/07_bemIntegrationGSS_val.20260710.py`) before editing.
- OD-2 (anchor) and OD-3 (2030 reference) are inputs to this improvement; do not run until they're set.
- Do **not** rebuild the BEM CSVs — they are current (Improvement 1). This is validation-only.

### Progress Log
- 2026-07-10 — Planned. Blockers: OD-1 (Option A), OD-2 (anchor), OD-3 (2030 reference). No execution yet.
- 2026-07-10 — **DONE.** Validator predecessor archived → `archive/07_bemIntegrationGSS_val.20260710.py`.
  Edits (manager, py_compile-clean): (1) check 1.1 schema **13 → 17 cols** + `OUT_COLS_BASELINE`/`STEP9_COLS`;
  (2) added `D2030_JOINT`, 2030 diary reference → `2030_synthetic_diaries_joint_raked.csv` (OD-3); (3) 72.3%
  anchor kept, provenance-note added distinguishing it from the Step-6 76.93% (OD-2); (4) §6.2 re-based to
  the 13-col baseline so the 17-col live file doesn't spuriously FAIL. **First run surfaced 5 count-gate
  FAILs** (1.2/1.3/5.2/5.4/5.5) — all one root cause: live BEM = **144,465 HH / 6,934,320 rows**, not the
  hardcoded 144,507. Confirmed via a targeted stock read (Haiku employee): `..._aug_Full_Aggregated_excl.csv`
  = **144,465 unique HH_ID / 285,367 person-rows** → the Jul-9 Step-5 refresh legitimately dropped 42 HH /
  52 persons. `N_HH` updated 144,507 → **144,465** (documented) + the two hardcoded "144,507-HH" strings.
  **Re-run: 2022 = 34 PASS / 0 WARN / 0 FAIL, 2030 = 33 PASS / 0 WARN / 0 FAIL** (re-derived from the report
  §7 tables). Key measured values — 2022: 1.1 PASS, §3.3 Δ0.44 / §3.4 Δ0.144 pp, §3.5 71.06% vs 72.3
  (Δ1.24), peak 0.947; 2030: §3.3 Δ0.089 / §3.4 Δ0.049 pp (vs the **joint** reference), peak 0.958.
  **Per the user's mid-run request, outputs written as `_v2`** (`step7_validation_report_{2022,2030}_v2.html`,
  Jul 10 12:45) and the **two Jun-11 originals preserved in place** (verified still Jun 11 21:30); a dated
  copy also sits in `previous/`. Each `_v2` report verified: 7 figures, provenance banner (correct build
  source named per year), 17-column note, **0 external refs** (self-contained base64). Doc-hygiene item
  (align `07_bemIntegrationGSS.md` input table to `--joint`) DEFERRED as non-blocking.
- 2026-07-10 (follow-up round, post-close-out) — **DONE.** (a) **File restore:** the two Jun-11 originals were
  only in `previous/`, not the `outputs_step7/` root; copied back to root (Jun-11 mtime preserved) so originals +
  `_v2` coexist. (b) **§4b "00h peak" fixed** (validator label bug, not a data defect): removed the stale
  `_clock(h)=(4+h)%24` helper — since the 2026-06-08 +4 h roll the BEM `Hour` is already clock time, so the helper
  wrongly shifted the reported lighting peak 20→0 and mislabelled the §3/§4/§4b chart x-axes by +4 h. Predecessor →
  `archive/07_bemIntegrationGSS_val.20260710_pre_clockfix.py` (py_compile-clean). (c) **`07_bemIntegrationGSS.md`
  aligned** to `--joint` + frame 144,507→144,465. (d) **Reports regenerated** (run3, exit 0): §4b now reads
  **"Lighting peak at 20h — PASS"** (2022 & 2030), calibration ref = `2030_synthetic_diaries_joint_raked.csv`,
  totals **2022 34/0/0 · 2030 33/0/0** unchanged (fix was cosmetic; no gate flipped). (e) **Handoff prompt** →
  `outputs_step7/prompt/step7_handoff_prompt.md`. #1 frame-propagation to Step-8/9 **data** (regen 2005/2010/2015)
  remains deferred to next-campaign prep.

---

## Improvement 3 — Validate the Step-9 internal-gain channels (Equipment / Lighting)

**Status:** PLANNED (depends on OD-4) · **Owner:** occupancy/BEM · **Created:** 2026-07-10
**Refs:** `07_aug_to_bem.py` (`_compute_hh_activity_fracs` L43-90, `Equipment_Fraction`/`Lighting_Fraction`/
`Equip_Design_W`/`Light_Design_W` write L141-144, inline Step-9 gates L215-218), `activity_loads.py`
(`compute_48slot_loads`, `calibrate_schedules`), `09_activityDrivenLoads*.md`

### Context
The pipeline emits four Step-9 internal-gain columns that go straight into EnergyPlus as equipment and
lighting loads, and `07_aug_to_bem.py` already asserts them inline (fractions ∈ [0,1], design-W ≥ 0). But the
**validation report validates them nowhere** — §1–§6 cover only occupancy, metabolic, and attributes. So the
report under-describes the file: two of the four load channels EnergyPlus reads are unverified in the paper's
validation artefact.

### Aim
Add a validator section that gives the Step-9 channels the same treatment occupancy/metabolic get: range
gates, diurnal-shape plausibility, per-HH-dtype SHEU calibration sanity, and figures.

### Approach
- New section (proposed **§4b** or a dedicated **§8**): 
  - **Ranges:** `Equipment_Fraction`, `Lighting_Fraction` ∈ [0,1]; `Equip_Design_W`, `Light_Design_W` ≥ 0
    (mirrors the inline asserts — but reported, with distributions).
  - **Diurnal shape:** non-trivial 24-h profile (evening lighting peak; equipment following occupancy);
    WD vs WE difference explained.
  - **Calibration sanity:** the per-HH-dtype path (`calibrate_schedules(dtype=...)`) uses the right SHEU
    targets per HighRise/MidRise/SingleD — spot-check that design-W distributions differ sensibly by DTYPE.
  - **+4 h roll:** confirm the Step-9 channels carry the same diary→clock +4 h roll as occupancy/metabolic
    (`np.roll(...,4)` at L84-85) so all four channels are phase-aligned to the weather clock.
- **Figures:** 24-h Equipment + Lighting fraction overlays (WD vs WE, both years); design-W box/violin by DTYPE.

### Expected result
The report validates all four EnergyPlus-facing load channels, with figures, for both years — no silent
un-validated channel remains.

### Test method
- All four columns pass their range gates in both years (reproduces the inline asserts, now reported).
- Lighting shows an evening peak; equipment tracks occupancy; +4 h alignment matches the occupancy channel.
- Design-W distributions differ by DTYPE in the expected direction (SHEU-target-driven).

### Risks / Open Decisions
- **OD-4:** fold Step-9 validation into the Step-7 report now, or run it as a dedicated Step-9 validation
  pass? Recommend **now** (the columns live in the Step-7 file; one report per file is cleaner for the paper).
- Adds a section but no threshold change to existing gates — additive, low-risk.

### Progress Log
- 2026-07-10 — Planned. Depends on OD-4; naturally bundles with the Improvement-2 re-run (same validator edit
  session). No execution yet.
- 2026-07-10 — **DONE (OD-4 = added now).** New method `validate_step9_channels` → **Section 4b**. Measured,
  both years PASS/INFO: 4b.1 Equip [0.026, 1.0] / Light [0.0, 1.0] ∈ [0,1] **PASS**; 4b.2 design-W ≥ 0
  (Equip min 168.3 W; max E 5,597 W [2022] / 6,377 W [2030], L 24,269 W) **PASS**; 4b.3 lighting peak
  **PASS** (lands at 00h — flagged as a late-peak follow-up, see the closeout box); 4b.4 equipment amplitude
  0.341 [2022] / 0.382 [2030] **PASS**; 4b.5 design-W spans 5 DTYPE levels **INFO**. Figure = 24-h Equipment
  & Lighting overlay (WD solid / WE dashed) + mean design-W by dwelling type. The 4 EnergyPlus-facing load
  channels are no longer un-validated.

---

## Improvement 4 — Figures + paper-ready deviation disposition

**Status:** PLANNED · **Owner:** occupancy/BEM · **Created:** 2026-07-10
**Refs:** the Step-4 `ACT_LABELS` 14-category legend (`02_harmonizeGSS.py`), `07_metabolicMap_verification.md`,
the Deviations + Risk Register in `07_bemIntegrationGSS.md`, Step-6 Imp-3/4 (the template this mirrors)

### Context
Mirrors the Step-6 figures-and-disposition work. The Step-7 report's activity-share / metabolic charts should
name activities (not codes), every figure should be captioned, and the five documented deviations should be
gathered into one coherent, paper-ready disposition panel instead of scattered Risk-Register lines.

### Aim
Make the fresh Step-7 reports self-explanatory and paper-ready: named-activity figures, captions, and a single
disposition panel + limitations paragraph.

### Approach
- **Names not codes:** relabel the metabolic activity-share chart with the 14-category names (Work & Related,
  Sleep & Naps & Resting, …) via the Step-4 `ACT_LABELS` crosswalk — consistent with the Step-6 refresh.
- **Captions:** every figure gets a caption cross-checked against its section table.
- **Disposition panel:** one "Documented deviations — disposition" block covering the five items in the
  Context table (metabolic un-calibrated · Sat/Sun pooled · 70 W/MET basis · MATCH_TIER within-HH ·
  classic-frame regression), each with a one-line BEM-impact note and its gate status kept visible.
- **Limitations paragraph:** a paper-ready Step-7 limitations paragraph (draft into this Progress Log first).

### Expected result
Fresh reports with named-activity captioned figures and a coherent deviation panel + limitations paragraph —
matching the Step-4/5/6 house style.

### Test method
- Every figure has a caption; activity axes show names; the disposition panel lists all five deviations with
  correct gate status; base64-only / offline / idempotent; the Improvement-2 tally untouched.

### Risks / Open Decisions
- Reporting-side only; keep all strict gates visible (no re-thresholding to "hide" a deviation).
- **(DEFERRED)** optional metabolic conversion-factor sensitivity (×1.19 / ×1.5) — a Methods-stage sensitivity
  run, not a validation gate.

### Progress Log
- 2026-07-10 — Planned. Bundles with the Improvement-2 regeneration. No execution yet.
- 2026-07-10 — **DONE.** `CAPTIONS` dict → a caption under each of the 7 figures (§1, §2, §3, §4, §4b, §5,
  §6); the §4 metabolic activity-share chart was already labelled by activity **name** (ACT_LABELS),
  verified. Added a "Documented deviations — disposition" panel (5 rows: metabolic un-calibrated · Sat/Sun
  pooled → Weekend · 70 W/MET ~60 kg basis · MATCH_TIER within-HH · classic-frame regression) + a
  paper-ready Step-7 limitations paragraph, and a provenance banner. Verified in both `_v2` reports: 8
  `.caption` blocks, 1 deviations panel, 0 external refs. Strict gates kept visible (no re-thresholding).
  Deferred: the optional ×1.19/×1.5 metabolic sensitivity (Methods-stage).
