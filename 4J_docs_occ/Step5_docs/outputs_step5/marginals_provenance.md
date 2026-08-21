# `marginals_provenance.md` — Step 5.1

Every marginal used by Step 5.2 and by `G6.1`'s raked-donor null, with its source table, its cell
codes, the URL it was retrieved from and the date. **One row of `marginals_<country>.csv` per category.**

**Basis, frozen by `D-S5-1` on 2026-08-20 and not re-openable here:** route 3, the national statistical
offices; **the census round is the primary**; the annual series is a declared sensitivity that is
reported separately and never mixed in.

🔴 **`D-S5-2`, `D-S5-4` and `D-S5-5` were all ruled by the author on 2026-08-20 and are applied in
these files.** Sections 7, 8 and 9 record what each ruling changed and what it cost. **Two of the
three rulings changed the basis of a field, so no number in sections 1 and 2 below survives unchanged
— read section 7 onward before quoting anything.**

🔴 **A SECOND ROUND was ruled the same night — see PART III (sections 12-15).** It closes §9.2
(Spain's age and sex stay on the microdata basis), applies `FINDING 51` (`es` is fitted on **five**
economic bands, which surfaced `FINDING 52` in the raking engine) and applies `D-S5-3`, which
produces two NEW files, `econ_11plus_uk.csv` and `econ_11plus_es.csv`. 🔴 **Step 5.2 rakes economic
status on THOSE, not on the `strat_econ_status` rows of `marginals_<c>.csv` — the two are on
different bases and are not interchangeable.**

---

## STATUS, 2026-08-20 (after the three rulings)

| country | status | file |
|---|---|---|
| `uk` | 🟢 **BUILT, all four fields, on the PRIVATE-HOUSEHOLD universe** | `marginals_uk.csv`, 23 category rows, md5 `5bd9d6c7feadcc2382e573a76d2f7b7e` |
| `es` | 🟢 **BUILT, all four fields, on the PRIVATE-HOUSEHOLD universe** — `homemaker` cannot be separated from `other_inactive` (`FINDING 51`) | `marginals_es.csv`, md5 `32e1d97d0c107ee8d2eb7034abd18a8a` |
| `it` | 🔴 **NOT BUILT** — every ISTAT dissemination route funnels into `esploradati.istat.it`, whose IP `193.204.90.13` **refuses TCP on 443** (connect timeout, ~21 s, IPv4-forced, browser UA, direct-to-IP — all identical). Nothing verified, nothing written | — |

🔴 **`outputs_step5/` holds two folds of three, and Italy is the whole of what is left of Step 5.1.**
`G6.1` is computable for `uk` and for `es`, and for `it` not at all.

**Both built folds are now on the frame HETUS actually samples: residents of private households.**
That was `D-S5-5`. It is not a cosmetic correction — it moved the UK `75+` band by 6.8 %, the UK
`15-24` band by 5.6 % and the UK `student` economic band by 9.6 %.

---
## 1. United Kingdom — retrieved 2026-08-20

**Source:** Nomis, the ONS census dissemination API. Geography `2092957697` = United Kingdom, ONS code
`K02000001`. Census year 2011. `measures=20100` (counts, not percentages).

Raw responses are stored verbatim under `raw/` and are the file of record. **The CSV is derived from
them by summation only; no value was re-typed.**

| table | Nomis id | file | md5 |
|---|---|---|---|
| `QS103UK` Age by single year | `NM_1531_1` | `raw/uk_QS103UK_age_single_year.csv` | `789b7244d9d2721b2189423b6c5cac8a` |
| `KS101UK` Usual resident population | `NM_158_1` | `raw/uk_KS101UK_usual_resident_population.csv` | `37aa394872553c2f952e5343e0e9de49` |
| `KS105UK` Household composition | `NM_1502_1` | `raw/uk_KS105UK_household_composition.csv` | `85601e9f78fa77a2b74ffdd0b9e664c5` |
| `KS601UK` Economic activity | `NM_1511_1` | `raw/uk_KS601UK_economic_activity.csv` | `3e01b724390cad46078b8f8fa09a308b` |

Retrieval pattern, reproducible without a browser:

```
https://www.nomisweb.co.uk/api/v01/dataset/<ID>.data.csv?geography=2092957697&measures=20100
```

🔴 **A note for whoever repeats this.** The documented range syntax `cell=0...9999999` returns
**HTTP 200 with a zero-byte body**. It fails silently, exactly like the tcsh `2>/dev/null` trap already
recorded in this project. Omit the cell filter entirely and the full codelist is returned.

### 1.1 Age — `QS103UK`, and it is EXACT

Our `11-14` band has no published five-year equivalent: the standard bands are `0-4, 5-9, 10-14`.
`QS103UK` publishes **single years of age, UK-wide**, so the band is summed directly rather than
estimated or subtracted.

**Verification:** the 101 single-year cells sum to **63,182,178**, which is the table's own published
`C_AGE_TOTAL`, **difference 0**. The band file is then restricted to ages 11 and over, base
**55,053,949**, with **8,128,229** persons under 11 excluded by design (the corpus age floor is 11,
confirmed by the author as `D-S2-17`).

| band | count | share of 11+ |
|---|---|---|
| `11-14` | 2,971,665 | 5.398 % |
| `15-24` | 8,293,650 | 15.065 % |
| `25-34` | 8,431,789 | 15.316 % |
| `35-44` | 8,820,112 | 16.021 % |
| `45-54` | 8,737,554 | 15.871 % |
| `55-64` | 7,422,052 | 13.481 % |
| `65-74` | 5,480,225 | 9.954 % |
| `75+` | 4,896,902 | 8.895 % |

🟢 **This retires an unsourced number.** `RL24`'s Part C asserted `m_A(11-14) ≈ 4 %` with no citation
and it was rejected on that ground. The measured UK value is **4.703 % of all ages**, or **5.398 % of
the 11-plus base**. Neither is 4 %. **Quote the measured figure and its base, never `RL24`'s.**

### 1.2 Sex — `KS101UK`, and it is an APPROXIMATION, flagged as one in the file

| category | count | share |
|---|---|---|
| `male` | 31,028,143 | 49.109 % |
| `female` | 32,154,035 | 50.891 % |

🔴 **The base is ALL AGES, not 11 and over, and this is a declared defect, not an oversight.**
`QS103UK` carries no sex dimension. `DC1117EW` and `LC1117EW` do carry sex by single year but are
**England and Wales only**. **No UK-wide 2011 census table of sex by age was found.** The two rows
therefore carry `status = APPROXIMATION_ALL_AGES`.

**Why it is tolerable and where it is not.** The sex ratio is close to 50/50 at every adult age and
diverges only in the oldest bands, where women predominate. So the error is small in aggregate and
**concentrated exactly in `75+`**, which is also the band with no economic-status marginal. **Those two
weaknesses coincide in one stratum and that must be said in the limitations.** `L26` D1 asks whether a
UK-wide table exists after all, or whether assembling one from ONS, NRS and NISRA separately is the
only route.

