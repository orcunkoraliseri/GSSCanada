# Architecture Comparison — Training Losses at Best Checkpoint

All values are **training losses at the best checkpoint epoch** (minimum val_score).

---

## Table 1: Full Data Training (sorted: act_loss ↑, then home_loss ↑)

| Architecture | act_loss | home_loss | cop_loss | val_score | best_ep | notes |
|---|---|---|---|---|---|---|
| J5_C | 0.0438 | 0.3370 | 0.1886 | 0.0152 | 100 | SHELVED |
| G4 | 0.0715 | 0.2214 | 0.0645 | 0.0467 | 67 | CrossAttn dec, label_smooth |
| H_Time | 0.0770 | 0.2154 | 0.0624 | 0.0555 | 58 | learnable PE + cyclical time |
| J5_A (X2) | 0.0818 | 0.2201 | 0.1917 | 0.0203 | 75 | SHELVED |
| H_Tanh | 0.0851 | 0.2265 | 0.0675 | 0.0508 | 58 | Tanh-bounded heads; 3/4 gates |
| J3 | 0.0878 | 0.3514 | 0.1919 | 0.0166 | 72 | arm2_act_proj; 4/4 GATES PASS |
| J5_B | 0.0913 | 0.3528 | 0.1921 | 0.0339 | 69 | SHELVED |
| J6_HC | 0.0928 | 0.3547 | 0.1921 | 0.0160 | 64 | J3 trunk + hierarchical COP; 3/4 gates, COP 6.25 |
| B2c (8B-3) | 0.0943 | 0.2307 | 0.1852 | 0.0391 | 66 | G4_NAT_COP soft-home-gate; 2/4 gates |
| J5_F | 0.0962 | 0.3556 | 0.2083 | 0.0222 | 66 | SHELVED |
| B2d (8B-3) | 0.0989 | 0.3710 | 0.1938 | 0.0138 | 62 | G4_NAT_COP AT_HOME→NAT (J3-style); 3/4 gates, COP 7.07 |
| J1 | 0.1028 | 0.3596 | 0.1943 | 0.0171 | 60 | Hybrid AR+NAT; 3/4 gates |
| J2 | 0.1031 | 0.3572 | 0.1943 | 0.0173 | 60 | lambda_home=0.9 |
| J2.5 | 0.1045 | 0.3595 | 0.1942 | 0.0176 | 60 | GELU head (no Tanh) |
| J6_HCHH | 0.1168 | 0.3572 | 0.1933 | 0.0143 | 55 | J3 trunk + hier_cop + HH-cop-cond; 3/4 gates, COP 6.44 |
| J5_X1b | 0.1177 | 0.2405 | 0.1583 | 0.0141 | 64 | cross-arm grad; best home+cop in J-series |
| J4_2 | 0.1318 | 0.3629 | 0.1951 | 0.0161 | 53 | hierarchical cop; SHELVED |
| J6_HT | 0.1352 | 0.3489 | 0.1947 | 0.0148 | 50 | J3 trunk + temporal home head; 2/4 gates |
| J5_X1 | 0.1379 | 0.3610 | 0.2090 | 0.0196 | 51 | dec_out.detach→binary; 3/4 gates |
| J4_1 | 0.1487 | 0.3675 | 0.1959 | 0.0171 | 49 | tod/dow embed; SHELVED |
| MDLM_G1 | 0.1570 | 0.3292 | 0.1887 | 0.0372 | 64 | MDLM champion; 2/4 gates |
| SEDD_C | 0.1646 | 0.3323 | 0.1899 | 0.0352 | 54 | SEDD tuned |
| G3 | 0.1909 | 0.0505 | 0.0847 | 0.0477 | 60 | CrossAttn dec; sched_sample_p=0.2 |
| J6_HHC | 0.1985 | 0.3707 | 0.1966 | 0.0192 | 39 | J3 trunk + HH-cop-cond; 2/4 gates |
| B2b (8B-3) | 0.2452 | 0.2517 | 0.1893 | 0.0444 | 35 | G4_NAT_COP mass-coupled; under-fit; 1/4 gates |
| J4_3 | 0.2461 | 0.3732 | 0.2069 | 0.0183 | 37 | logic loss; SHELVED |
| B2a (8B-3) | 0.2515 | 0.2529 | 0.1889 | 0.0549 | 33 | G4_NAT_COP +HH cond; under-fit; 1/4 gates |
| MDLM_C | 0.2542 | 0.3206 | 0.1865 | 0.0351 | 51 | MDLM tuned |
| J3_D2_H16 | 0.2806 | 0.3844 | 0.2065 | 0.0411 | 47 | n_heads=16; KILLED ep49 |
| J3_D2_DEC8 | 0.2961 | 0.3847 | 0.2065 | 0.0424 | 42 | n_dec=8; KILLED ep42 |
| MDLM_B | 0.3297 | 0.3472 | 0.2066 | 0.0490 | 36 | mask diffusion, d=256 |
| J3_D2_ENC8 | 0.3598 | 0.3884 | 0.2065 | 0.0536 | 38 | n_enc=8; KILLED ep38 |
| J3_DEMO_PSBLite | 0.3744 | 0.3872 | 0.2064 | 0.0503 | 38 | +PSB-Lite proj; SHELVED |
| J3_D2_CTRL | 0.3908 | 0.3893 | 0.2082 | 0.0496 | 35 | d_cond=90, no capacity; KILLED |
| J3_DEMO | 0.3908 | 0.3893 | 0.2082 | 0.0496 | 35 | d_cond=90 only; SHELVED |
| G2 | 0.4824 | 0.1048 | 0.0862 | 0.1151 | 92 | sched_sample + label_smooth |
| SEDD_B | 0.4938 | 0.3175 | 0.2191 | 0.0533 | 9 | score entropy diffusion |
| F10a | 0.5243 | 0.1064 | 0.0820 | 0.1362 | 95 | F-series closure |
| F8 | 0.5305 | 0.1072 | 0.0883 | 0.1273 | 93 | F7 + aux_stratum |
| G1 | 0.5424 | 0.1129 | 0.0815 | 0.1311 | 65 | proportional sampling |
| F7 | 0.5996 | 0.1083 | 0.0894 | 0.1468 | 89 | FiLM AR, d=256, no label-smooth |
| I1 | 1.4118 | 0.4168 | 0.2369 | 0.0925 | 67 | encoder-only port; FAILED |
| H_NAT | 1.5613 | 0.5007 | 0.2280 | 0.1060 | 34 | encoder-only NAT; FAILED |
| CC_B | 1.6958 | 0.5326 | 0.2660 | 0.1470 | 4 | continuous classifier |
| J_old | 1.6761 | 0.5126 | 0.2321 | 0.1058 | 16 | FAILED |
| CC_SPL_B | 1.7823 | 0.5374 | 0.2801 | 0.1293 | 3 | CC split-head |
| J3_D2_W512 | 1.8757 | 0.5392 | 0.2865 | 0.1699 | 1 | d=512; KILLED ep11 (barely started) |
| J3_CLEAN | 2.2383 | 0.5333 | 0.7744 | 0.2285 | 1 | loss-fix stack; CATASTROPHIC |

