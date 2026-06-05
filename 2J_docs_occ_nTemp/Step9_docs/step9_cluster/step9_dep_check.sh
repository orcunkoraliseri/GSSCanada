#!/encs/bin/bash
#SBATCH --job-name=s9_dep_check
#SBATCH --partition=ps
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/dep_check_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/dep_check_%j.err

# Phase 1: dependency + data-file check for Step 9 cluster run.
# Verifies step4 env has all required packages and that the data files exist.
# Run ONCE before Stage A. Read the log to confirm GO or identify what to install/upload.

. /encs/pkg/modules-5.3.1/root/init/bash

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
ROOT=/speed-scratch/o_iseri/step9_run
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

mkdir -p $ROOT/logs

echo "=== Step 9 dep check START ==="
echo "Node: $(hostname)  Date: $(date)"
echo "Python: $($PYTHON --version 2>&1)"

echo ""
echo "--- Python imports ---"
$PYTHON -c "
import sys
failed = []
for name in ['numpy', 'pandas', 'eppy']:
    try:
        __import__(name)
        print(f'  OK  {name}')
    except ImportError as e:
        print(f'  FAIL {name}: {e}')
        failed.append(name)

# Test eppy version
try:
    import eppy
    print(f'  eppy version: {eppy.__version__}')
except Exception as e:
    print(f'  eppy version check: {e}')

if failed:
    print(f'MISSING packages: {failed}')
    sys.exit(1)
else:
    print('All imports OK')
"
IMPORT_RC=$?

echo ""
echo "--- Data file check ---"
MISSING_FILES=0
check_file() {
    if [ -f "$1" ]; then
        SZ=$(du -sh "$1" | cut -f1)
        echo "  OK   $1  ($SZ)"
    else
        echo "  MISS $1"
        MISSING_FILES=1
    fi
}

check_file "$GCMAIN/0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_excl.csv"
check_file "$GCMAIN/0_Occupancy/Outputs_21CEN22GSS/forecast_2030/2030_synthetic_diaries.csv"
check_file "$GCMAIN/BEM_Setup/BEM_Schedules_2022.csv"
check_file "$GCMAIN/BEM_Setup/BEM_Schedules_2030.csv"
check_file "$GCMAIN/2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf"
check_file "$GCMAIN/2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/ASHRAE901_ApartmentHighRise_STD2022_Buffalo_NECB17_Z6_v242.idf"
check_file "$GCMAIN/2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/ASHRAE901_ApartmentMidRise_STD2022_Buffalo_NECB17_Z6_v242.idf"
check_file "$GCMAIN/BEM_Setup/WeatherFile/CAN_MB_Winnipeg.The.Forks.715790_TMYx_7A.epw"
check_file "$GCMAIN/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw"
check_file "$GCMAIN/BEM_Setup/WeatherFile/CAN_ON_Toronto.City-Univ.of.Toronto.715080_TMYx_5A.epw"
check_file "/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif"
check_file "$GCMAIN/2J_docs_occ_nTemp/activity_loads.py"
check_file "$GCMAIN/2J_docs_occ_nTemp/07_aug_to_bem.py"
check_file "$GCMAIN/2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/integration.py"
check_file "$GCMAIN/2J_docs_occ_nTemp/Step9_docs/step9_cluster/step9_idf_gen.py"

echo ""
if [ $IMPORT_RC -eq 0 ] && [ $MISSING_FILES -eq 0 ]; then
    echo "=== DEP CHECK: ALL PASS — GO for Stage A ==="
else
    echo "=== DEP CHECK: FAIL — resolve missing deps/files before Stage A ==="
    exit 1
fi
