# 4J re-run — draft text changes (plan Phase 1.7), 2026-10-01

Plan: `IMP/docs/2026-10-01_rerun-London-Bologna-stock-enduse_plan.md`. Line numbers are those of 2026-10-01
(`writing/submission/4J_manuscript_submission.md` = M, `4J_supplementary_material.md` = SI).
Blanks in [BRACKETS] are filled from the new output files only (Phase 8.2), never from this file.
Author rule (D2): new values only; no old value, no before/after, no process history in the prose.

Blanks and where each is read:
- [N_LDN], [N_BOL] flats; [B_LDN], [B_BOL] buildings: `step11input_manifest.json` (`n_flats`, `n_buildings_kept`).
- [N_EXCL] floor-averaged buildings, both cities, as a word if under 100: the two manifests (`dropped_floor_averaged`).
- [N_UNDIV] buildings whose plate could not be divided (Arm F) and [N_COURT] courtyard buildings: C2 `preflight_report.json`.
- [R2_LDN], [R2_BOL]: `step11_11-5_<fold>_reseed.json`; 2 decimals in M, 4 in SI.
- [DHW_LDN], [DHW_BOL] litres per dwelling-day: `g11_6_18/c2_<fold>/step11_stockboard_<fold>.json`; 2 decimals.

## Manuscript

**M1, line 129** (end of the hot-water paragraph). Replace from "At stock scale, ..." to the end of the paragraph with:

> At stock scale, the same appliance and hot-water model runs on [N_LDN] flats in [B_LDN] London buildings and
> [N_BOL] flats in [B_BOL] Bologna buildings, with one diary per flat. The number of flats in a building follows
> its floor area. [N_EXCL] buildings whose diaries were averaged per floor rather than assigned per flat are excluded.

(The sentence "A heating campaign on observed stock in three districts is recorded in Supplementary S9; no
result from it is used here." is deleted.)

**M2, line 237.** "At stock scale it is 0.43 in London and 0.08 in Bologna." becomes
"At stock scale it is [R2_LDN] in London and [R2_BOL] in Bologna." Then re-read the rest of the paragraph
(laundry cause) against the new values; if it no longer holds, stop (plan 4.2).

**M3, line 299.** Delete "Absolute results from the archetype and observed-stock campaigns are never compared."

**M4, line 69** (table row "Observed building stock ... London district | Bologna district | Stock-scale
appliance and hot-water loads"): no change.

**M5.** After filling: grep M for "observed stock", "observed-stock", "heating campaign", "35,090", "410",
"Madrid", "7,602", "29,902", "Forty-nine", "0.43", "0.08". Expected hits: none, except "Madrid" in references.

## Supplementary material

**SI-1, line 9.** "S9 the observed-stock campaigns." becomes "S9 the stock-scale end-use runs."

**SI-2, lines 191-193** (campaign sizes table). Delete the rows "Observed stock, heating campaign" and
"Observed stock, exploratory layout". The stock row becomes:

> | Stock-scale end use | London [N_LDN] flats in [B_LDN] buildings; Bologna [N_BOL] flats in [B_BOL] buildings; one diary per flat | 2 folds |

**SI-3, lines 386-387.** "At stock scale, on 7,602 London flats and 29,902 Bologna flats, agreement is 0.4347
and 0.0781." becomes "At stock scale, on [N_LDN] London flats and [N_BOL] Bologna flats, agreement is [R2_LDN]
and [R2_BOL]." (4 decimals.)

**SI-4, line 399.** "and at stock scale at 202.41 and 200.35." becomes "and at stock scale at [DHW_LDN] and [DHW_BOL]."

**SI-5, lines 426-428.** Delete the paragraph "**Exploratory observed-stock layout (410 cells).** ..."

**SI-6, lines 457-476.** Replace the whole of S9 with:

> ## S9. The stock-scale end-use runs
>
> The appliance and hot-water model runs on two districts, one in London and one in Bologna. Building
> footprints and storey counts come from national open registries, and each building carries the archetype
> identifier emitted by the stock pipeline. Each floor plate is divided into dwellings only: every square
> metre belongs to a flat, and no flat is narrower than two metres. Neither district has an observed dwelling
> count. A single-family or terraced house holds one dwelling. In a block of flats, the number of flats is the
> footprint area times the storey count, divided by the floor area per flat of its TABULA reference building
> (reference floor area over its number of flats), rounded, with at least one flat; where these inputs are
> missing, the reference building's number of flats is used. Each flat draws its own diary. The runs cover
> [N_LDN] flats in [B_LDN] London buildings and [N_BOL] flats in [B_BOL] Bologna buildings. [N_UNDIV]
> buildings whose floor plate could not be divided into flats and [N_COURT] courtyard buildings are outside
> the subdivision method. [N_EXCL] buildings carrying floor-averaged rather than per-flat diaries are
> excluded, never scored and never estimated. A Lyon district was kept in the wider project as a physical
> baseline only and is never a denominator for any result.

**SI-7, line 566.** Delete "Absolute intensities from the archetype and observed-stock campaigns are never
placed side by side or differenced."

**SI-8, line 584.** Delete "Results from the observed-stock campaign are numerically stable rather than
bitwise reproducible."

**SI-9, lines 599-600.** Delete "No scored result is taken from the larger observed-stock campaign."

**SI-10, lines 620-622.** Delete the paragraph "**Observed-stock campaign.** ..."

**SI-11.** After filling: grep SI for "observed-stock", "observed stock", "heating campaign", "35,090",
"35,290", "410", "Madrid", "courtyard", "7,602", "29,902", "0.4347", "0.0781", "202.41", "200.35".
Each remaining hit must be about something other than the dropped runs; S-number cross-references
(S7.6, S9) must still point at the right sections.

## Figures (plan Phase 7)

**F1, Figure 1 card 10** ("Real-stock UBEM", "observed footprints, one diary per dwelling"). The card still
describes what the re-run does (flats on observed footprints, one diary each), so no wording change is
needed unless the author wants "heating" removed from any label; check the installed image.
`generate_fig01_pipeline.py` cards 10-11 are the same.
