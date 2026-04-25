#!/encs/bin/bash
#SBATCH --job-name=04D_F5
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40Gb
#SBATCH --time=2-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04D_F5_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04D_F5_%j.err

# F5: F3-C base (aux_stratum_head + per_cs_marg + no activity boosts)
#     + COP_POS_WEIGHT=0: disables ALL cop pos_weights (F4 had large rare-channel
#       weights — parents 40.8x, friends 15.2x, children 11.0x — that caused FP16
#       overflow at epoch 1, NaN gradient, GradScaler skip → random-weight checkpoint).
#       COP_POS_WEIGHT=0 aligns with F1 (composite 1.045, best result to date).

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

cd /speed-scratch/o_iseri/occModeling
mkdir -p logs outputs_step4_F5/checkpoints

export COP_POS_WEIGHT=0
export ACTIVITY_BOOSTS=0
export MARG_MODE=per_cs
export AUX_STRATUM_HEAD=1

/speed-scratch/o_iseri/envs/step4/bin/python -u 04D_train.py \
    --data_dir    outputs_step4 \
    --output_dir  outputs_step4_F5 \
    --checkpoint_dir outputs_step4_F5/checkpoints \
    --fp16
