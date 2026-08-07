# 3 Methods

Each pipeline stage is presented with its design rationale and its validation result. Residential and
Office reuse the two-channel construction stage (Leg-2) without change to their harmonization,
architecture, or linkage logic; that stage is described here only where its output is a direct input to
the two new channels, or where one of its lessons became a hard gate carried into this paper. The
complete gate set referenced throughout this chapter is given in Table 4, with each threshold's
provenance (ASHRAE Guideline 14, project-chosen, or heuristic) marked explicitly there rather than
repeated in prose.

---

### 3.1 Harmonization and the AT_RETAIL Derivation

Residential and Office harmonization - the mapping of raw cycle-specific activity and location codes to
a shared vocabulary, and the tiling of each diary onto the 48-slot, 30-minute grid - is unchanged from
the two-channel construction stage and is not restated here. The one harmonization addition made for
this paper is the derivation of the Retail channel, AT_RETAIL, from columns the survey already carries
in every cycle: `occPRE` (location) and `occACT` (activity). No new GSS variable was collected or coded
for this addition.

The derivation rule, frozen 2026-07-02 (decision OD-1), is:

```
AT_RETAIL = (occPRE == 5) | ((occACT == 4) & occPRE in {5, 9})
```

The activity arm (`occACT == 4`, "Purchasing Goods & Services") is deliberately gated to
`occPRE in {5, 9}` to exclude a specific wrinkle: `occACT == 4 & occPRE == 1` records purchasing
conducted from the respondent's own home (online shopping), which is not retail-space presence and must
not be counted as such. This exclusion is not merely asserted; the online-shopping leak cross-tab is
recomputed and reported for every GSS cycle as a standing verification check, even though the rule
itself is not reopened by that check. The location-mapping detail differs by cycle, because the
underlying `PLACE`/`LOCATION` coding scheme changed across GSS redesigns: 2005 and 2010 use
`PLACE = 06 + 07`; 2015 uses `LOCATION = 306`; 2022 uses `LOCATION = 3306`. In both 2015 and 2022 the
grocery and general-merchandise shopping locations are collapsed into a single bucket, so the two cannot
be separated for those cycles (Table 2, footnote 1).

The merge step that appends AT_RETAIL to the diary record is the one place the GSS build pipeline itself
changes for this paper: the tiler that produces the 30-minute channel columns was already list-driven in
the two-channel construction stage, so adding Retail is one additional list entry rather than a new
tiling procedure. Retail is written to its own CSV file rather than into the existing residential/office
output, specifically so the addition cannot overwrite or reshape the two reused channels' columns.

Restaurant presence (`occPRE == 7`) is available in every cycle and was considered as a candidate fifth
channel; it is explicitly out of scope for this paper because no prototype Space in the Tall/SuperTall
towers corresponds to a restaurant use.

---

### 3.2 The Three-Head Transformer

The conditional generator used to synthesize unobserved day-types for the three GSS-derived channels is
grown directly from the two-channel construction stage's architecture, not designed from scratch. The
shared encoder is unchanged; the decoder side gains one head. The decoder therefore carries three heads
in total: Head 1 (Residential presence), Head 2 (AT_WORK / Office), and Head 3 (AT_RETAIL / Retail, the
one addition for this paper). Hotel has no head and never passes through this model at all; it is
produced by an entirely separate side-track described in §3.4.

The three heads are trained under fixed-weight scalarization with loss weights 1.0 : 0.5 : 0.3
(Residential : Office : Retail) combined with PCGrad pairwise gradient-conflict correction. This
combination was selected over dynamic loss-balancing schemes (SLAW, uncertainty weighting) because those
schemes proved unstable on the approximately 2%-positive Retail task; fixed weights tuned before
training matched or beat the dynamic alternatives at this task count. Retail's rarity is addressed with
a binary cross-entropy loss at `pos_weight = 49`, corrected at inference by subtracting the corresponding
`-ln 49` logit shift so that the class-imbalance correction does not distort the decoded probability
scale. Training proceeds as a 5-epoch head-only warmup followed by 15 epochs of joint fine-tuning with
PCGrad active throughout the joint phase. Decoding uses temperature T = 0.7 with a minimum-dwell
constraint of two consecutive slots, and per-head decision thresholds of 0.50 (Residential), 0.40
(Office), and 0.15 (Retail) - the lower Retail threshold reflecting its lower base rate.

