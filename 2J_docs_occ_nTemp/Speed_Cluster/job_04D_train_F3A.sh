#!/encs/bin/bash
#SBATCH --job-name=04D_F3A
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=2-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04D_F3A_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04D_F3A_%j.err

# F3-A: class-balanced pos_weight on co-presence BCE + remove manual activity boosts
# Delta vs F1: COP_POS_WEIGHT=1 + ACTIVITY_BOOSTS=0

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

cd /speed-scratch/o_iseri/occModeling
mkdir -p logs outputs_step4_F3A/checkpoints

export COP_POS_WEIGHT=1
export ACTIVITY_BOOSTS=0

/speed-scratch/o_iseri/envs/step4/bin/python -u 04D_train.py \
    --data_dir    outputs_step4 \
    --output_dir  outputs_step4_F3A \
    --checkpoint_dir outputs_step4_F3A/checkpoints \
    --fp16
