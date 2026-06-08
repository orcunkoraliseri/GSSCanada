"""
Round-2c: Output-level sensitivity check.
Estimates per-HH DELTA_EUI = (EUI if disk schedules used) - (as-run EUI)
using the empirical EUI-vs-occupancy slope within each (cell, year).
Determines whether the 2022/2030 provenance gap moves EUI beyond the
MC CI half-width of 1.80%.

NO new simulation — reads only existing eplustbl.csv outputs and IDF/CSV schedules.

Steps:
  1. Discover all paired HH directories
  2. Extract EUI (and peak demand) from each run's eplustbl.csv
  3. Extract as-built weekday occupancy from each IDF (reuse r2b parser)
  4. Load disk weekday occupancy from BEM_Schedules CSVs (reuse r2b loader)
  5. Join sanity: confirm HH34299/2022 IDF wd mean ≈ 0.736, N rows per year
  6. Per (cell, year): regress EUI on daily-mean as-built occupancy → slope, R²
  7. Per HH: DELTA_EUI_est = slope × (occ_disk - occ_idf), as % of cell mean EUI
  8. Aggregate: mean |DELTA_EUI%| and worst |DELTA_EUI%| per cell, overall
  9. Paired/WFH impact: slope × (Docc_2030 - Docc_2022)
 10. Save per-cell CSV and summary markdown
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy import stats

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT     = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main")
SIM_ROOT = ROOT / "BEM_Setup" / "SimResults_Step8" / "campaign_N50"
CSV_2022 = ROOT / "BEM_Setup" / "BEM_Schedules_2022.csv"
CSV_2030 = ROOT / "BEM_Setup" / "BEM_Schedules_2030.csv"
OUT_DIR  = ROOT / "2J_docs_occ_nTemp" / "Step8_docs" / "r2c_output_sensitivity"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MC_CI_HALFWIDTH = 1.80   # % — from 8F report gate 3.2

MIDDAY_HOURS = list(range(9, 18))   # h9..h17 inclusive


# ── IDF parser (verbatim from r2b_analysis.py) ────────────────────────────────

def parse_idf_weekday_occ(idf_path: Path, hh_id: int) -> np.ndarray | None:
    """Return 24-element weekday occupancy array from IDF Schedule:Compact block."""
    target_name = f"Occ_Sch_HH_{hh_id}"
    lines = idf_path.read_text(encoding="utf-8", errors="replace").splitlines()

    name_line_idx = None
    for i, line in enumerate(lines):
        content = line.split("!")[0].strip()
        if content.rstrip(",;") == target_name:
            name_line_idx = i
            break
    if name_line_idx is None:
        return None

    block_start = None
    for i in range(name_line_idx, max(name_line_idx - 10, -1), -1):
        content = lines[i].split("!")[0].strip()
        if content == "Schedule:Compact,":
            block_start = i
            break
    if block_start is None:
        return None

    block_end = None
    for i in range(block_start, min(block_start + 500, len(lines))):
        content = lines[i].split("!")[0].strip()
        if content.endswith(";"):
            block_end = i
            break
    if block_end is None:
        return None

    block_lines = lines[block_start:block_end + 1]

    in_weekday = False
    values = {}
    last_until = None

    for line in block_lines:
        content = line.split("!")[0].strip().rstrip(",").rstrip(";").strip()
        if not content:
            continue
        if content == "Schedule:Compact," or content.rstrip(",") == target_name:
            continue
        if re.match(r'Fraction', content, re.IGNORECASE):
            continue
        if re.match(r'Through:', content, re.IGNORECASE):
            continue
        m_for = re.match(r'For:\s*(.*)', content, re.IGNORECASE)
        if m_for:
            day_str = m_for.group(1).lower()
            in_weekday = "weekday" in day_str
            last_until = None
            continue
        m_until = re.match(r'Until:\s*(\d+):(\d+)', content, re.IGNORECASE)
        if m_until:
            last_until = int(m_until.group(1))
            continue
        if in_weekday and last_until is not None:
            try:
                val = float(content)
                values[last_until] = val
            except ValueError:
                pass

    if not values:
        return None

    arr = np.full(24, np.nan)
    prev = 0
    for uh in sorted(values.keys()):
        for h in range(prev, min(uh, 24)):
            arr[h] = values[uh]
        prev = uh

    if np.any(np.isnan(arr)):
        return None
    return arr


# ── CSV loader (verbatim from r2b_analysis.py) ────────────────────────────────

def load_csv_weekday(csv_path: Path, hh_ids: set) -> dict:
    """Load weekday occupancy from BEM_Schedules CSV for specific HH_IDs."""
    print(f"  Loading {csv_path.name} for {len(hh_ids)} HHs...", flush=True)
    acc_sum   = defaultdict(lambda: np.zeros(24))
    acc_count = defaultdict(lambda: np.zeros(24, dtype=int))
    hh_ids_set = set(int(x) for x in hh_ids)

    for chunk in pd.read_csv(
        csv_path,
        usecols=["SIM_HH_ID", "Day_Type", "Hour", "Occupancy_Schedule"],
        chunksize=200_000,
        dtype={"SIM_HH_ID": "int32", "Hour": "int8", "Occupancy_Schedule": "float32"},
    ):
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


# ── Discover pairs (adapted from r2b_analysis.py) ────────────────────────────

def discover_pairs():
    cells = [d for d in SIM_ROOT.iterdir()
             if d.is_dir() and "__" in d.name and not d.name.startswith("_")]
    pairs = {}
    for cell_dir in sorted(cells):
        cell_name = cell_dir.name
        samples = [d for d in cell_dir.iterdir()
                   if d.is_dir() and d.name.startswith("sample_")]
        for sample_dir in samples:
            m = re.match(r'sample_\d+_HH(\d+)', sample_dir.name)
            if not m:
                continue
            hh_id = int(m.group(1))
            idf_2022 = sample_dir / "2022" / "in.idf"
            idf_2030 = sample_dir / "2030" / "in.idf"
            if idf_2022.exists() and idf_2030.exists():
                pairs[(cell_name, hh_id)] = {
                    "2022": sample_dir / "2022",
                    "2030": sample_dir / "2030",
                    "cell": cell_name,
                }
    print(f"  Total paired HHs: {len(pairs)}")
    return pairs


# ── EUI extractor ────────────────────────────────────────────────────────────

def extract_eui(run_dir: Path) -> dict | None:
    """
    Extract from eplustbl.csv:
      - eui_site_total_kbtu_ft2:   Total Site Energy per total building area
      - eui_site_cond_kbtu_ft2:    Total Site Energy per conditioned building area
      - peak_elec_kbtuh:           Peak electricity demand (Total End Uses, Demand section)
      - cond_area_ft2:             Conditioned building area

    Returns None if file missing or parse fails.
    """
    tbl = run_dir / "eplustbl.csv"
    if not tbl.exists():
        return None
    try:
        lines = tbl.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return None

    result = {}
    in_demand_section = False

    for line in lines:
        # EUI: "Total Site Energy" line in Annual Building Utility Performance Summary
        if not in_demand_section and line.startswith(",Total Site Energy,"):
            parts = line.split(",")
            # parts[0]='', parts[1]='Total Site Energy', parts[2]=total_kbtu,
            # parts[3]=per_total_area_kbtu_ft2, parts[4]=per_cond_area_kbtu_ft2
            try:
                result["eui_site_total_kbtu_ft2"] = float(parts[3])
                result["eui_site_cond_kbtu_ft2"]  = float(parts[4])
            except (IndexError, ValueError):
                pass

        # Building area
        if not in_demand_section and ",Net Conditioned Building Area," in line:
            parts = line.split(",")
            try:
                result["cond_area_ft2"] = float(parts[2])
            except (IndexError, ValueError):
                pass

        # Detect entry into Demand End Use section
        if "REPORT:,Demand End Use Components Summary" in line:
            in_demand_section = True

        # Peak total end uses (electricity col=2) in demand section
        if in_demand_section and line.startswith(",Total End Uses,"):
            parts = line.split(",")
            try:
                result["peak_elec_kbtuh"] = float(parts[2])
            except (IndexError, ValueError):
                pass
            in_demand_section = False  # done

    if "eui_site_cond_kbtu_ft2" not in result:
        return None
    return result


# ── Main ─────────────────────────────────────────────────────────────────────

def run():
    print("=" * 70)
    print("Round-2c: Output-level EUI sensitivity analysis")
    print(f"  MC CI half-width target: {MC_CI_HALFWIDTH:.2f}%")
    print("=" * 70)

    # ── Step 0: Discover pairs ─────────────────────────────────────────────
    print("\n[STEP 0] Discovering paired HH directories...")
    pairs = discover_pairs()
    if not pairs:
        print("ERROR: No paired HHs found!")
        sys.exit(1)
    all_hh_ids = {hh_id for (_, hh_id) in pairs.keys()}

    # ── Step 1: Extract EUI for all 2022 + 2030 runs ─────────────────────
    print("\n[STEP 1] Extracting EUI from eplustbl.csv (2022 + 2030)...", flush=True)
    eui_data = {}   # (cell, hh_id, year) → dict with eui etc.
    failed_eui = []
    done = 0
    total = len(pairs) * 2
    for (cell, hh_id), info in pairs.items():
        for year in ("2022", "2030"):
            res = extract_eui(info[year])
            if res is None:
                failed_eui.append((cell, hh_id, year))
            else:
                eui_data[(cell, hh_id, year)] = res
            done += 1
            if done % 100 == 0:
                print(f"    {done}/{total} eplustbl.csv parsed...", flush=True)
    print(f"  Done: {len(eui_data)} OK, {len(failed_eui)} failed")
    if failed_eui:
        for item in failed_eui[:10]:
            print(f"    FAIL: {item}")

    # ── Step 2: Parse IDF weekday occupancy for 2022 + 2030 ───────────────
    print("\n[STEP 2] Parsing IDF weekday occupancy (2022 + 2030)...", flush=True)
    idf_data = {}   # (cell, hh_id, year) → np.ndarray(24)
    failed_idf = []
    done = 0
    for (cell, hh_id), info in pairs.items():
        for year in ("2022", "2030"):
            idf_path = info[year] / "in.idf"
            arr = parse_idf_weekday_occ(idf_path, hh_id)
            if arr is None:
                failed_idf.append((cell, hh_id, year))
            else:
                idf_data[(cell, hh_id, year)] = arr
            done += 1
            if done % 100 == 0:
                print(f"    {done}/{total} IDFs parsed...", flush=True)
    print(f"  Done: {len(idf_data)} OK, {len(failed_idf)} failed")

    # ── Step 3: Load CSV weekday occupancy ─────────────────────────────────
    print("\n[STEP 3] Loading BEM_Schedules CSVs (2022 + 2030)...", flush=True)
    csv_2022_data = load_csv_weekday(CSV_2022, all_hh_ids)
    csv_2030_data = load_csv_weekday(CSV_2030, all_hh_ids)

    # ── Step 4: Join sanity + build per-HH table ───────────────────────────
    print("\n[STEP 4] Join sanity + building per-HH data table...", flush=True)

    # Sanity: HH34299 / 2022 IDF wd mean
    idf34299 = idf_data.get(("SingleD__Toronto_5A", 34299, "2022"))
    if idf34299 is not None:
        idf34299_mean = float(np.mean(idf34299))
        ok = abs(idf34299_mean - 0.736) < 0.05
        print(f"  SANITY HH34299/2022 IDF wd mean: {idf34299_mean:.4f}  "
              f"(expected ~0.736) -> {'PASS' if ok else 'FAIL'}")
    else:
        print("  SANITY HH34299/2022 IDF: NOT FOUND")

    # Build records for 2022 and 2030
    records = []  # one row per (cell, hh_id, year)
    skipped = 0

    for year in ("2022", "2030"):
        csv_data = csv_2022_data if year == "2022" else csv_2030_data
        for (cell, hh_id) in sorted(pairs.keys()):
            eui_res = eui_data.get((cell, hh_id, year))
            idf_arr = idf_data.get((cell, hh_id, year))
            csv_arr = csv_data.get(hh_id)
            if eui_res is None or idf_arr is None or csv_arr is None:
                skipped += 1
                continue

            midday_sl = slice(MIDDAY_HOURS[0], MIDDAY_HOURS[-1] + 1)
            occ_idf_daily  = float(np.mean(idf_arr))
            occ_idf_midday = float(np.mean(idf_arr[midday_sl]))
            occ_csv_daily  = float(np.mean(csv_arr))
            occ_csv_midday = float(np.mean(csv_arr[midday_sl]))

            records.append({
                "cell":             cell,
                "hh_id":            hh_id,
                "year":             year,
                "eui_cond":         eui_res["eui_site_cond_kbtu_ft2"],
                "eui_total":        eui_res["eui_site_total_kbtu_ft2"],
                "peak_elec_kbtuh":  eui_res.get("peak_elec_kbtuh", np.nan),
                "cond_area_ft2":    eui_res.get("cond_area_ft2", np.nan),
                "occ_idf_daily":    occ_idf_daily,
                "occ_idf_midday":   occ_idf_midday,
                "occ_csv_daily":    occ_csv_daily,
                "occ_csv_midday":   occ_csv_midday,
                "docc_daily":       occ_csv_daily  - occ_idf_daily,
                "docc_midday":      occ_csv_midday - occ_idf_midday,
            })

    df = pd.DataFrame(records)
    print(f"  Records built: {len(df)} total "
          f"(2022: {(df.year=='2022').sum()}, 2030: {(df.year=='2030').sum()}), "
          f"skipped: {skipped}")

    # ── Step 5: Per-cell regression EUI ~ occ_idf_daily ───────────────────
    print("\n[STEP 5] Per-cell regression EUI ~ daily-mean as-built occ...", flush=True)

    cells = sorted(df["cell"].unique())
    years = ["2022", "2030"]

    cell_year_stats = {}   # (cell, year) → dict

    for cell in cells:
        for year in years:
            sub = df[(df["cell"] == cell) & (df["year"] == year)].copy()
            if len(sub) < 3:
                continue
            x = sub["occ_idf_daily"].values
            y_eui = sub["eui_cond"].values
            has_peak = sub["peak_elec_kbtuh"].notna().all()
            y_peak = sub["peak_elec_kbtuh"].values if has_peak else None

            # EUI regression
            slope_eui, intercept_eui, r_eui, p_eui, _ = stats.linregress(x, y_eui)
            r2_eui = r_eui ** 2

            # Peak regression (optional)
            if y_peak is not None:
                slope_peak, _, r_peak, _, _ = stats.linregress(x, y_peak)
                r2_peak = r_peak ** 2
            else:
                slope_peak = np.nan
                r2_peak    = np.nan

            cell_year_stats[(cell, year)] = {
                "cell":        cell,
                "year":        year,
                "n_hh":        len(sub),
                "mean_eui":    float(np.mean(y_eui)),
                "mean_occ_idf": float(np.mean(x)),
                "slope_eui":   float(slope_eui),
                "r2_eui":      float(r2_eui),
                "mean_docc_daily": float(np.mean(sub["docc_daily"])),
                "slope_peak":  float(slope_peak) if y_peak is not None else np.nan,
                "r2_peak":     float(r2_peak) if y_peak is not None else np.nan,
            }

    # ── Step 6: Per-HH DELTA_EUI estimate ─────────────────────────────────
    print("\n[STEP 6] Estimating per-HH DELTA_EUI...", flush=True)

    for idx, row in df.iterrows():
        key = (row["cell"], row["year"])
        stats_row = cell_year_stats.get(key)
        if stats_row is None or stats_row["mean_eui"] == 0:
            df.at[idx, "deui_est_kbtu_ft2"] = np.nan
            df.at[idx, "deui_est_pct"]      = np.nan
            df.at[idx, "dpeak_est_kbtuh"]    = np.nan
            df.at[idx, "dpeak_est_pct"]      = np.nan
            continue

        slope_eui  = stats_row["slope_eui"]
        mean_eui   = stats_row["mean_eui"]
        slope_peak = stats_row["slope_peak"]
        docc       = row["docc_daily"]

        deui_abs = slope_eui * docc
        deui_pct = 100.0 * deui_abs / mean_eui

        dpeak_abs = slope_peak * docc if not np.isnan(slope_peak) else np.nan
        # express peak % vs mean EUI (as a normalised sensitivity)
        dpeak_pct = 100.0 * dpeak_abs / mean_eui if not np.isnan(dpeak_abs) else np.nan

        df.at[idx, "deui_est_kbtu_ft2"] = deui_abs
        df.at[idx, "deui_est_pct"]      = deui_pct
        df.at[idx, "dpeak_est_kbtuh"]   = dpeak_abs
        df.at[idx, "dpeak_est_pct"]     = dpeak_pct

    df.to_csv(OUT_DIR / "r2c_per_hh.csv", index=False)
    print(f"  Saved r2c_per_hh.csv ({len(df)} rows)")

    # ── Step 7: Paired / WFH impact ───────────────────────────────────────
    print("\n[STEP 7] Computing paired (WFH 2030-2022) impact...", flush=True)

    # Join 2022 and 2030 per HH/cell
    df22 = df[df["year"] == "2022"].set_index(["cell", "hh_id"])
    df30 = df[df["year"] == "2030"].set_index(["cell", "hh_id"])
    paired_rows = []
    for key in df22.index.intersection(df30.index):
        cell, hh_id = key
        r22 = df22.loc[key]
        r30 = df30.loc[key]
        stats22 = cell_year_stats.get((cell, "2022"))
        stats30 = cell_year_stats.get((cell, "2030"))
        if stats22 is None or stats30 is None:
            continue

        # Within-HH WFH delta of Docc: Docc_2030 - Docc_2022
        wfh_docc = r30["docc_daily"] - r22["docc_daily"]
        # Use 2022 slope (the "WFH impact" is the average year's slope — use mean)
        mean_slope = 0.5 * (stats22["slope_eui"] + stats30["slope_eui"])
        mean_eui   = 0.5 * (stats22["mean_eui"]  + stats30["mean_eui"])
        if mean_eui == 0:
            continue

        paired_deui_abs = mean_slope * wfh_docc
        paired_deui_pct = 100.0 * paired_deui_abs / mean_eui

        paired_rows.append({
            "cell":           cell,
            "hh_id":          hh_id,
            "docc_2022":      r22["docc_daily"],
            "docc_2030":      r30["docc_daily"],
            "wfh_docc":       wfh_docc,
            "paired_deui_abs": paired_deui_abs,
            "paired_deui_pct": paired_deui_pct,
        })

    df_paired = pd.DataFrame(paired_rows)
    print(f"  Paired records: {len(df_paired)}")

    # ── Step 8: Aggregate per cell and overall ────────────────────────────
    print("\n[STEP 8] Aggregating per cell and overall...", flush=True)

    cell_rows_out = []
    for cell in cells:
        for year in years:
            sub = df[(df["cell"] == cell) & (df["year"] == year) &
                     df["deui_est_pct"].notna()]
            stats_row = cell_year_stats.get((cell, year), {})
            if sub.empty:
                continue
            mean_abs_pct  = float(sub["deui_est_pct"].abs().mean())
            worst_abs_pct = float(sub["deui_est_pct"].abs().max())
            mean_docc     = float(sub["docc_daily"].mean())
            mean_abs_docc = float(sub["docc_daily"].abs().mean())

            # Paired for this cell
            sub_p = df_paired[df_paired["cell"] == cell]
            paired_mean_abs = float(sub_p["paired_deui_pct"].abs().mean()) if not sub_p.empty else np.nan
            paired_worst    = float(sub_p["paired_deui_pct"].abs().max())  if not sub_p.empty else np.nan

            cell_rows_out.append({
                "cell":          cell,
                "year":          year,
                "n_hh":          stats_row.get("n_hh", len(sub)),
                "slope_eui":     round(stats_row.get("slope_eui", np.nan), 4),
                "r2_eui":        round(stats_row.get("r2_eui",    np.nan), 4),
                "mean_eui":      round(stats_row.get("mean_eui",  np.nan), 2),
                "mean_docc":     round(mean_docc, 4),
                "mean_abs_docc": round(mean_abs_docc, 4),
                "mean_abs_deui_pct":  round(mean_abs_pct, 4),
                "worst_abs_deui_pct": round(worst_abs_pct, 4),
                "paired_mean_abs_deui_pct":  round(paired_mean_abs, 4) if not np.isnan(paired_mean_abs) else np.nan,
                "paired_worst_abs_deui_pct": round(paired_worst, 4)    if not np.isnan(paired_worst)    else np.nan,
                "slope_peak":    round(stats_row.get("slope_peak", np.nan), 4),
                "r2_peak":       round(stats_row.get("r2_peak",    np.nan), 4),
            })

    cell_df_out = pd.DataFrame(cell_rows_out)
    cell_df_out.to_csv(OUT_DIR / "r2c_per_cell.csv", index=False)
    print(f"  Saved r2c_per_cell.csv ({len(cell_df_out)} rows)")

    # ── Overall metrics ───────────────────────────────────────────────────
    for year in years:
        sub_all = df[(df["year"] == year) & df["deui_est_pct"].notna()]
        ov_mean_abs  = float(sub_all["deui_est_pct"].abs().mean())
        ov_worst     = float(sub_all["deui_est_pct"].abs().max())
        worst_cell_idx = sub_all["deui_est_pct"].abs().idxmax()
        worst_cell_hh  = sub_all.loc[worst_cell_idx, "cell"]

        paired_all = df_paired if year == "2022" else df_paired  # only one set
        paired_ov_mean  = float(df_paired["paired_deui_pct"].abs().mean())
        paired_ov_worst = float(df_paired["paired_deui_pct"].abs().max())

        cell_sub = cell_df_out[cell_df_out["year"] == year]
        worst_cell_row = cell_sub.loc[cell_sub["worst_abs_deui_pct"].idxmax()]

        print(f"\n  ── YEAR {year} OVERALL ──")
        print(f"    Mean |ΔEUI%|  (level):  {ov_mean_abs:.3f}%")
        print(f"    Worst |ΔEUI%| (level):  {ov_worst:.3f}%  (HH in {worst_cell_hh})")
        print(f"    Worst CELL mean |ΔEUI%|: {worst_cell_row['mean_abs_deui_pct']:.3f}%  "
              f"({worst_cell_row['cell']})")
        print(f"    MC CI half-width:        {MC_CI_HALFWIDTH:.2f}%")
        if year == "2022":
            print(f"\n    Paired / WFH impact:")
            print(f"      Mean |ΔEUI%|:  {paired_ov_mean:.3f}%")
            print(f"      Worst |ΔEUI%|: {paired_ov_worst:.3f}%")

    # ── Classification ────────────────────────────────────────────────────
    sub_all_all = df[df["deui_est_pct"].notna()]
    overall_mean = float(sub_all_all["deui_est_pct"].abs().mean())
    overall_worst = float(sub_all_all["deui_est_pct"].abs().max())
    paired_mean  = float(df_paired["paired_deui_pct"].abs().mean())

    # ── Hand-check summary for one cell ──────────────────────────────────
    print("\n[HAND-CHECK] SingleD__Toronto_5A / 2022 — 3 sample HHs:")
    sub_check = df[(df["cell"] == "SingleD__Toronto_5A") & (df["year"] == "2022")].head(3)
    for _, row in sub_check.iterrows():
        print(f"  HH{row['hh_id']:>7}: occ_idf={row['occ_idf_daily']:.4f}  "
              f"occ_csv={row['occ_csv_daily']:.4f}  "
              f"Δocc={row['docc_daily']:+.4f}  "
              f"EUI={row['eui_cond']:.2f} kBtu/ft²  "
              f"ΔEUI_est={row['deui_est_pct']:+.3f}%")
    stats_check = cell_year_stats.get(("SingleD__Toronto_5A", "2022"), {})
    print(f"  Cell slope: {stats_check.get('slope_eui','?'):.4f}  "
          f"R²={stats_check.get('r2_eui','?'):.4f}")

    # ── Per-cell table ────────────────────────────────────────────────────
    print("\n  PER-CELL TABLE (2022 and 2030):")
    hdr = (f"  {'Cell':<32} {'Yr':>4} {'N':>4} {'Slope':>8} {'R²':>6} "
           f"{'MnDocc':>8} {'MnΔEUI%':>8} {'WstΔEUI%':>10}")
    print(hdr)
    print("  " + "-" * 84)
    for _, row in cell_df_out.iterrows():
        print(f"  {row['cell']:<32} {row['year']:>4} {row['n_hh']:>4} "
              f"{row['slope_eui']:>8.3f} {row['r2_eui']:>6.3f} "
              f"{row['mean_docc']:>+8.4f} {row['mean_abs_deui_pct']:>8.3f}% "
              f"{row['worst_abs_deui_pct']:>9.3f}%")

    # ── Classification ────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(f"OVERALL SUMMARY (both years combined)")
    print(f"  Mean  |ΔEUI%| (level):    {overall_mean:.3f}%")
    print(f"  Worst |ΔEUI%| (level):    {overall_worst:.3f}%")
    print(f"  Mean  |ΔEUI%| (paired):   {paired_mean:.3f}%")
    print(f"  MC CI half-width:          {MC_CI_HALFWIDTH:.2f}%")
    print()
    if overall_mean < 1.0:
        label = "A-VERIFIED"
    elif overall_mean < MC_CI_HALFWIDTH:
        label = "AMBIGUOUS"
    else:
        label = "FLAG"
    print(f"  CLASSIFICATION: {label}")
    print(f"    (A-VERIFIED: mean <1.0%  AMBIGUOUS: 1.0–1.8%  FLAG: >1.8%)")

    # ── Save summary markdown ─────────────────────────────────────────────
    sub22 = df[(df["year"] == "2022") & df["deui_est_pct"].notna()]
    sub30 = df[(df["year"] == "2030") & df["deui_est_pct"].notna()]
    n22 = len(sub22)
    n30 = len(sub30)
    ov22_mean  = float(sub22["deui_est_pct"].abs().mean())
    ov22_worst = float(sub22["deui_est_pct"].abs().max())
    ov30_mean  = float(sub30["deui_est_pct"].abs().mean())
    ov30_worst = float(sub30["deui_est_pct"].abs().max())
    worst_cell_2022 = cell_df_out[cell_df_out["year"] == "2022"].loc[
        cell_df_out[cell_df_out["year"] == "2022"]["worst_abs_deui_pct"].idxmax(), "cell"]
    worst_cell_2030 = cell_df_out[cell_df_out["year"] == "2030"].loc[
        cell_df_out[cell_df_out["year"] == "2030"]["worst_abs_deui_pct"].idxmax(), "cell"]

    sanity_str = (f"HH34299/2022 IDF wd mean: {idf34299_mean:.4f} (expected ≈0.736, "
                  f"{'PASS' if abs(idf34299_mean-0.736)<0.05 else 'FAIL'})"
                  if idf34299 is not None else "HH34299/2022: NOT FOUND")

    summary = f"""# Round-2c Output-Level EUI Sensitivity — Summary

