# Abstract

Static, deterministic occupancy schedules in residential building energy simulation miss the timing of
demand, not only its annual total, and occupant behaviour became non-stationary through the COVID-19
pandemic, so the future load shape needs an explicit, stated persistence assumption rather than a single
prediction. This study builds a household-level, survey-based occupancy model for the Canadian housing
stock, checked on a held-out survey year, and carries it into paired, stock-scale building energy
simulation across several dwelling archetypes and climate zones, comparing 2022 against four stated 2030
scenarios: main persistence, partial persistence, full reversion, and a standardized-reversion check.
The household-level model is also compared against a simpler average-profile method on the same
households, and the simulated load shape is checked, not validated, against a year of measured Toronto
and Ontario electricity data. In 2022 the weekday at-home rate sits 4.73 percentage points
above its 2005-to-2015 trend. Under the main 2030 scenario, annual electricity is nearly
flat, rising 0.12 percent, while midday share rises 0.73 and load factor rises 0.49 percentage points,
both real changes. The scenario spread is real: full reversion falls 0.12 percent and the
standardized-reversion check falls 0.44 percent, while partial persistence is not distinguishable from
zero. The average-profile method shifts the annual total by about 9 percent in one cell but collapses
household-to-household peak-timing diversity almost to zero, diversity only the household-level model preserves. For
grid planning, this shift is mainly a timing question, not a sizing one: annual demand changes little,
but when it is delivered does.

# Highlights

- Annual electricity nearly flat (0.12 percent) as midday share and load factor rise.
- Reversion scenarios fall 0.12 to 0.44 percent; partial persistence is not detectable.
- 2022 weekday at-home rate sits 4.73 percentage points above the 2005-to-2015 trend.
- Household model keeps peak-timing diversity an average-profile method erases.
- Load shape checked, not validated, against measured Toronto/Ontario 2022 data.

# Keywords

Residential occupancy modelling; time-use survey data; stock-scale building energy simulation;
work-from-home scenarios; residential load shape; peak demand and load factor; Canadian housing stock.

---

## Number trace table

| Value as written | Section of `draft_S3_results.md` it comes from | Rounding note |
|---|---|---|
| 4.73 percentage points (2022 weekday at-home rate above 2005-to-2015 trend) | 3.1, Manager addendum (entry (dv)) | As written; no rounding applied |
| 0.12 percent (main-scenario annual whole-building electricity, rise) | 3.3 (0.1209 percent) | Rounded from 0.1209 to two decimal places |
| 0.73 percentage points (midday share change, cluster-aware, main scenario) | 3.4 (0.73 pp) | As written in Results (already rounded from 0.0073235) |
| 0.49 percentage points (load factor change, main scenario) | 3.4 (0.49 pp) | As written in Results (already rounded from 0.004943) |
| 0.12 percent (full-reversion scenario, fall) | 3.2 (S-None Facility change, 0.1225 percent) | Rounded from 0.1225 to two decimal places; same rounded magnitude as the main-scenario 0.12 percent above but opposite direction (fall, not rise) -- see Open for the manager item 1 |
| 0.44 percent (standardized-reversion check, fall) | 3.2 (S-Revert-std Facility change, 0.4408 percent) | Rounded from 0.4408 to two decimal places |
| Partial persistence not distinguishable from zero | 3.2 (S-Partial Facility change, 0.0117 percent, interval negative 0.0065 to 0.0351 percent) | Not a number to round; the interval contains zero, stated in words, not a value, per the Must rule |
| Household-level peak-timing diversity kept vs. average-profile method erases it | 3.5 (circular standard deviation of peak hour: 3.493 h vs 0.084 h in 2022; 3.255 h vs 0.053 h in 2030) | No specific hour value quoted in the abstract or highlights; stated qualitatively only |
| Held-out survey year (generator checked on unseen 2022 cycle) | draft_S1_introduction.md, 1.5, with manager correction (dt) | Not a number; wording matches the corrected claim ("trained through 2015, tested on 2022") |
| Simulated load shape checked, not validated, against measured Toronto/Ontario 2022 data | 3.6 | Qualitative; no point value from the Toronto/Ontario comparison table is quoted in the abstract or highlights, per the Must rule against over-claiming validation |
| Several dwelling archetypes and climate zones (stock-scale, paired design) | draft_S1_introduction.md, 1.4-1.5; draft_S2_framework.md | Qualitative scope statement, not a specific count (no `[NUMBER FROM RESULTS]` placeholder value was available to substitute) |

## Character counts

