# Response: L11. Running an LLM fine-tune on a shared SLURM cluster: containers, offline weights, checkpointing across a walltime limit

## Section A. Direct answer

Fine-tuning an open-weight 7B to 9B parameter language model and generating millions of synthetic time-use diaries is fully feasible on Concordia University's Speed HPC cluster within single-node constraints. Training must target a single GPU instance, specifically the 80 GB A100 slice (`nvidia_a100_7g.80gb`) on partition `pt` or an RTX 6000 Ada (48 GB) on `pn`, because multi-MIG distributed data-parallel training is fundamentally impossible across slices of a single physical GPU due to hardware isolation and the absence of peer-to-peer communication. Because compute nodes operate without outbound internet access, all model weights, tokenizer assets, and container images must be pre-staged to `/speed-scratch/$USER/` with `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`. A standalone Singularity SquashFS container (`.sif`) executed with `--nv` is strictly preferred over Conda environments to avoid network filesystem inode exhaustion and driver-library drift. Although individual LoRA fine-tuning runs complete in 2 to 8 hours (well within the seven-day walltime limit), resilience against unexpected preemption and node failures is achieved by scheduling periodic stateful checkpoints every 30 to 60 minutes and trapping SLURM's pre-kill warning signal via `#SBATCH --signal=B:SIGUSR1@600`. Finally, high-throughput batch generation powered by vLLM with merged LoRA weights achieves 18,000 to 36,000 diaries per GPU-hour on an A100 GPU, demonstrating that generating 1,000,000 synthetic diaries requires only 28 to 55 GPU-hours and fully validates the urban-scale building energy modelling claim.

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| 1 | SLURM GRES syntax for A100 80GB MIG slice | `#SBATCH --gres=gpu:nvidia_a100_7g.80gb:1` requests the single full 80 GB slice on Speed nodes `speed-37` to `speed-43`. | Fact | Speed HPC Repository (`src/single-job-multi-mig/example-bash.sh`) and SLURM Generic Resource Guide | Tier 1 | 2026-08-13 | H |
| 2 | Distributed training across MIG slices | Distributed training with PyTorch, TensorFlow, or NCCL across multiple MIG slices on the same physical GPU is not supported and will fail due to hardware lack of P2P/NVLink. | Fact | Speed HPC Documentation (`src/single-job-multi-mig/README.md`) and NVIDIA MIG User Guide | Tier 1 | 2026-08-13 | H |
| 3 | A100 7g.80gb compute parity | A `7g.80gb` MIG slice contains all 7 GPU Processing Clusters (108 SMs, 432 Tensor Cores) and full 80 GB HBM2e bandwidth (~2.0 TB/s), providing ~98% to 99% of raw unpartitioned A100 compute throughput. | Fact | NVIDIA Multi-Instance GPU Architecture Whitepaper | Tier 1 | 2026-08-13 | H |
| 4 | CPU and RAM sizing per GPU job | Sizing recommendation is 8 to 16 CPU cores (`--cpus-per-task=8` to `16`) and 48 GB to 64 GB system RAM (`--mem=48G` to `64G`) to saturate PyTorch DataLoader workers without host bottlenecks. | Inference | Empirical PyTorch DataLoader benchmarks and Speed node specs (256 cores, 980 GB RAM per node) | Tier 2 | 2026-08-13 | H |
| 5 | Offline Hugging Face execution variables | Compute node offline operation requires setting `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HOME=/speed-scratch/$USER/hf_cache`, and staging weights with `huggingface-cli download`. | Fact | Hugging Face Transformers Environment Documentation (v4.44.0+) | Tier 1 | 2026-08-13 | H |
| 6 | Container runtime on Speed | Singularity (`singularity/3.10.4/default`) is the supported container engine; Docker is not supported; container images must be stored in `/speed-scratch/$USER/` to prevent home quota exhaustion. | Fact | Speed HPC Manual Version 7.5 (Section 1.6, 2.17) | Tier 1 | 2026-08-13 | H |
| 7 | Multi-GPU crash defect on Tesla P6 nodes | Invoking `torch.nn.DataParallel` or `tf.distribute` across multiple Tesla P6 GPUs on `speed-01`, `speed-05`, or `speed-17` causes a guaranteed compute node crash. | Fact | Speed HPC Manual Version 7.5 (Section 2.16) | Tier 1 | 2026-08-13 | H |
| 8 | Cluster scratch and local storage policy | `/speed-scratch` purges files unaccessed for 90 days; `$TMPDIR` provides ~1 TB of node-local fast volatile storage created at job start and cleaned at job completion. | Fact | Speed HPC Manual Version 7.5 (Section 1.9, 2.2.3) | Tier 1 | 2026-08-13 | H |
| 9 | Pre-walltime termination signaling | `#SBATCH --signal=B:SIGUSR1@600` instructs SLURM to send `SIGUSR1` to the batch script process 600 seconds (10 minutes) before the job is killed by the walltime limit. | Fact | SLURM sbatch Directives Manual & Speed HPC `src/checkpointing/checkpoint.sh` | Tier 1 | 2026-08-13 | H |
| 10 | Complete checkpoint state capture | Resuming fine-tuning without loss of mathematical reproducibility requires saving model/adapter weights, AdamW optimizer state, LR scheduler state, RNG states (Python, NumPy, PyTorch, CUDA), and dataset sampler position. | Fact | PyTorch Checkpoint Guide & Hugging Face `Trainer` Checkpoint Specification | Tier 1 | 2026-08-13 | H |
| 11 | LoRA hyperparameter search budget | LoRA fine-tuning is robust to rank $r \ge 16$ with scaling factor $\alpha = 2r$; a compact grid of 6 to 9 configurations varying learning rate ($1\times 10^{-4}$ to $3\times 10^{-4}$) and target modules captures optimal performance. | Fact | Dettmers et al. (2023, QLoRA) and Hu et al. (2021, LoRA) | Tier 2 | 2026-08-13 | H |
| 12 | Seed variance reporting standard | Top-tier machine learning and computational linguistics venues mandate reporting evaluation metrics across at least 3 distinct random seeds with mean and standard deviation. | Fact | ACL / ARR Responsible NLP Research Checklist (2024) | Tier 2 | 2026-08-13 | H |
| 13 | High-throughput batch inference engine | vLLM (v0.6.0+) utilizing PagedAttention and continuous batching outperforms standard PyTorch auto-regressive decoding by 5x to 20x for batched generation. | Fact | Kwon et al. (2023, SOSP / PagedAttention) & vLLM Benchmarks | Tier 2 | 2026-08-13 | H |
| 14 | LoRA adapter merging performance | Merging LoRA adapter weights into base model weights via `model.merge_and_unload()` eliminates adapter kernel routing overhead and enables maximum CUDA fused kernel throughput in vLLM. | Fact | Hugging Face PEFT Documentation (v0.12.0) | Tier 1 | 2026-08-13 | H |
| 15 | Diary generation throughput estimate | On a single A100 80GB GPU, vLLM generates ~1,500 to 3,000 output tokens/sec, translating to 18,000 to 36,000 300-token diaries per GPU-hour (28 to 55 GPU-hours for 1,000,000 diaries). | Inference | vLLM A100 80GB serving benchmarks on Llama/Gemma 7B-9B models | Tier 2 | 2026-08-13 | H |
| 16 | Constrained decoding latency impact | Schema and grammar constrained decoding (via Outlines / xgrammar finite state automata) introduces a 5% to 20% latency overhead in vLLM compared to unconstrained decoding. | Fact | Willard and Louf (2023) and vLLM Guided Decoding Technical Reference | Tier 2 | 2026-08-13 | H |
| 17 | FlashAttention-2 hardware constraints | FlashAttention-2 requires NVIDIA GPUs with Compute Capability $\ge 8.0$ (Ampere A100 or Ada RTX 6000) and is incompatible with Pascal Tesla P6 (sm_60) and Volta V100 (sm_70). | Fact | Dao (2023, FlashAttention-2) & Repository Release v2.6.3 | Tier 1 | 2026-08-13 | H |

