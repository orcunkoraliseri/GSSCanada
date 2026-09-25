# Appendix C — Documented corrections

Every correction below is read from the artefact that made it, not from a summary. Each entry states
what the defect was, why it needed correcting, how it was resolved, and whether any reported result
moved. No band value or gate verdict is changed by this appendix itself — every "how resolved" line
either points to a decision already taken and cited elsewhere, or states plainly that nothing has
moved yet.

---

## C.1 — Défaut 7: the tower floor-area table was 2.7-3.3x too small, and it shifted every EUI proportionally

**What it was.** The master pipeline document's per-channel "part occupiable" table carried floor
areas that were never parsed from the model: the old Tall column gave **24.4%** for three different
channels (office, retail, residential-implied) — three identical values to one decimal place, "a
template, not a measurement" — and the old SuperTall column (24.1/30.3/16.1/29.5) looked plausible
(distinct values summing to 100%) but corresponded to the model no better. Total building area was
given as **40,846 m² (SuperTall) / 26,750 m² (Tall)**.

**Why it needed correcting.** EUI is a division; the floor-area denominator fixes it entirely. The
pipeline's own **±2 pp** EUI-share gate compares modelled per-channel EUI shares against these
"parsed occupiable shares" — if the reference is a template rather than a parse, the gate compares the
model to nothing, and would fail on retail and office regardless of what the model does. This is
precisely the scenario the project's "a gate must be seen failing" rule exists to catch, and widening
the tolerance to make it pass would have been pure gate-shopping.

**How it was resolved.** Parsed directly from the injected IDF plus the EnergyPlus SQL `Zones` table:
`Σ(FloorArea × Multiplier)` over zones with `IsPartOfTotalArea = 1`, which reproduces EnergyPlus's own
*Total Building Area* exactly, identical across all 28 cells of each tower. Corrected totals:
**SuperTall 135,857.6 m² / Tall 72,623.1 m²** — occupiable **107,816.0 m² / 57,075.4 m²**,
Service/MEP **20.64% / 21.41% of gross** (not "~52% of gross" as the old doc claimed). Corrected
occupiable shares: office **44.33% / 44.65%**, hotel **26.37% / 24.91%**, residential
**22.50% / 22.40%**, retail **4.39% / 5.53%**, residential-common **2.40% / 2.50%**.

**Did any reported result move?** Yes, by construction: the old total areas were **2.7-3.3x too
small** (retail specifically off by ×3.7 SuperTall / ×4.4 Tall), and because EUI is energy divided by
this area, every channel's EUI moved proportionally when the correct denominator was substituted. The
correction is a documentation-and-derivation fix (the table is now derived from `agg_meta.csv` via
Step 8E, never hand-retyped) — **no band value was widened or moved** to absorb this; the EUI values
downstream were computed on the corrected area from the point this was found (2026-07-31) forward.