---

## Table 2: Sample Data Training (10% / 20% / 2%)

| Architecture | act_loss | home_loss | cop_loss | val_score | best_ep | sample | notes |
|---|---|---|---|---|---|---|---|
| MDLM_D3 | 0.2866 | 0.2486 | 0.1899 | 0.0345 | 35 | 10% | |
| MDLM_E3 | 0.1219 | 0.3694 | 0.1957 | 0.0350 | 43 | 10% | |
| MDLM_F0 | 1.0539 | 0.2627 | 0.2643 | 0.0815 | 9 | 10% | Stage F control |
| MDLM_F1 | 1.0539 | 0.2627 | 0.2643 | 0.0811 | 9 | 10% | steps=32 |
| MDLM_F2 | 1.2567 | 0.2749 | 0.2761 | 0.0913 | 6 | 10% | steps=64; WORSE |
| MDLM_F3 | 0.8166 | 0.2865 | 0.2521 | 0.0790 | 14 | 10% | cosine mask |
| MDLM_F4 | 1.0546 | 0.2636 | 0.2646 | 0.0808 | 9 | 10% | linear mask [0.1/0.9] |
| MDLM_F8 | — | — | — | — | — | 10% | WINNER (diag only, no log) |
| PP_H0–H5 | — | — | — | — | — | 10% | diagnostics only, no training logs |

