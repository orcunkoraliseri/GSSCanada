# T9-13 Task 1 -- per-channel weekly-mean occupancy for EVERY candidate reference.
# Mirrors commercial_integration.py::_channel_occ_24 exactly (48->24 pair-average, retail
# weekend = mean(sat24,sun24), hotel = 12-month average, residential = per-household 24h).
import os, sys, json
import pandas as pd, numpy as np

ROOT = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main"
S7 = os.path.join(ROOT, "3J_docs_occ_nTemp", "Leg3_4-split", "Step7_docs", "outputs_step7")
HIST = os.path.join(ROOT, "3J_docs_occ_nTemp", "Leg3_4-split", "Step8_docs",
                    "outputs_step8", "historical_schedules")
OFFICE_ARCHETYPE = "Office_Knowledge"
BUNDLE_OFFICE_BAND = {"cons": "conservative", "central": "hybrid", "opt": "fullyhybrid"}


def to24(v):
    v = [float(x) for x in v]
    if len(v) == 24:
        return v
    if len(v) == 48:
        return [(v[2 * h] + v[2 * h + 1]) / 2.0 for h in range(24)]
    raise ValueError(f"unexpected length {len(v)}")


def mean24(v):
    return sum(v) / len(v)


# ---- office -------------------------------------------------------------
def office_means(path, band):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    sub = df[(df["office_archetype"] == OFFICE_ARCHETYPE) & (df["BAND"] == band)]
    if sub.empty:
        raise ValueError(f"no office rows {path} band={band}")
    wd = sub[sub["Day_Type"] == "Weekday"].sort_values("Hour")["AT_WORK_fraction"].tolist()
    we = sub[sub["Day_Type"] == "Weekend"].sort_values("Hour")["AT_WORK_fraction"].tolist()
    assert len(wd) == 24 and len(we) == 24
    return mean24(to24(wd)), mean24(to24(we))


# ---- retail -------------------------------------------------------------
def retail_means(path, pr):
    df = pd.read_csv(path)
    sub = df[df["PR"] == pr]
    if sub.empty:
        raise ValueError(f"no retail rows {path} pr={pr}")
    out = {}
    for dt, k in [("Weekday", "wd"), ("Saturday", "sat"), ("Sunday", "sun")]:
        s = sub[sub["Day_Type"] == dt].sort_values("slot")
        assert len(s) == 48, f"{path} {dt} {len(s)}"
        out[k] = to24(s["multiplier"].tolist())
    we = [(a + b) / 2.0 for a, b in zip(out["sat"], out["sun"])]
    return mean24(out["wd"]), mean24(we)


# ---- hotel --------------------------------------------------------------
def hotel_means(path, pr):
    df = pd.read_csv(path)
    sub = df[df["PR"] == pr]
    if sub.empty:
        raise ValueError(f"no hotel rows {path} pr={pr}")
    mwd, mwe = [], []
    for m in range(1, 13):
        wd = sub[(sub["MONTH"] == m) & (sub["Day_Type"] == "Weekday")].sort_values("slot")
        we = sub[(sub["MONTH"] == m) & (sub["Day_Type"] == "Weekend")].sort_values("slot")
        assert len(wd) == 48 and len(we) == 48
        mwd.append(to24(wd["multiplier"].fillna(0.0).tolist()))
        mwe.append(to24(we["multiplier"].fillna(0.0).tolist()))
    avg_wd = [sum(m[h] for m in mwd) / 12.0 for h in range(24)]
    avg_we = [sum(m[h] for m in mwe) / 12.0 for h in range(24)]
    return mean24(avg_wd), mean24(avg_we)


# ---- residential --------------------------------------------------------
RESID_DTYPE = None  # filled from the injector's own constant


