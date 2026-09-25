# Table 6 - What Leg-3 added (the additive ledger)

This table carries the paper's additive claim: Leg-3 adds Retail and Hotel without invalidating a
prior Leg-2 figure. Per the standing hard rule, a **Bit-identical? = Yes** cell is entered only where
this task located file-level evidence (a shared file path, or an md5 computed in this task) - never
from the pipeline overview's prose alone. Where no such evidence was located, both the verdict and the
Evidence cell read `⚠ check source`; that is treated as a successful, honest outcome, not a gap to be
papered over.

| Pipeline step | Leg-2 artefact | Leg-3 change | Bit-identical? | Evidence |
|---|---|---|---|---|
| Step 1 - Data collection | `3rdJ_01_readingGSS_2split.py` - GSS column selection for AT_HOME / AT_WORK | `3rdJ_01_hotelIngest_4split.py` (new, non-GSS: `hotel_occupancy_monthly.csv` from ISQ/CBRE) + `3rdJ_01_readingGSS_4split_val.py`; no new GSS variables added for AT_RETAIL (derives from `occPRE`/`occACT` already carried) | ⚠ check source | Script renamed `2split` -> `4split` (`Leg2_2-split/Step1_docs/3rdJ_01_readingGSS_2split.py` vs `Leg3_4-split/Step1_docs/3rdJ_01_readingGSS_4split_val.py`); no byte-level or column-level comparison of GSS-column output was performed in this task |
| Step 2 - Data harmonization | `3rdJ_02_harmonizeGSS_2split.py` - crosswalk + OR-rule for AT_HOME / AT_WORK | `3rdJ_02_hotelHarmonize_4split.py` (new) + the AT_RETAIL OR-rule (frozen OD-1, see Table 2 footnote 1) | ⚠ check source | Script renamed; no byte-level or column-level comparison performed in this task |
| Step 3 - Merge and tiling | List-driven `tile_work_to_30min` tiler (cloned from the 9-channel co-presence tiler), residential + office 30-min output | `3rdJ_03_mergingGSS_4split.py` appends one list entry (AT_RETAIL); retail kept in a **separate CSV** (`retail_30min.csv`) specifically so it cannot overwrite the residential/office columns | ⚠ check source | The pipeline overview asserts "residential + office paths bit-identical" (`Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md`, STEP 3 box, line 57) - this is the design **intent** (separate CSV, additive list entry), but per the standing hard rule this prose claim is not itself acceptable evidence; no independent file/column comparison of the tiler's residential/office output was performed in this task |
| Step 4 - Three-GSS-head Transformer | 2-head Transformer (Head 1 resid, Head 2 AT_WORK), `3rdJ_04B_model_2split.py` | 3rd head (AT_RETAIL) added, `3rdJ_04B_model_4split.py`; backbone is "keep + targeted upgrades" (warmup + PCGrad + logit-adjusted BCE + raking), not a frozen copy (dr_L3-11, OD item 13) | No | `3rdJ_00_4split_Occupancy_Pipeline_Overview.md` VALIDATION GATES table, row "Transformer (Regression) \| Old head (Head 1 & Head 2) JS drift \| ΔJS ≤ 0.002 bits vs Leg-2 validation baseline" (line 205) - a **tolerance-based regression gate**, not a bit-identity claim; Head 1/2 outputs are expected to drift by up to 0.002 bits of JS divergence, not to reproduce Leg-2 bit for bit. The measured ΔJS value for this gate was not located in this task - ⚠ check source for the number itself |
| Step 5 - Archetype linkage | Residential Census linkage (Leg-1, `3rdJ_05_censusLinkage_2split.py`); Office NOCxNAICS linkage (Leg-2) | Retail: single PNNL "Retail Retail" archetype, population-level fraction, no lookup; Hotel: province-level multiplier (QC / AB), no respondent archetype | ⚠ check source | `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` STEP 5 box (lines 79-84) states residential/office linkage is reused ("DONE (Leg 1)" / "DONE (Leg 2)"), but no file/column-level comparison of the Leg-3 linkage output against the Leg-2 linkage output was performed in this task |
| Step 6 - Forecast to 2030 + hotel side-track | `W_2005->W_2010_ft->W_2015_ft->W_2022_ft` GSS raking chain + `DRIFT_MATRIX`; office WFH bands (conservative/hybrid/fullyhybrid) | Same raking chain code reused for GSS channels; retail lever (3 named 2030 bands) added; hotel SARIMA(1,1,1)(1,1,1,12) side-track added, bypassing the Transformer entirely | No | `Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md` "Defaut 4" (lines 267-332, OPEN as of this task): a measured Step-6 calibration bias - post-calibration 2030 work-presence is **-10.51 pp** vs OBS2022 (Cohen's d -0.649), 4-5x the ~2.4 pp WFH signal the campaign exists to detect. This is a documented, measured divergence in the Step-6 output magnitude, not a reproduction of a stable Leg-2-equivalent value; it directly contradicts a "residential/office Step-6 output is unchanged" reading for the 2005-2030 axis (the bias is reported as near-common-mode across the 3 WFH bands, so cross-band deltas are less affected, but the level itself has moved) |
| Step 7 - BEM/UBEM integration | `office_integration.py`, 2-channel Tag-based injection into the same PNNL Tall/SuperTall geometry | `commercial_integration.py::inject_mixed_use()`, Tag-2 exact-match dispatch across 4 channels; missing channel falls back to NECB baseline (additive-safe) | **Yes, for the base prototype geometry only** | Leg-3's own campaign driver reads the **same physical IDF files** from Leg-2's own Step-8 output directory, unmodified, with no copy made (`Leg3_4-split/Step8_docs/3rdJ_08D_campaign_cells.py:121`, `.../office_idfs_v242/{CAN_MTL,CAN_CLG}/`). Md5 computed in this task confirms the 4 files are byte-identical to the values recorded in `3rdJ_08_implementation_improvements.md` §C-bis: `CAN_MTL/TallBuilding_..._Z6_v242.idf` = `a2a4817624289d581c92e70d676ef78a`; `CAN_MTL/SuperTallBuilding_..._Z6_v242.idf` = `0365e7a0f1ddb7079a799c51f42d48ef`; `CAN_CLG/TallBuilding_..._Z7A_v242.idf` = `9390293b90c10fa36308d285a24e635b`; `CAN_CLG/SuperTallBuilding_..._Z7A_v242.idf` = `8c136554d3c369522e2bdbc8176ad9ad`. This is evidence for the shared **geometry**, not for the injector code: three copies of the related residential injector `eSim_bem_utils/integration.py` (live repo, the 2J snapshot, the Leg-2 frozen snapshot) were md5'd in this task and **do not match each other** (`9f886fb9427e6bbc4adb7599cbcf3600`, `537183b443846adeb20a0fc191c32159`, `6a92268be1f8dc3301df3bec80d6dd2e` respectively) - the injector code is not a frozen, bit-identical asset across legs, only the base building geometry is |
| Step 8 - BEM simulation | 72-run residential 2030 re-sim + office campaign; final scorecard **50 PASS / 2 WARN / 17 INFO / 0 FAIL** | 56-cell campaign (2 buildings x 2 cities x 14 scenarios), all 4 channels injected per cell | ⚠ check source (channel-isolation shown, cross-leg output not compared) | Leg-2 scorecard: `Leg2_2-split/improvement/2J_to_3J_improvement_implementation.md:1514` - "Full chain re-run on the mutex-clean `_C` deliverable ... agg+val **50P/2W/17I/0F** -> Step-9 **10P/1W/0F**. 0 FAIL end-to-end." Leg-3 channel-isolation evidence (a narrower, Leg-3-internal claim, not a cross-leg reproduction): `Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md`, "Etat verrouille" table row "Cloisonnement inter-canaux" (line 62, PASS, Δ = 0.0 exactly for any non-varied channel between cell pairs) and the "Trois recoupements quantitatifs independants" section (lines 573-583): "Δ office et hôtel rigoureusement inchangés ... désormais prouvé par simulation, pas déduit" against probe job `1169804`. This proves office/hotel are unperturbed **within Leg-3's own retail-fix re-simulation**, not that Leg-3's office/residential numbers reproduce Leg-2's own published Step-8 figures bit for bit - that cross-leg comparison was not performed in this task |
| Step 9 - Activity-driven end-use loads | Bi-channel (resid vs SHEU, office vs NECB-PNNL); final scorecard **10 PASS / 1 WARN / 0 FAIL**; Office EUI **172.7 kWh/m2/yr**, PNNL band [100, 200], PASS | Four-channel (resid, office, retail, hotel), 30 gates; scorecard `{PASS: 17, INFO: 10, FAIL: 3}`; 3 gates (office, retail, hotel EUI) left failing on purpose (see Table 5) | No | Leg-2: `Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.md:140` - "Office · Knowledge / Public / Sales \| tower \| 84 each \| 172.7 / 172.6 / 172.6 \| PNNL 100-200 \| **PASS**". Leg-3: `Leg3_4-split/Step9_docs/outputs_step9_deliverable/_PROVENANCE.md:15-19` - scorecard `{'PASS': 17, 'INFO': 10, 'FAIL': 3}` over 30 gates, arm = base + V2-D9 + V2-D10. 🔴 Comparability caveat, not resolved: `3rdJ_08_implementation_improvements.md` "Defaut 5" (lines 441-447) records an **open, user-untranscribed question** - Leg-2's Step-9 office EUI reads `Electricity:Facility` only (no gas), while the same shared tower IDF burns 13,884.91 GJ of natural gas per run; whether the Leg-2 172.7 figure is electricity-only or all-fuel, and therefore whether it is even the same **basis** as Leg-3's dual-basis all-fuel EUI, is explicitly unresolved in the source document |

---

## Sources

- `Leg2_2-split/Step1_docs/`, `Step2_docs/`, `Step5_docs/`, `Step7_docs/` directory listings (script
  names cited above).
- `Leg3_4-split/Step1_docs/`, `Step2_docs/`, `Step5_docs/` directory listings (script names cited
  above).
- `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` - STEP 3 box (line 57), STEP 5 box
  (lines 79-84), STEP 6 box (lines 86-102), STEP 7 box (lines 104-122), VALIDATION GATES table (line
  205, Transformer Regression row).
- `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md`, OPEN DECISIONS item 13 (line 281,
  dr_L3-11: "Keep + targeted upgrades").
- `Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md`:
  - "Etat verrouille au 2026-07-28" table (line 58, IDF reuse + 36-byte delta; line 62,
    channel-isolation PASS).
  - "Defaut 1" section, "Trois recoupements quantitatifs independants" (lines 573-583).
  - "Defaut 4" section (lines 267-332, Step-6 calibration bias, OPEN).
  - "Defaut 5" section, "Question ouverte" (lines 441-447, Leg-2 gas-reporting comparability, OPEN).
  - "C-bis" section (lines 689-701, IDF md5 table).
- `Leg3_4-split/Step8_docs/3rdJ_08D_campaign_cells.py`, lines 115-125 and 121 (IDF stock path,
  reused directly from `Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/`).
- md5 computed in this task (Bash `md5sum`) on
  `Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/{CAN_MTL,CAN_CLG}/*.idf` (4 files) and on
  `eSim_bem_utils/integration.py`, `2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/integration.py`,
  `Leg2_2-split/Step8_docs/eSim_bem_utils_3J/integration.py` (3 files) - values quoted above.
- `Leg2_2-split/improvement/2J_to_3J_improvement_implementation.md:1514` (Leg-2 final Step-8/9
  scorecard).
- `Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.md:140` (Leg-2 office EUI 172.7,
  PNNL band, PASS).
- `Leg3_4-split/Step9_docs/outputs_step9_deliverable/_PROVENANCE.md:15-19` (Leg-3 canonical Step-9
  scorecard and arm identity - read from the frozen deliverable directory only, per standing rule).

No em dashes or en dashes.

---

## Manager notes, added 2026-08-06 at review (additive; nothing above was altered)

### 1. 🔴 The additive claim is weaker than the pipeline overview states, and the manuscript must say so

The pipeline overview's KEY DESIGN DECISIONS table asserts *"Additive on Leg 2 ... residential +
office injection unchanged -> no prior figure invalidated"*
(`3rdJ_00_4split_Occupancy_Pipeline_Overview.md`, line 229). **Scored on file-level evidence, that
sentence is not currently supported.** Of the nine pipeline steps in the table above:

| Bit-identical? | steps | count |
|---|---|---|
| **Yes** (evidence located) | Step 7, and only for the base prototype geometry | **1** |
| **No** (evidence located, and it shows a change) | Steps 4, 6, 9 | **3** |
| `⚠ check source` (no file-level evidence located in this task) | Steps 1, 2, 3, 5, 8 | **5** |

**Two of the three explicit "No" rows matter for what the paper may claim.** Step 4 is a
*tolerance* gate (`ΔJS <= 0.002 bits`), which is a bounded-drift guarantee and not bit-identity.
Step 6 carries a **measured -10.51 pp** post-calibration 2030 work-presence bias against OBS2022
(Cohen's d -0.649), recorded as OPEN in `3rdJ_08_implementation_improvements.md` "Defaut 4" - four to
five times the ~2.4 pp WFH signal the campaign exists to detect.

**Manager decision.** The additive claim is **rewritten, not dropped, and not upgraded.** The
manuscript may claim exactly this, and no more:

> Leg-3 is additive **by construction** - a missing channel falls back to the NECB baseline, retail is
> written to a separate CSV rather than into the residential/office columns, and Leg-3's campaign reads
> **the same four prototype IDF files Leg-2 used, byte for byte** (md5s in the Step 7 row, recomputed
> independently at review on disk, all four confirmed). What has **not** been demonstrated is
> **bit-identity of the residential and office outputs across the two legs**; five of nine steps carry
> no cross-leg byte comparison at all, and the residential injector `integration.py` exists in three
> non-matching copies (`9f886fb9427e6bbc4adb7599cbcf3600` live repo, `537183b443846adeb20a0fc191c32159`
> 2J snapshot, `6a92268be1f8dc3301df3bec80d6dd2e` Leg-2 snapshot - all three recomputed at review).

**Recorded reason.** *Additive by construction* is a design property this project can evidence.
*No prior figure invalidated* is an empirical claim about two legs' outputs, and running the
comparison that would settle it needs a simulation, which this writing phase forbids. Stating the
weaker claim costs the paper nothing it can defend and removes a sentence a reviewer can falsify with
one diff. **The band and gate rule (R1) is untouched here: nothing was widened, and no verdict moved.**

**Written reopen trigger.** If a future authorised round runs a cross-leg byte or column comparison
of the Leg-2 and Leg-3 residential/office Step-3, Step-5 and Step-8 outputs, replace the five
`⚠ check source` cells with its result and re-score this decision - **in either direction**. A
confirming result upgrades the claim; a contradicting one is a finding in its own right.

### 2. 🔴 The Leg-2 office EUI of 172.7 in the Step 9 row is a PUBLISHED value that V4-B2 superseded

The Step 9 row cites Leg-2's published office EUI **172.7 kWh/m2/yr** from
`Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.md:140`. That citation is accurate as a
statement about what was *published*, and it stays. But the value itself was **recomputed on
2026-08-06 by `V4-B2` and is superseded**:

- corrected office median **106.56 kWh/m2/yr** (`improvements/v4/V4-B2_corrected.md`, lines 47 and 111;
  `improvements/v4/v4_b2_office_corrected.json`, `"corrected_median": 106.56` against
  `"published": 172.7`), the four corrected values being **106.56 / 106.66 / 106.71 / 106.56**.
- The **verdict does not change**: [100, 200] band, **IN before and IN after**. No gate moved.
- V4-B2 explicitly forbids re-deriving the corrected values by scaling the published ones
  (`V4-B2_corrected.md`, lines 228-229).

**Rule for the manuscript.** Any 3J sentence that quotes a Leg-2 or 2J EUI **magnitude** uses the
corrected value; the published figure appears only where the sentence is *about* the publication
history. This is the same hazard brief §1.2 raises for the 2J residential Table 5, applied to the
office channel. It also reinforces the Step 9 row's own unresolved caveat: whether Leg-2's office
figure is electricity-only while Leg-3's is all-fuel is **still open** ("Defaut 5"), so the two are
not yet known to share a basis and **must not be differenced in the prose**.
