# 3J Read-Through Review, Round R1

**Reviewer role:** first end-to-end read of `writing/fullSet/readySubmission.md`, all 1733 lines, as one
document. This review is READ-ONLY: no manuscript file was edited. Findings only; fixes are proposed,
not applied.

**Scope note.** `writing/fullSet/readySubmission.md` and `writing/fullSet/3J_full_manuscript.md` are no
longer byte-identical. The build status report (`3rdJ_build_status_report.md`) records both as 2,186
lines, md5 `c68924293b636061398154d9e31de948`, from one assembly pass. On disk today,
`readySubmission.md` is **1,733 lines**, md5 `fcb14eda441e7eeb53db4736c84efc20`;
`3J_full_manuscript.md` is still 2,186 lines, md5 `c68924293b636061398154d9e31de948`. Someone edited
`readySubmission.md` after assembly without touching its sibling, which breaks the "cannot diverge"
guarantee the build report states for these two files. This review covers only `readySubmission.md` as
instructed; it is reported here as a process fact, not analysed further.

---

## Verdict

**Not submittable as-is.** The single biggest problem is not any one wrong number, it is that this
document is still the project's internal engineering log wearing a paper's outline. Ninety-five
occurrences of internal task apparatus, task IDs (`dr_L3-06`, `V2-B3`, `OD-1`, `V4-B4`...), the phrase
"this task", French-language internal defect labels ("Défaut 7"), and unresolved `[confirm]` placeholders
in the author block, run through every chapter from the front matter to the appendix, and Appendix B1/C1
are not supplementary material in any normal sense, they are the project's own sprint board (rounds v0
through v5, a 49-item task board, "Gates moved" / "Bands moved" columns) transcribed into a journal
submission. Separately, and more damaging to the science itself, the paper's own headline quantified
retail finding is stated two different ways in two different chapters: Results/Discussion/Abstract say
the retail median is 75.63 kWh/m2/yr, 5.47% below its floor; the Limitations chapter (prose and table)
says 75.4 kWh/m2/yr, 5.7% below the same floor. A reviewer who reads the abstract against the limitations
table, which is a completely ordinary thing for a reviewer to do, will catch this in under a minute, and
it will cost the paper credibility on every other number after it.

---

## 1. Contradictions between chapters

### 1.1 [SEVERITY: HIGH] The retail EUI median disagrees with itself: 75.63 vs 75.4

- **Results, §5.2, line 877:** "the measured median is 75.63 kWh/m2/yr, which is 5.47 % below the 80
  kWh/m2/yr floor"
- **Results, "three failing gates" bullet, lines 1012-1013:** "the measured median is **75.63, which is
  5.47 % below the 80 floor** (re-derived from the 56 CFA values in the deliverable CSV)"
- **Results, "Scope of verification", line 1030:** "Retail: CFA range 63.63-96.84, median **75.63**"
- **Abstract, line 10:** "the retail median sits 5.47% below its floor"
- **Discussion §6.4** and **Conclusion** both refer back to this same 5.47%/75.63 figure.

versus

- **Limitations, §7.B, L7, line 1125:** "The retail median is **75.4** kWh/m2/yr against a floor of 80,
  **5.7% below**, with 44 of 56 cells under the floor."
- **Table 7, L7 row, line 1176:** "Retail median is **75.4** against a floor of **80**, i.e. **5.7 %
  below**, with **44 of 56** cells under."

Both pairs are internally self-consistent arithmetic (I re-derived both: `(80-75.63)/80 = 5.46%` rounds
to the stated 5.47%; `(80-75.4)/80 = 5.75%` rounds to the stated 5.7%), and both pairs agree on the "44
of 56 cells under the floor" count. What disagrees is the underlying median itself, 75.63 vs 75.4, for
the exact same quantity (retail channel EUI, CFA basis, median across the 56-cell campaign). The Results
chapter states its number was independently re-derived from the deliverable CSV; the Limitations chapter
gives no re-derivation and no source line for its 75.4. On the evidence stated in the document itself,
75.63/5.47% is the more trustworthy value and 75.4/5.7% in Chapter 7 looks like a stale figure carried
over from an earlier round that Chapter 7's own transcription note (line 1163: "Transcribed, not
rewritten... no number or verdict is paraphrased") did not catch.

