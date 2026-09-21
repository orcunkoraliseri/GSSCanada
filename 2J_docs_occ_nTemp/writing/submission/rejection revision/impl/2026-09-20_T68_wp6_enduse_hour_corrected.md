# T68 — WP6 Part A: end use × hour on the CORRECTED 2022 and 2030 rebuild — task doc

Task doc:   this file
Plan:       `../00_REVISION_PLAN.md` §3 WP6 (line 273), §10 Wave 4
Model:      Sonnet employee, fresh session, cluster-only
Status:     DISPATCHED 2026-09-20

---

## 0. What this task is, in one paragraph

WP6 answers reviewer R1-D18/D19: *annual energy barely moves between 2022 and 2030, so decompose the
result by end use and time of day and make the grid-facing story prominent.* The machinery already
exists — T06 built and ran it, but **on the OLD campaign and on 2022 only**, and author ruling (b)
forbids any old-campaign number from reaching the paper. This task re-points that machinery at the
**T21 rebuild, both years**, adds the per-dwelling-unit correction that T65/T66 discovered is
mandatory for multi-unit archetypes, and carries an interval on every 2022→2030 change so the
T28/T60 quoting rule can be applied. **Scenario arms (T29 λ arms, T32 S-Revert-std) are NOT in this
task** — they are Part B and will be dispatched separately.

**Nothing you produce here is manuscript prose.** You produce tables, controls and a report. The
manager rules.

---

## 1. Rulings that already bind this task — do not re-open, do not re-derive

1. **Author ruling (b): old numbers are dead.** T06's outputs (`impl/T06_out/`) were computed on the
   old `campaign_N50` tree. You may use them **only** as a shape plausibility comparison, and every
   such comparison must be printed with the label `OLD_CAMPAIGN_DO_NOT_QUOTE`. No old number enters
   any result column.

2. **The T21 rebuild has no overlay manifest, and `08_simulation_plots.py` must NEVER be run against
   it unmodified.** `discover_runs()` only accepts a run directory whose `(sample, sim_hh_id)` is
   tagged `source == "new_2022_2030"`, and that tag comes only from a
   `cell_manifest.csv.new_2022_2030_*` overlay file which **T21 does not have**. Run unmodified, it
   returns ZERO rows silently — a worse failure than a crash. Found and documented by T67
   (`impl/2026-09-20_T67_wp8_genuine_cluster_bootstrap_IMPL.md` step 0 item 3). T21's plain
   `cell_manifest.csv` (columns `sample,sim_hh_id,hhsize,dtype,pr`) is the whole truth for that tree.

3. **Multi-unit meters are WHOLE-BUILDING and must be divided per dwelling unit.** A deliberate
   2026-07-13 fix in `eSim_bem_utils_2J/integration.py` broadcasts each household's calibrated
   equipment load across every dwelling-unit-equivalent zone, so a HighRise meter is ~81 dwellings'
   worth of load. T66 derived the divisors **per cell from each cell's own `eplusout.eio`**, and they
   are uniform across the six cities: **SingleD 1, OtherDwelling 7, MidRise 33 (equipment) / 36
   (lighting), HighRise 81 (equipment) / 90 (lighting)**. Equipment and lighting divisors differ
   because the zone sets differ — **never assume one divisor for both**. The corrected validator that
   carries these as explicit per-cell dictionaries (`T66_CELL_EQUIP_DIVISOR`,
   `T66_CELL_LIGHT_DIVISOR`) is at
   `/speed-scratch/o_iseri/2J_revision/T66/scripts/step9_validate_full_corrected.py`. **Read those two
   dictionaries out of that file and reuse them. Do not re-derive, do not edit that file.**

