# T83 — WP10: Abstract + Highlights — implementation state

Task doc:   this file. Plan: `../00_REVISION_PLAN.md` §3 WP10 ("prose abstract"), plan log (ds)-(dw) BINDING.
Status:     DONE
Agent:      fresh Sonnet employee, text only. No cluster, no web, no literature search.

## Output
`../manuscript/draft_S0_abstract_highlights.md` holding:
1. **Abstract**: one prose paragraph, no headings, no bullet list, at most 250 words (Applied Energy's
   exact limit is checked at WP13; stay under 250). Order: problem, what was built, what was tested,
   main findings with numbers, one practical implication.
2. **Highlights**: 3 to 5 bullets, each at most 85 characters including spaces (Elsevier rule).
3. **Keywords**: 5 to 7.
Then the trailer: `## Number trace table` (value, section of the draft it comes from),
`## Character counts` (each highlight), `## Open for the manager`, `## WHAT I DID NOT VERIFY`.

## Sources (numbers only from these, as they stand now)
- `../manuscript/draft_S3_results.md` (3.1 was filled by the manager in (dv); read the file itself).
- `../manuscript/draft_S6_conclusion.md` and `draft_S4_discussion.md` (framing only).
- `../manuscript/draft_S1_introduction.md` (title options, aim).

## Must
- Headline: main-scenario annual electricity nearly flat (0.12 percent) while midday share (0.73 pp)
  and load factor (0.49 pp) rise; scenario spread (full reversion falls 0.12 percent, standardized
  reversion falls 0.44 percent, partial not distinguishable from zero); pandemic-era at-home break 4.73
  pp over the pre-pandemic trend; household peak-timing diversity kept by the full model and lost by an
  average-profile method; a measured Toronto/Ontario 2022 check (a check, not a validation).
- Say "scenario-based projection", never "forecast"; non-causal wording; the survey end-use comparison
  is a check against a fitted target, never validation.
- Never: "+2.2 to +3.9", "+5.2", "17.0-17.7 h", "48/48 within 2.7 %", EUI, 6,000 runs, any 2005-2015
  energy number, 64,061 diaries or 144,507 (retired or not re-derived; the frame is 144,465 if needed).
- No internal labels (J3, S-None, T-numbers, gate IDs, C-VAE unless spelled out); no em or en dashes;
  no +, ±, ~, Δ symbols; numbers written as in Results but rounded sensibly (state rounding in trace).

## Rules
Edit no other file. Fill Verified/Decisions/Next below, set Status DONE.

## Ledger
(no cluster jobs)

## Verified

- Read plan log entries (ds) through (dw) in `../00_REVISION_PLAN.md` (lines 4092-4218) before
  drafting; every headline number in the Abstract/Highlights traces to the rulings there (item 40
  per-dwelling divisor, Ruling 1-4 on retired numbers, item 17/T80 pandemic-break wording, item 41
  historic-schedule exclusion).
- Read `manuscript/draft_S3_results.md` in full (449 lines, including the Manager addendum at the
  bottom from entry (dv)) as the numeric source of record; every number quoted in the Abstract and
  Highlights was matched against a row in that file's own Number trace table or its Manager addendum
  table.
- Read `manuscript/draft_S4_discussion.md`, `draft_S6_conclusion.md` and `draft_S1_introduction.md`
  for framing, title options and the held-out-year wording (used for "checked on a held-out survey
  year" in the Abstract, matching entry (dt)'s manager correction: trained through 2015, tested on
  2022).
- Checked the six "Must" banned items (forecast, EUI, 6,000 runs, 17.0-17.7 h, 48/48 within 2.7
  percent, any 2005-2015 energy number, 64,061 diaries, 144,507) and the banned symbols/internal
  labels against the final Abstract/Highlights/Keywords text with `grep`; none present. Confirmed no
  em or en dash anywhere in the file with a byte-level `grep`.
- Abstract word count: 247 words (`wc -w` on the abstract text alone, scratch directory), under the
  250-word cap.
- Each of the 5 highlights counted with `wc -m` individually (no trailing newline in the count): 83,
  85, 83, 77, 78 characters -- all at or under the 85-character limit (Highlight 2 sits exactly at 85).

## Decisions

- Kept the main-scenario rise (0.1209 -> "0.12 percent") and the full-reversion fall (0.1225 -> "0.12
  percent") distinguished only by the words "rising" / "falls" in the Abstract, since both round to the
  same two-decimal figure; flagged as Open-for-the-manager item 1 in the output file rather than
  silently adding a third decimal place, which the task doc's own rounding instruction did not require.
- Left the household-archetype and simulation-run counts out of the Abstract as bare qualitative
  language ("several dwelling archetypes and climate zones") rather than inventing a number, since
  `draft_S1_introduction.md` Section 1.5 still carries unfilled `[NUMBER FROM RESULTS]` placeholders for
  those counts and this task's source list did not include a filled version.
- Did not quote any point value from the Toronto/Ontario measured comparison (Section 3.6) in the
  Abstract or Highlights, to stay under the word/character caps; stated only that the check exists and
  is a check, not a validation, per the Must rule. Flagged as Open-for-the-manager item 3.
- Chose 7 keywords (within the 5-7 range) since no existing keyword list was found anywhere in
  `manuscript/`, `previous/`, or `archive/` within this task's read scope; flagged as
  Open-for-the-manager item 4 since these are this draft's own choice, not sourced from a file.
- Used "percentage points" in full (not "pp" or a symbol) throughout the Abstract and Highlights, and
  "negative"/plain words instead of a minus sign for interval bounds in the trace table, matching the
  convention already used in `draft_S3_results.md`'s own prose.

## Next

- Manager reviews Open-for-the-manager items 1-4 in `manuscript/draft_S0_abstract_highlights.md`
  (rounding collision, missing archetype/run counts, no measured-check number in the Abstract,
  self-chosen keywords).
- Per plan log (dw): assembly is the next work package once Abstract + Highlights exist; all six main
  sections plus this Abstract/Highlights/Keywords file now exist as drafts.

## WHAT I DID NOT VERIFY

See `manuscript/draft_S0_abstract_highlights.md`'s own `## WHAT I DID NOT VERIFY` section for the full
list (not re-cluster-verified numbers, no keyword-list search outside the given scope, no house-style
check beyond the task doc's own rules, counts done with `wc`/`awk` since Python is not installed on this
machine).
