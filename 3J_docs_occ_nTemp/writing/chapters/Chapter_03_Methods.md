# 3 Methods

Each pipeline stage is presented with its design rationale and its validation result. Residential and
Office reuse the two-channel construction stage without change to their harmonization,
architecture, or linkage logic; that stage is described here only where its output is a direct input to
the two new channels, or where one of its lessons became a hard gate carried into this paper. The
complete gate set referenced throughout this chapter is given in Table 4, with each threshold's
provenance (ASHRAE Guideline 14, project-chosen, or heuristic) marked explicitly there rather than
repeated in prose.

---

### 3.1 Harmonization and the AT_RETAIL Derivation

Residential and Office harmonization, the mapping of raw cycle-specific activity and location codes to
a shared vocabulary and the tiling of each diary onto the 48-slot, 30-minute grid, is unchanged from the
two-channel construction stage and is not restated here. The one addition made for this paper is the
Retail channel, AT_RETAIL, derived from two columns the survey already carries in every cycle: occPRE
(location) and occACT (activity). No new GSS variable was collected or coded, and the rule was fixed
before any training run:

$$\mathrm{AT\_RETAIL} = (\mathrm{occPRE} = 5)\ \lor\ \left[(\mathrm{occACT} = 4)\ \land\ (\mathrm{occPRE} \in \{5,\,9\})\right]$$

The activity arm, occACT = 4 (Purchasing Goods and Services), is deliberately gated to occPRE in {5, 9}
to exclude purchasing conducted from the respondent's own home, which is online shopping rather than
retail-space presence. The exclusion is not merely asserted: the online-shopping cross-tab is recomputed
and reported for every cycle as a standing verification check, although the rule itself is not reopened
by that check. The underlying location coding changed across GSS redesigns, so the mapping differs by
cycle, and in both 2015 and 2022 the grocery and general-merchandise locations are collapsed into a
single bucket and cannot be separated. Table A2 gives the per-cycle codebook.

Appending AT_RETAIL to the diary record is the one place the GSS build pipeline itself changes for this
paper. The tiler that produces the 30-minute channel columns was already list-driven, so Retail is one
additional list entry rather than a new tiling procedure, and it is written to its own output rather
than into the existing residential and office columns, so the addition cannot overwrite or reshape the
two reused channels.

Restaurant presence (occPRE = 7) is available in every cycle and was considered as a candidate fifth
channel. It is out of scope here because no prototype Space in the Tall or SuperTall towers corresponds
to a restaurant use.

---

### 3.2 The Three-Head Transformer

The conditional generator used to synthesize unobserved day-types for the three GSS-derived channels is
grown directly from the two-channel construction stage's architecture, not designed from scratch. The
shared encoder is unchanged; the decoder side gains one head. The decoder therefore carries three heads
in total: Head 1 (Residential presence), Head 2 (AT_WORK / Office), and Head 3 (AT_RETAIL / Retail, the
one addition for this paper). Hotel has no head and never passes through this model at all; it is
produced by an entirely separate side-track described in §3.4. Figure 3 draws the resulting topology,
with the hotel side-track placed beside the encoder and connected to nothing inside it, because the
distinction between three GSS heads plus one non-GSS side-track and a four-head model is the one
reading of this architecture that must not be got wrong.

The three heads are trained under fixed-weight scalarization with loss weights 1.0 : 0.5 : 0.3
(Residential : Office : Retail) combined with PCGrad pairwise gradient-conflict correction. This
combination was selected over dynamic loss-balancing schemes (SLAW, uncertainty weighting) because those
schemes proved unstable on the approximately 2%-positive Retail task; fixed weights tuned before
training matched or beat the dynamic alternatives at this task count. Retail's rarity is addressed with
a binary cross-entropy positive-class weight of 49, corrected at inference by subtracting the
corresponding logit shift $-\ln 49$ so that the class-imbalance correction does not distort the decoded
probability scale. Training proceeds as a 5-epoch head-only warmup followed by 15 epochs of joint fine-tuning with
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
one-channel-at-a-time occupancy. Figure 4 traces one slot through that projection, from the three
independent sigmoid outputs that may conflict to the mutually exclusive decode, with the
impossible-state rate reported on both sides of it.

