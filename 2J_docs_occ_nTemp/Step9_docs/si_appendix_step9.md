# Supplementary Information — Activity-Driven Equipment and Lighting Loads

> Supplementary analysis for the occupancy-modelling paper. Section numbering (S4, S5) follows the
> main manuscript; renumber on final assembly. Bibliographic details (vol./pp./DOI) in the
> References should be verified against the publisher of record before submission.

---

## S4. Activity-Driven Load Adjustment Method

### S4.1 Motivation and approach

The primary EnergyPlus simulations use occupancy-*presence* schedules derived from the synthetic
diary model: equipment (plug-load) and lighting are switched between a high and a low level by a
presence flag, and the fractions within each occupied period come from the archetype default
schedules. This captures *whether* a dwelling is occupied but not *what its occupants are doing*.

The synthetic diaries, however, also predict a 30-minute time-series of **activities** (14 GSS
categories) and co-presence for every household. The activity-driven extension uses these activities
to shape the equipment and lighting demand, so that the daily electricity curve reflects the
predicted mix of cooking, laundry, screen use, home-office work and sleep — then re-anchors the
annual total to the Survey of Household Energy Use (SHEU 2019, Natural Resources Canada) so that
calibration is preserved. This deepens the occupancy→load-shape contribution to an
**activity→end-use-resolved** load shape.

The approach is a deliberately simplified ("light") adaptation of established activity-based
bottom-up demand models (Richardson et al., 2010; McKenna & Thomson, 2016; Widén & Wäckelgård,
2010). Those models *generate* activities stochastically (Markov chains) and draw appliance
switch-on events probabilistically. Because the present pipeline already **predicts** the activity
time-series, we apply it **deterministically as an expected-load shape** — no Markov chain and no
switch-on sampling — and calibrate the annual total to SHEU with a single per-end-use scalar, in the
manner of Richardson et al. (2010) and Armstrong et al. (2009).

### S4.2 Two-tier load decomposition

Each dwelling's electricity is split into two parts:

- **Always-on baseload** — the refrigerator (and freezer/networking/standby), modelled as a flat
  24/7 load and **never** modulated by activity. The refrigerator is retained from the archetype IDF
  at the SHEU appliance average of ≈448 kWh/yr (≈51 W continuous).
- **Activity-driven load** — cooking, dishwashing, laundry (washer/dryer), television/entertainment
  and computer/home-office, which are shaped by the activity diary.

Holding the baseload flat reproduces the observed overnight floor (it is roughly half of the
appliance block) and prevents the model from zeroing essential loads when the dwelling is empty or
asleep.

### S4.3 Activity → end-use crosswalk

For each 30-minute slot, each present household member's activity contributes a deterministic weight
to the relevant activity-driven end uses. Table S4.1 gives the weight matrix actually used. Activities
performed away from home (Purchasing, Community/volunteer, Travel) and Sleep contribute no active
load (baseload only). Lighting carries a weight of 1.0 in every active at-home state and is then
gated by daylight (§S4.6).

**Table S4.1 — Activity → end-use weight matrix (per active at-home member)**

| Code | Activity | Cooking | Dishwasher | Washer | Dryer | TV | PC | Lighting |
|---|---|---|---|---|---|---|---|---|
| 1 | Work (telework) | 0.05 | — | — | — | — | 0.90 | 1.0 |
| 2 | Household work & maint. | 0.10 | 0.20 | 0.30 | 0.20 | — | — | 1.0 |
| 3 | Caregiving | 0.10 | — | — | — | 0.30 | — | 1.0 |
| 4 | Purchasing | — | — | — | — | — | — | — |
| 5 | Sleep | — | — | — | — | — | — | — |
| 6 | Eating & drinking | 0.85 | 0.15 | — | — | — | — | 1.0 |
| 7 | Personal care | — | — | — | — | — | — | 1.0 |
| 8 | Education (at home) | 0.05 | — | — | — | — | 0.85 | 1.0 |
| 9 | Socializing | 0.15 | — | — | — | 0.40 | — | 1.0 |
| 10 | Passive leisure | — | — | — | — | 0.85 | 0.15 | 1.0 |
| 11 | Active leisure | — | — | — | — | 0.20 | — | 1.0 |
| 12 | Community/volunteer | — | — | — | — | — | — | — |
| 13 | Travel | — | — | — | — | — | — | — |
| 14 | Miscellaneous | — | — | 0.10 | — | 0.10 | 0.10 | 1.0 |