4. **THE DIVISOR RULING — this is the design decision of this task, taken by the manager, and it
   defines which of your outputs are quotable.**
   - **Relative quantities are divisor-invariant** — a percent change, a share of the facility total
     within one meter, a share of the day's energy falling in a given hour, load factor, midday
     share, peak hour, ramp as a fraction. Dividing every hour of a series by the same constant
     changes none of them. **These are the quotable core of WP6 and they carry no divisor risk.**
   - **Absolute per-dwelling kWh exists only for equipment and lighting**, because those are the only
     two meters whose divisor T66 actually derived and evidenced.
   - **For fans, the HVAC+DHW electricity remainder, `Electricity:Facility`, and every
     `*:EnergyTransfer` thermal meter, no derived divisor exists.** Report their absolutes as
     **whole-building raw** with the column plainly named so, and set their per-dwelling column to
     `NOT_EVALUABLE` with the reason string `no derived unit divisor (T66 covers equip+light only)`.
     **Do not invent a divisor. Do not reuse the equipment divisor for fans.** A missing number that
     says why is worth more than a plausible one that is wrong.
   - SingleD's divisor is 1 everywhere, so SingleD absolutes are quotable for every meter.

5. **T28/T60 quoting rule, binding on every change you report:** at 50 households a cell's annual
   electricity total resolves to better than ±0.6 %, but **per-cell 2022→2030 load-shape CHANGES are
   not resolved at 50 or at 200**. So **no per-cell 2022→2030 load-shape change may be described as a
   change unless its own interval excludes zero.** Every change row you write carries its interval
   and an explicit `excludes_zero` boolean. You report the boolean; you never soften a band.

6. **T67's clustering result, binding on `midday_share`:** the honest cell-level cluster bootstrap
   interval for `midday_share` is **39.8 % wider** than the plain pooled interval, and that wider
   interval is the one any main-text claim must cite. `load_factor` is unaffected (2.3 % narrower,
   negligible). The working script is
   `/speed-scratch/o_iseri/2J_revision/T67/T67_scripts/cell_cluster_bootstrap.py`. **Reuse it for the
   two metrics it already implements rather than writing a third bootstrap.** For the other metrics,
   use the same resampling unit it uses — whole cells drawn with replacement, 24 from 24 — so every
   interval in this task is on one consistent basis. The retired `method_b_cluster_bootstrap` in
   `impl/T03_scripts/ci_reproduction.py` is a STRATIFIED bootstrap and its "1.0–3.3 % narrower"
   figure must never be quoted in either direction.

7. **Meter rules, established by T06 and traced to the paper's own code
   (`2J_docs_occ_nTemp/Step8_docs/08_simulation_plots.py`, quote `file:line` in your report):** index
   meters **by name**, never by column order (`:79-91`); `Electricity:Facility` **already includes**
   lights + equipment + fans, so never add them to it (`:80`); `*:EnergyTransfer` columns are thermal
   loads, **never** summed into electricity (`:84-86,89`); the paper's code uses
   `Fan Electricity Energy`, not `Fans:Electricity`, and you follow the paper's own choice.

