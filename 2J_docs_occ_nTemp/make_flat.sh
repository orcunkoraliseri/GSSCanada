#!/bin/bash
set -e
SRC=/speed-scratch/o_iseri/GSSCanada/results/BatchAll_MC_N20_v2
DST=/speed-scratch/o_iseri/GSSCanada/results/BatchAll_MC_N20_flat
mkdir -p "$DST"
for n in NUS_RC1 NUS_RC2 NUS_RC3 NUS_RC4 NUS_RC5 NUS_RC6; do
  ln -sfn "$SRC/$n/$n" "$DST/$n"
done
ls -la "$DST"
