#!/usr/bin/env bash
# 4thJ_run_madrid_stock_campaign.sh
#
# Runs the Madrid (ES-MAD-BERRUGUETE) no-core stock campaign (Step 10 C2) from
# scratch under the CURRENT fixed driver (build_idf_for_cell with the FINDING
# 210/221 vertex-snap fix), then the three Step 11 passes (11.3 trigger, 11.5
# aggregation, 11.6 stockboard) on Madrid's own output, so Madrid's provenance
# matches London (uk) and Bologna (it) exactly.
#
# Evidence for every path, flag, and convention below is in:
#   writing/IMP/PREFLIGHT_madrid_stock_run_2026-09-14.md
# Written for Git Bash on local Windows. POSIX sh only, no bashisms beyond
# arrays (Git Bash's bash supports them).
#
# THIS SCRIPT DOES NOT AUTO-START ANYTHING BY BEING WRITTEN. It must be
# launched deliberately, by a human or an authorised session, with no flag
# (real run) or with --dry-run (prints commands, runs nothing, exits 0).
#
# Usage:
#   bash tools/4thJ_run_madrid_stock_campaign.sh --dry-run   # prints plan only
#   bash tools/4thJ_run_madrid_stock_campaign.sh              # REAL RUN

set -eu
set -o pipefail

DRY_RUN=0
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=1
fi

# ---------------------------------------------------------------------------
# Fixed paths and constants -- mirror the UK/IT local campaigns' OWN
# convention exactly (PREFLIGHT report section 1: rerun_both_fixes.sh and
# _local_runs/4J_IT_local/logs/supervisor.ps1, both read directly).
# ---------------------------------------------------------------------------
GSS_ROOT="C:/Users/o_iseri/Desktop/GSSCanada"
REPO_ROOT="$GSS_ROOT/GSSCanada-main/4J_docs_occ"
PYTHON_EXE="C:/Users/o_iseri/AppData/Local/Programs/Python/Python313/python.exe"

DISTRICT="ES-MAD-BERRUGUETE"
FOLD="es"

CITY_DIR="$GSS_ROOT/_local_runs/4J_ES_local"
OUT_DIR="$CITY_DIR/out/$DISTRICT"
RUN_ROOT="$CITY_DIR/runs/$DISTRICT"
LOG_DIR="$CITY_DIR/logs"

STEP10_TOOL="$REPO_ROOT/tools/4thJ_step10_nocore_campaign.py"
T11_3_TOOL="$REPO_ROOT/tools/4thJ_step11_trigger_campaign.py"
T11_5_TOOL="$REPO_ROOT/tools/4thJ_step11_aggregate.py"
T11_6_TOOL="$REPO_ROOT/tools/4thJ_step11_stockboard.py"

STEP11_C2_ES_DIR="$REPO_ROOT/Step11_docs/outputs_step11/c2_es"
STEP11_BOARD_ES_DIR="$REPO_ROOT/Step11_docs/outputs_step11/g11_6_18/c2_es"

STEP10_RESULTS="$OUT_DIR/campaign_results.json"
T11_3_OUT="$STEP11_C2_ES_DIR/step11_11-3_es_reseed.json"
T11_5_OUT="$STEP11_C2_ES_DIR/step11_11-5_es_reseed.json"
T11_6_MARKER="$STEP11_BOARD_ES_DIR/step11_stockboard_es.json"

WORKERS=4
MEM_THRESHOLD=75
POLL_SECONDS=20
MAX_STAGE_RETRIES=40
RETRY_SLEEP=15

TS="$(date '+%Y%m%d_%H%M%S')"
MASTER_LOG="$LOG_DIR/madrid_stock_campaign_${TS}.log"
WATCHDOG_PS1="$LOG_DIR/watchdog.ps1"

