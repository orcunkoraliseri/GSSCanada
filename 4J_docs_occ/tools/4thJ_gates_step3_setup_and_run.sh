#!/bin/bash
#SBATCH --job-name=4J_gates_step3
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_gates_step3_%j.out

# Step 3 gate battery: sixteen gates, twenty-one perturbations, V3.a-V3.i, one coverage
# clause, run against the already-emitted corpus (job 1255620) and harmonised.parquet.
# Copied from the shipped /speed-scratch/o_iseri/4thJ_null_structure_setup_and_run.sh template
# per the cluster rule: submit through a shipped .sh launcher, never a hand-rolled `sbatch --wrap`.
# Reuses the same venv (/speed-scratch/o_iseri/envs/4j_tok), which already carries
# pandas+pyarrow+transformers from the Step 3 build family of jobs.

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

"$ENVDIR/bin/python" -c "import pandas, pyarrow, numpy; print('pandas', pandas.__version__, 'pyarrow', pyarrow.__version__, 'numpy', numpy.__version__)"
cd /speed-scratch/o_iseri
mkdir -p /speed-scratch/o_iseri/4J_step3_gates_out
"$ENVDIR/bin/python" -u 4thJ_gates_step3.py \
    --corpus /speed-scratch/o_iseri/4J_step3_corpus.jsonl \
    --harmonised /speed-scratch/o_iseri/4J/outputs_step2/run_20260817-strata/harmonised.parquet \
    --crosswalks /speed-scratch/o_iseri/4J/outputs_step2 \
    --out /speed-scratch/o_iseri/4J_step3_gates_out \
    --perturbation all
