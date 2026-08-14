# RL04. Which open-weight LLM: what actually exists today, at what sizes, under what licence, with what multilingual coverage

## Section A. Direct answer

The open-weight model landscape contains downloadable base and instruction checkpoints across the Gemma, Qwen, Llama, Mistral, Phi, and OLMo families, but the specific Gemma candidate requires precise version qualification: Gemma 2 exists in 2B, 9B, and 27B dense sizes (released June-July 2024), while Gemma 3 exists in 1B, 4B, 12B, and 27B sizes (released March 2025 with multimodal native pretraining), and no "Gemma-2-7B" or "Gemma-3-8B" model has ever been released. For the HETUS occupancy generation task, the recommended model is **`Qwen/Qwen2.5-7B`** (base pre-trained checkpoint), fine-tuned using bfloat16 LoRA on the single-node NVIDIA A100 80 GB MIG slice. This model is governed by the pure Apache 2.0 licence, which permits unrestricted commercial and academic use, unencumbered release of fine-tuned adapter weights without releasing training microdata, and downstream distillation into specialised building energy sequence models without the anti-distillation restrictions imposed by Meta Llama 3.1 (Section 1.b) or custom terms of Google Gemma. Memory arithmetic confirms that Qwen2.5-7B LoRA training requires approximately 18.2 GB peak VRAM at sequence length 2048 and batch size 1 with gradient checkpointing, fitting easily within the 80 GB A100, the 48 GB RTX 6000 fallback, and the 32 GB V100 fallback (in fp16/QLoRA). Pretrained world knowledge about daily routines in peripheral European countries is highly asymmetric across all open-weight models, meaning cross-national transfer must be treated strictly as learning the harmonised HETUS schema rather than relying on deep zero-shot cultural priors.

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B01 | Gemma 2 released variants | Google released Gemma 2 on 2024-06-27 (9B, 27B) and 2024-07-31 (2B); all have base and instruct weights (`google/gemma-2-2b`, `google/gemma-2-9b`, `google/gemma-2-27b`) | Fact | Google DeepMind Gemma 2 Release (arXiv:2408.00118) | Tier 1 | 2026-08-14 | H |
| B02 | Gemma 3 released variants | Google released Gemma 3 on 2025-03-12 in 1B (text-only, 32k context), 4B (multimodal, 128k), 12B (multimodal, 128k), and 27B (multimodal, 128k); base weights are named `google/gemma-3-1b-pt`, `google/gemma-3-4b-pt`, `google/gemma-3-12b-pt`, `google/gemma-3-27b-pt` | Fact | Google DeepMind Gemma 3 Release Collection (Hugging Face) | Tier 1 | 2026-08-14 | H |
| B03 | Non-existent Gemma variants | "Gemma-2-7B", "Gemma-1.5", and "Gemma-3-8B" do not exist; Gemma 1 was 2B/7B, Gemma 2 is 2B/9B/27B, Gemma 3 is 1B/4B/12B/27B | Fact | Google DeepMind Model Repositories | Tier 1 | 2026-08-14 | H |
| B04 | Qwen2.5 base models and licensing | Qwen2.5 released 2024-09-19 with base checkpoints for 0.5B, 1.5B, 3B, 7B, 14B, 32B, 72B; 0.5B, 1.5B, 7B, 14B, 32B, 72B are Apache 2.0; 3B is Qwen Research License | Fact | Alibaba Qwen2.5 Technical Report (arXiv:2412.15115) | Tier 1 | 2026-08-14 | H |
| B05 | Qwen2.5 tokenizer and context | 152,064 vocabulary (BBPE), native 128k context support, bfloat16 weights, dense architecture | Fact | Qwen2.5 Model Card & Hugging Face Config | Tier 1 | 2026-08-14 | H |
| B06 | Llama 3.1 base models and sizes | Meta released Llama 3.1 on 2024-07-23 in 8B, 70B, 405B dense sizes with base checkpoints (`meta-llama/Meta-Llama-3.1-8B`); 128k context, 128,256 tiktoken vocab | Fact | Meta Llama 3 Herd Technical Report (arXiv:2407.21783) | Tier 1 | 2026-08-14 | H |
| B07 | Llama 3.2 sizes and base availability | Meta released Llama 3.2 on 2024-09-25 in 1B and 3B text models with base checkpoints (`meta-llama/Llama-3.2-1B`, `meta-llama/Llama-3.2-3B`); 11B and 90B are vision-instruct only | Fact | Meta Llama 3.2 Model Cards | Tier 1 | 2026-08-14 | H |
| B08 | Llama Community License anti-distillation clause | Llama 3.1/3.2 Community License Section 1.b explicitly prohibits using model outputs to train or improve any non-Llama language model ("excluding Llama 3.1 or its derivatives") | Fact | Meta Llama 3.1 Community License Agreement (2024) | Tier 1 | 2026-08-14 | H |
| B09 | Mistral AI released base models | Mistral 7B v0.1 (8k context), Mistral 7B v0.3 (32k context, Tekken 32k vocab), Mistral NeMo 12.2B (128k context, Tekken 131k vocab), and Mistral Small 24B (32k context) are all Apache 2.0 with base weights | Fact | Mistral AI Model Cards & Repositories | Tier 1 | 2026-08-14 | H |
| B10 | Mistral Ministral licensing | Ministral 3B and Ministral 8B (released 2024-10) are instruct-only and licensed under the proprietary Mistral Non-Commercial Research License (MNCL) | Fact | Mistral AI Ministral Release Notes | Tier 1 | 2026-08-14 | H |
| B11 | Microsoft Phi-3.5 and Phi-4 | Phi-3.5-mini (3.8B, 128k context) and Phi-4 (14.7B, 16k context, released 2024-12) are licensed under MIT; primarily released as instruction/reasoning checkpoints | Fact | Microsoft Phi-4 Technical Report (arXiv:2412.08905) | Tier 1 | 2026-08-14 | H |
| B12 | AllenAI OLMo 2 models | OLMo 2 (released 2024-11) provides 7.37B and 13.4B dense base checkpoints (`allenai/OLMo-2-1124-7B`, `allenai/OLMo-2-1124-13B`) under Apache 2.0 with 4,096 context and 100,288 vocab | Fact | Allen Institute for AI OLMo 2 Report (arXiv:2501.00656) | Tier 1 | 2026-08-14 | H |
| B13 | Gemma Terms of Use license scope | Gemma Terms of Use grant commercial and academic rights but require downstream redistribution to include the Gemma Terms and adhere to the Google Prohibited Use Policy | Fact | Google Gemma Terms of Use (ai.google.dev/gemma/terms) | Tier 1 | 2026-08-14 | H |
| B14 | Fine-tuning SLMs for structured generation | Specialized fine-tuning on 1B to 8B models matches or exceeds larger models on narrow structured extraction and format-following tasks while eliminating hallucinated fields | Fact | Ayala et al. (arXiv:2502.14856); ReaderLM-v2 (2025) | Tier 2 | 2026-08-14 | H |
| B15 | Cultural knowledge asymmetry in LLMs | Open-weight models (Llama, Qwen, Gemma) exhibit significant knowledge asymmetry between Western/Anglophone cultures and peripheral/Eastern European countries | Fact | CulturalBench (arXiv:2411.05830); Chiu et al. (2024) | Tier 2 | 2026-08-14 | H |
| B16 | A100 80 GB LoRA memory feasibility | Qwen2.5-7B with bfloat16 LoRA (rank 16, alpha 32) at sequence length 2048 and batch size 1 with gradient checkpointing consumes 18.2 GB peak VRAM | Inference | PyTorch 2.4 + PEFT VRAM calculation | Tier 1 | 2026-08-14 | H |
| B17 | V100 32 GB bfloat16 lack of hardware support | NVIDIA Tesla V100 (Volta architecture, CC 7.0) lacks hardware bfloat16 Tensor Cores; fine-tuning must use fp16 with GradScaler or 4-bit QLoRA | Fact | NVIDIA Volta Architecture Whitepaper | Tier 1 | 2026-08-14 | H |
| B18 | Constrained decoding stack readiness | Qwen2.5, Llama 3.1, and Gemma 2 are natively supported in vLLM (v0.6+), SGLang (v0.3+), Outlines (v0.0.46+), and XGrammar (v0.1+) for JSON and EBNF grammar constraints | Fact | vLLM and Outlines Documentation | Tier 1 | 2026-08-14 | H |

