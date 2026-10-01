# -*- coding: utf-8 -*-
"""5J Step 6 part A checks (Speed CPU jobs; Spain + Italy only; NO test truth is read: only drivers, own predictions and logs).
  s6_checks.py snapshot : md5 + size + mtime of every checkpoint used, written once to test/ckpt_md5_snapshot.tsv (read-only)
  s6_checks.py dcheck   : s6_data.Data equals s5_data.Data with default arguments (flags off) on every tensor; the refusals; the test-store
                          Data against an independent re-derivation of own channels, weather, calendar and the clipped static vector
  s6_checks.py final    : counts per model and list, content of a sample of prediction files, open logs of the whole part, md5 table"""
import hashlib, io, json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import pandas as pd
import s6_common as s6
import s5_common as c

T = c.TRAIN
fails = []


def chk(name, ok, text=""):
    print("CHECK %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)
    if not ok:
        fails.append(name)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


CK_FILES = [T + "winner/pinned/best.pt", T + "ckpt/S/3/best.pt", T + "ckpt/S_seed2/best.pt", T + "ckpt/S_seed3/best.pt", T + "ckpt/C_seed1/best.pt",
            T + "ckpt/S_loco_es/best.pt", T + "ckpt/S_loco_it/best.pt"] + \
           [T + "ckpt/%s/%s.joblib" % (m, t) for m in ("B1", "B1_loco_es") for t in ("heating", "cooling", "equipment")]


def snapshot():
    sp = s6.TEST + "ckpt_md5_snapshot.tsv"
    if os.path.exists(sp):
        print("REFUSED: snapshot exists")
        sys.exit(4)
    lines = []
    for p in CK_FILES:
        st = os.stat(p)
        lines.append("%s\t%s\t%d\t%s" % (p, md5(p), st.st_size, time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(st.st_mtime))))
        print("SNAPSHOT " + lines[-1], flush=True)
    io.open(sp, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    os.chmod(sp, 0o444)
    wj = json.load(open(T + "winner/winner.json"))
    chk("snapshot_pinned_equals_winner_json", dict(l.split("\t")[:2] for l in lines)[T + "winner/pinned/best.pt"] == wj["ckpt_md5"])
    print("SNAPSHOT_DONE n=%d at %s" % (len(lines), time.strftime("%Y-%m-%dT%H:%M:%S")), flush=True)


def dcheck():
    import torch
    import s5_data as sd5
    import s6_data as sd6
    names = ["static", "hh_row", "nb", "pa", "pb", "cl_idx", "cal_idx", "T", "HHT", "W", "CAL", "lo", "tmu", "tsd"]
    for label, kw in (("default", {}), ("country_it_noclimate", {"country": "it", "drop_climate": True}), ("blind", {"blind": True})):
        a = sd5.Data("validation", "cpu", load_targets=True, **kw)
        b = sd6.Data("validation", "cpu", load_targets=True, **kw)
        same = {nm: bool(torch.equal(getattr(a, nm), getattr(b, nm))) for nm in names}
        chk("flags_off_s6_Data_equals_s5_Data_on_all_tensors_%s" % label, all(same.values()) and a.stats == b.stats and a.static_names == b.static_names and a.flats.equals(b.flats), str(same))
        rows = torch.tensor([0, 5, 100, 4000, 7000]) if label != "country_it_noclimate" else torch.tensor([0, 5, 100, 2000, 3500])
        days = torch.tensor([0, 200, 364, 17, 90])
        xa, sa, ya = a.windows(rows, days)
        xb, sb, yb = b.windows(rows, days)
        chk("flags_off_windows_equal_%s" % label, bool(torch.equal(xa, xb) and torch.equal(sa, sb) and torch.equal(ya, yb)))
        del a, b
    # refusals
    def refused(fn):
        try:
            fn()
            return False
        except PermissionError:
            return True
    chk("s5_Data_still_refuses_test_list (seen failing)", refused(lambda: sd5.Data("test_both_new", "cpu", load_targets=False)))
    chk("s6_Data_default_store_refuses_test_list (seen failing)", refused(lambda: sd6.Data("test_both_new", "cpu", load_targets=False)))
    chk("s6_Data_test_store_refuses_targets (seen failing)", refused(lambda: sd6.Data("test_both_new", "cpu", load_targets=True, store=sd6.TEST_STORE)))
    chk("s6_Data_test_store_refuses_development_list (seen failing)", refused(lambda: sd6.Data("development", "cpu", load_targets=False, store=sd6.TEST_STORE)))
    chk("s6_Data_refuses_any_other_store (seen failing)", refused(lambda: sd6.Data("validation", "cpu", load_targets=False, store="/speed-scratch/o_iseri/5J/test/")))
    # the test-store Data against an independent re-derivation
    ck = torch.load(T + "winner/pinned/best.pt", map_location="cpu", weights_only=False)
    ss = ck["static_stats"]
    for nm in s6.TEST_LISTS:
        d = sd6.Data(nm, "cpu", stats=ss, load_targets=False, store=sd6.TEST_STORE)
        fl = pd.read_parquet(s6.TSTORE + "flats_%s.parquet" % nm)
        chk("test_Data_%s_rows_equal_parquet_no_targets_no_pairs" % nm, len(d.flats) == len(fl) and d.T is None and len(d.pa) == 0, "rows=%d clip=%s" % (len(fl), d.clip_info["values_clipped"]))
        norm = json.load(open(s6.TSTORE + "norm.json"))
        cn = norm["channels"]
        zs = {cc: np.load(s6.TSTORE + "hh_%s.npz" % cc) for cc in c.COUNTRIES}
        # rows: first, a middle one, the last, and one with the largest n_dwellings
        ndw = fl["s_n_dwellings"].to_numpy()
        pick = sorted({0, len(fl) // 2, len(fl) - 1, int(np.argmax(ndw))})
        days = torch.tensor([3, 200, 364, 120])
        ok_all = True
        for r_ in pick:
            row = fl.iloc[r_]
            cc, hh_i, cid = row["country"], int(row["hh_index"]), row["climate_id"]
            x, st, _ = d.windows(torch.tensor([r_] * len(days)), days, with_y=False)
            for k, dd in enumerate(days.tolist()):
                hrs = (24 * dd - 168 + np.arange(192)) % 8760
                for ci, chn in enumerate(c.HH_CHANNELS):
                    ref = (zs[cc][chn][hh_i][hrs].astype(np.float64) - cn[chn]["mean"]) / cn[chn]["sd"]
                    ok_all &= bool(np.allclose(x[k, :, ci].numpy(), ref, atol=2e-5))
                w = np.load(s6.TSTORE + "weather_%s.npy" % cid).astype(np.float64)
                for wi, chn in enumerate(c.WEATHER_CHANNELS):
                    ok_all &= bool(np.allclose(x[k, :, 13 + wi].numpy(), (w[hrs, wi] - cn[chn]["mean"]) / cn[chn]["sd"], atol=2e-5))
                cal = np.load(s6.TSTORE + "calendar_%s.npy" % cc).astype(np.float64)
                for ci, chn in enumerate(c.CALENDAR_CHANNELS):
                    ok_all &= bool(np.allclose(x[k, :, 20 + ci].numpy(), (cal[hrs, ci] - cn[chn]["mean"]) / cn[chn]["sd"], atol=2e-5))
            sjson = json.load(open(s6.TSTORE + "static_cols.json"))
            sv = row[sjson["static"]].to_numpy(dtype=np.float64)
            ref = np.clip((sv - np.array(ss["mean"])) / np.array(ss["sd"]), np.array(ss["zmin"]), np.array(ss["zmax"]))
            got = st[0].numpy()[:len(sjson["static"])].astype(np.float64)
            ok_all &= bool(np.allclose(got, ref, atol=2e-6))
            ok_all &= bool(np.allclose(st[0].numpy()[len(sjson["static"]):], row[sjson["climate_onehot"]].to_numpy(dtype=np.float64)))
        chk("test_Data_%s_windows_equal_independent_rederivation (own channels, weather, calendar, clipped static)" % nm, ok_all, "rows=%s days=%s" % (pick, days.tolist()))
        del d
    # planted: a changed norm statistic must be caught by the same comparison (seen failing)
    x0 = np.allclose((zs["es"]["people"][0][:10].astype(np.float64) - cn["people"]["mean"] - 1.0) / cn["people"]["sd"], (zs["es"]["people"][0][:10].astype(np.float64) - cn["people"]["mean"]) / cn["people"]["sd"], atol=2e-5)
    chk("rederivation_planted_shift_CAUGHT (seen failing)", not x0)
    print("DCHECK_DONE %s fails=%s" % ("OK" if not fails else "FAILED", fails), flush=True)


def final():
    L = s6.lists()
    LOG = []
    R = s6.runs(LOG)
    models = {"B0": None, "B1": None, "B1_loco_es": "it", "B1_loco_it": "es", "S": None, "C": None, "S_seed2": None, "S_seed3": None, "S_loco_es": "it", "S_loco_it": "es"}
    rng = np.random.default_rng(20260930)
    table = []
    for m, cc in models.items():
        ok_m = True
        for nm in s6.TEST_LISTS:
            ids = [r for r in L[nm] if cc is None or R[r]["country"] == cc]
            miss, extra = [], []
            have = set()
            for cl in sorted({R[r]["climate_id"] for r in ids}):
                d = "%s%s/%s/" % (s6.TPRED, m, cl)
                if os.path.isdir(d):
                    have |= {f[:-7] for f in os.listdir(d) if f.endswith(".csv.gz")}
            want = set(ids)
            miss = sorted(want - have)
            # extra files of other lists / countries inside this model folder are expected; report extras relative to ALL lists
            table.append((m, nm, len(ids), len(miss)))
            ok_m &= not miss
            print("COUNT model=%s list=%s runs_expected=%d files_present=%d missing=%d %s" % (m, nm, len(want), len(want & have), len(miss), miss[:3]), flush=True)
        # extra files: everything in the model folder must be a run of the three lists (of the predicted country)
        allids = {r for nm in s6.TEST_LISTS for r in L[nm] if cc is None or R[r]["country"] == cc}
        have_all = set()
        for cl in os.listdir(s6.TPRED + m):
            have_all |= {f[:-7] for f in os.listdir(s6.TPRED + m + "/" + cl) if f.endswith(".csv.gz")}
        chk("model_%s_folder_holds_exactly_the_expected_runs" % m, ok_m and have_all == allids, "present=%d expected=%d extra=%d" % (len(have_all), len(allids), len(have_all - allids)))
        # content of a sample
        ids = sorted(allids)
        big = sorted(ids, key=lambda r: -int(R[r]["n_dwellings"]))[:3]
        pick = sorted(set(rng.choice(ids, min(25, len(ids)), replace=False).tolist()) | set(big))
        bad = []
        mn = 1e9
        for rid in pick:
            nd = int(R[rid]["n_dwellings"])
            p = "%s%s/%s/%s.csv.gz" % (s6.TPRED, m, R[rid]["climate_id"], rid)
            df = pd.read_csv(p, comment="#", compression="gzip")
            v = df[c.TARGETS].to_numpy(dtype=np.float64)
            tot = df["equipment_kwh"] + (df["heating_kwh"] + df["cooling_kwh"]) / c.COP
            okf = (len(df) == nd * c.H and list(df.columns) == ["dwelling", "hour"] + c.TARGETS and np.isfinite(v).all() and v.min() >= 0.0 and
                   np.array_equal(df["dwelling"].to_numpy(), np.repeat(np.arange(nd), c.H)) and np.array_equal(df["hour"].to_numpy(), np.tile(np.arange(1, c.H + 1), nd)) and float(np.abs(tot - df["total_elec_kwh"]).max()) < 1e-4)
            mn = min(mn, float(v.min()))
            if not okf:
                bad.append(rid)
        chk("model_%s_sample_files_complete_finite_nonnegative_total_rule" % m, not bad, "sampled=%d bad=%s min_value=%.3g" % (len(pick), bad[:3], mn))
    # open logs of the whole part
    b0s = s6.b0_ids()
    n_lines, kinds, badl = 0, set(), []
    for f in sorted(os.listdir(s6.TEST)):
        if f.startswith("openlog_") and f.endswith(".tsv"):
            lines = s6.read_log_file(s6.TEST + f)
            n_lines += len(lines)
            kinds |= {k for k, _, _ in lines}
            bl = s6.check_lines(lines, b0s)
            badl += [(f,) + x for x in bl]
            print("OPENLOG file=%s lines=%d kinds=%s" % (f, len(lines), sorted({k for k, _, _ in lines})), flush=True)
    chk("all_open_logs_kind_driver_or_b0_nothing_under_extracted_except_b0_runs", not badl and kinds <= {"driver", "b0"}, "files_lines=%d kinds=%s offending=%d %s" % (n_lines, sorted(kinds), len(badl), badl[:2]))
    pl = s6.check_lines([("driver", "x", s6.EXTRACTED + "a/b.csv.gz"), ("truth", "x", "p")], b0s)
    chk("open_log_check_planted_lines_CAUGHT (seen failing)", len(pl) == 2)
    # b0 reads are b0 runs only and every b0 run read exists in b0_dev U b0_test
    b0lines = [x for x in s6.read_log_file(s6.TEST + "openlog_b0.tsv") if x[0] == "b0"]
    chk("b0_log_distinct_runs_inside_b0_lists", {x[1] for x in b0lines} <= b0s, "b0 reads=%d distinct=%d" % (len(b0lines), len({x[1] for x in b0lines})))
    print("FINAL_DONE %s fails=%s" % ("OK" if not fails else "FAILED", fails), flush=True)


if __name__ == "__main__":
    {"snapshot": snapshot, "dcheck": dcheck, "final": final}[sys.argv[1]]()
    sys.exit(0 if not fails else 1)
