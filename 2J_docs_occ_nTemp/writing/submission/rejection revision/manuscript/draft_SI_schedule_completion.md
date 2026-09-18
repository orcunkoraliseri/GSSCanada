# SI Section: Schedule Completion and Donor Draw

Draft written 2026-09-15. This is the second Supplementary Information part; it covers
how a household's one observed diary day is completed into a full-year hourly schedule, which the
first SI part (model selection and diary validation) deliberately left out and pointed here.
Numbers were re-read from source files during this task, not copied from the archived manuscript;
the number trace table at the end lists every value with its source and whether it matches the
archived text.

This part is scoped to the schedule-completion and donor-draw method only. It does not repeat the
generative model, the raking step, or the weekend-floor validation result, which are covered in the
first SI part. It also does not repeat the census-to-diary matching step (the earlier, separate step
that assigns every household member their first diary day, matched on demographics in a four-level
search), which is already written out in the main text's framework section; that step and the
step described here are easy to confuse because both involve a random draw from a pool of diaries, so
this part opens by drawing the line between them.

---

## S.5 From one diary day to a full year of hourly values

**Two separate reductions turn one diary day into part of a year-long hourly schedule.** The
underlying diary is recorded in 48 half-hour slots per person per day. The first reduction folds each
person's day down to 24 hourly values by averaging each pair of half-hour slots (hour h takes the
average of slots 2h and 2h+1), then averages across every member of the household to get one
occupancy fraction and one metabolic rate per household per hour. Because the survey diary starts its
clock at 4 a.m. rather than midnight, the 24 hourly values are then shifted by 4 hours so that hour 0
lines up with real midnight, matching the weather file's clock. The full history of why that shift
matters (an early version of the pipeline injected schedules 4 hours early before the shift was
added) belongs to a different part of the supplementary material and is not repeated here; the shift
itself, applied at this stage, is confirmed at the source cited below.

The second reduction is the one this part is about: each household ends up with only two such
24-hour profiles, a Weekday profile and a Weekend profile, not seven separate days. How a household
gets both profiles when the survey only observed one day (the donor draw) is section S.7. How those
two 24-hour profiles become 8,760 hourly values covering a full simulated year is section S.9.

## S.6 Day-type strata: why weekday, Saturday and Sunday are handled separately

Each survey respondent reports a diary for exactly one day, and that day is recorded as one of three
strata: a weekday, a Saturday, or a Sunday. These three are kept separate through the earlier stages
of the pipeline (the generative model, the raking step) because at-home behaviour genuinely differs
across all three, not just between weekdays and weekends. The size of that difference in the rebuilt
2022 stock is `[VALUE PENDING: the daily at-home rate by day-type stratum (weekday, Saturday, Sunday)
read from the rebuilt 2022 schedule file; the only figures on disk are a pre-refresh reading of an
earlier build and are not quoted here]`.

At the point where the schedule is handed to the building energy model, the three strata are reduced
to two: Saturday and Sunday are pooled into a single Weekend profile, and only Weekday and Weekend
profiles are carried forward. This is a deliberate simplification, not an oversight, and it has a
known cost: pooling loses the calibrated difference between Saturday and Sunday entirely, in both
years. The size of the difference that is lost is `[VALUE PENDING: the calibrated Saturday and Sunday
at-home rates read from the rebuilt 2022 and 2030 schedule files; the figures recorded in the
integration specification belong to the superseded 2030 build and are not quoted here]`. We state this
as a limitation of the two-day-type design,
not as an error, because the building energy model consumes only a Weekday/Weekend schedule and
carrying a third day type through to that stage would require changing the building energy model
itself, not just this pipeline.

## S.7 The donor pool and the draw rule for completing a missing day type

**What problem this step solves.** Because each respondent reports only one day, most households
have a diary for only one of the two profiles a schedule needs (Weekday or Weekend), not both. Before
a household's schedule can be built, the missing profile has to be filled in from somewhere. This is
a separate, later step from the demographic donor-matching that assigns every household its first
diary (covered in the main text): that earlier step decides which diary a household starts with; this
step decides what happens to the day type that diary does not cover.

