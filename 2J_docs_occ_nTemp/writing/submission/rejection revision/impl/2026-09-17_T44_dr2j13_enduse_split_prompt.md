# T44 - dr_2J-13 SHEU end-use split prompt - implementation state

Task doc: manager brief, 2026-09-17, "Write dr_2J-13_sheu_enduse_split_gemini_prompt.md: a
deep-research prompt for the measured residential end-use energy split for Canada, WP7 step 2 /
end-use breakdown of the Table 5 EUI gap."

Status: DONE

## Verified

- File written: `../deepResearch/dr_2J-13_sheu_enduse_split_gemini_prompt.md`.
- All four numbered decision rules present, verbatim from the brief, under "Pre-registered decision
  rule (fixed before any result is read)": (1) unambiguous split -> full breakdown, (2) shares only
  -> shares reported as shares, (3) space heating NOT FOUND -> breakdown not run at all, (4) our
  simulated values never rescaled, no band ever widened.
- Units and denominator requirement present under "What the numbers must allow", naming both
  candidate denominators (per household / per m2, total vs electricity only) and explaining why,
  with the paper's own simulated space heating range (12.6 to 29.5 kWh/m2/year) quoted as the reason
  a mismatched denominator would fake either an agreement or a gap.
- Positive control present ("Where to look" item 5): asks for the most recent national household
  end-use survey's overall space-heating share, without me stating its value anywhere in the prompt.
- Dashes: checked with `Grep` over the literal characters `[–—]` (en dash U+2013, em dash U+2014)
  against the new file; zero matches. Also re-read the file's own prose by eye for spelled-out
  ranges ("12.6 to 29.5", "2000 to 2023" style) rather than dash-joined ranges.
- "Calibration, not validation" wording constraint present: prompt tells the Gemini tool not to
  write "validate"/"validates" and to use "calibration"/"calibration closure" instead.
- "Gemini only, no Fable twin" one-line note present near the top, with the reason (no live search
  in the Fable setup).
- Registered on `../deepResearch/00_README_deepResearch.md`'s prompt table, one new row, same style
  as the existing dr_2J-09/dr_2J-10/dr_2J-11 rows; no other README structure touched.

## Decisions

- End-use list, geography priority (Ontario over national), dwelling-type and vintage handling, and
  the four decision-rule numbers were all given by the manager brief verbatim; not reopened.
- Positive control choice (national space-heating share from the most recent end-use survey) was my
  call within the brief's instruction to "choose something obvious and general, do not state its
  value" - it is the SHEU-style survey the paper already relies on, so a Gemini search that cannot
  find it flags a broken search rather than absent data.
- Did not create a `dr_2J-13b` verification-pass twin (unlike dr_2J-09/dr_2J-09b) - not asked for in
  this task; the manager can order one once a results file exists to verify.

## Next

Author runs `dr_2J-13_sheu_enduse_split_gemini_prompt.md` in Gemini Antigravity and saves the return
as `dr_2J-13_sheu_enduse_split_gemini_results.md` next to it. Manager then applies the pre-registered
decision rule (no re-arguing it) and updates `00_REVISION_PLAN.md` WP7 step 2 and this doc's Status.

## WHAT I DID NOT VERIFY

- I did not search for, open, or verify any actual end-use split source, DOI, survey table, or
  number - that is the author's job in Gemini, per the hard rule. Nothing in this task involved
  looking anything up.
- I did not check whether the most recent Canadian household end-use survey edition is the one the
  rest of the paper cites elsewhere (e.g. the SHEU edition already used for other calibration
  numbers) - the prompt asks Gemini to find and name it, that name is intentionally not pinned here.
- I did not re-read the full `00_REVISION_PLAN.md` end to end, only the WP7 section and the
  Progress Log entry (j) needed for context (T07's simulated space-heating range and dwelling-type
  count).
