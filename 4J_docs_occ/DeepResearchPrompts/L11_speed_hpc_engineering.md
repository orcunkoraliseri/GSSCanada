# L11. Running an LLM fine-tune on a shared SLURM cluster: containers, offline weights, checkpointing across a walltime limit

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, D and F used. **We have already measured our own hardware; do not re-derive it, use it.**

## Why we are asking

We know how to run our own small PyTorch training jobs on this cluster. We do not know the practices
that are specific to fine-tuning a multi-billion-parameter model on shared, queued, time-limited GPU
resources, and the failure modes there are expensive: a job that dies at hour 160 of a seven-day
walltime with no resumable checkpoint costs a week of a shared queue.

## Our hardware, measured, so your answer can be concrete

Queried on our cluster on **2026-08-13** with `sinfo -N -o '%N|%P|%f|%G|%m|%T'`. This is ground truth,
not an estimate. Treat it as given.

| Nodes | Partitions | GPU | Per-node GPU inventory | Node RAM |
|---|---|---|---|---|
| `speed-37`, `speed-39` to `speed-43` (6 nodes) | `ps`, `pt`, `cl` | NVIDIA **A100**, MIG-partitioned | `nvidia_a100_7g.80gb` x1, `nvidia_a100_2g.20gb` x9, `nvidia_a100_1g.20gb` x3 | 980 GB |
| `xailab` | `ps`, `cl`, `xi` | RTX 6000, 48 GB | x4 | 772 GB |
| `nebulae` | `pt`, `cl`, `pn` | RTX 6000, 48 GB | x2 | 515 GB |
| `antenna3` | `ps`, `cl`, `em` | RTX 6000, 48 GB | x1 | 1030 GB |
| `speed-03`, `speed-25`, `speed-27` | `pg`, `pa`, `pt`, `cl` | V100, 32 GB | x2 | 256 GB |
| `speed-01`, `speed-05`, `speed-17` | `pg`, `pa`, `p6`, `pi`, `cl` | Tesla **P6**, 16 GB | x6 | 256 to 515 GB |
| `cisr-1`, `cisr-2` | `pg`, `cr`, `cl` | A2, 16 GB | x1 | 257 GB |
| `speed-19` | `hip` | AMD S7100X | x1 | 515 GB |

Operational constraints, which are hard:

* **Login node is submission only.** No Python, no builds, no `pip`, no interactive `srun`. Everything
  goes through `sbatch`. This is enforced and has been escalated to us by administrators.
* **Seven-day maximum walltime**, and we request the maximum on every job by standing policy.
* **Shared queue.** We do not own a node and cannot reserve one.
* SLURM. Job scripts run under bash. The interactive login shell is tcsh.

Note the interesting fact in that table: a **full 80 GB A100 is reachable** as the MIG profile
`nvidia_a100_7g.80gb`, one per node, on six nodes. The remaining slices on the same physical card are
20 GB. So we have a small number of large-GPU slots and a larger number of small ones. That shape
should drive the recommendation.

## What we need

### Item 1. Requesting the right resource

1. What is the correct SLURM syntax for requesting a **specific MIG profile** by name as a generic
   resource, and what is known about how MIG slices behave for training: is a `7g.80gb` slice
   equivalent in throughput to a whole unpartitioned A100, or is there a documented penalty?
2. Is it ever better for our workload to take **several 20 GB slices** rather than one 80 GB slice?
   Naively no, for a single large model, but if the answer is that data-parallel training across MIG
   slices on one card is possible and useful, say so. If MIG slices cannot communicate for collective
   operations, state that plainly, since it settles the question.
3. What CPU count, system RAM and local scratch should accompany a GPU request for this workload?
   Dataloading, tokenisation and checkpoint writing are the usual bottlenecks, and asking for too
   little CPU is a documented way to leave a GPU idle.
4. Should we prefer a **queue with more nodes and smaller GPUs** if it means shorter queue waits? Give
   the reasoning in terms of total time to result, not GPU-hours.

### Item 2. Software environment without internet on the compute node

Assume the compute node **cannot reach the internet**. This is common and we should design for it.

