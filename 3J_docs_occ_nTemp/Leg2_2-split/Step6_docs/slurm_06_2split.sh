#!/bin/tcsh
#SBATCH --job-name=step6_2split
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --time=48:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --output=step6_2split_%j.out

/speed-scratch/o_iseri/envs/step4/bin/python /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step6_docs/3rdJ_06_longitudinalForecasting_2split.py --stage all --data /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/outputs_step4/sweep/R5_lr1e4/augmented_diaries.csv
