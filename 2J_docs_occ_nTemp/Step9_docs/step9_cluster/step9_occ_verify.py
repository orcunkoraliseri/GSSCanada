#!/usr/bin/env python3
"""step9_occ_verify.py — Gate check after Stage A of the corrected re-run.

Verifies that BEM_Schedules_2022.csv has the +4h diary->clock rotation applied.
Expected: weekday occupancy peaks overnight (h0-h5) and troughs midday (h11-h14).
Buggy symptom: occupancy peaks at h4-h9 (shifted 4h toward morning).

Run on the cluster after step9_a_generate_full.sh completes:
  /speed-scratch/o_iseri/envs/step4/bin/python step9_occ_verify.py
"""
import csv, sys
from pathlib import Path

CSV_PATH = Path("/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/BEM_Schedules_2022.csv")

if not CSV_PATH.exists():
    print("ERROR: BEM_Schedules_2022.csv not found — did Stage A complete?")
    sys.exit(1)

by_h = {}
n_rows = 0
with open(CSV_PATH) as f:
    for row in csv.DictReader(f):
        if row.get("Day_Type") != "Weekday":
            continue
        h = int(row["Hour"])
        by_h.setdefault(h, []).append(float(row["Occupancy_Schedule"]))
        n_rows += 1

if not by_h:
    print("ERROR: no Weekday rows found — check CSV format")
    sys.exit(1)

avg = {h: sum(v) / len(v) for h, v in by_h.items()}

night_avg  = sum(avg.get(h, 0) for h in range(0, 6)) / 6
midday_avg = sum(avg.get(h, 0) for h in range(11, 15)) / 4
peak_h     = max(avg, key=lambda k: avg[k])

print(f"Weekday occupancy check ({n_rows:,} rows):")
print(f"  Night  avg h00-h05 : {night_avg:.3f}")
print(f"  Midday avg h11-h14 : {midday_avg:.3f}")
print(f"  Peak hour           : h{peak_h:02d}  ({avg[peak_h]:.3f})")
print()
print("Hourly profile:")
for h in range(24):
    bar = "#" * int(avg.get(h, 0) * 30)
    marker = " <-- PEAK" if h == peak_h else ""
    print(f"  h{h:02d}: {avg.get(h, 0):.3f}  {bar}{marker}")

print()
if night_avg > midday_avg and peak_h < 6:
    print("RESULT: PASS — overnight peak, midday trough confirmed (fix applied)")
    sys.exit(0)
elif night_avg > midday_avg:
    print(f"RESULT: WARN — night > midday but peak at h{peak_h:02d}; accept if <=h07")
    sys.exit(0)
else:
    print("RESULT: FAIL — occupancy does NOT peak overnight. Upload may not have taken.")
    sys.exit(1)
