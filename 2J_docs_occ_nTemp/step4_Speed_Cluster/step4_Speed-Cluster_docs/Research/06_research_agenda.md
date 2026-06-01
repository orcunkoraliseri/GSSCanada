# Step-4 Deep-Research Agenda — Binary-Head Accuracy

Prepared 2026-05-15. Seven self-contained research prompts to paste into a web-based LLM (ChatGPT, Gemini, Claude.ai, Perplexity, etc.). Each prompt:

- Is **self-contained** — no references to internal files, folders, or job IDs the LLM cannot see.
- States the **research problem in domain-agnostic terms** so the LLM can answer with general deep-learning expertise.
- Asks for **comparison + recommendation + reading list**, not just a definition dump.
- Targets one specific failure mode observed in our Step-4 multi-head Transformer (AT_HOME binary head + 9-channel co-presence multi-label head + 14-class activity softmax head, jointly trained on time-use diaries).

---

## Background context to paste before any prompt (optional but recommended)

> I am training a multi-task Transformer that generates 24-hour activity diaries at 30-minute resolution (48 slots per day). Each slot has three outputs: a 14-class softmax (activity), a binary sigmoid (AT_HOME = at home / not at home), and a 9-channel multi-label sigmoid (co-presence = which household members are present). The model is trained jointly with a weighted sum of cross-entropy + two binary cross-entropy losses, plus a small marginal-distribution loss. Input is demographic features (age, sex, household size, employment) plus a target stratum (weekday / Saturday / Sunday) and a cycle year (2005 / 2010 / 2015 / 2022). The architecture is a 6-layer encoder + 6-layer cross-attention autoregressive decoder for the activity head, plus a parallel non-autoregressive fusion arm for the two binary heads. Training data is ~134k observed diaries; validation is held-out 2022 respondents.

---

## Prompt 1 — Calibration & loss formulation for binary heads

> I have a binary sigmoid head inside a multi-task Transformer that suffers from a specific pathology: at convergence, the sigmoid output collapses near 0.0 for almost every prediction (σ ≈ 0 across millions of slot predictions), yet the *marginal* aggregate prediction over a validation set is approximately correct (within 2 percentage points of ground-truth prevalence). The per-slot calibration is therefore broken — the model has learned the population-level base rate but not slot-conditional probability. Class prevalence of the positive label is roughly 60–70% (slightly imbalanced toward positive). Joint training with a 14-class softmax head and a 9-channel multi-label sigmoid head means the binary head competes for gradient with two other losses.
>
> Please give me a comprehensive comparison of modern loss functions and calibration techniques specifically designed for this failure mode. Cover at minimum:
>
> 1. **Focal Loss** (Lin et al. 2017) — how γ and α should be set when the *majority* class is positive (most "focal loss" literature assumes rare positives; my case is the opposite).
> 2. **Asymmetric Loss for Multi-Label Classification (ASL)** (Ben-Baruch et al. 2020) — whether it generalizes to single-label binary, and how the γ⁺ / γ⁻ split applies here.
> 3. **Class-Balanced Loss** (Cui et al. 2019) — the "effective number of samples" reweighting and whether it adds value when class imbalance is mild.
> 4. **Post-hoc calibration**: temperature scaling (Guo et al. 2017), Platt scaling, isotonic regression, **Beta calibration** (Kull et al. 2017), and **distribution calibration** (Kull et al. 2019 NeurIPS). Which is appropriate when the failure is sigmoid collapse rather than over-confidence?
> 5. **Label smoothing** — under what conditions it *helps* binary heads and when it actively causes the σ → 0 collapse signature I am seeing (I am currently using `home_label_smooth = 0.05`).
> 6. **Proper scoring rules** — should I be optimizing Brier score or log loss directly, and how does that interact with the multi-task loss?
>
> For each technique: explain the math in one paragraph, state when it should be preferred, and give the canonical reference. End with a **ranked recommendation** for my case (sigmoid collapse + mild positive-class imbalance + multi-task gradient competition) and three concrete implementation steps.

---

## Prompt 2 — Multi-task gradient balancing (automatic loss weighting)

