#!/bin/bash
# deploy_and_submit_v2.sh — Phase 6 Stage A re-fix + Stage B promotion
# Deploys bundle _bundle_sweepA_v2 and submits 7 jobs:
#   - 5 structural Stage A re-runs (HSMM/MDLM/HIER/MAMBA/SEDD), now routing to correct model class
#   - 2 Stage B promotions (CC_B / CC_SPL_B), 20% sample, 100 epochs, patience 15
set -e
cd /speed-scratch/o_iseri/occModeling

# Overwrite 04D_train.py with structural-fix version
/bin/cp -f _bundle_sweepA_v2/04D_train.py .

# Deploy new Stage B configs and wrappers
/bin/cp -f _bundle_sweepA_v2/step4_Speed_Cluster/sample_configs/CC_B.yaml sample_configs/
/bin/cp -f _bundle_sweepA_v2/step4_Speed_Cluster/sample_configs/CC_SPL_B.yaml sample_configs/
/bin/cp -f _bundle_sweepA_v2/step4_Speed_Cluster/sample_jobs/CC_B.sh sample_jobs/
/bin/cp -f _bundle_sweepA_v2/step4_Speed_Cluster/sample_jobs/CC_SPL_B.sh sample_jobs/

# Deploy 20% sample data (used by Stage B jobs)
/bin/cp -rf _bundle_sweepA_v2/outputs_step4_G2_sample20 .

# Fix CRLF on new wrappers
sed -i 's/\r$//' sample_jobs/CC_B.sh sample_jobs/CC_SPL_B.sh

# Submit 5 structural Stage A re-runs (configs/wrappers were deployed with v1 bundle)
for t in HSMM MDLM HIER MAMBA SEDD; do
  sbatch sample_jobs/${t}_A.sh
done

# Submit 2 Stage B jobs
sbatch sample_jobs/CC_B.sh
sbatch sample_jobs/CC_SPL_B.sh