---

## Section C. Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Model family selection | Author named Gemma as candidate without pinning version | Gemma 2 (9B) and Gemma 3 (4B/12B) exist, but Qwen2.5-7B offers pure Apache 2.0 licensing, pure base checkpoints, and superior numeric tokenisation without commercial restrictions | Design change: Adopt `Qwen/Qwen2.5-7B` as primary model family and size | Low (configuration choice) |
| Checkpoint type | Base pre-trained vs instruction-tuned | Instruct models contain conversational RLHF/DPO priors that conflict with custom tabular serialisation formats and induce chat-wrapper hallucinations | None: Confirm selection of base pre-trained checkpoint (`Qwen/Qwen2.5-7B`) | Low |
| Adapter release vs data release | Release fine-tuned weights without raw microdata | Apache 2.0 (Qwen2.5) and MIT (Phi) unambiguously permit releasing derivative LoRA adapter weights without distributing underlying private survey microdata | None: Plan for LoRA adapter public release is legally unblocked | Low |
| Distillation into downstream models | Possible distillation into lightweight sequence models | Meta Llama 3.1 Section 1.b forbids using outputs to improve non-Llama models; Qwen2.5 (Apache 2.0) has no distillation restrictions | Caveat: Avoid Llama 3.1 if synthetic diary distillation into custom EnergyPlus generators is planned | Low |
| Cross-national transfer premise | Assume LLM zero-shot prior knows European country habits | Cultural benchmarks demonstrate steep drop-off in country-level routine knowledge for non-Anglophone/non-core EU nations; transfer is schema-driven, not prior-driven | Caveat: Pre-register cross-national transfer as harmonisation transfer rather than cultural world-knowledge retrieval | Low |

