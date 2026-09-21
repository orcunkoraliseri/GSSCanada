#!/bin/sh
# T68 submission wrapper. -c 8 --mem=32G -t 7-00:00:00 (T06's shape, same input scale).
# Interpreter: /speed-scratch/o_iseri/envs/step4/bin/python
/speed-scratch/o_iseri/envs/step4/bin/python \
  /speed-scratch/o_iseri/2J_revision/T68/T68_scripts/enduse_hour_corrected.py \
  > /speed-scratch/o_iseri/2J_revision/T68/logs/t68_run.out
