#!/bin/bash
set -e
cd /speed-scratch/o_iseri/occModeling
/bin/cp -f _bundle_sweepB_v2/step4_Speed_Cluster/sample_configs/SEDD_B.yaml sample_configs/
/bin/cp -f _bundle_sweepB_v2/step4_Speed_Cluster/sample_configs/MDLM_B.yaml sample_configs/
/bin/cp -f _bundle_sweepB_v2/step4_Speed_Cluster/sample_jobs/SEDD_B.sh sample_jobs/
/bin/cp -f _bundle_sweepB_v2/step4_Speed_Cluster/sample_jobs/MDLM_B.sh sample_jobs/
sed -i 's/\r$//' sample_jobs/SEDD_B.sh sample_jobs/MDLM_B.sh
sbatch sample_jobs/SEDD_B.sh
sbatch sample_jobs/MDLM_B.sh
