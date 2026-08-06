# Residential + Office + Retail + Hotel Four-Channel Occupancy Pipeline for BEM/UBEM
### Longitudinal Occupancy-Driven Energy Demand (2005–2030) — Leg 3 of 3
#### Full Pipeline Overview — 4-Channel Split (Residential + Office reused; Retail + Hotel added)

---

## AIM
Extend the completed 2-channel GSS → BEM pipeline into a **four-channel generator** driving every occupiable use in the PNNL Tall / SuperTall mixed-use prototypes: **Residential (AT_HOME)** *replaces* baseline schedules, **Office (AT_WORK)** *modulates* code densities, **Retail (AT_RETAIL)** — the one new GSS channel — modulates the NECB retail baseline, and **Hotel** — the one non-GSS channel — modulates NECB guest-room schedules with a tourism-statistics-derived seasonal multiplier (ISQ for QC, CBRE for AB; no StatCan table exists — dr_L3-01). Per-Space routing key = IDF `Tag 2`; Service/MEP stays on NECB defaults.

> 🔴 **Surfaces CORRIGÉES 2026-07-31 (Défaut 7) — les deux tours.** Parsées du modèle
> (Σ `FloorArea` × `Multiplier` sur `IsPartOfTotalArea = 1`, reproduisant exactement la *Total
> Building Area* d'EnergyPlus), parts de l'occupiable **SuperTall · Tall** : bureau
> **44,33 % · 44,65 %**, hôtel **26,37 % · 24,91 %**, résidentiel **22,50 % · 22,40 %**, retail
> **4,39 % · 5,53 %**. Service/MEP **20,6 % · 21,4 % du brut**, et non les « ~52 % » longtemps
> cités. Surfaces totales **135 857,6 m² · 72 623,1 m²**, contre *40 846 · 26 750* au document —
> soit 2,7 à 3,3× trop petites, ce qui déplace tout EUI d'autant. Anciennes valeurs : la colonne
> Tall répétait 24,4 % pour trois canaux (un gabarit) ; la colonne SuperTall paraissait plausible
> mais ne correspondait pas non plus au modèle. Détail et conséquences dans
> `Step8_docs/3rdJ_08_implementation_improvements.md` § Défaut 7.

> **Three-leg roadmap.** Leg 1 = Residential (COMPLETE, 2nd Journal). Leg 2 = Residential + Office (COMPLETE, validated end-to-end 2026-07-01; office People-schedule wiring fix + re-sim is the one open closeout — its lessons are hard gates in Steps 7–8). **Leg 3 = + Retail + Hotel (this doc, 3rd-Journal target).**
>
> **Status convention.** Reused Legs 1–2 machinery = **DONE**; Retail delta = **PLANNED (Leg 3)**; Hotel side-track = **PLANNED (Leg 3, non-GSS)**. The GSS build delta is one tiler list entry + one Transformer head; the genuinely new machinery is the non-GSS hotel side-track. Companion detail doc: `3rdJ_00_4split_Occupancy_Pipeline.md`; spec: `4-channel_split.md`; unresolved numbers = **pending deep research** (`deepResearch/00_deep_research_prompts_Leg3.md`). **DESIGN FREEZE 2026-07-02: all 13 reports delivered and integrated, all 15 OPEN DECISIONS resolved — the build starts at Step 3.**

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  STEP 1 — DATA COLLECTION & COLUMN SELECTION                                 ║
║  GSS columns: DONE (Legs 1-2)   |   Hotel external source: PLANNED (Leg 3)   ║
║                                                                              ║
║  NO new GSS variables: AT_RETAIL derives from occPRE/occACT already carried  ║
║  retail STAFF invisible in GSS (logged as AT_WORK) -> stay in NECB baseline  ║
║  hotel: NO GSS code in any cycle -> monthly hotel-occupancy series (ISQ/CBRE)║
║    hotel_occupancy_monthly.csv: YEAR, MONTH, PR, occupancy_rate, ADR, RevPAR ║
║    (StatCan has no monthly occupancy; use ISQ and Alberta Economic/CBRE)     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 2 — DATA HARMONIZATION                                                 ║
║  occPRE crosswalk: DONE (Leg 1)  |  OR-rule + hotel series: PLANNED (Leg 3)  ║
║                                                                              ║
║  AT_RETAIL = (occPRE==5) | (occACT==4 "Purchasing Goods & Services")         ║
║    2005/2010 PLACE=06+07 | 2015 LOCATION=306 | 2022 LOCATION=3306 (all 4)    ║
║    grocery vs merchandise NOT separable 2015/22 (single shopping bucket)     ║
║  ONLINE-SHOPPING WRINKLE: occACT==4 & occPRE==1 = shopping FROM HOME         ║
║    RULE FROZEN 2026-07-02 (OD-1): activity arm gated to occPRE in {5,9};     ║
║    leak cross-tab still reported per cycle; other gates stay in force        ║
║  restaurant occPRE==7 available all cycles -- explicitly OUT OF SCOPE        ║
║  hotel series: QC+AB monthly 2005-2022 (ISQ/CBRE; keep COVID months as signal║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 3 — MERGE & TILING  <- THE ONE REAL GSS BUILD DELTA                    ║
║  Status: PLANNED (Leg 3) -- one list entry                                   ║
║                                                                              ║
║  Leg 2 already made tiling list-driven (tile_work_to_30min, cloned from      ║
║    the 9-channel co-presence tiler) -> appending AT_RETAIL = one entry       ║
║  same 4AM-origin slot math (startMin-240)%1440 | majority vote sum>=2        ║
║  1/0 encoding, ffill/bfill -> RETL30_001..048 -> retail_30min.csv            ║
║  CONSERVATIVE: separate CSV; residential + office paths bit-identical        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 4 — MODEL 1: THREE-GSS-HEAD CONDITIONAL TRANSFORMER                    ║
║  Backbone: DONE (Leg 2, AUGMENT) | Head 3: PLANNED (Leg 3) | hotel NOT in    ║
║  model                                                                       ║
║                                                                              ║
║  ENCODER (shared): token = [occACT(14), AT_HOME, AT_WORK, AT_RETAIL, 9 coP]  ║
║    conditioning unchanged: [demog, DDAY_STRATA, CYCLE_YEAR, COLLECT_MODE,    ║
║                             NOCS, COW, HRSWRK]                               ║
║  DECODER: Head 1 resid  |  Head 2 AT_WORK  |  Head 3 AT_RETAIL (NEW)         ║
║  loss a_resid:a_work:a_retail = 1.0:0.5:0.3 | per-head JS < 0.02/stratum     ║
║  DESIGN FROZEN 2026-07-02 (dr_L3-11 AUGMENT / -12 heads / -13 regimen):      ║
║    FIXED weights + PCGrad + diversity loss; SLAW/UW dropped (unstable on     ║
║    the 2% head) | CYCLE_YEAR = continuous projection (2030-safe)             ║
║    binary heads + decode-time argmax projection: ISR <= 0.5% raw, 0% final   ║
║    thresholds 0.50/0.40/0.15 | pos_weight=49 + (-ln 49) logit shift          ║
║    warmup 5ep -> joint 15ep + PCGrad | T=0.7 + min-dwell 2-slot decoding     ║
║  "4 heads" in the PNG = diagram shorthand; 3 GSS heads is authoritative      ║
║  retail targets (dr_L3-06): wkday 12-14h 0.06-0.10 CONFIRMED (~0.079);       ║
║    Sat 13-16h 0.09-0.12 | Sun AB 0.06-0.10 | Sun QC 0.04-0.07 (regulated)    ║
║    night 0.000-0.003 | episode-time share 1.50-2.14%, -25% (not stable)      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 5 — ARCHETYPE LINKAGE                                                  ║
║  Residential Census linkage: DONE (Leg 1) | Office NOCxNAICS: DONE (Leg 2)   ║
║                                                                              ║
║  retail: single PNNL "Retail Retail" archetype v1 -> population-level        ║
║    fraction, no lookup (grocery/merch split impossible, see Step 2)          ║
║  hotel: NO respondent archetype -> province-level multiplier (QC | AB)       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 6 — MODEL 2: FORECAST 2030 + THE HOTEL SIDE-TRACK                      ║
║  Fine-tuning: DONE (Leg 2) | retail lever + hotel track: PLANNED (Leg 3)     ║
║                                                                              ║
║  GSS channels: reuse W_2005->W_2010_ft->W_2015_ft->W_2022_ft + DRIFT_MATRIX  ║
║  office keeps WFH bands (conservative / hybrid / fullyhybrid)                ║
║  RETAIL lever = 3 named 2030 bands (0.97, 0.90, 1.05)                        ║
║    [dr_L3-04_instore_share_2030_REPORT.md]; applied BEFORE the Step-7        ║
║    peak-normalization | + QC-Sunday sub-axis (dr_L3-06): default             ║
║    restricted 0.60-0.75 x Sat peak, optimistic deregulated                   ║
║                                                                              ║
║  HOTEL SIDE-TRACK (bypasses the Transformer entirely):                       ║
║    ISQ/CBRE monthly rate -> SARIMA(1,1,1)(1,1,1,12) per province + COVID     ║
║    indicator (2020-03..2022-06) -> hotel_multiplier_2030.csv                 ║
║    hotel_multiplier(t,month,PR) = s(t) x monthly rate; s(t) = unit-          ║
║    normalized 48-slot guest-room shape (dr_L3-05: plateau 1.00 22-06h,       ║
║    day trough 0.200 wkday / 0.308 wknd) | 2030 bands 0.92/1.00/1.05          ║
║    backcast gate: QC+AB 2015-2019 MAE < 0.05; COVID dip w/o overshoot        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 7 — BEM/UBEM INTEGRATION  <- MODULATE, NOT REPLACE                     ║
║  Resid REPLACE + office MODULATE: DONE (Leg 2) | retail+hotel: PLANNED       ║
║                                                                              ║
║  office_integration.py -> commercial_integration.py :: inject_mixed_use()    ║
║  Tag-2 exact-match dispatch:                                                 ║
║    apartment tags -> residential REPLACE (Number_of_People = HHSIZE)         ║
║    office tags    -> NECB office  x AT_WORK_fraction(t)                      ║
║    Retail tags    -> People = 0.95* x peak-normalized shape_cd(t) in         ║
║                      customer hours; staff-only slots (<=0.10) = baseline    ║
║                      (dr_L3-06; density 24.97 m2/person = OFFICE value,      ║
║                       NECB retail is 29.97 -- see note below; NEVER scaled)  ║
║    GuestRoom5/6/7 -> NECB hotel   x hotel_multiplier(t,month,PR) monthly     ║
║    hotel amenity + service/MEP -> NECB baseline, untouched (measured         ║
║    20.6%/21.4% of gross -- see header note above for the superseded value)   ║
║  missing channel -> falls back to NECB baseline (additive-safe)              ║
║  !! HARD WIRING GATE (Leg-2 bug): assert modulated schedules referenced      ║
║     by the CORRECT field (Number_of_People_Schedule_Name, NOT                ║
║     Schedule_Name) -- the silent failure that flattened Leg-2 office         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 8 — BEM SIMULATION                                                     ║
║  Status: PLANNED (Leg 3)                                                     ║
║                                                                              ║
║  2-city sweep: CAN_MTL Z6 (6A) + CAN_CLG Z7A -- geometry-identical IDFs      ║
║    (SuperTall 135,857.6 / Tall 72,623.1 m2, measured -- see header note      ║
║     above for the superseded value + agg_meta.csv) -> EUI deltas isolate     ║
║     climate                                                                  ║
║  scenarios: Default vs cycles 2005-2022 vs 2030 bands (WFH x in-store x      ║
║    hotel SARIMA) -> EUI table per scenario x climate x channel               ║
║  EUI gates per channel: as-modelled band = PASS, empirical band = INFO       ║
║    retail: as-modelled [80, 110, 155] PASS, empirical [150, 280, 380] INFO   ║
║    hotel: as-modelled [180, 240, 300] PASS, empirical [220, 350, 480] INFO   ║
║  reporting (dr_L3-10): dual-basis EUI (CFA + GFA share); central plant =     ║
║    hourly load-weighted split; service/MEP prorated to the four uses         ║
║  !! TWO MANDATORY PROBES BEFORE ANY CAMPAIGN (Leg-2 lessons):                ║
║     1 scenario-differentiation: byte-identical outputs = automatic FAIL      ║
║     2 stale-output guard: a wiring fix invalidates skip_done completions     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STEP 9 — ACTIVITY-DRIVEN END-USE LOADS (equipment + lighting)               ║
║  Status: PLANNED (Leg 3) -- extend the unified 2-channel analysis to 4       ║
║                                                                              ║
║  retail: lighting/HVAC follow OPENING HOURS; plug follows STAFF (stays       ║
║    baseline); customer presence modulates People gains; Lmin/Pbase floors    ║
║  hotel: guest-room loads x s(t) x monthly amplitude; amenity = baseline      ║
║  calibrate vs NRCan SCIEU (commercial analogue of the SHEU anchoring)        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

> 🔴 **Box corrections 2026-08-04 (V2-C3/C4/C5) — three inline numbers above are wrong, retired here
> to keep the box unreflowed (full derivation + parse command in the companion doc):**
> - **Retail episode-time share** (STEP 4 lane) was "~2.1-2.3% stable"; measured per cycle it is
>   **1.50-2.14%, declining ~25% (2005→2022)**, not stable — `Step2_docs/3rdJ_02_harmonizeGSS_4split_val.md:77-82`.
>   The near-flat 0.97 2030 lever is **not** contradicted by this decline: R2's saturation argument
>   (2005–2022 = the steep phase of e-commerce displacement, now plateaued) reconciles the two — see
>   `3rdJ_00_4split_Occupancy_Pipeline.md` Step 2A.
> - **`0.95*`** (STEP 7 lane, retail injection) is the injected model's *office* schedule peak, not an
>   independently sourced NECB retail/sales peak fraction — a stated limitation (V2-F citation work
>   owed), not a bug; the 0.9215 = 0.95×0.97 injector output is separately verified exact.
> - **Retail density** (STEP 7 lane) — 🔴🔴 **RE-CORRECTED 2026-08-05, and finding B-11 is RETIRED.**
>   The old "~3.7 m2/person" was **not a second density**: NECB states occupancy in **occupants per
>   1000 ft2**, and office `3.72 occ/1000 ft2` converts to **24.97 m2/person** — the same figure the IDF
>   carries. The apparent 6.8x gap **is the conversion factor** (`25.0 / 3.7 = 6.76`); the number was
>   transcribed without its unit. **The real and much smaller defect:** retail runs NECB's *office*
>   density 24.97 where NECB gives **3.10 occ/1000 ft2 = 29.97 m2/person** for `Retail - sales`, so
>   retail is modelled **~20 % over-crowded**, and NECB's retail **schedule type C** is never loaded
>   (`grep -c "NECB-C-" injected.idf` = 0). The wider pattern is **unaffected and still stands**:
>   occupant density and plug density (`7.5028 W/m²`) are each **one blanket office value across all 17
>   space types in both towers**, while lighting **is** per-space-type. Consequence: office is the one
>   channel these two constants are plausibly right for, so correcting them cannot move office — which
>   *strengthens* the office band-applicability argument (V2-B1). Sources:
>   `improvements/v2/f8_necb_schedule_evidence/space_types_NECB2011.json` (md5 `b2cb54a8`, from
>   `NatLabRockies/openstudio-standards` @ `develop`) and
>   `improvements/investigation/investigation_v2/3rdJ_L3_backward_audit_2026-08-04.md` §B-11.

---

## VALIDATION GATES

**Tiered gates (per day-type — applied to AT_RETAIL exactly as to AT_WORK in Leg 2):**

| Tier | Metric | Threshold |
|---|---|---|
| 1 Distributional | KL (arrival/departure) | < 0.05 |
| 1 | 1-Wasserstein / EMD on hourly presence CDF | < 0.05 |
| 1 | Presence-rate RMS | ≤ 5 pp per day-type |
| 2 Structural | Transition-matrix Frobenius/MAE | < 0.05 |
| 2 | Dwell-time KS test | p > 0.05 (fail to reject) |
| 2 | Autocorrelation MAE (lags 1–24 h) | < 0.05 |
| 3 Downstream (ASHRAE G14) | NMBE | monthly ±5 %, hourly ±10 % |
| 3 | CV(RMSE) | monthly 15 %, hourly 30 % |
| 3 | Peak demand + timing | magnitude ±15 %; timing ≤ 1 h |

**Channel-specific gates (Leg-3 spec §7 + the Leg-2 lesson gates):**

| Layer | Check | Target |
|---|---|---|
| LOCATION mapping | AT_RETAIL rate, weekday 12:00–14:00, per cycle | 0.06–0.10 (CONFIRMED by dr_L3-06, central ≈ 0.079) |
| LOCATION mapping | Saturday peak rate 13:00–16:00 · Sunday per city · night 00–05h | 0.09–0.12 · AB 0.06–0.10 / QC 0.04–0.07 · 0.000–0.003 (dr_L3-06) |
| OR-rule leak | `occACT==4 & occPRE==1` (online shopping) share per cycle | rule FROZEN (gated, OD-1); cross-tab still reported as verification |
| Transformer (JS) | JS(AT_WORK), JS(AT_RETAIL) per stratum | < 0.02 each (Note: JS is toothless for AT_RETAIL; must be paired with PR-AUC/F1 gates) |
| Transformer (Resolution) | PR-AUC and F1-score on positive slots for AT_RETAIL | PR-AUC ≥ 0.15, F1-score ≥ 0.25 (to catch all-zeros failure) |
| Transformer (Dynamics) | Midday (11-14h) rate error & transitions per day for AT_RETAIL | Midday error ≤ 3.0 pp, transitions ≥ 0.05 transitions/day |
| Transformer (Regression) | Old head (Head 1 & Head 2) JS drift | ΔJS ≤ 0.002 bits vs Leg-2 validation baseline |
| Transformer (Exclusivity) | Impossible-State Rate: slots with > 1 of {AT_HOME, AT_WORK, AT_RETAIL} active | ISR ≤ 0.5 % raw; = 0 % after the decode-time projection (dr_L3-12) |
| Hotel backcast | QC + AB monthly 2015–2019 vs reconstruction | MAE < 0.05 |
| Hotel COVID dip | 2020-04 reconstruction | recovered without overshoot |
| Wiring | post-injection field-reference assertion | 100 % of modulated Spaces |
| Simulation | scenario-differentiation probe | outputs differ per channel |
| BEM end-to-end | Default vs 2022, Montreal SuperTall | EUI delta positive; Office + Hotel dominant |
| Floor-area sanity | per-channel EUI shares vs parsed occupiable shares | ±2 pp |

> **Threshold provenance (Leg-2 discipline kept).** NMBE / CV(RMSE) = **ASHRAE Guideline 14** (cite the standard). The `< 0.05` / ±15 % / ≤ 1 h gates, the 0.06–0.10 retail rate, the hotel MAE < 0.05, the ISR ≤ 0.5 % bar, the decode thresholds (0.50 / 0.40 / 0.15), and the ±2 pp EUI-share gate are **project-chosen**, set before tuning — never cite them to the literature (dr_L3-10: the ±2 pp gate is project-novel; dr_L3-11/13: PR-AUC ≥ 0.15 / F1 ≥ 0.25 are heuristic). Model selection on the **Pareto frontier**, operationalized per dr_L3-13 as gate-first filtering → lexicographic (maximize retail F1) — never a single composite.

---

## KEY DESIGN DECISIONS SUMMARY

| Decision | Rationale |
|---|---|
| Four channels, not one "occupant" channel | Distinct populations (households, workforce, customers, guests); conflation smears the longitudinal signal. |
| Hotel from provincial tourism stats (ISQ / CBRE), not GSS | GSS frame excludes hotel guests by construction — GSS-driven hotel zones would be systematically under-occupied. |
| Office / Retail / Hotel modulate; Residential replaces | Code-of-record peak densities preserved; only the *temporal* signal is injected. Residential replacement is per-household semantics. |
| Retail = customer presence only | Staff are AT_WORK in GSS; worker density already lives in the NECB baseline being modulated. |
| Hotel forecast via SARIMA, not the Transformer | Population-aggregate monthly series, no respondents behind it; 3 GSS heads + SARIMA side-track is authoritative over the PNG's "4 heads". |
| Tag 2 = per-Space routing key | PNNL prototypes leave Space Type blank; Tag 2 is the verified function string (exact match, not substring). |
| Service / MEP (20.6 % · 21.4 % of gross, measured — see header note above) untouched | No occupant-driven demand worth modelling; no GSS signal. |
| Additive on Leg 2 | Missing channel → NECB fallback; residential + office injection unchanged → no prior figure invalidated. |
| One scenario lever per channel | WFH (office), in-store share (retail), SARIMA trend (hotel) — re-runnable sensitivity bands, the Leg-2 reviewer-defusing pattern. |
| Wiring + differentiation gates mandatory | The Leg-2 People-field bug passed every input-side check; only output-side differentiation catches this failure class. |
| Binary heads + decode-time exclusivity projection | Categorical softmax would crush the ~2 % retail class and break Head-1 bit-compatibility; the projection keeps calibration and guarantees one-place-at-a-time (dr_L3-12). |
| Fixed-weight scalarization + PCGrad, not SLAW/UW | Dynamic balancers destabilize on a ~2 %-positive task; tuned fixed weights match or beat them at 2–4 tasks (dr_L3-13). |
| Dual-basis EUI + load-weighted plant allocation | CFA = thermodynamic truth; GFA share = SCIEU comparability; hourly coil-load split = defensible tenant attribution (dr_L3-10). |

---

## OPEN DECISIONS (resolve before/within Leg 3)

1. AT_RETAIL OR-rule — RESOLVED 2026-07-02 (user decision): activity arm gated, `AT_RETAIL = (occPRE==5) | ((occACT==4) & occPRE∈{5,9})`; the per-cycle leak cross-tab is still reported as verification, and the LOCATION-mapping + co-presence gates stay fully in force. Consequence: AT_HOME∧AT_RETAIL is not a legitimate overlap → the dr_L3-12 projection covers the full three-channel set.
2. Retail 2030 scenario band values — RESOLVED 2026-07-02. Sourced from deep-research report [dr_L3-04_instore_share_2030_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-04_instore_share_2030_REPORT.md). Plateau/Resilient Central = 0.97 (default), Continued-Shift = 0.90, In-Store Renaissance = 1.05.
3. StatCan hotel table ID / QC+AB monthly coverage 2005–2022 / breaks — RESOLVED 2026-07-02. Sourced from ISQ (for QC) and Travel Alberta/CBRE (for AB), with 2005–2009 AB spliced from CBRE National Market Report archives.
4. Hotel diurnal shape `s(t)` — RESOLVED 2026-07-02 ([dr_L3-05_hotel_diurnal_shape_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-05_hotel_diurnal_shape_REPORT.md)): PNNL guest-room-derived 48-slot unit shape; overnight plateau 1.00 (22:00–06:00), day trough 0.200 weekday (09:00–15:00) / 0.308 weekend (09:00–17:00); a fixed shape × monthly amplitude is defended by circadian stability.
5. Retail + hotel EUI plausibility bands — Retail EUI bands RESOLVED (2026-07-02, [dr_L3-02_retail_eui_bands_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-02_retail_eui_bands_REPORT.md)): as-modelled band **(low 80, central 110, high 155) kWh/m²/yr** = **PASS criterion**; empirical band **(low 150, central 280, high 380) kWh/m²/yr** = **INFO criterion**. Hotel EUI bands RESOLVED (2026-07-02, [dr_L3-03_hotel_eui_bands_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-03_hotel_eui_bands_REPORT.md)): as-modelled band **(low 180, central 240, high 300) kWh/m²/yr** = **PASS criterion**; empirical band **(low 220, central 350, high 480) kWh/m²/yr** = **INFO criterion**. 🔴🔴 **BAND DECISIONS TAKEN 2026-08-05 (V2-B1/B2/B3, propagated by V2-C6). No band value was widened and all three failing EUI gates are still failing** — the decisions fix provenance and decision rules, not thresholds:
   - **Hotel: the 300 ceiling STANDS, its citation MOVES.** `dr_L3-03`'s two primaries were chased to the end and **neither exists** (V2-F4: one `NOT FOUND`; `PNNL-28543` resolves to a nuclear-fuel report, confirmed twice independently). Replacement retrieved **first-party** (V2-F6): DOE/PNNL **Large Hotel, ASHRAE 90.1-2019 = 284.44 kWh/m²·yr (CZ 6A Rochester) / 299.28 (CZ 7 International Falls)**, parsed from the prototype ZIP's own `.table.htm`. The old ceiling rested on the 90.1-2004 lineage's **302.21**, so the vintage-matched value is **1.0 % away** and the *"a 2004 band is scoring a 2019 building"* objection is **dead**. `S9-EUI-hotel` still **FAILs 21/56**, all over the ceiling, all `Tall`. ⚠️ **Limitation, not a tolerance:** NECB-2017 Montréal/Calgary tower vs a 90.1-2019 Rochester / International Falls prototype — archetype and city sets do not match (goes to V2-G3).
   - **Retail: the rule is MEDIAN-IN-BAND, not 56-of-56** (V2-B3). The gate was turning on **0.15 % of its floor** — V2-E3 moved the median −0.05 % and flipped one cell. An all-cells rule on a spread smaller than its own uncertainty reports noise as a verdict. The retail **rate** gate → **INFO** (V2-D6): its only time-of-day reference (BLS ATUS A-3B) says we are ~44 % *high* while the old band said 24.5 % *low* — the references **disagree in direction**. Shape gates stay PASS/FAIL.
   - **Office: applicability is the finding and the floor is CONTESTED** (V2-B1). The *uninjected* `Default_NECB` control fails this gate too, and the floor of **100** sits **above NECB's own uninjected tower at 85.45** — a gate no untreated control can pass measures the band, not the model. Two mechanisms tested, **both refuted**. 🔴 The band's `src=` **points at a directory that does not exist** (V2-D4 provenance, checker seen failing 3/3). Written up as a **band-applicability limitation**; **the value is not moved to make it pass.**
   - **Hotel DHW plant (V2-B4): per-object resize.** `LAUNDRY` alone to **K ≈ 7** (targeted on the internal reference `BOOSTER`, same 180 °F, never clipped, 71.34 K); the other fifteen heaters stay at **K = 1**. A global K changed the *shares*, not the physics. Implementation = **V2-D10**.
6. Hotel amenity-zone modulation — RESOLVED 2026-07-02 (user-confirmed): v1 = NECB baseline; revisit only if the Step-8 hotel EUI gate (as-modelled 180–300) fails. ⚠️ **It did fail** (21/56 over the ceiling as of 2026-08-05) — but the failures are `Tall`-only and the resize work (V2-B4/D10) targets the DHW plant, not amenity modulation; revisiting amenity zones is **not** currently on the task list.
7. Office→retail lunch cross-use transition — RESOLVED 2026-07-02. Keep simulation channels independent (Option a) to prevent frame mismatch and double-counting, but present the GSS transition statistics as a diagnostic figure (Option b). Sourced justification: Feng et al. (2020) shows < 1.5% retail cooling load delta from coupling, as detailed in [dr_L3-07_crossuse_lunch_coupling_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-07_crossuse_lunch_coupling_REPORT.md).
8. Interpolate-to-Timestep — RESOLVED 2026-07-02 (user-confirmed): inherit the Leg-2 choice; apply uniformly to retail + hotel schedules; record the inherited value in the Step-7 doc.
9. Restaurant channel (`occPRE==7`) — available all cycles, explicitly out of scope (no prototype Space to drive).
10. Transformer rare head training recipe (dr_L3-08) — RESOLVED 2026-07-02. Sourced from deep-research report [dr_L3-08_rare_head_extension_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-08_rare_head_extension_REPORT.md). Head-only Warmup (5 epochs) followed by Joint Fine-Tuning (15 epochs) with PCGrad. Rarity is addressed using BCE loss with $pos\_weight = 49$, corrected post-hoc by subtracting $\ln(49) \approx 3.89$ from raw logits during inference. The old heads are protected using regression gates ($\Delta JS \le 0.002$ bits), and the toothless JS gate is augmented with PR-AUC $\ge 0.15$ and F1 $\ge 0.25$ gates to catch all-zeros failure.
11. Retail multiplier normalization + diurnal targets — RESOLVED 2026-07-02 ([dr_L3-06_retail_diurnal_targets_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-06_retail_diurnal_targets_REPORT.md)): peak-normalized shape-only injection, `retail_schedule_multiplier(t,c,d) = 0.95 × shape_c_d(t)` (Richardson 2010 lineage; raw-fraction injection REJECTED); staff-only slots (baseline ≤ 0.10) keep code; 2005→2022 level drift routed to the Step-6B lever applied before normalization. 🔴 **CORRECTED 2026-08-04 (V2-C4):** 0.95 is the office-baseline peak, inherited — not independently retail-sourced; stated limitation, re-sourcing owed to V2-F citation work; method unaffected. 🔴 **CORRECTED 2026-08-04 (V2-C5):** the 2005→2022 level drift is **1.50–2.14 %, a ~25 % decline** (not "~2.1–2.3 % stable"), reconciled with the near-flat 0.97 2030 lever via the saturation argument (see companion doc Step 2A). Weekday 0.06–0.10 gate CONFIRMED (≈ 0.079); NEW Saturday 0.09–0.12 @ 13–16h; Sunday AB 0.06–0.10 / QC 0.04–0.07; night 0.000–0.003; + QC-Sunday sub-axis on the 2030 lever. 🔴 **CORRECTED 2026-08-04 (V2-C8):** the ~~Richardson 2010 lineage~~ citation above is corrected. Richardson, Thomson & Infield (2008, *Energy and Buildings* 40(8), 1560–1566) and the 2010 follow-on (Richardson, Thomson, Infield & Clifford, *Energy and Buildings* 42(10), 1878–1887) were opened and read (V2-F1): they establish a **household-level first-order Markov chain over the active-occupant count S(t) ∈ {0…N}** at ten-minute resolution, with separate weekday/weekend calibration — **not** the any-present×N-style shape/amplitude model this project had cited them as supporting. Full text is paywalled; correction rests on abstracts + methods, not a page reference. Method and verdict unaffected — only the attribution changes.
12. Step-8/9 per-channel EUI reporting basis + paper novelty positioning — RESOLVED 2026-07-02 ([dr_L3-10_mixeduse_reporting_positioning_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-10_mixeduse_reporting_positioning_REPORT.md)): dual-basis EUI (CFA primary + occupiable GFA share for SCIEU comparison), hourly load-weighted central-plant allocation, service/MEP prorated by area; ±2 pp EUI-share gate confirmed project-novel. Novelty matrix: the TUS→4-channel→single-stacked-tower→2030 combination is unclaimed; differentiate vs Doma & Ouf (2023/2024), Buttitta & Finn (2020), Widén & Wäckelgård (2010).
13. Step-4 backbone keep/augment/replace at 3 heads vs 2023–2026 alternatives — RESOLVED 2026-07-02. Sourced from deep-research report [dr_L3-11_architecture_pressure_test_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-11_architecture_pressure_test_REPORT.md). Keep + targeted upgrades (Warmup + PCGrad + Logit-Adjusted BCE + Raking). MDLM rejection stands due to latency and transition noise.
14. Step-4 output representation — RESOLVED 2026-07-02. Sourced from deep-research report [dr_L3-12_output_representation_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-12_output_representation_REPORT.md). Keep independent binary heads calibrated using logit-adjusted sigmoid outputs, paired with a decode-time Threshold-Normalized Argmax Projection to enforce mutual exclusivity (100% physical consistency) without distorting individual marginals. Validation enforces an Impossible-State Rate (ISR) gate of ≤ 0.5% before projection.
15. **Step-4 training regimen playbook — RESOLVED 2026-07-02.** Sourced from deep-research report [dr_L3-13_training_regimen_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-13_training_regimen_REPORT.md). We recommend Unitary Scalarization (Fixed Weights $\alpha = 1.0 : 0.5 : 0.3$) + PCGrad pairwise gradient surgery as the loss balancing scheme, continuous year projection for `CYCLE_YEAR` to preserve progressive fine-tunability to 2030, stratified batching + inverse-frequency loss scaling for stratum balance, standard survey weights in loss with clipping (no active oversampling), dropout 0.1 (logits excluded) and weight decay 1e-4 (no label smoothing, no data augmentation), temperature 0.7 + minimum duration constraint for decoding, and gate-first filtering followed by lexicographic selection (maximizing retail F1) over a 3-run share-vs-separate backbone ablation.

> Graphical abstract `Residential-Office-Retail-Hotel_Pipeline.png` already exists in this folder (four-lane teal/orange/magenta/gold visual with the gold hotel lane sourced from tourism stats). Full spec: `4-channel_split.md`; detailed step-by-step: `3rdJ_00_4split_Occupancy_Pipeline.md`.
