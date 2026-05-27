#!/bin/bash
# deploy_and_submit_F.sh — Stage F: generate 10% sample, deploy configs/wrappers/model, sbatch all 9.
set -e

BASE=/speed-scratch/o_iseri/occModeling
BUNDLE="$BASE/_bundle_sweepF_v1"
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

echo "=== Generating per-split meta CSVs (if missing) ==="
if [ ! -f "$BASE/outputs_step4_G2/step4_train_meta.csv" ]; then
    $PYTHON "$BUNDLE/gen_split_metas.py" "$BASE/outputs_step4_G2"
else
    echo "  Split metas already exist, skipping."
fi

echo "=== Generating 10% stratified sample ==="
if [ ! -d "$BASE/outputs_step4_G2_sample10" ]; then
    $PYTHON "$BASE/04A_sample_assembly.py" --src "$BASE/outputs_step4_G2" --frac 0.10 --out "$BASE/outputs_step4_G2_sample10"
else
    echo "  Sample dir already exists, skipping."
fi

echo "=== Generating training pairs for 10% sample ==="
if [ ! -f "$BASE/outputs_step4_G2_sample10/training_pairs.pt" ]; then
    $PYTHON "$BASE/04C_training_pairs.py" --sample_dir "$BASE/outputs_step4_G2_sample10"
else
    echo "  training_pairs.pt already exists, skipping."
fi

echo "=== Deploying patched MDLM model (env-var configurable) ==="
cp "$BUNDLE/04B_model_MDLM.py" "$BASE/"

echo "=== Deploying Stage F configs ==="
cp "$BUNDLE/step4_Speed_Cluster/sample_configs"/MDLM_F*.yaml "$BASE/sample_configs/"

echo "=== Deploying Stage F wrappers ==="
cp "$BUNDLE/step4_Speed_Cluster/sample_jobs"/MDLM_F*.sh "$BASE/Speed_Cluster/jobs/"

echo "=== dos2unix ==="
dos2unix "$BASE/04B_model_MDLM.py" 2>/dev/null || true
dos2unix "$BASE/sample_configs"/MDLM_F*.yaml 2>/dev/null || true
dos2unix "$BASE/Speed_Cluster/jobs"/MDLM_F*.sh 2>/dev/null || true

echo "=== Submitting 9 Stage F jobs ==="
sbatch "$BASE/Speed_Cluster/jobs/MDLM_F0.sh"
sbatch "$BASE/Speed_Cluster/jobs/MDLM_F1.sh"
sbatch "$BASE/Speed_Cluster/jobs/MDLM_F2.sh"
sbatch "$BASE/Speed_Cluster/jobs/MDLM_F3.sh"
sbatch "$BASE/Speed_Cluster/jobs/MDLM_F4.sh"
sbatch "$BASE/Speed_Cluster/jobs/MDLM_F5.sh"
sbatch "$BASE/Speed_Cluster/jobs/MDLM_F6.sh"
sbatch "$BASE/Speed_Cluster/jobs/MDLM_F7.sh"
sbatch "$BASE/Speed_Cluster/jobs/MDLM_F8.sh"

echo "=== All 9 Stage F jobs submitted ==="