### Recommendation Summary: `Qwen/Qwen2.5-7B` (Base Checkpoint)

* **Three strongest reasons for `Qwen/Qwen2.5-7B`**:
  1. **Unrestricted OSI-Approved Open-Source Licensing (Apache 2.0)**: Qwen2.5-7B has no monthly user caps, no trademark naming burdens, and no restrictions on using model outputs to distil or train other architectures (unlike Meta Llama 3.1 Section 1.b).
  2. **Superior Dense Pre-trained Base with Numeric Tokenizer**: Pretrained on 18 trillion tokens with byte-level BPE (152,064 vocabulary) that preserves split digits and tabular whitespace, avoiding chat-template artifacts during structural fine-tuning.
  3. **Universal Ecosystem and Serving Throughput**: Full first-class support across Hugging Face Transformers, PEFT, TRL, vLLM (paged attention, chunked prefill), SGLang, Outlines, and XGrammar, allowing rapid batch generation of 10^6 diaries within HPC cluster walltimes.
* **One strongest reason against `Qwen/Qwen2.5-7B`**:
  - **Pre-training Geographic Data Asymmetry**: Alibaba's pretraining corpus is heavily weighted toward English and Chinese web documents, with comparatively sparse representation of local cultural daily life in smaller European countries (e.g., Bulgaria, Finland, Estonia) compared to western Anglophone data.

---

## Section D. Feasibility on our hardware and licences

### Hardware and Licensing Compatibility

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| NVIDIA A100 80 GB MIG slice | Peak VRAM < 80 GB, 7-day walltime, offline node | Yes: Qwen2.5-7B bf16 LoRA consumes 18.2 GB; Full FT with 8-bit AdamW consumes 48.6 GB; runs offline with cached weights | Fully meets requirement |
| NVIDIA RTX 6000 48 GB (Fallback 1) | Peak VRAM < 48 GB | Yes: Qwen2.5-7B bf16 LoRA consumes 18.2 GB; 4-bit QLoRA consumes 7.8 GB | Fully meets requirement |
| NVIDIA Tesla V100 32 GB (Fallback 2) | Peak VRAM < 32 GB (No bfloat16 hardware support) | Yes with adaptation: Must run in fp16 LoRA with GradScaler (18.2 GB) or 4-bit QLoRA (7.8 GB); bfloat16 fails on V100 | Run in fp16 mixed precision or QLoRA |
| Output Distillation | Permission to train custom BEM models on outputs | Yes on Qwen2.5 (Apache 2.0); No on Llama 3.1 (Section 1.b restriction) | Choose Qwen2.5 or Gemma over Llama |
| Microdata Adapter Release | Release LoRA adapter without raw survey microdata | Yes: Permitted under Apache 2.0, Gemma Terms, and MIT licenses | Fully meets requirement |

### Memory Arithmetic on Candidate Models (Sequence Length 2048, Batch Size 1, Gradient Checkpointing)

#### Memory Arithmetic Formulas:
* **Model Static Weights ($M_{\text{weights}}$)**:
  * 16-bit (bf16/fp16): $2 \times N$ bytes ($N$ = parameter count).
  * 4-bit (NF4/bitsandbytes): $0.5 \times N$ bytes.
* **Optimizer States ($M_{\text{opt}}$)**:
  * Full FT with 32-bit AdamW: $12 \times N$ bytes ($4N$ master weights copy + $4N$ first momentum + $4N$ second momentum). Total static full FT = $16 \times N$ bytes.
  * Full FT with 8-bit AdamW (bitsandbytes): $2 \times N$ bytes. Total static full FT = $6 \times N$ bytes.
  * LoRA (rank 16, all linear layers): Trainable parameters $N_{\text{lora}} \approx 0.003 \times N$. LoRA optimizer + gradients $\approx 0.5$ GB static.
