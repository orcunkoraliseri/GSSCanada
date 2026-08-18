#!/bin/bash
#SBATCH --job-name=4J_step3_rebuild
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step3_rebuild_%j.out

# Step 3 REBUILD after D-S3-11 / D-S3-12 / D-S3-13 (author, 2026-08-17).
#   D-S3-11  prefix 8 fields -> 6; `mode` and `scheme` no longer serialised.
#   D-S3-12  G3.9 re-pointed at fold-aware cross-country vocabulary; its
#            perturbation is `national_raw_hh_type_it`, replacing `mode_second_value`.
#   D-S3-13  G3.3 re-specified as a CHARACTER-level round trip; swap partner
#            moved off gpt2 (byte-level, lossless) to bert-base-uncased.
#
# ONE job, two phases, so nothing has to wait between them (no-parking rule):
#   phase 1  rebuild the corpus     -> 4thJ_step3_build.py
#   phase 2  re-run the battery     -> 4thJ_gates_step3.py --perturbation all
# Phase 2 runs ONLY if phase 1 exits 0. A stale corpus must never be gated.
#
# Copied from the shipped 4thJ_gates_step3_setup_and_run.sh template per the
# cluster rule: submit through a shipped .sh launcher, never a hand-rolled
# `sbatch --wrap`.
#
# 🔴 Job 1256012's evidence is NOT overwritten. The previous corpus is preserved
# under a job-stamped name before the rebuild, and this run writes its reports to
# a NEW output directory (4J_step3_gates_out_v2), leaving 4J_step3_gates_out
# exactly as job 1256012 left it.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/4j_tok
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp

if [ ! -x "$ENVDIR/bin/python" ]; then
    /speed-scratch/o_iseri/envs/step4/bin/python -m venv "$ENVDIR"
fi
"$ENVDIR/bin/python" -m pip install --upgrade pip
"$ENVDIR/bin/python" -m pip install "transformers>=4.45" tokenizers sentencepiece protobuf pandas pyarrow numpy

"$ENVDIR/bin/python" -c "import transformers, pandas, pyarrow, numpy; print('transformers', transformers.__version__, 'pandas', pandas.__version__, 'pyarrow', pyarrow.__version__, 'numpy', numpy.__version__)"
cd /speed-scratch/o_iseri

# --- preserve job 1256012's corpus before it is overwritten -----------------
OLD=/speed-scratch/o_iseri/4J_step3_corpus.jsonl
BK=/speed-scratch/o_iseri/4J_step3_corpus_1255620_8field.jsonl
if [ -s "$OLD" ]; then
    cp -p "$OLD" "$BK"
    if [ ! -s "$BK" ]; then
        echo "FATAL: backup $BK is empty or missing after cp -- refusing to rebuild"
        exit 1
    fi
    echo "backup ok: $(wc -l < "$BK") lines in $BK"
fi

# --- phase 1: rebuild the corpus at the six-field prefix --------------------
echo "=== PHASE 1: rebuilding corpus (6-field prefix, D-S3-11) ==="
"$ENVDIR/bin/python" -u 4thJ_step3_build.py
RC=$?
if [ $RC -ne 0 ]; then
    echo "FATAL: phase 1 (corpus rebuild) exited $RC -- NOT running the battery on a stale or partial corpus"
    exit $RC
fi

# --- phase 2: re-run the full battery ---------------------------------------
echo "=== PHASE 2: re-running the sixteen-gate battery ==="
mkdir -p /speed-scratch/o_iseri/4J_step3_gates_out_v2
"$ENVDIR/bin/python" -u 4thJ_gates_step3.py \
    --corpus /speed-scratch/o_iseri/4J_step3_corpus.jsonl \
    --harmonised /speed-scratch/o_iseri/4J/outputs_step2/run_20260817-strata/harmonised.parquet \
    --crosswalks /speed-scratch/o_iseri/4J/outputs_step2 \
    --out /speed-scratch/o_iseri/4J_step3_gates_out_v2 \
    --perturbation all
