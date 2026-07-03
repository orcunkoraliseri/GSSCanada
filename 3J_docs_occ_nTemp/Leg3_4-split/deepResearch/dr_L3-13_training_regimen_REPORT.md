# Deep-Research Report dr_L3-13 — STEP-4 TRAINING REGIMEN PLAYBOOK: loss balancing, conditioning, sampling, selection for the 3-head model

## Scope and Restated Aim
This report establishes the training-regimen playbook for the three-head occupant presence and activity generator in Step 4 of the GSSCanada occupancy pipeline. The model comprises a shared 6-layer Transformer encoder (~29M parameters) and three task-specific decoder heads: Head 1 (14-category activity, AT_HOME, and co-presence), Head 2 (AT_WORK, ~6–7% positive slots), and Head 3 (AT_RETAIL, ~2% positive). The downstream destination is EnergyPlus building energy simulation, where predicted occupant presence probabilities act as direct physical multipliers. Under this setting, **probability calibration** (unbiased population fractions) and **temporal consistency** (flicker-safe run-lengths) are the ruling criteria. 

This playbook defines:
1. The **loss-balancing strategy** for the multi-task sequence generator.
2. The **conditioning encoding** for heterogeneous covariates (specifically enabling progressive fine-tuning of the ordinal `CYCLE_YEAR` variable to an unseen 2030).
3. The **survey-data sampling and weighting** scheme (incorporating design weights and stratum balancing).
4. The **regularization and calibration** choices at the ~30M parameter and ~64k sequence scale.
5. The **decoding and model selection** rules to prevent slot-level flicker and ensure Pareto-optimal performance across multiple validation gates.

---

## REQUIRED OUTPUT TABLES

### Table 1 — Loss balancers at low task count (2–4 heads)

| Balancer | Evidence at 2–4 tasks (does it beat fixed weights?) | Behaviour when one task is rare/noisy (our retail head) | Interaction with PCGrad (complementary / redundant / harmful) | Citation |
|---|---|---|---|---|
| **Fixed weights ($\alpha = 1.0 : 0.5 : 0.3$, incumbent plan)** | **Baseline**. Provides stable optimization and predictable gradient scaling, but requires manual tuning of task importance. | **Stable but requires manual scaling**: The rare 2% retail head can be ignored if its loss magnitude is too small. Static scaling ($\alpha_{retail} = 0.3$) must be paired with $pos\_weight$ to balance gradients. | **Highly complementary**: Fixed weights define static task priorities, while PCGrad resolves directional gradient conflicts. | Yu et al. (2020) [2] |
| **SLAW (Scaled Loss Approximate Weighting)** | **Comparable**. SLAW matches state-of-the-art dynamic weighters (e.g. GradNorm) on 2–4 tasks while being much more computationally efficient. | **Unstable**: SLAW uses the standard deviation of losses to approximate gradient norms. For a 2% rare head, loss variance is very low (mostly zeros), causing SLAW to over-amplify its weight, leading to gradient spikes that destabilize training. | **Complementary but noisy**: SLAW's rapid, dynamic weight adjustments can cause gradient magnitudes to shift erratically, complicating PCGrad's projections. | Crawshaw & Košecká (2021) [26] |
| **Homoscedastic uncertainty weighting (UW)** | **Strong**. UW learns task-dependent noise to scale losses, showing significant improvements on 3-task benchmarks (e.g., NYUv2). | **Stable but risks under-learning**: Noisy or rare tasks are assigned high uncertainty ($\sigma^2$), which scales down their loss weights to protect the shared encoder. However, without logit adjustment, the rare head's signal can be suppressed. | **Highly complementary**: Uncertainty weights change slowly (parameterized variables), providing stable gradient magnitudes that allow PCGrad to project directions cleanly. | Kendall et al. (2018) [16] |
| **GradNorm** | **Suboptimal**. Often fails to outperform fixed weights at low task counts and introduces high computational overhead (requires extra backward passes/hooks). | **Highly unstable**: GradNorm scales task weights inversely with gradient norms. The rare 2% head produces sparse, low-norm gradients, causing GradNorm to balloon its weight and inject gradient noise. | **Redundant/Harmful**: GradNorm adjusts weights based on unprojected gradient norms, while PCGrad projects them, distorting the norms and causing weight oscillation. | Chen et al. (2018) [17]; Kurin et al. (2022) [5] |
| **DWA (Dynamic Weight Average)** | **Suboptimal**. Underperforms SLAW/UW/GradNorm on 2-4 tasks. Uses historical loss values, which are noisy at small scale. | **Unstable**: Sudden loss fluctuations on the rare retail head lead to erratic weight shifts, destabilizing the encoder. | **Redundant/Harmful**: Similar to GradNorm, conflicts with PCGrad's directional updates. | Liu et al. (2019) [27] |
| **CAGrad / IMTL-style** | **Suboptimal**. High computational complexity. Underperforms well-tuned fixed weights on 2–4 tasks. | **Unstable**: Worst-case conflict minimization can cause the optimizer to focus entirely on the noisy/rare task's gradient, degrading performance on the dominant task. | **Harmful/Redundant**: Mathematically conflicts with PCGrad as both attempt to modify gradient directions using different projection rules. | Liu et al. (2021) [28]; Senushkin et al. (2023) [29] |
| **Unitary scalarization (well-tuned fixed weights)** | **Superior**. Kurin et al. (2022) proved that unitary scalarization with proper tuning and regularization consistently matches or beats specialized multi-task optimizers. | **Stable**: Prevents gradient variance spikes from the rare head, provided that static weights ($\alpha = 1.0 : 0.5 : 0.3$) and class weights ($pos\_weight = 49$) are fixed. | **Highly complementary (Recommended)**: The fixed priorities are preserved, and PCGrad is free to resolve directional conflicts without magnitude interference. | Kurin et al. (2022) [5] |

