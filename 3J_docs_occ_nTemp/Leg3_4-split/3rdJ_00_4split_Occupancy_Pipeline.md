# Residential + Office + Retail + Hotel Four-Channel Occupancy Pipeline for BEM/UBEM
### Longitudinal Occupancy-Driven Energy Demand in Canadian Mixed-Use Tall Buildings (2005–2030)
#### Leg 3 of 3 — adds Retail (AT_RETAIL, GSS) and Hotel (StatCan, non-GSS) channels on top of the completed 2-channel pipeline

---

## AIM
Extend the completed two-channel GSS → BEM pipeline (Leg 2) into a **four-channel generator** that drives every occupiable functional use inside the PNNL Tall / SuperTall mixed-use prototypes (`BEM_Setup/Buildings/CAN_CLG`, `CAN_MTL`), each channel routed per-Space by IDF `Tag 2`:

| Channel | Source | Presence signal | Injection mode | Part occupiable — **mesurée** (SuperTall · Tall) |
|---|---|---|---|---|
| **Residential** | GSS `occPRE == 1` (home) | `AT_HOME` per household | **REPLACE** baseline; `Number_of_People = HHSIZE` | **22,50 % · 22,40 %** |
| **Office** | GSS `occPRE == 2` (workplace) | `AT_WORK` population fraction | **MODULATE** NECB/ASHRAE baseline | **44,33 % · 44,65 %** |
| **Retail** ⚠️ NEW | GSS `occPRE == 5` (shopping) OR `occACT == 4` | `AT_RETAIL` population fraction | **MODULATE** NECB retail baseline | **4,39 % · 5,53 %** |
| **Hotel** ⚠️ NEW | Provincial tourism monthly occupancy stats — ISQ (QC) / CBRE (AB) (**NOT GSS**; no StatCan table exists, dr_L3-01) | `hotel_multiplier(t, month, PR)` | **MODULATE** NECB guest-room baseline, monthly | **26,37 % · 24,91 %** |
| *Résidentiel commun* | — | — | *non injecté (base NECB)* | *2,40 % · 2,50 %* |

> 🔴 **CORRIGÉ 2026-07-31 (Défaut 7) — les DEUX colonnes étaient fausses.** L'ancienne colonne Tall
> portait **24,4 % pour trois canaux différents** : trois valeurs identiques au dixième sont un
> gabarit, pas une mesure. L'ancienne colonne SuperTall (24,1 / 30,3 / 16,1 / 29,5) semblait
> plausible — valeurs distinctes sommant à 100 % — mais ne correspond pas davantage au modèle.
> Écart sur le retail : **×3,7 en SuperTall, ×4,4 en Tall**.
>
> Valeurs parsées de l'IDF injecté + la table `Zones` du SQL, cellule par cellule :
> Σ(`FloorArea` × `Multiplier`) sur les zones `IsPartOfTotalArea = 1`, ce qui reproduit
> **exactement** la *Total Building Area* d'EnergyPlus. Identiques sur les 28 cellules de chaque tour.
>
> | | **SuperTall** | **Tall** | *au document* |
> |---|---:|---:|---|
> | Surface totale du bâtiment | **135 857,6 m²** | **72 623,1 m²** | *40 846 · 26 750* |
> | dont occupiable | 107 816,0 m² | 57 075,4 m² | — |
> | Service/MEP, % du brut | **20,64 %** | **21,41 %** | *« ~52 % du brut »* |
> | Plenums exclus (convention EnergyPlus) | 133 790,4 m² | 70 611,6 m² | — |
>
> Les surfaces totales du document sont **2,7 à 3,3× trop petites**, et l'EUI est une division : la
> même énergie donne 99 kWh/m²/an sur la surface mesurée contre 269 sur celle du document. Aucune
> bande dr_L3-02/03 n'a de sens tant que la base de surface n'est pas tranchée sur l'artefact.
> `Step8_docs/outputs_step8/agg/agg_meta.csv` émet désormais ces surfaces par cellule, pour qu'elles
> ne soient plus jamais retapées à la main.
>
> Enjeu au-delà de la prose : la gate **±2 pp** (dr_L3-10, *project-novel*) confronte les parts
> d'énergie aux parts occupiables **parsées**. Contre le gabarit elle aurait échoué sur le retail et
> le bureau quoi que fasse le modèle — et le réflexe d'élargir la tolérance en aurait fait une gate
> vide. Elle a été re-spécifiée (voir Step-9 §7).

> Service / MEP / Circulation reste sur les défauts ASHRAE 90.1 / NECB17 — **non** modulé. Le GSS n'a
> aucun signal pour les gaines d'ascenseur ni les locaux techniques. **Part mesurée : 20,6 %
> (SuperTall) et 21,4 % (Tall) du brut**, et non les « ~52 % » longtemps cités.

> **Three-leg roadmap.** **Leg 1 = Residential (AT_HOME)** — COMPLETE, shipped as the 2nd Journal. **Leg 2 = 2-channel split (Residential + Office)** — COMPLETE, validated end-to-end 2026-07-01 (the office People-schedule wiring fix + re-simulation is the one open closeout item; its lessons are encoded as hard gates in Steps 7–8 below). **Leg 3 = 4-channel split (+ Retail + Hotel)** — *this document*, the 3rd-Journal target.
>
> **Status convention.** Machinery reused from Legs 1–2 is tagged **✅ DONE (Leg 2, unchanged)**. ~~The Retail delta is tagged **⚠️ PLANNED (Leg 3)**; the Hotel side-track is tagged **⚠️ PLANNED (Leg 3, non-GSS)**.~~ **SUPERSEDED 2026-08-05 (V2-G2): both are BUILT AND RUN. Every former PLANNED tag below now reads ✅ DONE (Leg 3) and names the artefact that proves it.** This is a planning document — no code is written or run in this step. Numbers are sourced from `4-channel_split.md` (the Leg-3 spec), `../investigation/00_GSS_split_suitability_audit.md` (the feasibility audit), and the Leg-2 pair `../Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline.md` / `_Overview.md`, whose format this document mirrors. Anything not yet verifiable is marked **pending deep research** (prompts: `deepResearch/00_deep_research_prompts_Leg3.md`) — never assumed. **DESIGN FREEZE 2026-07-02: all 13 deep-research reports are delivered and integrated, and all 15 OPEN DECISIONS are resolved — the build starts at Step 3 (the tiler delta).**

---

## STEP 1 — DATA COLLECTION & COLUMN SELECTION
*No new GSS variables at all. The only new data source is external: the ISQ/CBRE hotel-occupancy series.*

### 1A. GSS Main File — nothing to add

The Leg-1 residential column set and the Leg-2 office employment-gating additions (activity-last-week, worked-last-week, LF status, hours/week, class of worker, NOC, NAICS, telework) are reused unchanged. **Retail requires no Main-file additions**: the customer-presence signal is entirely episode-level, and retail *staff* are deliberately not modelled from GSS (see the frame-caveat table in 1C).

### 1B. GSS Episode File — derived presence flags

| Derived flag | Source | Logic | Availability |
|---|---|---|---|
| `AT_HOME` | `occPRE` | `occPRE == 1` → 1 | All cycles ✅ DONE (Leg 1) |
| `AT_WORK` | `occPRE` | `occPRE == 2` → 1 (employment-gated) | All cycles ✅ DONE (Leg 2) |
| `AT_RETAIL` | `occPRE` + `occACT` | `(occPRE == 5) OR (occACT == 4)` → 1 | All cycles ✅ DONE (Leg 3) — `Step3_docs/3rdJ_03_mergingGSS_4split.py` |

> **Key finding (audit §3).** The harmonized 18-category `occPRE` scheme already carries **Shopping (code 5)** — and Restaurant/bar/club (code 7) — on **every episode row in all four cycles**. Like AT_WORK in Leg 2, AT_RETAIL is *already present in the data*; the only build work is the OR-rule derivation (Step 2) and tiling into the slot arrays (Step 3). No new survey variable, no new crosswalk sheet.

### 1C. NEW — external hotel data ✅ DONE (Leg 3, non-GSS) — `Step1_docs/3rdJ_01_hotelIngest_4split.py`

GSS samples Canadian residents at their place of residence: residents are not recorded as guests in their own city's hotels, and tourists / international guests are not in the GSS frame at all (audit §7: **no hotel location code exists in any cycle**). The Hotel channel is therefore driven by **provincial statistical/tourism body monthly hotel-occupancy series** (Tourisme Québec / ISQ for Quebec and Travel Alberta / CBRE for Alberta, as verified in [dr_L3-01_statcan_hotel_data_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-01_statcan_hotel_data_REPORT.md); no Statistics Canada table contains monthly occupancy rates, ADR, or RevPAR by province):

```
0_Occupancy/external/hotel_occupancy_monthly.csv:
  YEAR, MONTH, PR, occupancy_rate (0–1), ADR_CAD, RevPAR_CAD
```

