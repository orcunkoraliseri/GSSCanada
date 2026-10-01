#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -J s7_stage
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_stage_%j.out
# copies READ-ONLY sources into district/code (md5 of source and copy printed; any difference stops the job)
D=/speed-scratch/o_iseri/5J/district
C=$D/code
T=/speed-scratch/o_iseri/5J/test/code
K=/speed-scratch/o_iseri/5J/campaign
F=/speed-scratch/o_iseri/5J/freeze
echo "host=$(hostname) start=$(date -Iseconds)"
for f in s5_common.py s5_data.py s5_models.py s5_predict.py s5_store.py s6_common.py s6_data.py s6_store.py; do
  cp $T/$f $C/$f.tmp && mv -f $C/$f.tmp $C/$f
  a=$(md5sum < $T/$f | cut -d' ' -f1); b=$(md5sum < $C/$f | cut -d' ' -f1)
  [ "$a" = "$b" ] && echo "STAGED $f $a" || { echo "STAGE_MISMATCH $f"; exit 3; }
done
for f in camp_common.py camp_integrity.py camp_task.py; do          # camp_task.py added by the manager 2026-10-01 05:04 (pilot 1405234 failed: ModuleNotFoundError)
  cp $K/$f $C/$f.tmp && mv -f $C/$f.tmp $C/$f
  a=$(md5sum < $K/$f | cut -d' ' -f1); b=$(md5sum < $C/$f | cut -d' ' -f1)
  [ "$a" = "$b" ] && echo "STAGED $f $a" || { echo "STAGE_MISMATCH $f"; exit 3; }
done
cp $F/split_loader.py $C/split_loader.py.tmp && mv -f $C/split_loader.py.tmp $C/split_loader.py
echo "STAGED split_loader.py $(md5sum < $C/split_loader.py | cut -d' ' -f1) freeze=$(md5sum < $F/split_loader.py | cut -d' ' -f1)"
echo "end=$(date -Iseconds)"
