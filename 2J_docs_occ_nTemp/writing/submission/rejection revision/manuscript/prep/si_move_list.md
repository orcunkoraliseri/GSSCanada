# Move-to-SI list

Built 2026-09-15 by T33 (WP10 prep). Source file: `archive/2J_manuscript_submission.md`. Items come from
the plan's WP10 "Move to SI" list plus every gate score or similarity (JS) value found in old sections
3.2 and 3.4 (R1-M2c), plus the duplicated passages between old sections 3.5 and 4.2 (R1-D14). Line
numbers are from the archived file; they will need re-grepping once a working copy exists under
`manuscript/`.

## WP10 "Move to SI" items

| Item | Archived line range | First 8 words of the paragraph | Target (SI section) |
|---|---|---|---|
| J3 architecture detail | 208-216 (section 3.2, plus Fig. 3) | "The sole model to clear all four gates" | SI: model architecture table (already referenced as "SI Table B1" in the old text) |
| 40+ trial search detail | 206 (section 3.2) | "Model selection was conducted as a gated search" | SI: model-selection search detail (already referenced as "Fig. S1") |
| PASS/WARN/INFO scorecards | 241 (sec. 3.4, "35/35 PASS"); 270 (sec. 3.6, "6 PASS / 1 WARN / 3 INFO"); 310 (sec. 4.2, "29 PASS / 0 WARN / 0 FAIL" and "28 PASS..."); 356 (sec. 4.4, "24 PASS / 0 WARN / 3 INFO") | see the four rows below under "Gate scores in 3.2 and 3.4" for the 3.2/3.4 ones; the 3.6 and 4.4 ones read "Calibration constrains each archetype's..." and "The campaign completed at 6,000..." | SI: verification scorecards (one consolidated table) |
| DX-coil fix | 356 (section 4.4) | "The campaign completed at 6,000 / 6,000 runs." | SI: campaign verification detail |
| Schedule round-trip checks | 356 (section 4.4) | same paragraph as DX-coil fix ("Schedule round-trip fidelity is exact...") | SI: campaign verification detail |
| Clock-alignment debugging narrative | 308 (section 4.2); shorter mention also at 253 (section 3.5) | "A clock-alignment step rotates the 04:00-origin" | SI: correctness-fix narrative. Keep one sentence on this in the main text per the plan's own rule (section 6: the timing check stays visible). |
| Donor-draw history | 251 (section 3.5) | "For households whose record spans only one" | SI: schedule-completion method detail |
| Raking coherence cost | 210 (section 3.2) | "J3's gate scores are: activity JS 0.0191" (the coherence-cost sentence is the third sentence of this paragraph) | SI: post-hoc calibration detail |
| Weekend JS floor argument | 241 (section 3.4) | "Validation is conducted as a True-Future-Test in" (the weekend-floor sentence is mid-paragraph) | SI: validation detail table |

## Gate scores / JS values in archived sections 3.2 and 3.4 (R1-M2c)

| Location | Archived line | First 8 words | Value(s) | Target |
|---|---|---|---|---|
| Section 3.2 | 206 | "Model selection was conducted as a gated" | four gate thresholds (activity JS <= 0.05; AT_HOME RMS <= 5.3 pp; co-presence gap <= 5.0 pp; composite < 1.045) | SI: model-selection scorecard; keep the plain-language selection rule in Results |
| Section 3.2 | 210 | "J3's gate scores are: activity JS 0.0191" | activity JS 0.0191; AT_HOME RMS 4.57 pp; co-presence gap approx. 2.03 pp; composite 0.6355 | SI: model-selection scorecard; Results keeps only the plain conclusion ("the chosen model passed all four checks") |
| Section 3.4 | 241 | "Validation is conducted as a True-Future-Test in" | weekday JS 0.0619 (future-year test); weekday JS 0.0630 (backcast); weekend JS 0.16-0.18 (mixed set), 0.036-0.046 (observed-only); scorecard 35/35 PASS | SI: validation scorecard; Results keeps the plain conclusion and the weekend-floor caveat in one sentence |

## Duplicated passages: archived section 3.5 vs section 4.2 (R1-D14)

| Topic duplicated | Section 3.5 line range | Section 4.2 line range | Note |
|---|---|---|---|
| Four schedule channels (occupancy, metabolic, equipment, lighting) description | 245-247 | 302-306 | Near-identical description of the same four channels and the same EnergyPlus objects, once in each section. |
| Clock-alignment shift | 253 (one sentence, points to section 4 for detail) | 308 (full paragraph with the debugging narrative) | Section 3.5 already forward-references section 4 for this; the full narrative belongs in one place only (SI, per above), with the one-sentence pointer kept in Framework. |
| Donor-draw completion for missing day-types | 251 | 310 (one sentence, points back to section 3.5) | Section 4.2 already back-references 3.5; the full method belongs only in 3.5's replacement (Framework), SI keeps the history. |

Recommended merge: keep one schedule-integration description in the new Framework section (built from
old 3.5), and have the new Experimental-Design section (built from old 4.2) reference it by one sentence
instead of repeating it, matching the cross-referencing pattern the authors already used for the other
two items.

## WHAT I DID NOT VERIFY
- Did not check whether the SI (Appendix, lines 599 onward) already contains a home for each of these
  items (e.g. an existing SI table that a moved paragraph should be merged into rather than appended);
  a skim of the Appendix heading list found Figs. S1-S8 and tables labelled B1/A1-A3 referenced from the
  main text, but did not open the Appendix content itself.
- "Weekend JS floor argument" and "raking coherence cost" are described in this file by locating the
  sentence inside a longer paragraph, not by an exact standalone line range, since neither is its own
  paragraph in the archived file.
