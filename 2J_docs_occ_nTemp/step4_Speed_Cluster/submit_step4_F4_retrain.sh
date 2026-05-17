#!/encs/bin/bash
# submit_step4_F4_retrain.sh — single F4 retrain chain
#
# Usage (on the cluster, login node only):
#   bash submit_step4_F4_retrain.sh [CHAIN_TAG]
#   e.g.: bash submit_step4_F4_retrain.sh F4_retrain_$(date +%Y%m%d_%H%M)
#
# Chain: 04D_F4 -> 04E -> {04F, 04H, 04I, 04J} (parallel post-04E)
# Compare output against F3-C baseline: outputs_step4_F3C/diagnostics_v4_statistical.json
# Key gate: composite_score < 2.366 (F3-C) and Alone gap < 13.3 pp

set -euo pipefail

CHAIN_TAG="${1:-F4_retrain_$(date +%Y%m%d_%H%M)}"
BASE=/speed-scratch/o_iseri/occModeling
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
OUT_DIR=outputs_step4_F4
CKPT=${OUT_DIR}/checkpoints/best_model.pt

echo "============================================================"
echo "F4 retrain chain: $CHAIN_TAG"
echo "Config: F3-C + COP_ALONE_PW=0 (disable Alone pos_weight)"
echo "============================================================"

mkdir -p "$BASE/logs" "$BASE/${OUT_DIR}/checkpoints"

# 04D retrain (GPU, pg)
JID_D=$(sbatch --parsable job_04D_train_F4.sh)
echo "  04D_F4 submitted: $JID_D"

# 04E inference (GPU, pg)
JID_E=$(sbatch --parsable --dependency=afterok:$JID_D --partition=pg --gres=gpu:1 --mem=48Gb --time=04:00:00 --job-name=04E_F4 --output="logs/04E_F4_%j.out" --error="logs/04E_F4_%j.err" --export=ALL --wrap="cd $BASE && . /encs/pkg/modules-5.3.1/root/init/bash && module load cuda/12.8 && $PYTHON -u 04E_inference.py --data_dir outputs_step4 --checkpoint $CKPT --output ${OUT_DIR}/augmented_diaries.csv --temperature 0.8")
echo "  04E_F4 submitted: $JID_E (afterok:$JID_D)"

# 04F validation (CPU, ps)
JID_F=$(sbatch --parsable --dependency=afterok:$JID_E --partition=ps --mem=48G --time=02:00:00 --job-name=04F_F4 --output="logs/04F_F4_%j.out" --error="logs/04F_F4_%j.err" --wrap="cd $BASE && $PYTHON -u 04F_validation.py --data_dir ${OUT_DIR}")
echo "  04F_F4 submitted: $JID_F (afterok:$JID_E)"

# 04H diagnostics (CPU, ps)
JID_H=$(sbatch --parsable --dependency=afterok:$JID_E --partition=ps --mem=8G --cpus-per-task=4 --time=00:30:00 --job-name=04H_F4 --output="logs/04H_F4_%j.out" --error="logs/04H_F4_%j.err" --wrap="cd $BASE && $PYTHON -u 04H_diagnostics_cpu.py --data_dir ${OUT_DIR} --step3_dir outputs_step3 --output_json ${OUT_DIR}/diagnostics_v4.json")
echo "  04H_F4 submitted: $JID_H (afterok:$JID_E)"

# 04I activity+copresence diagnostics (CPU, ps)
JID_I=$(sbatch --parsable --dependency=afterok:$JID_E --partition=ps --mem=8G --cpus-per-task=4 --time=00:30:00 --job-name=04I_F4 --output="logs/04I_F4_%j.out" --error="logs/04I_F4_%j.err" --wrap="cd $BASE && $PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir ${OUT_DIR} --step3_dir outputs_step3 --output_json ${OUT_DIR}/diagnostics_v4_actcop.json")
echo "  04I_F4 submitted: $JID_I (afterok:$JID_E)"

# 04J statistical diagnostics (CPU, ps) — produces composite score for comparison
JID_J=$(sbatch --parsable --dependency=afterok:$JID_E --partition=ps --mem=8G --cpus-per-task=4 --time=00:30:00 --job-name=04J_F4 --output="logs/04J_F4_%j.out" --error="logs/04J_F4_%j.err" --wrap="cd $BASE && $PYTHON -u 04J_statistical_diagnostics.py --data_dir ${OUT_DIR} --step3_dir outputs_step3 --output_json ${OUT_DIR}/diagnostics_v4_statistical.json --n_bootstrap 1000")
echo "  04J_F4 submitted: $JID_J (afterok:$JID_E)"

echo ""
echo "============================================================"
echo "F4 chain submitted — tag: $CHAIN_TAG"
echo "Monitor:  squeue -u \$USER"
echo "Pull when done (locally):"
echo "  scp -r o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/${OUT_DIR}/diagnostics_v4_statistical.json ."
echo "Compare: composite < 2.366 and Alone gap < 13.3 pp beats F3-C baseline"
echo "============================================================"