**Date:** 2026-06-06
**Reference:** Step-8 Round-2c task
**MC CI half-width:** {MC_CI_HALFWIDTH:.2f}% (gate 3.2 from 8F report)

## Sanity Check
- {sanity_str}
- Joined rows: 2022 N={n22}, 2030 N={n30}

## Method
Cross-HH linear regression of as-run EUI on as-built daily-mean weekday occupancy,
within each (cell, year). Slope × Δocc_per_HH gives a first-order upper-bound
estimate of the EUI impact of the provenance gap.

**Note:** the slope absorbs HHSIZE and archetype-internal variation, so it
**overstates** the true dEUI/docc — i.e., results are a conservative upper bound.

## Overall Results

| Metric | 2022 | 2030 | Both |
|--------|------|------|------|
| N joined HH | {n22} | {n30} | {n22+n30} |
| Mean \\|ΔEUI%\\| (level) | {ov22_mean:.3f}% | {ov30_mean:.3f}% | {overall_mean:.3f}% |
| Worst HH \\|ΔEUI%\\| (level) | {ov22_worst:.3f}% | {ov30_worst:.3f}% | {overall_worst:.3f}% |
| Worst-cell mean \\|ΔEUI%\\| | (see table) | (see table) | — |
| Mean \\|ΔEUI%\\| (paired WFH) | — | — | {paired_mean:.3f}% |
| MC CI half-width | {MC_CI_HALFWIDTH:.2f}% | {MC_CI_HALFWIDTH:.2f}% | {MC_CI_HALFWIDTH:.2f}% |