### 1.3 Economic status — `KS601UK`, an EXACT six-way partition

🟢 **This is the single best result of item 5.1 and it vindicates the route decision.** The published
base is **46,410,490** and our six bands partition it with **residual exactly 0**.

| our band | `KS601UK` cells | count |
|---|---|---|
| `employed` | `200` In employment | 28,607,397 |
| `unemployed` | `KS601UK0005` | 2,054,146 |
| `student` | `KS601UK0006` active full-time student **+** `KS601UK0008` inactive student | 4,296,273 |
| `retired` | `KS601UK0007` | 6,443,875 |
| `homemaker` | `KS601UK0009` Looking after home or family | 1,981,470 |
| `other_inactive` | `KS601UK0010` long-term sick or disabled **+** `KS601UK0011` other | 3,027,329 |
| | **sum** | **46,410,490 = the published base** |

Two structural checks were run on the table before the mapping was accepted, because a category that is
*nested* rather than *disjoint* would double-count:

* In employment (28,607,397) **+** Unemployed (2,054,146) **+** active full-time student (1,606,992)
  **= 32,268,535 = "Economically active"**. So the active full-time student cell is **disjoint**, not a
  subset. It is therefore safe to add it to the inactive student cell.
* Employee part-time **+** Employee full-time **+** Self-employed **= 28,607,397 = "In employment"**.

🟢 **`RL24`'s central claim about the route is CONFIRMED against the file, not merely against the API
codelist:** the national table separates *Looking after home or family* from *Long-term sick or
disabled* and from *Other*. Eurostat's `CAS.L` does not. **The route decision rests on a real
distinction and we have now seen it in the numbers.**

🔴 **The coverage limit is real and is unchanged by any of this.** The table is titled *"All usual
residents aged 16 to 74"*. **Our `11-14` and `75+` bands have no economic-status marginal at either
end**, so their values must be **assigned, not fitted**. `strat_econ_status = unknown` is written into
the file as **count 0, status `NOT_PUBLISHED`** — a census has no item-non-response category, whereas
our corpus does. **A zero in that row means "the source cannot express this", not "nobody is unknown".**

### 1.4 Household type — `KS105UK`, and 8.06 % does not map

| our band | `KS105UK` cells | count | share |
|---|---|---|---|
| `one_person` | `100` | 8,086,989 | 30.584 % |
| `couple_no_children` | `KS105EW0005` married no children **+** `KS105EW0008` cohabiting no children | 4,624,572 | 17.489 % |
| `couple_with_children` | `0006 + 0007 + 0009 + 0010` | 6,714,613 | 25.394 % |
| `single_parent_with_children` | `203` lone parent | 2,851,354 | 10.783 % |
| `other_complex` | `300` other household types | 2,033,377 | 7.690 % |
| | **sum** | **24,310,905** | 91.94 % |

🔴 **Residual: 2,131,191 households, 8.060 % of the UK total, and it is a category we cannot assign.**
`KS105UK` publishes **"One family only: All aged 65 and over"** as a category *outside* the married /
cohabiting / lone-parent breakdown. Arithmetic confirms it is disjoint: all-65+ (2,131,191) + married
(8,785,131) + cohabiting (2,554,054) + lone parent (2,851,354) = 16,321,730 = "One family household".

It is a **one-family** household, so it is not `one_person`; beyond that the table does not say whether
it is a couple or a lone parent with a non-dependent child. It is written into the CSV as its own row,
`UNALLOCATED_one_family_all_aged_65_and_over`, with `status = AMBIGUOUS_needs_author_ruling`. 🔴 **It is
NOT silently folded into `couple_no_children`**, which is what it mostly is and which is exactly the
kind of quiet assumption this project's gates exist to prevent.

**This needs an author ruling before IPF runs**, and `L26` C4 asks whether ONS publishes a
cross-tabulation that would split it, and whether Spain and Italy carry the same category.

### 1.5 🔴 The denominator mismatch, now with real numbers on both sides

`RL24`'s Part D named the household-versus-person denominator mismatch as the thing we had not thought
to ask, and it was **right about the mechanism and unsourced on every number**, so its figures were
rejected. Both sides are now measured:

| | source | UK value |
|---|---|---|
| one-person **households** | `KS105UK`, census | **30.584 %** |
| diarists who **live alone** | our own corpus, 2,290 of 15,854 UK diaries | **14.444 %** |
| ratio | | **2.12x** |

**So the distortion is real and is a factor of 2.1, derived from one published table and our own
corpus rather than from `RL24`'s two unsourced ranges.** Fitting a household-based margin against
person-based margins without conversion would place roughly twice as many synthetic people in
one-person dwellings as belong there. **The conversion is mandatory and this is the number that
justifies it.**

For reference, the same person-side share in the other two folds: `es` 8.955 % (1,714 of 19,140),
`it` 15.564 % (5,955 of 38,260). **The one-person share is not transferable between countries** and the
conversion must be done per fold.

---

## 2. Spain — BUILT for THREE of four fields, retrieved 2026-08-20

`marginals_es.csv`, 22 rows, md5 `eff025b704ca993d35ba2ca2de5c335e`. Built after `RL26` supplied the
access route; **every number below was re-derived here from the two files in `raw/`, not copied from
the report.**

**Source:** INE, Censos de Poblacion y Viviendas 2011, served as static PC-Axis files from the INEbase
JAXI store. The 2011 census is **not** in the Tempus3 JSON API — that is why the earlier probe found
nothing — and `RL26`'s explanation of the two-architecture split is correct and was confirmed by
retrieval.

| table | matrix | file | md5 |
|---|---|---|---|
| `Poblacion por sexo, edad (ano a ano) y nacionalidad` | `03001` | `raw/es_03001_age_single_year_by_sex.px` | `7eff9805047b63c4641d9275bcef266a` |
| `Hogares segun su tamano por estructura del hogar` | `01011` | `raw/es_01011_household_structure_by_size.px` | `b83e145e8d5300f6d7835e66e50e911f` |

Retrieval pattern:

```
https://www.ine.es/jaxi/files/_px/es/px/t20/e244/<section>/p01/l0/<matrix>.px?nocab=1
```

### 2.1 🔴 The Spanish census publishes NON-INTEGER counts, and this changes how a marginal is checked

`03001.px` carries `DATA=4.6815916442321E7 ...`. The Censo 2011 was a **sample-based census with
grossing weights**, so every published cell is a float: the national total is `46,815,916.44`, not an
integer. **The `residual == 0` test that the UK tables pass exactly cannot be applied to Spain**; the
builder reports the residual as a float instead, and the age and household partitions both close to
better than `0.001` persons.

This also explains why `RL26`'s Spanish band counts are off by 1 to 4 from the file: it rounded each
band before summing. **The report's own 11-plus base is internally inconsistent by 5 as a result**
(`41,493,158` stated, `41,493,163` implied by total minus under-11). The measured base is
`41,493,161.67`. 🔴 **Use the CSV, never the report's table.**

