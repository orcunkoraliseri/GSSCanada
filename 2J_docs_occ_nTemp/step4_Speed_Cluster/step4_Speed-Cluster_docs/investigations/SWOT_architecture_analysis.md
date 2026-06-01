# SWOT Analysis: Candidate Architectures for Next Training Round

**Date:** 2026-05-26
**Context:** J3 and all D2 variants SHELVED. Pivoting to architectures with better gate-loss profiles.

---

## 1. The Core Tension

Three loss gates compete. No single architecture excels at all three:

| What wins | act_loss | home_loss | cop_loss | Why |
|---|---|---|---|---|
| FiLM AR, d=256 | 0.48-0.60 | **0.10-0.11** | **0.08-0.09** | Early affine fusion of demographics saturates binary heads but starves 14-class activity |
| CrossAttn AR, d=384 | **0.07-0.09** | 0.22 | **0.06-0.07** | Decoder-level cross-attention gives activity enough capacity; binary hits label-smooth floor |
| Hybrid AR+NAT | **0.04-0.09** | 0.35 | 0.19 | AR arm dominates activity; NAT arm fundamentally limited for binary fitting |
| CrossAttn + sched_sample | 0.19 | **0.05** | 0.08 | Scheduled sampling trains decoder for own-prediction recovery; boosts binary at activity cost |

**Key levers identified across 45+ trainings:**

| Lever | Effect on act_loss | Effect on home_loss | Effect on cop_loss |
|---|---|---|---|
| FiLM → CrossAttn decoder | 0.48→0.07 (huge improvement) | 0.10→0.22 (regression) | 0.09→0.06 (slight improvement) |
| d_model 256→384 | improves (bundled with CrossAttn) | worsens (bundled) | improves (bundled) |
| sched_sample_p 0.0→0.2 | 0.07→0.19 (3x worse) | 0.22→0.05 (4x better) | 0.06→0.08 (slight worse) |
| label_smooth 0.0→0.05 | negligible | creates floor ~0.20 | negligible |
| lambda_home 0.5→0.7→0.9 | slight degradation | marginal improvement in J-series | negligible |
| Tanh-bounded heads | negligible | negligible | negligible |
| Learnable PE + cyclical time | slight improvement | slight improvement | slight improvement |
| Arm-2 NAT (J-series) | best activity ever | 0.22→0.35 (catastrophic) | 0.06→0.19 (catastrophic) |

---

## 2. SWOT: Binary Champions

### F7 — FiLM AR, d=256, first valid F-run

| | |
|---|---|
| **Strengths** | home=0.108, cop=0.089 — solid binary fitting with raw BCE; simple architecture; no label_smooth means no artificial floor |
| **Weaknesses** | act=0.600 — worst activity among candidates; FiLM decoder cannot handle 14-class AR; d=256 underpowered for activity |
| **Opportunities** | Proves that raw BCE + FiLM can reach home~0.10; this binary floor is the target for any new architecture |
| **Threats** | FiLM decoder is fundamentally unsuited for activity — no amount of tuning fixes 0.60 act_loss |

### F8 — F7 + aux_stratum head

| | |
|---|---|
| **Strengths** | home=0.107, cop=0.088, act=0.530 — slight activity improvement from aux_stratum; stratum head provides cross-task signal |
| **Weaknesses** | act_loss still 0.53 — FiLM decoder bottleneck persists; aux_stratum alone is not enough |
| **Opportunities** | aux_stratum concept could transfer to CrossAttn architectures |
| **Threats** | Same FiLM ceiling; diminishing returns in F-series |

### F10a — F-series closure, spouse-axis optimized

| | |
|---|---|
| **Strengths** | home=0.106, cop=0.082 — best cop_loss in F-series; spouse_neg_weight=0.45 tuned |
| **Weaknesses** | act=0.524 — same FiLM ceiling; marginal gains over F7/F8 |
| **Opportunities** | cop_loss=0.082 sets the F-series benchmark for copresence; spouse weighting is transferable |
| **Threats** | F-series exhausted — no further moves improve activity meaningfully |

### G1 — FiLM AR + proportional sampling

| | |
|---|---|
| **Strengths** | home=0.113, cop=0.082 — best cop_loss tied with F10a; proportional sampling stabilizes rare strata |
| **Weaknesses** | act=0.542 — data-side sampling alone doesn't fix FiLM activity ceiling |
| **Opportunities** | Proportional sampling could combine with CrossAttn architectures |
| **Threats** | Still FiLM — architectural bottleneck unchanged |

### G2 — FiLM AR + sched_sample + label_smooth

