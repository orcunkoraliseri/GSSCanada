#!/encs/bin/bash
# submit_step4_array.sh — sweep driver for Step-4 YAML-config + job-array system
#
# Usage (on the cluster, login node only):
#   bash Speed_Cluster/submit_step4_array.sh configs/sweep_F9.yaml [CHAIN_TAG]
#   e.g.: bash Speed_Cluster/submit_step4_array.sh configs/sweep_F9.yaml F9_$(date +%Y%m%d_%H%M)
#
# Chain per trial: 04D (array) -> 04E -> {04F, 04H, 04I, 04J} (parallel) -> extract_metrics
# Results appended to: results_index/results.csv

set -euo pipefail

SWEEP_YAML="${1:?Usage: bash submit_step4_array.sh configs/sweep_XXXX.yaml [CHAIN_TAG]}"
CHAIN_TAG="${2:-$(basename "${SWEEP_YAML%.yaml}")_$(date +%Y%m%d_%H%M)}"
BASE=/speed-scratch/o_iseri/occModeling
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================================"
echo "Sweep: $SWEEP_YAML  |  chain: $CHAIN_TAG"
echo "============================================================"

mkdir -p "$BASE/logs" "$BASE/results_index"

# ── Read trial list + smoke flag from sweep YAML (grep/sed — no yq or PyYAML needed) ──
mapfile -t TAGS < <(grep -E '^\s+-\s+\S' "$SWEEP_YAML" | sed 's/^\s*-\s*//;s/[[:space:]]*$//' || true)
SMOKE_FLAG=$( { grep '^smoke:' "$SWEEP_YAML" || true; } | sed 's/^smoke:[[:space:]]*//' | tr -d '[:space:]')
[ -z "$SMOKE_FLAG" ] && SMOKE_FLAG="false"
N=${#TAGS[@]}
echo "  Trials (${N}): ${TAGS[*]}"

SWEEP_SMOKE=0
if [ "$SMOKE_FLAG" = "true" ]; then
    SWEEP_SMOKE=1
    echo "  Mode: SMOKE (--sample on 04D only; downstream uses trial data_dir + outputs_step3 ref data)"
fi

# ── Build colon-separated TRIAL_TAGS for array job ───────────────────────────
TRIAL_TAGS_STR=$(IFS=':'; echo "${TAGS[*]}")

# ── Submit 04D array job ──────────────────────────────────────────────────────
JID_D=$(sbatch --parsable --array=0-$((N-1)) --export=ALL,TRIAL_TAGS="$TRIAL_TAGS_STR",SWEEP_SMOKE="$SWEEP_SMOKE" "${SCRIPT_DIR}/job_04D_train_array.sh")
echo "  04D array submitted: $JID_D (array 0-$((N-1)))"

# ── Chain 04E/F/H/I/J + extract_metrics per trial ────────────────────────────
for i in "${!TAGS[@]}"; do
    TAG="${TAGS[$i]}"
    OUT_DIR="outputs_step4_${TAG}"
    CKPT="${OUT_DIR}/checkpoints/best_model.pt"

    # Use the trial's own data_dir (from its YAML) so 04E feature dims match 04D training.
    # Falls back to outputs_step4 if data_dir is not set in the YAML.
    TRIAL_DATA_DIR=$(grep '^data_dir:' "$BASE/configs/${TAG}.yaml" 2>/dev/null | sed 's/^data_dir:[[:space:]]*//')
    [ -z "$TRIAL_DATA_DIR" ] && TRIAL_DATA_DIR="outputs_step4"

    JID_E=$(sbatch --parsable --dependency=afterok:${JID_D}_${i} --partition=pg --gres=gpu:1 --mem=48Gb --time=04:00:00 --job-name=04E_${TAG} --output="logs/04E_${TAG}_%j.out" --error="logs/04E_${TAG}_%j.err" --export=ALL --wrap="cd $BASE && . /encs/pkg/modules-5.3.1/root/init/bash && module load cuda/12.8 && $PYTHON -u 04E_inference.py --data_dir ${TRIAL_DATA_DIR} --checkpoint $CKPT --output ${OUT_DIR}/augmented_diaries.csv --temperature 0.8")
    echo "  04E_${TAG}: $JID_E (afterok:${JID_D}_${i})"

    JID_F=$(sbatch --parsable --dependency=afterok:${JID_E} --partition=ps --mem=48G --time=02:00:00 --job-name=04F_${TAG} --output="logs/04F_${TAG}_%j.out" --error="logs/04F_${TAG}_%j.err" --wrap="cd $BASE && $PYTHON -u 04F_validation.py --step3_dir outputs_step3 --step4_dir ${OUT_DIR}")
    echo "  04F_${TAG}: $JID_F (afterok:${JID_E})"

    JID_H=$(sbatch --parsable --dependency=afterok:${JID_E} --partition=ps --mem=8G --cpus-per-task=4 --time=00:30:00 --job-name=04H_${TAG} --output="logs/04H_${TAG}_%j.out" --error="logs/04H_${TAG}_%j.err" --wrap="cd $BASE && $PYTHON -u 04H_diagnostics_cpu.py --data_dir ${OUT_DIR} --step3_dir outputs_step3 --output_json ${OUT_DIR}/diagnostics_v4.json")
    echo "  04H_${TAG}: $JID_H (afterok:${JID_E})"

    JID_I=$(sbatch --parsable --dependency=afterok:${JID_E} --partition=ps --mem=8G --cpus-per-task=4 --time=00:30:00 --job-name=04I_${TAG} --output="logs/04I_${TAG}_%j.out" --error="logs/04I_${TAG}_%j.err" --wrap="cd $BASE && $PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir ${OUT_DIR} --step3_dir outputs_step3 --output_json ${OUT_DIR}/diagnostics_actcop.json")
    echo "  04I_${TAG}: $JID_I (afterok:${JID_E})"

    JID_J=$(sbatch --parsable --dependency=afterok:${JID_E} --partition=ps --mem=8G --cpus-per-task=4 --time=00:30:00 --job-name=04J_${TAG} --output="logs/04J_${TAG}_%j.out" --error="logs/04J_${TAG}_%j.err" --wrap="cd $BASE && $PYTHON -u 04J_statistical_diagnostics.py --data_dir ${OUT_DIR} --step3_dir outputs_step3 --output_json ${OUT_DIR}/diagnostics_v4_statistical.json --n_bootstrap 1000")
    echo "  04J_${TAG}: $JID_J (afterok:${JID_E})"

    JID_X=$(sbatch --parsable --dependency=afterok:${JID_J} --partition=ps --mem=4G --time=00:10:00 --job-name=extract_${TAG} --output="logs/extract_${TAG}_%j.out" --error="logs/extract_${TAG}_%j.err" --wrap="cd $BASE && $PYTHON -u Speed_Cluster/extract_metrics.py ${OUT_DIR}/diagnostics_v4_statistical.json ${TAG} results_index/results.csv results_index/${TAG}/")
    echo "  extract_${TAG}: $JID_X (afterok:${JID_J})"
done

echo ""
echo "============================================================"
echo "Sweep submitted — chain: $CHAIN_TAG"
echo "Monitor:  squeue -u \$USER"
echo "Results:  cat $BASE/results_index/results.csv"
echo "Gates (per arm): composite < 1.045 | AT_HOME <= +5.3 pp | Spouse <= +10 pp | act_JS <= 0.05"
echo "============================================================"