### 2.2 Age and sex — both EXACT, and Spain is better off than the UK here

`03001.px` is **single year of age BY SEX**, so unlike the UK the Spanish sex marginal is computed on
the **11-plus base directly** and carries `status = EXACT` rather than `APPROXIMATION_ALL_AGES`. The
`75+` stratum therefore has one weakness in Spain where it has two in the UK.

| band | count | share of 11+ |
|---|---|---|
| `11-14` | 1,746,617.18 | 4.209 % |
| `15-24` | 4,718,447.63 | 11.372 % |
| `25-34` | 6,981,334.94 | 16.825 % |
| `35-44` | 7,931,397.43 | 19.115 % |
| `45-54` | 6,829,081.09 | 16.458 % |
| `55-64` | 5,169,932.21 | 12.460 % |
| `65-74` | 3,899,962.05 | 9.399 % |
| `75+` | 4,216,389.15 | 10.162 % |
| **base** | **41,493,161.67** | ages 0-10 excluded: 5,322,754.77 |

Sex on the same base: male `20,362,619.22` (49.075 %), female `21,130,542.45` (50.925 %).

### 2.3 Household type — an EXACT five-way partition, and NO ambiguous block

The eleven substantive structure cells of `01011.px` map onto our five bands with residual
`-0.0003` against the published base of `18,083,692.31` households.

| our band | `01011.px` structure cells | count | share |
|---|---|---|---|
| `one_person` | woman <65, man <65, woman 65+, man 65+ | 4,193,319.34 | 23.188 % |
| `couple_no_children` | `pareja sin hijos` | 3,804,677.39 | 21.039 % |
| `couple_with_children` | `pareja con hijos` (any <25, all 25+) | 6,321,922.38 | 34.959 % |
| `single_parent_with_children` | `padre o madre` (any <25, all 25+) | 1,693,257.70 | 9.364 % |
| `other_complex` | `pareja/padre-madre + otras personas`, `otro tipo` | 2,070,515.52 | 11.450 % |

**A nesting check was run, as it was for the UK.** The four one-person *structure* cells sum to
`4,193,319.34`, which is exactly the `1 persona` *size* column of the same table — **residual 0.0000**
on an axis the mapping does not use. The one-person mapping is confirmed by a second dimension.

🟢 **Spain has no analogue of the UK's 8.06 % unallocated block.** Its age-defined household cells are
one-person cells (`mujer sola de 65 anos o mas`, `hombre solo de 65 anos o mas`) and they map without
ambiguity. **`D-S5-2` is a UK-only problem.**

🔴 **One mapping decision, flagged in the CSV as `MAPPING_DECISION_see_provenance`.** The cell *"pareja
o padre/madre que convive con algun hijo menor de 25 anos y otra(s) persona(s)"* (894,955.63) is a
couple-or-lone-parent **with children plus other residents**. It is assigned to `other_complex`, which
matches how `KS105UK`'s *"Other household types: With dependent children"* was treated for the UK.
**The two folds are consistent with each other; neither is the only defensible reading.**

### 2.4 🔴 Economic status — Spain publishes NO static census table for it

This is the one field `RL26` did not deliver and reported as delivered. It cites matrix `03007.px` as
the Spanish economic-activity source. **That file was downloaded and its own `TITLE` is *"Poblacion en
establecimientos COLECTIVOS por sexo, nivel de estudios completados y relacion con la actividad
economica"*** — the institutional population of roughly 0.27 M persons, not the 38 M general
population. It is the wrong universe by two orders of magnitude.

**The absence was then checked directly rather than inferred.** `cen11_datos_resultados.htm` lists
every published Censo 2011 table tree: `avance` (population), `hogares`, `nucleos`, `colectivos`,
`vinculada`, `edificios`, `viviendas`. **There is no economic-activity tree for the general
population**, and the national population tree `avance/p01/l0/` contains exactly eight matrices
(`03001`-`03008`), none of which is about activity; `03009` and above return HTTP 204.

So for Spain the economic-status marginal must come from either the INE on-demand *Resultados
detallados* query tool or the census microdata (`RELAC`). **Both are a different basis from a
published static table, and that is an author decision, not a download.** Written into the CSV as
`strat_econ_status,NOT_AVAILABLE,...,NO_STATIC_CENSUS_TABLE_see_provenance` — **a blank, not a zero
and not a guess.**

---

## 3. Italy — NOT BUILT

`RL26` reports that the 2011 census dataflows exist on IstatData under the prefix `DF_DCSS_*` and do
not carry "census" or "censimento" in their identifier — which would explain why the earlier keyword
search of the 10 MB dataflow list found nothing, and is a plausible correction. It names six
dataflows and quotes national totals (59,433,744 residents; 24,611,766 households; one-person
31.199 %).

🔴 **None of it could be verified.** On re-check, `esploradati.istat.it` did not answer at all: six
dataflow requests and the dataflow list itself returned `HTTP 000` after a ~21 s connect failure,
while `www.istat.it` returned 200 from the same machine. **The host was reachable earlier the same
day, so this is a transient outage and not evidence against the report** — but the dataflow IDs, the
codelists and every Italian number remain **UNVERIFIED**, and none of them is in any file.

**No Italian number appears in `outputs_step5/`.**

---

## 4. What `RL26` was checked against, and what survived

| claim | checked how | verdict |
|---|---|---|
| Spain: 2011 census is on INEbase JAXI, not Tempus3, at `/t20/e244/` | four `.px` files downloaded, HTTP 200 | 🟢 **CONFIRMED** |
| Spain: `03001.px` is single year of age by sex | file parsed, 107 x 9 grid, totals match | 🟢 **CONFIRMED** |
| Spain: `01011.px` household structure, 18,083,692 households | file parsed, all eleven cells match to the unit | 🟢 **CONFIRMED** |
| Spain: age band counts (`11-14` = 1,746,616 etc.) | recomputed from the file | 🔴 **OFF BY 1 TO 4**, and the report's 11+ base is internally inconsistent by 5 |
| Spain: `03007.px` is the economic-activity source | file downloaded, `TITLE` read | 🔴 **FALSE** — it is the collective-establishment population |
| Spain: "no upper age ceiling on economic activity" | no static table exists to have a ceiling | 🔴 **UNSUPPORTED** |
| UK: `QS112UK` 65+ family block = 4,263,276 persons | `NM_1537_1` downloaded and parsed | 🟢 **CONFIRMED EXACTLY** |
| UK: mean size 2.0004 persons per household | 4,263,276 / 2,131,191 | 🟢 **CONFIRMED** (2.00042) |
| UK: "98.4 % are pensioner couples" from `QS111UK` 3,509,545 | `NM_1536_1` downloaded; that cell is HRP 65+, a superset | 🔴 **NON SEQUITUR** — the figure does not follow from the cited cells. The person-ratio argument is far stronger and is the one to use |
| UK: communal population 1,126,340 | `KS101UK` cells 4 and 5, already on disk | 🟢 **CONFIRMED EXACTLY** (63,182,178 - 62,055,838) |
| Italy: six `DF_DCSS_*` dataflows, all numbers | host unreachable | ⚪ **UNVERIFIED** |
| "8 of 8 country-field combinations have retrieved numbers" | counted | 🔴 **FALSE — it is 3 of 8** (Spain age, sex, household). Spain econ has none, Italy has none |
| "No unverified counts. Every figure directly parsed" | see above | 🔴 **FALSE** |
| "Did you recommend Eurostat or an annual series?" | read | 🟢 **NO** — the frozen basis was respected throughout |