CYCLE_YEAR is encoded as a continuous conditioning value rather than a categorical one, so that the
model remains usable for the 2030 forecast year without retraining on a held-out category (§3.4).

Because independent binary heads can jointly predict a respondent as present in more than one channel
at the same slot, the raw decoder output is passed through a decode-time, threshold-normalized argmax
projection that enforces mutual exclusivity across the three channels before the output is used
downstream. Table 4 reports this as the Impossible-State Rate (ISR) gate: raw ISR must fall at or below
0.5%, and the projected ISR must reach exactly 0%. A categorical softmax alternative was considered and
rejected, because it would crush the roughly 2%-positive Retail class and would also break bit-compatible
continuity with the two-channel construction stage's own Head-1/Head-2 outputs; the chosen
projection-after-independent-heads design preserves per-head calibration while still guaranteeing
one-channel-at-a-time occupancy.

Residential and Office are not left to drift freely as the third head is added: a regression gate
(Table 4) bounds how far the two reused heads' output may move relative to the two-channel construction
stage's own validation baseline, expressed as a Jensen-Shannon divergence tolerance rather than as a
bit-identity requirement.

**Checkpoint selection, and a disclosed deviation between the specification and the shipped artefact.**
The specified selection rule is gate-first then lexicographic: discard every checkpoint that fails any
hard gate, then maximize Retail F1 among the survivors, with no composite score at any stage. The
prohibition on composites is not stylistic. It is a finding carried forward from the first leg of this
project, where a composite score selected a model that passed only two of four gates, and it is
recorded as a standing principle in the two-channel stage's own pipeline document. **The shipped
weights were nevertheless not selected by that rule.** The training driver checkpoints on
`val_score = mean_js + 0.5 x (home_gap + work_gap + retail_gap) / 3`, a composite that contains
neither PR-AUC nor F1. The two rules select different epochs in four of five seeds. The shipped seed
ranks first of five on the composite and fourth of five on the metric the specification names, and it
sits 0.0218 Retail F1 below the specified rule's winner, which is 5.6 % in relative terms and 0.16
standard deviations of the cross-seed spread.

Three things are stated rather than smoothed over. First, the specification is not amended to describe
what the code does, because rewriting the rule at the moment it becomes inconvenient would delete the
principle that motivates it. Second, the reason for not re-selecting is evidential rather than
economic: both rules rank epochs on teacher-forced validation columns, and a separate person-level
probe established that those columns are blind to person-level Retail skill, so re-selecting would buy
0.0218 of a statistic already shown not to measure the quantity of interest. Third, the specified rule
was never implementable as written on this data. Two of its five hard-gate families are pool-level
quantities, computable only after inference and raking, and absent from every column of the training
log; and on the observed range the gate clause is inert in any case, since the worst epoch of the run
clears PR-AUC 0.518 against a bar of 0.15, F1 0.282 against 0.25, and raw ISR 0.014 % against 0.5 %,
so gate-first then argmax reduces to global argmax F1. A reader who wishes to re-implement the
specified rule must first make its first clause affordable or drop it explicitly.

---

### 3.3 Linkage and the Population-Level Retail/Hotel Fallbacks

Residential linkage (household matching via the Census PUMF) and Office linkage (workforce matching via
NOC-by-NAICS crosswalks) are unchanged from the two-channel construction stage; the mechanics of both
are not restated here.

Retail and Hotel do not receive a respondent-level linkage at all, for two different reasons that both
resolve to the same population-level fallback design. Retail cannot be linked to a specific archetype at
finer resolution than a single population fraction, because the grocery/merchandise location split
needed to place a respondent against a particular retail sub-type is not recoverable from the 2015/2022
GSS coding (§3.1); the channel is therefore driven by a single PNNL "Retail Retail" archetype applied as
a population-level fraction rather than as a per-household lookup. Hotel cannot be linked to any
respondent at all, because hotel guests are outside the GSS sampling frame by construction (Chapter 2,
§2.3); the channel is therefore driven by a province-level multiplier (Quebec or Alberta) rather than by
any individual archetype record. Both fallbacks are additive-safe in the same sense used elsewhere in
this pipeline: a channel with no per-respondent linkage available falls back to a population- or
province-level signal rather than to a missing value.

