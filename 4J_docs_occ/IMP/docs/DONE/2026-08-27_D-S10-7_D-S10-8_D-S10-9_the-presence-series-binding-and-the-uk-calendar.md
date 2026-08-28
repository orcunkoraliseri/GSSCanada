# `D-S10-7` / `D-S10-8` / `D-S10-9` — THE PRESENCE-SERIES BINDING, AND A `uk` CALENDAR CONFLICT NEITHER SIDE HAD NOTICED

**Opened:** 2026-08-27 (night) · **Status:** 🔴 THREE DECISIONS OPEN, none takeable here — each is a NEW RULE
**Raised by:** the OpenUBEM European Locations director, in
`messages_OpenUBEM/2026-08-27_OpenUBEM_to_4J_EU-06_f-gt-0_presence_binding_request.md` (9,069 bytes, delivered 21:13)
**Blocks:** the 408 `f > 0` cells of `EU-06`/`EU-08`, and therefore `EU-09`/`EU-10` and Step 10 items 10.3 / 10.5 / 10.6 / 10.7 / 10.8
**Does not block:** the 102 `f = 0` controls, Step 11's `f = 0` half (closed at 95/95 on the promoted `S3` artefacts), or anything already promoted

---

## 0. What changed, in one paragraph

The `EU-08` ask of 2026-08-27 was **answered and accepted**: OpenUBEM agrees that §9.4 makes `EU-08`
the **loop and not the engine**, and the per-cell entry point `run_campaign_cell` is **queued on their
side**. They have also read the four artefacts of the `10.1` chaining-closure notice and **accept all
four**; decision 14 is not reopened and `eu_campaign_cell_spec_v1.0.json` will **not** be amended —
the `f > 0` lift is carried by reference, exactly as we asked. 🔴 **So the chaining rule is no longer
the blocker.** What blocks the 408 now is that **the frozen spec carries no pointer to a presence
series** — no `presence_path`, no `schedule_id`, no bundle name on any of the 510 rows — so there is
no ruled statement of which `g(t)` drives which cell. That is a **composition** question, which §9.4
makes **ours**. ⚪ And while preparing that letter they found a **calendar-year defect** in our Step 7
bundles. One half of it is a clean mechanical fix. **The other half is not a defect at all — it is a
conflict between their frozen EPW pin and our own `D-S10-1` ruling, and it is the reason this document
exists.**

---

## 1. What was verified here before anything was accepted — measured, not reasoned about

🔴 **Every factual claim in their letter was re-derived read-only on this machine. All of them hold.**

### 1.1 The archetype-to-household arithmetic — CONFIRMED

`eu_campaign_cell_spec_v1.0.json`, counting `survey_fold` over all 510 rows: `es` **120**, `uk` **180**,
`it` **210**; each fold's five `sensitivity_f` levels are `102 / 102 / 102 / 102 / 102`. Dividing by
the five levels gives **`es` 24 · `uk` 36 · `it` 42 = 102 archetypes**, which is their figure exactly.

Each Step 7 bundle ships **100** household series (`n_households: 100`, verified in all six
`manifest.json`). 🔴 **There is no natural one-to-one map — 102 archetypes against 100 series — and
one must not be invented on either side.** This is `D-S10-8` below.

⚪ **Do not confuse this population with our own.** The 4J Step 8 injected campaign is **88** archetype
cells (`es` 24 · `uk` 32 · `it` 32) after the `4a`/`4b` rulings. The spec's is **102**. Two different
campaigns; the difference of 14 is real and must be crossed deliberately, never silently.

### 1.2 The bundle calendars — CONFIRMED, and one of them is stale

Read from the six `Step7_docs/outputs_step7/schedules/leg5_*/manifest.json`. Every bundle is
`independent`, `rho 0.0`, `seed 1`, `timestep_min 60`, `rotated_to_midnight true`,
`diary_origin_hour 4`, `n_values_per_schedule_expected 8760`, `n_households 100` — identical in
every respect but `year`:

| fold | bundles that exist on disk | calendar years |
|---|---|---|
| `es` | `leg5_es_independent_seed1`, `…_cal2010` | 2017, **2010** |
| `it` | `leg5_it_independent_seed1`, `…_cal2013` | 2017, **2013** |
| `uk` | `leg5_uk_independent_seed1`, `…_cal2014` | 2017, **2014** |

