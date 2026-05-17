"""
check_04E_output.py  —  Diagnostic for augmented_diaries.csv

Checks:
  1. Basic shape and IS_SYNTHETIC counts
  2. Activity marginal distribution: observed vs synthetic
  3. Sleep temporal pattern (should cluster at night)
  4. Work temporal pattern (should cluster 8 AM–6 PM)
  5. AT_HOME consistency (sleep-at-night → home; work → not home)
  6. Sample respondent: 3 strata diaries side-by-side

Usage (on cluster):
    cd /speed-scratch/o_iseri/occModeling
    /speed-scratch/o_iseri/envs/step4/bin/python check_04E_output.py
"""

import sys
import numpy as np
import pandas as pd

CSV_PATH = "outputs_step4/augmented_diaries.csv"

# Raw 1-indexed activity categories in the CSV (act_out + 1)
SLEEP_RAW = 5   # tensor 4 + 1
WORK_RAW  = 1   # tensor 0 + 1
N_SLOTS   = 48

# Night slots (0-indexed): 4:00-7:30 AM → 0-6; 10:30 PM-4:00 AM → 37-47
NIGHT_SLOTS = set(range(0, 7)) | set(range(37, 48))

ACT_LABELS = {
    1: "Work",
    2: "Education",
    3: "Domestic",
    4: "Volunteer",
    5: "Sleep",
    6: "Meals",
    7: "Personal care",
    8: "Shopping",
    9: "Social",
    10: "Recreation",
    11: "Sport",
    12: "TV/Screen",
    13: "Transit",
    14: "Other",
}

