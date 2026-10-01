#!/bin/bash
# 5J Step 6 part B (val section 4): the start-up checks seen failing, on scratch copies. Bash only. NO scorer call, NO truth file.
# For each case: a scratch ROOT of symlinks to the real files, ONE file (or one record) replaced by a copy with one byte changed;
# s6_startup.sh must exit 9, and the set of FAIL lines must equal the expected set exactly (so it failed for the planted reason,
# found value is a real 32-hex md5 = not just a missing file). Untouched scratch root and the real paths must PASS (exit 0).
FIVE=/speed-scratch/o_iseri/5J
SU=$FIVE/test/code/s6_startup.sh
SF=$FIVE/test/seenfail/job_${SLURM_JOB_ID:-manual}
echo "JOB ${SLURM_JOB_ID:-manual} start $(date -Iseconds) host=$(hostname)"
echo "STARTUP_SCRIPT $(md5sum $SU)"
mkdir -p $SF || exit 2
NBAD=0; NOK=0

mkroot() {  # $1 = scratch root: symlinks to every file the start-up script reads
  local r=$1 f
  mkdir -p $r/freeze $r/test/amend1 $r/splits $r/train/winner/pinned $r/train/logs
  for f in freeze/5thJ_04_scorer_t.py freeze/split_loader.py freeze/s6_reported_v2.py freeze/s6_reported_v2.md5 gates_frozen_amend1.md5 \
           test/amend1/gates_frozen.md test/ckpt_md5_snapshot.tsv splits/splits.md5 train/winner/winner.json train/winner/pinned/best.pt \
           train/logs/s5_cb1_1405050.out; do ln -s $FIVE/$f $r/$f || return 1; done
  for f in test_new_households test_new_buildings test_both_new b0_test b0_dev; do ln -s $FIVE/splits/$f.txt $r/splits/$f.txt || return 1; done
  for m in S/3 S_seed2 S_seed3 C_seed1 S_loco_es S_loco_it; do mkdir -p $r/train/ckpt/$m; ln -s $FIVE/train/ckpt/$m/best.pt $r/train/ckpt/$m/best.pt || return 1; done
  for m in B1 B1_loco_es B1_loco_it; do mkdir -p $r/train/ckpt/$m; for t in heating cooling equipment; do
    ln -s $FIVE/train/ckpt/$m/$t.joblib $r/train/ckpt/$m/$t.joblib || return 1; done; done
}
corrupt() {  # $1 root, $2 relative path, $3 byte offset: replace the symlink by a private copy and flip the low bit of one byte
  local t=$1/$2 real
  real=$(readlink -f $t) || return 1
  rm $t && cp $real $t && chmod u+w $t || return 1
  local b nb
  b=$(dd if=$t bs=1 skip=$3 count=1 2>/dev/null | od -An -tu1 | tr -d ' ')
  nb=$(( b ^ 1 ))
  printf "$(printf '\\x%02x' $nb)" | dd of=$t bs=1 seek=$3 conv=notrunc 2>/dev/null
  if cmp -s $real $t; then echo "FLIP_FAILED $t"; return 1; fi
  echo "FLIPPED $2 offset=$3 byte $b -> $nb ($(cmp $real $t 2>&1 | head -1))"
}
runcase() {  # $1 case name, $2 root, $3 expected FAIL names (space separated, "" = none)
  local out rc fails exp ok=1 n
  out=$(ROOT=$2 bash $SU); rc=$?
  fails=$(echo "$out" | grep '^STARTUP .* FAIL ' | awk '{print $2}' | sort | tr '\n' ' ')
  exp=$(echo $3 | tr ' ' '\n' | sort | tr '\n' ' ')
  echo "$out" | grep -E '^STARTUP .* FAIL |^STARTUP_ALL'
  if [ -z "$3" ]; then
    [ "$rc" = "0" ] && echo "$out" | grep -q '^STARTUP_ALL PASS' || ok=0
  else
    [ "$rc" = "9" ] || ok=0
    [ "$(echo "$fails" | tr -d ' \n')" = "$(echo "$exp" | tr -d ' \n')" ] && [ "$fails" = "$exp" ] || ok=0
    # every FAIL line must carry a real md5 as found value (a file that exists), not MISSING
    n=$(echo "$out" | grep '^STARTUP .* FAIL ' | awk '$5 !~ /^[0-9a-f]{32}$/' | wc -l)
    [ "$n" = "0" ] || ok=0
    echo "$out" | grep -q '^STARTUP_ALL FAIL' || ok=0
  fi
  if [ "$ok" = "1" ]; then NOK=$((NOK+1)); echo "SEENFAIL $1 EXIT $rc FAILS=[$fails] EXPECTED=[$exp] -> OK"
  else NBAD=$((NBAD+1)); echo "SEENFAIL $1 EXIT $rc FAILS=[$fails] EXPECTED=[$exp] -> BAD"; fi
}
newroot() { local r=$SF/$1; rm -rf $r; mkroot $r || { echo "MKROOT_FAILED $1"; NBAD=$((NBAD+1)); return 1; }; echo "ROOT $r"; }