# ---------------------------------------------------------------------------
log() {
  # timestamped line to stdout AND (in a real run) the master log
  local line
  line="$(date '+%Y-%m-%d %H:%M:%S')  $*"
  echo "$line"
  if [ "$DRY_RUN" -eq 0 ]; then
    mkdir -p "$LOG_DIR"
    echo "$line" >> "$MASTER_LOG"
  fi
}

fatal() {
  log "FATAL: $*"
  exit 1
}

# Write the memory watchdog PowerShell helper. Ported, not reinvented, from
# _local_runs/4J_UK_local/logs/watchdog.ps1 (read verbatim for the preflight
# report) -- same Win32_OperatingSystem poll, same taskkill /T /F kill.
write_watchdog_script() {
  mkdir -p "$LOG_DIR"
  cat > "$WATCHDOG_PS1" <<'PS1EOF'
param(
    [int]$CampaignPid,
    [int]$ThresholdPercent = 75,
    [int]$PollSeconds = 20
)

$logFile = Join-Path $PSScriptRoot "watchdog.log"
function Log($msg) {
    "$(Get-Date -Format s)  $msg" | Out-File -FilePath $logFile -Append -Encoding utf8
}

Log "watchdog started, watching PID $CampaignPid, kill threshold ${ThresholdPercent}% committed"

while ($true) {
    Start-Sleep -Seconds $PollSeconds

    $proc = Get-Process -Id $CampaignPid -ErrorAction SilentlyContinue
    if (-not $proc) {
        Log "watched PID $CampaignPid no longer running, watchdog exiting"
        break
    }

    $os = Get-CimInstance Win32_OperatingSystem
    $totalKB = $os.TotalVisibleMemorySize
    $freeKB = $os.FreePhysicalMemory
    $usedPercent = [math]::Round((($totalKB - $freeKB) / $totalKB) * 100, 1)

    if ($usedPercent -ge $ThresholdPercent) {
        Log "MEMORY THRESHOLD HIT: ${usedPercent}% used (>= ${ThresholdPercent}%) -- killing tree rooted at PID $CampaignPid"
        try {
            & taskkill /PID $CampaignPid /T /F
            Log "taskkill issued for PID $CampaignPid and children"
        } catch {
            Log "taskkill failed: $_"
        }
        break
    }
}

Log "watchdog stopped"
PS1EOF
}

