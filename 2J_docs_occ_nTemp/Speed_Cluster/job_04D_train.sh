#!/encs/bin/bash
#SBATCH --job-name=04D_train
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=2-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04D_train_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04D_train_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

cd /speed-scratch/o_iseri/occModeling
/speed-scratch/o_iseri/envs/step4/bin/python 04D_train.py \
    --fp16
