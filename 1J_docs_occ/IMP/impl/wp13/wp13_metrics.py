"""WP13: Section 4.1 occupancy metrics, Canada vs Quebec, HHSIZE split, matching-tier shares.
Read-only. Definitions are the paper's own (generate_occupancy_metrics_table.py).
Usage on Speed (inside sbatch):  python wp13_metrics.py --outdir <dir>
Local test:                      python wp13_metrics.py --test-file synthetic_grid.csv --outdir out_test
"""
import argparse, os, sys
import numpy as np
import pandas as pd

OCC = "/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy"
GRID = {
    "2005": f"{OCC}/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct_grid.csv",
    "2010": f"{OCC}/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct_grid.csv",
    "2015": f"{OCC}/Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct_grid.csv",
    "2022": f"{OCC}/Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct_grid.csv",
    "2025": "/speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025_grid.csv",
}
KEYS = {
    "2005": f"{OCC}/Outputs_06CEN05GSS/ProfileMatching/06CEN05GSS_Matched_Keys_sample25pct.csv",
    "2010": f"{OCC}/Outputs_11CEN10GSS/ProfileMatching/11CEN10GSS_Matched_Keys_sample25pct.csv",
    "2015": f"{OCC}/Outputs_16CEN15GSS/ProfileMatching/16CEN15GSS_Matched_Keys_sample25pct.csv",
    "2022": f"{OCC}/Outputs_21CEN22GSS/ProfileMatching/21CEN22GSS_Matched_Keys_sample25pct.csv",
    "2025": "/speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy/Outputs_Aligned/Matched_Population_Keys.csv",
}
USECOLS = ["SIM_HH_ID", "Day_Type", "Hour", "HHSIZE", "PR", "Occupancy_Schedule", "Metabolic_Rate"]
QUEBEC = "Quebec"   # PR is a text label in every grid file (checked with head), not the code 24
N_BOOT, SEED = 1000, 20260929

# Default profile: the paper's own 24 values (generate_occupancy_metrics_table.py DEFAULT_PROFILE_WEEKDAY)
DEFAULT_PROFILE = [1.0] * 7 + [0.85, 0.39] + [0.25] * 7 + [0.30, 0.52, 0.87, 0.87, 0.87, 1.0, 1.0, 1.0]


def transitions_steepest(p):
    """Verbatim logic of get_transition_times (steepest drop 5-12, steepest rise 12-23)."""
    p = np.asarray(p, float)
    d = np.diff(p, prepend=p[-1])
    mn, dep = 0, -1
    for h in range(5, 13):
        if d[h] < mn:
            mn, dep = d[h], h
    mx, ret = 0, -1
    for h in range(12, 24):
        if d[h] > mx:
            mx, ret = d[h], h
    return dep, ret


def transitions_cross50(p):
    """Fig 11 script's own rule: first hour 5-12 below 0.5; first hour 13-22 above 0.5 (-1 if none)."""
    dep = next((h for h in range(5, 13) if p[h] < 0.5), -1)
    ret = next((h for h in range(13, 23) if p[h] > 0.5), -1)
    return dep, ret


def profile_metrics(p):
    p = np.asarray(p, float)
    occ_hours = float(p.sum())
    day = float(p[9:17].mean())
    dep, ret = transitions_steepest(p)
    dep5, ret5 = transitions_cross50(p)
    return dict(occupied_hours=occ_hours, daytime_fraction=day, daytime_vacancy_pct=100 * (1 - day),
                mean_occupancy=float(p.mean()), dep_steepest=dep, ret_steepest=ret,
                dep_cross50=dep5, ret_cross50=ret5)


def hourly_profile(df, day_type):
    s = df.loc[df["Day_Type"] == day_type].groupby("Hour")["Occupancy_Schedule"].mean()
    return s.reindex(range(24)).to_numpy(float)


def met_stats(df, day_type):
    d = df.loc[df["Day_Type"] == day_type]
    if len(d) == 0:
        return dict(met_mean_occ_pos=np.nan, met_mean_all=np.nan, met_mean_gt1=np.nan)
    return dict(met_mean_occ_pos=float(d.loc[d["Occupancy_Schedule"] > 0, "Metabolic_Rate"].mean()),
                met_mean_all=float(d["Metabolic_Rate"].mean()),
                met_mean_gt1=float(d.loc[d["Metabolic_Rate"] > 1.0, "Metabolic_Rate"].mean()))


def block_metrics(df, day_type):
    p = hourly_profile(df, day_type)
    m = profile_metrics(p) if not np.isnan(p).any() else {}
    m.update(met_stats(df, day_type))
    m["n_households"] = int(df.loc[df["Day_Type"] == day_type, "SIM_HH_ID"].nunique())
    m["n_rows"] = int((df["Day_Type"] == day_type).sum())
    return m, p