Each end-use weight is multiplied by an appliance active-power rating to obtain the slot load before
calibration. The ratings (W) are: **cooking ≈930** (a composite of range, microwave and small
appliances, duty-prorated for the 30-min slot), **dishwasher 930** (a 90–120 min cycle that queues
forward across three slots, with a per-trigger cool-down so consecutive eating slots do not re-fire
the queue), **washer 470**, **dryer 2100**, **TV 100**, **PC 150**. Sub-30-minute loads are prorated
by their duty fraction within the slot. Because the annual total of every end use is subsequently
re-scaled to SHEU (§S4.5), these ratings set the *relative* shape; their absolute level is corrected
by the calibration scalar.

### S4.4 Co-presence scaling

Activities are resolved per member and aggregated with a non-linear co-presence rule that
distinguishes shared from personal devices:

- **Shared devices** {cooking, dishwasher, washer, dryer, TV} use an effective-occupancy factor
  EFF(N) that saturates with the number of members performing the activity: EFF = 1.0, 1.4, 1.7, 1.9,
  2.0 for N = 1, 2, 3, 4, ≥5. A second person watching the same television, for example, adds load
  sub-linearly rather than doubling it.
- **Personal devices** {PC} scale linearly with the number of members (EFF = N).

This prevents the model from over-predicting demand in multi-occupant dwellings (Richardson et al.,
2008/2010; Widén & Wäckelgård, 2010).

### S4.5 SHEU calibration

The raw activity-weighted annual profile for each end use is re-scaled by a single multiplicative
scalar, f = (SHEU target) / (raw activity-weighted annual sum), so that the **shape comes from
behaviour and the annual total comes from SHEU**. Diaries are resolved by day-type and annualised
with 261 weekdays + 104 weekend days. The baseload (refrigerator) is held fixed and the
activity-driven categories absorb the remaining target; the carrier is therefore calibrated to the
**net** target (gross SHEU appliance total minus the retained 448 kWh/yr refrigerator) so the fridge
is not double-counted.

**Table S4.2 — SHEU 2019 calibration targets by dwelling type (kWh/HH·yr)**

| Dwelling type | SHEU total¹ | Equipment net² | Equipment gross³ | Lighting |
|---|---|---|---|---|
| SingleD (single detached) | 12,694 | 3,252 | 3,700 | 1,262 |
| OtherDwelling (attached) | 10,750 | 2,691 | 3,139 | 1,100 |
| MidRise (low-rise apt.) | 7,417 | 1,718 | 2,166 | 736 |
| HighRise (high-rise apt.) | 6,583 | 1,474 | 1,922 | 736 |

¹ Published SHEU 2019 total household electricity intensity by dwelling type.
² Equipment net = the activity-driven carrier target = gross − 448 kWh/yr (retained refrigerator).
³ Equipment gross = published appliance total. For single detached this is published directly
(appliances ≈3,700, lighting 1,262 kWh/yr). For apartments and attached dwellings, SHEU does **not**
publish a per-end-use split; the appliance fraction (29.2 %, the single-detached ratio 3,700/12,694)
is applied to each dwelling type's published total, and lighting is set to the published apartment
value (736) or, for attached dwellings, the SingleD/apartment midpoint (1,100). These apartment
splits are therefore **model-grade estimates**, not published values (see S6).

### S4.6 Lighting

