"""
materiality_p4_analysis.py — P1.6 materiality + P4 CI outlier analysis.

P1.6: Ensemble diurnal shape: IDF as-built profiles vs current CSV for 2022.
P4:   List (arch, city, year) cells with 95% CI half-width > 2%.
"""
import os, re, csv, glob
import numpy as np
from collections import defaultdict
import sys

REPO    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BEM_SETUP = os.path.join(REPO, "BEM_Setup")
SIM_DIR   = os.path.join(BEM_SETUP, "SimResults_Step8", "campaign_N50")
AGG_DIR   = os.path.join(REPO, "2J_docs_occ_nTemp", "outputs_step8", "agg")

# -----------------------------------------------------------------------
def parse_compact_schedule(idf_text, sch_name):
    pat = r'Schedule:Compact\s*,\s*\n\s*' + re.escape(sch_name) + r'\s*,'
    m = re.search(pat, idf_text, re.IGNORECASE)
    if not m:
        return None, None
    block_end = idf_text.find(';', m.start())
    if block_end < 0:
        return None, None
    block = idf_text[m.start():block_end + 1]
    wd_arr, we_arr = None, None
    for sec in re.split(r'(?i)For\s*:', block)[1:]:
        label = sec.split('\n')[0].strip().rstrip(',').lower()
        is_wd = 'weekday' in label
        is_we = 'weekend' in label or 'allotherdays' in label
        if not (is_wd or is_we):
            continue
        pairs = re.findall(r'Until\s*:\s*(\d+)\s*:\s*\d+\s*,[^\n]*\n\s*([\d.]+)',
                           sec, re.IGNORECASE)
        if not pairs:
            pairs = re.findall(r'Until\s*:\s*(\d+)\s*:\s*\d+\s*,\s*([\d.]+)',
                               sec, re.IGNORECASE)
        arr = np.zeros(24)
        for h_str, v_str in pairs:
            idx = int(h_str) - 1
            if 0 <= idx < 24:
                arr[idx] = float(v_str)
        if is_wd and len(pairs) >= 20:
            wd_arr = arr.tolist()
        elif is_we and len(pairs) >= 20:
            we_arr = arr.tolist()
    return wd_arr, we_arr


