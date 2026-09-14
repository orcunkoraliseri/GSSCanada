# Investigation task — why does `G11.12` fail so hard at stock scale?

#### Date set: 2026-09-13 · Status: OPEN, not started · Requested by the author, on work item 11.5's closure
#### This is NOT work item 11.6 (the gate board) and NOT a reopening of 11.5 (closed, DONE). It is a
standalone, read-only diagnosis, deliberately kept in its own folder so it does not touch either
closed record.

---

## 0. What you are being asked, in one sentence

Work item 11.5 measured `G11.12` (aggregate diurnal load shape vs CREST's own published statistics,
R2 >= 0.85) at real stock scale and it FAILED for both cities that were run — London (uk)
R2=0.4347, n=7,602 flats; Bologna (it) R2=0.0781, n=29,902 flats. The closure record argued this is
consistent, not broken, because Step 9 already failed the same gate at 100 dwellings/fold. The
author then asked, twice, in plain words: **"why are they failing, can we investigate?"** This task
is that investigation. It explains the FAIL in as much mechanistic detail as the data on disk
supports — it does not try to make it pass.

**No simulation, no cluster job, no new `C2` read is needed.** Every number below is either already
written to disk or a short arithmetic pass over files already written to disk. This should take
minutes of compute, not hours.

---

## 1. Background you need before starting (read this, do not re-derive it)

* `G9.12` already failed once, at Step 9, on 100 dwellings/fold: `es` R2=0.2967, `uk` R2=0.4106,
  `it` R2=0.0346 (`Step9_docs/4thJ_09_enduseLoads.md` line 772-773). Read-only: do not touch Step 9.
* **`FINDING 142`** (same doc, line 727-730) already names one mechanism: *"the appliance peak falls
  six hours apart across the three countries... this is also why `G9.12` fails — CREST's statistics
  are UK-2000."* In plain words: our three countries' diaries put their peak activity at different
  clock hours (Spain 14:00, Italy 18:00, Britain 20:00 in the Step 9 run), but the single reference
  profile `G9.12` scores against is built from a UK survey, so only the UK fold's diary timing is
  close to what the reference expects. This is a **known, already-diagnosed** effect. Your job is to
  check how far it goes toward explaining the STOCK-SCALE numbers, and whether anything is left over.