# ---------------------------------------------------------------------------
# Generic stage runner.
#   stage_name   : human label, also used for per-stage log filenames
#   marker_file  : output file whose existence means the stage is DONE
#   py_args      : array of args to pass to $PYTHON_EXE (tool + its own args)
# Resumability:
#   - Step 10 stage: py_args includes --resume, so a relaunch after a
#     watchdog kill only rebuilds cells still missing from out/cells/ --
#     the SAME mechanism the UK/IT local campaigns used
#     (4thJ_step10_nocore_campaign.py's own --resume flag).
#   - Step 11 stages (11.3/11.5/11.6): confirmed by reading
#     tools/4thJ_step11_trigger_campaign.py, 4thJ_step11_aggregate.py,
#     4thJ_step11_stockboard.py -- NONE of the three accepts --resume or any
#     skip-completed flag. A watchdog kill mid-stage means the WHOLE stage
#     restarts from scratch when this script retries it. This is a genuine
#     gap, not an oversight -- recorded in the preflight report section on
#     resumability, not hidden here.
# ---------------------------------------------------------------------------
run_stage() {
  stage_name="$1"
  marker_file="$2"
  shift 2
  # remaining args: the python argument list (first element is the .py path)

  stdout_log="$LOG_DIR/${stage_name}_stdout.log"
  stderr_log="$LOG_DIR/${stage_name}_stderr.log"

  if [ -f "$marker_file" ]; then
    log "STAGE $stage_name: marker already present ($marker_file) -- SKIPPING (already complete)"
    return 0
  fi

  log "STAGE $stage_name: START"
  attempt=0
  while [ ! -f "$marker_file" ]; do
    attempt=$((attempt + 1))
    if [ "$attempt" -gt "$MAX_STAGE_RETRIES" ]; then
      fatal "STAGE $stage_name: exceeded $MAX_STAGE_RETRIES relaunch attempts without producing $marker_file -- stopping, NOT silently continuing"
    fi
    log "STAGE $stage_name: launch attempt $attempt (workers=$WORKERS, mem-kill-threshold=${MEM_THRESHOLD}%)"

    # Build the PowerShell one-liner that starts the python process and
    # prints its PID, so bash can hand that PID to the watchdog and then
    # wait on it. Args are passed as a PowerShell array literal.
    ps_args_literal=""
    for a in "$@"; do
      esc=$(printf '%s' "$a" | sed "s/'/''/g")
      ps_args_literal="${ps_args_literal}'${esc}',"
    done
    ps_args_literal="${ps_args_literal%,}"

    # PowerShell -File REFUSES any path without a .ps1 extension and exits 127;
    # mktemp gives none, which killed the first launch attempt. Deterministic,
    # inspectable path in the log dir instead.
    launch_ps="$LOG_DIR/_launch_${stage_name}.ps1"
    cat > "$launch_ps" <<PSCMD
\$p = Start-Process -FilePath "$PYTHON_EXE" -ArgumentList @($ps_args_literal) -PassThru -WindowStyle Hidden -RedirectStandardOutput "$stdout_log" -RedirectStandardError "$stderr_log"
Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile","-File","$WATCHDOG_PS1","-CampaignPid",\$p.Id,"-ThresholdPercent",$MEM_THRESHOLD,"-PollSeconds",$POLL_SECONDS) -WindowStyle Hidden | Out-Null
\$p.WaitForExit()
exit \$p.ExitCode
PSCMD
    # set -e would abort the whole campaign on the first non-zero exit, which is
    # exactly what a memory-watchdog kill looks like. Capture the code instead.
    ps_rc=0
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$launch_ps" || ps_rc=$?
    rm -f "$launch_ps"

    if [ -f "$marker_file" ]; then
      log "STAGE $stage_name: marker present after attempt $attempt -- COMPLETE"
      break
    fi
    log "STAGE $stage_name: attempt $attempt exited (rc=$ps_rc), marker still missing -- retrying in ${RETRY_SLEEP}s (this may be a memory-watchdog kill, or a real failure; the log above is the evidence)"
    sleep "$RETRY_SLEEP"
  done
  log "STAGE $stage_name: END"
}