Lighting is modelled as `active_occupancy(t) × daylight_gate(t)`, scaled to the SHEU lighting total
for the dwelling type. The daylight gate is the same one used in the baseline engine; the activity
extension adds the active-occupancy shape and the SHEU scaling, and is reconciled with the EnergyPlus
`Daylighting:Controls` so the daylight response is not double-counted. The archetype IDF default
(daylight-gated only, not occupancy-shaped) substantially under-counts lighting — e.g. ≈151 kWh/yr
for a single-detached Montreal dwelling against the 1,262 kWh/yr SHEU anchor — confirming that the
SHEU scaling is essential rather than cosmetic.

### S4.7 Injection into EnergyPlus

The calibrated schedules are injected at the same point in the building model where occupancy and
metabolic gains are already applied. For each dwelling, the non-refrigerator equipment and lighting
objects in the occupied zone are neutralised and replaced by a single calibrated activity carrier
(equipment and lighting) carrying the activity schedule; the load method is set explicitly to a
design-level (W) basis so the calibrated wattage is honoured (an earlier area-based default silently
ignored the calibrated level and was corrected). The carrier replaces — rather than adds to — the
default schedule, so loads are not double-counted, and the refrigerator object is preserved as the
flat baseload. Metabolic (people) gains remain a separate object and are unchanged.

**Multi-unit archetypes.** The apartment and attached IDFs model the *whole building* (all dwelling
units). The activity carrier is injected into one representative occupied unit and calibrated on a
**per-dwelling** basis; the other units retain only their baseload. The attached (OtherDwelling) IDF
contains seven named refrigerator objects (one per unit), all scaled to ≈51 W (448 kWh/yr). Because
the building-level equipment meter aggregates all seven, the per-dwelling calibration check subtracts
the six non-occupied units' refrigerator-years before comparing to the gross target:

```
equipment_per_dwelling = building_meter − 6 × 448 kWh/yr      (OtherDwelling, 7 units)
```

A consequence (see S6) is that the building-level *activity* total represents one occupied dwelling's
activity-driven load plus the building's baseload, not a fully occupied building; per-dwelling
magnitudes and all timing results are unaffected.

### S4.8 Validation grid and gate results

The method was validated on a full factorial grid: **4 archetypes × 6 climate zones** (Toronto 5A,
Kelowna 5B, Vancouver 5C, Montreal 6A, Calgary 6B, Winnipeg 7A) × **n = 50 households per cell**
(seed 42, the same sample as the primary simulations, for a paired comparison) × **2 years** (2022
retrospective, 2030 projection) × **2 arms** (presence-only baseline, activity-driven) = **4,800
paired EnergyPlus runs**. 4,790 completed; 8 runs were excluded from the diurnal analysis (7 high-rise
apartment-zone warm-up oscillations and 1 mid-rise HVAC non-convergence, ≤0.2 % of the grid), and
every cell-year-arm bucket retains n ≥ 48.

For each of the 48 cell × year combinations, two annual SHEU gates (±15 %, one each for equipment and
lighting) were evaluated on the activity arm.

**Table S4.3 — Annual calibration gate summary**

| Metric | Result |
|---|---|
| Equipment SHEU ±15 % | **48/48 PASS**; max \|deviation\| 2.5 % (MidRise Toronto 2030, under) |
| Lighting SHEU ±15 % | **48/48 PASS**; max \|deviation\| +2.3 % (HighRise Toronto 2030) |
| Combined | all 48 within ±2.6 %, comfortably inside the tighter ±10 % design aspiration |
| Sleep-hour floor (mean equip. Wh, 02:00–05:00) | elevated (>300 Wh) in 28/48 cell-years (all SingleD + all OtherDwelling + 4 MidRise-2022 cells) — the expected refrigerator/standby baseload, **not** a calibration error |
| Household pairing (n consistent across arms) | 24/24 cells balanced |

