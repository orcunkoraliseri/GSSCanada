#!/bin/bash
cd /speed-scratch/o_iseri/5J/train || exit 2
date
A=$(sbatch --parsable s5_shortlist.sbatch); echo A=$A
B=$(sbatch --parsable --array=0-5%6 --dependency=afterok:$A s5_wpred.sbatch); echo B=$B
C=$(sbatch --parsable --array=0-5%4 --dependency=afterok:$B:1404526 s5_wscore.sbatch); echo C=$C
D=$(sbatch --parsable --dependency=afterok:$C s5_wwinner.sbatch); echo D=$D
E=$(sbatch --parsable --dependency=afterok:$D s5_wreload.sbatch); echo E=$E
F=$(sbatch --parsable --dependency=afterok:$E s5_wcleanup.sbatch); echo F=$F