Worst cell 2022: {worst_cell_2022}
Worst cell 2030: {worst_cell_2030}

## Per-Cell Table

| Cell | Year | N | Slope (kBtu/ft²/occ) | R² | Mean Δocc | Mean\\|ΔEUI%\\| | Worst\\|ΔEUI%\\| |
|------|------|---|---------------------|----|-----------|--------------|--------------|
"""
    for _, row in cell_df_out.iterrows():
        summary += (f"| {row['cell']} | {row['year']} | {row['n_hh']} | "
                    f"{row['slope_eui']:.4f} | {row['r2_eui']:.3f} | "
                    f"{row['mean_docc']:+.4f} | {row['mean_abs_deui_pct']:.3f}% | "
                    f"{row['worst_abs_deui_pct']:.3f}% |\n")

    summary += f"""
## Classification

**VERDICT: {label}**

- A-VERIFIED: overall mean |ΔEUI%| < 1.0% AND well inside {MC_CI_HALFWIDTH:.2f}% CI
- AMBIGUOUS: 1.0–1.8% (near CI) → recommend Round-2d 48-run spot-check
- FLAG: >1.8% → output-material; escalate

## Limitations

- First-order linear estimate; EnergyPlus is nonlinear → treat as upper bound.
- Cross-HH slope also absorbs HHSIZE/composition effects → overstates sensitivity.
- Low R² cells: occupancy is not the dominant EUI driver; gap is likely harmless
  in those cells regardless of slope magnitude.
- Peak demand is an independent non-coincident peak (electricity at summer peak,
  gas at winter peak) — serves as supplementary, not primary, evidence.
"""
    (OUT_DIR / "r2c_summary.md").write_text(summary, encoding="utf-8")
    print(f"\n  Saved r2c_summary.md")
    print("\nDone.")


if __name__ == "__main__":
    run()
