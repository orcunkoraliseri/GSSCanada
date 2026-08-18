#!/bin/bash
#SBATCH --job-name=4J_act2
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_act2_%j.out

# Step 3, work item 3.2-bis: ACT2 tuple token-cost measurement.
# Reuses the same throwaway venv as 4thJ_tok_setup_and_run.sh / 4thJ_cop_measure.py
# (/speed-scratch/o_iseri/envs/4j_tok), extended with pandas+pyarrow (confirmed absent on
# 2026-08-17). Does NOT touch envs/step4's training install.

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
"$ENVDIR/bin/python" -u 4thJ_act2_measure.py
