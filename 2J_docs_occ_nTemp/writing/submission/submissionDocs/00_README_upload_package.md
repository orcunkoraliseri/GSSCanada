# Upload package — Building Simulation

Built 2026-08-07 against the journal's own instructions
(`../JournalOfBuildingSimulation/00_REQUIREMENTS_verified.md`). Submit at
**https://www.editorialmanager.com/buil**.

## What is in this folder

| File | What it is | Status |
|---|---|---|
| `Title_Page_and_Cover_Letter.docx` | The cover letter to the Editor-in-Chief plus title, authors, affiliations, corresponding email, ORCID, author contributions, competing interest, ethical approval, acknowledgements and funding | **ready** — dated 7 August 2026 |
| `Blinded_Manuscript.docx` | The full manuscript with every piece of author information removed | **ready** |
| `Supplementary_Material/Supplementary_Material.docx` | Tables A1–A3, B1, B2, C1, C2 and Appendix D, plus the data-file index and column dictionary | **ready** — blinded |
| `Supplementary_Material/data/*.csv` | 8 derived data files, 2.8 MB total | **ready** — no microdata |
| `*.md` | The markdown sources everything was generated from | working files |

**Upload order in Editorial Manager:** Title Page → Blinded Manuscript → Supplementary Material
(the `.docx` and the 8 CSVs, or a single zip of the `Supplementary_Material` folder).

**Why two files:** Building Simulation is double-blind. The instructions require "the entire manuscript
without any author information and acknowledgements" as one upload, and a separate title page carrying
all of it — including the cover letter, which goes *inside* the title page rather than as its own item.

## What was done to blind the manuscript

- Removed the Author Information block, funding, acknowledgements, and the CRediT statement. Data
  availability stays, since the instructions do not place it on the title page.
- **§1.4 rewritten in the third person.** It was titled "The Authors' Prior Line" and said "by the
  authors"; it now reads "The Prior Line" and "The present study departs from a specific prior line of
  work." Five other phrases carrying "the authors' prior line" were changed the same way, in §1
  (funnel paragraph), the Table 1 note, §1.5 and §6.
- **All self-citations were kept.** This is deliberate and is the option you chose: the originality
  argument your supervisor asked for only works if the reviewer can see what the prior paper did.
  Third-person citation of one's own published work is standard under double-blind review.
- Verified afterwards: zero occurrences of Orcun, Caroline, ORCID, NSERC, Voltage-Age, CRediT,
  Acknowledgement, Concordia, or the corresponding email anywhere in the file. The only remaining
  author surnames are the two reference-list entries for the cited prior work, which is intended.

## Resolved 2026-08-07

- ✅ **Department:** Gina Cody School of Engineering and Computer Science. Filled in both files.
- ✅ **ORCID:** Iseri `0000-0001-7735-3363`. Caroline Hachem-Vermette has none, so the second slot was
  removed rather than left as a placeholder. **No `[confirm]` markers remain anywhere in the manuscript.**
- ✅ **Editor-in-Chief:** **Prof. Da Yan**, School of Architecture, Tsinghua University, Beijing —
  verified on the journal's editorial board page. The cover letter is now addressed to him.
- ✅ **Osman et al. (2023) is now cited in §1.2**, in the Canadian strand alongside Armstrong et al.
  (2009), Osman and Ouf (2021) and Ferreira et al. (2024). The reference list is now **52 entries, all
  52 cited, zero broken cross-references, zero orphans**.
- ✅ **The *under review* companion has been removed from the reference list**, per the journal's rule
  that the list carries only published or accepted work. It is still described in §1.4 and in the Table
  1 note as "a companion manuscript currently under review" — which is exactly what the instructions
  ask for: unpublished work mentioned in the text, not listed.

- ✅ **No suggested reviewers, by the authors' decision.** The section has been removed from the title
  page. This is permitted: the instructions say authors are "welcome to suggest suitable reviewers" and
  that "the Journal may not use the suggestions" — it is an invitation, not a requirement. The upside is
  that it also removes the obligation to supply a verified institutional email for each name.

