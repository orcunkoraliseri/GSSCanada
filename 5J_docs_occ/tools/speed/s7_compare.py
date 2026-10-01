# -*- coding: utf-8 -*-
"""5J Step 7 part E (Speed CPU job, after the EnergyPlus runs, their integrity check and the S hourly files): S against EnergyPlus on the 20 check draws.
Reads (read only): pred_check/<climate>/<run>.csv.gz (S, per-dwelling hourly), ep/extracted/<climate>/<run>.csv.gz (EnergyPlus), in/ sealed tables,
hh/pool.csv, out/twin_range_es.csv. Writes under out_step7/ :
  district_check.csv          one row per dwelling and draw (40,680 rows): run, draw, twin, dwelling, household, splits, per target CV(RMSE) %, NMBE %, annual S, annual E
  district_check_runs.csv     one row per run (twin x draw): the scorer's run-level CV(RMSE) and NMBE over all dwelling-hours of the run
  district_check_draws.csv    one row per draw, scope, target: district annual and peak-hour totals, S vs EnergyPlus
  district_check_spread.csv   per scope and target: spread of the district annual total over the 20 draws (max - min, SD), S and EnergyPlus
  district_check_summary.md   the same by in range / out of range twin, seen / new code, seen / new household
Metric conventions = the frozen scorer (5thJ_04_scorer.py): e = S - EnergyPlus; CV(RMSE) = sqrt(mean(e^2)) / mean(EnergyPlus); NMBE = sum(e) / sum(EnergyPlus);
undefined (empty) where the EnergyPlus mean is 0. Here per dwelling over its 8,760 h (and per run over all its dwelling-hours). Reported, not gated."""
import io, json, multiprocessing as mp, os, sys, time
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import s7_common as s7
import s7_draws as dr
import s5_common as c

OUT = s7.D + "out_step7/"
H = c.H
TN = ["heating", "cooling", "equipment", "total_elec"]
SCOPES = ["all", "in_range", "out_of_range", "code_seen", "code_new", "hh_trained", "hh_new"]


def read_run(path, nd):
    df = pd.read_csv(path, comment="#", compression="gzip", usecols=["dwelling", "hour"] + c.TARGETS)
    assert len(df) == nd * H, (path, len(df), nd)
    assert (df["dwelling"].to_numpy() == np.repeat(np.arange(nd), H)).all() and (df["hour"].to_numpy() == np.tile(np.arange(1, H + 1), nd)).all(), path
    return df[c.TARGETS].to_numpy(dtype=np.float64).reshape(nd, H, 4)


def metrics(S, E, axis_hours=1):
    """S, E [..., hours, 4] -> cv, nmbe (fractions, nan where undefined) over the hour axis."""
    e = S - E
    mean = E.mean(axis_hours)
    sm = E.sum(axis_hours)
    rmse = np.sqrt((e ** 2).mean(axis_hours))
    cv = np.where(mean > 0, rmse / np.where(mean > 0, mean, 1.0), np.nan)
    nm = np.where(sm > 0, e.sum(axis_hours) / np.where(sm > 0, sm, 1.0), np.nan)
    return cv, nm


