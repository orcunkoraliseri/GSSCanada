#!/encs/bin/bash
#SBATCH --job-name=04D_F6
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40Gb
#SBATCH --time=2-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04D_F6_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04D_F6_%j.err

# F6: F5 (F3-C + COP_POS_WEIGHT=0) with fp16 removed.
#     F5 had 1 NaN gradient at epoch 1 → GradScaler skipped optimizer step →
#     random-weight checkpoint saved as best (same trap as F4).
#     fp32 eliminates FP16 overflow as a failure mode.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

cd /speed-scratch/o_iseri/occModeling
mkdir -p logs outputs_step4_F6/checkpoints

export COP_POS_WEIGHT=0
export ACTIVITY_BOOSTS=0
export MARG_MODE=per_cs
export AUX_STRATUM_HEAD=1

/speed-scratch/o_iseri/envs/step4/bin/python -u 04D_train.py \
    --data_dir    outputs_step4 \
    --output_dir  outputs_step4_F6 \
    --checkpoint_dir outputs_step4_F6/checkpoints