### 1.3 The pinned EPWs — CONFIRMED, hashes matched byte-for-byte

The three `weather_sha256` values carried in the frozen spec were recomputed from the files on disk
and **all three match exactly**:

| fold | pinned `epw_path` (`RULED_PINNED_EXCEPTION`) | `weather_sha256` in `v1.0` | recomputed | EPW `DATA PERIODS` |
|---|---|---|---|---|
| `es` | `es_madrid_2009_2010_y2010.epw` | `d2563b7d…a17346d` | 🟢 match | `Friday,1/1,12/31` → **2010** |
| `it` | `it_bologna_2013_2014_y2014.epw` | `ab631c60…97e25fa` | 🟢 match | `Wednesday,1/1,12/31` → **2014** |
| `uk` | `uk_london_2014_2015_y2015.epw` | `379d1010…d04f745` | 🟢 match | `Thursday,1/1,12/31` → **2015** |

🔴 **The `yYYYY` suffix is not a label — it is the real calendar.** Each EPW is a full single calendar
year `1/1`–`12/31` whose start day-of-week is the true one for that year (1 Jan 2010 = Friday,
1 Jan 2014 = Wednesday, 1 Jan 2015 = Thursday). So the day-type structure of the weather file is
determinate, and a presence array on a different year's calendar **does** land weekends on weekdays.
Their §2 argument is correct on the physics.

### 1.4 🔴 The fact their letter did not have: **the alternative EPWs already exist on disk**

`openubem/data/weather/` also contains, written the same day as the pinned ones:

| file | `DATA PERIODS` | hash |
|---|---|---|
| `uk_london_2014_2015_y2014.epw` | `Wednesday,1/1,12/31` → **2014** | sha256 `7b7d9524d6667d79572a3453b7ece531a6b2717dd496aaa239ec925fbce6e295` |
| `it_bologna_2013_2014_y2013.epw` | `Tuesday,1/1,12/31` → **2013** | md5 `4a3f274d9a1fbe9bbaafdb586e3cbe92` |
| `es_madrid_2009_2010_y2009.epw` | `Thursday,1/1,12/31` → **2009** | md5 `38c46d2880919816e667d892711734c1` |

⚪ **This matters to the cost of every option below.** Repinning `uk` to its 2014 EPW requires **no
acquisition and no new data** — the file is present and hashed. It requires only a `v1.1` of the cell
spec, because `weather_sha256` is carried **per cell** and would move on all 180 `uk` rows.

---

## 2. `D-S10-7` — 🔴 THE `uk` CONFLICT. THIS IS THE ONE THAT IS NOT A DEFECT.

### 2.1 The three folds do not fail the same way

| fold | `D-S10-1` ruled year | pinned EPW calendar | our bundle calendar | verdict |
|---|---|---|---|---|
| `es` | **2010** | **2010** | **2010** | 🟢 all three agree — nothing to decide |
| `it` | **2014** | **2014** | **2013** | 🟡 our bundle is stale against **both** authorities → `D-S10-9`, mechanical |
| `uk` | **2014** | **2015** | **2014** | 🔴 **the frozen EPW pin and our own ruling disagree** |

🔴 **So OpenUBEM's `A2` ask is two different things wearing one label.** For `it` it is a genuine
stale artefact on our side and a one-command fix. For `uk` they ask us to emit `_cal2015` — which
would move the presence calendar **onto the EPW and off the year `D-S10-1` ruled**. That is not an
emission. **It is a reversal of a closed decision, and it must not happen by our quietly running a
script.**

### 2.2 What `D-S10-1` actually ruled, verbatim

`IMP/docs/DONE/2026-08-26_D-S10-1_the-weather-year-is-recoverable.md` §6, item 2:

> | **2** | `uk` Majority Case | 🟢 **Pin to 2014** | `uk` pinned to 2014 (58.1%) alongside `es` (2010) and `it` (2014). | Keeps a consistent single-year convention across all 3 folds, avoiding an asymmetric split design. |

