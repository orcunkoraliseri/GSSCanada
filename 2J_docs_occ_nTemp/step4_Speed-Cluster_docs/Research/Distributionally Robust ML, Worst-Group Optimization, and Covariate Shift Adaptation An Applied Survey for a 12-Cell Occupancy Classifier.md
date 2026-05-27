# Distributionally Robust ML, Worst-Group Optimization, and Covariate Shift Adaptation: An Applied Survey for a 12-Cell Occupancy Classifier

## TL;DR
- **For the per-cell cancellation problem (Track A, aggregate +2.1 pp but per-cell RMSE 4.5 pp):** The dominant cause is class/group imbalance plus optimizer indifference to small cells. The decision-grade recommendation is **subgroup-balanced resampling (SUBG, Idrissi et al., CLeaR 2022) plus Deep-Feature-Reweighting–style last-layer retraining (Kirichenko, Izmailov, Wilson, ICLR 2023)**, with Group DRO (Sagawa et al., ICLR 2020) as the next escalation if SUBG/DFR underperform. These methods need only the year × day-type cell labels you already have, add essentially zero compute, and directly attack the within-cell estimation-variance pathology.
- **For the post-2020 covariate/label-shift problem (Track B, 2022×weekday at 9.7 pp):** The shift is temporal, mixes covariate-shift and label-shift components, and you have labels at validation time. The right primary tool is **supervised fine-tuning of a per-period LoRA adapter (Hu et al., ICLR 2022) on 2022 data, combined with BBSE-style label-shift correction (Lipton, Wang, Smola, ICML 2018)**. Unsupervised TTA (Tent/CoTTA) is the wrong abstraction once labels are available — it becomes ordinary fine-tuning. IRM, REx, and DANN are *not* recommended as primary tools: their reported gains over ERM disappear or invert in honest benchmarks; Gulrajani & Lopez-Paz (ICLR 2021, arXiv:2007.01434) explicitly conclude that "no algorithm included in DomainBed outperforms ERM by more than one point when evaluated under the same experimental conditions."
- **Methods to deprioritize:** IRM/IRMv1 and DANN — both are well-motivated theoretically but fail empirically on benchmarks closer to the user's tabular, temporally-shifted setting, and their key assumptions (multiple causal environments; unsupervised target) do not match this problem. Counterfactual augmentation (Kaushik et al., ICLR 2020) is impractical for tabular occupancy data because there is no human-revisable counterfactual operator.

---

## Key Findings

1. **Group label availability dominates method choice.** With known (year × day-type) cells you sit in the *supervised* group-robustness regime; the simplest baselines (SUBG, Group DRO, DFR) consistently match or beat sophisticated alternatives in head-to-head benchmarks.
2. **Per-cell cancellation is an estimation-variance problem, not a representation problem.** It is fixed by reweighting/resampling and capacity control, not by invariance penalties.
3. **The 2022×weekday failure is a genuine distribution shift, not a spurious-correlation problem.** ERM-style invariance methods (IRM, V-REx, DANN) are designed for the latter and have a poor track record on the former.
4. **Test-time adaptation literature presumes unlabeled target data.** Since the user has stratified validation labels, "TTA" collapses to standard supervised fine-tuning — and the relevant question becomes how to fine-tune without catastrophic forgetting of pre-2020 years.
5. **Label-shift correction is under-used.** A non-trivial fraction of the 2022 error is plausibly a change in the marginal positive-class rate (post-COVID occupancy patterns shifted P(Y)), which BBSE-style methods correct cheaply by solving a confusion-matrix linear system.
6. **Simple data balancing has become the consensus competitive baseline** (Idrissi et al., CLeaR 2022): the paper reports SUBG actually beats Group DRO on Waterbirds (worst-group accuracy 89.1 ± 1.1 vs 87.1 ± 3.4) and is within ~1.3 points on CelebA (85.6 ± 2.3 vs 86.9 ± 1.1), while the paper states verbatim that "the subsampling baselines are 3.8 times faster than JTT and 7 times faster than gDRO while only having slightly worse worst-group-accuracy."

---

## Details — The Eight Method Families

### 1. Group DRO (Sagawa, Koh, Hashimoto, Liang) and the Hashimoto et al. 2018 ancestor

