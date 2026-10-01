#!/bin/bash
# login node: sbatch only. Part B chain (see Step7_docs/impl/2026-10-01_wp5_district.md, "PART B")
D=/speed-scratch/o_iseri/5J/district
cd $D/code || exit 2
L=$D/logs
JA=$(sbatch --parsable s7_bgtime.sbatch); echo JA_time=$JA
JD=$(sbatch --parsable s7_bghourly.sbatch); echo JD_hourly=$JD
JC=$(sbatch --parsable s7_bgcpu.sbatch); echo JC_cpu1core=$JC
JWA=$(sbatch --parsable --dependency=afterok:$JA s7_bwcheck_a.sbatch); echo JWA_wcheck_a=$JWA
JB=$(sbatch --parsable --dependency=afterok:$JA s7_bgrun.sbatch); echo JB_draws_array=$JB
JWB=$(sbatch --parsable --dependency=afterok:$JB:$JD s7_bwcheck_b.sbatch); echo JWB_wcheck_b=$JWB
JF=$(sbatch --parsable --dependency=afterok:$JB s7_bspread.sbatch); echo JF_spread=$JF
JR=$(sbatch --parsable s7_bep_rest.sbatch); echo JR_ep_rest_prep=$JR
JEP=$(sbatch --parsable --dependency=afterok:$JR s7_bep_array.sbatch); echo JEP_ep_array=$JEP
JEC=$(sbatch --parsable --dependency=afterany:$JEP s7_bep_check.sbatch); echo JEC_ep_check_all=$JEC
JE=$(sbatch --parsable --dependency=afterok:$JEC:$JD s7_bcompare.sbatch); echo JE_compare=$JE
JG=$(sbatch --parsable --dependency=afterok:$JA:$JD:$JC:$JEC --export=ALL,LOG_TIME=$L/s7_bgtime_$JA.out,LOG_HOURLY=$L/s7_bghourly_$JD.out,LOG_CPU=$L/s7_bgcpu_$JC.out s7_bspeed.sbatch); echo JG_speed=$JG
squeue -u o_iseri | head -40
