# Step 10 real-stock campaign, run on BOTH platforms — implementation state

Task doc:   `Step10_docs/docs/2026-08-28_Step10_closure_questions_for_the_author.md` §6 (Q1–Q4 ruled (a))
            **plus the author's same-day reversal of Q3** (see §Decisions below)
Status:     DONE

---

## Ledger

| # | what | where | state | output |
|---|------|-------|-------|--------|
| L1 | first local run, 410 cells | Windows, EnergyPlus 23.1.0-87ed9199d4 | **SUPERSEDED** — 310 of 410, 100 cells failed on the arm-routing defect below | `realstock_campaign_run.log` (overwritten by L5) |
| L2 | `--emit-only` stage, 410 IDFs + gain schedules | Windows | SUPERSEDED — absolute Windows `Schedule:File` paths, not portable | — |
| L3 | `--emit-only` stage, portable paths | Windows | DONE, 410 of 410 emitted, 0 errors, 650.3 s | `_local_runs/step10_stage`, `outputs_step10/realstock_stage/manifests/*.json` |
| L4a | Speed prep, untar the 410 cells | `sbatch` **1287966**, `ps` | DONE, exit 0, 410 cell dirs | `/speed-scratch/o_iseri/step10_realstock/prep.out` |
| L4b | Speed EnergyPlus array, 410 tasks `%64` | `sbatch` **1287967**, `ps` | DONE | `/speed-scratch/o_iseri/step10_realstock/logs_1287967_*.out` |
| L4c | Speed IDF digests | `sbatch` **1288200**, `ps` | DONE, 410 lines | `idf_sha256_speed.txt` |
| L4d | Speed harvest | `sbatch` **1288122**, `ps`, dep `afterany:1287967` | DONE, **410 of 410 completed** | `speed_metrics.jsonl` |
| L5 | local re-run, 410 cells, routing fixed | Windows, EnergyPlus 23.1.0-87ed9199d4 | DONE, **410 of 410**, 0 failed, 4163.7 s | `realstock_campaign/realstock_campaign_manifest.csv` |
| L6 | platform comparison | Windows | DONE | `realstock_platform_arm.json` |
| L7 | scoring, `H10`, mutation battery | Windows | DONE, **battery 9 of 9 felled** | `realstock_gate_board.json`, `realstock_h10_report.json`, `realstock_cf_table.csv` |

L1 is kept in this ledger rather than dropped: it is the run whose 100 failures found the defect.

---

## Verified

**Both platforms completed the whole campaign.** 410 of 410 cells locally, 410 of 410 on Speed,
0 failed on either host, 0 severe, 0 fatal, 0 unstable-heat-balance markers.

**The platform arm — this is the number `FINDING 181` was waiting for.**
The SAME IDF bytes ran on both hosts: `idf_sha256` matched on **410 of 410** cells, so refusal `P1`
dropped nothing. EnergyPlus **23.1.0 on both** — the installed Windows build, and
`/speed-scratch/o_iseri/energyplus_23.1.0.sif` on Speed. Speed's extracted **24.2.0** trees were not
used and must never be for this campaign.

| metric | verdict | worst relative difference | on |
|---|---|---|---|
| `annual_heating_kwh` | agrees within 1e-6 | **8.66e-15** | `es__…240880159_part0__caseA__f050` |
| `peak_hourly_building_kw` | agrees within 1e-6 | **5.39e-14** | `es__…240880159_part0__caseB__f050` |
| `coincidence_factor` | agrees within 1e-9 | **3.45e-14** | `uk__…240880079_part0__caseB__f050` |
| `q99_hourly_building_kw` | agrees within 1e-6 | **6.30e-14** | `uk__…357175643_part0__caseB__f030` |
| peak **hour** index | same hour in **410 of 410** | max shift **0 h** | — |

🔴 The quotable sentence, and the only one: **numerically stable across the two hosts, NOT bitwise
reproducible, over 410 paired cells.** It is the same wording `D-EU-31` forces on the `it` figure,
and for the same reason. It does **not** move `G8.14`: that gate's platform arm is NOT SCOREABLE
because the **EU campaign's** 1,185 retained manifests carry `platform` in 0 of 1,185, and nothing
here backfills them.

**Gate board** (`realstock_gate_board.json`): `G10.7` INFO · `G10.11` PASS · `G10.12` PASS ·
`G10.15` OPEN_INHERITED · **`G10.19` NOT_EVALUABLE_FAIL_BY_POPULATION** · `G10.20` PASS ·
`G10.21` PASS · `G10.22` PASS. Mutation battery **9 of 9 felled**.

**`H10`, reported as INFO exactly as Q1 (a) ruled**, `N` declared, residuals shown, arms never pooled.
Case B minus Case A, medians over buildings:

| f | Arm D (n=18) median ΔCF | median Δpeak % | Arm F (n=23) median ΔCF | median Δpeak % |
|---|---|---|---|---|
| 0.00 | 0.00000 | 0.0000 | 0.00000 | 0.0000 |
| 0.15 | 0.00000 | −0.0221 | 0.00000 | −0.0176 |
| 0.30 | 0.00000 | −0.0484 | 0.00000 | −0.0351 |
| 0.50 | −0.00175 | −0.1200 | −0.00061 | −0.1254 |
| 1.00 | −0.00610 | −0.5909 | −0.01577 | −0.8469 |

