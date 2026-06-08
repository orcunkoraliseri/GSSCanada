#!/bin/bash
#SBATCH --job-name=s8_r2d
#SBATCH --partition=ps
#SBATCH --nodes=1
#SBATCH --mem=16G
#SBATCH --cpus-per-task=8
#SBATCH --time=48:00:00
#SBATCH --array=0-6
#SBATCH --output=/speed-scratch/o_iseri/step8_r2d/logs/r2d_%A_%a.out
#SBATCH --error=/speed-scratch/o_iseri/step8_r2d/logs/r2d_%A_%a.err

# Step 8 Round-2d spot-check: 7 borderline cell*year re-sims with DISK schedules.
# Purpose: measure actual mean-EUI shift vs 1.80% MC CI for cells near the threshold.
# Each task: N=50 HH x 1 year = 50 EnergyPlus runs (disk BEM_Schedules_{year}.csv).
# Produces /speed-scratch/o_iseri/step8_r2d/<cell>/ with eplustbl.csv per run.
# Do NOT run on the login node; submit with sbatch only.

. /encs/pkg/modules-5.3.1/root/init/bash
module load singularity/3.10.4

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
EP_BIN=/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
DRIVER=$GCMAIN/2J_docs_occ_nTemp/Step8_docs/run_paired_mc.py
OUT_ROOT=/speed-scratch/o_iseri/step8_r2d
LOG_DIR=$OUT_ROOT/logs

# 7 borderline cell*year tasks (Step 1 r2d_analysis.py selection)
# Format: ARCH  CITY  YEAR
ARCHS=(HighRise      HighRise      HighRise      HighRise      OtherDwelling SingleD       SingleD)
CITIES=(Calgary_6B   Calgary_6B    Toronto_5A    Toronto_5A    Toronto_5A    Toronto_5A    Toronto_5A)
YEARS=(2022          2030          2022          2030          2022          2022          2030)

ARCH=${ARCHS[$SLURM_ARRAY_TASK_ID]}
CITY=${CITIES[$SLURM_ARRAY_TASK_ID]}
YEAR=${YEARS[$SLURM_ARRAY_TASK_ID]}
CELL="${ARCH}__${CITY}"
OUT_DIR=$OUT_ROOT/$CELL

echo "=== Step 8 R2d spot-check | job=${SLURM_ARRAY_JOB_ID} task=${SLURM_ARRAY_TASK_ID} | cell=$CELL year=$YEAR ==="
echo "Node: $(hostname)  Date: $(date)"
mkdir -p $OUT_DIR $LOG_DIR

# --- Idempotent skip: 50 eplustbl.csv = 50 HH x 1 year ---
NEPTBL=$(find $OUT_DIR -path "*/$YEAR/eplustbl.csv" 2>/dev/null | wc -l)
if [ "$NEPTBL" -ge 50 ]; then
    echo "  Already complete ($NEPTBL/50 eplustbl.csv for $YEAR) — skipping."
    exit 0
fi
echo "  Found $NEPTBL/50 eplustbl.csv for $YEAR — running."

# --- Build per-task E+ wrapper dir on /speed-scratch ---
EP_WRAPPER=/speed-scratch/o_iseri/step8_r2d/.ep_wrapper_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}
mkdir -p $EP_WRAPPER

singularity exec --bind /speed-scratch $SIF cat ${EP_BIN}/Energy+.idd > $EP_WRAPPER/Energy+.idd
echo "  IDD extracted: $(wc -c < $EP_WRAPPER/Energy+.idd) bytes"

cat > $EP_WRAPPER/energyplus << 'EPEOF'
#!/bin/bash
exec singularity exec --bind /speed-scratch --pwd "$PWD" /speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif /EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus "$@"
EPEOF

cat > $EP_WRAPPER/ExpandObjects << 'EOEOF'
#!/bin/bash
exec singularity exec --bind /speed-scratch --pwd "$PWD" /speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif /EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/ExpandObjects
EOEOF

chmod +x $EP_WRAPPER/energyplus $EP_WRAPPER/ExpandObjects
echo "  Wrapper dir ready: $(ls $EP_WRAPPER | tr '\n' ' ')"

# --- Dep precheck ---
echo "--- Dep precheck ---"
$PYTHON -c "
import sys
fail = []
for p in ['numpy','pandas','eppy','matplotlib','scipy']:
    try: __import__(p); print('  OK',p)
    except ImportError as e: print('  FAIL',p,e); fail.append(p)
if fail: print('MISSING:',fail); sys.exit(1)
print('All deps OK')
"
if [ $? -ne 0 ]; then
    echo "ERROR: missing Python deps — abort task $SLURM_ARRAY_TASK_ID ($CELL/$YEAR)"
    rm -rf $EP_WRAPPER
    exit 1
fi

# --- Data file check ---
echo "--- Data file check ---"
MISS=0
for F in \
    $GCMAIN/BEM_Setup/BEM_Schedules_${YEAR}.csv \
    $GCMAIN/2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/ASHRAE901_ApartmentHighRise_STD2022_Buffalo_NECB17_Z6_v242.idf \
    $GCMAIN/2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf \
    $GCMAIN/2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/AttachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf \
    $DRIVER $SIF; do
    if [ -f "$F" ]; then echo "  OK $F"
    else echo "  MISS $F"; MISS=1; fi
done
if [ $MISS -ne 0 ]; then
    echo "ERROR: missing data files — abort"
    rm -rf $EP_WRAPPER
    exit 1
fi
echo "Data files OK"

# --- Run spot-check (disk schedules, 1 year only) ---
echo "--- run_paired_mc.py: $CELL year=$YEAR ---"
export ENERGYPLUS_DIR=$EP_WRAPPER
export IDD_FILE=$EP_WRAPPER/Energy+.idd
export ESIM_WORKERS=8
export MPLBACKEND=Agg

$PYTHON $DRIVER --archetype $ARCH --city $CITY --n 50 --seed 42 --sim-mode standard --years $YEAR --output-dir $OUT_DIR
RC=$?

NEPTBL_DONE=$(find $OUT_DIR -path "*/$YEAR/eplustbl.csv" | wc -l)
echo "  run_paired_mc.py exit=$RC  eplustbl.csv=$NEPTBL_DONE/50"

rm -rf $EP_WRAPPER

if [ $RC -ne 0 ]; then
    echo "FAIL: non-zero exit ($RC) for task $SLURM_ARRAY_TASK_ID ($CELL/$YEAR)"
    exit 1
fi

echo "=== Task $SLURM_ARRAY_TASK_ID COMPLETE: $CELL/$YEAR | $NEPTBL_DONE eplustbl files ==="
