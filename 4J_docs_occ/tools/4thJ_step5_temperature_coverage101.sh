#!/bin/bash
#SBATCH --job-name=4J_s5_cov
#SBATCH --partition=ps
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step5_cov_%j.out

# Step 5, item 5.4 -- D-S5-15, RULED (a) BY THE AUTHOR 2026-08-21.
#   usage: sbatch 4thJ_step5_temperature_coverage101.sh <fold>    # es | uk | it
#
# WHY THIS RUN EXISTS
# ===================
# `D-S5-14`(a) added a per-slot denominator (`at_home_mae_pp_covered`) and a
# coverage curve. The PRIMARY nine-point sweep predates that decision: all 27 of
# its rows carry `at_home_mae_pp_covered = null` and no `coverage_curve`, and its
# text was discarded, so the diagnostic CANNOT be re-derived from it without a
# GPU. The `D-S5-13`(a) replicate jobs do produce it -- but only on the THREE
# window points around `T_chosen`, and on two folds of three the FIDELITY optimum
# (`T_fidelity`) lies OUTSIDE that window:
#
#   es  T_chosen 1.30, T_fidelity 0.70  -> 4 grid steps outside   🔴
#   uk  T_chosen 1.10, T_fidelity 1.00  -> on the window edge     ok
#   it  T_chosen 1.20, T_fidelity 0.80  -> 3 grid steps outside   🔴
#
# So the coverage diagnostic would have been blind exactly where the confound it
# was invented for is LARGEST: on `es` the fidelity optimum sits at T = 0.70,
# where 14.8 % of diaries never terminate.
#
# WHAT THIS RUN DOES, AND WHAT IT MAY NOT DO
# ==========================================
# It runs ONLY the six grid points the replicate window does not already cover,
# at seed `101` ONLY. Spliced with the seed-`101` rows of the replicate artefact
# this yields a complete NINE-POINT, SINGLE-SEED, internally consistent coverage
# curve per fold. Every row records its own `gen_seed`, which is what makes the
# splice legal rather than a mixture.
#
# 🔴 IT DOES NOT CHOOSE A TEMPERATURE. `--gen-seeds` puts the script in replicate
# mode, in which it refuses to recompute the choice. `T_chosen` stays exactly as
# the primary artefact recorded it (es 1.30, uk 1.10, it 1.20), and
# `at_home_mae_pp` -- the statistic the choice was made on -- is not touched.
#
# 🔴 THE SPLICE MUST BE DECLARED, not silently assembled: author's directive,
# in `outputs_step5/temperature_calibration.md`.
#
# WHAT IS HELD IDENTICAL TO THE PRIMARY AND REPLICATE PASSES
# ==========================================================
#   prompt seed 42 · n_prompts 600 · top_p 1.0 · top_k 0 · max_new_tokens 1200
#   same base repo + pinned revision · same LoRA adapter per fold
# No grid point is invented: all six are already on the pre-registered uniform
# grid 0.50..1.30 step 0.10.

set -x
FOLD=${1:?usage: sbatch 4thJ_step5_temperature_coverage101.sh <es|uk|it>}

# The COMPLEMENT of the replicate window, on the pre-registered grid.
case "$FOLD" in
    es) MISSING="0.50,0.60,0.70,0.80,0.90,1.00" ;;   # window 1.10,1.20,1.30
    it) MISSING="0.50,0.60,0.70,0.80,0.90,1.00" ;;   # window 1.10,1.20,1.30
    uk) MISSING="0.50,0.60,0.70,0.80,0.90,1.30" ;;   # window 1.00,1.10,1.20
    *)  echo "unknown fold $FOLD"; exit 1 ;;
esac

SEEDS="101"

ENVDIR=/speed-scratch/o_iseri/envs/step4
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd /speed-scratch/o_iseri

"$ENVDIR/bin/python" -m py_compile 4thJ_step5_temperature.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- fold $FOLD not started"
    exit 1
fi

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

ADAPTER=/speed-scratch/o_iseri/4J_step4/runs_ds45/leg4_primary_fold_$FOLD/adapter
if [ ! -d "$ADAPTER" ]; then
    echo "NO ADAPTER AT $ADAPTER -- D-S5-15 coverage points cannot run for fold $FOLD."
    exit 1
fi

OUT=/speed-scratch/o_iseri/4J_step5
GENDIR=$OUT/generations_$FOLD
mkdir -p "$OUT"

"$ENVDIR/bin/python" -u 4thJ_step5_temperature.py \
    --fold "$FOLD" --adapter "$ADAPTER" --out "$OUT" \
    --gen-batch 8 --n-prompts 600 \
    --grid "$MISSING" --gen-seeds "$SEEDS" \
    --save-gen "$GENDIR" --tag coverage101

echo "--- artefact ---"
ls -l "$OUT"
md5sum "$OUT/temperature_calibration_${FOLD}_coverage101.json"
ls -l "$GENDIR" | head -30