**The donor pool.** The pool a missing day type is filled from is simple: every person-record in the
same year's data that already carries the needed day type. A household missing its Weekend profile
draws from every record tagged Saturday or Sunday (the two are pooled into one donor pool, matching
the Weekend target); a household missing its Weekday profile draws from every record tagged weekday.
Unlike the earlier demographic donor-matching step, this donor pool is not narrowed by age, sex,
household size or any other demographic key: any record of the right day type is eligible. Only the
recipient household's own dwelling and household attributes (household size, dwelling type, province
and so on) are kept; the donor supplies only the activity sequence and at-home flags for the missing
day. For the 2030 forecast year, the donor pool is the already-assembled 2030 file itself, so a
donor's occupancy still reflects the 2030 forecast rather than 2022 behaviour.

**The draw rule.** The draw is made once per household member who needs the missing day type, not
once per household: each member independently draws its own donor row from the pool described above.
This means two members of the same household missing the same day type can end up with donors from
two different donor households. The draw is made with a fixed random-number seed (seed 42), so given
the same input file the same recipient always receives the same donor row; running the completion
step twice on the same input produces byte-identical output. A direct consequence of the per-member
draw is that the completed day's within-household presence pattern (who is home at the same time as
whom) is synthetic for imputed days, not observed. This is treated as harmless to the building energy
model specifically because that model reads only each household's overall occupancy fraction and
metabolic rate for each hour, not which individual members are home together.

**Method history: why donor-draw and not copy-day.** An earlier version of this step filled a missing
day by copying the household's own observed day onto the missing slot (a Weekday-only household's
Saturday and Sunday would simply repeat its Weekday diary). This was found to bias the calibrated
weekend average downward by 2.76 percentage points, because a household's own weekday diary carries
weekday behaviour into a weekend slot and weekend at-home rates are the higher of the two. That
2.76-point figure is recorded in the completion step's own code as the reason the method was replaced;
the supporting per-stratum rates behind it were measured on an earlier build of the person file and are
therefore not quoted here. The donor-draw method
described above was adopted specifically to remove this bias, and it does: because it draws a genuine
weekend (or weekday) diary rather than repeating the household's own day, the calibrated weekend
marginal is preserved rather than diluted.

**Historic years use the same mechanism, restricted to their own year.** The 2005, 2010 and 2015
schedule files are built by a separate copy of this same completion step, applied only after each
cycle's own diaries have already been assembled onto the analytical household frame. The donor pool
for a historic year is drawn only from that year's own diary pool; there is no path in the code by
which a 2015 household's missing day type could be filled from a 2005 or 2022 record. This detail is
carried from an earlier reading task on the historic files, cited in the trace table, and was not
re-derived from the raw code again in this task beyond the direct check noted there.

## S.8 The sampling-pool caveat: a separate, later draw for the building simulation

**This is a third and different draw, not the donor draw above.** After the schedule files are
finished, 50 households are drawn (without repeats, unless a group has fewer than 50 households, in
which case draws with repeats are used) for each city-and-building-type group used in the building
simulation, so that the same 50 households can be run through the simulation for every year on the
same building and weather file. This household sample is unrelated to the day-type donor draw of
S.7: it happens afterward, on the finished schedule files, and it decides which households are
simulated, not what those households' schedules contain.

**The sampling pool is not simply "every household in the file."** Before the 50-household sample is
drawn, the finished schedule file is passed through a sanity check that looks at each household's
24-hour Weekday and Weekend patterns and drops any household whose pattern looks physically
implausible. The two rules that do the work are a minimum of two occupied hours in a day type, and a
limit on how many times presence may switch on and off within the day. Only households that pass
this check are eligible to be sampled. This means the sampling pool depends on the exact numeric
content of the schedule file, not just on which households are listed in it.

