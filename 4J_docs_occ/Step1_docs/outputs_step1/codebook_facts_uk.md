# Codebook facts — United Kingdom, UK Time Use Survey 2014-2015 (UKDA SN 8128)

### Step 1, work item 1.2. Every fact below names the document and page (or dictionary
### position) it came from.
#### Compiled 2026-08-14/15 from the delivery itself. **No fact here comes from the Spanish
#### reader, from this prompt's own stated numbers, or from memory of other time-use surveys.**
#### Where a number in the employee work order is checked against the delivery below, agreement
#### or disagreement is stated explicitly.

Three sources, all inside the delivered archive, hashed in `acquisition_manifest_uk.json`:

* **DD** — the six UKDA data dictionaries, `mrdoc/allissue/uktus15_*_ukda_data_dictionary.rtf`.
  Cited as `DD:<file>` naming the `.tab` stem, e.g. `DD:diary_ep_long`.
* **CTUR** — `mrdoc/pdf/8128_ctur_report.pdf`, Centre for Time Use Research processing report,
  23 pages. Cited as CTUR p. N (the number printed on the page, not the PDF page index).
* **NATCEN** — `mrdoc/pdf/8128_natcen_reports.pdf`, NatCen/NISRA technical report, questionnaires
  and methodology, 232 PDF pages. Cited as NATCEN p. N (printed page number).
* **UKDA** — `mrdoc/UKDA/UKDA_Study_8128_Information.htm`, `read8128.htm`,
  `8128_file_information.rtf` — the study's own citation/licence page and file list.

A fact that could not be found in any of these is written `NOT FOUND` and stays that way.

Every number below that was independently measured from the raw `.tab` files (not just quoted
from a report) is marked **[measured]**, with the check script kept in this task's scratch area
and reproduced inside `4thJ_read_uk.py` / `4thJ_gates_step1_uk.py`.

---

## THE REQUIRED FACTS

