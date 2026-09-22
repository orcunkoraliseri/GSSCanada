#!/bin/bash
#SBATCH --job-name=wp11_draw_task
#SBATCH --account=chachemv
#SBATCH -p ps
#SBATCH -c 5
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/1J_rerun/logs/wp11_draw_%A_%a.out

# WP11 item 4: one draw-block array task. Maps SLURM_ARRAY_TASK_ID to (block,
# neighbourhood) from ARRAY_KIND (LIGHT or HEAVY, set with --export at submission),
# runs 5 draws (WP11_DRAW_START=D, --iter-count 5 --workers 5) for that neighbourhood,
# then extracts+verifies (wp11_extract.py). NOT submitted by this task's employee --
# the manager submits the arrays after reading Gate 4 PASS, workers-check PASS and the
# swap probe PASS.
#
# Submission (manager, not hardcoded here):
#   sbatch --array=0-23%2 --mem=<from workers-check MaxRSS> --export=ARRAY_KIND=LIGHT  wp11_draw_task.sh
#   sbatch --array=0-11%4 --mem=<from workers-check MaxRSS> --export=ARRAY_KIND=HEAVY  wp11_draw_task.sh
# --mem is deliberately NOT hardcoded (task doc item 4: "given by the manager at submission").
#
# Task doc: 1J_docs_occ/IMP/impl/2026-09-22_WP11_stage4d_draws.md, item 4.

CODE=/speed-scratch/o_iseri/1J_rerun/code
WP11=/speed-scratch/o_iseri/1J_rerun/stage4/wp11
VENV=/speed-scratch/o_iseri/GSSCanada/venv
EP_DIR=/speed-scratch/o_iseri/EnergyPlus/EnergyPlus-24.2.0-94a887817b-Linux-CentOS7.9.2009-x86_64
DRAWS_ROOT=/speed-scratch/o_iseri/1J_rerun/stage4/draws

if [ -z "$ARRAY_KIND" ]; then
  echo "ERROR: ARRAY_KIND env var not set (must be LIGHT or HEAVY) -- stopping."
  exit 2
fi
if [ -z "$SLURM_ARRAY_TASK_ID" ]; then
  echo "ERROR: SLURM_ARRAY_TASK_ID not set -- this script must be run as a Slurm array task."
  exit 2
fi

I=$SLURM_ARRAY_TASK_ID

if [ "$ARRAY_KIND" = "LIGHT" ]; then
  # LIGHT = RC1-RC4, 24 tasks (6 blocks x 4 neighbourhoods): task i -> block i//4+1, RC(i%4+1)
  BLOCK=$(( I / 4 + 1 ))
  RC_NUM=$(( I % 4 + 1 ))
  NU="NUS_RC${RC_NUM}"
elif [ "$ARRAY_KIND" = "HEAVY" ]; then
  # HEAVY = RC5-RC6, 12 tasks (6 blocks x 2 neighbourhoods): task i -> block i//2+1, RC5 if i even else RC6
  BLOCK=$(( I / 2 + 1 ))
  if [ $(( I % 2 )) -eq 0 ]; then
    NU="NUS_RC5"
  else
    NU="NUS_RC6"
  fi
else
  echo "ERROR: ARRAY_KIND must be LIGHT or HEAVY, got '$ARRAY_KIND'"
  exit 2
fi

D=$(( 5 * (BLOCK - 1) + 1 ))
BLOCK_DIR="${DRAWS_ROOT}/block_${BLOCK}"
LOG_PATH="/speed-scratch/o_iseri/1J_rerun/logs/wp11_draw_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.out"

echo "=== WP11 draw task: ARRAY_KIND=$ARRAY_KIND task_id=$I -> block=$BLOCK nu=$NU draw_start=$D ==="
echo "Block dir: $BLOCK_DIR"
echo "Own log  : $LOG_PATH"

source "$VENV/bin/activate"
export ENERGYPLUS_DIR="$EP_DIR"

