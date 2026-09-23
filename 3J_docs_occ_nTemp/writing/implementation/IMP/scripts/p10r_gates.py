"""P10R gates (written BEFORE any P10R product exists; each must be seen failing on the frozen products).

Gate (a) Y2022 residential frame. Weekday clock-hour 09..16 mean of the hourly HH-mean of
    `Occupancy_Schedule` (exactly p10_05.res_levels + BIZH=range(9,17)) must be 0.4180 +/- 0.005.
    Frozen `BEM_Schedules_4split_2022.csv` (281d96c0) gives 0.3006 -> must FAIL.
Gate (b) Weekend labour-force rake. Per LFTAG (1 and 2), weekend (DDAY_STRATA 2,3) day-mean over
    48 slots of hom30 and wrk30 in the 2030 file, BAND == hybrid (central scenario), minus the same
    mean over OBS2022 (AUG CYCLE_YEAR==2022 & IS_SYNTHETIC==0, same LFTAG). All four |delta| <= 1.4 pp.
    `_C_v2` gives LFTAG1 home -8.99 / work +6.48 -> must FAIL. Pooled-over-bands and cons/opt printed
    as INFO (not gated; see P10R_fix.md Decisions).
Gate (c) Mutex. step7.check_mutex (H8) == 0 conflicts on every file/frame named, AND (if a
    calibration log is given) the log shows the post-resolution hard assert passed at every stage
    (6 stage labels present, final conflicts 0). Control: an in-memory copy with ONE injected
    home&work conflict must FAIL.
Gate (d) Cell provenance. For every cell dir given, manifest INPUTS_HASH_DETAIL must (1) point every
    channel at a file inside outputs_step7_P10R, (2) carry NO frozen-arm md5 for the residential,
    office or retail channel, and (3) match the P10R product registry md5 for that file name, which
    must also equal the md5 of the file on disk now. Frozen cell manifests must FAIL.

Outcomes per gate: NOT_RUN (not requested / input absent), PASS, FAIL, NOT_EVALUABLE (crashed; never
PASS). Exit code: 0 = every requested gate PASS; 1 = at least one FAIL; 2 = no FAIL but at least one
NOT_EVALUABLE; 3 = --expect FAIL given and some requested gate did NOT fail (control not seen failing).

    py -3 p10r_gates.py --res2022 F --c2030 F --mutex F [F ...] --callog LOG --cells D [D ...]
                        [--registry JSON] [--expect PASS|FAIL] [--out JSON]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

J3 = Path(__file__).resolve().parents[4]
LEG3 = J3 / "Leg3_4-split"
AUG = LEG3 / "Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv"
S7_OLD = LEG3 / "Step7_docs/outputs_step7"
S7_NEW = LEG3 / "Step7_docs/outputs_step7_P10R"
HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
WRK = [f"wrk30_{i:03d}" for i in range(1, 49)]
RET = [f"ret30_{i:03d}" for i in range(1, 49)]
BIZH = list(range(9, 17))
A_TARGET, A_TOL = 0.4180, 0.005
B_TOL_PP = 1.4
STAGES = ["post-StageB", "post-GlobalMindwell", "post-StageC0", "post-StageC1",
          "post-StageRetail", "post-StageC2"]
# frozen-arm md5s of the products P10R replaces (p10_01_manifests.out)
FROZEN_CHANGED_MD5 = {
    "281d96c06b25432336149c854ac1b2e2", "ff0fc98704042f79c66e993e0400a7bb", "e31f528e26bd74286a90c425921fd32b",
    "df94ff6a3a084c2b5543674b9b902c22", "d36388c8958f4f3ac72f5e9ae508c711", "4462726d24889c88d62831e30191d300",
    "1536c98c5358ece477290d45f0505e4f", "cf8721c62030fc7c1f23b999f85056d0",
    "0e3b256e69713b3942161adc1ee247d2", "f7152e5a887f636c4a13e5b4295555f9",
}
CHANGED_CHANNELS = ("residential", "office", "retail")


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _step7():
    spec = importlib.util.spec_from_file_location("s7_gates", LEG3 / "Step7_docs/3rdJ_07_aug_to_bem_4split.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- gate (a)
def gate_a(path):
    df = pd.read_csv(path, usecols=["Day_Type", "Hour", "Occupancy_Schedule"])
    wd = df[df.Day_Type == "Weekday"].groupby("Hour").Occupancy_Schedule.mean().reindex(range(24)).values
    v = float(wd[BIZH].mean())
    ok = abs(v - A_TARGET) <= A_TOL
    return ("PASS" if ok else "FAIL",
            f"{Path(path).name} md5={md5(path)[:8]} WD 09-17h = {v:.4f} vs {A_TARGET:.4f} +/- {A_TOL} "
            f"(|d|={abs(v - A_TARGET):.4f}); WD day-mean {np.nanmean(wd):.4f}")


# ---------------------------------------------------------------- gate (b)
def obs22():
    a = pd.read_csv(AUG, low_memory=False, usecols=["DDAY_STRATA", "LFTAG", "CYCLE_YEAR", "IS_SYNTHETIC"] + HOM + WRK + RET)
    return a[(a.CYCLE_YEAR == 2022) & (a.IS_SYNTHETIC == 0)]


def se_report(o):
    lines = []
    we = o[o.DDAY_STRATA.isin([2, 3])]
    for lf in (1, 2):
        s = we[we.LFTAG == lf]
        for nm, cols in (("home", HOM), ("work", WRK)):
            dm = s[cols].to_numpy(float).mean(1)
            se = dm.std(ddof=1) / np.sqrt(len(dm)) if len(dm) > 1 else float("nan")
            lines.append(f"OBS2022 weekend LFTAG={lf} n={len(s)} {nm} day-mean={dm.mean():.4f} SE={100 * se:.2f} pp")
    dm = we[HOM].to_numpy(float).mean(1)
    lines.append(f"OBS2022 weekend ALL n={len(we)} home SE={100 * dm.std(ddof=1) / np.sqrt(len(dm)):.2f} pp "
                 f"work SE={100 * we[WRK].to_numpy(float).mean(1).std(ddof=1) / np.sqrt(len(we)):.2f} pp")
    return lines


def gate_b(path, o):
    d = pd.read_csv(path, low_memory=False, usecols=["DDAY_STRATA", "LFTAG", "BAND"] + HOM + WRK)
    ow = o[o.DDAY_STRATA.isin([2, 3])]
    dw = d[d.DDAY_STRATA.isin([2, 3])]
    info, gated, ok = [], [], True
    for band in ("hybrid", "ALL", "conservative", "fullyhybrid"):
        db = dw if band == "ALL" else dw[dw.BAND == band]
        for lf in (1, 2):
            s, r = db[db.LFTAG == lf], ow[ow.LFTAG == lf]
            for nm, cols in (("home", HOM), ("work", WRK)):
                gap = 100 * (s[cols].to_numpy(float).mean() - r[cols].to_numpy(float).mean())
                txt = f"band={band:12s} LFTAG={lf} n={len(s):5d} {nm}: {gap:+.2f} pp"
                if band == "hybrid":
                    passed = abs(gap) <= B_TOL_PP
                    ok &= passed
                    gated.append(txt + ("  ok" if passed else "  OUT (> 1.4)"))
                else:
                    info.append("INFO " + txt)
    return ("PASS" if ok else "FAIL",
            f"{Path(path).name} md5={md5(path)[:8]}\n      GATED: " + "\n      GATED: ".join(gated)
            + "\n      " + "\n      ".join(info))


# ---------------------------------------------------------------- gate (c)
def gate_c(paths, callog, s7):
    msgs, ok = [], True
    for p in paths:
        df = pd.read_csv(p, low_memory=False, usecols=lambda c: c in set(HOM + WRK + RET))
        try:
            s7.check_mutex(df, Path(p).name)
            msgs.append(f"H8 0 conflicts: {Path(p).name} ({len(df):,} rows)")
        except AssertionError as e:
            ok = False
            msgs.append(f"H8 FAIL: {str(e)[:160]}")
    if callog:
        txt = Path(callog).read_text(encoding="utf-8", errors="replace")
        for st in STAGES:
            hit = re.findall(r"\[6H MUTEX\] " + re.escape(st) + r": ([^\n]*)", txt)
            if not hit:
                ok = False
                msgs.append(f"calibration log: stage {st} NOT FOUND (hard assert not seen)")
            else:
                msgs.append(f"calibration log: {st}: {hit[-1][:120]}")
        fin = re.findall(r"Final 3-way mutex conflicts: (\d+)", txt)
        if not fin or fin[-1] != "0":
            ok = False
        msgs.append(f"calibration log: final conflicts = {fin[-1] if fin else 'NOT FOUND'}")
    return ("PASS" if ok else "FAIL", "\n      ".join(msgs))


def gate_c_control(path, s7):
    df = pd.read_csv(path, low_memory=False, nrows=2000, usecols=lambda c: c in set(HOM + WRK + RET))
    df.loc[df.index[0], HOM[20]] = 1
    df.loc[df.index[0], WRK[20]] = 1
    df.loc[df.index[0], RET[20]] = 0
    try:
        s7.check_mutex(df, "control: 1 injected home&work conflict")
        return ("PASS", "check_mutex did NOT fire on an injected conflict")
    except AssertionError as e:
        return ("FAIL", f"check_mutex fired on the injected conflict: {str(e)[:120]}")


# ---------------------------------------------------------------- gate (d)
def gate_d(cells, registry):
    reg = json.load(open(registry, encoding="utf-8")) if registry and Path(registry).exists() else None
    msgs, ok, evaluable = [], True, True
    for c in cells:
        man = json.load(open(Path(c) / "manifest.json", encoding="utf-8"))
        det = man.get("INPUTS_HASH_DETAIL") or []
        if not det:
            ok = False
            msgs.append(f"{Path(c).name}: INPUTS_HASH_DETAIL empty")
            continue
        for d in det:
            ch, p, m = d["channel"], d["csv_path"], d["csv_md5"]
            name = Path(p.replace("\\", "/")).name
            in_new = Path(p.replace("\\", "/")).parent.resolve() == S7_NEW.resolve()
            frozen = m in FROZEN_CHANGED_MD5 and ch in CHANGED_CHANNELS
            if reg is None:
                evaluable = False
                reg_ok, rtxt = False, "registry absent"
            else:
                exp = reg.get(name)
                disk = md5(p) if Path(p).exists() else None
                reg_ok = exp is not None and exp == m == disk
                rtxt = f"registry={str(exp)[:8]} disk={str(disk)[:8]}"
            good = in_new and not frozen and reg_ok
            ok &= good
            msgs.append(f"{Path(c).name} {ch:11s} {name:45s} md5={m[:8]} in_P10R_dir={in_new} "
                        f"frozen_md5={frozen} {rtxt} -> {'ok' if good else 'BAD'}")
    if not ok:
        return ("FAIL", "\n      ".join(msgs))
    if not evaluable:
        return ("NOT_EVALUABLE", "\n      ".join(msgs))
    return ("PASS", "\n      ".join(msgs))


# ---------------------------------------------------------------- gate (e)  [added 2026-09-22 on the
# manager's scope change: the P10R arm carries the T9-9 standby-floor fix]
def _idf_objects(path):
    txt = Path(path).read_text(encoding="utf-8", errors="replace")
    txt = re.sub(r"!.*", "", txt)
    for raw in txt.split(";"):
        f = [x.strip() for x in raw.split(",")]
        if f and f[0]:
            yield f[0].upper(), f


def gate_e(idf_path):
    """Every office LIGHTS/ELECTRICEQUIPMENT object must carry a derived MXU_Office_Load_* schedule
    whose minimum value (all Schedule:Compact numeric fields) is > 0; none may carry MXU_Office_People_*.
    Retail and hotel are reported (INFO)."""
    objs = list(_idf_objects(idf_path))
    comp = {f[1]: f for c, f in objs if c == "SCHEDULE:COMPACT" and len(f) > 1}

    def minval(name):
        vals = []
        for x in comp.get(name, [])[3:]:
            try:
                vals.append(float(x))
            except ValueError:
                pass
        return min(vals) if vals else None

    rows, ok = [], True
    counts = {}
    for c, f in objs:
        if c not in ("LIGHTS", "ELECTRICEQUIPMENT") or len(f) < 4:
            continue
        sch = f[3]
        for ch in ("Office", "Retail", "Hotel"):
            if sch.startswith(f"MXU_{ch}_"):
                kind = "Load" if sch.startswith(f"MXU_{ch}_Load_") else ("People" if sch.startswith(f"MXU_{ch}_People_") else "other")
                mv = minval(sch)
                counts[(ch, c, kind)] = counts.get((ch, c, kind), 0) + 1
                if ch == "Office":
                    good = kind == "Load" and mv is not None and mv > 0
                    ok &= good
                    if len(rows) < 14:
                        rows.append(f"{c:17s} {f[1][:34]:34s} -> {sch[:44]:44s} min={mv} {'ok' if good else 'BAD'}")
    n_office = sum(v for (ch, c, k), v in counts.items() if ch == "Office")
    if n_office == 0:
        ok = False
    summ = ", ".join(f"{ch}/{c}/{k}={v}" for (ch, c, k), v in sorted(counts.items()))
    return ("PASS" if ok else "FAIL",
            f"{Path(idf_path).parent.name}/{Path(idf_path).name}: office objects on MXU_Office_*: {n_office}; "
            f"counts {summ}\n      " + "\n      ".join(rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res2022")
    ap.add_argument("--c2030")
    ap.add_argument("--mutex", nargs="*", default=[])
    ap.add_argument("--callog")
    ap.add_argument("--mutex-control", action="store_true")
    ap.add_argument("--cells", nargs="*", default=[])
    ap.add_argument("--registry")
    ap.add_argument("--idf", nargs="*", default=[], help="gate (e): injected_resized.idf path(s)")
    ap.add_argument("--se", action="store_true", help="print the OBS2022 weekend SEs")
    ap.add_argument("--expect", choices=["PASS", "FAIL"], default="PASS")
    ap.add_argument("--out")
    a = ap.parse_args()

    res = {k: ("NOT_RUN", "") for k in ("a", "b", "c", "c_control", "d", "e")}
    need_obs = a.c2030 or a.se
    o = obs22() if need_obs else None
    s7 = _step7() if (a.mutex or a.mutex_control or a.callog) else None
    if a.se:
        print("\n".join(se_report(o)))

    def run(k, fn):
        try:
            res[k] = fn()
        except Exception as e:
            res[k] = ("NOT_EVALUABLE", f"crashed: {type(e).__name__}: {e}\n{traceback.format_exc()[-800:]}")

    if a.res2022:
        run("a", lambda: gate_a(a.res2022))
    if a.c2030:
        run("b", lambda: gate_b(a.c2030, o))
    if a.mutex or a.callog:
        run("c", lambda: gate_c(a.mutex, a.callog, s7))
    if a.mutex_control:
        run("c_control", lambda: gate_c_control(a.mutex[0] if a.mutex else a.c2030, s7))
    if a.cells:
        run("d", lambda: gate_d(a.cells, a.registry))
    if a.idf:
        def _e():
            outs = [gate_e(p) for p in a.idf]
            st = "PASS" if all(o[0] == "PASS" for o in outs) else "FAIL"
            return (st, "\n      ".join(o[1] for o in outs))
        run("e", _e)

    print(f"\n==== P10R GATES (expect {a.expect}) ====")
    requested = [k for k, v in res.items() if v[0] != "NOT_RUN"]
    for k, (st, msg) in res.items():
        tag = ""
        if st != "NOT_RUN" and a.expect == "FAIL":
            tag = "  [control SEEN FAILING]" if st == "FAIL" else "  [control NOT seen failing]"
        print(f"gate ({k}): {st}{tag}\n      {msg}")
    sts = [res[k][0] for k in requested]
    if a.expect == "FAIL":
        code = 0 if all(s == "FAIL" for s in sts) else 3
    else:
        code = 1 if "FAIL" in sts else (2 if "NOT_EVALUABLE" in sts else 0)
    print(f"SUMMARY: " + "  ".join(f"({k})={res[k][0]}" for k in res) + f"  exit={code}")
    if a.out:
        json.dump({k: {"status": v[0], "detail": v[1]} for k, v in res.items()} | {"exit": code, "expect": a.expect},
                  open(a.out, "w", encoding="utf-8"), indent=2)
    sys.exit(code)


if __name__ == "__main__":
    main()