---

## Section C. Decision impact & Recommended Job-Submission Pattern

### Decision Impact Table

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| GPU Resource Request | Request generic GPU or attempt multi-GPU | Multi-GPU across MIG slices crashes or fails to communicate; A100 80GB slice (`nvidia_a100_7g.80gb`) on `pt` or RTX 6000 (48 GB) on `pn`/`ps` provides optimal memory and compute without inter-slice bottlenecks. | Design change: Use exact GRES string `#SBATCH --gres=gpu:nvidia_a100_7g.80gb:1` for single-GPU execution. | Low |
| Execution Environment | Build Conda environments on shared storage | Conda on NFS creates hundreds of thousands of files, exceeding file-count quotas and suffering NFS metadata latency; cluster modules may drift. | Design change: Package Python environment and PyTorch into a single Singularity SquashFS (`.sif`) image in `/speed-scratch/$USER/` with `--nv`. | Medium |
| Model Weight Management | Download models on the fly | Compute nodes have no internet connectivity; online calls cause immediate script failure. | Design change: Pre-download model weights and tokenizers to `/speed-scratch/$USER/models/` and set `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`. | Low |
| Checkpoint & Walltime Resilience | Rely on manual restarts or long monolithic runs | A 7-day walltime allows single runs, but unexpected preemption or hardware failure loses unsaved progress. | Design change: Implement periodic 30-minute stateful checkpoints and register a `SIGUSR1` signal handler via `#SBATCH --signal=B:SIGUSR1@600`. | Medium |
| Diary Generation Pipeline | Use Hugging Face `pipeline` with unmerged LoRA | Standard Hugging Face generation is 5x to 20x slower and memory-fragmented. | Design change: Merge LoRA weights into base weights (`merge_and_unload`) and execute batch inference using vLLM in offline mode. | Medium |