Source: `Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md:499-545` (finding, French,
"Défaut 7"); `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md:1-35` (corrected table in place, with
the superseded values struck-not-deleted per the project's archive rule).

---

## C.2 — The retail density conversion-factor error: `B-11` is RETIRED, and the real, smaller defect that survives

**What it was.** The backward audit's finding `B-11` originally reported that the model's retail
occupant density (25.0 m²/person, parsed from the injected IDF) contradicted the master document's
stated "~3.7 m²/person" for retail — a "6.8x gap" reported as a modelling defect.

**Why it needed correcting.** The "6.8x gap" was not a defect in the model. NECB states occupancy in
occupants per 1000 ft², not m²/person. Office = **3.72 occ/1000 ft²**, and converting units —
`(1000 / 10.7639) / 3.72 = 24.97 m²/person` — reproduces the value the IDF actually carries. The two
numbers (25.0 and 3.7) were never in conflict; the "6.8x" was the unit-conversion factor itself
(`25.0 / 3.7 = 6.76`), and the finding as originally written was a unit-label error in the project's
own documentation, not a defect in the model. **Why it survived three rounds of checking:** both
numbers were individually correct, so every consistency check that compares the two values passes —
only asking what each value is *denominated in* catches a unit-label error.

**How it was resolved.** `B-11` is **RETIRED** as originally stated. What survives, as a new and
smaller finding: the retail zones run the **office** occupant density (**24.97 m²/person**) where
NECB's own `Retail - sales` space type gives **3.10 occ/1000 ft² = 29.97 m²/person** — retail is
therefore modelled roughly **20% over-crowded** relative to its own NECB reference. Separately, NECB's
retail **schedule type C** is never loaded in the injected IDF (`grep -c "NECB-C-" injected.idf` = 0).
The correct value was loaded via `V2-D9` (NECB-C retail conversion); the blanket-constant observation
(occupancy and plug load both run one office-derived number across every space type, while lighting
*is* differentiated per space type) is unaffected by the retirement and still stands as a documented
limitation.

**Did any reported result move?** The retail occupant density and its NECB-C schedule were corrected
in the model (`V2-D9`, part of the frozen deliverable arm). **No EUI band value moved** to accommodate
this — `S9-EUI-retail` was already failing before and after, under the median-in-band rule (see C.3
below for the companion decision on that gate's rule basis).

Source: `improvements/v0/investigation/investigation_v2/3rdJ_L3_backward_audit_2026-08-04.md:1237-1257`
(retirement note), `:1275-1300` (measurement table); `improvements/v2/3rdJ_L3_v2_implementation.md:376`
(`V2-C3`, DONE 08-05) and the frozen-deliverable identity block,
`improvements/v2/V2-G1_FROZEN_DELIVERABLE.md:9` (`V2-D9` retail NECB-C, part of the deliverable arm).

---

## C.3 — The unsourced 0.95 retail peak fraction against NECB retail's actual 0.80

**What it was.** The master document's retail injection formula cited a "0.95 NECB retail peak
fraction" as the multiplier basis for retail schedule injection
(`retail_schedule_multiplier = 0.95 × peak-normalised shape`).

**Why it needed correcting.** Parsed directly from the injected IDF: the retail zones run the
`NECB-A-Occupancy` schedule, which peaks at **0.9**, not 0.95. The file's own `RetailStandalone`
schedule — the one that would actually apply a retail-specific peak — exists but is **inert** (never
referenced by any retail zone) and peaks at **0.80**. The only 0.95 anywhere in the file is the
**office** schedule's peak. So "0.95, NECB retail peak" was not a retail number in this model at all;
it was an office peak fraction, reused and mislabelled. Two further consequences follow directly: the
injector formula is implemented exactly as specified (`0.95 × shape × lever` produces an injected peak
of 0.9215, confirmed against the artefact — the amplitude effect of getting this constant wrong is a
modest **+2.4%** at peak), but the *baseline the retail channel replaces* is `NECB-A-Occupancy`, an
office-shaped curve that **dips to 0.5 at 12:00-14:00** — a lunch trough where retail's actual peak
should be. The retail channel is therefore a shape intervention, and a larger one than the old
documentation described.

**How it was resolved.** The 0.95 is re-sourced in both master documents as what it actually is (an
office-schedule peak fraction reused as a retail cap), with the office-shaped-baseline point added as
methods documentation. `dr_L3-06`'s original NECB table citation for the 0.95 could not be verified
from public sources and is recorded as unconfirmed.

**Did any reported result move?** No band value moved. The retail rate gate this constant feeds was
independently demoted from a hard all-cells rule to INFO for an unrelated reason (see the `S9-EUI-retail`
median-in-band decision, `V2-B3`) — the 0.95/0.80 correction is a provenance and documentation fix, not
a re-simulation.

Source: `improvements/v0/investigation/investigation_v2/3rdJ_L3_backward_audit_2026-08-04.md:1275-1300`
(measurement table); `improvements/v2/3rdJ_L3_v2_implementation.md:377` (`V2-C4`, retail peak
re-source).

---

## C.4 — The retail episode-time share: 1.50-2.14%, an approximately 25% decline, not "stable"

**What it was.** The master document's validation-target line for retail read "~2.1-2.3%, stable
across cycles" — stated as a target the synthetic diaries must reproduce.

**Why it needed correcting.** The measured weighted episode-time share in shopping locations is
**1.50-2.14%**, and it **declines by approximately 25% across the 2005-2022 GSS cycles**, not stable.
"Stable across cycles" is not merely imprecise; it is false, and it was listed as a validation target
the synthetic model must hit — a fabricated target is worse than an inaccurate description. An
external deep-research pass (`R2`) subsequently corroborated the decline independently: Canada GSS
2005-2022 **-25.0%**, US ATUS 2003-2022 **-20.8%**, UK TUS/CTUR 2000-2022 **-34.4%**, Eurostat HETUS
2000-2020 **-21.4%** — the Canadian decline is internationally normal in both magnitude and direction,
not a coding artefact, and roughly three-quarters of the drop is attributable to real behavioural
change with the remainder linked to a 2022 GSS coding-concentration effect the project had already
found on its own. The measured level (1.50-2.14%) is also internationally normal — every national
series examined falls in the 1.5-2.2% range.

**How it was resolved.** Both master documents were corrected to state "**1.50-2.14%, declining ~25%
across cycles**" in place of "~2.1-2.3%, stable across cycles." A reconciliation paragraph was added
explaining that the 0.97 in-store-share scenario lever survives this correction because it encodes
saturation of the e-commerce displacement curve (post-2022 footfall stabilising near 88-94% of 2019
levels) rather than linear extrapolation of the 2005-2022 trend — the two had appeared incompatible
only because the model behind the lever had never been written down.

**Did any reported result move?** The corrected level and trend are documentation fixes; the retail
rate gate this anchor partly feeds was independently reclassified (see C.3). No EUI band value moved.

Source: `improvements/v0/investigation/investigation_v2/3rdJ_L3_backward_audit_2026-08-04.md:874-918`
(R2 findings and revised action); `improvements/v2/3rdJ_L3_v2_implementation.md:378` (`V2-C5`, DONE
08-04); stale line still visible, struck-not-deleted, at
`Leg3_4-split/Step2_docs/3rdJ_02_harmonizeGSS_4split.md:43`.

---

## C.5 — The Richardson attribution correction (`V2-C8`)

**What it was.** Six sites across the master documents and `dr_L3-06` attributed the project's
peak-normalisation decode-time decision to Richardson et al. (2010), describing their model as
`any-present × N` — a shape-extraction / amplitude-anchoring construction.

**Why it needed correcting.** Richardson et al. (2010) does not use `any-present × N`. What they
actually implement is a **household-level first-order Markov chain over the active-occupant count
S(t) ∈ {0…N}** at 10-minute resolution — a materially different model class from what was cited. The
citation was checked against the paper's abstract and methods (the full text is paywalled, and this
limit is stated at each corrected site rather than hidden).

**How it was resolved.** The citation was corrected at all six sites it appears —
`3rdJ_00_4split_Occupancy_Pipeline.md:332` and `:486`, `..._Overview.md:241`,
`dr_L3-06_retail_diurnal_targets_REPORT.md:55`, `:106`, `:185` — struck-not-deleted, plus a new `:186`
entry for the 2008 companion paper (its DOI explicitly flagged as unverified). Every one of the six
sites explicitly states that **the peak-normalisation decision itself is unaffected**: the attribution
was wrong, the decision it was cited to support was not.

**Did any reported result move?** No. This is a citation-accuracy correction only; no band, gate, or
numeric result changed.

Source: `improvements/v2/3rdJ_L3_v2_implementation.md:381,783-797` (task spec),
`:2382-2392` (`V2-C8` closure, "verdict unaffected").

---

## C.6 — The `dr_L3-03` hotel-band primaries that do not exist, and the first-party replacement

**What it was.** The hotel EUI band `[180, 240, 300]` (as-modelled floor/central/ceiling) was cited to
`dr_L3-03_hotel_eui_bands_REPORT.md`, whose own Table 2 in turn cited two primary sources for the 300
ceiling, including a document identified as `PNNL-28543`.

**Why it needed correcting.** Both `dr_L3-03` primaries were chased to the document itself, and
**neither exists as cited**. One returns `NOT FOUND`. `PNNL-28543` resolves to a nuclear-fuel report —
confirmed **twice, independently** — not an energy-simulation prototype document. The band was
therefore **unsupported, not wrong**: a citation is not evidence until it has been opened, and this one
could not be opened into what it claimed to be.

**How it was resolved.** A first-party replacement was retrieved directly from the ASHRAE 90.1-2019
prototype building ZIP's own `.table.htm`: **DOE/PNNL Large Hotel, ASHRAE 90.1-2019 = 284.44 kWh/m²·yr
at CZ 6A, 299.28 kWh/m²·yr at CZ 7**. A pre-registered prediction that this retrieval route would
reproduce a companion report's numbers (`RV05`) was tested and **passed at 0.00% disagreement on
10/10 rows**. The **300 ceiling was kept, not moved** — it sits **1.0%** from the vintage-matched
90.1-2019 CZ 7 value (299.28), so the objection that "a 2004-vintage band is scoring a 2019 building"
does not hold once the citation is corrected to the right vintage. The residual archetype gap (the
project's NECB-2017 Montréal/Calgary geometry vs. the 90.1-2019 prototype's own Rochester/International
Falls climate stations) is recorded as a limitation, not folded into a tolerance.

**Did any reported result move?** The **citation moved; the number and the gate verdict did not.**
`S9-EUI-hotel` remains **FAIL** before and after this correction — the band values `[180, 240, 300]`
are unchanged, only their sourcing changed from a non-existent document to a verified first-party
retrieval.

Source: `improvements/v2/3rdJ_L3_v2_implementation.md:406,408` (`V2-F4` negative result, `V2-F6`
retrieval), `:3433-3441` (`V2-C6` propagation, "no band value was widened"), `:3168,3209-3243`
(the 284.44/299.28 figures and the 1.0% vintage-match check);
`improvements/v0/investigation/investigation_v2/3rdJ_L3_backward_audit_2026-08-04.md:2417` (`G-2`
terminal status, independently reproduced by the blind Gemini audit).

---

## C.7 — The `V4-B4` 2J EUI extraction defect, and the argument for Leg-3's immunity

**What it was.** The **submitted** 2J manuscript's Table 5 residential EUI values (SingleDetached,
OtherDwelling, MidRise, HighRise) were computed by a shared `calculate_eui()` function carrying two
defects: (1) a double-counted peak-demand table — a power quantity, summed into an annual energy total
as if it were an energy quantity — and (2) a water-heating guard (`if 'm3' in str(units)`) that
correctly zeroes water energy on SI runs but fails to recognise IP units (`gal`), so on IP runs water
volume is summed directly into the EUI as if it were kWh.

