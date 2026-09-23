# 4J paper: improvement plan built from the 2J rejection and revision (2026-09-22)

**Status:** decisions D1-D6 ANSWERED 2026-09-23, all as recommended (Section 7); work starts at P3 step 1. Nothing in the 4J manuscript, supplement, figures or build has been edited.
**Manuscript read in full:** `writing/submission/4J_manuscript_submission.md` (1,453 lines; about 17,100
words from Introduction to Conclusion, 24 references), `4J_supplementary_material.md` (S1-S5), and the top
of `Prompts/RESUME.md` (last+294).
**2J material read:** `2J_docs_occ_nTemp/writing/submission/rejection revision/00_REVISION_PLAN.md`
(§0-§3 reviewer triage, §5 unraised weaknesses, §6 rules, §7 decisions),
`rejection revision/IMP/2J_improvement_plan_author_comments_2026-09-22.md` (the author's 15 comments).
**3J material read:** `3J_docs_occ_nTemp/writing/submission/IMP/3J_improvement_plan_from_2J_lessons_2026-09-22.md`
(same exercise for 3J; this plan uses the same shape so the three papers stay in step).
**Earlier 4J round, not repeated here:** `writing/IMP/IMP_PLAN_2026-09-14.md` (fact corrections from the
Gemini and Fable reads, all applied by 2026-09-17). This plan is about presentation, evidence and framing.

**Why this plan exists.** 4J was marked "ready to submit" on 2026-09-17, before the 2J lessons were
turned into a checklist. 2J was rejected by Building Simulation (3 reviewers, all negative) for evidence
and presentation, not for its core science. 4J was written by the same pipeline in the same style, and
read side by side **it carries the 2J presentation problems in a stronger form than 3J does**: it is the
longest of the three papers, it has the most internal process vocabulary, and its downstream building
half is mostly checks that did not run, did not pass, or are not claimed. The science (a clean,
pre-registered negative result with a diagnostic) is strong. The paper around it reads like the
project's audit log.

---

## Rules that stay in force during every step

- 4J standing rules: no band moves, no gate verdict changes, no measured number changes; the headline
  factor is **1.1 to 3.9**, never "2 to 6"; the 320 collision cells stay excluded from any number;
  archive the predecessor before editing (`writing/submission/previous/`); never edit the .docx by hand,
  rebuild with `tools/4thJ_build_submission_docx.sh`; check the INSTALLED .docx.
- Classes (same as the 2J and 3J plans): **A** text only · **B** re-derive or re-read from an existing
  file · **C** new computation (author go needed; Speed only, sbatch only, inside the 32-CPU cap shared
  with 1J and 3J, never `histnu`) · **D** narrow a claim the paper cannot support · **E** external
  (deep-research prompt the author runs in Gemini; we vet before anything is cited).
- Never create images: new schematics are image prompts; plots computed from frozen data are allowed.
- Journal, not report: no meta notes, no process history, no "stated rather than smoothed over".
  "Limitation", never "failure", in prose; gate verdicts stay FAIL in tables.
- Re-derive every number from its artifact before quoting it, including the numbers in this plan.

---

## 1. The five 2J lessons, and where 4J stands on each

| 2J lesson (reviewers) | 4J today | Risk |
|---|---|---|
| 1. Reads like a technical report: internal QA, debugging stories, PASS/FAIL scorecards, self-defined labels, results inside Methods, meta sentences | Strongest of the three papers. "gate", "board", "band", "fold", "cell", "null", "coverage clause", "mutation battery", "refusal", "definition-of-done" throughout; check tallies inside Methods (§3.1 "seventeen scored and sixteen passed", §3.2 "Nineteen of twenty", §3.4 "34 of 36"); two defect stories as full sections (§3.8 phase error, §6.6 "five lessons it cost"); §7.10 "Items that are unfinished... A reviewer will find these"; one internal instruction printed verbatim in the paper (§3.4: "This stage is therefore never to be written as complete... the board is never to be reported as 36 of 36") | **High** |
| 2. No comparison with a simpler alternative (R1-M1) | **Already strong.** The raked donor pool, a first-order Markov chain and six single-donor pools are all compared. This is 4J's best defence; keep it and make it more visible | Low |
| 3. Calibration is not validation; nothing independent checks the hourly shape (R2-2, R2-6, R3-5) | The downstream half has no independent check against measured load for Spain, Italy or the UK. The stock appliance peak (14:00 / 18:00 / 20:00) comes from **generated** diaries that lost the transfer test, and it is never set beside the same appliance model driven by **real** diaries. The only external shape check (a British reference profile from about 2000) does not pass | **High** |
| 4. "Forecast" and one future year | Does not apply: 4J has no future year | None |
| 5. Statistics and thresholds (R1-M2d, R3-6, R3-7): what is sampled, intervals, where thresholds come from | Table 3 has no interval on any margin; one training seed per arm; the closest cell (-2.70 minutes, UK aged 65+) is the one a reviewer will ask about. Threshold provenance is well documented in SI S1 (good), and the primary test has no tunable threshold (margin above zero), which the paper never says plainly | Medium |

Two further risks specific to 4J, not in the 2J reviews but likely at Energy and Buildings:

| Risk | 4J today | Level |
|---|---|---|
| Venue fit | The paper leads with language-model and survey-statistics material; the building-energy content starts in §3.7 and most of it is non-results. An Energy and Buildings editor may desk-reject as out of scope | **High** |
| Reproducibility | The backbone model is **never named** in the paper or the supplement ("open-weight 7.30 B decoder, pinned revision"). No reviewer in an ML-adjacent area will accept that | **High** (cheap fix) |

---

## 2. Every 2J reviewer request, checked against 4J

Only rows that apply to 4J. "Where in 4J" uses section numbers and quoted text, since line numbers go stale.

### Reviewer 1

| 2J # | Request | Same problem in 4J? | Action for 4J | Class |
|---|---|---|---|---|
| M1, D1, D12 | Compare with simpler alternatives; show what the detailed model adds | No for the diaries (three nulls). **Yes for the building loads**: nothing shows what the generated diaries give that real or raked-donor diaries would not | P3: drive the same appliance model with the real held-out diaries and with the raked-donor diaries; report the three peak hours side by side | B or C |
| M2a | Concise workflow diagram | Figure 1 is "Pipeline, Steps 0 to 11" (project steps, report-style); graphical abstract embedded in the text | New simple three-row diagram (data, generation and comparison, building loads), image prompt only; graphical abstract becomes a separate upload file | A (prompt) |
| M2b, D11 | Mathematical formulation of models and metrics | Yes. Only the serialisation line and the gain equation are displayed | P6: equations for raking (IPF update), time-budget MAE and margin, fictional-country slope and R², dwell-time Wasserstein, transition total variation, diurnal Jensen-Shannon, membership-inference AUC, the two-stage appliance trigger, the hot-water draw, and the gain redistribution (exists). Keep 5-6 in text, rest in an appendix | A + E |
| M2c | Results inside Methods should move | Yes: check tallies in §3.1, §3.2, §3.4; chaining result in §3.6; phase-error consequence in §3.8; hot-water band story in §3.9 | Move numbers to Results or SI; one sentence per check in Methods | A |
| M2d | What is sampled, is it enough | Partly answered (5,200 diaries per fold, 100,000-person synthetic population, deterministic integerisation). Not answered: why 5,200 is enough for the per-band MAE | P5: sample-size statement plus a bootstrap interval on each Table 3 margin from the existing populations | B |
| M3 | Gap to a benchmark must not undermine the conclusions | The failing downstream checks (load-shape R² 0.03-0.43, hot-water per-person band) are presented at length | P4: one Results subsection that states which conclusions depend on the downstream half (only the peak-timing result) and which do not (the transfer verdict) | A + D |
| M4, D15 | More figures on occupancy and energy | 6 data figures exist; none shows an occupancy (at-home) profile by hour per country, real against generated | One plot from frozen data: at-home share by hour, real vs generated vs raked donor, per fold | B (plot) |
| D2 | Include the authors' own prior work in the comparison table | One own row (Iseri et al., 2026). 2J (resubmitting to Applied Energy) and 3J are not cited | P12: decide which companion papers to cite; own rows scored on the same criteria as the others | A |
| D3, D4 | Define terms at first use | Yes: LOCO, IPF, MAE, MAPE, TMYx, TABULA, CREST, AUC, "fold", "band", "cell", "null", "gate", "board", "Y25-44", "Y_GE65", `FACTORF`, `dia_wt_a`, `coefi2` | P1: define once or replace with plain words; variable names out of the main text | A |
| D5 | State the difference from the closest paper | No closest competitor is named; §1.2 and §6.4 rest on "the author searched ... did not find" | P7: a deep-research prompt that names the closest published LLM or generative synthetic-population work; one explicit paragraph against it | E + A |
| D6 | Why does it matter for building energy? | Weak for this venue: the building-energy stake (occupancy schedules drive stock models, many countries lack microdata) is one paragraph | P2: open on the building-energy need, cite the stock-modelling use of time-use data (from P7) | A + E |
| D7 | Contributions as scientific and practical statements | Four contributions; the third ("the apparatus") and fourth ("carried to its end regardless") read as project process | Rewrite as 2 scientific (transfer does not beat raking; direction vs amplitude diagnostic) + 2 practical (use raking for data-poor countries; an evaluation protocol for generative occupancy models) | A |
| D8, D9, D10 | Dataset-role table; one "Proposed framework" section | Datasets, Methods and Experimental Design are three chapters with 17 sub-sections; building parameters and weather sit under Datasets | P2: one framework section, six sub-sections; Table 2 extended with a "role in this study" column | A |
| D14 | Repeated descriptions | Yes: the weather-station story is told in §2.3 and again in §3.7; the England-only TABULA point twice; the secondary-activity "one fact prevents a misreading" twice (§3.9, §5.9); the shared-reference argument in §3.5 and §6.3; the 1.1-3.9 factor about seven times | Say each once | A |
| D16 | Text numbers must match figures | Known open item: campaign 35,290 cells (11,510 / 11,710 / 12,070) vs scorer 35,090 completed cells vs "840 Madrid cells did not complete" (35,290 − 35,090 = 200, not 840) | P9: number sheet; resolve this one first | B |
| D18, D19 | Small effects: decompose; lead with the shape metrics | §5.11 heating effect is a null on both channels | Keep the null short; the peak-timing result leads the downstream half | A |
| D20 | Figures too small | Check Figure 7 (three panels) and Figure 4 (two panels) at print width | Split any panel unreadable at 190 mm | A |

### Reviewer 2

| 2J # | Request | Same problem in 4J? | Action for 4J | Class |
|---|---|---|---|---|
| 1 | Report style; move internal QA to SI; plain terms | Yes (lesson 1) | P1 | A |
| 2 | External validation of the hourly profile against measured data | Yes, none for any country | P8: deep-research prompt for measured or published national residential hourly electricity profiles for Spain, Italy and the UK (candidates to be checked, NOT VERIFIED: regulator or system-operator standard load profiles such as the UK profile classes). If usable, compare normalised shape and peak hour; if not, soften "load shape" to "appliance timing" | E, then B or D |
| 4 | Abstract in plain prose | No. 517 words, with "*Context.* *Gap.* *Aim.*" labels that Elsevier does not print, seven-digit parameter counts | Rewrite in about 200-250 words, no labels, the limit read from the live Energy and Buildings guide | A |
| 5 | Delete meta-descriptions | Yes: "reported rather than suppressed", "stated rather than absorbed", "named here rather than left to be found", "This result must be told with its history", "It did not hold. This paper reports that", "There is no subset of Table 3 in which the method worked" | Delete or rewrite as plain statements | A |
| 6 | Calibration closure is not validation | Yes: the appliance model is calibrated to published cycle counts, and the hot-water replacement check scores the model against its own source's 200 litres | Name both "calibration" or "consistency check"; never "validation" | A + D |
| 7 | Figures too small | See R1-D20 | | A |

### Reviewer 3

| 2J # | Request | Same problem in 4J? | Action for 4J | Class |
|---|---|---|---|---|
| 1, 2, 4 | Future-year calibration and scenarios | Not applicable | Nothing | |
| 3 | No causal claims beyond the design | Mild: "the entire six-hour spread is the activity data speaking" (§5.8) is true only inside the model, and the diaries are generated ones that lost the transfer test | P3 decides the wording | D |
| 5 | Separate calibration from independent checks | Yes (see R2-6) | Two labelled parts in the framework section: what was fitted, what was checked independently | A |
| 6 | How were intervals built? | No intervals on the primary result | P5 | B |
| 7 | Where do thresholds come from; set before the results | Well answered by pre-registration and SI S1 provenance. Not said plainly: the primary bar is "margin above zero", so it has no threshold to tune | One sentence in Methods; keep SI S1 | A |

### 2J weaknesses the reviewers did NOT raise (2J plan §5), checked against 4J

| 2J item | Applies to 4J? | Action |
|---|---|---|
| Survey waves confounded with the effect being studied | **Yes, in a new form:** the three waves are different years (2009-10, 2013-14, 2014-15), so survey year is confounded with country, and therefore with the leave-one-country-out split. Not stated anywhere | One limitation sentence |
| Novelty table never tested by a systematic search; scoring criteria not stated | Yes: Table 1 has 6 rows, two of them reviews, **no language-model or deep generative competitor at all**, and no scoring criterion per column | P7 |
| Reference errors | Re-verified 2026-09-17 (22/24 exact, 2 fixed). But the list is **thin: 24 entries**, none on LLMs for tabular or sequence data beyond LoRA, none on synthetic population generation after 1996 besides Lovelace 2015. The revised 2J has 48 | P7: target about 40-50 vetted references |
| Companion paper status wrong | 2J and 3J not cited; if cited, use their current status | P12 |
| Figures below journal dpi | Check (not yet checked for 4J) | P14 |

---

## 3. Problems specific to 4J, found in this read

These were not in the 2J reviews, but an Energy and Buildings reviewer is likely to find them.

1. **The model fails in-sample too, and this sits in Limitations (§7.1).** The held-in regression check
   misses the bar on all six training-country cells (Table 4). A reviewer will say: this is a training or
   generation limitation, not a transfer result, so the title's framing ("cross-national transfer") does
   not follow. It must be answered in Results and Discussion, not in one Limitations paragraph. Two
   honest options: (a) report the in-sample MAE against the donor pool beside the transfer MAE, so the
   reader sees how much of the gap is transfer and how much is generation; (b) narrow the claim to "a
   fine-tuned model does not beat raking, in or out of sample". **B** (the held-in numbers exist) + **D**.
2. **The backbone is never named** (paper and SI S2). Name all three models and their revisions from the
   training record. **B**, trivial, blocking.
3. **The downstream headline rests on generated diaries.** Table 7's 14:00 / 18:00 / 20:00 peaks come from
   the generated populations, which lost the transfer test by 1.1 to 3.9 times. Without the same appliance
   run on real diaries, a reviewer can say the peaks are artefacts of a model the paper just rejected.
   This check decides whether the "practically useful half" (§6.5) survives. **P3.**
4. **Pre-registration is internal.** The file was "frozen and hash-locked" on 2026-08-18, but not
   deposited in a public registry. Reviewers expect a registry link (for example OSF) for the word
   "pre-registered". Depositing now would carry today's date, not 2026-08-18. Honest options: deposit the
   frozen file and its hash now with a note of the internal freeze date, and write "registered internally
   before training (hash-locked), deposited at submission". Author decision D4. **A + D.**
5. **An internal instruction is printed in the paper.** §3.4: "This stage is therefore never to be
   written as complete: it closes at four of five definition-of-done items ... and the board is never to
   be reported as 36 of 36." Delete before anyone sees it. **A**, blocking.
6. **Half the building-energy content is about things not claimed.** §4.4 describes a 35,290-cell
   campaign whose results are "not claimed anywhere in this paper", a 410-cell "core-era" campaign kept as
   a "record", two provenance-link gaps, and §7.10 lists unfinished items. For a journal paper, anything
   not claimed goes to the SI in one sentence or is cut. **A.**
7. **Length.** About 17,100 words from Introduction to Conclusion; Discussion about 2,600 and Limitations
   about 2,400. The revised 2J halved both sections. Target for 4J: about 9,000-10,000 words in the main
   text (confirm the Energy and Buildings limit, P14), Discussion about 1,200, Limitations about 900 (all
   points kept, SI carries the long form). **A.**
8. **Title.** "Beaten by Real Diaries: A Pre-Registered Leave-One-Country-Out Test of a Fine-Tuned Language
   Model..." is 29 words, opens on a slogan, and uses "Leave-One-Country-Out" jargon. Author's call (D2);
   a plain draft is offered there.
9. **"Britain" is not the UK.** The paper calls the UK fold "Britain" for brevity while the survey covers
   the whole United Kingdom. Use "UK" throughout. **A.**
10. **Excess precision reads as a log.** "7,377,965,056 parameters", "0.508305 against 0.513494",
    "1.70 standard deviations", "worst absolute marginal deviation below 1e-13". Round in the text; exact
    values in SI. **A.**
11. **Front matter in report order; generative-AI declaration missing.** Declarations and the graphical
    abstract sit before the Introduction. Elsevier order: CRediT, competing interests, funding, data,
    **declaration of generative AI use** (all the more expected in a paper about language models),
    acknowledgements, at the end before the References. Funding spelling "Voltage-Age Seed fund" here vs
    "Volt-Age Seed Fund" in the revised 2J: one spelling for all papers. **A.**
12. **"The author searched ... searched 2026-09-13"** (§1.2, §6.4, §7.1). A journal expects a cited
    literature review, not a dated personal search. After P7, replace with citations; keep at most one
    sentence on search scope. **A + E.**
13. **Anecdotes in the Introduction.** §1.3 "more than fifteen hundred employed thirteen-year-olds from a
    single donor day" is a debugging story. Keep the principle (marginals do not certify the joint), move
    the anecdote to SI. **A.**

---

## 4. The author's 15 comments on 2J, applied to 4J up front

| 2J comment | What it means for 4J |
|---|---|
| C1 Title in "Centered" style | Same build fix in `tools/4thJ_build_submission_docx.sh` |
| C3 Short, simple sentences everywhere | 4J sentences often run 40-60 words (§1.1, §1.2, §3.5, §6.x). One idea per sentence, about 20-25 words; a script lists every sentence over 30 words before and after |
| C6 Highlights: purpose, finding, benefit | Current highlights are close. Replace "hash-locked" and "92x trainable parameters" with plain words; add the practical benefit ("reweighting real diaries is the better tool for countries without microdata") |
| C11 Table 1 to an appendix | Same, after P7 enlarges it |
| C14 No separate "prior line" section | 4J has none; keep the one self-citation in §1.2 |
| C16 Merge aim and contributions | §1.5 has four contribution paragraphs then the aim; merge into one short paragraph |
| C18 Section 2 into 5-6 sub-sections; most equations to appendix | Datasets + Methods + Experimental Design = 17 sub-sections before Results; merge to six (P2) |
| C19 One-sentence captions | Captions are already short; move the "how to read" paragraphs under Tables 4 and 5 into the text |
| C22 A source for every equation | One Gemini prompt listing each equation (like 2J's dr_2J-17) |
| C26 Simple method figures | Figure 2 (LOCO design) exists. Add one only if an equation needs it (fictional-country slope and R²) |
| C35 Nomenclature before the appendix | Same (new) |
| C41 Paragraph, figure, paragraph, figure | Figures 1 and 2 are stacked at the end of §1.5; Table 1 sits in the middle of §1.2 |
| C47 Discussion cut by half | About 2,600 words to about 1,200; §6.6 (process lessons) goes to SI |
| C49 Limitations cut by half, keep every point | About 2,400 words to about 900; §7.10 (unfinished items) and §7.8-§7.9 fold into two sentences each; every point listed in a checklist and ticked |

---

## 5. Work packages, in the order they should be done

Format per project rule: aim, steps, expected result, test.

### P3. Appliance peaks from real and raked-donor diaries (B, else C; critical path)
**Aim.** Decide whether the paper's practically useful result (the six-hour peak spread) holds for real
diaries, and turn it from a claim about generated data into a comparison.
**Steps.** (1) Check whether the Step 9 or Step 11 records already hold appliance-trigger runs on the
real corpus or on the raked-donor populations (`Step9_docs/4thJ_09_enduseLoads.md:90` says the step
consumes generated diaries; the real corpus is used only to estimate the trigger probability, line 291).
(2) If not, run the same appliance model, same seed rule, on (a) the real held-out diaries and (b) the
raked-donor diaries, per country. This is Python, not EnergyPlus: small, Speed only, sbatch. Controls
first: reproduce one published generated-population peak (Spain 14:00, 518 W) before trusting the run.
**Expected.** A three-row table (real, raked donor, generated) of peak hour and peak power per country.
If real diaries give the same ordering, the result strengthens and §6.5 can say so. If not, the downstream
claim narrows (D) and the paper says generated diaries do not carry the timing.
**Test.** Values read from the output files, named by path; the control reproduces exactly.

### P2. New structure (A)
Target, following the revised 2J:

| New | Title (draft) | From 4J today |
|---|---|---|
| 1 | Introduction: 1.1 Occupancy data for building stock models, and the countries without it; 1.2 Existing work and the gap (Table 1 to Appendix A); 1.3 Aim and contributions | §1.1-§1.5 |
| 2.1 | Data: three surveys, census tables, building parameters, weather (one dataset-role table) | §2, Table 2 |
| 2.2 | Harmonisation and text representation of diaries | §3.1, §3.2 |
| 2.3 | Fine-tuned model and synthetic populations | §3.3, §3.4, §3.6 |
| 2.4 | Leave-one-country-out design and the comparison baselines | §3.5, §4.1, §4.2 |
| 2.5 | From diaries to building loads: archetypes, gains, appliances, hot water | §3.7, §3.9, §4.3, §4.4 (one sentence) |
| 2.6 | Metrics, statistics and the pre-registered decision rule | §4.5 (one paragraph), P5, P6 |
| 3 | Results: 3.1 transfer against raking; 3.2 capacity; 3.3 direction vs amplitude; 3.4 joint structure and the Markov baseline; 3.5 appliance timing (with P3); 3.6 heating (short null); 3.7 privacy (short) | §5.1-§5.11 |
| 4 | Discussion (about 1,200 words) | §6.1-§6.5, §6.7 |
| 5 | Limitations (about 900 words, all points) | §7 |
| 6 | Conclusion | §8 |
| | Nomenclature · Appendix A (Table 1) · Appendix B (equations) · declarations · References | new |

To SI: §3.8 phase-error story (one Methods sentence stays: the schedule clock was checked against an
independent implementation and every run was repeated after a correction); §6.6 lessons; §7.10; check
tallies from §3.1-§3.4; the 410-cell record; the documentation-defect notes (§5.3, §7.10, S2).

### P1. From report to paper: vocabulary and meta text (A)
**Steps.** (1) Jargon inventory in `writing/submission/IMP/prep/jargon_inventory.md`: gate, board, band,
cell, fold, null, coverage clause, mutation battery, refusal, definition-of-done, hash-locked, core-era,
no-core, day origin, re-based, Britain, Y25-44, Y_GE65, weight variable names, "the reported model",
"ruling". Replace or define each once ("check" for gate, "tolerance" for band, "held-out country" for
fold, "baseline" for null). (2) Delete every meta sentence (list in Section 2, R2-5). (3) Delete the §3.4
internal instruction (Section 3 item 5). (4) Round excess precision (Section 3 item 10).
**Test.** A scripted search of the built .docx finds none of the inventory terms undefined, and no
sentence from the meta list.

### P5. Intervals and sample size for the primary result (B)
**Aim.** 2J R1-M2d and R3-6, on the one table everything rests on.
**Steps.** (1) From the existing generated and raked-donor populations, a bootstrap over diaries of each
Table 3 margin (resampling diaries within each country and age band; say so). (2) State the sample sizes
per band. (3) State once that training used one seed per arm and what that means (the §5.4 seed-noise
probe covers generation noise only).
**Expected.** Table 3 gains a 95 % interval column. The UK aged 65+ cell (-2.70) is the one to watch: if
its interval crosses zero, the text says "8 of 9 cells clearly, the ninth not distinguishable" and the
pre-registered verdict (which has no interval) is reported unchanged beside it.
**Test.** Script quoted with `file:line`; the point estimates reproduce Table 3 exactly before any
interval is trusted. Runs via sbatch or locally, never on the login node.

### P10. In-sample against out-of-sample (B + D)
**Aim.** Answer Section 3 item 1 before a reviewer does.
**Steps.** Read the held-in regression outputs (six training-country cells) and set the model's
in-sample MAE beside the donor pool's in-sample MAE and beside the transfer MAE.
**Expected.** One short table or two sentences in Results 3.1 saying how much of the gap exists already
in-sample. The title and aim wording follow (D2).
**Test.** Numbers read from the Step 6 output files, named by path.

### P6. Equations with sources (A + E)
Write the formulation (list in Section 2, R1-M2b). Keep in the text only the ones that carry the argument
(proposal: raking update, time-budget MAE and margin, fictional-country slope and R², gain
redistribution, appliance trigger); the rest to Appendix B. Then one Gemini prompt,
`DeepResearchPrompts/RL34_4J_equation_sources.md`, asking for the standard source of each; mark own
definitions "defined here". Vet with the usual 7 steps before citing.

### P7. Literature, novelty table, references (E + A)
**Steps.** (1) One deep-research prompt (`DeepResearchPrompts/RL35_4J_literature_and_competitors.md`),
run by the author, covering: language models for synthetic tabular data and for activity or mobility
sequences; synthetic population synthesis (IPF, combinatorial optimisation, deep generative) and
transfer across populations; time-use data in building stock energy models; cross-national occupancy
differences; evaluation of generative models on held-out populations; membership inference on
fine-tuned models; pre-registration in energy research. It must try to break Table 1 and name the closest
competitor. (2) Rebuild Table 1 with the vetted rows and one scoring sentence per column. (3) Replace the
"author searched ... 2026-09-13" sentences with citations.
**Target.** About 40-50 vetted references. **Test.** Every new citation opened by the author; vetting file
beside the return.

### P8. Independent check of the appliance timing (E, then B or D)
Prompt (can go in the same RL35 run or a separate RL36) for published hourly residential electricity
profiles for Spain, Italy and the UK. If usable data exists, compare normalised weekday shape and peak
hour per country against the P3 real-diary and generated-diary curves. If not, say plainly that timing is
checked only against real diaries through the same model, and write "appliance timing" rather than
"load shape".

### P9. Number sheet and provenance (B)
Like 2J's `prep/results_number_sheet.md`: every number in abstract, highlights, text, tables and figures,
with its source file. First item: reconcile 35,290 / 35,090 / 840 (or remove the campaign numbers from the
main text under P2, which makes the question disappear from the paper but not from the record). Run
before the rewrite and after it; the two must match except where P3, P5 or P10 add numbers.

### P4. Reframe the downstream half (A + D)
Keep every verdict and number. Change the weight: the transfer verdict and the diagnostic are the paper;
the building half is one clear positive (appliance timing, after P3), one clear null (heating), and the
checks that did not pass in one short paragraph with their reason. Say in one sentence that the transfer
conclusion does not depend on any downstream check.

### P12. Consistency with the other papers (A)
Decide which companion papers to cite (1J JBPS status, 2J under review at Applied Energy once submitted,
3J); one funding spelling for all; the Table 1 own rows scored on the new criteria. Keep the existing
self-citation.

### P13. Writing pass (A), last
Apply Section 4: short sentences, new abstract (about 200-250 words, no labels), new highlights (at most
85 characters), captions, alternation, Nomenclature, title style, declarations at the end including the
generative-AI declaration. Numbers identical before and after (P9).

### P14. Journal package and final audit
Read the live Energy and Buildings Guide for Authors (the 2J trick: the author saves the page with a
browser, since the fetch tool gets 403): abstract limit, word or page limit, highlights file, graphical
abstract file, figure dpi, declaration order, AI-use rules. Write the cover letter (none exists for 4J
yet). Then one pre-submission audit prompt run by the author in Gemini and a second model, both vetted,
every accepted item fixed and re-checked on the installed .docx.

---

## 6. Order of work

```
Step 0  author answers the decisions in Section 7
Step 1  checks that decide what can be claimed (reads first, compute only if needed):
        P3 step 1 (do real-diary appliance runs exist?) -> P10 -> P5 -> P9 (first pass)
        at the same time: write the P6, P7, P8 prompts; author runs them in Gemini
Step 2  compute only with author go: P3 step 2 (appliance model on real and donor diaries, Speed)
Step 3  restructure and rewrite: P2 -> P1 -> P4 -> P12 -> P6 (after vetting) -> P7 (after vetting)
Step 4  P13 writing pass -> P9 second pass -> rebuild manuscript and SI -> checks on the installed files
Step 5  P14 journal package, cover letter and external audit -> fix -> submit
```

Biggest risk: P3 finds that real diaries do not reproduce the six-hour spread. Then the downstream
"practically useful half" narrows to "the generated diaries place the peak at different hours, the real
ones at ...", and the Highlights and Conclusion change with it.

---

## 7. Decisions the author owns (recommendation first)

| ID | Decision | Recommendation |
|---|---|---|
| D1 | Submit 4J now, or after this plan? | After. The paper is scientifically finished; the 2J reviews are a free preview of the presentation objections, and a desk reject costs months |
| D2 | Title | Drop the slogan and the jargon. Draft: "Can a fine-tuned language model generate time-use diaries for a country without survey data? A pre-registered test against reweighted real diaries". Author's call |
| D3 | Approve P3 compute (appliance model on real and raked-donor diaries; Python on Speed, small) if the runs do not already exist | Yes; it protects the paper's only downstream positive result |
| D4 | Pre-registration wording and deposit | Deposit the frozen file and its hash on a public registry at submission; wording "registered internally and hash-locked before training on 2026-08-18; deposited at submission" |
| D5 | Target length | About 9,000-10,000 words main text (after the guide is read); everything not claimed goes to the SI |
| D6 | Venue | Stay with Energy and Buildings, but only after P2 and P7 re-centre the paper on building-stock occupancy. If the author prefers to keep the ML weight, Building and Environment (secondary) has the same fit question; an ML-oriented energy venue would be a new venue search |



**Author answers (2026-09-23, final; supersedes the withdrawn 2026-09-22 answers):** all six as
recommended. D1 improve first, then submit. D2 plain draft title above. D3 P3 compute APPROVED (Python on
Speed, sbatch only, inside the 32-CPU cap, never `histnu`) if the runs do not already exist. D4 deposit the
frozen file and hash on a public registry at submission, with the "registered internally ... deposited at
submission" wording. D5 about 9,000-10,000 words main text (confirm against the guide, P14). D6 Energy and
Buildings, after P2 and P7 re-centre the paper on building-stock occupancy.

---

## 8. What closes this round

- [x] Section 7 decisions answered (2026-09-23, all as recommended)
- [ ] P3, P10, P5 done, each with its implementation doc in `writing/submission/IMP/impl/`
- [ ] Deep-research returns (P6, P7, P8) run by the author and vetted before any citation
- [ ] Every row of Sections 2 and 3 mapped to a change (internal response map, `IMP/prep/response_map.md`)
- [ ] Manuscript and SI rebuilt; numbers identical to the number sheet; checks green on the installed files
- [ ] Journal guide read live; declarations complete including generative AI; cover letter written
- [ ] Pre-submission external audit run and vetted
- [ ] `Prompts/RESUME.md`, the tracker artifact and memory updated (the 4J closure ritual)
