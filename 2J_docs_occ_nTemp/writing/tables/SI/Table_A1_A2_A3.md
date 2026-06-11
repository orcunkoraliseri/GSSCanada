# Tables A1–A3 — End-Use Load Model Reference Tables

*Source:* `09_activityDrivenLoads.md` §9.1–9.5; `methodology_assessment_and_paper_skeleton.md` Part 3b Step-9 block

---

## Table A1 — Activity × End-Use Weight Matrix (9 end uses × 14 activity categories)

Cells give the fractional weight allocated to each end use for each activity code. Weights apply to the activity-driven tier only (not to the flat baseload — see Table A3).

| Code | Activity | Cook | Dishw | Washer | Dryer | TV/Ent | PC/Office | Care+DHW | Light |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Work (home/telework) | 0.05 | 0 | 0 | 0 | 0 | 0.90 | 0.05 | 1.0 |
| 2 | Household work & maint. | 0.10 | 0.20 | 0.30 | 0.20 | 0 | 0 | 0.20 | 1.0 |
| 3 | Caregiving | 0.10 | 0 | 0 | 0 | 0.30 | 0 | 0.10 | 1.0 |
| 4 | Purchasing (away) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | Sleep | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 6 | Eating & drinking | 0.85 | 0.15 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 7 | Personal care | 0 | 0 | 0 | 0 | 0 | 0 | 0.90 | 1.0 |
| 8 | Education (home) | 0.05 | 0 | 0 | 0 | 0 | 0.85 | 0 | 1.0 |
| 9 | Socializing | 0.15 | 0 | 0 | 0 | 0.40 | 0 | 0 | 1.0 |
| 10 | Passive leisure | 0 | 0 | 0 | 0 | 0.85 | 0.15 | 0 | 1.0 |
| 11 | Active leisure | 0 | 0 | 0 | 0 | 0.20 | 0 | 0.20 | 1.0 |
| 12 | Community/volunteer (away) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 13 | Travel (away) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 14 | Misc (home) | 0 | 0 | 0.10 | 0 | 0.10 | 0.10 | 0 | 1.0 |

**Column definitions:**
- **Cook** = cooking appliances (range/oven, microwave, kettle)
- **Dishw** = dishwasher
- **Washer** = washing machine
- **Dryer** = clothes dryer
- **TV/Ent** = television and entertainment electronics
- **PC/Office** = desktop computer, laptop, home-office equipment
- **Care+DHW** = personal care appliances (hair dryer) + domestic hot water
- **Light** = lighting (see Table A3 note; Lighting weight = 1.0 for every active at-home state, then as-built = binary occupied-and-awake × SHEU scale, no daylight gate — R1)

**Within-activity sub-splits** (fracture a broad GSS code into constituent appliances at the Cook/Dishw/Washer/Dryer/TV/PC level):
- Code 2 (Household work): washer 0.35 / dryer 0.25 / dishwasher 0.20 / cleaning 0.20
- Code 6 (Eating & drinking): range 0.45 / microwave 0.35 / small-appliance 0.20; time-of-day variant: 06–10 h → small-appliance 0.50 / microwave 0.40; 16–20 h → range 0.70
- Code 10 (Passive leisure): TV 0.65 / PC 0.20 / laptop 0.15

**Co-presence scaling (§9.3):**
- *Shared devices* (cooking, dishwasher, washer, dryer, TV): sub-linear effective-occupancy EFF(N) = 1.0 / 1.4 / 1.7 / 1.9 / 2.0 for N = 1 / 2 / 3 / 4 / ≥5
- *Personal devices* (PC, hair-dryer, personal DHW): linear scaling (= N)

---

## Table A2 — Appliance Wattages and Sub-30-Min Prorating Rule

*Source:* `09_activityDrivenLoads.md` §9.2 DR-2 resolved values

| Appliance | Rated power (W) | End-use category | Notes |
|---|---|---|---|
| Range / oven | 3,000 | Cook | |
| Microwave | 1,500 | Cook | |
| Kettle | 1,200 | Cook | |
| Dishwasher | 930 | Dishw | Cycles >30 min queue forward |
| Washing machine | 470 | Washer | |
| Clothes dryer | 2,100 | Dryer | |
| Television | 100 | TV/Ent | |
| Desktop computer | 150 | PC/Office | |
| Laptop | 45 | PC/Office | |

**Sub-30-min prorating rule:** loads with episode duration D < 30 min are prorated as P_rated × (D / 30). Dishwasher cycles longer than one 30-min slot queue forward into the next slot(s).

> Note: The prototype (`Step9_docs/prototype/activity_loads.py`) used a simplified aggregated subset (e.g. one ~930 W "cooking" bucket); the per-end-use SHEU scalar re-levels the annual total regardless of the within-Cook split, so prototype-vs-production differences are absorbed by calibration.

---

## Table A3 — Baseload Roster (flat 24/7, never occupancy-modulated)

*Source:* `09_activityDrivenLoads.md` §9.1 + §9.4 DR-1 resolved values; `methodology_assessment_and_paper_skeleton.md` Part 3b Step-9 block

| Appliance | Annual energy (kWh/yr) | Average power (W) | Notes |
|---|---|---|---|
| Refrigerator | 448 | 51 | SHEU 2019 / CEUD T16 published UEC; held fixed (flat 24/7) |
| Freezer | 343 | 39 | SHEU 2019 / CEUD T16 published UEC; held fixed (flat 24/7) |
| Standby (networking, misc. always-on) | ~400–430 | 45–49 | SHEU-derived range; held flat 24/7 |

**Two-tier calibration logic:** Baseload (fridge + freezer + standby, ~1,000–1,200 kWh/hh·yr) is held fixed at its published SHEU values and is never zeroed when the dwelling is empty or during sleep. The activity-driven tier absorbs the residual to reach the per-dwelling SHEU total via the calibration scalar f_e = SHEU_target_e(dwelling) / simulated_annual_e.

**Multi-unit fridge correction (Deviation D8):** For OtherDwelling (attached/row-house) archetypes, the IDF may include multiple fridge objects. The net SHEU target used for calibration is: SHEU_EQUIP_KWH_NET = 3,700 − 448 = 3,252 kWh (single-detached reference; the IDF's always-on `refrigerator1` object accounts for the 448 kWh, so the STEP9 BASELOAD_W (130 W flat) must not double-count it). Verified: SHEU_EQUIP_KWH_NET = 3,252 kWh. See Appendix D entry D8.

**Per-dwelling SHEU equipment targets (activity-driven tier anchor):**
| Dwelling type | SHEU equipment total (kWh/hh·yr) | Net SHEU after IDF fridge (kWh) |
|---|---|---|
| SingleDetached | 3,700 | 3,252 |
| OtherDwelling (attached) | 3,139 | ⚠ check source |
| MidRise apartment | 2,166 | ⚠ check source |
| HighRise apartment | 1,922 | ⚠ check source |

**SHEU lighting targets (kWh/hh·yr):**
| Dwelling type | SHEU lighting (kWh/hh·yr) |
|---|---|
| SingleDetached | 1,262 |
| OtherDwelling | 1,100 |
| Apartment (MidRise / HighRise) | 736 |

> National average lighting: 1,053 kWh/hh·yr (SHEU 2019).
