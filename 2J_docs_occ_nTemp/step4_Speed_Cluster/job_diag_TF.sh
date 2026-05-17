#!/encs/bin/bash
#SBATCH --job-name=diag_TF
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/diag_TF_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/diag_TF_%j.err

# H-Tier-1.6: AR-cascade falsification diagnostic — runs G4 then H_Tanh sequentially.
# Three inference modes (A=AR, B=teacher-forced, C=oracle-home) × 2 checkpoints = 6 rows.
# Wall-time: 1h (6 forward passes over val set, no training).
# Spec: DONE_step4_training_v2.md §H-Tier-1.6

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
DIAG_SCRIPT="$BASE/Speed-Cluster_docs/diag_teacher_forcing.py"
OUT_DIR="$BASE/diagnostics_tier_1_6"
DATA_DIR="$BASE/outputs_step4_G1"

mkdir -p "$BASE/logs" "$OUT_DIR"
rm -f "$OUT_DIR/tier_1_6_results.csv"   # ensure clean 6-row CSV on requeue

echo "============================================================"
echo "H-Tier-1.6 diagnostic: AR-cascade falsification (TF + oracle-home)"
echo "Output dir: $OUT_DIR"
echo "============================================================"

# ── Run G4 (plain Linear heads, H_TANH_HEADS=0) ──────────────────────────────
echo ""
echo "--- G4 pass (tanh_heads=0) ---"
$PYTHON -u "$DIAG_SCRIPT" \
    --checkpoint "$BASE/outputs_step4_G4/checkpoints/best_model.pt" \
    --data_dir   "$DATA_DIR" \
    --output_dir "$OUT_DIR" \
    --tag        G4 \
    --tanh_heads 0
echo "--- G4 pass DONE ---"

# ── Run H_Tanh (Tanh-wrapped heads, H_TANH_HEADS=1) ──────────────────────────
echo ""
echo "--- H_Tanh pass (tanh_heads=1) ---"
$PYTHON -u "$DIAG_SCRIPT" \
    --checkpoint "$BASE/outputs_step4_H_Tanh/checkpoints/best_model.pt" \
    --data_dir   "$DATA_DIR" \
    --output_dir "$OUT_DIR" \
    --tag        H_Tanh \
    --tanh_heads 1
echo "--- H_Tanh pass DONE ---"

echo ""
echo "============================================================"
echo "Verify (6 rows expected in tier_1_6_results.csv):"
wc -l "$OUT_DIR/tier_1_6_results.csv"
cat "$OUT_DIR/tier_1_6_results.csv"
echo "DIAG DONE"
echo "============================================================"
