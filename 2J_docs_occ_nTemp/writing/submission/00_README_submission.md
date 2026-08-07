# Submission package — 2nd journal paper

**Manuscript:** *From "How Much" to "When": Forecasting the Residential Energy Load Shape from a Calibrated Behavioural Occupancy Time-Series (Canada, 2005–2030)*
**Authors:** O.K. Iseri, C. Hachem-Vermette · Concordia University
**Assembled:** 2026-08-07

---

## Contents

| Path | What it is |
|---|---|
| `2J_manuscript_submission.md` | Submission copy of the manuscript. Verbatim `fullSet/readySubmission.md` with the new §1.4 originality statement, plus figure paths rebased from `../figures/` to `figures/`. |
| `2J_manuscript_submission.docx` | The same file rendered by pandoc, figures embedded. Regenerate after any `.md` edit (command below). |
| `figures/Figure_01–07*.png` | The 7 main-text figures, in citation order. |
| `figures/SI/Figure_S01–S09*.png` | The 9 supplementary figures cited in the Appendix. |
| `figures/graphicalAbstract/` | Three graphical-abstract candidates — **one still to be chosen**. |
| `tables/Table_01–05*.md` | The 5 main-text tables. |
| `tables/SI/` | Appendix tables A1–A3, B1–B2, C1–C2, and the Appendix-D deviations list. |

All 16 image links in the `.md` were verified to resolve against the copied files (0 broken).

## Regenerating the .docx

The plain pandoc call is no longer enough — the journal's export rules live in a patched reference
document, and table formatting is applied afterwards. Rebuild with:

```
pandoc 2J_manuscript_submission.md -o raw.docx --reference-doc=ref_submit.docx --resource-path=.
py post.py raw.docx 2J_manuscript_submission.docx
py submit_check.py 2J_manuscript_submission.docx submissionDocs/Blinded_Manuscript.docx
```

`ref_submit.docx` carries 12 pt Times, double spacing, black headings and cross-references, justified
body text, centred 10 pt captions, and the page-number footer. `post.py` sets table text to 10 pt
single-spaced. `submit_check.py` is the pre-upload gate — **run it against the installed files, not
the build output.** All three live in the session scratchpad; copy them here if you want them kept.

**Any edit to the master must be mirrored in `submissionDocs/Blinded_Manuscript.md`.** The two are
kept in sync except for **10 author-information lines removed and 6 lines rewritten in the third
person** (§1 funnel paragraph, the Table 1 note, the §1.4 heading and opener, §1.5, §6). A multiset
line diff must return exactly **16 master-only / 6 blinded-only** — anything else is drift.

---

## What changed in this build (2026-08-07)

1. **New originality statement** added at the end of §1.4, per supervisor request — an explicit
   *how much* (prior journal paper) versus *when* (this paper) contrast. Added identically to
   `chapters/Chapter_01_Introduction.md`, `fullSet/2J_full_manuscript.md`, and
   `fullSet/readySubmission.md`.

2. **Three items restored to the submission copy.** The earlier submission strip had dropped them
   from `readySubmission.md` while `2J_full_manuscript.md` kept them:
   - the in-text self-citation `(Iseri and Hachem-Vermette, under review)` on the prior journal
     paper in §1.4 — the predecessor was described in prose but **not cited**;
   - its entry in the master reference list;
   - the note under Table 1 explaining that the gap matrix scores **external** competitors only.

## ✅ SUBMITTED — 2026-08-07

**Submitted to Building Simulation** (Springer / Tsinghua University Press), double-blind, via
`editorialmanager.com/buil`. What went up is what is in `submissionDocs/`: Title Page and Cover
Letter, Blinded Manuscript, and the Supplementary Material document with its 8 derived data files.
`submissionDocs/00_README_upload_package.md` records the package exactly as uploaded.

**Do not edit these files further.** They are now the record of what the journal holds. Any revision
starts by copying them, so that the submitted version stays diffable against whatever comes back.

Two things still to record here when they arrive: the **Editorial Manager manuscript ID**, and the
date of the editor's acknowledgement.

**When the decision arrives, start from `../Prompts/2J_manager_prompt_ON_REVISION_DECISION.md`** —
a standing handoff written the day of submission. Fill its §0, paste it into a new session with the
reviewer reports, and let it triage before anything is edited.

Closed before submission:

- **Reference status.** The prior journal paper is *under review* and has been **removed from the
  reference list**, per the journal's rule that the list carries published or accepted work only. It
  is still described in the text, which is what the instructions ask for.
- **Front matter.** Department is Gina Cody School of Engineering and Computer Science; ORCID
  `0000-0001-7735-3363` for Iseri, none for Hachem-Vermette. **Zero `[confirm]` markers remain.**
- **Graphical abstract.** Not required by this journal. The three candidates stay where they are.
- **Abstract.** One paragraph, ~237 words against a 100–250 cap. Nothing to cut.
- **Formatting.** All journal export rules are now inside the `.docx`. See the upload README.

Carried past submission — neither blocked the upload, both need settling before the revision:

1. 🟠 **13 of the 16 figures are below 600 dpi** at the printed width. They went up as they stand,
   which is fine for a review copy; the journal asks for 600 dpi in the **separate figure files**
   requested at acceptance. Re-export from the plotting scripts before that point. Table of pixel
   widths in the upload README.
2. 🟠 **The activity crosswalk's leaf-code counts (182 / 265 / 64 / 123) disagree with §3.1 and
   Table B2 (182 / 264 / 64 / 121)** for 2010 and 2022. The crosswalk was held out of the
   Supplementary Material, so **nothing submitted contradicts anything submitted** — but the
   §3.1 figures are now in a manuscript under review. Settle which is right before the revision:
   either the sheet carries rows the pipeline never used, or §3.1 and Table B2 need to say
   265 and 123.

**`sharingCHV/2ndOcc_Journal.docx` is stale** (2026-08-04) and superseded by
`2J_manuscript_submission.docx`.
