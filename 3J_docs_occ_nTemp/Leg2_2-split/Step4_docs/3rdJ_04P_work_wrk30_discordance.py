"""
3rdJ Step 4P -- Work-activity vs AT_WORK-binary discordance probe.

The S4-02 deep-research report flagged that after raking ~61% of work-activity
slots have wrk30==0, calling it a "critical semantic fail". That number conflates
LEGITIMATE telework (work activity while AT_HOME) with the only truly impossible
state (work activity while NEITHER at home NOR at work). This probe decomposes it.

For all SYNTHETIC rows (and OBS for reference), over slots where act30 == 1 (Work):
  - AT-WORK   wrk30==1                      -> consistent (at the workplace)
  - TELEWORK  wrk30==0 AND hom30==1         -> legitimate (working from home)
  - FLOATING  wrk30==0 AND hom30==0         -> the only genuinely impossible state

Run on a RAKED diaries csv (e.g. R7_cap_raked/augmented_diaries.csv).
"""
import sys
import numpy as np
import pandas as pd

N_SLOTS = 48
WORK_CAT = 1
ACT = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
HOM = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
WRK = [f"wrk30_{s:03d}" for s in range(1, N_SLOTS + 1)]


def measure(d, name):
    a = d[ACT].to_numpy(dtype=float)
    h = d[HOM].to_numpy(dtype=float)
    w = d[WRK].to_numpy(dtype=float)
    work = (a == WORK_CAT)
    n_work = work.sum()
    if n_work == 0:
        print(f"[{name}] n={len(d):,}  no work slots")
        return
    atwork   = (work & (w == 1)).sum()
    telework = (work & (w == 0) & (h == 1)).sum()
    floating = (work & (w == 0) & (h == 0)).sum()
    print(f"[{name}] n={len(d):,}  work-slots={int(n_work):,}")
    print(f"    AT-WORK   (wrk=1)            : {100*atwork/n_work:6.2f}%")
    print(f"    TELEWORK  (wrk=0 & hom=1)    : {100*telework/n_work:6.2f}%  <- legitimate")
    print(f"    FLOATING  (wrk=0 & hom=0)    : {100*floating/n_work:6.2f}%  <- the only impossible state")
    print(f"    [report's '61% wrk=0' = TELEWORK + FLOATING = {100*(telework+floating)/n_work:6.2f}%]")


def main():
    path = sys.argv[1]
    df = pd.read_csv(path, low_memory=False)
    print("=== Work-activity vs AT_WORK discordance (all 48 slots, act==1) ===")
    print(f"file: {path}\n")
    measure(df[df["IS_SYNTHETIC"] == 0], "OBS")
    print()
    measure(df[df["IS_SYNTHETIC"] == 1], "SYN")


if __name__ == "__main__":
    main()
