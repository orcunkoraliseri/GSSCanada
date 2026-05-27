#!/bin/bash
set -e
cd /speed-scratch/o_iseri/occModeling
/bin/cp -rf _bundle_sweepA/*.py .
/bin/cp -rf _bundle_sweepA/step4_Speed_Cluster/sample_configs .
/bin/cp -rf _bundle_sweepA/step4_Speed_Cluster/sample_jobs .
/bin/cp -f _bundle_sweepA/step4_Speed_Cluster/config_to_env.sh Speed_Cluster/
/bin/cp -f _bundle_sweepA/step4_Speed_Cluster/config_to_env.py Speed_Cluster/
/bin/cp -rf _bundle_sweepA/outputs_step4_G2_sample2 .
sed -i 's/\r$//' sample_jobs/*.sh Speed_Cluster/config_to_env.sh
for t in CC CC_SPL CC_FACT HSMM MDLM HIER MAMBA SEDD SINK GCE; do
  sbatch sample_jobs/${t}_A.sh
done
