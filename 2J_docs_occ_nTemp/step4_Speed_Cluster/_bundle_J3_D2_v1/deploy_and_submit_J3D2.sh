#!/encs/bin/tcsh
# deploy_and_submit_J3D2.sh — Phase 7: J3 demographics + architecture HPT (6 trials)
# Usage: tcsh /speed-scratch/o_iseri/occModeling/_bundle_J3_D2_v1/deploy_and_submit_J3D2.sh

set BASE = /speed-scratch/o_iseri/occModeling
set BUNDLE = "$BASE/_bundle_J3_D2_v1"

# Deploy patched 04D_train.py (adds DROPOUT env var support)
cp "$BUNDLE/04D_train.py" "$BASE/04D_train.py"

# Deploy patched config_to_env.sh (adds dropout mapping)
cp "$BUNDLE/config_to_env.sh" "$BASE/Speed_Cluster/config_to_env.sh"

# Deploy 6 configs
cp $BUNDLE/step4_Speed_Cluster/sample_configs/*.yaml "$BASE/configs/"

# Deploy 6 SLURM wrappers
cp $BUNDLE/step4_Speed_Cluster/sample_jobs/*.sh "$BASE/Speed_Cluster/jobs/"

# dos2unix all deployed files
dos2unix "$BASE/04D_train.py"
dos2unix "$BASE/Speed_Cluster/config_to_env.sh"
dos2unix "$BASE/configs/J3_D2_"*.yaml
dos2unix "$BASE/Speed_Cluster/jobs/J3_D2_"*.sh

# Submit 6 parallel jobs
echo "=== Submitting Phase 7: J3 D2 bundle (6 trials) ==="
sbatch "$BASE/Speed_Cluster/jobs/J3_D2_CTRL.sh"
sbatch "$BASE/Speed_Cluster/jobs/J3_D2_ENC8.sh"
sbatch "$BASE/Speed_Cluster/jobs/J3_D2_DEC8.sh"
sbatch "$BASE/Speed_Cluster/jobs/J3_D2_H16.sh"
sbatch "$BASE/Speed_Cluster/jobs/J3_D2_W512.sh"
sbatch "$BASE/Speed_Cluster/jobs/J3_D2_D15.sh"
echo "=== All 6 submitted ==="