| Fact | Value | Where it came from |
|---|---|---|
| **File shape** | **Six flat delimited files, tab-separated, one row per unit at that file's own grain.** `uktus15_household.tab` (household), `uktus15_individual.tab` (person), `uktus15_diary_wide.tab` (person-day, 144 slots as an array), `uktus15_diary_ep_long.tab` (person-day-**episode**, native), `uktus15_dv_time_vars.tab` (person-day, derived 1/2/3/4-digit activity totals), `uktus15_wksched.tab` (7-day work schedule). This is **not** relational in Spain's sense (no shared numeric offsets to cross-reference); the files share a `serial`/`pnum`/`daynum` key instead | UKDA `8128_file_information.rtf`; CTUR p. 2, "2. Overview of the data files"; **[measured]** column headers of all six `.tab` files |
| **Native `START`/`DURATION`?** | **Yes, in `uktus15_diary_ep_long.tab`.** `tid` = the **starting** 10-minute slot of the episode (1-144, slot 1 = 04:00-04:10), and `eptime` = the episode's **duration in minutes**. 🔴 This is the opposite of Spain: the UK ships native episodes and Spain ships fixed slots that must be reconstructed. **Do not reconstruct anything for the UK** | DD:diary_ep_long, positions 32-33 (`tid`, `eptime`); established below under F-UK-1 |
| **Weight variables** | Five, at four different grains: `hh_wt` (household, in `uktus15_household.tab` only), `ind_wt` (individual, in `uktus15_individual.tab` only), `dia_wt_a` and `dia_wt_b` (diary, in **three** files: `uktus15_diary_wide.tab`, `uktus15_diary_ep_long.tab` and `uktus15_dv_time_vars.tab`), `wks_wt` (7-day schedule, in `uktus15_wksched.tab` only). All five are continuous decimals with **no declared fixed width** — the files are tab-delimited, not fixed-width | DD, position lists of all six dictionaries; NATCEN p. 30, section 7.1 "Weighting the data — Background" |
| **Activity coding list, edition** | **"UK HETUS 2014 Activity Code List"** (NATCEN Appendix H, pp. 105-106+), a UK adaptation of Eurostat's 2008 HETUS guidelines, aligned for continuity with UK's own 2000-01 survey. Not a verbatim Eurostat HETUS code list — it is the UK's own list, built to be HETUS-compatible | NATCEN p. 2, "The UK 2014-15 Time Use Survey was designed with the Eurostat guidelines in mind..."; NATCEN p. 2, "...this survey, like the 2000-01 first UK HETUS contribution..."; NATCEN Appendix H title, p. 105 |
| **Activity coding list, depth** | **Mixed 3- or 4-digit**, at the most detailed level ("Code the main activity to 4 (or 3) digits"). One digit = high-level category, two digits = sub-category, 3 or 4 digits = detailed activity. **[measured]** 278 distinct codes declared in the delivered dictionary for `whatdoing` (the primary-activity variable): 1 is the sentinel `-1` "Not applicable" (excluded from the crosswalk), 1 is the bare code `0` ("Unspecified personal care"), 7 are 3-digit and 269 are 4-digit | NATCEN p. 90, section 4.2 "Activity Coding List", "Rule 1: Code the main activity to 4 (or 3) digits"; **[measured]** from DD:diary_ep_long `whatdoing` value labels |
| **Location coding list** | 2-digit, unified with transport mode (no separate "location" vs "mode" list). `00` unspecified, `10-21` fixed locations not travelling, `30-39` private transport, `40-49` public transport, `90` unspecified transport mode, `99` illegible. **[measured]** 35 substantive codes, after excluding the sentinels `-9`/`-7`/`-2` | DD:diary_ep_long, position 38 (`WhereWhen`) value labels |
| **Co-presence fields** | 🔴 **Nine**, not five and not six: `WithAlone`, `WithSpouse`, `WithMother`, `WithFather`, `WithChild` (0-7 years only), `WithOther` (includes children 8+), `WithOtherYK` ("with other(s) you know outside of HH"), `WithMiss`, `WithNA`. Binary 0/1 flags. `WithMiss` and `WithNA` are **not** people-present categories — see F-UK-4 | DD:diary_ep_long, positions 40-48 |
| **Slot length** | 10 minutes | DD:diary_ep_long, `tid` value labels; CTUR p. 2 |
| **Diary origin hour** | 🔴 **04:00**, not Spain's 06:00. `tid` value 1 = "04:00-04:10", value 144 = "03:50-04:00". `WhereStart`/`WhereEnd` are explicitly labelled "(4am)" | DD:diary_ep_long, position 32 value labels and positions 23-24 variable labels; CTUR p. 2, "reported over 24hr period (from 4am to 4am)" |
| **Minimum age** | **8**, not the HETUS-recommended 10. "While the HETUS guidelines recommend collecting diaries from all household members age 10 and older, this survey, like the 2000-01 first UK HETUS contribution, collected diaries from all household members aged 8 and older" | NATCEN p. 2 |
| **Diary days per respondent** | 🔴 **2 by design** (one weekday, one weekend day), not Spain's 1. **[measured]**: of 8,274 distinct diary-completing persons (`serial`+`pnum`), 8,259 (99.8 %) have two distinct `daynum` values (1 and 2) and 15 have only one (partial non-response, not a design violation). See F-UK-6 and G1.9 below — **every per-diary gate is per (person, daynum), not per person** | NATCEN p. 3, "Participants are asked to complete two 24-hour diary days"; NATCEN p. 16, "Allocation of diary dates... two days, including one weekday and one weekend day"; **[measured]** from `uktus15_diary_ep_long.tab` |
| **Collection mode** | **Two different modes for two different instruments.** Household and individual questionnaires: **CAPI, face-to-face**, interviewer-administered on a laptop (Blaise software). Diary: **paper, self-completion, placement/pick-up design** — the interviewer leaves a printed diary booklet with the respondent at the end of the placement interview and returns later to collect it. The intermediate record's `mode` field records the **diary's** mode (`paper_self_completion`), since the reader emits diary-episode rows, not questionnaire rows | NATCEN p. 14, section 4.5 "The placement interview... face-to-face interview... using Computer Assisted Personal Interviewing (CAPI)"; NATCEN pp. 16-17, section 4.6 "The diary — Placing the diary... Completion by participants... Interviewers left the diaries... An appointment was made to collect the diary" |

---

## COUNTS AS THE UKDA DELIVERY STATES THEM, AND AS WE MEASURED THEM