| | |
|---|---|
| **Strengths** | home=0.105, cop=0.086 — best home_loss in FiLM family; sched_sample=0.2 + label_smooth=0.05 introduced as training regularization |
| **Weaknesses** | act=0.482 — moderate improvement over F-series but still unacceptable; label_smooth creates floor for future CrossAttn runs |
| **Opportunities** | Proved sched_sample works for binary fitting; this recipe transferred to G3 with dramatic results |
| **Threats** | Label_smooth=0.05, once adopted, persisted into all subsequent architectures — may be unnecessarily constraining home_loss in CrossAttn models |

---

## 3. SWOT: The Bridge (G3)

### G3 — CrossAttn AR, d=384, sched_sample=0.2

| | |
|---|---|
| **Strengths** | home=0.050, cop=0.085, act=0.191 — **only architecture that achieves sub-0.10 home_loss AND sub-0.20 act_loss simultaneously**; proved CrossAttn + sched_sample can have both; act_loss 2.5x better than any FiLM model |
| **Weaknesses** | act=0.191 still 2.7x worse than G4 (0.071); notes flag home_loss=0.050 as "sched_sample artifact"; no diagnostic gate results available — we don't know if inference-time gates pass |
| **Opportunities** | **THE most important candidate to evaluate.** If G3's diagnostic gates are decent, then sched_sample with CrossAttn is the winning recipe — just tune the rate. The "artifact" label may be wrong: sched_sample trains for own-prediction recovery, which IS useful at inference |
| **Threats** | If diagnostic gates show poor generation quality despite low training loss, then sched_sample truly is an artifact and the low home_loss doesn't translate |

---

## 4. SWOT: Activity Champions

### G4 — CrossAttn AR, d=384, no sched_sample, label_smooth=0.05

| | |
|---|---|
| **Strengths** | act=0.071, cop=0.065 — 2nd best activity, best copresence among candidates; best balanced architecture overall; **3x improvement over G3 in activity from simply removing sched_sample** |
| **Weaknesses** | home=0.221 — 4.4x worse than G3; label_smooth creates floor at ~0.20 that cannot be broken with current setup; no gate diagnostics available |
| **Opportunities** | Removing label_smooth could unlock sub-0.20 home_loss (F-series floor is 0.10 without it); tuning lambda_home from 0.6→0.9 could push harder; light sched_sample (0.05) might recover some binary without tanking activity |
| **Threats** | Without label_smooth, sigmoid heads may saturate (the original reason for smoothing); lambda_home=0.9 in J-series didn't help much |

### H_Tanh — CrossAttn AR, Tanh-bounded heads, lambda_home=0.7

| | |
|---|---|
| **Strengths** | act=0.085, home=0.227, cop=0.068 — 3/4 gates PASS (only AT_HOME RMS fails at 5.70 pp vs 5.3 threshold — margin of 0.40 pp); Tanh prevents logit explosion; closest to shipping |
| **Weaknesses** | AT_HOME RMS 5.70 pp fails by narrow margin; Tanh didn't measurably improve home_loss vs G4; lambda_home=0.7 slightly worse activity than G4 (0.6) |
| **Opportunities** | Only 0.40 pp from AT_HOME gate — capacity increase or training tricks could close the gap; Tanh + sched_sample combination untested |
| **Threats** | Tanh may limit expressiveness at tail occupancy states; H_Time proved learnable PE gives more bang for complexity budget |

### H_Time — CrossAttn AR, learnable PE + cyclical time

| | |
|---|---|
| **Strengths** | act=0.077, home=0.215, cop=0.062 — **best cop_loss of any full-data model**; best home_loss among activity champions; learnable PE captures temporal patterns sinusoidal PE misses |
| **Weaknesses** | No gate diagnostics available; home=0.215 still double the F-series floor; lambda_home=0.6 (not pushed) |
| **Opportunities** | **Best starting point for hybrid experiments.** Learnable PE is independently beneficial and compatible with any other modification (sched_sample, no label_smooth, capacity increase) |
| **Threats** | Learnable PE adds parameters that may overfit on small strata; untested at different capacities |

### J5_C — Hybrid AR+NAT (activity king)

| | |
|---|---|
| **Strengths** | act=0.044 — **lowest activity loss ever recorded**; proves the AR decoder CAN reach sub-0.05 |
| **Weaknesses** | home=0.337, cop=0.189 — completely unacceptable binary; NAT arm fundamentally limited; 3x worse cop than G4 |
| **Opportunities** | Limited. The activity breakthrough comes from the hybrid split, but that split is what kills binary. Could contribute as a reference point for activity-loss floor |
| **Threats** | Any modification to improve binary in J-series degrades the AR activity pathway (proven across J1-J5, D2 variants) |

