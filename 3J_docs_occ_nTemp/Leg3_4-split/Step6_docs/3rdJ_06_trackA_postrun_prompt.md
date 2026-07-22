# Builder prompt — Step 6 Track A: post-training calibration chain + validate (4-split)

> Paste into a fresh Sonnet session. Manager-authored 2026-07-21. This is Part 2 of 2 for Track A —
> **only issue this once the cluster job from `3rdJ_06_trackA_builder_prompt.md` has a `.out` file
> showing COMPLETED** (one-shot `tail`/`cat` on the login node to check, no polling loop). All work in
> this prompt is **local** (`py -3 -X utf8`, pandas/numpy only) — no cluster needed from here.

---

You are the **employee**. Execute the task below and append a Progress Log entry on completion.

## Read first

1. Runbook: `Leg3_4-split/Step6_docs/3rdJ_06_longitudinalForecasting_4split.md` (sections 6B/6G retail
   lever, 6H cleanup/mutex, 6F backcast gate)
2. Validation plan: `Leg3_4-split/Step6_docs/3rdJ_06_longitudinalForecasting_4split_val.md`
3. Fork bases (Leg-2):
   - `Leg2_2-split/Step6_docs/calibrate_weekday_work_2split.py` (Calibration B: weekday work-tail trim)
   - `Leg2_2-split/Step6_docs/3rdJ_06_calibrate_C_activity_weekend_2split.py` (Calibration C: weekend
     home restore + activity re-anchor — **the current file, mtime Jul-17, is the FIXED version; do
     NOT fork `archive/3rdJ_06_calibrate_C_activity_weekend_2split.20260717_pre_mutexfix.py`, that is
     the WRONG base**)
4. **The module list in the Leg-3 runbook names exactly one combined file,
   `3rdJ_06_calibrate_C_4split.py`, described as "calibration B/C ports + retail cap stage" — build
   ONE file that does both Calibration B and C plus the retail cap, not two separate scripts.**
