# VETTING — `RL27` (HETUS weighting rule · fieldwork calendars and AMY licensing · TABULA licence)

Vetted 2026-08-27 (night). Report: `RL27_hetus_weights_amy_weather_tabula_licence.md` (116 lines,
returned 2026-08-22). Prompt: `L27_hetus_weights_amy_weather_tabula_licence.md`.

🔴 **Why this was owed.** `RL27` has sat in `DeepResearchPrompts/` since 2026-08-22 **cited by no
document**, and the Step 8 weather card has carried *"`RL27` has never been vetted at all"* since
`D-S8-4`. One of its rows (`B12`) was falsified in passing on 2026-08-25 while choosing the weather
stations. This is the full pass.

⚪ **Method, and its one hard limit.** Every row that can be tested against an artefact **we already
hold** was tested against it — the three harmonised parquets, the raw deliveries under
`_local_runs/4J/raw/`, and the rulings already on the record. **No external document was fetched and
no DOI was resolved**: literature retrieval is external to this seat, so every row whose only
evidence is an external PDF is marked `UNVERIFIABLE HERE` rather than accepted or rejected. An
unverifiable row is not a refuted row, and it is not a confirmed one either.

---

## 1. Verdict table

| row | claim, in brief | verdict | on what evidence |
|---|---|---|---|
| `B1` | Eurostat 2008 guidelines recommend 5/7 weekday, 2/7 weekend | ⚪ **UNVERIFIABLE HERE** | external PDF; not fetched |
| `B2` | the guidelines are non-binding; NSIs are sovereign | ⚪ **UNVERIFIABLE HERE** | external PDF; not fetched |
| `B3` | 2000 / 2008 / 2018 editions carry identical guidance | ⚪ **UNVERIFIABLE HERE** | external PDFs; not fetched |
| `B4` | Spain: 50.00 / 25.00 / 25.00 weekday / Sat / Sun | 🟢 **NUMBER CONFIRMED**, 🔴 **COLUMN NAME WRONG** | measured **50.017 / 25.001 / 24.982** on `harmonised_es.parquet` |
| `B5` | UK: 71.43 / 14.29 / 14.29 | 🟢 **NUMBER CONFIRMED**, 🔴 **COLUMN NAME WRONG** | measured **71.446 / 14.316 / 14.238** on `harmonised_uk.parquet` |
| `B6` | Italy: 33.33 / 33.33 / 33.33 | 🟢 **NUMBER CONFIRMED**, 🔴 **COLUMN NAME WRONG** | measured **33.333 / 33.333 / 33.333** on `harmonised_it.parquet` |
| `B7` | Spain fieldwork 1 Oct 2009 – 30 Sep 2010, uniform | 🟢 **CONFIRMED** (window), 🟢 **SUPPORTED at quarter grain** (uniformity) | `D-S10-1`; quarter counts max/min **1.133** |
| `B8` | UK fieldwork Apr 2014 – Dec 2015, *continuous*, 12-month core May 2014 – Apr 2015 | 🟢 **span CONFIRMED**, 🔴 **"continuous" and the "12-month core" REFUTED** | month × year crosstab: **Sep 2015 = 0 diaries** |
| `B9` | Italy fieldwork 1 Nov 2013 – 31 Oct 2014, uniform over 4 quarters | 🟢 **CONFIRMED** (window), 🟢 **SUPPORTED at quarter grain** | `D-S10-1`; quarter counts max/min **1.112** |
| `B10` | ERA5 / Copernicus licence permits derived publication | ⚪ **UNVERIFIABLE HERE** | external licence page; not fetched |
| `B11` | commercial AMY vendors forbid raw redistribution | ⚪ **UNVERIFIABLE HERE** | external EULAs; not fetched |
| `B12` | TABULA reference stations are Madrid-Barajas / London Kew-Heathrow / Rome-Bologna | 🔴 **FALSIFIED** (2026-08-25, `D-S8-4`) | those three measure out as the **worst** ES candidate, a 2.8× worse English one and the **worst** IT one |
| `B13` | TABULA/EPISCOPE licence permits derived-table redistribution | ⚪ **UNVERIFIABLE HERE** | external project terms; not fetched |