echo "=== Pre-flight: disk quota check for /speed-scratch (need >= 400 G free) ==="
mkdir -p "$WP11/logs"
QUOTA_FILE="$WP11/logs/quota_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.txt"
quota -s > "$QUOTA_FILE" 2>&1
cat "$QUOTA_FILE"
QUOTA_PARSED=$(python "$WP11/wp11_quota_check.py" "$QUOTA_FILE")
echo "$QUOTA_PARSED"
FREE_GB=$(echo "$QUOTA_PARSED" | grep -oE 'FREE_GB=[0-9.]+' | cut -d= -f2)
if [ -z "$FREE_GB" ]; then
  echo "WP11 PREFLIGHT DISK: FAIL -- could not parse quota -s output ($QUOTA_PARSED)"
  exit 3
fi
FREE_OK=$(python -c "print(1 if float(\"$FREE_GB\") >= 400.0 else 0)")
if [ "$FREE_OK" != "1" ]; then
  echo "WP11 PREFLIGHT DISK: FAIL -- free=${FREE_GB} G < 400 G"
  exit 3
fi
echo "WP11 PREFLIGHT DISK: PASS -- free=${FREE_GB} G >= 400 G"

echo "=== Pre-flight: md5 dedupe check on staged schedule CSVs (copied from wp10_stage4_default_RC6.sh) ==="
M2005=$(md5sum "$CODE/BEM_Setup/BEM_Schedules_2005.csv" | awk '{print $1}')
M2010=$(md5sum "$CODE/BEM_Setup/BEM_Schedules_2010.csv" | awk '{print $1}')
M2015=$(md5sum "$CODE/BEM_Setup/BEM_Schedules_2015.csv" | awk '{print $1}')
M2022=$(md5sum "$CODE/BEM_Setup/BEM_Schedules_2022.csv" | awk '{print $1}')
M2025=$(md5sum "$CODE/BEM_Setup/BEM_Schedules_2025.csv" | awk '{print $1}')
echo "2005=$M2005"
echo "2010=$M2010"
echo "2015=$M2015"
echo "2022=$M2022"
echo "2025=$M2025"

DUP=0
if [ "$M2005" = "$M2010" ] || [ "$M2005" = "$M2015" ] || [ "$M2005" = "$M2022" ] || [ "$M2005" = "$M2025" ] || \
   [ "$M2010" = "$M2015" ] || [ "$M2010" = "$M2022" ] || [ "$M2010" = "$M2025" ] || \
   [ "$M2015" = "$M2022" ] || [ "$M2015" = "$M2025" ] || \
   [ "$M2022" = "$M2025" ]; then
  DUP=1
fi
if [ "$DUP" -eq 1 ]; then
  echo "ERROR: two staged schedule CSVs share an md5 -- stopping before run."
  exit 3
fi
echo "Dedupe check OK: all five schedule CSV md5 distinct."

echo "=== Running run_batch_hpc.py $NU, draws $D..$((D+4)) (WP11_DRAW_START=$D, --iter-count 5 --workers 5) ==="
mkdir -p "$BLOCK_DIR"
export WP11_DRAW_START=$D
python "$CODE/eSim_bem_utils/run_batch_hpc.py" \
    --idf        "$CODE/BEM_Setup/Neighbourhoods/${NU}.idf" \
    --region     Quebec \
    --sim-mode   standard \
    --iter-count 5 \
    --output-dir "$BLOCK_DIR" \
    --workers    5

RUNNER_EXIT=$?
echo "RUNNER EXIT: $RUNNER_EXIT (1 = known plotting crash, seen at Gate 3/R7/Stage 4c -- never read success from this code)"

echo "=== Task dir size BEFORE extraction/cleanup ==="
du -sh "${BLOCK_DIR}/${NU}" 2>&1 || echo "du failed (dir may not exist)"

echo "=== Extracting + verifying (E1-E5); cleanup (delete .eso, gzip .sql) runs inside wp11_extract.py only on VERIFIED ==="
python "$WP11/wp11_extract.py" --mode real \
    --nu "$NU" --task-dir "$BLOCK_DIR" --draw-start "$D" --n-draws 5 --log "$LOG_PATH"
EXTRACT_EXIT=$?

echo "=== Task dir size AFTER extraction/cleanup ==="
du -sh "${BLOCK_DIR}/${NU}" 2>&1 || echo "du failed"

echo "Done: WP11 draw task ARRAY_KIND=$ARRAY_KIND task_id=$I block=$BLOCK nu=$NU draw_start=$D (extract exit code: $EXTRACT_EXIT)"
exit $EXTRACT_EXIT
