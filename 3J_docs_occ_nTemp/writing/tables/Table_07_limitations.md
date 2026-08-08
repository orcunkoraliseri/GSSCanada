# Table 7 - Limitations (transcribed from the consolidated section)

*Transcribed, not rewritten, from `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md` §
"LIMITATIONS - CONSOLIDATED" (written 2026-08-05). Sixteen items, fifteen carry a number;
L15 carries none and is marked accordingly rather than given an invented figure. Wording is trimmed to
fit a table cell; no number or verdict is paraphrased.*

| ID | Group | Statement | Bounding measurement |
|---|---|---|---|
| L1 | A Frame | Hotel guests are outside the GSS frame by construction; the channel is driven by a non-GSS tourism series (Step 6C), not by time-use data. | GSS observes **0 %** of hotel occupancy. Consequence: the "one longitudinal TUS source to four channels" contribution is really **3 of 4 channels TUS-driven, 1 of 4 series-driven**. |
| L2 | A Frame | Retail sees customers only; staff are excluded by construction (GSS logs retail workers as `AT_WORK`, not shopping). | **0 %** of retail staff presence enters the occupancy signal; **0 %** of retail plug load is modulated by it (plug follows staff, staff stay on the NECB baseline). |
| L3 | A Frame | Residential intra-household presence diversity is partial, not complete; the stronger claim once made internally, that it is exactly zero, is falsified by this measurement. | **3,499 of 16,367** multi-person households (**21.38 %**) carry at least one slot value outside `{0, 0.5, 1}`. Surviving defect: Step 5 computes a household **maximum** that Step 7 never reads; aggregation is the **mean** (V2-B5). |
| L4 | B Reference bands | The office band's floor is contested and unsourced; the gate is a band-applicability finding, not a model defect. | Uninjected `Default_NECB` control scores **85.45** against a floor of **100** - fails by **15 %** before this work touches it. Two candidate mechanisms refuted: modelled heating share **17 %** vs band's **35-45 %**; rebasing on service/MEP moves **56 of 56** cells *down*. Source document gives three different floors for itself (Table 7.1 = 100.0; line 21 = 80-140; Table 2.1 = 85.0-115.0). Value not moved to make the gate pass. |
| L5 | B Reference bands | The hotel band is archetype- and city-mismatched, and that is stated rather than absorbed; our tower is NECB-2017 Montreal/Calgary, the reference is DOE/PNNL Large Hotel at ASHRAE 90.1-2019. | Reference: **284.44** kWh/m2*yr (Rochester MN, CZ 6A) / **299.28** (International Falls MN, CZ 7), read first-party from the prototype's own packaged table. Gate FAILs on **28 of 56** cells, all `Tall`, every one **OVER the 300 ceiling**; deliverable range **203.33-318.42** (corrected 2026-08-06, V4-A4, read from `outputs_step9_deliverable/`, not the superseded `outputs_step9/` which inverted the direction). Vintage-matched value (90.1-2004 lineage, 302.21) is only **1.0 %** away; the archetype/city gap remains and is recorded, not converted to a tolerance. |
| L6 | B Reference bands | The "stacked channel" explanation for low EUIs (a mid-tower channel has little roof/ground/facade load, so a low EUI is expected) was tested and REFUTED; do not cite it. | Wrong in sign and order in **56 of 56** cells: hotel is the *least*-exposed of the three banded channels and sits *closest* to its floor, not furthest. Second bound: geometry varies only `Tall`/`SuperTall`, so `exposure_ratio` takes **2** distinct values per channel, not 56 independent ones. Gate `S9-EUI-EXPOSURE` is INFO, never PASS/FAIL. |
| L7 | B Reference bands | The retail channel is validated on SHAPE, not on LEVEL; no population-denominated in-store presence reference exists at time-of-day resolution in ATUS, HETUS or the UK TUS. | EUI gate rule is **median-in-band**, not 56-of-56, because the spread is smaller than the quantity's own uncertainty: a single re-run moved the median by **-0.05 %** and flipped a cell. Retail median is **75.63** against a floor of **80**, i.e. **5.47 % below**, with **44 of 56** cells under. Rate gate demoted to INFO: BLS ATUS A-3B says retail runs ~44 % *high*, the previous band said 24.5 % *low* - references disagree in direction. |
| L8 | B Reference bands | The residential channel has no as-modelled band at all; SHEU-2019 HighRise is carried as context only and is never a PASS criterion, because a channel inside a mixed-use tower is not the stock basis SHEU sampled. | SHEU-2019 HighRise: **130.6 [113.9-147.2]** kWh/m2*yr, context only, `lo=None` in `BENCH["residential"]`. |
| L9 | C Internal gains | Retail runs on NECB's OFFICE occupant density, not NECB's own retail figure. | Model uses **24.97 m2/person** (**3.72 occ/1000 ft2**, NECB `WholeBuilding` Office); NECB `Retail - sales` is **3.10 occ/1000 ft2 = 29.97 m2/person** - retail modelled roughly **20 % over-crowded**. (An earlier alleged **6.8x** density error was retired 2026-08-05: `25.0 / 3.7 = 6.76` is the unit-conversion factor between m2/person and occ/1000 ft2, the same number written two ways, not two numbers.) |
| L10 | C Internal gains | Equipment power density is a single blanket value, while lighting is differentiated per space type. | **7.5028 W/m2** on **every** space type in **both** towers. Occupancy and plug load are the two internal-gain fields never parameterised. |
| L11 | C Internal gains | The retail occupancy peak of 0.95 has no source, and NECB's real retail schedule (type C) was never loaded. | NECB retail (type C): weekday peak **0.80 at 16:00**, no midday dip, Saturday **0.90**, Sunday **0.40**. Our tower carries NECB office (type A) byte for byte (peaks **0.90** with a **0.50** lunch dip). Injector applies **0.95** - retail runs **18.75 %** hot at peak on the wrong-shaped curve; `grep -c "NECB-C-" injected.idf` returns **0**. |
| L12 | D Method conventions | `MIN_POOL = 15` is an analyst judgement call and is presented as one; no numeric convention for a minimum adjustment-cell size was located in the literature. | Anchor previously cited for it gives **n = 5**, that paper's own study design, not a recommendation. Gate W1 is **non-monotonic**: FAIL at 10, PASS at 11-20, FAIL at 30 - not a selection criterion. |
| L13 | D Method conventions | Household aggregation is the MEAN, and the three legs of this project do not agree; the 2J converter, the Leg-2 converter and the Leg-3 pipeline each aggregate household presence differently. | **3 legs, 3 different implementations.** Leg 3 uses the **mean**, decided and recorded rather than inherited; verified against each leg's own code, never against another leg's prose. |
| L14 | D Method conventions | The retail episode-time share DECLINES across cycles; the earlier "stable" claim was a documentation defect. | Measured **2.00 % -> 2.14 % -> 1.66 % -> 1.50 %** across the four cycles, a **-25 %** decline, which ATUS, UK TUS and HETUS all confirm is internationally normal. Superseded text read "~2.1-2.3 %, stable across cycles". |
| L15 | E Physical model | Ground-level EPW on a supertall; this is the one item here with NO bounding measurement. | **Not quantified.** No altitudinal temperature or wind-speed gradient is represented over a tower of this height; it would take either a vertical weather profile or an instrumented tall building, and this work has neither. Listed with an explicit "not quantified" rather than a plausible-sounding guess. |
| L16 | E Physical model | The hotel DHW plant is capacity-pinned on a single object, and a global fix does not fix it. | `LAUNDRY` slope **-0.98** in both arms (`E ∝ V^0.02`) - delivered energy almost completely insensitive to draw volume. Raising a global K to 6 made every other heater's slope exactly **0.000** and moved `LAUNDRY`'s share of hotel DHW from **26.7 %** to **65.4 %**; share-reweighting alone reproduces the resulting **0.334** elasticity. Correct instrument: per-object resize (`LAUNDRY` alone at K ~ 7 against internal `BOOSTER` reference of 71.34 K, other fifteen heaters at K = 1). |