**The route and the access mechanics are the part of `RL26` that is worth keeping. Its Spanish
arithmetic and its Spanish economic-status claim are not.**

---

## 5. What item 5.1 still owes

1. 🔴 **Italy, entirely.** Retry `esploradati.istat.it`; the dataflow IDs from `RL26` are the starting
   point but must be opened, not trusted.
2. 🔴 **Spain's economic-status marginal**, which no static census table supplies — an author decision
   between the INE query tool, the census microdata, and a declared absence.
3. 🔴 **`D-S5-2`**, now answerable for the UK: `QS112UK` gives the 65+ family block a mean size of
   2.00042 persons, so at most 894 of its 2,131,191 households hold more than two people.
4. 🔴 **`D-S5-3`**, unchanged, and Spain's `75+` weakness is unchanged.
5. 🔴 **The private-household universe.** Our UK age and sex marginals are `All usual residents`
   (63,182,178) but HETUS samples private households only (62,055,838 in `KS101UK`). **1,126,340
   persons, 1.78 %, concentrated in `75+` and `15-24`.** This is a defect in `marginals_uk.csv` as
   built and it was found by `RL26`, in a table we already had on disk.
6. **The household-to-person conversion**, Step 5.2, with the Spanish ratio now measurable:
   one-person households 23.188 % against 8.955 % of Spanish diarists living alone = **2.59x**, worse
   than the UK's 2.12x.

---

## 6. How to re-derive these files

* UK: `tools/4thJ_step5_nomis_parse.awk` extracts `CELL_NAME`, `CELL_CODE`, `OBS_VALUE` from the Nomis
  CSVs; banding is arithmetic on those three columns.
* Spain: `sh tools/4thJ_step5_build_es.sh Step5_docs/outputs_step5/raw > marginals_es.csv` regenerates
  the file in full from the two `.px` files.

**No value in either CSV was typed by hand, and no value came from `RL26`.**

---

# PART II — THE THREE RULINGS OF 2026-08-20, AS APPLIED

Sections 1 to 6 above describe the files **as they were built before the author ruled**. Everything
below supersedes them where the two disagree. Section 10 is the audit trail.

---

## 7. `D-S5-2` — RULED (a): the 8.06 % block is folded into `couple_no_children`

`KS105UK`'s *"One family only: All aged 65 and over"* — **2,131,191 households, 8.060 %** — sat
outside the married/cohabiting/lone-parent breakdown and was written into the file as its own
`AMBIGUOUS_needs_author_ruling` row rather than quietly absorbed.

**The evidence that settled it.** `QS112UK` (`NM_1537_1`, now in `raw/` with its md5) publishes the
same block as **people**: **4,263,276 persons** in **2,131,191 households**. Disjointness holds on the
person base exactly —
`4,263,276 + 27,677,022 + 75,188 + 7,162,262 + 7,409,415 = 46,587,163` = *One family only: Total*.

Mean size = **2.00042 persons per household**. A one-family household holds at least two people, so
the excess over `2 × 2,131,191` is **894 persons**: **at most 894 households — 0.042 % of the block —
contain more than two people.**

**Applied.** The block is now inside `couple_no_children`:

| our band | count | share | source cells |
|---|---|---|---|
| `one_person` | 8,086,989 | 30.5838 % | `100` |
| `couple_no_children` | **6,755,763** | **25.5493 %** | `KS105EW0005 + KS105EW0008 + KS105EW0004` |
| `couple_with_children` | 6,714,613 | 25.3936 % | `KS105EW0006+0007+0009+0010` |
| `single_parent_with_children` | 2,851,354 | 10.7834 % | `203` |
| `other_complex` | 2,033,377 | 7.6899 % | `300` |

**The partition now closes exactly**: `26,442,096` against a published base of `26,442,096`,
**residual 0**, where before the ruling it was short by exactly the 2,131,191 held out.

🔴 **What the limitations text must say.** The block was assigned, not resolved. The census does not
publish the couple-versus-elderly-parent-and-adult-child split. What the assignment cannot be right
about is a **two-person household of a lone parent and a 65+ non-dependent child**, which requires a
parent aged roughly 85 or more. State the 2.00042 and the 894.

⚪ **`RL26`'s own argument for the same conclusion is a non sequitur and must not be reproduced.** It
claimed `QS111UK`'s 3,509,545 "proves over 98.4 % are pensioner couples"; that cell was downloaded and
is *"Age of HRP 65 and over: Two or more person household: No dependent children"* — a **superset** of
the block. The person-ratio argument above is tighter and actually follows from its cited numbers.

---

## 8. `D-S5-5` — RULED: restrict every marginal to residents of PRIVATE HOUSEHOLDS

The census enumerates **all usual residents**; HETUS samples **private households only**. Fitting one
against the other pushes institutional residents into private dwellings, and the modal destination is
`one_person` — the same band the household-to-person denominator mismatch already inflates.

### 8.1 The United Kingdom — the communal population is published in total but NOT by age

**Total, exact.** `QS419UK` (*Position in communal establishment*) gives **1,126,340** people, which
equals `KS101UK`'s *All usual residents* 63,182,178 minus *Lives in a household* **62,055,838**, to the
person. Of them, 1,049,504 are residents, 41,259 staff or owners and 35,577 family of staff — **all of
them are outside the HETUS frame, so all 1,126,340 are removed.**

🔴 **There is no UK-wide census table of residence type by age.** The full UK-suffixed 2011 catalogue
was enumerated on Nomis (78 tables); `QS101UK` publishes residence type with no age dimension,
`KS405UK` publishes communal residents by establishment type with no age dimension, and every
residence-type-by-age table — `DC1104EW`, `LC1104EW`, `LC1105EW`, `DC1602EWla` — is **England and Wales
only**. Scotland's and Northern Ireland's equivalents are not on Nomis, and `scotlandscensus.gov.uk`
serves a JavaScript application with no reachable CSV.

**So the profile is England and Wales, scaled to the UK total.** `DC1104EW` at geography
`2092957703` (`K04000001`) gives the communal population by age band and sex; E&W communal total is
**1,004,799**, so the scale factor is `k = 1,126,340 / 1,004,799 = 1.12096051`. **E&W is 88.8 % of the
UK population, so the borrowed part of this is the residual 11.2 %.** Flagged in every affected row as
`PRIVATE_HH_D-S5-5_EW_PROFILE_SCALED_TO_UK`.