# ---------------------------------------------------------------------------
# DRY RUN: print the plan, touch nothing, exit 0.
# ---------------------------------------------------------------------------
if [ "$DRY_RUN" -eq 1 ]; then
  echo "=========================================================================="
  echo "DRY RUN -- Madrid (ES-MAD-BERRUGUETE) stock campaign, Step 10 C2 + Step 11"
  echo "Nothing below this line is executed. No directory is created. No process"
  echo "is launched. Exit code will be 0."
  echo "=========================================================================="
  echo
  echo "Would create directories:"
  echo "  mkdir -p \"$LOG_DIR\""
  echo "  mkdir -p \"$OUT_DIR\""
  echo "  mkdir -p \"$RUN_ROOT\""
  echo "  mkdir -p \"$STEP11_C2_ES_DIR\""
  echo "  mkdir -p \"$STEP11_BOARD_ES_DIR\""
  echo
  echo "Would write watchdog helper: $WATCHDOG_PS1"
  echo "  (ported from _local_runs/4J_UK_local/logs/watchdog.ps1, threshold ${MEM_THRESHOLD}% committed memory, poll ${POLL_SECONDS}s, taskkill /T /F on breach)"
  echo
  echo "Master log: $MASTER_LOG"
  echo
  echo "-------------------------------------------------------------------------"
  echo "STAGE 1/4 -- Step 10 campaign C2, district $DISTRICT, fold $FOLD"
  echo "  marker (stage complete when this file exists): $STEP10_RESULTS"
  echo "  resumable: YES, via the tool's own --resume flag (skips cells already"
  echo "  written under $OUT_DIR/cells/ -- same mechanism the UK/IT local runs used)"
  echo "  command, relaunched with the same flags after every watchdog kill until"
  echo "  the marker file exists (max $MAX_STAGE_RETRIES attempts, ${RETRY_SLEEP}s between):"
  echo "    \"$PYTHON_EXE\" \"$STEP10_TOOL\" \\"
  echo "        --district $DISTRICT --shakedown --resume --workers $WORKERS \\"
  echo "        --out \"$OUT_DIR\" --run-root \"$RUN_ROOT\""
  echo "  stdout/stderr: $LOG_DIR/step10_c2_es_stdout.log / _stderr.log"
  echo "  watched by: powershell.exe -File \"$WATCHDOG_PS1\" -CampaignPid <pid> -ThresholdPercent $MEM_THRESHOLD -PollSeconds $POLL_SECONDS"
  echo
  echo "-------------------------------------------------------------------------"
  echo "STAGE 2/4 -- Step 11 work item 11.3, per-dwelling trigger campaign"
  echo "  marker: $T11_3_OUT"
  echo "  resumable: NO -- 4thJ_step11_trigger_campaign.py has no --resume/skip"
  echo "  flag (confirmed by reading its argparse block). A kill mid-stage means"
  echo "  a full restart of this stage on relaunch."
  echo "  gated on: STAGE 1's marker existing (Step 10 must have finished first)"
  echo "  command:"
  echo "    \"$PYTHON_EXE\" \"$T11_3_TOOL\" \\"
  echo "        --root \"$REPO_ROOT\" --c2-out \"$OUT_DIR\" \\"
  echo "        --diary-diversity reseed --out \"$T11_3_OUT\""
  echo "  stdout/stderr: $LOG_DIR/step11_11-3_es_stdout.log / _stderr.log"
  echo
  echo "-------------------------------------------------------------------------"
  echo "STAGE 3/4 -- Step 11 work item 11.5, stock-scale aggregation (G11.12)"
  echo "  marker: $T11_5_OUT"
  echo "  resumable: NO (same as stage 2, confirmed by reading its argparse block)"
  echo "  gated on: STAGE 2's marker existing"
  echo "  command:"
  echo "    \"$PYTHON_EXE\" \"$T11_5_TOOL\" \\"
  echo "        --root \"$REPO_ROOT\" --c2-out \"$OUT_DIR\" \\"
  echo "        --diary-diversity reseed --out \"$T11_5_OUT\""
  echo "  stdout/stderr: $LOG_DIR/step11_11-5_es_stdout.log / _stderr.log"
  echo
  echo "-------------------------------------------------------------------------"
  echo "STAGE 4/4 -- Step 11 work item 11.6, gate-board stock inputs (G11.6/8/18)"
  echo "  marker: $T11_6_MARKER"
  echo "  resumable: NO (same as stage 2, confirmed by reading its argparse block)"
  echo "  gated on: STAGE 3's marker existing"
  echo "  command:"
  echo "    \"$PYTHON_EXE\" \"$T11_6_TOOL\" \\"
  echo "        --root \"$REPO_ROOT\" --c2-out \"$OUT_DIR\" \\"
  echo "        --diary-diversity reseed --out-dir \"$STEP11_BOARD_ES_DIR\""
  echo "  stdout/stderr: $LOG_DIR/step11_11-6_es_stdout.log / _stderr.log"
  echo
  echo "-------------------------------------------------------------------------"
  echo "NOTE (not automated by this script -- see preflight report section 8):"
  echo "  the UK/IT Step 11 launch found 49 buildings (both cities combined)"
  echo "  carrying SYNTHETIC floor-averaged diaries rather than real per-flat"
  echo "  Step 7 diaries, and excluded them via a hand-built filtered COPY of"
  echo "  out/cells/ before pointing 11.3/11.5/11.6 at it. Whether Madrid's"
  echo "  fresh Step 10 output contains any such buildings is NOT established by"
  echo "  this script and was NOT FOUND in the record -- check"
  echo "  $OUT_DIR/cells/*.json for a non-real diary_origin marker (the same way"
  echo "  the UK/IT seam was found) before STAGE 2 runs for real, and if any"
  echo "  exist, build a filtered '_step11input' copy the same way and point"
  echo "  --c2-out at that copy instead of \"$OUT_DIR\" directly."
  echo
  echo "DRY RUN complete. Exiting 0. Nothing was created or executed."
  exit 0
