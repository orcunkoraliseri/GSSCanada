#!/bin/bash
#SBATCH --job-name=4J_s6_mia
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step6_mia_%j.out

# Step 6.5 -- G6.10 / G6.11 / G6.12 plus the untuned-base and perplexity-gap controls.
#   usage: sbatch 4thJ_step6_privacy_mia.sh <fold> [leg] [n]
#
# `FINDING 9`: the GRES is NAMED. A 2g.20gb slice is enough for the LEG-4 1.48 B
# rehearsal; a Leg-5 run of this needs the 7g.80gb instance and is a separate
# submission, not a flag on this one.
#
# `envs/step4` is used, not `envs/step7`: this needs `transformers` + `peft` to
# score per-token losses through the adapter, which is the environment that
# trained it. Nothing is installed.

set -x
FOLD=${1:?usage: sbatch 4thJ_step6_privacy_mia.sh <es|uk|it> [leg] [n] [control]}
LEG=${2:-4}
N=${3:-2000}
CONTROL=${4:-none}

ENVDIR=/speed-scratch/o_iseri/envs/step4
STAGE=/speed-scratch/o_iseri
WORK=/speed-scratch/o_iseri/4J_step6

export HF_HOME=/speed-scratch/o_iseri/hf_cache
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TMPDIR=/speed-scratch/o_iseri/tmp
export PYTHONIOENCODING=utf-8
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

if [ "$LEG" = "4" ]; then
    ADAPTER=/speed-scratch/o_iseri/4J_step4/runs_ds45/leg4_primary_fold_$FOLD/adapter
else
    ADAPTER=/speed-scratch/o_iseri/4J_step4/runs_leg5/leg${LEG}_primary_fold_$FOLD/adapter
fi
# md5 ca89d2295603c547f2384a40dd1909ba -- checked byte-identical to the local copy,
# and it is the HOUSEHOLD-split corpus (D-S6-1 (b), job 1266814), not the
# respondent-split one sitting beside it under an almost identical name.
CORPUS=/speed-scratch/o_iseri/4J_step3_corpus.jsonl

# ---------------------------------------------------------------------------
# `D-S6-14`, author 2026-08-22 -- the fourth argument, `control`.
# Adds the RANDOM-LABEL-PERMUTATION CEILING to this run: the permuted adapter is
# scored on the permuted corpus it trained on, through the same functions the
# baseline goes through, and the headroom is recorded beside the measured AUCs.
# The pre-registered bars do NOT move.
#
# 🔴 A LEG-5 CONTROL RUN DOES NOT FIT THIS SCRIPT. It loads two 7 B bases
# (the reported one and a fresh one for the control) and the GRES above is a
# 2g.20gb slice. Submit a Leg-5 audit with --gres=gpu:nvidia_a100_7g.80gb:1 and
# --mem=192G on the sbatch line, or it will OOM after loading the first model.
PERM_ARGS=""
if [ "$CONTROL" = "control" ]; then
    PERM_CORPUS=/speed-scratch/o_iseri/4J_step4/shards_permuted_control/corpus_permuted_control.jsonl
    if [ "$LEG" = "4" ]; then
        PERM_ADAPTER=/speed-scratch/o_iseri/4J_step4/runs_permuted_control/leg4_permuted_fold_$FOLD/adapter
    else
        PERM_ADAPTER=/speed-scratch/o_iseri/4J_step4/runs_leg5_permuted_control/leg${LEG}_permuted_fold_$FOLD/adapter
    fi
    if [ ! -d "$PERM_ADAPTER" ]; then
        echo "NO PERMUTED ADAPTER AT $PERM_ADAPTER -- the ceiling has not been"
        echo "trained for fold $FOLD leg $LEG. Refusing to run a control that"
        echo "would silently be absent from the artefact."
        exit 1
    fi
    if [ ! -s "$PERM_CORPUS" ]; then
        echo "NO PERMUTED CORPUS AT $PERM_CORPUS -- build it with"
        echo "4thJ_step4_shards.py --permute-labels."
        exit 1
    fi
    PERM_ARGS="--permuted-adapter $PERM_ADAPTER --permuted-corpus $PERM_CORPUS"
    echo "D-S6-14 CONTROL ARMED: $PERM_ADAPTER"
fi

if [ ! -d "$ADAPTER" ]; then
    echo "NO ADAPTER AT $ADAPTER -- fold $FOLD leg $LEG not audited."
    exit 1
fi
if [ ! -s "$CORPUS" ]; then
    echo "NO CORPUS AT $CORPUS."
    exit 1
fi

mkdir -p "$WORK/tools" "$WORK/outputs_step6" || exit 1
for f in 4thJ_step6_privacy_mia.py decoder.py encoder.py; do
    cp "$STAGE/$f" "$WORK/tools/$f" || exit 1
done
md5sum "$WORK/tools/4thJ_step6_privacy_mia.py"

cd "$WORK/tools" || exit 1
"$ENVDIR/bin/python" -m py_compile 4thJ_step6_privacy_mia.py || exit 1

nvidia-smi

"$ENVDIR/bin/python" -u 4thJ_step6_privacy_mia.py \
    --fold "$FOLD" --leg "$LEG" --adapter "$ADAPTER" \
    --corpus "$CORPUS" --n "$N" $PERM_ARGS \
    --out "$WORK/outputs_step6"
echo "privacy audit exit status: $?   (0 = ok, 2 = NOT RUN)"

ls -l "$WORK/outputs_step6"