**Why it needed correcting.** All 6,000 published run directories behind 2J's Table 5 were recomputed
(a full census, not a sample, because the raw outputs turned out to be present locally rather than
cluster-only). The recomputed electricity total was cross-checked against a path the defect cannot
reach — `elec_facility_kWh`, built from the raw hourly EnergyPlus meter stream by a separate script —
with **maximum disagreement 0.067%** across 400 cross-checked runs, confirming the corrected numbers
are right and the published numbers are not.

**How it was resolved — the corrected residential EUI (2022, kWh/m²·yr, rounded as reported in the
live submission table):**

| Archetype | Published (2022) | **Corrected (2022)** | Band (NRCan SHEU-2019) | Verdict change |
|---|--:|--:|---|---|
| SingleDetached | 200.0 | **115** | 130.6-186.1 | above upper (+7%) → **below lower (≈12%)** |
| OtherDwelling | 114.9 | **100** | 136.1-186.1 | below lower (16%) → below lower, deeper (≈27%) |
| MidRise | 169.6 | **108** | 111.1-216.7 | within band ("Yes") → **below lower (≈3%)** |
| HighRise | 127.8 | **78** | 113.9-147.2 | within band ("Yes") → **below lower (≈31%)** |

(Pooled five-year-mean figures, a different basis reported alongside the 2022 column in the same
source, are larger still for the published side — e.g. SingleDetached pooled published 200.40 vs.
corrected 118.44 — and show the identical direction and all-four-below-band pattern; the 2022 column
above is the one reproduced in the live submission table cited below.)