**Proposed fix:** re-derive the retail median directly from `step9_eui_by_channel.csv` one more time,
confirm which of 75.63/75.4 the frozen deliverable actually carries, and correct the losing occurrence
(most likely L7 and Table 7's L7 row) to match. Do not average or split the difference.

### 1.2 [SEVERITY: MEDIUM, hedged] Table 5 refuses to invent a Residential empirical-band central value; Chapter 7's L8 states one anyway

- **Table 5 / "Scope of verification", lines 1037-1039:** "no as-modelled band (`band_lo/central/hi`
  empty, gate is INFO-only); empirical/INFO band 113.9/n/r/147.2" - the build report's own flags table
  confirms this `n/r` is deliberate: "`info_central` is not a column in the deliverable CSV; a midpoint
  was not invented."
- **Limitations, L8, line 1127 and Table 7 L8, line 1177:** "The SHEU-2019 HighRise reference is 130.6
  kWh/m2/yr (113.9-147.2), context only."

130.6 is suspiciously exactly the arithmetic midpoint of 113.9 and 147.2 (`(113.9+147.2)/2 = 130.55`,
which rounds to 130.6). Table 5 goes out of its way, in its own sourcing note, to say a midpoint was
*not* invented for this cell; Chapter 7 then reports a number that is, to one decimal place, exactly that
midpoint. This may be an entirely legitimate, independently-sourced SHEU central estimate that simply
happens to sit near the middle of its own stated range (bands are often built that way), in which case
this is a false alarm and the two chapters are not actually in conflict, only inconsistent in how hard
each one looked for the same figure. I could not resolve this from the manuscript text alone, because
L8 gives no source line for 130.6 the way L7 gives "re-derived from the 56 CFA values" for 75.63.

**Proposed fix:** add a source citation to L8's 130.6 (which SHEU-2019 table/page it is read from), or,
if it turns out to have been computed as a midpoint after all, remove it and bring L8 into line with
Table 5's own stated convention of not inventing a central value.

---

## 2. Numbers that disagree with each other, or that do not reconcile with their own stated derivation

### 2.1 [SEVERITY: MEDIUM] L11's "18.75% hot" does not reconcile with the mechanism L11 itself describes

- **Limitations, L11, line 1135:** "the tower instead carries the code's office schedule (type A) byte
  for byte, which peaks at 0.90 with a 0.50 lunch-hour dip, and the injector applies a further 0.95
  multiplier on top of that curve. Retail therefore runs approximately 18.75% hot at peak"
- **Table 7, L11 row, line 1180:** same figure, "retail runs **18.75 %** hot at peak"

Read literally, the injected peak this sentence describes is `0.90 x 0.95 = 0.855`. Compared to NECB
retail's own actual peak of 0.80 (the value the same limitation names two sentences earlier), that is
`(0.855-0.80)/0.80 = 6.9%` hot, not 18.75%. The number 18.75% only falls out of `(0.95-0.80)/0.80`, i.e.
treating the bare 0.95 constant as if it were the injected peak on its own, without the 0.90 multiplier
the sentence says it is applied on top of. Appendix C.3 (line 1546) gives a third, different figure for
a related comparison ("a modest +2.4% at peak") using yet another pairing of the same three constants
(0.95, 0.90, 0.80, and a 0.97 in-store-share lever), and I could not make that one reconcile with either
of the other two either. At least two of these three percentages (6.9%, 18.75%, 2.4%) describing the same
handful of constants cannot simultaneously be correct without a step the text does not show.

**Proposed fix:** whoever wrote L11 should show the arithmetic (which peak value, against which
reference, gives 18.75%) either in the limitation itself or in a footnote, and reconcile it against
C.3's "+2.4%" so the two don't read as two independent, disagreeing claims about the same injected curve.

### 2.2 [SEVERITY: LOW] Office "fails by 15%" is a rounded figure, stated as if exact, in five places

`85.45` against a floor of `100` is `14.55%` short, which the document rounds to "15%" at lines 995,
1079, 1083, 1119 (L4) and in Table 7's L4 row (1173). This rounding is applied consistently everywhere
it appears, so it is not a contradiction, just worth flagging: a reviewer who multiplies `100 x 0.15`
and gets `85` instead of the stated `85.45` may momentarily think the paper's own arithmetic is off by
0.45. Not a required fix, but a parenthetical "(14.55%, rounded to 15%)" on first use would pre-empt it.

