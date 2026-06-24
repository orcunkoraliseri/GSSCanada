"""
Q1-Q4 gap analysis script.
READ-ONLY.
"""
import pandas as pd
import numpy as np

POOL = r'C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step4_docs\outputs_step4\augmented_diaries.csv'
FULL_SCHED = r'C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step5_docs\outputs_step5\3rdJ_25CEN_aug_Full_Schedules.csv'
MATCHED_KEYS = r'C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step5_docs\outputs_step5\3rdJ_25CEN_aug_Matched_Keys.csv'

WRK_PEAK_SLOTS = list(range(9, 21))  # 0-indexed 8-19 = columns wrk30_009..wrk30_020
WRK_PEAK_COLS = [f'wrk30_{i:03d}' for i in range(9, 21)]
COL_PEAK_COLS = [f'colleagues30_{i:03d}' for i in range(9, 21)]

print("=" * 70)
print("Q1: DDAY SEMANTICS + WORK-PEAK BREAKDOWN IN POOL")
print("=" * 70)

# Load only what we need from pool
pool_needed = ['DDAY_STRATA', 'IS_SYNTHETIC', 'LFTAG'] + WRK_PEAK_COLS + COL_PEAK_COLS
pool = pd.read_csv(POOL, usecols=pool_needed, low_memory=False)
print(f"Pool shape: {pool.shape}")
print(f"\nDDAY_STRATA value counts:")
print(pool['DDAY_STRATA'].value_counts().sort_index())

print(f"\nIS_SYNTHETIC value counts:")
print(pool['IS_SYNTHETIC'].value_counts().sort_index())

print(f"\nCross-tab DDAY_STRATA x IS_SYNTHETIC:")
print(pd.crosstab(pool['DDAY_STRATA'], pool['IS_SYNTHETIC']))

# Work peak per DDAY
pool['work_peak'] = (pool[WRK_PEAK_COLS] == 1).any(axis=1)
print(f"\nWork-peak rate by DDAY_STRATA:")
for dday in [1, 2, 3]:
    mask = pool['DDAY_STRATA'] == dday
    n = mask.sum()
    rate = pool.loc[mask, 'work_peak'].mean() * 100
    print(f"  DDAY_STRATA={dday}: N={n:,}  work_peak_rate={rate:.2f}%")

# Work-peak by IS_SYNTHETIC and DDAY cross
print(f"\nWork-peak rate by DDAY_STRATA x IS_SYNTHETIC:")
for dday in [1, 2, 3]:
    for syn in [0, 1]:
        mask = (pool['DDAY_STRATA'] == dday) & (pool['IS_SYNTHETIC'] == syn)
        n = mask.sum()
        if n > 0:
            rate = pool.loc[mask, 'work_peak'].mean() * 100
            print(f"  DDAY={dday}, IS_SYN={syn}: N={n:,}  work_peak={rate:.2f}%")

print("\n" + "=" * 70)
print("Q2: POOL PROVENANCE — columns check")
print("=" * 70)

# Check for rake-specific columns
rake_indicators = ['RAKE_WEIGHT', 'WEIGHT_RAKED', 'RAKE_ITER', 'RAKED',
                   'ipf_weight', 'before_work', 'after_work']
all_cols = pd.read_csv(POOL, nrows=0).columns.tolist()
found_rake = [c for c in all_cols if any(r.lower() in c.lower() for r in ['rake', 'weight', 'ipf', 'floataware', 'calibrat'])]
print(f"Rake/calibration-like columns in pool: {found_rake if found_rake else 'NONE FOUND'}")
print(f"Total pool columns: {len(all_cols)}")
print(f"IS_SYNTHETIC present: {'IS_SYNTHETIC' in all_cols}")

# Work peak observed vs synthetic
obs_mask = pool['IS_SYNTHETIC'] == 0
syn_mask = pool['IS_SYNTHETIC'] == 1
wp_obs = pool.loc[obs_mask, 'work_peak'].mean() * 100
wp_syn = pool.loc[syn_mask, 'work_peak'].mean() * 100
print(f"\nPool work-peak (IS_SYN=0/obs): {wp_obs:.2f}%")
print(f"Pool work-peak (IS_SYN=1/syn): {wp_syn:.2f}%")
print(f"  Obs vs Syn gap: {wp_obs - wp_syn:.2f} pp")

print("\n" + "=" * 70)
print("Q3 + Q4: OUTPUT DECOMPOSITION (Full_Schedules.csv)")
print("=" * 70)

# Load Full_Schedules — only needed cols
sched_needed = ['PID', 'IS_SYNTHETIC', 'LFTAG'] + WRK_PEAK_COLS + COL_PEAK_COLS
try:
    sched = pd.read_csv(FULL_SCHED, usecols=sched_needed, low_memory=False)
    print(f"Full_Schedules shape: {sched.shape}")
