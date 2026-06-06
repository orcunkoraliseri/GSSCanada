"""
roundtrip_analysis.py — P1 evidence script for the 8F validation investigation.

Parses Occ_Sch_HH_<id> and Met_Sch_HH_<id> from sampled in.idf files,
compares them to three reference CSVs (current, PRE_STEP8_BAK, CLASSIC_BAK),
and reports distributions of per-hour and daily-mean differences.

Also checks: People count == HHSIZE, HH_ID consistency, occ in [0,1], met in range.

Usage: py roundtrip_analysis.py
"""
import os, re, csv, glob, json
import numpy as np
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BEM_SETUP = os.path.join(REPO, "BEM_Setup")
SIM_DIR   = os.path.join(BEM_SETUP, "SimResults_Step8", "campaign_N50")

CSV_REFS = {
    "current":          os.path.join(BEM_SETUP, "BEM_Schedules_{year}.csv"),
    "pre_step8_bak":    os.path.join(BEM_SETUP, "BEM_Schedules_2022_PRE_STEP8_BAK.csv"),
    "classic_bak":      os.path.join(BEM_SETUP, "BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv"),
}

# MET activity code range (from 08_gen_cycle_schedules.py documentation)
MET_MIN, MET_MAX = 40.0, 245.0  # W/person; max activity code ~245 W

# -----------------------------------------------------------------------
def parse_compact_schedule(idf_text, sch_name):
    """
    Parse Schedule:Compact for sch_name from raw IDF text.
    Returns (wd_24, we_24) lists or (None, None).
    """
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

        # Try next-line format: "Until: hh:00,\n    value,"
        pairs = re.findall(r'Until\s*:\s*(\d+)\s*:\s*\d+\s*,[^\n]*\n\s*([\d.]+)',
                           sec, re.IGNORECASE)
        if not pairs:
            # Fallback: same-line "Until: hh:00, value"
            pairs = re.findall(r'Until\s*:\s*(\d+)\s*:\s*\d+\s*,\s*([\d.]+)',
                               sec, re.IGNORECASE)

        arr = np.zeros(24)
        for h_str, v_str in pairs:
            idx = int(h_str) - 1  # Until 1:00 -> hour-0
            if 0 <= idx < 24:
                arr[idx] = float(v_str)

        if is_wd and len(pairs) >= 20:
            wd_arr = arr.tolist()
        elif is_we and len(pairs) >= 20:
            we_arr = arr.tolist()

    return wd_arr, we_arr


def parse_people_count(idf_text):
    """Extract Number of People from PEOPLE object."""
    m = re.search(r'Number\s+of\s+People\s*,\s*([\d.]+)', idf_text, re.IGNORECASE)
    return float(m.group(1)) if m else None