### 2.3 Numbers checked and found consistent (listed here rather than under "orphans" so the pattern of what *does* hold up is visible)

- Hotel cluster gap: `302.86 - 218.22 = 84.64`, and `84.64 / (300-180) = 70.5%` - both re-derived by me
  and correct, consistent across abstract (line 10), Results §5.2 (868-874), Discussion §6.3 (1089),
  and Table 7 L5 (1174).
- Retail over-crowding: `(1/24.97)/(1/29.97) = 1.200`, i.e. 20.0% over-crowded - re-derived by me,
  matches L9/Table 7 L9 exactly, and the "20%" figure is used consistently everywhere it appears
  (§3.5, L9, Table 7 L9, C.2).
- L3 household diversity: `3,499/16,367 = 21.38%` - re-derived by me, correct, consistent between L3
  prose and Table 7's L3 row.
- 56-cell campaign arithmetic: `2 towers x 2 cities x 14 scenarios = 56`, and `14 = 1 (Default) + 4
  (historical cycles) + 3 (B-bundles) + 6 (sens_* pairs)` - both re-derived by me and correct,
  consistent in §4.3, Table 3's footer, and every results section.
- Tower areas (72,623.1 m2 Tall / 135,857.6 m2 SuperTall) are identical everywhere they are quoted:
  §4.1 (597), Table 3 (703-704), and Appendix C.1 (1477).
- The hotel band citation correction (PNNL-28543 does not exist; replaced by a first-party 284.44/299.28
  retrieval) is stated consistently in Appendix C.6, Table 5, §6.3, and L5.

---

## 3. Repetition

### 3.1 [SEVERITY: HIGH] The office control-fails-its-own-band narrative is told in full, with identical numbers, five separate times

- Results §5.2, lines 858-866 (full paragraph)
- Results, "The three failing gates, at full strength" bullet, lines 991-1000 - appears roughly 130
  lines after 3.1's first telling, **inside the same chapter**, restating the same numbers (85.45, 100,
  15%, heating share 17% vs 35-45%, the three contested floors 100.0/80-140/85.0-115.0) in near-identical
  sentence structure
- Discussion §6.2, lines 1079-1083 (same numbers again, in essay form - this one is defensible, it is
  the chapter whose job is to interpret the finding)
- Limitations L4, line 1119 (condensed but still repeats all the same figures)
- Table 7, L4 row, line 1173 (table form - also defensible, a limitations table is supposed to be
  self-contained)

The pair at 3.1 is the one worth fixing: the Results chapter states the finding in full prose immediately
before Table 5, then restates it in full prose immediately after Table 5, with the table sitting between
two copies of the same paragraph. Discussion and the Limitations table each earning their own telling is
normal; having it twice inside Results itself is not.

**Proposed fix:** keep the fuller telling in one of the two Results locations (the "three failing gates"
bullet block reads as the more complete of the two, since it states the source files) and shrink the
other to a forward pointer, e.g. "see 'The three failing gates' below for the full evidence."

### 3.2 [SEVERITY: MEDIUM] The AT_RETAIL derivation rule and its online-shopping exclusion are given in full three times

- Table 2, footnote 1, lines 309-321
- §3.1 Methods, lines 350-365 (near-identical wording to the footnote, including the same
  "occACT==4 & occPRE==1" exclusion explanation)
- Table B1 section, "The AT_RETAIL rule itself", lines 1330-1341 (same formula, same exclusion logic,
  again)

A table footnote restating a Methods rule is defensible (tables should be self-contained). A third,
near-identical prose restatement in an appendix is not adding information the reader doesn't already
have from §3.1.

**Proposed fix:** keep §3.1 as the canonical statement of the rule; trim the Appendix B1 occurrence to a
one-line pointer ("see §3.1 / Table 2 footnote 1 for the frozen rule").

### 3.3 [SEVERITY: LOW] The checkpoint-selection composite-score deviation is told in full twice

- §3.2, lines 418-442 (Methods)
- Appendix A1.5, lines 1283-1308 (Supplementary)

Same numbers both times (0.0218 F1 gap, 5.6% relative, 0.16 sd, 4 of 5 seeds). This one is closer to
acceptable, since Methods states the finding and Appendix gives the fuller hyperparameter-table context,
but the two paragraphs overlap almost sentence for sentence rather than one summarizing the other.

