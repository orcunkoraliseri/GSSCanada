#!/bin/bash
RESULTS=/speed-scratch/o_iseri/GSSCanada/results/BatchAll_MC_N20_v2
echo "=== Queue ==="
squeue -u o_iseri
echo ""
echo "=== Iterations ==="
for h in NUS_RC1 NUS_RC2 NUS_RC3 NUS_RC4 NUS_RC5 NUS_RC6; do
    count=$(find "$RESULTS/$h/$h" -maxdepth 1 -name "iter_*" -type d 2>/dev/null | wc -l)
    csv=$(test -f "$RESULTS/$h/$h/aggregated_eui.csv" && echo "[CSV ready]" || echo "")
    echo "$h: $count/20 $csv"
done
