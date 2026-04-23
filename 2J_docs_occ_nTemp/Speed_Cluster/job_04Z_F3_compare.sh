#!/encs/bin/bash
#SBATCH --job-name=04Z_F3cmp
#SBATCH --partition=ps
#SBATCH --mem=4G
#SBATCH -c 2
#SBATCH --time=00:15:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04Z_F3cmp_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04Z_F3cmp_%j.err

# Reads 4x diagnostics_v4_statistical.json + F1 baseline, emits ranking + HTML
# CHAIN_TAG must be set by the submitting script (--export=ALL,CHAIN_TAG=...)

cd /speed-scratch/o_iseri/occModeling
mkdir -p logs deliveries/F3_sweep/${CHAIN_TAG}

/speed-scratch/o_iseri/envs/step4/bin/python -u 04Z_F3_compare.py \
    --f1_json   outputs_step4/diagnostics_v4_statistical.json \
    --f3a_json  outputs_step4_F3A/diagnostics_v4_statistical.json \
    --f3b_json  outputs_step4_F3B/diagnostics_v4_statistical.json \
    --f3c_json  outputs_step4_F3C/diagnostics_v4_statistical.json \
    --f3d_json  outputs_step4_F3D/diagnostics_v4_statistical.json \
    --out_dir   deliveries/F3_sweep/${CHAIN_TAG}