The complete hyperparameter set behind the paragraphs above, including the encoder fields carried
unchanged from the two-channel construction stage and the one line that could not be confirmed against
either the design document or the code, is reported as a model card in Table A1 rather than scattered
through this section.

Residential and Office are not left to drift freely as the third head is added: a regression gate
(Table 4) bounds how far the two reused heads' output may move relative to the two-channel construction
stage's own validation baseline, expressed as a Jensen-Shannon divergence tolerance rather than as a
bit-identity requirement.

Checkpoint selection carries a disclosed deviation between the specification and the shipped artefact.
The specified rule is gate-first then lexicographic: discard every checkpoint failing a hard gate, then
maximize Retail F1 among the survivors, with no composite score at any stage. The prohibition on
composites is not stylistic; it is carried forward from an earlier stage of this project, where a
composite score selected a model that passed only two of four gates. The shipped weights were
nevertheless not selected by that rule. The training driver checkpoints on a composite of the mean
Jensen-Shannon divergence and the three per-head presence-rate gaps,

$$\mathrm{val\_score} = \overline{\mathrm{JS}} + \tfrac{1}{2}\cdot\frac{g_{\mathrm{home}} + g_{\mathrm{work}} + g_{\mathrm{retail}}}{3}$$

which contains neither PR-AUC nor F1, and the two rules select different epochs in four of five seeds.
The shipped seed ranks first of five on the composite and fourth of five on the metric the specification
names, 0.0218 Retail F1 below the specified rule's winner, 5.6 % in relative terms and 0.16 standard
deviations of the cross-seed spread.

Three things are stated rather than smoothed over. The specification is not amended to describe what the
code does, because rewriting a rule at the moment it becomes inconvenient deletes the principle behind
it. The reason for not re-selecting is evidential rather than economic: both rules rank epochs on
teacher-forced validation columns, and a separate person-level probe established that those columns are
blind to person-level Retail skill. And the specified rule was never implementable as written on this
data, since two of its five hard-gate families are pool-level quantities computable only after inference
and raking; on the observed range its gate clause is inert in any case, the worst epoch clearing PR-AUC
0.518 against a bar of 0.15, F1 0.282 against 0.25, and a raw impossible-state rate of 0.014 % against
0.5 %, so gate-first then argmax reduces to global argmax F1.

---

**Figure 3.** *(insert `Figure_03_three_head_transformer.png` here)* - Three-head Transformer with hotel side-track.

**Figure 4.** *(insert `Figure_04_exclusivity_projection.png` here)* - Exclusivity projection across three channels.

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

$$m(t,\ \mathrm{month},\ \mathrm{PR}) = s(t)\times r(\mathrm{month},\ \mathrm{PR})$$

where r is the forecast monthly occupancy rate for that province and s(t) is a unit-normalized,
48-slot guest-room diurnal shape common to both provinces: an
overnight plateau at 1.00 from 22:00 to 06:00, and a day trough of 0.200 on weekdays versus 0.308 on
weekends. The side-track's own backcast validation gate (Table 4) requires QC and AB monthly
reconstructions for 2015-2019 to reach a mean absolute error below 0.05, and requires the 2020-04
COVID-dip reconstruction to recover without overshoot. The 2030 forecast is expressed as three named
bands (0.92, 1.00, 1.05) around the central SARIMA projection, mirroring the scenario-lever pattern used
for the Office WFH band and the Retail in-store-share band (§3.5, §4). Figure 5 follows the side-track
end to end, from the provincial monthly series through the SARIMA fit and its COVID indicator to the
half-hourly multiplier that reaches the guest-room schedules.

---

**Figure 5.** *(insert `Figure_05_hotel_sidetrack.png` here)* - Hotel SARIMA side-track.

