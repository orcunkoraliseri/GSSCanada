#!/bin/bash
# part E chain (rules R8, R9). Only sbatch calls.
cd /speed-scratch/o_iseri/5J/train || exit 2
date
J0=$(sbatch --parsable s5_ctrl_check.sbatch); echo J0_check=$J0
J1=$(sbatch --parsable --dependency=afterok:$J0 s5_ctrl_reload.sbatch); echo J1_reload=$J1
BE=$(sbatch --parsable --dependency=afterok:$J0 s5_ctrl_b1.sbatch es); echo B1_loco_es=$BE
BI=$(sbatch --parsable --dependency=afterok:$BE s5_ctrl_b1.sbatch it); echo B1_loco_it=$BI
BM=$(sbatch --parsable --array=0-4%4 --dependency=afterok:$J0:$J1 s5_ctrl_train.sbatch); echo B_train_SC=$BM
BL=$(sbatch --parsable --array=5-6%2 --dependency=afterok:$J0:$J1 s5_ctrl_train.sbatch); echo B_train_loco=$BL
DP=$(sbatch --parsable --array=0-4%4 --dependency=afterok:$BM s5_ctrl_pred.sbatch); echo D_pred=$DP
DS=$(sbatch --parsable --array=0-4%2 --dependency=afterok:$DP s5_ctrl_score.sbatch); echo D_score=$DS
D3=$(sbatch --parsable --dependency=afterok:$DS s5_ctrl_s3c.sbatch); echo D_S3vsC=$D3
E=$(sbatch --parsable --dependency=afterok:$D3 s5_ctrl_seeds.sbatch); echo E_seeds=$E
