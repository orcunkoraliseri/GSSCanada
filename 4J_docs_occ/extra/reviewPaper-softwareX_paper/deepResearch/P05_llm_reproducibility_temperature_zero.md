# P05. Reproducibility of LLM-in-the-loop simulation studies: what temperature 0 does and does not buy, and what a study must record

Paste `00_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Section D applies.

## Why we are asking

Simulation studies that put a language model inside the loop routinely claim reproducibility on the
grounds that the sampling temperature was set to 0. We believe that claim is materially weaker than
it is usually stated, and we need to know exactly how weak, in language precise enough to write into
a paper — and precise enough to say to someone else in a review context without being wrong.

We also need the constructive half: **what must a study record, and what must it do, for an
LLM-in-the-loop result to be reproducible in practice?** Our own paper decodes from weights we
fine-tuned ourselves and can pin, which we believe is a genuine methodological advantage over the
hosted-API pattern — but we do not want to claim that advantage until we know its real size.

## What we need

### Item 1. What greedy decoding actually guarantees

1. State precisely what setting `temperature = 0` (or `do_sample=False`) does in the major inference
   stacks. Distinguish: the *sampling* step becoming deterministic given identical logits, versus the
   *logits themselves* being identical across runs.
2. 🔴 Enumerate the documented sources of run-to-run variation that survive greedy decoding, with
   sources:
   * **batch-size dependence of reduction kernels** — we understand this is the dominant cause in
     practice, not floating-point non-associativity per se, and we want that ordering confirmed or
     corrected;
   * floating-point non-associativity and accumulation order;
   * shape-dependent kernel/algorithm selection (cuBLAS/cuDNN autotuning);
   * non-deterministic GPU atomics and reductions;
   * mixture-of-experts routing under batching;
   * speculative decoding, prefix/KV caching, continuous batching;
   * server-side changes: silent model updates, quantisation changes, routing between hardware
     generations.
3. Is there a **measured** figure for how often outputs actually diverge at temperature 0 for a fixed
   hosted model? A divergence rate, a token-level disagreement rate, anything quantitative.
4. What is the current state of **batch-invariant kernels** as a fix — what does it cost in
   throughput, and is it available in the mainstream serving stacks (vLLM, SGLang, TensorRT-LLM,
   llama.cpp, Ollama) or is it research-grade?

### Item 2. The hosted-API problem, separately

1. What do the major providers actually commit to regarding determinism? Do any offer a
   reproducibility control (a seed parameter, a system fingerprint, a pinned snapshot), and what do
   their own docs say it guarantees?
2. What is documented about **model deprecation and silent updates** behind a stable model alias?
   Any case studies of a published result becoming unreproducible because the endpoint changed?
3. How long are dated model snapshots typically retained? This decides whether "record the model
   version" is actually sufficient.

### Item 3. The constructive half — what a study must record

🔴 We want a **checklist we can adopt and cite**, not prose.

1. Is there an existing reproducibility checklist for LLM-in-the-loop research (from a venue, a
   community standard, a reproducibility-initiative document)? Name it and give the items.
2. What is the minimum record: provider, model version string, date of the runs, decoding parameters,
   prompt templates and their version, seed, serving stack and version, quantisation, number of
   repeats?
3. 🔴 What is the recommended practice when determinism cannot be guaranteed — **run N times and
   report the distribution**? Is there guidance on how large N should be, and are there worked
   examples in simulation contexts?
4. Are there venues or journals that now **require** any of this for papers with LLM components?

### Item 4. Local open-weight models — how much better, really?

This is the part that bears on our own claim.

1. If a study pins a **local open-weight model** at a fixed revision, with a fixed serving stack, on
   fixed hardware, and decodes greedily — **is that bit-reproducible?** Under what conditions does it
   still fail?
2. Does the answer change between the common local stacks — HuggingFace `transformers` `generate`,
   vLLM, llama.cpp, Ollama? Which is most reproducible and at what throughput cost?
3. Does **hardware** have to be fixed too? Same GPU model, same driver, same CUDA version — which of
   these actually matter, measurably?
4. What about **adapter-based** setups: base model at a pinned revision plus a LoRA adapter, which is
   our configuration. Any additional reproducibility hazards from adapter merging, dtype, or
   quantisation?
5. 🔴 Assess honestly, in Section G: **how strong a reproducibility claim can a fine-tuned
   open-weight, locally served, greedily decoded generator legitimately make in 2026?** We would
   like to claim "reproducible in a way a hosted-API pipeline is not". Tell us if that is overclaiming
   and what the correctly hedged version is.

### Item 5. Sampling-temperature calibration, adjacent

We separately calibrate a decoding temperature by sweeping it and matching a distributional statistic
of the generated population to the real one.

1. Is there prior art for **choosing a decoding temperature by matching a distributional statistic**
   (entropy, diversity, a downstream fidelity metric) rather than by held-out likelihood?
2. What is known about the **stability** of such a choice — how many replicate runs per grid point
   are needed before the curve is distinguishable from noise? Any guidance on the design.
3. Is there a documented case of a temperature chosen from a single-realisation sweep that did not
   replicate?

## Section D

Answer for a shared single-node SLURM cluster with A100 MIG slices (`nvidia_a100_2g.20gb` and
`_7g.80gb`), no root, and jobs that may land on different physical nodes between runs. Does that last
fact alone break bit-reproducibility, and if so what is the cheapest mitigation?
