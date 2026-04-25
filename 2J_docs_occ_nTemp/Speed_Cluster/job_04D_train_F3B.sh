#!/encs/bin/bash
#SBATCH --job-name=04D_F3B
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40Gb
#SBATCH --time=2-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04D_F3B_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04D_F3B_%j.err

# F3-B: F3-A + per-(target_cycle x target_stratum) marginal loss
# Delta vs F3-A: MARG_MODE=per_cs

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

cd /speed-scratch/o_iseri/occModeling
mkdir -p logs outputs_step4_F3B/checkpoints

export COP_POS_WEIGHT=1
export ACTIVITY_BOOSTS=0
export MARG_MODE=per_cs

/speed-scratch/o_iseri/envs/step4/bin/python -u 04D_train.py \
    --data_dir    outputs_step4 \
    --output_dir  outputs_step4_F3B \
    --checkpoint_dir outputs_step4_F3B/checkpoints \
    --fp16
