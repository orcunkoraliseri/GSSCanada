# Manager prompt — 3J Leg-3 Step 9, **2026-08-03** (rewritten after arm H closed)

Paste this whole file as the first message of a fresh session. It is self-contained.

> **Third and current version of this file.** The morning version is kept beside it as
> `3rdJ_L3_manager_prompt_2026-08-03_PRE-ARMH.md`; the launch version it replaces described the
> campaign as *running*. **Arm H is now COMPLETE, AGGREGATED and CLEAN.** Nothing in this file is
> waiting on a cluster job. Two things are waiting on the user (§5), and one substantial piece of
> analysis is waiting on you (§4).

---

You are the manager on the 3J Leg-3 four-channel mixed-use tower BEM pipeline. Work in
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\`.

## Standing rules — non-negotiable

- 🔴 **NEVER run a blocking `srun`, `python`, or any computation on the Speed login node
  (`speed-submit2`). ALWAYS `sbatch`.** Flagged three times; one more is account suspension.
  Allowed on the login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, and single-file `tail`/`head`/`grep`/`wc -l`/`cat`. `tar`, `find`, `python`,
  **`md5sum`** are **not** allowed there — put hash checks inside the job, on the compute node.
  The login shell is **tcsh** — no `for` loops, no `2>&1`, **no `2>/dev/null`**, one short line.
  - 🔴 **`2>/dev/null` inside an `ssh speed "..."` command is a tcsh parse error** ("Ambiguous output
    redirect"), and it does **not** fail loudly — the command's stdout comes back empty and the
    caller reads that as "no result". On 2026-08-03 a poll loop built this way reported an empty job
    state 40 times over 3.3 h and never noticed the job had finished in 29 min. If you must suppress
    stderr on the cluster, don't: read the error.
- **Every job requests `-t 7-00:00:00` minimum.** No exceptions, even for one-minute probes.
- Cluster commands single-line, each labelled "locally" or "on the cluster".
- **Never widen a band or relax a gate to erase a FAIL.** The remedy is re-specification or an
  explicit `N/A`. A gate counts as validation only once it has been *seen failing*; write the
  falsifiable prediction **before** running the test. **A miss is recorded, not repaired.**
- 🔴 **Vacuous tests are the recurring failure on this project — TEN kinds.** Before recording any
  PASS, ask: *what result would have made this fail?*
  - **#9 — the gate whose REFERENCE is derived from the same source it audits.** `D8` passed while
    the defect was live because the corrupted Saturday was simultaneously its reference and its
    target. Replaced by `D9`, which reads the **saved IDF**.
  - **#10 — the gate that reads the WRONG PROCESS's exit code.** `smoke_f9fix.sh:47` ran the T9-13
    suite as `$PY test_t9_13.py | tail -3` then reported `$?` — **tail's** status, always 0.
    ✅ **The suspicion that this pattern "was copied around" is REFUTED**: a repo-wide sweep found
    **exactly one** occurrence, the one already fixed. Do not re-run that sweep.
  - **A new bound, not a new kind — a gate can be real and still not prove what it is quoted for.**
    Arm H's `G2` requires office/retail Saturday to differ from Sunday, and it passes at +151.69 % /
    +95.18 %. But the **zero-injection** `Default_NECB` control gives office **2.5169**, identical to
    four decimals to the fully-injected cells: the Sat/Sun *ratio* is inherited from the DOE
    prototype and is structurally invariant under T9-13, because Saturday and Sunday both take the
    same weekend multiplier `r_we`, which cancels. G2 therefore separates "FINDING-9-fixed injector"
    from "pre-fix injector" (its stated counterfactual, ratio → 1) but does **not** separate
    "injected" from "not injected at all". **Never quote "office Sat/Sun differs by 151 %" as
    evidence the injection reached the model.** The gate that shows that is `G1`.
  - **Silence is a failure mode, and it must be made loud.** A reader that returns 0.0 for an input
    form it doesn't understand blames the simulation for its own gap — this cost 16 spurious FAILs
    in job 1171607. Every reader must now itemise what it could not read (`G4` pattern).
  - Related method note: a falsification that patches the READER when the defect lived in the
    WRITER tells you about your harness before it tells you about your gate.
- **A local `py_compile` is NOT a valid syntax check for cluster code.** Local Python is **3.13**
  (PEP 701), the cluster env is **3.10.20**. Compile inside the job, under `$PY`, and refuse to run
  if it fails. (`recheck_armH.sh` §0 is the pattern to copy.)
- **Do not append to the Progress Log with PowerShell `Add-Content`.** PS 5.1 `Get-Content` reads a
  UTF-8 file as ANSI and double-encodes the whole insert. Append with bash `cat >>` / heredoc.
- **Verify every number you inherit.** Re-derive from the artefact's own columns. **Including
  numbers from earlier in this same log** — it is append-only, so an early section can be flatly
  contradicted by a later one (the arm-E scorecard, FINDING 8's mechanism). **The last statement
  wins; grep forward before quoting.**
- 🔴 **Never count lines with PowerShell.** `Measure-Object -Line` counts an empty line as zero and
  silently undercounts by the number of blanks. Use `wc -l` via the Bash tool, always.
- **Update the Progress Log live** — same response as each state change, not batched. The live doc
  is `3J_docs_occ_nTemp/improvements/3rdJ_L3_improvements_step9.md`, **5,659 lines** (`wc -l`, end of
  2026-08-03). Read the last ~600 **counted from the real total**.
- **Leg-2 is closed and paper-ready — no file under `Leg2_2-split/` may be modified.** Reading its
  IDFs and `eplusout.sql` is fine.
- All documents in English; reply to the user in English even though they write French. Keep replies
  short.
- Cheap models for mechanical work; minimum monitoring interval 30 min; never poll in a loop.

---

## 1. ✅ ARM H IS DONE — 56/56, aggregated, clean

User ruling, 2026-08-03: *"lance la campagne 56 cells avec volume_scaled"*, then *"continue jusqu'à
la fin"*. Executed to completion.

| | |
|---|---|
| campaign | job **`1171496`**, array `0-55%20`, 56 cells, ~4 h wall — **all COMPLETED** |
| aggregation | job **`1171607`**, COMPLETED exit 0, 29 min |
| follow-up checks | jobs **`1171754`** (re-check) and **`1171755`** (G4 falsifier), both COMPLETED |
| flags | `--lighting-model calibrated_v2 --dhw-model volume_scaled` (identical to arm E) |
| results | `/speed-scratch/o_iseri/step8_4split/campaign/out_H_allfix/campaign_233932d7` |
| tables | `campaign/agg_H_allfix/` — `agg_annual`, `agg_annual_by_channel`, `agg_diurnal`, `agg_meta`, `agg_peak` |

**Aggregate:** 56 / 56 cells, **attribution residual 0.000000 % on every cell**, zero
cool/hvac/dhw fallbacks. Site energy 27,502 GJ (`Y2010__Tall__CLG`) → 52,887 GJ
(`sens_office_cons__SuperTall__MTL`).

`H − E` isolates the four fixes and nothing else:

| fix | carrier | md5 |
|---|---|---|
| FINDING 6 — office 2030 on the matched stock frame | `office_presence_multiplier_2030.csv` | `575d17e5` |
| FINDING 7 — retail 2030 rewired to calibrated `_C_v2` | `retail_presence_multiplier_2030_{cons,central,opt}.csv` | `82b425b5` / `11414644` / `700398d0` |
| FINDING 8 — DHW cache-key collision | `commercial_integration.py` | `233932d7` |
| FINDING 9 — per-day-type Sat/Sun volume loss | same injector | `233932d7` |

### Every structural guard holds

| guard | result |
|---|---|
| injector-hash guard on the campaign dir | `campaign_233932d7` — OK |
| cell count | 56 / 56 |
| P1 `t9_13_audit` | **50 PASS / 2 FAIL (both verified admissible) / 4 N/A** |
| `n_dhw_excluded == 0`, `n_dhw_unresolved == 0` | 56 / 56 both |
| `r` saturated at `r_max` | 0 |
| D7 (assignment, re-read from the saved IDF) | 56 pass, 0 fail, **0 absent** |
| D9 (per-day-type, re-read from the saved IDF) | 0 absent, 0 with `n_d9>0`, **0 unchecked**, **0 two-day-type FALLBACK** |

`n_audited` is constant within every (geometry, channels) group — 0 non-constant groups — and is
**not** a universal 47, which is the whole point of gate 2b:

    SuperTall | office,retail,hotel,residential | 71  (20 cells)
    SuperTall | office,retail,residential       | 47  ( 6 cells)
    SuperTall | []                              |  0  ( 2 cells)
    Tall      | office,retail,hotel,residential | 47  (20 cells)
    Tall      | office,retail,residential       | 31  ( 6 cells)
    Tall      | []                              |  0  ( 2 cells)

**The 2 P1 FAILs are documented-admissible, not repaired.** Both are `Y2015__SuperTall__{CLG,MTL}`,
same object and same household, read off the saved IDF in job 1171754:

    F38 Resi_bot_S_Apartment_4 Service Water Use 0.06gpm 140F
      Schedule  MXU_Residential_DHWv2_HH46341_APARTMENTHIGHRISE_APT_DHW_SCH_r0000w0996
                                                                          ^^^^^ r_wd = 0.000

`r_wd = 0.000` is exactly the pre-registered exception — a household with zero weekday occupancy has
no weekday peak hour to preserve, so `D2 peak hour 7 → 0` is correct. **The provenance line still
reads `t9_13_audit_verdict=FAIL` and was deliberately left untouched.**

### The DHW volume series — the whole point of arm H — is verified three ways

1. **G1–G7 sweep, 56/56 on every gate.** Pre-registered hotel-saturation test **CONFIRMED**: cells
   with `r_hotel > 1` show lower annual hotel ΔT (24.504 K vs 25.543 K at `r == 1`, Δ = −1.039 K;
   `corr(r_hotel, ΔT) = −0.3395`, negative as predicted).
2. **Volume identity vs EnergyPlus's own reported volume, all 56 cells:** 09E reader **40 FAIL /
   16 PASS**, corrected reader **56 PASS / 0 FAIL**. The 16 cells where 09E passes are exactly the
   ones whose hotel channel was never injected — a clean mechanistic confirmation that **09E's miss
   is caused by injection, not by the cell**. Worst objects everywhere: the hotel laundry read
   **3.500× too low** (mean 0.0833 vs 0.2917, +1194.7 m³/yr), the two office restroom blocks 1.118×.
3. **FINDING 9 at the OUTPUT level, all 56 cells: 56/56 PASS.** Fully-injected cell:

       channel        sat pred  sat meas   err %  sun pred  sun meas   err %   sat/sun
       office           0.4685    0.4685  -0.00    0.1861    0.1861  +0.00    2.5169
       retail           0.0295    0.0295  +0.00    0.0151    0.0151  +0.00    1.9518
       hotel            3.2859    3.2873  -0.04    3.2728    3.2714  +0.04    1.0049
       residential      1.0979    1.0979  +0.00    1.0979    1.0980  -0.01    0.9999

   Residential Sat == Sun **by construction** (`For: Saturday Sunday Holidays AllOtherDays`, and the
   residential channel resolves only `r_wd`/`r_we`) — FINDING 9 was a commercial defect and never
   applied to residential. Hotel flat at 1.0049 is the pre-registered `G3` outcome.

**Read the miss, not just the result.** This gate first ran **40 PASS / 16 FAIL**, and the 16 were
**our reader's fault**: the predictor read `Schedule:Compact` only, so any channel the injector had
*not* rewritten (`Default_NECB` ×4 with `channels_requested=[]`; `Y2005/2010/2015` ×12 with no hotel,
because the QC hotel truth series starts in 2019) kept its prototype `Schedule:Year → Week:Daily →
Day:Interval` chain, was skipped, and was predicted at **0.0000** against a measured 2.9237 m³/h.
Fixed by teaching the predictor the Schedule:Year chain — **not** by touching the 1 % band — plus a
new gate `G4` that itemises any schedule it cannot read instead of silently predicting zero.

**`G4` was falsified before being counted (job 1171755).** Perturbation: disable the Schedule:Year
reader only. Three predictions written first, three landed — P1 G4 fails on the control with 47
itemised objects; P2 the old −100 % symptom is reproduced; **P3 the injected cell is unaffected
(unreadable = 0), so the perturbation is surgical.** P3 is the one that matters.

---

## 2. FIRST ACTIONS OF THE SESSION

There is no cluster job to check. Start at §4 — the scoring work — after reading the last ~600 lines
of the Progress Log (from the real `wc -l` total, 5,659).

The arm-H tables are already local-ready; pull them with `scp` from `campaign/agg_H_allfix/` if you
need them locally. **Do not re-run the campaign, the aggregation, or the three volume sweeps** —
all four are complete and their logs are in `campaign/logs/` (`aggH_1171607.out`,
`aggH_dhwvol_1171607.csv`, `aggH_identity_1171607.txt`, `aggH_daytype_1171607.txt`,
`recheckH_1171754.out`, `falsG4_1171755.out`).

---

## 3. What arm H changed beyond the four findings — CLOSED

`Water Use Equipment Total Volume` was never requested as an output, so every volume column in arms
A–E reads `nan`. It is now requested (`DHW_VOLUME_VARIABLE` in `3rdJ_08P_probe_driver.py`) and
written per channel to `dhw_volume_hourly.csv`. **Verified present, 8760 rows, non-`nan`, no
`dhw_volume_hourly_exception` in any manifest.**

**The motive was anti-vacuity.** The only prior statement of the T9-13 volume identity (0.9647) came
from `3rdJ_09E_dhw_identity_probe.py`, which parses the IDF **with our own reader** — audited
quantity and auditing reference both products of code we wrote, i.e. vacuous-gate kind #9 sitting
inside the one number quoted as proof T9-13's arithmetic is correct. EnergyPlus integrates the
schedule it was actually handed, so its reported volume is a reference our parser cannot corrupt.

**That was the right suspicion and it paid off.** The pre-registered 3 % identity gate **FAILED** at
−36.89 % / −38.52 %. Cause located in **our reader**, not in T9-13: 09E's `compact_profiles()`
resolves a `For:` field with a first-substring-match chain, so

    For: Weekdays Saturday Sunday Holidays SummerDesignDay WinterDesignDay AllOtherDays

— one field naming seven day types — collapses entirely onto the **weekend** bucket and the weekday
profile stays 0.0. The two hotel laundry objects use exactly that form, and
`Laundry Service Water Use 30.6gpm 180F` is the single largest DHW draw in the tower.

- **The published residential 0.9647 is unaffected** — 09E's `volume_table()` filters on
  `RESID_TOKENS`, so it never reads a laundry or restroom object. Checked, not assumed.
- 09E now **REFUSES** a multi-day-type `For:` field rather than mis-reading it
  (`_for_field_is_ambiguous`). Residential behaviour is unchanged.
- The as-published defective chain is **frozen verbatim** inside
  `3rdJ_09H_volume_identity_indep.py::_compact_profiles_as_published` so the −36.89 % FAIL stays
  reproducible. A recorded miss must not become irreproducible because the bug was fixed.
- The corrected reader closes to **1.0000 / +0.00 %**, and was falsified 3-for-3 (peak ×1.50 → FAIL,
  ×1.05 → PASS, ×1.12 → FAIL — all on the predicted side of the 3 % band).
- Calendar is **read from the IDF's RunPeriod**, never guessed from the cell name: the cells are
  named `Y2022` but the RunPeriod is **2006 starting Sunday** (52 Saturdays, 53 Sundays).
- `OUTPUT_SCHEMA_HASH` **`db4e729f` → `93dd5129`**, by design; checked for *uniformity* across cells,
  not against a literal. `INJ_HASH` does **not** move.

---

## 4. Scoring — RE-ISSUED against arm H, **4 PASS / 2 FAIL** (job 1171763)

**Both scorecards stand. Neither supersedes the other.** Arm E's verdicts were scored against
predictions written before arm E ran; arm H's against predictions written before arm H was read. A
later run produces new numbers, it does not repair an old verdict.

| | arm E | **arm H** | arm-H detail |
|---|---|---|---|
| P1 shape | PASS | **PASS** | night 00–05 share 0.0834 → 0.0857, peak hour **06:00 unmoved** |
| P2 office DHW | FAIL | **PASS** ← changed | +5.89 / −5.23 / −19.78 % vs re-derived +6.0 / −5.4 / −20.4 |
| P3 hotel DHW | FAIL | **FAIL** | **+5.21 %** vs +12.4 ± 2.0 — misses **LOW** (arm E missed high, +15.31) |
| P4 residential | FAIL | **FAIL** | **+7.70 %** vs +8…+18 — misses the floor by **0.30 pp** (arm E: +51.40) |
| P5 non-DHW bound | PASS | **PASS** | 0 of 220 material end uses over 0.5 % on the 20 F6/F7-free cells |
| P6 integrity | PASS | **PASS** | 56 = 56 tags, max \|ΔArea\| = 0.0 m² over 392 pairs |

Arm E's own table, for reference: P2 office DHW +21.7 / +8.4 / −3.7 % vs predicted +0.3 / −11.2 /
−21.8; P3 hotel +15.31 %; P4 residential +51.40 %. **The earlier 2P/3F/1U arm-E table is superseded
by 3P/3F/0U — do not quote it.**

**P2's re-derivation is the template to reuse.** The arm-E model
`ΔV/V = (5·V_wd·r_wd + 2·V_we·r_we)/(5·V_wd + 2·V_we) − 1` (V_wd = 11.95, V_we = 3.71) was validated
**backward** against its own recorded past (reproduces +0.3 / −11.2 / −21.8 to ≤ 0.02 pp) *before*
being used forward on the corrected office `r`. It then predicted arm H to 0.11 / 0.17 / 0.62 pp.
Office DHW spread arm C **0.004 %** → arm H **27.419 %**. A qualitative claim died here and is
recorded: arm E's "`B_cons` must come out flat" was a property of the **defective** product; with the
corrected one `B_cons` rises +6 %.

### 🔴 P3 and P4 both miss LOW, and the mechanism is now measured

`3rdJ_09H_saturation_probe.py` (job 1171765), inside arm H only:
**hotel VOLUME elasticity w.r.t. `r` = 1.0000 (R² = 1.000)** — T9-13 delivers exactly the draw it
specifies — against **ENERGY elasticity 0.5617**.

That probe also printed "SATURATION CONFIRMED"; **that verdict was WITHDRAWN as under-specified.** A
constant standby loss gives an energy elasticity below 1 with no capacity constraint at all
(`E = L + V·ρc·ΔT`). The discriminator is the **marginal** m³, which under a fixed loss must still be
served at the full target rise. `3rdJ_09H_saturation_discriminate.py` (job 1171767):

* target rises in the IDF **140F → 49.2 K, 180F → 71.4 K** (mains 10.81 °C);
* implied **marginal** rise **22.66 K = 46.1 %** of the most generous benchmark, < 70 % in all four
  (geometry, city) groups → **D3 SATURATION met, D2 CONSTANT-LOSS not met**;
* **D4, which needs no fit**: average delivered rise falls monotonically 41.65 K at `r = 1.0` to
  38.40 K at `r = 1.2031`, `d(ΔT)/d(ln r) = −17.56 K`;
* **D1, my own linearity control, FAILED in one group of four** (`SuperTall__CLG`, R² 0.9654 < 0.98).
  Quadratic terms are ~1e-6 with inconsistent sign, so it is scatter not curvature — but per its own
  pre-registration that group is inadmissible, so **the conclusion rests on the other three plus D4.**

**P3 is therefore MIS-SPECIFIED, not merely missed**: it predicted a *volume* change (+12.4 % from
`r = 1.1244`) and scored it against an *energy* measurement. Decomposition of the 7.2 pp gap —
~1.7 pp is the prediction's own city-averaging (the four `B_central` cells average **r = 1.1070**,
so the volume-side prediction should have been +10.70 %), and +10.70 % volume → +5.21 % energy is the
plant, a local elasticity of **0.50**. **The remedy is re-specification — predict volume, or predict
energy through an explicit plant model — which changes declared gate semantics and is the USER'S
CALL. Do not widen the band.**

**P4's 0.30 pp miss** is consistent with the same mechanism reaching the residential channel via the
aggregator's attribution of the un-prefixed hotel `Laundry Service Water Use 30.6gpm 180F` — the most
saturation-limited object in the tower — to **residential**. **Candidate, NOT tested**: the laundry
cannot be split out of a channel total from the aggregate tables.

**Spent P4 candidates — do not re-run.** Job `1171408` tested "peak flow rose against hard-sized
heaters → more recovery time": **REFUTED**, `Water Use Equipment Heating Energy` ×1.389. FINDING 8
explained ~29 % of arm E's +51.40 % (the laundry attribution, +1848 GJ of a +6366 GJ residential
rise); the rest is now accounted for by the F8/F9 fixes bringing arm E's +51.40 % down to +7.70 %.

### Still open in §4

**The `Y2022` office channel (+28.6 % at `r ≈ 1.0`)** — the office restroom objects moved **×0.952**,
i.e. *down*, while the office channel total rose. An **attribution** question. FINDING 9 accounts for
the ×0.952 itself (now ×1.000 in arm H), so **re-measure in arm H before theorising.**

---

## 5. 🔴 Waiting on the USER — do not decide these yourself

1. 🔴 **Hotel DHW plant is undersized by construction, in every arm A–H — and it is now measured as
   an ACTIVE DISTORTION, not a static observation.** Inherited from ARCH B, not introduced by any
   finding. Mains at 10.81 °C; Y2022 delivered fractions office 100.0 %, retail 100.0 %, residential
   94.5 %, **hotel 36.8 %** — **4,432.3 GJ unmet**. `Laundry 30.6gpm 180F` alone demands **577.1 kW**
   against **447.6 kW** installed tower-wide across six hard-sized `WaterHeater:Mixed` (no `Autosize`).
   **New, from arm H (§4):** the marginal cubic metre is served at **22.66 K against a 49.2 K target
   — 46 %**, so **~54 % of any increase in hotel draw never appears as delivered energy.** Every
   "hotel DHW rises X % under scenario Y" statement in Steps 8–9 is a plant-capacity statement as
   much as an occupancy statement. `Autosize`-ing the six objects moves every hotel and residential
   DHW number in every arm → **re-simulation decision, the user's to take.** Do not quietly autosize.
2. **How to re-specify P3.** It predicted a *volume* change and scored it against an *energy*
   measurement on a saturated plant. The remedy is re-specification (predict volume — which T9-13
   delivers at elasticity 1.0000 — or predict energy through an explicit plant model). That changes
   declared gate semantics, so it is the user's call. **The band must not be widened.**

## 5b. Open items — flagged, not fixed

1. **`F30 HOTEL_BOT_LAUNDRY`, 1.9 %.** Peak-flow rescale **excluded by measurement** (job 1171446).
   Remaining candidate: plant-loop coupling with the main `LAUNDRY` draw, which fell 67 % on the same
   service-water system. **Untested.** The FINDING 9 smoke's discriminating prediction held (F30
   required to stay at 1.019 because its prototype has Sat == Sun, and it did), so the FINDING 8
   attribution stands and F30 is genuinely separate.
2. **T9-12's `k = 0.60` needs re-checking** after the FINDING 7 retail rewire — it was calibrated
   against the *uncalibrated* pool's weekday mean and the shape source changed underneath it.
   **Arm H runs the un-retuned `k`**, so any arm-H retail lighting result is provisional.
3. **Arms A–E all carry FINDING 9** (retail DHW +7.7 %, office +4.8 %, hotel `BLDG` +0.5 %). Nothing
   retracted; the §4 re-issue is the remedy.
4. **The 3 Step-9 EUI FAILs** stay FAIL and stay explained-but-not-rescued.
5. **The hotel EUI band question is still open and still blocking `S9-EUI-hotel`.** R1 (amenity
   classification) says `[240, 300]` → **0/56**. R2 (NECB 2017 / CanmetENERGY 2020, CZ-matched) says
   `[140,220]`/`[160,240]` → much better. Tie-breaker is one unanswered question: **is the
   CanmetENERGY NECB 2017 hotel archetype full-service or limited-service?** Requires the
   CanmetENERGY *Commercial Archetypes Performance Study* (2020), not in `deepResearch/`. Until it
   is read, adopting R2 would be choosing the band that rescues the gate over the band that condemns
   it, on no evidence. Currently three **INFO-only** gates; `S9-EUI-hotel` keeps `[180,300]` and its
   FAIL.
6. **Decision 5 (Leg-2 office-EUI corrigendum) needs one bounded read-only job**: run the corrected
   EUI query against **Leg-2's own** `eplusout.sql`. The 1.706× factor was measured on a *Leg-3* run;
   `172.7 / 1.706 ≈ 101.2` is an indication of magnitude, **not a derived value**. Version A of the
   caveat (no number) is publishable today. **Never claim the published band was affected — checked
   and refuted; `OFFICE_EUI_BAND` is hard-coded from literature, not simulation.**
7. Neither `D8` nor `D9` can catch a defect in `_schedule_daytype_profiles` itself, since both
   consult it. The independent guard is `Step9_docs/3rdJ_09F_daytype_loss.py` (its own IDF parser,
   token-based, verified immune to the FINDING 9 defect) — keep running it after any change to the
   schedule readers.

---

## 6. Files and provenance

**New this session:** `Step9_docs/3rdJ_09H_volume_identity_indep.py` (corrected reader + frozen
as-published reader), `Step9_docs/3rdJ_09H_daytype_volume_verify.py` (output-level FINDING 9,
Schedule:Year chain, gate `G4`), `Step9_docs/3rdJ_09H_dhwvol_sweep.py`, `Step9_docs/recheck_armH.sh`,
`Step9_docs/falsify_g4.py`, `Step8_docs/agg_armH.sh`, `Step8_docs/3rdJ_08D_campaign_speed_armH.sh`
(md5 `da7085b9`).

**Modified:** `Step8_docs/3rdJ_08P_probe_driver.py` (md5 `b42dc4ba`) — `DHW_VOLUME_VARIABLE`,
`_write_dhw_hourly_csv(variable=, col_prefix=)`, `dhw_volume_hourly.csv` in `_do_postprocess()`,
`OUTPUT_SCHEMA_HASH` `db4e729f` → `93dd5129`. `Step9_docs/3rdJ_09E_dhw_identity_probe.py` — guard
that refuses a multi-day-type `For:` field. `Step8_docs/smoke_f9fix.sh` — vacuous-gate #10 fixed.

**Unchanged, re-uploaded to guarantee the cluster copy:** `eSim_bem_utils/commercial_integration.py`
(`233932d7`, 2,976 lines by `wc -l`), `eSim_tests/test_t9_13.py` (`9fe462e6`, 58 tests),
`Step7_docs/3rdJ_07_aug_to_bem_4split.py` (`361ad354`), the four Step-7 2030 product CSVs,
`3rdJ_08D_campaign_driver.py` (`8164c10b`), `3rdJ_08D_campaign_cells.py` (`dca23502`).

**Cluster:** `campaign/out_H_allfix/campaign_233932d7` (arm H, complete, `.sql` retained);
`campaign/agg_H_allfix/` (5 tables). Earlier smoke dirs `out_F_f8fix/campaign_456301f5` and
`out_G_f9fix/campaign_233932d7` both keep their `.sql`, so further scoring of those is a 30-second
job with no re-simulation.

**Jobs, 2026-08-03:** 1171438, 1171441/1171442, 1171443, 1171444/1171445, 1171446, 1171448
(cancelled), 1171449 (F9 smoke, 10 PASS / 0 FAIL), **1171496 (arm H campaign, 56/56)**,
**1171607 (arm H aggregation)**, **1171754 (day-type re-check, 56/56 PASS)**,
**1171755 (G4 falsifier, 3/3)**.

Useful local command:
`py -3 3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09G_finding9_verify.py --falsify`
— injects both cells with the campaign driver's own call, runs the independent predictor, then
re-creates the pre-fix writer and requires `D9` to catch it. Needs `EPLUS_IDD` =
`C:/EnergyPlusV24-2-0/Energy+.idd`. About 3 minutes, no cluster. Note `py`, not `python` — on this
Windows box `python`/`python3` are Microsoft Store stubs.