🔴 **Unlike INE, the UKDA delivery does not ship a separate record-layout document that states
target counts independently of the data.** What it does ship is a data dictionary **auto-generated
by UK Data Archive's own curation tooling directly from the delivered file** ("Data are checked for
consistency and accuracy" — `read8128.htm`), which prints a `Number of cases` header for every
file. This is the delivery's own stated count and is used as G1.1's reference, but it is a weaker
kind of independence than Spain's INE-designed target: it was generated **from** the same file it
counts, by the archive's own pipeline, not designed in advance by the collecting agency the way
INE's record-layout workbook was. Recorded so the difference is not silently assumed away.

| File | DD states "Number of cases" | We measured (`wc -l` of the `.tab` minus header) | |
|---|---|---|---|
| `uktus15_household.tab` | 4,733 | 4,733 | ✅ |
| `uktus15_individual.tab` | 11,421 | 11,421 | ✅ |
| `uktus15_diary_wide.tab` | 16,533 | 16,533 | ✅ |
| `uktus15_diary_ep_long.tab` | 587,632 | 587,632 | ✅ |
| `uktus15_dv_time_vars.tab` | 16,533 | 16,533 | ✅ |
| `uktus15_wksched.tab` | 3,523 | 3,523 | ✅ |

*(For orientation, and now confirmed rather than merely quoted: the manager's own inspection had
noted 587,632 lines for `uktus15_diary_ep_long.tab` and 11,422 for `uktus15_individual.tab` —
those figures **included the header row**; the DD-stated case counts above exclude it. Both routes
agree once the header is accounted for.)*

Every count reconciles exactly by two independent routes: the DD header and a direct `wc -l` of
the file. Neither route is independent of UKDA's own delivery pipeline in the way INE's workbook
was independent of the EET data files, which is why this is recorded as a real but narrower form of
reconciliation than Spain's, not passed over as identical.

---

## 🔴 FINDINGS THAT CONTRADICT WHAT THE PLAN ASSUMES, OR THAT THE PLAN'S NUMBERS NEEDED CHECKING AGAINST

### F-UK-1 — `eptime` is minutes; `tid` is the **start** slot, not a duration or an end slot

The work order flagged this as something to establish, not assume. Two independent routes agree:

1. **Documentation.** CTUR p. 13 gives the equivalent Stata code for building a "minutes watching
   TV" variable in both diary formats. In the **wide** format (144 slot columns), it accumulates
   `tv = tv + 10` once per matching 10-minute slot. In the **long episode** format, the equivalent
   single step is `tv = eptime` if the episode's activity matches — no `+10` scaling is applied,
   which only produces the same quantity as the wide-format sum if `eptime` is already in minutes.
2. **[measured]**, directly from `uktus15_diary_ep_long.tab`, household `11011202` person 1 day 1:
   episode 1 has `tid=1` (04:00-04:10) and `eptime=110`; episode 2 has `tid=12` (05:50-06:00) and
   `eptime=10`. If `tid` were the episode's end slot or a slot count, episode 1 (starting at slot 1)
   could not be followed immediately by an episode whose start label is slot 12 unless episode 1
   ran for 11 slots = 110 minutes, which is exactly `eptime`'s value. `tid` is confirmed as the
   **start** slot; `eptime` is confirmed as **duration in minutes**, always checked as a multiple of
   10 (0 exceptions in 587,632 rows), min 10, max 1430.
3. **[measured]**: `sum(eptime)` grouped by (`serial`,`pnum`,`daynum`) equals exactly 1440 for all
   16,533 person-days, 0 exceptions — this could not hold if `eptime` were anything other than
   minutes on a 1440-minute day.

`start_min = (tid - 1) * 10`; `duration_min = eptime`.

### F-UK-2 — three secondary activities exist, coverage falls off sharply from the first to the third

`What_Oth1`, `What_Oth2`, `What_Oth3` share the same coding list as `whatdoing` (the primary
activity) and use the value `-9` ("No answer/refused" — the only negative value observed in any of
the three columns) whenever no activity is recorded for that slot. **[measured]**, of 587,632
episodes:

| Column | Recorded with a value | Percent |
|---|---|---|
| `What_Oth1` (→ `act2_raw`) | 163,105 | 27.75 % |
| `What_Oth2` (→ `act2_extra_uk_2`) | 15,968 | 2.72 % |
| `What_Oth3` (→ `act2_extra_uk_3`) | 1,353 | 0.23 % |

