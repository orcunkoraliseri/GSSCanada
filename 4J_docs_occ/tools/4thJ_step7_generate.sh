#!/bin/bash
#SBATCH --job-name=4J_s7_gen
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step7_gen_%j.out

# Step 7, work item 7.3 -- generate one fold.
#   usage: sbatch 4thJ_step7_generate.sh <fold> <n> [--no-grammar]
#
# `FINDING 9`: the GRES is NAMED, never a bare `gpu:1`. A bare request lets Slurm
# hand out a slice already shared with three other processes, which is how the
# Step 4 pilot lost its memory footprint (`FINDING 2`).
#
# Leg 4 by default. Under `D-S7-3` (a) that is a REHEARSAL and the script stamps
# every record `LEG-4 PILOT -- NOT REPORTABLE` itself.

set -x
FOLD=${1:?usage: sbatch 4thJ_step7_generate.sh <es|uk|it> <n> [--no-grammar]}
N=${2:-600}
EXTRA=${3:-}
LEG=${LEG:-4}

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
# `flashinfer` is UNINSTALLED from envs/step7 (it dies at module scope on
# Python 3.10: `array.array[int]` is only subscriptable from 3.12). vLLM reaches
# the all-reduce fusion pass through `find_spec` and skips it when absent, but
# `flashinfer_sampler_supported()` does a BARE import with no guard -- it returns
# False before that import only when this variable is 0. Env-only; nothing installed.
export VLLM_USE_FLASHINFER_SAMPLER=0

if [ ! -x "$ENVDIR/bin/python" ]; then
    echo "NO STEP 7 ENV AT $ENVDIR -- run 4thJ_step7_env_build.sh first."
    exit 1
fi
for f in "$IN/generation_config_${FOLD}.json" "$IN/prefixes_${FOLD}.jsonl"; do
    if [ ! -s "$f" ]; then
        echo "MISSING $f -- scp the Step 5 inputs before submitting."
        exit 1
    fi
done

mkdir -p "$WORK/tools" "$WORK/outputs_step7" || exit 1
for f in 4thJ_step7_grammar.py 4thJ_step7_ebnf.py 4thJ_step7_generate.py; do
    cp "$STAGE/$f" "$WORK/tools/$f" || exit 1
done
md5sum "$WORK/tools"/4thJ_step7_{grammar,ebnf,generate}.py

cd "$WORK/tools" || exit 1
"$ENVDIR/bin/python" -m py_compile 4thJ_step7_generate.py || exit 1

nvidia-smi

"$ENVDIR/bin/python" -u 4thJ_step7_generate.py \
    --fold "$FOLD" --leg "$LEG" --n "$N" $EXTRA \
    --step2 "$WORK/Step2_docs/outputs_step2" \
    --config "$IN/generation_config_${FOLD}.json" \
    --prefixes "$IN/prefixes_${FOLD}.jsonl" \
    --out "$WORK/outputs_step7"
echo "generation exit status: $?   (0 = ok, 2 = NOT RUN)"

ls -l "$WORK/outputs_step7"