8. **`WaterSystems:EnergyTransfer` is genuinely absent for every MidRise household** (0 of 300 in
   T06's old-campaign read). If that repeats on the rebuild it is a real "meter absent for this
   archetype" case, **not** a partial read — report it as absent with the count, and make sure no
   stock-weighted total silently becomes `NaN` because of it.

9. **Item 32, recorded so you do not rediscover it:** 43 households carry a `DTYPE` of literal `8` and
   are excluded from every stock-weighted figure upstream of you. 43 of 144,465 changes no number.
   Do not "fix" it, do not drop rows, do not investigate it here.

---

## 2. Inputs — exact paths, all verified by T67 on 2026-09-20

- **Rebuild tree (this is your input):**
  `/speed-scratch/o_iseri/2J_revision/T21/out/step8/<Arch>__<City>/sample_NNN_HH<id>/<year>/hourly_meters.csv`
  24 cell directories (25 entries minus `SimResults_Plotting_Schedules`), 1,200 `sample_*` dirs,
  **2,400 meter files = 1,200 households × 2 years (2022 and 2030)**. Each file is 8,761 lines
  (header + 8,760). Per-cell manifest at `<cell>/cell_manifest.csv`.
- **Divisor source:** `/speed-scratch/o_iseri/2J_revision/T66/scripts/step9_validate_full_corrected.py`
  (read the two divisor dictionaries; never modify the file).
- **Interval machinery:** `/speed-scratch/o_iseri/2J_revision/T67/T67_scripts/cell_cluster_bootstrap.py`
  and the corrected aggregate it consumed,
  `/speed-scratch/o_iseri/2J_revision/T67/out/agg_annual.csv` (2,400 rows — your own annual table must
  agree with it, see control C2).
- **Starting point for your script:** `impl/T06_scripts/enduse_hour_2022_v2.py` in this repo. **Copy it
  into `T68_scripts/` and work on the copy. T06's originals are never edited.** What you change:
  input root and discovery (ruling 2 — plain manifest, no overlay logic), both years instead of one,
  the divisor columns (ruling 4), and the change/interval table. What you do **not** change: the meter
  selection, the weighting, the hourly-profile shape, or any metric definition.
- Interpreter on nodes: `/speed-scratch/o_iseri/envs/step4/bin/python`. Staging:
  `/speed-scratch/o_iseri/2J_revision/T68/`.

---

## 3. What to produce

All under `/speed-scratch/o_iseri/2J_revision/T68/out/`:

1. `enduse_annual.csv` — one row per household × year × meter. Columns must include the raw
   whole-building annual kWh, the divisor used, its source, the per-dwelling kWh **or**
   `NOT_EVALUABLE` plus reason (ruling 4).
2. `enduse_hourly_profile.csv` — mean load by hour of day, per household × year × meter × season
   (`all`/`heating`/`cooling`) × daytype (`all`/`weekday`/`weekend`), exactly T06's shape.
3. `grid_metrics.csv` — per household × year, on `Electricity:Facility`: peak demand, peak hour
   (circular mean), load factor, midday share (the paper's own window, hours 9–16 inclusive, as used
   by T67's builder), evening ramp 14:00→17:00, hours above the household's own annual p90.
4. `enduse_change_2022_2030.csv` — **the deliverable that answers the reviewer.** Per cell and
   stock-weighted, per end use: 2022 value, 2030 value, absolute change, **percent change**, the
   cluster-bootstrap interval on the change, and `excludes_zero`. Percent change and the shape
   metrics are the divisor-invariant columns; mark each row `QUOTABLE` or `NOT_EVALUABLE` by ruling 4
   and ruling 5 **in the file itself**, so no later reader has to re-derive the rule.
5. `closure.csv` — the identity check: lights + equipment + fans + remainder = `Electricity:Facility`,
   per household per year. This is an identity, so it must close to floating-point noise; the
   remainder is reported as its own end use ("HVAC and water-heating electricity"), exactly as T06
   does. **The old 0.07 % test is not this check and must not be reinstated** — that figure compares
   corrected TABULAR electricity against the HOURLY facility meter, a different thing entirely.
6. `controls.json` — see §4. Every control records **did not run / ran and did not fire / ran and
   fired** as three distinct outcomes. A control that crashed is `NOT_EVALUABLE`, never a pass.
7. `run_meta.json` — households read, households skipped **with reason**, row counts, the divisor
   table actually used, any `undelivered.csv` found anywhere in the tree with its reason strings
   (T21 writes none — if that holds, say so, and say plainly that its absence is **uninformative,
   not reassuring**, because T21 is one of the trees that never writes one).

---

## 4. Controls — all four run BEFORE any real number is read, all in the same job

**Every check must be seen failing once on a fake case before its PASS is trusted.** Print each
control's own line in the log and record it in `controls.json`.

- **C1 — seen-failing, hour-of-day.** Take one household's 8,760-row file, roll every column **except
  the `hour` column** forward by 3 positions (the `hour` column names the bucket, so a whole-record
  reorder is a no-op — this is T48's established lesson, plan entry (bx)). The peak hour must move by
  exactly +3 h and the midday share must change. **If it does not move, your hour-of-day machinery is
  not measuring what you think, and no shape number from this task may be quoted.**
- **C2 — seen-working, against a known-good independent number.** Your own annual
  `Electricity:Facility` and `load_factor`/`midday_share` for the households in T67's
  `agg_annual.csv` must reproduce it. Report the max absolute difference over all 2,400 rows. Also
  reproduce the one hand-verified household, `SingleD__Montreal_6A` `sample_001_HH130228` 2022:
  **8209.333463 kWh annual, 4.318054 kW peak** (T45 hand-check, independently reproduced by T67 from
  a different tree). Agreement to 6 decimals is expected; anything larger is a STOP.
- **C3 — divisor invariance, and it is the one that protects ruling 4.** Compute the 2022→2030
  **percent** change for equipment on the raw whole-building series and on the per-dwelling divided
  series. They must be identical to floating-point tolerance. This demonstrates rather than asserts
  that the quotable relative columns carry no divisor risk.
- **C4 — divisor applied, sanity against a passed gate.** After division, HighRise and MidRise
  per-dwelling **equipment** and **lighting** annual kWh must be the same order of magnitude as
  SingleD's and OtherDwelling's per-dwelling values. T66's corrected validator passed 48/48 against
  the SHEU band on exactly this basis, so a per-dwelling HighRise equipment figure still in the
  hundreds of thousands means the divisor was not applied. Print the before/after pair per archetype.

---

## 5. Submission and the rules you work under

- **`sbatch` only. No python on the login node, ever, including one-liners. No `find`, no `du`, no
  recursive listing, no `md5sum`, no `cp`, no `mkdir` on the login node.** The complete allowed list
  on `speed-submit2` is: `sbatch squeue sacct scancel scontrol cd ls scp module load` plus
  **single-file** `tail head grep wc -l cat`. **`find` is forbidden** — T48's employee used it and it
  is recorded; "no python on the login node" is not the whole rule. Any directory iteration,
  `eio` parsing, or file counting happens **inside the job**.
- Login shell is tcsh: no `2>&1`, no `2>/dev/null` in ssh strings.
  `ssh -o BatchMode=yes -o ConnectTimeout=60 o_iseri@speed.encs.concordia.ca`; retry once if the
  connection closes.
- Every job `-p ps -t 7-00:00:00`. Use `-c 8 --mem=32G` (T06's shape, same input scale). **The 2J
  ceiling is 32 CPUs in flight and the account's other 32 belong to a different project — do not
  raise `%N` or `--cpus-per-task` beyond this.** Check `squeue` before submitting.
- **Editing anything already on the cluster: `scp` it down, edit locally, `scp` it back.** Never edit
  in place on the login node.
- **Write state before you stop.** Create `impl/2026-09-20_T68_wp6_enduse_hour_corrected_IMPL.md`
  with the standard sections (Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY), put the
  JobID and every output path in the Ledger as it happens, and keep the ledger append-only — a failed
  job stays, with the line that supersedes it.
- **Submit, write the JobID, end your turn.** No polling, no `sleep`, no background waiter, no
  no-op call to hold the turn open. Collection is the manager's job. If you pass roughly 150k tokens,
  stop, write state, and say "handoff needed".
- Syntax-check your script before upload (`py_compile` if a local interpreter exists; if none does,
  say so plainly and substitute a line-by-line re-read, as T66 did).

## 6. What would make this task a failure

Reporting a per-dwelling absolute for a meter whose divisor nobody derived; calling a 2022→2030
load-shape change a change when its interval contains zero; quoting an old-campaign number; or
returning a number without its controls having been seen firing first.