def resid_stats(path):
    df = pd.read_csv(path, usecols=["SIM_HH_ID", "Day_Type", "Hour", "DTYPE",
                                    "Occupancy_Schedule"])
    df = df[df["DTYPE"].isin(RESID_DTYPE)]
    cnt = df.groupby(["SIM_HH_ID", "Day_Type"]).size().unstack(fill_value=0)
    ok = cnt.index[(cnt.get("Weekday", 0) == 24) & (cnt.get("Weekend", 0) == 24)]
    n_drop = len(cnt.index) - len(ok)
    df = df[df["SIM_HH_ID"].isin(ok)]
    g = df.groupby(["SIM_HH_ID", "Day_Type"])["Occupancy_Schedule"].mean().unstack()
    return {"n_hh": int(len(ok)), "n_dropped": int(n_drop),
            "mean_wd": float(g["Weekday"].mean()), "mean_we": float(g["Weekend"].mean()),
            "hh_wd": g["Weekday"].to_numpy(), "hh_we": g["Weekend"].to_numpy()}


# ---- scenario wiring (mirrors _build_scenarios) --------------------------
SCEN = [
    ("Y2022",            ("office_presence_multiplier_2022.csv", S7, "observed"),
                          ("retail_presence_multiplier_2022.csv", S7),
                          ("hotel_schedule_multiplier_2022.csv", S7),
                          ("BEM_Schedules_4split_2022.csv", S7)),
    ("B_cons",           ("office_presence_multiplier_2030.csv", S7, BUNDLE_OFFICE_BAND["cons"]),
                          ("retail_presence_multiplier_2030_cons.csv", S7),
                          ("hotel_schedule_multiplier_2030_cons.csv", S7),
                          ("BEM_Schedules_4split_2030_cons.csv", S7)),
    ("B_central",        ("office_presence_multiplier_2030.csv", S7, BUNDLE_OFFICE_BAND["central"]),
                          ("retail_presence_multiplier_2030_central.csv", S7),
                          ("hotel_schedule_multiplier_2030_central.csv", S7),
                          ("BEM_Schedules_4split_2030_central.csv", S7)),
    ("B_opt",            ("office_presence_multiplier_2030.csv", S7, BUNDLE_OFFICE_BAND["opt"]),
                          ("retail_presence_multiplier_2030_opt.csv", S7),
                          ("hotel_schedule_multiplier_2030_opt.csv", S7),
                          ("BEM_Schedules_4split_2030_opt.csv", S7)),
    ("Y2005",            ("office_presence_multiplier_2005.csv", HIST, "observed"),
                          ("retail_presence_multiplier_2005.csv", HIST), None,
                          ("BEM_Schedules_4split_2005.csv", HIST)),
    ("Y2010",            ("office_presence_multiplier_2010.csv", HIST, "observed"),
                          ("retail_presence_multiplier_2010.csv", HIST), None,
                          ("BEM_Schedules_4split_2010.csv", HIST)),
    ("Y2015",            ("office_presence_multiplier_2015.csv", HIST, "observed"),
                          ("retail_presence_multiplier_2015.csv", HIST), None,
                          ("BEM_Schedules_4split_2015.csv", HIST)),
    ("sens_office_cons", ("office_presence_multiplier_2030.csv", S7, BUNDLE_OFFICE_BAND["cons"]),
                          ("retail_presence_multiplier_2030_central.csv", S7),
                          ("hotel_schedule_multiplier_2030_central.csv", S7),
                          ("BEM_Schedules_4split_2030_cons.csv", S7)),
    ("sens_office_opt",  ("office_presence_multiplier_2030.csv", S7, BUNDLE_OFFICE_BAND["opt"]),
                          ("retail_presence_multiplier_2030_central.csv", S7),
                          ("hotel_schedule_multiplier_2030_central.csv", S7),
                          ("BEM_Schedules_4split_2030_opt.csv", S7)),
    ("sens_retail_cons", ("office_presence_multiplier_2030.csv", S7, BUNDLE_OFFICE_BAND["central"]),
                          ("retail_presence_multiplier_2030_cons.csv", S7),
                          ("hotel_schedule_multiplier_2030_central.csv", S7),
                          ("BEM_Schedules_4split_2030_central.csv", S7)),
    ("sens_retail_opt",  ("office_presence_multiplier_2030.csv", S7, BUNDLE_OFFICE_BAND["central"]),
                          ("retail_presence_multiplier_2030_opt.csv", S7),
                          ("hotel_schedule_multiplier_2030_central.csv", S7),
                          ("BEM_Schedules_4split_2030_central.csv", S7)),
    ("sens_hotel_cons",  ("office_presence_multiplier_2030.csv", S7, BUNDLE_OFFICE_BAND["central"]),
                          ("retail_presence_multiplier_2030_central.csv", S7),
                          ("hotel_schedule_multiplier_2030_cons.csv", S7),
                          ("BEM_Schedules_4split_2030_central.csv", S7)),
    ("sens_hotel_opt",   ("office_presence_multiplier_2030.csv", S7, BUNDLE_OFFICE_BAND["central"]),
                          ("retail_presence_multiplier_2030_central.csv", S7),
                          ("hotel_schedule_multiplier_2030_opt.csv", S7),
                          ("BEM_Schedules_4split_2030_central.csv", S7)),
]