`CF(N) = g_inf + (1 − g_inf)/√N`, one free parameter, Arm D only, `N` in 1..28, n = 18 per level:

| f | `g_inf` | R² | RMSE | max abs residual | CF spread | pairs decreasing |
|---|---|---|---|---|---|---|
| 0.15 | 0.9993 | 0.2837 | 0.0004 | 0.0009 | 0.0015 | 116 of 141 |
| 0.30 | 0.9975 | 0.1928 | 0.0013 | 0.0029 | 0.0046 | 109 of 141 |
| 0.50 | 0.9943 | 0.2484 | 0.0027 | 0.0078 | 0.0117 | 101 of 141 |
| 1.00 | 0.9776 | 0.2856 | 0.0084 | 0.0219 | 0.0372 | 104 of 141 |

🔴 **Read this as INFO and nothing more.** The sign is the pre-registered one — `CF` falls as `N_u`
rises, and falls further as `f` rises — but **R² is 0.19–0.29**, the CF spread at `f = 1.00` is
0.037, and the population is **es 9 / uk 5 / it 3** against `G10.19`'s 30 per fold. `H10` is
**NOT EVALUABLE at the pre-declared strength** and no `g_inf` above is a result. `f = 0.00` is not
fitted: `CF` is degenerate there by construction, which is the control working.

⚪ **The annual channel stayed null, as the 92.4–97.5 % diurnal-attenuation prior said it would**:
median Δannual is 0.0000 % to −0.0363 % in Arm D across every `f`. The effect is a **peak-and-timing**
effect, per `FINDING 184`.

⚪ **Arm F is the control and it behaves like one.** Its `CF` moves with zone count and `f` while
`N_u = 1` throughout, which is precisely why `G10.22` calls it a **lower bound** and why the two arms
are never averaged together.

---

## Decisions

**D — the author reversed `Q3` on 2026-08-28, in his own words, after the doc was ruled.**
`Q3` had been ruled **(a) local Windows only, ~400 runs, no cluster staging, no two-platform
divergence**. The author then wrote: *"tu peux utiliser des ressources de la speed avec de la
simulation parallele plus de 32 different cpu, pourquoi locale?"* and, when told that (a) was his own
ruling, *"utiliser le speed, change le decision … soumettre des runs meme a la speed, vas-y"*.
🔴 **The ruling is superseded and must never again be cited as a reason not to use Speed.** The
questions doc carries the reversal additively in §7; §6 was not rewritten.

**D — the campaign runs on both hosts, and that is a gain rather than the "divergence" Q3 feared.**
What `Q3` (a) was protecting against was two hosts producing two different answers with no way to
tell which. Shipping ONE set of IDF bytes and pinning EnergyPlus 23.1.0 on both removes that risk and
converts the second host into the measurement `FINDING 181` has been missing since `EU-08` closed
with `platform` in 0 of 1,185 manifests.

**D — Speed rebuilds no geometry.** Speed has **no `shapely` and no `geopandas`** (env
`envs/step4` carries `eppy`/`numpy`/`pandas` only) and `/speed-scratch/o_iseri/openubem` is a partial
tree. Installing a geometry stack there would have made the Speed cells a *different construction*,
not a different platform. So the IDFs and their hourly gain CSVs are emitted once on Windows and
shipped, and Speed runs EnergyPlus and nothing else.

**D — `Schedule:File` now carries a bare file name, on BOTH hosts.**
`emit_step8_gain_schedule` writes an absolute Windows path, which cannot resolve on Linux. Rewriting
it to the basename after emission (EnergyPlus resolves it against the run directory, where the CSV
already sits) is what lets the *same bytes* run on both hosts. The local arm was **re-run** under the
new emitter so that the two sides are genuinely the same file — not patched on one side only.

**D — the census decides the arm; the layout probe never overrules it.** See the defect below.

---

## 🔴 The defect the first local run found

Four — and then ten — Arm **F** buildings failed with *"geometry route disagrees with the census
arm"*: `BATIMENT…240877159`, `…240879467`, `…240880393`, `…240881134` and others, every one recorded
`FALLBACK_PENDING_LAYOUT` / `PARTITION_AUDIT_FAILED` in `s1_layout_reachability_census.csv`.

**Cause.** The route was chosen by *re-probing* `generate_european_dwelling_layout` at
`units_per_floor`. The census had audited a **different** requested count and refused; the re-probe at
2, 4, 3 and 5 dwellings per floor **succeeded**. The code then saw `emitted = True` against a census
arm of `F` and refused the cell.

**Why it mattered more than the 100 failures.** Had the refusal not been there, a successful probe
would have **promoted those buildings into Arm D** and manufactured `N_u > 1` for buildings the
census had explicitly refused to partition — inflating the only population in the project where
`N_u > 1`, which is the population `H10` is measured on.

