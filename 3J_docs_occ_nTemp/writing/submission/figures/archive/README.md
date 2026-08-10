# Superseded figure artwork, 2026-08-09

Nothing here was deleted from the project; this is the revert path.

## `superseded_matplotlib/`

The seventeen files replaced when the author-generated images were installed on 2026-08-09: nine PNGs
and the eight vector PDFs that went with them. The PDFs were taken out of the live trees rather than
left in place, because a vector PDF showing the old artwork beside a PNG showing the new one is two
different figures under one name.

| replaced file | was | is now | prompt that produced the replacement |
|---|---|---|---|
| `Figure_01_pipeline_4split` | 6600 x 3000, 300 dpi, + PDF | 1376 x 768 | `../Prompts_Images/Figure_01_pipeline_4split.md` |
| `Figure_02_three_leg_roadmap` | 6000 x 2970, 300 dpi, + PDF | 1376 x 768 | `../Prompts_Images/Figure_02_three_leg_roadmap.md` |
| `Figure_03_three_head_transformer` | 6000 x 3480, 300 dpi, + PDF | 1376 x 768 | `../Prompts_Images/Figure_03_three_head_transformer.md` |
| `Figure_04_exclusivity_projection` | 5400 x 2100, 300 dpi, + PDF | 1376 x 768 | `../Prompts_Images/Figure_04_exclusivity_projection.md` |
| `Figure_05_hotel_sidetrack` | 5850 x 3300, 300 dpi, + PDF | 1376 x 768 | `../Prompts_Images/Figure_05_hotel_sidetrack.md` |
| `Figure_06_tag2_dispatch` | 5700 x 3960, 300 dpi, + PDF | 1376 x 768 | `../Prompts_Images/Figure_06_tag2_dispatch.md` |
| `SI/Figure_S01_occupiable_shares` | 2850 x 3210, 300 dpi, + PDF | 1200 x 896 | `../Prompts_Images/Figure_S01_occupiable_shares.md` |
| `SI/Figure_S02_scenario_levers` | 4500 x 1950, 300 dpi, + PDF | 1376 x 768 | `../Prompts_Images/Figure_S02_scenario_levers.md` |
| `graphicalAbstract` | 2752 x 1536 | 1376 x 768 | `../Prompts_Images/graphicalAbstract.md` |

**Figures 7 to 11 and S3 are not here.** They were never replaced: no generated version existed, and
7 to 11 carry the paper's measured results. Prompts for all six now exist in `../Prompts_Images/`,
and the five data prompts carry their series in full.

### To revert

Copy the `superseded_matplotlib/` tree back over `writing/figures/` and
`writing/submission/figures/`, then rebuild. A second, independent copy of the same files is at
`writing/figures/archive_matplotlib_2026-08-09/`.

Alternatively, **re-running `f5_figure_check.py` reverts Figures 1 to 6, S1 and S2 by itself**, in
`writing/figures/` only - its determinism arm re-runs the plotting scripts and they write to the real
output paths. That is a hazard when you did not intend it and a shortcut when you did.

## `generated_jpg_duplicates/`

The nine `.jpg` copies that arrived alongside the generated `.png` files. The manuscript references
the PNGs; the JPEGs are duplicates at lower fidelity and were moved out of `Prompts_Images/` so that
folder holds one image per prompt.