* The gate's own scoring code, unchanged since Step 9 and imported (never re-implemented) by Step
  11's tool: `4thJ_gates_step9.py` — `crest_expected_diurnal()` (builds the reference, conditioned on
  the fold's occupancy/household-size distribution, `occ_dist`), `r_squared()` (Pearson r, squared —
  read the docstring, it is NOT the regression R2, it cannot penalise a pure scale/offset mismatch in
  the mean, only shape), `_rebin()` (144 ten-minute CREST bins -> the fold's own timestep count).
* Step 9's occupancy narrowing: only **100 distinct presence diaries exist per fold**, ever — Step 7
  shipped exactly that many and no later step widens the pool. Step 11's `reseed` mode redraws
  *ownership* of those same 100 diaries onto each flat; it never adds a new diary
  (`4thJ_11_stockEndUseLoads.md` §1.1, the 2026-09-08 last+46 entry). Whatever differs between Step
  9's fold-level result and Step 11's stock-level result for the SAME country is NOT differently
  diverse occupants — it is a different mix of buildings/household-sizes drawing on the same 100.
* Step 11's population is spatially narrower than Step 9's: one neighbourhood, one weather file, a
  correlated construction-epoch mix, never pooled across cities (§1.2). Step 9 drew its 100 across a
  whole fold. That is a second, independent reason the two numbers need not match even if the
  country-timing mechanism were the whole story.

## 2. Files you will read (all already on disk — do not regenerate anything)

* Step 9, per fold: `Step9_docs/outputs_step9/stock_series_{es,uk,it}.csv` (per-timestep aggregate
  electricity, one row per timestep) and `Step9_docs/outputs_step9/step9_manifest_{es,uk,it}.json`
  (carries `timestep_min`, `n_dwellings`, `calibration` hazards, `household_sizes` or equivalent —
  read whichever field `_occupancy_distribution()` in `4thJ_gates_step9.py` line 954 actually reads).
* Step 11, per fold (only `uk` and `it` exist — `es`/Madrid was never run at stock scale, note this
  gap, do not fill it):
  `Step11_docs/outputs_step11/c2_uk/step11_11-5_uk_reseed.json`,
  `Step11_docs/outputs_step11/c2_it/step11_11-5_it_reseed.json`. Each already carries
  `ours_mean_diurnal_w_per_dwelling`, `crest_reference_diurnal_w_per_dwelling`,
  `occupancy_distribution`, `r_squared`, `per_day_bins`.
* The gate code itself: `tools/4thJ_gates_step9.py` (functions named in §1 above) — read it, do not
  edit it.
* The CREST source table: `Step9_docs/outputs_step9/sources/crest_activity_statistics_wd.csv`.

## 3. What to actually compute

Write one throwaway script (Python, stdlib + csv/json only — no new dependency) that, for each of
the four (fold, scale) pairs where data exists — Step9/es, Step9/uk, Step9/it, Step11/uk, Step11/it
— loads `ours` and `ref` as equal-length arrays and reports:

1. **Peak-hour offset.** The clock hour (or bin) of `ours`'s maximum and of `ref`'s maximum, and the
   difference between them. Does Step 11's peak-hour offset for `uk` and `it` match, roughly, what
   Step 9 already measured for the same country? Does the offset direction/size line up with
   `FINDING 142`'s claimed hours?
2. **Best-shift R2.** Holding `ref` fixed, circularly shift `ours` through every possible bin offset
   and recompute `r_squared()` (imported, not re-derived) at each shift. Report the shift that
   maximises R2 and that maximum value, next to the reported (zero-shift) R2. **If the best-shift R2
   is much higher than the reported R2, that is direct, quantitative support for "right shape, wrong
   clock hour" — the known mechanism. If the best-shift R2 is barely better, the FAIL is not
   (only) a timing offset, and that is a new, open finding — say so plainly, do not paper over it.**
3. **Occupancy-distribution drift.** Compare Step 9's fold-level `occ_dist` against Step 11's
   stock-level `occupancy_distribution` for the same country (both already on disk, no
   re-derivation). Report the per-household-size percentage-point differences. Because
   `crest_expected_diurnal()` is CONDITIONED on this distribution, a shifted household-size mix
   moves the reference profile itself, independent of diary timing — quantify whether this shift is
   large enough to matter (rebuild `ref` with Step 9's `occ_dist` swapped in for Step 11's population
   and see how much `r_squared` moves; imported code only, do not touch the function).
4. **Magnitude of the gap widening for `it`.** Step 9 `it` was already the worst fold (0.0346); Step
   11 `it` is 0.0781 — a small absolute move but on a very small base, and it is now the ONLY number
   that changed direction (up, not down) while `uk` moved a similar small amount. State plainly
   whether items 1-3 above account for this move, or whether it is unexplained residual.
5. **A sanity check for a scoring/alignment bug**, because this is a NEW tool
   (`tools/4thJ_step11_aggregate.py`) built for 11.5 and it has never been cross-checked against
   Step 9's own `g9_12()` on data both could read. Pick ONE Step 9 fold (suggest `uk`, the file is
   smallest) and confirm `4thJ_step11_aggregate.py`'s aggregation arithmetic — sum, divide by dwelling
   count, rebin — reproduces `4thJ_gates_step9.py`'s own `stock_series_uk.csv`-derived `ours` array to
   the same precision Step 9 already reports, when fed the same manifest. If it does not reproduce,
   that is a bug in the new tool, not a modelling result, and it changes everything above — report it
   first and loudest if you find it.

## 4. Hard rules — read before writing anything

* **Read-only.** Do not edit `4thJ_gates_step9.py`, `4thJ_step11_aggregate.py`, any manifest, any
  `.csv`, any band, any threshold. Your throwaway script lives under the scratchpad or this
  `investigate/` folder, never inside `tools/`.
* **No re-scoring.** This task does not produce a new `G11.12` verdict. The verdict already exists
  (FAIL, both cities) and work item 11.5 is closed on it. You are explaining the number, not
  re-measuring it.
* **No band moves, ever.** `G11.12` inherits `G9.12`'s 0.85 floor verbatim and that is not open for
  discussion here, same as everywhere else in Step 9/11.
* **Falsify, don't assume.** `FINDING 142`'s mechanism is the leading candidate, not a given. If your
  numbers do not support it as the (near-)whole explanation, say so — an investigation that only
  confirms the existing story when the numbers say otherwise is worthless.
* If you find something that looks like a genuine bug (item 5, or anything else) rather than a
  modelling mismatch, stop, report it clearly as a finding, and do NOT attempt a fix — that is the
  author's decision to make, not this task's.

## 5. Deliverable

One written record, same style as
`Step11_docs/docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md` (headline, what was asked vs
returned, numbered findings, an explicit "nothing moved" line): put it at
`Step11_docs/docs/2026-09-13_G11.12-stock-scale-failure-investigation.md`. Include the throwaway
script's output numbers inline (peak-hour offsets, best-shift R2 per fold/scale, occupancy-drift
percentages) so the record is self-checking. **Do not touch `4thJ_11_stockEndUseLoads.md`'s work-item
table, `RESUME.md`, or the memory files** — this investigation does not close or reopen a work item;
if it turns up something the author must rule on, name it plainly as an open question at the end of
the record and stop there.