> I am hand-tuning the loss weights of a multi-task Transformer with three output heads: a primary categorical head (14-class softmax), a binary head (AT_HOME), and a multi-label head (9-channel co-presence). My current weights are `λ_act = 1.0`, `λ_home = 0.7–0.9` (varies by experiment), `λ_cop = 0.3`, plus a small `λ_marg = 0.1` for a marginal-distribution auxiliary loss. Each sweep of these weights costs ~17 GPU-hours on an A100, and across a 6-month investigation I have run ~20 such sweeps without convincing myself the weights are anywhere near optimal. The binary head specifically appears under-trained — its loss plateaus at ~0.20 (a label-smoothed floor) while the activity head continues to improve.
>
> I want to replace manual lambda tuning with an **automatic / adaptive multi-task gradient balancing** algorithm. Please give me a thorough comparison of the leading methods, in chronological order:
>
> 1. **Uncertainty Weighting** (Kendall, Gal, Cipolla 2018 CVPR) — learn `log σ²` per task, treat as homoscedastic noise.
> 2. **GradNorm** (Chen et al. 2018 ICML) — normalize task gradient magnitudes to a target rate.
> 3. **MGDA-UB** (Sener & Koltun 2018 NeurIPS) — Pareto-optimal multi-task descent.
> 4. **PCGrad** (Yu, Kumar, Gupta, Levine, Hausman, Finn 2020 NeurIPS) — project conflicting gradients onto orthogonal directions.
> 5. **CAGrad** (Liu et al. 2021 NeurIPS) — conflict-averse gradient descent.
> 6. **Nash-MTL** (Navon et al. 2022 ICML) — game-theoretic equilibrium across tasks.
> 7. **Auto-λ** (Liu et al. 2022) and **FAMO** (Liu et al. 2024) — newest entries.
>
> For each method, cover: (a) the algorithmic idea in plain language, (b) the per-step overhead vs vanilla SGD (some methods require N backward passes, where N = number of tasks — this matters for a 17h training run), (c) known failure modes, and (d) the canonical reference + a high-quality follow-up paper.
>
> End with: a **decision tree** — given my specific setup (3 heads, one of which is plateauing, one of which is well-trained, training takes 17h per run, A100 budget), which method should I try first, second, third? Why?

---

## Prompt 3 — Multi-label dependency modeling & structured prediction

> I have a 9-channel multi-label binary classification head (predicting which of 9 household-member categories are co-present at each time slot). One of the 9 channels is "Alone" — by construction it is mutually exclusive with the other 8 channels. My current setup treats each channel as an independent BCE, which produces two known failure modes:
>
> 1. The model occasionally predicts `Alone=1` simultaneously with `Spouse=1` or `Children=1`. I tried an inference-time clip (`others *= (alone < 0.5)`) but that is a band-aid, not a learned structural constraint.
> 2. I tried a soft logic-loss penalty (`λ · p_alone · sum(p_others)`) and it *collapsed* the spouse channel: training pushed `p_alone` to ~0.5 everywhere and made `p_other_i` small individually, which minimized the product term cheaply while breaking per-channel calibration.
>
> I want to model the *structure* of the label set properly. Please give me a comprehensive overview of **structured prediction approaches for multi-label outputs with known dependency constraints**:
>
> 1. **Conditional Random Fields (CRFs) on top of neural encoders** — Lample et al. 2016 for sequence labeling; how to apply CRF potentials to a *non-sequential* multi-label problem.
> 2. **Probabilistic Classifier Chains** (Read et al. 2009 ECML) — explicit `p(y_2 | y_1) p(y_3 | y_1, y_2) ...` decomposition. Pros and cons vs joint modeling.
> 3. **Structured Prediction Energy Networks (SPENs)** — Belanger & McCallum 2016 ICML — energy-based joint scoring.
> 4. **Deep Value Networks** (Gygli et al. 2017) — learn an oracle scoring network.
> 5. **Hierarchical multi-label classification** — when the label tree is known a priori (Alone is the root; the 8 others are children of "not alone"), how can the loss reflect that?
> 6. **Mutual-exclusivity constraints** during training — log-barrier methods, Lagrangian relaxation, projected gradient. Why does soft logic loss fail and what alternatives exist?
> 7. **Latent variable models** — model `p(alone | y_others)` jointly via a small graphical-model head.
>
> For each: math sketch, when it works, when it doesn't, and canonical reference. End with a **specific recommendation** for my case (9 channels, 1 root-exclusive channel, BCE-trained heads, multi-task setting). Include 3 specific implementation ideas with rough complexity.

