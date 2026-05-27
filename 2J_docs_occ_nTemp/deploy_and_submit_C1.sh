#!/bin/bash
set -e
cd /speed-scratch/o_iseri/occModeling
/bin/cp -f _bundle_sweepC_v1/step4_Speed_Cluster/sample_configs/MDLM_C.yaml sample_configs/
/bin/cp -f _bundle_sweepC_v1/step4_Speed_Cluster/sample_configs/SEDD_C.yaml sample_configs/
/bin/cp -f _bundle_sweepC_v1/step4_Speed_Cluster/sample_jobs/MDLM_C.sh sample_jobs/
/bin/cp -f _bundle_sweepC_v1/step4_Speed_Cluster/sample_jobs/SEDD_C.sh sample_jobs/
sed -i 's/\r$//' sample_jobs/MDLM_C.sh sample_jobs/SEDD_C.sh
sbatch sample_jobs/MDLM_C.sh
sbatch sample_jobs/SEDD_C.sh