PRS = ["QC", "AB"]


def main():
    global RESID_DTYPE
    sys.path.insert(0, ROOT)
    from eSim_bem_utils.commercial_integration import RESIDENTIAL_DTYPE_APARTMENT
    RESID_DTYPE = list(RESIDENTIAL_DTYPE_APARTMENT)
    print(f"# RESIDENTIAL_DTYPE_APARTMENT = {RESID_DTYPE}")

    off_cache, ret_cache, hot_cache, res_cache = {}, {}, {}, {}
    table = {}
    for tag, off, ret, hot, res in SCEN:
        row = {}
        k = (off[0], off[2])
        if k not in off_cache:
            off_cache[k] = office_means(os.path.join(off[1], off[0]), off[2])
        row["office"] = {"QC": off_cache[k], "AB": off_cache[k], "src": f"{off[0]}[{off[2]}]"}

        row["retail"] = {"src": ret[0]}
        for pr in PRS:
            kk = (ret[0], pr)
            if kk not in ret_cache:
                ret_cache[kk] = retail_means(os.path.join(ret[1], ret[0]), pr)
            row["retail"][pr] = ret_cache[kk]

        if hot is None:
            row["hotel"] = None
        else:
            row["hotel"] = {"src": hot[0]}
            for pr in PRS:
                kk = (hot[0], pr)
                if kk not in hot_cache:
                    hot_cache[kk] = hotel_means(os.path.join(hot[1], hot[0]), pr)
                row["hotel"][pr] = hot_cache[kk]

        if res[0] not in res_cache:
            res_cache[res[0]] = resid_stats(os.path.join(res[1], res[0]))
            s = res_cache[res[0]]
            print(f"# resid {res[0]}: n_hh={s['n_hh']} dropped={s['n_dropped']} "
                  f"mean_wd={s['mean_wd']:.6f} mean_we={s['mean_we']:.6f}", flush=True)
        s = res_cache[res[0]]
        row["residential"] = {"QC": (s["mean_wd"], s["mean_we"]),
                              "AB": (s["mean_wd"], s["mean_we"]), "src": res[0]}
        table[tag] = row

    # ---------------- part 1: raw weekly means ----------------
    print("\n" + "=" * 100)
    print("PART 1 -- weekly-mean occupancy per scenario x channel (mean_wd / mean_we)")
    print("=" * 100)
    hdr = f"{'scenario':<18}" + "".join(
        f"{c[:6]+'.'+pr:>18}" for c in ("office", "retail", "hotel", "resid") for pr in PRS)
    print(hdr)
    for tag, _o, _r, _h, _s in SCEN:
        row = table[tag]
        cells = []
        for ch in ("office", "retail", "hotel", "residential"):
            for pr in PRS:
                v = row[ch]
                if v is None:
                    cells.append(f"{'--absent--':>18}")
                else:
                    cells.append(f"{v[pr][0]:>8.4f}/{v[pr][1]:<8.4f}"[:18].rjust(18))
        print(f"{tag:<18}" + "".join(cells))

    # ---------------- part 2: r/R for every candidate baseline ----------------
    print("\n" + "=" * 100)
    print("PART 2 -- r_wd / r_we / R for every candidate baseline reference")
    print("       R>1.5 flagged with '!!'  (water-heater resize -- plant-sizing effect)")
    print("=" * 100)
    flags = []
    for base_tag, _o, _r, _h, _s in SCEN:
        base = table[base_tag]
        print(f"\n--- baseline = {base_tag} " + "-" * 60)
        print(f"{'scenario':<18}{'channel':<14}{'r_wd':>10}{'r_we':>10}{'R':>10}   note")
        for tag, _o2, _r2, _h2, _s2 in SCEN:
            row = table[tag]
            for ch in ("office", "retail", "hotel", "residential"):
                for pr in PRS:
                    if ch in ("office", "residential") and pr == "AB":
                        continue        # pr-independent, printed once
                    b, t = base[ch], row[ch]
                    label = ch if ch in ("office", "residential") else f"{ch}.{pr}"
                    if b is None:
                        print(f"{tag:<18}{label:<14}{'':>10}{'':>10}{'':>10}   "
                              f"BASELINE HAS NO {ch.upper()} -> unresolvable")
                        continue
                    if t is None:
                        print(f"{tag:<18}{label:<14}{'':>10}{'':>10}{'':>10}   "
                              f"channel not injected in this scenario")
                        continue
                    bwd, bwe = b[pr]
                    twd, twe = t[pr]
                    r_wd = twd / bwd if bwd > 1e-12 else float("nan")
                    r_we = twe / bwe if bwe > 1e-12 else float("nan")
                    R = max(r_wd, r_we)
                    note = ""
                    if R > 1.5:
                        note = "!! R>1.5"
                        flags.append((base_tag, tag, label, R))
                    if abs(r_wd - 1) < 1e-9 and abs(r_we - 1) < 1e-9:
                        note = "(exact no-op)"
                    print(f"{tag:<18}{label:<14}{r_wd:>10.4f}{r_we:>10.4f}{R:>10.4f}   {note}")

    # ---------------- part 3: residential per-household r spread ----------------
    print("\n" + "=" * 100)
    print("PART 3 -- residential is per-HOUSEHOLD: r varies within the channel.")
    print("          Spread of r_wd over the eligible pool, per baseline (r_max=3.0 clip risk)")
    print("=" * 100)
    print(f"{'baseline':<18}{'scenario':<18}{'min':>9}{'p50':>9}{'p95':>9}{'p99':>9}"
          f"{'max':>9}{'%>1.5':>9}{'%>3.0':>9}")
    for base_tag, _o, _r, _h, bs in SCEN:
        bref = res_cache[bs[0]]["mean_wd"]
        for tag, _o2, _r2, _h2, ts in SCEN:
            hh = res_cache[ts[0]]["hh_wd"] / bref
            print(f"{base_tag:<18}{tag:<18}{hh.min():>9.3f}"
                  f"{np.percentile(hh,50):>9.3f}{np.percentile(hh,95):>9.3f}"
                  f"{np.percentile(hh,99):>9.3f}{hh.max():>9.3f}"
                  f"{100*(hh>1.5).mean():>9.2f}{100*(hh>3.0).mean():>9.2f}")

    print("\n" + "=" * 100)
    print(f"R>1.5 flags: {len(flags)}")
    for f in flags:
        print(f"  baseline={f[0]:<16} scenario={f[1]:<18} {f[2]:<14} R={f[3]:.4f}")

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "t913_reference_table.json"), "w") as fh:
        json.dump({t: {c: (None if v is None else {k: list(x) if isinstance(x, tuple) else x
                                                   for k, x in v.items()})
                       for c, v in r.items()} for t, r in table.items()}, fh, indent=1)


if __name__ == "__main__":
    main()
