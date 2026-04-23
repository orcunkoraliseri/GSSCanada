#!/encs/bin/bash
# submit_step4_F3_sweep.sh — F3 hyper-parameter sweep launcher
#
# Usage (on the cluster, login node only):
#   bash submit_step4_F3_sweep.sh [CHAIN_TAG]
#   e.g.: bash submit_step4_F3_sweep.sh F3_sweep_$(date +%Y%m%d)
#
# WARNING: Run only after the F1 best_model.pt has been archived to
#   deliveries/F1_baseline/checkpoints/best_model.pt
#   (Option-B-v2 lesson: no revert path if checkpoint is clobbered)
#
# Submits 4 retrain chains in parallel (F3-A / B / C / D) up to the pg GPU cap.
# Each chain: 04D -> 04E -> {04F, 04H, 04I, 04J} (parallel post-04E)
# After all 4 chains complete, submits 04Z_F3_compare (CPU, ps).

set -euo pipefail

CHAIN_TAG="${1:-F3_sweep_$(date +%Y%m%d_%H%M)}"
BASE=/speed-scratch/o_iseri/occModeling
SCRIPTS=$BASE

echo "============================================================"
echo "F3 hyper-parameter sweep: $CHAIN_TAG"
echo "============================================================"

# --- pre-flight ---
mkdir -p "$BASE/logs" "$BASE/deliveries/F3_sweep/$CHAIN_TAG"

for tag in F3A F3B F3C F3D; do
    mkdir -p "$BASE/outputs_step4_${tag}/checkpoints"
done

# Check required scripts exist
for f in job_04D_train_F3A.sh job_04D_train_F3B.sh job_04D_train_F3C.sh job_04D_train_F3D.sh \
         job_04E_inference.sh job_04F_validation.sh job_04H_diagnostics.sh \
         job_04I_diagnostics.sh job_04J_diagnostics.sh job_04Z_F3_compare.sh; do
    if [ ! -f "$SCRIPTS/$f" ] && [ ! -f "$SCRIPTS/Speed_Cluster/$f" ]; then
        echo "ERROR: required script $f not found in $SCRIPTS or $SCRIPTS/Speed_Cluster" >&2
        exit 1
    fi
done

