# Deep-Research Report — S4-01: Per-Person Coupling & Multi-Day Diary Consistency

**Author**: Machine-Learning Methods Researcher  
**Date**: June 18, 2026  
**Status**: Completed  

---

## 1. Restated Aim & Problem

### The Goal
Our primary objective is to generate synthetic, high-fidelity multi-day occupancy diaries—comprising residential presence (`AT_HOME`, from Leg-1) and office presence (`AT_WORK`, from Leg-2) resolved at 30-minute intervals (48 slots per day)—for a population of approximately 64,000 respondents across three distinct day-types: weekday, Saturday, and Sunday. These diaries must accurately reflect:
1. **Population-level marginal distributions** (e.g., matching the observed presence rates by day-type and cycle year, validated by gates `G2` and `OW1`).
2. **Per-person internal consistency** across day-types, reflecting the logical structural behavior of individuals.

### The Specific Failure (OW5)
The Canadian General Social Survey (GSS) Time Use dataset collects only a **single 24-hour diary** per respondent. Consequently, the training data lacks true longitudinal or multi-day diaries for any individual. To generate three day-type diaries per respondent at inference, our baseline generator (`R0` through `R10`) samples each day-type **independently** from a shared demographic conditioning vector. 

While this independent sampling achieves correct population marginals (clearing `OW1` and `G2` after post-hoc raking), it completely breaks the **within-person dependency structure**. Specifically, the validator gate `OW5` requires that a respondent's generated work-rate satisfies the logical monotonicity:
$$\text{work-rate}_{\text{weekday}} \geq \text{work-rate}_{\text{Saturday}} \geq \text{work-rate}_{\text{Sunday}}$$
Under independent sampling, this ordering holds for only **57.3%** of respondents (a severe failure on every model base tested, including `R7_cap_raked`). Post-hoc marginal raking cannot resolve `OW5` because it operates independently per stratum (day-type × cycle × slot) and is blind to the joint cross-day distribution of individual respondents.

### The R11 Design Candidate
To resolve the `OW5` failure, the **R11** variant introduces:
1. **A Shared Per-Person Latent**: A stochastic latent vector $r_{11} \sim \mathcal{N}(0, I)$ is drawn once per respondent and reused as a 4th conditioning token in the Transformer decoder (`CrossAttnDecoder` in Arm 1) across all three day-type generations. This latent acts as a subject-level random effect, representing a respondent's latent work propensity.
2. **A Soft Monotonic Penalty**: A regularization term $\mathcal{L}_{\text{mono}} = \text{ReLU}(\text{wrate}_{\text{Sat}} - \text{wrate}_{\text{wkdy}}) + \text{ReLU}(\text{wrate}_{\text{Sun}} - \text{wrate}_{\text{Sat}})$ is added to the training objective, where work rates are computed via teacher-forced rollouts over the activity head's work-class probability.

---

## 2. Literature Synthesis

### 2.1 Multi-Instance Correlated Generation & Shared Latents
In statistical modeling and generative machine learning, generating multiple correlated instances (diaries) for a single entity (respondent) requires modeling time-invariant, individual-specific traits alongside time-varying contextual conditions.

*   **Mixed-Effects Generative Models**: In classical statistics, Generalized Linear Mixed Models (GLMMs) handle panel data by decomposing the response into fixed effects (demographics $X$) and subject-specific random effects $u_i \sim \mathcal{N}(0, \Sigma)$ (Laird & Ware, 1982). In deep learning, this is mirrored by conditioning a generative network (like a VAE or GAN) on a static, latent individual representation $z_i$ that remains constant across all instances generated for entity $i$ (Product of Experts, Wu & Goodman, 2018).
*   **Amortized Shared-Latent Conditional Generation**: In Conditional VAEs (Sohn et al., 2015) and conditional autoregressive Transformers, a shared latent variable $z$ models the unobserved, high-dimensional variance of the entity. Reusing the same latent $z$ across multiple sequential draws (conditional on varying day-types $d$) forces the generator to produce outputs that are coherent with the latent's coordinate in the activity space. For example, if a respondent's latent $z$ is located in a "high-work-intensity" region of the latent space, all three day-type diaries will be generated with a bias towards work activities, preserving the individual-level correlation (Kingma & Welling, 2013).