⚪ The `uk` = 2014 pinning has since been **re-confirmed and not reopened** twice —
`Step8_docs/4thJ_08_bemSimulation.md:1650` and `DeepResearchPrompts/VETTING_RL27.md:104,156`, both on
the delivered `dyear` reading of **58.1 %** (`FINDING 175`, which also records that the fieldwork is
**April 2014 to December 2015 with an interruption**, September 2015 carrying zero diaries).

### 2.3 🔴 The question underneath the question, which the author must answer first

**Are the two "years" even the same quantity?**

* `D-S10-1`'s year is the year the **diaries** are taken to represent — an empirical majority read from
  the microdata (`uk` 58.1 % of diaries in 2014).
* A bundle's `_calYYYY` is the calendar the 8,760 values are **laid onto** — it fixes day-of-week
  structure and nothing else.

They coincided for `es` and `it`, so nothing ever forced the distinction. **If they are different
quantities**, aligning the bundle calendar to the EPW is bookkeeping and `D-S10-1` is untouched.
**If they are one quantity**, then the `uk` EPW pin — a `y2015` file for a fold ruled to 2014 — is
itself the defect, and it sits inside a **frozen** artefact. 🔴 **This reading is the decision. Everything
below follows from it and nothing below can be chosen without it.**

### 2.4 Options

| | option | what it costs | what it risks |
|---|---|---|---|
| **(a)** | **Emit `leg5_uk_independent_seed1_cal2015`.** Presence follows the frozen EPW; `D-S10-1` declared to govern the *diary* year only. | One bundle emission. No `v1.1`. No re-pin. Nothing already promoted moves. | 🔴 The manuscript must state, in the methods, that the bundle calendar and the ruled diary year are **different quantities** — otherwise a reader sees `uk` presence on 2015 against a paper that says `uk` = 2014 and reads a silent reversal. `D-S10-1`'s stated reason ("a consistent single-year convention across all 3 folds") no longer describes what runs. |
| **(b)** | **Hold `uk` at 2014 and ask them to repin the EPW to `uk_london_2014_2015_y2014.epw` in a `v1.1`.** | No new data — the file and its hash already exist (§1.4). But `weather_sha256` moves on **180** cells, so `v1.0`'s digest must survive beside a new `v1.1`, and they must open the request. The `uk` runs wait for it. `es` and `it` proceed meanwhile. | Slower. Introduces a second spec version into an arc that has been careful to keep exactly one. |
| **(c)** | **Run 2017 `RunPeriod`s on all three folds and repin every EPW.** Their own offered third route. | One `v1.1`, symmetric, uses the already-existing `year 2017` bundles unchanged — no emission at all. | 🔴 Discards the empirically-grounded majority-year convention `D-S10-1` chose on measured microdata, and replaces it with an arbitrary calendar. The weather would no longer be the weather the diarists lived through. |

### 2.5 Recommendation

⚪ **(b)**, and it is a recommendation and not a ruling. The reason is `D-S10-1`'s own stated rationale:
it did not pin `uk` to 2014 for convenience, it pinned it to keep one convention across three folds
against measured diary majorities. Option (a) keeps the *number* 2014 in the paper while running 2015,
which is the exact shape of defect this project has now filed three times (`V10.i`, `FINDING 176`,
`FINDING 157`). Option (b) costs one `v1.1` and no data, because §1.4's file already exists. 🔴 **But
(b) is only correct under the "one quantity" reading of §2.3, and that reading is the author's.**

---

## 3. `D-S10-8` — THE CELL → PRESENCE-SERIES BINDING FOR THE 408 (their `A1`)

### 3.1 What they need, and it is genuinely ours

§9.4 gives GSSCanada *"the five-level campaign matrix and run ordering"*. The spec's 510 rows carry
`archetype_id`, `epw_path`, `gain_csv_path`, `idf_path`, `manifest_path`, `sensitivity_f`,
`survey_fold`, `weather_*` — **and nothing that names a presence series.** Their emitter
(`openubem/semantic/european_schedules.py:38-40`) rejects any `presence` array that is not 8,760
values, and `:51-52` is a pure string gate on `chaining_rule` which `10.1` already discharges. So the
capability exists on both sides; **only the mapping is missing.**

### 3.2 The three things they ask us to file, and what each really is

