# 2J paper: improvement plan from the author's comments (2026-09-22)

**Source:** 15 Word comments in `manuscript/2J_manuscript_AE_revised.docx` (saved 2026-09-22 14:48).
**Checked:** the .docx text matches the .md text (only comments were added, no text edits, no tracked
changes). So `manuscript/2J_manuscript_AE_revised.md` stays the master file; the .docx is rebuilt from it.
**Status:** FULLY APPLIED 2026-09-22 (plan log (ev); S4 in (ew), vetting in `deepResearch/dr_2J-17_VETTING.md`).

**Rules that stay in force during every step below**
- No number changes. Every number in the paper stays as it is; this is a writing and layout revision.
- Title stays verbatim (author order); only its paragraph style changes (comment C1).
- No em/en dashes in prose; "limitation", never "failure"; claim the designed 2030 shift, never the level.
- Keep every self-citation and the "how much vs when" contrast with the prior papers when Section 1.4 is
  folded in (removing them once before created a self-plagiarism risk).
- Never create images: new method figures are image PROMPTS the author runs in Gemini.
- Deep research is external: equation sources come from a Gemini prompt the author runs; nothing is cited
  until the author's results are vetted.
- Backup the .md and .docx before the first edit (`manuscript/prep/*_pre_IMP_2026-09-22.*.bak`).

---

## 1. The 15 comments, one line each

| # | Where | Comment (short) | Plan step |
|---|---|---|---|
| C1 | Title | Use "Centered" paragraph style | S10 |
| C3 | Abstract | Simpler, shorter sentences; **apply to the whole document** | S8 |
| C4 | Abstract | (empty comment on the same sentence as C3) | treated as part of C3 |
| C6 | Highlights | More striking: purpose, findings, benefit | S7 |
| C11 | Table 1 (Sec 1.2) | Move to the appendix | S2 |
| C14 | Sec 1.4 | Do not keep a separate "prior line" section; fold it into other sections (reads like a report) | S1 |
| C16 | Sec 1.5 | Merge the aim paragraph with the contributions paragraph | S1 |
| C18 | Sec 2 | Merge 12 sub-sections into 5-6; move most equations to the appendix, keep the essential ones | S2, S3 |
| C19 | Figure 1 caption | All figure and table captions: one short sentence; the rest goes into the text | S6 |
| C22 | Eq. 3 (Sec 2.2) | Give a source reference for every equation; write Gemini deep-research prompts | S4 |
| C26 | Sec 2.5 | Add simple method figures that explain the equations; write Gemini image prompts | S5 |
| C35 | Symbol list | Move it, maybe just before the appendix | S2 |
| C41 | Figure 4 (Sec 3.4) | Alternate paragraph / figure / paragraph / figure; no figures stacked together | S6 |
| C47 | Sec 4 Discussion | Shorten by 50 percent | S9 |
| C49 | Sec 5 Limitations | Shorten by 50 percent, keep every point | S9 |

---

## 2. Steps, in the order they should be done

Structure first (things move), then shortening, then the sentence-by-sentence rewrite last, so the
plain-language pass is done once on the final text.

### S1. Introduction: fold Section 1.4 away and merge the 1.5 paragraphs (C14, C16)
- Delete the heading "1.4 Departure from the authors' prior line".
- Its first paragraph (what the prior C-VAE line did, with its three citations) moves into Section 1.2,
  where the gap is described: the prior work becomes part of the research track it belongs to.
- Its second paragraph (prior paper asked "how much"; this paper asks "when") moves into Section 1.5 as
  one or two sentences in front of the contributions, so each contribution reads as a clear step beyond
  the prior work.
- Section 1.5: merge the one-sentence aim with the "three scientific contributions" paragraph into one
  paragraph (C16). Old 1.5 becomes 1.4.
- Check after the move: all three self-citations still appear in the text and in the reference list.
- Result: Introduction goes from 5 to 4 sub-sections.

### S2. New appendix and new places (C11, C18, C35)
Create **Appendix A** at the end of the main paper (after the Conclusion, before the References, the usual
Elsevier order). The Supplementary Information file stays as it is for the long checks.
- **Table 1** (framework dimensions, nine studies) moves to Appendix A as **Table A1**. Section 1.2 keeps
  its one-sentence summary and points to Table A1.
