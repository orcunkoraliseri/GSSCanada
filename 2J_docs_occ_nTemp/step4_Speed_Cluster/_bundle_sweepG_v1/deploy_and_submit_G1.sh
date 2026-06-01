#!/bin/bash
# deploy_and_submit_G1.sh — Stage G: G1 full-data + 6 preprocessing HPT trials (H0-H5).
set -e

BASE=/speed-scratch/o_iseri/occModeling
BUNDLE="$BASE/_bundle_sweepG_v1"
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

echo "=== Deploying patched model (entity embed support) ==="
cp "$BUNDLE/04B_model_MDLM.py" "$BASE/"
dos2unix "$BASE/04B_model_MDLM.py" 2>/dev/null || true

echo "=== Patching 04C: make K configurable via KNN_K env var ==="
sed -i 's/^K = 5/K = int(os.environ.get("KNN_K", "5"))/' "$BASE/04C_training_pairs.py"

echo "=== Patching 04D: add CYCLE_OVERSAMPLE_2022 support ==="
if ! grep -q "CYCLE_OVERSAMPLE_2022" "$BASE/04D_train.py"; then
    sed -i '/sample_weights = sample_weights \* wght_per/a\    # Stage H: cycle rebalancing\n    cycle_os_factor = float(os.environ.get("CYCLE_OVERSAMPLE_2022", "1.0"))\n    if cycle_os_factor > 1.0:\n        cycle_years = train_data["cycle_idx"][train_pairs["src_idx"]].numpy()\n        cycle_2022_mask = (cycle_years == 3)\n        sample_weights[cycle_2022_mask] *= cycle_os_factor\n        print(f"  CYCLE_OVERSAMPLE_2022={cycle_os_factor}: {cycle_2022_mask.sum()} pairs up-weighted")' "$BASE/04D_train.py"
    # Also add the block for when DATA_SIDE_SAMPLING is off
    sed -i '/sampler = WeightedRandomSampler/i\    # Stage H: cycle rebalancing (also applies without DATA_SIDE_SAMPLING)\n    cycle_os_factor = float(os.environ.get("CYCLE_OVERSAMPLE_2022", "1.0"))\n    if cycle_os_factor > 1.0 and os.environ.get("DATA_SIDE_SAMPLING", "0") != "1":\n        cycle_years = train_data["cycle_idx"][train_pairs["src_idx"]].numpy()\n        cycle_2022_mask = (cycle_years == 3)\n        sample_weights[cycle_2022_mask] *= cycle_os_factor\n        print(f"  CYCLE_OVERSAMPLE_2022={cycle_os_factor}: {cycle_2022_mask.sum()} pairs up-weighted")' "$BASE/04D_train.py"
fi

echo "=== Deploying all configs ==="
cp "$BUNDLE/step4_Speed_Cluster/sample_configs/"*.yaml "$BASE/sample_configs/"

echo "=== Deploying all wrappers ==="
cp "$BUNDLE/step4_Speed_Cluster/sample_jobs/"*.sh "$BASE/Speed_Cluster/jobs/"

echo "=== dos2unix ==="
dos2unix "$BASE/sample_configs/MDLM_G1.yaml" "$BASE/sample_configs/PP_H"*.yaml 2>/dev/null || true
dos2unix "$BASE/Speed_Cluster/jobs/MDLM_G1.sh" "$BASE/Speed_Cluster/jobs/PP_H"*.sh 2>/dev/null || true

echo "=== Submitting G1 (full data, F8 mask bounds) ==="
sbatch "$BASE/Speed_Cluster/jobs/MDLM_G1.sh"

echo "=== Submitting 6 preprocessing HPT trials (10% sample) ==="
sbatch "$BASE/Speed_Cluster/jobs/PP_H0.sh"
sbatch "$BASE/Speed_Cluster/jobs/PP_H1.sh"
sbatch "$BASE/Speed_Cluster/jobs/PP_H2.sh"
sbatch "$BASE/Speed_Cluster/jobs/PP_H3.sh"
sbatch "$BASE/Speed_Cluster/jobs/PP_H4.sh"
sbatch "$BASE/Speed_Cluster/jobs/PP_H5.sh"

echo "=== All 7 jobs submitted (1 full-data G1 + 6 preprocessing HPT) ==="
