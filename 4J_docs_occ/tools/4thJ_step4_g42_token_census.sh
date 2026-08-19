#!/bin/bash
#SBATCH --job-name=4J_s4_g42census
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step4_g42census_%j.out

# D-S4-4's precondition. CPU ONLY -- no --gres, no model, tokenizer only, so this does
# NOT contend with a training fold for the GPU (FINDING 2) and can run while one is up.
#
# Reuses envs/4j_tok, which already carries transformers from the Step 3 build family.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/4j_tok
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp
export TOKENIZERS_PARALLELISM=false

cd /speed-scratch/o_iseri

"$ENVDIR/bin/python" -m py_compile 4thJ_step4_g42_token_census.py
if [ $? -ne 0 ]; then
    echo "SYNTAX ERROR -- census not started"
    exit 1
fi

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

"$ENVDIR/bin/python" -u 4thJ_step4_g42_token_census.py --fold es --n 300