---

### 3.4 Forecasting and the Hotel SARIMA Side-Track

Residential and Office are forecast to 2030 by the same reused mechanism as the two-channel construction
stage: progressive fine-tuning across the GSS cycle chain (2005 to 2010 to 2015 to 2022) with weight
inheritance, plus the same demographic drift-matrix accounting. Retail reuses this same GSS chain for its
generative-model output, and layers a separate scenario lever on top: three named 2030 in-store-share
bands (0.97 plateau/resilient-central default, 0.90 continued-shift, 1.05 in-store-renaissance), applied
before the peak-normalization step described in §3.5, plus a QC-Sunday sub-axis reflecting Quebec's
distinct regulated Sunday retail hours.

Hotel is forecast by a side-track that bypasses the three-head Transformer entirely, because it has no
respondent-level structure for that model to condition on. The monthly ISQ (Quebec) and CBRE (Alberta)
occupancy-rate series (Chapter 2, §2.3) are each fit with a SARIMA(1,1,1)(1,1,1,12) model per province,
with an explicit COVID-19 indicator covering March 2020 through June 2022 so that the pandemic-era
occupancy collapse does not bias the fitted seasonal structure. The fitted model produces a monthly
occupancy-rate forecast that is converted into a half-hourly multiplier by:

```
hotel_multiplier(t, month, PR) = s(t) x monthly_rate(month, PR)
```

where `s(t)` is a unit-normalized, 48-slot guest-room diurnal shape common to both provinces: an
overnight plateau at 1.00 from 22:00 to 06:00, and a day trough of 0.200 on weekdays versus 0.308 on
weekends. The side-track's own backcast validation gate (Table 4) requires QC and AB monthly
reconstructions for 2015-2019 to reach a mean absolute error below 0.05, and requires the 2020-04
COVID-dip reconstruction to recover without overshoot. The 2030 forecast is expressed as three named
bands (0.92, 1.00, 1.05) around the central SARIMA projection, mirroring the scenario-lever pattern used
for the Office WFH band and the Retail in-store-share band (§3.5, §4).

---

### 3.5 Tag-2 Dispatch and Modulate-vs-Replace

Injection into the building energy model is dispatched per Space using the IDF `Tag 2` field as an
exact-match routing key, because the PNNL Tall/SuperTall prototypes leave the standard EnergyPlus Space
Type field blank. Four dispatch outcomes follow from the tag match, and they are not interchangeable:

- **Apartment tags -> Residential, REPLACE.** The code default `People` schedule is fully substituted by
  the modelled schedule (`Number_of_People` driven by household size). Replacement is appropriate here
  because residential occupancy is per-household, not a code-density baseline to be adjusted.
- **Office tags -> Office, MODULATE.** The NECB office occupant density is multiplied by the modelled
  AT_WORK fraction over time, preserving the code-of-record peak density while injecting the temporal
  signal.
- **Retail tags -> Retail, MODULATE.** Customer presence is injected as `People = 0.95 x
  peak-normalized shape_cd(t)` during customer hours; slots identified as staff-only (baseline occupancy
  at or below 0.10) are left on the NECB baseline rather than modulated, consistent with Retail modelling
  customer presence only (§2.1, Table 2 footnote 2). The occupant density used for this Space type is the
  NECB office value (24.97 m2/person) rather than NECB's own Retail-Sales value (29.97 m2/person); this
  is documented as a limitation, not corrected in this paper, because it is a code-density input, not an
  occupancy-schedule question, and correcting it is outside this paper's scope.
- **Guest-room tags -> Hotel, MODULATE.** The NECB guest-room schedule is multiplied by
  `hotel_multiplier(t, month, PR)` from §3.4.
