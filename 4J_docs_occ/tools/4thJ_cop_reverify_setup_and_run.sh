#!/bin/bash
#SBATCH --job-name=4J_cop_reverify
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_cop_reverify_%j.out

# COP-packing RE-VERIFICATION: checks whether D-S3-1 (job 1252633, tools/4thJ_cop_measure.py)
# was measured against the wrong LOC alphabet (short numeric placeholders instead of D-S2-3's
# four semantic-class strings). Reuses the same throwaway venv as 4thJ_act2_setup_and_run.sh
# (/speed-scratch/o_iseri/envs/4j_tok, symlinked to envs/step4's python), which already has
# transformers/pandas/pyarrow/numpy installed as of job 1255143. Does NOT touch envs/step4's
# training install. Does NOT touch job 1255143 (unrelated ACT2 job) or its files.

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
"$ENVDIR/bin/python" -u 4thJ_cop_reverify.py