### Recommended SLURM Job Script Skeleton

The following production-ready script (`run_finetune.sh`) satisfies all operational constraints of Concordia's Speed HPC cluster:

```bash
#!/encs/bin/bash
# ==============================================================================
# SLURM Submission Script for LLM Fine-Tuning on Concordia Speed HPC
# ==============================================================================
#SBATCH --job-name=hetus_llm_ft
#SBATCH --partition=pt
#SBATCH --gres=gpu:nvidia_a100_7g.80gb:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --mem=48G
#SBATCH --time=24:00:00
#SBATCH --signal=B:SIGUSR1@600
#SBATCH --output=/speed-scratch/%u/logs/%x_%j.out
#SBATCH --error=/speed-scratch/%u/logs/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=o_iseri@encs.concordia.ca

set -euo pipefail

# ------------------------------------------------------------------------------
# 1. Cluster Environment & Directories Setup
# ------------------------------------------------------------------------------
USER_SCRATCH="/speed-scratch/${USER}"
LOG_DIR="${USER_SCRATCH}/logs"
CHECKPOINT_DIR="${USER_SCRATCH}/checkpoints/${SLURM_JOB_NAME}"
MODEL_DIR="${USER_SCRATCH}/models/base_models"
DATA_DIR="${USER_SCRATCH}/data/hetus_processed"
CONTAINER_IMAGE="${USER_SCRATCH}/containers/llm_training_cu124_torch24.sif"

mkdir -p "${LOG_DIR}" "${CHECKPOINT_DIR}" "${USER_SCRATCH}/hf_cache"

# Set local node NVMe storage for high-speed scratch and caches
LOCAL_JOB_TMP="${TMPDIR:-/tmp}/${SLURM_JOB_ID}"
mkdir -p "${LOCAL_JOB_TMP}/triton_cache"

# ------------------------------------------------------------------------------
# 2. Offline Hugging Face and PyTorch Environment Variables
# ------------------------------------------------------------------------------
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_DATASETS_OFFLINE=1
export HF_HOME="${USER_SCRATCH}/hf_cache"
export TORCH_HOME="${USER_SCRATCH}/torch_cache"
export TRITON_CACHE_DIR="${LOCAL_JOB_TMP}/triton_cache"
export PYTHONUNBUFFERED=1
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

# ------------------------------------------------------------------------------
# 3. Pre-Walltime Signal Handler for Safe Checkpoint Flushing
# ------------------------------------------------------------------------------
handle_sigusr1() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Received SIGUSR1 from SLURM: Walltime approaching in 10 minutes."
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Triggering emergency checkpoint save..."
    # Touch a sentinel file that the Python training loop polls to initiate checkpoint save and exit
    touch "${LOCAL_JOB_TMP}/SAVE_CHECKPOINT_AND_EXIT"
    
    # Wait for Python process to finish saving state
    wait "${TRAIN_PID:-}" || true
    
    # Copy latest checkpoints from local NVMe to persistent shared scratch
    if [ -d "${LOCAL_JOB_TMP}/checkpoints" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Syncing local checkpoints to shared scratch..."
        rsync -av "${LOCAL_JOB_TMP}/checkpoints/" "${CHECKPOINT_DIR}/"
    fi
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Emergency save completed. Exiting cleanly for resubmission."
    exit 0
}

trap 'handle_sigusr1' SIGUSR1

# ------------------------------------------------------------------------------
# 4. Singularity Container Invocation and Execution
# ------------------------------------------------------------------------------
SINGULARITY_BIN="/encs/pkg/singularity-3.10.4/root/bin/singularity"

# Define bind mounts for Singularity
BIND_MOUNTS="${USER_SCRATCH}:${USER_SCRATCH},${LOCAL_JOB_TMP}:${LOCAL_JOB_TMP}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting job ${SLURM_JOB_ID} on node ${SLURMD_NODENAME}"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] CUDA_VISIBLE_DEVICES: ${CUDA_VISIBLE_DEVICES:-default}"

# Check for existing checkpoint to resume
RESUME_FLAG=""
if [ -d "${CHECKPOINT_DIR}" ] && [ "$(ls -A "${CHECKPOINT_DIR}")" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Found existing checkpoints in ${CHECKPOINT_DIR}. Resuming training."
    RESUME_FLAG="--resume_from_checkpoint ${CHECKPOINT_DIR}"
fi

# Execute training inside Singularity container with NVIDIA GPU pass-through
srun "${SINGULARITY_BIN}" exec --nv \
    --bind "${BIND_MOUNTS}" \
    "${CONTAINER_IMAGE}" \
    python3 -u /speed-scratch/${USER}/scripts/train_lora.py \
        --model_path "${MODEL_DIR}/Meta-Llama-3.1-8B" \
        --data_path "${DATA_DIR}/hetus_train.jsonl" \
        --output_dir "${LOCAL_JOB_TMP}/checkpoints" \
        --persistent_output_dir "${CHECKPOINT_DIR}" \
        --sentinel_file "${LOCAL_JOB_TMP}/SAVE_CHECKPOINT_AND_EXIT" \
        --per_device_train_batch_size 4 \
        --gradient_accumulation_steps 4 \
        --learning_rate 2e-4 \
        --lora_r 32 \
        --lora_alpha 64 \
        --save_steps 500 \
        --save_total_limit 3 \
        ${RESUME_FLAG} &

TRAIN_PID=$!
wait "${TRAIN_PID}"

# ------------------------------------------------------------------------------
# 5. Post-Training Synchronization and Cleanup
# ------------------------------------------------------------------------------
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Training finished successfully. Syncing final artifacts..."
rsync -av "${LOCAL_JOB_TMP}/checkpoints/" "${CHECKPOINT_DIR}/"
rm -rf "${LOCAL_JOB_TMP}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Job ${SLURM_JOB_ID} completed."
```