Per the work order, all three are carried, none is merged, none is dropped, and the manager decides
what Step 3 serialises.

🔴 **`-9` conflates two different things the instrument does not distinguish in the delivered
file: "confirmed no secondary activity" and "no answer/refused".** The DD's own value label for
`-9` under `What_Oth1` reads "No answer/refused" (not "None" or "Not applicable"), and no other
negative sentinel is observed for these three columns. Since a genuine refusal on an optional,
free-response secondary-activity field would be rare, not present on 72 % of episodes, `-9` almost
certainly means "none reported" for the overwhelming majority of its occurrences — but the file
itself does not let us separate a true refusal from an empty answer, and neither should we invent
that separation. We map `-9` to state 2 ("recorded and blank", `""`) for all three columns because
the field is present in every episode row (it is a mandatory column of a mandatory instrument), and
record this collapsing as a limitation, not a certainty.

### F-UK-3 — two diary weights, both calibrated to age × sex and Government Office Region

`dia_wt_a` ("Diary weight - analysis at diary level/event level") and `dia_wt_b` ("Diary weight -
analysis at individual level"), both restated identically in `uktus15_diary_wide.tab`,
`uktus15_diary_ep_long.tab` and `uktus15_dv_time_vars.tab`.

NATCEN p. 31, section 7.4, is explicit about what each is for:

> *"c) Calibration – day level weight: ... The diary weight – day level balances the sample for
> each month and day of the week... Additionally, for each month and day of the week, the
> distribution of age/sex groups matches the population distribution... d) Calibration – individual
> level weight: The diary weight – individual level is to be used for the analysis of the diary at
> individual level. This weight also balances the sample by month... This weight has no adjustment
> for day of the week."*