**Who each channel actually sees (frame caveats — carry into the paper's limitations):**

| Channel | GSS sees | GSS misses | Compensation |
|---|---|---|---|
| Retail | **customers** (shopper side) | **staff** (logged as AT_WORK, not shopping) | NECB/SCIEU worker densities stay in the baseline being modulated |
| Hotel | nothing | guests (out of frame by construction) | ISQ/CBRE tourism series side-track (Step 6) |

---

## STEP 2 — DATA HARMONIZATION
*Confirm the retail crosswalk per cycle; handle the online-shopping wrinkle; harmonize the StatCan hotel series.*

### 2A. AT_RETAIL location-code crosswalk ✅ DONE (Leg 3) — `Step2_docs/3rdJ_02_harmonizeGSS_4split_val.py`

`occPRE == 5` is the harmonized "Shopping" code, already produced by the Leg-1 harmonizer's presence crosswalk (`3rdJ_02_harmonizeGSS_2split.py` + the execution Excel under `references_Pre_coPre_Codes/`):

| Unified | 2005 (C19) | 2010 (C24) | 2015 (C29) | 2022 (GSSP) | Status |
|---|---|---|---|---|---|
| `occPRE == 5` (shopping) | `PLACE = 06` Grocery + `07` Other store / Mall | `PLACE = 06` + `07` | `LOCATION = 306` Grocery / stores / mall | `LOCATION = 3306` Grocery / stores / mall | ✅ Confirmed all cycles (audit §2) |

> **Granularity note (audit §2).** 2015/2022 collapse grocery and general merchandise into one bucket; 2005/2010 kept them separate. The harmonization already merges both into a single "Shopping" category, so the channel is cross-cycle consistent — but a grocery-vs-merchandise archetype split is impossible from GSS. Weighted share of episode-time in shopping locations: ~~**~2.1–2.3 %**, stable across cycles~~ → 🔴 **CORRECTED 2026-08-04 (V2-C5).** Measured per cycle (gated OR-rule, the AT_RETAIL definition): **2005 2.00 % · 2010 2.14 % · 2015 1.66 % · 2022 1.50 %** — a **decline of ~25 %**, not a stable band. Source: `Step2_docs/3rdJ_02_harmonizeGSS_4split_val.md:77-82` (re-run: `py -3 -X utf8 3rdJ_02_harmonizeGSS_4split_val.py` from `Step2_docs/`). Reconciliation with the near-flat 2030 lever below.

> 🔴 **Reconciliation — the decline is real, the 0.97 2030 lever is not contradicted.** R2 (deep-research,
> `deepResearch Prompts/R2_tus_presence_vs_footfall_report.md`) puts the measured −25.0 % alongside three
> long international series over comparable spans — US ATUS −20.8 %, UK TUS/CTUR −34.4 %, Eurostat HETUS
> −21.4 % — so the decline is **behavioural and internationally corroborated**, not a Canadian coding
> artefact (R2 attributes roughly three-quarters of it to real behaviour, one-quarter to a 2022 GSS
> coding-concentration effect already found and gated at Step-2 §2.3, below). The measured **1.50–2.14 %**
> level is itself internationally normal (1.5–2.2 % in every national series R2 examined), not a weak
> signal. The Step-6B 2030 default (0.97, near-flat) is **not** in tension with a −25 % historical decline:
> R2's argument is **saturation**, not stability — the 2005→2022 drop is the steep phase of e-commerce
> displacement; post-2022 e-commerce share has plateaued (~15–19 % of retail sales) and footfall has
> stabilised at ~88–94 % of 2019, so 0.97 encodes the *flattening* of the displacement curve, not a linear
> extrapolation of its steep phase (linear extrapolation of 2005–2022 would give ≈0.88, near the
> conservative band edge). The 0.97 default and the −25 % measurement describe two different phases of the
> same curve.

### 2B. The OR-rule and the online-shopping wrinkle

The spec (`4-channel_split.md §3.3`) derives retail presence from **location OR activity**, because some cycles record errands with a store/mall location but a generic activity, while other respondents record only the shopping activity:

```python
AT_RETAIL = (occPRE == 5) | (occACT == 4)   # occACT 4 = "Purchasing Goods & Services" (ACT_LABELS[4])
```

> **⚠️ The online-shopping wrinkle (Leg-3 analogue of Leg 2's WFH wrinkle).** `occACT == 4` includes purchasing done **from home** (online shopping, phone banking) — an episode with `occACT == 4` & `occPRE == 1` puts nobody in a store. The raw OR-rule would leak these into the retail channel, and the leak grows over the 2005→2022 cycles (e-commerce trend), corrupting exactly the longitudinal signal we care about.
>
> **✅ RULE FROZEN 2026-07-02 (OPEN DECISION 1, user-approved):** gate the activity arm on plausible retail locations —
> `AT_RETAIL = (occPRE == 5) | ((occACT == 4) & occPRE.isin({5, 9}))`.
> Consequences: (a) `AT_HOME ∧ AT_RETAIL` is **not** a legitimate overlap, so the dr_L3-12 exclusivity projection applies to the full {AT_HOME, AT_WORK, AT_RETAIL} set; (b) the per-cycle `occACT==4 × occPRE` cross-tab is **still produced** as a Step-2 validation output — the freeze does not skip the verification; (c) the gating **adds to, never replaces,** the other mandatory gates — the LOCATION-mapping rate gates and the co-presence channel checks stay in force unchanged.

### 2C. Restaurant — available but excluded

`occPRE == 7` (Restaurant / bar / club ← `PLACE 04` / `LOCATION 309` / `3309`) exists in all four cycles (audit §2) and would be one more list entry in the Step-3 tiler. It is **explicitly out of scope for Leg 3**: the PNNL prototypes route `Dining` to the Office channel and `LargeHotel Cafe` to hotel-amenity baseline, so a restaurant channel has no Space to drive. Recorded here so the exclusion is a decision, not an oversight.

### 2D. Hotel series harmonization ✅ DONE (Leg 3, non-GSS) — `Step2_docs/3rdJ_02_hotelHarmonize_4split.py`

- **Geography:** monthly occupancy rate for **QC and AB** (the two simulated cities: Montreal Z6, Calgary Z7A); national series kept as fallback.
- **Window:** 2005–2022 to parallel the GSS cycles; keep all months (the COVID collapse 2020-03 onward is signal for the forecast's COVID indicator, not a gap to fill).
- **Fields:** `occupancy_rate` is the driver; `ADR_CAD` / `RevPAR_CAD` are carried for context only.
- **Known risk:** Resolved in [dr_L3-01_statcan_hotel_data_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-01_statcan_hotel_data_REPORT.md): Statistics Canada does not publish monthly hotel occupancy by province. We use ISQ data (for QC) and Travel Alberta/Alberta Economic Dashboard data (sourced from CBRE, for AB). QC covers 2005–2022 continuously, but AB dashboard data starts in 2008/2010; years 2005–2009 for AB must be spliced from CBRE archives.

---

## STEP 3 — MERGE & TILING (THE ONE REAL GSS BUILD DELTA)
*Add AT_RETAIL to the list-driven tiler. Leg 2 already turned this into a one-list-entry operation.*

Leg 2 closed the tiling gap by cloning the proven 9-channel list-driven co-presence tiler (`tile_copresence_to_30min`, `03_mergingGSS.py:821–944`) into `tile_work_to_30min` (`3rdJ_03_mergingGSS_2split.py:1118–1261`) → `work_30min.csv`. Leg 3 appends one channel (audit §9.2 — "adding a 4th channel is literally one list entry"):

```python
# Derive once, before the tiling loop (episode level):
episodes_sorted["AT_WORK"]   = (episodes_sorted["occPRE"] == 2).astype(float)      # ✅ DONE (Leg 2)
episodes_sorted["AT_RETAIL"] = (
    (episodes_sorted["occPRE"] == 5) |               # location: Shopping
    ((episodes_sorted["occACT"] == 4) &
     episodes_sorted["occPRE"].isin({5, 9}))         # activity arm — FROZEN 2B gate (OD-1, 2026-07-02)
).astype(float)                    # ✅ DONE (Leg 3) -- 3rdJ_03_mergingGSS_4split.py

BINARY_CHANNELS = ["AT_WORK", "AT_RETAIL"]           # restaurant (occPRE == 7) = one more entry, if ever

# Reuse the proven pattern, unchanged in shape:
#   4 AM-origin slot math (startMin-240) % 1440
#   binary majority vote  sum_present >= 2  (144 → 48 slots)
#   1/0 encoding (match AT_HOME, not co-presence's 1/2)
# → emits RETL30_001 .. RETL30_048 → retail_30min.csv
```

| Decision | Choice | Rationale |
|---|---|---|
| Output routing | **conservative variant**: separate `retail_30min.csv`, anchored to the same `occID` order | Residential and office paths stay bit-identical → zero risk to shipped Leg-1/Leg-2 results; retail is purely additive |
| Empty-slot fill | ffill/bfill like AT_HOME / AT_WORK | One policy across all occupancy channels |
| Validation twin | `validate_retail_30min()` cloned from `validate_work_30min()` | Shape, occID alignment, values ∈ {0,1}, plus a night-shopping sanity check (24 h grocery ≈ rare) |

---

## STEP 4 — MODEL 1: THREE-GSS-HEAD CONDITIONAL TRANSFORMER
*Shared encoder (reuse the Leg-2 multi-head backbone) + a third output head for AT_RETAIL. Hotel never enters this model.*

### Architecture

```
ENCODER (shared — reuse Leg-2 backbone, J3 lineage, 6-layer, d_model 384)
  Input slot token = [occACT (14-cat), AT_HOME, AT_WORK, AT_RETAIL,
                      9 × co-presence]                       → 14 features
  Conditioning     = [demog, DDAY_STRATA, CYCLE_YEAR, COLLECT_MODE,
                      NOCS, COW, HRSWRK]                     (unchanged from Leg 2)

DECODER (multi-head, shared cross-attention)
  Head 1 (Leg 1): 48 activity + 48 AT_HOME + 9 × 48 co-presence
  Head 2 (Leg 2): 48 AT_WORK tokens (binary)
  Head 3 (NEW):   48 AT_RETAIL tokens (binary)
```

Loss = weighted sum of per-head losses, **α_resid : α_work : α_retail = 1.0 : 0.5 : 0.3** (spec §3.5, set by signal magnitude — retail occupies ~2 % of episode-time vs ~6–7 % for work). Tune so **each per-head JS divergence < 0.02 per stratum**. Of the Leg-2 multi-head machinery, **PCGrad gradient surgery and the diversity-preserving loss** (the COP peak-collapse countermeasures) carry over unchanged — but the **dynamic loss balancer (SLAW / homoscedastic UW) does NOT survive the third head**: dr_L3-13 (Table 1) shows dynamic weighters destabilize when one task is ~2 %-positive (mostly-zero losses → near-zero loss variance → weight spikes → gradient noise into the shared encoder), while well-tuned fixed weights match or beat them at 2–4 tasks (Kurin et al. 2022). Leg 3 therefore trains with **unitary scalarization (the fixed α above) + PCGrad**. Adding Head 3 is a config change plus the design freeze below — not new machinery.

### Step-4 design freeze — the ML trio verdicts (dr_L3-11 / 12 / 13, all RESOLVED 2026-07-02)

> **dr_L3-11 — backbone verdict: AUGMENT** ([dr_L3-11_architecture_pressure_test_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-11_architecture_pressure_test_REPORT.md)).
> Keep the multi-head conditional Transformer; no 2023–2026 challenger (post-MDLM discrete diffusion,
> decoder-only AR / LLM-style joint token stream, SSM/Mamba, discrete flow matching, non-AR iterative
> decoding) passes our gates at our scale. The **Leg-2 MDLM/SEDD rejection stands**: 2024–26 variants
> still carry 8–16× inference overhead plus dwell-time decay (rare states emitted as single-slot
> flickers) on a ~2 %-positive channel. Keep-*unchanged* is also rejected — plain BCE would ship a
> dead retail head. Future replacement bar (record it): a challenger must show stratum JS < 0.02
> **and** transition JS < 0.02 on an occupancy/mobility dataset of ≤ 10⁵ sequences at ≤ 2 forward
> passes per sequence; none found in the 2023–2026 literature.

**(a) Backbone upgrade menu (dr_L3-11, ranked, all low-risk to the shipped heads):**

1. **Logit-adjusted class-weighted BCE on Head 3** — train with `pos_weight = 49`, subtract `ln 49 ≈ 3.89` from raw logits at inference: mathematically exact calibration under imbalance (Menon et al. 2020). Do first.
2. **Head-only warmup → joint fine-tune with PCGrad** — the resolved dr_L3-08 recipe (5 epochs frozen-encoder warmup, then 15 epochs joint), protecting Heads 1–2 (ΔJS ≤ 0.002 bits).
3. **Auxiliary consistency loss** — soft penalty guiding `P(AT_HOME) + P(AT_WORK) + P(AT_RETAIL) ≤ 1`; training-side support for the (b) exclusivity projection.
4. ~~Scheduled sampling~~ — **dropped.** dr_L3-11 ranked it fourth, but the dedicated regimen report rejects it at 48-slot length (training instability + calibration distortion; teacher forcing plus decode-time constraints preferred — dr_L3-13 Table 5). Conflict resolved in favour of the regimen report; flicker is handled at decode time in (c).

**(b) Output representation (dr_L3-12): independent binary heads KEPT + decode-time exclusivity projection.**
The categorical location head is **rejected** — softmax competition against the ~65 % home class crushes the ~2 % retail class, per-class calibration becomes coupled (calibrating one class shifts all others), the dr_L3-08 recipe stops carrying over, and shipped Head 1 would need a bit-compatibility-breaking migration. Hierarchical two-stage is rejected on stage-1 error cascade. The location/trajectory-generation precedents split exactly this way: categorical-state generators (ALBATROSS; GPT-style trajectory models) systematically under-represent rare categories, while Page et al. (2008) ran independent binary channels and resolved conflicts with decode-time priority rules. What ships:

- **ISR — the new exclusivity gate.** Impossible-State Rate = share of generated slots with more than one of {AT_HOME, AT_WORK, AT_RETAIL} active. **Raw model outputs: ISR ≤ 0.5 %** (hard validation gate — evidence the encoder learned the negative location correlation). **Final injected schedules: ISR = 0 %** by construction, via the projection below.
- **Threshold-Normalized Argmax Projection (decode time).** Per-head decision thresholds **θ_home = 0.50, θ_work = 0.40, θ_retail = 0.15** (F1-derived on validation; recalibrate if the 2030 scenario distributions drift). A slot with more than one channel over threshold keeps only `c* = argmax_c p_c(t) / θ_c` — threshold-normalization lets the rare retail channel compete fairly against home. Calibration is untouched: training never sees the constraint, conflicts are rare (< 5 % of slots), and marginals stay individually calibrated (the loss-penalty and grouped-softmax alternatives both bias marginals — dr_L3-12 Table 2).
- **Ordering constraint — SATISFIED 2026-07-02.** OPEN DECISION 1 froze the gated OR-rule (Step 2B), so online shopping is excluded from AT_RETAIL and `AT_HOME ∧ AT_RETAIL` is **not** a legitimate overlap: the projection applies to the **full {AT_HOME, AT_WORK, AT_RETAIL} set**, no exemptions.

**(c) Training regimen (dr_L3-13) — the frozen build checklist (the Step-4 doc and code inherit this table):**

| Block | Frozen choice |
|---|---|
| Loss balancing | **Unitary scalarization** — fixed α = 1.0 : 0.5 : 0.3 + **PCGrad** pairwise; diversity-preserving loss retained from Leg 2. **Never SLAW / UW / GradNorm / DWA / CAGrad**: dynamic weighters spike on the rare head's degenerate loss statistics (dr_L3-13 mistake #1). |
| Conditioning — demographics | `nn.Embedding` per categorical (AGEGRP, SEX, NOCS, COW, …), projected and appended as static context. |
| Conditioning — CYCLE_YEAR | **Continuous projection**: normalize to [0, 1] as `(year − 2005) / 25`, then `nn.Linear(1, d_model)`. **Never a categorical embedding** — 2030 would be an untrained index; continuous projection extrapolates (dr_L3-13 mistake #2). |
| Conditioning — DDAY_STRATA | `nn.Embedding(3, d_model)` added to the input — it drives the whole diurnal shape. |
| Conditioning — COLLECT_MODE | Low-capacity `nn.Embedding(2, 16)` — confound control, not signal; keep it too small to leak. |
| Batching | Stratified batch composition (50 % weekday / 25 % Sat / 25 % Sun per batch) + inverse-cycle-frequency weighting during joint pre-training (2022 has the fewest diaries), before the progressive fine-tuning chain takes over. |
| Survey weights | `WGHT_PER` inside the loss, clipped at the 99th percentile. **No retail-diary oversampling** — it shifts the prior and silently invalidates the −ln 49 correction (double-correction risk). |
| Regularization | Dropout 0.1 (attention/residual only — **never on output projections**), weight decay 1e-4 (AdamW). **Label smoothing = 0** (calibration-destroying, dr_L3-13 mistake #3) and **no diary augmentation** (slot jitter / cyclic shifts corrupt circadian synchronization). |
| Schedule | Phase 1 warmup: 5 epochs, Head 3 only, lr 1e-3. Phase 2 joint: 15 epochs, all parameters, lr 1e-4, PCGrad on. |
| Decoding | AR activity arm: temperature 0.7 + nucleus p = 0.9; **minimum-dwell constraint ≥ 2 slots (60 min) for work + retail events** — the flicker countermeasure; retail logit shift −ln 49; then the (b) projection; then post-hoc raking. |
| Selection | **Gate-first filter → lexicographic**: keep only checkpoints passing every hard gate (ΔJS ≤ 0.002 bits on old heads, ISR ≤ 0.5 %, PR-AUC ≥ 0.15 ∧ F1 ≥ 0.25, midday error ≤ 3.0 pp, transitions ≥ 0.05/day), then maximize retail F1 among survivors. Early stopping on the gate set (patience 10), never on training loss. Report mean ± sd over **5 seeds** (normal: 1–2 % sd on F1/PR-AUC, 0.001–0.002 bits on JS). |

**(d) Ablation budget — hard cap 4 runs (dr_L3-13).** Everything in (c) is fixed by citation; the single ablation worth its cost is **shared-vs-separate backbone**: Run 1 = fully shared 6-layer encoder (incumbent); Run 2 = frozen Leg-2 encoder + LoRA adapters (r = 8) + Head 3 (zero old-head degradation by construction); Run 3 = semi-shared (layers 1–5 shared, layer 6 split per task). One run held in reserve for seed/debug. Progressive fine-tunability is preserved by construction (continuous CYCLE_YEAR, no prior-shifting resampling, warmup-protected encoder) — the regimen does not fight the dr_L3-08 recipe.

> **Heads count, resolved.** The graphical abstract and spec §10 say "4 output heads"; spec §3.5 defines **3 GSS heads**. **§3.5 is authoritative: three GSS heads + a non-GSS hotel side-track.** The Transformer is conditioned on individual-respondent demographics; hotel occupancy is a population-aggregate monthly series with no respondents behind it — there is nothing for a fourth head to train on. The "4 heads" wording is the diagram's simplification.

### Retail diurnal targets the synthetic AT_RETAIL must reproduce

| Quantity | Target | Source |
|---|---|---|
| Weekday peak window | 12:00–14:00 (lunch spike; secondary 17:00–19:00) | dr_L3-06 (Storeforce / Avison Young footfall + GSS pattern) |
| Weekday 12:00–14:00 population rate | **0.06–0.10 — CONFIRMED** (derived central ≈ 0.079) | dr_L3-06 (HIGH confidence) |
| Saturday peak window + rate | 13:00–16:00; **0.09–0.12** — NEW distinct gate (the weekday gate is too low for the Saturday peak) | dr_L3-06 (MEDIUM confidence, derived) |
| Sunday — Calgary (AB, deregulated since 1985) | 12:00–16:00; the weekday gate 0.06–0.10 applies | dr_L3-06 |
| Sunday — Montreal (QC, trading-hours regulated) | 12:00–17:00 compressed; **0.04–0.07** — province-specific gate (the weekday gate would pass an overshoot) | dr_L3-06 |
| All-day episode-time share | ~~~2.1–2.3 %, stable across cycles~~ 🔴 **1.50–2.14 %, declining ~25 % (2005→2022) — see Step 2A reconciliation** | `Step2_docs/3rdJ_02_harmonizeGSS_4split_val.md:77-82` (was: audit §2) |
| Night 00:00–05:00 | 0.000–0.003, all day types, both cities | dr_L3-06 |

These are **validation targets, not training inputs** — same discipline as the Leg-2 office diurnal targets. Empirical footfall shapes for cross-checking live in `../deepResearch_Resources/Retail Occupancy for Energy Modelling.md`; numeric per-day-type targets — including a check of the project-chosen 0.06–0.10 gate — are **RESOLVED 2026-07-02** in [dr_L3-06_retail_diurnal_targets_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-06_retail_diurnal_targets_REPORT.md): weekday 0.06–0.10 gate **CONFIRMED** (central estimate 0.079); Saturday peak gate **NEW: 0.09–0.12 at 13:00–16:00**; Sunday Calgary gate 0.06–0.10; Sunday Montreal gate 0.04–0.07 (regulated baseline). The Head-3 training recipe for a ~2 %-positive channel (imbalance/calibration, fine-tune vs retrain, α check, regression gates protecting the shipped heads, metrics that fail an all-zeros head) is **RESOLVED 2026-07-02** in [dr_L3-08_rare_head_extension_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-08_rare_head_extension_REPORT.md).

---

## STEP 5 — ARCHETYPE LINKAGE
*Residential and Office unchanged; Retail gets the trivial case; Hotel has no respondent-level archetype at all.*

- **Residential — ✅ DONE (Leg 1, unchanged).** Census-GSS probabilistic linkage (K-means archetypes → RF assignment → building-variable aggregation).
- **Office — ✅ DONE (Leg 2, unchanged).** NOC × NAICS → `office_archetype_ID` lookup.
- **Retail — ✅ DONE (Leg 3), `Step7_docs/3rdJ_07_aug_to_bem_4split.py`.** The PNNL prototypes carry a **single "Retail Retail" archetype**, so v1 needs no lookup: one population-level `at_retail_fraction(t)` per cycle × DDAY_STRATA drives all retail Spaces. If grocery-vs-merchandise separation is ever wanted, introduce a `retail_archetype_ID` analogous to the office lookup — blocked anyway by the 2015/2022 single shopping bucket (Step 2A), so explicitly deferred.
- **Hotel — ✅ DONE (Leg 3, non-GSS), `Step6_docs/3rdJ_06_hotel_sarima_4split.py`.** No respondent, no archetype: the multiplier is **province-level** (`PR ∈ {QC, AB}`), applied per guest-room Space via Tag 2.

---

## STEP 6 — MODEL 2: FORECAST 2030 (+ THE HOTEL SIDE-TRACK)
*GSS channels reuse progressive fine-tuning; retail gets its own scenario lever; hotel is forecast by classical time-series, outside the Transformer.*

### 6A. GSS channels — ✅ DONE (Leg 3), retail head included — `Step6_docs/3rdJ_06_longitudinalForecasting_4split.py`

The four-stage progressive fine-tuning (`W_2005 → W_2010_ft → W_2015_ft → W_2022_ft`, per-transition DRIFT_MATRIX, pooled recency-weighted 2030 inference) is reused with the 3-head model. The office channel keeps its **WFH sensitivity bands** (conservative / hybrid / fullyhybrid, as built in Leg-2 Step 6/7).

### 6B. The retail scenario lever ✅ DONE (Leg 3) — `Step6_docs/3rdJ_06_retail_lever_4split.py`

The office channel's dominant 2030 lever is WFH; the retail channel's is **in-store vs e-commerce share**. DRIFT_MATRIX_1522 will absorb the COVID shopping shock, but 2030 retail presence must be reported with scenario bands exactly as office is:

- Band values (three named scenarios, Canadian e-commerce penetration + foot-traffic recovery evidence) are sourced from the deep-research report [dr_L3-04_instore_share_2030_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-04_instore_share_2030_REPORT.md). The three named scenarios for 2030 retail presence (relative to 2022 = 1.00) are: Plateau/Resilient Central (Default) = 0.97, Continued-Shift (Conservative) = 0.90, and In-Store Renaissance (Optimistic) = 1.05.
- Mechanics mirror WFH: a derived scalar (in-store shopping share during opening hours), sensitivity bands = re-run, not retrain. The lever multiplies `at_retail_fraction_2030(t)` **before** the Step-7 peak-normalization, so amplitude scenarios survive the shape-only injection (dr_L3-06 §C.3).
- **Two-province Sunday sub-axis (dr_L3-06 §C.4).** Quebec's trading-hours Act historically closes most non-exempt retail by 17:00 on Sundays (a voluntary one-year pilot from 2026-03-11 extends eligible retailers to 21:00); Alberta has been deregulated since 1985 (*R. v. Big M Drug Mart*, 1985). The 2005–2022 QC Sunday shapes encode the restriction naturally through QC respondents — no manual adjustment. For 2030, the retail lever gains a Quebec-Sunday option: **default = restricted (Sunday ≈ 0.60–0.75 × Saturday peak); optimistic = deregulated (Alberta-like uplift on the QC Sunday shape)**.

### 6C. The hotel side-track ✅ DONE (Leg 3, non-GSS) — `Step6_docs/3rdJ_06_hotel_sarima_4split.py`

```
hotel_multiplier(t, month, PR) = s(t) × monthly_occupancy_rate(month, PR)   # ISQ (QC) / CBRE (AB)
```

- **`s(t)`** — a unit-normalized 48-slot diurnal guest-room shape (max = 1.0), derived from the DOE/PNNL Large Hotel prototype guest-room schedule and resolved in [dr_L3-05_hotel_diurnal_shape_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-05_hotel_diurnal_shape_REPORT.md). The shape distinguishes weekdays from weekends/holidays. The overnight plateau is 1.00 (22:00-06:00), the morning exit ramp drops to a daytime vacancy trough of 0.200 for weekdays (09:00-15:00) and 0.308 for weekends (09:00-17:00), and the evening return ramp climbs back to 1.00.
- **Monthly amplitude** — the monthly occupancy rate per month per province/market (sourced from ISQ for QC and Alberta Economic Dashboard/CBRE for AB, see Step 1C/2D) → `0_Occupancy/processed/hotel_multiplier_lookup.csv`.
- **2030 forecast** — **SARIMA(1,1,1)(1,1,1,12) per province with a COVID indicator (2020-03…2022-06)**, NOT the Transformer (spec §3.4/§9): hotel occupancy is a population-aggregate series; classical seasonal time-series is the right tool and adds negligible compute. Output 12 monthly values per province for 2030 → `0_Occupancy/forecasts/hotel_multiplier_2030.csv`, then multiply by `s(t)`. The intervention specification (pulse vs level shift), order-selection defence, and three named 2030 hotel scenario bands (Low = 0.92, Central = 1.00, High = 1.05) are resolved in [dr_L3-09_hotel_2030_forecast_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-09_hotel_2030_forecast_REPORT.md).
- **Backcast gate** before trusting the forecast: reconstruct 2015–2019 QC + AB months, **MAE < 0.05** vs historical benchmarks (ISQ/CBRE); the 2020-04 COVID dip must be recovered without overshoot (spec §7).

---

## STEP 7 — BEM/UBEM INTEGRATION (MODULATE, NOT REPLACE)
*Extend `office_integration.py` → `commercial_integration.py`; one Tag-2 dispatch covers all four channels.*

**Injection mode per channel** (the Leg-2 asymmetry, now generalized):

| Channel | Formula | People count |
|---|---|---|
| Residential (✅ Leg 1) | `schedule(t) = presence(t)·default(t) + (1−presence(t))·baseload` | `Number_of_People = HHSIZE` |
| Office (✅ Leg 2) | `necb_office_baseline(t) × AT_WORK_fraction(t)` | NECB density (25.0 m²/person) — never HHSIZE |
| Retail (⚠️ Leg 3) | People: `0.95 × shape_c_d(t)` in customer hours (peak-normalized, dr_L3-06 — see blockquotes below); staff-only slots (baseline ≤ 0.10) keep the baseline; Lights/Plug per the Step-9 rules (opening-hours / staff) | ~~NECB retail density (~3.7 m²/person → 25.0 m²/person, not an intended retail density)~~ → 🔴 **RE-CORRECTED 08-05: the model uses 24.97 m²/person, which is NECB's *office* density (3.72 occ/1000 ft²). NECB's own retail figure is 3.10 occ/1000 ft² = 29.97 m²/person, so retail is modelled ~20 % over-crowded.** The old "~3.7" was the same number in occ/1000 ft², not a second density — see the blockquote below and V2-E3 — **do not scale the count** |
| Hotel guest rooms (⚠️ Leg 3) | `necb_hotel_guestroom_baseline(t) × hotel_multiplier(t, month, PR)` — monthly-varying | NECB hotel density — never scaled |

> 🔴🔴 **RE-CORRECTED 2026-08-05 (V2-C3 second pass) — the "~3.7" was never a competing density. It is
> the same quantity in a different unit, and finding B-11 is RETIRED.** NECB states occupancy as
> **occupants per 1000 ft²**, not as area per person. The office value is **3.72 occupants/1000 ft²**,
> and `(1000 / 10.7639) / 3.72 = ` **24.97 m²/person**. That is the `25.0` the IDF carries. The
> apparent **6.8× gap is exactly the conversion factor** (`25.0 / 3.7 = 6.76`), and it entered this
> document because the density was transcribed **without its unit**. Verified against
> `openstudio-standards` (`NatLabRockies/openstudio-standards` @ `develop`,
> `lib/openstudio-standards/standards/necb/NECB2011/data/space_types.json`, md5 `b2cb54a8`, mirrored at
> `improvements/v2/f8_necb_schedule_evidence/`).
>
> 🔴 **What IS wrong, and it is a different and smaller defect: retail carries the OFFICE density.**
> NECB's own table gives **`Retail - sales` = 3.10 occupants/1000 ft² = 29.97 m²/person**, against
> **`Office` = 3.72 = 24.97**. Our retail zones run at 24.97, so they are modelled **~20 % more crowded
> than NECB specifies for retail**. The same row of that table assigns retail to **schedule type C**,
> which the tower does not load at all (`grep -c "NECB-C-" injected.idf` = **0**) — see V2-C4 and V2-D9.
>
> The blanket-constant pattern described below is **unaffected by this correction and still stands**:
> occupancy and plug density really are one office value repeated across all 17 space types, while
> lighting really is per-space-type. What changes is only the size and the character of the density
> error — a wrong *space type*, not a wrong *order of magnitude*.
>
> ~~🔴 **CORRECTED 2026-08-04 (V2-C3, finding B-11) — retail occupant density is 25.0 m²/person, not
> 3.7 m²/person.**~~ Parsed directly from the injected IDF, self-verified for that correction:
> the `Retail Retail` / `Retail Back_Space` / `Retail Point_of_Sale` `PEOPLE` objects carry
> `0.040015 person/m²` = **25.0 m²/person** — bit-identical to `OpenOffice`. Re-run:
> ```
> grep -A6 "Retail Retail People\|OpenOffice People" \
>   3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/CAN_MTL/TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf \
>   | grep "People per Floor Area"
> # both return 0.040015  ->  1 / 0.040015 = 25.0 m²/person
> ```
> This is **not** an intended retail density (ruled out 2026-08-03, three independent checks in the
> audit below). It is one symptom of a wider pattern, confirmed by directly parsing the same IDF:
> **occupant density (`0.040015 person/m²`) and plug density (`7.5028 W/m²`) are each a single blanket
> office value repeated across all 17 space types in both towers**, while **lighting** is correctly
> parameterised per-space-type — e.g. `OpenOffice` 6.566 W/m² vs `Retail Entry` 9.042 W/m² vs
> `Retail Retail`/`Retail Point_of_Sale` 9.5 W/m², on distinct schedule families (self-verified against
> the same IDF, 2026-08-04). **Consequence, stated plainly:** office is the one channel these two
> blanket constants are plausibly right for, so correcting them can move retail, hotel and residential
> — but **cannot** move office. This *strengthens* the office band-applicability argument (V2-B1): the
> office FAIL is not explained by an occupant/plug-density error, because office already carries the
> correct constants. Source: `improvements/investigation/investigation_v2/3rdJ_L3_backward_audit_2026-08-04.md`
> §B-11 (lines 1237–1366).

> **✅ Retail normalization — RESOLVED 2026-07-02** ([dr_L3-06_retail_diurnal_targets_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-06_retail_diurnal_targets_REPORT.md)). The raw `AT_RETAIL_fraction(t)` (population fraction, peak ~0.08) is **peak-normalized per cycle** before injection — the REJECT verdict for raw-fraction direct injection is sourced and unanimous in the TUS-to-BEM literature (Richardson et al. 2010, IEA Annex 66/Haldi et al. 2017, Reinhart & Cerezo Davila 2016). The injector formula is: `retail_schedule_multiplier(t,c,d) = 0.95 × [at_retail_fraction_c_d(t) / max_t(at_retail_fraction_c_d(t))]`, where ~~0.95 is the NECB 2017/2020 retail/sales peak fraction~~ → 🔴 **CORRECTED 2026-08-04 (V2-C4).** Self-verified against the injected IDF: 0.95 is the model's *office* occupancy-schedule peak (`NECB-A-Occupancy`, which also dips to **0.5 at 12:00–14:00** — a lunch trough, the opposite of a retail midday peak); no retail-specific peak fraction was independently sourced, and `dr_L3-06`'s NECB-table citation could not be verified from public sources. **This is a stated limitation, inherited from the office baseline, not an independently sourced retail NECB value** — the injector formula and its 0.9215 = 0.95 × 0.97 output are otherwise verified exact (the mechanism is right; the constant's provenance is not). Re-sourcing from the NECB 2017/2020 tables directly is owed to V2-F-class citation work. Staff-only shoulder slots (pre-open/post-close, code fraction ≤ 0.10) are retained from the NECB baseline unmodified. The 2005→2022 level change is **deliberately routed to the Step-6B scenario lever** (dr_L3-04 multipliers, corrected measured range 1.50–2.14 % — see Step 2A), not absorbed in the normalization formula, allowing clean amplitude sensitivity analysis. 🔴 **CORRECTED 2026-08-04 (V2-C8):** the ~~Richardson et al. 2010~~ citation above is corrected. Richardson, Thomson & Infield (2008), *Energy and Buildings* 40(8), 1560–1566, and the 2010 follow-on (Richardson, Thomson, Infield & Clifford, *Energy and Buildings* 42(10), 1878–1887) were opened and read (V2-F1): they establish a **household-level first-order Markov chain over the active-occupant count S(t) ∈ {0…N}** at ten-minute resolution, with separate weekday/weekend calibration — **not** the shape-extraction/amplitude-anchoring (any-present×N-style) model this project had cited them as supporting. Full text is paywalled; this correction rests on the abstracts and methods descriptions, not a page reference. This does **not** change the REJECT verdict for raw-fraction direct injection or the peak-normalization recommendation — only the attribution.

**Tag-2 routing table** (verbatim from spec §4; dispatch is exact `Tag 2 == "<literal>"`, not substring):

| Tag 2 (verbatim from IDF) | Channel | Injection |
|---|---|---|
| `HighriseApartment Apartment` | Residential | per-household TUS, `Number_of_People = HHSIZE` |
| `HighriseApartment Corridor`, `HighriseApartment Office` | Residential (common areas) | residential multiplier on Lights only |
| `OpenOffice`, `ClosedOffice` | Office | NECB baseline × `AT_WORK_fraction(t)` |
| `Conference`, `Classroom`, `Dining`, `Restroom` | Office (support) | same as Office |
| `Retail Retail`, `Retail Back_Space`, `Retail Point_of_Sale`, `Retail Entry` | Retail | peak-normalized retail multiplier `0.95 × shape_c_d(t)` (dr_L3-06; 🔴 **0.95 = office-baseline peak, inherited — not independently retail-sourced, see the Step-7 correction blockquote above**) |
| `LargeHotel GuestRoom5`, `GuestRoom6`, `GuestRoom7` | Hotel | NECB hotel baseline × `hotel_multiplier(t, month, PR)` |
| `LargeHotel Banquet`, `Cafe`, `Kitchen`, `Lobby`, `Laundry`, `Storage`, `Corridor`, `Retail` | Hotel (support) | NECB baseline only (no modulation in v1) |
| `Corridor`, `Storage`, `Elec/MechRoom`, `Elevator Shaft`, `Elevator Lobby`, `Plenum Space Type`, `Main Electrical`, `Main Mechanical`, `Elevator Machine Room` | Service / MEP / Circulation | NECB baseline, **no modulation** |

> `HighriseApartment Office` (1 Space per prototype) is intentionally **Residential** — it serves the apartment block, not commercial tenants.

**Implementation:** extend `inject_office_schedules()` (Leg-2 `office_integration.py`) into **`inject_mixed_use()` in `eSim_bem_utils/commercial_integration.py`** — the four Tag-2 sets + per-channel `modulate_baseline()` / `modulate_baseline_monthly()` dispatch, skeleton in spec §5. `modulate_baseline()` rewrites the referenced `Schedule:Compact` / `Schedule:File` as `new(t) = baseline(t) × multiplier(t)`, leaving all density fields untouched. Fall-back guarantee: a channel with missing data reverts its Spaces to NECB baseline — the rest of the pipeline still produces valid output (spec §9).

> **🔴 HARD WIRING GATE (lesson from Leg 2, 2026-07-02).** In Leg-2 Step 8 the office injector wrote the presence multiplier to the wrong `People` field — `Schedule_Name` instead of **`Number_of_People_Schedule_Name`** (`office_integration.py:254`). EnergyPlus accepted the IDF silently and **all 7 office scenarios simulated byte-identical**; inputs looked fine, outputs were flat (probe job 1057830). `commercial_integration.py` must therefore ship with a post-injection assertion, per Space: *every schedule the injector claims to have modulated is actually referenced by the correct IDF field* (`Number_of_People_Schedule_Name` for People; the analogous named fields for Lights / ElectricEquipment), and the modulated series differs from baseline wherever the multiplier ≠ 1. This gate runs at injection time, before any simulation is queued.

---

## STEP 8 — BEM SIMULATION
*Add retail + hotel zones to the 2-city sweep; two mandatory probes before any campaign.* ✅ DONE (Leg 3) — `Step8_docs/3rdJ_08D_campaign_cells.py`, 56/56 cells run

- **Design:** end-to-end runs of the geometry-identical prototypes — `CAN_MTL/*Z6_v221.idf` (Montreal 6A, McTavish EPW) and `CAN_CLG/*Z7A_v221.idf` (Calgary 7A, Olympic Park EPW); SuperTall **135,857.6 m²** / Tall **72,623.1 m²** (parsed; superseded legacy values in the blockquote below) verified identical across cities, so EUI deltas isolate climate. Scenarios: Default (NECB baseline) vs per-cycle (2005/2010/2015/2022) vs 2030 bands (office WFH × retail in-store × hotel SARIMA).

> **✅ Prose synced 2026-08-04 (finding G-1, reproducing B-8 blind) to the parsed values the header
> 🔴 CORRIGÉ blockquote (line 18 above, Défaut 7, 2026-07-31) already established; this Step-8 body
> text was the one place still quoting the superseded 40,846 / 26,750 m². Per cell, these areas are
> emitted in [`Step8_docs/outputs_step8/agg/agg_meta.csv`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/outputs_step8/agg/agg_meta.csv) (`total_building_area_m2`), never retyped by hand.
- **Output:** one EUI table per **scenario × climate × channel**, plus load-shape and peak-timing metrics per channel band (annual EUI is secondary — the contribution is the load shape, as in Legs 1–2).
- **Reporting spec (locked 2026-07-02, [dr_L3-10_mixeduse_reporting_positioning_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-10_mixeduse_reporting_positioning_REPORT.md)):**
  - **Dual-basis EUI per channel:** (1) **Conditioned Floor Area** of the channel's Spaces — the primary, thermodynamic basis; (2) **occupiable share of Gross Floor Area** — the stock-comparison basis for the SCIEU/CEUD INFO bands. Expect the CFA basis to read ~5–10 % higher than GFA-basis databases (the known "basis mismatch" — the Leg-2 SingleD-WARN analogue); state the basis on every table and figure.
  - **Central-plant attribution:** **hourly load-weighted allocation** — each timestep, split shared chiller/boiler electricity and gas across the four channels by their share of total simulated coil load. Never area-weighted, never left unattributed ("arbitrary plant allocation" is a standard reviewer criticism, dr_L3-10 Table 4).
  - **Service/MEP (20.6 % · 21.4 % of gross, measured — superseded value in the blockquote below):** prorated by area onto the four tenant channels (floor area plus core lighting / elevators / circulation ventilation) whenever comparing to SCIEU-style stock EUIs; kept as a separate fifth "core" row in the as-modelled tables.

  > **✅ Prose synced 2026-08-04 (rest of B-8)** to the "Service/MEP, % du brut" row of the header
  > 🔴 CORRIGÉ blockquote (line 32 above, Défaut 7, 2026-07-31): **20.64 % (SuperTall) / 21.41 %
  > (Tall)** of gross, measured by `parse_channel_areas()` in `3rdJ_08E_aggregate_4split.py`
  > (Step8_docs) from each injected IDF's `Zones.FloorArea × Multiplier` — not the "~52 % gross"
  > placeholder. `3rdJ_08E_aggregate_4split.py` has always prorated by this *measured* per-cell
  > share (verified: no `0.52` literal anywhere in the aggregator), so no GFA-share EUI already
  > produced is affected — only this prose was stale. The area-weighted prorating **operation**
  > above is unchanged; it redistributes a smaller service/MEP quantity (~21 %, not ~52 %) onto the
  > four tenant channels, so GFA-share EUIs move *less* than the old prose implied.
  - **Figure set:** stacked diurnal load curves (winter + summer, weekday + weekend, all four channels coincident — the load-timing story) and per-channel end-use EUI stacked bars (heating, cooling, fans, pumps, interior lighting, equipment, DHW).
- **EUI plausibility gates**, following the Leg-2 office pattern (as-modelled prototype band = pass criterion; empirical survey band = INFO):
  - 🔴 **Office EUI Bands — ADDED 2026-08-05 (V2-D4). This band has been live in the scorer since Leg-2 and was never written down here.** That is exactly backwards for the one band whose floor is contested and whose citation was found unresolvable: the blocking gate was the *only* one a reader could not check against a document. Inherited from Leg-2 (`Leg2_2-split/Step8_docs/deepResearch/Office Reference EUI (NECB 2020, ASHRAE 90.1, DOE-PNNL prototypes) — As-Modelled Bands.md`, Table 7.1): as-modelled band **(low 100, central 135, high 200) kWh/m²/yr** = **PASS criterion**; empirical band **(low 170, central 230, high 360) kWh/m²/yr** = **INFO criterion** (SCIEU/CEUD). **`rule: all-cells`.** 🔴 **PROVENANCE CORRECTED 2026-08-06 (V3-H3): the VALUES are inherited from Leg-2; the RULE and the SEVERITY are not.** Leg-2 scored these same numbers on the **channel median**, and graded a miss **WARN** — twice, independently: `Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.py:462-470` (gate `G2o`, `med = o["eui_kWh_m2"].median()`, `PASS if okb else WARN`) and `Leg2_2-split/Step8_docs/3rdJ_08_simulation_2split_val.py:1420-1431` (gate `4.3-office`, median, WARN, the text says *"non-blocking"*). Leg-3 applied `all_cells` **and** FAIL without recording that it had changed either. **Nothing here changes the rule** — the correction is to the citation, and adopting Leg-2's convention is V3-H3's open decision, with the caveat that Leg-2's convention is *median AND WARN together*: taking only the median half is neither leg's rule. ⚠️ **The floor of 100 is CONTESTED AND UNSOURCED** — see decision 3 in the blockquote below; the value is published as contested and is **not** moved.
  - **Retail EUI Bands:** Locked via [dr_L3-02_retail_eui_bands_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-02_retail_eui_bands_REPORT.md) (2026-07-02): as-modelled band **(low 80, central 110, high 155) kWh/m²/yr** = **PASS criterion**; empirical band **(low 150, central 280, high 380) kWh/m²/yr** = **INFO criterion**. **`rule: median-in-band`** (V2-B3, 2026-08-05 — values unchanged, criterion changed).
  - **Hotel EUI Bands:** Locked via [dr_L3-03_hotel_eui_bands_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-03_hotel_eui_bands_REPORT.md) (2026-07-02): as-modelled band **(low 180, central 240, high 300) kWh/m²/yr** = **PASS criterion**; empirical band **(low 220, central 350, high 480) kWh/m²/yr** = **INFO criterion**. **`rule: all-cells`.** ⚠️ The *citation* for the as-modelled band moved on 2026-08-05 (V2-B2) — see decision 1 below; **the values did not**.

> 🔴🔴 **BAND DECISIONS — TAKEN 2026-08-05 (V2-B1 / V2-B2 / V2-B3, propagated here by V2-C6).**
> **No band value was widened, and all three EUI gates that were failing are still failing.** That is
> the intended outcome: the decisions fix *provenance* and *decision rules*, not thresholds. Recorded
> here because these three gates are the ones a reader will check first.
>
> **1. Hotel — the 300 ceiling STANDS, and its citation MOVES.**
> `dr_L3-03`'s two primary sources were chased to the end and **neither exists** (V2-F4: one `NOT
> FOUND`, the other, `PNNL-28543`, resolves to a nuclear-fuel report — confirmed twice, independently).
> The band was therefore unsupported, not wrong. **We retrieved a replacement ourselves** (V2-F6):
> the DOE/PNNL **Large Hotel** prototype at **ASHRAE 90.1-2019** reads **284.44 kWh/m²·yr in CZ 6A
> (Rochester MN)** and **299.28 in CZ 7 (International Falls MN)**, parsed from
> `Site and Source Summary` in the ZIP's own `.table.htm`
> (`energycodes.gov/sites/default/files/2023-10/ASHRAE901_HotelLarge_STD2019.zip`; evidence and parser
> in `improvements/v2/f6_prototype_evidence/`). The old ceiling rested on the 90.1-2004 lineage's
> **302.21**; the vintage-matched value is **299.28**, **1.0 % away**. **So the standing objection —
> "a 2004 band is being used to score a 2019/NECB-2017 building" — is dead, and `S9-EUI-hotel` is not
> a vintage artefact.** It still **FAILs on ~~21~~ 28 of 56 cells, all over the ceiling, all `Tall`,
> zero `SuperTall`.**
>
> ~~🔴 **CORRECTION 2026-08-06 (V4-A2/A3, struck not deleted): that sentence describes the K=6
> DHW-resize arm, not the Step-9 artefact this document scores.** In `outputs_step9/step9_gates.json`
> the hotel gate reads **28 of 56 failing, every one of them UNDER the 180 floor, all `SuperTall`,
> zero `Tall`** — range **147.9–209.4** against a ceiling of 300, so **no cell is over the ceiling at
> all.** The two arms fail at **opposite ends** and the count differs; quoting one under the other's
> heading is the same defect as the office `band_src` and the `all_cells` rule citation.~~
>
> 🔴🔴 **RETRACTION 2026-08-06, later the same day (V4-A4). The correction immediately above is wrong
> and the original sentence was right.** It was computed from `Step9_docs/outputs_step9/`
> (**2026-07-31 11:42**), which is **not** the artefact this document scores. The frozen deliverable is
> `Step9_docs/outputs_step9_deliverable/` (**2026-08-06 00:05**), named as such in
> `improvements/v2/V2-G1_FROZEN_DELIVERABLE.md`, and in it the hotel cells run **203.33–318.42** with
> **28 above the 300 ceiling, 0 below the 180 floor**, and `verdict_asmodelled` tallying **`Tall` 28
> FAIL / `SuperTall` 28 PASS**. **Over the ceiling, `Tall`-only, zero `SuperTall` — exactly as
> originally written.** The superseded directory predates `V2-D10`, the per-object `LAUNDRY` resize
> that moved this channel, and the inversion **was already recorded** in
> `3rdJ_L3_manager_prompt_2026-08-06_v2_close.md` §V2-E5 (*"the failing end inverted while the count
> held still"*). **The count is the one part genuinely wrong: 28, not 21** — 21 matches neither the CFA
> basis (28 out) nor the GFA-share basis (14 out), and its provenance is not established.
> ⚠️ **This retraction is the same defect the correction accused this document of** — a number
> imported from a neighbouring artefact without its label — committed in the correction itself.
> Full derivation: `improvements/v4/V4-A4_split_scorecard.md` §5.
> ⚠️ **Stated limitation, not a tolerance:** our tower is **NECB-2017,
> Montréal/Calgary**; the reference prototype is **90.1-2019, Rochester / International Falls**. The
> archetype and city sets do not match, and that goes in the limitations section (V2-G3) rather than
> into a widened band.
>
> **2. Retail — the gate rule is MEDIAN-IN-BAND, not 56-of-56.** Decided at V2-B3 and stated in
> advance of the numbers. Rationale: the retail gate was turning on **0.15 % of its floor** — V2-E3
> moved the median by −0.05 % and that flipped one cell (55/56 → 54/56). **An all-cells rule on a
> quantity whose spread is smaller than its own uncertainty reports noise as a verdict.** The retail
> **rate** gate is demoted to **INFO** (V2-D6): its only time-of-day reference, BLS ATUS A-3B, says we
> are ~44 % *high* while the previous band said 24.5 % *low* — the two references **disagree in
> direction**, so neither can arbitrate. The retail **shape** gates stay PASS/FAIL.
>
> **3. Office — the band's applicability is the finding, and the floor is CONTESTED.**
> The `S9-EUI-office` FAIL is **not an occupancy problem**: the *uninjected* `Default_NECB` control
> fails it too, and the band's floor of **100** sits **above NECB's own uninjected tower at 85.45**.
> A gate no untreated control can pass is measuring the band, not the model. Two candidate mechanisms
> were tested and **both refuted** (heating share 17 % vs the band's 35–45 %; rebasing on Service/MEP
> moves all 56 cells *down*). 🔴 **And the band's own citation does not resolve:** its `src=` string
> points at a directory that does not exist (V2-D4 provenance pass, `3rdJ_09_bench_provenance_check.py`,
> seen failing 3/3). **The floor is therefore recorded as contested and unsourced**; the gate is
> written up as a **band-applicability limitation**, not as a model defect, and **the value is not
> moved to make it pass.**
>
> **4. THE RULE PRINCIPLE — written down 2026-08-06 (V3-H3), because until now `rule` was a
> per-channel value with no stated criterion for choosing it.** Default = **`all_cells`**.
> **`median` applies only where a channel's across-cell spread is small enough that a re-run's own
> noise can flip the verdict** — V2-B3's condition, verbatim. Measured across-cell range / band
> width on the shipped deliverable: **office 0.285 · retail 0.443 · hotel 0.959.** Retail is the one
> channel where V2-E3 demonstrated that noise (a −0.05 % median move flipped a cell); **hotel's cells
> span 96 % of its own band**, so they differ genuinely and `all_cells` reports signal there.
> **Applying the principle changes NOTHING** — office and retail FAIL under both rules, hotel keeps
> `all_cells`. ⚖️ **Disclosure:** the spreads were measured *after* it was known which rule clears
> hotel, so **no numeric boundary is written** — only the condition. 🔴 **And the case against this
> choice is on file too**: Leg-2 scored the office band on the **median** and graded a miss **WARN**,
> so "restore the precedent" is an honest argument — but Leg-2's convention is *median **and** WARN
> together*, and adopting it whole turns the EUI block from **3 FAILs into 1 PASS + 2 WARNs**. A
> basis change that turns FAIL into WARN is a band change in disguise (the 2026-07-21 R1 decision,
> re-affirmed 2026-08-05). Reopens if the user accepts the precedent argument, if a channel's spread
> ever falls below its own re-run noise, or if the frozen deliverable is reopened for another reason.
>
> **4. Hotel DHW plant (V2-B4) — per-object resize, not a global K.** At K = 6 every heater except
> `LAUNDRY` has slope exactly 0.000, and `LAUNDRY` is capacity-pinned in both arms, so the sweep sized
> sixteen objects with the factor that fixes one: it changed the *shares*, not the physics.
> `LAUNDRY` alone goes to **K ≈ 7**, targeted on the internal reference `BOOSTER` (same 180 °F
> setpoint, never clipped, 71.34 K); the other fifteen heaters stay at **K = 1**. Implementation is
> **V2-D10**.

> **🔴 TWO MANDATORY PROBES (lessons from Leg 2, 2026-07-02) — run BEFORE the full campaign:**
> 1. **Scenario-differentiation probe.** Simulate one building for ≥ 2 scenarios per channel and diff the outputs. **Byte-identical results across scenarios = automatic FAIL** — the modulation is not reaching the engine, regardless of how correct the inputs look.
> 2. **Stale-output guard.** After any wiring fix, `skip_done`-style completion checks must be invalidated (fingerprint the injector version into the output path or force a clean re-run). Leg 2's flat outputs survived one fix attempt purely because old results were skipped as "done".

> **Paper positioning (dr_L3-10 novelty matrix).** The unclaimed combination = **one longitudinal TUS
> database (GSS 2005–2022 + 2030 forecast) driving four channels inside a single vertically stacked
> mixed-use tower**. Closest priors to cite-and-differentiate in the 3rd-Journal related work:
> **Doma & Ouf (2023, 2024)** — mixed-use Montreal, but SafeGraph mobility snapshots, district-scale
> separate buildings, no forecast; **Buttitta & Finn (2020)** and **Widén & Wäckelgård (2010)** —
> TUS-driven but residential-only, single-wave. Reviewer-exposure checklist the design already answers:
> occupant double-counting across zones (→ the dr_L3-12 exclusivity projection), EUI basis mismatch
> (→ dual-basis reporting), arbitrary plant allocation (→ the hourly load-weighted rule); acknowledge
> ground-level EPW on a supertall (no altitudinal temperature/wind gradient) as a stated limitation.
> The draft one-sentence contribution statement lives in the report's Part C §3.

---

## STEP 9 — ACTIVITY-DRIVEN END-USE LOADS
*Extend the unified activity-driven analysis from 2 to 4 channels — equal importance ≠ identical parameters.* ✅ DONE (Leg 3) — `Step9_docs/3rdJ_09_activityDrivenLoads_4split.py`, 30 gates scored

- **Retail:** lighting and HVAC follow **opening hours** (near-flat while open, off overnight); plug loads follow **staff**, not footfall — customer presence (our GSS signal) modulates People-driven gains, while the staff-driven plug baseload stays in the NECB baseline. Keep the Leg-2 floors: `Lmin` egress lighting, `Pbase` never-zero plug loads.
- **Hotel:** guest-room equipment + lighting scaled by `s(t) ×` monthly amplitude; amenity zones stay baseline (consistent with Step 7 v1).
- **Calibration:** anchor commercial magnitudes to NRCan SCIEU (the commercial analogue of the SHEU anchoring used for residential), per channel.
- **Output:** the Leg-2 Step-9 tables (`eui_by_channel`, `loadshape_peaks`, `longitudinal`, `scenario_response`) extended to four channels, reported on the dr_L3-10 dual basis (CFA primary, GFA-share for stock comparison) with hourly load-weighted central-plant attribution.

---

## VALIDATION PLAN
*The Leg-2 three-tier gates applied per new channel, plus channel-specific gates from the spec, plus the two Leg-2-lesson wiring gates.*

**Tiered gates (per day-type, applied to AT_RETAIL as they were to AT_WORK):**

| Tier | Metric | Threshold |
|---|---|---|
| **1 Distributional** | KL (arrival/departure) | < 0.05 |
| 1 | 1-Wasserstein / EMD on hourly presence CDF | < 0.05 |
| 1 | Presence-rate RMS error | ≤ 5 pp per day-type |
| **2 Structural** | Transition-matrix Frobenius/MAE | < 0.05 |
| 2 | Dwell-time KS test | fail to reject H₀ (p > 0.05) |
| 2 | Autocorrelation MAE, lags 1–24 h | < 0.05 |
| **3 Downstream (ASHRAE G14)** | NMBE | monthly ±5 %, hourly ±10 % |
| 3 | CV(RMSE) | monthly 15 %, hourly 30 % |
| 3 | Peak demand + timing shift | magnitude ±15 %; timing ≤ 1 h |

**Channel-specific gates (spec §7 + Steps above):**

| Layer | Check | Target |
|---|---|---|
| LOCATION mapping | per-cycle AT_RETAIL rate, weekday 12:00–14:00 | 0.06–0.10 (CONFIRMED by dr_L3-06, central ≈ 0.079) |
| LOCATION mapping | Saturday peak rate, 13:00–16:00 | 0.09–0.12 (dr_L3-06 — distinct Saturday gate) |
| LOCATION mapping | Sunday peak rate, per city | Calgary 0.06–0.10 · Montreal 0.04–0.07 (dr_L3-06 — province-specific) |
| LOCATION mapping | night slots 00:00–05:00, all day types | 0.000–0.003 |
| OR-rule leak | `occACT==4 & occPRE==1` share excluded from AT_RETAIL, per cycle | rule FROZEN (gated, OD-1 2026-07-02); cross-tab still reported as verification |
| Transformer (JS) | JS(AT_WORK), JS(AT_RETAIL) per stratum | < 0.02 each (Note: JS is toothless for AT_RETAIL; must be paired with PR-AUC/F1 gates) |
| Transformer (Resolution) | PR-AUC and F1-score on positive slots for AT_RETAIL | PR-AUC ≥ 0.15, F1-score ≥ 0.25 (to catch all-zeros failure) |
| Transformer (Dynamics) | Midday (11-14h) rate error & transitions per day for AT_RETAIL | Midday error ≤ 3.0 pp, transitions ≥ 0.05 transitions/day |
| Transformer (Regression) | Old head (Head 1 & Head 2) JS drift | ΔJS ≤ 0.002 bits vs Leg-2 validation baseline |
| Transformer (Exclusivity) | Impossible-State Rate: slots with > 1 of {AT_HOME, AT_WORK, AT_RETAIL} active | ISR ≤ 0.5 % on raw outputs; = 0 % after the decode-time projection (Step 4b, dr_L3-12) |
| Hotel backcast | Historical QC + AB monthly occupancy 2015–2019 vs reconstruction | MAE < 0.05 |
| Hotel COVID dip | 2020-04 reconstruction | recovers the low without overshoot |
| Wiring | post-injection field-reference assertion (Step 7 gate) | 100 % of modulated Spaces pass |
| Simulation | scenario-differentiation probe (Step 8 gate) | outputs differ across scenarios, per channel |
| BEM end-to-end | Default vs 2022, Montreal SuperTall | EUI delta positive, dominated by Office + Hotel bands |
| Floor-area sanity | per-channel EUI shares vs parsed occupiable shares | within ±2 pp |

> **Threshold provenance (inherited from Leg 2 — keep the discipline).** NMBE and CV(RMSE) values = **ASHRAE Guideline 14** (cite the standard). The `< 0.05` / ±15 % / ≤ 1 h gates, the 0.06–0.10 retail rate (project-chosen, since externally CONFIRMED by dr_L3-06; its Saturday 0.09–0.12 and QC-Sunday 0.04–0.07 companions are dr_L3-06-derived, medium confidence), the hotel MAE < 0.05, the ISR ≤ 0.5 % bar, the decode thresholds (0.50 / 0.40 / 0.15), and the ±2 pp EUI-share gate are **project-chosen acceptance bars**, set before tuning — do not cite them to the literature (dr_L3-10 confirms the ±2 pp gate is project-novel: ASHRAE 211 suggests the comparison, no code enforces it; dr_L3-11/13 flag PR-AUC ≥ 0.15 / F1 ≥ 0.25 as heuristic — relax to PR-AUC ≥ 0.10 only if diary noise demands it, and say so in the paper). Select models on the **Pareto frontier**, operationalized per dr_L3-13 as **gate-first filtering → lexicographic selection (maximize retail F1 among survivors)** — never a single composite; the Leg-1 lesson.

---

## KEY DESIGN DECISIONS

| Decision | Rationale |
|---|---|
| Four channels, not one unified "occupant" channel | Each use has a distinct underlying population (household members, workforce, customers, guests); conflating them smears the longitudinal signal the project depends on. |
| Hotel sourced from ISQ / CBRE tourism stats, not GSS | The GSS frame excludes hotel guests by construction; GSS-driven hotel zones would be systematically under-occupied. |
| Office / Retail / Hotel **modulate**; Residential **replaces** | Preserves code-of-record peak densities (W/m², people/m²) for regulatory comparability; injects only the *temporal* signal. Residential is per-household and idiosyncratic — replacement is the right semantic. |
| Retail = customer presence only; staff stay in the baseline | GSS logs retail staff as AT_WORK; the NECB baseline being modulated already embodies worker density (SCIEU-consistent). |
| Hotel forecast via SARIMA, not the Transformer | The Transformer conditions on individual respondents; hotel occupancy is a population-aggregate monthly series. Three GSS heads + a SARIMA side-track (spec §3.5) is authoritative over the diagram's "4 heads". |
| Tag 2 is the per-Space routing key | PNNL Tall/SuperTall prototypes leave `Space Type` blank; Tag 2 is the function string carried by OpenStudio Standards (verified by parsing both IDFs). |
| Service / MEP / Circulation (20.6 % · 21.4 % of gross, measured — see Step-8 blockquote) left on NECB baseline | No occupant-driven demand worth modelling; no GSS signal exists for it. |
| 4-channel is strictly additive on 2-channel | A missing channel falls back to NECB baseline; residential and office injection are unchanged, so no prior Leg-1/Leg-2 figure is invalidated. |
| Scenario levers: WFH (office) + in-store share (retail) + SARIMA trend (hotel) | Each channel's dominant 2030 uncertainty gets an explicit, re-runnable sensitivity band — the reviewer-defusing pattern proven in Leg 2. |
| Geometry-identical CLG + MTL IDFs as a 2-city sweep | Identical floor areas isolate the climate signal, holding occupancy + geometry constant. |
| Wiring + differentiation gates are mandatory, not advisory | The Leg-2 office People-field bug produced silently flat results that passed every input-side check; only output-side differentiation catches this class of failure. |
| Independent binary heads + decode-time exclusivity projection, not a categorical location head | Softmax competition would crush the ~2 % retail class and force a Head-1 migration; the Threshold-Normalized Argmax Projection keeps per-channel calibration AND guarantees one-place-at-a-time (dr_L3-12). |
| Fixed-weight loss scalarization + PCGrad, not SLAW/UW/GradNorm | Dynamic balancers destabilize when one task is ~2 %-positive; well-tuned fixed weights match or beat them at 2–4 tasks (Kurin et al. 2022, via dr_L3-13). |
| Dual-basis per-channel EUI + hourly load-weighted plant allocation | CFA is the thermodynamic truth; the GFA-share basis makes the SCIEU/CEUD INFO bands comparable; a load-weighted plant split is the only defensible tenant attribution (dr_L3-10). |

---

## OPEN DECISIONS (resolve before/within Leg 3)

1. **OR-rule refinement (Step 2B) — RESOLVED 2026-07-02 (user decision).** Activity arm gated: `AT_RETAIL = (occPRE == 5) | ((occACT == 4) & occPRE.isin({5, 9}))`. The per-cycle online-shopping leak cross-tab is **still produced** as a Step-2 validation output, and the gating **adds to — never replaces —** the LOCATION-mapping rate gates and the co-presence channel checks, which stay fully in force (user condition). Consequence for Step 4: `AT_HOME ∧ AT_RETAIL` is not a legitimate overlap, so the dr_L3-12 projection covers the full three-channel set.
2. **Retail 2030 scenario band values — RESOLVED 2026-07-02.** Sourced from deep-research report [dr_L3-04_instore_share_2030_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-04_instore_share_2030_REPORT.md). The three named scenarios for 2030 retail presence (relative to 2022 = 1.00) are defined as: Plateau/Resilient Central = 0.97 (default), Continued-Shift (Conservative) = 0.90, and In-Store Renaissance (Optimistic) = 1.05. These multipliers scale the customer occupancy presence fraction, leaving baseline peak densities intact. The lever scales presence amplitude only, keeping the diurnal shape fixed, with a more resilient central scenario justified for grocery-anchored podium retail.
3. **StatCan hotel table ID, coverage and breaks — RESOLVED 2026-07-02.** Verified in [dr_L3-01_statcan_hotel_data_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-01_statcan_hotel_data_REPORT.md) that Table 24-10-0048-01 does not exist. No Statistics Canada table provides monthly occupancy rates, ADR, or RevPAR by province. Sourced instead from Tourisme Québec / ISQ (for QC, 2005–2022 monthly) and Travel Alberta / Alberta Economic Dashboard (sourced from CBRE, for AB, 2010–2022 monthly), with 2005–2009 for AB spliced from CBRE National Market Report archives.
4. **Hotel diurnal shape `s(t)` numbers — RESOLVED 2026-07-02.** Sourced from deep-research report [dr_L3-05_hotel_diurnal_shape_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-05_hotel_diurnal_shape_REPORT.md). Recommended unit-normalized 48-slot curve (max = 1.0) derived from the PNNL Large Hotel prototype guest-room schedule, with distinct weekday and weekend variants. The weekday shape has an overnight plateau of 1.00 (22:00-06:00), morning checkout ramp down to a trough of 0.200 (09:00-15:00), and evening return. The weekend shape has an overnight plateau of 1.00 (19:00-21:00 and 00:00-06:00) and a shallower trough of 0.308 (09:00-17:00). A fixed shape scaled by the monthly occupancy rate is defensible due to human circadian stability, and the trough depth deviation from the flat 0.80 NECB baseline is highly energy-material.
5. **Retail + hotel EUI plausibility bands.** Retail EUI bands RESOLVED (2026-07-02, [dr_L3-02_retail_eui_bands_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-02_retail_eui_bands_REPORT.md)): as-modelled band **(low 80, central 110, high 155) kWh/m²/yr** = **PASS criterion**; empirical band **(low 150, central 280, high 380) kWh/m²/yr** = **INFO criterion**. Hotel EUI bands RESOLVED (2026-07-02, [dr_L3-03_hotel_eui_bands_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-03_hotel_eui_bands_REPORT.md)): as-modelled band **(low 180, central 240, high 300) kWh/m²/yr** = **PASS criterion**; empirical band **(low 220, central 350, high 480) kWh/m²/yr** = **INFO criterion**. 🔴🔴 **SUPERSEDED IN PART, 2026-08-05 (V2-C6) — see the full band-decision blockquote in §"EUI plausibility gates" above.** In one line each: **hotel** — `dr_L3-03`'s two primaries do not exist (V2-F4), the **300 ceiling stands** and is re-cited to the first-party **Large Hotel 90.1-2019 = 284.44 (CZ 6A) / 299.28 (CZ 7)** we retrieved ourselves (V2-F6), which is **1.0 %** from the 302.21 the ceiling was built on, so the vintage objection is dead and the gate still **FAILs ~~21/56~~ 28/56, all `Tall`, all over the ceiling** (count corrected 2026-08-06 by V4-A4 against the frozen deliverable; the direction was always right); **retail** — the rule is now **median-in-band**, not 56-of-56, and the *rate* gate is demoted to **INFO**; **office** — the floor of 100 is **contested and its `src=` does not resolve**, so the gate is a **band-applicability limitation**. **No band value was widened.**
6. **Hotel amenity-zone modulation — RESOLVED 2026-07-02 (user-confirmed).** v1 leaves Banquet/Cafe/Kitchen/Lobby on NECB baseline (weakly coupled to room occupancy); revisit only if the Step-8 hotel EUI gate (as-modelled 180–300 kWh/m²/yr) fails. ⚠️ **Update 2026-08-05: it did fail** — ~~21~~ **28** of 56 cells sit over the 300 ceiling. The trigger condition written here is therefore met, but the located mechanism is the **DHW plant** (V2-B4 → V2-D10, `LAUNDRY` capacity-pinned), not amenity modulation, and **the failures are `Tall`-only with zero `SuperTall`**, which points at the geometry axis rather than at amenity zones. **Revisiting amenity modulation is deliberately NOT on the task list**; recorded here so the unmet trigger is not mistaken for an oversight. ~~🔴 **CORRECTION 2026-08-06 (V4-A2/A3): the two struck clauses describe the K=6 resize arm, not Step 9.** In the Step-9 artefact the hotel failures are **28 of 56, all UNDER the 180 floor, `SuperTall`-only with zero `Tall`** — **the exact inverse of the sentence above**, at the opposite end of the band. **The conclusion drawn here survives and is in fact strengthened**: the failure still sits on the geometry axis rather than on amenity zones, and the Step-9 artefact shows it more sharply — hotel EUI moves by **≤0.70 %** when occupancy is injected, so amenity modulation could not plausibly reach it either. **But the conclusion was reached through an inverted reading of the evidence**, and a resolved open decision resting on a number from the wrong arm is recorded as such rather than quietly re-justified.~~ 🔴🔴 **RETRACTED the same day (V4-A4): the correction above is wrong and this decision never argued from a wrong arm.** It compared against `Step9_docs/outputs_step9/` (2026-07-31) rather than the frozen `Step9_docs/outputs_step9_deliverable/` (2026-08-06 00:05). In the deliverable the hotel failures are **28 of 56, `Tall`-only, every one OVER the 300 ceiling**, range **203.33–318.42** — **as this entry originally said.** Only the count 21 was wrong. **This resolved decision therefore stands on the evidence it actually cited, and its footing is restored.** The supporting point holds and is stronger on the deliverable: injection moves hotel EUI by **≤1.00 %** (−1.55 to +2.60 kWh/m²/yr) against an empty gap of **84.64** between the two geometry clusters, so amenity modulation could not plausibly reach it either. Derivation: `improvements/v4/V4-A4_split_scorecard.md` §4–§5.
7. **Office→retail lunch cross-use transition — RESOLVED 2026-07-02.** Keep the simulation channels independent (Option a) to prevent frame mismatch, double-counting, and identifiability issues, but calculate and present the GSS-derived conditional transition probability as an offline diagnostic figure (Option b) to capture cross-use novelty. This choice is justified by building energy simulation studies (e.g., Feng et al., 2020) showing that schedule coupling has negligible energy materiality (< 1.5% retail cooling load delta), as detailed in [dr_L3-07_crossuse_lunch_coupling_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-07_crossuse_lunch_coupling_REPORT.md).
8. **Interpolate-to-Timestep (`Yes`/`No`) — RESOLVED 2026-07-02 (user-confirmed).** Inherit whatever Leg 2 chose for `Schedule:File` @ 30-min; apply uniformly to retail + hotel schedules; record the inherited value in the Step-7 doc when the injector is built.
9. **Restaurant channel (`occPRE == 7`).** Explicitly out of scope for Leg 3 (Step 2C) — no prototype Space to drive; revisit only with a different building archetype.
10. **Transformer rare head training recipe (dr_L3-08) — RESOLVED 2026-07-02.** Sourced from deep-research report [dr_L3-08_rare_head_extension_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-08_rare_head_extension_REPORT.md). We recommend a Head-only Warmup (5 epochs) followed by Joint Fine-Tuning (15 epochs) with PCGrad. Rarity is addressed using BCE loss with $pos\_weight = 49$, corrected post-hoc by subtracting $\ln(49) \approx 3.89$ from raw logits during inference to ensure probability calibration. The old heads are protected using regression gates ($\Delta JS \le 0.002$ bits), and the toothless JS gate is augmented with PR-AUC $\ge 0.15$ and F1 $\ge 0.25$ gates to catch all-zeros failure (which passes bare JS with 0.010 bits).
11. **Retail multiplier normalization + diurnal validation targets — RESOLVED 2026-07-02.** Sourced from deep-research report [dr_L3-06_retail_diurnal_targets_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-06_retail_diurnal_targets_REPORT.md). Raw-fraction injection is REJECTED (collapses retail to ~8% of design load; no published TUS-to-BEM precedent). **Peak-normalization per cycle is RECOMMENDED** (Richardson et al. 2010; IEA Annex 66/Haldi et al. 2017; Reinhart & Cerezo Davila 2016): `retail_schedule_multiplier(t,c,d) = 0.95 × shape_c_d(t)` where `shape_c_d(t) = at_retail_fraction_c_d(t) / max_t(at_retail_fraction_c_d(t))`. 🔴 **CORRECTED 2026-08-04 (V2-C4):** the 0.95 constant is, on citation check, the injected model's *office* occupancy-schedule peak (`NECB-A-Occupancy`), not an independently sourced NECB retail/sales peak fraction — self-verified against the injected IDF; carried as a stated limitation, re-sourcing owed to V2-F citation work. This does not change the RESOLVED normalization *method*, only the constant's provenance label. The 2005→2022 level trend is routed to the Step-6B scenario lever, not the normalization formula — 🔴 **measured range corrected 2026-08-04 (V2-C5): 1.50–2.14 %, declining ~25 %, not "~2.1–2.3 % stable"; see Step 2A.** Validation gates: weekday 12:00–14:00 gate **0.06–0.10 CONFIRMED** (central estimate ~0.079); new Saturday 13:00–16:00 gate **0.09–0.12**; Sunday Calgary **0.06–0.10**; Sunday Montreal **0.04–0.07** (historically regulated; Quebec 2026 pilot adds uncertainty for 2030). Night gate: 0.000–0.003 all day-types. 🔴 **CORRECTED 2026-08-04 (V2-C8):** the ~~Richardson et al. 2010~~ citation above is corrected. Richardson, Thomson & Infield (2008), *Energy and Buildings* 40(8), 1560–1566, and the 2010 follow-on (Richardson, Thomson, Infield & Clifford, *Energy and Buildings* 42(10), 1878–1887) were opened and read (V2-F1): they establish a **household-level first-order Markov chain over the active-occupant count S(t) ∈ {0…N}** at ten-minute resolution, with separate weekday/weekend calibration — **not** the "shape_c_d(t) × 0.95" any-present×N-style peak-normalization model this project had cited them as supporting. Full text is paywalled; this correction rests on the abstracts and methods descriptions, not a page reference. The RESOLVED normalization method and its recommendation are **unaffected** — only the attribution changes; IEA Annex 66/Haldi et al. 2017 and Reinhart & Cerezo Davila 2016 remain the load-bearing citations for the shape/amplitude method itself.
12. **Step-8/9 per-channel reporting basis + paper positioning — RESOLVED 2026-07-02.** Sourced from deep-research report [dr_L3-10_mixeduse_reporting_positioning_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-10_mixeduse_reporting_positioning_REPORT.md). Dual-basis EUI reporting (CFA primary + occupiable GFA share for stock comparison), hourly load-weighted central-plant allocation, service/MEP (20.6 % · 21.4 % of gross, measured — superseded value in the Step-8 blockquote) prorated by area for SCIEU comparability, and the ±2 pp EUI-share sanity gate confirmed as project-novel (ASHRAE 211 suggests the comparison; no code enforces it). The novelty matrix confirms the contribution combination — one longitudinal TUS source → four channels → single stacked tower → 2030 forecast — is unclaimed; closest priors to differentiate: Doma & Ouf (2023/2024), Buttitta & Finn (2020), Widén & Wäckelgård (2010). Reporting spec + positioning blockquote encoded in Step 8.
13. **Step-4 backbone keep/augment/replace — RESOLVED 2026-07-02.** Sourced from deep-research report [dr_L3-11_architecture_pressure_test_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-11_architecture_pressure_test_REPORT.md). We recommend the **AUGMENT** option: retain the incumbent hybrid conditional Transformer backbone while grafting targeted upgrades (Head-only Warmup + Joint Fine-Tuning with PCGrad Gradient Surgery, Class-Weighted Loss with $pos\_weight = 49$, Inference Logit Adjustment, and Joint Post-Hoc Raking). This combination stabilizes training, protects shipped heads, and meets all validation gates (PR-AUC $\ge$ 0.15, F1 $\ge$ 0.25). The Leg-2 discrete-diffusion (MDLM/SEDD) rejection stands due to excessive inference latency and temporal transition noise.
14. **Step-4 output representation — RESOLVED 2026-07-02.** Sourced from deep-research report [dr_L3-12_output_representation_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-12_output_representation_REPORT.md). We recommend keeping the **independent binary heads calibrated using logit-adjusted sigmoid outputs**, and resolving co-activation conflicts at decode time via a **Threshold-Normalized Argmax Projection** (Option 2). This guarantees a 0% physical violation rate in the final schedules while preserving individual-channel probability calibration. Validation enforces a pre-projection **Impossible-State Rate (ISR) gate of ≤ 0.5%** to check whether the model has implicitly learned negative location correlation.
15. **Step-4 training regimen — RESOLVED 2026-07-02.** Sourced from deep-research report [dr_L3-13_training_regimen_REPORT.md](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-13_training_regimen_REPORT.md). We recommend Unitary Scalarization (Fixed Weights $\alpha = 1.0 : 0.5 : 0.3$) + PCGrad pairwise gradient surgery as the loss balancing scheme, continuous year projection for `CYCLE_YEAR` to preserve progressive fine-tunability to 2030, stratified batching + inverse-frequency loss scaling for stratum balance, standard survey weights in loss with clipping (no active oversampling), dropout 0.1 (logits excluded) and weight decay 1e-4 (no label smoothing, no data augmentation), temperature 0.7 + minimum duration constraint for decoding, and gate-first filtering followed by lexicographic selection (maximizing retail F1) over a 3-run share-vs-separate backbone ablation.

---

## LIMITATIONS — CONSOLIDATED
*Written 2026-08-05 (V2-G3). This is the canonical limitations section for Leg 3; the
`..._Overview.md` points here rather than duplicating it.*

**The organising rule of this section: every limitation below is stated with the measurement that
bounds it.** A limitation with a number attached is a result — it tells a reader how wrong the work
could be, in units. A limitation without one is an apology, and it invites exactly the reviewer
question it was meant to pre-empt. **Sixteen items follow. Fifteen carry a number. The one that does
not is marked as such**, deliberately, so that the exception is visible instead of blending in.

Several of these were not known when this work started — they are limitations *because* something was
measured, not despite it. Three were promoted from suspected defects to bounded, stated limitations,
and one alleged defect was **retired outright** when the measurement showed it did not exist (L9).

---

### A. Frame — what the source data can and cannot see

**L1 — Hotel guests are outside the GSS frame by construction.** GSS sees **nothing** of hotel
occupancy: guests are not Canadian time-use respondents in a hotel, and no re-weighting recovers them.
The channel is therefore driven by a **non-GSS tourism series** (Step 6C), not by time-use data.
**The bounding number is zero: GSS observes 0 % of hotel occupancy**, so this is not a coverage
weakness to be quantified as a percentage error — it is a channel the source data cannot see at all.
*Consequence, stated plainly:* every hotel occupancy claim in this work is a claim about a forecast
series, and the paper's "one longitudinal TUS source → four channels" contribution is really
**3 of 4 channels TUS-driven, 1 of 4 series-driven**. *Evidence:* frame-caveat table, Step 1C.

**L2 — Retail sees customers only; staff are excluded by construction.** GSS logs retail workers as
`AT_WORK`, not as shopping, so the retail signal is the **shopper side only**. Two bounding numbers,
both zero and both deliberate: **0 % of retail staff presence enters the occupancy signal**, and
**0 % of retail plug load is modulated by it** — plug follows staff, and staff stay in the NECB
baseline. What the occupancy signal moves in this channel is the People-driven gain and nothing else.
*Evidence:* frame-caveat table, Step 1C; Step-9 retail rules.

**L3 — Residential intra-household presence diversity is partial, not complete.** The residential
channel drives People from household size times mean member presence. Measured on the shipped pool:
**3,499 of 16,367 multi-person households (21.38 %)** carry at least one slot value outside
`{0, 0.5, 1}`, which is unreachable if co-resident vectors were identical. So diversity is real but
bounded, and the stronger claim once made internally — that it is *exactly zero* — is **falsified by
this measurement**. The surviving defect is narrower: Step 5 computes a household **maximum** that
Step 7 never reads. Aggregation is the **mean** (V2-B5). *Evidence:* backward audit B-1 falsifier.

---

### B. Reference bands — what "plausible" is being measured against

**L4 — The office band's floor is contested and unsourced, and the gate is a band-applicability
finding, not a model defect.** The **uninjected `Default_NECB` control** — the code's own reference
implementation, with no occupancy signal applied — scores **85.45** against a floor of **100**, i.e.
it fails the band by **15 % before this work touches it**. A gate that no untreated control can pass
is measuring the band. Two candidate mechanisms were tested and **both refuted**: modelled heating
share is **17 %** against the band's **35–45 %**, and rebasing on service/MEP moves **56 of 56** cells
*down*, not up. The source document gives **three different floors for itself** (Table 7.1 = 100.0;
line 21 = 80–140; Table 2.1 = 85.0–115.0). **The value was not moved to make the gate pass.**
*Evidence:* V2-B1; scorer `BENCH["office"]`.

**L5 — The hotel band is archetype- and city-mismatched, and that is stated rather than absorbed.**
Our tower is **NECB-2017, Montréal / Calgary**. The reference is the DOE/PNNL **Large Hotel** prototype
at **ASHRAE 90.1-2019**, which is **Rochester MN (CZ 6A) = 284.44** and **International Falls MN
(CZ 7) = 299.28 kWh/m²·yr**, read first-party from the prototype's own packaged table. The **vintage**
half of this objection is now dead — the 300 ceiling rested on the 90.1-2004 lineage's **302.21**, and
the vintage-matched value is **1.0 %** away — but the **archetype and city gap remains** and is
recorded here instead of being converted into a tolerance. The gate still ~~**FAILs on 21 of 56
cells**~~ ~~**FAILs on 28 of 56 cells, all under the floor** (corrected 2026-08-06 — the struck figure
is the K=6 resize arm; see L8)~~ **FAILs on 28 of 56 cells, all `Tall`, every one of them OVER the 300
ceiling** — 🔴 **re-corrected the same day (V4-A4): the count 28 was right, the direction was not.**
The middle clause read `outputs_step9/` (2026-07-31) instead of the frozen
`outputs_step9_deliverable/` (2026-08-06 00:05); the deliverable range is **203.33–318.42**. See
`improvements/v4/V4-A4_split_scorecard.md` §5.
*Evidence:* V2-F6, `improvements/v2/f6_prototype_evidence/`; V2-B2.

---

**L8 — The three EUI failures are three different findings, and only one of them is about the
occupancy model.** Derived 2026-08-06 (V4-A2/A3) and 🔴 **re-derived the same day (V4-A4) on the
correct file** — ~~`outputs_step9/step9_eui_by_channel.csv`~~ **`outputs_step9_deliverable/step9_eui_by_channel.csv`**,
the frozen deliverable (`improvements/v2/V2-G1_FROZEN_DELIVERABLE.md`). The first derivation read the
superseded **2026-07-31** sibling directory, which predates `V2-D10`; **office and retail were
unaffected to ~0.1 %, hotel was wrong in both magnitude and direction.** No simulation, no re-scoring,
no gate or band touched. The decomposition compares each of the four `building × city` groups against
**its own uninjected `Default_NECB` cell**, which holds geometry, envelope, climate and plant fixed and
varies only the schedules.

| channel | uninjected control | what the injection then does | reading |
|---|---|---|---|
| **office** | **81.65 – 90.21**, all four **below** the 100 floor (−9.79 to −18.35) | a further **−12.98 to −19.93** | **roughly half and half** |
| **retail** | **87.21 – 96.84**, all four **inside** [80, 155] (+7.21 to +16.84) | **−10.63 to −25.04** | **entirely the injection** |
| **hotel** | **204.83 / 216.06 `SuperTall` (in band)** · **304.41 / 315.82 `Tall` (already over the 300 ceiling)** | **−1.55 to +2.60, i.e. ≤ 1.00 %** | **not occupancy at all** |

~~Superseded row values, kept for traceability: office 81.70–90.33 / −15.21 to −18.48; retail
87.60–97.05 / −19.65 to −23.94; hotel 149.36 / 160.65 `SuperTall` · 195.41 / 206.79 `Tall`, +0.06 to
+1.45.~~

**Office — the band is unreachable by this configuration, not merely missed.** The strongest form of
L4: across all 56 cells and all 14 scenarios the **highest office value in the entire set is ~~90.33~~
90.21**, still **~~9.67~~ 9.79 % below the floor**, and the uninjected control is already below it. **No cell reaches the
band under any scenario, including the untreated one.** ⚠️ **Correction to an earlier figure:** the
often-quoted *"~15 of the 22 kWh/m² predates the injection"* comes from the **arm-A** artefact, not
from Step 9. On the Step-9 artefact the split is closer to **half and half** and the total gap is
**26–37**, not 22. *A number carried across arms without its arm label is how L5 above went wrong.*

**Retail — the only one of the three that is a statement about our model.** Its uninjected control
**passes in all four groups**, so nothing here predates the injection; the injection removes
**~~20–24~~ 11–25 kWh/m² (≈12–26 %)** and pushes it under. The gate's 12 passing cells are exactly the
**4 control cells plus the 8 Montréal cells of the four observed eras** — every Calgary cell fails,
every 2030 bundle fails, every sensitivity cell fails. **The survivors clear the floor by
~~0.57 %–3.3 %~~ 0.82 %–3.53 %** (the four control cells aside, which clear it by 9–21 %), the thinnest
margin on the scorecard, which is why this gate has already been seen to flip on a −0.05 % DHW-driven
move. **The gate is not widened and stays FAIL.** *(Digits re-derived on the frozen deliverable by
V4-A4; the structural claim — survivors = 4 controls + 8 Montréal era cells — is unchanged.)*

🔴 **Hotel — `S9-EUI-hotel` has no resolving power about occupancy, and a band boundary lies in a
region where no building exists.** The 56 cells form **two disjoint clusters**: `SuperTall`
**203.33–218.22** and `Tall` **302.86–318.42**. The largest gap between consecutive values is
**84.64 kWh/m² — 70.5 % of the band's own width — and the 300 ceiling sits inside it.** So no cell can
land near the threshold, the median (**260.54**) describes **no building in the set**, and the verdict
is decided entirely by which of the two geometries a cell has. Injecting occupancy moves the channel by
**−1.55 to +2.60 kWh/m² (≤ 1.00 %)** against that 84.64 gap, and 🔴 **both `Tall` uninjected controls
are already over the ceiling (304.41 / 315.82) while both `SuperTall` controls are already in band
(204.83 / 216.06) — every sub-verdict is set before any occupancy is injected.** **The gate returns the
same answer with and without the occupancy model**, which is the condition this project calls a vacuous
reading — here in a gate that is currently *blocking*.

~~Superseded statement of the same finding (computed on `outputs_step9/`, 2026-07-31): clusters
147.87–162.76 and 193.83–209.43, gap 31.07 = 25.9 % of the band, the **180 floor** inside it, median
178.29, injection ≤1.45.~~ 🔴 **Re-derived on the frozen deliverable by V4-A4: the finding holds and is
substantially larger, but the failing end is the opposite one.** The struck figures were the reason
`V4-A4`'s two pre-registered sub-verdicts came out inverted — see
`improvements/v4/V4-A4_split_scorecard.md`.

✅ **`V4-A1` decided 2026-08-06 — score per geometry — and `V4-A4` executed it.** Under the split:
`SuperTall` **PASS** (28/28 in band, median 210.45) and `Tall` **FAIL** (28/28 over the ceiling, median
310.15). **At least one sub-gate still FAILs, so the split does not clear a blocker** (R1). The same
split was applied to office and retail and **changes nothing there** — both sub-gates FAIL in both
channels. ⚖️ **The limitation above survives the decision:** a better unit improves *attribution*; it
does not make this gate informative about occupancy.

*Evidence:* `outputs_step9_deliverable/step9_eui_by_channel.csv`; V4-A2, V4-A3, **V4-A4** in
`improvements/v4/` (`3rdJ_L3_v4_implementation.md`, `V4-A4_split_scorecard.md`,
`v4_a4_split_scorecard.json`).

**L6 — The "stacked channel" explanation for low EUIs was tested and REFUTED; do not cite it.** The
intuitive story — a channel buried mid-tower has almost no roof, ground or facade load, so a low EUI
is expected — makes a falsifiable prediction: least-exposed channel shows the largest negative gap to
its floor. **Measured, it is wrong in sign and order in 56 of 56 cells**: hotel is the *least*-exposed
of the three banded channels and sits *closest* to its floor, not furthest. **The three EUI failures
are therefore not explained by this mechanism and remain unexplained.** A second bound on the same
test: this campaign varies geometry only between `Tall` and `SuperTall`, so `exposure_ratio` takes
**two** distinct values per channel — the inference rests on **2 geometries, not 56 independent
cells**. *Evidence:* `3rdJ_09X_envelope_exposure.py`; gate `S9-EUI-EXPOSURE` (INFO, never PASS/FAIL,
precisely so a refuted hypothesis is not laundered into a PASS).

**L7 — The retail channel is validated on SHAPE, not on LEVEL.** No population-denominated in-store
presence reference exists at time-of-day resolution in **ATUS, HETUS or the UK TUS** — a genuine gap
in the time-use literature. The retail *rate* gate is therefore **INFO**, not PASS/FAIL: its two
candidate references disagree **in direction** (BLS ATUS A-3B says we run ~44 % *high*; the previous
band said 24.5 % *low*), so neither can arbitrate. The *shape* gates carry the validation. The EUI
gate rule is **median-in-band**, not 56-of-56, because the spread is smaller than the quantity's own
uncertainty — a single re-run moved the median by **−0.05 %** and flipped a cell. Retail median is
**75.4** against a floor of **80**, i.e. **5.7 % below**, with 44 of 56 cells under.
*Evidence:* V2-B3, V2-D6, V2-F2; V2-D4 measurement.

**L8 — The residential channel has no as-modelled band at all.** SHEU-2019 HighRise
(**130.6 [113.9–147.2]**) is carried as **context only** and is never a PASS criterion, because a
channel inside a mixed-use tower is not the stock basis SHEU sampled. *Evidence:* scorer
`BENCH["residential"]`, `lo=None`.

---

### C. Internal-gain inputs that were never parameterised

**L9 — Retail runs on NECB's OFFICE occupant density.** The model uses **24.97 m²/person**
(**3.72 occupants per 1000 ft²**, NECB `WholeBuilding` Office). NECB's own `Retail - sales` figure is
**3.10 occ/1000 ft² = 29.97 m²/person**, so **retail is modelled roughly 20 % over-crowded.**
🔴 **A correction belongs here, because the earlier version of this limitation was wrong and was
published internally:** an alleged **6.8× density error** was **retired** on 2026-08-05 once the units
were checked — `25.0 / 3.7 = 6.76` **is the unit-conversion factor** between m²/person and
occ/1000 ft². It was the same number written two ways, not two numbers. The real limitation is the
20 % above, and it is an order of magnitude smaller than the one it replaces. *Evidence:* V2-F8,
`improvements/v2/f8_necb_schedule_evidence/`.

**L10 — Equipment power density is a single blanket value.** **7.5028 W/m²** on **every** space type
in **both** towers, while **lighting is differentiated per space type**. Occupancy and plug load are
the two internal-gain fields never parameterised, and they are the two the paper's claim runs through.
*Evidence:* backward audit B-12.

**L11 — The retail occupancy peak of 0.95 has no source, and NECB's real retail schedule was never
loaded.** NECB publishes a dedicated retail schedule (**type C**): weekday peak **0.80 at 16:00, no
midday dip**, Saturday 0.90, Sunday 0.40 — a genuinely retail shape that builds through the afternoon.
NECB's office schedule (**type A**) peaks at **0.90** with a **0.50 lunch dip**, and our tower carries
its 24 hourly values **byte for byte**. Our injector applies **0.95**, which is **neither** — it is
unsourced. Two consequences, both stated: we run retail **18.75 % hot at peak**, on a curve whose
midday *dip* is the opposite of retail's midday *build*; and `grep -c "NECB-C-" injected.idf` returns
**0**. *Evidence:* V2-C4, V2-F8. *Open work:* V2-D9.

---

### D. Method conventions that are judgement, not derivation

**L12 — `MIN_POOL = 15` is an analyst judgement call and is presented as one.** No numeric convention
for a minimum adjustment-cell size was located in the literature; the anchor previously cited for it
gives **n = 5**, which is that paper's own study design rather than a recommendation. It cannot be
justified by the gate that selected it either: gate W1 is **non-monotonic** — FAIL at 10, PASS at
11–20, FAIL at 30 — so it is not a selection criterion. *Evidence:* V2-C9, V2-F3.

**L13 — Household aggregation is the MEAN, and the three legs of this project do not agree.**
**3 legs, 3 different implementations**: the 2J converter, the Leg-2 converter and the Leg-3 pipeline
each aggregate household presence differently, and the manuscripts do not all describe what their own
code does. Leg 3 uses the **mean**, decided and recorded rather than inherited — and the cross-leg
reach of that difference is verified against **each leg's own code**, never against another leg's
prose, which is the error that produced two earlier overreaching claims. *Evidence:* V2-B5, V2-G4.

**L14 — The retail episode-time share DECLINES across cycles; the earlier "stable" claim was a
documentation defect.** Measured **2.00 % → 2.14 % → 1.66 % → 1.50 %** across the four cycles, a
**−25 %** decline, which ATUS, UK TUS and HETUS all confirm is internationally normal. The superseded
text read "~2.1–2.3 %, stable across cycles". *Evidence:* V2-C5.

---

### E. Physical model

**L15 — Ground-level EPW on a supertall, and this is the one item here with NO bounding
measurement.** Both prototypes are driven by ground-station weather files (Montréal McTavish, Calgary
Olympic Park), so **no altitudinal temperature or wind-speed gradient is represented** over a tower of
this height. Nothing in this work measures the size of that error: it would take either a vertical
weather profile or an instrumented tall building, and we have neither. **It is listed with an explicit
"not quantified" rather than a plausible-sounding guess**, because an invented bound would be worse
than an admitted gap. *Evidence:* Step-8 design note; **no measurement**.

**L16 — The hotel DHW plant is capacity-pinned on a single object, and a global fix does not fix it.**
`LAUNDRY` has slope **−0.98 in both arms**, i.e. `dT ∝ V^−0.98` and therefore `E ∝ V^0.02`: its
delivered energy is **almost completely insensitive to draw volume**. Raising a **global** K to 6 made
every other heater's slope exactly **0.000** and moved `LAUNDRY`'s share of hotel DHW from **26.7 % to
65.4 %** — and share-reweighting alone reproduces the resulting **0.334** elasticity. **The global
resize changed the shares, not the physics.** The correct instrument is a **per-object** resize
(`LAUNDRY` alone at K ≈ 7 against the internal `BOOSTER` reference of 71.34 K, the other fifteen
heaters at K = 1). *Evidence:* V2-B4. *Open work:* V2-D10.

---

### Self-check on this section

| Requirement | Status |
|---|---|
| Every limitation names its evidence | **16 / 16** |
| Every limitation carries a bounding measurement | **15 / 16** — L15 (EPW altitude) is explicitly unquantified and says so |
| No limitation was written to excuse a failing gate | **held** — L4, L5 and L7 each record a gate that **still fails**, and in all three cases the band value was left where it was |
| Corrections carried rather than deleted | **held** — L9 states the retired 6.8× claim and why it was wrong; L14 states the superseded "stable" text |