---

## Key Observations

**The home_loss comparison is NOT apples-to-apples across architecture families:**
- F-series (~0.10): raw BCE, no label smoothing, FiLM decoder
- G4/H-series (~0.22): label_smooth=0.05 introduced, CrossAttn decoder
- J-series (~0.35): Arm-2 NAT split changes what home_loss measures
- D2 variants (~0.39): same J-series formula but d_cond=90 makes it harder

**Lowest cop_loss (best copresence fitting):**
1. G4: 0.0645
2. H_Time: 0.0624
3. H_Tanh: 0.0675
4. F10a: 0.0820
5. J5_X1b: 0.1583

**Lowest home_loss (best binary fitting):**
1. G3: 0.0505 (sched_sample artifact — not real)
2. F7–F10a: 0.106–0.113
3. G4: 0.2214
4. J5_X1b: 0.2405
5. J5_A: 0.2201

**Lowest act_loss (best activity fitting):**
1. J5_C: 0.0438
2. G4: 0.0715
3. H_Time: 0.0770
4. J3: 0.0878
5. J5_A: 0.0818

---

## Table 3: Inference Performance — Diagnostic Gate Results

**Low training loss ≠ good generation quality.** The model practiced only with cheat sheets, so it scores perfectly on homework but fails the real exam. Training uses teacher forcing (correct history); inference uses own predictions — mistakes snowball.

**Gate thresholds:** AT_HOME RMS ≤ 5.3 pp | COP max gap ≤ 5.0 pp | act_JS ≤ 0.05 | composite < 1.045

| Architecture | AT_HOME RMS (pp) | COP max gap (pp) | act_JS | Composite | Gates | Notes |
|---|---|---|---|---|---|---|
| **J3 (raw)** | **4.57** | **~2.03** | **0.0191** | **0.6355** | **4/4** | Only 4/4-gate model · raw at-inference; **production = calibrated J3** (J3 + Phase 8B raking — see § below) |
| J5_X1 | **4.15** | 5.32 | 0.0311 | 0.6667 | 3/4 | composite FAIL by 0.031 |
| J2 | 5.70 | — | 0.0239 | 0.6884 | 3/4 | AT_HOME FAIL by 0.40 |
| J1 | 5.83 | — | 0.0274 | 0.69 | 3/4 | AT_HOME FAIL by 0.53 |
| H_Tanh | 5.70 | — | — | ~0.85 | 3/4 | AT_HOME FAIL by 0.40 |
| J4_2 | 5.88 | 6.22 | 0.0266 | 0.6578 | 3/4 | AT_HOME FAIL |
| B2d (8B-3) | **4.94** | 7.07 | 0.0238 | **0.670** | 3/4 | AT_HOME→NAT (J3-style); COP FAIL by 2.07; best 8B-3 variant |
| J6_HC | 4.82 | 6.25 | 0.0228 | **0.6300** | 3/4 | hierarchical COP; composite beats J3; COP FAIL by 1.25 |
| J6_HCHH | 5.19 | 6.44 | 0.0325 | 0.6825 | 3/4 | hier_cop + HH_cond; COP FAIL by 1.44 |
| MDLM_G1 | 7.81 | **4.57** | 0.053 | **0.5592** | 2/4 | Best composite, AT_HOME+act_JS FAIL |
| J5_X1b | 5.88 | 8.14 | 0.0285 | 0.8086 | 2/4 | cross-arm gradient distorted cop |
| B2 (8B-2) | 5.75 | 10.21 | 0.0202 | 0.801 | 2/4 | hybrid AR-act + NAT-COP base; AT_HOME+COP FAIL (8B-3 parent) |
| B2c (8B-3) | 6.14 | 9.67 | 0.0279 | 0.802 | 2/4 | soft home gate; flat vs B2 base, COP unfixed |
| J6_HT | 6.10 | 5.83 | 0.0351 | 0.6866 | 2/4 | temporal home head; AT_HOME+COP FAIL (backfired on home) |
| J6_HHC | 7.36 | 6.79 | 0.0461 | 0.7736 | 2/4 | HH-cop-cond; AT_HOME+COP FAIL |
| **H_Time** | 5.68 | **22.86** | **0.0233** | 1.3214 | **1/4** | Best training losses but catastrophic inference COP |
| G3 | 6.06 | **19.77** | **0.0241** | 1.2284 | **1/4** | sched_sample=0.2 did NOT fix COP; Spouse channel=19.77 pp |
| G4 | 5.66 | **20.55** | **0.0296** | 1.2564 | **1/4** | Best training act_loss (0.07) but COP catastrophic (Alone=20.55 pp) |
| J4_1 | 6.43 | 9.29 | 0.0400 | 0.8247 | 1/4 | temporal injection regressed |
| J4_3 | 7.83 | 8.89 | 0.0684 | 0.9449 | 1/4 | logic loss catastrophic |
| B2a (8B-3) | 7.78 | 7.99 | 0.0697 | 0.923 | 1/4 | +HH cond; under-fit broke act_JS |
| B2b (8B-3) | 7.63 | 10.50 | 0.0659 | 0.983 | 1/4 | mass-coupled; under-fit, COP worse than base |

