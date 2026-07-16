#!/bin/bash
squeue -u o_iseri | grep 953076
echo "---"
for t in 0 1 2 3 4 5; do
  log=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/logs/step8_953076_${t}.out
  if [ -f "$log" ]; then
    cnt=$(grep -c "^\[" "$log" 2>/dev/null || echo 0)
    last=$(grep -E "^\[" "$log" | tail -1)
    arch=$(head -1 "$log")
    echo "  task$t ($arch): $cnt sims done | $last"
  fi
done
echo "---"
echo "hourly_meters found: $(find /speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/campaign_N50 -name hourly_meters.csv 2>/dev/null | wc -l) / 6000"
