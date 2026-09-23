# Shared brief for the IMP rewrite (2026-09-22). Every writer reads this first.

Paper: "From 'How Much' to 'When'..." (2J), target journal Applied Energy. The author read the paper and
asked for the changes in `../../../IMP/2J_improvement_plan_author_comments_2026-09-22.md` (plan APPROVED).
The manuscript was split into chunks in this folder (`*_orig.md`). Each writer rewrites ONE chunk into a
`*_new.md` file in this folder and writes a short `*_report.md`. Never edit `*_orig.md`, the main
manuscript, the SI, or anything outside this folder. The manager assembles the chunks afterwards.

## Writing rules (author's words: "simpler sentences, not combined sentences, for all the document")

1. One idea per sentence. Aim for 15 to 25 words. **No sentence over 30 words** unless it is a single
   number with its confidence interval that cannot be split. Split "X, and Y, comparing Z: a, b and c"
   chains into separate sentences. Turn long inline lists into short sentences.
2. Plain, common words. Keep technical terms the reader needs (load factor, confidence interval,
   archetype), drop decorative ones.
3. **Keep every fact and every number exactly** (same value, same decimals, same units). Do not round,
   do not add new numbers, do not recompute. If you drop a number (only allowed where your chunk
   instructions say so), list it in your report.
4. Keep every citation exactly as written (author-year form). Do not add or remove references.
5. No em dashes or en dashes in prose (use "to" for ranges). The title and the reference list are the
   only exceptions.
6. Journal paper, not a report: no notes about process, no "stated here", "not quoted", "noted here only
   because the code defines them", no task IDs, no reviewer talk, no "as an error". Say "limitation",
   never "failure".
7. For 2030, describe the designed scenario shift; never claim the simulated level equals a target.
8. British spelling as in the original (behaviour, modelling).
9. Markdown conventions stay: headings `#`/`##`, figures `![](path){width=16cm}` followed by a blank line
   and `**Figure N.** Caption.`, tables preceded by `**Table N.** Caption.`, display equations as
   `$$ ... \tag{n} $$` blocks, inline math `$...$`.

## Captions and layout (author: "one sentence very short captions, the rest inside the text";
## "one paragraph one figure one paragraph one figure")

- Every figure and table caption = **one short sentence** (about 8 to 15 words). Everything cut from
  the caption (samples, what bars mean, which households) must appear in the paragraph that cites it.
- Every figure and table is placed right after the paragraph that first cites it.
- **Never two figures or tables in a row**: there must be at least one paragraph between any two floats.
- Every figure and table is cited in the text before it appears, and in numerical order.

## New numbering (use these everywhere in your chunk)

Sections: 1.1, 1.2, 1.3 unchanged; old 1.4 is folded away; old 1.5 -> 1.4.
Old 2.1 -> 2.1; old 2.2 + 2.3 -> 2.2; old 2.4 + 2.5 -> 2.3; old 2.6 -> 2.4; old 2.7 + 2.8 + 2.9 -> 2.5;
old 2.10 + 2.11 + 2.12 -> 2.6. Section 2 now runs "Sections 2.1 to 2.6". Sections 3.1 to 3.8, 4, 5, 6
keep their numbers.
New titles: 2.1 Data and diary preparation; 2.2 Generative occupancy model and calibration;
2.3 From diaries to household schedules; 2.4 Activity-driven end-use loads; 2.5 2030 scenarios,
household sampling and stock weighting; 2.6 Load-shape metrics, statistics and comparison methods.

Equations. Main text keeps six: old 8 -> (1) equipment power; old 9 -> (2) calibration scalar;
old 10 -> (3) 2030 scenario target; old 12 -> (4) stock weights; old 16 -> (5) confidence interval;
old 18 -> (6) average-profile arm. Moved to **Appendix B**: old 1 -> B.1; 2 -> B.2; 3 -> B.3; 4 -> B.4;
5 -> B.5; 6 -> B.6; 7 -> B.7; 11 -> B.8; 13 -> B.9; 14 -> B.10; 15 -> B.11; 17 -> B.12.

Tables. Old Table 1 (framework dimensions) -> **Table A1** in **Appendix A**. Old Table 2 (datasets) ->
**Table 1**.

Figures. Figure 1 (workflow) stays. New method figures in Section 2: Figure 2 = diary to hourly schedule
(`../../figures/Figure_M1_diary_to_hourly.png`), Figure 3 = raking (`../../figures/Figure_M2_raking.png`),
Figure 4 = activities to equipment power (`../../figures/Figure_M3_activity_to_power.png`),
Figure 5 = 2030 scenarios (`../../figures/Figure_M4_2030_scenarios.png`). Old Results figures:
old 2 -> 6, old 3 -> 7, old 4 -> 8, old 5 -> 9, old 6 -> 10, old 7 -> 11, old 8 -> 12.
SI numbering (Table S1 to S5, Figure S1, S2, Sections S1 to S11) is unchanged.

Back matter order after the Conclusion: Nomenclature, Appendix A, Appendix B, References.

## Report file (`<chunk>_report.md`, short)

- Words before and after.
- Any sentence still over 30 words (quote it, say why).
- Numbers dropped or changed (should be none unless your chunk allows it); for each dropped number,
  where else it appears (Results, SI, or "only here").
- Cross-references you changed (old -> new).
- Anything you were unsure about.
