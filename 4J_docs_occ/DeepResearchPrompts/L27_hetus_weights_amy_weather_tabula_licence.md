# L27. Three documents we need and cannot get from the data: the HETUS weighting rule, the fieldwork calendars plus an open actual-year weather source, and TABULA's licence

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.

---

## 🔴 CORRECTIONS TO THE MASTER BRIEF — READ THESE BEFORE THE BRIEF ITSELF

1. **The corpus is HETUS only.** Canada and the United States are out of the paper.
2. **One survey wave per country, not several.**
3. 🔴 **The corpus is THREE countries: Spain 2009-10, United Kingdom 2014-15, Italy 2013-14.** France
   was excluded on 2026-08-15.
4. **There is no forecast and no temporal claim anywhere in the paper.**
5. **The fine-tuned model will never be released.**

---

## 🔴 READ THIS FIRST: WHAT IS ALREADY RULED AND IS NOT UP FOR DISCUSSION

Three decisions are frozen. **Do not recommend an alternative to any of them.** Recommending one is a
mandatory negative control below.

| | ruled | date |
|---|---|---|
| **scoring weight** | Step 6 scores on `weight_dia_cal`, a CALENDAR-WEEK weight. `weight_dia` is reported beside it as a declared sensitivity and never mixed into the headline. | `D-S6-4`, 2026-08-21 |
| **weather** | Each fold is simulated on the ACTUAL meteorological year covering its own fieldwork window. Not a typical year, not one shared year. | Step 8 section 6 item 6, 2026-08-21 |
| **archetypes** | TABULA / EPISCOPE, EU boundary-condition set, existing-state variant `001` only. 102 archetypes across the three folds, already extracted. | 2026-08-20 / 2026-08-21 |

**We are not asking what to do. We are asking for three documents and what they say.**

---

## Why all three at once

Each is a piece of paper we cannot derive from any dataset, each currently blocks a specific thing,
and each is small enough that splitting them into three prompts would waste more effort than it saves.

* **Part A** closes the only item `D-S6-4` still owes.
* **Part B** is the difference between the weather ruling being a decision and it being a runnable
  design. Nothing weather-driven may be quoted until it lands.
* **Part C** has been owed since 2026-08-20 and gates PUBLICATION, not use.

---

# PART A. What weight basis were the national institutes REQUIRED to tabulate on?

## The question, in one sentence

**Do the HETUS guidelines (2000, 2008 and 2018 editions) require that a national time use survey's
published tabulations be representative of the CALENDAR WEEK, and if so, in which numbered section of
which edition is that requirement written?**

## Why it is being asked, with the measurement that provoked it

Our three folds' diary weights do not sit on the same day base. Measured on all 73,254 diaries, the
weighted share of weekday / saturday / sunday diaries is:

| fold | weekday | saturday | sunday | what that is |
|---|---:|---:|---:|---|
| `uk` | 71.45 % | 14.32 % | 14.24 % | the calendar week, 5/7 and 1/7 and 1/7 |
| `es` | 50.00 % | 25.00 % | 25.00 % | an equal-thirds-of-a-week-type design |
| `it` | 33.33 % | 33.33 % | 33.33 % | equal thirds |

All three are exact to three decimals, so none is an accident. Only the UK is calendar
representative. Moving all three onto a calendar-week basis changes at-home time by `es` +0.947 pp,
`it` +1.300 pp and `uk` -0.003 pp, which is **country-correlated** and therefore lands directly on a
leave-one-country-out design.

We have already built `weight_dia_cal` and Step 6 scores on it. What we do not know is whether the
national institutes were **required** to publish on the calendar week and the three simply implemented
it differently, or whether the guidelines left the choice open. Those two readings need different
sentences in the paper, and only a document can decide between them.

## What we need back

1. The **exact numbered section and page** of each guideline edition that states the weighting or
   representativity requirement, quoted verbatim in its own language plus a translation.
2. Whether the requirement is on the **calendar week**, on **day types with equal weight**, or is left
   to the national institute.
3. Whether the 2008 edition, which governs Spain 2009-10, and the 2018 edition, which governs the UK
   2014-15 and Italy 2013-14, **differ** on this point. If they differ, that alone explains our table.
4. 🔴 Whether any of the three national methodology reports (INE, ONS/UKDA, ISTAT) states which basis
   its published weight is on, quoted verbatim.
5. A stable URL for each document, opened by you, plus the date you opened it.

🔴 **If the guidelines are silent, say SILENT.** A silence is a usable answer here and an invented
section number is not.

---

# PART B. The fieldwork calendars, and an actual-year weather source we are allowed to publish from

## B1. The calendars

## The question, in one sentence

**For each of the three surveys, on which calendar dates did diary fieldwork begin and end, and is
fieldwork spread evenly across the months of that window or concentrated in particular months?**

Surveys, with the identifiers we hold:

| fold | survey | wave |
|---|---|---|
| `es` | Encuesta de Empleo del Tiempo, INE | 2009-2010 |
| `uk` | United Kingdom Time Use Survey, Centre for Time Use Research, via UKDA | 2014-2015 |
| `it` | Indagine Uso del Tempo, ISTAT | 2013-2014 |

## Why it is being asked

