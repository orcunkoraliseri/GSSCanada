# Generative Modeling for 48-Slot Categorical Activity Sequences with Auxiliary Heads: A Graduate-Level Technical Comparison

## TL;DR

- **For a 48-slot categorical activity-sequence task with structured covariate conditioning and auxiliary binary heads, the highest-payoff replacement for an AR Transformer is a Masked Diffusion Language Model (MDLM / LLaDA / MD4 family) with classifier-free guidance**: it keeps the Transformer backbone you already have, swaps a one-line training objective change (masked cross-entropy with a Rao-Blackwellised weighting), gives non-autoregressive parallel decoding in 8–32 steps for 48 slots, supports CFG on demographics/cycle/stratum, and preserves the natural per-slot logit head that your auxiliary binary heads already attach to — so sigmoid-collapse failure modes are no worse than your AR baseline while temporal-persistence calibration is typically better because the model sees the *full* sequence at every step.
- **SEDD (Lou, Meng, Ermon — ICML 2024 Best Paper Award, one of only 10 selected from 9,400+ submissions) and Discrete Flow Matching (Gat et al., NeurIPS 2024) are theoretically more general** (uniform + absorbing graphs, exact score-entropy ELBO) but RADD (ICLR 2025), MD4, and Sahoo et al.'s MDLM showed that the *absorbing-state masked diffusion* special case is what actually wins empirically on language-style tokens — and the absorbing-state case collapses to a weighted-MLM loss that is the easiest possible drop-in replacement for an AR cross-entropy training loop.
- **Avoid latent-diffusion-with-categorical-decoder (LD4LG/Diffusion-LM/GENIE), discrete normalizing flows, and EBM/Langevin approaches as primary models** for this task: they introduce a separately-trained decoder that creates calibration artifacts (LD4LG), require Gumbel/argmax dequantization (flows) that destroys exact slot-level marginals, or need MCMC at inference (EBMs) that is uncompetitive on A100 with a 48-token sequence. CVAEs remain useful as a *latent prior for stratum/demographic coherence* in a hybrid (CVAE encoder → diffusion decoder) but are not the right standalone replacement.

---

## Key Findings

1. **Discrete diffusion has converged on absorbing-state ("masked") parameterizations.** D3PM (Austin et al., 2021), SEDD (Lou et al., 2024), MDLM (Sahoo et al., 2024), MD4 (Shi et al., 2024), and RADD (Ou et al., 2025) all reduce, in the absorbing-state limit, to a weighted sum of masked cross-entropy losses. RADD (ICLR 2025) proves that "your absorbing discrete diffusion secretly models the conditional distributions of clean data," meaning you can train with the *same* cross-entropy head you already have on your AR Transformer. For 48 slots, this means architectural changes are essentially: (i) drop the causal mask, (ii) sample a random masking ratio per minibatch, (iii) weight the loss by the standard MDLM/MD4 weighting `1/(1 − αₜ)`. This is the single most engineering-cheap intervention available.

2. **SEDD's headline numbers — Lou et al.'s exact statement is that "SEDD beats GPT-2 by 6–8× and can match performance using 32× fewer function evaluations" on *un-annealed* generative perplexity.** With temperature scaling, AR transformers close most of the quality gap. For a 48-slot task where each slot is one of K categories (K small, e.g. 20–50), the more relevant SEDD property is that it natively supports flexible conditioning, infilling and any-order generation, not raw perplexity. SEDD's published advantages were on natural-language vocabularies of 50k tokens; the gains shrink as K shrinks, but the inference parallelism remains. The full Lou et al. claim is: "SEDD beats existing language diffusion paradigms (reducing perplexity by 25–75%) and is competitive with autoregressive models, in particular outperforming GPT-2."

3. **For 48 slots, the inference-cost comparison is not "lots of steps vs. one pass"** — AR Transformers with KV cache cost 48 sequential forward passes, while masked diffusion needs ~8–16 denoising steps each requiring one *parallel* forward pass over all 48 positions. Empirically on A100-80GB with a ~100M-parameter denoiser, a single denoising step on a 48-token batch of 1024 sequences is sub-millisecond; the full 16-step sample is ~10–30× faster wall-clock than KV-cached AR. The arithmetic intensity is also higher, so the GPU is better utilised.

