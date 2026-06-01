# Step 4 — Occupancy Diary Augmentation: The Story

*This is the narrative overview of Step 4. The design specs, training logs, and experiment records live in the linked documents (see the **Document Map** at the bottom) — this page is just the story: what we set out to do, how the model got where it is, the final result, and what we learned.*

---

## 1. What Step 4 set out to do

Every GSS respondent reports exactly **one** diary day — one of Weekday / Saturday / Sunday. Step 4 trains a conditional generative model to fill in the **two unobserved day-types** for each respondent, conditioned on their observed diary and demographics. The output is **~192,183 synthetic diary-days** (64,061 respondents × 3 day-types) at 30-min resolution, each carrying **activity** (14 classes), **AT_HOME** (location), and **co-presence** (9 channels).

These synthetic diaries are the occupancy backbone for everything downstream — Step 5 (census linkage), Step 6 (2030 forecast), Step 7 (EnergyPlus BEM). The shipped model is **calibrated J3**.

---

## 2. The journey

We started with a **Conditional Transformer** (encoder–decoder) generating diaries autoregressively. It hit a structural floor: a persistent AT_HOME bias the AR decoder couldn't shake. The F-series sweep (F1 → F10a) closed at a composite ≈ 1.3, failing the AT_HOME and activity-JS gates.

Rather than keep burning full-data runs, we switched to a **sample-first progressive funnel** — screen many architectures on 2%/10% samples, promote only winners to full data. In ~3 days it swept F → **G** (cross-attention, scheduled sampling, label smoothing) → **H** (Tanh-bounded heads, cyclical time) → **I** (encoder-only port), plus a discrete-diffusion branch (**MDLM / SEDD**), where weeks of one-shot runs had failed.

The winner was the **J-series: a Hybrid AR-Encoder** — a shared encoder trunk, an autoregressive arm for activity, and a parallel non-autoregressive arm for the binary heads (AT_HOME + co-presence), with a `detach()` barrier so the two arms don't fight over the representation. J1 → J2 refined it; **J3 was the first model to pass all four hard gates**.

Then we spent a long time trying to beat J3 — and couldn't. The **J5 series** (re-routing the binary heads, CRF/Viterbi decoding, smoothing), the **J6 family** (hierarchical and household-conditioned co-presence), and a **CrossAttn rescue** all failed to clear 4/4 across **40+ trials**. A recurring surprise: the models with the *best training loss* (the CrossAttn decoders) collapsed catastrophically on co-presence at inference. J3 stayed the production model.

The last move wasn't an architecture at all. Downstream validation (Step 5/6) scores the **per-(cycle × stratum × slot) marginals**, and under that harsher view even J3's strong aggregate AT_HOME (4.57 pp) hid a **15.37 pp** max gap. The fix was post-hoc **Phase 8B calibration** — raking the binary marginals to observed/projected targets, in the exact population the validator scores. That produced **calibrated J3**, which is what ships and what the BEM schedules are built from (OP1–OP5).

---

## 3. The models we tried

Every model on the four hard gates (lower is better everywhere). **J3 is the only 4/4 across 40+ trials.**

| Model | composite | AT_HOME RMS (pp) | COP max gap (pp) | act_JS | Gates |
|---|--:|--:|--:|--:|:--:|
| J1 | 0.690 | 5.83 ❌ | ~1.9 ✅ | 0.0274 ✅ | 3/4 |
| J2 | 0.688 | 5.70 ❌ | ~1.47 ✅ | 0.0239 ✅ | 3/4 |
| **J3 — production** | **0.6355** | **4.57 ✅** | **~2.03 ✅** | **0.0191 ✅** | **4/4** |
| J5_X2 (best J5) | 0.675 | 4.42 ✅ | 5.73 ❌ | 0.0297 ✅ | 3/4 |
| J6_HC (best J6) | 0.630 | 4.82 ✅ | 6.25 ❌ | 0.0228 ✅ | 3/4 |
| MDLM-G1 (best diffusion) | 0.559 | 7.81 ❌ | 4.57 ✅ | 0.0529 ❌ | 2/4 |
| CrossAttn-G4 | 1.256 | 5.66 ❌ | 20.55 ❌ | 0.0296 ✅ | 1/4 |

*Thresholds: composite < 1.045 · AT_HOME RMS ≤ 5.3 · COP max gap ≤ 5.0 · act_JS ≤ 0.05. The full table (~25 trials, training losses + inference gates) is in `step4_Speed_Cluster/step4_Speed-Cluster_docs/comparision.md`.*

---

## 4. Raw J3 → Calibrated J3 (the shipped model)

