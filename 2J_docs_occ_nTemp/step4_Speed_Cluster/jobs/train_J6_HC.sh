#!/encs/bin/bash
#SBATCH --job-name=J6_HC
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=48G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J6_HC_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J6_HC_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

mkdir -p "$BASE/logs"
mkdir -p "$BASE/outputs_step4_J6_HC/checkpoints"

export MODEL_TYPE=J6
export ENABLE_HIERARCHICAL_COP=1
export ENABLE_HH_COP_COND=0
export LAMBDA_ACT=1.0
export LAMBDA_HOME=0.7
export LAMBDA_COP=0.3
export LAMBDA_MARG=0.1
export SPOUSE_NEG_WEIGHT=0.45
export HOME_LABEL_SMOOTH=0.05
export SCHED_SAMPLE_P=0.0
export DROPOUT=0.1

echo "============================================================"
echo "J6-HC: J3 trunk + hierarchical COP only (ENABLE_HIERARCHICAL_COP=1)"
echo "============================================================"

$PYTHON -u 04D_train.py --data_dir "$BASE/outputs_step4_G1" --output_dir "$BASE/outputs_step4_J6_HC" --checkpoint_dir "$BASE/outputs_step4_J6_HC/checkpoints" --batch_size 256 --max_epochs 100 --patience 15 --lr 5e-5 --d_model 384 --n_heads 8 --n_enc_layers 6 --n_dec_layers 6

echo "============================================================"
echo "J6_HC TRAINING COMPLETE"
echo "============================================================"