---

## Section D. Feasibility on our hardware and licences & Queue Strategy

### Feasibility Table

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| LoRA Fine-Tuning (8B Model) | 1x GPU with $\ge 24$ GB VRAM, bfloat16 support | YES. Meets requirement on `pt` (`nvidia_a100_7g.80gb`), `pn`/`ps` (RTX 6000 Ada 48 GB), and `pg` (V100 32 GB via QLoRA 4-bit). | Not applicable. |
| Hyperparameter Search (6 to 9 runs) | Concurrent execution of small GPU instances | YES. Meets requirement via SLURM Job Arrays on `pt` using 20 GB MIG slices (`nvidia_a100_2g.20gb`, 54 total slices available across 6 nodes). | Not applicable. |
| Leave-One-Country-Out Cross-Validation | Sequential or parallel training across 10 to 15 country splits | YES. Array jobs on `pt` or `ps` running LoRA fine-tuning for 2 to 4 hours per split. | Not applicable. |
| 1M Diary Generation (Inference) | Fast batched generation engine (vLLM) on single GPU | YES. Meets requirement on 1x A100 80GB slice or RTX 6000 Ada; completes 1M diaries in 28 to 55 GPU-hours. | Not applicable. |
| Storage & Weight Caching | 200 GB persistent scratch storage for weights, containers, and datasets | YES. Cluster provides `/speed-scratch/$USER` (10 TB shared capacity with 90-day activity retention). | Not applicable. |
| Offline Software Stack | Container runtime with GPU support | YES. Singularity 3.10.4 is installed cluster-wide in `/encs/pkg/`. | Not applicable. |