def load_csv_ref_fast(csv_path, hh_ids_needed=None):
    """Load occupancy WD/WE for requested HH_IDs only."""
    ref = {}
    if not os.path.exists(csv_path):
        return ref
    need = set(hh_ids_needed) if hh_ids_needed else None
    with open(csv_path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            hid = row['SIM_HH_ID']
            if need and hid not in need:
                continue
            if hid not in ref:
                ref[hid] = {'Weekday': [None]*24, 'Weekend': [None]*24,
                             'met_wd': [None]*24}
            dt = row['Day_Type']
            try:
                hr  = int(row['Hour'])
                occ = float(row['Occupancy_Schedule'])
                met = float(row['Metabolic_Rate'])
            except (ValueError, KeyError):
                continue
            if dt == 'Weekday':
                ref[hid]['Weekday'][hr] = occ
                ref[hid]['met_wd'][hr]  = met
            elif dt == 'Weekend':
                ref[hid]['Weekend'][hr] = occ
    return ref


# -----------------------------------------------------------------------
def main():
    print("=== P1.6 Materiality: ensemble IDF vs current CSV (2022) ===\n")

    # Collect 2022 IDF samples (up to 200 per arch for ensemble stability)
    arch_idf = defaultdict(list)   # arch -> [(hh_id, wd_24, we_24)]
    arch_hh_ids = defaultdict(set)

    for cell_dir in sorted(glob.glob(os.path.join(SIM_DIR, "*__*"))):
        arch = os.path.basename(cell_dir).split("__")[0]
        for samp_dir in sorted(glob.glob(os.path.join(cell_dir, "sample_*_HH*"))):
            m = re.search(r'HH(\d+)', os.path.basename(samp_dir))
            if not m:
                continue
            hh_id = m.group(1)
            idf_path = os.path.join(samp_dir, "2022", "in.idf")
            if not os.path.exists(idf_path):
                continue
            if len(arch_idf[arch]) >= 200:
                continue
            with open(idf_path, errors='replace') as f:
                txt = f.read()
            wd, we = parse_compact_schedule(txt, f"Occ_Sch_HH_{hh_id}")
            if wd is None:
                continue
            arch_idf[arch].append((hh_id, wd, we))
            arch_hh_ids[arch].add(hh_id)

    # Load current CSV for needed HH_IDs
    all_hh = set()
    for ids in arch_hh_ids.values():
        all_hh.update(ids)
    print(f"Loading current BEM_Schedules_2022.csv for {len(all_hh)} unique HH...")
    cur_ref = load_csv_ref_fast(os.path.join(BEM_SETUP, "BEM_Schedules_2022.csv"), all_hh)

    # Compute ensemble stats per arch
    midday_slots = list(range(9, 18))  # hours 9-17
    print("\n--- Ensemble WD Profile: IDF as-built vs current CSV ---")
    print(f"{'Arch':14s}  {'N':5s}  {'IDF midday':>12s}  {'CSV midday':>12s}  {'delta_pp':>10s}  {'max_h_diff':>12s}")
    for arch in sorted(arch_idf.keys()):
        samples = arch_idf[arch]
        idf_wds, csv_wds = [], []
        for hh_id, idf_wd, _ in samples:
            csv_data = cur_ref.get(hh_id, {})
            csv_wd = csv_data.get('Weekday', [None]*24)
            if all(v is not None for v in csv_wd):
                idf_wds.append(idf_wd)
                csv_wds.append(csv_wd)

        if not idf_wds:
            continue
        idf_arr = np.array(idf_wds)
        csv_arr = np.array(csv_wds)

        idf_mean = np.mean(idf_arr, axis=0)
        csv_mean = np.mean(csv_arr, axis=0)
        diff_h = np.abs(idf_mean - csv_mean)

        idf_mid = np.mean(idf_arr[:, midday_slots])
        csv_mid = np.mean(csv_arr[:, midday_slots])
        delta_pp = (idf_mid - csv_mid) * 100

        print(f"  {arch:12s}  {len(idf_wds):5d}  {idf_mid:12.4f}  {csv_mid:12.4f}  "
              f"{delta_pp:+10.2f}pp  {diff_h.max():12.4f}")

    # Overall ensemble across all archs
    all_idf, all_csv = [], []
    for arch in arch_idf:
        for hh_id, idf_wd, _ in arch_idf[arch]:
            csv_data = cur_ref.get(hh_id, {})
            csv_wd = csv_data.get('Weekday', [None]*24)
            if all(v is not None for v in csv_wd):
                all_idf.append(idf_wd)
                all_csv.append(csv_wd)

    if all_idf:
        idf_all = np.array(all_idf)
        csv_all = np.array(all_csv)
        idf_peak = float(np.argmax(np.mean(idf_all, axis=0)))
        csv_peak = float(np.argmax(np.mean(csv_all, axis=0)))
        idf_lf   = np.mean(idf_all) / (np.max(np.mean(idf_all, axis=0)) or 1)
        csv_lf   = np.mean(csv_all) / (np.max(np.mean(csv_all, axis=0)) or 1)
        idf_mid  = np.mean(idf_all[:, midday_slots])
        csv_mid  = np.mean(csv_all[:, midday_slots])

        print(f"\n  OVERALL (N={len(all_idf)})")
        print(f"    Midday share: IDF={idf_mid:.4f}  CSV={csv_mid:.4f}  delta={idf_mid-csv_mid:+.4f}")
        print(f"    Peak hour:    IDF={idf_peak:.0f}h  CSV={csv_peak:.0f}h")
        print(f"    Load factor:  IDF={idf_lf:.4f}  CSV={csv_lf:.4f}  delta={idf_lf-csv_lf:+.4f}")
        diff = np.abs(np.mean(idf_all, axis=0) - np.mean(csv_all, axis=0))
        print(f"    Max per-hour ensemble diff: {diff.max():.4f}")

    # -----------------------------------------------------------------------
    print("\n\n=== P4: MC CI Outlier Cells (EUI 95% CI half-width > 2%) ===\n")

    agg_annual_path = os.path.join(AGG_DIR, "agg_annual.csv")
    if not os.path.exists(agg_annual_path):
        print(f"  agg_annual.csv not found at {agg_annual_path}")
        return

    # Load annual data
    rows = []
    with open(agg_annual_path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            try:
                rows.append({
                    'arch': row['arch'], 'city': row['city'], 'year': row['year'],
                    'eui': float(row['eui_kWh_m2']),
                })
            except (KeyError, ValueError):
                continue

    # Group by cell
    cell_euis = defaultdict(list)
    for r in rows:
        key = (r['arch'], r['city'], r['year'])
        cell_euis[key].append(r['eui'])

    from scipy import stats as scipy_stats
    outliers = []
    all_ci = []
    for (arch, city, year), vals in sorted(cell_euis.items()):
        n = len(vals)
        if n < 2:
            continue
        mean = np.mean(vals)
        se   = scipy_stats.sem(vals)
        ci_hw = scipy_stats.t.interval(0.95, n-1, loc=mean, scale=se)[1] - mean
        ci_p  = 100 * ci_hw / mean if mean > 0 else 0
        all_ci.append(ci_p)
        if ci_p >= 2.0:
            outliers.append({'arch': arch, 'city': city, 'year': year,
                             'n': n, 'mean': round(mean, 1), 'ci_hw_pct': round(ci_p, 2)})

    outliers.sort(key=lambda x: -x['ci_hw_pct'])
    print(f"  Max CI: {max(all_ci):.2f}%  Mean CI: {np.mean(all_ci):.2f}%  N cells: {len(all_ci)}")
    print(f"  Cells with CI >= 2%: {len(outliers)}\n")
    if outliers:
        print(f"  {'Arch':14s}  {'City':20s}  {'Year':6s}  {'N':5s}  {'Mean EUI':>10s}  {'CI%':>8s}")
        for o in outliers:
            print(f"  {o['arch']:14s}  {o['city']:20s}  {o['year']:6s}  {o['n']:5d}  "
                  f"{o['mean']:10.1f}  {o['ci_hw_pct']:8.2f}%")
    else:
        print("  No cells exceed 2% CI threshold.")

    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
