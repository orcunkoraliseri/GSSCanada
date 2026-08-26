# `D-S10-1` — THE WEATHER YEAR. Route (a) was tried and it **WORKED**.

**Date:** 2026-08-26 · **Owner:** the author · **Status:** 🔴 OPEN, but the question has changed shape
**Blocks:** Step 10, Step 11, **and the OpenUBEM boundary-contract freeze** (MVP §12.8, `FINDING EU-S2-03`)
**Supersedes the framing in:** `Step10_docs/4thJ_10_ubemRealStock.md` §4.1

---

## 0. What changed, in one paragraph

§4.1 measured the **harmonised** corpus and correctly concluded it *cannot* answer this: `wave` carries
a two-year window and `strat_season_raw` is a quarter (`es`/`it`) or a month (`uk`), and neither
separates the two calendar years. That measurement stands. **What it did not say is that the raw
deliveries cannot answer it either — and they can.** All three were read on 2026-08-26. **Every fold's
calendar year is recoverable**, two of the three exactly. Route (a), the recommended one, succeeded.

🔴 **So this is no longer a decision about missing information.** It is now a decision about *what to do
with information we have*, which is a much smaller decision — and one of its three options has become
strictly better than it was, while a fourth has become possible.

---

## 1. What the raw deliveries actually carry — measured, not reasoned about

### 1.1 `es` — INE *Encuesta de Empleo del Tiempo* 2009-2010 — **EXACT, no straddle**

The year is **inside the quarter code**. `DISEnOS DE REGISTRO EET 2009 2010.xlsx`, the delivery's own
record-layout workbook, gives `TRIM`'s value labels verbatim:

```
1er. Trimestre (de 2010)
2º  Trimestre (de 2010)
3er. Trimestre (de 2010)
4º  Trimestre (de 2009)      <-- the only 2009 quarter
```

Confirmed independently by the INE methodology (`meth_t25304471.pdf` p. 14): *"El trabajo de campo se ha
desarrollado a lo largo de un año completo, **desde el 1 de octubre de 2009 hasta el 30 de septiembre de
2010**"*. A 12-month window starting in October — so `TRIM=4` is Oct–Dec **2009** and `TRIM=1,2,3` are
Jan–Sep **2010**. **The mapping is exact and total; no Spanish diary straddles a year boundary.**

Measured on `DIARIO2.TXT` (character position 8, the `TRIM` field), 2,778,480 slots = 19,295 diaries:

| `TRIM` | calendar year | slots | diaries | share |
|---|---|---|---|---|
| 1 | 2010 | 711,648 | 4,942 | 25.6 % |
| 2 | 2010 | 726,624 | 5,046 | 26.2 % |
| 3 | 2010 | 696,096 | 4,834 | 25.1 % |
| 4 | **2009** | 644,112 | 4,473 | 23.2 % |
| | **2010 total** | **2,134,368** | **14,822** | **76.8 %** |

### 1.2 `uk` — UKDS SN 8128, UKTUS 2014-15 — **EXACT, per diary, and it is a delivered variable**

`uktus15_diary_ep_long.tab` carries **`dyear`** at position 18, label *"DV: Diary year"*, alongside
`dmonth` (17) and `DiaryDate_Act` (14). Step 2 simply did not keep it. Measured over 587,632 episodes
de-duplicated to **16,533 diaries** on `(serial, pnum, daynum)`:

| `dyear` | diaries | share |
|---|---|---|
| **2014** | **9,609** | **58.1 %** |
| 2015 | 6,924 | 41.9 % |

⚪ The UK window is **not** a clean 12 months — fieldwork runs Apr 2014 → Dec 2015, and the monthly
crosstab is lumpy (Sep 2015 has **zero** diaries; Aug and Dec 2015 have 7 and 5). Months **1, 2, 3 are
2015 only** and month **9 is 2014 only**; the other eight months are genuinely mixed. **This is exactly
why the harmonised month field cannot do the job on its own and the join is required.**

### 1.3 `it` — ISTAT *Uso del Tempo* 2013-2014 — **RECOVERABLE, with one straddling quarter**

`uso_tempo_Microdati_Anno_2013_DiarioGiornaliero.txt` carries a column literally named `anno`, but
🔴 **`anno` is a constant `2013` on all 1,077,657 rows** — its own layout calls it *"anno di **inizio**
della rilevazione"*, a wave stamp, **not a record year**. A reader taking `anno` as the diary year would
be wrong on roughly three quarters of the file. The year comes instead from `meseri` crossed with the
fieldwork window:

* `meseri` value labels (`..._DiarioGiornaliero_var3.html`): `1` = Nov, Dec, Jan · `2` = Feb, Mar, Apr ·
  `3` = May, Jun, Jul · `4` = Aug, Sep, Oct
* Fieldwork window (`uso_tempo_NotaMetodologicaIndagine_Anno 2013.pdf` p. 8): *"condotta **dal 1° novembre
  2013 al 31 ottobre 2014**"*

| `meseri` | months | calendar year | rows | share |
|---|---|---|---|---|
| 1 | Nov, Dec, **Jan** | 🔴 **2013 / 2014 — STRADDLES** | 293,651 | 27.2 % |
| 2 | Feb, Mar, Apr | 2014 | 272,625 | 25.3 % |
| 3 | May, Jun, Jul | 2014 | 256,793 | 23.8 % |
| 4 | Aug, Sep, Oct | 2014 | 254,588 | 23.6 % |

**Bounds, stated as bounds:** 2014 is **at least 72.8 %** and 2013 **at most 27.2 %**. Under an
equal-months assumption inside `meseri=1` the split would be ≈ 81.8 % / 18.2 %, but **the delivery ships
no month field for the daily diary**, so that figure is an interpolation and must never be quoted as a
measurement.

### 1.4 The harmonised corpus can be repaired without re-running Step 2

`strat_season_raw` was checked against the raw codes and is the **same variable** — shares agree to
under 0.3 pp on `es` and under 0.1 pp on `it`. So:

| fold | how the year attaches | cost |
|---|---|---|
| `es` | pure value map on the existing column: `{1,2,3} → 2010`, `{4} → 2009` | **free**, no join, no re-run |
| `it` | same map for `{2,3,4} → 2014`; `{1}` stays **ambiguous by construction** | free, but one quarter unresolved |
| `uk` | join `dyear` on `(serial, pnum, daynum)` — `hid` **is** `serial` and `pid` **is** `serial_pnum`, verified | small join, no re-run |

---

## 2. What is now actually being decided

An EPW is one year and a cell needs exactly one. The recovered facts do **not** by themselves choose it.
Options remain, but they are no longer the same three:

| | option | what it costs | what it buys | changed by §1? |
|---|---|---|---|---|
| **(A)** | **Pin the majority year per fold: `es` 2010, `uk` 2014, `it` 2014** | nothing | one EPW per fold; the contract can be signed today | 🟢 **yes — this used to be a bare convention (old option c) and is now a documented majority with a measured share** |
| **(B)** | **Carry the year as a design factor and run both** | doubles the weather axis (not the campaign) | cannot invent an answer; a sensitivity margin falls out for free | unchanged, still the strictly-honest option |
| **(C)** | **Assign each diary its own year and use the matching EPW** | a real change to what a cell *is* — weather stops being a fold constant | maximum fidelity | 🟢 **newly POSSIBLE** — it was not on the table before §1, because the year did not exist per record |

🔴 **The recommendation is (A), and the reason is stated rather than assumed.** The majority is decisive
on `es` (76.8 %) and on `it` (≥ 72.8 %), and merely clear on `uk` (58.1 %). It is the only option that
does not change what a Step 10 cell is — and `H10` is a pre-declared hypothesis about `N_u`, the number
of independently diarised dwellings, **not** about weather. Spending the weather axis on a year contrast
buys precision on a variable the pre-declared hypothesis does not test.

⚪ **(B) is the right fallback if `uk`'s 58/42 is judged too close to call**, and it is the only option
under which a reviewer's *"why that year?"* has a numerical answer rather than a rule. It doubles the
weather axis only; it does not double the campaign.

🔴 **(C) is recorded because it is now possible, not because it is recommended.** Under (C) weather
ceases to be constant within a fold, so an `N_u` effect and a year effect become confounded inside the
same cell — which is precisely the class of confound work item 10.3 exists to remove. **Choosing (C)
would re-open a confound this project has already paid to close.**

---

## 3. What the author is being asked to rule

1. **(A), (B) or (C)?** Recommended: **(A)**.
2. **If (A): is `uk` at 58.1 % close enough to pin, or does `uk` alone go to (B)?** A per-fold split
   answer is legitimate — nothing requires the three folds to take the same option.
3. **`it`'s straddling quarter.** Under (A) it is absorbed (the fold pins to 2014 anyway and `meseri=1`
   is a minority of a minority). Under (B) or (C) it needs its own rule, and 🔴 **the delivery cannot
   supply one** — there is no month field on the Italian daily diary.

---

## 4. What was NOT done, and why

* ⚪ **Nothing was written to `harmonised_*.parquet`.** The mapping in §1.4 is specified and verified but
  deliberately not applied — applying it before the ruling would bake option (A) into the corpus silently.