J3's aggregate gates pass, but downstream scores per-cell-slot — so the production model is **J3 + Phase 8B raking**. The raking sits *downstream* of the 04J gates (it does not change composite/act_JS); it zeroes the AT_HOME marginal gap where the validator actually measures it.

| Downstream metric (per-cell-slot) | Raw J3 | **Calibrated J3 (shipped)** |
|---|--:|--:|
| AT_HOME (stratum×slot) gap | 15.37 pp max | **within-stratum EXACT** (4.48 pp residual = day-type composition → 0.0037 pp held) |
| 0.30-floor HH exclusions | 1,413 | **1,118** |
| Spouse marginal (gate 6.3) | 2.23 pp PASS | 2.23 pp PASS (already compliant) |
| Activity / Work (gate 6.2) | — | unchanged — act30 not raked (Work over-fire persists) |
| 2030 (COVID-persists) | — | AT_HOME **79.70%**; gates 5.1–5.6 PASS |

*Honesty flags: the harsher per-cell-slot COP max (19.85 pp raw) was not raked — the Spouse marginal already passed; coherence cost ~1.8–2.1% of slot-records, BEM-harmless (BEM keys off hom30). Detail → `step4_Speed_Cluster/step4_Speed-Cluster_docs/comparision.md` Table 4 and `04_augmentationGSS_IMP_2.md` in the same folder.*

---

## 5. What we learned in Step 4

- **Composite score ≠ gate quality.** The composite is dominated by `cop_cal_MAE` (not a paper gate) — MDLM had the *best* composite yet failed two hard gates. Always read the four hard gates individually.
- **Low training loss ≠ good generation.** Teacher-forced loss hides exposure bias: the CrossAttn decoders had the best training `cop_loss` but produced ~20 pp co-presence gaps at inference. Judge by full diagnostic gates, never training loss.
- **Calibrate in the space the gate measures.** Raking the diary *pool* (8B-5) was diluted by Step-5 re-sampling; raking the *post-linkage population the validator scores* (8B-5b) made the marginal exact.
- **Aggregate metrics hide per-cell-slot gaps.** J3's 4.57 pp aggregate AT_HOME masked a 15.37 pp per-(stratum×slot) max. The downstream gates are per-cell — so measure there.
- **Architecture wasn't the downstream bottleneck — calibration was.** 40+ trials couldn't beat J3 on the gates; the real blocker was marginal calibration, solved post-hoc, not by a better model.
- **Sample-first beats single-shot.** The progressive funnel (2% → 10% → 100%) found the winning family in ~3 days where full-data one-shot runs had burned weeks.
- **Topology was right; capacity was the limiter.** J3's wiring was correct early on; extra demographic conditioning only helped when paired with added model capacity.
- **Supervision topology is the deepest open lever.** Activity and AT_HOME are never co-supervised on a shared representation in the J-series — the binding constraint, noted for any future work.

---

## 6. Document map

The operational docs sit **at root**; all the design / experiment / history detail lives under **`step4_Speed_Cluster/step4_Speed-Cluster_docs/`** (shown as `…/` below).

| Topic | Document |
|---|---|
| HPC / Speed-cluster operations (all 9 phases) | `04_augmentationGSS_hpc.md` *(root)* |
| Local testing plan · validation gates | `04_augmentationGSS_testing.md` · `04_augmentationGSS_val.md` *(root)* |
| Original build spec (4A–4F: inputs, architecture, training, schemas) | `…/04_implementation_spec.md` |
| Improvement Phases 1–6 (Levers A/B/C; F→G→H→I + MDLM/SEDD search; all-time leaderboard) | `…/04_augmentationGSS_IMP.md` |
| Phase 7/8/8B — J3 HPT, CrossAttn rescue, **Phase 8B calibration**, OP1–OP5 production + BEM wiring | `…/04_augmentationGSS_IMP_2.md` |
| J5 series training log | `…/step4_training_v4.md` |
| Architecture comparison tables (losses + inference gates; raw vs calibrated) | `…/comparision.md` |
| Earlier training logs (F/G/H/I series) | `…/DONE/` |
| Research & theory (diffusion, MTL, structured prediction) | `…/Research/` |
| Diagnostics & investigations | `…/investigations/` |

---

*Final status: Step 4 complete. **Calibrated J3** is the production model, wired into `BEM_Setup/BEM_Schedules_{2022,2030}.csv` (Step 7). See `step4_Speed_Cluster/step4_Speed-Cluster_docs/04_augmentationGSS_IMP_2.md` for the full calibration + BEM-wiring record.*