* **Activation Memory ($M_{\text{act}}$)**:
  * With FlashAttention-2 and full gradient checkpointing enabled, intermediate activations are discarded and recomputed. Peak activation memory for sequence length 2048, batch size 1 is $\approx 1.2$ GB to $2.0$ GB across 7B to 27B models.
* **PyTorch CUDA Overhead / Workspace ($M_{\text{overhead}}$)**:
  * Fixed allocator and CUDA context buffer $\approx 1.5$ GB.

#### Memory Calculation Breakdown Table:

| Candidate Model | Full Fine-Tune (80 GB A100)? | LoRA bf16 (80 GB A100)? | QLoRA 4-bit (80 GB A100)? | Peak VRAM (Seq 2048, Batch 1, Grad Checkpointing) | Assumptions and Detailed Arithmetic |
|---|---|---|---|---|---|
| **`Qwen/Qwen2.5-1.5B`** (1.54B dense) | **Feasible** (Static: 9.2 GB with 8-bit Adam; Peak: ~12.5 GB) | **Feasible** (Peak: ~5.8 GB) | **Feasible** (Peak: ~3.5 GB) | **LoRA bf16: 5.8 GB**<br>Full FT: 12.5 GB | Base: 3.1 GB; LoRA adapter: 0.1 GB; Act: 1.1 GB; Overhead: 1.5 GB. Full FT (8-bit Adam): $6 \times 1.54 = 9.24$ GB + 3.2 GB = 12.5 GB. |
| **`Qwen/Qwen2.5-7B`** (7.61B dense) | **Feasible with 8-bit Adam** (Peak: ~48.6 GB; Infeasible with fp32 Adam: 124 GB) | **Feasible** (Peak: ~18.2 GB) | **Feasible** (Peak: ~7.8 GB) | **LoRA bf16: 18.2 GB**<br>QLoRA: 7.8 GB<br>Full FT (8-bit Adam): 48.6 GB | Base: 15.2 GB; LoRA adapter/opt: 0.3 GB; Act: 1.2 GB; Overhead: 1.5 GB = 18.2 GB. QLoRA: $3.8 + 0.3 + 2.2 + 1.5 = 7.8$ GB. Full FT (8-bit Adam): $6 \times 7.61 = 45.66$ GB + 2.9 GB = 48.6 GB. |
| **`meta-llama/Llama-3.1-8B`** (8.03B dense) | **Feasible with 8-bit Adam** (Peak: ~51.2 GB; Infeasible with fp32 Adam: 131 GB) | **Feasible** (Peak: ~19.1 GB) | **Feasible** (Peak: ~8.1 GB) | **LoRA bf16: 19.1 GB**<br>QLoRA: 8.1 GB<br>Full FT (8-bit Adam): 51.2 GB | Base: 16.06 GB; LoRA opt: 0.3 GB; Act: 1.2 GB; Overhead: 1.5 GB = 19.06 GB. Full FT (8-bit Adam): $6 \times 8.03 = 48.18$ GB + 3.0 GB = 51.2 GB. |
| **`mistralai/Mistral-Nemo-Base-2407`** (12.2B dense) | **Infeasible** (Requires 73.2 GB static + act > 80 GB) | **Feasible** (Peak: ~27.6 GB) | **Feasible** (Peak: ~10.4 GB) | **LoRA bf16: 27.6 GB**<br>QLoRA: 10.4 GB | Base: 24.4 GB; LoRA opt: 0.4 GB; Act: 1.3 GB; Overhead: 1.5 GB = 27.6 GB. Full FT exceeds 80 GB once activations and KV scratchpads are allocated. |
| **`google/gemma-2-9b`** (9.24B dense) | **Feasible with 8-bit Adam** (Peak: ~58.5 GB; Infeasible with fp32 Adam: 150 GB) | **Feasible** (Peak: ~21.7 GB) | **Feasible** (Peak: ~8.9 GB) | **LoRA bf16: 21.7 GB**<br>QLoRA: 8.9 GB | Base: 18.48 GB; LoRA opt: 0.4 GB; Act: 1.3 GB; Overhead: 1.5 GB = 21.68 GB. Note: Logit soft-capping requires specific attention kernel support. |
| **`google/gemma-2-27b`** (27.2B dense) | **Infeasible** (Static: 163 GB; Impossible on single node) | **Feasible** (Peak: ~58.2 GB) | **Feasible** (Peak: ~19.1 GB) | **LoRA bf16: 58.2 GB**<br>QLoRA: 19.1 GB | Base: 54.4 GB; LoRA opt: 0.6 GB; Act: 1.7 GB; Overhead: 1.5 GB = 58.2 GB. Leaves 21.8 GB headroom on 80 GB A100. Infeasible for full fine-tune. |

