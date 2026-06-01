#!/bin/bash
# deploy_and_submit_E.sh — Stage E: copy configs/wrappers/model, dos2unix, sbatch all 4.
set -e

BASE=/speed-scratch/o_iseri/occModeling
BUNDLE="$BASE/_bundle_sweepE_v1"

echo "=== Deploying Stage E configs ==="
cp "$BUNDLE/step4_Speed_Cluster/sample_configs"/MDLM_E*.yaml "$BASE/sample_configs/"

echo "=== Deploying Stage E wrappers ==="
cp "$BUNDLE/step4_Speed_Cluster/sample_jobs"/MDLM_E*.sh "$BASE/Speed_Cluster/jobs/"

echo "=== Deploying MDLM_v2 model file ==="
cp "$BUNDLE/04B_model_MDLM_v2.py" "$BASE/"

echo "=== Deploying patched 04B_model.py and 04D_train.py ==="
cp "$BUNDLE/04B_model.py" "$BASE/"
cp "$BUNDLE/04D_train.py" "$BASE/"

echo "=== dos2unix ==="
dos2unix "$BASE/sample_configs"/MDLM_E*.yaml 2>/dev/null || true
dos2unix "$BASE/Speed_Cluster/jobs"/MDLM_E*.sh 2>/dev/null || true
dos2unix "$BASE/04B_model_MDLM_v2.py" 2>/dev/null || true
dos2unix "$BASE/04B_model.py" 2>/dev/null || true
dos2unix "$BASE/04D_train.py" 2>/dev/null || true

echo "=== Submitting 4 Stage E jobs ==="
sbatch "$BASE/Speed_Cluster/jobs/MDLM_E1.sh"
sbatch "$BASE/Speed_Cluster/jobs/MDLM_E2.sh"
sbatch "$BASE/Speed_Cluster/jobs/MDLM_E3.sh"
sbatch "$BASE/Speed_Cluster/jobs/MDLM_E4.sh"

echo "=== All 4 Stage E jobs submitted ==="
