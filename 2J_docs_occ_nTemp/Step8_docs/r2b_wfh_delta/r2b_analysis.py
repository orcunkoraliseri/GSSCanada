"""
Round-2b: WFH Delta contamination analysis.
Measures whether the 2022/2030 provenance gap contaminates the within-HH WFH Î”.

Steps:
  1. Sanity-check: reproduce R1 values for HH34299 (IDF wd mean â‰ˆ 0.736, CSV wd mean â‰ˆ 0.653)
  2. Extract paired weekday hourly occupancy from IDF and CSV for all paired HH
  3. Compute Î”_asbuilt, Î”_disk, DoD (difference-of-differences)
  4. Aggregate per cell and overall; classify CLEAN / GREY / CONTAMINATED
  5. Save per-cell CSV and summary table
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

import pandas as pd
import numpy as np

# â”€â”€â”€ Paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ROOT = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main")
SIM_ROOT = ROOT / "BEM_Setup" / "SimResults_Step8" / "campaign_N50"
CSV_2022 = ROOT / "BEM_Setup" / "BEM_Schedules_2022.csv"
CSV_2030 = ROOT / "BEM_Setup" / "BEM_Schedules_2030.csv"
OUT_DIR  = ROOT / "2J_docs_occ_nTemp" / "Step8_docs" / "r2b_wfh_delta"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Midday hours h9..h17 inclusive (9 hours covering 09:00â€“17:59)
MIDDAY_HOURS = list(range(9, 18))


# â”€â”€â”€ IDF parser â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def parse_idf_weekday_occ(idf_path: Path, hh_id: int) -> np.ndarray | None:
    """
    Extract 24-element weekday occupancy array from a Schedule:Compact IDF block.

    Strategy (robust to large files):
      1. Find the line containing "Occ_Sch_HH_<id>,"
      2. Scan backward to the opening "Schedule:Compact," line
      3. Scan forward from there to the closing ";" to extract the block
      4. Parse the weekday For: sub-block with a state machine

    Alignment: IDF "Until: HH:00" = value DURING [HH-1:00, HH:00).
    So Until:01:00 â†’ hour index 0; Until:24:00 â†’ hour index 23.
    """
    target_name = f"Occ_Sch_HH_{hh_id}"
    lines = idf_path.read_text(encoding="utf-8", errors="replace").splitlines()

    # Step 1: Find the name line
    name_line_idx = None
    for i, line in enumerate(lines):
        content = line.split("!")[0].strip()
        if content.rstrip(",;") == target_name:
            name_line_idx = i
            break

    if name_line_idx is None:
        return None

    # Step 2: Scan backward to find "Schedule:Compact,"
    block_start = None
    for i in range(name_line_idx, max(name_line_idx - 10, -1), -1):
        content = lines[i].split("!")[0].strip()
        if content == "Schedule:Compact,":
            block_start = i
            break

    if block_start is None:
        return None

    # Step 3: Scan forward from block_start to find closing ";"
    block_end = None
    for i in range(block_start, min(block_start + 500, len(lines))):
        content = lines[i].split("!")[0].strip()
        if content.endswith(";"):
            block_end = i
            break

    if block_end is None:
        return None

    block_lines = lines[block_start:block_end + 1]

    # Step 4: State machine over block lines
    in_weekday = False
    values = {}    # until_hour (1..24) â†’ float
    last_until = None

    for line in block_lines:
        content = line.split("!")[0].strip().rstrip(",").rstrip(";").strip()
        if not content:
            continue

        # Schedule:Compact, or name line â†’ skip
        if content == "Schedule:Compact," or content.rstrip(",") == target_name:
            continue

        # Fraction / Schedule Type
        if re.match(r'Fraction', content, re.IGNORECASE):
            continue

        # Through:
        if re.match(r'Through:', content, re.IGNORECASE):
            continue

        # For:
        m_for = re.match(r'For:\s*(.*)', content, re.IGNORECASE)
        if m_for:
            day_str = m_for.group(1).lower()
            in_weekday = "weekday" in day_str
            last_until = None
            continue

        # Until:
        m_until = re.match(r'Until:\s*(\d+):(\d+)', content, re.IGNORECASE)
        if m_until:
            last_until = int(m_until.group(1))  # 1..24
            continue

        # Value line
        if in_weekday and last_until is not None:
            try:
                val = float(content)
                values[last_until] = val
            except ValueError:
                pass

    if not values:
        return None

    # Build 24-element array: Until:HH â†’ fill hours [prev_until..HH-1]
    arr = np.full(24, np.nan)
    prev = 0
    for uh in sorted(values.keys()):
        for h in range(prev, min(uh, 24)):
            arr[h] = values[uh]
        prev = uh

    if np.any(np.isnan(arr)):
        return None

    return arr


# â”€â”€â”€ Discover all cells and paired HHs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def discover_pairs():
    """
    Returns:
      pairs: dict {(cell_name, hh_id): {'2022': Path, '2030': Path, 'cell': cell_name}}
      cell_counts: dict {cell_name: int}
    """
    cells = [d for d in SIM_ROOT.iterdir()
             if d.is_dir() and "__" in d.name and not d.name.startswith("_")]

    pairs = {}
    cell_counts = {}

    for cell_dir in sorted(cells):
        cell_name = cell_dir.name
        samples = [d for d in cell_dir.iterdir()
                   if d.is_dir() and d.name.startswith("sample_")]
        cell_pairs = 0

        for sample_dir in samples:
            m = re.match(r'sample_\d+_HH(\d+)', sample_dir.name)
            if not m:
                continue
            hh_id = int(m.group(1))

            idf_2022 = sample_dir / "2022" / "in.idf"
            idf_2030 = sample_dir / "2030" / "in.idf"

            if idf_2022.exists() and idf_2030.exists():
                pairs[(cell_name, hh_id)] = {
                    "2022": idf_2022,
                    "2030": idf_2030,
                    "cell": cell_name,
                }
                cell_pairs += 1

        cell_counts[cell_name] = cell_pairs
        print(f"  {cell_name}: {cell_pairs} paired HHs")

    print(f"\n  Total paired HHs: {len(pairs)}")
    return pairs, cell_counts


# â”€â”€â”€ CSV loader (memory-efficient chunked) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def load_csv_weekday(csv_path: Path, hh_ids: set) -> dict:
    """
    Load weekday occupancy from BEM_Schedules CSV for specific HH_IDs only.
    Reads in 200k-row chunks to avoid materialising the full 674 MB file.

    Returns: {hh_id: np.ndarray(24)} or {hh_id: None} if not found.
    CSV Hour column: 0..23.
    """
    print(f"  Loading {csv_path.name} for {len(hh_ids)} HHs...", flush=True)
    # Accumulators: sum and count per (hh_id, hour)
    acc_sum   = defaultdict(lambda: np.zeros(24))
    acc_count = defaultdict(lambda: np.zeros(24, dtype=int))

    hh_ids_set = set(int(x) for x in hh_ids)

    for chunk in pd.read_csv(
        csv_path,
        usecols=["SIM_HH_ID", "Day_Type", "Hour", "Occupancy_Schedule"],
        chunksize=200_000,
        dtype={"SIM_HH_ID": "int32", "Hour": "int8", "Occupancy_Schedule": "float32"},
    ):
        # Filter
        mask = (
            chunk["SIM_HH_ID"].isin(hh_ids_set) &
            chunk["Day_Type"].str.contains("Weekday", case=False, na=False)
        )
        sub = chunk[mask]
        if sub.empty:
            continue

        for row in sub.itertuples(index=False):
            hid = int(row.SIM_HH_ID)
            h   = int(row.Hour)
            v   = float(row.Occupancy_Schedule)
            if 0 <= h <= 23:
                acc_sum[hid][h]   += v
                acc_count[hid][h] += 1

    # Average
    final = {}
    for hid in hh_ids_set:
        c = acc_count[hid].copy()
        if np.all(c == 0):
            final[hid] = None
        else:
            c[c == 0] = 1
            final[hid] = acc_sum[hid] / c

    found = sum(1 for v in final.values() if v is not None)
    print(f"    Found {found}/{len(hh_ids_set)} HHs in {csv_path.name}")
    return final


# â”€â”€â”€ Main â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def run():
    print("=" * 70)
    print("Round-2b: WFH Delta contamination analysis")
    print("=" * 70)

    # â”€â”€ Step 0: Discover pairs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\n[STEP 0] Discovering paired HH directories...")
    pairs, cell_counts = discover_pairs()

    if not pairs:
        print("ERROR: No paired HHs found!")
        sys.exit(1)

    all_hh_ids = {hh_id for (_, hh_id) in pairs.keys()}

    # â”€â”€ Step 1: Sanity check â€” HH34299 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\n[STEP 1] Sanity check: HH34299 (2022 IDF vs 2022 CSV)")

    idf34299_path = SIM_ROOT / "SingleD__Toronto_5A" / "sample_001_HH34299" / "2022" / "in.idf"
    if not idf34299_path.exists():
        print("  ERROR: HH34299 IDF not found at expected path!")
        idf34299_arr = None
    else:
        idf34299_arr = parse_idf_weekday_occ(idf34299_path, 34299)
        if idf34299_arr is None:
            print("  ERROR: IDF parse failed for HH34299!")
        else:
            idf_mean = np.mean(idf34299_arr)
            print(f"  IDF weekday mean: {idf_mean:.4f}  (expected â‰ˆ 0.736)")
            print(f"  IDF per-hour:  {[round(float(v), 3) for v in idf34299_arr]}")

    # Temporarily load CSV just for HH34299 sanity check
    san = load_csv_weekday(CSV_2022, {34299})
    csv34299_arr = san.get(34299)
    if csv34299_arr is None:
        print("  ERROR: HH34299 not found in BEM_Schedules_2022.csv!")
    else:
        csv_mean = np.mean(csv34299_arr)
        print(f"  CSV weekday mean: {csv_mean:.4f}  (expected â‰ˆ 0.653)")
        print(f"  CSV per-hour:  {[round(float(v), 3) for v in csv34299_arr]}")

    # Sanity gate
    idf_ok = (idf34299_arr is not None and abs(np.mean(idf34299_arr) - 0.736) < 0.05)
    csv_ok = (csv34299_arr is not None and abs(np.mean(csv34299_arr) - 0.653) < 0.05)
    if not idf_ok:
        print("\n  *** IDF sanity check FAILED â€” check parser before trusting results! ***")
    if not csv_ok:
        print("\n  *** CSV sanity check FAILED â€” check Day_Type filter! ***")
    if idf_ok and csv_ok:
        print("\n  Sanity check PASSED. Proceeding.")

    # â”€â”€ Step 2: Extract IDF occupancy for ALL paired HHs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\n[STEP 2] Parsing IDF weekday occupancy (all paired HHs)...", flush=True)
    idf_data = {}   # (cell, hh_id, year) â†’ np.ndarray(24)
    failed_idf = []

    total = len(pairs) * 2
    done = 0
    for (cell, hh_id), info in pairs.items():
        for year in ("2022", "2030"):
            arr = parse_idf_weekday_occ(info[year], hh_id)
            if arr is None:
                failed_idf.append((cell, hh_id, year))
            else:
                idf_data[(cell, hh_id, year)] = arr
            done += 1
            if done % 50 == 0:
                print(f"    {done}/{total} IDFs parsed...", flush=True)

    print(f"  Done: {len(idf_data)} OK, {len(failed_idf)} failed")
    if failed_idf:
        for item in failed_idf[:10]:
            print(f"    FAIL: {item}")

    # â”€â”€ Step 3: Load CSVs for all paired HHs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\n[STEP 3] Loading BEM_Schedules CSVs (weekday, sampled HHs only)...", flush=True)
    csv_2022_data = load_csv_weekday(CSV_2022, all_hh_ids)
    csv_2030_data = load_csv_weekday(CSV_2030, all_hh_ids)

    # â”€â”€ Step 4: Compute Î” per HH â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\n[STEP 4] Computing Î”_asbuilt, Î”_disk, DoD per paired HH...", flush=True)

    records = []
    skipped = 0

    for (cell, hh_id) in sorted(pairs.keys()):
        idf22 = idf_data.get((cell, hh_id, "2022"))
        idf30 = idf_data.get((cell, hh_id, "2030"))
        csv22 = csv_2022_data.get(hh_id)
        csv30 = csv_2030_data.get(hh_id)

        if any(x is None for x in [idf22, idf30, csv22, csv30]):
            skipped += 1
            continue

        delta_ab   = idf30 - idf22    # (24,)
        delta_disk = csv30 - csv22    # (24,)
        dod        = delta_ab - delta_disk  # (24,)

        midday_sl = slice(MIDDAY_HOURS[0], MIDDAY_HOURS[-1] + 1)

        midday_dod  = float(np.mean(dod[midday_sl]))
        midday_ab   = float(np.mean(delta_ab[midday_sl]))
        midday_disk = float(np.mean(delta_disk[midday_sl]))
        max_abs_dod = float(np.max(np.abs(dod)))

        peak_h_ab   = int(np.argmax(delta_ab))
        peak_h_disk = int(np.argmax(delta_disk))

        wfh_dir_ab   = int(np.sign(midday_ab))
        wfh_dir_disk = int(np.sign(midday_disk))
        dir_preserved = (wfh_dir_ab == wfh_dir_disk)

        records.append({
            "cell": cell,
            "hh_id": hh_id,
            "midday_dod_pp":  round(midday_dod  * 100, 4),
            "midday_ab_pp":   round(midday_ab   * 100, 4),
            "midday_disk_pp": round(midday_disk * 100, 4),
            "max_abs_dod_pp": round(max_abs_dod * 100, 4),
            "peak_h_ab":    peak_h_ab,
            "peak_h_disk":  peak_h_disk,
            "peak_shift":   peak_h_ab - peak_h_disk,
            "wfh_dir_ab":   wfh_dir_ab,
            "wfh_dir_disk": wfh_dir_disk,
            "dir_preserved": dir_preserved,
            # per-hour arrays stored separately for aggregation
            "_dod":       dod,
            "_delta_ab":  delta_ab,
            "_delta_disk": delta_disk,
        })

    print(f"  Processed: {len(records)} HHs, skipped: {skipped} (missing data)")

    # â”€â”€ Step 5: Aggregate â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\n[STEP 5] Aggregating per cell and overall...", flush=True)

    # Per-HH CSV (no internal arrays)
    df = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")}
                       for r in records])
    df.to_csv(OUT_DIR / "r2b_per_hh.csv", index=False)
    print(f"  Saved r2b_per_hh.csv ({len(df)} rows)")

    midday_sl = slice(MIDDAY_HOURS[0], MIDDAY_HOURS[-1] + 1)

    # Per-cell
    cell_rows = []
    for cell in sorted(df["cell"].unique()):
        sub_df  = df[df["cell"] == cell]
        sub_rec = [r for r in records if r["cell"] == cell]

        mean_dod_h  = np.mean([r["_dod"]       for r in sub_rec], axis=0)
        mean_ab_h   = np.mean([r["_delta_ab"]   for r in sub_rec], axis=0)
        mean_disk_h = np.mean([r["_delta_disk"] for r in sub_rec], axis=0)

        cell_rows.append({
            "cell": cell,
            "n_hh": len(sub_df),
            "midday_dod_pp":       round(float(np.mean(mean_dod_h [midday_sl])) * 100, 3),
            "midday_ab_pp":        round(float(np.mean(mean_ab_h  [midday_sl])) * 100, 3),
            "midday_disk_pp":      round(float(np.mean(mean_disk_h[midday_sl])) * 100, 3),
            "max_abs_dod_pp":      round(float(sub_df["max_abs_dod_pp"].max()), 3),
            "pct_dir_preserved":   round(float(sub_df["dir_preserved"].mean() * 100), 1),
            "peak_shift_mode":     int(sub_df["peak_shift"].mode().iloc[0]) if len(sub_df) > 0 else None,
        })

    cell_df = pd.DataFrame(cell_rows)
    cell_df.to_csv(OUT_DIR / "r2b_per_cell.csv", index=False)
    print(f"  Saved r2b_per_cell.csv ({len(cell_df)} rows)")

    # Overall
    all_dod_h   = np.mean([r["_dod"]       for r in records], axis=0)
    all_ab_h    = np.mean([r["_delta_ab"]   for r in records], axis=0)
    all_disk_h  = np.mean([r["_delta_disk"] for r in records], axis=0)

    ov_midday_dod_pp  = float(np.mean(all_dod_h [midday_sl])) * 100
    ov_midday_ab_pp   = float(np.mean(all_ab_h  [midday_sl])) * 100
    ov_midday_disk_pp = float(np.mean(all_disk_h[midday_sl])) * 100
    ov_max_abs_dod_pp = float(df["max_abs_dod_pp"].max())

    ov_peak_ab   = int(np.argmax(all_ab_h))
    ov_peak_disk = int(np.argmax(all_disk_h))
    ov_peak_shift = ov_peak_ab - ov_peak_disk

    pct_dir_preserved = float(df["dir_preserved"].mean()) * 100

    worst_idx = cell_df["midday_dod_pp"].abs().idxmax()
    worst_cell = cell_df.loc[worst_idx]

    # â”€â”€ Print results â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"\n  Total paired HHs analysed : {len(records)}")
    print(f"  Cells covered             : {len(cell_df)}")

    print(f"\n  OVERALL (mean across all HH):")
    print(f"    Midday Î”_asbuilt (pp) : {ov_midday_ab_pp:+.3f}")
    print(f"    Midday Î”_disk    (pp) : {ov_midday_disk_pp:+.3f}")
    print(f"    Midday DoD       (pp) : {ov_midday_dod_pp:+.3f}   â† key metric")
    print(f"    Max|DoD| (pp)         : {ov_max_abs_dod_pp:.3f}   (worst HH, worst hour)")
    print(f"    Peak WFH hour as-built: h{ov_peak_ab}  ({ov_peak_ab}:00â€“{ov_peak_ab+1}:00)")
    print(f"    Peak WFH hour disk    : h{ov_peak_disk}  ({ov_peak_disk}:00â€“{ov_peak_disk+1}:00)")
    print(f"    Peak-hour shift       : {ov_peak_shift:+d}h")
    print(f"    WFH dir preserved     : {pct_dir_preserved:.1f}% of HHs")

    print(f"\n  WORST CELL: {worst_cell['cell']}")
    print(f"    Midday DoD : {worst_cell['midday_dod_pp']:+.3f} pp")
    print(f"    Max|DoD|   : {worst_cell['max_abs_dod_pp']:.3f} pp")
    print(f"    Dir%       : {worst_cell['pct_dir_preserved']:.1f}%")

    print("\n  PER-CELL TABLE:")
    hdr = f"  {'Cell':<32} {'N':>4} {'MidDay_DoD_pp':>14} {'MaxDoD_pp':>10} {'Dir%':>6} {'PkShift':>8}"
    print(hdr)
    print("  " + "-" * 76)
    for _, row in cell_df.iterrows():
        print(f"  {row['cell']:<32} {row['n_hh']:>4} "
              f"{row['midday_dod_pp']:>+13.3f} "
              f"{row['max_abs_dod_pp']:>9.3f} "
              f"{row['pct_dir_preserved']:>5.1f}% "
              f"{row['peak_shift_mode']:>+7}h")

    # â”€â”€ Classification â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\n  CLASSIFICATION THRESHOLDS:")
    print("    CLEAN        : midday |DoD| â‰¤ 1.0 pp AND peak_shift=0 AND dir 100%")
    print("    GREY         : midday |DoD| 1.0â€“1.5 pp  (flag for manager)")
    print("    CONTAMINATED : midday |DoD| > 1.5 pp OR peak_shiftâ‰ 0 OR dir flip")

    flags = []
    abs_dod = abs(ov_midday_dod_pp)
    if abs_dod > 1.5:
        flags.append(f"midday|DoD|={abs_dod:.3f}pp > 1.5pp threshold")
    if ov_peak_shift != 0:
        flags.append(f"peak-hour shift={ov_peak_shift:+d}h (as-built h{ov_peak_ab} vs disk h{ov_peak_disk})")
    if pct_dir_preserved < 100.0:
        n_flips = int((1 - df["dir_preserved"].mean()) * len(df))
        flags.append(f"WFH direction flipped in {n_flips} HHs ({100-pct_dir_preserved:.1f}%)")
    # Worst cell
    wc_abs = abs(float(worst_cell["midday_dod_pp"]))
    if wc_abs > 1.5:
        flags.append(f"worst-cell '{worst_cell['cell']}' midday|DoD|={worst_cell['midday_dod_pp']:+.3f}pp > 1.5pp")

    if flags:
        verdict = "CONTAMINATED"
    elif abs_dod <= 1.0 and ov_peak_shift == 0 and pct_dir_preserved == 100.0:
        verdict = "CLEAN"
    else:
        verdict = "GREY"

    print(f"\n  VERDICT: *** {verdict} ***")
    if flags:
        for f in flags:
            print(f"    FLAG: {f}")
    else:
        print("    No contamination flags raised.")

    # â”€â”€ Per-hour overall DoD table â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\n  PER-HOUR OVERALL MEAN (Î”_ab, Î”_disk, DoD in pp):")
    print(f"  {'Hour':>4} {'Î”_ab':>8} {'Î”_disk':>8} {'DoD':>8} {'|DoD|':>7}")
    print("  " + "-" * 40)
    for h in range(24):
        mid_flag = "*" if h in MIDDAY_HOURS else " "
        print(f"  {h:>4}{mid_flag} {all_ab_h[h]*100:>+7.3f}  {all_disk_h[h]*100:>+7.3f}  "
              f"{all_dod_h[h]*100:>+7.3f}  {abs(all_dod_h[h])*100:>6.3f}")

    # â”€â”€ Save summary markdown â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    idf_note = f"IDF wd mean HH34299: {np.mean(idf34299_arr):.4f}" if idf34299_arr is not None else "IDF sanity: FAILED"
    csv_note = f"CSV wd mean HH34299: {np.mean(csv34299_arr):.4f}" if csv34299_arr is not None else "CSV sanity: FAILED"

    summary = f"""# Round-2b WFH Delta Analysis â€” Summary