def draw_task(args):
    d, seed, twins, info, rng, prow = args
    a = dr.assign(seed, twins, [r["hid"] for r in prow], None)
    trained = {r["hid"]: r["trained_by_model"] == "1" for r in prow}
    hs = {s: np.zeros((H, 4)) for s in SCOPES}
    he = {s: np.zeros((H, 4)) for s in SCOPES}
    drows, rrows = [], []
    for tid, cls, nd, _r in twins:
        rid = "es_madrid_%s_d%03d" % (tid, d)
        S = read_run("%spred_check/%s/%s.csv.gz" % (s7.D, s7.CLIMATE, rid), nd)
        E = read_run("%sep/extracted/%s/%s.csv.gz" % (s7.D, s7.CLIMATE, rid), nd)
        cv, nm = metrics(S, E)                         # [nd, 4]
        cvr, nmr = metrics(S.reshape(1, nd * H, 4), E.reshape(1, nd * H, 4))
        inr = rng[tid] == "in_range"
        seen = info[tid]["code_seen_in_dev_buildings"] == "seen"
        hh = a[tid]
        tr = np.array([trained[x] for x in hh])
        rrows.append([rid, d, tid, cls, nd, "in_range" if inr else "out_of_range", "seen" if seen else "new"] + ["%.6g" % (100 * v) if np.isfinite(v) else "" for k in range(4) for v in (cvr[0, k], nmr[0, k])])
        sa, ea = S.sum(1), E.sum(1)
        for j in range(nd):
            row = [rid, d, tid, j, hh[j], "in_range" if inr else "out_of_range", "seen" if seen else "new", "trained" if tr[j] else "new"]
            for k in range(4):
                row += ["%.6g" % (100 * cv[j, k]) if np.isfinite(cv[j, k]) else "", "%.6g" % (100 * nm[j, k]) if np.isfinite(nm[j, k]) else "", "%.8g" % sa[j, k], "%.8g" % ea[j, k]]
            drows.append(row)
        masks = {"all": np.ones(nd, bool), "in_range": np.full(nd, inr), "out_of_range": np.full(nd, not inr), "code_seen": np.full(nd, seen), "code_new": np.full(nd, not seen),
                 "hh_trained": tr, "hh_new": ~tr}
        for s, m in masks.items():
            if m.any():
                hs[s] += S[m].sum(0)
                he[s] += E[m].sum(0)
    return d, drows, rrows, hs, he


