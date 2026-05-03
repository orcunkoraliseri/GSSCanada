#!/encs/bin/bash
#SBATCH --job-name=diag_H_Tanh_vs_G4
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/diag_H_Tanh_vs_G4_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/diag_H_Tanh_vs_G4_%j.err

# H-Tier-1.5: inference-only logit/loss diagnostic — runs G4 then H_Tanh sequentially.
# Wall-time: 1h (two ~15-min forward passes on a V100; not a 2-day training slot).
# Spec: step4_training_v2.md §H-Tier-1.5

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
DIAG_SCRIPT="$BASE/Speed-Cluster_docs/diagnostic_H_Tanh_vs_G4.py"
OUT_DIR="$BASE/diagnostics_H_Tanh_vs_G4"
DATA_DIR="$BASE/outputs_step4_G1"

mkdir -p "$BASE/logs" "$OUT_DIR"

echo "============================================================"
echo "H-Tier-1.5 diagnostic: G4 vs H_Tanh logit/loss dump"
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
echo "Verify (8 files expected):"
ls -lh "$OUT_DIR"
echo "DIAG DONE"
echo "============================================================"