- **Equations moved to the appendix** (see S3 for the list) go to Appendix A as A.1, A.2 and so on.
- **Symbol list**: moves to just before Appendix A (after the Conclusion), renamed "Nomenclature"
  (Elsevier's usual name). It is trimmed to the symbols still used in the main text plus the appendix.
- Section 2 is merged from 12 into **6 sub-sections**:

| New | Title (draft) | Old sections merged |
|---|---|---|
| 2.1 | Data and diary preparation | 2.1 (with Table 2) |
| 2.2 | Generative occupancy model and calibration | 2.2 + 2.3 |
| 2.3 | From diaries to household schedules | 2.4 + 2.5 |
| 2.4 | Activity-driven end-use loads | 2.6 |
| 2.5 | 2030 scenarios, household sampling and stock weighting | 2.7 + 2.8 + 2.9 |
| 2.6 | Load-shape metrics, statistics and comparison methods | 2.10 + 2.11 + 2.12 |

- Every cross-reference ("Section 2.7", "Sections 2.1 to 2.12", "Eq. 13" and so on) in the main text, the
  SI and the Figure 1 caption is updated. A final search confirms no old section or equation number is left.

### S3. Which equations stay in the main text (C18)
The paper has 18 numbered equations. Proposed: keep the **6 that carry the paper's argument**, move 12.

| Eq. | What it is | Proposal |
|---|---|---|
| 1, 2 | 10-minute diary slots to 30-minute activity and at-home slots | Appendix |
| 3 | Training loss of the generative model | Appendix (SI S1 already details the model) |
| 4, 5 | Raking targets and slot adjustments | Appendix |
| 6, 7 | Household averaging of at-home and metabolic slots | Appendix |
| **8** | **Activity-driven equipment power per slot** | **Keep** |
| **9** | **Calibration scalar to the national end-use survey** | **Keep** |
| **10** | **2030 scenario construction (persistence parameter)** | **Keep** |
| 11 | Simple random sample of 50 households | Appendix (one sentence in the text is enough) |
| **12** | **Stock aggregation weights** | **Keep** |
| 13, 14 | Circular mean and spread of peak hour | Appendix |
| 15 | Paired household difference | Appendix |
| **16** | **Confidence interval of the paired change** | **Keep** |
| 17 | Fixed-schedule arm | Appendix |
| **18** | **Average-profile comparison arm** | **Keep** |

The three short inline load-shape definitions (load factor, midday share, evening ramp) stay inline,
because they define the paper's main outputs. Equations are renumbered 1 to 6 in the main text and
A.1 to A.12 in the appendix.

### S4. A source reference for every equation (C22)
Most equations are either standard methods (need a textbook or original citation) or the authors' own
definitions (need no citation, but the text should say "defined here"). Current reference list has 36
entries; none of the standard sources below is in it yet.

| Eq. | Likely source type | Candidate sources to verify (NOT yet checked) |
|---|---|---|
| 1, 2 | Time-use harmonization practice | HETUS guidelines (Eurostat 2018, already cited) |
| 3 | Cross-entropy losses; encoder-decoder with cross-attention | Deep-learning textbook; the original transformer paper |
| 4, 5 | Raking / iterative proportional fitting | Deming and Stephan 1940; Deville and Sarndal 1992 |
| 6, 7 | Metabolic weights per activity | Compendium of Physical Activities |
| 8 | Activity-to-appliance load models | Richardson et al. and Widen et al. (already cited; confirm they fit) |
| 9 | Calibration to national end-use survey | NRCan SHEU (already cited) |
| 10 | Work-from-home persistence | Own definition; Barrero et al. 2023 (already cited) for the idea |
| 11 | Simple random sampling | Survey-sampling textbook (Cochran) |
| 12 | Stock weights | Own definition |
| 13, 14 | Circular statistics | Fisher; Mardia and Jupp |
| LF, midday, ramp | Load factor, ramp | Power-systems textbook; Denholm et al. (already cited) |
| 15, 16 | Paired t interval | Statistics textbook |
| 17, 18 | Fixed and average schedules | Own definitions; cite a standard-schedule source |

Deliverable: one Gemini deep-research prompt, `deepResearch/dr_2J-17_equation_sources_gemini_prompt.md`,
listing each equation verbatim and asking for the original or standard source, with the house rules
(open every source, check every DOI on Crossref, "NOT FOUND" is better than an invented reference, no
dashes). The author runs it; we vet the result (the usual 7-step check) before any reference enters
the paper. Equations marked "own definition" get the words "defined here" instead of a citation.

### S5. Simple method figures (C26)
Proposed four new method figures, each an image prompt for Gemini (author generates, we never draw):
1. **From diary to hourly schedule** (Eqs. 1, 2, 6, 7): one person's 10-minute diary, grouped into
   30-minute slots, averaged over household members, reduced to 24 hourly values.
2. **Raking in one picture** (Eqs. 4, 5): model at-home share vs target share for one slot, and the
   slots flipped to close the gap.
3. **How activities become equipment power** (Eq. 8): people at home, their activities, shared vs
   personal devices, the co-occupancy factor, and the calibration step (Eq. 9).
4. **The 2030 scenarios** (Eq. 10): the 2005-2015 trend line, the 2022 jump, and the three persistence
   settings (keep all, keep half, keep none). If the author prefers, this one can instead be a plot
   from the paper's own data (plots from data are allowed).
Deliverable: four prompt files in `submission/figures/Prompts_Images/` (same style as
`Figure_01_workflow_prompt.md`); every number in a prompt copied verbatim from the paper. After the
author installs the images, each is opened and checked against the text before it is accepted.
Adds 4 figures (8 to 12 in the main paper). Figures in the appendix are an option if the count
becomes a concern once the Applied Energy guide is read.

### S6. Captions and figure placement (C19, C41)
- Every figure and table caption in the main paper and the SI becomes **one short sentence**. What is
  cut from a caption (samples, what the bars mean, which households) moves into the paragraph that
  cites the figure, so no information is lost.
- Layout rule: **paragraph, figure, paragraph, figure**. No two figures or tables in a row.
  The worst case today is Section 3.4 (Figures 4, 5 and 6 back to back); each is placed right after
  the paragraph that first discusses it. Same check for Table 2 and Figure 1 in Section 2 and for the
  new method figures.

### S7. New Highlights (C6)
Elsevier limit: 3 to 5 bullets, at most 85 characters each (to be confirmed in the guide). Aim:
purpose, method, main findings, benefit. Draft for the author to choose from (all numbers already in
the paper):
- Survey-based household occupancy model runs from 2005 to 2030 across Canada.
- Work from home changes when homes use electricity, not how much they use.
- Annual electricity is nearly flat, but midday share and load factor rise.
- Four 2030 scenarios show how much of the pandemic shift may persist.
- Average schedules hide the spread of household peak times; our model keeps it.
Then the Abstract is rewritten in short sentences (part of S8) around the same message.

### S8. Plain, short sentences in the whole paper (C3, applies everywhere)
Rule for the rewrite: **one idea per sentence**, about 20-25 words at most, no stacked "and ...,
and ..., comparing ..." chains, no long lists inside a sentence. Order: Abstract, Highlights, then
Sections 1 to 6, Appendix, SI.
- Method: split long sentences; turn inline lists into short separate sentences; keep every fact.
- Check after the pass: a script lists every sentence over 30 words that is left, and every number
  before and after is compared (must be identical).

### S9. Shorten Discussion and Limitations by half (C47, C49)
- **Discussion:** about 1,290 words now, target about 640. First list every argument as a checklist,
  keep the ones that interpret results for grid planning and the literature, drop repetition of
  Results numbers and of Limitations.
- **Limitations:** about 1,420 words now, target about 710. **All 12 limitations stay**, each shortened
  to 2-3 sentences (what it is, what it affects). A checklist of the 12 is ticked after the rewrite.

### S10. Title style, rebuild and final check (C1)
- Title paragraph uses the "Centered" style (set in the build step so it survives every rebuild).
- Rebuild the .docx with `py impl/T94_scripts/build_main_docx.py`; rebuild the SI the usual way.
- Final checks: numbers unchanged (before/after compare), no old section or equation numbers, every
  figure and table cited in order, no two floats in a row, word count reported, all self-citations present.

---

## 3. What the author owes

1. Say yes or no to the proposals above, especially: appendix inside the main paper (S2), the 6 kept
   equations (S3), the new Section 2 titles (S2), the four method figures (S5), the Highlights draft (S7).
2. Run the equation-source prompt in Gemini once it is written (S4).
3. Generate the four method figures in Gemini from the prompts (S5).
4. Still open from before: save the Applied Energy Guide for Authors as PDF (limits for highlights,
   abstract, figures and words are not yet verified).

## 4. Rough size of the work

| Step | Who | Size |
|---|---|---|
| S1-S3 structure moves | agent | medium |
| S4 equation-source prompt | agent writes, author runs Gemini | small + author time |
| S5 four image prompts | agent writes, author runs Gemini | small + author time |
| S6 captions and placement | agent | small |
| S7 Highlights | agent drafts, author picks | small |
| S8 plain-sentence pass | agent | large (whole paper + SI) |
| S9 shorten two sections | agent | medium |
| S10 rebuild and checks | agent | small |

Suggested order of work: S1, S2, S3, S6, S9, S8, S7, S10; S4 and S5 prompts can be written first so
Gemini runs while the text work goes on.
