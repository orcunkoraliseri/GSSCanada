# Image prompts v2 — terminology-corrected

Same prompts as `Prompts_Images/`, with one change: every prompt now carries a **TERMINOLOGY LOCK**
block forbidding `Leg-1` / `Leg-2` / `Leg-3` / `2J` / `3J` in the artwork and giving the descriptive
replacement for each.

## How to use

Open the file, paste **only the fenced code block** into Gemini Antigravity. Everything outside the
fence is authoring notes and provenance.

## Generate these 9

| file | drop-in name for the PNG |
|---|---|
| `Figure_01_pipeline_4split.md` | `Figure_01_pipeline_4split.png` |
| `Figure_02_three_leg_roadmap.md` | `Figure_02_three_leg_roadmap.png` |
| `Figure_03_three_head_transformer.md` | `Figure_03_three_head_transformer.png` |
| `Figure_04_exclusivity_projection.md` | `Figure_04_exclusivity_projection.png` |
| `Figure_05_hotel_sidetrack.md` | `Figure_05_hotel_sidetrack.png` |
| `Figure_06_tag2_dispatch.md` | `Figure_06_tag2_dispatch.png` |
| `Figure_S02_scenario_levers.md` | `SI/Figure_S02_scenario_levers.png` |
| `Figure_S03_leg2_pipeline.md` | `SI/Figure_S03_leg2_pipeline.png` |
| `graphicalAbstract.md` | `graphicalAbstract.png` |

**Keep the filenames exactly as listed.** They are referenced by the manuscript build; renaming breaks it.

## Do NOT generate these 6

`Figure_07`, `Figure_08`, `Figure_09`, `Figure_10`, `Figure_11`, `Figure_S01` — data figures. Their
prompts are here for reference only. An image tool invents the numbers (it produced `4.0.1` and
`0.37` for S01), so these stay plotted from the CSVs.

## Two things to check on what comes back

1. **No stage codes anywhere in the pixels** — that is the whole point of v2.
2. **Long edge ≥ 3500 px.** Elsevier wants 500 dpi at 7 in placed width. The previous round came back
   at 1376 × 768 ≈ 197 dpi. Do not upscale after the fact; regenerate larger.

Put the finished PNGs anywhere and tell me the folder — I will install them and rebuild.
