"""
3rdJ Step 4P -- Work-activity vs AT_WORK-binary discordance probe (Leg-3, four-split).

Forked from Leg-2's 3rdJ_04P_work_wrk30_discordance.py. The Leg-2 tool decomposed
"work activity while wrk30==0" into legitimate TELEWORK vs impossible FLOATING. Leg-3
adds a third occupancy channel (ret30 / AT_RETAIL), which introduces a new
inconsistency mode: work activity recorded while the person is at a retail location
(ret30==1) with neither hom30 nor wrk30 set. That is not physically impossible in the
same sense as pure FLOATING (e.g. a retail employee's shift), but it IS a case where
the physical-state signal is retail, not workplace, so it is reported separately
rather than folded into either AT-WORK or FLOATING.

For all SYNTHETIC rows (and OBS for reference), over slots where act30 == 1 (Work):
  - AT-WORK             wrk30==1                                  -> consistent
                                                                       (at the workplace)
  - TELEWORK            wrk30==0 AND hom30==1                     -> legitimate
                                                                       (working from home)
  - RETAIL-incompatible wrk30==0 AND hom30==0 AND ret30==1        -> physical-state
                                                                       signal is retail,
                                                                       not workplace
  - FLOATING            wrk30==0 AND hom30==0 AND ret30==0        -> the only genuinely
                                                                       impossible state
                                                                       (no location
                                                                       signal at all)

This is the GA-3 before/after evidence tool: run once on the pre-04T pool
(<BASE>_raked3_mindwell/augmented_diaries.csv) and once on the post-04T pool
(<BASE>_raked3_mindwell_actv/augmented_diaries.csv) to show Gate GA (FLOATING-rate
excess) closing.

Run on a RAKED diaries csv (e.g. <BASE>_raked3_mindwell_actv/augmented_diaries.csv).

Usage:
    py -3 3rdJ_04P_discordance_4split.py <csv_path>
"""
import sys
import numpy as np
import pandas as pd

N_SLOTS = 48
WORK_CAT = 1
ACT = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
HOM = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
WRK = [f"wrk30_{s:03d}" for s in range(1, N_SLOTS + 1)]
RET = [f"ret30_{s:03d}" for s in range(1, N_SLOTS + 1)]


def measure(d, name):
    a = d[ACT].to_numpy(dtype=float)
    h = d[HOM].to_numpy(dtype=float)
    w = d[WRK].to_numpy(dtype=float)
    r = d[RET].to_numpy(dtype=float)
    work = (a == WORK_CAT)
    n_work = work.sum()
    if n_work == 0:
        print(f"[{name}] n={len(d):,}  no work slots")
        return
    atwork   = (work & (w == 1)).sum()
    telework = (work & (w == 0) & (h == 1)).sum()
    retail_incompat = (work & (w == 0) & (h == 0) & (r == 1)).sum()
    floating = (work & (w == 0) & (h == 0) & (r == 0)).sum()
    print(f"[{name}] n={len(d):,}  work-slots={int(n_work):,}")
    print(f"    AT-WORK              (wrk=1)                  : {100*atwork/n_work:6.2f}%")
    print(f"    TELEWORK             (wrk=0 & hom=1)          : {100*telework/n_work:6.2f}%  <- legitimate")
    print(f"    RETAIL-incompatible  (wrk=0 & hom=0 & ret=1)  : {100*retail_incompat/n_work:6.2f}%  <- location signal is retail, not workplace")
    print(f"    FLOATING             (wrk=0 & hom=0 & ret=0)  : {100*floating/n_work:6.2f}%  <- the only impossible state")
    print(f"    [Leg-2's '61% wrk=0' analogue = TELEWORK + RETAIL-incompatible + FLOATING = "
          f"{100*(telework+retail_incompat+floating)/n_work:6.2f}%]")


def main():
    path = sys.argv[1]
    df = pd.read_csv(path, low_memory=False)
    print("=== Work-activity vs AT_WORK discordance (all 48 slots, act==1, 4-way) ===")
    print(f"file: {path}\n")
    measure(df[df["IS_SYNTHETIC"] == 0], "OBS")
    print()
    measure(df[df["IS_SYNTHETIC"] == 1], "SYN")


if __name__ == "__main__":
    main()