---

## 5. Cross-Architecture Analysis

### What drives each loss component?

**act_loss (activity cross-entropy):**
- Decoder type is king: CrossAttn (0.07) >> FiLM (0.50) >> no decoder/NAT-only
- sched_sample hurts: 0.0→0.2 triples act_loss (G4→G3)
- d_model helps: 384 > 256 (but bundled with decoder change)
- lambda_home slightly hurts: higher weight diverts capacity from activity

**home_loss (AT_HOME binary cross-entropy):**
- label_smooth sets floor: ~0.20 with smooth, ~0.10 without
- sched_sample dramatically helps: 0.22→0.05 (G4→G3)
- FiLM decoder helps: early affine fusion gives binary heads better signal
- NAT arm hurts: ~0.35 floor in all J-series

**cop_loss (copresence binary cross-entropy):**
- CrossAttn slightly better than FiLM: 0.06 vs 0.08
- NAT arm terrible: 0.19 in J-series
- Relatively stable across most modifications (0.06-0.09 range)
- spouse_neg_weight and cop_pos_weight affect this

### The label_smooth hypothesis

The strongest signal in the data: **label_smooth=0.05 creates a hard floor at home_loss~0.20 for CrossAttn models.**

Evidence:
- F-series (no label_smooth): home_loss = 0.106-0.113
- G2 (FiLM + label_smooth): home_loss = 0.105 (FiLM strong enough to overcome)
- G3 (CrossAttn + label_smooth + sched_sample): home_loss = 0.050 (sched_sample overcomes floor)
- G4 (CrossAttn + label_smooth, no sched_sample): home_loss = 0.221 (stuck at floor)
- H_Time (CrossAttn + label_smooth): home_loss = 0.215 (same floor)
- H_Tanh (CrossAttn + label_smooth): home_loss = 0.227 (same floor)

**Conclusion:** CrossAttn without sched_sample cannot break the label_smooth floor. Two paths forward:
1. Remove label_smooth → risk sigmoid saturation but potentially reach 0.10-0.15 home_loss
2. Add light sched_sample → G3 proved this works; find the right dose

### The sched_sample dose-response question

Only two data points exist:
- sched_sample_p=0.0 (G4): act=0.071, home=0.221
- sched_sample_p=0.2 (G3): act=0.191, home=0.050

The relationship is likely nonlinear. Values 0.02-0.10 are completely unexplored.

---

## 6. Inference Performance (Diagnostic Gate Results)

**Critical lesson: Low training loss ≠ good generation quality.** The model practiced only with cheat sheets, so it scores perfectly on homework but fails the real exam. Training uses teacher forcing (correct history given); inference uses own predictions — mistakes snowball.

### Table 3: Inference Gate Results (sorted by gates passed)

| Architecture | AT_HOME RMS (pp) | COP max gap (pp) | act_JS | Composite | Gates | Notes |
|---|---|---|---|---|---|---|
| **J3** | **4.57** | **~2.03** | **0.0191** | **0.6355** | **4/4** | Only model passing all gates |
| J5_X1 | **4.15** | 5.32 | 0.0311 | 0.6667 | 3/4 | composite FAIL by 0.031 |
| J2 | 5.70 | — | 0.0239 | 0.6884 | 3/4 | AT_HOME FAIL by 0.40 |
| J1 | 5.83 | — | 0.0274 | 0.69 | 3/4 | AT_HOME FAIL by 0.53 |
| H_Tanh | 5.70 | — | — | ~0.85 | 3/4 | AT_HOME FAIL by 0.40 |
| J4_2 | 5.88 | 6.22 | 0.0266 | 0.6578 | 3/4 | AT_HOME FAIL |
| MDLM_G1 | 7.81 | **4.57** | 0.053 | **0.5592** | 2/4 | Best composite, AT_HOME+act_JS FAIL |
| J5_X1b | 5.88 | 8.14 | 0.0285 | 0.8086 | 2/4 | cross-arm gradient distorted cop |
| **H_Time** | 5.68 | **22.86** | **0.0233** | 1.3214 | **1/4** | cop_loss=0.062 (best training) but catastrophic inference COP |
| J4_1 | 6.43 | 9.29 | 0.0400 | 0.8247 | 1/4 | temporal injection regressed |
| J4_3 | 7.83 | 8.89 | 0.0684 | 0.9449 | 1/4 | logic loss catastrophic |
| G3 | 6.06 | **19.77** | **0.0241** | 1.2284 | **1/4** | sched_sample=0.2 did NOT fix COP; Spouse=19.77 pp |
| G4 | 5.66 | **20.55** | **0.0296** | 1.2564 | **1/4** | Best training act/cop but COP catastrophic (Alone=20.55 pp) |