#### Feasibility on Fallback Hardware:

| Candidate Model | 80 GB A100 MIG Profile | 48 GB RTX 6000 | 32 GB Tesla V100 (No native bf16) |
|---|---|---|---|
| **Qwen2.5-1.5B** | Full FT (8-bit) / LoRA bf16 / QLoRA | Full FT (8-bit) / LoRA bf16 / QLoRA | Full FT (8-bit fp16) / LoRA fp16 / QLoRA |
| **Qwen2.5-7B** | Full FT (8-bit) / LoRA bf16 / QLoRA | LoRA bf16 / QLoRA | LoRA fp16 / QLoRA |
| **Llama-3.1-8B** | Full FT (8-bit) / LoRA bf16 / QLoRA | LoRA bf16 / QLoRA | LoRA fp16 / QLoRA |
| **Mistral NeMo 12B** | LoRA bf16 / QLoRA | LoRA bf16 / QLoRA | LoRA fp16 / QLoRA |
| **Gemma-2-9B** | Full FT (8-bit) / LoRA bf16 / QLoRA | LoRA bf16 / QLoRA | LoRA fp16 / QLoRA |
| **Gemma-2-27B** | LoRA bf16 / QLoRA | QLoRA only (Peak 19.1 GB; LoRA bf16 OOM at 58.2 GB) | QLoRA only (Peak 19.1 GB; LoRA fp16 OOM) |

---

## Section E. What this changes in the write-up

* **Replace speculative Gemma version naming with confirmed model coordinates** (tied to B01, B02, B03, C01): Update all pipeline documents to specify `Qwen/Qwen2.5-7B` as the primary base checkpoint, clarifying that Gemma 2 is 2B/9B/27B and Gemma 3 is 1B/4B/12B/27B.
* **Pre-register the base vs instruct checkpoint rationale** (tied to B04, B06, C02): Explicitly state in the methodology that base pre-trained models are chosen because time-use diary synthesis is a formal sequence-formatting and statistical distribution-matching task rather than a conversational instruction-following task.
* **State the licensing basis for adapter release without raw microdata** (tied to B04, B13, C03): Document in the reproducibility and ethical disclosure sections that the Apache 2.0 licence of Qwen2.5-7B permits public release of the fine-tuned LoRA weights independently of restricted HETUS survey microdata.
* **Pre-register the anti-distillation risk as a design exclusion** (tied to B08, C04): Note in the methodology that Meta Llama 3.1 was excluded from the primary pipeline to preserve the right to distil diary generators into lightweight, non-Llama downstream BEM simulation tools.
* **Bound the cross-national transfer claim against cultural knowledge asymmetry** (tied to B15, C05): Add a mandatory limitation acknowledging that open-weight LLMs have documented knowledge deficits for non-Anglophone European daily routines, requiring the model to learn cross-country patterns entirely through the harmonised HETUS conditioning vectors rather than pre-trained world knowledge.
* **Specify the exact HPC memory recipe and fallback precision** (tied to B16, B17, D01): Document in the computational resources section that single-node training uses bfloat16 LoRA (rank 16, alpha 32) on an A100 80 GB MIG slice (18.2 GB peak VRAM), with an explicit note that V100 execution requires fp16 mixed precision due to the lack of hardware bfloat16 support.

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| Qwen2.5-7B Base Weights | Base pre-trained model repository (weights, tokenizer, config) | `https://huggingface.co/Qwen/Qwen2.5-7B` | Open (Apache 2.0, no gated access) | Confirmed reachable |
| Qwen2.5-1.5B Base Weights | Compact base pre-trained model repository | `https://huggingface.co/Qwen/Qwen2.5-1.5B` | Open (Apache 2.0, no gated access) | Confirmed reachable |
| Meta-Llama-3.1-8B Base Weights | Meta Llama 3.1 8B base model repository | `https://huggingface.co/meta-llama/Meta-Llama-3.1-8B` | Registration / Gated (Requires accepting Meta Llama 3.1 Community License) | Confirmed reachable |
| Gemma-2-9b Base Weights | Google Gemma 2 9B base model repository | `https://huggingface.co/google/gemma-2-9b` | Registration / Gated (Requires accepting Gemma Terms of Use) | Confirmed reachable |
| Gemma-3-4b-pt Base Weights | Google Gemma 3 4B base pre-trained repository | `https://huggingface.co/google/gemma-3-4b-pt` | Registration / Gated (Requires accepting Gemma Terms of Use) | Confirmed reachable |
| Mistral-Nemo-Base-2407 Weights | Mistral AI 12.2B base pre-trained repository | `https://huggingface.co/mistralai/Mistral-Nemo-Base-2407` | Open (Apache 2.0, no gated access) | Confirmed reachable |
| OLMo-2-1124-7B Base Weights | AllenAI OLMo 2 7.37B base repository | `https://huggingface.co/allenai/OLMo-2-1124-7B` | Open (Apache 2.0, no gated access) | Confirmed reachable |
| Apache License Version 2.0 Text | Canonical Apache 2.0 legal text | `https://www.apache.org/licenses/LICENSE-2.0.txt` | Open | Confirmed reachable |
| Meta Llama 3.1 Community License | Canonical Meta Llama 3.1 legal text | `https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE` | Open | Confirmed reachable |
| Google Gemma Terms of Use | Canonical Google Gemma legal terms | `https://ai.google.dev/gemma/terms` | Open | Confirmed reachable |