- **Amenity and service/MEP tags -> untouched NECB baseline.** No occupant-driven channel is defined for
  these Space types, so the code default is left in place.
- **Missing channel -> NECB fallback.** Any Space whose tag does not resolve to one of the four channels
  falls back to the untouched NECB default, the same additive-safe behaviour used for the Retail/Hotel
  linkage fallbacks in §3.3.

A hard wiring gate is asserted after every injection, and its origin is a defect found in the two-channel
construction stage, not in this paper's own new code. In that construction stage, a modulated People
schedule was referenced by the field `Schedule_Name` rather than the field the `People` object actually
consumes at simulation time, `Number_of_People_Schedule_Name`. Because the misreferenced field still
existed and still held a syntactically valid schedule, every input-side check available at the time -
schedule presence, schedule syntax, field non-emptiness - passed cleanly; the defect flattened the Office
channel's temporal signal and was caught only when Office simulation output failed to differ from an
unmodulated baseline, an output-side observation. The post-injection gate that now asserts the correct
field on 100% of modulated Spaces (Table 4, Wiring row) closes that specific input-side blind spot. But
an input-side assertion, however strict, is still an input-side check, and the defect that motivated it
was caught only on the output side; this is why the campaign design in Chapter 4 additionally makes two
output-side probes mandatory before any Leg-3 campaign cell is accepted, rather than leaving output-side
verification to good practice. The wiring defect and the gates it motivated are a methods contribution
carried forward from the two-channel construction stage into this paper's validation design; the
construction stage itself does not receive a results narrative here.

---

### 3.6 End-Use Loads

Activity-driven equipment and lighting loads follow channel-specific rules rather than one shared rule
across all four uses, because the four uses do not share an occupancy semantics. For Retail, lighting and
HVAC-relevant schedules follow the Space's opening hours rather than the customer-presence signal itself,
plug load follows the staff schedule (and therefore stays on the NECB baseline, consistent with §3.5),
and customer presence modulates only the People-driven internal gain; minimum lighting and baseline plug
floors (`Lmin`, `Pbase`) are enforced so that an empty-of-customers slot during opening hours is not
modelled as a fully unlit, unpowered space. For Hotel, guest-room loads are modulated by the same `s(t)`
diurnal shape and monthly amplitude used for occupancy (§3.4), while amenity-zone loads remain on the
NECB baseline, matching the amenity-zone occupancy treatment in §3.5.

The activity-driven end-use layer is calibrated against the NRCan Survey of Commercial and Institutional
Energy Use (SCIEU), the commercial analogue of the residential SHEU anchoring used in the two-channel
construction stage and in the authors' residential-only prior work.

---

## Sources (this chapter)

- `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md`: STEP 1-2 box (AT_RETAIL derivation,
  no-new-GSS-variable statement), STEP 3 box (list-driven tiler, separate retail CSV), STEP 4 box
  (three-head Transformer design, loss weights, PCGrad, pos_weight, decode thresholds), STEP 5 box
  (linkage reuse, retail/hotel population-level fallbacks), STEP 6 box (2030 forecast chain, retail
  lever bands, hotel SARIMA side-track and `hotel_multiplier` formula), STEP 7 box (Tag-2 dispatch,
  REPLACE/MODULATE assignment, the wiring gate), STEP 9 box (retail/hotel end-use rules, SCIEU
  calibration); `## VALIDATION GATES` and `## KEY DESIGN DECISIONS SUMMARY` sections (gate provenance,
  wiring + differentiation gate rationale); `## OPEN DECISIONS` items 1, 4, 10, 11, 14, 15 (AT_RETAIL
  OR-rule freeze, hotel diurnal shape, training regimen, retail multiplier normalization, output
  representation, training playbook).
- `writing/tables/Table_02_channels.md` - channel provenance, derivation, injection mode, scenario
  lever, and the AT_RETAIL / retail-staff footnotes.
- `writing/tables/Table_04_validation_gates.md` - full gate set and threshold provenance
  classification.

No em dashes or en dashes.

---

**Table 6.** *(insert `Table_06_leg2_leg3_delta.md` here)*

