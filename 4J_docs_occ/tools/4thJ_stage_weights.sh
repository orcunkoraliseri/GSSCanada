#!/bin/bash
#SBATCH --job-name=4J_stage
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_stage_%j.out

# 4J Step 4.1 - pre-stage the three checkpoints and record their revision hashes.
# Reuses the venv built by 4thJ_tok_setup_and_run.sh. Does not touch envs/step4.
# Download only: no GPU, no model load, no measurement.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/4j_tok
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export HF_HUB_ENABLE_HF_TRANSFER=0

if [ ! -x "$ENVDIR/bin/python" ]; then
    /speed-scratch/o_iseri/envs/step4/bin/python -m venv "$ENVDIR"
    "$ENVDIR/bin/python" -m pip install --upgrade pip
    "$ENVDIR/bin/python" -m pip install "transformers>=4.47" tokenizers sentencepiece protobuf
fi

"$ENVDIR/bin/python" -c "import huggingface_hub; print('hub', huggingface_hub.__version__)"
cd /speed-scratch/o_iseri
"$ENVDIR/bin/python" -u 4thJ_stage_weights.py
df -h /speed-scratch | tail -2