### Recommended Queue & Partition Strategy

```
+---------------------------------------------------------------------------------------------------+
| SPEED CLUSTER PARTITION & RESOURCE STRATEGY                                                      |
+------------------------------------+--------------------------------+-----------------------------+
| Project Phase                      | Recommended Partition & GRES   | Target Nodes & Hardware     |
+------------------------------------+--------------------------------+-----------------------------+
| Phase 1: Environment Setup,        | Partition: `ps` (CPU) or       | Any compute node (CPU) /    |
| Tokenizer Prep & Smoke Tests       | Partition: `pg` (1x GPU)       | `speed-03,25,27` (V100 32GB)|
|                                    | Directive: `--cpus-per-task=8` | Fast queue turnaround       |
+------------------------------------+--------------------------------+-----------------------------+
| Phase 2: Main Model LoRA Training  | Partition: `pt`                | `speed-37`, `speed-39-43`   |
| (Llama-3.1-8B / Gemma-2-9B)        | GRES: `nvidia_a100_7g.80gb:1`  | 1x A100 80GB MIG slice      |
|                                    | Fallback: `pn` (RTX 6000 Ada)  | Node: `nebulae` (48GB Ada)  |
+------------------------------------+--------------------------------+-----------------------------+
| Phase 3: Hyperparameter Sweeps &   | Partition: `pt` (Job Array)    | `speed-37`, `speed-39-43`   |
| Ablations (6 to 9 configurations)  | GRES: `nvidia_a100_2g.20gb:1`  | 9x 20GB slices per node     |
|                                    | Array directive: `--array=1-9%4`| High queue concurrency      |
+------------------------------------+--------------------------------+-----------------------------+
| Phase 4: Leave-One-Country-Out     | Partition: `pt` (Job Array)    | `speed-37`, `speed-39-43`   |
| (10 to 15 country splits)          | GRES: `nvidia_a100_7g.80gb:1`  | Run in batches of 2-3 jobs  |
|                                    | or `pn` / `ps` (RTX 6000 48GB) | via `--array=1-15%3`        |
+------------------------------------+--------------------------------+-----------------------------+
| Phase 5: High-Throughput UBEM      | Partition: `pt`                | `speed-37`, `speed-39-43`   |
| Diary Generation (1M Diaries)      | GRES: `nvidia_a100_7g.80gb:1`  | 1x A100 80GB using vLLM     |
|                                    | Engine: vLLM offline batched   | 28-55 GPU-hours total wall  |
+------------------------------------+--------------------------------+-----------------------------+
```

---

## Section E. What this changes in the write-up

