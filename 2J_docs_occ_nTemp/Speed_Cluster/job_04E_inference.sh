#!/encs/bin/bash
#SBATCH --job-name=04E_infer
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=48G
#SBATCH --time=04:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04E_infer_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04E_infer_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

cd /speed-scratch/o_iseri/occModeling
/speed-scratch/o_iseri/envs/step4/bin/python -u 04E_inference.py \
    --data_dir outputs_step4 \
    --checkpoint outputs_step4/checkpoints/best_model.pt \
    --output outputs_step4/augmented_diaries.csv \
    --temperature 0.8
