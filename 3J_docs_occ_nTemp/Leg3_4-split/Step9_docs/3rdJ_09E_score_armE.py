"""Score arm E (T9-13 DHW volume scaling) against the six predictions recorded in
`improvements/3rdJ_L3_improvements_step9.md` BEFORE the array was submitted.

Written 2026-08-02 while job 1171323 was still running, i.e. before any arm E result existed. That
ordering is the point: the thresholds below cannot have been chosen to fit the data, because the
data did not exist when they were written. Do not edit a threshold in this file after reading a
result — record the miss instead.

Usage:
    py -3 3rdJ_09E_score_armE.py --arm-c <dir with agg_annual.csv> --arm-e <dir> [--dhw-hourly-c f --dhw-hourly-e f]

Exit code 0 if every prediction PASSES, 1 otherwise. A prediction that cannot be evaluated (missing
input) is reported UNTESTABLE and counts as a failure of the run, not as a pass.
"""
from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

# ---------------------------------------------------------------------------
# The predictions, as recorded before submission. Values are % change of arm E vs arm C.
# ---------------------------------------------------------------------------
P2_OFFICE_DHW = {"B_cons": (+0.3, 3.0), "B_central": (-11.2, 3.0), "B_opt": (-21.8, 3.0)}
P3_HOTEL_DHW = ("B_central", +12.4, 2.0)          # scenario, expected %, tolerance pp
P4_RESID_DHW = ("B_central", +8.0, +18.0)         # scenario, low %, high %
P5_NONDHW_BOUND = 0.5                              # % -- thermal coupling only
# P5 is only meaningful where the end use is large enough that a % is not noise. Rule fixed in
# advance: an end use is TESTED if it is >= 1 % of its channel's total energy in arm C; smaller
# ones are REPORTED but not scored, and the report says how many were skipped.
P5_MATERIALITY = 1.0                               # % of channel total

_RESULTS = []


def record(pid, name, ok, detail):
    _RESULTS.append((pid, name, ok, detail))
    tag = {True: "PASS", False: "FAIL", None: "UNTESTABLE"}[ok]
    print(f"\n[{pid}] {tag} -- {name}\n     {detail}")


def load(d):
    p = os.path.join(d, "agg_annual.csv")
    if not os.path.isfile(p):
        raise SystemExit(f"missing {p}")
    df = pd.read_csv(p)
    df["energy_GJ"] = df["energy_J"] / 1e9
    return df


def pct(new, old):
    return float("nan") if abs(old) < 1e-12 else 100.0 * (new - old) / old