**Tally: 4 confirmed, 3 confirmed-but-mislabelled, 1 part-refuted, 1 falsified, 5 unverifiable here.**
🔴 **`RL27` may not be cited as a whole.** Row by row or not at all.

---

## 2. `FINDING 174` — the percentages are right to two decimals and **all three column names are wrong**

Measured on our own artefacts, deduplicating to a diary key `(hid, pid, diary_day)` — the same key
`FINDING 53` had to be corrected onto:

| | weekday | saturday | sunday | `RL27` says | measured |
|---|---|---|---|---|---|
| `es` (19,140 diaries) | 50.017 | 25.001 | 24.982 | 50.00 / 25.00 / 25.00 | 🟢 agrees |
| `uk` (15,854) | 71.446 | 14.316 | 14.238 | 71.43 / 14.29 / 14.29 | 🟢 agrees |
| `it` (38,260) | 33.333 | 33.333 | 33.333 | 33.33 / 33.33 / 33.33 | 🟢 agrees |

🔴 **And every variable name it attaches to those numbers is absent from the delivery it names.**

| country | `RL27` names | the delivery actually carries | checked |
|---|---|---|---|
| ES | `FACTOR_ADULTOS` / `FACTOR_DIARIO` | **`FACTORF`** (and `FACTOR_hogar`) | both `RL27` names return **0 hits** anywhere under `raw/spain/` |
| UK | `ddaywgt` | **`dia_wt_a`** / `dia_wt_b` (fields 29–30 of `uktus15_diary_ep_long.tab`) | `ddaywgt` returns **0 hits** anywhere under `raw/uk/` |
| IT | `PESO` / `COEF_IND` | **`coefin`** (individual) / **`coefi2`** (diary) | `COEF_IND` returns **0 hits**; `PESO` occurs only in saved methodology prose, never in the tracciato |

⚪ **What that pattern means, and it is the useful part.** A report that reconstructed these designs
**from the microdata** would carry the microdata's names. `RL27` carries the *methodology prose's*
names and the *design targets'* values — so it is a faithful reading of the national methodology
reports and **not** a reading of the files. That is fine for what it claims and dangerous for what it
would be quoted for.

🔴 **Operative rule: never quote `RL27`'s variable names into the methods, the code or a data
statement.** The names in this project's own readers are the checkable ones. A methods sentence
naming `ddaywgt` would be unreproducible against SN 8128 as delivered.

⚪ **And the numbers are not new.** `FINDING 53` measured the same three splits on 2026-08-20 — two
days **before** `RL27` was written — as `uk` 71.45 / 14.32 / 14.24, `es` 50.02 / 25.00 / 24.98,
`it` 33.33 × 3, and `D-S6-4` had already ruled `weight_dia_cal` as the repair. **`RL27` therefore
confirms an existing measurement from the source side; it does not supply one.** What it does add,
and it is worth having, is the *reason* — `B1`+`B2`, that the calendar-week rule is a recommendation
and the NSIs are sovereign — and that reason is one of the five rows this seat cannot verify.

---

## 3. `FINDING 175` — UK fieldwork is **21 months with a hole in it**, and the report's "continuous" is refuted

Reconstructed by joining the harmonised month (`strat_season_raw`) to the delivered diary year from
the `D-S10-1` sidecar (`basis = exact: delivered dyear`), 15,854 of 15,854 diaries joined:

| month | 2014 | 2015 | | month | 2014 | 2015 |
|---|---|---|---|---|---|---|
| Jan | 0 | 1,336 | | Jul | 908 | 187 |
| Feb | 0 | 1,424 | | Aug | 1,209 | 7 |
| Mar | 0 | 1,273 | | **Sep** | 990 | **0** |
| Apr | 588 | 639 | | Oct | 1,165 | 756 |
| May | 1,067 | 167 | | Nov | 1,295 | 487 |
| Jun | 1,134 | 363 | | Dec | 857 | 2 |

🟢 **The span is exactly as `B8` says**: first diary April 2014, last December 2015.