except Exception as e:
    # Try to get available columns first
    sched_all_cols = pd.read_csv(FULL_SCHED, nrows=0).columns.tolist()
    print(f"Available columns in Full_Schedules: {sched_all_cols[:40]}")
    print(f"Error loading with usecols: {e}")
    sched = pd.read_csv(FULL_SCHED, nrows=5)
    print(sched.head())
    exit()

print(f"IS_SYNTHETIC value counts:")
print(sched['IS_SYNTHETIC'].value_counts().sort_index())

if 'LFTAG' not in sched.columns:
    # Try loading keys file to get LFTAG
    print("LFTAG not in Full_Schedules — checking Matched_Keys...")
    keys = pd.read_csv(MATCHED_KEYS, low_memory=False)
    print(f"Matched_Keys columns: {keys.columns.tolist()[:20]}")
    keys_needed = [c for c in ['PID', 'LFTAG', 'DDAY_STRATA', 'AGEGRP', 'SEX'] if c in keys.columns]
    sched = sched.merge(keys[keys_needed], on='PID', how='left')
    print(f"After merge shape: {sched.shape}")

# Work-peak on output
sched['work_peak'] = (sched[WRK_PEAK_COLS] == 1).any(axis=1)
print(f"\nQ3 — Output work-peak by IS_SYNTHETIC:")
for syn in [0, 1]:
    mask = sched['IS_SYNTHETIC'] == syn
    n = mask.sum()
    rate = sched.loc[mask, 'work_peak'].mean() * 100
    print(f"  IS_SYNTHETIC={syn}: N={n:,}  work_peak={rate:.2f}%")

# Q3: Split by LFTAG (employment)
if 'LFTAG' in sched.columns:
    print(f"\nLFTAG value counts (from output):")
    print(sched['LFTAG'].value_counts().sort_index())

    # LFTAG==1 = Employed (check what values are present)
    # Typical values: 1=Employed, 2=Unemployed, 3=Not in LF, etc.
    employed_vals = sched['LFTAG'].value_counts().sort_index()
    print(f"\nAssuming employed = LFTAG==1 (most common employment code)")

    for lftag_val in sorted(sched['LFTAG'].dropna().unique()):
        mask_lf = sched['LFTAG'] == lftag_val
        n_total = mask_lf.sum()
        if n_total < 10:
            continue
        for syn in [0, 1]:
            mask = mask_lf & (sched['IS_SYNTHETIC'] == syn)
            n = mask.sum()
            if n > 0:
                rate = sched.loc[mask, 'work_peak'].mean() * 100
                print(f"  LFTAG={lftag_val}, IS_SYN={syn}: N={n:,}  work_peak={rate:.2f}%")

    # Employed share within each IS_SYNTHETIC group
    print(f"\nEmployed share (LFTAG==1) by IS_SYNTHETIC:")
    for syn in [0, 1]:
        mask = sched['IS_SYNTHETIC'] == syn
        if mask.sum() > 0:
            emp_share = (sched.loc[mask, 'LFTAG'] == 1).mean() * 100
            print(f"  IS_SYNTHETIC={syn}: employed_share={emp_share:.2f}%")

print("\n" + "=" * 70)
print("Q4 — COLLEAGUES DECOMPOSITION (output level)")
print("=" * 70)

# Colleagues at work peak: among AT_WORK agents at peak slots
sched['at_work_peak'] = (sched[WRK_PEAK_COLS] == 1).any(axis=1)
col_cols_present = [c for c in COL_PEAK_COLS if c in sched.columns]
if col_cols_present:
    sched['colleagues_peak'] = (sched[col_cols_present] == 1).any(axis=1)
    print(f"\nAmong at-work-peak agents, colleagues rate by IS_SYNTHETIC:")
    for syn in [0, 1]:
        mask = (sched['IS_SYNTHETIC'] == syn) & sched['at_work_peak']
        n = mask.sum()
        if n > 0:
            rate = sched.loc[mask, 'colleagues_peak'].mean() * 100
            print(f"  IS_SYNTHETIC={syn}: N={n:,}  colleagues_at_peak={rate:.2f}%")

    if 'LFTAG' in sched.columns:
        print(f"\nAmong employed (LFTAG==1) at-work-peak agents, colleagues rate by IS_SYNTHETIC:")
        for syn in [0, 1]:
            mask = (sched['IS_SYNTHETIC'] == syn) & (sched['LFTAG'] == 1) & sched['at_work_peak']
            n = mask.sum()
            if n > 0:
                rate = sched.loc[mask, 'colleagues_peak'].mean() * 100
                print(f"  IS_SYNTHETIC={syn}, LFTAG=1, at_work: N={n:,}  colleagues={rate:.2f}%")
else:
    print("No colleagues30 columns found in Full_Schedules.")

print("\nDone.")