## Before you upload

The three upload files are complete and can go as they stand. Two things to do, one to know:

1. 🔴 **Re-export the figures at 600 dpi** before uploading the figure set. 13 of 16 fall short —
   detailed below.
2. 🔴 **Settle the crosswalk count** (182 / 265 / 64 / 123 in the file against 182 / 264 / 64 / 121 in
   §3.1) before adding the crosswalk to the SI — detailed below. Nothing currently uploaded contradicts
   anything; the file is held back precisely so it stays that way.
3. **One Concordia name sits on the editorial board:** Prof. Liangzhu (Leon) Wang is an Associate Editor
   of Building Simulation. Not a conflict you must declare under double-blind review, but worth knowing
   in case Editorial Manager offers an editor-exclusion field.

Nothing else in the formatting list is left to do.

## Formatting — applied 2026-08-07

All of it is now baked into the `.docx` files. Verified by `submit_check.py` against the **installed**
files, not the build output:

| Journal rule | State |
|---|---|
| 12-point **Times Roman**, **double-spaced**, single column | ✅ applied via the document defaults |
| Automatic page numbering | ✅ centred `PAGE` field in a page footer |
| **Do not add line numbers** | ✅ none present — Editorial Manager adds them |
| Figures cited and captioned **`Fig. N`**, not "Figure 1" | ✅ 16 captions + 51 in-text references converted |
| Tables captioned `Table N …`, no bold, no period | ✅ 5 captions converted |
| Figure captions **below**, table captions **above** | ✅ |
| Citations name-and-year, **no comma** — "(Thompson 1990)" | ✅ 51 converted |
| Captions short, centred, 10 pt; tables 10 pt single-spaced | ✅ |
| Headings and cross-references black, body justified | ✅ zero coloured runs in either file |
| No page breaks | ✅ 0 |

Two defects were found and fixed in the same pass:

- **Every figure carried a duplicate caption.** The markdown alt text (`![Figure 5](…)`) made pandoc
  emit a bare "Figure 5" line under each image, immediately above the real caption. Alt text emptied;
  16 stray paragraphs gone.
- **The blinded `.docx` on disk was missing content** — Table 3's *TMY weather file* column, Table 5's
  two *Within band?* columns, and five figure labels. It had been built from a stale source. Rebuilt
  and diffed against the master: the only remaining differences are the 9 author blocks and the 7
  third-person §1.4 rewrites.

## Supplementary Material — added 2026-08-07

**It was not optional.** The manuscript already cited **SI Table B1, SI Table B2 and Tables A1–A3**,
and no supplementary file existed. Those were dangling references a reviewer would have hit
immediately. The four SI documents had been written but never assembled into a submittable file.

`Supplementary_Material.docx` now carries Tables A1–A3 (end-use load model), B1 (generator model
card), B2 (14-category activity codebook), C1–C2 (per-step validation and True-Future-Test results),
Appendix D (documented deviations), and an index plus column dictionary for the data.

Prepared for publication rather than for the project: internal `*Source:*` working-document lines
removed, report-style `> Note:` blockquotes folded into ordinary paragraphs, and internal script
filenames replaced with prose. Blinding verified across the document and all 8 data files.

**What the data files are, and what they are deliberately not.** No Statistics Canada microdata and
no record-level derivative of it is redistributed — not the augmented diaries, not the episode or
main files. What ships is the derived layer, 2.8 MB, enough to reproduce every calibration gate and
every load-shape statistic in the paper:

| File | Rows | What it settles |
|---|---:|---|
| `S1_sheu_calibration_48_cells.csv` | 48 | the binding calibration gate, 48/48 within ±2.7% |
| `S2_campaign_annual_by_household.csv` | 6,000 | EUI, load factor, midday share, mean peak hour |
| `S3_campaign_peak_by_household.csv` | 6,000 | annual and daily peak demand and peak hour |
| `S4_stock_peak_by_cell.csv` | 120 | circular mean peak hour and evening-peaking fraction |
| `S5_enduse_annual_heating_cooling.csv` | 600 | heating and cooling by fuel |
| `S6_loadshape_profiles_hourly.csv` | 2,304 | hourly baseline-vs-activity profiles |
| `S7_peak_hours_by_arm.csv` | 96 | peak hour per arm |
| `S8_peak_shift_summary.csv` | 48 | the §5.4 null result |