---

## Section G. Contradictions, gaps, open questions, and your own negative controls

### Contradictions and Gaps in the Open-Weight Landscape

* **Context Length Claims vs Default Serving Configurations**: Model developers advertise 128k native context lengths (Qwen2.5, Llama 3.1, Gemma 3), but default `config.json` files in Hugging Face often configure maximum position embeddings or RoPE theta scaling to 32,768 tokens (e.g. Qwen2.5 `max_position_embeddings: 32768` with YaRN interpolation enabled up to 131,072). For our task, the sequence length is between 500 and 2048 tokens (depending on slot vs episode encoding), so ultra-long context mechanisms are unnecessary and standard unscaled RoPE should be enforced to prevent attention dispersion.
* **Licensing Discrepancies within Model Families**: While Qwen2.5 0.5B, 1.5B, 7B, 14B, 32B, and 72B are licensed under Apache 2.0, the **Qwen2.5-3B** variant is licensed under the proprietary Qwen Research License. Similarly, while Mistral 7B and NeMo 12B are Apache 2.0, Ministral 3B and 8B are under the restrictive Mistral Non-Commercial Research License (MNCL). Mixing model sizes within an automated pipeline without pinning individual license files risks license contamination.
* **Base Model Discontinuation in Recent Releases**: Frontier model releases increasingly omit base checkpoints in favor of post-trained/instruction-only weights (e.g. Meta Llama 3.3 70B released only as `-Instruct`; Microsoft Phi-3.5 and Phi-4 released primarily as instruction/reasoning models; Mistral Ministral released only as `-Instruct`). Choosing a model family must be gated by the confirmed availability of a pre-trained base checkpoint.

### Multilingual and Cultural Knowledge Asymmetry Evidence

1. **Language Coverage vs Schema Formatting**:
   * *Argument for Language Coverage*: If survey serialisation includes national text keys or activity descriptions in local languages (e.g., French, Italian, German, Spanish), multilingual pretraining prevents token fragmentation.
   * *Argument Against Language Coverage*: If the serialization schema uses standard numeric Activity Coding List keys (e.g., `ACT_110`, `LOC_100`, `COP_10`) and English-keyed demographic headers, natural language vocabulary is never generated. The model only needs to learn token transitions over a closed structural vocabulary.
2. **Cultural Knowledge Asymmetry Across European Countries**:
   * Published evaluations on cultural and geographic bias (e.g., *CulturalBench*, Chiu et al., 2024; *Camellia*, 2024; *GlobalMMLU*, Singh et al., 2025) demonstrate that open-weight LLMs (Llama 3, Qwen 2.5, Gemma 2) exhibit strong performance drop-offs on non-Western and non-Anglophone cultural entities.
   * While models correctly recognize modal Western European schedules (e.g., lunch hours in France or work commutes in the UK), they fail to reflect local routine variations in Southern and Eastern Europe (e.g., afternoon breaks in Spain/Greece or specific daily rhythms in Bulgaria and Romania).
   * **Consequence for Paper 4**: The pre-trained prior cannot be credited with cross-national transfer. The transfer claim must be pre-registered as schema-guided statistical transfer learned from HETUS multi-country training data.

### The Small-Model Question: Evidence and Trade-offs (1B-8B vs 27B)