## Sanity Check (HH34299, 2022)
- {idf_note}  (expected â‰ˆ 0.736)
- {csv_note}  (expected â‰ˆ 0.653)

## Dataset
- Paired HHs analysed: {len(records)}
- Cells covered: {len(cell_df)}
- HHs skipped (missing data): {skipped}

## Overall Metrics (h9â€“h17 midday window)
| Metric | Value |
|--------|-------|
| Midday Î”_asbuilt | {ov_midday_ab_pp:+.3f} pp |
| Midday Î”_disk | {ov_midday_disk_pp:+.3f} pp |
| Midday DoD (key) | {ov_midday_dod_pp:+.3f} pp |
| Max |DoD| (any HH, any hour) | {ov_max_abs_dod_pp:.3f} pp |
| Peak WFH hour as-built | h{ov_peak_ab} |
| Peak WFH hour disk | h{ov_peak_disk} |
| Peak-hour shift | {ov_peak_shift:+d}h |
| WFH direction preserved | {pct_dir_preserved:.1f}% |

## Worst Cell
- {worst_cell['cell']}: midday DoD={worst_cell['midday_dod_pp']:+.3f} pp, max|DoD|={worst_cell['max_abs_dod_pp']:.3f} pp, dir={worst_cell['pct_dir_preserved']:.1f}%