The calibration is numerically stable across climate zones and sample draws (deviation does not vary
systematically with climate zone). The elevated sleep-hour floor in single-detached and attached
dwellings reflects the retained refrigerator baseload and, for attached dwellings, the seven
building fridges summing at the building meter; the paired Δ isolates the activity-driven component
against the same baseload.

**Supplementary figures (calibration).**

- **Fig S1** — Equipment annual kWh: baseline vs activity by dwelling type, with the SHEU ±15 % band.
  All activity bars fall within the band; the single-detached baseline exceeds the activity level
  because the default presence-filtered schedule draws more than the SHEU-calibrated activity total.
- **Fig S2** — Lighting annual kWh, same layout. The baseline is very low (≈140–160 kWh) because the
  default schedule is daylight-gated only; the activity injection supplies the full SHEU target,
  confirming proper injection.
- **Fig S3** — SHEU gate deviation (%) for all 48 cell-years, equipment and lighting; all within the
  ±15 % gate and under ±3 %.
- **Fig S4** — Sleep-hour mean equipment load (Wh, 02:00–05:00) per cell; the 300 Wh advisory
  threshold and the physically expected baseload for each archetype.
- **Fig S5** — 2022→2030 equipment differential: activity vs baseline trend, with the activity-minus-
  baseline sharpness as markers.

---

## S5. Diurnal Load Shape and Peak-Hour Shift

### S5.1 Motivation

Annual SHEU totals confirm that the activity-load model is well-calibrated (§S4.8) but mask the
within-day temporal redistribution, which is the primary contribution of the activity-driven
approach. This section characterises the diurnal load shape and the peak-hour shift across the full
24-cell grid, for both equipment and lighting.

### S5.2 Metric definitions

- **Building-level metric** — the `InteriorEquipment:Electricity` / `InteriorLights:Electricity`
  meter, converted to mean Watts (W = J·h⁻¹ / 3600) and averaged over all households in the
  cell-year-arm bucket. This is the metric used for all reported diurnal findings.
- **Zone-level metric** — the equivalent zone meters, used as a single-unit sanity check (see below).
- **Peak hour** — argmax of the 24-point mean diurnal profile (hour mod 24).
- **Peak shift** (activity − baseline) — negative values mean the activity peak occurs earlier.

### S5.3 Full-grid results

The building-level **equipment** peak shifts **−4 h** essentially uniformly across all 24 cells:
baseline equipment peaks at h17–18 (late afternoon/evening); the activity arm peaks at h13–14 (early
afternoon, post-lunch cooking and appliance use). The mean shift is −4.1 h (σ = 0.4 h in 2022, 0.3 h
in 2030; range −3 to −5 h). The **lighting** peak shifts **−2 to −5 h**: baseline lighting peaks at
h19–20 (evening), the activity arm at h14–17 (a broad daytime profile consistent with screen and
task-lighting activity in the diaries).

The shift is essentially identical in 2022 and 2030 (per-cell peak hours are unchanged between the
two years in the great majority of cells), which confirms that the temporal redistribution is driven
by the activity model itself rather than by the year-specific synthetic diary mix.

A direct baseline-vs-activity comparison for single-detached dwellings (**Fig S9**) makes the dual
effect explicit: the default presence-gated IDF equipment averages ≈6,640 kWh/yr (six-city mean,
2022) and peaks in the evening (h18), whereas the activity arm lands on the SHEU anchor (≈3,700
kWh/yr) **and** peaks in the early afternoon (h14). The method thus corrects both the magnitude (the
default over-states single-detached equipment by ≈80 %) and the timing.

### S5.4 Meter notes and sanity check

**Zone-level meters are not usable for multi-unit archetypes.** For apartments and attached dwellings
the zone meter captures only the single occupied unit, where the flat refrigerator dominates and the
daily argmax falls at h0; the zone-level peak-shift column consequently reads −17 to −19 h, an
artifact. The building-level meter aggregates all unit zones and correctly reflects the diurnal
pattern, and is used for every reported finding.

