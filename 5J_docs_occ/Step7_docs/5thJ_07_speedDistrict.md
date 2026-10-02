# Step 7 — WP5: what the speed buys (RQ4)

### 5J occupancy-aware surrogate. Implementation specification.
#### Parent: `../5thJ_00_Occupancy_Surrogate_Pipeline.md` Step 7. Validation: `5thJ_07_speedDistrict_val.md`

Written 2026-09-28. Week 4, in parallel with Step 6 only once the Step 6 scoring job has been submitted.

---

## STATUS

🟢 CLOSED (2026-10-01 13:15 EDT): 1,000 draws, spread, writer check and manager recount all verified (`impl/2026-10-01_wp5_district.md`, last entry); outputs in `outputs_step7/`; gate 1.4 WARN on 3 of 8 series (kept as a result). Before: 🟡 IN PROGRESS (2026-10-01 04:22 EDT): design ruling `impl/2026-10-01_step7_design.md` replaces every DRAFT item (archetype twins of 100 real Madrid buildings, 560-household pool, draws sized by measured time, 20-draw EnergyPlus check with the 5J builder); part A employee launched. Before: ⬜ NOT STARTED. Needs Step 5 closed (winner pinned). Its RQ4 claim is read together with Step 6: if S
fails G5J.3, the district spread is reported as "what the surrogate says", not as a validated spread.

## AIM

Show what the speed is for: the spread of a district's demand under occupancy uncertainty, from 100,000
occupancy draws that EnergyPlus could not run in the time available, and how wrong the surrogate is on
that district when EnergyPlus is run on a random subsample.

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Where |
|---|---|
| One European district from OpenUBEM, dwelling-level, no-core rule | Parent Step 7; 4J Step 10 |
| The surrogate is checked against EnergyPlus on a random subsample of the same draws | Parent Step 7 |
| Speed is reported, not gated (G5J.7) | Overview |

## 7A. THE DISTRICT (DRAFT)

* A Spanish district from the 4J real-stock work (Madrid, `4J_docs_occ/Step10_docs/`), so every file can
  be read by the manager (UK rule). Its dwellings, their classes and floor areas come from the 4J no-core
  records; the Step 1 inventory names the exact file.
  From the inventory (2026-09-28 night, section C `step10_stock_buildings` and E): district
  `ES-MAD-BERRUGUETE` (4J fold es, Madrid), run by `4thJ_step10_nocore_campaign.py`; outputs on Speed
  under `/speed-scratch/o_iseri/4J_step10_nocore/out/ES-MAD-BERRUGUETE` (and `_v2`), local runs under
  `_local_runs/4J_ES_local/runs/ES-MAD-BERRUGUETE/`. Its EnergyPlus is 23.1.0 multi-zone OpenUBEM
  (about 79 s per cell per worker), a different builder from the 5J box: the out-of-range mapping
  below is therefore also a builder change, stated as such.
* 🔴 **Out of range.** The surrogate learned archetype boxes; real buildings are not boxes. Each real
  dwelling is mapped to the building vector of 5J (class, floor area, TABULA envelope values for its
  age band, orientation). Dwellings whose mapped values fall outside the Latin hypercube ranges are
  counted and reported, and scored separately in 7C.

## 7B. THE DRAWS

* One draw = every dwelling gets one household drawn with survey weights from the Spanish diary pool
  (all households, not only the 60 of the campaign) and one household-year of schedules built by the 4J
  path. Weather = the campaign's Madrid EPW.
* 100,000 draws (DRAFT; fewer if the GPU time does not allow, stated). District hourly demand per draw
  = sum over dwellings. Reported: median and 90 % interval of annual and peak-hour district demand per
  end use, and how many draws the interval needs to settle (the He 2015 question: about 100 profiles for
  a stable mean, their p. 2104).

## 7C. THE CHECK AGAINST ENERGYPLUS

* A random subsample of draws (DRAFT 20 draws × all dwellings, sized from the Step 2 time per run) run
  through EnergyPlus on the real geometry via OpenUBEM, `sbatch` only.
* Reported: per dwelling and per draw, surrogate error against EnergyPlus (load and district total);
  split by in-range and out-of-range dwellings.

## 7D. SPEED (G5J.7)

Time per dwelling-year on the same Speed node type: EnergyPlus (median of the 7C runs, wall seconds per
run on one CPU) against the surrogate (batched on one A100 and on one CPU core, both reported).
Measured with the job's own clock lines, not estimated.

## 7E. BEFORE THE GPU ENDS

✅ Checkpoint copy DONE 2026-10-01 04:19 (parent Progress Log; 24/24 md5 OK). 🔴 All GPU work finished and the checkpoints copied off Speed (Spain and Italy locally; UK-trained ones
kept only where the licence allows) before about 31 Oct 2026. A dated line in the parent Progress Log
confirms the copy with md5s.

## OUTPUTS

`outputs_step7/district_spread.csv`, `district_check.csv`, `speed.md`, `impl/<date>_wp5_district.md`.

## PROGRESS LOG (append-only)
- 2026-09-28 (manager): doc written as a plan. Next: Step 5.