**Data availability has been rewritten** in both manuscripts accordingly — it no longer rests on
"available from the corresponding author on reasonable request" for the results-bearing data.

## 🔴 Blocker before you upload the SI: two counts do not reconcile

The activity harmonization crosswalk (`references_activityCodes/Data Harmonization_activityCategories
- execution.xlsx`) is the most useful thing in the whole package, and it is **deliberately held back**.

Counting its leaf activity codes, excluding the one `Work-related` section-header row, gives
**182 / 265 / 64 / 123** for the 2005 / 2010 / 2015 / 2022 cycles. **§3.1 of the manuscript and the
headline line in Table B2 both state 182 / 264 / 64 / 121.** 2005 and 2015 agree; 2010 is one over
and 2022 is two over.

The extra rows sit out of numeric order at the end of each sheet — `712.0` and `713.0` in 2010
(duplicating the labels of `720.0` and `741.0`), and `1105`, `1303`, `1304` in 2022 — which reads
like codes added to the sheet after the count was taken. But that is an inference, not a finding,
and I have not verified which mapping the pipeline actually consumed.

**Resolve it before shipping the crosswalk**, because a reviewer holding both can count. Either the
sheet has rows the pipeline never used, or §3.1 needs to say 265 and 123. Once it is settled the
crosswalk drops straight into `Supplementary_Material/data/` as `S0_activity_harmonization_crosswalk.csv`.

Related: **Table B2's "Raw-code magnitudes" column was 14 cells of `⚠ check source`** and could not
be submitted as it stood. That column has been removed rather than filled, for the same reason — the
per-category counts are derivable from the crosswalk, and publishing them commits to the disputed
totals. B2 now reads Code / Category / Notes and carries the manuscript's own headline figures.

## 🔴 The other item that is not fixable from here: figure resolution

The instructions require **600 dpi relative to final printed size**. At the 5.83-inch text width, that
means **≥ 3,498 pixels wide**. **13 of the 16 figures fall short** and must be re-exported from their
plotting scripts (`savefig(..., dpi=600)` or a wider `figsize`):

| Figure | px wide | effective dpi |
|---|---|---|
| Figure_S05_calibration, Figure_S06_sheu_pct, Figure_S07_peak_shift_null | 2,100 | 360 |
| Figure_S02_linkage | 2,528 | 433 |
| Figure_01_pipeline, Figure_02_dataprep, Figure_03_J3_architecture, Figure_04_schedule_integration, Figure_S01_search_funnel, Figure_S03_forecasting | 2,752 | 472 |
| Figure_S04_enduse_model | 2,816 | 483 |
| Figure_S08_longitudinal | 2,998 | 514 |
| Figure_05_occupancy_driver | 3,249 | 557 |

Passing already: `Figure_06_loadshape` (6,836 px), `Figure_S09_eui` (4,691 px),
`Figure_07_activity_equipment` (3,964 px).

This is a review-copy manuscript, so it is not a desk-reject risk on its own — but Building Simulation
asks for the figures **as separate files** at 600 dpi, and those are the ones that matter. Re-export
before uploading the figure set.

## Other norms, deliberately not changed

- "Generally, the total number of tables should be less than 5" and there are five. That sits inside a
  section opening "there is no strict limit", so it is a norm, not a gate. Submitting with five.
- The reference list keeps its current entry format. Springer copy-editing restyles reference lists as
  a matter of course; restyling 52 entries by hand before acceptance buys nothing and risks breaking
  the 52 working cross-references.
- The abstract is **one paragraph, ~237 words** (cap 100–250), carries no citations, and now defines
  `pp` on first use. Nothing to cut.
