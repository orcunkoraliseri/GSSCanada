# Task 13 — residential occupant-count NaN: short status report

## The issue

`step9_scenario_response.csv` (§R3 of the Step-9 report) has NaN `occ_mean` /
`occ_pct_vs_2022` for every residential row. Root cause: the residential EnergyPlus runs
never requested a "Zone People Occupant Count" output variable, so there's no occupant-count
in the raw simulation output (only the office channel has it).

Chosen fix (over re-simulating): derive occupant-count after the fact from the *input*
occupancy schedule that actually drove each simulation — `Occupancy_Schedule × HHSIZE`,
joined by household ID (`SIM_HH_ID`) — no EnergyPlus re-run needed, in principle.

## What's confirmed working

- The derivation logic itself is implemented and physically correct (occupancy dips at
  midday, rises with WFH share in 2030 scenarios, as expected).
- Checked it against the households actually used by the real residential campaign
  (1,163 distinct households, re-pulled fresh from the cluster to correct an earlier
  measurement error). For **2022 and all three 2030 scenarios, coverage is 100%** — every
  simulated household's occupant-count is recoverable this way. This covers 5 of the 7
  simulated years — the majority of residential rows.

## What's still broken

For the **historical years (2005, 2010, 2015)**, only **11.7%** of the real campaign's
households show up in the historical occupancy-schedule data. Investigated as far as
possible locally:

- The historical-schedule generator is deterministic and reproducible (re-ran it, got a
  byte-identical result) — so re-running it again won't change anything.
- It only ever produces occupancy data for ~2,883 of the ~23,211 total households, by
  design (only households with a valid demographic match to a historical survey cycle get
  one) — that part is expected, not a bug.
- But the code that actually built the real campaign guarantees, by construction, that
  every household it simulated must have existed in the historical data *at the time it
  ran*. Project records confirm the historical files did exist on the cluster when the
  campaign completed (2026-06-30). They don't exist anywhere now (checked both locally and
  on the cluster) and can't be regenerated to match what the campaign actually used — the
  best explanation is the original files were deleted from cluster scratch sometime after
  the campaign ran, and are gone for good.

**Net effect:** the fix can populate `occ_mean` for 2022 + 2030 (conservative/hybrid/fully
hybrid) but not for 2005/2010/2015 — those would stay NaN.

## Three options going forward

1. **Ship 2022/2030 now.** Submit the fix as-is. Populates the majority of rows correctly;
   historical rows stay NaN with a documented caveat in the report. Fastest, no further
   digging or cluster cost.
2. **Keep digging for the lost historical population.** Chase cluster job logs from the
   2026-06-30 run window to see if the exact historical data (or a record of it) is
   recoverable anywhere. Uncertain payoff — it may genuinely be unrecoverable.
3. **Re-simulate historical years only (the original "option 3" fallback).** Add the real
   EnergyPlus occupant-count output variable and re-run just the 2005/2010/2015 residential
   simulations (~3,600 runs), leaving 2022/2030 on the already-working derivation.

No cluster job has been submitted yet — nothing above required cluster compute, only local
checks and a read-only pull of small manifest files.

---

## Manager review & recommendation (2026-07-06)

**Recommendation: Option 1 — and it's a stronger choice than "fastest, just caveat it."**
Inspecting the actual outputs (`step9_scenario_response.csv`, `step9_longitudinal.csv`) and
the builder (`3rdJ_09_activityDrivenLoads_2split.py`) shows the historical gap is essentially
cosmetic, not analytically load-bearing:

- **`occ_mean` is the only NaN column, and it lives only in §R3.** §R4 (longitudinal,
  `build_longitudinal`, L229–243) has no occupancy-count column at all — it runs on
  `midday_share`, `mean_peak_hour`, `energy_kWh`. And resid `midday_share` *is* populated for
  every year including 2005/2010/2015 (0.25 / 0.253 / 0.235), because it comes from the
  electricity meter (which exists for residential), not from the occupant count (which was
  never output). So the historical occupancy/WFH *shape* story is already told without
  `occ_mean`.
- **The WFH narrative caption uses the office channel, not resid.** `build_scenario`'s
  caption path (L608) pulls **office** `occ_pct_vs_2022` for its numbers; resid `occ_mean`
  being NaN doesn't break the report's prose.
- **§R3 is inherently a "vs 2022" comparison** (`occ_pct_vs_2022`). The 2022 + 3×2030 rows —
  which derive at 100% coverage under the corrected 1,163-household basis — *are* the scenario
  response. The historical rows in §R3 are longitudinal context that §R4 already covers.

Net: resid `occ_mean` is the least load-bearing quantity in the whole report, and Option 1
populates the 5 scenario-years that actually carry §R3's purpose.

**Against the other options:**

- **Do not force the derivation onto the historical years.** Coverage there is 11.7% — forcing
  it would silently mis-join ~88% *wrong* households and emit a number derived from a different
  population than the one actually simulated. An honest "n/a" beats a fabricated value; this is
  a data-integrity argument, not just a convenience one.
- **Option 3 (re-simulate ~3,600 historical runs) is a poor trade.** It fills 3 cells per
  channel that aren't §R3's actual purpose, and the newly-simulated `occ_mean` would be based on
  today's regenerated household population — inconsistent with the *already-validated* historical
  `energy_kWh` in the same rows (which came from the lost original population). Making it
  consistent means re-simulating and re-validating the historical years wholesale, reopening a
  pipeline that is currently paper-ready. Not worth it for cosmetic cells.
- **Option 2 (keep digging) has near-zero expected payoff.** The trace already establishes a
  deterministic generator + purged original files; chasing job logs is unlikely to recover a
  byte-matching population.

**One tweak to Option 1:** render the historical resid cells as an explicit
`n/a — occupant count not recoverable for historical population` rather than a blank NaN, with
a one-line footnote in §R3. That reads as a documented limitation instead of a bug.

**Before shipping, confirm:** Option 1 rests on the corrected 100% coverage measured against
the real campaign manifests (1,163 IDs re-pulled fresh), *not* the earlier 14.9%/599 artifact
from the wrong local directory — which the 2026-07-06 Progress Log entry already establishes.
