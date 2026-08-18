# Codebook facts — United Kingdom, strata addendum (M-8 / D-S2-18)

### Step 1, contract change M-8-a. The six conditioning-strata sources, transcribed from the
### delivery's own documentation. Extends `codebook_facts_uk.md`, does not replace it.
#### Compiled 2026-08-17 from the delivery itself. **No source here is taken from `RL02`, `RL17`,
#### or from Spain's or Italy's codebook.**

Same source class as `codebook_facts_uk.md`:

* **DD** — the UKDA data dictionaries, `mrdoc/allissue/uktus15_*_ukda_data_dictionary.rtf`. Cited
  as `DD:<file>` pos. N (the dictionary's own `Pos.` field).

Row-level population counts below were measured directly from `uktus15_individual.tab` (11,421
rows) and `uktus15_diary_ep_long.tab` (587,632 rows) at
`_local_runs/4J/raw/uk/unpacked/UK-TUS/UKDA-8128-tab/tab/`.

A stratum that could not be found in the delivery is written `NOT FOUND` and stays that way. None
of the six was NOT FOUND for the UK.

---

## THE SIX STRATA

| Stratum | Variable | File | Position | Grain | Value list (delivery's own labels) | Citation |
|---|---|---|---|---|---|---|
| **age** | `DVAge` | `uktus15_individual.tab` | pos. 25 | person | Continuous, "Age" — no value labels, exact single years. Declared sentinels: `-8` Don't know; `-7` Interview not achieved; `-2` Schedule not applicable; `-1` Item not applicable; `-9` No answer/refused | DD:individual, pos. 25. Already carried in Step 1's UK parquet. **[measured]**: 0 of 11,421 rows blank or carrying any of the five sentinels |
| **sex** | `DMSex` | `uktus15_individual.tab` | pos. 11 | person | "Gender from household grid". `1` Male; `2` Female; sentinels `-1`/`-9`/`-8`/`-7` | DD:individual, pos. 11. Already carried. **[measured]**: 0 of 11,421 rows blank or sentinel |
| **household type** | `dhhtype` | `uktus15_individual.tab` | pos. 588 | **household** (verified: 0 of 4,733 `serial` groups carry more than one distinct value) | "DV: Household type — 8 categories". `1` Single person household; `2` Married/cohab couple - with children ≤15; `3` Married/cohab couple - no children ≤15; `4` Single parent - with children ≤15; `5` Single parent - no children ≤15; `6` Unclassified - married/cohab couples in complex hhlds; `7` Unclassified - single parents in complex hhlds; `8` Other hhlds e.g. brothers/sisters, unrelated, etc. | DD:individual, pos. 588. **Not previously carried.** 🔴 `DV` = derived variable, UKDA's own construction from the household grid — it is still the delivery's own documented field, not an invented proxy |
| **economic status** | `deconact` | `uktus15_individual.tab` | pos. 598 | person | "DV: Economic activity and employment status (detailed)". `1` Employee - full time; `2` Employee - part time; `3` Self employed; `5` In employment - other; `6` Unemployed (ILO definition); `7` Retired; `8` Student; `9` Looking after family/home; `10` Long-term sick/disabled; `11` Other reasons e.g. temp sick, believes no jobs; `13` Under 16yrs; sentinels `-9`/`-8`/`-7`/`-1` | DD:individual, pos. 598. **Not previously carried.** See F-UK-16 for the two rejected alternatives (`WorkSta`, `dilodefr`) |
| **day type** | `DiaryDay_Act` | `uktus15_diary_ep_long.tab` | pos. 15 | diary-day | "Diary Day - ACTUAL DAY". `1` Sunday; `2` Monday; `3` Tuesday; `4` Wednesday; `5` Thursday; `6` Friday; `7` Saturday; sentinels `-9`/`-7`/`-2` | DD:diary_ep_long, pos. 15. Already carried. **[measured]**: 0 of 587,632 episodes blank or sentinel. See F-UK-17 for `ddayw`, the pre-banded weekday/Saturday/Sunday derived variable found alongside it |
| **season** | `dmonth` | `uktus15_diary_ep_long.tab` | pos. 17 | diary-day | "DV: Diary month". `1` January … `12` December | DD:diary_ep_long, pos. 17. **Not previously carried.** **[measured]**: 0 of 587,632 episodes blank. The UK is the only one of the three countries that ships a native month rather than a pre-banded quarter |

---

## ROW-LEVEL MISSINGNESS, MEASURED DIRECTLY

| Field | Blank / sentinel count | Denominator | Prevalence |
|---|---|---|---|
| `DVAge` | 0 | 11,421 persons | 0.0 % |
| `DMSex` | 0 | 11,421 persons | 0.0 % |
| `dhhtype` | 411 (blank) | 11,421 persons | 3.6 % |
| `deconact` | 722 (25 blank + 38 `-9` + 3 `-8` + 656 `-1`) | 11,421 persons | 6.3 % |
| `DiaryDay_Act` | 0 | 587,632 episodes | 0.0 % |
| `dmonth` | 0 | 587,632 episodes | 0.0 % |

🔴 **`deconact`'s `-1` ("Item not applicable") accounts for 656 of the 722 non-substantive rows —
91 % of the UK's economic-status gap.** This is distinct from the `13` "Under 16yrs" substantive
code (2,370 rows, not counted above), so `-1` is marking something else. What exactly `-1` means
for `deconact` specifically (as opposed to the general item-not-applicable sentinel shared across
many UK variables) is **not resolved here** — see "What is not established" below.

---

## 🔴 FINDINGS

### F-UK-16 — two alternative economic-status fields exist and were rejected in favour of `deconact`

* `WorkSta` (DD:individual, pos. 17), "Economic activity status" — a **raw** interview question, 10
  substantive categories (self-employed, in paid employment, unemployed, retired, on maternity
  leave, looking after family/home, full-time student, long-term sick/disabled, government
  training scheme, unpaid worker in family business) plus "doing something else" and sentinels.
  Closer in spirit to Spain's `HRELACTIV` and Italy's `newcondm` (both raw interview responses),
  but its category boundaries (e.g. "unpaid worker in family business", "government training
  scheme") do not correspond to any category either other country's raw field carries.
* `dilodefr` (DD:individual, pos. 597), "DV: Economic activity according to the ILO definition — 3
  categories" (in employment / unemployed / economically inactive / under 16) — the coarsest of
  the three UK candidates.
* `deconact` is used above because it is the UK's own *detailed* derived classification and its
  categories (employee/self-employed, unemployed, retired, student, homemaker, long-term
  sick/disabled, other) line up qualitatively with Italy's `newcondm` and Spain's `HRELACTIV` more
  closely than `WorkSta`'s interview-specific wording does. Which of the three the manager wants as
  the harmonisation source is **not decided here** — `strata_proposal.md` proposes with `deconact`
  and flags the alternatives.

### F-UK-17 — `ddayw` is Italy's `gsett` in UK form, and is a stronger day-type source than `DiaryDay_Act`

`ddayw` (DD:diary_ep_long, pos. 19), "DV: Day of week: Weekday, Saturday, Sunday" — `1` Mon-Fri;
`2` Saturday; `3` Sunday — is a UKDA-derived field with **exactly** the same three-way split as
Italy's `gsett`. Since Italy binds the day-type proposal to that three-way split (D-S2-18 Rule 2,
codebook_facts_italy_strata.md), `ddayw` requires no further collapsing to serve as the UK's
day-type source, where `DiaryDay_Act` (7-way) would need one. `DiaryDay_Act` is recorded above
because it is the field already carried in the Step 1 UK parquet and the finer-grained one; the
proposal in `strata_proposal.md` uses `ddayw`'s bands as the target and treats `DiaryDay_Act` as
available for `_raw` carrying, not as the harmonisation source.

### F-UK-18 — `dhhtype`'s "no children ≤15" category cannot be distinguished from Spain's "childless" category

The UK's `dhhtype` code `3` ("Married/cohab couple - no children ≤15") is defined purely by the
**absence of children aged 0-15** in the household — it does not distinguish a couple with no
children at all from a couple whose only children are 16 or older. Spain's `TIPOHOG`, by contrast,
carries a dedicated code (`2`, "Pareja sola") for a childless couple, separate from code `4`
("Pareja con todos los hijos mayores de 25 años", couple with only adult children). **A UK
household in `dhhtype=3` could correspond to either of Spain's codes `2` or `4`, and the UK's own
documentation gives no way to tell them apart.** This is a second, independent reason (beyond
Italy's `tipfa2m` carrying no child-age qualifier at all, F-IT-16) that the household-type proposal
in `strata_proposal.md` cannot preserve a "childless couple" vs. "couple with grown children"
distinction even where two of the three countries' raw fields might otherwise support it.

---

## WHAT IS **NOT** ESTABLISHED HERE

* What `deconact = -1` specifically represents for this field (as opposed to the shared
  "item not applicable" sentinel meaning across the UK dictionary generally) — not resolved from
  the delivered documentation; this is left as an open item for whoever builds `crosswalk_strata.csv`.
* Whether `WorkSta` or `dilodefr` would harmonise more cleanly than `deconact` against Spain's and
  Italy's economic-status fields — three candidates are recorded, none is chosen here beyond the
  proposal's working assumption.
* Nothing here builds `crosswalk_strata.csv` or touches the reader.
