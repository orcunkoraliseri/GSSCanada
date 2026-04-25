---
name: data-pipeline
description: Conventions for eSim data flow — Census + GSS → aligned profiles → BEM schedules → IDF injection.
scope: builder, reviewer
---

# Data Pipeline (eSim)

The pipeline has five canonical stages. Edits should respect stage boundaries.

## Canonical stage order

1. `*_alignment.py` — align demographic categories between Census PUMF and GSS time-use diaries.
2. `*_ProfileMatcher.py` — match each Census household to one or more GSS diary profiles.
3. `*_HH_aggregation.py` — aggregate matched profiles to household-level activity / occupancy traces.
4. `*_occToBEM.py` — convert household occupancy traces into EnergyPlus schedule arrays (5-min → 30-min or hourly).
5. `*_main.py` — orchestrate runs across neighborhoods/years.

The ML path (`eSim_occ_utils/25CEN22GSS_classification/`) replaces stages 1–2 with `run_step1.py` / `run_step2.py`, then feeds `run_step3.py` (= occToBEM).

## Invariants to enforce at every stage

- **Schema stability.** Stage N's output schema is Stage N+1's input contract. Don't change column names without updating the consumer.
- **Row counts trace cleanly.** A merge that drops or duplicates rows must be intentional. Assert counts before/after.
- **Units stay explicit.** Person-units vs. household-units must be encoded in column names (`n_persons_hh`, `act_minutes_per_person`).
- **No silent demographic remapping.** All Census/GSS code translations go through a single mapping module.
- **Data sources are read-only.** `0_Occupancy/DataSources_*` is never written to. Never print raw rows from there.

## Output conventions

- Processed intermediate data → `0_Occupancy/Outputs_<year>/...` as Parquet (or `.npy` for fixed-shape arrays).
- Filenames include the year and neighborhood/sample identifier when relevant.
- Each stage writes a small `_meta.json` next to its output: row counts, source files, run timestamp, code commit (if available).

## Schedule contract (handoff to BEM)

When `*_occToBEM.py` produces an EnergyPlus-bound array, it must satisfy:

- Length is exactly 8760 (hourly), 17520 (30-min), or 105120 (5-min).
- Dtype is `float64` or `float32`, no NaN, no Inf.
- Range is plausible for the variable: occupancy fraction ∈ [0, 1]; people count ∈ ℕ; activity multiplier ≥ 0.
- Time origin is documented: "hour 0 = Jan 1 00:00 local standard time".

## Validation

For data-changing tasks, a passing test means:
- Schema check: column names + dtypes match the expected schema.
- Row count check: within expected bounds for the input year.
- Spot check: at least one demographic stratum's distribution is reproduced from a known reference.

Document what was *not* checked. Full re-runs are expensive; partial validation is honest.
