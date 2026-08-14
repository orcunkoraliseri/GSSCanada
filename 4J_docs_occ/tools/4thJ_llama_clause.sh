#!/bin/bash
#SBATCH --job-name=4J_llama
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_llama_%j.out

# Reuses the venv built by 4thJ_tok_setup_and_run.sh. Does not touch envs/step4.

set -x
ENVDIR=/speed-scratch/o_iseri/envs/4j_tok
export TMPDIR=/speed-scratch/o_iseri/tmp

cd /speed-scratch/o_iseri
"$ENVDIR/bin/python" -u 4thJ_llama_clause.py