**Gate thresholds:** AT_HOME RMS ≤ 5.3 pp | COP max gap ≤ 5.0 pp | act_JS ≤ 0.05 | composite < 1.045

### Key insight from H_Time diagnostics (2026-05-26)

H_Time has the best training losses in the CrossAttn family (cop_loss=0.062, home_loss=0.215, act_loss=0.077) but **catastrophic inference quality** on copresence (22.86 pp Alone gap). This proves:

1. **Training loss is NOT a reliable proxy for generation quality.** The CrossAttn decoder overfits to teacher-forcing conditions.
2. **J3 was correct to promote despite worse training losses.** Its Arm-2 NAT per-slot parallel fusion avoids cascading errors — each slot predicts independently from encoder features, not from previous predictions.
3. **Scheduled sampling does NOT fix CrossAttn COP at inference.** G3 (sched_sample_p=0.2) achieves excellent act_JS=0.024 but COP max gap=19.77 pp — still catastrophic. Sched_sample helps activity robustness but copresence cascading errors persist in AR decoders.
4. **The reason J3 passes 4/4 gates:** Not because J3 fits better during training, but because its Arm-2 NAT per-slot parallel architecture avoids cascading errors entirely.
5. **ALL CrossAttn AR decoders fail COP at inference.** G3 (19.77 pp), G4 (20.55 pp), H_Time (22.86 pp) — all catastrophic regardless of training cop_loss. This is a structural limitation, not a hyperparameter problem.

### Diagnostic availability status

| Architecture | Training losses | Diagnostic gates | Status |
|---|---|---|---|
| G3 | yes | **COMPLETE** | 1/4 gates (COP=19.77 pp, Spouse channel) |
| G4 | yes | **COMPLETE** | 1/4 gates (COP=20.55 pp, Alone channel) |
| H_Time | yes | **COMPLETE** | 1/4 gates (COP=22.86 pp, Alone channel) |
| H_Tanh | yes | partial (3/4 gates) | AT_HOME=5.70 pp FAIL |
| F7, F8, F10a, G1, G2 | yes | **NO** | not prioritized |

---

## 7. Proposed Architectures (Priority Order)

### Priority 0: Run diagnostics on existing checkpoints (no training needed)

Run inference + diagnostic gates on G3, G4, H_Time. This data determines everything:
- If G3 passes gates → sched_sample + CrossAttn IS the answer; sweep sched_sample_p
- If G4 passes gates → label_smooth removal is the priority lever
- If H_Time passes gates → learnable PE is load-bearing; use as base for all experiments

### P1: G4_NoLS — G4 without label smoothing

| Parameter | Value |
|---|---|
| Base | G4 (CrossAttn AR, d=384) |
| Change | home_label_smooth: 0.0 (was 0.05) |
| Hypothesis | Label_smooth floor (~0.20) is the bottleneck. F-series reaches 0.10 without it. CrossAttn should reach 0.12-0.18 without smoothing. |
| Risk | Sigmoid saturation on binary heads — mitigated by Tanh bounding (from H_Tanh) |
| Expected | act~0.07, home~0.12-0.18, cop~0.06 |

### P2: G4_SS005 — G4 with light scheduled sampling

| Parameter | Value |
|---|---|
| Base | G4 (CrossAttn AR, d=384, label_smooth=0.05) |
| Change | sched_sample_p: 0.05 (was 0.0; G3 used 0.2) |
| Hypothesis | G3 proved sched_sample helps binary dramatically. 0.05 is 4x lighter than G3's 0.2 — should give marginal binary improvement without destroying activity. |
| Risk | Even light sched_sample may degrade activity; nonlinear response possible |
| Expected | act~0.09-0.12, home~0.10-0.15, cop~0.07 |

### P3: H_Time_NoLS — H_Time without label smoothing

| Parameter | Value |
|---|---|
| Base | H_Time (CrossAttn AR, d=384, learnable PE) |
| Change | home_label_smooth: 0.0 (was 0.05) |
| Hypothesis | Same as P1 but with learnable PE advantage. H_Time has best cop_loss — removing LS could make it best on ALL three gates. |
| Risk | Same sigmoid saturation risk as P1 |
| Expected | act~0.08, home~0.12-0.18, cop~0.06 |

### P4: G4_SS01 — G4 with moderate scheduled sampling