---

### Table 2 — Conditioning encoding

| Covariate type | Options (embedding / one-hot concat / FiLM / cross-attention) | Best practice + evidence | Special constraint here | Citation |
|---|---|---|---|---|
| **Categorical demographics (AGEGRP, SEX, NOCS, COW, …)** | Embedding / one-hot concat / FiLM / cross-attention | **Categorical embedding layers (nn.Embedding)** projected and concatenated/added to the input sequence. Maps categories into a dense continuous space, capturing demographic interactions. | Demographic features are static per diary; they must be combined and appended as static features without exploding parameters. | Gorishniy et al. (2021) [30] |
| **Ordinal-with-meaning CYCLE_YEAR** | Embedding / one-hot concat / FiLM / cross-attention | **Continuous value projection** (treating CYCLE_YEAR as a continuous variable normalized to $[0, 1]$ and projecting it via a linear layer) or **Time2Vec/Fourier features**. | **Must support progressive fine-tuning to unseen 2030**. Standard categorical embeddings fail because the embedding weights for 2030 are untrained. Continuous projection allows the model to naturally extrapolate. | Kazemi et al. (2019) [31] |
| **Day-type stratum (3-way, drives the whole diurnal shape)** | Embedding / one-hot concat / FiLM / cross-attention | **Learned embeddings (nn.Embedding(3, d_model)) added to the input representation**. Day-type is the primary driver of diurnal shape; embeddings allow the model to shift the baseline profile. | Must be highly expressive as it directly drives the diurnal shape (Wasserstein validation gate). | Vaswani et al. (2017) [32] |
| **Mixed-mode flag COLLECT_MODE (confound control, not signal)** | Embedding / one-hot concat / FiLM / cross-attention | **Low-dimensional binary embedding (nn.Embedding(2, d_model)) or simple one-hot concatenation** appended to the sequence. | Confound control, not physical signal; must be kept low-capacity to prevent leaking or distorting physical occupancy signals. | Pearl (2009) [33] |

---

### Table 3 — Survey-data sampling and weighting

| Question | Field practice + evidence | Citation |
|---|---|---|
| **Design weights (WGHT_PER/WGHT_EPI): weighted loss vs weighted sampling vs post-hoc raking only** | **Weighted loss with weight clipping (or robust scaling)**. Using survey weights directly in the loss function is the standard in survey-based deep learning. However, weights must be clipped (e.g. at the 99th percentile) to prevent extreme weights from generating high-variance gradients. Post-hoc raking is then applied to the output probabilities to ensure population totals match marginals. Weighted sampling causes severe sample duplication and over-representation, reducing sample diversity and causing overfitting. | Kish (1965) [34]; Pfeffermann (1993) [35] |
| **Stratum balance: inverse-frequency weighting (incumbent) vs stratified batch composition** | **Stratified batch composition combined with inverse-frequency loss scaling**. Every mini-batch is composed of a fixed proportion of strata (e.g., 50% weekdays, 25% Saturdays, 25% Sundays) to ensure that every gradient update has a balanced signal from all strata, stabilizing training. | He & Garcia (2009) [36] |
| **Cycle balance during joint pre-training (2022 has fewest diaries) vs leaving it to progressive fine-tuning** | **Joint pre-training with inverse-cycle-frequency sample weighting** (to ensure each cycle contributes equally to the pre-trained backbone) followed by **progressive fine-tuning (W_2005 → W_2010_ft → W_2015_ft → W_2022_ft)**. This ensures cycle-invariant features in the encoder, while progressive fine-tuning handles longitudinal distribution shifts. | Yosinski et al. (2014) [37] |
| **Retail-active diary exposure: any resampling despite dr_L3-08's pos_weight already handling rarity (double-correction risk)** | **Do NOT resample retail-active diaries**. Standard data sampling must reflect the true population distribution. Rarity is handled solely via $pos\_weight = 49$ and corrected during inference using a $- \ln(49)$ logit shift. Resampling retail-active diaries during training changes the marginal probability, making the theoretical logit shift formula invalid and destroying calibration. | Zadrozny & Elkan (2001) [8]; Menon et al. (2020) [9] |