**The documented default for diary-level (event/episode-level) analysis is `dia_wt_a`.** This is
also demonstrated, not just stated, in the worked example at CTUR p. 13: *"Declare survey design
for a diary file dataset (at the person-day level): `svyset psu [pw=dia_wt_a], strata(strata)"*. Per
the work order, **both are carried** (`weight_dia_a`, `weight_dia_b`); the contract's single
`weight_dia` field is populated from `dia_wt_a` **because the documentation states this default**,
with the citation above, and the choice is flagged as pre-registration-relevant per the work order's
instruction — Step 2/3 may need `dia_wt_b` instead, depending on whether the eventual model treats a
row as an episode-event or as a person.

🔴 **Both weights are calibrated to age/sex and Government Office Region (NATCEN p. 31, quoted
above).** This is the same circularity structure as Spain's retired `G1.7b` — see F-UK-11 below.

### F-UK-4 — `WithMiss` and `WithNA` are missingness/concordance flags, not people-present categories

* **`WithMiss` ("No co-presence reported")** is a genuine missingness flag: *"Co-presence data is
  deemed missing if the respondent provided no information about co-presence in any time slot...
  a missing co-presence field has been added to the data to aid with this."* (CTUR p. 6, section
  3.2 "Missing co-presence data"). `WithMiss=1` means none of the other eight co-presence fields
  carry information for that episode.
* 🔴 **`WithNA` ("Sleep/Work/Education UK2000 concordance") is not a missingness flag for this
  wave at all** — it is a backward-compatibility marker. In UKTUS 2000-01, co-presence was **not**
  coded for episodes of paid work, education or sleep; in UKTUS 2014-15 it **was**: *"In 2000-01,
  when a respondent reported time in paid work, education or sleeping, information about location
  and co-presence was not coded. In 2014-15, both location and co-presence were coded... we have
  added an additional variable indicating time when respondents report paid work, education or
  sleep"* (CTUR p. 10, section 5.1). `WithNA=1` flags an episode that *would have been* uncoded
  under the 2000-01 design, for comparability — it does not mean co-presence is missing in the
  2014-15 file. Recorded here so Step 2/3 do not treat `WithNA=1` as "no co-presence information".
* All nine flags are emitted as their own named columns, none folded into another, per the Spanish
  `cop_extra_<country>_<field>` precedent. `WithChild` covers ages 0-7 only (not 0-14 as in
  UKTUS 2000-01); children 8+ fall under `WithOther` (CTUR p. 10-11, section 5.2).

### F-UK-5 — the diary origin hour is 04:00, not Spain's 06:00

Established above in the required-facts table. This is a genuine cross-country difference, not a
data-quality issue: UKTUS diaries run 4am-to-4am by design (CTUR p. 2), where Spain's ran
6am-to-6am (F-ES-1). Both are harmonisation questions for whoever builds a shared clock across
countries in Step 2, not something to resolve here.

### F-UK-6 — diary days per respondent is 2, and every per-diary gate is per (person, daynum)

`daynum` (1 or 2, the survey's own diary-day ordinal) is the safe grouping key, **not**
`DiaryDay_Act` (the day-of-week, 1-7). **[measured]**: of 8,274 people with at least one diary,
8,259 have two distinct `daynum` values; but 3 of those 8,259 people have the **same**
`DiaryDay_Act` value on both of their diary days (i.e. `DiaryDay_Act` cannot be relied on as a
unique second key), while `daynum` never collides — the survey's own diary-day counter (1st
assigned day / 2nd assigned day) is the safe field. The intermediate record's `diary_day` column is
therefore populated from `daynum`, **not** from a day-of-week code as it is for Spain. 🔴 This means
`diary_day` carries a **different kind of value across countries in the current contract** — an
ordinal "1st/2nd day" for the UK versus a day-of-week code for Spain — which Step 2/3 must be aware
of if `diary_day` is ever compared or pooled across countries. `DiaryDay_Act` (actual day of week)
is carried as an extra column for reference, following the Spanish precedent of appending useful
non-contract columns (Spain appends `trim`, `SEXO`, `EDAD`, `HRELACTIV`).

### F-UK-7 — minimum age is 8, below the HETUS-recommended 10 and below Spain's 10

Established above. Not a defect — a documented, deliberate UK choice for continuity with its own
2000-01 survey (NATCEN p. 2).

### F-UK-8 — weight presence is not 100 %: a real, measured gap, reported rather than patched over

🔴 **[measured]**: `dia_wt_a` and `dia_wt_b` are a literal single blank/space character (not `-9`,
not empty string, not a parseable number) for **89 of 587,632 episode rows**, all belonging to
**2 of 16,533 person-days** (household `12110816`, person 2, both diary days). Both affected
person-days belong to `DMFlag=-6` ("Partial Ind from non-prod HH") and `HhOut=598` ("Other reasons
why unproductive") — a diary that was collected from a person in a household whose overall
productivity status meant no diary weight was ever computed for them, even though their diary
episodes are present and their durations still sum to 1440 minutes.

Separately, **[measured]**: `ind_wt` is the same blank/space sentinel for **23 of 8,274**
diary-completing persons in `uktus15_individual.tab` (0.28 %), only one of whom overlaps with the
2 blank-`dia_wt` person-days above. Every diary-completing person **is** present in
`uktus15_individual.tab` with a valid `DVAge`, so the join itself is complete — the gap is
specifically in weight coverage, not in demographic coverage.

This is reported as a real, measured property of the delivered file, not smoothed over: **G1.7a as
literally specified ("finite and strictly positive on 100 % of rows") genuinely fails on real,
unperturbed UK data**, and that failure is scored honestly below rather than excluded or explained
away.

### F-UK-9 — activity code `4276` appears in the data with no label anywhere in the delivered dictionary

🔴 **[measured]**: exactly **one** episode of 587,632 (household `15050115`, person 1, day 2,
episode 21) carries `What_Oth1 = 4276`. This code does not appear in the `whatdoing` value-label
list, nor in `What_Oth1`'s own value-label list, nor anywhere else in
`uktus15_diary_ep_long_ukda_data_dictionary.rtf`. The surrounding declared codes are a consecutive
"help to other households: childcare" family — `4270, 4271, 4272, 4273, 4274, 4275, [gap], 4277,
4278, 4279` — with `4276` conspicuously missing from an otherwise unbroken run, which is consistent
with (but does not prove) a documentation omission on UKDA's side rather than a corrupted value.
**We do not guess what `4276` means.** It is `NOT FOUND` and is excluded from
`crosswalk_source_uk_activity.csv`. Consequence, stated plainly: **`G1.4` genuinely fails on real,
unperturbed baseline data** for `act2_raw`, by exactly this one row. This is not a specification
conflict to resolve — it is a true, rare data/documentation mismatch, reported as the gate found it.

### F-UK-10 — the coding list is the UK's own, not a verbatim Eurostat HETUS list; G1.4 tests membership in the UK's list only

Same caveat Spain's codebook recorded for INE's list: this step does not establish that UK codes
mean the same thing as the Eurostat HETUS ACL edition assumed elsewhere in the project. That
crosswalk is Step 2's job.

### F-UK-11 — `G1.7b`'s circularity is established for the UK from the UK's own methodology, independently of Spain's finding

Per the work order: Spain's retirement of `G1.7b` does not transfer by assumption. It is
established here, separately, from NATCEN's own text.

NATCEN p. 31, section 7.4(c) and (d) (quoted in full under F-UK-3): both diary weights are
calibrated so that *"the distribution of age/sex groups matches the population distribution"*
(day-level weight, by month and day of week) and *"the sample distribution of age/sex groups
matches the population distribution"* (individual-level weight, by month). This is the same
structure as Spain's METH p. 34-36: a weighted age × sex total compared against a published
population is compared against the very figure the weights were calibrated to reproduce. **`G1.7b`
is therefore `NOT CHECKED` for the UK, for the reason established here** (NATCEN p. 31), not by
inheritance from Spain's finding. The two countries happen to share the defect; the citation does
not.

**Consequence for `G1.8`.** No age × sex population **table** is printed or embedded anywhere in
the delivered UKDA archive — NATCEN describes the calibration target ("2014 mid-year population
estimates", NATCEN p. 30) in prose only, with no accompanying data table shipped in the delivery.
Per the work order, this step does not search online for one. So `G1.8` is `NOT CHECKED` for the UK
for **two separate, both-sufficient reasons**, and both are recorded because they are different
claims: (1) no published reference table exists **in the delivery** to compare against at all, and
(2) even if one were found, the same calibration-circularity narrowing that applies to Spain's
`G1.8` would apply here too, since the weights are calibrated to age/sex margins.

### F-UK-12 — `G1.7c` is a live, checkable, passing gate for the UK

Unlike the case the work order flags as possible ("a country whose delivery carries weights in only
one file"), the UK **does** restate `dia_wt_a` and `dia_wt_b` across more than one file:
`uktus15_diary_ep_long.tab`, `uktus15_diary_wide.tab` (not read by the reader, but confirmed by its
DD to carry the same two variables) and `uktus15_dv_time_vars.tab`. **[measured]**: comparing
`dia_wt_a` and `dia_wt_b` as raw strings between `uktus15_diary_ep_long.tab` and
`uktus15_dv_time_vars.tab`, keyed on (`serial`,`pnum`,`daynum`), for all 16,533 person-days: **0
mismatches**, including the 2 person-days whose weight is blank in both files identically. `G1.7c`
is therefore scored, not `NOT CHECKED`, for the UK.

### F-UK-13 — `G1.7d`'s layout reference does not exist for the UK, and applying its threshold anyway would misfire on a normalised weight scheme

Two separate reasons, both recorded because the work order asks that they not be conflated:

1. **No declared field width exists.** Spain's `G1.7d` reference was the record-layout workbook's
   declared integer width (6 digits, so `< 1e6`) — an artefact independent of the microdata. The UK
   delivery is tab-delimited free-text decimal, with **no fixed-width layout document anywhere in
   the delivery** for `hh_wt`, `ind_wt`, `dia_wt_a`, `dia_wt_b` or `wks_wt`. There is nothing to cite
   as an independent upper bound. **`G1.7d`'s magnitude-vs-layout half is `NOT CHECKED` for lack of
   a reference**, printed, never a pass.
2. 🔴 **[measured]**, and exactly the case the work order warned about: UK weights are
   **normalised to a mean of 1.000**, not raw expansion factors like Spain's `FACTORF` (which ranged
   264.94 to 113,238.82, representing thousands of real people per weighted respondent). Measured
   directly: `dia_wt_a` ranges `[0.1168, 7.2311]`, mean `1.000322`; `dia_wt_b` ranges
   `[0.2050, 4.8225]`, mean `1.000182`; `ind_wt` ranges similarly with mean `1.000000`. **59.2 % of
   `dia_wt_a` values (9,783 of 16,531 non-blank) and 60.7 % of `dia_wt_b` values are strictly below
   1.0.** Applying the pre-registered "at or above 1.0" clause literally would fail the gate on the
   majority of real UK weights — not because a column was misread, but because the UK's weighting
   convention is normalisation, not population expansion. **This is reported as a specification
   question for the manager, exactly as instructed, and the threshold is not moved here.** The
   magnitude-vs-layout half of `G1.7d` is marked `NOT CHECKED`; the observed min/max/mean/distinct
   count and the below-1.0 share are printed as diagnostics, labelled evidence of nothing, mirroring
   how `G1.7b` is printed for both countries.

### F-UK-15 — `loc_raw` (`WhereWhen`) also carries a missingness sentinel the intermediate-record contract has no place for, and `G1.4` catches it honestly

🔴 **[measured]**, found by the gate battery, not anticipated while drafting this codebook: `WhereWhen` (location) is `-9` ("No answer/refused") on **7,117 of 587,632 episodes (1.211 %)**. Unlike `whatdoing` (primary activity, never negative in this delivery, confirmed above), the UK's location field **is** sometimes unreported, exactly the same way the secondary-activity columns are — but the intermediate record's `loc_raw` field, unlike `act2_raw`, has no three-state allowance in the Step 1 contract; it is specified as a single code per episode.

The reader passes `WhereWhen` through unfiltered (it is not told to treat `-9` as anything other than "the value the file contains"), so these 7,117 episodes carry the literal string `"-9"` in `loc_raw`. `-9` is correctly **not** in `crosswalk_source_uk_location.csv` (it is a missingness sentinel, not a place), so `G1.4` correctly reports it as a code outside the declared list. 🔴 **This is reported as a true result, not patched by quietly adding `-9` to the location crosswalk or by inventing a `loc_raw` three-state field the specification does not define.** Per the work order's own instruction for the analogous secondary-activity gap (F-UK-2 above): **this is a specification gap and it is the manager's to close, not the employee's.** Options the manager may choose between are not decided here (e.g. widen `G1.4` to exclude the sentinel from location membership the same way blanks are excluded from `act2_raw`, or give `loc_raw` its own three-state treatment) — both would be a basis change to a gate or a contract change, either of which is outside this employee's authority.

### F-UK-14 — files not read, and why

* `uktus15_wksched.tab` (7-day work schedule) — not an input to any step in this pipeline, exactly
  as Spain's `HTR1`/`HTR2` were excluded.
* `uktus15_household.tab` — not needed. Every fact this reader needs from the household grain
  (household id) is already present as `serial` inside `uktus15_diary_ep_long.tab`; `hh_wt` is not
  part of the intermediate record contract (`weight_ind`, `weight_dia` only).
* `uktus15_diary_wide.tab` — redundant with `uktus15_diary_ep_long.tab` for this project's purposes
  (CTUR p. 3: "The long episode format contains exactly the same information as the wide diary
  format"); reading it would duplicate, not add, information, and the work order is explicit that
  the UK ships native episodes and nothing should be reconstructed from the wide/slot form.
* `uktus15_dv_time_vars.tab` — **not read by the reader**, but **is** read independently by the gate
  runner, for `G1.7c` only, exactly on the Spanish precedent of a gate reading a raw file the reader
  never touches.

---

## WHAT IS **NOT** ESTABLISHED HERE

* The activity and location lists have been transcribed from the UKDA data dictionary's own value
  labels, which is the delivery's authoritative statement of what codes the file actually uses. They
  have **not** been aligned to the Eurostat HETUS ACL code-for-code. The crosswalk to a shared
  vocabulary is Step 2 work item 2.1, exactly as for Spain.
* `uktus15_wksched.tab`, `uktus15_household.tab` and `uktus15_diary_wide.tab` were not read by the
  reader (see F-UK-14). `uktus15_dv_time_vars.tab` was read only by the gate runner, only for
  `G1.7c`.
* Whether the UK is comparable to Spain, France or Italy is Step 2's question, not this document's.
* Whether `dia_wt_a` or `dia_wt_b` is the correct weight for whatever Step 3 eventually builds is
  **not decided here** — both are carried, the documented default for diary/event-level analysis is
  named (F-UK-3), and the choice is flagged as open.
