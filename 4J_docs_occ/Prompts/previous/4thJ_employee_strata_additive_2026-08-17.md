# Employee task — the conditioning strata: read them, harmonise them, and move nothing else

**Role: employee.** You execute. You do not choose bands, you do not choose thresholds, and 🔴 **you
never move a threshold or adjust a perturbation because something fails.** A failure is a result.
Where this document tells you to **stop and report**, stop — the step after it is a manager decision
and taking it yourself is the defect this round exists to avoid.

**Governing decision: D-S2-18**, in `4J_docs_occ/Step2_docs/4thJ_02_harmonisation.md`, last section.
Read it in full before anything else. Then **M-8** at the end of
`4J_docs_occ/Step1_docs/4thJ_01_corpusAcquisition.md`, and the record contract **D-S2-12**.

---

## WHY THIS ROUND EXISTS, IN FOUR LINES

Step 3 serialises each diary as a **nine-field conditioning prefix** plus the episode tuple:
`country, age band, sex, household type, economic status, day type, season, MODE, SCHEME`.

`harmonised.parquet` supplies **three** of the nine — `country`, `mode`, `scheme`. The other six do
not exist in it, and four of them do not exist in the Step 1 parquets either. **Step 5's argument for
training without design weights depends on the prefix containing the design strata**, so they cannot
be dropped to make the problem go away.

---

## 🔴 CLUSTER RULES — VIOLATING THESE COSTS THE ACCOUNT

* **`sbatch` only.** Never a blocking `srun`. **Never bare `python`/`python3` on the login node, not
  even a one-liner.** Flagged three times already; a fourth is suspension.