🔴 **Two of its clauses are not.** (i) **Fieldwork is not continuous** — **September 2015 carries zero
diaries** while October and November 2015 carry 1,243 between them, so there is a gap inside the
span, not a taper at its end. (ii) **The "12-consecutive-month core" does not exist in the data.**
Under either candidate window `RL27` offers, the 2014 share of a uniformly-worked window would be
8/12 (66.7 %) or 9/12 (75.0 %); the delivery reads **58.1 %** (9,213 of 15,854). December 2015 = 2
diaries and August 2015 = 7 are the other tell: those are stragglers, not a core.

⚪ **This costs nothing and settles something.** `D-S10-1` already ruled `uk` to **2014** on the
majority share, and this reconstruction is the same 58.1 % read a second way, so **the ruling is
untouched**. What changes is only what may be *written*: the manuscript may say the UK fieldwork ran
**April 2014 to December 2015 with an interruption**, and may **not** say it ran continuously or that
it has a twelve-month core.

⚪ **ES and IT uniformity, checked rather than assumed:** the delivery carries quarter, not month, so
the claim is testable only at quarter grain — `es` 25.60 / 26.19 / 25.11 / 23.10 % (max/min **1.133**)
and `it` 26.56 / 25.44 / 24.12 / 23.89 % (max/min **1.112**). Near-uniform, and reported as
*supported at quarter grain*, never as "uniform across all 12 months", which this delivery cannot say.

---

## 4. `FINDING 176` — `RL27`'s decision-impact table is superseded by a ruling made three days after it

Section C row 2 tells us to *"keep exact 12-month AMY windows as pre-registered"* and its negative
control 1 records that it *"did not recommend a typical-year weather file"*.

🔴 **The author reversed that ruling on 2026-08-25 (`D-S8-4`).** Step 8 runs on **`TMYx.2009-2023`**,
one shared base period for all three folds, precisely to remove the confound the actual-year design
carried. So `RL27`'s row is not wrong about what was pre-registered — it is **stale**, and it is the
class `V10.i` exists for: a recorded position outliving the thing it was a position about.

⚪ **The AMY half is not dead, it moved.** Step 10 runs ERA5 actual-year files, so `B10`'s licence
question is live *there* — and it is one of the five rows this seat cannot verify.
🔴 So: `RL27` may not be cited in Step 8's weather section at all, and may be cited in Step 10's only
for a licence claim someone has read at source.

---

## 5. Two further cautions, neither of them a finding

⚪ **It cites us back to ourselves.** Reference [R16] is **Iseri et al. (2025)**, *Energy and
Buildings* 337:115620 — the author's own prior paper, listed as read-in-full among the sources
supporting this brief. `RL29` did the same thing with a 2026 reference and it was called
**laundering** there. Here it is load-bearing for nothing, so it is noted rather than charged.

⚪ **`B12`'s falsification impugns its sources, not only its claim.** `B12` rests on [R12]–[R14], the
three national TABULA brochures, all marked *Tier 1, read full text*. The claim measured out as the
**worst** station in two folds of three. Either those brochures were not read, or they do not say
what the row says they say. **Rows [R12]–[R14] carry no weight in this project until someone opens
them.**

---

## 6. What this vetting changes

* 🟢 **The `RL27` debt is discharged.** The Step 8 weather card's *"never been vetted at all"* is now
  false and is corrected by this file, additively — the sentence stays, dated, with this record beside it.
* 🔴 **`RL27` is admissible row-by-row only**, on the table in §1, and **never for a variable name**.
* 🟢 **Nothing moved.** No band, threshold, verdict, gate or count changed; no gate was scored; no
  artefact was regenerated; no compute beyond four read-only pandas passes over parquet files already
  on disk. `FINDING 53` and `D-S6-4` stand exactly as written, and `D-S10-1`'s `uk` = 2014 pinning is
  re-confirmed rather than reopened.
* ⚪ **What a person could still retire:** the five `UNVERIFIABLE HERE` rows — `B1`, `B2`, `B3`, `B10`,
  `B13` — each of which needs one external document opened at source. Only `B10` and `B13` are
  load-bearing (they are the licence claims a data-availability statement would rest on).