**Canonical references.**
- Hashimoto, Srivastava, Namkoong, Liang. *Fairness Without Demographics in Repeated Loss Minimization.* ICML 2018, PMLR 80:1929–1938. arXiv:1806.08010.
- Sagawa, Koh, Hashimoto, Liang. *Distributionally Robust Neural Networks for Group Shifts: On the Importance of Regularization for Worst-Case Generalization.* ICLR 2020. arXiv:1911.08731.

**Follow-up.** Idrissi, Arjovsky, Pezeshki, Lopez-Paz. *Simple Data Balancing Achieves Competitive Worst-Group Accuracy.* CLeaR 2022, PMLR 177:336–351. arXiv:2110.14503.

**Formulation.** Group DRO solves
$$ \min_\theta \max_{g \in \mathcal{G}} \; \mathbb{E}_{(x,y)\sim P_g}[\ell(\theta;x,y)] . $$
Sagawa et al. operationalize this with an online algorithm that maintains group weights $q_g$ updated by exponentiated gradient ascent on per-group loss. Hashimoto et al.'s prior unsupervised variant uses a chi-squared ambiguity set
$\mathcal{U}_\chi(\rho) = \{Q : D_\chi(Q \Vert P) \le \rho\}$, equivalent to a CVaR-style upper tail when groups are unknown; the worst-case risk has a closed form involving conditional value-at-risk of the per-example losses.

**Assumptions about group structure.** Sagawa: discrete, pre-defined groups partitioning the training data. Hashimoto: groups latent; method controls the worst quantile.

**Group labels at train time?** Yes for Sagawa-style Group DRO. No for Hashimoto-style χ²-DRO/CVaR.

**Compute overhead vs. ERM.** Sagawa: ~1× ERM (only a per-group running-loss tracker and softmax weight update). Memory: negligible. The bottleneck Sagawa et al. identify is not compute but *regularization*: strong L2 (often 10–100× ERM) and early stopping are required for the worst-group loss to generalize.

**Known failure modes.**
- *Overparameterized fit kills worst-group generalization.* If the network can drive all training losses to zero, the min-max objective and ERM coincide, and worst-group **test** error is poor. Mitigation: strong weight decay + early stopping (Sagawa et al. 2020).
- *Optimization instability* when one group's loss dominates the inner max.
- *Group annotation cost.*
- *Beaten by simpler baselines on multiple benchmarks.* Idrissi et al. (2022) report SUBG matches or beats gDRO on Waterbirds (89.1 ± 1.1 vs 87.1 ± 3.4) and is comparable on CelebA (85.6 ± 2.3 vs 86.9 ± 1.1), while running 7× faster.

---

### 2. Invariant Risk Minimization (IRM)

**Canonical reference.** Arjovsky, Bottou, Gulrajani, Lopez-Paz. *Invariant Risk Minimization.* arXiv:1907.02893, 2019.

**Follow-ups.**
- Rosenfeld, Ravikumar, Risteski. *The Risks of Invariant Risk Minimization.* ICLR 2021. arXiv:2010.05761.
- Kamath, Tangella, Sutherland, Srebro. *Does Invariant Risk Minimization Capture Invariance?* AISTATS 2021. arXiv:2101.01134.

**Formulation.** Find representation $\Phi$ such that a single classifier $w$ is simultaneously optimal across all training environments $e \in \mathcal{E}$:
$$ \min_{\Phi,w} \sum_{e} R^e(w\circ\Phi) \quad \text{s.t.} \quad w \in \arg\min_{\bar w} R^e(\bar w \circ \Phi)\;\forall e. $$
The practical surrogate IRMv1 fixes $w = 1.0$ scalar and penalizes the gradient of the per-environment risk:
$$ \min_\Phi \sum_e R^e(\Phi) + \lambda \, \big\| \nabla_{w|w=1.0} R^e(w\cdot\Phi)\big\|_2^2. $$

**Assumptions.** Multiple training environments with shared causal structure but different spurious distributions; the support of invariant features sufficiently covers the test environment.

**Group labels at train time?** Yes — environment labels are required.

**Compute overhead.** ~1.2–1.5× ERM (one extra backward through the gradient-norm penalty). The penalty weight $\lambda$ typically needs an annealing schedule and is notoriously brittle.