---

## Prompt 4 — Temporal persistence in non-autoregressive sequence generation

> My Transformer generates 48-slot activity diaries (24 hours × 30-minute resolution). The model produces correct **marginal** distributions per slot (Jensen-Shannon divergence < 0.05 against ground truth, well within my target), but the **transition rate** of generated diaries is approximately **158× higher** than observed diaries. In other words, the model thrashes between activities slot-by-slot rather than holding the same activity for natural durations. Real diaries show strong autocorrelation — people sleep for ~7 contiguous slots, work for ~16 contiguous slots — but the generated diaries look like white noise over a correct marginal.
>
> The architecture has a hybrid trunk: a 6-layer encoder + 6-layer autoregressive cross-attention decoder for the activity head, plus a parallel non-autoregressive fusion arm for two binary heads (AT_HOME and co-presence). The AR decoder uses teacher forcing during training; scheduled sampling was tried and *destroyed* the co-presence axis.
>
> I want to fix the temporal persistence issue *without* losing the marginal accuracy. Please give me a deep treatment of methods for enforcing temporal coherence and duration modeling in neural sequence generators:
>
> 1. **Hidden Semi-Markov Models / Neural HSMM** — Yu 2010 (HSMM survey); Liu, Yan, Zhao 2019 NeurIPS "Structured Inference for Recurrent Hidden Semi-Markov Model". Explicit duration distribution per state.
> 2. **Hidden Markov layers on top of Transformer outputs** — using Transformer logits as emission probabilities, with a small HMM enforcing transitions.
> 3. **Neural Hawkes / Marked Point Processes** — Mei & Eisner 2017 NeurIPS — event-based modeling instead of slot-based.
> 4. **Block-autoregressive / chunked generation** — generate contiguous "blocks" rather than slot-by-slot.
> 5. **Persistence regularization** — explicit loss term penalizing high transition rate (an entropy or TV regularizer over consecutive slots). What's a good formulation, and what risks does it introduce?
> 6. **Levenshtein Transformer / AR refinement of NAT outputs** — Gu, Wang, Zhao 2019 NeurIPS — iterative refinement.
> 7. **Discrete diffusion models on sequences** — Austin et al. 2021 (D3PM), Hoogeboom et al. 2021 (Multinomial Diffusion), Lou et al. 2024 (SEDD: Score Entropy Discrete Diffusion). Do these naturally enforce persistence?
> 8. **Duration modeling with negative binomial / Weibull** — used in survival analysis and event-detection literature.
>
> For each: how it works, computational cost vs my current Transformer, and references. End with a **recommendation ranked by tractability** for a single graduate researcher with one A100 — i.e., which method requires the least architectural surgery for the biggest expected reduction in transition-rate ratio? Include three concrete implementation paths.

---

## Prompt 5 — Distributional robustness & per-group calibration

