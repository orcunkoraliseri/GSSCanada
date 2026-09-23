# 3J paper: improvement plan built from the 2J rejection and revision (2026-09-22)

**Status:** PLAN ONLY. Nothing in the 3J manuscript, SI, figures or build has been edited.
**Manuscript read:** `writing/submission/3J_manuscript_submission.md` (872 lines, 12,604 words incl.
references), `3J_supplementary_material.md`, `Title_Page_and_Cover_Letter.md`, and `Prompts/RESUME.md`.
**2J material read:** `2J_docs_occ_nTemp/writing/submission/rejection revision/00_REVISION_PLAN.md`
(reviewer triage §1-§2, work packages §3, unraised weaknesses §5, log (ec)-(ex)),
`rejection revision/IMP/2J_improvement_plan_author_comments_2026-09-22.md` (the author's 15 comments),
and the revised `manuscript/2J_manuscript_AE_revised.md` (structure, abstract, aim section).

**Why this plan exists.** 2J was rejected by Building Simulation (3 reviewers, all negative) for reasons
that were about evidence and presentation, not about the core science. 3J was built by the same
pipeline, in the same writing style, before that rejection arrived. Read side by side, **3J as it
stands carries almost every weakness the 2J reviewers named**, plus two scientific problems of its own
(Section 3 below). Building and Environment already rejected 0J for "insufficient quality", so a fast
reject is the realistic risk. Fixing these before submission is far cheaper than a second rejection.

---

## Rules that stay in force during every step

- 3J standing rules (RESUME "Hard rules"): no band moves, no gate verdict changes, no measured number
  changes; archive the predecessor before editing; never edit a built file by hand; verify the
  INSTALLED .docx; build both documents every time.
- **3J is in a writing phase: zero simulation.** Steps marked **C** (new computation) need the author's
  explicit go. Steps marked **B** read existing frozen outputs only, but re-rendering or re-reading
  frozen aggregates is still authorisation-gated (RESUME), so say so before starting.
- Never create images (write prompts; plots from frozen data are allowed).
- Deep research is external: we write prompts, the author runs Gemini, we vet before anything is cited.
- 2J rules adopted from its revision: re-derive every number from its artifact before quoting;
  plain words, no internal vocabulary; **journal, not report: no meta notes in prose, tables or
  figures**; "limitation", never "failure" in prose (gate verdicts stay FAIL in tables).

Classes (same as the 2J plan): **A** text only · **B** re-derive from an existing file · **C** new
computation (author go needed) · **D** narrow a claim the paper cannot support · **E** external
(deep-research prompt the author runs).

---

## 1. The five 2J lessons, and where 3J stands on each

| 2J lesson (reviewers) | 3J today | Risk |
|---|---|---|
| 1. The paper reads like a technical report (R1, R2): internal QA, debugging stories, PASS/WARN/INFO scorecards, self-defined labels, results inside Methods, meta sentences | Same, and stronger: wiring-bug story (§3.5, §4.4), checkpoint-selection audit (§3.2), Table 6 "Bit-identical?" ledger with "three non-matching copies" of the injector, "Chapter N", "Tag-2", "two-channel construction stage", "gate", "PASS/FAIL/INFO", L-numbers in the Introduction, "No band value was moved" repeated about five times, "not reported" inside the reference list | **High** |
| 2. No comparison with a simpler schedule (R1-M1, D1, D12): "show what the detailed model adds" | The paper already simulated the plain code-schedule case (the uninjected baseline, one of the 14 scenarios), but only uses it for the office gate. Peak hours, coincidence factor and day/night ratios are never compared against it | **High** (and cheap to fix, see P3) |
| 3. Calibration is not validation; nothing independent checks the hourly shape (R2-2, R2-6, R3-5); EUI gap vs benchmark must not undermine the conclusions (R1-M3) | No measured load data for any channel. The end-use layer is "calibrated" against the commercial end-use survey (§3.6). The headline is three failing EUI gates plus residential outside its band in 55 of 56 cells | **High** |
| 4. "Forecast" and a single 2030 future (R2-3, R3-2, R3-4) | Title "(Canada, 2005-2030)", abstract "forecast 2005-2030", and "Forecast to a future year" is one of the four axes the novelty claim rests on. Scenarios do exist (3 bundles + 6 one-lever variants), which is good | Medium |
| 5. Statistics and thresholds (R1-M2d, R3-6, R3-7): what is sampled, is it enough, how intervals are built, where thresholds come from, were they set before the results | Results are medians and ranges over **4 building-city cells**, no interval, no run-to-run noise, effects of 0.07 % to 2.5 %. Thresholds are listed in SI Table 4 with provenance (good), but the retail scoring rule change reads as post hoc (§5.2) and the shipped model checkpoint was chosen by a composite score the spec forbids (§3.2) | **High** |

---

## 2. Every 2J reviewer request, checked against 3J

Only rows that apply to 3J are listed. "Where in 3J" uses quoted text or section numbers, since line
numbers go stale.

### Reviewer 1 (the most detailed of the three)

| 2J # | Request | Same problem in 3J? | Action for 3J | Class |
|---|---|---|---|---|
| M1, D1, D12 | Compare with simpler schedules; show what stochastic, individual modelling adds | Yes. Claim "A single-channel schedule cannot carry a difference between populations" (§6) is asserted, never tested | P3: report the uninjected code-schedule case beside the injected one for peak hours, coincidence factor, day/night ratio, per-channel EUI. If code schedules already peak at different hours, say so and narrow the claim | B (+D) |
| M2a | Concise workflow diagram | Partly. Figure 1 is "Steps 1-9" (a report-style pipeline); Figure 2 is a roadmap of the authors' own three stages | Replace Figure 1 with a simple 8-10 box, three-row diagram (the 2J redraw worked well); drop Figure 2 or move it to SI | A (image prompt) |
| M2b, D11 | Mathematical formulation of models and metrics | Yes. Only 3 displayed equations (retail rule, val_score, hotel multiplier) | P6: equations for the training loss, exclusivity projection, REPLACE and MODULATE injection, SARIMA, EUI on both floor-area bases, circular-mean peak hour, coincidence factor, day/night ratio. Keep 5-6 in text, rest in an appendix | A |
| M2c | Results inside Methods should move | Yes. §3.2 carries checkpoint F1, PR-AUC and impossible-state numbers; Table 6 verdicts sit in Methods; §3.5/§4.4 carry defect history | Move numbers to Results or SI; keep one sentence per check in Methods | A |
| M2d | What is sampled, and is the sample big enough? | Yes, and not answered anywhere: how many households, workers, customers per tower, which seeds, one realisation or several? | P5: write the sampling procedure from the code (B). Run-to-run noise needs seed replicates (C, author call) | B + C |
| M3 | EUI far from the benchmark: show the conclusions survive it | Yes, it is the paper's headline | P4: separate "benchmark applicability" from "behavioural result"; state in one place that the timing results do not depend on the EUI level | A + D |
| M4, D15 | More figures for occupancy, energy, shape, peak | Partly. 11 results/method figures exist, but no occupancy-profile figure per channel (presence by hour, 2005-2022) | Add one plot from frozen data: the four presence channels by hour of day, per cycle | B (plot) |
| D2 | Include the authors' own prior studies in the comparison table | Done (one row). Must match the revised 2J Appendix A scoring | Sync the own-row with 2J's revised table (2J's own row now scores present on two dimensions only) | A |
| D3, D4 | Define terms at first use | Yes: GSS, SARIMA, PCGrad, SLAW, EUI, CFA, GFA, NECB, PNNL, ISR, JS, PR-AUC, TMYx, GSSP, AT_RETAIL, occPRE, occACT, CYCLE_YEAR | Define or replace every one; drop code names from prose (P1) | A |
| D5 | Say explicitly how you differ from the closest paper | Partly (Doma and Ouf) | One explicit paragraph against the single closest competitor, after the new literature search (P7) | A + E |
| D6 | Why does *when* matter, why 2030? | Weak. The practical meaning of four peaks and a coincidence factor (plant sizing, shared central plant, district and grid peak) is never spelled out | One motivation paragraph with citations (from P7) | A + E |
| D7 | Contributions as scientific and practical statements | No. The four "advances" include "a validation stance" and "the experimental design" | Rewrite as 2-3 scientific + 2 practical contributions (the 2J format) | A |
| D8, D9, D10 | Dataset-role table; building models do not belong under Datasets; call the section "Proposed modelling and simulation framework" | Yes: §2.4 (prototypes) and §2.5 (weather) sit under Datasets; Datasets, Methods and Experimental Design are three chapters | Merge into one framework section, six sub-sections (P2); Table 2 becomes the dataset/channel-role table | A |
| D14 | Repeated descriptions | Yes: "unchanged from the two-channel construction stage" appears in almost every subsection; hotel-outside-the-survey is explained four times; retail-staff exclusion three times | Say each once | A |
| D16 | Text numbers must match the figures | Risk: this already happened once in 3J (retail median stated two ways, fixed in August) | P9: a number sheet, every number re-read from the frozen deliverable, text against figure data | B |
| D18, D19 | Tiny annual differences: decompose by end use and hour; make shape metrics prominent | Yes: office -1.21 %, residential -0.07 %, levers ±2 %. No end-use split per channel | If the frozen deliverable holds end-use meters per channel, one end-use-by-hour figure (B); otherwise state it as a limitation | B or D |
| D20 | Figures too small and dense | Check Figures 9, 10, 11 at print size (multi-panel) | Split if a panel is unreadable at 190 mm | A |

### Reviewer 2

| 2J # | Request | Same problem in 3J? | Action for 3J | Class |
|---|---|---|---|---|
| 1 | Report style; move internal QA to SI; plain terms | Yes (lesson 1 above) | P1 | A |
| 2 | External validation of the hourly profile against measured data | Yes, none for any channel | P8: a deep-research prompt for measured Canadian (or North American) hourly data for office, retail, hotel or mixed-use buildings. If nothing usable exists, say plainly that the load shape is checked only indirectly | E, then B or D |
| 3 | Reconsider "forecast"; use "scenario-based projection" | Yes | Author decision D2 (2J kept its title by author order; the body text can still change) | A |
| 4 | Abstract in plain prose, no symbols | Partly. No symbols, but it uses labels ("*Context.* *Gap.* *Aim.*...") that Elsevier journals do not print, and it is number-heavy | Rewrite in short plain sentences, about 200-240 words | A |
| 5 | Delete meta-descriptions of the paper's own structure | Yes: "The four subsections below move from...", "This is the gap the present study addresses: not ... but ...", "Three things are stated rather than smoothed over" | Delete | A |
| 6 | Calibration closure is not validation | Yes (SCIEU calibration in §3.6; EUI bands) | Name the SCIEU step "calibration" everywhere; never call it validation; list the independent checks separately | A + D |
| 7 | Figures too small | See R1-D20 | | A |

### Reviewer 3

| 2J # | Request | Same problem in 3J? | Action for 3J | Class |
|---|---|---|---|---|
| 1 | Re-run the 2030 calibration on the correct 2022 frame | **Possibly.** 3J reuses the same raking chain for residential and office, and its own Table 6 says "2030 work presence sits 10.51 percentage points below observed 2022, four to five times the signal the campaign exists to detect". That is the same shape of defect 2J had (a 2022-to-2030 level jump the scenario never intended). NOT VERIFIED | P10: re-derive 2022 and 2030 at-home and at-work shares from the 3J schedule products; find which 2022 frame the 2030 targets were raked against | B, then author decision |
| 2, 4 | At least two 2030 scenarios in the main results | Done: 3 bundles + 6 one-lever variants in §5.4 | Keep; say "scenario" not "forecast" | A |
| 3 | Do not claim a causal COVID/WFH effect | Yes: §1.3 "Office presence is pulled down by the persistence of hybrid...", "Retail presence is pulled down by ... e-commerce" | "associated with", plus a limitation naming other concurrent changes | A + D |
| 5 | Separate calibration from independent checks | Yes | Two labelled parts in the framework section: what was fitted, what was checked independently | A |
| 6 | How were intervals built? | No intervals at all | P5 (report spread honestly; seeds if author approves) | B + C |
| 7 | Where do thresholds come from; were they set before the results; sensitivity | Partly answered in SI Table 4. Two open sores: the retail rule change (§5.2) and the composite-selected checkpoint (§3.2) | P11: state from the record the date each rule was set relative to the numbers; move the checkpoint story to SI with one Methods sentence | B + A |

### 2J weaknesses the reviewers did NOT raise, but that 3J shares (2J plan §5)

| 2J item | Applies to 3J? | Action |
|---|---|---|
| Typical weather (TMY), not future climate, for 2030 | Yes, and not in 3J's 16 limitations (L15 is ground-level weather only) | Add one limitation sentence |
| Survey collection-mode change (telephone to self-completed questionnaire) lands on the same 2022 cycle as the pandemic | **Yes, and not stated anywhere in 3J.** It matters more here: retail's "reversal" is a 2022 jump (+2.36 %), exactly the cycle where the mode changed | Add a limitation; soften any claim built on the 2022 retail jump |
| Novelty table never tested by a systematic search; scoring criteria not stated | Partly: RV09 tested it; criteria given for only two of eight axes; Table 1 shows only 3 competitors although RV09 scored 10 | Add the vetted RV09 rows; one-line criterion per axis (P7) |
| Reference errors (wrong volume, truncated title) | Likely: several entries literally say "not reported" | Full reference re-verification (P7) |
| Figures below the journal's dpi | Already fixed in 3J (500-880 dpi) | Nothing |
| Companion paper status wrong in the text | Yes: 3J cites 2J as "under review b ... Building Simulation" (now rejected; going to Applied Energy) | Update both self-citations (P12) |

---

## 3. Problems specific to 3J, found in this read

These were not in the 2J reviews, but a Building and Environment reviewer is likely to find them.

1. **"Coincidence factor below 1 in all four cells" is not a finding, it is arithmetic.** The peak of a
   sum can never exceed the sum of the peaks, so the ratio is at most 1 for any building, and equals 1
   only if every channel peaks in the same hour. It is Highlight 2, and it appears in the Abstract,
   §1.5, §5.3, §6 and §7 as evidence that "use diversity flattens the peak". What would be a finding is
   *how much lower* it is with the survey-driven channels than with the code schedules (P3). Fix before
   any reviewer sees it.
2. **"Four peaks at four different hours" may also be true of the code schedules.** The office, retail,
   hotel and apartment code schedules are different curves too. Without the baseline comparison (P3) a
   reviewer can say the result comes from the building's code schedules, not from the survey model.
3. **The reference list is too thin for this venue.** 18 entries, of which 4 are the authors' own or
   standards, and 5 say "not reported" or "Edition not reported". §1.1 makes its opening claim ("widely
   recognised as a dominant ... driver") with no citation at all. The revised 2J has 48 references.
4. **Unsourced claims written as if checked internally.** §1.3: "a decline this study's own
   deep-research check found to be internationally normal"; §2.3: "No StatCan table of monthly
   hotel-occupancy rates exists (a data-availability check run for this study)". Either cite a source
   or remove the clause.
5. **Retail scoring rule reads as changed after the numbers.** §5.2 says the median rule was "decided in
   advance of the numbers" and, in the next sentence, that the old all-cells rule "was itself replaced
   because it was turning on a margin of only 0.15 %". A reviewer reads that as a rule changed once the
   verdict was known. State the date order from the record, or report both rules with equal weight.
6. **A paragraph that damages the authors' other paper.** §6's "reproducibility caveat" says the prior
   2J residential intensity table had two compounding defects and that fixing them "moved three of four
   band verdicts". The revised 2J recomputed its intensities from scratch, so this now describes a
   version of 2J that no longer exists, and in any version it hands a reviewer a reason to doubt both
   papers. Delete it (the 3J method is not affected).
7. **Supplementary figures sit inside the main text.** Figures S1 and S2 are embedded in §4.1 and §4.3
   of the manuscript, while the SI file holds only S3. Either promote them to main figures or move
   them to the SI file.
8. **Front matter and declarations are in report order.** Declarations and the graphical abstract sit
   before the Introduction. Elsevier's order (confirmed from the Applied Energy guide for 2J) is CRediT,
   competing interests, funding, data, generative-AI declaration, acknowledgements at the end, before
   the References; the graphical abstract and highlights go as separate upload files. The generative-AI
   declaration is still missing (RESUME item 5). Funding reads "Voltage-Age Seed fund" here and
   "Volt-Age Seed Fund" in the revised 2J; one spelling for both papers.
9. **Title and headings do not state the finding.** "From One Channel to Four: A Jointly-Trained..." is
   a method title; several section headings are long claims ("Behaviour Is Non-Stationary Per Use, and
   the Uses Move in Different Directions"). 2J's revised headings are short and neutral.
10. **"Retail Retail"** appears twice as an archetype name; it reads as a typo.

---

## 4. The author's 15 comments on 2J, applied to 3J up front

The author read 2J and asked for these changes; the same reader will ask for them in 3J. Doing them now
saves a round.

| 2J comment | What it means for 3J |
|---|---|
| C1 Title in "Centered" style | Same build fix (title block via YAML, as in 2J) |
| C3 Short, simple sentences everywhere | 3J sentences are often 50-70 words (§1.1, §1.4, §7). One idea per sentence, about 20-25 words; a script lists every sentence over 30 words before and after |
| C6 Highlights: purpose, finding, benefit | Two of five 3J highlights are about failing gates, and one is the coincidence-factor identity. Redraft around: four populations, what survey channels change versus code schedules, what benchmarks can and cannot judge, and the practical use for plant sizing |
| C11 Table 1 to an appendix | Same: Table 1 to Appendix A, one summary sentence in §1.2 |
| C14 No separate "prior line" section | 3J §1.4 "The Authors' Prior Line" is the same section 2J had. Fold it into §1.2 (the prior work as part of the literature) and one sentence before the contributions. Keep all self-citations (self-plagiarism rule from 2J) |
| C16 Merge aim and contributions | Same: one short paragraph |
| C18 Section 2 into 5-6 sub-sections; most equations to appendix | 3J has 15 sub-sections across three chapters before Results. Merge to six (P2). Keep essential equations in text |
| C19 One-sentence captions; the rest into the text | 3J captions are already short, but Tables 2, 3, 5 and 6 carry explanatory paragraphs under the caption. Move those into the text |
| C22 A source for every equation | Same: one Gemini prompt listing each equation (like 2J's dr_2J-17) |
| C26 Simple method figures | 3J already has Figures 3-6 as schematics. Only add one if an equation needs it (coincidence factor) |
| C35 Nomenclature before the appendix | Same |
| C41 Paragraph, figure, paragraph, figure | 3J stacks: Figures 1+2, 3+4, 9+10, Figure 11 + Table 5. Tables are placed far from first citation (Table 3 cited in §2, placed end of §4; Table 5 cited in §5.2, placed end of §5.4) and numbered 1, 2, 6, 3, 5 |
| C47 Discussion cut by half | Already 697 words; keep, but rewrite around the new comparison (P3) |
| C49 Limitations cut by half, keep every point | 3J has no Limitations section in the main text (all 16 are in SI Table 7). Add a short Limitations section in the paper (about 500 words, all 16 plus the two new ones), keep Table 7 in SI |

---

## 5. Work packages, in the order they should be done

Format per project rule: aim, steps, expected result, test.

### P10. Check the 2030 level first (B, critical path)
**Aim.** Rule out the 2J defect before any 2030 number is rewritten. §5.3's peak hours and coincidence
factor are all "under the central 2030 scenario", so they depend on it.
**Steps.** (1) Read the 3J 2022 and 2030 schedule products for residential and office; compute
weekday at-home and at-work shares. (2) Find which 2022 reference the 2030 raking targets used
(pre- or post-relink frame, the 2J WP1 question). (3) Explain the "10.51 percentage points below observed
2022" line in Table 6.
**Expected.** Either the 2030 drift is explained and harmless, or it is the 2J defect. If it is the
defect, stop and hand the author a decision (re-rake and re-run = C), because §5.3 would then be
reported on 2022 instead of 2030.
**Test.** Shares re-derived from the files, not from a log; the 10.51 is reproduced before it is
explained.

### P3. Compare against the code-schedule case already in the campaign (B)
**Aim.** Answer 2J R1-M1 with data 3J already has, and turn the coincidence-factor identity into a real
result.
**Steps.** From the frozen deliverable, for the uninjected baseline in all four building-city cells:
per-channel peak hour, whole-building peak hour, coincidence factor, weekday day/night ratio,
per-channel EUI. Put them beside the injected 2022 (and 2030 central, after P10) values. Controls:
reproduce one published injected value first (for example the 0.941 median) before trusting the
reader.
**Expected.** One table or one two-panel figure, and a rewritten §5.3 and §6: "compared with code
schedules, the survey-driven channels move the whole-building peak from X h to Y h and lower the
coincidence factor from A to B". If the difference is small, say so and narrow the claim (D).
**Test.** Baseline values come from the baseline rows of the deliverable, named by file and column;
the injected values match Table 5 and §5.3.
**Needs:** author OK to read and plot frozen aggregates (RESUME gate). No simulation.

### P5. What is sampled, and how noisy the results are (B + optional C)
**Aim.** 2J R1-M2d and R3-6.
**Steps.** (1) From the code, write down exactly what is drawn per cell: which households, workers and
customer profiles, how many, which seed, one realisation or many. (2) If one realisation per cell,
state it and report the spread across the four building-city cells as a spread, not an interval.
(3) Optional C: rerun one cell with 5-10 seeds to measure run-to-run noise, so a reader can judge
whether a 0.07 % or 1 % change is signal.
**Expected.** Two Methods sentences; if (3) runs, one SI table.
**Test.** The written procedure is quoted with `file:line`.

### P11. Rule timing and model selection (B + A)
**Aim.** 2J R3-7.
**Steps.** (1) From the 3J record (V2-B3 and the Step-9 gate doc), write the date the retail
median-in-band rule was fixed and the date the numbers existed. (2) Rewrite §5.2 to state that order
plainly, or report both rules side by side without ranking them. (3) Move the checkpoint-selection
paragraphs of §3.2 to SI; leave one Methods sentence saying the shipped checkpoint was chosen by a
composite score and differs from the specified rule by 0.0218 Retail F1.
**Test.** Every date quoted from a file, not from memory.

### P1. From report to paper: vocabulary and meta text (A)
**Aim.** 2J R2-1, R2-5, R1-D3/D4, and the author's "journal, not report" rule.
**Steps.** (1) Make a jargon inventory like 2J's `prep/jargon_inventory.md`: gate, as-modelled band,
empirical band, PASS/FAIL/INFO, Tag-2 dispatch, modulate-vs-replace, three-head, side-track,
two-channel construction stage, Steps 1-9, cell, frozen deliverable, uninjected, occPRE, occACT,
CYCLE_YEAR, AT_HOME/AT_WORK/AT_RETAIL, val_score, ISR, PCGrad, SLAW, TMYx, GSSP, CFA, GFA-share,
L-numbers, "Chapter N". Replace or define each once. (2) Delete every meta sentence (structure
announcements, "stated rather than smoothed over", repeated "No band value was moved..." keep once in
Methods). (3) Move the defect histories (wiring bug §3.5, stale-output guard §4.4, checkpoint audit
§3.2) to SI, one sentence each in Methods. (4) Table 6 (additive ledger) to SI or cut; keep one
sentence in Methods saying the building geometry was confirmed unchanged and what was not compared.
**Test.** A scripted search of the built .docx finds none of the inventory terms undefined.

### P2. New structure (A)
Target, following the revised 2J:

| New | Title (draft) | From 3J today |
|---|---|---|
| 1 | Introduction: 1.1 Background, 1.2 Existing work and the gap (incl. prior line), 1.3 Non-stationary behaviour per use, 1.4 Aim and contributions | §1.1-§1.5 |
| 2.1 | Data and the four occupancy channels | §2.1-§2.3, §3.1, Table 2 |
| 2.2 | Generative occupancy model and hotel side-track | §3.2, §3.3, §3.4 (model part) |
| 2.3 | Scenarios to 2030 | §3.4 (levers), §4.3 (levers part) |
| 2.4 | Injection into the tower and end-use loads | §3.5, §3.6 |
| 2.5 | Buildings, climates and simulation campaign | §2.4, §2.5, §4.1-§4.3, Table 3 |
| 2.6 | Metrics, checks and comparison with code schedules | §4.4 (one sentence), metric definitions, P3 method |
| 3 | Results: 3.1 channels over time, 3.2 load shape and peaks vs code schedules, 3.3 scenarios, 3.4 energy intensity against reference bands | §5.1, §5.3 + P3, §5.4, §5.2 |
| 4 | Discussion | §6 |
| 5 | Limitations (new, short, all points) | Table 7 summary + 2 new |
| 6 | Conclusion | §7 |
| | Nomenclature · Appendix A (Table 1) · Appendix B (equations) · declarations · References | new |

Note the proposed Results order: the behavioural and timing result first, the failing reference bands
last. That keeps the binding B&E commitment (the abstract opens on behaviour) and follows 2J R1-M3.

### P6. Equations with sources (A + E)
Write the formulation (list in Section 2, row M2b). Keep in the text only the ones that carry the
argument (proposal: exclusivity projection, REPLACE/MODULATE injection, hotel multiplier, EUI on two
bases, coincidence factor); the rest to Appendix B. Then one Gemini prompt,
`deepResearch_Resources/V<NN>_3J_equation_sources.md`, asking for the standard source of each; mark
own definitions "defined here". Vet before citing.

### P7. Literature, novelty table, references (E + A)
**Steps.** (1) One deep-research prompt, run by the author, covering: mixed-use and tall-building
occupancy modelling; multi-task or Transformer occupancy generators; diversity and coincidence factors
in mixed-use buildings; EUI benchmarks for mixed-use and tall buildings; work-from-home effects on
office and home energy; e-commerce and in-store retail trend (source for §1.3); hotel occupancy
forecasting with SARIMA; measured hourly data (P8). It must also try to break Table 1 and name the
closest competitor. (2) Add the vetted RV09 rows to Table 1 and one scoring sentence per axis.
(3) Re-verify every reference (Crossref, full title, volume) and fill the five "not reported" entries
(ISQ table number, CBRE report, PNNL prototype release, SCIEU year, ASHRAE Guideline 14 edition).
**Target.** Roughly 35-50 vetted references.
**Test.** Every new citation opened by the author; 7-step vetting file beside the return.

### P8. Independent check of the load shape (E, then B or D)
Prompt for measured hourly office, retail, hotel or mixed-use building data in Canada or a comparable
climate (utility load-research profiles, open building datasets). If something usable exists, compare
normalised weekday shape and peak hour per channel (B). If not, say plainly that the shapes are checked
only against survey presence and code schedules, and soften "load shape" claims (D). Never present a
modelled profile as measured.

### P9. Number sheet and provenance (B)
Like 2J's `prep/results_number_sheet.md`: every number in abstract, highlights, text, tables, figures
and cover letter, with file and column in the frozen deliverable. Run before the rewrite and after it;
the two must match except where P3, P5 or P10 add new numbers.

### P4. Reframe the failing gates (A + D)
Keep every verdict and every number. Change the weight: the failing bands become one Results
subsection and one contribution about what single-use benchmarks can and cannot judge in a stacked
tower, not the paper's centre. State in one sentence that the timing results (peak hours, coincidence
factor, levers) do not depend on the absolute EUI level. "Limitation", not "failure", in prose.

### P12. Consistency with the revised 2J and 1J (A)
Update the 2J citation (title as in the revised 2J; journal once the author has submitted to Applied
Energy, "under review" or "submitted"); update the 1J JBPS status; make the 3J "prior study" Table 1 row
match the revised 2J own-row; check that every 3J sentence about 2J's findings matches the revised 2J
numbers; delete the §6 reproducibility paragraph (Section 3 item 6); one funding spelling.

### P13. Writing pass (A), last
Apply Section 4 (the author's 15 comments): short sentences, new abstract (about 200-240 words, no
labels), new highlights (at most 85 characters), captions, alternation, Nomenclature, title style,
declarations at the end including the generative-AI declaration. Numbers identical before and after.

### P14. Journal package and final audit
Read the live Building and Environment Guide for Authors (the 2J trick worked: save the page with a
browser; the fetch tool gets 403): abstract limit, highlights file, graphical abstract file, AI-figure
caption rule, declaration order, line spacing. Update the cover letter (it still quotes internal names
such as `Default_NECB` and says "gates"). Then the 2J Wave-5 step: one pre-submission audit prompt run by
the author in Gemini and in a second model, both vetted, every accepted item fixed and re-checked on the
installed .docx.

---

## 6. Order of work

```
Step 0  author answers the decisions in Section 7
Step 1  checks that decide what can be claimed (no simulation, reads only):
        P10 (2030 level) -> P3 (code-schedule comparison) -> P5 step 1-2 -> P11 -> P9 (first pass)
        at the same time: write the P6, P7, P8 prompts; author runs them in Gemini
Step 2  optional compute, only with author go: P5 seed replicates; P10 re-rake if it is the 2J defect
Step 3  restructure and rewrite: P2 -> P1 -> P4 -> P12 -> P6 (after vetting) -> P7 (after vetting)
Step 4  P13 writing pass -> P9 second pass -> rebuild both documents -> checks on the installed files
Step 5  P14 journal package and external audit -> fix -> submit
```

Biggest risk: P10 finds the 2J defect. Then every 2030-based number in §5.3 and §5.4 needs a re-run
(C), or the paper reports timing on 2022 and keeps 2030 only as scenario differences.

---

## 7. Decisions the author owns (recommendation first)

| ID | Decision | Recommendation |
|---|---|---|
| D1 | Submit 3J now, or after this plan? | After. The 2J reviews are a free preview of the same objections |
| D2 | Keep "forecast" in the title and novelty axis? | Replace with "scenario-based projection" in the text and in Table 1's axis name; the title is the author's call (2J kept its title) |
| D3 | What leads the paper: the failing reference bands, or the behavioural and timing result against code schedules? | The timing result (after P3). The cover-letter commitment to lead with the uninjected control was made before the 2J rejection; keep the control in the letter, but not as the paper's centre |
| D4 | Approve reading frozen aggregates for P3, P10 and the new occupancy figure | Yes; it is reading, not simulation |
| D5 | Approve seed replicates (P5 step 3) | Yes, one cell, 5-10 seeds; small cost, answers the most likely statistics question |
| D6 | Limitations: back into the main text as a short section? | Yes, about 500 words, all points kept, Table 7 stays in SI |
| D7 | Venue: stay with Building and Environment? | Stay, but only after P3 and P7; a thin reference list and an untested "four peaks" claim are exactly what an "insufficient quality" reject looks like |

**Author answers (2026-09-22, chat):**
- D1: after this plan (fix first).
- D2: replace "forecast" in the text and in the Table 1 axis name; the title stays.
- D3: lead with the timing result against code schedules. Condition: it holds only if P3 shows that the
  timing differs from the code-schedule run; if P3 shows no difference, revisit D3.
- D4: approved (read-only work on frozen aggregates).
- The author also asked for a way to validate the results beyond the published reference ranges, and said
  compute is available for extra simulations. All four validation tracks approved (V1-V4, Section 7a).
  The standing "zero simulation in the writing phase" rule is lifted for V3 and V4 only.
- D5: the fastest seed-replicate design that fits inside the allocated 32 CPUs on Speed. The remaining
  CPUs belong to the `histnu` jobs and must not be touched. Note: the 1J revision draws on the same
  32-CPU cap, so 3J runs must be sequenced with the live 1J jobs, never stacked on top of them.
- D6: yes, a Limitations section in the main text, but shorter than 500 words (target about 250).
- D7: stay with Building and Environment, submitting only after P3 and P7.

## 7a. Validation tracks (approved 2026-09-22)

Rule for all four: the reference bands and gate verdicts stay exactly as frozen. The new evidence sits
beside them; it never re-scores them.

| Track | What | Compute | First step |
|---|---|---|---|
| V1 | Yearly energy intensity against measured Canadian buildings (candidates: Montreal large-building energy disclosure open data, Canadian benchmark medians) | None (reading) | Deep-research prompt plus a direct check that the dataset exists, is public and splits by building use; nothing cited until vetted |
| V2 | Hourly presence profiles against independent measured occupancy data, per channel | None (reading) | Deep-research prompt; independence check: the data must not be the data the channel was trained or fitted on (hotel SARIMA inputs excluded) |
| V3a | Seed replicates: run-to-run spread | Speed, within 32 CPUs | Size the design from the Step-7 campaign run times: the smallest set of cells (target one per city and tower) and seeds that runs in one wave inside 32 CPUs |
| V3b | Plumbing check: code schedules sent through the injection path must reproduce the uninjected run | Speed, within 32 CPUs | Define the pass tolerance before the run; watch it fail on a deliberately wrong schedule first |
| V4 | Second building model: repeat the timing comparison on a different tower model | Speed, within 32 CPUs, largest cost | Design note first (which model, which cells, what counts as "same result"); author approves the design before any run |

Order: V3b first (cheap, and it protects every other number), then V3a, V1 and V2 prompts in parallel with
P10 and P3, V4 last. Every run goes through `sbatch` only; nothing runs on the login node.

---

## 8. What closes this round

- [ ] Section 7 decisions answered
- [ ] P10, P3, P5, P11 done, each with its implementation doc in `writing/implementation/`
- [ ] Deep-research returns (P6, P7, P8) run by the author and vetted before any citation
- [ ] Every row of Section 2 and Section 3 mapped to a change in the manuscript (keep a response map,
      like 2J's `prep/response_map.md`, as an internal checklist only)
- [ ] Manuscript and SI rebuilt; numbers identical to the number sheet; checks green on the installed files
- [ ] Journal guide read live; declarations complete; cover letter updated
- [ ] Pre-submission external audit run and vetted
- [ ] `Prompts/RESUME.md`, the Progress Log in `writing/implementation/3rdJ_paper_TASKS.md`, the board
      and memory updated (the 3J closure ritual)
