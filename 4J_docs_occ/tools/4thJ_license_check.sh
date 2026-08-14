#!/bin/bash
#SBATCH --job-name=4J_lic
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_lic_%j.out

# Reuses the venv built by 4thJ_tok_setup_and_run.sh. Does not touch envs/step4.
# Pure stdlib, but run under the same interpreter for consistency with the other jobs.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/4j_tok
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp

if [ ! -x "$ENVDIR/bin/python" ]; then
    /speed-scratch/o_iseri/envs/step4/bin/python -m venv "$ENVDIR"
    "$ENVDIR/bin/python" -m pip install --upgrade pip
    "$ENVDIR/bin/python" -m pip install "transformers>=4.47" tokenizers sentencepiece protobuf
fi

cd /speed-scratch/o_iseri
"$ENVDIR/bin/python" -u 4thJ_license_check.py