**Single-detached sanity check (confirmed).** For a single-detached dwelling, one unit *is* the whole
building, so the zone and building meters must agree. Across all 12 single-detached cell-years the
building and zone peak hours match exactly for both equipment and lighting, confirming the meter
implementation.

**Note on the prototype.** An early single-cell prototype (n = 5) reported an activity equipment peak
at h7. The full-grid result for the same cell (n = 50) peaks at h13–14: at n = 5 one or two early-
breakfast households dominate the mean, whereas at n = 50 the distribution averages to the post-lunch
peak. The direction (earlier than the evening baseline) is consistent; the prototype h7 value should
not be reported as the representative aggregate.

### S5.5 Per-cell peak-hour shift

**Table S5.1 — Peak-hour shift (activity − baseline), 2022**

| Cell | equip_bldg (h) | light_bldg (h) | BL equip peak | AC equip peak | BL light peak | AC light peak |
|---|---|---|---|---|---|---|
| HighRise__Calgary_6B | −4 | −5 | h17 | h13 | h19 | h14 |
| HighRise__Kelowna_5B | −4 | −3 | h17 | h13 | h19 | h16 |
| HighRise__Montreal_6A | −4 | −3 | h17 | h13 | h19 | h16 |
| HighRise__Toronto_5A | −4 | −4 | h17 | h13 | h19 | h15 |
| HighRise__Vancouver_5C | −4 | −3 | h17 | h13 | h19 | h16 |
| HighRise__Winnipeg_7A | −4 | −4 | h17 | h13 | h19 | h15 |
| MidRise__Calgary_6B | −4 | −5 | h17 | h13 | h19 | h14 |
| MidRise__Kelowna_5B | −4 | −4 | h17 | h13 | h19 | h15 |
| MidRise__Montreal_6A | −4 | −4 | h17 | h13 | h19 | h15 |
| MidRise__Toronto_5A | −4 | −4 | h17 | h13 | h19 | h15 |
| MidRise__Vancouver_5C | −4 | −5 | h17 | h13 | h19 | h14 |
| MidRise__Winnipeg_7A | −3 | −4 | h17 | h14 | h19 | h15 |
| OtherDwelling__Calgary_6B | −4 | −2 | h17 | h13 | h19 | h17 |
| OtherDwelling__Kelowna_5B | −4 | −3 | h18 | h14 | h20 | h17 |
| OtherDwelling__Montreal_6A | −4 | −3 | h18 | h14 | h19 | h16 |
| OtherDwelling__Toronto_5A | −4 | −3 | h18 | h14 | h20 | h17 |
| OtherDwelling__Vancouver_5C | −4 | −3 | h18 | h14 | h19 | h16 |
| OtherDwelling__Winnipeg_7A | −5 | −5 | h18 | h13 | h20 | h15 |
| SingleD__Calgary_6B | −5 | −5 | h18 | h13 | h20 | h15 |
| SingleD__Kelowna_5B | −4 | −3 | h18 | h14 | h20 | h17 |
| SingleD__Montreal_6A | −4 | −3 | h18 | h14 | h19 | h16 |
| SingleD__Toronto_5A | −4 | −3 | h18 | h14 | h20 | h17 |
| SingleD__Vancouver_5C | −4 | −4 | h18 | h14 | h19 | h15 |
| SingleD__Winnipeg_7A | −5 | −3 | h18 | h13 | h20 | h17 |

*All shifts are negative (activity peak earlier). Mean equip_bldg shift = −4.1 h (σ = 0.4 h).*

**Table S5.2 — Peak-hour shift (activity − baseline), 2030**