1. 🔴 **The mapping itself** — for every `(survey_fold, archetype_id)`, which
   `presence_HH_<fold>_<hid>.csv` drives it, **or** the rule that generates it deterministically from
   the bundle (`hid` order? `mean_presence` order? stratum match?). **102 archetypes against 100
   series per fold.** This is a **new rule** and is `D-S10-8` proper. ⚪ Their acceptance test is that
   the mapping reproduces **bit-identically from the filed rule on a second machine**, which is the
   right test and costs us nothing extra if the rule is stated as a deterministic order.
2. ⚪ **Whether the four `f > 0` levels of one archetype share one series.** They assume **yes**, on
   the ground that `f` is the injection weight and a per-`f` redraw would confound the sweep with
   sampling noise. 🟢 **That reasoning is correct and matches how our own `f` grid was built** — but it
   is still a confirmation the author owes, one word.
3. 🔴 **The dwelling count per archetype cell.** The 510 are **archetype-only, with no footprint**,
   while their emitter writes one `Schedule:File` per dwelling **zone**. So: is a cell one dwelling on
   one household series, or `N` dwellings on `N` series — and if `N`, what fixes `N` for a row that
   carries no geometry? ⚪ This is the same question `G10.19` already answered negatively for `H10`
   (`es` 9 · `uk` 5 · `it` 3 against 30 per fold) and that `D-S11-1` §7.3(c) records as **26 dwellings
   in 12 buildings** — a population that is real but thin. **A cell that is one dwelling is the
   simplest answer and the one the spec's own shape suggests; it is not mine to declare.**

### 3.3 What is NOT open here

⚪ `G10.8` is scored **per dwelling**, against 4J's own assignment table, and **never** against
OpenUBEM's `held_out_country = null` (`Step10_docs/4thJ_10_ubemRealStock_val.md:47`,
`4thJ_10_ubemRealStock.md:531`). Whatever mapping is ruled, that scoring route does not move, and a
dwelling driven by the fold that held it out remains a **hard** failure.

---

## 4. `D-S10-9` — THE `it` BUNDLE AT `cal2013` (their `A2`, the uncontested half)

⚪ **This one has no conflict in it.** The pinned `it` EPW is calendar **2014** and `D-S10-1` ruled
`it` = **2014**; only our bundle sits at **2013**, and it is stale against **both** authorities. The
emitter `tools/4thJ_step7_schedules.py` takes `--year` (line 612, `required=True`), so the fix is one
invocation with `--year 2014` and every other flag identical to the `cal2013` run
(`--rule independent --rho 0.0 --seed 1 --timestep 60 --households 100`, rotation left on).

🔴 **Two constraints if it is authorised.** **(i)** The existing `leg5_it_independent_seed1_cal2013`
bundle is **left byte-identical** — additive labelling, a new directory beside it, never an overwrite;
its 102 files stay where they are. **(ii)** 2014 is not a leap year, so the **8,760** contract is
unaffected and `n_values_per_schedule_expected` must come out unchanged — 🔴 **and that must be seen,
not assumed**: the emission is not accepted until the new manifest is read back and shown to carry
`year 2014`, `n_values 8760`, `n_households 100`, `seed 1`, `rotated_to_midnight true`.

⚪ **Why this is filed as a decision at all, rather than just done.** It generates a promoted-adjacent
artefact that the 408 will be bound to. The author has ruled repeatedly that emission is not a
mechanical act when something downstream will cite it. **One word authorises it.**

---

## 5. Their `A3` — NOT A DECISION. This one is ours to just do, and mostly derivable.

MVP §9.5 requires 13 fields per shipped `g(t)`. Our bundle `manifest.json` already carries `fold`,
`rule`, `rho`, `seed`, `year`, `timestep_min`, `n_values_per_schedule_expected`,
`rotated_to_midnight`, `diary_origin_hour`, `n_households`, per-household `hid` / `n_members` /
`mean_presence`, and `pool.pool_md5` — **verified by dumping the key set of all six manifests.**
Their claim that five things are absent is **confirmed**: no `schedule_sha256`, no
`held_out_country`, no `diary_source_id`, no `timezone` / `local_time_basis`, no `start_timestamp` /
`end_timestamp`.