**Key finding:** Every CrossAttn AR decoder model catastrophically fails the COP gate at inference (~20 pp), regardless of training cop_loss. G4 has cop_loss=0.064 (best), G3 has cop_loss=0.085, H_Time has cop_loss=0.062 — yet all produce COP max gap 19–23 pp. Meanwhile J3 (cop_loss=0.192, 3x worse training loss) achieves COP max gap ~2.03 pp. The Arm-2 NAT per-slot parallel architecture avoids cascading errors that destroy CrossAttn copresence at inference. Scheduled sampling (G3, p=0.2) does NOT fix this — it improves activity (act_JS=0.024) but COP remains catastrophic.

**J6 family (Phase 8B-4, J3-trunk variants):** All four J6 variants take J3's exact Arm-2 NAT trunk plus one structural tweak each, and **all four fail the COP gate at inference** (5.83–6.79 pp vs J3's 2.03) — including J6_HT, which leaves the COP path untouched. Unlike the CrossAttn catastrophe (~20 pp), this is a milder but **systematic** ~4–5 pp regression shared across the whole family, pointing to a common cause (shared J6 training recipe — `LAMBDA_COP=0.3`, `SPOUSE_NEG_WEIGHT=0.45` — rather than the per-variant flags). The three COP-targeting mechanisms (hierarchical COP, HH-cop-cond, both) did not improve COP over the COP-agnostic temporal variant. Notably **J6_HC's composite (0.6300) edges out J3 (0.6355)** — the only model to beat J3 on composite — yet still misses COP; if the shared cause is fixed it is the strongest 4/4 candidate.

**Phase 8A inference rescue test (job 936884, G4 checkpoint):** Three inference-side fixes tested on 5000-respondent subset — all FAILED. (1) Seed variance: 10 seeds produce 20.65–21.02 pp (std=0.12), confirming systematic bias. (2) COP threshold sweep 0.30–0.70: best=0.70 → 12.88 pp, but trades Alone over-generation for Spouse under-generation (seesaw effect). (3) Per-respondent multi-sample K=10 Bernoulli: cherry-pick → 14.89 pp. Best overall 12.88 pp — still 2.6× above the 5.0 pp gate. COP bias is structural in the AR decoder, not fixable by inference tricks.

