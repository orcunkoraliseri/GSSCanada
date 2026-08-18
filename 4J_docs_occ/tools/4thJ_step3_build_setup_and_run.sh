#!/bin/bash
#SBATCH --job-name=4J_step3_build
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_step3_build_%j.out

# Step 3, work items 3.3/3.4/3.5: build encoder/decoder round-trip, run the four
# tokenizer assertions, emit corpus.jsonl and token_stats.md.
# Copied from the shipped /speed-scratch/o_iseri/4thJ_null_structure_setup_and_run.sh
# template per the cluster rule: submit through a shipped .sh launcher, never a
# hand-rolled `sbatch --wrap`. Reuses the same venv
# (/speed-scratch/o_iseri/envs/4j_tok) that already carries pandas+pyarrow+transformers.

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
"$ENVDIR/bin/python" -u 4thJ_step3_build.py