def hh_matrix(df, day_type):
    """households x 24 matrix of Occupancy (NaN where a household lacks an hour) + Quebec flag."""
    d = df.loc[df["Day_Type"] == day_type]
    mat = d.pivot_table(index="SIM_HH_ID", columns="Hour", values="Occupancy_Schedule", aggfunc="mean")
    mat = mat.reindex(columns=range(24))
    pr = d.groupby("SIM_HH_ID")["PR"].first().reindex(mat.index)
    return mat.to_numpy(float), (pr == QUEBEC).to_numpy()


def boot_diff(H, q, n_boot=N_BOOT, seed=SEED, batch=50):
    """Quebec-minus-Canada difference in occupied hours and daytime fraction, resampling households.
    Returns (point_hours, lo, hi, point_daytime, lo, hi)."""
    rng = np.random.default_rng(seed)
    n = H.shape[0]
    Hn = np.nan_to_num(H, nan=0.0)
    qf = q.astype(float)

    def stats(w):
        wc = w.sum(1, keepdims=True)
        wq = w * qf[None, :]
        wqs = wq.sum(1, keepdims=True)
        canada = (w @ Hn) / wc
        que = np.where(wqs > 0, (wq @ Hn) / np.maximum(wqs, 1), np.nan)
        dh = que.sum(1) - canada.sum(1)
        dd = que[:, 9:17].mean(1) - canada[:, 9:17].mean(1)
        return dh, dd

    ph, pdd = stats(np.ones((1, n)))
    dh_all, dd_all = [], []
    for s in range(0, n_boot, batch):
        b = min(batch, n_boot - s)
        w = rng.multinomial(n, np.full(n, 1.0 / n), size=b).astype(float)
        dh, dd = stats(w)
        dh_all.append(dh)
        dd_all.append(dd)
    dh_all = np.concatenate(dh_all)
    dd_all = np.concatenate(dd_all)
    return (float(ph[0]), *np.nanpercentile(dh_all, [2.5, 97.5]),
            float(pdd[0]), *np.nanpercentile(dd_all, [2.5, 97.5]))


def bucket(v):
    if pd.isna(v):
        return None
    v = int(round(v))
    if v <= 0:
        return None
    return "5+" if v >= 5 else str(v)


def process_year(year, path, outrows):
    print(f"=== {year}: {path}", flush=True)
    df = pd.read_csv(path, usecols=USECOLS, dtype={"SIM_HH_ID": str, "Day_Type": str, "PR": str})
    n_hh = df["SIM_HH_ID"].nunique()
    print(f"{year}: rows={len(df):,} households={n_hh:,} rows/hh={len(df)/n_hh:.3f} (48 expected)")
    print(f"{year}: PR values (households): " + str(df.groupby("PR")["SIM_HH_ID"].nunique().to_dict()))
    print(f"{year}: HHSIZE max={df['HHSIZE'].max()} NaN Occ={df['Occupancy_Schedule'].isna().sum()} NaN HHSIZE={df['HHSIZE'].isna().sum()}")
    res = {}
    for region in ["Canada", "Quebec"]:
        sub = df if region == "Canada" else df[df["PR"] == QUEBEC]
        for dt in ["Weekday", "Weekend"]:
            m, p = block_metrics(sub, dt)
            res[(region, dt)] = (m, p)
            outrows["metrics"].append(dict(year=year, region=region, day_type=dt, **m))
            for h in range(24):
                outrows["profiles"].append(dict(year=year, region=region, day_type=dt, hour=h, mean_occupancy=p[h]))
    for dt in ["Weekday", "Weekend"]:
        H, q = hh_matrix(df, dt)
        cm = res[("Canada", dt)][0]
        qm = res[("Quebec", dt)][0]
        full_p = np.nanmean(H, axis=0)
        chk = np.nanmax(np.abs(full_p - res[("Canada", dt)][1]))
        print(f"{year} {dt}: matrix profile vs row profile max abs diff = {chk:.2e}; incomplete households = {int(np.isnan(H).any(1).sum())}")
        dh, dh_lo, dh_hi, dd, dd_lo, dd_hi = boot_diff(H, q)
        outrows["qvc"].append(dict(year=year, day_type=dt,
            canada_occupied_hours=cm["occupied_hours"], quebec_occupied_hours=qm["occupied_hours"],
            diff_occupied_hours=qm["occupied_hours"] - cm["occupied_hours"],
            boot_point_diff_hours=dh, boot_lo_hours=dh_lo, boot_hi_hours=dh_hi,
            canada_daytime_fraction=cm["daytime_fraction"], quebec_daytime_fraction=qm["daytime_fraction"],
            diff_daytime_fraction=qm["daytime_fraction"] - cm["daytime_fraction"],
            boot_point_diff_daytime=dd, boot_lo_daytime=dd_lo, boot_hi_daytime=dd_hi,
            n_hh_canada=cm["n_households"], n_hh_quebec=qm["n_households"], n_boot=N_BOOT, seed=SEED))
    df["HHB"] = df["HHSIZE"].map(bucket)
    for b in ["1", "2", "3", "4", "5+"]:
        sub = df[df["HHB"] == b]
        for dt in ["Weekday", "Weekend"]:
            if len(sub) == 0 or (sub["Day_Type"] == dt).sum() == 0:
                outrows["hhsize"].append(dict(year=year, hhsize=b, day_type=dt, n_households=0))
                continue
            m, _ = block_metrics(sub, dt)
            outrows["hhsize"].append(dict(year=year, hhsize=b, day_type=dt, **m))
    print(f"{year}: HHSIZE households by bucket: " + str(df.groupby('HHB')['SIM_HH_ID'].nunique().to_dict()), flush=True)
    del df


