#!/encs/bin/bash
# resume_04E_F3_sweep.sh — re-submit corrected 04E chains for all F3 configs
#
# Run AFTER cancelling the bad pending jobs (see comments in header).
# F3A/B: 04D already done — submit 04E immediately.
# F3C/D: 04D still running (902833, 902839) — submit 04E with afterok dependency.
#
# Fix: 04E now uses --data_dir outputs_step4 (shared preprocessed .pt files),
#      not outputs_step4_F3X (which only has checkpoints and logs).
#
# Usage (on the cluster, login node):
#   bash resume_04E_F3_sweep.sh [CHAIN_TAG]

set -euo pipefail

CHAIN_TAG="${1:-F3_sweep_20260424_1635}"
BASE=/speed-scratch/o_iseri/occModeling
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

submit_04E_chain() {
    local TAG=$1
    local DEP_D=$2  # job ID of 04D to wait for; empty = submit immediately

    local OUT_DIR=outputs_step4_${TAG}
    local CKPT=${OUT_DIR}/checkpoints/best_model.pt

    local DEP_ARG=""
    if [ -n "$DEP_D" ]; then DEP_ARG="--dependency=afterok:${DEP_D}"; fi

    local JID_E
    JID_E=$(sbatch --parsable $DEP_ARG --partition=pg --gres=gpu:1 --mem=48Gb --time=04:00:00 --job-name=04E_${TAG} --output="logs/04E_${TAG}_%j.out" --error="logs/04E_${TAG}_%j.err" --export=ALL --wrap="cd $BASE && . /encs/pkg/modules-5.3.1/root/init/bash && module load cuda/12.8 && $PYTHON -u 04E_inference.py --data_dir outputs_step4 --checkpoint $CKPT --output ${OUT_DIR}/augmented_diaries.csv --temperature 0.8")
    echo "  $TAG  04E: $JID_E" >&2

    local JID_F
    JID_F=$(sbatch --parsable --dependency=afterok:$JID_E --partition=ps --mem=48G --time=02:00:00 --job-name=04F_${TAG} --output="logs/04F_${TAG}_%j.out" --error="logs/04F_${TAG}_%j.err" --wrap="cd $BASE && $PYTHON -u 04F_validation.py --data_dir ${OUT_DIR}")
    echo "  $TAG  04F: $JID_F" >&2

    local JID_H
    JID_H=$(sbatch --parsable --dependency=afterok:$JID_E --partition=ps --mem=8G --cpus-per-task=4 --time=00:30:00 --job-name=04H_${TAG} --output="logs/04H_${TAG}_%j.out" --error="logs/04H_${TAG}_%j.err" --wrap="cd $BASE && $PYTHON -u 04H_diagnostics_cpu.py --data_dir ${OUT_DIR} --step3_dir outputs_step3 --output_json ${OUT_DIR}/diagnostics_v4.json")
    echo "  $TAG  04H: $JID_H" >&2

    local JID_I
    JID_I=$(sbatch --parsable --dependency=afterok:$JID_E --partition=ps --mem=8G --cpus-per-task=4 --time=00:30:00 --job-name=04I_${TAG} --output="logs/04I_${TAG}_%j.out" --error="logs/04I_${TAG}_%j.err" --wrap="cd $BASE && $PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir ${OUT_DIR} --step3_dir outputs_step3 --output_json ${OUT_DIR}/diagnostics_v4_actcop.json")
    echo "  $TAG  04I: $JID_I" >&2

    local JID_J
    JID_J=$(sbatch --parsable --dependency=afterok:$JID_E --partition=ps --mem=8G --cpus-per-task=4 --time=00:30:00 --job-name=04J_${TAG} --output="logs/04J_${TAG}_%j.out" --error="logs/04J_${TAG}_%j.err" --wrap="cd $BASE && $PYTHON -u 04J_statistical_diagnostics.py --data_dir ${OUT_DIR} --step3_dir outputs_step3 --output_json ${OUT_DIR}/diagnostics_v4_statistical.json --n_bootstrap 1000")
    echo "  $TAG  04J: $JID_J" >&2

    echo "$JID_J"
}

echo "Submitting corrected 04E chains (data_dir=outputs_step4) for tag: $CHAIN_TAG"
echo ""
JID_J_A=$(submit_04E_chain F3A ""      | tail -1)
JID_J_B=$(submit_04E_chain F3B ""      | tail -1)
JID_J_C=$(submit_04E_chain F3C 902833  | tail -1)
JID_J_D=$(submit_04E_chain F3D 902839  | tail -1)

echo ""
DEP="afterok:${JID_J_A}:${JID_J_B}:${JID_J_C}:${JID_J_D}"
JID_Z=$(sbatch --parsable --dependency=$DEP --export=ALL,CHAIN_TAG=$CHAIN_TAG job_04Z_F3_compare.sh)
echo "  04Z: $JID_Z (afterok all 04J)"

echo ""
echo "Done — monitor with: squeue -u \$USER"