"Diary-survey-year weather" is not yet a definite year. Every one of these windows spans parts of two
calendar years, so a rule is needed to pin each fold to twelve consecutive months. The rule we
propose, and which this report should either confirm or contradict, is: **the twelve consecutive
months that contain the most diaries.** We can measure that from our own microdata dates. What we
cannot measure is whether the published methodology says something different, and if it does, the
methodology wins.

🔴 A second reason, and it may matter more. If fieldwork is **not** evenly spread across months, then
the survey's own seasonal mix is a design artefact of the same family as the day-base table in Part A,
and it is country-correlated in the same way. Please report the monthly distribution of fieldwork if
it is published, even approximately.

## B2. The weather

## The question, in one sentence

**Which sources publish hourly actual-meteorological-year weather files for Spain 2009-2010, Great
Britain 2014-2015 and Italy 2013-2014, in EPW or in a format convertible to EPW, under a licence that
permits publishing simulation results derived from them?**

## Why it is being asked, and what the constraint actually is

The licence is the binding constraint, not the availability. We are not asking what exists. We are
asking what we may **publish results from**. Please treat "freely downloadable" and "licensed for
derived publication" as two different questions and answer both separately for every candidate.

Candidate families we already know of, listed so you do not spend effort rediscovering them. For each,
we need the licence text and its URL, not a characterisation of it:

* **ERA5 / Copernicus** reanalysis, and any EPW conversion service built on it.
* **Oikolab**, **Meteonorm**, **White Box Technologies**, and other commercial AMY vendors: what
  exactly does the licence permit for published research?
* **National meteorological services**: AEMET (Spain), Met Office / MIDAS via CEDA (United Kingdom),
  and the Italian regional or national services. State what is free, what needs registration, and what
  each licence permits.
* Any **open EPW archive** that carries actual years rather than typical years.

## B3. The station question

TABULA's typologies carry a region tag rather than a coordinate: `ES.ME`, `GB.ENG`, `IT.MidClim`. If
any published source states which climate region or reference location TABULA's national calculations
assume, that is directly useful and should be quoted. If it does not, say NOT FOUND rather than
proposing a city.

---

# PART C. TABULA's licence, in its own words

## The question, in one sentence

**Under what licence are the TABULA / EPISCOPE workbooks published, and does that licence permit
redistributing a derived parameter table with attribution?**

## Why it is being asked

We hold both workbooks and have extracted 102 archetypes from them:

```
tabula-values.xlsx      md5 7347b2cae3c4d9f5ce78221e9d5fb832
tabula-calculator.xlsx  md5 c99ddc9ffcb6dc0ae7391273d9619e37
```

An earlier report asserted that redistribution of derived tables is permitted with attribution under
the IEE / IWU terms. 🔴 **That claim was never verified and the terms were never located.** This
matters at publication, not at use: we may compute with the workbooks today regardless, but we may not
print a derived parameter table without knowing what the licence says.

## What we need back

1. The **licence text itself**, quoted, with the URL you opened and the date.
2. Whether it distinguishes **use** from **redistribution**, and whether a derived table counts as
   redistribution.
3. The **required attribution wording**, verbatim, if one is specified.
4. Whether the licence differs between the two workbooks, or between the TABULA and EPISCOPE phases of
   the project.
5. 🔴 If no licence statement can be found on the project site or in the workbooks themselves, say
   **NOT FOUND** and quote the closest thing to a terms-of-use statement that does exist. Do not infer
   a licence from the fact that the files download without a password.

---

## HOW TO ANSWER

Use `_RESPONSE_TEMPLATE.md`. In addition:

* **Open every source before citing it.** A citation to a document you did not open is the failure
  mode this project has been burned by four times.
* **Verify every DOI through CrossRef**, and check that the resolved record matches the title, the
  volume, the issue, the pages AND the first author. 🔴 `FINDING 47`: a previous report gave a
  "CrossRef-verified" DOI that resolved to an unrelated paper about passive cooling in Brazil. Title
  agreement alone is not verification.
* **`NOT FOUND` beats an invented number, a guessed section, or a plausible licence.** There is no
  penalty for a NOT FOUND in this report and there is a large one for a fabrication.
* **Never relax a requirement because our design fails it.** If the guidelines mandate something our
  corpus does not do, report the mandate.
* **No em dashes and no en dashes anywhere in the report.**
* Quote every number to the precision the source prints it at, and say what that precision is.

---

## MANDATORY NEGATIVE CONTROLS FOR THIS REPORT

Each of these is a thing a plausible report would do and which would make it useless to us. State
explicitly, in the report, that you did not do each one.

1. **Do not recommend a typical-year weather file.** The actual-year ruling is frozen. If you believe
   it is wrong, that belief goes in one clearly labelled paragraph at the very end and nowhere else.
2. **Do not recommend a weighting basis.** Part A asks what the guidelines SAY, not what we should do.
3. **Do not infer the TABULA licence from the absence of a paywall.**
4. **Do not substitute a nearby year.** If actual-year data for Spain 2009-2010 is unavailable, say
   unavailable. A 2012 file offered as "close enough" is worse than nothing, because it would silently
   become the pre-registered design.
5. **Do not give a national methodology report's prose as if it were the HETUS guidelines.** They are
   different documents and Part A asks about both separately.
6. **Do not answer Part B2 with a list of vendors and no licence text.** The licence text is the
   deliverable; the vendor list is not.