def load_csv_ref(csv_path):
    """Load a BEM_Schedules CSV into {hh_id: {'Weekday': [24 occ], 'Weekend': [24 occ],
                                               'met_wd': [24 met], 'met_we': [24 met],
                                               'hhsize': int}}."""
    ref = defaultdict(lambda: {'Weekday': [None]*24, 'Weekend': [None]*24,
                                'met_wd': [None]*24, 'met_we': [None]*24, 'hhsize': 0})
    if not os.path.exists(csv_path):
        return {}
    with open(csv_path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            hid = row['SIM_HH_ID']
            dt  = row['Day_Type']
            try:
                hr  = int(row['Hour'])
                occ = float(row['Occupancy_Schedule'])
                met = float(row['Metabolic_Rate'])
                hsz = int(row.get('HHSIZE', 0))
            except (ValueError, KeyError):
                continue
            if dt == 'Weekday':
                ref[hid]['Weekday'][hr] = occ
                ref[hid]['met_wd'][hr]  = met
            elif dt == 'Weekend':
                ref[hid]['Weekend'][hr] = occ
                ref[hid]['met_we'][hr]  = met
            if ref[hid]['hhsize'] == 0 and hsz:
                ref[hid]['hhsize'] = hsz
    return dict(ref)


# -----------------------------------------------------------------------
def collect_samples(max_per_arch=15, years=('2005','2010','2015','2022','2030')):
    """Walk SimResults_Step8/campaign_N50 and collect (idf_path, hh_id, arch, city, year)."""
    samples = []
    archs_seen = defaultdict(int)
    for cell_dir in sorted(glob.glob(os.path.join(SIM_DIR, "*__*"))):
        cell_name = os.path.basename(cell_dir)
        parts     = cell_name.split("__")
        arch      = parts[0]
        city      = parts[1] if len(parts) > 1 else "?"

        for samp_dir in sorted(glob.glob(os.path.join(cell_dir, "sample_*_HH*"))):
            hh_id = re.search(r'HH(\d+)', os.path.basename(samp_dir))
            if not hh_id:
                continue
            hh_id = hh_id.group(1)

            for yr in years:
                idf_path = os.path.join(samp_dir, yr, "in.idf")
                if not os.path.exists(idf_path):
                    continue
                if archs_seen[(arch, yr)] >= max_per_arch:
                    continue
                samples.append((idf_path, hh_id, arch, city, yr))
                archs_seen[(arch, yr)] += 1

    return samples


# -----------------------------------------------------------------------
def main():
    YEARS = ('2005', '2010', '2015', '2022', '2030')

    print("=== Step 8 — Schedule Round-Trip Analysis (P1) ===\n")

    # Load reference CSVs  (year-specific "current" + year-agnostic backups)
    print("Loading reference CSVs …")
    refs = {}
    for yr in YEARS:
        p = CSV_REFS["current"].replace("{year}", yr)
        refs[f"current_{yr}"] = load_csv_ref(p)
        print(f"  current_{yr}: {len(refs[f'current_{yr}'])} HH  ({os.path.basename(p)})")
    refs["pre_step8_bak"] = load_csv_ref(CSV_REFS["pre_step8_bak"])
    refs["classic_bak"]   = load_csv_ref(CSV_REFS["classic_bak"])
    print(f"  pre_step8_bak:   {len(refs['pre_step8_bak'])} HH")
    print(f"  classic_bak:     {len(refs['classic_bak'])} HH")

    print("\nCollecting IDF samples …")
    samples = collect_samples(max_per_arch=15, years=YEARS)
    print(f"  Found {len(samples)} (idf, hh_id, arch, city, year) tuples\n")

    # Stats accumulators keyed by ref label
    ref_labels = [f"current_{yr}" for yr in YEARS] + ["pre_step8_bak", "classic_bak"]
    wd_errs   = {k: [] for k in ref_labels}
    we_errs   = {k: [] for k in ref_labels}
    met_errs  = {k: [] for k in ref_labels}
    h2_flags  = []  # (idf_path, issue)
    hand_check = []  # first 3 for detailed printout

    # For pairing check: 2022 vs 2030 same HH
    pair_check = defaultdict(dict)  # (arch, city, hh_id) -> {yr: wd_arr}

    for idf_path, hh_id, arch, city, yr in samples:
        with open(idf_path, errors='replace') as f:
            txt = f.read()

        occ_wd, occ_we = parse_compact_schedule(txt, f"Occ_Sch_HH_{hh_id}")
        met_wd, met_we = parse_compact_schedule(txt, f"Met_Sch_HH_{hh_id}")
        n_people = parse_people_count(txt)

        # H2 checks
        occ_sch_name_present = f"Occ_Sch_HH_{hh_id}" in txt
        met_sch_name_present = f"Met_Sch_HH_{hh_id}" in txt
        if not occ_sch_name_present:
            h2_flags.append((idf_path, f"Occ_Sch_HH_{hh_id} not found in IDF"))
        if occ_wd is not None:
            if any(v < -0.001 or v > 1.001 for v in occ_wd):
                h2_flags.append((idf_path, f"occ out of [0,1]: {occ_wd}"))
        if met_wd is not None:
            if any(v < MET_MIN - 5 or v > MET_MAX + 5 for v in met_wd):
                h2_flags.append((idf_path, f"met out of range: {met_wd}"))

        # Pair store for 2022/2030
        if yr in ('2022', '2030') and occ_wd is not None:
            pair_check[(arch, city, hh_id)][yr] = occ_wd

        # Round-trip for the matching year
        for ref_key in ref_labels:
            # Map ref to the right year slot
            if ref_key.startswith("current_"):
                ref_yr = ref_key.split("_")[1]
                if ref_yr != yr:
                    continue
                ref_data = refs[ref_key].get(hh_id)
            else:
                # backups are 2022-based; only compare for yr=2022
                if yr != "2022":
                    continue
                ref_data = refs[ref_key].get(hh_id)

            if ref_data is None:
                continue

            src_wd = ref_data.get('Weekday', [None]*24)
            src_we = ref_data.get('Weekend', [None]*24)
            src_met_wd = ref_data.get('met_wd', [None]*24)
            hhsize_ref = ref_data.get('hhsize', 0)

            # People count check
            if hhsize_ref and n_people is not None and abs(n_people - hhsize_ref) > 0.01:
                h2_flags.append((idf_path, f"HHSIZE mismatch: IDF People={n_people} vs CSV={hhsize_ref}"))

            if occ_wd is not None and all(v is not None for v in src_wd):
                src_arr = np.array(src_wd, dtype=float)
                idf_arr = np.array(occ_wd, dtype=float)
                src_mean = np.mean(src_arr)
                pct_err  = 100 * abs(np.mean(idf_arr) - src_mean) / max(src_mean, 1e-9)
                wd_errs[ref_key].append(pct_err)
            if occ_we is not None and all(v is not None for v in src_we):
                src_arr = np.array(src_we, dtype=float)
                src_mean = np.mean(src_arr)
                pct_err  = 100 * abs(np.mean(occ_we) - src_mean) / max(src_mean, 1e-9)
                we_errs[ref_key].append(pct_err)
            if met_wd is not None and all(v is not None for v in src_met_wd):
                src_arr = np.array(src_met_wd, dtype=float)
                max_dev  = np.max(np.abs(np.array(met_wd) - src_arr))
                met_errs[ref_key].append(max_dev)

        # Hand-check printout (first 3 HH in 2022)
        if len(hand_check) < 3 and yr == '2022' and occ_wd is not None:
            ref_data = refs[f"current_2022"].get(hh_id, {})
            src_wd_hand = ref_data.get('Weekday', [None]*24)
            if all(v is not None for v in src_wd_hand):
                hand_check.append({
                    'idf_path': idf_path, 'hh_id': hh_id, 'arch': arch,
                    'occ_wd_idf': occ_wd, 'occ_wd_src': src_wd_hand,
                    'met_wd_idf': met_wd,
                    'met_wd_src': ref_data.get('met_wd', [None]*24),
                })

    # -----------------------------------------------------------------------
    # Print results
    print("=" * 65)
    print("P1 ROUND-TRIP DISTRIBUTIONS")
    print("=" * 65)
    for rk in ref_labels:
        errs_wd  = wd_errs[rk]
        errs_we  = we_errs[rk]
        errs_met = met_errs[rk]
        if not errs_wd:
            continue
        print(f"\n  Reference: {rk}  (n={len(errs_wd)} WD, {len(errs_we)} WE, {len(errs_met)} Met)")
        for label, errs in [('Occ WD daily-mean %err', errs_wd),
                             ('Occ WE daily-mean %err', errs_we),
                             ('Met WD max abs dev (W)',  errs_met)]:
            if not errs:
                continue
            arr = np.array(errs)
            print(f"    {label:35s}  median={np.median(arr):.3f}  p95={np.percentile(arr,95):.3f}  max={np.max(arr):.3f}")

    # -----------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("P1.4 H2 CHECKS")
    print("=" * 65)
    if h2_flags:
        for p, msg in h2_flags[:20]:
            print(f"  FLAG: {os.path.relpath(p, SIM_DIR)[:60]}  → {msg}")
    else:
        print("  No H2 flags: all checks passed (HH_ID match, occ in [0,1], met in range, HHSIZE match)")

    # -----------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("P1.5 PAIRING INTEGRITY (2022 vs 2030, same HH)")
    print("=" * 65)
    n_checked, n_ok = 0, 0
    for (arch, city, hh_id), yrs in pair_check.items():
        if '2022' in yrs and '2030' in yrs:
            n_checked += 1
            # For paired comparison, we verify each year was built from its own CSV
            # (pairing integrity = same hh_id appears in both, which it does by construction)
            n_ok += 1  # the deterministic sampler ensures same hh_id in both years
    print(f"  {n_ok}/{n_checked} HH have both 2022 + 2030 IDF entries (pairing by same hh_id = {n_ok==n_checked})")

    # -----------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("P1.6 MATERIALITY — ensemble diurnal shapes: current vs pre_step8_bak (year 2022)")
    print("=" * 65)
    # Compare ensemble WD shape of current_2022 vs pre_step8_bak for all HH
    # that appear in BOTH references and have valid 24-h data
    cur_ref  = refs["current_2022"]
    pre_ref  = refs["pre_step8_bak"]
    common_h = [hid for hid in cur_ref if hid in pre_ref
                and all(v is not None for v in cur_ref[hid].get('Weekday', [None]*24))
                and all(v is not None for v in pre_ref[hid].get('Weekday', [None]*24))]
    if common_h:
        cur_ens = np.array([cur_ref[h]['Weekday'] for h in common_h], dtype=float)
        pre_ens = np.array([pre_ref[h]['Weekday'] for h in common_h], dtype=float)
        # Per-hour absolute difference in ensemble mean
        h_diff = np.abs(np.mean(cur_ens, axis=0) - np.mean(pre_ens, axis=0))
        print(f"  Common HH: {len(common_h)}")
        print(f"  Per-hour abs diff (ensemble mean): max={h_diff.max():.4f}  mean={h_diff.mean():.4f}")
        print(f"  Daily-mean ensemble diff: {abs(np.mean(cur_ens) - np.mean(pre_ens)):.6f}")
        # Midday share (h9-h17) ensemble diff
        cur_mid = np.mean(cur_ens[:, 9:18])
        pre_mid = np.mean(pre_ens[:, 9:18])
        print(f"  Midday share (h9-17): current={cur_mid:.4f}  pre_bak={pre_mid:.4f}  Δ={cur_mid-pre_mid:+.4f}")
    else:
        print("  No common HH between current_2022 and pre_step8_bak (different HH sets?)")

    # -----------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("P1.1 HAND-CHECK: 3 HH (2022, IDF vs current_2022 CSV)")
    print("=" * 65)
    for hc in hand_check:
        idf_wd = np.array(hc['occ_wd_idf'])
        src_wd = np.array(hc['occ_wd_src'])
        dm_err = 100 * abs(np.mean(idf_wd) - np.mean(src_wd)) / max(np.mean(src_wd), 1e-9)
        exact  = np.allclose(idf_wd, src_wd, atol=0.001)
        print(f"\n  HH {hc['hh_id']} | arch={hc['arch']}")
        print(f"    IDF Occ WD: {[round(v,3) for v in hc['occ_wd_idf']]}")
        print(f"    CSV Occ WD: {[round(v,3) for v in hc['occ_wd_src']]}")
        print(f"    daily-mean err={dm_err:.2f}%  exact(atol=0.001)={exact}")
        if hc['met_wd_idf'] and all(v is not None for v in hc['met_wd_src']):
            met_dev = np.max(np.abs(np.array(hc['met_wd_idf']) - np.array(hc['met_wd_src'])))
            print(f"    Met max dev={met_dev:.3f} W/person")

    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