---

## 4. Argument flow

### 4.1 [SEVERITY: LOW] Front matter's own claim about where Leg-2 magnitudes appear is not quite accurate

Line 59: "No result or magnitude from the two-channel construction stage this paper builds on appears
anywhere above; that stage is a construction step for this paper and is discussed only in Methods and
in the Introduction's departure-point narrative (§1.4)." In fact §1.4 (lines 133-136) contains no
numeric magnitude at all - the only Leg-2 magnitude in the whole document (172.7, Table 6, line 578)
appears in Methods only. The claim that magnitudes appear "in Methods and in... §1.4" over-states where
they actually are; harmless, but worth tightening to "discussed only in Methods, and narratively (with
no magnitude) in the Introduction's departure-point narrative (§1.4)."

### 4.2 Otherwise, the funnel holds up

Chapter 1's four stated advances (§1.5, Architecture / Injection / Experimental design / Validation
stance) map cleanly onto Chapters 3, 3.5, 4, and 5-6 respectively, and the aim statement in §1.5 is
answered point for point in the Conclusion (§8). Discussion §6 discusses exactly the three gates Results
§5.2 reports failing, in the same order, with no discussion of a result Results never reported. I found
no promise made in Chapter 1 that a later chapter fails to deliver.

---

## 5. Orphans (broken or misleading cross-references)

### 5.1 [SEVERITY: HIGH] "Table 4" is cited seven times and never once captioned

Lines 335, 406, 414, 489, 532, 686, and 689 all say "(Table 4)" or "Table 4 reports..." / "Table 4,
Wiring row" etc., pointing at the validation-gates content that actually appears under the headers
"(a) Tiered gates", "(b) Channel-specific gates", "(c) Wiring + differentiation gates" (starting line
725). There is no line in the document reading "**Table 4.**" the way every other table (1, 2, 3, 5, 6,
7, A1, B1, C1) is introduced. A reader following any of the seven "(Table 4)" pointers has to guess
that the untitled three-part gate table three chapters later is the referent.

**Proposed fix:** add a "**Table 4.**" caption line immediately before "(a) Tiered gates", matching the
style used for every other numbered table in the document.

### 5.2 [SEVERITY: HIGH] Figure numbers do not follow the order in which the figures are first cited, and one cross-reference points at the wrong figure number

Figures actually appear, in reading order: Figure 1 (line 150, marked NOT FOUND), **Figure 10** (line
842, in §5.1), **Figure 7** (line 890, in §5.2), Figure 8 (line 925, §5.3), Figure 9 (line 928, §5.3),
Figure 11 (line 965, §5.4), Figure S3 (line 1729). Figure 10 (the longitudinal chart) is captioned
*before* Figure 7 (the EUI chart) even though 10 > 7. This produces a direct broken pointer: line 840,
in §5.1, reads "This asymmetry... is the structural backdrop for the per-channel band verdicts in
**Section 5.2 (Figure 10)**" - but Figure 10 is the longitudinal figure that belongs to §5.1 itself, and
the figure actually used in §5.2 is Figure 7. The sentence should read "Section 5.2 (Figure 7)".

**Proposed fix:** renumber the five results figures in their order of first appearance (longitudinal=7,
EUI=8, diurnal=9, peak-hour=10, scenario=11, or renumber the section order instead) and fix the line-840
cross-reference to point at whichever figure actually illustrates §5.2.

### 5.3 [SEVERITY: MEDIUM] Seven of the eight promised schematic figures (2, 3, 4, 5, 6, S1, S2) never appear anywhere in the manuscript body

A grep across the whole document for "Figure" turns up only Figure 1 (placeholder, NOT FOUND), Figures
7-11 (Results), and Figure S3 (Appendix). The build status report's own Bucket A lists eight schematics
as drafted (Fig 1 pipeline, Fig 2 roadmap, Fig 3 three-head, Fig 4 projection, Fig 5 tag2, Fig 6 hotel,
Fig S1 shares, Fig S2 levers), but Figures 2 through 6, S1 and S2 have no caption, no placeholder, and no
in-text reference anywhere in `readySubmission.md` - not even a "NOT FOUND" marker like Figure 1 got. A
reader of the actual manuscript would have no way to know these were ever planned. This is most visible
in Methods (Chapter 3), which is exactly where a three-head-Transformer diagram (Fig 3), an
exclusivity-projection diagram (Fig 4), and a Tag-2 dispatch diagram (Fig 5) would normally anchor the
architecture description that is currently text-only for pages at a stretch.