**Fix.** The route is now driven by `cell["arm"]`, which comes from the census (pinned by refusal
`R3`). The probe result is still computed and **recorded** — `probe_emitted`,
`probe_disagrees_with_census_arm` — so the disagreement is measured on every cell rather than
swallowed. The refusal now fires only in the honest direction: census says **D** and the layout
contract will not emit.

---

## WHAT I DID NOT VERIFY

- **Nothing here is an accuracy claim.** Heating-only, two end uses, `Zone Ideal Loads` hourly. Step
  10 §11 forbids a measured-accuracy statement and none is made.
- **The corpus is Lyon geometry.** All 41 buildings are `FR-LYO-HAUTCOEURPENTES` BD TOPO footprints
  under the 10.4 exercise relabelling. No national stock claim, for `es`, `uk`, `it` or France.
  `G10.11` is satisfied because there is no French fold, no French diary and no French cell in a
  denominator — the geometry provenance is printed on every artefact rather than hidden.
- **`G10.21`(ii) is still not scored on simulated power.** It was scored on the emitted `φ` channel at
  10.9 (PASS) and is CARRIED, NOT SCORED here, with the measurement printed. No threshold moved.
- **`G10.19` can never PASS on this corpus.** Recorded `NOT_EVALUABLE_FAIL_BY_POPULATION`,
  permanently, per Q1 (a). No contract was relaxed to reach a population.
- **`D-EU-31` was not touched.** Q4 (a) scopes it to the 149 certified EU archetype cells; no
  certified-cell number is quoted, computed or re-run anywhere in this campaign.
- **`prereg.md` stays frozen** at md5 `e4243e07cdd80c9c846b91f40e3e8c45`, checked by refusal `R1`
  before every one of the runs above.
- The Speed run tree under `/speed-scratch/o_iseri/step10_realstock/cells/` was **not** deleted; only
  `speed_metrics.jsonl` and `idf_sha256_speed.txt` were pulled back.

## Next

Nothing owed on this campaign. `FINDING 181`'s second-Windows-box arm remains an owner ACTION.


---

## 🔴 CORRECTION, ADDITIVE — `FINDING 193`: THE SENTENCE "0 UNSTABLE-HEAT-BALANCE MARKERS" IS **FALSE**, AND WHAT IS ACTUALLY THERE IS `FINDING 182` REPRODUCED ON AN INDEPENDENT CORPUS

🔴 **The wrong claim is left in place above and corrected here.** §Verified and §7.4 of the
questions doc both say *"0 severe, 0 fatal, 0 unstable-heat-balance markers"*. The first two are true.
**The third is not.** The scored board never said it — `realstock_gate_board.json` records
`G10.15.diverging_heat_balance_markers = 190` — so this is a prose error against our own artefact,
which is the class `V10.h` exists for.

⚪ **What is measured.** **190 of 410** cells carry one marker each, and the distribution is not
random: **190 of 190 `es` cells carry it and 0 of 220 `uk` + `it` cells do.** Identical on **both
hosts** — Speed's `speed_metrics.jsonl` splits 190 / 220 exactly the same way — so it is **not** a
platform artefact and it does not disturb the platform arm.

⚪ **What the marker is, read from the `.err` rather than named from memory.**
`** Warning ** Temperature out of range [-100. to 200.] (PsyPsatFnTemp)`,
`Routine=PsyTwbFnTdbWPb, During Sizing, Environment=ANNUALSIZINGPERIOD`, input temperature
**−126.168377 °C**. The recurring-error summary reports it **1 total time, 0 during Warmup,
0 during the annual run**. 🔴 **It therefore enters no hourly series, no annual total, no peak,
no `CF` and no `q99`** — every number in this document stands. 410 of 410 completed on both hosts,
0 severe, 0 fatal: still true.

⚪ **The `es` weather file is clean, so the −126 °C is generated inside EnergyPlus.**
`es_madrid_2009_2010_y2010.epw`: 8,760 rows, dry-bulb **−5.3 … 37.3 °C**, dew point
**−12.4 … 17.3 °C**, no sentinel values, and 12/26 13:00–16:00 reads 3.2 / 4.2 / 5.0 / 6.8 °C.
The out-of-range temperature is produced by the **sizing period** on that weather, not read from it.

🔴 **Why this is worth a finding rather than a typo fix.** `FINDING 182` recorded `marker_psy`
as **perfectly confounded with the `es` fold** on the EU campaign's certified cells. This campaign
**reproduces that confounding at 190 of 190** while sharing **no cell, no footprint, no archetype and
no injection** with it. The only factor common to both is the **`es` weather basis**, and the file
itself is clean — which points at the sizing-period construction on that weather and away from the
geometry, the campaign and the platform. ⚪ **It is an OpenUBEM-side observation, raised as a
measurement; nothing here diagnoses their sizing objects.**

⚪ **What moves on the board: nothing.** `G10.15` was already `OPEN_INHERITED` and is now open with
a **measured, structured population** instead of a clean count — which is the gate working. No
threshold moved, no verdict changed, `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched.