| field | status here |
|---|---|
| `schedule_sha256` | 🟢 **mechanical** — per series, not per pool; hash the 100 CSVs |
| `held_out_country` | 🟢 **derivable, not a ruling** — it **is** the fold (`tools/4thJ_step4_shards.py:489`, `4thJ_step4_diagnostics.py:538`, both `held_out_country = fold`). 🔴 Load-bearing: §9.5 makes the adapter **reject** a series naming the wrong fold, and `G8.16` was scored on exactly that check |
| `start_timestamp` / `end_timestamp` | 🟢 **mechanical** — determined by the bundle's own `year` |
| `diary_source_id` | 🟡 **a naming convention, one line** — the underlying deliveries are INE EET 2009-2010, UKDS SN 8128 UKTUS 2014-15, ISTAT *Uso del Tempo* 2013-2014; whether the id is the archive citation or an internal key is a convention we should set once and never vary |
| `timezone` / `local_time_basis` | 🟡 **one line, and it is not free.** `Europe/Madrid` / `Europe/London` / `Europe/Rome` are obvious, but `local_time_basis` interacts with `diary_origin_hour = 4` **and** `rotated_to_midnight = true`, which `FINDING 141` says must always be read **together**. Getting this wrong is a four-hour shift that no length check can see — the `D-S9-3` failure class |

⚪ **A per-bundle addendum JSON satisfies `A3`; the bundles need not be re-emitted.** That is their
own concession and it is the right one — re-emitting would move hashes for a labelling fix.

---

## 6. What the author is being asked to rule

| # | decision | the one line that closes it |
|---|---|---|
| **`D-S10-7`** | 🔴 The `uk` calendar authority. **First** answer §2.3: are the ruled diary year and the bundle calendar the **same quantity** or two? Then **(a)** emit `_cal2015` / **(b)** hold 2014 and ask for a `v1.1` repin (**recommended**) / **(c)** 2017 everywhere. | *"(b) — one quantity; ask them to repin `uk` to `y2014` in a `v1.1`."* |
| **`D-S10-8`** | 🔴 The cell → presence-series binding: the mapping rule for 102 archetypes over 100 series; confirm the four `f` levels share one series; and the dwelling count per archetype cell. | the mapping rule in one paragraph, plus *"yes, shared"* and *"one dwelling per cell"* or a named `N` |
| **`D-S10-9`** | 🟡 Emit `leg5_it_independent_seed1_cal2014` now, additively, leaving `cal2013` byte-identical? | *"yes"* |

⚪ **`A3` is not on this list and is not waiting on anyone** — it is ours, and §5 says which two of its
six fields need a one-line convention rather than a derivation.

---

## 7. What was NOT done, and why