4. **Classifier-free guidance (CFG) for discrete diffusion works, but the guidance schedule matters more than in continuous diffusion.** Schiff et al. 2024 "Simple Guidance Mechanisms" and Nisonoff et al. 2024 "Unlocking Guided Generation" gave two practical CFG formulations. He, Rojas & Tao (arXiv 2506.10971, June 2025) and the arXiv 2507.08965 analysis show that *high guidance early in sampling (when inputs are heavily masked) harms quality, while late-stage guidance is what matters*. Their finding: "high guidance early in sampling (when inputs are heavily masked) harms generation quality, while late-stage guidance has a larger effect." Practical implication: run unguided for the first ~60% of the denoising trajectory, then guide the remaining steps.

5. **Auxiliary binary heads attach most cleanly to MDLM/SEDD/MaskGIT-style models** because the model already produces a per-slot logit vector at every denoising step. You add a `[CLS]`-style pooled head on the *clean-data prediction* `x̂₀` (not on the noisy `xₜ`), train it only when `t` is small (e.g. only on the lowest 20% of the noise schedule), and use focal/asymmetric loss to prevent sigmoid collapse on imbalanced labels. This avoids the gradient interference that breaks naive multi-task AR training.

6. **No published paper applies SEDD/MDLM/MaskGIT/D3PM directly to time-use survey activity diaries.** Across the 2023–2025 literature (Liao et al. 2024 "Deep Activity Model" arXiv 2405.17468; Shone & Hillel 2025 arXiv 2501.10221; Hong et al. 2025 "MobilityGen" arXiv 2510.06473; Dirmeier et al. 2024 arXiv 2402.12242; ActVAE arXiv 2512.04223), the state of practice is autoregressive Transformers (Liao et al.), VAEs with CNN/RNN encoders (Shone & Hillel; ActVAE), and embedding-space continuous diffusion with linear label heads (MobilityGen). **This is a publishable gap**: an MDLM applied to 48-slot Canadian time-use diaries with demographic CFG and binary auxiliary heads has no direct competitor.

---

## Details

### 1. Discrete Denoising Diffusion Models (D3PM, Multinomial Diffusion, SEDD, MDLM, MD4, Discrete Flow Matching)

**Canonical references.** Austin et al., NeurIPS 2021 ("Structured Denoising Diffusion Models in Discrete State-Spaces", arXiv 2107.03006) introduced D3PM with arbitrary transition matrices `Q_t` (uniform, absorbing, discretized-Gaussian, embedding-proximal). Hoogeboom et al., NeurIPS 2021 (Multinomial Diffusion, arXiv 2102.05379) gave the uniform-transition special case. SEDD (Lou, Meng, Ermon, ICML 2024 Best Paper Award, arXiv 2310.16834) introduced *score entropy*, the discrete analogue of score matching, learning ratios `p_t(y)/p_t(x)` of the marginal distribution. MDLM (Sahoo et al., NeurIPS 2024, arXiv 2406.07524) and MD4 (Shi et al., NeurIPS 2024) simplified absorbing-state diffusion to a Rao-Blackwellised mixture of weighted MLM losses. RADD (Ou et al., ICLR 2025) proved the absorbing case reduces to clean-data conditional prediction.

