# Table 6 - What Leg-3 added (the additive ledger)

This table carries the paper's additive claim, and it carries the limits of that claim in the same
place. A Bit-identical? = Yes cell is entered only where file-level evidence was located, meaning
a shared file path or a hash computed directly on the files themselves, and never from a design
document's own prose. Where no such evidence exists, the verdict cell reads `⚠ check source` and the
basis cell says plainly what was not compared. An unexamined step is reported as unexamined, which is
a result about the strength of the claim rather than a gap to be filled with an assumption.

| Pipeline step | Two-channel stage artefact | Four-channel change | Bit-identical? | Basis for the verdict |
|---|---|---|---|---|
| Step 1 - Data collection | Survey column selection for residential and office | A non-survey hotel ingest of the provincial monthly series is added; retail needs no new survey variable | ⚠ check source | Nothing was compared. The collection scripts differ in name, and no byte- or column-level comparison of their output was run |
| Step 2 - Data harmonization | Crosswalk and OR-rule for residential and office | A hotel harmonization step is added, plus the retail OR-rule frozen 2026-07-02 (Table 2, footnote 1) | ⚠ check source | Nothing was compared, as at Step 1 |
| Step 3 - Merge and tiling | List-driven tiler producing 30-minute residential and office output | One added list entry for retail, written to a separate file so it cannot reshape the reused columns | ⚠ check source | Design intent only. The separate-file arrangement was never tested against the tiler's own output, and a statement about a program is not evidence about what it wrote |
| Step 4 - Three-head Transformer | Two-head Transformer, residential and office presence | A third head for retail; the backbone is kept with targeted upgrades rather than frozen and copied | No | The governing gate is a tolerance, bounding drift at 0.002 bits of Jensen-Shannon divergence, which is not bit-identity. The measured drift was not located and is left unreported |
| Step 5 - Archetype linkage | Residential dwelling-stock and office workforce linkage | Retail is driven by one archetype as a population-level fraction, hotel by a province-level multiplier | ⚠ check source | Documented as carried over unchanged, but no file- or column-level comparison across the two stages was run |
| Step 6 - Forecast to 2030 and the hotel side-track | Survey-cycle raking chain, demographic drift matrix, office work-from-home bands | The raking chain is reused; a retail lever and the hotel SARIMA side-track are added | No | The measured level has moved. Post-calibration 2030 work presence sits 10.51 percentage points below observed 2022 (Cohen's d -0.649), four to five times the roughly 2.4 percentage-point signal the campaign exists to detect |
| Step 7 - Building-model integration | Two-channel tag-based injection into the tower prototypes | Four-channel exact-match dispatch, a missing channel falling back to the code baseline | Yes, base prototype geometry only | Both campaigns read the same four prototype model files, all confirmed byte-identical by hash at review. That covers geometry only: the injector exists in three non-matching copies, so the building is shared and the code writing into it is not |
| Step 8 - Building simulation | 72-run residential re-simulation plus the office campaign | The 56-cell campaign, all four channels injected per cell | ⚠ check source | Channel isolation was demonstrated inside this study's own campaign, by simulation rather than by inference. The two stages' outputs were never compared |
| Step 9 - Activity-driven end-use loads | Two-channel end-use validation against survey and prototype references | Four-channel validation over thirty gates, three left failing on purpose (Table 5) | No | Different gate sets, and possibly a different basis: whether the earlier office figure counts electricity only is open in that stage's own record, so the two cannot be differenced |

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
(`3rdJ_00_4split_Occupancy_Pipeline_Overview.md`, line 229). Scored on file-level evidence, that
sentence is not currently supported. Of the nine pipeline steps in the table above:

| Bit-identical? | steps | count |
|---|---|---|
| Yes (evidence located) | Step 7, and only for the base prototype geometry | 1 |
| No (evidence located, and it shows a change) | Steps 4, 6, 9 | 3 |
| `⚠ check source` (no file-level evidence located in this task) | Steps 1, 2, 3, 5, 8 | 5 |

Two of the three explicit "No" rows matter for what the paper may claim. Step 4 is a
*tolerance* gate (`ΔJS <= 0.002 bits`), which is a bounded-drift guarantee and not bit-identity.
Step 6 carries a measured -10.51 pp post-calibration 2030 work-presence bias against OBS2022
(Cohen's d -0.649), recorded as OPEN in `3rdJ_08_implementation_improvements.md` "Defaut 4" - four to
five times the ~2.4 pp WFH signal the campaign exists to detect.

Manager decision. The additive claim is rewritten, not dropped, and not upgraded. The
manuscript may claim exactly this, and no more:

> Leg-3 is additive by construction - a missing channel falls back to the NECB baseline, retail is
> written to a separate CSV rather than into the residential/office columns, and Leg-3's campaign reads
> the same four prototype IDF files Leg-2 used, byte for byte (md5s in the Step 7 row, recomputed
> independently at review on disk, all four confirmed). What has not been demonstrated is
> bit-identity of the residential and office outputs across the two legs; five of nine steps carry
> no cross-leg byte comparison at all, and the residential injector `integration.py` exists in three
> non-matching copies (`9f886fb9427e6bbc4adb7599cbcf3600` live repo, `537183b443846adeb20a0fc191c32159`
> 2J snapshot, `6a92268be1f8dc3301df3bec80d6dd2e` Leg-2 snapshot - all three recomputed at review).

Recorded reason. *Additive by construction* is a design property this project can evidence.
*No prior figure invalidated* is an empirical claim about two legs' outputs, and running the
comparison that would settle it needs a simulation, which this writing phase forbids. Stating the
weaker claim costs the paper nothing it can defend and removes a sentence a reviewer can falsify with
one diff. The band and gate rule (R1) is untouched here: nothing was widened, and no verdict moved.

Written reopen trigger. If a future authorised round runs a cross-leg byte or column comparison
of the Leg-2 and Leg-3 residential/office Step-3, Step-5 and Step-8 outputs, replace the five
`⚠ check source` cells with its result and re-score this decision - in either direction. A
confirming result upgrades the claim; a contradicting one is a finding in its own right.

### 2. 🔴 The Leg-2 office EUI of 172.7 in the Step 9 row is a PUBLISHED value that V4-B2 superseded

The Step 9 row cites Leg-2's published office EUI 172.7 kWh/m2/yr from
`Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.md:140`. That citation is accurate as a
statement about what was *published*, and it stays. But the value itself was recomputed on
2026-08-06 by `V4-B2` and is superseded:

- corrected office median 106.56 kWh/m2/yr (`improvements/v4/V4-B2_corrected.md`, lines 47 and 111;
  `improvements/v4/v4_b2_office_corrected.json`, `"corrected_median": 106.56` against
  `"published": 172.7`), the four corrected values being 106.56 / 106.66 / 106.71 / 106.56.
- The verdict does not change: [100, 200] band, IN before and IN after. No gate moved.
- V4-B2 explicitly forbids re-deriving the corrected values by scaling the published ones
  (`V4-B2_corrected.md`, lines 228-229).

Rule for the manuscript. Any 3J sentence that quotes a Leg-2 or 2J EUI magnitude uses the
corrected value; the published figure appears only where the sentence is *about* the publication
history. This is the same hazard brief §1.2 raises for the 2J residential Table 5, applied to the
office channel. It also reinforces the Step 9 row's own unresolved caveat: whether Leg-2's office
figure is electricity-only while Leg-3's is all-fuel is still open ("Defaut 5"), so the two are
not yet known to share a basis and must not be differenced in the prose.