1. What is the practical procedure for making model weights available offline: pre-download to shared
   scratch on the login node or a data-transfer node, set the relevant cache environment variables, and
   enable offline mode. Name the exact environment variables and the library versions they apply to.
2. Container versus conda environment on a shared cluster: what does each cost, which is more robust,
   and what are the known pitfalls with GPU drivers, CUDA versions and container runtimes. Our cluster
   documentation mentions container support; treat that as available.
3. What is the reproducible way to pin an environment for a paper: a lockfile, a container image
   digest, or both. What would a reviewer expect us to report.
4. Known version-compatibility traps between the CUDA driver, the PyTorch build, the quantisation
   libraries and flash attention implementations. **This is where a first-timer loses a week**, so be
   specific and name versions.

### Item 3. Surviving the walltime limit

1. How should a fine-tuning run be **checkpointed and resumed** so that a seven-day wall does not lose
   the run? Cover optimiser state, learning-rate scheduler state, dataloader position and RNG state.
   Name the library support that exists for this and what it does not cover.
2. What is the recommended **checkpoint cadence**, given that checkpoints are large and shared storage
   is not free? Give the trade-off calculation, not a number pulled from the air.
3. How should a **job chain** be built: submit a successor job with a dependency, resume from the last
   checkpoint, and stop when a criterion is met. Give the SLURM mechanism.
4. What signal does SLURM send before a walltime kill, and how should the training loop catch it to
   write a final checkpoint? Name the mechanism and the flag that enables it.

### Item 4. Making the experiment plan fit the queue

We will need to run a hyperparameter sweep, several ablations, and a leave-one-country-out experiment
with one run per held-out country. That is potentially dozens of runs on a shared queue.

1. What is the sane structure: SLURM job arrays, one job per configuration, or a single long job that
   sweeps internally? Consider queue fairness and the risk of losing a whole sweep to one failure.
2. Is there evidence-based guidance on **how few runs a hyperparameter search can get away with** for
   LoRA fine-tuning? We would rather run six informed configurations than sixty blind ones.
3. What is the accepted practice for reporting variance across seeds when compute is scarce, and what
   is the minimum a reviewer will accept? Name a venue policy if one exists.

### Item 5. Throughput for the generation phase

Training is not our only cost. Populating an urban model may need **millions of generated diaries**.

1. What inference stack should we use for high-throughput batch generation of many short sequences from
   a fine-tuned model with an adapter: a serving engine, plain `transformers` with batching, or an
   offline batch mode. Name the option and the version.
2. What does adapter merging do to throughput, and is there a reason to keep the adapter unmerged?
3. Give an order-of-magnitude estimate for **diaries per GPU-hour** for a small model at a sequence
   length in the low hundreds of tokens, with the assumptions stated. We need to know whether
   generating a million diaries is an afternoon or a fortnight, because it decides whether the urban
   scale claim in the paper is real.
4. Does constrained decoding (`L12`) cost throughput, and how much?

### Item 6. Cluster-specific documentation

Read our cluster's public documentation at `https://nag-devops.github.io/speed-hpc/` and tell us, with
direct links, what it says about: GPU job submission syntax, container usage, module availability,
scratch storage and quotas, and any policy on long jobs or GPU fair-share. **If the documentation
contradicts anything in this prompt, the documentation wins and we want that flagged.**

## Hard constraints specific to this prompt

* **Nothing multi-node.** Nothing requiring a reservation. Nothing requiring administrator intervention
  beyond ordinary account access.
* **Version-pin every recommendation** and say when you checked.
* Do not propose running anything on the login node, in any form, for any reason.
* Do not recommend cloud fallback. There is no budget.

## Deliverable

**Section C** is a recommended job-submission pattern, written as an actual SLURM script skeleton with
the resource request, the environment activation, the offline cache variables, the checkpoint-resume
logic and the signal handler.

**Section D** is the queue strategy: which partition and GPU profile for which stage of the work.

**Section F** is the documentation links, including the cluster's own pages.

**Section G** carries the version-compatibility traps and your negative controls.
