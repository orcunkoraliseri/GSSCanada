"""Re-issue of the arm-E scorecard against ARM H (the FINDING-6/7/8/9-corrected build).

Built from `3rdJ_09E_score_armE.py`. The scoring machinery is deliberately identical; what changes
is stated here and nowhere else, so a diff of the two files IS the list of changes.

  1. P2's predicted values are RE-DERIVED forward from the corrected office 2030 product. The
     tolerance (+/- 3.0 pp) is NOT renegotiated.
  2. P5 is scored on the 20 cells that FINDINGS 6 and 7 do not touch, and the confounded full-56
     number is reported beside it.
  3. Arm E's own verdicts are printed alongside, marked as NOT superseded.

Every constant below was written into
`improvements/3rdJ_L3_improvements_step9.md` BEFORE this script was run against arm H. Do not edit a
threshold after reading a result -- record the miss.

Usage:
    python 3rdJ_09H_score_armH.py --arm-c <dir> --arm-h <dir> [--dhw-hourly-c f --dhw-hourly-h f]

Exit 0 only if every prediction PASSES. UNTESTABLE counts as a failure of the run.
"""
from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

# ------------------------------------------------------------------------------------------------
# P2, RE-DERIVED. Model, validated backward against its own past before being used forward:
#
#     dV/V = (5*V_wd*r_wd + 2*V_we*r_we) / (5*V_wd + 2*V_we) - 1     V_wd = 11.95, V_we = 3.71
#
# With the PRE-FINDING-6 r values it reproduces the three recorded arm-E predictions to <= 0.02 pp
# (+0.31 / -11.22 / -21.82 vs the recorded +0.3 / -11.2 / -21.8). That agreement is the licence to
# use it forward. `r` is fixed by the Step-7 product and the reference table, both of which exist
# before any simulation, so this is a prediction and not a fit.
# ------------------------------------------------------------------------------------------------
V_WD, V_WE = 11.95, 3.71
R_OFFICE_CORRECTED = {          # from arm H's provenance; an INPUT, not an outcome
    "B_cons":    (0.868615, 2.603310),
    "B_central": (0.800255, 2.116786),
    "B_opt":     (0.695172, 1.603564),
}
R_OFFICE_ARM_E = {              # the pre-FINDING-6 values, kept only for the backward validation
    "B_cons":    (0.818140, 2.492355),
    "B_central": (0.739882, 2.079011),
    "B_opt":     (0.663995, 1.730205),
}
ARM_E_RECORDED = {"B_cons": +0.3, "B_central": -11.2, "B_opt": -21.8}
P2_TOL = 3.0


def volume_model(r_wd, r_we):
    return 100.0 * ((5 * V_WD * r_wd + 2 * V_WE * r_we) / (5 * V_WD + 2 * V_WE) - 1.0)


P2_OFFICE_DHW = {s: (round(volume_model(*r), 1), P2_TOL) for s, r in R_OFFICE_CORRECTED.items()}

P3_HOTEL_DHW = ("B_central", +12.4, 2.0)          # unchanged -- F6/F7 do not touch hotel
P4_RESID_DHW = ("B_central", +8.0, +18.0)         # unchanged -- F6/F7 do not touch residential
P5_NONDHW_BOUND = 0.5
P5_MATERIALITY = 1.0

# The five scenarios with NO 2030 product, hence untouched by FINDINGS 6 and 7. Declared in the
# Progress Log before this ran, and chosen because it isolates the variable P5 is about.
P5_CLEAN_SCENARIOS = ["Default_NECB", "Y2005", "Y2010", "Y2015", "Y2022"]

ARM_E_SCORECARD = {"P1": "PASS", "P2": "FAIL", "P3": "FAIL",
                   "P4": "FAIL", "P5": "PASS", "P6": "PASS"}

_RESULTS = []


def record(pid, name, ok, detail):
    _RESULTS.append((pid, name, ok, detail))
    tag = {True: "PASS", False: "FAIL", None: "UNTESTABLE"}[ok]
    print("\n[%s] %s -- %s\n     %s" % (pid, tag, name, detail))


def load(d):
    p = os.path.join(d, "agg_annual.csv")
    if not os.path.isfile(p):
        raise SystemExit("missing %s" % p)
    df = pd.read_csv(p)
    df["energy_GJ"] = df["energy_J"] / 1e9
    return df


def pct(new, old):
    return float("nan") if abs(old) < 1e-12 else 100.0 * (new - old) / old