| Cell | equip_bldg (h) | light_bldg (h) | BL equip peak | AC equip peak | BL light peak | AC light peak |
|---|---|---|---|---|---|---|
| HighRise__Calgary_6B | −4 | −3 | h17 | h13 | h19 | h16 |
| HighRise__Kelowna_5B | −4 | −3 | h17 | h13 | h19 | h16 |
| HighRise__Montreal_6A | −4 | −3 | h17 | h13 | h19 | h16 |
| HighRise__Toronto_5A | −4 | −3 | h17 | h13 | h19 | h16 |
| HighRise__Vancouver_5C | −4 | −3 | h17 | h13 | h19 | h16 |
| HighRise__Winnipeg_7A | −4 | −3 | h17 | h13 | h19 | h16 |
| MidRise__Calgary_6B | −4 | −3 | h17 | h13 | h19 | h16 |
| MidRise__Kelowna_5B | −4 | −3 | h17 | h13 | h19 | h16 |
| MidRise__Montreal_6A | −4 | −3 | h17 | h13 | h19 | h16 |
| MidRise__Toronto_5A | −4 | −3 | h17 | h13 | h19 | h16 |
| MidRise__Vancouver_5C | −4 | −3 | h17 | h13 | h19 | h16 |
| MidRise__Winnipeg_7A | −4 | −3 | h17 | h13 | h19 | h16 |
| OtherDwelling__Calgary_6B | −4 | −2 | h18 | h14 | h19 | h17 |
| OtherDwelling__Kelowna_5B | −4 | −3 | h18 | h14 | h19 | h16 |
| OtherDwelling__Montreal_6A | −5 | −3 | h18 | h13 | h20 | h17 |
| OtherDwelling__Toronto_5A | −4 | −2 | h18 | h14 | h19 | h17 |
| OtherDwelling__Vancouver_5C | −5 | −2 | h18 | h13 | h19 | h17 |
| OtherDwelling__Winnipeg_7A | −4 | −3 | h18 | h14 | h20 | h17 |
| SingleD__Calgary_6B | −4 | −4 | h18 | h14 | h19 | h15 |
| SingleD__Kelowna_5B | −4 | −3 | h18 | h14 | h20 | h17 |
| SingleD__Montreal_6A | −4 | −2 | h18 | h14 | h19 | h17 |
| SingleD__Toronto_5A | −4 | −4 | h18 | h14 | h20 | h16 |
| SingleD__Vancouver_5C | −4 | −3 | h18 | h14 | h19 | h16 |
| SingleD__Winnipeg_7A | −4 | −2 | h17 | h13 | h19 | h17 |

*Mean equip_bldg shift = −4.1 h (σ = 0.3 h); 2022 and 2030 shifts are statistically identical.*

### S5.6 Supplementary figures (load shape)

- **Fig S6** — Equipment diurnal load *shape*, 2022: four archetype panels, each the six-city mean
  **normalised to its own daily mean**, so baseline and activity are compared on shape/timing alone
  (calibrated magnitudes are in Fig S1). The activity peak sits ≈4 h earlier than the evening-peaked
  baseline (early afternoon h13–14 vs late afternoon/evening h17–18) in every archetype and climate
  zone. Normalisation is essential for the multi-unit panels: the building-level baseline aggregates
  all dwellings whereas the activity arm injects only the occupied unit (§S4.7), so an absolute-Watts
  overlay would understate the activity curve by roughly the unit count; totals are gated separately
  in §S4.8.
- **Fig S7** — Equipment baseline→activity peak-hour shift, 2022: all 24 cells as dumbbells (baseline
  vs activity peak hour), grouped by archetype. The uniform downward (−4 h) shift moves the peak from
  the evening baseline (h17–18) into the early afternoon (h13–14).
- **Fig S8** — Lighting diurnal load *shape*, 2022: same layout and normalisation as Fig S6. The
  baseline is sharply evening-peaked (h19–20); the activity curve is a broad daytime profile peaking
  in the afternoon (h14–17) — a −2 to −5 h shift.
