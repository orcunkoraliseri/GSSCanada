# T71 -- WP11: the four WP6-derived figures -- implementation state

Task doc: `impl/2026-09-21_T71_wp11_figures_wp6_set.md`
Status:   **DONE -- ACCEPTED by manager 2026-09-21.** See "Manager collection" section at the end.

## Ledger

- **JobID `1341185`** -- `wp11_figures.py` (all four figures, one sequential job). Submitted from
  `speed-submit2` via:
  `sbatch -p ps -c 8 --mem=32G -t 7-00:00:00 --wrap '/speed-scratch/o_iseri/envs/step4/bin/python /speed-scratch/o_iseri/2J_revision/T71/T71_scripts/wp11_figures.py > /speed-scratch/o_iseri/2J_revision/T71/logs/t71_run.out'`
  Interpreter: `/speed-scratch/o_iseri/envs/step4/bin/python` (same one T68/T69 used).
  Pre-submission checks (all single-file/login-node-safe):
  - `python -c "import matplotlib; import matplotlib.pyplot"` -- OK, matplotlib 3.10.8.
  - `python -c "from PIL import Image"` -- OK, Pillow 12.1.1 (needed to verify saved-PNG dpi
    metadata after the fact, per ruling 2 -- "do not just assert the dpi= kwarg was set").
  - `python -m py_compile wp11_figures.py` on the cluster copy -- clean.
  - `squeue -u o_iseri --format='%i %j %t %C'` -- only a `histnu` row (1 CPU) running; 0 of the 2J
    project's CPU budget in use before this job's 8 CPUs were requested.
  - Single `squeue -j 1341185` immediately after submission: `R` (running), node `edmonds`,
    0:02 elapsed -- not polled further, per the no-parking rule.
  Output paths (all under `/speed-scratch/o_iseri/2J_revision/T71/`):
  - `logs/t71_run.out` -- stdout/stderr of the whole job (progress lines + traceback if it fails)
  - `out/figures/fig02_annual_by_enduse.png` + `.csv`
  - `out/figures/fig03_intraday_load_shape.png` + `.csv`
  - `out/figures/fig04_peak_loadfactor_ramp_ci.png` + `.csv`
  - `out/figures/fig05_enduse_hour_diff.png` + `.csv`
  - `out/figures/run_meta.json` -- per-figure dpi/pixel-size (read back from the saved PNG via
    Pillow, not asserted from the `dpi=` kwarg), the seen-working control's result, the figure-3
    household-basis check, and the figure-4 CI-availability check (see Decisions/Findings below).
  Script uploaded to `T71/T71_scripts/wp11_figures.py`; local copy at
  `impl/T71_scripts/wp11_figures.py` (scp'd back after upload, see below) and also archived in
  this session's scratchpad alongside the synthetic-test harness (not part of the deliverable,
  local-only).

  **No number in `out/figures/` has been read yet by this employee from the REAL cluster run.**
  A failed job stays in this ledger with the line that supersedes it -- it is never dropped.

## Verified (numbers actually read, with source)

