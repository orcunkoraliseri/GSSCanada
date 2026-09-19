# 1J — Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials

First journal paper (Iseri & Hachem-Vermette), submitted to the *Journal of Building Performance
Simulation* (JBPS), manuscript ID **266775447**. Pipeline: a Conditional Variational Autoencoder
(C-VAE) + CBVM framework builds historically grounded occupancy profiles from GSS time-use and
Census PUMF data across cycles 2005/2010/2015/2022 plus a synthetic 2025 cycle, integrated into
EnergyPlus simulations of six Neighbourhood Unit typologies in Montreal (climate zone 6A), yielding
residential code calibration factors of +10% heating / -20% cooling. On 2026-09-19 the editor (Jan
Hensen) returned a **reject-and-resubmit / major-revision** decision with 12 months to resubmit and
one reviewer's report still outstanding — see `review_round1/JBPS_decision_2026-09-19.md` for the
full text. This folder is a read-only staging copy; every file below is a **copy**, and every
original still lives at its source path (verified in step 6).

**Revision work:** `IMP/00_REVISION_PLAN.md` (full plan, written by the manager session) and
`IMP/REVISION_STEPS.txt` (short step list).

## Copied files

| New path (`1J_docs_occ/...`) | Original path (`GSSCanada-main/...`) | Size |
|---|---|---|
| `manuscript/1st_Occ_Journal.md` | `2J_docs_occ_nTemp/writing/resources/1st_Occ_Journal.md` | 1.2 MB |
| `manuscript/030_FullPaper.docx` | `2J_docs_occ_nTemp/writing/resources/030_FullPaper.docx` | 1.9 MB |
| `manuscript/submission_Occ_NUsJournal.docx` | `2J_docs_occ_nTemp/writing/resources/submission_Occ_NUsJournal.docx` | 13 MB |
| `conference_eSim/ConferencePaper.md` | `2J_docs_occ_nTemp/writing/resources/ConferencePaper.md` | 368 KB |
| `conference_eSim/eSim/` (whole folder) | `eSim/` (whole folder) | 23 MB |

`review_round1/JBPS_decision_2026-09-19.md` and this `README.md` are new files written for this
staging folder (not copies of anything). `figures/` is currently empty — no separate figures folder
for 1J was found anywhere in the tree; the paper's figures appear to be embedded directly inside the
two `.docx` files, and neither `.md` manuscript file contains markdown image links.

### Which docx is the submitted version (likely, not certain)

`submission_Occ_NUsJournal.docx` is **likely** the file actually submitted to JBPS:
- Its embedded text carries the real author names (Orcun Koral Iseri, Caroline Hachem-Vermette,
  Concordia University) and the abstract/keywords/highlights match the paper description in this
  task word for word (five GSS cycles, C-VAE, six Neighbourhood Unit typologies, Montreal 6A,
  +10%/-20% calibration).
- Its Word document properties show `revision=43`, created 2026-04-27, last modified
  **2026-06-03** — a mature, heavily revised file.
- It exists in **two byte-identical copies** (same MD5 `e40c48c...`): one at
  `2J_docs_occ_nTemp/writing/resources/submission_Occ_NUsJournal.docx`, one at
  `2J_docs_occ_nTemp/examples/Journal1st/submission_Occ_NUsJournal.docx` — the second location's
  name ("Journal1st" examples folder) suggests it was deliberately filed as the reference copy of
  the submitted journal paper. Only the `writing/resources/` copy was brought into this folder; the
  `examples/Journal1st/` copy was left in place (identical content, so nothing is lost).

`030_FullPaper.docx` is **likely an earlier draft**, not the submission:
- Author fields are still placeholders (`XX1`, `XX2`, "Institution 1/2"), i.e. not filled in or
  anonymized for review.
- Word properties show `revision=2`, created **and** modified 2026-02-27 (much earlier, single
  editing session) — a template/build artifact rather than the final manuscript.
- Filename pattern (`030_...`) matches a numbered pipeline build step rather than a submission
  package name.

Filesystem `mtime`s on this machine are not reliable for this comparison (a `git clone`/checkout
resets them, as seen from many unrelated files sharing the same date) — the "likely" judgement above
is based on the documents' own internal `docProps/core.xml` timestamps and content, not folder
`ls -la` dates.

## Large / not copied

| Item | Size | Why not copied |
|---|---|---|
| *(none — `eSim/` at 23 MB was under the 200 MB threshold and was copied in full)* | | |

No file or folder belonging to 1J exceeded 200 MB. The large project data trees (`0_Occupancy/`
~37 GB, `2J_docs_occ_nTemp/` ~38 GB, `3J_docs_occ_nTemp/` ~43 GB) hold shared pipeline code and raw
Census/GSS data used by all four papers — none of it is 1J-specific, so none of it was copied or is
listed here.

## Other file found nearby, not part of 1J

`2J_docs_occ_nTemp/writing/resources/extra/Conference Paper - Long-Term Changes in Time Use and
Impacts on Residential Energy Demand.md` — this is **someone else's** conference paper (R. Yin et
al., ASim2024, Osaka University), kept locally as background reading. It is not authored by
Iseri/Hachem-Vermette and does not cite 1J; it was left out of `1J_docs_occ/` entirely.

## Cites 1J (2J/3J files that reference this paper — not copied, listed only)

These files quote the paper's title or reference it in a bibliography/status table. They belong to
the 2J and 3J projects and were left untouched in place:

- `GSSCanada-main/README.md` — top-level project tracker; lists 1J's status as "Under Evaluation"
  (now stale — the 2026-09-19 decision above supersedes it; not changed here since it is out of
  scope for this task).
- `2J_docs_occ_nTemp/writing/chapters/Chapter_01_Introduction.md` and its five dated `archive/`
  variants — 2J's introduction, cites 1J as prior work.
- `2J_docs_occ_nTemp/writing/chapters/Chapter_06_Discussion.md` — 2J discussion chapter.
- `2J_docs_occ_nTemp/writing/fullSet/2J_full_manuscript.md` and two dated `archive/` variants.
- `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md`.
- `2J_docs_occ_nTemp/writing/methodology_assessment_and_paper_skeleton.md` and its `archive/`
  variant.
- `2J_docs_occ_nTemp/writing/resources/2nd_Occ_Journal_Skeleton.md` and its `archive/` variant.
- `2J_docs_occ_nTemp/writing/submission/extra/01_originality_statement.md`,
  `2J_manuscript_submission_BEFORE_refs_captions.md`, `2J_manuscript_submission_BEFORE_osman_orcid.md`.
- `2J_docs_occ_nTemp/writing/submission/deepReserchPrompts/00_README_journal_targeting.md` and
  `dr_2J-01_journal_fit_shortlist_results.md`.
- `3J_docs_occ_nTemp/writing/chapters/Chapter_09_References.md` and its `archive/` variant.
- `3J_docs_occ_nTemp/writing/chapters/archive/Chapter_01_Introduction.*.md` (five dated variants).
- `3J_docs_occ_nTemp/writing/submission/3J_manuscript_submission.md` and its `archive/` variant.
- `5J_docs_occ/DeepResearch/_scan/scan_gsscanada_progress.md` — automated repo scan, mentions 1J in
  passing.

This list comes from a text search for the exact phrase "Longitudinal Analysis of Occupancy" across
the tree; it is a best-effort scan of the writing/documentation folders, not a byte-for-byte
guarantee that no other citation exists anywhere in the 100+ GB of raw pipeline/data directories.