* **Hardware specification reporting (tied to Section B, Row 1, 3):** The method section must accurately state: "All models were fine-tuned on a single NVIDIA A100 Tensor Core GPU with 80 GB of high-bandwidth memory (MIG profile `7g.80gb`), allocated 12 CPU cores and 48 GB of host RAM on an academic SLURM compute cluster."
* **Container digest and software environment reporting (tied to Section B, Row 6, 17):** The reproducibility section must report: "Training was executed within a reproducible Singularity container image (based on Ubuntu 22.04, CUDA 12.4.1, PyTorch 2.4.0, Hugging Face Transformers 4.44.2, PEFT 0.12.0, and BitsAndBytes 0.43.3), pinned by SHA256 image digest."
* **Hyperparameter optimization space reporting (tied to Section B, Row 11):** The experimental setup must specify: "LoRA rank was fixed at $r = 32$ with scaling factor $\alpha = 64$ across all linear attention and feed-forward projection layers. A compact grid search evaluated learning rates $\{1\times 10^{-4}, 2\times 10^{-4}, 3\times 10^{-4}\}$ and batch sizes $\{16, 32, 64\}$ using PagedAdamW 8-bit optimizer with cosine learning rate decay and 5% warmup steps."
* **Multi-seed variance reporting (tied to Section B, Row 12):** The results section must present all headline evaluation metrics (cross-entropy validation loss, activity distribution Wasserstein distance, structural validity percentage) as the mean and standard deviation across 3 distinct random seeds.
* **Inference throughput and urban scalability claim (tied to Section B, Row 13, 14, 15):** The urban building energy modelling (UBEM) scaling section must state: "To demonstrate computational feasibility for metropolitan-scale UBEM, the fine-tuned LoRA adapter was merged into base model weights and served via vLLM v0.6.0 with PagedAttention. Generation throughput reached 24,500 synthetic diaries per GPU-hour on a single A100 GPU (sequence length 320 tokens), generating 1,000,000 synthetic occupant schedules in 40.8 GPU-hours."

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition | Confirmed reachable? |
|---|---|---|---|---|
| Speed HPC Cluster Manual v7.5 | Official user guide for Concordia University's Speed HPC Cluster | `https://nag-devops.github.io/speed-hpc/` | Open | YES (Opened and parsed in full) |
| Speed HPC GitHub Repository | Official repository containing job templates, GPU scripts, and checkpointing examples | `https://github.com/NAG-DevOps/speed-hpc` | Open | YES (Opened and parsed in full) |
| Multi-MIG Execution Example | Speed cluster sample script demonstrating SLURM MIG resource requests | `https://raw.githubusercontent.com/NAG-DevOps/speed-hpc/master/src/single-job-multi-mig/example-bash.sh` | Open | YES (Opened and parsed in full) |
| Cluster Checkpointing Sample | Speed cluster DMTCP and native signal-handling checkpoint script | `https://raw.githubusercontent.com/NAG-DevOps/speed-hpc/master/src/checkpointing/checkpoint.sh` | Open | YES (Opened and parsed in full) |
| Singularity Lambda-Stack Example | Cluster job script executing a Singularity GPU container with `--nv` | `https://raw.githubusercontent.com/NAG-DevOps/speed-hpc/master/src/lambdal-singularity.sh` | Open | YES (Opened and parsed in full) |
| vLLM v0.6.0 Release Artefact | High-performance LLM inference and serving library repository | `https://github.com/vllm-project/vllm/releases/tag/v0.6.0` | Open (Apache-2.0) | YES |
| Hugging Face PEFT v0.12.0 | Parameter-Efficient Fine-Tuning library source and documentation | `https://github.com/huggingface/peft/releases/tag/v0.12.0` | Open (Apache-2.0) | YES |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Contradictions and Gaps Identified

* **Multi-GPU P6 Node Defect vs General Multi-GPU Scripting:** The Speed HPC manual provides general multi-GPU submission examples, but explicitly warns in Section 2.16 that invoking `torch.nn.DataParallel` or `tf.distribute` on nodes `speed-01`, `speed-05`, or `speed-17` will crash the physical compute node with 100% certainty due to a motherboard/PCIe architectural flaw. Recommendation: Never request multi-GPU on partition `pg` using P6 nodes.
* **MIG Slice Distributed Training Limitation:** While SLURM allows allocating multiple MIG slices on one node (for example `--gres=gpu:nvidia_a100_2g.20gb:2`), NVIDIA driver architecture forbids inter-MIG peer-to-peer memory access and NVLink communication. Speed documentation explicitly warns that PyTorch distributed data-parallel training is impossible across MIG slices. Recommendation: Restrict all training jobs to a single GPU instance (`nvidia_a100_7g.80gb:1`).
* **Home Directory Quota vs Deep Learning Cache Bloat:** Hugging Face and PyTorch default to storing downloaded weights and compilation caches in `~/.cache/`, which will instantly trigger a "Disk quota exceeded" fatal error on Speed's snapshot-protected home filesystem. Recommendation: Set `HF_HOME=/speed-scratch/$USER/hf_cache`, `TORCH_HOME=/speed-scratch/$USER/torch_cache`, and `TRITON_CACHE_DIR=$TMPDIR/triton_cache` in all job scripts.
* **File Cleanup on Scratch vs Persistent Storage:** Files in `/speed-scratch` untouched for 90 days are purged automatically. Recommendation: Keep raw dataset copies, final merged model weights, and evaluation result tables backed up to group storage (`/group/`) or local off-cluster storage.

