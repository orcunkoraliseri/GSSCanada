#!/encs/bin/bash
#SBATCH --job-name=cop_rescue
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=48G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/cop_rescue_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/cop_rescue_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

mkdir -p "$BASE/logs"

echo "============================================================"
echo "COP Rescue Test -- G4 Inference Modifications"
echo "============================================================"

$PYTHON -u 04E_cop_rescue_test.py --checkpoint "$BASE/outputs_step4_G4/checkpoints/best_model.pt" --data_dir "$BASE/outputs_step4_G1" --subset 5000 --K 10 --output_json "$BASE/outputs_step4_G4/cop_rescue_test.json"

echo "============================================================"
echo "COP RESCUE TEST COMPLETE"
echo "============================================================"
