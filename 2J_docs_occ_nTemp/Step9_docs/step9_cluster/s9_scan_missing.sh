#!/encs/bin/bash
#SBATCH --job-name=s9_scan
#SBATCH --partition=ps
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_scan_%j.out

ROOT=/speed-scratch/o_iseri/step9_run
echo "=== Missing hourly_meters.csv audit | job=${SLURM_JOB_ID} ==="
echo "Date: $(date)"
echo ""
echo "--- HighRise__Winnipeg_7A/activity (task 47 scope) ---"
for d in $ROOT/idfs/HighRise__Winnipeg_7A/activity/sample_*/*/; do
    if [ ! -f "${d}hourly_meters.csv" ]; then echo "MISSING: $d"; fi
done
echo ""
echo "--- ALL cells: complete missing list ---"
for d in $ROOT/idfs/*/*/sample_*/*/; do
    if [ ! -f "${d}hourly_meters.csv" ]; then echo "MISSING_ALL: $d"; fi
done
echo ""
echo "=== SCAN DONE: $(date) ==="
