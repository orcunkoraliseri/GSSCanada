# P12 — 3J consistency facts against 2J's and 1J's CURRENT (revised) state

Compiled 2026-09-22. All 2J/1J facts below are re-derived directly from the files named in each
section — never from memory, the 3J plan doc, or the MEMORY.md index. Every "3J" line below was found
by scanning `3J_docs_occ_nTemp/writing/chapters/*.md`, `3J_docs_occ_nTemp/writing/tables/*.md` (both
current, non-`archive/` versions), `3J_docs_occ_nTemp/writing/fullSet/readySubmission.md`,
`readySubmission_SI.md`, and `3J_docs_occ_nTemp/writing/submission/Title_Page_and_Cover_Letter.md`.

## Summary

3J's current text is **not** consistent with 2J's and 1J's current state, and the gap is large enough
to matter at submission. Worst offenders: (1) the funding line is misspelled everywhere it appears in
3J — "the Voltage-Age Seed fund" — against 2J's verbatim, author-sourced "the Volt-Age Seed Fund"; this
is a straight typo (Volt-Age → Voltage-Age) repeated in the front matter, the cover letter and the
assembled manuscript. (2) 3J's cover letter (`Title_Page_and_Cover_Letter.md:68-70`) and reference list
(`Chapter_09_References.md:19,21`) both say 2J is "under review at Building Simulation" — 2J was
**rejected** by Building Simulation on 2026-09-15 and has not yet been submitted anywhere else (it is
waiting on the supervisor's approval before going to Applied Energy); "under review at Building
Simulation" is not true of 2J at any point in its history that overlaps with 3J's current draft dates,
and is stale now regardless. (3) The same two locations say 1J is "under review at the Journal of
Building Performance Simulation" — 1J was **rejected** by JBPS on 2026-09-19 with an invitation to
resubmit after major revision (i.e., reject-and-resubmit), not "under review." (4) 3J's Discussion
(`Chapter_06_Discussion.md:49-54`, mirrored `readySubmission.md:822`) and two internal-only SI/table
files cite specific 2J numbers ("Table 5," "SingleDetached," SHEU-band verdicts) that could not be
located anywhere in 2J's current, heavily restructured AE-revised manuscript — the AE revision folded
away the old section/table numbering entirely, so this claim is unverifiable against the current 2J
text as written and needs a citation-form check, not just a status-word swap.

---

## 1. 2J facts (re-derived from the revised-2J files)

**Source files used:** `2J_docs_occ_nTemp/writing/submission/rejection revision/manuscript/2J_manuscript_AE_revised.md` (title page/cover letter section + body); `2J_docs_occ_nTemp/writing/Prompts/2J_manager_prompt_RESUME_AE_resubmission.md`.

**Title (verbatim):**
> From "How Much" to "When": Forecasting the Residential Energy Load Shape from a Calibrated
> Behavioural Occupancy Time-Series (Canada, 2005–2030)

**Full author list (verbatim, from the title page):**
> Orcun Koral Iseri^a,\*^, Caroline Hachem-Vermette^a^
> ^a^ Gina Cody School of Engineering and Computer Science, Concordia University, 1455 De Maisonneuve
> Blvd. W., Montréal, Québec, H3G 1M8, Canada

Two authors only. Corresponding author: Orcun Koral Iseri (orcunkoral.oseri@concordia.ca). ORCID given
only for Iseri; Hachem-Vermette carries none.

**Status — quoted exactly from the RESUME file's own top line** (`2J_manager_prompt_RESUME_AE_resubmission.md:3-4`):
> "Last updated: **2026-09-22, after plan log (fa). Approval email SENT to the supervisor; waiting on
> her reply. Submission happens only after her approval. Nothing is live on the cluster or in any
> agent.**"

So: **2J has NOT been submitted to Applied Energy.** It was rejected by *Building Simulation* on
2026-09-15 (RESUME line 62/1143: "Venue: Applied Energy, CONFIRMED by the author 2026-09-21" and, in
the historical section, "The paper was rejected by Building Simulation on 2026-09-15. Target venue is
**Applied Energy**"). It is currently sitting with the co-author awaiting her approval to submit; no
submission has happened at any journal since the Building Simulation rejection.

**Table-1/Appendix-A "own prior work" row** — quoted verbatim from `2J_manuscript_AE_revised.md:1016`
(Appendix A, Table A.1, framework dimensions C1–C6: C1 time-series occupancy, C2 calibrated model, C3
future-year scenario across the pandemic break, C4 activity/end-use resolved, C5 stock-scale, C6
load-shape/peak):
> "Authors' own prior line: companion journal manuscript, under review, and companion conference study
> (Iseri and Hachem-Vermette 2026) | check | check | cross | cross | P | P"

I.e., 2J scores its OWN prior line (the JBPS paper = 1J, plus the eSim 2026 conference paper) present
on C1 and C2, **absent** on C3 and C4, and only **partial** on C5 and C6. Note this row itself calls
the JBPS paper "under review" (line 1016) — that wording is 2J's own text, written before 1J's 2026-09-19
rejection; it is not something 3J invented, but it means 2J's own manuscript is *also* stale on this
point and should not be treated as unimpeachable ground truth for 1J's status. For 1J's actual current
status, Section 2 below (1J's own files) governs.

**Funding-line spelling — quoted exactly** from `2J_manuscript_AE_revised.md:1211-1212` (Funding
section):
> "This work was supported by the Natural Sciences and Engineering Research Council of Canada (NSERC)
> through a Discovery Grant, and by the **Volt-Age Seed Fund**, Concordia University."

Also appears (Acknowledgements, line 1238): "...the NSERC Discovery Grant and the **Volt-Age Seed
Fund**, administered through the Department of Building, Civil and..." Both instances spell it
**"Volt-Age Seed Fund"** — hyphen between "Volt" and "Age," capital F on "Fund." Per 2J plan log entry
(ey): this spelling is sourced from "the author's postdoc offer letter, which says 'PI's research
grants of NRC (Volt-Age) and NSERC DG'" — i.e., it is the author-verified correct spelling, not a
guess.

---

## 2. 1J facts (re-derived from the 1J files)

**Source files used:** `1J_docs_occ/Prompts/1J_manager_prompt_RESUME.md`; `1J_docs_occ/IMP/00_REVISION_PLAN.md`.

**Current title (verbatim)** — from `00_REVISION_PLAN.md:3`:
> **Paper:** *Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials*

This is still the working/submitted title. `00_REVISION_PLAN.md:38-40` lists two **suggested** new
titles ("author picks one; changing the title makes the repositioning visible") but neither the plan
file nor the RESUME file (searched for "title"/"Title" — no hits at all in RESUME) records that the
author has picked one yet. Treat the title above as current until a pick is recorded.

**Current status — quoted exactly** from `00_REVISION_PLAN.md:1,4-5`:
> "# 1J — Revision Plan (JBPS, reject-and-resubmit)"
> "**Journal:** Journal of Building Performance Simulation (JBPS), manuscript 266775447"
> "**Decision:** 2026-09-19. Rejected in its current form, but a resubmission after major revision is
> invited (editor J. Hensen). One reviewer's report is received. A second report is overdue and will be
> forwarded if it arrives."

Confirmed: **reject-and-resubmit**, not "under review." Rejected 2026-09-19; resubmission deadline
2027-09-19 (12 months). The revision itself is actively in progress (RESUME.md:6-22: Stage 4d draws
running as of 2026-09-22).

---

## 3. 3J → 2J consistency table

| # | Location (file:line) | 3J sentence (verbatim/close) | What it claims about 2J | vs. Section 1 | Verdict |
|---|---|---|---|---|---|
| 1 | `Chapter_09_References.md:21` (mirrored `readySubmission.md:856`) | "Iseri, O. and Hachem-Vermette, C. (under review b) *From "How Much" to "When"...* Building Simulation." | 2J's title correct; status "under review"; venue "Building Simulation" | 2J rejected by Building Simulation 2025-09-15; not submitted anywhere since; title matches | **STALE** — journal name wrong (2J no longer at Building Simulation) and status wrong (not "under review" anywhere) |
| 2 | `Title_Page_and_Cover_Letter.md:70` | "...a second, which established the single-channel residential occupancy pipeline this work grew from, is under review at *Building Simulation*." | 2J status = "under review at Building Simulation" | Same as above | **STALE** |
| 3 | `Title_Page_and_Cover_Letter.md:3-4` | "*Modelled on the 2J title page as submitted to Building Simulation on 2026-08-07..." | Historical: 2J WAS submitted to Building Simulation on 2026-08-07 | True as a historical fact at that date; 2J was later rejected there (2026-09-15) | **MATCH** as a dated historical note, but risks being read as current — flag for the rewrite agent to make the "as submitted" / historical framing unambiguous |
| 4 | `Title_Page_and_Cover_Letter.md:14` | "Review model: single-anonymized... unlike the 2J one [double-blind]." | 2J used double-blind review (at Building Simulation) | True of 2J's old Building Simulation submission; unknown/unstated for 2J's next venue (Applied Energy) | **STALE-ish** — compares 3J to a 2J venue that no longer applies; needs re-basing to AE if this comparison is kept |
| 5 | `Title_Page_and_Cover_Letter.md:104` | "Hachem-Vermette's ORCID is absent from the 2J submission as well..." | 2J's title page lists no ORCID for Hachem-Vermette | Confirmed still true in `2J_manuscript_AE_revised.md` (only Iseri's ORCID given) | **MATCH** |
| 6 | `Chapter_00_FrontMatter.md:44`, mirrored `Title_Page_and_Cover_Letter.md:142`, `readySubmission.md:31` | "...the Natural Sciences and Engineering Research Council of Canada (NSERC) and the **Voltage-Age Seed fund**." | Funding source name/spelling, shared with 2J | 2J: "**Volt-Age Seed Fund**" (author-verified spelling) | **MISMATCH** — "Voltage-Age" (merged, wrong) vs "Volt-Age" (correct); also case differs, "fund" vs "Fund" |
| 7 | `Chapter_01_Introduction.md:25` (section 1.4 body), mirrored `readySubmission.md` (same paragraph, ~line 101) | "...(Iseri and Hachem-Vermette, under review a; Iseri and Hachem-Vermette, under review b; Iseri and Hachem-Vermette, 2026)." | In-text citation to 2J ("under review b") as part of the "prior line" | Points to the same stale Ref-list entry as #1 | **STALE** (inherits #1's problem) |
| 8 | `Chapter_02_Datasets.md:14-15`, mirrored `readySubmission.md:136-137` | "...used in the authors' prior work (Statistics Canada, 2022; Iseri and Hachem-Vermette, under review b): Cycle 19 (2005)..." | Cites 2J as source/precedent for GSS cycle use | Same underlying ref-list staleness | **STALE** (inherits #1) |
| 9 | `Chapter_03_Methods.md:236-238`, mirrored `readySubmission.md:452` | "...the residential SHEU anchoring (Natural Resources Canada, 2019) used in the two-channel construction stage and in the authors' residential-only prior work (Iseri and Hachem-Vermette, under review b)." | Cites 2J's SHEU-anchoring method | Same ref-list staleness | **STALE** (inherits #1) |
| 10 | `Chapter_06_Discussion.md:49-54`, mirrored `readySubmission.md:822` | "The residential intensity table in the authors' prior single-channel study (Iseri and Hachem-Vermette, under review b) rests on an extraction function with two compounding defects... correcting both moved three of four band verdicts." | Specific 2J **finding/number**: an EUI-extraction bug in 2J moved 3 of 4 band verdicts | Could not locate a "Table 5," "SingleDetached/MidRise/HighRise" EUI-band table, or SHEU band-verdict language anywhere in the current `2J_manuscript_AE_revised.md` (grepped for "SingleDetached," "Table 5" — zero hits; the AE revision restructured the paper around load-shape metrics, not SHEU EUI bands) | **STALE/UNVERIFIABLE against current 2J text** — the claim may still be historically true of the correction event, but the current 2J manuscript does not appear to carry the table structure this sentence describes; needs a citation-form check before the rewrite, not just a word swap |
| 11 | `Table_01_gap_matrix.md:66-76` (Sources section only; apparatus note says "stripped from the submission copy," and confirmed **not** present in `readySubmission.md`) | Cites `../2J_docs_occ_nTemp/writing/tables/Table_01_gap_matrix.md` as a source | Points to a 2J file path | That path no longer exists — `2J_docs_occ_nTemp/writing/tables/` was reorganized; the file now lives at `2J_docs_occ_nTemp/writing/submission/tables/Table_01_gap_matrix.md` (or `archive/tables/`) | **STALE PATH**, but low severity — internal build note only, not reader-facing |
| 12 | `SI/Appendix_C_corrections.md:216-225, 262-269` (internal-only; **excluded from the assembled submission** by `assemble_3J.py:521-527`, confirmed not in `readySubmission_SI.md`) | "The submitted 2J manuscript's Table 5 residential EUI values..."; "The corrected values are live in the 2J submission copy's Table 5..."; cites `../2J_docs_occ_nTemp/writing/fullSet/readySubmission.md:367` as source of truth | Same "Table 5" claim as #10, plus a specific file:line pointer | The pointed-to path (`2J_docs_occ_nTemp/writing/fullSet/readySubmission.md`) no longer exists (2J reorganized; it is now under `2J_docs_occ_nTemp/writing/archive/fullSet/readySubmission.md`, and is itself an old, superseded draft, not the current AE-revised manuscript) | **STALE** (both the number/table claim and the file pointer) — internal audit trail only, not manuscript text, but should be fixed or annotated as historical if the audit trail is kept live |
| 13 | `Table_06_leg2_leg3_delta.md:89` | "...`537183b443846adeb20a0fc191c32159` 2J snapshot..." (an md5 hash label) | Labels a hashed file snapshot as "the 2J snapshot" | Purely an internal provenance label, not a claim about 2J's content/status | **N/A** — not a factual claim about 2J, no action needed |
| 14 | `Table_06_leg2_leg3_delta.md:116-118` | "Any 3J sentence that quotes a Leg-2 or 2J EUI magnitude uses the corrected value... This is the same hazard brief §1.2 raises for the 2J residential Table 5..." | Same "2J residential Table 5" claim as #10/#12 | Same non-existence of "Table 5" in current 2J text | **STALE/UNVERIFIABLE** — same caveat as #10; this sentence did **not** show up under a literal `\b2J\b` search of `readySubmission.md`, so it may not be part of the assembled reader-facing text (needs a check of what actually gets inlined from `Table_06_leg2_leg3_delta.md` at its chapter placeholder) |

---

## 4. 3J → 1J consistency table

| # | Location (file:line) | 3J sentence (verbatim/close) | What it claims about 1J | vs. Section 2 | Verdict |
|---|---|---|---|---|---|
| 1 | `Chapter_09_References.md:19` (mirrored `readySubmission.md:854`) | "Iseri, O. and Hachem-Vermette, C. (under review a) *Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials.* Journal of Building Performance Simulation." | 1J's title correct; status "under review" | 1J = reject-and-resubmit, rejected 2026-09-19; title still matches (`00_REVISION_PLAN.md:3`) | **STALE** — status wrong ("under review" vs. rejected/major-revision-invited); title itself is still correct (no new title picked yet) |
| 2 | `Title_Page_and_Cover_Letter.md:68-69` | "A predecessor manuscript is under review at the *Journal of Building Performance Simulation*..." | 1J status = "under review" | Same as above | **STALE** |
| 3 | `Chapter_01_Introduction.md:25` (in-text citation "Iseri and Hachem-Vermette, under review a"), mirrored `readySubmission.md` (~line 101) | Same in-text citation as 2J-table row 7, sharing the sentence | Cites 1J as part of "the authors' prior line" | Inherits the ref-list staleness (#1 above) | **STALE** (inherits #1) |
| 4 | `Chapter_09_References.md:17` (mirrored `readySubmission.md:852`) | "Iseri, O. and Hachem-Vermette, C. (2026) *Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials* (companion conference paper). eSim 2026, IBPSA-Canada." | Not 1J itself — the eSim 2026 conference paper — but it carries the **identical title string** as the JBPS (1J) entry immediately below it | 1J's real title (`00_REVISION_PLAN.md:3`) matches word-for-word; 2J's own reference list (`2J_manuscript_AE_revised.md:1292`) gives a *different* title for this same conference paper: "Longitudinal analysis of occupancy-driven energy demand in Canadian residential buildings (2005–2025)" | **MISMATCH (internal to 3J)** — 3J's conference-paper title does not match 2J's own citation of the same conference paper, and duplicates 1J's exact title, which looks like a copy-paste error rather than two genuinely identically-titled papers; needs the author to confirm the eSim 2026 paper's real title |

---

## 5. All citation locations — flat list (file:line) for the rewrite agent

Every place 2J or 1J is cited, mentioned, or referenced in the scanned 3J sources (current/non-archive
files only):

- `3J_docs_occ_nTemp/writing/chapters/Chapter_00_FrontMatter.md:44` — funding line (shared with 2J, misspelled)
- `3J_docs_occ_nTemp/writing/chapters/Chapter_01_Introduction.md:25` — in-text citation, "under review a/b" (1J/2J)
- `3J_docs_occ_nTemp/writing/chapters/Chapter_02_Datasets.md:14-15` — cites 2J ("under review b") for GSS cycle use
- `3J_docs_occ_nTemp/writing/chapters/Chapter_03_Methods.md:236-238` — cites 2J ("under review b") for SHEU anchoring
- `3J_docs_occ_nTemp/writing/chapters/Chapter_06_Discussion.md:49-54` — cites 2J ("under review b") for the EUI-extraction-defect finding
- `3J_docs_occ_nTemp/writing/chapters/Chapter_09_References.md:17` — reference entry, eSim 2026 conference paper (title mismatch vs. 2J's own citation of it)
- `3J_docs_occ_nTemp/writing/chapters/Chapter_09_References.md:19` — reference entry, 1J (JBPS), status "under review" (STALE)
- `3J_docs_occ_nTemp/writing/chapters/Chapter_09_References.md:21` — reference entry, 2J, status "under review," venue "Building Simulation" (STALE)
- `3J_docs_occ_nTemp/writing/tables/Table_01_gap_matrix.md:3,64,66-76` — internal Sources-section-only references to "2J" (stripped from submission; one stale file path)
- `3J_docs_occ_nTemp/writing/tables/Table_06_leg2_leg3_delta.md:18` — table row, "Building simulation" (unrelated word match, not a 2J/1J citation — false positive, no action)
- `3J_docs_occ_nTemp/writing/tables/Table_06_leg2_leg3_delta.md:89` — md5-hash provenance label "2J snapshot" (not a factual claim)
- `3J_docs_occ_nTemp/writing/tables/Table_06_leg2_leg3_delta.md:116-118` — "2J residential Table 5" claim (STALE/unverifiable; possibly not inlined into the assembled manuscript — check)
- `3J_docs_occ_nTemp/writing/tables/SI/Appendix_C_corrections.md:76` — "companion decision" (internal, NOT about 2J/1J — false positive)
- `3J_docs_occ_nTemp/writing/tables/SI/Appendix_C_corrections.md:169` — "2008 companion paper" (an external reference, NOT 2J/1J — false positive)
- `3J_docs_occ_nTemp/writing/tables/SI/Appendix_C_corrections.md:196` — "companion report" internal reproducibility check (NOT 2J/1J — false positive)
- `3J_docs_occ_nTemp/writing/tables/SI/Appendix_C_corrections.md:216-225` — "the submitted 2J manuscript's Table 5..." (internal-only file, excluded from submission; STALE claim)
- `3J_docs_occ_nTemp/writing/tables/SI/Appendix_C_corrections.md:262-269` — "the 2J manuscript directly... corrected values are live in the 2J submission copy's Table 5" + stale file-path pointer (internal-only, excluded from submission)
- `3J_docs_occ_nTemp/writing/tables/SI/Table_B1_improvement_rounds.md:23` — "one finding (B-13) briefly reached the submitted 2J manuscript..." (internal-only, excluded from submission; historically accurate, references the old rejected Building Simulation draft)
- `3J_docs_occ_nTemp/writing/fullSet/readySubmission.md:31` — funding line (mirrors Chapter_00:44)
- `3J_docs_occ_nTemp/writing/fullSet/readySubmission.md:99,101` — section 1.4 heading + in-text citation (mirrors Chapter_01)
- `3J_docs_occ_nTemp/writing/fullSet/readySubmission.md:136-137` — GSS-cycle citation (mirrors Chapter_02)
- `3J_docs_occ_nTemp/writing/fullSet/readySubmission.md:452` — SHEU-anchoring citation (mirrors Chapter_03)
- `3J_docs_occ_nTemp/writing/fullSet/readySubmission.md:471` — Table 6 row (false positive, "Building simulation" as a pipeline step name)
- `3J_docs_occ_nTemp/writing/fullSet/readySubmission.md:822` — EUI-extraction-defect citation (mirrors Chapter_06)
- `3J_docs_occ_nTemp/writing/fullSet/readySubmission.md:846` — Doma & Ouf reference to "Building Simulation 2023" conference (false positive — unrelated conference proceedings, not 2J/1J)
- `3J_docs_occ_nTemp/writing/fullSet/readySubmission.md:848` — Doma & Ouf 2024 reference in *Applied Energy* the journal (false positive — unrelated paper, not 2J's target venue)
- `3J_docs_occ_nTemp/writing/fullSet/readySubmission.md:852` — reference entry, eSim 2026 conference paper (mirrors Chapter_09:17)
- `3J_docs_occ_nTemp/writing/fullSet/readySubmission.md:854` — reference entry, 1J/JBPS (mirrors Chapter_09:19)
- `3J_docs_occ_nTemp/writing/fullSet/readySubmission.md:856` — reference entry, 2J/Building Simulation (mirrors Chapter_09:21)
- `3J_docs_occ_nTemp/writing/fullSet/readySubmission_SI.md` — **no 2J/1J mentions found** (searched, zero hits)
- `3J_docs_occ_nTemp/writing/submission/Title_Page_and_Cover_Letter.md:3-4` — "Modelled on the 2J title page as submitted to Building Simulation on 2026-08-07" (historical, dated correctly)
- `3J_docs_occ_nTemp/writing/submission/Title_Page_and_Cover_Letter.md:14` — "unlike the 2J one" (double-blind review comparison, needs re-basing)
- `3J_docs_occ_nTemp/writing/submission/Title_Page_and_Cover_Letter.md:68-70` — "Relationship to concurrent work" paragraph, states both 1J and 2J status (STALE for both)
- `3J_docs_occ_nTemp/writing/submission/Title_Page_and_Cover_Letter.md:104` — 2J's missing co-author ORCID (MATCH, still true)
- `3J_docs_occ_nTemp/writing/submission/Title_Page_and_Cover_Letter.md:142` — funding line (mirrors Chapter_00:44)

**Not scanned / out of the requested scope, but noted in passing:** `3J_docs_occ_nTemp/writing/submission/3J_manuscript_submission.md` and `3J_supplementary_material.md` were not in the task's file list and were not opened; if they are separately maintained (not regenerated from `readySubmission.md`), they likely carry the same stale citations and should be checked before the rewrite ships.