5. Do **not** port `3rdJ_06_forecast_rake_2split.py` (Leg-2's later-added conditional act30 rake) —
   it is not in the Leg-3 module list. If you believe it's needed after reading the runbook yourself,
   stop and flag it rather than building it silently; this is a decision-level question, not yours to
   resolve.

## Files to create (all under `Leg3_4-split/Step6_docs/`)

- `3rdJ_06_retail_lever_4split.py` — post-hoc amplitude lever + QC-Sunday sub-axis
- `3rdJ_06_calibrate_C_4split.py` — calibration B/C port + retail cap stage + **3-way mutex guard**
- `3rdJ_06_longitudinalForecasting_4split_val.py` — validator, Sections 1–8 per the val doc

## 1. Retail lever (`3rdJ_06_retail_lever_4split.py`)

Reads the raw 2030 `at_retail_fraction_2030(t)` produced by Track A's `D2` stage, applies a scalar
multiplier **before** any Step-7 peak-normalization:

| Scenario | Multiplier (rel. 2022 = 1.00) |
|---|---|
| Plateau/Resilient Central (Default) | **0.97** |
| Continued-Shift (Conservative) | **0.90** |
| In-Store Renaissance (Optimistic) | **1.05** |

QC-Sunday sub-axis: default = restricted (Sunday ≈ 0.60–0.75 × Saturday peak, matches the historical
QC trading-hours pattern already present in respondent data); optimistic = deregulated (AB-like
uplift) — emit this as an **extra file**, not a 4th band:
`at_retail_fraction_2030_{plateau,shift,renaissance}[_qcSundayDereg].csv` per day-type.

## 2. Calibration B/C + retail cap (`3rdJ_06_calibrate_C_4split.py`)

Port the Leg-2 Calibration-B (weekday work-tail trim) and Calibration-C (weekend home restore +
activity re-anchor, `seed=42`, vectorized per-slot×state group draws, never loop per row) stages
verbatim in mechanics — **`wrk30` is never modified** by either stage, same as Leg-2. Extend with a
**retail cap stage**: cap 2030 per-slot retail at `observed-2022 profile × lever value`
(target-anchored — set the value directly, never delta-subtraction; delta-subtraction was the
Leg-2 over-correction lesson).

**No 04L marginal/joint rake on 2030** — this isn't a flag to set, it's simply never calling
`3rdJ_04L_joint_rake_4split.py`; there is no observed-2030 marginal to rake to (would be circular
against the model's own projection). Only run: deterministic mutual-exclusion cleanup +
`3rdJ_04M_mindwell_4split.py` min-dwell smoothing (both already 3-way ready if you built them that
way — confirm).

### 🔴 3-way mutex guard — the mandatory pattern, not optional cleanup

Leg-2's Calibration-C had a real bug here: `apply_min_dwell()` is a pure single-channel smoother with
zero visibility into the other channel(s) — it can re-raise a slot purely to satisfy a dwell-length
rule, silently re-introducing a conflict a prior stage had just resolved. The Leg-2 fix (current file
lines 416–426, `hom_we2[conflict_we] = 0` unconditional resolve — "**wrk30 wins**, hom30 loses" for
that 2-way case) is the pattern to generalize, not copy verbatim:

1. **Decide and document an explicit priority order for the 3-way case** — e.g. `work > retail > home`
   (work is the most behaviorally constrained/least-ambiguous signal; retail typically means a
   verifiable trip; home is the default/residual state) — this is a modeling judgment call. If you're
   not confident which ordering is correct, **stop and ask** rather than picking one silently; this
   affects downstream Step-7/8/9 numbers.
2. **After every single-channel smoothing/raking pass** that touches any of {home, work, retail} —
   not just at the very end — recompute all three pairwise conflict masks (`home∧work`,
   `home∧retail`, `work∧retail`) over the affected rows, resolve by the priority order, and print the
   count cleared.
3. **Hard `assert` gate immediately after each such stage** (not deferred to a single end-of-script
   check): `(hom∧wrk).sum() == (hom∧ret).sum() == (wrk∧ret).sum() == 0`, matching the Leg-2 pattern
   at lines 432–434 (`assert n_conflict_all == 0, "INTEGRITY FAIL..."`) — abort, never warn. This is
   the exact gap that let 4,280 impossible cells reach a 72-task re-simulation in Leg-2: the assert
   existed around Stage-1's own raking loop but not around the min-dwell pass that ran afterward.

### File hygiene

- Canonical deliverable: `2030_synthetic_diaries_4split_calibrated_mindwell_C.csv`
- Atomic write (temp file + `os.replace`) + one-per-day `_BAK_<date>` backup, same pattern as Leg-2's
  `atomic_write()`.
- Move any superseded variant (`_BAK_*`, `.preRake_*`, non-`_C` file) to `outputs_step6/archive_pre_*/`
  at write time — never leave beside the canonical file (glob-hazard lesson).
- **Record the `_C` file's MD5 in the Progress Log at sign-off** — this was a ledger gap in Leg-2,
  don't repeat it.

## 3. Validator (`3rdJ_06_longitudinalForecasting_4split_val.py`)

Port `LongitudinalForecastingValidator2Split` structurally; class becomes
`LongitudinalForecastingValidator4Split`. Key porting notes from reviewing the Leg-2 validator:

- **Sections 1–2 (training convergence, true-future-test) are not computable from any on-disk
  artifact in Leg-2 either** — they're INFO-only prose transcriptions there, not real PASS/FAIL. Port
  the same INFO-only structure; do not invent data to make these "real" gates unless Track A's
  training loop was changed to log real per-epoch/per-phase metrics (it wasn't, per this prompt's
  scope).
- **Section 4 (2022 backcast) — profile metric only, never raw flattened-binary JS.** Leg-2 learned
  this the hard way: raw JS saturates near ln 2 on sparse binary channels, and retail (~2% positive)
  is the worst case for Leg-3. Implement shape-JS + level-MAD < 0.10, gates: home ±2pp, work ±3pp,
  **retail ±1.5pp level / MAD<0.10** (small absolute band, channel is small), WFH_RATE ±5pp.
  **Regenerate the backcast fresh in this session** (don't trust any locally-cached
  `reconstructed_*_4split.csv` from an earlier smoke run) — Leg-2 had a documented incident where a
  stale temp=0.0 backcast artifact was scored for weeks before anyone noticed it predated the
  never-greedy fix.
- **Section 3 (DRIFT plausibility):** extend to the retail axis (3.7 NEW: retail directional decrease
  in `_1522`; 3.8 non-trivial retail activity count).
- **Section 5 (2030 plausibility):** add the retail block (5.20–5.27 in the val doc) — weekday
  midday 12-14h in 0.06-0.10×lever, Saturday peak > weekday (reverse of office!), Sunday QC
  0.04-0.07/AB 0.06-0.10, night ≈0, lever exactness (band ratios 0.90/0.97/1.05 ±0.01 — this one is
  exact by construction, a deviation means the lever leaked through normalization somewhere upstream),
  QC-Sunday sub-axis check, continuity vs 2022, no retail-WFH cross-contamination.
- **Section 6 (BEM readiness):** generalize the mutex hard gate (6.7) to 3-way, 0 violations.
- **Section 8 (hotel SARIMA)** is a separate track — only wire this section in if
  `3rdJ_06_hotel_sarima_4split.py`'s outputs already exist when you run the validator; if Track B
  hasn't landed yet, skip Section 8 and note it as PENDING rather than failing the whole report.

## Test method

1. Run the calibration chain locally end-to-end on the cluster job's raw 2030 output.
2. `py -3 -X utf8 3rdJ_06_longitudinalForecasting_4split_val.py` → target **0 FAIL**. Inspect the
   DRIFT triple-signal chart, backcast profile overlays, band-monotonicity charts (office WFH
   monotone, retail lever exact 0.90/0.97/1.05).

## Progress Log

Append to `3rdJ_06_longitudinalForecasting_4split.md`: mutex priority-order decision (§2.3) and
rationale, `_C` file MD5, gate-by-gate scorecard, any FAIL/WARN with disposition (never silently
relax a threshold — document with evidence per the Step-5 3-FAIL closeout template if something
doesn't clear). Keep non-closure discipline: "Step 6 NOT declared done" until 0 FAIL.

## Return

Concise report: scorecard (P/W/F/I counts), the mutex priority order you chose and why, `_C` MD5,
and — **critically** — flag that the manager must now stop and get the user's confirmation on the
2030 scenario matrix (3 aligned bundles + baseline vs. the full 27-cross) before Step 7 starts. Do
not proceed to Step 7 yourself.