| Parameter | Value |
|---|---|
| Base | G4 (CrossAttn AR, d=384, label_smooth=0.05) |
| Change | sched_sample_p: 0.10 (halfway between G4's 0.0 and G3's 0.2) |
| Hypothesis | If P2 (0.05) doesn't move binary enough, 0.10 is the next step. Linear interpolation between G4 and G3 loss profiles. |
| Risk | Activity regression — but should still be <0.15 (vs G3's 0.19 at p=0.2) |
| Expected | act~0.12-0.15, home~0.08-0.12, cop~0.07-0.08 |

### P5: G4_NoLS_Tanh — G4 without label smoothing, with Tanh heads

| Parameter | Value |
|---|---|
| Base | G4 (CrossAttn AR, d=384) |
| Changes | home_label_smooth: 0.0, Tanh-bounded binary heads (from H_Tanh) |
| Hypothesis | Tanh bounding prevents the sigmoid saturation that label_smooth was designed to avoid. This gives us the best of both: no artificial floor AND no saturation. |
| Risk | Tanh may not fully prevent saturation; adds slight complexity |
| Expected | act~0.08, home~0.12-0.18, cop~0.06-0.07 |

### P6: H_Time_SS005 — H_Time with light scheduled sampling

| Parameter | Value |
|---|---|
| Base | H_Time (CrossAttn AR, d=384, learnable PE) |
| Change | sched_sample_p: 0.05 |
| Hypothesis | Combine H_Time's best-in-class temporal modeling with light sched_sample binary boost. |
| Risk | Same as P2 but with learnable PE potentially compensating for some activity loss |
| Expected | act~0.09-0.12, home~0.10-0.15, cop~0.06-0.07 |

---

## 8. Recommended Execution Plan

### Phase A: Diagnostics — COMPLETE (2026-05-26)

All 3 models diagnosed. Results: G3 1/4, G4 1/4, H_Time 1/4. Every CrossAttn AR model catastrophically fails COP at inference (19–23 pp max gap). Scheduled sampling (G3) does NOT fix this.

### Phase B: BLOCKED — Proposals P1–P6 are invalidated

All 6 proposals were built on CrossAttn AR decoder (G4/H_Time base). Diagnostic results show this decoder family has a structural COP inference problem that no hyperparameter change (label_smooth, sched_sample, learnable PE) can fix. COP max gap 19–23 pp vs threshold of 5.0 pp — this is not a marginal failure.

**The only architecture passing COP at inference is J3 (Arm-2 NAT).** J3's per-slot parallel fusion avoids the AR cascading error that destroys CrossAttn copresence.

### Phase C: Revised direction

The investigation must pivot. Options:
1. **Return to J3** and address its weaknesses (act_loss, home_loss) through capacity/demographic experiments
2. **Hybrid architecture** — CrossAttn activity head (proven act_JS=0.024) + NAT copresence/binary head (proven COP ~2 pp)
3. **NAT-only exploration** — test if a full NAT decoder can achieve CrossAttn-level activity while maintaining COP robustness

---

## 9. Summary: What Each Architecture Family Teaches Us

| Family | Lesson | Transferable to next round? |
|---|---|---|
| **F-series** | home_loss=0.10 is achievable without label_smooth | yes — try removing label_smooth from CrossAttn |
| **G1/G2** | sched_sample and proportional sampling help binary marginally with FiLM | partially — sched_sample transfers, proportional sampling worth testing |
| **G3** | CrossAttn + sched_sample=0.2 → incredible binary (0.05) at activity cost (0.19) | **YES — the key lever. Dose-response sweep needed** |
| **G4** | CrossAttn without sched_sample → best activity (0.07) but binary stuck at LS floor | **YES — the base architecture. Remove LS or add light sched_sample** |
| **H_Tanh** | Tanh bounding doesn't help/hurt much; 3/4 gates (AT_HOME fails by 0.40 pp) | yes — Tanh as safety net for no-LS experiments |
| **H_Time** | Learnable PE + cyclical time gives best all-around balance | **YES — best base for next experiments** |
| **J5_C** | Hybrid AR+NAT = best activity ever but binary disaster | no — NAT arm is a dead end for binary |

**Bottom line (REVISED after diagnostics 2026-05-26):** CrossAttn AR is a dead end for COP inference — all 3 tested models (G3, G4, H_Time) fail catastrophically (19–23 pp vs 5.0 pp threshold). J3's Arm-2 NAT architecture remains the only path to passing all 4 gates. Next round must either (a) improve J3 directly, or (b) design a hybrid that keeps NAT copresence while borrowing CrossAttn's activity strength.