**One within-band assumption.** `DC1104EW` bands are `10 to 14`, and our band starts at 11. The
communal count for `10-14` is assumed uniform across the five single years, so `11-14` takes four
fifths. The whole band is **22,971.62 people against 2,971,665** — the assumption can be wrong by at
most a few thousand.

**What it moved:**

| band | all residents | communal removed | private households | shift |
|---|---|---|---|---|
| `11-14` | 2,971,665 | 22,971.62 | **2,948,693.38** | −0.77 % |
| `15-24` | 8,293,650 | 465,175.07 | **7,828,474.93** | **−5.61 %** |
| `25-34` | 8,431,789 | 100,519.89 | **8,331,269.11** | −1.19 % |
| `35-44` | 8,820,112 | 56,324.90 | **8,763,787.10** | −0.64 % |
| `45-54` | 8,737,554 | 49,936.55 | **8,687,617.45** | −0.57 % |
| `55-64` | 7,422,052 | 41,555.13 | **7,380,496.87** | −0.56 % |
| `65-74` | 5,480,225 | 45,777.79 | **5,434,447.21** | −0.84 % |
| `75+` | 4,896,902 | 332,473.52 | **4,564,428.48** | **−6.79 %** |
| base | 55,053,949 | 1,114,734.47 | **53,939,214.53** | partition residual **0.00** |

🔴 **Two bands carry two thirds of the correction, and they are the two bands this study is weakest
in.** `15-24` is halls of residence and barracks; `75+` is care homes. Had this not been corrected,
IPF would have been fitting 332,474 care-home residents and 465,175 students into private dwellings.

**Sex.** Communal is 48.674 % male, close enough to the population that the shares barely move
(49.1090 → **49.1169 %**). The rows are on the exact private-household base of **62,055,838**, and
male + female reproduce it exactly. 🔴 **The correction does nothing for the `APPROXIMATION_ALL_AGES`
weakness — the sex marginal is still an all-ages split, because no UK-wide sex-by-age table exists.
`75+` therefore still has two weaknesses in the UK where Spain has one.**

**Economic status.** `DC1602EWla` (*Residence type by economic activity by age*) supplies the communal
economic vector; its `65 and over` band is split to `65-74` by **40,838 / 337,435 = 0.121025**, a ratio
**measured** against `DC1104EW` — the two tables agree on the 65+ communal total to the person — with
the composition within 65+ assumed uniform. Mapped onto our six bands exactly as `KS601UK` was
(economically-active full-time students are a **disjoint** category, not a subset), scaled by the same
`k`:

| band | all residents 16-74 | communal removed | private households | shift |
|---|---|---|---|---|
| `employed` | 28,607,397 | 117,900.82 | **28,489,496.18** | −0.41 % |
| `unemployed` | 2,054,146 | 16,746.75 | **2,037,399.25** | −0.82 % |
| `student` | 4,296,273 | 410,916.26 | **3,885,356.74** | **−9.56 %** |
| `retired` | 6,443,875 | 43,960.18 | **6,399,914.82** | −0.68 % |
| `homemaker` | 1,981,470 | 1,848.38 | **1,979,621.62** | −0.09 % |
| `other_inactive` | 3,027,329 | 156,345.26 | **2,870,983.74** | −5.16 % |
| base | 46,410,490 | 747,717.65 | **45,662,772.35** | partition residual **0.00** |

**Household type needed no correction** — `KS105UK` counts private households by construction.

### 8.2 Spain — INE's own microdata is defined on exactly the frame we need

`D-S5-4` admitted the Censo 2011 person microdata. Line 2 of INE's record layout states its universe:
***"Un registro para cada persona residente en viviendas principales"*** — **persons resident in main
dwellings, which is the private-household frame, with no subtraction required.**

🟢 **The universe claim was verified arithmetically, not taken on trust.**

| quantity | value | source |
|---|---|---|
| published total population | 46,815,916.44 | `03001.px` |
| population in collective establishments | 444,100.79 | `colectivos/01001.px` |
| of whom **usually resident there** | **241,186.87** | `colectivos/01002.px` |
| **microdata weighted total** | **46,574,725.58** | 4,107,465 records × `FACTOR` |
| `46,815,916.44 − 241,186.87 =` | 46,574,729.57 | |
| **gap** | **3.99 persons** | on 46.8 million |

**Four people out of forty-six million.** The microdata is the published census population minus
exactly the people whose usual residence is an institution. That is what makes it usable here, and it
is why the collective population had to be split by registration status first: **the 444,100.79 in the
collectives table is not the number to subtract** — over 45 % of the people counted in Spanish
collective establishments are registered as usually resident somewhere else, and the census already
counts them in their family dwelling.

⚪ `RL26` quoted the Spanish collective population as **271,760**. It matches neither total; the
closest published figure is `Residencias de personas mayores` = 270,285.89, one establishment type out
of five.

**Applied — age (base 41,254,298.76) and sex, weighted by `FACTOR`:**

| band | published, all residents | microdata, private households | shift |
|---|---|---|---|
| `11-14` | 1,746,617.18 | **1,746,785.99** | +0.010 % |
| `15-24` | 4,718,447.63 | **4,716,821.31** | **−0.034 %** |
| `25-34` | 6,981,334.94 | **6,964,591.30** | −0.240 % |
| `35-44` | 7,931,397.43 | **7,918,587.11** | −0.162 % |
| `45-54` | 6,829,081.09 | **6,816,856.09** | −0.179 % |
| `55-64` | 5,169,932.21 | **5,156,883.83** | −0.252 % |
| `65-74` | 3,899,962.05 | **3,876,122.17** | −0.611 % |
| `75+` | 4,216,389.15 | **4,057,650.95** | **−3.765 %** |

Sex: male **20,272,126.58** (49.1394 %), female **20,982,172.18** (50.8606 %), summing to the base
exactly. **Spanish sex remains `EXACT` where the UK's is an approximation.**

🔴 **The single most interesting number in this section is `15-24`: the UK band loses 5.61 % to
communal establishments and the Spanish band loses 0.034 % — a factor of 165.** British students live
in halls; Spanish students live at home. This is a real structural difference between two of the three
folds, it is invisible in any all-resident marginal, and it lands directly on `strat_age_band ×
strat_hh_type`, which is what Step 5.2 has to fit. **Any LOCO result on `uk` or `es` that involves
young adults has to be read with this in it.**

**Household type needed no correction** — `01011.px` counts households.

---

## 9. `D-S5-4` — RULED (b): Spain's economic status comes from the census microdata

**Retrieved.** `Microdatos_personas_nacional.zip`, 155,860,498 bytes, md5
`0c8f9b44b70b079b25f2f20fdbd2e83f`, expanding to `MicrodatosCP_NV_per_nacional_3VAR.txt`,
1,158,305,130 bytes, **4,107,465 person records** of 280 fixed-width characters. Record layout
`Personas detallado_WEB.xls`, converted and stored as
`raw/es_cen11_microdata_record_layout.csv`. Fields used: `FACTOR` 20-33, `EDAD` 40-42, `SEXO` 43,
`RELA` 123, `ESCUR1` 135-136. The file is **not** committed — it is 1.1 GB — but
`tools/4thJ_step5_build_es_micro.sh` regenerates every number in one pass from the zip.

