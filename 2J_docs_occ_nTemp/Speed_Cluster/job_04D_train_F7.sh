#!/encs/bin/bash
#SBATCH --job-name=04D_F7
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40Gb
#SBATCH --time=2-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04D_F7_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04D_F7_%j.err

# F7: F6 (F3-C + COP_POS_WEIGHT=0 + fp32) with warmup-gate fix.
#     F6 trap: epoch-1 near-uniform predictions scored deceptively low on
#     val_JS (0.1844) during warmup → saved as best → patience exhausted at
#     epoch 16 against a near-random checkpoint.
#     Fix: best-model saving and patience counter now gated on past_warmup.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

cd /speed-scratch/o_iseri/occModeling
mkdir -p logs outputs_step4_F7/checkpoints

export COP_POS_WEIGHT=0
export ACTIVITY_BOOSTS=0
export MARG_MODE=per_cs
export AUX_STRATUM_HEAD=1

/speed-scratch/o_iseri/envs/step4/bin/python -u 04D_train.py \
    --data_dir    outputs_step4 \
    --output_dir  outputs_step4_F7 \
    --checkpoint_dir outputs_step4_F7/checkpoints