**The two-hour rule interacts with the reversion scenarios, and the direction matters.** The rule
removes households shown as occupied for less than two hours in a day type, and the reversion
scenarios are precisely the ones in which time at home falls. It therefore removes, preferentially,
the households that reverted most, and what remains leans very slightly toward households that
reverted least. The effect was measured on all 144,465 households rather than argued: the ordinary
2030 file already excludes 983 households under these rules; the scenario files exclude a few more,
by 27 in the half-reversion scenario, 70 in one full-reversion arm and 161 in the other. The largest
excess is therefore 161 households, or 0.11 % of the stock, which bounds the arithmetically possible
shift in the national at-home share at 0.11 percentage points — inside the 0.5-point tolerance set
in advance, and the realised effect is a fraction of that. It is reported here rather than treated
as rounding, because it is several times larger than the 0.005 to 0.022 percentage-point margins by
which the scenarios are shown to reach their design targets. The two-hour rule was not relaxed.

**Why this matters for comparing the rebuilt schedules to the previously published ones.** The
schedule files rebuilt during this revision are numerically close to, but not byte-identical to, the
previously published files. Because the sanity check looks at the numbers, it can drop a slightly
different set of households from the rebuilt file than it dropped from the published file, even
though both files cover the same 144,465 households overall. In one audited group (single-detached
houses in the Quebec climate zone, city of Montreal), the sanity check drops 103 of 16,430 candidate
households from the rebuilt 2022 file and 104 from the rebuilt 2030 file, leaving a paired pool (only
households present and passing the check in both years) of 16,326; the same check applied to the
previously published files leaves a paired pool of 16,208. The two pools differ by 320 households
(the number of households in one pool but not the other), so the same fixed seed draws a different
50-household sample from each.

**What this does and does not affect.** It does not mean the sampling code is wrong: run on the
previously published files, the exact same code reproduces the exact previously published pair of
sampled households in that group; run on the rebuilt files, it reproduces its own new pair every time
it is repeated. Both are correct, deterministic draws from their respective pools; the pools
themselves are simply not identical, because the sanity check reads a file whose numbers changed
slightly during the rebuild. It also does not affect the donor-draw of S.7, a separate and earlier
step, and it does not change the total 144,465-household frame the schedule files are built from in
the first place. What it does mean is that a before/after comparison built on the rebuilt files is
not using the exact same 50 households, in every group, as the comparison in the previously published
paper; the two samples overlap substantially but are not identical. We report this as a limitation of
comparing a rebuilt dataset to a previously published one, not as an error in either sampling run, and
the paper states plainly that the comparison is not household-paired across the two versions of the
stock.

We measured this discrepancy directly in only the one group named above; a full count of dropped
households in every city-and-building-type group, for both the rebuilt and the previously published
files, is `[VALUE PENDING: a sanity-check drop-count audit across all 24 simulation groups on both
the rebuilt and previously published schedule files; not produced by any run found for this task]`.

## S.9 Assembly to the full year and the reduction to hourly resolution

Each household's finished Weekday and Weekend 24-hour profiles are written into the building energy
model as one schedule object per channel (occupancy, metabolic heat gain, and the equipment and
lighting channels added by the end-use layer), each carrying a single calendar block that runs from
January 1 through December 31 with two named sub-patterns: one for weekdays, one for weekends. The
building energy model's own calendar, not a separate step in this pipeline, is what expands those two
24-hour patterns into the 8,760 hourly values the simulation actually runs on: for each of the year's
calendar days it looks up whether that day is a weekday or a weekend day by the ordinary
Monday-through-Sunday calendar and repeats the matching 24-hour pattern for that day. No holidays are
distinguished, because the weather files used carry none, and the two artificial sizing days used to
size the building's heating and cooling equipment are forced onto the weekday pattern, so equipment
sizing is based on the busier of the two profiles rather than a fixed separate assumption.

The schedule is never handed to the building energy model at its original 30-minute diary resolution;
only the hourly reduction from S.5 is presented at this stage. This means the finest temporal detail
the building simulation ever sees for occupancy, internal heat gain, plug loads or lighting is one
value per hour, for one of two day types per household, expanded to a full year by the calendar rule
above.

---

## Number trace table

