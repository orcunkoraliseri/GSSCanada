# Tables B1–B2 — Generator Model Card and Activity Codebook

*Source:* `methodology_assessment_and_paper_skeleton.md` Part 3b Step-4 block; `04_augmentationGSS.md` §2–4; `04_augmentationGSS_IMP_2.md`; `04A_dataset_assembly.py` (CAT_COLS/CONT_COLS/BIN_COLS); `02_harmonizationGSS.md` §co-presence

---

## Table B1 — Calibrated-J3 Generator Model Card

*Shipped model = J3 + Phase-8B per-(cycle × stratum × slot) marginal raking. Sole 4/4-gate model in 40+ trials.*

### Architecture

| Component | Specification |
|---|---|
| Encoder | Shared 6-layer Transformer encoder |
| Activity decoder (Arm 1) | 6-layer autoregressive (AR) activity decoder → 14-category activity sequence, 48 slots |
| Binary heads (Arm 2) | Parallel non-autoregressive (NAT) binary heads: AT_HOME (1) + co-presence (9; `colleagues` masked for 2005/2010); gradient-detach barrier between Arm 1 and Arm 2 |
| d_model | 384 |
| n_heads | 8 |
| d_ff | 1,536 |
| Dropout | 0.1 |
| Parameter count | ~29.25M |

### Conditioning (d_cond = 90)

The conditioning vector concatenates all variables below (one-hot encoded categoricals + standardised continuous + binary flags) before injection at both encoder and decoder.

| Variable group | Variables | Type |
|---|---|---|
| Demographics (categorical one-hots) | AGEGRP, SEX, MARSTH, HHSIZE, PR, CMA, KOL, LFTAG, HRSWRK, NOCS, COW, DDAY_STRATA | 12 categorical variables, one-hot encoded |
| Phase-2 demographics | ATTSCH (school attendance), POWST (work-from-home status), MODE (commute mode) | 3 categorical variables, one-hot encoded |
| Continuous | TOTINC (household income, standardised) | 1 continuous |
| Binary flags | COLLECT_MODE (CATI=0 / EQ=1), TOTINC_SOURCE | 2 binary |
| Learned embedding (not part of d_cond vector) | CYCLE_YEAR (cycle index 0–3 → learned 16-dim embedding, injected separately) | learned |

> Note: COLLECT_MODE explicitly encodes the survey mode shift (CATI→EQ); POWST directly encodes work-from-home status (the COVID/WFH narrative variable).

### Training Protocol

| Item | Value |
|---|---|
| Split (stratified cycle × day-type) | 70 / 15 / 15 → 44,843 / 9,609 / 9,609 |
| K-nearest-neighbour supervision | K = 5 demographic neighbours; neighbour-disagreement JS floor 0.1888 |
| Learning rate | 1×10⁻⁴ (2,000-step warmup → cosine decay) |
| Batch size | 256 |
| Early stop patience | 10 epochs |
| Loss weights | λ_home = 0.9 · λ_act = 0.5 · λ_cop = 0.5 |
| Label smoothing | 0.05 |

### Hard Gate Results (Raw J3)

| Gate | Threshold | Raw J3 achieved | Result |
|---|---|---|---|
| Activity distribution JS | ≤ 0.05 | **0.0191** | PASS |
| AT_HOME RMS | ≤ 5.3 pp | **4.57 pp** | PASS |
| Co-presence max gap | ≤ 5.0 pp | **~2.03 pp** | PASS |
| Composite score | < 1.045 | **0.6355** | PASS |

**J3 is the only 4/4-gate model across 40+ trials (progressive 2% → 20% → 100% data funnel).**

Key negative findings from the search:
- MDLM-G1 (masked discrete diffusion): best composite (0.559) but 2/4 gates (AT_HOME RMS 7.81 pp; act_JS 0.0529)
- Best-training-loss CrossAttn decoders: collapsed 20+ pp on co-presence at inference (exposure bias, empirically confirmed)

### Phase-8B Calibration (Post-Hoc Raking)

Per-(cycle × stratum × slot) marginal raking applied after inference; zeroes AT_HOME marginals where downstream validator measures. Coherence cost ~1.8–2.1% of slot-records (BEM-harmless — BEM keys off occupancy only). Raw per-cell max AT_HOME gap 15.37 pp before raking → within-stratum marginals EXACT after raking.

### Inference

- Activity sampled at temperature τ = 0.8
- Binary heads thresholded at 0.5
- Consistency rules: night Sleep → home; Work → away (when POWST=0)

### Output

**~192,183 diary-days** (≈128k synthetic + 64k observed)

---

## Table B2 — 14-Category Activity Codebook

*Source:* `02_harmonizationGSS.md`; `03_mergingGSS.md`; `methodology_assessment_and_paper_skeleton.md` Part 3b Steps 1–2

### Activity Categories

| Code | Category | Raw-code magnitudes (2005 / 2010 / 2015 / 2022) | Notes |
|---|---|---|---|
| 1 | Work (paid work + telework) | ⚠ check source | Includes at-home and away-from-home paid work; POWST distinguishes WFH |
| 2 | Household work & maintenance | ⚠ check source | Cleaning, laundry, cooking preparation, repairs |
| 3 | Caregiving | ⚠ check source | Care for household members, children, elderly |
| 4 | Purchasing (shopping) | ⚠ check source | Retail, services, errands — presence = away |
| 5 | Sleep | ⚠ check source | All sleep including naps |
| 6 | Eating & drinking | ⚠ check source | Meals, snacks, beverages |
| 7 | Personal care | ⚠ check source | Grooming, hygiene, health |
| 8 | Education | ⚠ check source | Formal study, classes; presence depends on ATTSCH |
| 9 | Socializing | ⚠ check source | Social visits, hospitality |
| 10 | Passive leisure | ⚠ check source | TV/screen/reading/relaxation |
| 11 | Active leisure | ⚠ check source | Sport, exercise, hobbies |
| 12 | Community / volunteer | ⚠ check source | Civic, religious, volunteer — presence = away |
| 13 | Travel | ⚠ check source | All travel episodes — presence = away |
| 14 | Misc | ⚠ check source | Residual / unclassified |

**Cross-walk magnitudes (number of raw GSS activity codes mapped to the 14-category scheme):**
- 2005: **182** raw codes → 14
- 2010: **264** raw codes → 14
- 2015: **64** raw codes → 14
- 2022: **121** raw codes → 14
- **Zero disambiguation conflicts** across all four cycles

> Note: Per-code breakdown (which raw codes map to which of the 14 categories) is in `02_harmonizationGSS_actCodes.md`. The individual code-to-category crosswalk is not reproduced here; the above magnitudes are the headline count.

### Co-Presence Columns

| Unified column | Description | 2005/2010 availability |
|---|---|---|
| Alone | No other person present | All cycles |
| Spouse | Spouse or partner present | All cycles |
| Children | Children under 15 present | All cycles |
| parents | Parents or parents-in-law present | All cycles |
| otherInFAMs | Other household members ≥ 15 present | All cycles |
| otherHHs | Other household members | All cycles |
| friends | Friends present | All cycles |
| others | Other persons | All cycles |
| colleagues | Work colleagues present | **Not collected 2005/2010 (100% NaN)** |

**Raw → unified consolidation:** 10 raw GSS co-presence columns → 9 unified columns (the 10th raw = `colleagues`, absent 2005/2010). Per-cycle NaN rates (non-missing): 2005 ≈ 20% / 2010 ≈ 19.3% / 2015 ≈ 0.1% / 2022 ≈ 6.8%.