# --- helper: submit_chain TAG ---
# Submits the full 04D->04E->{04F,04H,04I,04J} chain for one F3 config.
# Prints the final JID (last job in chain, used for afterok on compare job).
submit_chain() {
    local TAG=$1          # e.g. F3A
    local OUT_DIR="outputs_step4_${TAG}"
    local CKPT_DIR="${OUT_DIR}/checkpoints"

    # 04D retrain (GPU, pg)
    local JID_D
    JID_D=$(sbatch --parsable job_04D_train_${TAG}.sh)
    echo "  $TAG  04D submitted: $JID_D"

    # 04E inference (GPU, pg) — depends on 04D
    local JID_E
    JID_E=$(sbatch --parsable \
        --dependency=afterok:$JID_D \
        --job-name=04E_${TAG} \
        --output="logs/04E_${TAG}_%j.out" \
        --error="logs/04E_${TAG}_%j.err" \
        --export=ALL \
        --wrap="cd $BASE && mkdir -p ${OUT_DIR} && \
            /speed-scratch/o_iseri/envs/step4/bin/python -u 04E_inference.py \
            --data_dir ${OUT_DIR} \
            --checkpoint ${CKPT_DIR}/best_model.pt \
            --output ${OUT_DIR}/augmented_diaries.csv \
            --temperature 0.8")
    echo "  $TAG  04E submitted: $JID_E (afterok:$JID_D)"

    # 04F, 04H, 04I, 04J — all parallel, all depend on 04E
    local JID_F
    JID_F=$(sbatch --parsable \
        --dependency=afterok:$JID_E \
        --partition=ps \
        --mem=48G \
        --time=02:00:00 \
        --job-name=04F_${TAG} \
        --output="logs/04F_${TAG}_%j.out" \
        --error="logs/04F_${TAG}_%j.err" \
        --wrap="cd $BASE && \
            /speed-scratch/o_iseri/envs/step4/bin/python -u 04F_validation.py \
            --data_dir ${OUT_DIR}")
    echo "  $TAG  04F submitted: $JID_F (afterok:$JID_E)"

    local JID_H
    JID_H=$(sbatch --parsable \
        --dependency=afterok:$JID_E \
        --partition=ps \
        --mem=8G \
        --cpus-per-task=4 \
        --time=00:30:00 \
        --job-name=04H_${TAG} \
        --output="logs/04H_${TAG}_%j.out" \
        --error="logs/04H_${TAG}_%j.err" \
        --wrap="cd $BASE && \
            /speed-scratch/o_iseri/envs/step4/bin/python -u 04H_diagnostics_cpu.py \
            --data_dir ${OUT_DIR} \
            --step3_dir outputs_step3 \
            --output_json ${OUT_DIR}/diagnostics_v4.json")
    echo "  $TAG  04H submitted: $JID_H (afterok:$JID_E)"

    local JID_I
    JID_I=$(sbatch --parsable \
        --dependency=afterok:$JID_E \
        --partition=ps \
        --mem=8G \
        --cpus-per-task=4 \
        --time=00:30:00 \
        --job-name=04I_${TAG} \
        --output="logs/04I_${TAG}_%j.out" \
        --error="logs/04I_${TAG}_%j.err" \
        --wrap="cd $BASE && \
            /speed-scratch/o_iseri/envs/step4/bin/python -u 04I_activity_copresence_diagnostics.py \
            --data_dir ${OUT_DIR} \
            --step3_dir outputs_step3 \
            --output_json ${OUT_DIR}/diagnostics_v4_actcop.json")
    echo "  $TAG  04I submitted: $JID_I (afterok:$JID_E)"

    local JID_J
    JID_J=$(sbatch --parsable \
        --dependency=afterok:$JID_E \
        --partition=ps \
        --mem=8G \
        --cpus-per-task=4 \
        --time=00:30:00 \
        --job-name=04J_${TAG} \
        --output="logs/04J_${TAG}_%j.out" \
        --error="logs/04J_${TAG}_%j.err" \
        --wrap="cd $BASE && \
            /speed-scratch/o_iseri/envs/step4/bin/python -u 04J_statistical_diagnostics.py \
            --data_dir ${OUT_DIR} \
            --step3_dir outputs_step3 \
            --output_json ${OUT_DIR}/diagnostics_v4_statistical.json \
            --n_bootstrap 1000")
    echo "  $TAG  04J submitted: $JID_J (afterok:$JID_E)"

    # Return the last JID in chain (04J, the one that produces the score we compare)
    echo "$JID_J"
}

# --- submit all 4 chains ---
echo ""
echo "[F3-A] baseline_balanced_bce"
JID_LAST_A=$(submit_chain F3A | tail -1)

echo ""
echo "[F3-B] +stratum_marg"
JID_LAST_B=$(submit_chain F3B | tail -1)

echo ""
echo "[F3-C] +aux_stratum_head"
JID_LAST_C=$(submit_chain F3C | tail -1)

echo ""
echo "[F3-D] +data_side_sampling"
JID_LAST_D=$(submit_chain F3D | tail -1)

# --- compare job: depends on all 4 terminal 04J jobs ---
echo ""
echo "[04Z] F3 comparison"
DEP="afterok:${JID_LAST_A}:${JID_LAST_B}:${JID_LAST_C}:${JID_LAST_D}"
JID_Z=$(sbatch --parsable \
    --dependency=$DEP \
    --export=ALL,CHAIN_TAG=$CHAIN_TAG \
    job_04Z_F3_compare.sh)
echo "  04Z submitted: $JID_Z (afterok all 04J)"

# --- summary ---
echo ""
echo "============================================================"
echo "F3 sweep submitted — tag: $CHAIN_TAG"
echo "Monitor:  squeue -u \$USER"
echo "Cancel:   scancel $JID_LAST_A $JID_LAST_B $JID_LAST_C $JID_LAST_D $JID_Z"
echo "Pull when done (locally):"
echo "  scp -r o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/deliveries/F3_sweep/$CHAIN_TAG ."
echo "============================================================"
