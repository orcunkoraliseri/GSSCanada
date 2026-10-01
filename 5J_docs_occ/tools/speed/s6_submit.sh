#!/bin/bash
# Step 6 part C chain (sbatch calls only). Amendment 1 is already locked (jobs 1405152, 1405153).
cd /speed-scratch/o_iseri/5J/test/code || exit 2
date
SN=$(sbatch --parsable s6_snapshot.sbatch); echo SN_snapshot=$SN
ST=$(sbatch --parsable s6_store.sbatch); echo ST_store=$ST
B0=$(sbatch --parsable s6_b0.sbatch); echo B0_b0=$B0
DC=$(sbatch --parsable --dependency=afterok:$ST s6_dcheck.sbatch); echo DC_dcheck=$DC
B1=$(sbatch --parsable --dependency=afterok:$ST:$SN s6_b1.sbatch "B1 B1_loco_es"); echo B1_b1_and_loco_es=$B1
BI=$(sbatch --parsable --dependency=afterok:$ST:$SN:1405050 --kill-on-invalid-dep=yes s6_b1.sbatch B1_loco_it); echo B1IT_b1_loco_it=$BI
PR=$(sbatch --parsable --array=0-5%3 --dependency=afterok:$ST:$SN:$DC s6_pred.sbatch); echo PR_pred_array=$PR
FI=$(sbatch --parsable --dependency=afterok:$B0:$B1:$BI:$PR s6_final.sbatch); echo FIN_final=$FI
squeue -u o_iseri -o "%i %j %T %r"
