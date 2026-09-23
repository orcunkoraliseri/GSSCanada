#!/bin/bash
# P10R sibling arm on Speed: ALL 56 cells (array index = cell_index of 3rdJ_08D_campaign_cells.py), 1 CPU each.
# Each task: verify the uploaded mirror md5s, then run ONE cell with 3rdJ_08D_campaign_cell_P10R.py
# (inject [standby floor ON] -> ensure outputs -> D9 -> D10 -> EnergyPlus 24.2.0 SIF -> post-process).
# The runner writes channel_hourly.csv, hourly_meters.csv, dhw_hourly.csv, dhw_volume_hourly.csv,
# hotel_dT_by_type.csv, manifest.json, injected_resized.idf; run/ keeps only eplusout.sql, which
# p10r_slim_sql.py then cuts to the aggregator's tables (~160 MB -> ~1 MB, aggregation byte-identical).
# --nice: histnu and 1J always win a freed CPU; 3J only takes CPUs nobody else is waiting for.
# Throttle (%N) is set by the manager at submission from the live CPU count (histnu never touched).
#SBATCH --job-name=3J_P10R
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-55%26
#SBATCH --nice=10000
#SBATCH --output=/speed-scratch/o_iseri/3J_P10R/logs/p10r_%A_%a.out
ROOT=/speed-scratch/o_iseri/3J_P10R
export REPO=$ROOT/repo
export EPLUS_IDD=$REPO/Energy+.idd
export OMP_NUM_THREADS=1
PY=/speed-scratch/o_iseri/envs/step4/bin/python
echo "P10R task $SLURM_ARRAY_TASK_ID node $(hostname) $(date)"
$PY -u $REPO/3J_docs_occ_nTemp/writing/implementation/IMP/scripts/p10r_verify_mirror.py $REPO || exit 3
cd $REPO/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs || exit 1
$PY -u 3rdJ_08D_campaign_cell_P10R.py --cell $SLURM_ARRAY_TASK_ID --outroot $ROOT/campaign_P10R
RC=$?
if [ $RC -eq 0 ]; then
  CELLDIR=$($PY - <<PYEOF
import json, glob, os
hit = []
for m in glob.glob("$ROOT/campaign_P10R/*/manifest.json"):
    try:
        man = json.load(open(m))
    except Exception:
        continue
    if str(man.get("cell_index", "")) == "$SLURM_ARRAY_TASK_ID" and man.get("P10R_STATUS") == "ok":
        hit.append(os.path.dirname(m))
print(hit[0] if len(hit) == 1 else "")
PYEOF
)
  echo "P10R task $SLURM_ARRAY_TASK_ID cell_dir=$CELLDIR"
  if [ -n "$CELLDIR" ]; then $PY -u $REPO/3J_docs_occ_nTemp/writing/implementation/IMP/scripts/p10r_slim_sql.py $CELLDIR || RC=5; else echo "SLIM_SKIPPED no cell_dir"; RC=6; fi
fi
echo "P10R task $SLURM_ARRAY_TASK_ID exit=$RC $(date)"
exit $RC