def tier_shares(outrows):
    for year, path in KEYS.items():
        if not os.path.exists(path):
            print(f"[WARN] keys missing {year}: {path}")
            continue
        k = pd.read_csv(path, usecols=lambda c: c in ("MATCH_TIER_WD", "MATCH_TIER_WE"))
        print(f"{year}: keys rows={len(k):,} cols={list(k.columns)}")
        pooled = None
        for col, lab in [("MATCH_TIER_WD", "weekday"), ("MATCH_TIER_WE", "weekend")]:
            if col not in k.columns:
                print(f"[WARN] {year}: {col} absent")
                continue
            vc = k[col].value_counts(dropna=False)
            pooled = vc if pooled is None else pooled.add(vc, fill_value=0)
            for t, n in vc.items():
                outrows["tiers"].append(dict(year=year, assignment=lab, tier=str(t), n=int(n),
                                             share_pct=100.0 * n / len(k), n_total=len(k)))
        if pooled is not None:
            tot = pooled.sum()
            for t, n in pooled.items():
                outrows["tiers"].append(dict(year=year, assignment="pooled_wd_we", tier=str(t), n=int(n),
                                             share_pct=100.0 * n / tot, n_total=int(tot)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--test-file")
    ap.add_argument("--test-label", default="TEST")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    rows = {k: [] for k in ["metrics", "profiles", "qvc", "hhsize", "tiers"]}
    dp = sum(DEFAULT_PROFILE)
    print(f"Default profile occupied hours = {dp:.4f} (task doc said 16.39; the script's 24 values sum to 16.42, "
          f"paper says 16.4 and 0.684 = 16.42/24); daytime frac = {np.mean(DEFAULT_PROFILE[9:17]):.4f}")
    if round(dp, 1) != 16.4 or abs(dp / 24 - 0.684) > 0.0005 or abs(100 * (1 - np.mean(DEFAULT_PROFILE[9:17])) - 74.4) > 0.05:
        print("FAIL: Default profile does not reproduce the paper's 16.4 h / 0.684 / 74.4 % vacancy")
        sys.exit(2)
    dm = profile_metrics(DEFAULT_PROFILE)
    rows["metrics"].append(dict(year="Default", region="Default", day_type="Weekday", **dm))
    rows["metrics"].append(dict(year="Default", region="Default", day_type="Weekend", **dm))
    if a.test_file:
        process_year(a.test_label, a.test_file, rows)
    else:
        for y, p in GRID.items():
            process_year(y, p, rows)
        tier_shares(rows)
    names = dict(metrics="metrics_by_year_region.csv", profiles="profiles_by_year_region.csv",
                 qvc="quebec_vs_canada.csv", hhsize="metrics_by_hhsize.csv", tiers="tier_shares.csv")
    for k, f in names.items():
        pd.DataFrame(rows[k]).to_csv(os.path.join(a.outdir, f), index=False)
        print(f"wrote {f}: {len(rows[k])} rows")
    if rows["tiers"]:
        t = pd.DataFrame(rows["tiers"])
        w = t[(t.year == "2025") & (t.assignment == "weekday")]
        print("2025 weekday tier shares NEW:", dict(zip(w.tier, w.share_pct.round(2))), "| paper: Tier 2 = 84.6, Tier 4 = 0.3")
    print("METRICS DONE")


if __name__ == "__main__":
    main()