**Proposed fix:** either insert the missing figure captions/placeholders at their intended locations in
Chapters 1-3, or, if they are being deliberately dropped for this submission, remove references to an
eight-figure schematic set from any internal planning language that might still leak into a cover letter.

### 5.4 [SEVERITY: MEDIUM] Table 6 appears out of numeric sequence, three chapters before Tables 3, 4 and 5

Table 6 (the Leg-2/Leg-3 pipeline-delta table) is captioned at line 559, at the very end of Chapter 3
(Methods). Tables 3 (line 693), 4 (line 725, see 5.1 above) and 5 (line 970) all appear later, in
Chapters 4 and 5. A reader proceeding front-to-back meets Table 6 before ever seeing Tables 3, 4 or 5,
which reads as a numbering error even though each individual table is internally fine and Discussion
§6.1 (line 1073, "Table 6 records this step by step") correctly assumes the reader has already seen it
by that point.

**Proposed fix:** either renumber Table 6 to reflect its actual position (it would sit naturally as
"Table 3" if Datasets/Methods tables are numbered in chapter order), or move its content to sit after
Table 5, consistent with its current number.

---

## 6. Tone / register

### 6.1 [SEVERITY: LOW] Diacritics on "Widén and Wäckelgård" are dropped inconsistently

Prose citations (line 85 caption, references lines 169-170) use the full diacritics "Widén and
Wäckelgård"; Table 1's own column note and reading paragraph (lines 94-95, 99-105, 111) drop them to
"Widen & Wackelgard." Both spellings refer to the same author and appear within ten lines of each other
in places. Minor, but a copyeditor will flag it, and it is a small tell of four different authors' text
having been merged without a final consistency pass.

### 6.2 French internal defect labels survive untranslated into English body text

Appendix C's section headers use the French project term "Défaut" untranslated ("C.1 - Défaut 7:...",
line 1458; "Défaut 5" referenced at line 578; "Défaut 4" at line 575) inside what is otherwise an English
manuscript. See §7 below for the fuller apparatus-contamination finding this belongs to; flagged here
specifically as a register break, since it is the one place a non-English word survives into body text
rather than a citation or file path.

---

## 7. Internal project apparatus beyond Table 6's Evidence column

The prompt already flags Table 6's Evidence column; the items below are places the same problem surfaces
**outside** that column, which is most of the document. A single grep for the combined pattern
`this task|standing (hard )?rule|dr_L3-\d\d|V2-[A-Z]\d|V3-[A-Z]\d|V4-[A-Z]\d|OD-\d|Défaut|\[confirm\]`
returns **95 hits in this one file** - it is not confined to one table.

### 7.1 [SEVERITY: HIGH] Front matter carries four unresolved `[confirm]` placeholders and an editorial aside

- Line 39: "1 Concordia University, Montreal, Quebec, Canada - *(department/institute to confirm)*"
- Line 43: "*ORCID:* Iseri - [confirm]; Hachem-Vermette - [confirm]"
- Line 49: "*(reused from the 2J front matter; confirm still accurate for this manuscript before
  submission)*" attached to the Funding declaration
- Line 55: "*(draft - confirm/adjust the split)*" attached to the CRediT statement
- Line 59: an entire paragraph titled "Front-matter notes for the author" listing what still needs
  confirming

These are exactly the kind of thing that must be resolved, not merely flagged, before a submission
copy goes anywhere near an editor - a funding declaration and a competing-interest declaration with a
live "[confirm]" next to them is a compliance problem, not a style one.

### 7.2 [SEVERITY: HIGH] Internal task/decision IDs appear directly in body prose, not just in tables

