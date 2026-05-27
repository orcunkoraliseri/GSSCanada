#!/bin/bash
cd /speed-scratch/o_iseri/GSSCanada/GSSCanada-main
source /speed-scratch/o_iseri/GSSCanada/venv/bin/activate
export ENERGYPLUS_DIR=/speed-scratch/o_iseri/EnergyPlus/EnergyPlus-24.2.0-94a887817b-Linux-CentOS7.9.2009-x86_64
mkdir -p /speed-scratch/o_iseri/GSSCanada/smoke_test/NUS_RC1
python eSim_bem_utils/run_batch_hpc.py \
  --idf BEM_Setup/Neighbourhoods/NUS_RC1.idf \
  --region Quebec \
  --sim-mode weekly \
  --iter-count 2 \
  --output-dir /speed-scratch/o_iseri/GSSCanada/smoke_test/NUS_RC1
