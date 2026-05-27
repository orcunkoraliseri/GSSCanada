#!/bin/bash
set -e
cd /speed-scratch/o_iseri/occModeling
for TAG in MDLM_D1 MDLM_D2 MDLM_D3 MDLM_D4 MDLM_D5 MDLM_D6; do
  /bin/cp -f _bundle_sweepD_v1/step4_Speed_Cluster/sample_configs/${TAG}.yaml sample_configs/
  /bin/cp -f _bundle_sweepD_v1/step4_Speed_Cluster/sample_jobs/${TAG}.sh sample_jobs/
  sed -i 's/\r$//' sample_jobs/${TAG}.sh
done
for TAG in MDLM_D1 MDLM_D2 MDLM_D3 MDLM_D4 MDLM_D5 MDLM_D6; do
  sbatch sample_jobs/${TAG}.sh
done