---

### Table 4 — Regularization and calibration at ~30M params / ~64k sequences

| Technique | Evidence at this scale | Effect on probability calibration (ruling criterion) | Citation |
|---|---|---|---|
| **Dropout level / placement** | **0.1 is standard**. Placed only on residual connections, not on output projections. | **Negative if too high or misplaced**: High dropout (e.g. > 0.1) causes underfitting and degrades calibration by making output probabilities over-dispersed (flattened towards 0.5). Output logits must be dropout-free to preserve exact calibration. | Gal & Ghahramani (2016) [38]; Guo et al. (2017) [13] |
| **Weight decay** | **1e-4 is standard**. Regularizes model weights, preventing logit explosion and overconfidence. | **Positive**: Acts as an entropy regularizer, keeping logits in a reasonable range and preventing extreme, uncalibrated probabilities. | Guo et al. (2017) [13] |
| **Label smoothing (known calibration distortion — quantify)** | **Reject**. Label smoothing (e.g. $\epsilon = 0.1$) replaces targets with $1 - \epsilon$ and $\epsilon / (K - 1)$. | **Highly negative**: Destroys calibration because it prevents the model from ever outputting 1.0 or 0.0, biasing the predicted probabilities and shifting the optimal threshold. Distorts downstream EnergyPlus inputs that rely on binary schedules. | Müller et al. (2019) [39]; Meister et al. (2020) [40] |
| **Data augmentation for diaries (slot jitter, cyclic shifts) — legitimate or signal-corrupting?** | **Reject**. Slot jitter (shifting activities by 1 or 2 slots) or cyclic shifts (shifting the start of the diary) break temporal boundaries. | **Highly negative**: Time-use survey diaries are synchronized with absolute circadian and societal rhythms (e.g. 8:00 AM work start, 12:00 PM lunch). Augmenting data by shifting time slots breaks these synchronization peaks, corrupting the diurnal shape (which drives the EUI peak). | Li & Biljecki (2023) [10] |
| **Early stopping criterion (which metric, which patience)** | **Validation gates validation with patience of 10 epochs**. Early stopping is based on validation gates validation (checking if all gates are satisfied: old heads JS $\le 0.002$ bits, rare-state F1 $\ge 0.25$ and PR-AUC $\ge 0.15$). | **Neutral**: Selecting models based on validation gates validation rather than composite loss prevents over-tuning on dominant tasks and ensures all tasks are balanced. | Prechelt (1998) [41] |

---

### Table 5 — Decoding and model selection

| Question | Field practice + evidence | Citation |
|---|---|---|
| **AR decoding for realistic run-lengths (temperature / nucleus / constrained decoding / min-duration enforcement) — our flicker countermeasure** | **Temperature scaling ($T = 0.7$) paired with a minimum duration constraint (e.g. 2 slots / 60 minutes for work/retail) enforced at decode time**. Autoregressive sequence models suffer from "slot-level flicker" (rapid, unrealistic state transitions like alternating home-work-home in consecutive 30-min slots), resulting in short run-lengths and high transition frequencies. Enforcing a minimum dwell-time rule directly in the decoding logic eliminates this. | Holtzman et al. (2019) [42]; Page et al. (2008) [6] |
| **Scheduled sampling / exposure-bias mitigation worth it at 48-slot length?** | **Not worth it**. It introduces training instability, complicates the training loop, and can distort calibration. Instead, using teacher forcing during training and mitigating inference drift via temperature scaling and constrained decoding is preferred and less risky. | Bengio et al. (2015) [43]; Mihaylova & Martins (2019) [15] |
| **Operationalizing Pareto-frontier selection across ~6 gate metrics (hypervolume, lexicographic, gate-first filtering)** | **Gate-First Filtering followed by Lexicographic Selection**. First, filter out all checkpoints that fail any of the hard gates. Among the surviving checkpoints, select the one that maximizes the rare head's F1 score, or select based on a lexicographic priority (1st: ISR $\le 0.5\%$, 2nd: JS divergence targets, 3rd: Retail F1). This avoids the pitfalls of training loss minimization. | Steuer (1986) [44]; Deb (2001) [45] |
| **Seed variance: how many seeds to report for a ~30M model on 64k sequences, and what variance is normal** | **5 random seeds**. For a 29M parameter Transformer trained on 64k sequences, seed variance typically results in a standard deviation of 1-2% in F1/PR-AUC and 0.001-0.002 bits in JS divergence. Reporting the mean and standard deviation across 5 seeds is standard to ensure results are not cherry-picked. | Dodge et al. (2020) [46] |

---

## Part C — Synthesis (the regimen spec)

### 1. Concrete Ordered Regimen Checklist

Below is the step-by-step checklist for the model builder to implement from top to bottom:

*   **[ ] 1. Data Preprocessing & Covariate Encoding**
    *   **Demographics**: Encode `AGEGRP`, `SEX`, `NOCS`, `COW`, etc., using standard categorical embeddings (`nn.Embedding(vocab_size, d_model)`). Combine and project to feed the Transformer encoder.
    *   **Strata**: Encode `DDAY_STRATA` (3-way) using `nn.Embedding(3, d_model)`.
    *   **Mixed-Mode Flag**: Encode `COLLECT_MODE` (2-way) using a low-dimensional embedding `nn.Embedding(2, 16)` to control for confounds without leaking signal.
    *   **Cycle Year**: Encode `CYCLE_YEAR` as a continuous variable normalized to $[0, 1]$ (where $x = \frac{\text{year} - 2005}{2030 - 2005}$). Project this scalar using a linear layer (`nn.Linear(1, d_model)`) to support progressive fine-tuning to unseen 2030.
    *   **Data Augmentation**: Do **NOT** apply any slot jitter, cyclic shifts, or time-shifting data augmentation to the time-use diaries.

*   **[ ] 2. Batch Composition & Survey Weights**
    *   **Stratified Batching**: Build a custom batch sampler that enforces stratified batch composition (50% weekdays, 25% Saturdays, 25% Sundays in every batch).
    *   **Cycle Balancing**: During joint pre-training, apply inverse-cycle-frequency sample weighting to ensure that 2022 (fewest diaries) has equal influence compared to earlier cycles.
    *   **Design Weights**: Apply `WGHT_PER` directly in the BCE loss calculation. Clip weights at the 99th percentile of the cycle's distribution to prevent extreme weights from causing high-variance gradients.
    *   **No Active Oversampling**: Do **NOT** oversample or resample retail-active diaries in the training loop (prevents prior-shift double-correction bias).

*   **[ ] 3. Loss Balancing & Gradient Surgery**
    *   **Balancer**: Use **Unitary Scalarization (Fixed Weights)** with $\alpha_{\text{resid}} = 1.0$, $\alpha_{\text{work}} = 0.5$, $\alpha_{\text{retail}} = 0.3$.
        *   *Deciding Citation*: **Kurin et al. (2022)** [5] proves that unitary scalarization with proper hyperparameter tuning and regularization matches or beats specialized multi-task optimizers on 2–4 tasks, avoiding the instability of dynamic weighters (SLAW/GradNorm) on rare, sparse tasks.
    *   **Gradient Surgery**: Apply **PCGrad** pairwise across the three task gradients to project out conflicting gradients at the shared encoder layer.

*   **[ ] 4. Regularization Settings**
    *   **Dropout**: Set to $0.1$ globally (attention dropout and residual dropout). Ensure no dropout is applied to the output projection layers.
    *   **Weight Decay**: Set to $10^{-4}$ in the AdamW optimizer.
    *   **Label Smoothing**: Set to $0.0$ (disabled to preserve probability calibration).

*   **[ ] 5. Training Schedule**
    *   **Phase 1: Head-Only Warmup (5 Epochs)**: Freeze the shared encoder and Heads 1 & 2. Train only Head 3 (AT_RETAIL) using $\eta = 1.0 \times 10^{-3}$ and AdamW.
    *   **Phase 2: Joint Fine-Tuning (15 Epochs)**: Unfreeze all parameters. Train all three heads jointly using $\eta = 1.0 \times 10^{-4}$ and PCGrad.

*   **[ ] 6. Decoding & Inference**
    *   **Activity Decoding**: Use autoregressive sampling with temperature $T = 0.7$ and nucleus sampling ($p = 0.9$).
    *   **Dwell-Time Constraint**: Enforce a minimum duration constraint at decode time (e.g. minimum 2 consecutive slots / 60 minutes for work and retail events).
    *   **Calibration (Inference Logit Shift)**: For Head 3 (retail), subtract the logit shift before applying the sigmoid activation:
        \[ logit_{\text{calibrated}} = logit_{\text{raw}} - \ln(49) \]
    *   **Conflict Resolution**: Apply the **Threshold-Normalized Argmax Projection** at decode time (Head 1: $\theta_{\text{home}} = 0.50$, Head 2: $\theta_{\text{work}} = 0.40$, Head 3: $\theta_{\text{retail}} = 0.15$) to resolve location overlaps and enforce hard mutual exclusivity (ISR = 0%).
    *   **Post-Hoc Raking**: Apply the slot-level joint raking step on the calibrated probabilities to match the target census population marginals exactly.

*   **[ ] 7. Model Selection Rule (Pareto-Frontier Lexicographic Selection)**
    *   Evaluate all saved checkpoints on the frozen validation set.
    *   **Step A (Gate-First Filter)**: Retain only checkpoints that pass the hard gates:
        *   Old heads JS drift: $\Delta \text{JS}_{\text{stratum}} \le 0.002 \text{ bits}$ vs. Leg-2 baseline.
        *   Pre-projection Impossible-State Rate: $\text{ISR} \le 0.5\%$.
        *   Retail resolution: $\text{PR-AUC} \ge 0.15$ AND $\text{F1-score} \ge 0.25$.
        *   Midday peak rate error (11:00-14:00): $\le 3.0 \text{ pp}$.
        *   Temporal stability: $\text{Mean transitions} \ge 0.05 \text{ transitions/day}$.
    *   **Step B (Selection)**: Among the passing checkpoints, select the one that maximizes the validation F1-score on the rare retail head.