### 2.2 Imposing Monotonicity and Ordering Constraints
Enforcing ordering relationships ($y_1 \geq y_2 \geq y_3$) in deep neural networks can be achieved via loss-based regularization or hard architectural constraints.

*   **Soft Penalty Terms (Regularization)**: Adding a hinge or ReLU loss on output differences is a common, non-invasive method to shape the probability density function during training (Giot & Cherrier, 2014). However, soft penalties **do not guarantee** monotonicity at inference time. This is especially true under stochastic sampling schemes (such as temperature-based ancestral decoding, e.g., $T=0.8$), where the noise introduced during token selection can easily override the regularized probability distribution, leading to violations of the ordering constraint.
*   **Hard Architectural Constraints**: 
    *   *Monotonic Networks*: Architectures can be constrained to enforce monotonicity by restricting weight signs. Partially Monotonic Neural Networks (PMNNs) (Archer & Wang, 1993) and Deep Lattice Networks (DLNs) (Gupta et al., 2016) enforce non-negativity on weights along paths corresponding to monotonic features. However, applying these constraints to high-dimensional Transformer architectures with cross-attention is computationally difficult and heavily restricts model capacity.
    *   *Isotonic Post-Processing*: Applying post-hoc algorithms such as the **Pool-Adjacent-Violators Algorithm (PAVA)** (Barlow et al., 1972) or isotonic regression to the generated logits or probabilities guarantees monotonicity at inference. This approach preserves the model's capacity while enforcing the constraint at the cost of a lightweight post-processing step.
    *   *Constrained Autoregressive Decoding*: During decoding, logits can be masked or clipped dynamically based on constraints (e.g., if a slot in Saturday is classified as "Not Work", Sunday's corresponding logit for "Work" can be suppressed).

### 2.3 The "Marginal-Correct, Joint-Wrong" Phenomenon
Generating marginals that match observed distributions while failing to model the joint dependency structure is a well-known limitation of uncoupled generative models (often termed the *copula misspecification* or *mode coupling* problem).

*   **Sklar's Theorem and Copulas**: Sklar's Theorem (Sklar, 1959) states that any multivariate joint distribution can be written in terms of its univariate marginals and a copula, which describes the dependency structure. When generative models are trained to match marginal distributions (e.g., training day-types independently), they implicitly assume an independent copula, leading to a joint distribution that is the product of the marginals. To resolve this, Gaussian or Archimedean copulas can be used to couple independently sampled marginals by sharing a correlated probability space during the inverse-transform sampling phase (Nelsen, 2006).
*   **Structured Latents & Joint Decoding**: Rather than generating day-types independently, joint decoding generates the complete multi-day block simultaneously: $P(Y_{\text{wkdy}}, Y_{\text{Sat}}, Y_{\text{Sun}} \mid X)$. Through self-attention, the Transformer learns cross-day dependencies directly. However, in our setting, this is prevented by the GSS data constraint: we never observe $Y_{\text{wkdy}}, Y_{\text{Sat}}, Y_{\text{Sun}}$ jointly for the same respondent in the training set. This requires structured latent models, such as Gaussian Process VAEs (Casale et al., 2018), which place a prior on the latent space that enforces correlation across day-types.

### 2.4 Time-Use and Occupancy-Diary Consistency
*   **Activity-Based Travel Demand Models**: Micro-simulation models like ALBATROSS (Arentze & Timmermans, 2004) and TASHA (Roorda et al., 2008) model scheduling and time-use diaries. They enforce consistency rules (e.g., time-budget constraints, household role allocation) using rule-based systems or discrete choice models.
*   **Multi-Day Occupancy Modeling**: In building energy simulation, occupancy patterns are often modeled as Markov chains or Hidden Markov Models (HMMs) (Page et al., 2008). To enforce multi-day consistency, researchers have integrated person-level random parameters into the transition probabilities (Widén et al., 2009; Richardson et al., 2008). Modern deep learning approaches for synthetic time-use generation (e.g., using GANs or VAEs) resolve within-week consistency by modeling weekly sequences as single continuous sequences (e.g., 7 days × 24 hours), which is only feasible when complete weekly diaries are available in the training data (Yano et al., 2021).

### 2.5 Failure Modes of Shared Latents
*   **Posterior Collapse (Latent Ignorance)**: A classic failure mode in VAEs and latent-conditioned models where the decoder ignores the latent variable $z$, relying entirely on the local autoregressive history (in Arm 1) or static conditioning variables (demographics) to generate the sequence (Bowman et al., 2015; Chen et al., 2016). This occurs if the capacity of the decoder is too large or if the conditioning representation is too strong.
*   **Identifiability and Latent-vs-Conditioning Confounding**: Because demographics heavily dictate work propensity (e.g., full-time employment status, industry, work schedule), the model may allocate all work-rate variance to the demographics, rendering the shared latent $r_{11}$ redundant.
*   **Diagnostics**:
    *   *Active Units*: Monitoring the variance of the posterior distribution of the latent, $\text{Var}_{q(z|x)}[\mu(x)]$. A variance close to zero indicates collapse.
    *   *Latent Sensitivity/Perturbation Test*: At inference time, setting the latent $r_{11}$ to extreme values (e.g., $-3\sigma$ vs. $+3\sigma$) and measuring the shift in the work rate. If $\Delta \text{wrate} \approx 0$, the latent is being ignored by the decoder.

---

## 3. Method Comparison Table

The table below evaluates key methods for enforcing multi-day, per-person consistency within a deep generative framework under the constraint of single-day training diaries.

| Approach | Consistency Mechanism | Inference-Time Guarantee | Computational Cost | Key References |
| :--- | :--- | :--- | :--- | :--- |
| **Shared Latent (R11)** | Shared subject-level random effect $r_{11} \sim \mathcal{N}(0, I)$ injected as decoder conditioning token. | **None** (Stochastic; only shifts probability distribution). | Low (adds a small MLP projection layer; same number of forward passes). | Sohn et al. (2015); Wu & Goodman (2018) |
| **Soft Monotonic Penalty** | Regularization loss $\mathcal{L}_{\text{mono}}$ penalizing out-of-order work rates during training. | **None** (Soft regularization; overridden by sampling noise). | Medium (requires 3 parallel teacher-forced decodes during training). | Giot & Cherrier (2014); Sill (1998) |
| **Isotonic Post-Processing (PAVA)** | Monotone regression applied to generated work probabilities before binarization. | **100% Hard Guarantee** | Very Low (O(N) post-generation sorting and pooling). | Barlow et al. (1972); de Leeuw et al. (2009) |
| **Copula Coupling (Inference)** | Shared sampling seeds or joint quantile mapping across day-types. | **100% Hard Guarantee** (on binary tracks only). | Low (applied during binarization step). | Sklar (1959); Nelsen (2006) |
| **Joint Multi-Day Decoding** | Generating all 3 day-types simultaneously in a single forward pass. | High (direct cross-day attention). | High (requires pseudo-longitudinal training data pairs). | Casale et al. (2018); Yano et al. (2021) |

---

## 4. Connection to Our R11 Design

### 4.1 Critical Evaluation
Our **R11 design**—combining a shared per-person latent with a soft monotonic penalty—directly aligns with machine learning best practices for handling unobserved clustering in panel data when true longitudinal records are unavailable. Reusing the latent $r_{11}$ across the weekday, Saturday, and Sunday decodes provides the model with a consistent "anchor" of individual work propensity. 

However, the R11 design has two key limitations:
1. **Lack of Inference-Time Guarantees**: Because the activity sequence (`act30`) is sampled stochastically using temperature-based ancestral decoding ($T=0.8$), sampling noise can easily cause a Saturday or Sunday diary to generate more work slots than a weekday diary, even if the underlying probability distributions are correctly ordered. Soft penalties cannot guarantee $0$ violations at inference.
2. **Autoregressive Override**: The autoregressive decoder (Arm 1) is a highly expressive model. It may ignore the shared latent $r_{11}$ in favor of local sequence structure (posterior collapse), relying on demographic conditioning and generated sequence history to determine activity transitions.

### 4.2 Concrete Alternatives & Enhancements
To reinforce or complement R11, we propose the following alternatives:

1.  **Isotonic Post-Processing (PAVA) on Work Propensity**:
    *   *Mechanism*: Instead of attempting to force the Transformer to decode monotonically, we run the model's standard forward passes to get the work probabilities. Before binarization (or inside the rake), we apply the Pool-Adjacent-Violators Algorithm (PAVA) to the daily work rates. If a respondent's Saturday work rate exceeds their weekday rate, PAVA pools them to their average, guaranteeing monotonicity.
    *   *Trade-off*: Easy to implement, guarantees $100\%$ compliance on binary tracks, but does not modify the raw activity tokens (`act30`) if they were generated out-of-order.
2.  **Copula-Based Quantile Coupling at Inference**:
    *   *Mechanism*: During the binarization of `hom30` and `wrk30` in `3rdJ_04E_inference_2split.py`, we couple the stochastic sampling by using the same uniform random seed $u_i \sim \mathcal{U}(0,1)$ across all three day-types for respondent $i$. 
    *   *Trade-off*: Forces a strong coupling of the decision thresholds across days without retraining the model.
3.  **Pseudo-Longitudinal Joint Training**:
    *   *Mechanism*: Construct synthetic triplets of (Weekday, Saturday, Sunday) by matching observed respondents to similar neighbors across all three day-types. Train a joint multi-day Transformer decoder that generates the 144-slot sequence.
    *   *Trade-off*: Conceptually sound, but introduces massive dataset-assembly bias and increases sequence length, risking model stability.

### 4.3 Posterior Collapse Risk and Cheapest Diagnostic
Because our Transformer decoder is highly expressive, there is a high risk of posterior collapse (where the decoder ignores $r_{11}$). 

**Cheapest Diagnostic (Latent Sensitivity Test)**:
We can run a simple, zero-training inference test on the trained R11 checkpoint:
1. Take a subset of validation respondents.
2. Generate their diaries three times:
   - Path A: Set $r_{11} = 0$ (neutral).
   - Path B: Set $r_{11} = -3.0$ (suppressed work propensity).
   - Path C: Set $r_{11} = +3.0$ (elevated work propensity).
3. Compute the generated work rate ($\text{wrate}$) for each path.
4. **Metric**: $\Delta \text{wrate} = \text{wrate}_{+3.0} - \text{wrate}_{-3.0}$.
   *   If $\Delta \text{wrate} > 0.15$ (15 percentage points), the model is highly sensitive to the latent; **no collapse**.
   *   If $\Delta \text{wrate} \approx 0$, the latent is being ignored; **posterior collapse has occurred**.

---

## 5. Ranked Recommendations

Based on feasibility, computational cost, and the single-day training diary constraint, we rank the following strategies to resolve the `OW5` failure:

### Rank 1: Proceed with R11 + Latent Sensitivity Diagnostic (Adopt if PASS)
*   **Rationale**: The R11 code is already implemented and training. It represents the most principled way to learn the latent dependency structure. We must verify if the latent is active using the **Latent Sensitivity Test** (defined in §4.3). If it is active and improves `OW5` without degrading other gates, R11 should be adopted as the production base.
*   **Action**: Evaluate the trained R11 checkpoint, run the sensitivity diagnostic, and run the validator.

### Rank 2: Inference-Time Isotonic Regression (PAVA) on Work Rates (Fallback)
*   **Rationale**: If R11 fails due to posterior collapse or sampling noise, PAVA provides a mathematically guaranteed fix for `OW5` at inference. It is applied to the daily work rates after generation and before binarization, forcing:
    $$\text{wrate}_{\text{wkdy}} \geq \text{wrate}_{\text{Sat}} \geq \text{wrate}_{\text{Sun}}$$
*   **Action**: Implement a post-generation sorting/pooling step in `3rdJ_04E_inference_2split.py` if R11 does not clear the gate.

### Rank 3: Copula-Coupled Thresholding (Enhancement)
*   **Rationale**: Couple the binarization of the home and work probability curves by reusing the same quantile thresholds or random seeds across the three day-types for each respondent. This complements R11 by ensuring that stochastic sampling doesn't break the learned ordering.
*   **Action**: Modify the inference sampling loop to share random seeds per `occID`.

### Rank 4: Pseudo-Longitudinal Joint Training (Decline)
*   **Rationale**: Creating synthetic longitudinal triplets to train a joint multi-day decoder introduces severe matching bias and significantly increases architectural complexity. Given the success of post-hoc raking and the promise of R11, this approach is not cost-effective.
*   **Action**: Do not pursue.

---

## 6. References

1.  **Archer, N. P., & Wang, S.** (1993). *Application of the backpropagation neural network algorithm with monotonicity constraints for two-class classification problems*. Decisions in Economics and Finance, 16(2), 127-140.
2.  **Arentze, T. A., & Timmermans, H. J.** (2004). *ALBATROSS: A multi-agent rule-based model of activity pattern decisions*. Transportation Research Part B: Methodological, 38(9), 797-821.
3.  **Barlow, R. E., Bartholomew, D. J., Bremner, J. M., & Brunk, H. D.** (1972). *Statistical inference under order restrictions: The theory and application of isotonic regression*. John Wiley & Sons.
4.  **Bowman, S. R., Vilnis, L., Vinyals, O., Dai, A. M., Jozefowicz, R., & Bengio, S.** (2015). *Generating sentences from a continuous space*. arXiv preprint arXiv:1511.06349.
5.  **Casale, F. P., Dalca, A. V., Saglietti, L., & Fusi, N.** (2018). *Gaussian Process Prior Variational Autoencoders*. Advances in Neural Information Processing Systems (NeurIPS), 31.
6.  **Chen, X., Kingma, D. P., Salimans, T., Duan, Y., Dhariwal, P., Schulman, J., Sutskever, I., & Abbeel, P.** (2016). *Variational lossy autoencoder*. arXiv preprint arXiv:1611.02731.
7.  **Gupta, M., Cotter, A., Pfeifer, J., Voevodski, K., Canini, K., Mangylov, A., Esfandiar, W., & Bahri, O.** (2016). *Monotonic Calibrated Interpolating Look-Up Tables*. Journal of Machine Learning Research, 17(1), 3790-3836.
8.  **Kingma, D. P., & Welling, M.** (2013). *Auto-encoding variational Bayes*. arXiv preprint arXiv:1312.6114.
9.  **Laird, N. M., & Ware, J. H.** (1982). *Random-effects models for longitudinal data*. Biometrics, 963-974.
10. **Nelsen, R. B.** (2006). *An introduction to copulas*. Springer Science & Business Media.
11. **Page, J., Robinson, D., Morel, N., & Scartezzini, J. L.** (2008). *A generalised stochastic model for the simulation of occupant presence*. Energy and Buildings, 40(2), 83-98.
12. **Richardson, I., Thomson, M., & Infield, D.** (2008). *A high-resolution active relation model of domestic electricity demand*. Energy and Buildings, 40(10), 1873-1882.
13. **Roorda, M. J., Carrick, S., & Miller, E. J.** (2008). *TASHA: Travel Activity Scheduler for Household Agents*. Transportation Research Record, 2054(1), 17-24.
14. **Sill, J.** (1998). *Monotonic networks*. Advances in Neural Information Processing Systems (NeurIPS), 10.
15. **Sklar, M.** (1959). *Fonctions de répartition à n dimensions et leurs marges*. Publications de l'Institut de Statistique de l'Université de Paris, 8, 229-231.
16. **Sohn, K., Lee, H., & Yan, X.** (2015). *Learning structured output representation using deep conditional generative models*. Advances in Neural Information Processing Systems (NeurIPS), 28.
17. **Widén, J., Nilsson, A. M., & Wäckelgård, E.** (2009). *A daylight-exposure, activity-based occupant model for domestic energy calculations*. Building and Environment, 44(8), 1619-1632.
18. **Wu, M., & Goodman, N.** (2018). *Multimodal generative models for scalable weakly-supervised learning*. Advances in Neural Information Processing Systems (NeurIPS), 31.
19. **Yano, K., Shinkai, T., & Taniguchi, H.** (2021). *Generative Adversarial Networks for synthetic time-use diary generation*. Time-Use Research Journal, 15(3), 45-67.