fi

# ---------------------------------------------------------------------------
# REAL RUN
# ---------------------------------------------------------------------------
mkdir -p "$LOG_DIR" "$OUT_DIR" "$RUN_ROOT" "$STEP11_C2_ES_DIR" "$STEP11_BOARD_ES_DIR"
write_watchdog_script

log "=========================================================================="
log "Madrid (ES-MAD-BERRUGUETE) stock campaign -- START"
log "District: $DISTRICT  Fold: $FOLD  Workers: $WORKERS  Mem-kill-threshold: ${MEM_THRESHOLD}%"
log "Master log: $MASTER_LOG"
log "=========================================================================="

# ---- STAGE 1: Step 10 campaign C2 --------------------------------------
run_stage "step10_c2_es" "$STEP10_RESULTS" \
  "$STEP10_TOOL" --district "$DISTRICT" --shakedown --resume --workers "$WORKERS" \
  --out "$OUT_DIR" --run-root "$RUN_ROOT"

[ -f "$STEP10_RESULTS" ] || fatal "STAGE 1 (Step 10) did not produce $STEP10_RESULTS -- refusing to start Step 11 on an incomplete campaign"

# ---- STAGE 2: Step 11 work item 11.3 (trigger campaign) -----------------
run_stage "step11_11-3_es" "$T11_3_OUT" \
  "$T11_3_TOOL" --root "$REPO_ROOT" --c2-out "$OUT_DIR" \
  --diary-diversity reseed --out "$T11_3_OUT"

[ -f "$T11_3_OUT" ] || fatal "STAGE 2 (Step 11.3) did not produce $T11_3_OUT -- refusing to start 11.5"

# ---- STAGE 3: Step 11 work item 11.5 (stock-scale aggregation) ----------
run_stage "step11_11-5_es" "$T11_5_OUT" \
  "$T11_5_TOOL" --root "$REPO_ROOT" --c2-out "$OUT_DIR" \
  --diary-diversity reseed --out "$T11_5_OUT"

[ -f "$T11_5_OUT" ] || fatal "STAGE 3 (Step 11.5) did not produce $T11_5_OUT -- refusing to start 11.6"

# ---- STAGE 4: Step 11 work item 11.6 (gate-board stock inputs) ----------
run_stage "step11_11-6_es" "$T11_6_MARKER" \
  "$T11_6_TOOL" --root "$REPO_ROOT" --c2-out "$OUT_DIR" \
  --diary-diversity reseed --out-dir "$STEP11_BOARD_ES_DIR"

[ -f "$T11_6_MARKER" ] || fatal "STAGE 4 (Step 11.6) did not produce $T11_6_MARKER"

log "=========================================================================="
log "Madrid (ES-MAD-BERRUGUETE) stock campaign -- ALL FOUR STAGES COMPLETE"
log "Step 10 results:  $STEP10_RESULTS"
log "Step 11.3 output: $T11_3_OUT"
log "Step 11.5 output: $T11_5_OUT"
log "Step 11.6 output: $STEP11_BOARD_ES_DIR"
log "=========================================================================="