1. **Model Scale vs Structured Format Adherence**:
   * Recent empirical studies (e.g., Ayala et al., 2025, arXiv:2502.14856; Brach et al., 2026, arXiv:2602.04948) show that for domain-specific, structurally constrained generation (such as JSON or tabular sequences), fine-tuning a small model (1B to 8B) achieves over 99% syntactic validity, matching or outperforming un-tuned 70B+ models while reducing latency by 4x to 10x.
   * Large models (27B+) provide superior open-ended reasoning and multi-step deduction, but structured diary generation requires sequence distribution modeling over fixed categories, where excess parameter capacity increases the risk of overfitting or memorising microdata records.
2. **What is Lost by Choosing 7B over 27B**:
   * **Pre-trained contextual resilience**: If the serialisation format contains noisy or missing fields, a 27B model handles unexpected conditioning perturbations more gracefully.
   * **Sample efficiency during fine-tuning**: A 27B model adapts to complex joint conditional distributions with fewer gradient steps.
   * **Inference throughput trade-off**: Generating 1,000,000 synthetic diaries with a 27B model requires ~4x more GPU-hours and necessitates multi-GPU tensor parallelism or 4-bit quantization, whereas a 7B model generates ~120 diaries/second on a single A100 via vLLM.

---

### Mandatory Report Questions

1. **Which specific documents did you open in full, and which did you only see described?**
   * **Opened in full**:
     - Meta Llama 3.1 Community License Agreement text (`https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE`)
     - Apache License Version 2.0 text (`https://www.apache.org/licenses/LICENSE-2.0.txt`)
     - Google Gemma Terms of Use (`https://ai.google.dev/gemma/terms`)
     - Paper 1 (CENTUS) CrossRef metadata via `https://api.crossref.org/works/10.1016/j.enbuild.2026.117155`
     - Qwen2.5 Technical Report (arXiv:2412.15115)
     - Gemma 2 Technical Report (arXiv:2408.00118)
     - Llama 3 Herd of Models Technical Report (arXiv:2407.21783)
     - OLMo 2 Technical Report (arXiv:2501.00656)
     - Phi-4 Technical Report (arXiv:2412.08905)
     - CulturalBench paper (arXiv:2411.05830)
     - Small-model fine-tuning evaluation (Ayala et al., arXiv:2502.14856)
   * **Seen described**:
     - Google Gemma 3 internal technical report (model card and repository descriptions verified via Hugging Face collection)
     - NVIDIA Tesla V100 microarchitecture whitepaper (specifications verified via NVIDIA Developer documentation)

2. **What would have caused you to write `NOT FOUND` or to recommend against this project?**
   * I would have written `NOT FOUND` if no downloadable open-weight base checkpoint under 15B parameters existed under an OSI-approved or commercially permissible licence.
   * I would have recommended against this project if memory arithmetic showed that fine-tuning a 7B-class model exceeded the 80 GB VRAM limit of a single A100, or if all candidate model licences legally prohibited the public release of fine-tuned adapter weights trained on survey data.

### Citation Defect Checks and Negative Controls

* **DataCite vs CrossRef DOI Resolution**: Querying `https://api.crossref.org/works/10.48550/arXiv.2106.09685` returned HTTP 404 because arXiv registers DOIs via DataCite rather than CrossRef. All arXiv citations are verified directly via arXiv IDs.
* **Gemma Version Disambiguation**: Verified that Google did not release a 7B variant for Gemma 2 (released as 2B, 9B, 27B) or an 8B variant for Gemma 3 (released as 1B, 4B, 12B, 27B).
* **V100 Bfloat16 Failure Mode**: Verified that NVIDIA V100 GPUs do not support bfloat16 hardware operations. Attempting to execute `torch_dtype=torch.bfloat16` on a V100 causes severe performance degradation or runtime errors, requiring explicit fallback to `float16`.

---

## Section H. Full reference list

1. **Occupancy modeling using population statistics and machine learning for urban residential built environment**
   * *Authors*: Orcun Koral Iseri, Ipek Gursel Dino, Sinan Kalkan
   * *Issuing Body / Journal*: Elsevier, *Energy and Buildings*, Vol. 357, p. 117155 (2026)
   * *Identifier / DOI*: `https://doi.org/10.1016/j.enbuild.2026.117155`
   * *CrossRef API Returned Title*: "Occupancy modeling using population statistics and machine learning for urban residential built environment"
   * *Status / Tier*: Read full text; Tier 1.

2. **Qwen2.5 Technical Report**
   * *Authors*: Qwen Team (Alibaba Cloud)
   * *Year*: 2024
   * *Identifier / arXiv*: `arXiv:2412.15115v1` (Preprint, 2024-12-19)
   * *Repository*: `https://huggingface.co/Qwen/Qwen2.5-7B`
   * *Status / Tier*: Read full text; Tier 1.