## Sources

`Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md`, section "LIMITATIONS - CONSOLIDATED"
(heading at line 605):

- L1: lines 623-630
- L2: lines 632-637
- L3: lines 639-645
- L4: lines 651-659
- L5: lines 661-674 (core statement and count/range), plus the same-topic decomposition and
  V4-A1/V4-A4 evidence at lines 678-745
- L6: lines 746-755
- L7: lines 757-765
- L8: lines 767-770
- L9: lines 776-784
- L10: lines 786-789
- L11: lines 791-798
- L12: lines 804-808
- L13: lines 810-815
- L14: lines 817-820
- L15: lines 826-832
- L16: lines 834-841

Group headers as transcribed: "A. Frame - what the source data can and cannot see" (line 621),
"B. Reference bands - what \"plausible\" is being measured against" (line 649), "C. Internal-gain
inputs that were never parameterised" (line 774), "D. Method conventions that are judgement, not
derivation" (line 802), "E. Physical model" (line 824).

## Discrepancy flagged to the manager

`writing/implementation/3rd_Occ_Journal_BuildInstructions.md` §1.1 (lines 82-85) summarises L7 as
"the gate was turning on **0.15 % of its floor**". The consolidated LIMITATIONS section's own L7
(lines 757-765) does not state a 0.15 % figure at all: it states a **-0.05 %** re-run move that
flipped one cell, and a final measurement of **retail median 75.4 vs floor 80, i.e. 5.7 % below**,
with 44 of 56 cells under. The "0.15 %" figure does appear elsewhere in the same document, at line
453, inside an earlier quoted V2-B3 decision block ("the retail gate was turning on 0.15 % of its
floor" as the rationale for choosing median-in-band over all-cells), which is a different location
and a different point in time from the consolidated L7 write-up. Table 7 above transcribes the
consolidated section's own L7 numbers (-0.05 %, 75.4, 80, 5.7 %, 44/56) per the task's transcription
rule, and does not carry the brief's "0.15 %" figure forward, since that number is not present in the
source section this table is required to transcribe. L4 (85.45 vs floor 100) and L5 (28/56 above the
300 ceiling, range 203.33-318.42) both match the brief's summary numbers exactly; no discrepancy found
there.

## Manager notes, added 2026-08-06 at review (additive; nothing above was altered)

### 1. The source numbers L8 twice, and this table follows the source's own count

Enumerating the bold `**L<n> - ...**` headings between lines 605 and 853 of the source returns
**seventeen** statements, and the ID **`L8` is used twice**:

- line **678** - "L8 - The three EUI failures are three different findings, and only one of them is
  about the occupancy model." Dated in its own text to 2026-08-06 (V4-A2/A3, re-derived by V4-A4).
- line **767** - "L8 - The residential channel has no as-modelled band at all."

Two readers reached this independently (the transcribing employee, and the manager reading the source
directly). The reconciliation adopted here is the employee's: the line-678 block is carried as the
**decomposition and evidence continuing L4/L5**, not as a seventeenth item, and it is cited that way
in the Sources list above. That is the only reading under which the section's own declared group span
(**B = L4 to L8, five items**) and its own self-check (**"Every limitation names its evidence -
16 / 16"**, line 849) are both true.

**Recorded reason.** The section was written 2026-08-05 with sixteen items; the line-678 block is
dated 2026-08-06 and was inserted the next day onto an ID that was already in use. Nothing is deleted
by this reading: the block's full content is transcribed into L5's row and cited by line range, so a
reader loses no statement and no number.

**Written reopen trigger.** If the canonical source is ever renumbered, or if the line-678 block is
given its own ID, this table must be rebuilt at seventeen rows and every "sixteen limitations"
sentence in the manuscript, in the pipeline overview and in the build brief must be re-counted from
the headings rather than from prose. **Until that happens, no manuscript sentence may claim the count
was verified - it is the source's own count, adopted, with a known ID collision underneath it.**

### 2. L7's retail median predates the frozen deliverable; Table 5 uses the deliverable

L7 as transcribed states **retail median 75.4 against a floor of 80, i.e. 5.7 % below** (evidence:
"V2-D4 measurement"). Re-derived from the 56 retail CFA values in the frozen deliverable
`outputs_step9_deliverable/step9_eui_by_channel.csv`, the median is **75.626, i.e. 5.47 % below the
80 floor**, with **44 of 56** cells under the floor.

The **44/56 tally and the FAIL verdict are identical** on both; only the median's third significant
figure moves. **Table 7 keeps L7's own wording because this table is a transcription. Table 5 uses
the deliverable value, because that table reports measurements.** They are not in conflict; they are
two different jobs. No band moved and no verdict changed either way.

### 3. The brief's "0.15 % of its floor" is a decision margin, not a distance from the floor

Confirmed against the source at line 453: the 0.15 % figure is the margin on which the **retired
all-cells rule** was turning, which is why a -0.05 % median shift in the V2-E3 arm flipped a cell. It
is **not** the gap between the retail median and its floor (that gap is 5.47 %). An early draft of
Table 5 conflated the two and was corrected before closure.

### 4. L7's retail median corrected 75.4 to 75.63, found by the R1 read-through

**Corrected 2026-08-06 night.** L7 stated the retail median as **75.4** against the 80 floor,
**5.7 % below**. Chapter 5, the Abstract and the Discussion all stated **75.63** and **5.47 %** for the
same quantity. Both pairs are internally consistent arithmetic, which is exactly why neither side
looked wrong on its own; they were only wrong **relative to each other**, and no check in this project
compares a number in one chapter against the same number in another.

**Re-derived from the frozen deliverable at the point of correction**, not from either document:
`outputs_step9_deliverable/step9_eui_by_channel.csv`, 56 retail rows, `eui_CFA_kWh_m2`
**median = 75.6260**, range 63.63 to 96.84, giving **(80 - 75.6260) / 80 = 5.4675 %** below the floor.
75.4 appears nowhere in the CSV on either basis (the GFA-share median is 73.2736). **75.63 is correct
and 75.4 is a stale pre-deliverable carry-over.** Chapter 7 and this table are corrected to 75.63 /
5.47 %; predecessors archived as `*.2026-08-06_pre_retail_median_fix.md`.

🔴 **No band moved and no verdict changed** by this correction: retail was below its floor at 75.4 and
is below its floor at 75.63, the gate stays FAIL, and 44 of 56 cells stay under. *The finding is not
that the number mattered to the verdict. It is that the manuscript stated two different values for
its own headline retail result, and it took a reader going end to end to see it.*

*Reopen trigger:* any re-run of Step 9 that changes `step9_eui_by_channel.csv` requires this median to
be re-derived and both locations updated together.

### 5. L8's residential central 130.6 is the midpoint of its own range, and Table 5 refuses to state it

**Flagged 2026-08-06 night by the R1 read-through, not corrected, because correcting it would break
this table's transcription contract.**

L8 above carries **130.6 [113.9-147.2]** for the SHEU-2019 HighRise context band. Three facts, each
checked at the point of writing:

1. The source document does state it: `3rdJ_00_4split_Occupancy_Pipeline.md:768`. This table
   transcribes the source, so the cell is a faithful transcription and is **left as it stands**.
2. **`130.6` appears nowhere in the frozen deliverable CSV**, on either basis. The residential rows
   carry `info_lo = 113.9` and `info_hi = 147.2` and **there is no `info_central` column at all**.
3. **(113.9 + 147.2) / 2 = 130.55**, which is 130.6 to one decimal. The value is the arithmetic
   midpoint of its own range.

🔴 **This puts the manuscript in contradiction with itself.** Table 5 leaves the residential
empirical-band central cell marked `n/r` and says so explicitly, *because `info_central` is not a
column in the deliverable CSV and a midpoint was not invented*. Table 7 then prints the midpoint for
the same quantity. **One of the two documents is wrong about whether that number exists**, and it is
not decidable from inside this project: only SHEU-2019 itself can say whether 130.6 is a reported
central value that happens to sit at the midpoint, or a midpoint somebody computed and wrote down.

Operationally it changes nothing: the residential band is **context only and never a PASS criterion**,
so no gate depends on it. It is recorded because a number that is exactly the midpoint of its own
range, absent from the data file, and explicitly declined by a sibling table, is the shape of an
invented figure.

*Reopen trigger:* if SHEU-2019 is opened and reports a central value, record it with its source and
this note closes. If it reports only a range, **130.6 must be struck from L8** and the cell brought
into line with Table 5.
