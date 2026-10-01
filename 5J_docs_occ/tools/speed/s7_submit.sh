#!/bin/bash
# login node: sbatch only. Part A chain (see Step7_docs/impl/2026-10-01_wp5_district.md)
D=/speed-scratch/o_iseri/5J/district
cd $D/code || exit 2
J0=$(sbatch --parsable s7_stage.sbatch); echo J0_stage=$J0
J1=$(sbatch --parsable --dependency=afterok:$J0 s7_sample.sbatch); echo J1_sample=$J1
J2=$(sbatch --parsable --dependency=afterok:$J0 s7_hh_draw.sbatch); echo J2_hhdraw=$J2
J3=$(sbatch --parsable --dependency=afterok:$J2 s7_hh_pilot.sbatch); echo J3_hhpilot=$J3
J5=$(sbatch --parsable --dependency=afterok:$J3 s7_hh_full.sbatch); echo J5_hhfull=$J5
J7=$(sbatch --parsable --dependency=afterok:$J1:$J5 s7_draws.sbatch); echo J7_draws=$J7
J8=$(sbatch --parsable --dependency=afterok:$J7 s7_gpu.sbatch); echo J8_gpu=$J8
J9=$(sbatch --parsable --dependency=afterok:$J7 s7_ep_table.sbatch); echo J9_eptable=$J9
J10=$(sbatch --parsable --dependency=afterok:$J9 s7_ep_array.sbatch); echo J10_eparray=$J10
J11=$(sbatch --parsable --dependency=afterany:$J10 s7_ep_check.sbatch); echo J11_epcheck=$J11
squeue -u o_iseri | head -30
