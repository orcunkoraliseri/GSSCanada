# P14 - journal package (cover letter, highlights, declarations, reviewers, audit prompt, open items)

Written 2026-09-23. Target journal: Building and Environment (Elsevier). Read first: plan
`submission/IMP/3J_improvement_plan_from_2J_lessons_2026-09-22.md` (P14, decisions D1-D7, §7/7a);
execution doc `implementation/3J_IMP_execution_2026-09-22.md` (status table, log); facts
`implementation/IMP/P12_consistency_facts.md`; chapters_v2 00/01/05/06/10 (read only, not edited here);
journal requirements `deepResearch_Resources/RV10_building_and_environment_author_requirements.md`
(vetted, per `VETTING_RV09_RV10_2026-08-08.md`; the CRKN 100% APC-waiver claim in RV10 item 30 is
flagged and NOT acted on anywhere in this document).

**Reused, not started from nothing:** `submission/Title_Page_and_Cover_Letter.md` (2026-08-11 draft,
modelled on the 2J title page) supplied the letter's structure, the ethics/data-availability wording
and the "no disclosure of the earlier 0J rejection" reasoning, all kept below. Its central paragraph
(the "85.45 kWh/m2/yr control" framing) is replaced, because the manager's D3 ruling
(execution log, entry beginning "D3 RULING") withdrew the claim that the survey model lowers peak
coincidence; the new lead follows the chapters_v2 abstract and conclusion instead.
`chapters_v2/00_FrontMatter.md` supplied the highlights verbatim (already measured at 75-80 characters
each in `IMP/rewrite_log.md`). `chapters_v2/10_Declarations.md` supplied the declarations text
(CRediT, competing interest, funding, data availability, generative-AI template, acknowledgements),
carried below with the Elsevier-required "Declarations of interest: none" line added and the funding
spelling corrected to "Volt-Age Seed Fund" per `P12_consistency_facts.md` (the 2018 offer-letter
spelling; the old cover letter's "Voltage-Age Seed fund" was a typo, already fixed in chapters_v2).

Numbers that sit inside a `⟦P10R:...⟧` marker in the chapters are written the same way here, never
with an invented value. Companion-paper status is stated only from `P12_consistency_facts.md`: 2J was
rejected by Building Simulation on 2026-09-15 and is not yet submitted anywhere else; 1J was rejected
by JBPS on 2026-09-19 with an invitation to resubmit after major revision. Neither is "under review."

---

## 1. Cover letter draft (350 words)

Date and salutation to be set at submission; addressed "Dear Editor" (Building and Environment does
not publish a single handling editor for unsolicited papers - kept from the old letter's reasoning).

> We are pleased to submit our manuscript, "From One Channel to Four: A Jointly-Trained Time-Use
> Occupancy Model for Mixed-Use Building Energy Simulation (Canada, 2005 to 2030)," for consideration
> as a research article in Building and Environment.
>
> Tall mixed-use buildings stack residential, office, retail and hotel uses on one plant, yet their
> energy models usually run most uses on a single code schedule. This study gives each use its own
> schedule: one jointly trained Transformer generates residential, office and retail presence from
> four cycles of the Canadian General Social Survey time-use diaries (2005 to 2022), and a seasonal
> time-series model of provincial tourism statistics generates hotel presence (hotel guests fall
> outside the survey frame). The four schedules drive EnergyPlus models of two prototype towers in
> Montreal and Calgary, run once on code schedules and once on survey-based schedules, across four
> survey years and nine scenarios to 2030.
>
> Running both schedule sets through the same pipeline separates what survey-based occupancy changes
> from what it does not. It changes who is in the tower and when: hotel guests and residents are
> present at night, while code schedules keep both on office hours. That reaches energy only where
> lighting and equipment follow occupancy, moving office and retail intensity by ⟦P10R:-16 to -20⟧%
> and ⟦P10R:-12 to -15⟧% against the code-schedule tower. Whole-building timing barely moves: the load
> centroid shifts by under ⟦P10R:0.3⟧ hour, and the peak stays a winter-morning plant start-up either
> way. Single-use reference intensity ranges judge the tower poorly: the office floor is missed even
> by the code-schedule tower, which the occupancy model cannot be responsible for.
>
> We report this honestly, including one place it narrowed our earlier reading: an early draft
> credited the survey model with lowering peak coincidence, but the code-schedule control already
> staggers its four uses, so that claim was withdrawn.
>
> Two related manuscripts from this project are in revision, not under review: one declined by the
> Journal of Building Performance Simulation (2026-09-19, invited to resubmit) and one declined by
> Building Simulation (2026-09-15).
>
> The manuscript is original, unpublished, and not under consideration elsewhere. We have no
> competing interests to declare.
>
> Thank you for considering our work.
>
> Sincerely,
> Orcun Koral Iseri, on behalf of both authors

**Not disclosed, kept from the old letter's reasoning:** the earlier rejection of a different, earlier
manuscript (0J) by Building and Environment is not this manuscript's history and is not volunteered.

---

## 2. Highlights (from `chapters_v2/00_FrontMatter.md`, verbatim; character counts re-measured here)

Building and Environment requires 3-5 bullets, each at most 85 characters including spaces
(`RV10_building_and_environment_author_requirements.md` item 2, `STATED`). All five below meet it.

1. Four occupancy schedules drive one mixed-use tower, 2005 to 2030 scenarios. (75)
2. Survey-based schedules put hotel guests and residents in the tower at night. (76)
3. Office and retail energy follow survey occupancy; building peak timing does not. (80)
4. A winter-morning plant start-up sets the building peak under both schedule sets. (80)
5. Single-use intensity ranges cannot judge tenant uses inside a stacked tower. (76)

To be filed as a separate Highlights upload file at submission (Elsevier order; see chapters_v2 HTML
comment on this point, already recorded as an open item in `IMP/rewrite_log.md`).

---

## 3. Declarations

Source: `chapters_v2/10_Declarations.md` (read only; not edited), with the journal's required wording
added where the guide states one (`RV10` items 18-23).

**Declaration of competing interest.** The authors declare that they have no known competing financial
interests or personal relationships that could have appeared to influence the work reported in this
paper. Declarations of interest: none. *(The second sentence is the exact form Building and Environment
requires for a null declaration, RV10 item 22.)*

**Funding.** This work was supported by the Natural Sciences and Engineering Research Council of
Canada (NSERC) [AUTHOR TO CONFIRM: through a Discovery Grant, as 2J states, or a different award type]
and by the Volt-Age Seed Fund, Concordia University. The funders had no role in the study design, in
the collection, analysis and interpretation of data, in the writing of the article, or in the decision
to submit it for publication.

**CRediT authorship contribution statement.** Orcun Koral Iseri: Conceptualization, Methodology,
Software, Formal analysis, Investigation, Data curation, Validation, Visualization, Writing - original
draft. Caroline Hachem-Vermette: Conceptualization, Supervision, Funding acquisition, Resources,
Writing - review and editing.

**Data availability.** This study uses the Statistics Canada General Social Survey time-use public-use
microdata files (2005, 2010, 2015 and 2022 cycles) and the 2021 Census of Population public-use
microdata file. These files are available from Statistics Canada under its licence terms, which do not
allow the authors to redistribute them. The provincial hotel-occupancy series are published by the
Institut de la statistique du Québec and by CBRE and Travel Alberta. The derived occupancy schedules,
building model files and scripts that support the findings of this study are available from the
corresponding author upon reasonable request.

**Declaration of generative AI and AI-assisted technologies in the manuscript preparation process.**
During the preparation of this work the authors used [AUTHOR TO CONFIRM: tool name, e.g. Claude
(Anthropic)] in order to [AUTHOR TO CONFIRM: reason, e.g. improve the language and readability of the
manuscript] [AUTHOR TO CONFIRM: any further tool/reason pairs, e.g. Gemini for literature research and
schematic figures]. After using this tool/service, the authors reviewed and edited the content as
needed and take full responsibility for the content of the published article. *(Wording matches the
Elsevier-prescribed template, RV10 item 18: "the author(s) used [NAME TOOL / SERVICE] in order to
[REASON]. After using this tool/service, the author(s) reviewed and edited the content as needed and
take(s) full responsibility for the content of the publication.")*

**Ethical approval.** This study involves no experiments on human or animal subjects. It uses
anonymized public-use microdata released by Statistics Canada and published provincial tourism
statistics.

**Acknowledgements.** The authors gratefully acknowledge the financial support for this postdoctoral
research provided by NSERC and the Volt-Age Seed Fund. Both are administered through the Department of
Building, Civil and Environmental Engineering, Gina Cody School of Engineering and Computer Science,
Concordia University, Montréal, Québec, Canada.

**ORCID.** Mandatory for the corresponding author (`RV10` item 21). Orcun Koral Iseri:
https://orcid.org/0000-0001-7735-3363. Caroline Hachem-Vermette: none on file, left blank rather than
invented (matches the 2J submission's own title page, per `P12_consistency_facts.md`).

---

## 4. Suggested reviewers

[AUTHOR TO FILL] - do not invent names. Building and Environment requests "the names and institutional
e-mail addresses of several potential reviewers" and states the editor "retains the sole right to
decide whether or not the suggested reviewers are used" (`RV10` item 16). Exclude anyone at the
authors' own institution or with a recent (about 3-year) co-authorship with either author.

---

## 5. Audit prompt (for the author to paste into an external model, e.g. Gemini)

```
You are reviewing a submitted manuscript for Building and Environment (Elsevier) as a hostile,
skeptical peer reviewer whose job is to find reasons to reject it, not to be encouraging. You will be
given the full manuscript text (and, if provided, the supplementary material, cover letter and
highlights). Read the attached files before writing anything. Do not use outside knowledge of this
research group's other papers unless it is in the attached files.

Before citing or asserting anything about a claim in the manuscript, open and read the actual sentence
and the actual number in the actual file; do not paraphrase from memory or from the file name.
If you cannot verify something from the attached material, write NOT FOUND for that item rather than
inventing a page number, a value, or a citation. NOT FOUND is a correct and useful answer; a fabricated
one is not.

Check specifically for the following, and report each as a numbered finding with a quoted sentence and
its approximate location (section/paragraph):

1. Report-style writing: internal jargon, code names, step numbers, gate/pipeline vocabulary,
   PASS/FAIL/INFO-style scorecards, or any sentence that describes the paper's own structure ("this
   section does X") rather than the science.
2. Places where a calibration or curve-fitting step is described, or could be read, as "validation."
   Calibration against a fitting target is not independent validation; flag any sentence that blurs
   the two, including in table or figure captions.
3. Any use of "forecast" for the 2030 results. If the 2030 numbers are scenario projections rather
   than forecasts, flag "forecast" wherever it appears (except inside a quoted title of a cited work).
4. Missing statistics: are sample sizes, seeds, number of realizations, or any measure of run-to-run
   variability (standard deviation, range, confidence interval) given for the reported results? If a
   number is reported as a single point estimate with no spread, flag it.
5. Whether the comparison between the code-schedule (uninjected) case and the survey-driven case
   actually supports each claim built on it. Check specifically: does the code-schedule control
   building make sense as a fair baseline (for example, what occupancy schedule does it place on
   residential and hotel spaces)? Does every claim about "what changes" and "what does not change"
   trace to a number the reader can find in a table or figure?
6. Number consistency: pick at least 15 numbers that appear in the abstract, the highlights, and the
   body text or tables, and check each one is the same number in every place it appears (same sign,
   same units, same rounding). List every mismatch found.
7. Limitation wording: the paper should describe things it does not resolve as "limitation," "does not
   meet," or "falls outside" a reference range, never as "failure" or "fails," in its prose (tables
   that report a verdict column, e.g. PASS/FAIL, are the one place FAIL is allowed to stand). Flag any
   prose sentence that uses "fail," "fails," or "failure."
8. Any place a number is written as a placeholder, e.g. inside double-angle brackets like
   "P10R:something" - these are not typos; they mark a number waiting on a data update, and should be
   listed separately, not treated as a normal finding.
9. Any em dash or en dash character anywhere in the manuscript, cover letter or highlights (the long
   and medium horizontal dash characters used in place of a comma or parenthesis, distinct from the
   short hyphen used in compound words and number ranges). Report every occurrence with its
   surrounding sentence. These characters should not appear anywhere; the fix is a comma, a colon, or
   the word "to."
10. Whether the introduction's stated contributions match what the results and discussion actually
    show, and whether any claim of novelty goes beyond what the introduction's own contribution
    paragraph states.

End with: (a) a short list of the findings you judge would justify a desk rejection or a major-revision
request on their own, ranked most severe first; (b) a full list of every other finding, however minor;
(c) a confirmation that you read the attached files rather than answering from general knowledge of
similar papers.
```

---

## 6. Open items (everything waiting on the rebuilt-arm numbers or the author)

**Waits on P10R numbers** (per execution-doc status table, P10R phase B/C not yet run as of this
writing; `IMP/rewrite_log.md` open item 1 lists the same markers):
- All `⟦P10R:...⟧` values in the cover letter above (office/retail intensity change, load-centroid
  shift) must be substituted from the new arm before the letter is finalized, together with the
  matching numbers in the abstract, results, discussion, limitations and conclusion of `chapters_v2/`.
- The Highlights and Declarations sections above carry no `⟦P10R:...⟧` markers and do not need this
  step, but should be re-read against `chapters_v2/00_FrontMatter.md` and `10_Declarations.md` once
  those files are updated, in case wording (not just numbers) changes.

**Waits on the author, independent of P10R:**
- Funding wording: NSERC "Discovery Grant" or a different award type (`rewrite_log.md` open item 8).
- Generative-AI declaration: which tools were used and for what (chapters_v2 template and this file
  both carry the placeholder; `RV10` item 18 gives the exact sentence form to fill in).
- Suggested reviewers: names and institutional emails (Section 4 above).
- Cover letter date, and confirmation that "Dear Editor" (no named handling editor) is acceptable.
- Confirm the two companion-paper sentences in the cover letter and, separately, the self-citations
  inside `chapters_v2/11_References.md` (not opened for this task) are updated together, so the letter
  and the reference list never disagree about 1J/2J status.
- `rewrite_log.md` open item 30 (RV10) flags the CRKN 100% APC-waiver claim as unverified; do not
  select Gold open access on that basis without an independent check.
- Graphical abstract: `chapters_v2/00_FrontMatter.md` notes the existing image still shows the
  withdrawn "four peak hours" lead; a new image prompt is needed (author generates; none made here).
- Once P14 is finalized, run the audit prompt (Section 5) in Gemini and, per the plan's Wave-5 step,
  a second model; vet both sets of findings before acting on any of them, and re-check every accepted
  item on the installed .docx.

## Progress Log

- 2026-09-23: P14 draft written (`IMP/P14_package.md`); cover letter, highlights, declarations,
  reviewers placeholder and audit prompt done; reused `Title_Page_and_Cover_Letter.md` and
  `chapters_v2/00_FrontMatter.md` + `10_Declarations.md`; open items listed in Section 6.