# ---- case 0: untouched scratch root, and the real paths (both must PASS)
newroot c00_untouched && runcase c00_untouched $SF/c00_untouched ""
echo "REAL_PATHS (default ROOT)"; out=$(bash $SU); rc=$?; echo "$out" | grep -E '^STARTUP .* FAIL |^STARTUP_ALL'
if [ "$rc" = "0" ]; then NOK=$((NOK+1)); echo "SEENFAIL c00_real EXIT $rc -> OK"; else NBAD=$((NBAD+1)); echo "SEENFAIL c00_real EXIT $rc -> BAD"; fi

# ---- file cases: one byte of one real kind of file changed
newroot c01 && corrupt $SF/c01 freeze/5thJ_04_scorer_t.py 1000 && runcase c01_scorer $SF/c01 "scorer_md5"
newroot c02 && corrupt $SF/c02 test/amend1/gates_frozen.md 1000 && runcase c02_gates_doc $SF/c02 "gates_md5"
newroot c03 && corrupt $SF/c03 freeze/split_loader.py 500 && runcase c03_split_loader $SF/c03 "split_loader_md5"
newroot c04 && corrupt $SF/c04 freeze/s6_reported_v2.py 1000 && runcase c04_reported_v2_py $SF/c04 "reported_v2_md5"
newroot c05 && corrupt $SF/c05 train/winner/pinned/best.pt 100000 && runcase c05_S_pinned $SF/c05 "ck_S_pinned_snapshot ck_S_pinned_winner"
newroot c06 && corrupt $SF/c06 train/ckpt/S_seed2/best.pt 100000 && runcase c06_S_seed2 $SF/c06 "ck_S_seed2_snapshot"
newroot c07 && corrupt $SF/c07 train/ckpt/S_seed3/best.pt 100000 && runcase c07_S_seed3 $SF/c07 "ck_S_seed3_snapshot"
newroot c08 && corrupt $SF/c08 train/ckpt/C_seed1/best.pt 100000 && runcase c08_C_seed1 $SF/c08 "ck_C_seed1_snapshot"
newroot c09 && corrupt $SF/c09 train/ckpt/S_loco_es/best.pt 100000 && runcase c09_S_loco_es $SF/c09 "ck_S_loco_es_snapshot"
newroot c10 && corrupt $SF/c10 train/ckpt/S_loco_it/best.pt 100000 && runcase c10_S_loco_it $SF/c10 "ck_S_loco_it_snapshot"
newroot c11 && corrupt $SF/c11 train/ckpt/B1/cooling.joblib 100000 && runcase c11_B1_cooling $SF/c11 "ck_B1_cooling_snapshot"
newroot c12 && corrupt $SF/c12 train/ckpt/B1_loco_es/equipment.joblib 100000 && runcase c12_B1_loco_es_equipment $SF/c12 "ck_B1_loco_es_equipment_snapshot"
newroot c13 && corrupt $SF/c13 train/ckpt/B1_loco_it/heating.joblib 100000 && runcase c13_B1_loco_it_heating $SF/c13 "ck_B1_loco_it_heating_log"
newroot c14 && corrupt $SF/c14 splits/b0_test.txt 5 && runcase c14_b0_test_list $SF/c14 "split_b0_test_splits_md5 split_b0_test_step3_log"
newroot c15 && corrupt $SF/c15 splits/test_new_households.txt 5 && runcase c15_test_new_households_list $SF/c15 "split_test_new_households_splits_md5 split_test_new_households_step3_log"
newroot c16 && corrupt $SF/c16 splits/b0_dev.txt 5 && runcase c16_b0_dev_list $SF/c16 "split_b0_dev_splits_md5 split_b0_dev_step3_log"