* Every job: `-t 7-00:00:00`, partition `ps`, CPU only.
* Login node allows only `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, and single-file `tail`/`head`/`grep`/`wc -l`/`cat`.
* tcsh login shell: **no `2>&1` in ssh commands**, no bash `while ... done` loops. **One `sacct` call,
  not a poll loop** — the first poller on this project was killed by exactly that mistake.
* Speed interpreter `/speed-scratch/o_iseri/envs/step4/bin/python`; locally `py`.

**Where things are on the cluster:** raw trees at `/speed-scratch/o_iseri/4J/raw/{spain,italy,uk}`,
already md5-verified after transfer. Step 1's accepted outputs are the run-stamped directory
**`Step1_docs/outputs_step1/run_20260816-2210`** — 🔴 **never a stale copy from an earlier run.**

---

# TASK A — TRANSCRIBE, THEN **STOP**

## A1. The six strata, per country, from that country's own codebook

For **each** of Spain, Italy and the UK, and **each** of the six strata below, establish from the
delivery's own documentation:

| Stratum | What you are looking for |
|---|---|
| **age** | the respondent's age or age band, and its exact band boundaries if banded |
| **sex** | the respondent's sex and its value labels |
| **household type** | the composition of the household the respondent lives in |
| **economic status** | employed / unemployed / student / retired / other, in the delivery's own words |
| **day type** | what kind of day the diary covers (weekday, Saturday, Sunday, …) |
| **season** | the month, quarter or season of fieldwork for that diary |

**Record for each:** variable name, the file it lives in, its complete value list with the delivery's
own labels, the grain it is delivered at (person, household, diary-day), and 🔴 **the document and
page or sheet number it came from.** That is the standard every fact in `codebook_facts_<country>.md`
already meets and this round does not lower it.

🔴 **A stratum that does not exist in a delivery is written `NOT FOUND` and stays that way.** Do not
substitute a proxy, do not derive it from another country, and **do not take a variable name from
`RL02` or `RL17`** — both have been caught inventing variable names on this project, and the
co-presence and location fields they were confident about were wrong three times out of four.

**Already carried in the Step 1 parquets, so start there and confirm rather than hunt:** Spain `EDAD`,
`SEXO`, `HRELACTIV`, `trim`; Italy `sesso`, `claseta2`, `meseri`; the UK `DVAge`, `DMSex`,
`DiaryDay_Act`. 🔴 **Household type is carried by no country** — the delivered household files are
Spain's `DHOGAR` / `MHOGAR`, the UK's `uktus15_household.tab`, Italy's `Individui.txt` at `profam`
grain, and **no round has read any of them.**

🔴 **Italy's `claseta2` must be transcribed band by band, all eleven.** It is the binding constraint on
the whole age classification and D-S2-13 already turned on one of its boundaries.

## A2. Propose the harmonised band set — **propose, do not build**

For each stratum, propose the target band set that all three countries will map into, and for each
proposed band give the source values it is built from in each country.

**Three rules bound the proposal, and they are not yours to trade off:**

1. 🔴 **A stratum that any one country cannot supply is dropped from the prefix for ALL countries** —
   never emitted by two and blanked for the third, never given an `unknown` only one country uses. A
   symbol only one country can emit is a country marker, and a country marker inside a
   leave-one-country-out design measures our bookkeeping rather than transfer. **If you reach this
   case, say so and stop; the manager decides what is dropped.**
2. 🔴 **Every target band must be expressible in every country's delivery, and Italy binds.** Italy
   ships age pre-banded, so **every target age band must be a union of whole `claseta2` bands.** A
   target band that splits an Italian band cannot be produced from the Italian file — and would be
   produced anyway, wrongly. Same rule for any other stratum Italy delivers pre-banded.
3. 🔴 **A band that only one of the three countries would emit is a defect in the proposal**, and the
   repair is to coarsen the band, never to keep it and note it. `G2.18 (a)` will fail it later; catch
   it here, where it costs nothing.

**Row-level missingness is different from country-level absence.** Where a country fields the variable
but an individual record is missing it, the value maps to an **`unknown`** band that
`crosswalk_strata.csv` declares **for all three countries**. Report `unknown`'s expected prevalence per
country per stratum in the proposal — 🔴 **if it is heavily concentrated in one country, that is a
finding for the manager, not a detail to absorb.**

## A3. 🛑 STOP HERE

**Deliverables of Task A**, all under `Step1_docs/outputs_step1/`:

* `codebook_facts_<country>_strata.md`, three files, fully cited.
* `strata_proposal.md` — the proposed band set per stratum, the per-country source values for every
  band, the expected `unknown` prevalence, and **every case where a rule above bites.**

**Then message the manager (`main`) and wait.** Do not write a reader, do not write a crosswalk, do
not submit a job. **The band set is a manager decision** — a classification chosen by the person
implementing it, against the data in front of them, is chosen to be easy to produce.

---

# TASK B — BUILD. THE BAND SET IS APPROVED (D-S2-19, 2026-08-17)

🔴 **Task A is done and the manager has ruled. Build exactly the band set below and nothing else.** The
ruling is `D-S2-19` at the end of `Step2_docs/4thJ_02_harmonisation.md` — **read it before you start**;
this section is a summary of it and the doc governs where they differ.

**`season` is DROPPED from the prefix for all three countries.** Spain's `TRIM` and Italy's `meseri`
are each delivered pre-banded, offset by one month at every edge, share no boundary, and neither
country ships anything finer, so no non-trivial band is expressible in all three. 🔴 **You still build
`strat_season_raw`. You do not build `strat_season`, and `crosswalk_strata.csv` has no `season` rows.**

**The five harmonised strata, approved:**

| Column | Bands |
|---|---|
| `strat_age_band` | `11-14, 15-24, 25-34, 35-44, 45-54, 55-64, 65-74, 75+` — Italy's populated `claseta2` bands; Spain's `EDAD` and the UK's `DVAge` are exact ages |
| `strat_sex` | `male, female` — Spain's `SEXO=6` is female |
| `strat_day_type` | `weekday, saturday, sunday` — 🔴 **the UK source is `ddayw`, not `DiaryDay_Act`** |
| `strat_econ_status` | `employed, unemployed, student, retired, homemaker, other_inactive, unknown` |
| `strat_hh_type` | `one_person, couple_no_children, couple_with_children, single_parent_with_children, other_complex, unknown` — 🔴 **no band splits on child age**; Italy's `tipfa2m` carries no age qualifier |

Per-country source values are in `strata_proposal.md`. **`unknown` is declared for all three countries
in the crosswalk even where its observed prevalence is zero** — that is what makes it not a country
marker under `G2.18 (a)` as amended.

🔴 **One thing Task A left open and you must not close by folding.** Italy's `tipfa2m` codes
`12, 13, 17, 18, 26, 27, 31, 32` are **not enumerated in CLS-var16**. If any of them is observed in
the raw file, **the run FAILs and the code is registered in `crosswalk_unmapped.md` with a reason.**
It is never folded into `other_complex` because that is where an unrecognised code looks like it
belongs. Report their observed frequencies either way.

**Two limitations to carry in your fragment, not to repair:** UK `dhhtype = 3` cannot separate a
childless couple from a couple whose children are all 16+ (F-UK-18), where Spain's `TIPOHOG` separates
`2` from `4`; and UK `deconact = -1` maps to `unknown` on the generic "not applicable" reading, which
is an assumption, not an established fact.

## B1. The three Step 1 readers carry the national values, unbanded

Extend `tools/4thJ_read_{spain,italy,uk}.py` to emit one column per stratum holding **the delivery's
own value** — no mapping, no banding, no collapsing. Column names
`strat_<name>_raw`: `strat_age_band_raw`, `strat_sex_raw`, `strat_hh_type_raw`,
`strat_econ_status_raw`, `strat_day_type_raw`, `strat_season_raw`.

Household type requires **joining the household file** to the diary rows on that country's own key.
🔴 **A join that matches nothing must FAIL loudly, not produce nulls** — per D-S2-16, the number of
distinct join keys that matched must be non-zero for every country and the reader refuses otherwise.
This is the exact failure that would have made every Step 2 gate pass vacuously last night.

**All six are person- or diary-day-level constants** repeated on every episode of that diary. They are
not episode properties.

## B2. Re-run Step 1 and prove nothing moved

Three `sbatch` jobs, one per country, **never chained**, then the sixteen-gate battery on all three.

🔴 **Acceptance: every count and every gate verdict identical to `run_20260816-2210`.** Episodes
ES 430,754 / UK 587,632 / IT 1,077,657. **Italy's `G1.6b` must still FAIL and the UK's `G1.4` must
still FAIL.** A round that quietly repairs a known FAIL has stopped reading the thing it audits and is
thrown away rather than accepted. Adding columns may not move a row.

## B3. `crosswalk_strata.csv`

One shipped file in `Step2_docs/outputs_step2/`, the fifth crosswalk, built like the other four:

`stratum, country, source_value, source_label, target_band, citation`

Every row cited to a page or sheet. Every source value either mapped or registered in
`crosswalk_unmapped.md` with a reason. 🔴 **The `unknown` band is declared for all three countries or
for none.**

## B4. The harmoniser emits the five harmonised columns

Extend `tools/4thJ_harmonise_step2.py`: read the crosswalk, emit `strat_age_band`, `strat_sex`,
`strat_hh_type`, `strat_econ_status`, `strat_day_type` beside the **six** `_raw` carriers —
`strat_season_raw` ships without a harmonised partner (D-S2-19). **Eleven new columns, 40 → 51.**

🔴 **Lowercase `country` on read and assert every crosswalk join matched** (D-S2-16). The parquet holds
`ES`/`UK`/`IT` and the crosswalks hold `es`/`uk`/`it`.

🔴 **The `_raw` columns stay in the shipped table.** A transform that discards its inputs cannot be
audited — the same reason `act_raw`, `act2_raw` and `loc_raw` ride along. They are **not** serialised
into the prefix; that is Step 3's decision and not yours.

## B5. Re-run work item 2.4 and prove nothing moved

🔴 **The acceptance test is four fixed numbers, and it is not negotiable:**

| | ES | UK | IT |
|---|---|---|---|
| **episodes** | **446,547** | **567,381** | **1,010,140** |
| **splits** | **37,830** | **0** | **0** |

Total **2,024,068 rows, 51 columns.** Every diary still tiles `[0, 1440)` exactly once, all 73,254 of
them. `act2` nulls still **587**. The only column containing `origin` is still `split_at_origin`.

**A rebuild that moves one episode means the column set is entangled with the transform, and the whole
delivery goes back.** That is exactly what the UK's four-column re-run tested and passed on
2026-08-16.

**Age floor stays 11** (D-S2-13, confirmed by the author 2026-08-17). It is a runner parameter with no
default; pass it explicitly.

---

## 🔴 ACCEPTANCE TESTS — state each one explicitly in your report

1. Every stratum fact carries a document and page or sheet citation, or reads `NOT FOUND`.
2. Task A stopped and waited for the manager. The band set you built is the one that was approved.
3. Step 1 re-run: all counts and all sixteen gate verdicts unchanged, **including both standing
   FAILs.**
4. Step 2 re-run: the four fixed numbers above reproduced exactly, 51 columns, 73,254 diaries tiling.
5. Every crosswalk join asserted non-zero matched keys per country.
6. **No threshold moved, no gate edited, no perturbation adjusted.** Say this in terms, or say exactly
   what you changed and why. Silence here is not acceptable.

## DELIVERABLES

`codebook_facts_<country>_strata.md` ×3, `strata_proposal.md`, the three updated readers, the updated
harmoniser, `crosswalk_strata.csv`, the rebuilt `harmonised.parquet`, and Progress Log **fragments**
at `outputs_step1/proglog_strata_step1.md` and `outputs_step2/proglog_strata_step2.md` for the manager
to merge. **They are fragments, not the Progress Logs themselves.**

Each fragment ends with a section headed **WHAT I DID NOT VERIFY.**

🔴 **Report anything this document did not decide for you, and say plainly what you assumed.** Three of
the four new Step 2 decisions came from an employee stopping on something odd instead of coding around
it. That is the behaviour being asked for here.