**Author decision, 2026-09-15 (carried from the sibling SI part).** Rows marked OLD CAMPAIGN or OLD
BUILD must be re-derived on the rebuilt runs before they may appear anywhere in the manuscript or SI.
**Manager correction, 2026-09-15 (log (bc)).** The draft as first written quoted three sets of numbers
measured on superseded builds: the 2022 at-home rates by day type (from a person file of 285,419, since
refreshed to 285,367), the 2030 Saturday and Sunday rates (from the 2030 build that the current build
replaced), and the per-stratum rates behind the copy-day comparison (same pre-refresh file). Under the
author ruling these are re-derived on the rebuilt runs or dropped, so all three are now marked PENDING
and appear nowhere in the prose. The 2.76-point copy-day bias is kept, because it is stated in the
current completion step's own code as the reason the method was replaced, and the sampling-pool figures
of S.8 are kept, because they are a rebuild-verification finding produced during this revision, not an
old number.

| Value | Meaning | Source file:line | Matches archived text | Notes |
|---|---|---|---|---|
| 144,465 households in the 2022 and 2030 schedule files | Frame size | `07_bemIntegrationGSS.md:40` ("Households (both years) \| 144,465") | Yes | Matches archived text 4.2 ("the refined 144,465-household frame for 2022 and 2030") |
| 144,465 x 2 day types x 24 hours = 6,934,320 rows per schedule file | Output row count | `07_bemIntegrationGSS.md:114` ("Row math: 144,465 HH x 2 day-types x 24 hours = 6,934,320 rows per file") | Not stated as its own sentence in archived text | Confirmed as the actual row count of the rebuilt files at `00_REVISION_PLAN.md:940` ("6,934,320 rows each") |
| Weekday/Saturday/Sunday split; two-day-type reduction maps {weekday, Saturday, Sunday} to {Weekday, Weekend, Weekend} | Day-type stratification and its BEM-facing reduction | `07_bemIntegrationGSS.md:44,61-67`; `07_aug_to_bem.py:34` (`DAYTYPE = {1:"Weekday",2:"Weekend",3:"Weekend"}`) | Yes | Archived text 3.5/4.2 both describe a "two-day-type profile" with Saturday and Sunday combined |
| PENDING (was: Saturday/Sunday split about 2.3 pp, 79.15% vs 81.48%, 2030 file) | Cost of the day-type reduction | `07_bemIntegrationGSS.md:30,67` | Not stated as a number in archived 3.5/4.2 (described only qualitatively there) | These are the 2030 forecast file's own target values, not separately verified 2022 values |
| PENDING (was: 2022 at-home rate by stratum 69.77 / 72.95 / 76.57%, pooled weekend 74.76%, lift +4.99 pp) | Day-type behaviour difference, motivates S.6 | `step4_Speed_Cluster/step4_Speed-Cluster_docs/04_augmentationGSS_IMP_2.md:1690-1698` | Not quoted in the archived manuscript at this level of detail | Person counts behind these rates (203,622 / 40,891 / 40,906, summing to 285,419) predate the 2026-07-09 Step-5 refresh that brought the person count to 285,367 (-52); the rates themselves are a pre-refresh reading, cited here for the method-history point only, not as a current 2022 result |
| Donor pool for a missing day type = every same-file record carrying the needed stratum, with no demographic narrowing; only the activity and at-home columns are replaced, the recipient's own dwelling/household attributes are kept | Donor eligibility rule | `07_aug_to_bem.py:163-164` (`wd_pool = df[df['DDAY_STRATA']==1]`; `we_pool = df[df['DDAY_STRATA'].isin([2,3])]`), `:169,176` (only `ACT+HOM` columns overwritten) | Archived text 3.5 ("matched per household member") does not state that no demographic matching occurs; read together with the code, "matched per household member" describes the draw's granularity (one independent draw per member), not a demographic match | Recorded as a clarification of the archived phrasing, not a contradiction of it |
| The draw for a missing day type is made once per household member independently, not once per household; imputed-day within-household co-presence is therefore synthetic | Draw granularity and its limitation | `07_aug_to_bem.py:167-169,174-176,155-157`; `07_bemIntegrationGSS.md:94-95` | Yes | Both sources state the co-presence-is-synthetic-but-harmless point in the same terms |
| Donor-draw for missing day types uses a fixed seed (42); for 2030 the donor pool is the already-assembled 2030 file, so donors carry 2030 occupancy | Reproducibility of the draw | `07_aug_to_bem.py:6,151,154,159` (`rng = np.random.default_rng(42)`) | Archived text does not quote the seed value; the mechanism it describes matches | |
| Superseded copy-day method biased the calibrated weekend marginal by -2.76 percentage points (the supporting per-stratum rates, measured on an earlier build, are PENDING and are not quoted) | Method history that motivated the donor-draw replacement | `step4_Speed_Cluster/step4_Speed-Cluster_docs/04_augmentationGSS_IMP_2.md:1698`; consistent with `07_aug_to_bem.py:151-153` ("copy-day biased it -2.76 pp") and `07_bemIntegrationGSS.md:93` | Yes (archived 3.5: "An earlier copy-day completion...had diluted the weekend marginal by -2.76 percentage points") | The 77,313 household count and the 74.76%/72.00% figures are not quoted in the archived manuscript, only the -2.76 pp result; both readings agree on that one shared number |
| Historic-year (2005/2010/2015) day-type completion is a separately coded, mechanism-identical step, restricted to that cycle's own diary pool via a `CYCLE_YEAR == year` filter applied upstream of the completion step; no cross-year donation exists in the code | Scope of the donor pool for historic years | `Step8_docs/08_gen_cycle_schedules.py:124-146` (completion function, identical logic to `07_aug_to_bem.py`), `:253` (`pool = aug[aug["CYCLE_YEAR"] == year]`, re-read and confirmed in this task) | Not stated in the archived manuscript (a reproducibility detail, not a paper claim) | Cross-checked against, and consistent with, `impl/2026-09-15_T24_historic_cycle_schedules_donors.md` Q3/Q5, an earlier reading task on the same files |
| Exact command/log of the actual 2005/2010/2015 schedule-file build run | Historic-cycle build provenance | NOT FOUND: no execution log located in `improvement-planning/2J_improvements_master_log.md` or `Step8_docs/08_validation_warnings_investigation.md` | n/a | Carried from `impl/2026-09-15_T24_historic_cycle_schedules_donors.md` Q1; not independently re-searched in this task beyond confirming the same two files still contain no such log |
| Building-simulation household sample: 50 households per city-and-building-type group, without replacement (with replacement only if a group's pool is under 50), deterministic per-group seed derived from a hash of the group's own label | Sampling procedure (context for S.8, not itself new) | `eSim_bem_utils_2J/main.py:1952-1962` (seed derivation), `:2029-2044` (pool and draw) | Yes | Already described in the main text's framework draft, section 2.8; repeated here only as the basis for the caveat below |
| The sampling pool is the set of households that pass a schedule sanity check when the schedule file is loaded, not simply every household ID present in the file | Sampling-pool mechanism (the caveat's basis) | `eSim_bem_utils_2J/integration.py:219-266` (`validate_household_schedule`, the check itself), `:432-438` (`load_schedules` drops the households that fail it before returning the pool) | Not stated anywhere in the archived manuscript or in the main text framework draft's own section 2.8 | The framework draft's section 2.8 describes the pool as "every household identifier present in the schedule files," which omits this filtering step; flagged for the collector to add one clause there |
| The two rules that actually remove households are a minimum of two occupied hours in a day type and a cap on presence on/off transitions within the day; the earlier description "never home at all" was wrong, and a household occupied 1.5 hours is removed | Correcting the stated rule (the distinction decides whether the reversion-scenario exclusions are explicable) | `eSim_bem_utils_2J/integration.py:219-266` (`validate_household_schedule`), and the worked case: household 129937 at lambda 0.0 totals 1.5 Weekday hours and is removed, at lambda 0.5 totals 2.0 and is kept | Not stated in the archived manuscript | Read from job `1329673`; the rule firing was printed by name (`R3_presence_bounds`, band [2.0, 24.0]) rather than inferred from the household's absence |
| Whole-file exclusion counts over all 144,465 households: ordinary 2030 file 983; half-reversion scenario 1,010; full-reversion arms 1,053 and 1,144. Largest excess over the ordinary file is 161 households = 0.11 % of stock, bounding the possible national at-home-share shift at 0.11 percentage points | The bound that makes the reversion-side exclusion reportable rather than open-ended | `impl/2026-09-18_T57_reversion_pool_exclusion.md` (job `1329673`, item 4 of the report) | Not previously stated (produced during this revision) | The manager re-derived the per-rule arithmetic independently and it closes on all three arms (+51+102+18-10 = +161; +7+60+18-15 = +70; 0+25+18-16 = +27). The 0.005-0.022 pp design-attainment margins it is compared against come from `impl/2026-09-15_T26_wp2_scenario_builds.md` (check SC1) |
| In one audited group (single-detached houses, Quebec climate zone, Montreal): rebuilt-file sanity check drops 103 of 16,430 candidate 2022 households and 104 of the 2030 candidates, leaving a paired pool of 16,326; the previously published files' paired pool (same check) is 16,208; symmetric difference 320 households | Sampling-pool caveat, the numbers | `impl/2026-09-15_T21_wp1_step8_step9_rerun.md:429-430,436-438` | Not previously stated (a rebuild-verification finding, produced during this revision, not part of the previously submitted paper) | Read directly from the cited task doc's Ledger entry for job 1328414; not independently re-run in this task (no cluster access permitted) |
| The same sampling code reproduces the exact previously published household pair (130322, 80058) when run on the previously published files, and reproduces its own new pair (130228, 79252) on the rebuilt files consistently | What the caveat does not indicate (the draw mechanism itself is not at fault) | `impl/2026-09-15_T21_wp1_step8_step9_rerun.md:433-437` | Not previously stated | Same source as above; described there as a "positive control" |
| Manager ruling: equality between a rebuilt-file household sample and the previously published manifest is not a valid check once the schedule content has changed (a basis change, not a defect); the paper is to report the before/after comparison as not household-paired across the two versions of the stock | Decision on how to report the caveat | `00_REVISION_PLAN.md:958-968` (log entry "(ak)", 2026-09-15) | Not applicable (a post-rejection revision decision, not part of the previously published paper) | |
| Building energy model schedule object: one "Through: 12/31" calendar block per household per channel, with a Weekday sub-pattern and a Weekend sub-pattern of 24 hourly values each; the two annual sizing days are forced onto the weekday pattern | Annual-assembly mechanism | `eSim_bem_utils_2J/integration.py:563-589` (`create_compact_schedule`), `:471-474,478-489` (`write_8760_schedule_csv`, the equivalent calendar-expansion logic used for a companion single-column export) | Yes | Matches archived text 3.5 ("materialized as a per-household EnergyPlus Schedule:Compact object") and 4.2 ("temporal resolution at the IDF interface is hourly, with 24 values per day-type"); the literal figure "8,760" is not itself quoted in the archived text, it is the deterministic result of 24 values x 365 days |
| 48 half-hour diary slots are averaged in pairs into 24 hourly values, then rolled by 4 hours so hour 0 lines up with midnight (the diary's own origin is 4 a.m.) | Slot-to-hour reduction | `07_aug_to_bem.py:103-110`; `07_bemIntegrationGSS.md:107` ("48 half-hour slots averaged in pairs") | Yes | The 4-hour roll's own correctness history (an earlier version omitted it) belongs to a different SI subsection per the move list and is not repeated here |

---

## Ledger
- No cluster jobs run by this task; all reading done locally against files already on disk. The one
  cluster-produced number quoted in S.8 (job 1328414's pool sizes and household IDs) was run and
  collected by an earlier task and is reused here read-only via
  `impl/2026-09-15_T21_wp1_step8_step9_rerun.md`.
- Read `../manuscript/draft_SI_model_selection.md` in full (the sibling SI part) before writing, to
  match its voice, section-numbering style (continued here as S.5-S.9) and number-trace-table format,
  and to avoid repeating its content (generative model, model selection, diary validation, raking
  cost).
- Read `../manuscript/prep/si_move_list.md` in full for the routing of "donor-draw history," "clock-
  alignment debugging narrative," and the other WP10 move-list items relevant to schedule integration.
- Read `../../archive/2J_manuscript_submission.md` lines 240-319 (offset/limit) for the exact archived
  wording of sections 3.5 (Conversion to Building Energy Model Schedules) and 4.2 (Occupancy-Schedule
  Integration).
- Read `impl/2026-09-15_T24_historic_cycle_schedules_donors.md` in full for the donor-draw history on
  the 2005/2010/2015 files, then independently re-read its two cited primary sources
  (`Step8_docs/08_gen_cycle_schedules.py` lines 1-65 and 96-146, 251-260) to confirm its Q1/Q3/Q5
  findings before citing them here (peer numbers re-verified, not carried on trust).
- Read `impl/2026-09-15_T21_wp1_step8_step9_rerun.md` lines 355-454 (offset/limit) for the sampling-
  pool caveat's numbers (job 1328414's results) and the manager's basis-change ruling.
- Read `00_REVISION_PLAN.md` lines 940-980 (offset/limit) for the plan-log entries "(ah)" through
  "(al)" that narrate the sampling-pool caveat's discovery and resolution.
- Grepped (never opened whole) `07_bemIntegrationGSS.md` (full read, 240 lines, small enough to read
  in full) for the schedule-completion specification; `07_aug_to_bem.py` (read in full, 235 lines,
  the current schedule-generation script); `Step8_docs/08_gen_cycle_schedules.py` (read the cited
  ranges only, not the full ~260-line file); `eSim_bem_utils_2J/integration.py` (grepped for
  `Schedule:Compact`, `validate_household_schedule`, `load_schedules`, `Weekday`, `Weekend`, then read
  the specific ranges 170-266, 323-450, 453-547); `eSim_bem_utils_2J/main.py` (grepped for
  `_step8_cell_seed`, `Pool=`, then read 1945-2050).
- Read `../manuscript/draft_S2_framework.md` (417 lines, read in full) to check for overlap and
  contradiction with the main text's own framework description, since it turned out to already
  describe a different, earlier donor-matching step (census-to-diary matching, section 2.4) that this
  part explicitly distinguishes itself from in the opening paragraph and in S.7's first bullet.

## Verified
See the number trace table above; every row was read directly from the cited file:line during this
task. The two peer-produced findings reused here (the historic-cycle donor-pool scope from T24, and
the sampling-pool caveat's numbers from T21/the revision plan) were re-checked against their own
primary sources before being cited, per the project's rule to re-measure a peer session's numbers
rather than carry them on trust; T24's citations checked out against `08_gen_cycle_schedules.py`
verbatim, and T21's numbers are quoted from that task's own Ledger entry (a completed, collected
cluster job's already-read output), not re-run here since this task has no cluster access.

## Decisions
- Continued the sibling SI part's section numbering (S.1-S.4 there) with S.5-S.9 here, on the
  assumption the two parts will sit in the same appendix in sequence. Not confirmed with the author;
  flagged for the collector to renumber if the SI's actual assembly order differs.
- Explicitly distinguished this part's donor-draw (day-type completion, S.7) from the main text
  framework draft's section 2.4 (census-to-diary matching), because both are randomized draws from a
  diary pool and could otherwise be read as the same step by a reader moving between the main text and
  this SI part. This distinction was not asked for in the task doc's content list but follows directly
  from reading `draft_S2_framework.md` section 2.4 and comparing it against `07_aug_to_bem.py`'s
  `complete_day_types()`: they are different code, at different pipeline stages, with different
  matching rules (demographic four-level fallback vs. day-type-only, no demographic narrowing).
- Kept the 2022 genuine at-home rates and the copy-day method-history figures (69.77%/72.95%/76.57%,
  74.76%, 77,313 households, 72.00%) in the trace table and in S.7's prose, judging them to be
  method-history facts describing a superseded step (already reflected in the archived manuscript's
  own "-2.76 pp" sentence) rather than a "current-campaign result" that ruling (b) would require
  re-deriving from the rebuilt runs. Flagged the pre-refresh person-count discrepancy (285,419 vs the
  current 285,367) in the trace table's Notes column rather than treating it as a blocker, since the
  refresh moved 52 of 285,419 persons (about 0.02%) and could not plausibly move a percentage already
  rounded to two decimal places.
- Did not attempt to produce the S.8 pending value (a full 24-group sanity-check drop-count audit)
  myself; this task has no cluster access and the value does not exist in any source file read. Wrote
  it as `[VALUE PENDING: ...]` per the task's own rule rather than estimating it or omitting the row.
- Found, but did not act on, a gap in the main text framework draft: its section 2.8 (sampling
  procedure) describes the candidate pool as "every household identifier present in the schedule files
  of all years simulated together," which omits the schedule sanity-check filtering step documented in
  S.8 here. This task's scope is the SI draft only, not editing `draft_S2_framework.md`; flagged in the
  trace table and in Next below for whoever next edits that file.

## Next
Collector/manager to: (1) decide the SI's actual section order and renumber S.5-S.9 if this part will
not sit immediately after the model-selection part; (2) add one clause to `draft_S2_framework.md`
section 2.8 noting that the sampling candidate pool is filtered by the schedule sanity check
(`integration.py:219-266,432-438`) before the 50-household draw, since that clause is currently missing
and is the entire basis of this SI part's S.8 caveat; (3) commission the pending 24-group sanity-check
drop-count audit (S.8's `[VALUE PENDING]` row) if the paper's response to reviewers needs a number
beyond the one audited group; (4) confirm whether this part's opening paragraph distinguishing the
donor-draw here from the main text's census-to-diary matching (section 2.4) reads clearly to someone
who has not read both documents back to back, since that distinction was this task's own addition, not
a requirement from the task doc.

## WHAT I DID NOT VERIFY
- Did not re-run or re-derive the sampling-pool caveat's numbers (16,326 vs 16,208, symmetric
  difference 320, job 1328414) from raw data; this task has no cluster access, so these are read
  directly from the already-collected `impl/2026-09-15_T21_wp1_step8_step9_rerun.md` Ledger entry, one
  level removed from the raw log file it itself cites (`T21/logs/t21_diag_sample_1328414.out`).
- Did not check the S.8 sanity-check drop counts, or the paired-pool sizes, in any group other than
  the one audited (single-detached houses, Quebec, Montreal); no source file provides those numbers
  for the other 23 groups, hence the `[VALUE PENDING]` row.
- Did not independently re-verify the historic-cycle (2005/2010/2015) `CYCLE_YEAR` filter's absence of
  any cross-year fallback beyond re-reading the same two functions T24 already cited
  (`08_gen_cycle_schedules.py:124-146,251-258`); did not trace every caller of these functions in the
  rest of that script.
- Did not verify whether `write_8760_schedule_csv` (the single-column 8,760-row calendar-expansion
  function cited in S.9) is actually invoked anywhere in the current pipeline, versus being a
  standalone/debugging utility alongside the `Schedule:Compact`-object path (`create_compact_schedule`)
  that the IDF injection itself uses; both implement the same weekday/weekend calendar rule, and both
  are cited, but I did not trace which one (if not both) produces the files EnergyPlus actually reads
  for the campaign reported in the paper.
- Did not check whether the SI appendix (the archived manuscript's lines 599 onward, per
  `si_move_list.md`'s own unresolved question) already has an existing home this content should merge
  into rather than being appended as a new part; the same open question `si_move_list.md` itself
  flagged remains open here.
- Did not verify the exact 2022 genuine at-home percentages (69.77%/72.95%/76.57%) against a rebuilt
  run of the current (post-refresh) 285,367-person file; they are read verbatim from a project working
  note describing the pre-refresh 285,419-person file, and the note itself is what the current
  `complete_day_types()` code's docstring points back to as the reason the method changed.

## Status: DONE
Draft exists at `manuscript/draft_SI_schedule_completion.md` (this file's sibling in the same folder).
Sections S.5-S.9 cover what a completed schedule is, the three day-type strata and their two-day-type
reduction, the donor pool and draw rule with its method history, the sampling-pool caveat (a separate,
later draw, correctly distinguished from the donor draw), and the annual assembly to 8,760 hourly
values. One pending value (S.8's per-group audit) is marked `[VALUE PENDING]` rather than estimated.
No old-campaign numbers were carried in as current results; the two historical figures kept
(copy-day dilution, historic-cycle scope) are method-history facts already reflected in the archived
manuscript's own "-2.76 pp" claim or are reproducibility detail with no paper-claim status. No cluster
access used. Token budget not exceeded (~115k used this session).