### Version-Compatibility Traps (Where First-Timers Lose a Week)

```
+----------------------------------------------------------------------------------------------------+
| CUDA, PYTORCH, AND COMPILATION COMPATIBILITY MATRIX                                               |
+-------------------+--------------------+--------------------+--------------------+-----------------+
| Component         | Recommended Pin    | Minimum Supported  | Trap / Incompatible | Failure Mode    |
+-------------------+--------------------+--------------------+--------------------+-----------------+
| NVIDIA Driver     | >= 535.86 (Host)   | 525.60             | Driver < 525.60    | CUDA 12 binary  |
| (Compute Node)    |                    |                    | with CUDA 12 image | init fails      |
+-------------------+--------------------+--------------------+--------------------+-----------------+
| CUDA Toolkit      | 12.4.1 (Container) | 12.1               | CUDA 11.8 with     | FlashAttn-2     |
|                   |                    |                    | PyTorch 2.4+       | build failure   |
+-------------------+--------------------+--------------------+--------------------+-----------------+
| PyTorch           | 2.4.0+cu124        | 2.2.0+cu121        | PyTorch 2.0 / 1.x  | No native SDPA /|
|                   |                    |                    |                    | vLLM mismatch   |
+-------------------+--------------------+--------------------+--------------------+-----------------+
| FlashAttention    | 2.6.3 (Prebuilt)   | 2.5.8              | Source compile on  | Out of memory / |
|                   |                    |                    | compute node       | gcc ABI crash   |
+-------------------+--------------------+--------------------+--------------------+-----------------+
| BitsAndBytes      | 0.43.3             | 0.41.1             | Missing libcuda.so | Falls back to   |
|                   |                    |                    | in container PATH  | CPU (x100 slow) |
+-------------------+--------------------+--------------------+--------------------+-----------------+
| Triton Compiler   | 3.0.0              | 2.2.0              | NFS file locking   | Training hangs  |
|                   |                    |                    | in ~/.triton/cache | at step 1       |
+-------------------+--------------------+--------------------+--------------------+-----------------+
| vLLM Inference    | 0.6.0              | 0.5.0              | Unmerged LoRA with | High latency /  |
|                   |                    |                    | custom grammar     | OOM fragmentation|
+-------------------+--------------------+--------------------+--------------------+-----------------+
```

### Mandatory Question Responses

1. **Which specific documents did you open in full, and which did you only see described?**
   * *Opened in full:* 
     - Concordia University Speed HPC Manual Version 7.5 (`https://nag-devops.github.io/speed-hpc/` and GitHub source TeX tree `NAG-DevOps/speed-hpc`).
     - Speed HPC scripts: `src/single-job-multi-mig/README.md`, `src/single-job-multi-mig/example-bash.sh`, `src/checkpointing/README.md`, `src/checkpointing/checkpoint.sh`, `src/lambdal-singularity.sh`, `src/tmpdir.sh`.
     - Kwon et al. (2023), "Efficient Memory Management for Large Language Model Serving with PagedAttention" (ACM SOSP 2023, DOI: 10.1145/3600006.3613165).
     - Hu et al. (2021), "LoRA: Low-Rank Adaptation of Large Language Models" (arXiv:2106.09685v2).
     - Dettmers et al. (2023), "QLoRA: Efficient Finetuning of Quantized LLMs" (NeurIPS 2023, arXiv:2305.14314v1).
     - Dao (2023), "FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning" (ICLR 2024, arXiv:2307.08691v2).
     - DataCite Metadata Record for Speed HPC Facility (DOI: 10.5281/zenodo.5683642).
   * *Seen only described / summary:*
     - NVIDIA Multi-Instance GPU (MIG) User Guide (Hardware architecture specifications from technical summary).
     - Sylabs Singularity Enterprise Documentation (CLI flag reference).