> My model is evaluated on a stratified validation set with 12 cells: 4 time periods (years 2005 / 2010 / 2015 / 2022) × 3 strata (weekday / Saturday / Sunday). The **aggregate** validation metric looks good (gap of +2.1 percentage points on a key binary classifier), but the **per-cell variance is large**: individual cells range from −4 pp to +4 pp, and the root-mean-square error across cells is 4.5 pp. The aggregate is "fine" only because cells cancel.
>
> Even worse: one specific cell (most recent year × weekday) shows a 9.7 pp error because a real-world covariate shift (post-2020 remote work) inflated the positive-class rate in that cell relative to training data from earlier years. The model cannot capture this shift because it sees all four years jointly during training with simple recency weighting.
>
> I want to learn methods to **explicitly optimize worst-case-group performance** rather than average performance, and to handle **covariate shift** across the time-period dimension. Please give me a deep dive on:
>
> 1. **Distributionally Robust Optimization (DRO)** — Sagawa, Koh, Hashimoto, Liang 2019/2020 ICLR "Group DRO" — directly minimizes worst-group loss.
> 2. **Invariant Risk Minimization (IRM)** — Arjovsky, Bottou, Gulrajani, Lopez-Paz 2019 — learn representations whose predictor is optimal across environments.
> 3. **REx (Risk Extrapolation)** — Krueger et al. 2021 ICML — penalize cross-environment risk variance.
> 4. **Domain-Adversarial Neural Networks (DANN)** — Ganin et al. 2016 JMLR — adversarial domain classifier on encoder features.
> 5. **Counterfactual data augmentation** — for under-represented sub-groups (in my case the 2022-weekday shift).
> 6. **Per-group importance weighting / focal-style group weighting**.
> 7. **Mixture-of-Experts / Adapters per cycle (LoRA-style)** — Hu et al. 2021 — let each year have its own low-rank adaptation.
> 8. **Test-time adaptation** — Tent (Wang et al. 2021), continual TTA — though I have labels at test time, so this may not apply.
>
> For each method: what assumption it makes about the relationship between groups, whether it requires explicit group labels at training time (I have them), and the typical compute overhead. End with a **two-track recommendation**: one for the per-cell cancellation problem (an estimation issue) and one for the post-2020 distribution shift (a generalization issue). Give the canonical reference + one recent follow-up for each.

---

## Prompt 6 — Generative alternatives: diffusion, VAEs, flows for discrete sequences

> I currently use an autoregressive Transformer to generate categorical 48-slot sequences. The model has reached a quality ceiling where adding capacity no longer helps the binary auxiliary heads, and I have empirically observed several failure modes: per-slot sigmoid collapse (model learns the marginal not the slot-level probability), broken within-sequence persistence, and difficulty modeling joint multi-label structure. I want to understand whether **modern generative models for discrete sequences** could give me a calibrated, structurally coherent alternative to AR Transformers.
>
> Please give me a thorough comparison of the leading approaches:
>
> 1. **Discrete denoising diffusion models** — Austin et al. 2021 NeurIPS "Structured Denoising Diffusion Models in Discrete State-Spaces" (D3PM); Hoogeboom et al. 2021 "Argmax Flows and Multinomial Diffusion"; Lou et al. 2024 ICML "Discrete Diffusion Modeling by Estimating the Ratios of the Data Distribution" (SEDD, current SOTA). How do these handle conditional generation and multi-head outputs?
> 2. **Conditional Variational Autoencoders for sequences** — Sohn et al. 2015; Bowman 2016 for text; how to adapt for stratified categorical sequences with auxiliary outputs.
> 3. **Normalizing flows for discrete data** — Argmax Flows (Hoogeboom 2021), Voice Flow, integer flows.
> 4. **Latent diffusion + categorical decoder** — Rombach et al. 2022 adapted to sequences.
> 5. **Score-based models / EBMs** for joint sequence + binary head modeling.
> 6. **Masked language modeling as generative pretext** (MAE-style) — Devlin et al. 2019 (BERT); whether MLM logits can be used as a calibrated generator.
>
> For each approach: (a) inference cost vs an AR Transformer of equivalent capacity (this matters — I have an A100, not a TPU pod), (b) how conditional generation works (in my case, conditioning on demographics + cycle + stratum), (c) how auxiliary binary/multi-label heads can be attached without breaking the generative objective, (d) calibration properties — are samples naturally well-calibrated or does it need post-hoc fixing? End with a **practical ranking** by *expected payoff per engineering hour* for replacing or augmenting an AR Transformer on a discrete sequence task. Include the canonical reference and the best survey paper for each family.

---

## Prompt 7 — Structured prediction as a unifying framework, plus self-supervised pretraining

