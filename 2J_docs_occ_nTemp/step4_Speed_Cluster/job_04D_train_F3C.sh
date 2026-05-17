#!/encs/bin/bash
#SBATCH --job-name=04D_F3C
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40Gb
#SBATCH --time=2-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04D_F3C_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04D_F3C_%j.err

# F3-C: F3-B + auxiliary stratum-prediction MLP head on decoder layer-0 hidden
# Delta vs F3-B: AUX_STRATUM_HEAD=1

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

cd /speed-scratch/o_iseri/occModeling
mkdir -p logs outputs_step4_F3C/checkpoints

export COP_POS_WEIGHT=1
export ACTIVITY_BOOSTS=0
export MARG_MODE=per_cs
export AUX_STRATUM_HEAD=1

/speed-scratch/o_iseri/envs/step4/bin/python -u 04D_train.py \
    --data_dir    outputs_step4 \
    --output_dir  outputs_step4_F3C \
    --checkpoint_dir outputs_step4_F3C/checkpoints \
    --fp16
