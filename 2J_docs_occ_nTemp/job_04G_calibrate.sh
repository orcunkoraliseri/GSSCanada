#!/encs/bin/bash
#SBATCH --job-name=step4G_calib
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH -c 8
#SBATCH --time=0-02:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04G_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04G_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

cd /speed-scratch/o_iseri/occModeling

echo "=== Starting 04G calibration sweep ==="
# Sweeps (temperature x home_threshold) on a stratified subsample.
# Matches 04F metric definitions: §3 |ΔAT_HOME| per (cycle, strata), §4.2 transition ratio.
# Grid: T in {0.5,0.6,0.7,0.8} x θ in {0.50,0.55,0.60,0.65,0.70} -> 20 combos.
/speed-scratch/o_iseri/envs/step4/bin/python -u 04G_calibrate.py \
    --data_dir outputs_step4 \
    --checkpoint outputs_step4/checkpoints/best_model.pt \
    --out_dir outputs_step4/calibration \
    --per_bucket 150

echo "=== 04G Calibration Complete ==="
echo "--- sweep_summary.txt ---"
cat outputs_step4/calibration/sweep_summary.txt