**Per-cell-slot reality — why this gate table understates the downstream gap (Phase 8B-4, 2026-05-30):** Table 3's metrics are *aggregate* (AT_HOME RMS, COP mean), but downstream Steps 5/6 validate the per-(cycle × stratum × slot) **MAX** gap. Under that harsher view even **J3 — 4/4 above — shows AT_HOME max 15.37 pp and COP max 19.85 pp** (vs its 4.57 / 2.03 aggregate). A Work-calibration diagnostic (`04K`, jobs 940277/940278) tested whether capping synthetic Work at observed (cascading Work ⇒ AT_HOME = 0) closes the AT_HOME gap post-hoc — it did **not**: J3 15.37→14.60, J5_X1 & J6_HC unchanged, MDLM_G1 23.80→23.31; all still 5–8× over the ≤ 3 pp downstream gate. The worst AT_HOME cell-slots are not the Work-overshoot slots (only MDLM_G1's error is Work-driven, corr 0.92, and it is the worst model). Lone win: single-person-HH 0.30-floor exclusions dropped sharply (J5_X1 283→6, J3 121→55). **Conclusion: the lever is direct per-cell-slot raking of the binary marginals, not architecture or the Work proxy.** Next test (`04L`): joint AT_HOME + COP raking to observed per cell-slot, scored by edit-cost + per-person coherence damage (marginal residual ≈ 0 by construction). *No new training/inference rows added — 04K/04L are post-hoc diagnostics on existing model outputs, not new models.*

---

## Table 4: Calibrated J3 — the production model (Phase 8B, RESOLVED 2026-05-31)

Tables 1–3 are the **raw J3 model**. The shipped Step-5/6/7 input is **calibrated J3 = J3 + post-hoc per-(cycle × stratum × slot) raking** — the "direct per-cell-slot raking" flagged as the lever in the note above, now executed (8B-5b for 2022, 8B-6 for 2030). This is the last inference-side improvement and the version that feeds BEM. It does **not** change J3's aggregate 04J gates (composite/act_JS); it operates in the downstream per-cell-slot marginal space the Step-5/6 validators actually score.

| Downstream metric (Step-5/6 validators, per-cell-slot) | Raw J3 | **Calibrated J3** |
|---|---|---|
| AT_HOME per-(stratum×slot) gap | **15.37 pp max** | **within-stratum EXACT** — raked to observed; 4.48 pp aggregate residual is pure DDAY_STRATA day-type composition (composition-held = **0.0037 pp**), a documented paper caveat (§4.2), not a model error → AT_HOME gate **PASS** |
| Single-person-HH 0.30-floor exclusions | 1,413 HHs | **1,118 HHs** |
| Spouse marginal (gate 6.3) | 2.23 pp PASS | 2.23 pp PASS — already < 3 pp, so the conditional Spouse30 rake was **skipped** |
| Activity (gate 6.2 Work; act_JS) | unchanged | **unchanged — act30 deliberately NOT raked** → Work 3.27 pp expected-FAIL persists (documented limitation) |
| 2030 (8B-6, COVID-persists p=1) | — | AT_HOME **79.70%**; gates 5.1–5.6 **all PASS** |

**What it does:** zeroes — by construction, per stratum × slot — the AT_HOME marginal gap that the raw aggregate gate (4.57 pp) masked and the per-cell-slot view exposed (15.37 pp). 8B-5b raked the exact 286,537-row post-linkage population the validator measures (raking one step upstream, 8B-5, was diluted by `--full` re-sampling to ~5.5 pp, still FAIL).
**What it does NOT do:** leaves activity untouched (Work proxy still over-fires), and does **not** separately rake the harsher per-cell-slot COP max (19.85 pp raw) — that wasn't triggered because the Spouse *marginal* gate already passed; 04L proved joint AT_HOME+COP raking feasible if a future gate needs it.
**Coherence cost:** ~1.82% (2022) / ~2.07% (2030) of slot-records become act/hom-incoherent — BEM-harmless (BEM occupancy keys off hom30).

Calibrated J3 is what Step-5 linkage, the Step-6 2030 forecast, and the OP4 `BEM_Schedules_{2022,2030}.csv` all consume. Full record: `../04_augmentationGSS_IMP_2.md` Phase 8B-5b / 8B-6 + OP1–OP5 Progress Logs.