> I want to take a step back and understand the **principled umbrella** under which many of my failure modes sit. The pattern I keep seeing is: marginal distributions correct, joint distributions wrong. The model predicts the right per-slot activity histogram but cannot enforce mutual-exclusivity between co-presence labels, cannot model the joint distribution of (activity, AT_HOME) coherently, and cannot enforce temporal persistence (a structural property of the joint).
>
> This is the signature problem of **structured prediction**. Please give me a thorough survey of the modern deep-structured-prediction literature, organized as a primer for someone who has trained Transformers but never explicitly studied structured output spaces:
>
> 1. **The fundamental gap**: why pointwise losses (cross-entropy, BCE) cannot enforce joint structure, and what theoretical guarantees structured losses provide. Reference: Niculae et al. 2020 "Structured Prediction with Deep Learning: A Survey", and Niculae's PhD thesis as the best long-form entry point.
> 2. **Energy-based formulations**: LeCun 2006 tutorial; Belanger & McCallum 2016 (SPEN); modern revival in joint-EBMs (Grathwohl et al. 2020 ICLR "Your Classifier is Secretly an Energy Based Model").
> 3. **Differentiable approximations to combinatorial losses**: SparseMAP (Niculae et al. 2018); LP-relaxation losses; perturb-and-MAP (Papandreou & Yuille 2011); Gumbel-based relaxations (Jang et al. 2017, Maddison et al. 2017).
> 4. **Self-supervised pretraining as structural prior**: how does masked-diary modeling (predict held-out slots from context) bias the model toward joint coherence even when the downstream loss is pointwise? Reference: BERT 2019, T5 2020, the more recent literature on contrastive sequence learning (SimCLR adapted to sequences; SeqCLR).
> 5. **Auxiliary structural losses** as a pragmatic middle ground: pairwise consistency losses, transition penalties, label co-occurrence regularizers — when they help and when they fight the primary objective (I have empirical evidence that one such loss collapsed a head in my setup — see prompt 3).
> 6. **The connection to graphical models**: when should I add an explicit CRF or HMM layer on top of the Transformer instead of relying on the network to learn structure implicitly?
> 7. **Empirical evidence**: are there published case studies where adding structure to a strong neural baseline produced *clear* downstream gains? Or is the literature dominated by toy benchmarks where pure neural methods already saturate?
>
> End with a **research roadmap** for a researcher whose model already has good marginals but persistent joint-structure failures: which structural intervention is highest-leverage, and what is the experimental order to test it? Include the 6 most important papers (with year and venue) to read in sequence.

---

## How to use these prompts

1. Copy the **Background context** block + **one prompt** into a fresh LLM conversation. Don't combine prompts in a single conversation — each is dense enough to fill the LLM's working memory.
2. For each response, ask follow-up: *"For the top-ranked method, write me a 50-line PyTorch implementation that I could drop into a 6-layer Transformer with 3 output heads."* That gets you concrete starting code.
3. Cross-check: paste the same prompt into 2–3 different LLMs (Claude, GPT-4, Gemini) and compare which papers all three agree are canonical vs which are LLM-specific recommendations. Real canonical papers appear in every model's answer.
4. Record the recommended-paper list in a separate file; read the surveys/thesis-length references first, then the specific method papers second.

## Mapping back to Step-4 failure modes

| Prompt | Targets Step-4 issue |
|---|---|
| 1 | `home_head` σ=0.0 collapse; J2.5 GELU regression; label-smooth floor at ~0.20 |
| 2 | Manual `λ_home` 0.5→0.9 sweeps over 20+ runs without convergence |
| 3 | 2005/2010 Alone +21/+17 pp; J4_3 PINN logic-loss collapsing Spouse |
| 4 | Transition rate ratio = 157.95 (synthetic vs observed) in 04F §4 |
| 5 | Per-stratum AT_HOME RMS=4.57 pp despite aggregate +2.1 pp; 2022×WD |Δ|=9.69 pp |
| 6 | Architectural ceiling of AR Transformer — alternative to F→G→H→I→J ladder |
| 7 | Unifying frame: marginals correct, joints wrong — the signature throughout |
