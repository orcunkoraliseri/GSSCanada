#!/bin/bash
#SBATCH --job-name=s8_heavy
#SBATCH --partition=ps
#SBATCH --nodes=1
#SBATCH --mem=16G
#SBATCH --cpus-per-task=8
#SBATCH --time=48:00:00
#SBATCH --array=0-11
#SBATCH --output=/speed-scratch/o_iseri/step8_speed/logs/s8_%A_%a.out
#SBATCH --error=/speed-scratch/o_iseri/step8_speed/logs/s8_%A_%a.err

# Step 8 heavy-cell SLURM array — 12 tasks (MidRise×6 + HighRise×6).
# Each task: N=50 HH × 5 years = 250 paired EnergyPlus runs for one cell.
# Schedule injection + hourly-meter extraction via host Python (step4 env).
# EnergyPlus 24.2 invoked via nrel/energyplus SIF (validated in Step 9 spike).
# Do NOT run on the login node; submit with sbatch only.

. /encs/pkg/modules-5.3.1/root/init/bash
module load singularity/3.10.4

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
EP_BIN=/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
DRIVER=$GCMAIN/2J_docs_occ_nTemp/Step8_docs/run_paired_mc.py
OUT_ROOT=/speed-scratch/o_iseri/step8_speed/campaign_N50
LOG_DIR=/speed-scratch/o_iseri/step8_speed/logs

# 12-cell lookup: tasks 0-5 = MidRise x 6 cities, tasks 6-11 = HighRise x 6 cities
ARCHS=(MidRise MidRise MidRise MidRise MidRise MidRise HighRise HighRise HighRise HighRise HighRise HighRise)
CITIES=(Toronto_5A Kelowna_5B Vancouver_5C Montreal_6A Calgary_6B Winnipeg_7A Toronto_5A Kelowna_5B Vancouver_5C Montreal_6A Calgary_6B Winnipeg_7A)

ARCH=${ARCHS[$SLURM_ARRAY_TASK_ID]}
CITY=${CITIES[$SLURM_ARRAY_TASK_ID]}
CELL="${ARCH}__${CITY}"
OUT_DIR=$OUT_ROOT/$CELL

echo "=== Step 8 heavy array | job=${SLURM_ARRAY_JOB_ID} task=${SLURM_ARRAY_TASK_ID} | cell=$CELL ==="
echo "Node: $(hostname)  Date: $(date)"
mkdir -p $OUT_DIR $LOG_DIR

# --- Idempotent skip: 250 hourly_meters.csv = one per (sample x year) ---
NHOURLY=$(find $OUT_DIR -name hourly_meters.csv 2>/dev/null | wc -l)
if [ "$NHOURLY" -ge 250 ]; then
    echo "  Already complete ($NHOURLY/250 hourly_meters.csv) — skipping."
    exit 0
fi
echo "  Found $NHOURLY/250 hourly_meters.csv — running."

# --- Build per-task E+ wrapper dir on /speed-scratch ---
EP_WRAPPER=/speed-scratch/o_iseri/step8_speed/.ep_wrapper_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}
mkdir -p $EP_WRAPPER

# Extract Energy+.idd from SIF (needed by eppy and by simulation.py copy-to-rundir)
singularity exec --bind /speed-scratch $SIF cat ${EP_BIN}/Energy+.idd > $EP_WRAPPER/Energy+.idd
echo "  IDD extracted: $(wc -c < $EP_WRAPPER/Energy+.idd) bytes"

# energyplus wrapper: delegates to SIF, preserves CWD and all args
cat > $EP_WRAPPER/energyplus << 'EPEOF'
#!/bin/bash
exec singularity exec --bind /speed-scratch --pwd "$PWD" /speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif /EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus "$@"
EPEOF

# ExpandObjects wrapper: delegates to SIF, inherits CWD (reads in.idf from cwd)
cat > $EP_WRAPPER/ExpandObjects << 'EOEOF'
#!/bin/bash
exec singularity exec --bind /speed-scratch --pwd "$PWD" /speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif /EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/ExpandObjects
EOEOF

chmod +x $EP_WRAPPER/energyplus $EP_WRAPPER/ExpandObjects
echo "  Wrapper dir ready: $(ls $EP_WRAPPER | tr '\n' ' ')"

# --- Python dep precheck (fail fast before spending walltime) ---
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
    echo "ERROR: missing Python deps — abort task $SLURM_ARRAY_TASK_ID ($CELL)"
    rm -rf $EP_WRAPPER
    exit 1
fi

# --- Data file check ---
echo "--- Data file check ---"
MISS=0
for F in $GCMAIN/BEM_Setup/BEM_Schedules_2005.csv $GCMAIN/BEM_Setup/BEM_Schedules_2010.csv $GCMAIN/BEM_Setup/BEM_Schedules_2015.csv $GCMAIN/BEM_Setup/BEM_Schedules_2022.csv $GCMAIN/BEM_Setup/BEM_Schedules_2030.csv $GCMAIN/2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/ASHRAE901_ApartmentMidRise_STD2022_Buffalo_NECB17_Z6_v242.idf $GCMAIN/2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/ASHRAE901_ApartmentHighRise_STD2022_Buffalo_NECB17_Z6_v242.idf $DRIVER $SIF; do
    if [ -f "$F" ]; then echo "  OK $F"
    else echo "  MISS $F"; MISS=1; fi
done
if [ $MISS -ne 0 ]; then
    echo "ERROR: missing data files — abort task $SLURM_ARRAY_TASK_ID ($CELL)"
    rm -rf $EP_WRAPPER
    exit 1
fi
echo "Data files OK"

# --- Run paired MC (host Python, E+ via wrapper) ---
echo "--- run_paired_mc.py: $CELL ---"
export ENERGYPLUS_DIR=$EP_WRAPPER
export IDD_FILE=$EP_WRAPPER/Energy+.idd
export ESIM_WORKERS=8
export MPLBACKEND=Agg

$PYTHON $DRIVER --archetype $ARCH --city $CITY --n 50 --seed 42 --sim-mode standard --output-dir $OUT_DIR
RC=$?

NHOURLY_DONE=$(find $OUT_DIR -name hourly_meters.csv | wc -l)
echo "  run_paired_mc.py exit=$RC  hourly_meters.csv=$NHOURLY_DONE/250"

rm -rf $EP_WRAPPER

if [ $RC -ne 0 ]; then
    echo "FAIL: non-zero exit ($RC) for task $SLURM_ARRAY_TASK_ID ($CELL)"
    exit 1
fi

echo "=== Task $SLURM_ARRAY_TASK_ID COMPLETE: $CELL | $NHOURLY_DONE hourly files ==="