* ⚪ **No threshold, gate or `prereg.md` field was touched.** md5 `e4243e07cdd80c9c846b91f40e3e8c45`
  unchanged. This decision sits upstream of every gate.
* ⚪ **The `anno` trap was filed, not stepped in.** A future reader of the Italian delivery will find a
  four-digit `anno` column that looks exactly like a diary year and is not one. §1.3 exists so the next
  agent does not have to rediscover it.
* 🔴 **This document does not rule anything.** It converts an *unanswerable* decision into an *answerable*
  one and hands it back. The block on the OpenUBEM contract freeze lifts **only** with the ruling in §3,
  not with this file.

---

## 5. Evidence — every claim above, and where it came from

| claim | source, read directly |
|---|---|
| `es` `TRIM` value labels name the year | `raw/spain/unpacked/DISEnOS DE REGISTRO EET 2009 2010.xlsx`, `xl/sharedStrings.xml` |
| `es` fieldwork 1 Oct 2009 – 30 Sep 2010 | `raw/spain/meth_t25304471.pdf` p. 14 |
| `es` `TRIM` counts | `raw/spain/unpacked/DIARIO2.TXT`, character position 8, 2,778,480 slots |
| `uk` `dyear` exists at position 18 | `.../UKDA-8128-tab/mrdoc/allissue/uktus15_diary_ep_long_ukda_data_dictionary.rtf` |
| `uk` year split, 16,533 diaries | `.../UKDA-8128-tab/tab/uktus15_diary_ep_long.tab`, de-duplicated on `(serial, pnum, daynum)` |
| `it` `anno` is constant 2013 | `.../MICRODATI/uso_tempo_Microdati_Anno_2013_DiarioGiornaliero.txt`, col 2, all 1,077,657 rows |
| `it` `meseri` month groups | `.../Classificazioni/uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_var3.html` |
| `it` fieldwork 1 Nov 2013 – 31 Oct 2014 | `.../METADATI/uso_tempo_NotaMetodologicaIndagine_Anno 2013.pdf` p. 8 |
| harmonised `strat_season_raw` = the raw code | `Step2_docs/outputs_step2/harmonised_{es,it,uk}.parquet`, shares compared to raw |
| `hid` = `serial`, `pid` = `serial_pnum` | same parquet, `hid=11011202`, `pid=11011202_1` |

⚪ Raw root on this workstation: `C:\Users\o_iseri\Desktop\GSSCanada\_local_runs\4J\raw\{spain,uk,italy}\`.

---

## 6. AUTHOR'S RULINGS & DIRECTIVES (`D-S10-1`)

| # | Question / Item | Ruling | Adopted Specification | Rationale & Directives |
|---|---|---|---|---|
| **1** | Overall Strategy | 🟢 **Option (A)** | **Pin the majority calendar year per fold: `es` 2010, `uk` 2014, `it` 2014.** | Empirically grounded by raw microdata (`es` 76.8% in 2010; `uk` 58.1% in 2014; `it` $\ge 72.8\%$ in 2014). Preserves within-cell weather constancy for OpenUBEM scaling experiments ($N_u$). |
| **2** | `uk` Majority Case | 🟢 **Pin to 2014** | `uk` pinned to 2014 (58.1%) alongside `es` (2010) and `it` (2014). | Keeps a consistent single-year convention across all 3 folds, avoiding an asymmetric split design. |
| **3** | `it` Straddling Quarter | 🟢 **Absorbed into 2014** | `it` pinned to 2014; `meseri=1` (Nov 2013 – Jan 2014) is absorbed into the majority year. | Avoids unmeasured interpolation since ISTAT microdata does not provide individual diary months. |

### Formal Directives for Steps 10 & 11 and OpenUBEM Freeze:
1. **Lift OpenUBEM Contract Freeze**: The OpenUBEM boundary-contract freeze (MVP §12.8, `FINDING EU-S2-03`) is hereby **LIFTED**. Steps 10 and 11 are unblocked to proceed under the majority-year convention.
2. **Corpus Attachment**: Apply the clean value maps from §1.4 (`es`: `{1,2,3} → 2010, {4} → 2009`; `it`: `{2,3,4} → 2014, {1} → 2013/2014`; `uk`: join `dyear`) to enrich the metadata without altering the underlying harmonised schema or invalidating Step 2 gates.
3. **Scientific Reporting**: Document the exact empirical year distributions in the manuscript methods and declare the majority-year convention as a pre-registered design invariant.

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` remains strictly frozen. Decision `D-S10-1` is formally resolved and closed.
