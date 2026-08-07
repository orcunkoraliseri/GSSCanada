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
kept in sync except for 9 author-information paragraphs and 7 third-person rewrites in §1.4.

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

## Status, 2026-08-07 end of day

**Target journal fixed: Building Simulation** (Springer / Tsinghua University Press), double-blind,
submitted at `editorialmanager.com/buil`. The upload package is assembled in `submissionDocs/` —
**read `submissionDocs/00_README_upload_package.md` before uploading anything**, it is the operative
document. This file describes the working directory; that one describes what gets uploaded.

Closed since this file was first written:

- **Reference status.** The prior journal paper is *under review* and has been **removed from the
  reference list**, per the journal's rule that the list carries published or accepted work only. It
  is still described in the text, which is what the instructions ask for.
- **Front matter.** Department is Gina Cody School of Engineering and Computer Science; ORCID
  `0000-0001-7735-3363` for Iseri, none for Hachem-Vermette. **Zero `[confirm]` markers remain.**
- **Graphical abstract.** Not required by this journal. The three candidates stay where they are.
- **Abstract.** One paragraph, ~237 words against a 100–250 cap. Nothing to cut.
- **Formatting.** All journal export rules are now inside the `.docx`. See the upload README.

Still open, both flagged in the upload README:

1. 🔴 13 of the 16 figures are **below 600 dpi** at the printed width and need re-exporting.
2. 🔴 The activity crosswalk's leaf-code counts (**182 / 265 / 64 / 123**) disagree with §3.1 and
   Table B2 (**182 / 264 / 64 / 121**) for 2010 and 2022. The crosswalk is held out of the
   Supplementary Material until that is settled.

**`sharingCHV/2ndOcc_Journal.docx` is stale** (2026-08-04) and superseded by
`2J_manuscript_submission.docx`.