**Known failure modes.**
- *Identifiability requires E > d_e* (environments must exceed dimension of spurious features) in the linear regime (Rosenfeld et al. 2021). The paper states verbatim: *"we demonstrate that IRM can fail catastrophically unless the test data are sufficiently similar to the training distribution—this is precisely the issue that it was intended to solve. Thus, in this setting we find that IRM and its alternatives fundamentally do not improve over standard Empirical Risk Minimization."*
- *Non-invariant predictors can have arbitrarily small IRMv1 penalty* (Kamath et al. 2021), so the surrogate does not enforce the original constraint.
- *DomainBed (Gulrajani & Lopez-Paz, ICLR 2021, arXiv:2007.01434)* concludes verbatim that *"no algorithm included in DomainBed outperforms ERM by more than one point when evaluated under the same experimental conditions."*
- *Three training years is insufficient* for the user's setting — the 2005/2010/2015 environments are unlikely to "span" the post-2020 spurious-feature dimension.

---

### 3. Risk Extrapolation (REx)

**Canonical reference.** Krueger, Caballero, Jacobsen, Zhang, Binas, Le Priol, Courville. *Out-of-Distribution Generalization via Risk Extrapolation (REx).* ICML 2021, PMLR 139:5815–5826. arXiv:2003.00688.

**Follow-up.** Rame, Dancette, Cord. *Fishr: Invariant Gradient Variances for Out-of-Distribution Generalization.* ICML 2022. arXiv:2109.02934.

**Formulation.** V-REx penalizes variance of per-environment risks; MM-REx minimaxes over affine (extrapolated) combinations:
- V-REx: $\min_\theta \sum_e R^e(\theta) + \beta \cdot \mathrm{Var}\big(\{R^e(\theta)\}_{e\in\mathcal{E}}\big)$.
- MM-REx: $\min_\theta \max_{\sum \alpha_e = 1,\,\alpha_e \ge -\lambda_{\min}} \sum_e \alpha_e R^e(\theta)$.

**Assumptions.** Same as IRM but stronger: the authors prove V-REx recovers causal mechanisms and provides covariate-shift robustness when training environments are representative of the *direction* of test-time shifts. Better than IRM when both causal and anti-causal elements are present.

**Group labels at train time?** Yes — environment labels required.

**Compute overhead.** ~1.05× ERM (just compute variance of per-environment losses); much cheaper than IRMv1's gradient-norm penalty.

**Known failure modes.**
- *Variance penalty enforces equal training risks*, which is wrong when environments genuinely have different intrinsic difficulty (e.g., a noisier year). Pushes the model to underfit easier environments.
- *Requires more environments than spurious-feature dimensions* — same identifiability bottleneck as IRM.
- DomainBed-style evaluations show V-REx tracks ERM closely on real-world benchmarks.

---

### 4. Domain-Adversarial Neural Networks (DANN)

**Canonical reference.** Ganin, Ustinova, Ajakan, Germain, Larochelle, Laviolette, Marchand, Lempitsky. *Domain-Adversarial Training of Neural Networks.* JMLR 17(59):1–35, 2016. arXiv:1505.07818.

**Follow-up.** Acuna, Zhang, Law, Fidler. *Domain Adversarial Training: A Game Perspective.* ICLR 2022. The follow-up explicitly documents that *"GRL transforms gradient descent into a competitive gradient-based algorithm which may converge to periodic orbits"* and proposes alternative optimizers.

**Architecture.** Feature extractor $G_f$ → (label head $G_y$ + domain classifier $G_d$). A **Gradient Reversal Layer (GRL)** sits between $G_f$ and $G_d$: it is the identity on the forward pass and multiplies gradients by $-\lambda$ on the backward pass, so $G_f$ adversarially minimizes domain discriminability while $G_y$ minimizes task loss:
$$ \min_{\theta_f,\theta_y}\max_{\theta_d}\; \mathcal{L}_y(\theta_f,\theta_y) - \lambda \mathcal{L}_d(\theta_f,\theta_d). $$

**Assumptions.** Source has labels, target has unlabeled samples; goal is feature-space domain invariance.

**Group labels at train time?** Yes (source vs target labels). Target task labels not required.

**Compute overhead.** ~1.3–1.5× ERM (extra domain head + adversarial optimization). Known to be unstable: GRL transforms gradient descent into a competitive game that can converge to periodic orbits or saddle points (Acuna et al. ICLR 2022).