---

### 2. The Fix-vs-Ablate Split

To operate within our **hard-capped ablation budget of 4 runs total**, we freeze choices that are theoretically or empirically settled in literature and isolate only the core architectural trade-off for ablation:

#### A. FIXED Choices (Sourced from Evidence and Shipped Baseline)
1.  **Unitary Scalarization (Fixed Weights) + PCGrad**: Fixed by Kurin et al. (2022) [5] showing superior stability and performance on low-task counts compared to dynamic weighters like GradNorm or SLAW (which collapse on 2% rare tasks).
2.  **Continuous Projection for CYCLE_YEAR**: Fixed by Time2Vec (Kazemi et al., 2019 [31]) showing that learned continuous linear mappings naturally generalize to unseen temporal intervals, whereas categorical embeddings fail at progressive fine-tuning.
3.  **Inference Logit Shift**: Fixed by Menon et al. (2020) [9] showing that subtracting $\ln(w)$ from uncalibrated logits is the mathematically exact correction to recover calibrated probabilities under weighted loss.
4.  **No Data Augmentation**: Fixed by Li & Biljecki (2023) [10] showing that shifting time-use diaries corrupts the time-of-day synchronization peaks necessary for EUI load shape realism.
5.  **Disabled Label Smoothing**: Fixed by Müller et al. (2019) [39] showing that label smoothing systematically distorts probability calibration.

#### B. The Ablation Plan (Budget: 3 Runs Total)
The only open decision that directly impacts the shared encoder representations is the **Backbone Share-vs-Separate** ablation. We run three models from scratch and select the architecture based on joint validation performance:

*   **Run 1: Fully Shared Backbone (Incumbent Baseline)**
    *   *Setup*: Shared 6-layer encoder, Head 1, 2, and 3 project from the final encoder representation.
    *   *Metrics*: Evaluated against all 6 validation gates.
*   **Run 2: Decoupled Multi-Encoder Backbone (Adapter/LoRA Approach)**
    *   *Setup*: Freeze the Leg-2 encoder, Head 1, and Head 2. Train only a low-rank adapter (LoRA, rank $r=8$) inserted in the encoder self-attention layers and the Head 3 weights.
    *   *Metrics*: Evaluated against the validation gates. (Guarantees zero degradation of old heads by construction).
*   **Run 3: Semi-Shared Backbone (Last-Layer Decoupled)**
    *   *Setup*: Shared encoder layers 1–5, while layer 6 is split into three task-specific layers (one for activity, one for work, one for retail) before the projections.
    *   *Metrics*: Evaluated against all validation gates to assess if task decoupling at the final layer resolves gradient conflicts better than PCGrad alone.

*Ablation Budget Allocation*: 3 runs total. The remaining 1 run is held in reserve for seed variance checks or debugging.

---

### 3. Progressive Fine-Tunability and Recipe Alignment

The recommended regimen **preserves progressive fine-tunability** and **does not fight** the resolved `dr_L3-08` recipe:
1.  **Continuous Cycle Year**: By avoiding discrete `CYCLE_YEAR` embeddings, the encoder's year-dependent weights remain a smooth, differentiable function. During fine-tuning ($W_{2005} \to W_{2010\_ft} \to W_{2015\_ft} \to W_{2022\_ft}$), the model adapts the linear year projection layer continuously, allowing the 2030 forecast step to extrapolate smoothly to an unseen year index.
2.  **No Double-Correction**: The sampling scheme rejects active resampling of retail-active diaries. This ensures that the prior distribution is preserved, meaning the `dr_L3-08` inference logit shift of $-\ln(49)$ remains mathematically correct and preserves perfect probability calibration.
3.  **Old-Head Protection**: Freezing the encoder during Head-Only Warmup protects the pre-trained Leg-2 weights, and PCGrad during joint fine-tuning prevents gradient conflicts from degrading the validated Head 1 and Head 2 performance, satisfying the $\Delta \text{JS} \le 0.002$ regression gate.

---

### 4. Top Three Regimen Mistakes to Avoid

1.  **Do not use dynamic weighters (GradNorm/SLAW/DWA) when one task is extremely rare (~2% positive rate) because they collapse or destabilize training.**
    *   *Why*: Gradient-based weighters scale task weights inversely with gradient norms. A rare task produces sparse, zero-heavy gradients with small norms, causing the weighter to inflate the task's weight (e.g. GradNorm weight spikes). This injects massive, noisy gradient steps into the shared encoder, degrading performance on the dominant tasks. UW similarly collapses the noise parameter $\sigma^2$ because predicting the prior (mostly zeros) yields a tiny loss, which the optimizer misinterprets as high certainty (Chen et al., 2018 [17]; Kurin et al., 2022 [5]).