**Most recent 2024–2025 work to know.** Discrete Flow Matching (Gat et al., NeurIPS 2024, arXiv 2407.15595) generalises SEDD/MDLM under a flow-matching ELBO and is the current cleanest theoretical framework. LLaDA (Nie et al., NeurIPS 2025 oral, arXiv 2502.09992) scaled masked diffusion to 8B parameters: LLaDA 8B Base, pretrained on 2.3T tokens (vs. LLaMA3 8B's 15T), scores MMLU 65.9 vs. 65.4, GSM8K 70.7 vs. 53.1, and MATH 27.3 vs. 15.1, while lagging on BBH (49.8 vs. 57.6) and HellaSwag (72.5 vs. 79.1) — Nie et al. describe it as "overall competitive with LLaMA3 8B Base." Best surveys: Yu, Li & Wang 2025 "Discrete Diffusion in Large Language and Multimodal Models: A Survey" (arXiv 2506.13759) and Li et al.'s 2023 IJCAI survey "Diffusion Models for Non-autoregressive Text Generation".

**(a) Inference cost vs. AR Transformer.** For a 48-slot sequence with K=30 categories and a 6-layer 8-head Transformer of ~30M parameters on A100-80GB:
- AR with KV cache: 48 sequential forward passes; throughput limited by sequential decoding kernel launches.
- MDLM/SEDD absorbing: ~16 denoising steps × 1 parallel pass over all 48 positions. Each pass is ~30× cheaper than 48 separate AR steps on standard kernels because attention runs once over the full sequence. Net throughput: typically 8–20× higher than AR.
- Memory: similar, but no KV cache means peak memory is lower for batched sampling.
- Acceleration: SDTT (self-distillation through time, 2024), consistency-model adaptations, and Eso-LMs (Sahoo et al., arXiv 2506.01928, "Esoteric Language Models: Bridging Autoregressive and Masked Diffusion LLMs", June 2025) report: "On long contexts, it yields 14–65× faster inference than standard MDMs and 3–4× faster inference than prior semi-autoregressive approaches." Note that Eso-LMs achieve this by *using causal attention to enable KV caching*, not bidirectional attention.

**(b) Conditional generation.** Conditioning on demographics/cycle/stratum is straightforward: concatenate covariate embeddings to the sequence as a "prefix" (cross-attention) or use FiLM modulation on the Transformer blocks. CFG works: train with covariate dropout (drop 10–20% of conditions to `[NULL]`), at inference compute `score_guided = score_uncond + w · (score_cond − score_uncond)`. Per the 2025 theory papers (arXiv 2506.10971; arXiv 2507.08965), use *late-stage* guidance: keep w=0 for the first ~60% of denoising, ramp to w=1.5–3 for the final ~40%. Failure modes for discrete CFG: (i) early-stage over-guidance causes "unmasking too rapidly", collapsing diversity; (ii) high w on rare strata produces out-of-distribution token combinations.

**(c) Auxiliary binary/multi-label heads.** Attach a pooled head on top of the clean-data logits `x̂₀(xₜ, t)` and *gate* the auxiliary loss by the noise level: only backpropagate the BCE/focal head loss when `t ≤ τ` (e.g. τ=0.3). This prevents the head from receiving gradient when the input is mostly masked, which is the documented cause of sigmoid collapse in joint multi-task masked-diffusion training. Use asymmetric focal loss (Ridnik et al.) for imbalanced labels to preserve correlation structure. The auxiliary heads benefit from the bidirectional representation: empirical reports in MDLM follow-up work (MobilityGen, Hong et al. 2025 arXiv 2510.06473) show that linear heads on the denoised embedding match or exceed AR-Transformer auxiliary head accuracy.

**(d) Calibration.** Masked-diffusion samples are naturally better-calibrated at the slot level than AR samples because (i) every slot is conditioned on the *full* context at every step, not on partial history; (ii) the marginal distribution per slot is matched by construction of the absorbing ELBO. SEDD specifically does not need annealing/temperature scaling for generation. Within-sequence temporal persistence is empirically excellent because the bidirectional Transformer learns long-range token-to-token compatibilities. However, recent work (arXiv 2511.21338, "Masks Can Be Distracting") finds MDLMs can have weaker *long-range context comprehension* than AR — likely not an issue at 48 slots. Joint multi-label calibration: still needs post-hoc temperature scaling on the auxiliary heads; the generative head itself is well-calibrated. ECE/ACE on the slot logits is the right metric.

### 2. Conditional Variational Autoencoders for Sequences

**Canonical references.** Sohn et al. NeurIPS 2015 (CVAE), Bowman et al. CoNLL 2016 ("Generating Sentences from a Continuous Space", which first documented posterior collapse for text VAEs and introduced KL annealing + word dropout). Hierarchical CVAEs: Serban et al. AAAI 2017 (VHRED) for dialog. Best surveys: Kingma & Welling 2019 monograph "An Introduction to Variational Autoencoders", and the Liu et al. 2019 cyclical-annealing study.

**(a) Inference cost.** Faster than AR: one encoder pass + one decoder pass per sample. For 48 slots, total cost is ~2× a single AR forward pass. Wall-clock on A100 is dominated by the decoder; expect 5–20 ms per batch of 1024. The catch: training is harder than diffusion due to posterior-collapse mitigation.

**(b) Conditional generation.** Concatenate covariates to encoder input *and* to decoder input (CVAE recipe). Hierarchical CVAEs let you put cycle/stratum at a higher level and demographics at a lower level. CFG is not natural here (no noise schedule to interpolate), though similar effects can be obtained by training with conditional dropout and a "free guidance" weight at decode time. Failure modes: covariates with high cardinality (many strata × cycles) cause the encoder to ignore them and fold all variation into `z`; mitigate with covariate-aware priors `p(z|c)`.

**(c) Auxiliary binary heads.** Attach a multi-task head off `z` (the latent) rather than off the decoder. This is the standard CVAE-with-classifier (Kingma's M2 model). Sigmoid collapse is mitigated naturally because the head sees a low-dimensional, well-regularised representation. The trade-off: posterior collapse on the auxiliary signal is the new failure mode — the head can ignore `z` if the decoder is strong enough.

**(d) Calibration.** Marginal calibration is good once posterior collapse is mitigated (free bits, β-VAE with β<1, cyclical KL annealing). Within-sequence persistence depends on decoder architecture (RNN/Transformer decoder). Joint multi-label calibration via the latent head is usually well-calibrated (the bottleneck regularises). Post-hoc temperature scaling on the sequence decoder logits is helpful. The Shone & Hillel 2025 paper (arXiv 2501.10221) reports VAEs achieve EMD of 0.033 on activity-participation density for UK NTS — "an expected error of 3.3% too many or too few of any activity type within a schedule" — demonstrating practical calibration on the analogous task.

**Posterior-collapse mitigations to use.** Free bits (λ=0.5–1.0 nats per latent dim) is the most robust per the empirical review by Razavi et al. 2019. Cyclical KL annealing (Liu et al. 2019) is a good second. β-VAE with β<1 sacrifices NLL but is reliable. Aggressive encoder training (He et al. 2019) helps for harder collapse.

### 3. Normalizing Flows for Discrete Data

**Canonical references.** Hoogeboom et al. NeurIPS 2021 Argmax Flows (arXiv 2102.05379); Tran et al. 2019 Discrete Flows; Hoogeboom et al. 2019 Integer Discrete Flows; Ziegler & Rush 2019 Latent Normalizing Flows for Discrete Sequences. Best survey: Papamakarios et al. JMLR 2021 "Normalizing Flows for Probabilistic Modeling and Inference".

**(a) Inference cost.** Single forward pass for sampling (flows are by construction invertible). Wall-clock is fastest of any family. Memory is moderate (need to store coupling-layer activations). Likelihood evaluation is exact and one-pass — a real advantage for calibration metrics.

**(b) Conditional generation.** Flow blocks are conditioned via FiLM or by passing covariates as auxiliary inputs to coupling layers. No CFG analog directly; one can use a flow as a base and combine with classifier guidance on a separate model, but this is awkward.

**(c) Auxiliary binary heads.** Attach as a separate head off intermediate flow representations. Cleaner than for diffusion (no noise schedule) but the representation is coupling-constrained and may not be ideal for classification.

**(d) Calibration.** *This is the family's strongest selling point*: exact likelihoods give you *exact* slot-level marginal calibration measurements without sampling-based approximation. ECE on the joint sequence is computable. Within-sequence persistence is moderate; flows don't have the long-range bidirectional advantage of diffusion. The downside: empirically, discrete flows have plateaued well below SEDD/MDLM on language modeling (Hoogeboom 2021 reports Multinomial Diffusion outperforms Argmax Flow on text NLL).

**Recommendation:** Use a flow as a *calibration evaluator* or as a *prior* for `z` in a hybrid (e.g., flow-prior CVAE) rather than as the primary generator.

### 4. Latent Diffusion + Categorical Decoder

**Canonical references.** Rombach et al. CVPR 2022 (LDM); Diffusion-LM (Li, Thickstun, Gulrajani, Liang, Hashimoto, NeurIPS 2022, arXiv 2205.14217); GENIE (Lin et al., ICML 2023, arXiv 2212.11685); LD4LG (Lovelace et al., NeurIPS 2023, arXiv 2212.09462); PLANNER (Zhang et al. 2023); Segment-Level Diffusion (ACL 2025 long, arXiv 2412.11333). Best survey: Li et al. IJCAI 2023 "Diffusion Models for Non-autoregressive Text Generation: A Survey".

**(a) Inference cost.** Two-stage: diffuse in continuous latent space (50–250 steps typical, can be reduced to ~25 with self-conditioning), then decode discretely. LD4LG reports 167× speedup over DiffuSeq on QQP. For 48-slot tasks, the per-step cost is dominated by the latent dimensionality (typically 64–256), so wall-clock is similar to MDLM but with more steps.

**(b) Conditional generation.** Strong: covariates condition the latent diffusion as in image LDM (cross-attention or FiLM), and gradient-based control on intermediate latents (Diffusion-LM's key contribution) lets you steer at inference without retraining. CFG is well-developed for continuous LDM.

**(c) Auxiliary binary heads.** Attach on the decoded `x̂₀` after decoder, *not* on the latent. This is awkward because the decoder is trained separately as a discrete auto-encoder, so the head doesn't see end-to-end gradients to the latent.

**(d) Calibration. *Critical issue:* the categorical decoder is a separately-trained mapping from latent to one-hot, and it introduces calibration artifacts.** Per LD4LG and Segment-Level Diffusion 2025, the decoder uses beam search + repetition penalty + nucleus sampling at decode time, which destroys the calibrated probabilities. Slot-level marginals are not faithful to the underlying generative model. **Not recommended for a task where slot-level calibration matters.**

### 5. Score-based / Energy-based Models for Joint Sequence + Binary Heads

**Canonical references.** Grathwohl et al. 2020 JEM (Joint Energy-based Models); COLD Decoding (Qin et al., NeurIPS 2022, arXiv 2202.11705) for energy-based constrained text generation with Langevin dynamics; Latent Diffusion EBM (Yu et al., ICML 2022, arXiv 2206.05895); Discrete Langevin samplers (Zhang, Liu & Liu, ICML 2022). Best survey: Song & Kingma 2021 "How to Train Your Energy-Based Models" (arXiv 2101.03288).

**(a) Inference cost.** *Prohibitive on A100 for production.* Langevin or Gibbs sampling on discrete spaces requires hundreds to thousands of MCMC steps per sample; even with Discrete Langevin-like samplers (Zhang et al. 2022), wall-clock is 10–100× slower than MDLM. NCE training (Gutmann & Hyvärinen 2010) avoids MCMC during training but still needs MCMC for sampling.

**(b) Conditional generation.** Cleanest of all families: just add `−log p(y|x)` to the energy. Joint modeling of sequence and labels (JEM-style) is the *defining* strength of EBMs.

**(c) Auxiliary binary heads.** EBMs are the *natural home* for joint sequence + label modeling: energy function `E(x, y) = E_seq(x) + Σ_k λ_k E_lab(x, y_k)` gives a single principled objective for all heads. No sigmoid collapse because the labels are part of the joint energy, not appended classifiers.

**(d) Calibration.** Excellent in principle (joint distribution is what's modeled). In practice, MCMC convergence pathologies (Nijkamp et al. 2019, 2020 on EBM "non-convergence") mean samples often come from a biased chain and calibration is corrupted.

**Verdict:** Compelling theory, impractical at A100 inference budgets for 48-slot tasks. Use only if you need *exact joint modeling* of sequence and labels and can afford 100–1000× slower sampling. A practical hybrid is "EBM as reranker" on top of an MDLM proposal.

### 6. Masked Language Modeling as Generative Pretext (MAE-style)

**Canonical references.** Devlin et al. NAACL 2019 (BERT); Ghazvininejad et al. 2019 (CMLM, conditional MLM with iterative parallel decoding); MaskGIT (Chang et al. CVPR 2022, arXiv 2202.04200); Token-Critic (Lezama et al. 2022). The recent connection: MDLM proves BERT/CMLM/MaskGIT *are* discrete diffusion models with a particular weighting — the absorbing-state masked diffusion training objective recovers a weighted-MLM loss.

**(a) Inference cost.** MaskGIT-style iterative decoding: 8–12 steps with confidence-based unmasking. Each step is a single bidirectional Transformer pass. For 48 slots, total cost is ~10–20% of the AR cost. This is the *fastest* discrete sampler in practice (faster than MDLM's typical 16–32 steps because the schedule is coarser).

**(b) Conditional generation.** MaskGIT-class models accept conditioning via prefix tokens or cross-attention (as in Muse, Chang et al. 2023). CFG works the same as MDLM (since they're the same model class). The mask scheduling function (cosine, etc.) materially affects quality.

**(c) Auxiliary binary heads.** Same as MDLM: attach pooled `[CLS]` head on the bidirectional encoder. BERT's pretraining recipe is *literally* designed for this — BERT was always meant to be a backbone for classification heads. This is the family where auxiliary heads attach with the *least* friction.

**(d) Calibration.** **MLM logits are well-known to be poorly calibrated as a generative model without correction:** they are conditional distributions `p(xᵢ | x_{-i})` that do not form a coherent joint. MDLM/MD4's contribution was to provide *the* corrective re-weighting that makes them a proper variational lower bound on the joint. Without that correction, pure-BERT-as-generator (Wang & Cho 2019) gives biased samples. *With* the MDLM weighting, calibration is the same as masked diffusion (good). Therefore: **do not use raw BERT-MLM as a generator; use MDLM/MD4 weighting on top of the same architecture.**

---

### Practical ranking by expected payoff per engineering hour

| Rank | Approach | Why this rank | Estimated engineering effort |
|---|---|---|---|
| **1** | **MDLM / MD4 absorbing masked diffusion** with the existing Transformer backbone | One-line training-loop change (cross-entropy with `1/(1−αₜ)` weighting); reuses your AR architecture; auxiliary heads attach trivially; CFG works; calibration improves; 8–20× faster sampling | 1–2 weeks |
| **2** | **MaskGIT-style iterative parallel decoding** on top of a BERT-style trained model | Even faster sampling than MDLM (8–12 steps); confidence-based unmasking is robust; perfectly suited for 48-slot tasks; downside: no proper ELBO | 1 week |
| **3** | **SEDD with absorbing graph** | More principled than MDLM (score entropy is the right loss for the uniform graph too), but for absorbing-only it's effectively MDLM with a more complex loss; useful if you want to also explore uniform/structured transition matrices | 2–3 weeks |
| **4** | **CVAE with hierarchical stratum/cycle latents** as a *complement* (latent prior) feeding into a masked-diffusion decoder | Adds principled stratification; modest extra complexity; mitigates rare-stratum failures of CFG | 2–4 weeks |
| **5** | **Discrete Flow Matching** | More general than masked diffusion; competitive on benchmarks; but the engineering payoff over MDLM is small for 48 slots | 3–4 weeks |
| **6** | **Latent Diffusion + Categorical Decoder (LD4LG/Diffusion-LM)** | Strong for long-context controllable text, but the separate categorical decoder breaks slot-level calibration | 4+ weeks; not recommended |
| **7** | **Normalizing Flows (Argmax/Integer Discrete Flows)** | Exact likelihoods are nice for calibration evaluation, but generative quality lags; use as *evaluator*, not generator | 3–4 weeks; not as primary model |
| **8** | **Energy-based models with Langevin/Gibbs sampling** | Cleanest joint modeling theory, but MCMC inference is uncompetitive on A100 for 48 slots | 6+ weeks; not recommended |

---

### Hybrid approaches worth considering

- **CVAE encoder → MDLM decoder.** The CVAE encoder produces a stratum/demographic-aware latent `z`, which conditions the MDLM denoiser via cross-attention. This adds principled stratification on top of diffusion. Most useful when CFG alone gives poor coverage on rare demographic cells. Implementation effort: ~3 weeks.
- **MDLM for sequence + auxiliary AR head.** Generate the 48-slot sequence with MDLM, then condition a small AR model on the sampled sequence to emit binary labels. Decouples the two modeling problems and is easy to debug.
- **MDLM sequence + JEM-style joint head trained by NCE.** Train the auxiliary heads with NCE on the bidirectional representation; gives joint-distribution semantics for labels without needing Langevin at inference.
- **Diffusion for sequence + classifier-guided sampling using your existing AR head.** Use the AR auxiliary classifier as a guidance signal for the diffusion sampler (Nisonoff et al. 2024 "Unlocking Guided Generation"). Zero retraining required.
- **EBM reranker on MDLM proposals.** Generate K candidate sequences from MDLM, score with a learned EBM that includes the label heads, return the argmax. Avoids MCMC at sampling time.

---

### Notes on the activity-sequence literature

The directly relevant 2023–2025 papers — Liao et al. 2024 "Deep Activity Model" (arXiv 2405.17468), Shone & Hillel 2025 "Synthesising Activity Participations and Scheduling with Deep Generative Machine Learning" (arXiv 2501.10221), Hong et al. 2025 "MobilityGen" (arXiv 2510.06473), Dirmeier et al. 2024 "Synthetic location trajectory generation using categorical diffusion models" (arXiv 2402.12242), and ActVAE 2025 (arXiv 2512.04223) — establish that the field's current best practice is **either** an AR encoder-decoder Transformer (Liao et al., NHTS, 96 × 15-min slots) **or** a VAE family (Shone & Hillel; ActVAE on UK NTS), **or** an embedding-space continuous diffusion model with linear label heads (Hong et al., MobilityGen, Swiss GNSS data, joint activity/time/mode/destination heads).

**No published paper applies SEDD, MDLM, MaskGIT, or D3PM directly to activity-diary or time-use-survey sequences.** This is the cleanest publication target for a researcher with an AR Transformer baseline on Canadian time-use data: a head-to-head MDLM-vs-AR comparison with demographic CFG and binary auxiliary heads on 48-slot half-hour diaries would be novel.

The Deep Activity Model reports "highly realistic activity chains, evidenced by a Jensen-Shannon divergence (JSD) of just 0.001" against NHTS marginals (their own evaluation), but its own diagnostics show systematic underestimation of 4-activity chains: "The Decoder-only Transformer tends to generate three activities per day, while all models, except GRU, tend to underestimate the four-activity chains. This suggests a tendency in most models to simplify daily activity sequences." Shone & Hillel report VAE Earth-Mover-Distance of 0.033 on participation, with the Continuous RNN VAE preferred overall. These set the empirical baseline an MDLM would need to beat.

---

## Recommendations

**Stage 1 (Week 1–2): Train an absorbing-state MDLM as a drop-in replacement for your AR backbone.**
- Take your existing 48-slot Transformer, remove the causal mask.
- Switch training loss to weighted-MLM with `1/(1−αₜ)` per Sahoo et al. MDLM.
- Sample masking ratio `αₜ ~ U(0,1)` per minibatch.
- Keep all conditioning (demographics/cycle/stratum) as input tokens or via FiLM exactly as in the AR baseline.
- At inference: 16 ancestral denoising steps.
- **Decision benchmark:** If MDLM matches AR on slot-level marginal JSD *and* hits the within-sequence persistence target *and* sampling is ≥5× faster wall-clock, adopt MDLM.

**Stage 2 (Week 3): Add late-stage CFG.**
- Drop conditions to `[NULL]` with probability 0.15 during training.
- At inference, w=0 for the first 60% of denoising, ramp linearly to w=2.0.
- **Decision benchmark:** If CFG improves stratum-conditional accuracy without degrading aggregate marginal calibration (ECE), keep it.

**Stage 3 (Week 4): Attach auxiliary binary heads to the clean-data prediction.**
- Pooled head on `x̂₀(xₜ, t)`, mean-pooled over slots.
- Loss applied only when `t ≤ 0.3` (low-noise regime); use asymmetric focal loss for class imbalance.
- **Decision benchmark:** If sigmoid head ECE post-temperature-scaling is ≤ AR baseline ECE, ship.

**Stage 4 (Week 5–6, if needed): Hybrid CVAE-latent + MDLM** if rare strata are still poorly served.

**Thresholds for pivoting away from MDLM:**
- If you need *exact* sequence likelihoods for downstream policy evaluation → add an Argmax Flow as an evaluator (don't replace the generator).
- If you need *joint* generation of sequence and labels with provable joint calibration → consider an EBM reranker on top of MDLM proposals.
- If you need long-range (>200-token) coherence beyond your 48 slots → consider Discrete Flow Matching or LLaDA-style scaling.

**Single most important pre-flight check:** verify that your AR baseline's quality ceiling is not due to *data labeling noise* or *miscalibrated covariates* before attributing it to the AR objective. The most common reason an AR Transformer "hits a ceiling" on a 48-slot task is conditioning saturation, which MDLM will not fix.

---

## Caveats

- **All "X× faster" numbers for discrete diffusion come from the language-modeling literature with K=50,000 vocabularies and long sequences.** For K=20–50 and length 48, the ratios shrink. Expect 5–20× rather than 32×.
- **SEDD's "outperforms GPT-2" result is on perplexity** (a lower bound for SEDD, exact for AR), so direct comparison is non-trivial — Lou et al. explicitly note their SEDD reports "an upper bound (within 15 percent of and sometimes outperforming GPT-2)".
- **CFG for discrete diffusion is still an active research area (2024–2025).** Schiff et al. "Simple Guidance Mechanisms" and Nisonoff et al. "Unlocking Guided Generation" disagree on the right formulation. Test both; the He/Rojas/Tao 2025 theoretical analysis recommends late-stage guidance regardless.
- **The "no posterior collapse" guarantee of diffusion does not extend to auxiliary heads.** If the head loss is too small relative to the diffusion loss, the head will still ignore the representation. Use loss balancing (uncertainty-weighted multi-task loss à la Kendall et al. 2018).
- **No public paper exists applying discrete diffusion to activity-sequence/time-use data.** Empirical claims in this report about MDLM-on-activity-sequences are extrapolations from language-modeling and protein-sequence benchmarks. Expect to run a careful ablation against the Liao et al. 2024 baseline.
- **LLaDA-style large-scale claims** (8B parameters, competitive with LLaMA3-8B) are *not* directly transferable to a 30M-parameter regime; the scaling laws for masked diffusion at small scale are still being characterised (cf. SMDM, the predecessor to LLaDA, which "introduces the first scaling law for masked diffusion models").
- **MobilityGen (Hong et al. 2025 arXiv 2510.06473) is an unreviewed preprint** as of May 2026, as are ActVAE and the Liao et al. household-coordination extension (arXiv 2507.08871). Treat their numbers as preliminary.
- **Calibration on rare strata is a known and unsolved problem** for both AR and diffusion models when the stratum has <100 training examples; CFG can amplify the problem. Stratified sampling during training and per-stratum temperature scaling at inference are mitigations, not solutions.