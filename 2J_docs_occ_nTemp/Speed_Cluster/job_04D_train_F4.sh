#!/encs/bin/bash
#SBATCH --job-name=04D_F4
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40Gb
#SBATCH --time=2-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04D_F4_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04D_F4_%j.err

# F4: F3-C base (aux_stratum_head + per_cs_marg + no activity boosts + per-channel cop pw)
#     + COP_ALONE_PW=0: disables Alone's pos_weight (freq≈0.35 → pw≈1.86 upweights
#       Alone=1 predictions, worsening the +13.3 pp over-prediction gap in F3-C).
#       All other COP channels retain their computed pos_weights.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

cd /speed-scratch/o_iseri/occModeling
mkdir -p logs outputs_step4_F4/checkpoints

export COP_POS_WEIGHT=1
export COP_ALONE_PW=0
export ACTIVITY_BOOSTS=0
export MARG_MODE=per_cs
export AUX_STRATUM_HEAD=1

/speed-scratch/o_iseri/envs/step4/bin/python -u 04D_train.py \
    --data_dir    outputs_step4 \
    --output_dir  outputs_step4_F4 \
    --checkpoint_dir outputs_step4_F4/checkpoints \
    --fp16