The mechanism is a unit-system split, not a uniform bug: on **SI** runs the water guard correctly
zeroes water energy, so the double-counted demand table is the operative defect (dominant on
MidRise/HighRise, apartment archetypes, 34-37% of the published total); on **IP** runs the water
volume is summed as if it were energy, so the water-unit defect dominates (SingleDetached/OtherDwelling,
up to 40.8% of the published total). Every run carries both mechanisms; the unit system decides which
one is negligible and which is decisive. All four archetypes fall **below** their SHEU regional-average
ranges once corrected — the published table had reported one archetype above its band, one below, and
two inside; the corrected table reports all four below.

**The Leg-3 immunity argument.** Leg-3 (this paper) is verified immune to this defect because its EUI
values are read from **hourly meter streams**, never from the tabular demand-summary table
`calculate_eui()` reads. This is worth one sentence in Leg-3's own Limitations as a reproducibility
point: the same class of extraction defect exists in the codebase this project descends from, and
Leg-3's pipeline structurally does not route through the vulnerable function.

**Did any reported result move?** Yes, in the 2J manuscript directly: **three of the four SHEU band
verdicts change**, and both archetypes previously reported "within band" (MidRise, HighRise) now read
below their lower bound. **No SHEU band value itself moved** — the correction is entirely in the
simulated column; the NRCan reference ranges are unchanged. The corrected values are live in the 2J
submission copy's Table 5, not in an archived pre-correction copy.

**Source of truth, and what is explicitly not the source of truth.** Corrected values verified present
at `../2J_docs_occ_nTemp/writing/fullSet/readySubmission.md:367` (SingleDetached row reads **115** /
**116** for 2022/2030). **Not** the archived pre-`V4-B4` copies, and **not**
`writing/sharingCHV/2ndOcc_Journal.docx`, which still carries the stale (published, uncorrected) table.
A second, independent defect was found while tracing this one: `2J_full_manuscript.md` (as opposed to
`readySubmission.md`) reproduces from a **different, superseded** simulation campaign entirely — both
files share the same modification timestamp, so the divergence is invisible from the filesystem and
was only found by reproducing each table from its own underlying data.

Source: `improvements/v4/V4-B4_RESULTS.md` (full derivation, §§1-5); `improvements/v4/V4-B4_PREREGISTRATION.md`
(pre-registered predictions, one of five — Q4, "the campaign is uniformly SI" — **FAILED**, corrected
to "3,000 SI / 3,000 IP, split cleanly by archetype"); `improvements/v4/3rdJ_L3_v4_implementation.md:71`
(status row, "6,000 runs re-read; 3 of 4 band verdicts change").