### 9.1 🔴 `FINDING 51` — the Spanish census has no `homemaker` category, so one of our six bands cannot be filled

`RELA` has **six** values and only six:

```
1 Ocupado
2 Parado que ha trabajado antes
3 Parado buscando su primer empleo
4 Persona con invalidez laboral permanente
5 Jubilado, prejubilado, pensionista o rentista
6 Otra situacion
blanco, si edad < 16
```

**There is no `Labores del hogar`, and there is no `Estudiante`.** `RL26` states in two places that
`RELA` "explicitly distinguishes Category 6 *Labores del hogar* from Category 7 *invalidez* and
Category 8 *Otra situacion*" — **that is false for the public microdata file**, and it was one of the
report's two grounds for recommending this route.

`student` is recoverable, because `ESCUR1` records the studies a person is currently receiving:
a person with `RELA = 6` and a non-blank `ESCUR1` is a student. **`homemaker` is not recoverable by any
combination of published variables**, because the census never asked the question.

**Applied, on the 16-74 base to match `KS601UK` exactly:**

| band | count | share | rule |
|---|---|---|---|
| `employed` | 17,443,246.20 | 49.8007 % | `RELA = 1` |
| `unemployed` | 7,324,467.88 | **20.9115 %** | `RELA = 2 or 3` |
| `student` | 1,929,663.51 | 5.5092 % | `RELA = 6` and `ESCUR1` non-blank |
| `retired` | 5,250,817.52 | 14.9912 % | `RELA = 5` |
| `homemaker` | *(blank)* | — | **`NOT_SEPARABLE_RELA_has_no_homemaker_category_FINDING_51`** |
| `other_inactive` | 3,077,889.96 | 8.7874 % | `RELA = 4`, or `RELA = 6` and not studying — **includes every homemaker** |
| base | **35,026,085.07** | | partition residual **0.0000** |

🔴 **The size of the problem, stated plainly.** The Spanish corpus has **11.140 % of diarists in
`homemaker`**. The census's entire residual inactive band, homemakers included, is **8.787 %**. *The
census category that must contain all the homemakers is smaller than the homemaker band alone.* The
two instruments do not classify Spanish inactivity the same way, and IPF cannot repair that — it will
move mass between `homemaker` and `retired` on a basis the census does not support. **Fit `es` on the
five-band collapsed vector and say so; do not fit a six-band Spanish econ marginal.**

🔴 **Second asymmetry, and it is the one `D-S5-4` was ruled against my recommendation to avoid.** The
UK economic marginal is a **published aggregate** (`KS601UK`, six bands); the Spanish one is a table
**we tabulated ourselves** from microdata (five bands). Inside a leave-one-country-out design, the
held-out country's marginal is the whole of the null's information, so the two folds are not being
scored against sources of equal standing. The author ruled it; it is recorded here so the paper
declares it rather than discovers it.

⚪ **One thing the ruling bought that was not expected.** Because the microdata universe is *viviendas
principales*, the Spanish econ marginal arrived already on the private-household frame — so `D-S5-4`
and `D-S5-5` are satisfied by the same file, with the reconciliation in §8.2 as the proof.

🔴 **`unemployed` at 20.91 % against the UK's 4.46 %** is not an error. It is Spain in 2011. It is also
the largest single cross-country difference in any marginal we hold, and it will dominate any raked
donor null built for the `es` fold.

### 9.2 🔴 A basis consequence that the author has not yet been asked about

`D-S5-1` froze the basis as **published census aggregates**. Applying `D-S5-5` to Spain required a
private-household age and sex distribution, which INE does **not** publish — the collectives tables
carry no age dimension at all (only type × sex, type × registration, type × municipality size). The
only source that has it is the microdata the author admitted for economic status.

**So Spain's `strat_age_band` and `strat_sex` rows are now tabulated from microdata too**, flagged
`PRIVATE_HH_FROM_MICRODATA_D-S5-5`, with the published all-resident counts retained as `#` reference
lines inside `marginals_es.csv` and the per-band differences printed beside them. **This follows from
combining two of the author's own rulings, but it was not itself ruled on, and it is a change of basis
for two fields.** It is recorded at the top of section 11 as the first thing owed.

---

## 10. Audit trail — every file, with its hash

| file | md5 | what it is |
|---|---|---|
| `marginals_uk.csv` | `5bd9d6c7feadcc2382e573a76d2f7b7e` | 23 category rows, all four fields, private households |
| `marginals_es.csv` | `32e1d97d0c107ee8d2eb7034abd18a8a` | all four fields, private households, `homemaker` blank |
| `raw/uk_QS103UK_age_single_year.csv` | (unchanged) | age by single year, UK |
| `raw/uk_KS101UK_usual_resident_population.csv` | (unchanged) | sex; and the communal/household split |
| `raw/uk_KS105UK_household_composition.csv` | (unchanged) | household composition |
| `raw/uk_KS601UK_economic_activity.csv` | (unchanged) | economic activity 16-74 |
| `raw/uk_QS112UK_household_composition_people.csv` | `cb49dd863c69a39948bd71224e8ff316` | **the evidence for `D-S5-2`** |
| `raw/uk_QS419UK_position_in_communal_establishment.csv` | `960147f77f56d0002d9c698d1f71f811` | UK communal total, 1,126,340 |
| `raw/uk_DC1104EW_residence_type_by_sex_by_age.csv` | `343489225d62cf5a7070645f249cb21a` | E&W communal by age and sex |
| `raw/uk_DC1602EW_residence_type_by_economic_activity_by_age.csv` | `a34c3043fb69df9fcb5399340fe84844` | E&W communal by economic activity |
| `raw/es_03001_age_single_year_by_sex.px` | `7eff9805047b63c4641d9275bcef266a` | published age by single year and sex |
| `raw/es_01011_household_structure_by_size.px` | `b83e145e8d5300f6d7835e66e50e911f` | household structure |
| `raw/es_col_01001_collective_population_by_type_and_sex.px` | `67d229dbb6cea195a88e5bffc543e0ec` | collectives by type and sex |
| `raw/es_col_01002_collective_population_by_registration.px` | `70a27fef098caa8ea09db15cdda85316` | **collectives by registration — the 241,186.87** |
| `raw/es_cen11_microdata_record_layout.csv` | `01387cb6546e28af7a390d3a86f73e6c` | INE record layout, converted from `.xls` |
| `es_microdata_tabulation.tsv` | — | the tabulation itself, 36 lines |
| *(not committed)* `Microdatos_personas_nacional.zip` | `0c8f9b44b70b079b25f2f20fdbd2e83f` | 155,860,498 bytes |

**Scripts.** `tools/4thJ_step5_nomis_parse.awk` (Nomis quoted-CSV), `tools/4thJ_step5_build_es.sh`
(the two `.px` files), `tools/4thJ_step5_privhh_uk.sh` (the UK communal vector),
`tools/4thJ_step5_build_es_micro.sh` (the Spanish microdata pass).
**No value in either CSV was typed by hand.**