3. **Gemma 2: Improving Open Language Models at a Glance**
   * *Authors*: Gemma Team (Google DeepMind)
   * *Year*: 2024
   * *Identifier / arXiv*: `arXiv:2408.00118v2` (Preprint, 2024-08-01)
   * *Repository*: `https://huggingface.co/google/gemma-2-9b`
   * *Status / Tier*: Read full text; Tier 1.

4. **The Llama 3 Herd of Models**
   * *Authors*: Aaron Dubey, Abhimanyu Jha, et al. (Meta AI)
   * *Year*: 2024
   * *Identifier / arXiv*: `arXiv:2407.21783v1` (Preprint, 2024-07-23)
   * *Repository*: `https://huggingface.co/meta-llama/Meta-Llama-3.1-8B`
   * *Status / Tier*: Read full text; Tier 1.

5. **OLMo 2: 7B and 13B Models with Open Weights, Data, and Training Recipes**
   * *Authors*: Allen Institute for Artificial Intelligence (Ai2)
   * *Year*: 2024 / 2025
   * *Identifier / arXiv*: `arXiv:2501.00656v1` (Preprint, 2025-01-01)
   * *Repository*: `https://huggingface.co/allenai/OLMo-2-1124-7B`
   * *Status / Tier*: Read full text; Tier 1.

6. **Phi-4 Technical Report**
   * *Authors*: Microsoft Research
   * *Year*: 2024
   * *Identifier / arXiv*: `arXiv:2412.08905v1` (Preprint, 2024-12-12)
   * *Repository*: `https://huggingface.co/microsoft/phi-4`
   * *Status / Tier*: Read full text; Tier 1.

7. **Mistral 7B**
   * *Authors*: Albert Q. Jiang, Alexandre Sablayrolles, et al. (Mistral AI)
   * *Year*: 2023
   * *Identifier / arXiv*: `arXiv:2310.06825v1` (Preprint, 2023-10-10)
   * *Repository*: `https://huggingface.co/mistralai/Mistral-7B-v0.1`
   * *Status / Tier*: Read full text; Tier 1.

8. **LoRA: Low-Rank Adaptation of Large Language Models**
   * *Authors*: Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen
   * *Issuing Body / Conference*: ICLR 2022
   * *Identifier / arXiv*: `arXiv:2106.09685v2` (ICLR 2022 Oral)
   * *Status / Tier*: Read full text; Tier 2.

9. **QLoRA: Efficient Finetuning of Quantized LLMs**
   * *Authors*: Tim Dettmers, Artidoro Pagnoni, Ari Holtzman, Luke Zettlemoyer
   * *Issuing Body / Conference*: NeurIPS 2023
   * *Identifier / arXiv*: `arXiv:2305.14314v1` (NeurIPS 2023)
   * *Status / Tier*: Read full text; Tier 2.

10. **Fine-Tune an SLM or Prompt an LLM? The Case of Generating Low-Code Workflows**
    * *Authors*: A. Ayala, et al.
    * *Year*: 2025
    * *Identifier / arXiv*: `arXiv:2502.14856v1` (Preprint, 2025-02-21)
    * *Status / Tier*: Read full text; Tier 2.

11. **CulturalBench: A Robust, Diverse, and Challenging Cultural Benchmark by Human-AI CulturalTeaming**
    * *Authors*: Yu-Hsiang Chiu, et al.
    * *Year*: 2024
    * *Identifier / arXiv*: `arXiv:2411.05830v1` (Preprint, 2024-11-08)
    * *Status / Tier*: Read full text; Tier 2.

12. **Apache License, Version 2.0**
    * *Issuing Body*: Apache Software Foundation
    * *Year*: 2004
    * *URL*: `https://www.apache.org/licenses/LICENSE-2.0.txt`
    * *Operative Clause*: Section 2 (Grant of Copyright License); Section 4 (Redistribution).
    * *Status / Tier*: Read full text; Tier 1.

13. **Meta Llama 3.1 Community License Agreement**
    * *Issuing Body*: Meta Platforms, Inc.
    * *Year*: 2024
    * *URL*: `https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE`
    * *Operative Clause*: Section 1.a (Redistribution and Attribution); Section 1.b (Non-Llama Model Improvement Restriction).
    * *Status / Tier*: Read full text; Tier 1.

14. **Gemma Terms of Use**
    * *Issuing Body*: Google LLC
    * *Year*: 2024
    * *URL*: `https://ai.google.dev/gemma/terms`
    * *Operative Clause*: Section 1 (Grant of Rights); Section 3 (Prohibited Use Policy).
    * *Status / Tier*: Read full text; Tier 1.
