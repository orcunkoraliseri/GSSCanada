#!/bin/bash
# 5J Step 6 part B: start-up checks before the ONE scoring job (bash, md5sum + grep + awk + sed only; no python, no truth file).
# Usage: [ROOT=<dir laid out like /speed-scratch/o_iseri/5J>] bash s6_startup.sh
# Every check prints  STARTUP <name> PASS|FAIL <expected> <found>.  All checks run (no early stop); any FAIL -> last line
# "STARTUP_ALL FAIL <n>" and exit 9. All PASS -> last line "STARTUP_ALL PASS" and exit 0. A missing file prints found=MISSING = FAIL.
R=${ROOT:-/speed-scratch/o_iseri/5J}
NFAIL=0
NCHK=0
TAB=$'\t'
HEX='^[0-9a-f]{32}$'
md() { if [ -f "$1" ]; then md5sum < "$1" | cut -d' ' -f1; else echo MISSING; fi; }
chk() {  # name expected found ; the expected value must itself be a 32-hex md5, else FAIL (a broken record cannot pass)
  NCHK=$((NCHK+1))
  if [[ "$2" =~ $HEX ]] && [ "$2" = "$3" ]; then echo "STARTUP $1 PASS $2 $3"; else echo "STARTUP $1 FAIL ${2:-EMPTY} $3"; NFAIL=$((NFAIL+1)); fi
}
echo "STARTUP_SCRIPT_MD5 $(md "$0") root=$R"

# ---- (1) code and gates: records = gates_frozen_amend1.md5 (val 1.1) and freeze/s6_reported_v2.md5
AM=$R/gates_frozen_amend1.md5
rec_am() { if [ "$(grep -c "/$1\$" "$AM" 2>/dev/null)" = "1" ]; then grep "/$1\$" "$AM" | cut -d' ' -f1; fi; }
chk scorer_md5        "$(rec_am 5thJ_04_scorer_t.py)" "$(md $R/freeze/5thJ_04_scorer_t.py)"
chk gates_md5         "$(rec_am gates_frozen.md)"     "$(md $R/test/amend1/gates_frozen.md)"
chk split_loader_md5  "$(rec_am split_loader.py)"     "$(md $R/freeze/split_loader.py)"
RV=$R/freeze/s6_reported_v2.md5
chk reported_v2_md5   "$( [ "$(wc -l < "$RV" 2>/dev/null)" = "1" ] && cut -d' ' -f1 "$RV" )" "$(md $R/freeze/s6_reported_v2.py)"

# ---- (2) checkpoints (val 1.2): records = test/ckpt_md5_snapshot.tsv, train/winner/winner.json, MODEL_MD5 lines of the Step 5 B1_loco_it log
SN=$R/test/ckpt_md5_snapshot.tsv
rec_sn() { if [ "$(grep -F -c -- "$1$TAB" "$SN" 2>/dev/null)" = "1" ]; then grep -F -- "$1$TAB" "$SN" | cut -f2; fi; }
WJ=$R/train/winner/winner.json
rec_wj() { if [ "$(grep -c '"ckpt_md5"' "$WJ" 2>/dev/null)" = "1" ]; then grep '"ckpt_md5"' "$WJ" | sed 's/.*"ckpt_md5": *"\([0-9a-f]*\)".*/\1/'; fi; }
K=$R/train/ckpt
chk ck_S_pinned_snapshot "$(rec_sn /train/winner/pinned/best.pt)" "$(md $R/train/winner/pinned/best.pt)"
chk ck_S_pinned_winner   "$(rec_wj)"                              "$(md $R/train/winner/pinned/best.pt)"
chk ck_S3_snapshot       "$(rec_sn /train/ckpt/S/3/best.pt)"      "$(md $K/S/3/best.pt)"
chk ck_S3_winner         "$(rec_wj)"                              "$(md $K/S/3/best.pt)"
for m in S_seed2 S_seed3 C_seed1 S_loco_es S_loco_it; do
  chk ck_${m}_snapshot "$(rec_sn /train/ckpt/$m/best.pt)" "$(md $K/$m/best.pt)"
done
for m in B1 B1_loco_es; do
  for t in heating cooling equipment; do
    chk ck_${m}_${t}_snapshot "$(rec_sn /train/ckpt/$m/$t.joblib)" "$(md $K/$m/$t.joblib)"
  done
done
LG=$R/train/logs/s5_cb1_1405050.out
rec_lg() { if [ "$(grep -c "^MODEL_MD5 $1 " "$LG" 2>/dev/null)" = "1" ]; then grep "^MODEL_MD5 $1 " "$LG" | awk '{print $3}'; fi; }
for t in heating cooling equipment; do
  chk ck_B1_loco_it_${t}_log "$(rec_lg $t)" "$(md $K/B1_loco_it/$t.joblib)"
done

# ---- (3) split lists (val 1.3): records = splits/splits.md5 AND the Step 3 Progress Log line of 2026-09-30 18:50 (copied below)
SP=$R/splits/splits.md5
declare -A S3LOG=( [test_new_households]=b03e94ea47beb22dec9ac06e40f5d076 [test_new_buildings]=13278a13f8b44097f36e87341c9065d4
                   [test_both_new]=78464ddb3c1c406929314554c99bd635 [b0_test]=0b4faa5eac5b2b86390e1b5d7e809532 [b0_dev]=a22b94129679fc9ef94bc82ad9ebadfe )
for L in test_new_households test_new_buildings test_both_new b0_test b0_dev; do
  F=$(md $R/splits/$L.txt)
  RS=""
  if [ "$(grep -c " $L.txt\$" "$SP" 2>/dev/null)" = "1" ]; then RS=$(grep " $L.txt\$" "$SP" | awk '{print $1}'); fi
  chk split_${L}_splits_md5 "$RS" "$F"
  chk split_${L}_step3_log  "${S3LOG[$L]}" "$F"
done

if [ "$NFAIL" = "0" ]; then echo "STARTUP_ALL PASS ($NCHK checks)"; exit 0; fi
echo "STARTUP_ALL FAIL $NFAIL of $NCHK"
exit 9
