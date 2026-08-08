# V2-G1 -- FROZEN DELIVERABLE ARM (3J Leg-3, four-split)

**Frozen 2026-08-06 00:05.** This is the arm the paper reports. Its predecessor is kept intact; only the pointer moves.

## Identity

| field | value |
|---|---|
| arm | **deliverable** = base arm + V2-D9 (retail `NECB-C`) + V2-D10 (per-object DHW resize) |
| resize spec | `Laundry Service Water Use 30.6gpm 180F=8.5` |
| resize mode | `per_object`, default K = **1.0** on every other burner |
| burners moved | **1 of 11** (`300gal Natural Gas Water Heater - 300kBtu/hr 9 0.804 Therm Eff`) |
| plant | 887.2 kW -> 1546.6 kW installed |
| `INJ_HASH` | `cf69d508` (inherited -- the injection did not change) |
| `INPUTS_HASH` | `85773432` |
| `OUTPUT_SCHEMA_HASH` | `['93dd5129']` |
| cells | **56 / 56** |
| platform | `['win32']` (measured per cell, not inherited -- see V2-D10's provenance fix) |
| EnergyPlus | 24.2.0, build `94a887817b` |
| host / OS / python | `tabletop1` / `Windows-11-10.0.26100-SP0` / `3.13.5` |
| SLURM job IDs | **none -- this arm ran on local win32.** Speed unavailable by standing instruction; a placeholder job id would be a fabricated provenance field |

## Code hashes

| component | md5 | path |
|---|---|---|
| injector (Step 7) | `fa8bb8a8124c0df1ea07b05d87c5a699` | `3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/3rdJ_07_aug_to_bem_4split.py` |
| campaign cell (resize) | `8a4530b6de697566dc25b5e0a35e1dce` | `3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09H_resize_campaign_cell.py` |
| resize primitive | `94d28d1e20644a7b6a4e7ec4045f1e24` | `3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09H_plant_resize_probe.py` |
| retail NECB-C converter | `28714c43c0ae6b1db75b5390fa0ebedb` | `3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09J_retail_necb_c.py` |
| aggregator (Step 8E) | `64d2c530a4f23c9e7043d0835c2b283f` | `3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08E_aggregate_4split.py` |
| scorer (Step 9) | `e4283d83577940a4cc6a5245bf6e278f` | `3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.py` |

## Aggregate tables

| table | md5 | rows |
|---|---|---|
| `agg_annual.csv` | `7b96e4f6f15dbf90093041c1c8ead7ff` | 4088 |
| `agg_annual_by_channel.csv` | `f5b67444480d504cbdc2e3ffebf8e015` | 392 |
| `agg_diurnal.csv` | `2636786563b6dcab0a55fd9bef3028c3` | 129024 |
| `agg_meta.csv` | `9cd67667548b15469b8c73ed600b607b` | 56 |
| `agg_peak.csv` | `a65aaca4d2cd9fe88512b9396dcf3011` | 2072 |

## Step-9 deliverable assets (added 2026-08-06 -- the manuscript reads these)

Every figure and table the 3rd-journal manuscript cites is copied from
`Leg3_4-split/Step9_docs/outputs_step9_deliverable/`. Their md5s are registered here for the same
reason the aggregate tables above are: so a copy can be verified by content after it has been
renamed. `improvements/v5/f3_asset_provenance_check.py` reads this section.

| asset | md5 |
|---|---|
| `figures/fig_diurnal_4ch.png` | `5117cfabf0a252738d36a9cd00c68ba4` |
| `figures/fig_eui_4ch.png` | `b17ca5e2c65331ee624d1f52213bf5f0` |
| `figures/fig_longitudinal_4ch.png` | `4e32389ff3ac42ac551e01d52558a76c` |
| `figures/fig_peakhour_4ch.png` | `83ebb7de79398205c9df088d729dfdc0` |
| `figures/fig_scenario_4ch.png` | `6e94a2332d67e505f30283dcbf86bcf2` |
| `step9_eui_by_channel.csv` | `9f2367ddda83ca5351a3fb077b3d9994` |
| `step9_gates.json` | `e5ea569e7f072b700bc771dda9870757` |
| `step9_loadshape_peaks.csv` | `7722369e3de7493036a70ff880524ff8` |
| `step9_longitudinal.csv` | `735f19a98982228616bece8af06d7658` |
| `step9_report.html` | `259b104aa0f6e87b8d3ee0607500d407` |
| `step9_scenario_response.csv` | `8e927778362ed50885f8f9a4db5de810` |
| `figures_hires/fig_diurnal_4ch.png` | `e1d6e0c712e7dce3256382ce122d4cc6` |
| `figures_hires/fig_eui_4ch.png` | `15af64b6d1cf9bd3b42e6cfb131ed156` |
| `figures_hires/fig_longitudinal_4ch.png` | `474314e9d455ef6acf237f94eea8f870` |
| `figures_hires/fig_peakhour_4ch.png` | `ae4d14cc14beec07c7d05c7e80d8915a` |
| `figures_hires/fig_scenario_4ch.png` | `6f4a6703147335bc714e52920f594c39` |

> **Why `figures_hires/` at 600 dpi and not the 300 dpi set registered here earlier the same day.**
> The first re-render targeted 300 dpi, on the assumption that 300 is *the* publisher minimum. `RV10`
> item 7 then reported Elsevier's minimums as **300 dpi for halftones, 500 dpi for combination art,
> and 1000 dpi for bitmapped line drawings**. These five are line plots carrying text, which is
> combination art, so **the 300 dpi set would have shipped still failing the stated minimum.** It was
> replaced, not supplemented, and a vector PDF is now written beside each PNG. This is the second
> time in one day that a number was acted on before its source was read; the first was the abstract.

**The `figures_hires/` rows are an ADDITION, made 2026-08-08. Nothing above them changed.** The
140 dpi figures in `figures/` remain the frozen render and keep the md5s registered above; the
manuscript now carries the 300 dpi copies because 140 dpi is below the publisher's artwork minimum.

The two renders are the same figure. That claim is not asserted, it is tested by
`improvements/v5/f6_figure_replot_equivalence.py`, whose load-bearing arm re-renders at the
**original** 140 dpi and requires byte-identity with the frozen files. All five reproduce exactly,
which isolates the pipeline from the resolution: the same code reading the same aggregates returns
the same image, so a dpi change can only add pixels.

🔴 **The input that produces them is not the Step-9 script's own default.** `DEFAULT_AGG` at
`3rdJ_09_activityDrivenLoads_4split.py:63` points at `outputs_step8/agg`, which is the **superseded**
arm; the canonical deliverable was built from `outputs_step8/agg_deliverable`. Rendering on the
default reproduces only 1 of 5 figures, and the tables rebuilt from it differ from the shipped ones
in EUI, in peak hour, and in **16 `verdict_asmodelled` cells**. A default inside a pipeline script is
not provenance.

> 🔴 **One collision this manifest cannot resolve.** The superseded sibling
> `Step9_docs/outputs_step9/` (2026-07-31 11:42) carries **the same 11 filenames**. Ten differ, and
> **`fig_diurnal_4ch.png` is byte-identical in both** -- so for that one file a content check has no
> signal and both directories are correct answers. Its provenance must be recorded at copy time.
> The sibling is **not** deletable: `step9_envelope_exposure.csv` and the three `finding9_verify/`
> IDFs exist nowhere else. Both directories carry a `_PROVENANCE.md` stating which is which.

## Scorecard

`{'FAIL': 3, 'INFO': 10, 'PASS': 17}` over **30** gates.

| gate | status |
|---|---|
| `S9-EUI-office` | **FAIL** |
| `S9-EUI-retail` | **FAIL** |
| `S9-EUI-hotel` | **FAIL** |

## Test method -- one headline number re-derived from the frozen artefact's own columns

Hotel channel EUI median, recomputed here as `sum(agg_annual.energy_GJ where channel==hotel) / agg_meta.area_hotel_m2 x 277.7778`:

```
median = 260.5411 kWh/m2/yr   (min 203.3295, max 318.4200, n = 56)
```

The scorer, reading the same tree independently, reported:

```
RULE IN FORCE = all_cells -> FAIL. Median 260.5 kWh/m2/yr vs [180.0-300.0]; 28/56 cells inside, 0 below the 180.0 floor / 28 above the 300.0 ceiling; range 203.3-318.4. COUNTERFACTUAL: the median-in-band rule would return PASS on this same data -- *** THE TWO RULES DISAGREE HERE, so this gate's status is set by the RULE CHOICE and not by the model; read the decision in band_src before quoting it. (ASHRAE 90.1-2019 Large Hotel prototype, retrieved first-party by V2-F6 from the prototype ZIP's own .table.htm: 284.44 kWh/m2/yr at CZ 6A, 299.28 at CZ 7 (evidence: improvements/v2/f6_prototype_evidence/). *** SUPERSEDES dr_L3-03 as the CITATION for these values (V2-B2, 2026-08-05): V2-F4 chased dr_L3-03's two primaries to the end and NEITHER EXISTS (one NOT FOUND; PNNL-28543 resolves to a nuclear-fuel report). The band was unsupported, not wrong -- the 300 ceiling rested on the 90.1-2004 lineage's 302.21 and the vintage-matched 2019 value is 1.0 % from it, so the 'a 2004 band scores a 2019 building' objection is dead. Values unchanged; gate still FAILs. Residual archetype gap (NECB-2017 MTL/Calgary vs 90.1-2019 Rochester / International Falls) is a LIMITATION -> V2-G3, NOT a tolerance)
```

Attribution residual across all cells: **0.00000000 %** (max |value|).


## Where it lives

| artefact | path (relative to `3J_docs_occ_nTemp/`) |
|---|---|
| 56 cells (IDF, manifests, hourly CSVs) | `Leg3_4-split/Step8_docs/campaign_local_deliverable/` |
| §8E aggregate, 5 tables | `Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/` |
| Step-9 scorecard + report + figures | `Leg3_4-split/Step9_docs/outputs_step9_deliverable/` |
| pre-registration (written before the run) | `improvements/v2/V2-E5_PREREGISTRATION.md` |

**The predecessor is intact and the pointer moved, per the project's archive-predecessor rule.**
The base arm remains at `Step8_docs/campaign_local_v2/campaign_cf69d508/`, its aggregate at
`outputs_step8/agg/`, and its scorecard at `outputs_step9/`. Nothing was overwritten.

> **What is NOT kept, stated so its absence is not mistaken for loss.** Each cell's `run/` directory
> — `eplusout.sql`, `.eso`, `.err` and the rest, **311 MB per cell, 23 GB for the arm** — is not
> copied here. It is regenerable from `injected_resized.idf` plus the EPW named in the manifest, by
> the EnergyPlus build hashed above. What is kept is everything the aggregate and the scorecard were
> derived FROM, so every published number can be re-derived without re-simulating.