- **Fig S9** — Default vs activity-driven equipment demand: a four-panel archetype comparison. The
  single-detached panel is in absolute Watts (with annual kWh and the SHEU anchor annotated),
  showing the default ≈6,640 kWh/yr evening-peaked profile re-shaped to the SHEU-anchored ≈3,700
  kWh/yr early-afternoon profile; the multi-unit panels are normalised to daily mean for the reasons
  in Fig S6.

---

## S6. Limitations

- **Temporal resolution.** The 30-minute activity resolution flattens short appliance spikes (a
  3-minute microwave burst becomes a low sustained load). This is appropriate for load-*shape* and
  peak-*hour* analysis but not for instantaneous appliance peak-kW.
- **Derived apartment end-use splits.** SHEU 2019 publishes per-end-use splits only for single
  detached dwellings; the apartment and attached equipment/lighting targets (Table S4.2) are derived
  by applying the single-detached appliance fraction to each dwelling type's published total. The
  single SHEU scalar bounds the error in the *total* but not the split between end uses.
- **Season-pooled activity inputs.** The activity inputs are pooled across survey months; a seasonal
  modulation of cooking/DHW was considered but **not applied** in this analysis, so the reported
  shapes are season-independent. Seasonal swings in space-conditioning are handled by the thermal
  model, not by the activity loads.
- **Crosswalk assumptions.** The activity→appliance mapping (Table S4.1) is judgement-based and
  adapted from the literature; it determines the relative end-use mix within the SHEU-constrained
  total.
- **Multi-unit per-dwelling injection.** For apartment and attached archetypes the activity carrier
  is injected into a single representative occupied unit and calibrated per dwelling; the building-
  level *activity* total therefore represents one occupied dwelling plus the building baseload, not a
  fully occupied building. Per-dwelling magnitudes and all timing/peak-shift results are valid; whole-
  building absolute activity totals are not.
- **Excluded runs.** 8 of 4,800 runs (≤0.2 %) were excluded for warm-up oscillation (7 high-rise) or
  HVAC non-convergence (1 mid-rise); all reported buckets retain n ≥ 48.

---

## References (SI)

*Verify volume/pages/DOI against the publisher of record before submission. The 2023 Canadian
stochastic generator citation is to be completed by the authors.*

1. Richardson, I., Thomson, M., Infield, D., & Clifford, C. (2010). Domestic electricity use: A
   high-resolution energy demand model. *Energy and Buildings*, 42(10), 1878–1887.
2. Richardson, I., Thomson, M., & Infield, D. (2008). A high-resolution domestic building occupancy
   model for energy demand simulations. *Energy and Buildings*, 40(8), 1560–1566.
3. McKenna, E., & Thomson, M. (2016). High-resolution stochastic integrated thermal–electrical
   domestic demand model. *Applied Energy*, 165, 445–461.
4. Widén, J., & Wäckelgård, E. (2010). A high-resolution stochastic model of domestic activity
   patterns and electricity demand. *Applied Energy*, 87(6), 1880–1892.
5. Armstrong, M. M., Swinton, M. C., Ribberink, H., Beausoleil-Morrison, I., & Millette, J. (2009).
   Synthetically derived profiles for representing occupant-driven electric loads in Canadian
   housing. *Journal of Building Performance Simulation*, 2(1), 15–30.
6. Saldanha, N., & Beausoleil-Morrison, I. (2012). Measured end-use electric load profiles for 12
   Canadian houses at high temporal resolution. *Energy and Buildings*, 49, 519–530.
7. Johnson, G., & Beausoleil-Morrison, I. (2017). High-resolution measured residential electric load
   profiles for 23 Canadian houses. *[journal, vol., pp. — verify]*.
8. Natural Resources Canada (2019). *Survey of Household Energy Use (SHEU) 2019* and the
   Comprehensive Energy Use Database. Office of Energy Efficiency.
9. *[Author(s)] (2023). [Canadian stochastic residential load generator — title]. Building and
   Environment. [complete citation].*