# ---- record cases: one hex character of one md5 record changed (the files are fine, the record is wrong)
newroot r01 && corrupt $SF/r01 gates_frozen_amend1.md5 $(grep -b -E '5thJ_04_scorer_t.py$' $FIVE/gates_frozen_amend1.md5 | cut -d: -f1) && runcase r01_amend1_record $SF/r01 "scorer_md5"
newroot r02 && corrupt $SF/r02 freeze/s6_reported_v2.md5 0 && runcase r02_reported_v2_record $SF/r02 "reported_v2_md5"
L=$(grep -b -F '/train/ckpt/C_seed1/best.pt' $FIVE/test/ckpt_md5_snapshot.tsv | cut -d: -f1); P=$(grep -F '/train/ckpt/C_seed1/best.pt' $FIVE/test/ckpt_md5_snapshot.tsv | cut -f1)
newroot r03 && corrupt $SF/r03 test/ckpt_md5_snapshot.tsv $((L + ${#P} + 1)) && runcase r03_snapshot_record_C_seed1 $SF/r03 "ck_C_seed1_snapshot"
LN=$(grep -b -F '"ckpt_md5"' $FIVE/train/winner/winner.json | cut -d: -f1); TX=$(grep -F '"ckpt_md5"' $FIVE/train/winner/winner.json); RS=${TX#*\"ckpt_md5\": \"}
newroot r04 && corrupt $SF/r04 train/winner/winner.json $((LN + ${#TX} - ${#RS})) && runcase r04_winner_json_record $SF/r04 "ck_S_pinned_winner ck_S3_winner"
newroot r05 && corrupt $SF/r05 splits/splits.md5 $(grep -b -F ' b0_test.txt' $FIVE/splits/splits.md5 | cut -d: -f1) && runcase r05_splits_md5_record_b0_test $SF/r05 "split_b0_test_splits_md5"
M=$(grep -b -F 'MODEL_MD5 heating' $FIVE/train/logs/s5_cb1_1405050.out | cut -d: -f1)
newroot r06 && corrupt $SF/r06 train/logs/s5_cb1_1405050.out $((M + 18)) && runcase r06_B1_loco_it_log_record $SF/r06 "ck_B1_loco_it_heating_log"

# ---- a missing record file must also stop it (found/expected rules), without being counted as a data check
newroot m01 && rm $SF/m01/test/ckpt_md5_snapshot.tsv && echo "REMOVED snapshot record (symlink only)"; out=$(ROOT=$SF/m01 bash $SU); rc=$?
echo "$out" | grep -E '^STARTUP_ALL'; if [ "$rc" = "9" ]; then NOK=$((NOK+1)); echo "SEENFAIL m01_snapshot_record_missing EXIT $rc -> OK"; else NBAD=$((NBAD+1)); echo "SEENFAIL m01_snapshot_record_missing EXIT $rc -> BAD"; fi

# ---- the real files are unchanged (the planted copies were private)
out=$(bash $SU); rc=$?; echo "$out" | grep -E '^STARTUP .* FAIL |^STARTUP_ALL'
if [ "$rc" = "0" ]; then NOK=$((NOK+1)); echo "SEENFAIL final_real_paths EXIT $rc -> OK"; else NBAD=$((NBAD+1)); echo "SEENFAIL final_real_paths EXIT $rc -> BAD"; fi
if [ "$((NOK+NBAD))" != "26" ]; then NBAD=$((NBAD+1)); echo "SEENFAIL cases_counted=$((NOK+NBAD)) expected 26: a case was skipped -> BAD"; fi
echo "SEENFAIL_DONE ok=$NOK bad=$NBAD end=$(date -Iseconds)"
[ "$NBAD" = "0" ] && exit 0
exit 1