---

## 11. What Step 5.1 still owes

1. 🔴 **A yes/no on §9.2** — Spain's age and sex are now microdata-based. Confirm, or revert those two
   fields to the published all-resident aggregates and accept an uncorrected universe for `es`.
2. 🔴 **Italy, the whole fold.** `esploradati.istat.it` resolves (`193.204.90.13`,
   `01a-filtro.istat.it`) but **times out on TCP 443** — identically under IPv4, a browser
   user-agent, and a direct-to-IP request; `dati.istat.it` and `dati-censimentopopolazione.istat.it`
   both redirect into it. This is an outage or a block, not a wrong URL. Eurostat is **not** an
   admissible substitute (`D-S5-1`). `RL26`'s `DF_DCSS_*` dataflow identifiers remain the starting
   point and remain **unverified**.
3. 🔴 **`D-S5-3`** — `unknown` for `11-14` in all three folds; `75+` = `retired`, quoting the weak
   fold (`uk` 95.4 %, `it` 71.9 %, **`es` 58.9 %**). Unchanged by these rulings.
4. 🔴 **The five-band Spanish econ fit** (§9.1) has to be carried into Step 5.2's IPF setup, not just
   noted here.
5. **Step 5.2, the household-to-person conversion**, now with both denominators on one frame.

---

# PART III — the second round of rulings, 2026-08-20 (night)

🔴 **Part III supersedes Part II's section 11 "what 5.1 still owes".** Three of the five items there
are now closed. The author ruled all three on 2026-08-20, each as recommended.

| item | ruling | effect |
|---|---|---|
| §9.2, Spain's age and sex basis | **(a) keep the microdata basis** | no file changes; the basis change is now ruled, not merely recorded |
| `FINDING 51`, the Spanish econ fit | **(a) `es` on five bands, `uk` on six** | `tools/4thJ_step6_rakeddonor.py` extended; `FINDING 52` found and fixed |
| `D-S5-3`, econ status outside 16-74 | **(a) `unknown` for `11-14` in all folds**; `75+` = `retired` | new artefacts `econ_11plus_uk.csv`, `econ_11plus_es.csv` |

---

## 12. Spain's age and sex stay on the microdata basis

`D-S5-1` froze the basis as published census aggregates. §9.2 recorded that satisfying `D-S5-5` for
Spain had forced `strat_age_band` and `strat_sex` off that basis, because INE publishes no
private-household age or sex distribution — its `colectivos` tree is type × sex, type × registration
and type × municipality size, with **no age dimension anywhere**. The author has now ruled that the
microdata basis **stays**.

**What this settles.** `marginals_es.csv` is unchanged; the `PRIVATE_HH_FROM_MICRODATA_D-S5-5` status
flag on those two fields is now a *ruled* basis, not an open question, and the published all-resident
counts stay in the file as `#` reference lines with the per-band differences printed beside them.

🔴 **What it does not settle, and what the paper must say.** Three of Spain's four marginal fields are
now tables we tabulated ourselves; three of the UK's four are published aggregates. In a LOCO design
the held-out country's marginal carries the whole of the null's information, so **the `es` and `uk`
folds are not scored against sources of equal standing.** This is now a declared property of the
design. It is not a defect that can be repaired — the alternative was mixing two universes inside one
file — but it must be stated wherever a cross-fold comparison of `G6.1` margins appears.

---

## 13. `FINDING 51` applied — `es` is fitted on five bands, and `FINDING 52` came out of doing it

### 13.1 The ruling

The Spanish census has no `homemaker` category (`RELA` has six values, and neither *Labores del
hogar* nor *Estudiante* is among them), so Spain can supply only five of the six economic bands.
The ruling: **each fold uses the best marginal its own country publishes.** `es` is raked on five
bands with `homemaker` merged into `other_inactive`; `uk` keeps all six. The folds are scored
separately, so nothing breaks — but the *strength* of the bar is not comparable across countries and
the paper must say so.

### 13.2 🔴 `FINDING 52` — `rake()` deletes a donor category the target never names, and reports a
### perfect fit while doing it

Implementing the ruling meant handing `rake()` a five-category target against a donor pool that
carries six. That is not what the function does with it.

`rake()` builds its IPF adjustment factors **only from the categories the target names**:

```python
factor = {}
for cat, want in tgt.items():
    have = cur.get(cat, 0.0)
    factor[cat] = (want / have) if have > 0 else 0.0
weights = [w * factor.get(d[var], 0.0) for d, w in zip(donors, weights)]
```

A donor whose category is absent from `tgt` hits `factor.get(..., 0.0)` and is multiplied by **zero**.
It is not merged, not flagged and not counted — it is deleted from the pool.

**Measured, not inferred.** On a 120-donor `uk + it` pool against Spain's five published bands:

| | |
|---|---|
| donors carrying `homemaker` | **20 of 120** |
| donors given weight exactly `0.0` | **20 of 20** |
| effective pool after raking | 100 of 120 — **16.67 % deleted** |
| `max_dev_pp` reported | **5.6e-15** |
| error raised | **none** |

🔴 **The diagnostic reports a flawless fit precisely because it converged on the categories that
survived.** Every category the target named matched to fifteen decimal places; the sixth had been
annihilated before the deviation was measured. There is no output of `rake()` from which this is
visible. Had the five-band ruling been implemented naively, the `es` null would have been built on a
silently truncated pool and the number would have looked *better*, not worse.

⚪ **The existing guard is the mirror image of this one and does not catch it.** `rake()` already
refuses a target that names a category **no donor has** ("IPF cannot create them"). The dangerous
direction is the other one — a donor carrying a category **the target never names** — and it was
unguarded. This is `feedback_gates_must_be_seen_failing` in its purest form: a check that passes for
the wrong reason looks exactly like a check that passes.

### 13.3 The fix, additive

`tools/4thJ_step6_rakeddonor.py` 173 → 227 lines. Two additions, no existing behaviour changed:

1. **`collapse={variable: {donor_category: target_category}}`**, an optional argument applied to a
   *copy* of the donor records before raking. It has its own two guards: the variable must be one
   that is actually raked on, and the destination must be a category the target names (otherwise the
   donors are deleted twice over).
2. **Guard 5** — after the collapse, any donor category the target does not name raises `RakeError`
   naming the count, the variable and the orphan categories. Refused, never warned.

🟢 **A collapse is stamped onto the provenance label**, e.g.
`outputs_step5/marginals_es.csv@2026-08-20|collapse=strat_econ_status:homemaker>other_inactive`.
This buys a third protection for free: `score_margin()`'s existing handicap guard, which refuses to
compare two runs raked onto different marginals, **now automatically refuses to compare a five-band
null against a six-band model.** A declared loss of resolution cannot silently become a comparison.

### 13.4 The demonstration