---

### 3.5 Tag-2 Dispatch and Modulate-vs-Replace

Injection into the building energy model is dispatched per Space using the IDF Tag 2 field as an
exact-match routing key, because the PNNL Tall and SuperTall prototypes leave the standard EnergyPlus
Space Type field blank. Figure 6 shows the dispatch for every Space in the tower, including the branch
that matters most for the additivity claim in Chapter 6: an unrecognised tag falls back to the untouched
code baseline rather than to an undefined state.

The dispatch outcomes are not interchangeable. Apartment tags route to Residential and REPLACE the code
default occupancy schedule with the modelled one, driven by household size, which is appropriate because
residential occupancy is per-household rather than a code-density baseline to be adjusted. Office tags
route to Office and MODULATE, multiplying the NECB office occupant density by the modelled AT_WORK
fraction over time so that the code-of-record peak density is preserved while the temporal signal is
injected. Retail tags likewise MODULATE, injecting customer presence as 0.95 times a peak-normalized
customer-hours shape, while slots identified as staff-only (baseline occupancy at or below 0.10) are
left on the NECB baseline, consistent with Retail modelling customer presence only. The occupant density
used for that Space type is the NECB office value of 24.97 m2/person rather than NECB's own retail-sales
value of 29.97 m2/person; this is reported as a limitation rather than corrected here, because it is a
code-density input rather than an occupancy-schedule question. Guest-room tags MODULATE the NECB
guest-room schedule by the hotel multiplier of §3.4. Amenity and service/MEP tags carry no
occupant-driven channel and keep the code default, and any Space whose tag resolves to none of the four
channels falls back to the untouched NECB default, the same additive-safe behaviour used for the Retail
and Hotel linkage fallbacks in §3.3.

A hard wiring gate is asserted after every injection, and its origin is a defect found in the
two-channel construction stage rather than in this paper's own new code. There, a modulated occupancy
schedule was referenced by the wrong field of the People object, one that still existed and still held a
syntactically valid schedule. Every input-side check available at the time, schedule presence, schedule
syntax and field non-emptiness, therefore passed cleanly; the defect flattened the Office channel's
temporal signal and was caught only when Office simulation output failed to differ from an unmodulated
baseline. The post-injection gate that now asserts the correct field on 100 % of modulated Spaces
(Table 4) closes that blind spot. But an input-side assertion, however strict, is still an input-side
check, and the defect that motivated it was caught on the output side; this is why the campaign design
in Chapter 4 additionally makes two output-side probes mandatory before any campaign cell is accepted.

---

**Figure 6.** *(insert `Figure_06_tag2_dispatch.png` here)* - Tag-2 dispatch per building Space.

---

### 3.6 End-Use Loads

Activity-driven equipment and lighting loads follow channel-specific rules rather than one shared rule
across all four uses, because the four uses do not share an occupancy semantics. For Retail, lighting and
HVAC-relevant schedules follow the Space's opening hours rather than the customer-presence signal itself,
plug load follows the staff schedule (and therefore stays on the NECB baseline, consistent with §3.5),
and customer presence modulates only the occupant-driven internal gain; minimum lighting and baseline
plug floors are enforced so that an empty-of-customers slot during opening hours is not modelled as a
fully unlit, unpowered space. For Hotel, guest-room loads are modulated by the same diurnal shape and
monthly amplitude used for occupancy (§3.4), while amenity-zone loads remain on the NECB baseline,
matching the amenity-zone occupancy treatment in §3.5.

The activity-driven end-use layer is calibrated against the NRCan Survey of Commercial and Institutional
Energy Use (SCIEU; Natural Resources Canada), the commercial analogue of the residential SHEU anchoring
(Natural Resources Canada, 2019) used in the two-channel construction stage and in the authors'
residential-only prior work (Iseri and Hachem-Vermette, under review b).

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

**Table 6.** *(insert `Table_06_leg2_leg3_delta.md` here)* - Additive ledger across nine steps.