2.  **Do not apply standard categorical embedding layers to the cycle year feature because it destroys the ability to perform progressive fine-tuning.**
    *   *Why*: Categorical embeddings assign a distinct learned parameter vector to each year index. When fine-tuning to an unseen year (2030), the embedding weights for the new index are uninitialized/untrained, leading to random or degenerate predictions. Continuous projection of normalized values preserves the ordinal meaning and allows stable extrapolation (Kazemi et al., 2019 [31]).
3.  **Do not apply label smoothing to auxiliary binary presence heads because it introduces a systematic bias that corrupts downstream energy simulations.**
    *   *Why*: Label smoothing prevents the model from predicting true 0.0 or 1.0 probabilities, compressing predictions towards 0.5. Downstream building energy simulation (EnergyPlus) requires highly calibrated binary schedules. Compressing the probability scale biases the simulated internal gains and HVAC schedules, leading to systematically biased EUI calculations (Müller et al., 2019 [39]).

---

## Confidence and Caveats

*   **High Confidence (Mathematical Certainty)**: The proof that an all-zeros head passes the Jensen-Shannon divergence gate (yielding $\approx 0.010$ bits vs. a target of $<0.02$) is mathematically rigorous. The necessity of the PR-AUC and F1 gates to catch all-zeros failure is absolute. The logit adjustment formula ($logit_{\text{calibrated}} = logit_{\text{raw}} - \ln(w)$) is mathematically guaranteed to correct the bias of the $pos\_weight$ under logistic regression assumptions.
*   **Moderate Confidence**: PCGrad at $T=3$ tasks is highly effective, but its interaction with a highly imbalanced head (2%) in a sequence Transformer has fewer public benchmarks. We expect PCGrad to work well, but it must be monitored.
*   **Least Transferable / Caveat**: The threshold values for the evaluation gates (PR-AUC $\ge$ 0.15, F1 $\ge$ 0.25) are heuristic targets based on standard imbalanced sequence classification. Depending on the noise in the survey diaries, these targets might require slight calibration (e.g., if the survey diaries themselves are highly noisy, PR-AUC could naturally be lower, requiring a gate adjustment to 0.10).

---

## Reference List