| # | Highlight | Characters (incl. spaces) |
|---|---|---|
| 1 | Annual electricity nearly flat (0.12 percent) as midday share and load factor rise. | 83 |
| 2 | Reversion scenarios fall 0.12 to 0.44 percent; partial persistence is not detectable. | 85 |
| 3 | 2022 weekday at-home rate sits 4.73 percentage points above the 2005-to-2015 trend. | 83 |
| 4 | Household model keeps peak-timing diversity an average-profile method erases. | 77 |
| 5 | Load shape checked, not validated, against measured Toronto/Ontario 2022 data. | 78 |

Counted with `wc -m` on each line in isolation (no trailing newline included in the count), in the
session scratch directory; all five are at or under the 85-character limit (Highlight 2 sits exactly at
the limit).

Abstract word count: 247 words (counted with `wc -w` on the abstract text alone, in the scratch
directory), under the 250-word cap.

## Open for the manager

1. **Same rounded magnitude, opposite direction.** The main scenario's annual electricity change
   (0.1209 percent, a rise) and the full-reversion scenario's change (0.1225 percent, a fall) both round
   to "0.12 percent." The abstract and Highlight 1/2 keep them apart only through the words "rising" and
   "falls." If the manager wants this de-risked further (for example, one of the two carried to three
   decimal places, or the full-reversion number phrased as "about 0.12 percent" to visually distinguish
   it from the exact "0.12 percent" main-scenario figure), that is a wording call this draft did not make
   on its own.
2. **Household archetype and climate-zone counts are not stated.** Section 1.5 of
   `draft_S1_introduction.md` still carries `[NUMBER FROM RESULTS]` placeholders for households per
   panel, simulation runs, and architectures searched; none of those placeholders were filled as of this
   task, so the abstract says only "several dwelling archetypes and climate zones" rather than a number.
   If those placeholders are filled before assembly, the abstract could optionally gain one more concrete
   number; not added here since the task's source list did not include a filled version of that section.
3. **Toronto/Ontario measured check has no number in the abstract or highlights.** The Must list asks for
   "a measured Toronto/Ontario 2022 check (a check, not a validation)" as part of the headline; this
   draft states that the check exists and is a check rather than validation, but does not quote any of
   Section 3.6's point comparisons (for example, load factor 0.4680 vs 0.4305), to keep both the abstract
   under 250 words and every highlight under 85 characters. Flagging in case the manager wants one such
   number added, which would require cutting something else to stay within the caps.
4. **Keywords are this draft's own choice**, not sourced from any file (no existing keyword list was
   found anywhere in `manuscript/`, `previous/`, or `archive/` within this task's read scope). Seven
   keywords given, within the 5-to-7 range the task doc sets; the manager may want to swap or trim these
   to match Applied Energy's own keyword conventions or an existing author keyword list not found here.

## WHAT I DID NOT VERIFY

- Did not open any T-numbered `impl/` file, CSV, or cluster output directly; every number in the
  abstract and highlights is copied from `draft_S3_results.md`'s own prose or its Number trace table (or,
  for the held-out-year claim, from `draft_S1_introduction.md` as corrected by plan log entry (dt)), not
  re-derived from a raw file.
- Did not search for an existing Elsevier/Applied Energy keyword list, author-supplied keywords, or a
  prior submission's abstract anywhere outside `manuscript/`, `draft_S1_introduction.md`,
  `draft_S3_results.md`, `draft_S4_discussion.md`, and `draft_S6_conclusion.md`; the task's own source
  list did not name such a file, and a broader search would have been a literature/archive search beyond
  the task's "text only" scope.
- Did not check Applied Energy's own house-style rules for abstract or highlights formatting (for
  example, whether Highlights must be numbered, whether a period is required at the end of each bullet,
  or the platform's exact abstract word-limit enforcement) beyond the word-count and character-count
  limits stated in this task doc itself; the task doc notes Applied Energy's exact abstract limit is
  checked at WP13, and this draft stays under 250 words as instructed.
- Did not verify the word count and character counts by any means other than `wc -w` and `wc -m` on
  plain-text scratch files built from this draft's own final wording, run in the session scratch
  directory (Python was confirmed not installed on this machine before falling back to `wc`/`awk`).
- Did not re-check every number in this draft against the underlying CSV files named in
  `draft_S3_results.md`'s own Number trace table; this draft treats that table, and the Results section's
  prose, as the source of record, per the task doc's "numbers only from these" instruction.
- Did not confirm whether "the future load shape" (Abstract, sentence 1) or "this shift" (Abstract, final
  sentence; Highlight wording) could be read as implying one predicted outcome rather than the
  scenario-based framing intended; re-read once after drafting and judged consistent with "scenario-based
  projection" wording used throughout the source drafts, but flagging since this is a judgment call, not
  a mechanical check.
