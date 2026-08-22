#!/bin/bash
#SBATCH --job-name=4J_s7_tput
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_7g.80gb:1
#SBATCH --mem=128G
#SBATCH --cpus-per-task=8
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step7_tput_%j.out

# Step 7, work item 7.2 -- the throughput comparison, before the campaign is sized.
#   usage: sbatch 4thJ_step7_throughput.sh [n]
#
# `FINDING 9`: the GRES is NAMED. The FULL 7g.80gb instance, not a MIG slice --
# the whole point of the measurement is the KV cache the engine can allocate, and
# a 20 GB slice would report a cap belonging to the slice rather than to the model.

set -x
N=${1:-200}

ENVDIR=/speed-scratch/o_iseri/envs/step7
STAGE=/speed-scratch/o_iseri
WORK=/speed-scratch/o_iseri/4J_step7
IN=/speed-scratch/o_iseri/4J_step5/inputs

export HF_HOME=/speed-scratch/o_iseri/hf_cache
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TMPDIR=/speed-scratch/o_iseri/tmp
export PYTHONIOENCODING=utf-8
export TOKENIZERS_PARALLELISM=false
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export VLLM_USE_FLASHINFER_SAMPLER=0   # FINDING 79

mkdir -p "$WORK/tools" "$WORK/outputs_step7" || exit 1
for f in 4thJ_step7_grammar.py 4thJ_step7_ebnf.py 4thJ_step7_generate.py 4thJ_step7_throughput.py; do
    cp "$STAGE/$f" "$WORK/tools/$f" || exit 1
done
md5sum "$WORK/tools"/4thJ_step7_throughput.py

cd "$WORK/tools" || exit 1
"$ENVDIR/bin/python" -m py_compile 4thJ_step7_throughput.py || exit 1

nvidia-smi

"$ENVDIR/bin/python" -u 4thJ_step7_throughput.py \
    --step2 "$WORK/Step2_docs/outputs_step2" \
    --config "$IN/generation_config_es.json" \
    --prefixes "$IN/prefixes_es.jsonl" \
    --n "$N" \
    --out "$WORK/outputs_step7"
echo "throughput exit status: $?   (0 = ok, 2 = NOT RUN)"

ls -l "$WORK/outputs_step7"