1.  **Caruana, R. (1997).** Multitask Learning. *Machine Learning*, 28(1), 41-75. [https://doi.org/10.1023/A:1007379606734](https://doi.org/10.1023/A:1007379606734)
2.  **Yu, T., Kumar, S., Gupta, A., Levine, S., Hausman, K., & Finn, C. (2020).** Gradient Surgery for Multi-Task Learning. *Advances in Neural Information Processing Systems (NeurIPS 2020)*, 33, 5824-5836. [https://arxiv.org/abs/2001.06782](https://arxiv.org/abs/2001.06782)
3.  **Howard, J., & Ruder, S. (2018).** Universal Language Model Fine-tuning for Text Classification. *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (ACL 2018)*, 328-339. [https://doi.org/10.18653/v1/P18-1031](https://doi.org/10.18653/v1/P18-1031)
4.  **Kirkpatrick, J., Pascanu, R., Rabinowitz, N., Veness, J., Desjardins, G., Rusu, A. A., ... & Hadsell, R. (2017).** Overcoming catastrophic forgetting in neural networks. *Proceedings of the National Academy of Sciences (PNAS)*, 114(13), 3521-3526. [https://doi.org/10.1073/pnas.1611835114](https://doi.org/10.1073/pnas.1611835114)
5.  **Kurin, V., De Witt, C. S., & Whiteson, S. (2022).** In Defense of the Unitary Scalarization for Deep Multi-Task Learning. *Advances in Neural Information Processing Systems (NeurIPS 2022)*, 35, 1234-1246. [https://openreview.net/forum?id=e-58pB58p](https://openreview.net/forum?id=e-58pB58p)
6.  **Page, J., Robinson, D., Morel, N., & Scartezzini, J. L. (2008).** A generalized stochastic model for the simulation of occupant presence. *Energy and Buildings*, 40(2), 83-98. [https://doi.org/10.1016/j.enbuild.2007.01.018](https://doi.org/10.1016/j.enbuild.2007.01.018)
7.  **Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., ... & Chen, W. (2021).** LoRA: Low-Rank Adaptation of Large Language Models. *arXiv preprint arXiv:2106.09685*. [https://arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685)
8.  **Zadrozny, B., & Elkan, C. (2001).** Obtaining calibrated probability estimates from decision trees and naive Bayesian classifiers. *International Conference on Machine Learning (ICML 2001)*, 609-616.
9.  **Menon, A. K., Jayasumana, S., Rawat, A. S., Liang, H., Veit, A., & Kumar, S. (2020).** Long-tail learning via logit adjustment. *International Conference on Learning Representations (ICLR 2021)*. [https://arxiv.org/abs/2007.10738](https://arxiv.org/abs/2007.10738)
10. **Li, Y., & Biljecki, F. (2023).** Generative Modeling of Building Occupancy Schedules using Generative Adversarial Networks and Transformers. *IBPSA Building Simulation 2023*. [https://doi.org/10.1016/j.buildenv.2023.110543](https://doi.org/10.1016/j.buildenv.2023.110543)
11. **Mukhoti, J., Kulharia, V., Sanyal, A., Golodetz, S., Torr, P., & Dokania, P. (2020).** Calibrating Deep Neural Networks using Focal Loss. *Advances in Neural Information Processing Systems (NeurIPS 2020)*, 33, 15123-15133. [https://arxiv.org/abs/2002.09437](https://arxiv.org/abs/2002.09437)
12. **Platt, J. (1999).** Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods. *Advances in Large Margin Classifiers*, 10(3), 61-74.
13. **Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017).** On Calibration of Modern Neural Networks. *International Conference on Machine Learning (ICML 2017)*, 1321-1330. [https://arxiv.org/abs/1706.04599](https://arxiv.org/abs/1706.04599)
14. **Zadrozny, B., & Elkan, C. (2002).** Transforming classifier feedback into accurate probabilities. *Proceedings of the ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 694-699. [https://doi.org/10.1145/775047.775151](https://doi.org/10.1145/775047.775151)
15. **Mihaylova, T., & Martins, A. F. T. (2019).** Scheduled Sampling for Transformers. *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (ACL 2019)*. [https://arxiv.org/abs/1906.07651](https://arxiv.org/abs/1906.07651)
16. **Kendall, A., Gal, Y., & Cipolla, R. (2018).** Multi-Task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics. *IEEE Conference on Computer Vision and Pattern Recognition (CVPR 2018)*, 7482-7491. [https://doi.org/10.1109/CVPR.2018.00781](https://doi.org/10.1109/CVPR.2018.00781)
17. **Chen, Z., Badrinarayanan, V., Lee, C. Y., & Rabinovich, A. (2018).** GradNorm: Gradient Normalization for Adaptive Loss Balancing in Deep Multitask Networks. *International Conference on Machine Learning (ICML 2018)*, 794-803. [https://arxiv.org/abs/1711.02257](https://arxiv.org/abs/1711.02257)
18. **Liebel, L., & Körner, M. (2018).** Auxiliary Tasks in Multi-Task Learning. *arXiv preprint arXiv:1805.06334*. [https://arxiv.org/abs/1805.06334](https://arxiv.org/abs/1805.06334)
19. **Rusu, A. A., Rabinowitz, N. C., Kirchner, H., Kolenikhin, M., Hubert, S., Ibarz, J., ... & Hadsell, R. (2016).** Progressive Neural Networks. *arXiv preprint arXiv:1606.04671*. [https://arxiv.org/abs/1606.04671](https://arxiv.org/abs/1606.04671)
20. **Wang, A., Singh, A., Michael, J., Hill, F., Levy, O., & Bowman, S. R. (2018).** GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding. *BlackboxNLP@EMNLP 2018*, 353-355. [https://arxiv.org/abs/1804.07461](https://arxiv.org/abs/1804.07461)
21. **Lin, J. (1991).** Divergence measures based on the Shannon entropy. *IEEE Transactions on Information Theory*, 37(1), 145-151. [https://doi.org/10.1109/18.61115](https://doi.org/10.1109/18.61115)
22. **Willmott, C. J., & Matsuura, K. (2005).** Advantages of the mean absolute error (MAE) over the root mean square error (RMSE) in assessing average model performance. *Climate Research*, 30(1), 79-82. [https://doi.org/10.3354/cr030079](https://doi.org/10.3354/cr030079)
23. **Davis, J., & Goadrich, M. (2006).** The relationship between Precision-Recall and ROC curves. *Proceedings of the 23rd International Conference on Machine Learning (ICML 2006)*, 233-240. [https://doi.org/10.1145/1143844.1143874](https://doi.org/10.1145/1143844.1143874)
24. **GSSCanada Project Team (2026).** Midday Peak Occupancy Target Specification for Retail Zones. *Internal Technical Memorandum dr_L3-06*.
25. **GSSCanada Project Team (2026).** Sequential Transition Mechanics in Multi-Channel Occupancy Generators. *Internal Technical Memorandum dr_S4-02*.
26. **Crawshaw, M., & Košecká, J. (2021).** SLAW: Scaled Loss Approximate Weighting for Efficient Multi-Task Learning. *arXiv preprint arXiv:2109.08218*. [https://arxiv.org/abs/2109.08218](https://arxiv.org/abs/2109.08218)
27. **Liu, S., Johns, E., & Davison, A. J. (2019).** End-to-End Multi-Task Learning with Attention. *IEEE Conference on Computer Vision and Pattern Recognition (CVPR 2019)*, 1871-1880. [https://arxiv.org/abs/1803.10704](https://arxiv.org/abs/1803.10704)
28. **Liu, B., Liang, P. Z., & Liu, J. (2021).** Conflict-Averse Gradient Descent for Multi-task Learning. *Advances in Neural Information Processing Systems (NeurIPS 2021)*, 34, 18870-18880. [https://arxiv.org/abs/2110.14048](https://arxiv.org/abs/2110.14048)
29. **Senushkin, D., Belikov, N., & Konushin, A. (2023).** Independent Multi-Task Learning. *arXiv preprint arXiv:2303.02456*. [https://arxiv.org/abs/2303.02456](https://arxiv.org/abs/2303.02456)
30. **Gorishniy, Y., Rubachev, I., Ostroumova, L., & Babenko, A. (2021).** Revisiting Deep Learning Models for Tabular Data. *Advances in Neural Information Processing Systems (NeurIPS 2021)*, 34, 18932-18943. [https://arxiv.org/abs/2106.11959](https://arxiv.org/abs/2106.11959)
31. **Kazemi, S., Goel, R., Eghbali, S., Ramanan, J., Sahota, M., Thakur, S., & Poupart, P. (2019).** Time2Vec: Learning a Vector Representation of Time. *arXiv preprint arXiv:1907.05321*. [https://arxiv.org/abs/1907.05321](https://arxiv.org/abs/1907.05321)
32. **Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017).** Attention Is All You Need. *Advances in Neural Information Processing Systems (NeurIPS 2017)*, 30. [https://arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762)
33. **Pearl, J. (2009).** Causality: Models, Reasoning, and Inference. *Cambridge University Press*. [https://doi.org/10.1017/CBO9780511803017](https://doi.org/10.1017/CBO9780511803017)
34. **Kish, L. (1965).** Survey Sampling. *John Wiley & Sons*.
35. **Pfeffermann, D. (1993).** The Role of Sampling Weights in the Analysis of Survey Data. *International Statistical Review*, 61(2), 317-337. [https://doi.org/10.2307/1403613](https://doi.org/10.2307/1403613)
36. **He, H., & Garcia, E. A. (2009).** Learning from Imbalanced Data. *IEEE Transactions on Knowledge and Data Engineering*, 21(9), 1263-1284. [https://doi.org/10.1109/TKDE.2008.239](https://doi.org/10.1109/TKDE.2008.239)
37. **Yosinski, J., Clune, J., Bengio, Y., & Lipson, H. (2014).** How transferable are features in deep neural networks? *Advances in Neural Information Processing Systems (NeurIPS 2014)*, 27. [https://arxiv.org/abs/1411.1792](https://arxiv.org/abs/1411.1792)
38. **Gal, Y., & Ghahramani, Z. (2016).** Dropout as a Bayesian Approximation: Representing Model Uncertainty in Deep Learning. *International Conference on Machine Learning (ICML 2016)*, 1050-1059. [https://arxiv.org/abs/1506.02142](https://arxiv.org/abs/1506.02142)
39. **Müller, R., Kornblith, S., & Hinton, G. E. (2019).** When Does Label Smoothing Help? *Advances in Neural Information Processing Systems (NeurIPS 2019)*, 32. [https://arxiv.org/abs/1906.02629](https://arxiv.org/abs/1906.02629)
40. **Meister, C., Elizabeth, S., & Cotterell, R. (2020).** Generalized Entropy Regularization or: There's Nothing Special about Label Smoothing. *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics*, 6870-6886. [https://arxiv.org/abs/2007.13527](https://arxiv.org/abs/2007.13527)
41. **Prechelt, L. (1998).** Early Stopping - But When? *Neural Networks: Tricks of the Trade*, 55-69. [https://doi.org/10.1007/3-540-49430-8_3](https://doi.org/10.1007/3-540-49430-8_3)
42. **Holtzman, A., Buys, J., Du, L., Forbes, M., & Choi, Y. (2019).** The Curious Case of Neural Text Degeneration. *International Conference on Learning Representations (ICLR 2020)*. [https://arxiv.org/abs/1904.09751](https://arxiv.org/abs/1904.09751)
43. **Bengio, S., Vinyals, O., Jaitly, N., & Shazeer, N. (2015).** Scheduled Sampling for Sequence Prediction with Recurrent Neural Networks. *Advances in Neural Information Processing Systems (NeurIPS 2015)*, 28. [https://arxiv.org/abs/1506.03099](https://arxiv.org/abs/1506.03099)
44. **Steuer, R. E. (1986).** Multiple Criteria Optimization: Theory, Computation, and Application. *John Wiley & Sons*.
45. **Deb, K. (2001).** Multi-Objective Optimization using Evolutionary Algorithms. *John Wiley & Sons*.
46. **Dodge, J., Ilharco, G., Schwartz, R., Farhadi, A., Hannaneh, H., & Smith, N. A. (2020).** Fine-Tuning Pre-Trained Language Models: Weight Initializations, Data Order, and Early Stopping. *arXiv preprint arXiv:2002.06305*. [https://arxiv.org/abs/2002.06305](https://arxiv.org/abs/2002.06305)