def dhw_by(df, scenario, channel):
    m = (df.scenario == scenario) & (df.channel == channel) & (df.end_use == "dhw")
    return float(df.loc[m, "energy_GJ"].sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm-c", required=True)
    ap.add_argument("--arm-e", required=True)
    ap.add_argument("--dhw-hourly-c", default=None)
    ap.add_argument("--dhw-hourly-e", default=None)
    a = ap.parse_args()

    C, E = load(a.arm_c), load(a.arm_e)
    print(f"arm C: {a.arm_c}  rows={len(C)}")
    print(f"arm E: {a.arm_e}  rows={len(E)}")

    # -----------------------------------------------------------------------
    # P6 FIRST. No delta is quoted until the two arms are shown comparable.
    # -----------------------------------------------------------------------
    tags_c, tags_e = set(C.cell_tag.unique()), set(E.cell_tag.unique())
    same_tags = tags_c == tags_e and len(tags_c) == 56
    detail = f"{len(tags_c)} vs {len(tags_e)} cell tags; identical={tags_c == tags_e}"
    if tags_c ^ tags_e:
        detail += f"; symmetric difference={sorted(tags_c ^ tags_e)[:6]}"

    area_ok, area_detail = None, "areas not comparable"
    ac = os.path.join(a.arm_c, "agg_annual_by_channel.csv")
    ae = os.path.join(a.arm_e, "agg_annual_by_channel.csv")
    if os.path.isfile(ac) and os.path.isfile(ae):
        dc = pd.read_csv(ac).set_index(["cell_tag", "channel"])["total_building_area_m2"]
        de = pd.read_csv(ae).set_index(["cell_tag", "channel"])["total_building_area_m2"]
        j = pd.concat([dc.rename("c"), de.rename("e")], axis=1).dropna()
        maxdiff = float((j.e - j.c).abs().max()) if len(j) else float("nan")
        area_ok = maxdiff == 0.0
        area_detail = f"max |area_E - area_C| = {maxdiff} m2 over {len(j)} (cell,channel) pairs"

    record("P6", "integrity: same 56 cells, identical areas",
           bool(same_tags) and bool(area_ok), f"{detail}. {area_detail}")

    if not same_tags:
        print("\n*** P6 failed on cell tags -- refusing to quote any E-C delta. Stopping. ***")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # P2 -- office DHW stops being flat; sign AND magnitude fixed in advance
    # -----------------------------------------------------------------------
    rows, ok2 = [], True
    for scen, (exp, tol) in P2_OFFICE_DHW.items():
        c, e = dhw_by(C, scen, "office"), dhw_by(E, scen, "office")
        got = pct(e, c)
        hit = abs(got - exp) <= tol
        ok2 &= hit
        rows.append(f"{scen}: {c:.2f} -> {e:.2f} GJ = {got:+.2f} % "
                    f"(predicted {exp:+.1f} +/- {tol} pp) {'ok' if hit else 'MISS'}")
    # the flatness half: arm C office DHW must be flat across scenarios, arm E must not be
    oc = [dhw_by(C, s, "office") for s in P2_OFFICE_DHW]
    oe = [dhw_by(E, s, "office") for s in P2_OFFICE_DHW]
    spread_c = (max(oc) - min(oc)) / max(1e-12, sum(oc) / len(oc)) * 100
    spread_e = (max(oe) - min(oe)) / max(1e-12, sum(oe) / len(oe)) * 100
    rows.append(f"office DHW spread across the 3 bundles: arm C {spread_c:.3f} % -> arm E {spread_e:.3f} %")
    ordering = oe[0] > oe[1] > oe[2]      # cons > central > opt
    rows.append(f"ordering cons > central > opt in arm E: {ordering}")
    record("P2", "office DHW moves, with the predicted sign and magnitude",
           bool(ok2) and bool(ordering) and spread_e > 1.0, "\n     ".join(rows))

    # -----------------------------------------------------------------------
    # P3 -- hotel DHW now moves (laundry no longer excluded); reversal of arm D's P5
    # -----------------------------------------------------------------------
    scen, exp, tol = P3_HOTEL_DHW
    c, e = dhw_by(C, scen, "hotel"), dhw_by(E, scen, "hotel")
    got = pct(e, c)
    record("P3", "hotel DHW rises -- laundry is scaling now",
           abs(got - exp) <= tol,
           f"{scen}: {c:.2f} -> {e:.2f} GJ = {got:+.2f} % (predicted {exp:+.1f} +/- {tol} pp). "
           f"Arm D reported -8.7 % with laundry frozen. A move < +5 % means laundry still is not scaling.")

    # -----------------------------------------------------------------------
    # P4 -- residential moves with occupancy and does NOT repeat T9-11's +40.8 %
    # -----------------------------------------------------------------------
    scen, lo, hi = P4_RESID_DHW
    c, e = dhw_by(C, scen, "residential"), dhw_by(E, scen, "residential")
    got = pct(e, c)
    record("P4", "residential DHW moves modestly, no T9-11 blow-up",
           lo <= got <= hi,
           f"{scen}: {c:.2f} -> {e:.2f} GJ = {got:+.2f} % (predicted +{lo:.0f}..+{hi:.0f} %). "
           f"T9-11 gave +40.8 %; anything > +25 % is that signature returning.")

    # -----------------------------------------------------------------------
    # P5 -- non-DHW end uses move only through thermal coupling, bound stated first
    # -----------------------------------------------------------------------
    kc = C[C.end_use != "dhw"].groupby(["scenario", "channel", "end_use"])["energy_GJ"].sum()
    ke = E[E.end_use != "dhw"].groupby(["scenario", "channel", "end_use"])["energy_GJ"].sum()
    j = pd.concat([kc.rename("c"), ke.rename("e")], axis=1).fillna(0.0)
    tot = C.groupby(["scenario", "channel"])["energy_GJ"].sum()
    j["chan_tot"] = [tot.get((s, ch), float("nan")) for s, ch, _u in j.index]
    j["share"] = 100.0 * j.c / j.chan_tot
    j["pct"] = [pct(r.e, r.c) for r in j.itertuples()]
    tested = j[j.share >= P5_MATERIALITY]
    skipped = len(j) - len(tested)
    worst = tested.reindex(tested.pct.abs().sort_values(ascending=False).index).head(6)
    lines = [f"{i[0]} / {i[1]} / {i[2]}: {r.c:.2f} -> {r.e:.2f} GJ = {r.pct:+.3f} % "
             f"(share {r.share:.1f} %)" for i, r in worst.iterrows()]
    n_over = int((tested.pct.abs() >= P5_NONDHW_BOUND).sum())
    record("P5", f"non-DHW end uses bounded at {P5_NONDHW_BOUND} %",
           n_over == 0,
           f"{n_over} of {len(tested)} material end uses exceed the bound "
           f"({skipped} skipped as < {P5_MATERIALITY} % of channel total). Largest movers:\n     "
           + "\n     ".join(lines))

    # -----------------------------------------------------------------------
    # P1 -- the identity T9-11 violated. Needs the hourly file; agg_armE.sh does the 56-cell
    # provenance sweep separately.
    # -----------------------------------------------------------------------
    if a.dhw_hourly_c and a.dhw_hourly_e and os.path.isfile(a.dhw_hourly_c) \
            and os.path.isfile(a.dhw_hourly_e):
        def shape(path):
            d = pd.read_csv(path)
            col = next((x for x in d.columns if "resid" in x.lower()), d.columns[-1])
            v = d[col].to_numpy(dtype=float)
            h = v.reshape(-1, 24).mean(axis=0)
            return float(h[0:6].sum() / h.sum()), int(h.argmax())
        nc, pc_ = shape(a.dhw_hourly_c)
        ne, pe_ = shape(a.dhw_hourly_e)
        record("P1", "night share and peak draw hour unchanged (the identity T9-11 broke)",
               abs(ne - nc) < 0.005 and pc_ == pe_,
               f"residential night 00-05 share {nc:.4f} -> {ne:.4f}; peak hour {pc_} -> {pe_}. "
               f"Arm D: 0.0834 -> 0.3286 and 06:00 -> 04:00.")
    else:
        record("P1", "night share and peak draw hour unchanged", None,
               "no dhw_hourly.csv pair supplied -- run agg_armE.sh for the 56-cell provenance "
               "sweep, and pass --dhw-hourly-c/--dhw-hourly-e for the hourly half.")

    # -----------------------------------------------------------------------
    print("\n" + "=" * 78)
    npass = sum(1 for _, _, ok, _ in _RESULTS if ok is True)
    nfail = sum(1 for _, _, ok, _ in _RESULTS if ok is False)
    nunt = sum(1 for _, _, ok, _ in _RESULTS if ok is None)
    print(f"SCORECARD: {npass} PASS / {nfail} FAIL / {nunt} UNTESTABLE  of {len(_RESULTS)}")
    for pid, name, ok, _ in _RESULTS:
        print(f"  {pid}: {{True:'PASS',False:'FAIL',None:'UNTESTABLE'}}"
              .replace("{True:'PASS',False:'FAIL',None:'UNTESTABLE'}",
                       {True: "PASS", False: "FAIL", None: "UNTESTABLE"}[ok]) + f"  {name}")
    print("\nA MISS IS RECORDED, NOT REPAIRED. Do not widen a tolerance in this file after the fact.")
    sys.exit(0 if nfail == 0 and nunt == 0 else 1)


if __name__ == "__main__":
    main()