- **Real-file reconnaissance on the cluster before writing the script** (all single-file `head`/
  `wc -l`/`cat`, allowed on the login node):
  - `T68/out/enduse_annual.csv` header (58 columns) confirmed byte-identical to what
    `T68_scripts/enduse_hour_corrected.py`'s `ANN_COL`/divisor-column-naming logic produces --
    read directly, not assumed from the script alone.
  - `T68/out/enduse_hourly_profile.csv` header (14 columns) confirmed; unique `meter` values (8:
    `Cooling:EnergyTransfer, Electricity:Facility, Fan Electricity Energy, HVACDHW:Electricity,
    Heating:EnergyTransfer, InteriorEquipment:Electricity, InteriorLights:Electricity,
    WaterSystems:EnergyTransfer`), unique `season` values (3: `all, cooling, heating` -- **no
    `shoulder` row is ever written**, even though `SEASON_WINDOWS` defines one in the script --
    confirmed by reading `profile_meters`/the season loop in `T68_scripts/enduse_hour_corrected.py:331`,
    which only iterates `("all","heating","cooling")`), unique `daytype` values (3: `all, weekday,
    weekend`) -- all read directly off the real 4,017,600-row file via `awk`, not inferred.
  - `T69/out/{S-None,S-Partial,S-Revert-std}` and `T69/out/cross_scenario_common_basis.csv`
    directory listing and file sizes confirmed (each arm's `enduse_hourly_profile.csv` is
    ~510-512 MB, matching the task doc's estimate).
  - `T69/out/cross_scenario_common_basis.csv` read in full: four-way intersection = **1198**,
    per-arm singleton counts S-Full=1200, S-None=1198, S-Partial=1200, S-Revert-std=1199 -- this
    is the number figure 3's own computed household set must reproduce (see Decisions/Findings).
- **`T68/out/enduse_change_2022_2030.csv` and `T69/out/S-None/enduse_change_2022_2030.csv` scp'd
  down and read with real pandas locally (not shell `awk`, which mis-splits the file's one
  free-text `ci_method` column that contains an embedded comma -- the same trap T68's own manager
  collection already flagged; avoided here by using a real CSV parser from the start):**
  - T68's file: 250 rows, exactly 10 distinct `metric` values with a `stock_weighted` row
    (`Electricity:Facility, InteriorLights:Electricity, InteriorEquipment:Electricity,
    Fan Electricity Energy, Heating:EnergyTransfer, Cooling:EnergyTransfer,
    WaterSystems:EnergyTransfer, HVACDHW:Electricity, midday_share, load_factor`). **`peak_kW_annual`
    and every ramp metric are ABSENT from this list** -- confirmed by reading the actual file, not
    inferred from the script (see FINDING 1 below).
  - The `load_factor` stock-weighted row: `point_change_pct=0.004943184695576`,
    `ci_low_pct=0.0041284557418345`, `ci_high_pct=0.005743231074777`, `change_type=
    absolute_fraction`, `change_quotable=QUOTABLE` -- read directly, matches T68's own accepted
    number (last+292/T68 collection already quoted this exact triple for `load_factor`).
  - T69's `S-None` file: same 21 real columns plus a leading `scenario` column (all `S-None`);
    missing only the `provenance` column T68's file carries (used solely for the T67-reuse CI
    row's source path) -- confirmed this does not block `pd.concat`, matching the manager's
    already-ACCEPTED decision 4 in the T69 IMPL doc ("APPROVED... WP11's figure-generation script
    may `pd.concat` the four files directly").
- **matplotlib 3.10.8 and Pillow 12.1.1 confirmed importable** in
  `/speed-scratch/o_iseri/envs/step4/bin/python`, via two single-file `python -c` checks on the
  login node (never a script execution, per CLAUDE.md rule #2).
- **`py_compile` clean**, both locally (`py -3.13 -m py_compile wp11_figures.py`) and on the
  cluster copy with the actual project interpreter (`.../envs/step4/bin/python -m py_compile`).
- **Local functional test against a synthetic tree** (`make_synthetic_and_test.py`, not uploaded
  -- local-only harness), shaped exactly like the real four-scenario layout: 4 archetypes x 2
  cities x 2 households x 2 years = 32 household-years per scenario, all four scenario directories
  populated with the real column schema (annual, hourly-profile, grid-metrics, change-table,
  including the `scenario` leading column for the three non-S-Full arms). Run with the real
  Python 3.13 interpreter available locally via the `py` launcher (plain `python`/`python3` are
  non-functional Microsoft Store stubs on this machine, confirmed by their own error text, not
  assumed missing). Results, module imported and its path constants monkeypatched to point at the
  synthetic tree rather than the cluster:
  - **Seen-working control fired and MATCHED on the synthetic data**: the hand-read value (a
    direct boolean-mask `pandas.read_csv`, no chunking, no shared code with the aggregation path)
    and the pipeline's own chunked-reader value for the same (household, meter, season, daytype,
    year, hour) cell agreed to floating-point precision (`match: true`).
  - All four figure functions (`figure_02` through `figure_05`) ran to completion with no
    exception, each writing a PNG + CSV.
  - **DPI verified by reading the saved PNG back with Pillow**, not by trusting the `dpi=600`
    kwarg: all four PNGs report `dpi=(599.9988, 599.9988)` -- this is a known PNG
    pixels-per-metre round-trip artifact (dpi is stored in the `pHYs` chunk as an integer
    pixels-per-metre value, and converting 600 dpi -> pixels/metre -> back to dpi through the
    inches-per-metre constant loses ~0.0002%), not an actual resolution shortfall. Effective
    resolution is 600 dpi to 4 decimal places. Flagging this explicitly so the manager does not
    mistake `599.9988` for "just under the ≥600 dpi bar" -- it is not.
  - Figure widths landed at 6.94-7.79 inches depending on `bbox_inches="tight"` cropping per
    figure (the nominal `FIG_WIDTH_IN=7.0` setting plus tight-bbox trimming of whitespace/legends)
    -- all comfortably at or above the intended 7-inch print width.
  - **Figure 3's household-basis check fired exactly as it should on synthetic data**: the
    synthetic four-way common set (n=16, all synthetic households, since none of the four
    synthetic sets differ) does NOT match the real `cross_scenario_common_basis.csv`'s 1198 (it
    can't -- this is synthetic data) -- the mismatch note in `RUN_META["notes"]` fired correctly,
    proving the check itself is live and will actually compare against something meaningful on the
    real run, not silently pass.
  - **Figure 4's CI-availability check fired correctly**: on the synthetic change-table (built to
    mimic the real file's shape metric list exactly), `peak_has_ci=False` and `ramp_has_ci=False`
    were both correctly detected, confirming the guard logic works before it is trusted on the
    real 250-row file.

## Decisions (things the task doc left to this employee, and what was assumed)

1. **FINDING -- the task doc's assumption for figure 4 is only partly true.** Section 2 item 3
   says "Peak demand, load factor, ramp, with CIs ... from `enduse_change_2022_2030.csv`'s
   `ci_low_pct`/`ci_high_pct` columns". Reading the real file (see Verified above) shows this file
   only ever carries a `stock_weighted` CI row for the 8 end-use energy meters (percent change)
   and for `midday_share`/`load_factor` (absolute-fraction change) -- **never for
   `peak_kW_annual` or any ramp metric**, confirmed both by reading
   `T68_scripts/enduse_hour_corrected.py`'s own change-table loop (`for metric in ("midday_share",
   "load_factor")` -- that is the entire list of shape metrics it ever scores) and by loading the
   real 250-row file and listing every `metric` with a `stock_weighted` row. Ruling 3 forbids
   recomputing a CI, so figure 4 does NOT invent one for peak/ramp. Instead: **load factor gets
   its real bootstrapped CI (reused verbatim, unchanged, labelled `QUOTABLE`)**; **peak and ramp
   get 2022-vs-2030 point values only, drawn with a hatched fill and an explicit "(no CI
   computed)" subtitle**, visually and textually distinct from the load-factor panel, per ruling 4
   ("never silently drop or plot [a non-evaluable value] as if it were solid"). The underlying CSV
   (`fig04_peak_loadfactor_ramp_ci.csv`) marks peak/ramp's `status` column
   `"NOT_EVALUABLE (no CI in accepted WP6 output)"` explicitly, never blank.
2. **The `point_change_pct`/`ci_low_pct`/`ci_high_pct` column NAMES for `midday_share`/
   `load_factor` say "pct" but the real units are an absolute fraction-point delta** (`change_type
   == "absolute_fraction"`), e.g. `0.0049` means +0.49 percentage points of load factor, not
   "0.49%". The script reads `change_type` at runtime and asserts it equals `"absolute_fraction"`
   before trusting the value (a hard `assert`, not a silent cast), and labels figure 4's axis
   "fraction (0-1)" / "absolute fraction points", never "%", for this one panel.
3. **Figure 2's per-end-use bar chart is split into two panels** rather than one 8-bar chart on a
   single axis: Panel A shows the stock-weighted WHOLE-BUILDING annual kWh for all 8 end uses
   (always well-defined, no divisor needed); Panel B shows the stock-weighted PER-DWELLING annual
   kWh for equip+lights only (the only two end uses with a derived unit divisor from T66). This is
   the literal reading of ruling 3's own instruction ("only equip/lights get a per-dwelling
   report... everything else reports whole-building or percent-change only") -- whole-building was
   chosen over percent-change for panel A because it is directly comparable across all 8 meters on
   one axis and needs no additional derivation, whereas percent-change would have required reading
   from a second file (`enduse_change_2022_2030.csv`) for a chart whose whole point is the absolute
   annual-energy picture.
4. **Figure 3 plots year 2030 only, all four scenarios**, not 2022-vs-2030 per scenario. The three
   T69 arms (S-None/S-Partial/S-Revert-std) exist specifically as alternate 2030 work-from-home/
   population-mix assumptions layered on the same 2022 baseline (T69 IMPL doc, decision 5/Verified
   section: all three arms share T21's identical 2022 tree) -- so "one line per scenario" reads
   most naturally as "how does the 2030 load shape differ under four different 2030 assumptions",
   not as four separate 2022-vs-2030 comparisons (which would need 8 lines and defeat the point of
   a scenario comparison). **Weekday** was chosen as the task doc's own suggested day type
   (section 2 item 2: "pick weekday, state which day type explicitly"). `season="all"` (whole-year
   weekday average) was used rather than a single season, since no single season was specified and
   an annual average is the least arbitrary default for a headline scenario-comparison figure.
5. **Figure 3's household-count control is COMPUTED, not copied from
   `cross_scenario_common_basis.csv`** (which only stores counts, not the actual household-ID
   list needed for row-level filtering). The script independently builds the four-way intersection
   of `(arch, city, sim_hh_id)` from each arm's own `enduse_annual.csv` (year 2030 rows) and
   asserts/logs whether it matches the file's already-ACCEPTED 1198. This is the figure's own
   "seen-working"-style check for its household basis, separate from ruling 1's own instruction
   to print the count. **If the real run's computed count does not equal 1198, `run_meta.json`'s
   `notes` array will say so explicitly -- the manager must read this before trusting figure 3's
   caption n.**
6. **Figure 5 uses `season="all", daytype="all"`** (the whole-year, all-day-types average diurnal
   pattern) rather than restricting to one season or day type, because the task doc does not
   specify either for this figure and an unrestricted annual average is the least arbitrary choice
   for what the brief itself calls "the figure most likely to be the paper's new headline result" --
   a single reviewer-facing summary, not a season- or day-type-specific claim. This is a genuinely
   new aggregation (no existing file precomputes end-use x hour percent change), so it carries
   **no confidence interval** -- ruling 3 (no result number without CSV traceability) is satisfied
   because every plotted cell is directly traceable to a stock-weighted mean of raw `load_kW`
   values in `enduse_hourly_profile.csv`, but no significance claim is attached. The figure's own
   title, caption text baked into `run_meta.json`'s per-figure note, and the CSV's `status` column
   all say explicitly "POINT ESTIMATE ONLY, no CI at this granularity, not a quotable change claim
   on its own" -- this distinction (point estimate vs. the project's official CI-backed `QUOTABLE`
   status) is deliberately never blurred, since a later WP10 rewrite pass could otherwise mistake
   this heatmap for a quotable per-cell change.
7. **PNG chosen over PDF** for all four figures: PNG lets the saved file's dpi be read back
   mechanically via Pillow (`Image.open(path).info["dpi"]`) and checked against the ≥600 dpi bar
   without a second rendering step; a vector PDF has no equivalent embedded-and-checkable dpi
   field (its "resolution" only exists once rasterized for print), which would have made ruling 2's
   "confirm the actual saved dpi... do not just assert the kwarg" harder to satisfy mechanically.
8. **7-inch nominal figure width** was used as the print-width default (a common single-figure
   double-column journal width; Applied Energy's own template was not read for an exact number,
   so this is a reasonable default, not a verified house-style value) -- `bbox_inches="tight"`
   then trims to the actual content bounding box, so final saved widths range 6.94-7.79 inches
   across the four figures (all still ≥600 dpi at that width, so the print-DPI bar is met
   regardless of the small width variation).
9. **Figure 5's meter list is all 8 categories from figure 2** (facility total + 7 components/
   remainder), not just the 7 non-facility components. Facility is kept as its own heatmap row
   because it is a legitimate, informative aggregate row (the whole-building total's own diurnal
   percent-change pattern), not a duplicate of any other row -- dropping it would have been an
   uninstructed scope cut the task doc did not ask for (ruling 1: "do not add panels... beyond
   what's listed", read here as also meaning do not silently remove one of the 8 meters the task
   doc's own figure-2 list already names).

## Next

- Manager collection, in the same fixed order T68/T69 used: read `run_meta.json`'s
  `seen_working_control` FIRST (both the hourly-profile cell match and the change-table cell hand
  value), then `figure_03_household_basis`/`figure_04_ci_availability`/`notes` (these carry the
  two findings above -- confirm they read the same on the real data as on the synthetic test),
  then the four PNG/CSV pairs themselves.
- If figure 3's computed household count does NOT equal 1198 on the real run, that is a new,
  real finding needing its own diagnosis before the figure's caption `n` can be trusted -- do not
  round it or silently substitute the file's 1198.
- scp the four PNGs + four CSVs + `run_meta.json` back to `impl/T71_out/` for manager/author
  viewing without a further cluster round-trip (not yet done as of this write -- job was still
  running when this doc was written; a follow-up scp is needed once the job completes, either by
  the manager at collection or a short dispatched step).

## WHAT I DID NOT VERIFY

- **Any number produced by the actual cluster job (`1341185`) on the real T68/T69 data.**
  Everything in `## Verified` above about the script's correctness comes from direct reconnaissance
  of the real (small) files, a synthetic local functional test, and `py_compile` -- not from this
  job's real output. `out/figures/run_meta.json` and all eight PNG/CSV deliverables are unread as
  of writing this doc.
- Whether the real job completes within a reasonable time or hits a memory/walltime issue. The
  script performs roughly six full-or-chunked reads of ~500 MB hourly-profile files across the
  four figures (one non-chunked full read in `seen_working_control`, one chunked read per arm in
  figure 3 x4, one more chunked read of T68's file in figure 5) -- expected to finish in a few
  minutes given T68/T69's own heavier per-household-file jobs finished in 2-4 minutes, but this is
  an expectation, not a measurement of THIS job.
- Whether the real four-way common household count for figure 3 actually equals 1198 when computed
  by this script's own logic (vs. simply trusting `cross_scenario_common_basis.csv`) -- the
  synthetic test proved the CHECK fires, not that the real numbers will match (they should, since
  both use the same underlying `enduse_annual.csv` files, but this is unread).
- Whether any real end-use x hour cell in figure 5 hits the zero-2022-denominator guard (unlikely
  for stock-weighted aggregates across 1200 households, but not measured -- the guard exists and
  was proven to fire correctly on engineered synthetic zero-value data during an earlier design
  pass of this same guard pattern in T68, not re-engineered into this synthetic test specifically).
- Whether `bbox_inches="tight"` ever crops a figure below the intended 7-inch print width in a way
  that matters for the journal's actual house style (not verified against Applied Energy's own
  figure guidelines, which were not read for this task).

## Manager collection (2026-09-21)

Fixed order followed: `run_meta.json` first (`seen_working_control`, then the two findings' real
values), then the four PNG/CSV pairs, then an independent cross-check done from scratch -- never
reusing the employee's own code path.

- `sacct -j 1341185 -X`: COMPLETED, exit 0:0, 54s -- consistent with T68/T69's own runtimes on
  similar file sizes.
- `run_meta.json`: `seen_working_control.hourly_profile_cell.match = true` and the change-table
  hand-read matches figure 4's own read. **Independently re-verified from a completely separate
  code path** (not trusting the employee's self-report):
  - Grepped `T68/out/enduse_hourly_profile.csv` directly (household 32811, `Electricity:Facility`,
    `all/weekday`, year 2030, hour 17) and got `1.2460543510412319` -- matches the reported
    `1.246054351041232` to float precision.
  - Downloaded `T68/out/enduse_change_2022_2030.csv` and parsed it with a real CSV reader (not
    `awk`, which mis-splits this file's one free-text column with an embedded comma -- the same
    trap T68's own collection already flagged) -- the `stock_weighted`/`load_factor` row read back
    `point_change_pct=0.004943184695576`, `ci_low=0.0041284557418345`, `ci_high=0.005743231074777`,
    `change_type=absolute_fraction` -- exact match, both sides.
  **Both control values reproduce exactly on a fresh, independent read. Control fires clean.**
- **Figure 3 household basis**: `run_meta.json` shows the script's own independently-computed
  four-way intersection = 1198, matching `cross_scenario_common_basis.csv`'s already-accepted
  count exactly (`matches_expected: true`). Per-arm sizes (1200/1198/1200/1199) match items 30/33
  exactly, same numbers this project has now reproduced independently three times (T69, T71).
- **Figure 4 CI-availability finding CONFIRMED real, not a bug**: `enduse_change_2022_2030.csv`
  genuinely carries a `stock_weighted` CI row for only 10 metrics (the 8 energy meters plus
  `midday_share`/`load_factor`) -- `peak_kW_annual` and ramp never got one. This is a real gap in
  what T68's own script was ever asked to bootstrap, not an error in T71. Figure 4 correctly shows
  peak/ramp as hatched, explicitly labelled "no CI computed," visually distinct from load factor's
  solid bar with a real error bar -- confirmed by eye on the actual PNG.
- **All four PNGs visually inspected** (not just file-existence-checked):
  - Figure 2: two-panel bar chart, whole-building all 8 end uses + per-dwelling equip/lights only,
    axis labels correct, 2022 vs 2030 bars nearly overlapping (small percent changes, expected).
  - Figure 3: four scenario lines over 24 hours, correctly showing S-Revert-std with a flatter
    midday (people staying home) and a higher evening peak than S-Full/S-None/S-Partial -- the
    expected work-from-home signature, a sensible and informative result.
  - Figure 4: three panels, peak/ramp hatched grey with "no CI computed," load factor solid with a
    visible error bar -- exactly the required visual distinction, confirmed by eye.
  - Figure 5: heatmap, 8 end uses x 24 hours, sensible pattern (lights/equipment strongly negative
    overnight and positive midday, matching a shift toward daytime occupancy). Checked the CSV
    directly: **0 of 192 cells are `NOT_EVALUABLE`** -- all real stock-weighted means, none hidden
    or silently dropped, consistent with 1200-household stock-weighting making a zero-denominator
    hit very unlikely.
- All eight files (4 PNG + 4 CSV) plus `run_meta.json` present on the cluster, non-empty, sizes
  match `run_meta.json`'s reported pixel dimensions; scp'd back to `impl/T71_out/` for viewing.
  dpi read back via Pillow at 599.9988 on every figure -- confirmed a harmless PNG pixels-per-metre
  rounding artifact (600 dpi to 4 decimal places), not a real shortfall.
- Decisions 1-9 reviewed: all well-reasoned, correctly grounded in what the real files actually
  contain rather than what the task brief assumed. No re-litigation needed; Decision 1 (figure 4's
  peak/ramp handling) and Decision 2 (fraction-vs-percent column-name mismatch) are genuine, useful
  findings that should be carried into the WP10 manuscript rewrite so the same mismatch is not
  reintroduced in prose.

**Verdict: T71 ACCEPTED, full controls-first verification complete, including two independent
from-scratch cross-checks of the seen-working control (not merely re-reading the employee's own
numbers) and a direct visual inspection of all four figures.** WP11's four T68/T69-derived figures
are done. Remaining WP11 work: Figure 7 (plot T70's numbers -- data ready, no figure yet), Figure 6
(blocked on T30), Figures 1/8/9 (need path confirmation).
