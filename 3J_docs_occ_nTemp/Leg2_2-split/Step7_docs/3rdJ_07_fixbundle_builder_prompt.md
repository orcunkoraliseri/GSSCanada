# Builder prompt — Step-7 fix bundle (A: province labels · B: donor-draw attrs · C: weekend work)

> Paste into a fresh Sonnet session. Manager-authored 2026-06-26. One coherent bundle, three fixes,
> sequential. Surfaced by the Step-7 validator (`step7_validation_report_2030.html`).

---

You are the **employee**. Execute the three fixes below as ONE bundle, in order, re-run the
affected stages, re-run the validator to confirm the FAILs clear, then append Progress Log entries.
Work **locally** only (no cluster). `pandas` + `numpy` (+ `matplotlib` for the validator) only — no
new packages. `seed=42`, reproducible, atomic writes. Read relevant files before editing. Make the
smallest correct change. Do NOT modify any locked Step-4 *model* file. You MAY edit our Step-7
producer and the calibration-C script (both ours).

**Path shorthand:** `ROOT` = `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split`

## Archive first (HARD rule — before any edit)
- `cp ROOT\Step7_docs\3rdJ_07_aug_to_bem_2split.py` → `ROOT\Step7_docs\archive\3rdJ_07_aug_to_bem_2split.preFixBundle_2026-06-26.py`
- `cp ROOT\Step6_docs\3rdJ_06_calibrate_C_activity_weekend_2split.py` → `ROOT\Step6_docs\archive\3rdJ_06_calibrate_C_activity_weekend_2split.preWeekendWork_2026-06-26.py`
- Back up the current Step-7 outputs (the 4+ CSVs in `ROOT\Step7_docs\outputs_step7\`) and the current `_C` deliverable to a dated `.preFixBundle` copy each, before regenerating.

---

## Fix A — Province labels (producer `3rdJ_07_aug_to_bem_2split.py`) — FAIL G (both years)
**Symptom:** `PR` column ships raw numeric GSS codes (1–6) because the ported `PR_LBL` map covers
census codes (10–70) only, so nothing matched and the relabel was a no-op.

**Do:**
1. Inspect the distinct `PR` values in `ROOT\Step5_docs\outputs_step5\3rdJ_25CEN_aug_Full_Aggregated_excl.csv`.
2. **Find the AUTHORITATIVE PR code→label map already used upstream in the 2-split pipeline** — grep
   the Step-1/Step-2/Step-5 scripts (`3rdJ_01_*`, `3rdJ_02_harmonize*`, `3rdJ_05_censusLinkage*`)
   for the PR/province mapping. **Reuse that exact map. Do NOT invent province assignments** (this
   is publishable geography — a wrong code→province mapping corrupts results). If you truly cannot
   find an upstream map, STOP and report rather than guess.
3. Apply it in the producer so `PR` exits as province/region names consistently for BOTH years.
4. Update `PR_VALID` (and any province set) in the validator `3rdJ_07_bemIntegration_2split_val.py`
   to the resulting label set so gate G passes legitimately.
5. Document the mapping you used (and its source file) in the Progress Log.

## Fix B — Donor-draw dwelling attributes (producer `complete_day_types()`) — FAIL G (both years)
**Symptom:** 2,086 HH show DTYPE/PR drift across their two day-type blocks — the day-completion
donor-draw is carrying the DONOR's dwelling/geo metadata into the recipient HH's filled block.

**Do:**
1. Read how 2J's `2J_docs_occ_nTemp\07_aug_to_bem.py` `complete_day_types()` handles this — 2J's
   validator reports **0 drift**, so 2J does it correctly. Port that behavior.
2. In our `complete_day_types()`: after drawing a donor block to fill recipient HH X's missing
   day-type, **overwrite ALL household-level attribute columns** (`SIM_HH_ID, HHSIZE, DTYPE, BEDRM,
   CONDO, ROOM, REPAIR, PR, MATCH_TIER`) on the donor block with **X's own values** (read from X's
   existing present block). Only the diary-derived schedule columns (`Occupancy_Schedule,
   Metabolic_Rate`) come from the donor. Result: 0 within-HH DTYPE/PR drift.

## Fix C — Weekend work cap (complete calibration-C) — FAIL E.4 (2030 only)
**Symptom:** for all 9 archetype×band combos the office 24h WD mean < WE mean — i.e. offices look
busier on weekends than weekdays. Root cause: calibration-B capped weekday work only; **weekend
`wrk30` was never capped**, leaving weekend NIGHT work ~22% (observed ~2–3%). Biz-hours band
monotonicity is unaffected (still PASS) — this is purely a weekend (mostly night) `wrk30` leftover.
2022 is real data and is fine; only the 2030 forecast needs this.

**Design decision (manager):** do NOT stack a separate calibration-D. **Complete calibration-C** —
it simply omitted the weekend work channel. Add a weekend work-cap stage that runs BEFORE C's
existing weekend-home rake, and **regenerate the `_C` deliverable from the pre-C input** so there is
one coherent calibration pass and one deliverable name (`…_C.csv`).

**Edit `ROOT\Step6_docs\3rdJ_06_calibrate_C_activity_weekend_2split.py`:**
- Input stays the pre-C file `ROOT\Step6_docs\outputs_step6\2030_synthetic_diaries_2split_calibrated_mindwell.csv`.
- **NEW Stage 0 — weekend work cap** (runs first, strata 2 & 3 only):
  - Target = observed-2022 weekend per-slot `wrk30` mean from the Step-5 stock (weekend strata),
    per slot (48 slots). (Compute over all stock weekend persons; non-employed contribute 0 — same
    population basis as the deliverable.)
  - For each weekend slot where the 2030 `wrk30` rate > observed target: **trim only** — flip
    `round((p30−p_obs)*n)` person-slots from `wrk30` 1→0, chosen `seed=42` among currently-working
    rows. Do NOT fabricate weekend work (no 0→1 flips). Mirror calibration-B's style.
  - Flipped slots become not-working; their `hom30`/`act30` are settled by the EXISTING Stage 1
    (weekend home rake) + Stage 2 (activity restore conditional on final state), which now see the
    freed rows and land them on the observed weekend home marginal + home activities. (This also
    completes the weekend HOME restoration that C's "only flip OUT rows" left unfinished where
    rows were locked at work.)
- Stages 1 & 2 and the 04M min-dwell step: keep as-is (they run after Stage 0).
- `wrk30` for **weekday (stratum 1) stays untouched**; only weekend `wrk30` changes. Update the
  in-script comment / the doc's calibration-C section to record that C now also caps weekend work
  (the earlier "wrk30 never modified" note applied to weekday; weekend is now consciously capped).
- Regenerate `ROOT\Step6_docs\outputs_step6\2030_synthetic_diaries_2split_calibrated_mindwell_C.csv`
  (atomic; same schema, 111,024 rows).

---

## Re-run (in order)
1. Producer 2022 (gets A+B): `py 3rdJ_07_aug_to_bem_2split.py --year 2022`
2. Calibration-C (regenerate `_C` with Stage 0): run the edited script.
3. Producer 2030 (gets A+B + the new weekend-capped `_C`):
   `py 3rdJ_07_aug_to_bem_2split.py --year 2030 --deliverable <the _C file>`
4. Validator both years: `py 3rdJ_07_bemIntegration_2split_val.py --year both`

## Verify (report all; be honest about any residual)
- **Fix A:** validator gate G PR-label check PASS both years; `PR` shows province names.
- **Fix B:** within-HH DTYPE/PR drift = **0** both years (was 2,086 HH).
- **Fix C:** office E.4 — weekday 24h mean office presence now > weekend for all 9 archetype×band
  combos; weekend night `wrk30` ≈ observed (~2–3%, was ~22%).
- **Regression guard (must still hold from the original calibration-C):** sleep share ~35%, WD
  metabolic ~110 W, weekend daytime home ~0.55, residential band ordering cons<hyb<fully, office
  biz-hours band monotonicity cons>hyb>fully. Report before→after for each so nothing silently
  regressed.
- Final validator scorecard per year (PASS/WARN/FAIL counts) — confirm the prior 11 (2030) / 2
  (2022) FAILs are cleared, and report any that remain with the reason.

## Docs
- Append a dated Progress Log row to `ROOT\Step7_docs\3rdJ_07_bemIntegration_2split.md` (the 3 fixes,
  the PR map + source, before→after FAIL counts, files touched, archives made).
- Update the gate table + append a Progress Log row in `ROOT\Step7_docs\3rdJ_07_bemIntegration_2split_val.md`.
- One-line note in `ROOT\Step6_docs\3rdJ_06_longitudinalForecasting_2split.md` Progress Log that
  calibration-C was completed with a weekend work-cap stage (triggered by the Step-7 validator E.4).

## Return
Concise report: the 3 fixes' before→after, the regression-guard before→after, final per-year
PASS/WARN/FAIL, the PR map used (+ source file), and any residual FAIL with its reason.