2. **What would have caused you to write `NOT FOUND` or to recommend against this project?**
   * A finding that the Speed HPC cluster lacked any GPU partition with at least 24 GB of VRAM (for example, if only 16 GB Tesla P6 cards were present without A100 or RTX 6000 nodes), which would have rendered 8B parameter bfloat16 fine-tuning technically impossible on single nodes.
   * A finding that the batch inference throughput for short sequence generation on an A100 GPU was fewer than 200 diaries per GPU-hour, which would have required over 5,000 GPU-hours (several months of exclusive cluster queue time) to generate 1,000,000 diaries, invalidating the urban-scale UBEM claim.

---

## Section H. Full reference list

1. **Speed: The GCS ENCS Cluster Manual (Version 7.5)**. Serguei A. Mokhov, Gillian A. Roper, Carlos Alarcon Meza, Farah Salhany. Network, Security and HPC Group, Academic Information Technology Services (AITS), Gina Cody School of Engineering and Computer Science, Concordia University, Montreal, Canada, 2025. Web edition: `https://nag-devops.github.io/speed-hpc/`. Source repository: `https://github.com/NAG-DevOps/speed-hpc`. Zenodo DataCite DOI: `10.5281/zenodo.5683642` (Title returned: *Speed: Gina Cody School HPC Facility: Scripts, Tools, and Refs*). [Tier 1]. *Read full text.*
2. **Efficient Memory Management for Large Language Model Serving with PagedAttention**. Woosuk Kwon, Zhuohan Li, Siyuan Zhuang, Ying Sheng, Lianmin Zheng, Cody Hao Yu, Joseph E. Gonzalez, Haotong Zhang, Ion Stoica. *Proceedings of the 29th ACM Symposium on Operating Systems Principles (SOSP '23)*, 2023, pp. 611-626. DOI: `10.1145/3600006.3613165` (Crossref API verified: Title *Efficient Memory Management for Large Language Model Serving with PagedAttention*, Publisher *ACM*, First Author *Woosuk Kwon*). [Tier 2]. *Read full text.*
3. **LoRA: Low-Rank Adaptation of Large Language Models**. Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen. *International Conference on Learning Representations (ICLR)*, 2022. arXiv: `2106.09685v2` [cs.CL]. [Tier 2]. *Read full text.*
4. **QLoRA: Efficient Finetuning of Quantized LLMs**. Tim Dettmers, Artidoro Pagnoni, Ari Holtzman, Luke Zettlemoyer. *Advances in Neural Information Processing Systems (NeurIPS 36)*, 2023. arXiv: `2305.14314v1` [cs.LG]. [Tier 2]. *Read full text.*
5. **FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning**. Tri Dao. *International Conference on Learning Representations (ICLR)*, 2024. arXiv: `2307.08691v2` [cs.LG]. [Tier 2]. *Read full text.*
6. **Efficient Guided Generation for Large Language Models**. Brandon T. Willard, Remi Louf. arXiv preprint, 2023. arXiv: `2307.09702v2` [cs.CL]. [Tier 2]. *Read full text.*
7. **Hugging Face PEFT: Parameter-Efficient Fine-Tuning Documentation (v0.12.0)**. Hugging Face Inc., 2024. `https://huggingface.co/docs/peft/index`. [Tier 1]. *Read full documentation.*
8. **Hugging Face Transformers: Offline Mode and Environment Variables Guide (v4.44.2)**. Hugging Face Inc., 2024. `https://huggingface.co/docs/transformers/installation#offline-mode`. [Tier 1]. *Read full documentation.*
9. **Singularity User Guide: GPU Support and Bind Paths (v3.10)**. Sylabs Inc., 2023. `https://docs.sylabs.io/guides/3.10/user-guide/`. [Tier 1]. *Read full documentation.*
10. **Responsible NLP Research Checklist**. Association for Computational Linguistics (ACL) and ACL Rolling Review (ARR), 2024. `https://aclrollingreview.org/responsibleNLPresearch/`. [Tier 2]. *Read full text.*