def dhw_by(df, scenario, channel):
    m = (df.scenario == scenario) & (df.channel == channel) & (df.end_use == "dhw")
    return float(df.loc[m, "energy_GJ"].sum())


def p5_block(C, H, scenarios, label):
    """Return (n_over, n_tested, n_skipped, lines) for the P5 bound over a scenario subset."""
    c = C[C.scenario.isin(scenarios)] if scenarios else C
    h = H[H.scenario.isin(scenarios)] if scenarios else H
    kc = c[c.end_use != "dhw"].groupby(["scenario", "channel", "end_use"])["energy_GJ"].sum()
    kh = h[h.end_use != "dhw"].groupby(["scenario", "channel", "end_use"])["energy_GJ"].sum()
    j = pd.concat([kc.rename("c"), kh.rename("h")], axis=1).fillna(0.0)
    tot = c.groupby(["scenario", "channel"])["energy_GJ"].sum()
    j["chan_tot"] = [tot.get((s, ch), float("nan")) for s, ch, _u in j.index]
    j["share"] = 100.0 * j.c / j.chan_tot
    j["pct"] = [pct(r.h, r.c) for r in j.itertuples()]
    tested = j[j.share >= P5_MATERIALITY]
    worst = tested.reindex(tested.pct.abs().sort_values(ascending=False).index).head(6)
    lines = ["%s / %s / %s: %.2f -> %.2f GJ = %+.3f %% (share %.1f %%)"
             % (i[0], i[1], i[2], r.c, r.h, r.pct, r.share) for i, r in worst.iterrows()]
    n_over = int((tested.pct.abs() >= P5_NONDHW_BOUND).sum())
    print("\n  -- P5 %s: %d of %d material end uses exceed %.1f %% (%d skipped as < %.1f %% of "
          "channel total)" % (label, n_over, len(tested), P5_NONDHW_BOUND,
                              len(j) - len(tested), P5_MATERIALITY))
    for ln in lines:
        print("       %s" % ln)
    return n_over, len(tested), len(j) - len(tested), lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm-c", required=True)
    ap.add_argument("--arm-h", required=True)
    ap.add_argument("--dhw-hourly-c", default=None)
    ap.add_argument("--dhw-hourly-h", default=None)
    a = ap.parse_args()

    C, H = load(a.arm_c), load(a.arm_h)
    print("arm C: %s  rows=%d" % (a.arm_c, len(C)))
    print("arm H: %s  rows=%d" % (a.arm_h, len(H)))

    print("\n" + "=" * 86)
    print("P2 PREDICTION PROVENANCE -- the model is validated BACKWARD before it is used FORWARD")
    print("=" * 86)
    print("  %-11s %-22s %10s %12s" % ("band", "arm-E r_wd / r_we", "model", "recorded"))
    back_ok = True
    for s, r in R_OFFICE_ARM_E.items():
        m = volume_model(*r)
        d = abs(m - ARM_E_RECORDED[s])
        back_ok &= d <= 0.1
        print("  %-11s %-22s %+9.2f %% %+11.1f %%   dev %.2f pp" % (s, "%.6f / %.6f" % r, m,
                                                                    ARM_E_RECORDED[s], d))
    print("  backward validation: %s" % ("PASS -- model reproduces all three to <= 0.1 pp"
                                         if back_ok else "FAIL -- do NOT trust the forward use"))
    if not back_ok:
        print("\n*** the prediction model does not reproduce its own recorded past. Stopping. ***")
        sys.exit(1)
    print("")
    print("  %-11s %-22s %14s" % ("band", "corrected r_wd / r_we", "RE-DERIVED"))
    for s, r in R_OFFICE_CORRECTED.items():
        print("  %-11s %-22s %+13.1f %%" % (s, "%.6f / %.6f" % r, P2_OFFICE_DHW[s][0]))

    # ---------------------------------------------------------------------------------------
    # P6 FIRST. No delta is quoted until the two arms are shown comparable.
    # ---------------------------------------------------------------------------------------
    tags_c, tags_h = set(C.cell_tag.unique()), set(H.cell_tag.unique())
    same_tags = tags_c == tags_h and len(tags_c) == 56
    detail = "%d vs %d cell tags; identical=%s" % (len(tags_c), len(tags_h), tags_c == tags_h)
    if tags_c ^ tags_h:
        detail += "; symmetric difference=%s" % sorted(tags_c ^ tags_h)[:6]

    area_ok, area_detail = None, "areas not comparable"
    ac = os.path.join(a.arm_c, "agg_annual_by_channel.csv")
    ah = os.path.join(a.arm_h, "agg_annual_by_channel.csv")
    if os.path.isfile(ac) and os.path.isfile(ah):
        dc = pd.read_csv(ac).set_index(["cell_tag", "channel"])["total_building_area_m2"]
        dh = pd.read_csv(ah).set_index(["cell_tag", "channel"])["total_building_area_m2"]
        j = pd.concat([dc.rename("c"), dh.rename("h")], axis=1).dropna()
        maxdiff = float((j.h - j.c).abs().max()) if len(j) else float("nan")
        area_ok = maxdiff == 0.0
        area_detail = "max |area_H - area_C| = %s m2 over %d (cell,channel) pairs" % (maxdiff, len(j))

    record("P6", "integrity: same 56 cells, identical areas",
           bool(same_tags) and bool(area_ok), "%s. %s" % (detail, area_detail))
    if not same_tags:
        print("\n*** P6 failed on cell tags -- refusing to quote any H-C delta. Stopping. ***")
        sys.exit(1)

    # ---------------------------------------------------------------------------------------
    # P2 -- office DHW, re-derived prediction
    # ---------------------------------------------------------------------------------------
    rows, ok2 = [], True
    for scen, (exp, tol) in P2_OFFICE_DHW.items():
        c, h = dhw_by(C, scen, "office"), dhw_by(H, scen, "office")
        got = pct(h, c)
        hit = abs(got - exp) <= tol
        ok2 &= hit
        rows.append("%s: %.2f -> %.2f GJ = %+.2f %% (re-derived %+.1f +/- %.1f pp) %s "
                    "[arm E predicted %+.1f]"
                    % (scen, c, h, got, exp, tol, "ok" if hit else "MISS", ARM_E_RECORDED[scen]))
    oc = [dhw_by(C, s, "office") for s in P2_OFFICE_DHW]
    oh = [dhw_by(H, s, "office") for s in P2_OFFICE_DHW]
    spread_c = (max(oc) - min(oc)) / max(1e-12, sum(oc) / len(oc)) * 100
    spread_h = (max(oh) - min(oh)) / max(1e-12, sum(oh) / len(oh)) * 100
    rows.append("office DHW spread across the 3 bundles: arm C %.3f %% -> arm H %.3f %%"
                % (spread_c, spread_h))
    ordering = oh[0] > oh[1] > oh[2]
    rows.append("ordering cons > central > opt in arm H: %s" % ordering)
    record("P2", "office DHW moves, re-derived sign and magnitude",
           bool(ok2) and bool(ordering) and spread_h > 1.0, "\n     ".join(rows))

    # ---------------------------------------------------------------------------------------
    # P3 -- hotel. Prediction unchanged; the sharp question is whether F8+F9 explain arm E's miss.
    # ---------------------------------------------------------------------------------------
    scen, exp, tol = P3_HOTEL_DHW
    c, h = dhw_by(C, scen, "hotel"), dhw_by(H, scen, "hotel")
    got = pct(h, c)
    record("P3", "hotel DHW rises -- laundry is scaling now",
           abs(got - exp) <= tol,
           "%s: %.2f -> %.2f GJ = %+.2f %% (predicted %+.1f +/- %.1f pp, UNCHANGED from arm E). "
           "Arm E measured +15.31 %% with FINDINGS 8 and 9 both live; both are fixed in arm H, so a "
           "move toward +12.4 is the evidence those two fixes explain the arm-E miss."
           % (scen, c, h, got, exp, tol))

    # ---------------------------------------------------------------------------------------
    # P4 -- residential. Attribution caveat stated in the log BEFORE this ran.
    # ---------------------------------------------------------------------------------------
    scen, lo, hi = P4_RESID_DHW
    c, h = dhw_by(C, scen, "residential"), dhw_by(H, scen, "residential")
    got = pct(h, c)
    record("P4", "residential DHW moves modestly, no T9-11 blow-up",
           lo <= got <= hi,
           "%s: %.2f -> %.2f GJ = %+.2f %% (predicted +%.0f..+%.0f %%, UNCHANGED). Arm E gave "
           "+51.40 %%. NOTE, stated in advance: the aggregator attributes the un-prefixed hotel "
           "`Laundry Service Water Use 30.6gpm 180F` to the RESIDENTIAL channel, and no finding "
           "changed that -- so this channel total still carries a hotel-r-scaled laundry the band "
           "never accounted for. Do NOT widen the band for it." % (scen, c, h, got, lo, hi))

    # ---------------------------------------------------------------------------------------
    # P5 -- scored on the F6/F7-free cells, full 56 reported beside it as confounded
    # ---------------------------------------------------------------------------------------
    n_over_all, n_all, _sk_all, _l_all = p5_block(C, H, None, "ALL 56 CELLS (CONFOUNDED by F6/F7)")
    n_over, n_tested, n_skip, lines = p5_block(C, H, P5_CLEAN_SCENARIOS,
                                               "20 F6/F7-FREE CELLS (the scored version)")
    record("P5", "non-DHW end uses bounded at %.1f %% (20 F6/F7-free cells)" % P5_NONDHW_BOUND,
           n_over == 0,
           "%d of %d material end uses exceed the bound on the 20 clean cells (%d skipped as "
           "< %.1f %% of channel total). Confounded full-56 figure, reported not scored: %d of %d "
           "over the bound -- F6/F7 change office and retail OCCUPANCY in the 36 2030-family cells, "
           "so lighting and equipment move there for reasons that are not T9-13. Largest movers "
           "among the clean cells:\n     %s"
           % (n_over, n_tested, n_skip, P5_MATERIALITY, n_over_all, n_all, "\n     ".join(lines)))

    # ---------------------------------------------------------------------------------------
    # P1 -- the identity T9-11 violated
    # ---------------------------------------------------------------------------------------
    if a.dhw_hourly_c and a.dhw_hourly_h and os.path.isfile(a.dhw_hourly_c) \
            and os.path.isfile(a.dhw_hourly_h):
        def shape(path):
            d = pd.read_csv(path)
            col = next((x for x in d.columns if "resid" in x.lower()), d.columns[-1])
            v = d[col].to_numpy(dtype=float)
            hh = v.reshape(-1, 24).mean(axis=0)
            return float(hh[0:6].sum() / hh.sum()), int(hh.argmax())
        nc, pc_ = shape(a.dhw_hourly_c)
        nh, ph_ = shape(a.dhw_hourly_h)
        record("P1", "night share and peak draw hour unchanged (the identity T9-11 broke)",
               abs(nh - nc) < 0.005 and pc_ == ph_,
               "residential night 00-05 share %.4f -> %.4f; peak hour %d -> %d. "
               "Arm D (T9-11): 0.0834 -> 0.3286 and 06:00 -> 04:00." % (nc, nh, pc_, ph_))
    else:
        record("P1", "night share and peak draw hour unchanged", None,
               "no dhw_hourly.csv pair supplied")

    # ---------------------------------------------------------------------------------------
    print("\n" + "=" * 86)
    npass = sum(1 for _, _, ok, _ in _RESULTS if ok is True)
    nfail = sum(1 for _, _, ok, _ in _RESULTS if ok is False)
    nunt = sum(1 for _, _, ok, _ in _RESULTS if ok is None)
    print("ARM H SCORECARD: %d PASS / %d FAIL / %d UNTESTABLE  of %d"
          % (npass, nfail, nunt, len(_RESULTS)))
    print("  %-4s %-8s %-8s %s" % ("", "arm E", "arm H", "prediction"))
    order = {"P1": 0, "P2": 1, "P3": 2, "P4": 3, "P5": 4, "P6": 5}
    for pid, name, ok, _ in sorted(_RESULTS, key=lambda r: order.get(r[0], 9)):
        v = {True: "PASS", False: "FAIL", None: "UNTEST"}[ok]
        flip = "" if ARM_E_SCORECARD.get(pid) == v else "   <-- CHANGED"
        print("  %-4s %-8s %-8s %s%s" % (pid, ARM_E_SCORECARD.get(pid, "?"), v, name, flip))
    print("\nARM E'S SCORECARD (3 PASS / 3 FAIL / 0 UNTESTABLE) IS *NOT* SUPERSEDED BY THIS TABLE.")
    print("Those verdicts were scored against predictions written before arm E ran. A later run")
    print("produces new numbers; it does not repair an old verdict. A MISS IS RECORDED, NOT REPAIRED.")
    sys.exit(0 if nfail == 0 and nunt == 0 else 1)


if __name__ == "__main__":
    main()