## Per-Cell Table
| Cell | N | MidDay_DoD_pp | MaxDoD_pp | Dir% | PkShift |
|------|---|---------------|-----------|------|---------|
"""
    for _, row in cell_df.iterrows():
        summary += (f"| {row['cell']} | {row['n_hh']} | {row['midday_dod_pp']:+.3f} | "
                    f"{row['max_abs_dod_pp']:.3f} | {row['pct_dir_preserved']:.1f}% | "
                    f"{row['peak_shift_mode']:+d}h |\n")

    summary += f"""
## Classification
**VERDICT: {verdict}**

Thresholds:
- CLEAN: midday |DoD| â‰¤ 1.0 pp AND peak_shift = 0h AND dir preserved 100%
- GREY: midday |DoD| 1.0â€“1.5 pp
- CONTAMINATED: midday |DoD| > 1.5 pp OR peak_shift â‰  0h OR direction flip
"""
    if flags:
        summary += "\nFlags raised:\n"
        for f in flags:
            summary += f"- {f}\n"
    else:
        summary += "\nNo contamination flags raised.\n"

    (OUT_DIR / "r2b_summary.md").write_text(summary, encoding="utf-8")
    print(f"\n  Saved r2b_summary.md")
    print("\nDone.")


if __name__ == "__main__":
    run()

