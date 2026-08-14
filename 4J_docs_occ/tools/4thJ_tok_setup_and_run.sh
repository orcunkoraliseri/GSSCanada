#!/bin/bash
#SBATCH --job-name=4J_tok
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_tok_%j.out

# Builds a small throwaway venv for the tokenizer measurement, then runs it.
# It does NOT touch envs/step4. Needs network on the compute node for pip and for
# the tokenizer files; if there is none, the log says so on the pip line.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/4j_tok
export HF_HOME=/speed-scratch/o_iseri/hf_cache
export PIP_CACHE_DIR=/speed-scratch/o_iseri/pip_cache
export TMPDIR=/speed-scratch/o_iseri/tmp

if [ ! -x "$ENVDIR/bin/python" ]; then
    /speed-scratch/o_iseri/envs/step4/bin/python -m venv "$ENVDIR"
    "$ENVDIR/bin/python" -m pip install --upgrade pip
    "$ENVDIR/bin/python" -m pip install "transformers>=4.45" tokenizers sentencepiece protobuf
fi

"$ENVDIR/bin/python" -c "import transformers; print('transformers', transformers.__version__)"
cd /speed-scratch/o_iseri
"$ENVDIR/bin/python" -u 4thJ_tok_measure.py
