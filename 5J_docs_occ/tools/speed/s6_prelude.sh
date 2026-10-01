# sourced by every Step 6 job: fresh split_loader copy, code md5 printed and compared with the Step 5 copies, syntax check (no bytecode written)
PY=/speed-scratch/o_iseri/envs/step4/bin/python
C=/speed-scratch/o_iseri/5J/test/code
T=/speed-scratch/o_iseri/5J/train
F=/speed-scratch/o_iseri/5J/freeze
export PYTHONDONTWRITEBYTECODE=1
cd $C || exit 2
echo "host=$(hostname) start=$(date -Iseconds) job=$SLURM_JOB_ID task=${SLURM_ARRAY_TASK_ID:-none}"
cp $F/split_loader.py $C/split_loader.py.tmp$$ && mv -f $C/split_loader.py.tmp$$ $C/split_loader.py
echo "split_loader md5 freeze=$(md5sum $F/split_loader.py | cut -d' ' -f1) copy=$(md5sum $C/split_loader.py | cut -d' ' -f1)"
for f in s5_common.py s5_data.py s5_models.py s5_predict.py s5_b0.py s5_b1.py s5_store.py; do
  if [ "$(md5sum < $C/$f | cut -d' ' -f1)" = "$(md5sum < $T/$f | cut -d' ' -f1)" ]; then echo "CODE_EQUALS_TRAIN $f $(md5sum < $C/$f | cut -d' ' -f1)"; else echo "CODE_DIFFERS_FROM_TRAIN $f: STOP"; exit 3; fi
done
for f in s6_common.py s6_data.py s6_store.py s6_b0_task.py s6_b1_task.py s6_pred_task.py s6_checks.py; do
  $PY -c "import sys; compile(open('$C/$f').read(), '$f', 'exec')" && echo "SYNTAX_OK $f $(md5sum < $C/$f | cut -d' ' -f1)" || exit 3
done