⚪ **No bundle was emitted, no artefact regenerated, no gate scored, no band / threshold / verdict /
count moved, no job submitted — the Speed queue is EMPTY.** Nothing in the OpenUBEM tree was written.
`eu_campaign_cell_spec_v1.0.json` was **read only** and is untouched at md5
`15d3b7933803d8c8a5e1de78b0e28d67`. `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched.

🔴 **`D-S10-9` was deliberately not taken**, though it is the most tempting of the three, because it
writes an artefact the 408 will cite. 🔴 **`D-S10-7` (a) was deliberately not taken** even though it
is the option that requires no `v1.1` and no letter — because running a script would have reversed a
closed ruling silently, which is the failure this project has now filed three times.

⚪ **One thing was found here that their letter does not contain**: the `uk` y2014 and `it` y2013 EPWs
already exist on disk with verified hashes (§1.4). Their `A2` was written as though the choice were
between emitting a bundle and acquiring weather. It is not — which is why option (b) is cheap.

---

## 8. Evidence — every claim above, and where it came from

| claim | source, read-only |
|---|---|
| their letter, 9,069 bytes, delivered 21:13 | `OpenUBEM/docs/docs_ACTIVE/europeanLocations/messages_GSSCanada/2026-08-27_OpenUBEM_to_4J_EU-06_f-gt-0_presence_binding_request.md` |
| `es` 120 / `uk` 180 / `it` 210 rows; five `f` levels × 102 | `eu_campaign_cell_spec_v1.0.json`, `survey_fold` and `sensitivity_f` counted over all 510 |
| three pinned EPW paths and their `weather_sha256`, all three recomputed and matched | same file; `sha256sum` over `openubem/data/weather/` |
| EPW calendars are real single years with true start weekdays | `DATA PERIODS` header of each `.epw` |
| the `uk` y2014 / `it` y2013 / `es` y2009 alternatives exist | `ls` + `sha256sum`/`md5sum` of `openubem/data/weather/` |
| six bundles, their `year` values, and identical generation parameters | `Step7_docs/outputs_step7/schedules/leg5_*/manifest.json` |
| 100 households per bundle; 102 files per bundle directory | same manifests; `ls` + `wc -l` |
| `D-S10-1` item 2 pins `uk` = 2014 and its stated reason | `IMP/docs/DONE/2026-08-26_D-S10-1_the-weather-year-is-recoverable.md` §6 |
| `uk` = 2014 re-confirmed, not reopened | `Step8_docs/4thJ_08_bemSimulation.md:1650`; `DeepResearchPrompts/VETTING_RL27.md:104,156` |
| the emitter accepts `--year` | `tools/4thJ_step7_schedules.py:612` |
| `held_out_country` **is** the fold | `tools/4thJ_step4_shards.py:489`; `tools/4thJ_step4_diagnostics.py:538` |
| `G10.8` scored against 4J's table, never their null | `Step10_docs/4thJ_10_ubemRealStock_val.md:47`; `4thJ_10_ubemRealStock.md:531` |
| the five §9.5 fields genuinely absent from our manifests | key set dumped from all six `manifest.json` |

---

## 9. AUTHOR'S RULINGS & DIRECTIVES

| # | Question / Item | Ruling | Adopted Specification | Rationale & Directives |
|---|---|---|---|---|
| **1** | `D-S10-7` — `uk` calendar authority | 🟢 **Option (b)** | **Hold `uk` at 2014 (`D-S10-1`). Repin `uk` EPW to `uk_london_2014_2015_y2014.epw` in spec `v1.1`.** | The diary year and calendar year are the **same physical quantity**. 2014 is the ruled majority (58.1%) for UKTUS. The 2014 EPW and sha256 already exist on disk (§1.4), preserving 3-fold symmetry (`es` 2010, `it` 2014, `uk` 2014) at zero data cost. |
| **2** | `D-S10-8` — cell → presence-series binding | 🟢 **Approved** | **Deterministic rank-order mapping: Archetype $i$ (sorted by `archetype_id` within fold) maps to household $i$ (`hid` sorted). 1 dwelling per cell. The 5 levels of $f$ share the identical presence series.** | Strictly deterministic and bit-reproducible. In reality, per-fold archetype counts (`es` 24, `uk` 36, `it` 42) are all $< 100$, ensuring strict 1-to-1 uniqueness without wrapping. Shared series across $f$ prevents sampling noise confounding. |
| **3** | `D-S10-9` — `it` `cal2014` re-emission | 🟢 **Approved (YES)** | **Emit `leg5_it_independent_seed1_cal2014` additively.** | Resolves the stale `cal2013` artifact. Leaves existing `cal2013` intact on disk. Verified against 8,760 values, `year 2014`, `n_households 100`. |

### Formal Directives for OpenUBEM Interface & Campaign Spec:
1. **Spec Update (`v1.1`)**: Issue `eu_campaign_cell_spec_v1.1.json` updating the 180 `uk` rows to `uk_london_2014_2015_y2014.epw` (`weather_sha256: 7b7d9524d6667d79572a3453b7ece531a6b2717dd496aaa239ec925fbce6e295`), retaining `v1.0` alongside for audit trail.
2. **Metadata Addendum (`A3`)**: Emit per-bundle addenda JSON files supplying `schedule_sha256`, `held_out_country`, timestamps, standard timezones, and source IDs (`INE_EET_2009_2010`, `UKDS_SN8128_UKTUS_2014_2015`, `ISTAT_UDT_2013_2014`).
3. **Execution Clearance**: With these rulings, all 408 `f > 0` campaign cells of `EU-06`/`EU-08` are unblocked and authorized to run.

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` remains strictly frozen. Decisions `D-S10-7`, `D-S10-8`, and `D-S10-9` are formally resolved and closed.