def slot_label(s0):
    """0-indexed slot → time string, e.g. slot 0 → '4:00'"""
    minutes = 4 * 60 + s0 * 30
    h = (minutes // 60) % 24
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

def bar(frac, width=30):
    n = int(round(frac * width))
    return "[" + "#" * n + " " * (width - n) + f"] {100*frac:5.1f}%"

def main():
    print("=" * 60)
    print("04E Output Diagnostic")
    print("=" * 60)

    print(f"\nLoading {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH, low_memory=False)
    print(f"  Shape: {df.shape}")

    # ── 1. Basic counts ────────────────────────────────────────────
    print("\n── 1. IS_SYNTHETIC counts ────────────────────────────────")
    obs_n = (df["IS_SYNTHETIC"] == 0).sum()
    syn_n = (df["IS_SYNTHETIC"] == 1).sum()
    print(f"  IS_SYNTHETIC=0 (observed): {obs_n:>8,}")
    print(f"  IS_SYNTHETIC=1 (synthetic): {syn_n:>7,}")
    print(f"  Total rows:                {len(df):>8,}  (expect {len(df)//3 * 3})")
    rows_per = df.groupby("occID").size().value_counts()
    print(f"  Rows per occID: {dict(rows_per)}")

    cycle_counts = df["CYCLE_YEAR"].value_counts().sort_index()
    print(f"  Cycle years: {dict(cycle_counts)}")

    # ── 2. Activity marginal distribution ─────────────────────────
    act_cols = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]

    obs_acts = df[df["IS_SYNTHETIC"] == 0][act_cols].values.flatten()
    syn_acts = df[df["IS_SYNTHETIC"] == 1][act_cols].values.flatten()

    print("\n── 2. Activity marginal distribution ─────────────────────")
    print(f"  {'Cat':>3}  {'Label':<15}  {'Observed':>8}   {'Synthetic':>9}")
    print(f"  {'-'*3}  {'-'*15}  {'-'*28}")

    all_cats = sorted(set(np.unique(obs_acts).tolist() + np.unique(syn_acts).tolist()))
    for cat in all_cats:
        o_pct = 100 * np.mean(obs_acts == cat)
        s_pct = 100 * np.mean(syn_acts == cat)
        label = ACT_LABELS.get(int(cat), "?")
        flag = "  <-- LARGE DIFF" if abs(o_pct - s_pct) > 5 else ""
        print(f"  {int(cat):>3}  {label:<15}  {o_pct:6.1f}%   {s_pct:6.1f}%{flag}")

    # ── 2b. Per-stratum activity distribution ─────────────────────
    print("\n── 2b. Per-stratum activity distribution ─────────────────")
    strata_names = {1: "Weekday", 2: "Saturday", 3: "Sunday"}
    for s in [1, 2, 3]:
        obs_s = df[(df["IS_SYNTHETIC"] == 0) & (df["DDAY_STRATA"] == s)][act_cols].values.flatten()
        syn_s = df[(df["IS_SYNTHETIC"] == 1) & (df["DDAY_STRATA"] == s)][act_cols].values.flatten()
        if len(obs_s) == 0 or len(syn_s) == 0:
            print(f"  DDAY_STRATA={s} ({strata_names[s]}): insufficient data")
            continue
        print(f"\n  DDAY_STRATA={s} ({strata_names[s]}):  "
              f"obs n={len(obs_s)//N_SLOTS:,}  syn n={len(syn_s)//N_SLOTS:,}")
        print(f"  {'Cat':>3}  {'Label':<15}  {'Observed':>8}   {'Synthetic':>9}")
        for cat in range(1, 15):
            o_pct = 100 * np.mean(obs_s == cat)
            s_pct = 100 * np.mean(syn_s == cat)
            label = ACT_LABELS.get(cat, "?")
            flag = "  <-- LARGE DIFF" if abs(o_pct - s_pct) > 5 else ""
            print(f"  {cat:>3}  {label:<15}  {o_pct:6.1f}%   {s_pct:6.1f}%{flag}")

    # ── 3. Sleep temporal pattern ──────────────────────────────────
    print("\n── 3. Sleep temporal pattern (slot 0 = 4:00 AM) ─────────")
    print("  Fraction of respondents sleeping each slot (synthetic only):")
    syn_df = df[df["IS_SYNTHETIC"] == 1]
    night_ok = True
    day_sleep_slots = []

    for s0 in range(N_SLOTS):
        col = f"act30_{s0+1:03d}"
        frac = (syn_df[col] == SLEEP_RAW).mean()
        is_night = s0 in NIGHT_SLOTS
        marker = " [night]" if is_night else ""
        if s0 % 4 == 0 or s0 in (0, 47):  # print every 2 hours + boundaries
            print(f"  slot {s0:02d} ({slot_label(s0)}) {bar(frac, 20)}{marker}")
        # Sanity: daytime sleep > 20% is suspicious
        if not is_night and frac > 0.20:
            day_sleep_slots.append((s0, slot_label(s0), frac))
            night_ok = False

    if day_sleep_slots:
        print("  WARNING: high daytime sleep fraction:")
        for s0, t, f in day_sleep_slots:
            print(f"    slot {s0:02d} ({t}): {100*f:.1f}%")
    else:
        print("  OK: no suspicious daytime sleep spikes")

    # ── 4. Work temporal pattern ───────────────────────────────────
    print("\n── 4. Work temporal pattern (slot 0 = 4:00 AM) ──────────")
    print("  Fraction working each slot (synthetic only):")
    work_peak_found = False
    for s0 in range(N_SLOTS):
        col = f"act30_{s0+1:03d}"
        frac = (syn_df[col] == WORK_RAW).mean()
        # Work peak should be roughly 8 AM–6 PM = slots 8–27
        if 8 <= s0 <= 27 and frac > 0.05:
            work_peak_found = True
        if s0 % 4 == 0:
            print(f"  slot {s0:02d} ({slot_label(s0)}) {bar(frac, 20)}")

    if work_peak_found:
        print("  OK: work peak detected during business hours")
    else:
        print("  WARNING: no clear work peak during 8 AM–6 PM — check generation")

    # ── 5. AT_HOME consistency ─────────────────────────────────────
    print("\n── 5. AT_HOME consistency (synthetic rows only) ──────────")
    hom_cols = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]

    violations_sleep = 0
    violations_work  = 0
    total_sleep_night = 0
    total_work        = 0

    for s0 in range(N_SLOTS):
        a_col = f"act30_{s0+1:03d}"
        h_col = f"hom30_{s0+1:03d}"
        acts = syn_df[a_col].values
        home = syn_df[h_col].values

        # Sleep at night → must be home
        if s0 in NIGHT_SLOTS:
            mask = acts == SLEEP_RAW
            total_sleep_night += mask.sum()
            violations_sleep  += ((mask) & (home != 1)).sum()

        # Work → must not be home
        mask = acts == WORK_RAW
        total_work       += mask.sum()
        violations_work  += ((mask) & (home != 0)).sum()

    if total_sleep_night > 0:
        viol_pct = 100 * violations_sleep / total_sleep_night
        flag = "  OK" if viol_pct < 1 else "  WARNING"
        print(f"  Sleep@night not AT_HOME: {violations_sleep:,} / {total_sleep_night:,} ({viol_pct:.2f}%){flag}")
    if total_work > 0:
        viol_pct = 100 * violations_work / total_work
        flag = "  OK" if viol_pct < 1 else "  WARNING"
        print(f"  Work but AT_HOME=1:      {violations_work:,} / {total_work:,} ({viol_pct:.2f}%){flag}")

    # ── 6. Sample respondent ───────────────────────────────────────
    print("\n── 6. Sample respondent (first occID) ────────────────────")
    ex_id = df["occID"].iloc[0]
    ex_cy = df["CYCLE_YEAR"].iloc[0]
    ex    = df[(df["occID"] == ex_id) & (df["CYCLE_YEAR"] == ex_cy)].sort_values("DDAY_STRATA")

    SLOT_LABELS = [slot_label(s) for s in range(N_SLOTS)]
    for _, row in ex.iterrows():
        acts = [row[f"act30_{s:03d}"] for s in range(1, N_SLOTS + 1)]
        home = [row[f"hom30_{s:03d}"] for s in range(1, N_SLOTS + 1)]
        tag = "observed" if row["IS_SYNTHETIC"] == 0 else "synthetic"
        print(f"\n  DDAY_STRATA={row['DDAY_STRATA']} [{tag}]")
        # Print compact diary: 4 hours per line
        for line_start in range(0, N_SLOTS, 8):
            times = "  ".join(f"{SLOT_LABELS[s]:>5}" for s in range(line_start, line_start + 8))
            a_str = "  ".join(f"  {int(acts[s]):>2}" for s in range(line_start, line_start + 8))
            h_str = "  ".join(f"  {int(home[s]):>2}" for s in range(line_start, line_start + 8))
            if line_start == 0:
                print(f"    Time: {times}")
            print(f"    Act:  {a_str}")
            print(f"    Home: {h_str}")

    print("\n" + "=" * 60)
    print("Diagnostic complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
