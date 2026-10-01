#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -J s7_bsyntax
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_bsyntax_%j.out
. /speed-scratch/o_iseri/5J/district/code/s7_prelude.sh
for m in s7_draws_gpu s7_wcheck s7_ep_rest s7_spread s7_compare s7_speed; do $PY -c "import $m; print('IMPORT_OK $m')" || echo "IMPORT_FAIL $m"; done
echo "s7_bsyntax end=$(date -Iseconds)"
