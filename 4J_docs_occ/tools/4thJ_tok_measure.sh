#!/bin/bash
#SBATCH --job-name=4J_tok
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/4J_tok_%j.out

export HF_HOME=/speed-scratch/o_iseri/hf_cache
cd /speed-scratch/o_iseri
/speed-scratch/o_iseri/envs/step4/bin/python -u 4thJ_tok_measure.py