Examples beyond Table 6: line 87-89 ("Differentiation targets named in dr_L3-10 §2.4..."), line 350
("frozen 2026-07-02 (decision OD-1)"), line 876-877 and line 1011 ("decided at V2-B3, in advance of the
numbers"), line 1653-1659 ("V2-F4 negative result, V2-F6 retrieval... V2-C6 propagation"), line 1259
("~2% positive, from dr_L3-08/dr_L3-11"). A journal reviewer has no context for what "V2-B3" or "OD-1"
means; these read as internal ticket numbers because that is what they are.

### 7.3 [SEVERITY: HIGH] Appendix Tables B1 and C1 are the project's own QA sprint log, not supplementary material

Table B1 (lines 1354-1447) is literally a round-by-round audit tracker: "v0 - backward audit", "v1 - Step-9
fix log", "v2 - WP-A/B/C/D/E/F/G execution (49-item board)", with columns "Done / Withdrawn / Blocked /
Gates moved / Bands moved" and footnotes citing internal file line numbers like
`improvements/v2/3rdJ_L3_v2_implementation.md:201-205`. Table C1 (lines 1448-1728) is six-plus
"defect" writeups in the same idiom, including phrases like "this is precisely the scenario the
project's 'a gate must be seen failing' rule exists to catch" (line 1471-1472) and "the project's own
'a gate must be seen failing' rule" - referring to a house rule of the authors' own workflow, stated as
if it were a citable methodological principle. This is not a supplementary-material problem that can be
fixed by moving it to an SI file; it is content that documents an internal engineering process and does
not belong in a submission at all in its current form.

### 7.4 [SEVERITY: MEDIUM] "This task" appears as a citation qualifier throughout Table 6 and recurs in Appendix C

E.g. line 570: "no byte-level or column-level comparison of GSS-column output was performed **in this
task**"; line 1524-1525 uses the same idiom in Appendix C.2's sourcing. "This task" is agent-session
language (a unit of work in the authors' own AI-assisted workflow), not manuscript language; a human
author would write "in this study" or simply state what was and was not checked.

**Proposed fix for §7 overall:** this is the single largest cleanup remaining before submission. A
mechanical pass is not safe (the build report itself warns that an automated strip could delete a real
caveat along with the apparatus), so this needs a human editorial pass, chapter by chapter, that (a)
resolves every `[confirm]` in the front matter, (b) either drops internal task IDs from body prose or
replaces them with a proper citation/footnote, and (c) either moves Tables B1/C1's content into a
project changelog that lives outside the manuscript, or rewrites them from scratch in the register of a
methods/limitations appendix, keeping only the substantive findings (the corrected numbers, what changed
and why) and dropping the sprint-tracking scaffolding around them.

---

## Numbers cross-check

**Re-derived myself (arithmetic redone from figures already in the document, not taken on trust):**

| Claim | Stated | My recomputation | Consistent? |
|---|---|---|---|
| Retail median-to-floor gap (Results version) | 75.63 vs 80 floor = 5.47% | (80-75.63)/80 = 5.46% | Yes (rounding) |
| Retail median-to-floor gap (Limitations version) | 75.4 vs 80 floor = 5.7% | (80-75.4)/80 = 5.75% | Yes internally, but **disagrees with the Results version above - see Finding 1.1** |
| Hotel cluster gap as % of band width | 84.64 / 120 = 70.5% | 302.86-218.22=84.64; 84.64/120=70.53% | Yes |
| Office control shortfall vs floor | 85.45 vs 100 = "15%" | (100-85.45)/100=14.55%, rounds to 15% | Yes (rounded) |
| Retail over-crowding (L9) | ~20% | (1/24.97)/(1/29.97)=1.200 -> 20.0% | Yes |
| L3 multi-person household diversity | 3,499/16,367 = 21.38% | 3499/16367=0.21379 -> 21.38% | Yes |
| 56-cell campaign structure | 2x2x14=56, 14=1+4+3+6 | confirmed both | Yes |
| L11 "18.75% hot at peak" | stated mechanism 0.90 base x 0.95 multiplier | 0.90x0.95=0.855; (0.855-0.80)/0.80=6.9%, not 18.75% - only reconciles as (0.95-0.80)/0.80 | **No - see Finding 2.1** |
| Residential empirical central (L8) | 130.6 | (113.9+147.2)/2=130.55 -> matches to 1 decimal, but Table 5 explicitly declines to report this figure | Flagged, not resolved - see Finding 1.2 |

**Taken on trust (internal to the document, cross-checked for consistency across mentions but not
independently re-derived against an external source or the underlying CSV/JSON):**

- Office CFA range 61.72-90.21, median 71.02; Hotel CFA range 203.33-318.42, median 260.54 - these
  appear multiple times (Table 5, "three failing gates" bullets, Scope of verification, Discussion) and
  are consistent everywhere they occur, but I did not have access to `step9_eui_by_channel.csv` or
  `step9_gates.json` to verify them against the source artefact myself.
- 172.7 (Leg-2 published office EUI, Table 6 only) - consistent with the one place it appears and
  correctly framed as a superseded, comparability-caveated historical figure, never used as a live
  magnitude. This document does not repeat the error the task briefing warned about.
- "not four building archetypes" (line 296) - the only occurrence of the phrase "building archetypes"
  in the document, correctly negated.
- Tower floor areas (72,623.1 / 135,857.6 m2), gate scorecard tallies (17 PASS/10 INFO/3 FAIL, 30 gates)
  - consistent everywhere quoted, not independently re-derived from simulation output.

---

## What I could not check and why

- **The underlying data artefacts** (`step9_eui_by_channel.csv`, `step9_gates.json`,
  `_PROVENANCE.md`) were not opened in this review; every number check above is a check of the
  manuscript's internal consistency with itself, not a re-verification against the frozen deliverable.
  In particular, Finding 1.1 (75.63 vs 75.4) can only be fully resolved by re-reading the CSV directly,
  which this review did not do (out of scope: this was a read-through-as-a-paper task, not a data
  audit).
- **Citations and DOIs** (Doma & Ouf, Buttitta & Finn, Widen & Wackelgard, Richardson et al.) were read
  as prose but not independently verified against their source PDFs; per the project's own standing
  rule, that kind of verification is external deep-research work, not something to be done inside this
  review.
- **Whether `3J_full_manuscript.md` shares readySubmission.md's defects** - I did not open the sibling
  file. Given the two are no longer byte-identical (see Scope note above), findings in this review
  should not be assumed to automatically apply to `3J_full_manuscript.md` without a separate check.
- **Figure image content** - none of the referenced PNGs (Figure_07_eui_4ch.png etc.) were opened; this
  review only checked that captions and cross-references resolve, not that the images themselves show
  what their captions claim.
- **Whether the "seventeen statements under sixteen IDs" limitations-count issue is visible inside this
  document** - per the task briefing this is a known issue in the source document behind Table 7; I
  confirmed no sentence in `readySubmission.md` itself claims the limitations count was independently
  verified, and I did not find a second, duplicated L-number printed twice within this file (the
  duplication the briefing describes lives in the consolidated source document, not in what actually
  made it into this manuscript's Table 7/Chapter 7 text).

---

## Progress Log

**2026-08-06 - R1 read-through complete.** Read `writing/fullSet/readySubmission.md` end to end (1,733
lines) as one document, first full read since assembly. Delivered this review file. Headline findings:
(1) a genuine internal contradiction on the paper's own headline retail number - Results/Discussion/
Abstract state retail median 75.63 kWh/m2/yr (5.47% below floor), Limitations Chapter 7 (both prose L7
and Table 7's L7 row) states 75.4 kWh/m2/yr (5.7% below floor) for the identical quantity; (2) Table 4
is cited seven times in body prose and never once captioned; (3) figure numbers do not follow reading
order (Figure 10 is captioned before Figure 7) and one cross-reference (line 840) points at the wrong
figure number as a result; (4) seven of eight promised schematic figures (2-6, S1, S2) never appear
anywhere in the manuscript body; (5) Table 6 physically appears three chapters before Tables 3-5 despite
its higher number; (6) internal project apparatus (task IDs, "this task", unresolved `[confirm]`
placeholders in the front matter, an appendix that is literally the project's own sprint-tracking board)
appears 95 times across the document, well beyond the already-known Table 6 Evidence column. No
manuscript file was edited; no band, gate, or reference-band value was touched or proposed for change.
Two findings (L8's 130.6 possibly-invented midpoint, L11's "18.75% hot" arithmetic) are flagged with
explicit hedging because I could not fully resolve them from the manuscript text alone. Not checked:
the underlying `step9_eui_by_channel.csv`/`step9_gates.json` artefacts, citation/DOI accuracy, image
content of any figure, and whether `3J_full_manuscript.md` (no longer byte-identical to
`readySubmission.md` - 2,186 lines / md5 `c68924293b636061398154d9e31de948` vs 1,733 lines / md5
`fcb14eda441e7eeb53db4736c84efc20`) shares any of these defects.