`tools/4thJ_step6_rakeddonor_selftest.py` 133 → 194 lines, section 6 added. **23 → 34 checks, all
passing**, and the 23 pre-existing checks were re-run green *before* the new ones were added, so the
change is shown additive rather than asserted (section 4 of
`Resources/preprocessing_precedents.md` — the Leg-3 bit-identity precedent).

| check | result |
|---|---|
| Guard 5 fires on the uncollapsed pool | ✅ raises, naming `['homemaker']` |
| collapsed run converges | ✅ 3.89e-14 pp |
| and keeps the **whole** pool | ✅ 120 of 120, 0 deleted |
| collapse stamped on the provenance label | ✅ |
| collapsed null vs uncollapsed model refused by the handicap guard | ✅ |
| collapsing **into** a category the target does not name is refused | ✅ |
| collapsing a variable nobody rakes on is refused | ✅ |
| callers that never needed a collapse are unaffected | ✅ `collapse=None`, label unchanged |

⚪ Section 7 of the selftest, which still said `outputs_step5/` was empty, was corrected: the bar is
computable for `uk` and `es` and for `it` not at all.

### 13.5 What Step 5.2 must do

**`es` must be raked with**
`collapse={"strat_econ_status": {"homemaker": "other_inactive"}}`. Not by dropping `homemaker`
donors, and not by leaving it to `rake()` to work out — as of Guard 5 it will refuse, which is the
intended behaviour.

---

## 14. `D-S5-3` applied — the economic marginal over the whole 11+ population

### 14.1 The problem the ruling solves

The censuses publish economic activity for **16-74** only (`KS601UK`; the Spanish microdata was cut
to the same base deliberately, to match). The synthetic population starts at **11**. So three age
slices have no published economic status and IPF has nothing to rake them onto.

### 14.2 The ruling, and one slice it did not cover

| slice | assignment | status |
|---|---|---|
| `11-14` | `unknown` | **`D-S5-3` as ruled.** A declared value of the field for all three countries, the value Italy's own data uses, and the only choice that asserts nothing the source does not say |
| **age 15** | `unknown` | 🔴 **NOT covered by `D-S5-3` as put.** Assigned by the same argument — `KS601UK` starts at 16, so the census is equally silent here. **One-line confirmation owed** |
| `75+` | `retired` | **`D-S5-3` as ruled.** Corpus-modal in all three countries but **not clean in Spain**: `uk` 95.4 %, `it` 71.9 %, **`es` only 58.9 %** (Spain also records 251 `homemaker` and 539 `other_inactive` at 75+). Quote the Spanish figure wherever this marginal is used |

⚪ The age-15 slice exists because the age bands and the econ base do not align: `11-14` and `75+`
fall wholly outside 16-74, but the `15-24` band straddles it. It is **1.415 %** of the UK's 11+ base
and **1.027 %** of Spain's — small, but not nothing, and it had to be assigned to something.

⚪ Why not read it off the corpus: that would mean either importing one country's convention as a
universal one (the argument that killed `RL24`'s assign-`student` proposal) or reading the held-out
country's own data to set its marginal, which is contamination and would be invisible in the LOCO
result. `unknown` is the same answer for the same reason.

### 14.3 How it is computed

`tools/4thJ_step5_econ11plus.sh <outputs_step5_dir>` reads `marginals_<c>.csv` and writes
`econ_11plus_<c>.csv`. The age-15 slice is **never counted directly** — it is taken as the residual
of the four bases already in the marginals file, so it cannot drift away from them:

```
age15 = base(11+) − band(11-14) − base(16-74) − band(75+)
```

🟢 **Independently checked for the UK.** `QS103UK` publishes single years, so age 15 can be measured:
774,892 all-resident, minus the `DC1104EW` communal count 10,323 scaled by `k = 1.12096051`
(= 11,571.87), gives **763,320.13** in private households. The residual route gives **763,320.32**.
**The two agree to 0.19 persons**, which is the rounding carried in the four bases.

### 14.4 The result

| | `uk` | `es` |
|---|---|---|
| base, 11+ private households | 53,939,214.53 | 41,254,298.76 |
| `11-14` → `unknown` | 2,948,693.38 | 1,746,785.99 |
| age 15 → `unknown` | 763,320.32 (1.415 %) | 423,776.75 (1.027 %) |
| **`unknown` total** | **3,712,013.70 (6.882 %)** | **2,170,562.74 (5.261 %)** |
| `75+` folded into `retired` | 4,564,428.48 | 4,057,650.95 |
| **`retired` total** | **10,964,343.30 (20.327 %)** | **9,308,468.47 (22.564 %)** |
| `homemaker` | 1,979,621.62 (3.670 %) | **blank — `FINDING 51`** |
| **partition residual vs base** | **−0.00** | **0.00** |

`econ_11plus_uk.csv` md5 `b4b3935816bf238c2f3c3248e578412f`,
`econ_11plus_es.csv` md5 `24e3b6f3625f8dc2a3dff9ba38db9a73`.

🔴 **`retired` doubles and becomes the second-largest band.** On the published 16-74 base the UK's
`retired` share is 14.02 %; over 11+ with `D-S5-3` applied it is **20.33 %**. Spain moves 14.99 % →
**22.56 %**. Any statement about retired-person occupancy has to name which base it is on. **The two
files are not interchangeable**: `marginals_<c>.csv` carries the published fields on their published
bases, `econ_11plus_<c>.csv` carries the econ field with a *convention* applied on top. Step 5.2 rakes
on the latter; anything quoting a census figure cites the former.

⚪ `unknown` is now a real category with mass — 6.9 % in the UK, 5.3 % in Spain — where in
`marginals_<c>.csv` it is a `0` row flagged `NOT_PUBLISHED_census_has_no_nonresponse_band`. Donors
must therefore be able to carry `strat_econ_status = unknown`, and they can: it is a declared
crosswalk value in all three countries, and in Italy it is the whole `11-14` band (`FINDING 48`).

---

## 15. What Step 5.1 still owes, after Part III

1. 🔴 **Italy, the whole fold.** Unchanged and unchanged in kind: `esploradati.istat.it` resolves to
   `193.204.90.13` and times out on TCP 443 under every variation tried. Not a wrong URL. Eurostat
   is not admissible (`D-S5-1`). `RL26`'s `DF_DCSS_*` identifiers remain the starting point and
   remain unverified. **This is now the whole of the critical path.**
2. 🔴 **One line: confirm age 15 → `unknown`** (§14.2). Applied as the direct extension of `D-S5-3`'s
   own argument; 1.4 % of the UK base, 1.0 % of Spain's. A one-line change if the answer is no.
3. **Step 5.2** — the household-to-person conversion, with `es` raked using the `collapse` argument
   of §13.5 and both folds raking econ on `econ_11plus_<c>.csv`, not on `marginals_<c>.csv`.

⚪ Items 1, 4 and 5 of Part II §11 are closed by §12, §13 and §14 respectively. Item 2 (Italy) and
item 3 (`D-S5-3`) are carried forward — item 3 only as the age-15 residue.
