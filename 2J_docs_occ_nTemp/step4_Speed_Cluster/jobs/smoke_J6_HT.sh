#!/encs/bin/bash
#SBATCH --job-name=smoke_J6_HT
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=16G
#SBATCH --time=00:15:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/smoke_J6_HT_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/smoke_J6_HT_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

export MODEL_TYPE=J6
export ENABLE_HIERARCHICAL_COP=0
export ENABLE_HH_COP_COND=0
export ENABLE_HOME_TEMPORAL=1

echo "=== J6-HT smoke: --sample 10 epochs ==="
$PYTHON -u 04D_train.py --sample --data_dir "$BASE/outputs_step4_G1" --output_dir "$BASE/outputs_step4_J6_HT_smoke" --checkpoint_dir "$BASE/outputs_step4_J6_HT_smoke/checkpoints"

echo "=== SMOKE DONE ==="