def main():
    s7.stamp("s7_compare start")
    os.makedirs(OUT, exist_ok=True)
    fails = []
    seals = {l.split()[1]: l.split()[0] for l in io.open(s7.IN + "SEALS.md5", encoding="utf-8") if len(l.split()) == 2}
    ok = all(seals.get(n) == s7.md5(s7.IN + n) for n in ("draws.json", "twins_info_es.csv", "district_runs_es.csv"))
    print("GATE sealed_inputs_unchanged %s" % ("PASS" if ok else "FAIL"))
    dj = json.load(io.open(s7.IN + "draws.json", encoding="utf-8"))
    chk = dj["check_indices"]
    twins = dr.load_twins()
    info = {r["twin_id"]: r for r in s7.read_csv(s7.IN + "twins_info_es.csv")}
    rng = {r["twin_id"]: r["range"] for r in s7.read_csv(s7.D + "out/twin_range_es.csv")}
    prow = s7.read_csv(s7.HH + "pool.csv")
    # self test of the metric code (seen failing: a known 10 % bias and a known shift must come out as 10 % and the planted shift must change the result)
    E0 = np.abs(np.random.RandomState(1).randn(3, H, 4)) + 1.0
    cv0, nm0 = metrics(E0, E0)
    cv1, nm1 = metrics(1.1 * E0, E0)
    # manager fix 2026-10-01 07:21: a 10 % scale-up gives NMBE = 0.1 exactly, but CV(RMSE) = 0.1 * sqrt(mean(E^2)) / mean(E) (not 0.1
    # unless E is constant); the first test expected 0.1 and failed on correct metric code (job 1405283).
    cv1_hand = 0.1 * np.sqrt((E0 ** 2).mean(1)) / E0.mean(1)
    st_ok = bool(np.allclose(cv0, 0) and np.allclose(nm0, 0) and np.allclose(cv1, cv1_hand) and np.allclose(nm1, 0.1) and not np.allclose(cv1, 0.1))
    S2 = E0.copy()
    S2[0, 100, 0] += 5.0
    cv2, _ = metrics(S2, E0)
    st_ok = st_ok and bool(cv2[0, 0] > 0 and np.allclose(cv2[1:], 0) and np.isclose(cv2[0, 0], np.sqrt(25.0 / H) / E0[0, :, 0].mean()))
    print("SELFTEST metric code (identity gives 0, a 10%% bias gives 10%%, a planted single-hour shift gives the hand value) %s" % ("PASS" if st_ok else "FAIL"))
    if not st_ok:
        sys.exit(1)
    missing = []
    for d in chk:
        for tid, _c, _n, _r in twins:
            rid = "es_madrid_%s_d%03d" % (tid, d)
            for p in ("%spred_check/%s/%s.csv.gz" % (s7.D, s7.CLIMATE, rid), "%sep/extracted/%s/%s.csv.gz" % (s7.D, s7.CLIMATE, rid)):
                if not os.path.exists(p):
                    missing.append(p)
    print("GATE all_2000_S_files_and_2000_EnergyPlus_files_exist %s (missing %d)" % ("PASS" if not missing else "FAIL", len(missing)))
    if missing:
        print("MISSING first 5: %s" % missing[:5])
        sys.exit(1)
    t0 = time.time()
    with mp.Pool(6) as pool:
        res = pool.map(draw_task, [(d, dj["seeds"][d], twins, info, rng, prow) for d in chk], chunksize=1)
    print("READ_AND_COMPARE draws=%d seconds=%.0f" % (len(res), time.time() - t0), flush=True)
    res.sort(key=lambda x: x[0])
    cols = ["run_id", "draw", "twin_id", "dwelling", "hid", "range", "code", "household"] + ["%s_%s" % (t, q) for t in TN for q in ("cvrmse_pct", "nmbe_pct", "annual_S_kwh", "annual_E_kwh")]
    dw = pd.DataFrame([r for x in res for r in x[1]], columns=cols)
    # manager fix 2026-10-01 07:26: the rows hold formatted strings ("%.8g"); the summary needs numbers (job 1405334 TypeError)
    for c_ in cols:
        if c_.endswith(("_kwh", "_pct")):
            dw[c_] = pd.to_numeric(dw[c_], errors="coerce")
    rcols = ["run_id", "draw", "twin_id", "class", "dwellings", "range", "code"] + ["%s_%s" % (t, q) for t in TN for q in ("cvrmse_pct", "nmbe_pct")]
    rn = pd.DataFrame([r for x in res for r in x[2]], columns=rcols)
    for c_ in rcols:                                   # manager fix 07:26: numbers, as for dw
        if c_.endswith(("_pct",)) or c_ == "dwellings":
            rn[c_] = pd.to_numeric(rn[c_], errors="coerce")
    dw.to_csv(OUT + "district_check.csv", index=False)
    rn.to_csv(OUT + "district_check_runs.csv", index=False)
    print("WROTE district_check.csv rows %d ; district_check_runs.csv rows %d" % (len(dw), len(rn)))
    # per draw district
    drows = []
    ann = {}
    for d, _a, _b, hs, he in res:
        for s in SCOPES:
            for k, t in enumerate(TN):
                aS, aE = hs[s][:, k].sum(), he[s][:, k].sum()
                pS, pE = hs[s][:, k].max(), he[s][:, k].max()
                drows.append([d, s, t, "%.8g" % aS, "%.8g" % aE, "%.6g" % (100 * (aS - aE) / aE) if aE > 0 else "", "%.8g" % pS, "%.8g" % pE, "%.6g" % (100 * (pS - pE) / pE) if pE > 0 else "",
                              int(hs[s][:, k].argmax()) + 1, int(he[s][:, k].argmax()) + 1])
                ann[(s, t, d)] = (aS, aE)
    s7.write_csv(OUT + "district_check_draws.csv", ["draw", "scope", "target", "annual_S_kwh", "annual_E_kwh", "annual_diff_pct", "peak_hour_S_kwh", "peak_hour_E_kwh", "peak_diff_pct", "peak_hour_index_S", "peak_hour_index_E"], drows)
    srows = []
    for s in SCOPES:
        for t in TN:
            S_ = np.array([ann[(s, t, d)][0] for d in chk])
            E_ = np.array([ann[(s, t, d)][1] for d in chk])
            r = float(np.corrcoef(S_, E_)[0, 1]) if S_.std() > 0 and E_.std() > 0 else float("nan")
            srows.append([s, t, "%.8g" % (S_.max() - S_.min()), "%.8g" % (E_.max() - E_.min()), "%.6g" % S_.std(ddof=1), "%.6g" % E_.std(ddof=1),
                          "%.4f" % ((S_.max() - S_.min()) / (E_.max() - E_.min())) if E_.max() > E_.min() else "", "%.4f" % r, "%.8g" % S_.mean(), "%.8g" % E_.mean()])
    s7.write_csv(OUT + "district_check_spread.csv", ["scope", "target", "range_S_kwh", "range_E_kwh", "sd_S_kwh", "sd_E_kwh", "range_ratio_S_over_E", "pearson_r_S_vs_E_over_20_draws", "mean_S_kwh", "mean_E_kwh"], srows)
    # summary
    L = ["# Step 7 district check: S against EnergyPlus, 20 check draws x 100 twins (%d dwelling-years)" % len(dw), "",
         "Conventions as the frozen scorer: e = S - EnergyPlus; CV(RMSE) = RMSE / mean(EnergyPlus); NMBE = sum(e) / sum(EnergyPlus); per dwelling over 8,760 h. Reported, not gated.", ""]

    def grp_table(title, key, vals):
        L.extend(["## " + title, "", "| group | target | dwelling-years | median CV(RMSE) % | p10 | p90 | median NMBE % | pooled NMBE % (annual) | share CV<=30 and |NMBE|<=10 |", "|---|---|---|---|---|---|---|---|---|"])
        for v in vals:
            sub = dw if key is None else dw[dw[key] == v]
            for t in TN:
                cv, nm = sub[t + "_cvrmse_pct"], sub[t + "_nmbe_pct"]
                okm = cv.notna() & nm.notna()
                pooled = 100 * (sub[t + "_annual_S_kwh"].sum() - sub[t + "_annual_E_kwh"].sum()) / sub[t + "_annual_E_kwh"].sum() if sub[t + "_annual_E_kwh"].sum() > 0 else float("nan")
                L.append("| %s | %s | %d | %.1f | %.1f | %.1f | %.2f | %.2f | %.3f |" % (v, t, len(sub), cv.median(), cv.quantile(0.1), cv.quantile(0.9), nm.median(), pooled,
                                                                                    float(((cv[okm] <= 30) & (nm[okm].abs() <= 10)).mean()) if okm.any() else float("nan")))
        L.append("")
    grp_table("All dwellings", None, ["all"])
    grp_table("By twin range", "range", ["in_range", "out_of_range"])
    grp_table("By building code (seen / new in development)", "code", ["seen", "new"])
    grp_table("By household (trained_by_model / new to the model)", "household", ["trained", "new"])
    L.extend(["## Run level (the scorer's unit: all dwelling-hours of a run), median over runs", "", "| group | target | runs | median CV(RMSE) % | median NMBE % |", "|---|---|---|---|---|"])
    for key, vals in (("range", ["in_range", "out_of_range"]), ("code", ["seen", "new"])):
        for v in vals:
            sub = rn[rn[key] == v]
            for t in TN:
                L.append("| %s | %s | %d | %.1f | %.2f |" % (v, t, len(sub), sub[t + "_cvrmse_pct"].median(), sub[t + "_nmbe_pct"].median()))
    L.extend(["", "## District totals per draw (annual, kWh) and the spread over the 20 draws", ""])
    # manager fix 2026-10-01 07:30: header order now equals the row order (and the csv columns)
    L.extend(["| scope | target | S range (max-min) | EnergyPlus range | S SD | EnergyPlus SD | range ratio S/E | Pearson r over 20 draws | S mean | EnergyPlus mean |", "|---|---|---|---|---|---|---|---|---|---|"])
    for r in srows:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % tuple(r))
    L.append("")
    pk = [r for r in drows if r[1] == "all"]
    L.extend(["## District peak hour, scope all (kWh): S vs EnergyPlus, mean difference over the 20 draws", ""])
    for t in TN:
        v = [float(r[8]) for r in pk if r[2] == t and r[8] != ""]
        va = [float(r[5]) for r in pk if r[2] == t and r[5] != ""]
        L.append("* %s: annual difference S - E %.2f %% (mean over draws), peak-hour difference %.2f %% (mean), peak hour same in %d of 20 draws" % (t, np.mean(va), np.mean(v), sum(1 for r in pk if r[2] == t and r[9] == r[10])))
    io.open(OUT + "district_check_summary.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    for f in ("district_check.csv", "district_check_runs.csv", "district_check_draws.csv", "district_check_spread.csv", "district_check_summary.md"):
        print("WROTE %s md5 %s" % (f, s7.md5(OUT + f)))
    for ln in L[:40]:
        print("SUMMARY_MD " + ln)
    print("SUMMARY fails=%d %s" % (len(fails), fails))


if __name__ == "__main__":
    main()