**Known failure modes.**
- *Domain confusion ≠ task-relevant invariance.* DANN can match marginal feature distributions while destroying label-relevant signal (especially under label shift — exactly the user's case).
- *Conditional shift broken.* DANN minimizes $H$-divergence on the marginal $P(\Phi(X))$ and does not protect against $P(Y|X)$ change.
- Inferior to IRM-family on causal benchmarks where the spurious feature is in the input distribution.

---

### 5. Counterfactual and Targeted Data Augmentation

**Canonical references (multiple, by sub-method).**
- (a) **Re-weighting / oversampling.** Idrissi, Arjovsky, Pezeshki, Lopez-Paz. *Simple Data Balancing Achieves Competitive Worst-Group-Accuracy.* CLeaR 2022, PMLR 177:336–351. arXiv:2110.14503.
- (b) **Counterfactual augmentation.** Kaushik, Hovy, Lipton. *Learning the Difference that Makes a Difference with Counterfactually-Augmented Data.* ICLR 2020. arXiv:1909.12434. Follow-up: Kaushik, Setlur, Hovy, Lipton. *Explaining the Efficacy of Counterfactually Augmented Data.* ICLR 2021.
- (c) **SMOTE.** Chawla, Bowyer, Hall, Kegelmeyer. *SMOTE: Synthetic Minority Over-sampling Technique.* JAIR 16:321–357, 2002.
- (d) **Importance weighting via density ratios.** Sugiyama, Suzuki, Nakajima, Kashima, von Bünau, Kawanabe. *Direct Importance Estimation for Covariate Shift Adaptation.* AISM 60:699–746, 2008. Also Shimodaira (2000) for the foundational formula $w(x) = q_\mathrm{test}(x)/p_\mathrm{train}(x)$.

**Formulations.**
- (a) Reweighting: $L = \sum_i (n / |g_i|) \cdot \ell(\theta; x_i, y_i)$ where $g_i$ is sample $i$'s group; subsampling: drop majority samples until balanced.
- (b) Counterfactual: human (or model) revises $(x, y) \to (x', y')$ that flips the label with minimal edits; train on $\mathrm{data} \cup \mathrm{CAD}$.
- (c) SMOTE: synthesize minority sample $\tilde{x} = x_i + \delta(x_j - x_i)$ where $x_j$ is a minority k-NN of $x_i$; adapt for tabular by encoding categoricals first.
- (d) IW-ERM: $\min_\theta \mathbb{E}_{p_{\mathrm{train}}}[\hat{w}(x) \ell(\theta; x, y)]$ with $\hat w$ from KLIEP, KMM, or LSIF.

**Assumptions.** (a) Discrete groups. (b) Existence of meaningful counterfactual edits (works for sentiment; **fails for occupancy-sensor tabular data** — there is no "counterfactual day"). (c) Local geometry of minority class is informative. (d) Source covers target support; density-ratio bounded.

**Group labels at train time?** (a) Yes. (b) Yes (which label to flip to). (c) Class label only. (d) No, only an *unlabeled* target sample.

**Compute overhead.** All ≤ 1.5× ERM; counterfactual augmentation cost is human-labor, not training cost.

**Known failure modes.**
- *Augmentation can mask rather than fix true shift.* Oversampling 2022×weekday simply re-runs ERM on a balanced set; if the conditional $P(Y|X)$ in 2022 actually differs (label shift), no amount of resampling fixes the prediction calibration.
- *SMOTE on tabular features near categorical boundaries* produces non-realistic interpolations and can hurt calibration.
- *Density-ratio estimation is unstable in high dimensions* and breaks when the train support does not cover test (Sugiyama et al. 2012). Unbounded importance weights inflate variance.
- *Counterfactual augmentation can have unintended consequences* — Joshi & He, *An Investigation of the (In)effectiveness of Counterfactually Augmented Data*, ACL 2022 (doi:10.18653/v1/2022.acl-long.256), document that *"(a) while features perturbed in CAD are indeed robust features, it may prevent the model from learning unperturbed robust features; and (b) CAD may exacerbate existing spurious correlations in the data."*

---

### 6. Per-Group Importance Weighting and Focal-Style Group Weighting

**Canonical references.**
- **Inverse-frequency / reweight-group (RWG).** Discussed in Idrissi et al. 2022 (arXiv:2110.14503) and Sagawa et al. 2020 baseline.
- **Focal loss (per-example).** Lin, Goyal, Girshick, He, Dollár. *Focal Loss for Dense Object Detection.* ICCV 2017. arXiv:1708.02002. $\mathrm{FL}(p_t) = -(1-p_t)^\gamma \log p_t$.
- **JTT.** Liu, Haghgoo, Chen, Raghunathan, Koh, Sagawa, Liang, Finn. *Just Train Twice: Improving Group Robustness without Training Group Information.* ICML 2021, PMLR 139:6781–6792. arXiv:2107.09044.
- **SUBG.** Idrissi et al. 2022 (above).

**Follow-up.** Kirichenko, Izmailov, Wilson. *Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations* (DFR). ICLR 2023. arXiv:2204.02937. The paper states verbatim: *"simple last layer retraining can match or outperform state-of-the-art approaches on spurious correlation benchmarks, but with profoundly lower complexity and computational expenses."*

**Formulations.**
- RWG: each sample weighted by $1/|g_i|$.
- Focal-on-groups: replace per-example $(1-p_t)^\gamma$ with per-group $(1 - \bar p_g)^\gamma$ where $\bar p_g$ is mean predicted probability for group $g$.
- JTT: Stage 1 train ERM for $T$ epochs ($T$ small). Stage 2 retrain with examples misclassified by stage-1 model upweighted by factor $\lambda_{\mathrm{up}}$ (typically 5–100). The paper reports that JTT "closes 75% of the gap in worst-group accuracy between standard ERM and group DRO, while only requiring group annotations on a small validation set in order to tune hyperparameters."
- SUBG: subsample each (class, group) cell to size of smallest cell; train standard ERM.
- DFR: train ERM on full data, freeze feature extractor, retrain only the final linear classifier on a group-balanced (validation) set.

**Assumptions.** Groups known (RWG, SUBG, DFR); groups unknown but worst-group misclassifications detectable on training set (JTT).

**Group labels at train time?** RWG/SUBG yes; JTT no (uses group labels only for validation hyperparameter selection); DFR uses group labels only on a small reweighting set.

**Compute overhead.** RWG: 1×. SUBG: <1× (less data!). Focal-on-groups: 1×. JTT: 2× (two training runs). DFR: trivially small additional cost (linear regression on frozen features).

**Known failure modes.**
- *RWG fails under overparameterization* unless paired with strong regularization (Sagawa et al. 2020).
- *Focal loss does not control worst-group error* directly; it controls hard *examples*, which may or may not align with worst groups.
- *JTT's stage-1 hyperparameters (epoch count $T$) are extremely sensitive*; selecting them requires a group-labeled validation set, so JTT is "group-label-free" only at training, not at model selection.
- *SUBG discards data*: when minority groups are tiny, the resulting balanced dataset may be too small to learn from. The user's 2022×weekday cell may be the smallest — subsampling all 11 other cells down to its size could throw away most data.
- *DFR caveat: requires a high-quality group-balanced reweighting set.* The user's validation set is exactly suited for this.

**Quantitative anchor (Idrissi et al. 2022, Table 2):** Worst-group accuracy on Waterbirds — gDRO 87.1 ± 3.4, **SUBG 89.1 ± 1.1**, JTT 85.6 ± 0.2, ERM 85.5 ± 1.0. On CelebA — gDRO 86.9 ± 1.1, SUBG 85.6 ± 2.3. The paper states verbatim: *"The subsampling baselines are 3.8 times faster than JTT and 7 times faster than gDRO while only having slightly worse worst-group-accuracy."*

---

### 7. Mixture-of-Experts and LoRA-Style Adapters per Temporal Group

**Canonical references.**
- **LoRA.** Hu, Shen, Wallis, Allen-Zhu, Li, Wang, Wang, Chen. *LoRA: Low-Rank Adaptation of Large Language Models.* ICLR 2022. arXiv:2106.09685.
- **Sparse MoE.** Shazeer, Mirhoseini, Maziarz, Davis, Le, Hinton, Dean. *Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer.* ICLR 2017. arXiv:1701.06538.
- **Switch Transformer.** Fedus, Zoph, Shazeer. *Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity.* JMLR 23:1–40, 2022. arXiv:2101.03961.

**Follow-up.** Hayou, Ghosh, Yu. *LoRA+: Efficient Low Rank Adaptation of Large Models.* ICML 2024. arXiv:2402.12354. Also relevant: Pfeiffer et al., *AdapterFusion*, EACL 2021.

**Formulations.**
- LoRA: replace each weight update with $W = W_0 + BA$, where $B\in\mathbb{R}^{d\times r}, A\in\mathbb{R}^{r\times k}, r \ll \min(d,k)$. Only $A, B$ are trained; $W_0$ is frozen. The LoRA paper reports it can "reduce the number of trainable parameters by 10,000 times" relative to full fine-tuning of GPT-3.
- Sparse MoE: $y = \sum_{i=1}^N G(x)_i \cdot E_i(x)$ with $G$ a sparse top-$k$ gate that activates only a few experts per token.
- Switch: hard top-1 routing — each input goes to exactly one expert.

**Application to year groups.** Hard assignment: one LoRA adapter per year (4 adapters, $r=4$–16 typical), trained on its year's data, dispatched by year ID at inference. Soft gating: learn a gate $g(\text{year})$ that mixes adapter outputs; useful when the 2020→2022 transition is smooth.

**Assumptions.** Group identity (year, day-type) known at both train and inference time.

**Group labels at train time?** Yes — required for hard assignment. Soft gating relaxes this.

**Compute overhead.** Per-adapter parameter count $\approx 2 r d_{\text{layer}}$; for a small MLP backbone this is a few percent of base. Training: roughly 1× ERM per adapter, in parallel. Inference: one forward pass with the year-specific adapter; ~1.05× ERM cost.

**Known failure modes.**
- *Year ID must be available at inference.* For forward-looking predictions (2026 onward) you must either pick an existing adapter, train a new one, or use the soft gate's extrapolation — none of which are robust.
- *Small per-cell sample sizes* (e.g., 12 cells × small data) overfit per-adapter parameters quickly; rank $r$ and early stopping become critical.
- *Information sharing across years is sacrificed* if adapters are fully separated; this is the fundamental tradeoff vs. one global model.
- *MoE load-balancing issues* in soft gating (router collapse, dead experts) — Switch's load-balancing loss is a partial fix.

---

### 8. Test-Time Adaptation (TTA)

**Canonical references.**
- **Tent.** Wang, Shelhamer, Liu, Olshausen, Darrell. *Tent: Fully Test-Time Adaptation by Entropy Minimization.* ICLR 2021 spotlight. arXiv:2006.10726.
- **CoTTA.** Wang, Fink, Van Gool, Dai. *Continual Test-Time Domain Adaptation.* CVPR 2022, pp. 7201–7211. arXiv:2203.13591.
- **T3A.** Iwasawa, Matsuo. *Test-Time Classifier Adjustment Module for Model-Agnostic Domain Generalization.* NeurIPS 2021 spotlight.
- **LAME.** Boudiaf, Mueller, Ben Ayed, Bertinetto. *Parameter-Free Online Test-Time Adaptation.* CVPR 2022 oral. arXiv:2201.05718.

**Formulations.**
- Tent: minimize entropy of predictions $H(\hat y) = -\sum_c \hat p_c \log \hat p_c$ on each test batch; update only batch-norm affine parameters online.
- CoTTA: weight-averaged teacher provides pseudo-labels under augmentation averaging; stochastic restoration of a random fraction of weights back to source values prevents catastrophic forgetting.
- T3A: maintain per-class running prototypes from confident pseudo-labeled test samples; classify by distance to prototypes. Back-prop free.
- LAME: solve a Laplacian-regularized maximum-likelihood objective on test predictions via CCCP, adjusting outputs (not parameters). The paper warns that competing TTA methods *"perform well only in narrowly-defined experimental setups and sometimes fail catastrophically when their hyperparameters are not selected for the same scenario in which they are being tested."*

**Critical point for this user: TTA's defining premise is unlabeled target data.** The user has stratified validation labels, so unsupervised TTA is *strictly dominated* by supervised fine-tuning. The TTA literature is relevant only as a *robustness* check at deployment time on future unlabeled data.

**Compute overhead.**
- Tent: ~1.01× inference (one gradient step on BN affines per batch).
- CoTTA: ~3× inference (teacher + augmentation averaging + stochastic restoration).
- T3A, LAME: back-propagation-free, negligible overhead.

**Known failure modes.**
- *Catastrophic forgetting under long online adaptation* (CoTTA was designed to fix this; Tent suffers).
- *Tent fails when test batches are class-imbalanced* — entropy minimization with skewed predictions amplifies bias (Boudiaf et al. 2022 explicitly document this).
- *Label shift is invisible to entropy minimization* — exactly the case where the 2022 positive-class rate changed.
- *Pitfalls of TTA* (Zhao et al., "On Pitfalls of Test-Time Adaptation", ICML 2023) document many setups where TTA hurts.

---

## Recommendations — Two-Track Plan

### Track A — Per-Cell Cancellation / Estimation Variance (RMSE 4.5 pp issue)

**Diagnosis.** Aggregate +2.1 pp with per-cell range −4 to +4 pp means the model has *learned the marginal* but is delivering noisy per-cell predictions whose biases happen to cancel. The 12 cells are not symmetric in size; recency-weighted ERM gives small cells too little optimization signal.

**Decision-grade recommendation (in order):**

1. **First action: SUBG (subgroup-balanced subsampling) + ERM, then DFR last-layer retrain on a balanced reweighting split.**
   - Why: Idrissi et al. (CLeaR 2022) report SUBG matches or beats gDRO on Waterbirds and is roughly comparable on CelebA at 7× the speed; Kirichenko et al. (ICLR 2023) show that retraining only the final linear layer on a group-balanced split matches gDRO with near-zero compute. Both require only the year × day-type labels you have.
   - Concrete protocol: (i) compute the smallest cell size $n_{\min}$; (ii) subsample each cell to $n_{\min}$; (iii) train ERM; (iv) on the full validation set restricted to balanced cells, retrain only the last linear layer (DFR).
   - Stop criterion: per-cell RMSE drops below 2.5 pp **and** no cell exceeds 5 pp absolute error.

2. **Escalation if (1) underperforms: Group DRO with strong L2 + early stopping.**
   - Sagawa et al. ICLR 2020 explicitly warn that the worst-group benefit appears only with **stronger-than-typical L2** (try 1e-2 to 1e-1 vs. ERM 1e-4) **and** validation-set early stopping on worst-group, not average, loss.
   - Stop criterion: worst-cell error within 2 pp of average.

3. **Do not use** IRM, V-REx, DANN here. The problem is small-cell variance, not spurious correlation across environments.

**Benchmarks that would change the recommendation.**
- If after SUBG the per-cell RMSE is *still* 4+ pp but biases are now in the *same direction*, the issue is a missing covariate, not a group-imbalance issue, and you should add features (e.g., explicit weekday × month dummies) before turning to weighted methods.
- If the smallest cell contains <100 samples, SUBG will throw away too much data and you should instead use RWG (reweighting) with capacity control.

---

### Track B — Post-2020 Covariate/Label Shift (2022×weekday 9.7 pp error)

**Diagnosis.** This is a *temporal* shift where (a) the input distribution P(X) changed (remote work → different sensor signatures on weekdays), (b) plausibly the positive-class rate P(Y) changed (fewer occupied weekday cells overall), and (c) you have validation labels for 2022. This is **supervised distribution-shift adaptation**, not unsupervised TTA.

**Decision-grade recommendation (in order):**

1. **First action: Per-period LoRA adapter for 2022 + BBSE label-shift correction.**
   - LoRA (Hu et al., ICLR 2022, arXiv:2106.09685) on a small backbone: freeze the global model, learn rank-$r$ ($r=4$–8) corrections $W_0 + BA$ on the 2022 training data. Inference uses the 2022 adapter for any 2022+ prediction; rolling re-fits as more 2022+ data arrives.
   - In parallel, apply BBSE (Lipton, Wang, Smola. *Detecting and Correcting for Label Shift with Black Box Predictors.* ICML 2018, arXiv:1802.03916). BBSE estimates importance weights $w(y) = q(y)/p(y)$ by solving the linear system $C \cdot w = \mu$, where $C$ is the source confusion matrix (estimated on labeled source data) and $\mu$ is the predicted-label marginal on (possibly unlabeled) 2022 data. The paper notes BBSE "works even when predictors are biased, inaccurate, or uncalibrated, so long as their confusion matrices are invertible." This corrects label-shift even when only a small amount of labeled 2022 data exists.
   - Why this combination: LoRA handles the covariate-shift component (P(X) change) by fitting period-specific features; BBSE handles the label-shift component (P(Y) change) and only requires the source classifier + 2022 marginals. Compute is well under 2× ERM, and parameter overhead is <5%.

2. **Secondary action: Recency-weighted Group DRO over the 12 cells with worst-cell weight pinned to 2022×weekday.**
   - Standard recency weighting (exponential decay) gives the optimizer the right gradient signal but cannot guarantee worst-cell performance. Group DRO with the 12 cells as groups, **but with a minimum weight floor on the 2022×weekday cell**, directly optimizes the failing cell.

3. **Sanity-check: Re-evaluate after holding 2022 out completely** to estimate the *intrinsic* shift gap (training only on 2005–2015 vs 2005–2022). If the gap is still ≥5 pp on a frozen architecture, no group-weighting will help; you need either more 2022 data or feature engineering for post-2020 behavior.

4. **Do not use** unsupervised Tent/CoTTA — you have labels, so this collapses to ordinary fine-tuning with no benefit and a real catastrophic-forgetting risk. **Do not use** IRM/V-REx — three pre-2020 environments cannot span the post-COVID spurious-feature dimension, and Rosenfeld et al. (ICLR 2021) prove the resulting predictor can fail catastrophically. **Do not use** DANN — its assumption of unlabeled target and its destruction of label-relevant signal under label shift are both wrong for this problem.

**Why not counterfactual augmentation?** Kaushik et al. require human-generated label-flipping edits; for tabular occupancy data there is no operational notion of a "counterfactual day" that preserves coherence, and synthesizing via SMOTE in raw feature space across a temporal boundary will produce non-realistic 2022 samples that mix pre/post-COVID dynamics. Joshi & He (ACL 2022) further document that CAD can *"exacerbate existing spurious correlations in the data,"* which is exactly the failure mode you want to avoid.

**Benchmarks that would change the recommendation.**
- If a confusion-matrix analysis on 2022 validation shows the marginal $P(Y)$ is approximately unchanged (≤1 pp drift), drop BBSE — pure LoRA fine-tuning will suffice.
- If 2022 sample size is very small (<200 labeled examples per cell), prefer DFR-style last-layer retraining on 2022 data over LoRA (fewer params, less overfitting).
- If you later need to predict 2024+ before any 2024 training data exists, none of these methods help; you need an explicit forecasting/extrapolation approach (e.g., temporal MoE with a year-embedding extrapolator), and you should treat the prediction as out-of-support.

---

## Caveats

1. **Benchmark gap.** All cited results (Waterbirds, CelebA, CivilComments, ColoredMNIST, ImageNet-C) are vision/NLP datasets with discrete spurious correlations or synthetic corruptions. The user's setting is tabular, temporal, and small-scale; quantitative gains will not transfer 1:1.
2. **Model-selection hidden cost.** Methods marketed as "group-label-free" at training time (Hashimoto-DRO, JTT, Tent) generally still require group labels at **validation** to tune hyperparameters. With the user's 12-cell stratified validation, this is not a blocker — but it is a real constraint when the user claims "no group labels are needed."
3. **Honest baselines.** Gulrajani & Lopez-Paz (ICLR 2021, arXiv:2007.01434) conclude *"no algorithm included in DomainBed outperforms ERM by more than one point when evaluated under the same experimental conditions."* Treat any single-paper claim of large gains over ERM with skepticism unless model selection was specified honestly.
4. **The 2022×weekday cell may be irreducible.** If post-2020 occupancy is fundamentally driven by a new covariate (e.g., remote-work prevalence, building-policy changes) that is not in the feature set, no algorithmic robustness method can compensate. The 9.7 pp error may be a *feature-engineering* problem in disguise. The fastest diagnostic is: train a 2022-only model and see what RMSE it achieves; if it cannot beat 5 pp on 2022 alone, the problem is not method choice.
5. **Speculative claims flagged.** Statements about future-year extrapolation (e.g., 2026 predictions) are inherently outside the support of training data; none of the surveyed methods carry formal guarantees for unseen years.
6. **The Idrissi et al. "1.7 pp average" figure was not independently re-verified** in the original paper's text body during this survey; the per-dataset Waterbirds and CelebA worst-group numbers (89.1 vs 87.1; 85.6 vs 86.9) and the verbatim 7×/3.8× speed quote are both confirmed, but readers should sanity-check any aggregate-difference claims directly against the paper's Table 2 before using them in production decisions.