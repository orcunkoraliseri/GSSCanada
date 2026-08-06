#!/usr/bin/env python
"""V2-D9 scorer -- does loading NECB `Retail - sales` move `S9-EUI-retail`?

Scores the four pre-registered predictions of the D9 block in
`improvements/v2/3rdJ_L3_v2_implementation.md` by differencing the NECB-C cells against their
EXACT matched controls: the same arm-H source IDFs, the same
`3rdJ_09H_resize_campaign_cell.py`, the same K = 1.0, differing ONLY in the retail People
density and the retail occupancy schedule.

    P1  SIGN       retail EUI FALLS.                          FAIL if it rises.
    P2  MAGNITUDE  |delta retail EUI| <= 1.5 kWh/m2.          FAIL if larger.
    P3  GATE       `S9-EUI-retail` stays FAIL, fails by MORE. FAIL if it passes, or if the
                   median moves up at all.
    P4  CONTROL    office / hotel / residential move < 0.05 %. FAIL if any moves more.

READ THIS BEFORE COMPARING THE NUMBERS TO ANYTHING ELSE
-------------------------------------------------------
**Both arms are read from §8E `agg_annual.csv` + `agg_meta.csv`, which is what the gate scores
-- NOT from `channel_hourly.csv`.** The first cut of this file summed the per-channel hourly
columns instead, and the two definitions are not interchangeable. On `B_cons__Tall__MTL`:

    aggregator  1,033.49 GJ  ->  EUI  90.88 kWh/m2   (9 end uses, incl. dhw / fans / pumps /
                                                      heat_recovery / heat_rejection)
    hourly      1,307.25 GJ  ->  EUI 114.95 kWh/m2   (lights + equip + gasequip + syscool +
                                                      sysheat, a different HVAC split)

a **26.5 %** gap. A delta scored on the hourly basis would have been a real number answering a
question the gate does not ask, and P3 -- the only prediction about the gate -- would have been
measured against a quantity `S9-EUI-retail` never sees.

Areas come from each cell's own `agg_meta.csv` row, never from a constant typed here. The D9
pre-registration quoted the retail channel as **4,738.47 m2**; that is the **SuperTall** area,
and every D9 probe cell is **Tall**, where retail is **3,158.98 m2**. The GJ figures in that
block are unaffected -- only its per-m2 conversions were, and they are corrected in the closure
entry rather than silently restated.

`<channel>_people` in `channel_hourly.csv` is an OCCUPANT COUNT (`Zone People Occupant Count`,
mapped at `3rdJ_08P_probe_driver.py:239`), not joules. It is read here ONLY as the direct check
that the density edit landed, and never enters an energy total.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import pandas as pd

J_TO_KWH = 1.0 / 3.6e6
CHANNELS = ("retail", "office", "hotel", "residential")


def load_bench() -> dict:
    """Import the retail band FROM THE GATE THAT APPLIES IT -- never a copy typed here.

    A second copy of a band is a band that can drift out of sync with the gate, invisibly: this
    script would keep printing PASS/FAIL against numbers the scorecard no longer uses. The first
    cut of this file did exactly that -- an 80/140 band and an implicit all-cells rule, when the
    shipped band is 80/155 and V2-B3 changed the rule to MEDIAN-in-band.
    """
    src = Path(__file__).with_name("3rdJ_09_activityDrivenLoads_4split.py")
    if not src.exists():
        raise SystemExit(f"[FATAL] cannot find the gate module next to this script: {src}")
    spec = importlib.util.spec_from_file_location("_s9gate", src)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:                                    # noqa: BLE001
        raise SystemExit(f"[FATAL] could not import the gate module for its bands: {exc}")
    b = getattr(mod, "BENCH", {}).get("retail")
    if not b or b.get("lo") is None or b.get("hi") is None:
        raise SystemExit("[FATAL] BENCH['retail'] missing or has no band -- refusing to invent one.")
    return b


def read_agg(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    ann, meta = root / "agg_annual.csv", root / "agg_meta.csv"
    for f in (ann, meta):
        if not f.exists():
            raise SystemExit(f"[FATAL] {f} not found -- run 3rdJ_08E_aggregate_4split.py first.")
    return pd.read_csv(ann), pd.read_csv(meta)


def eui_table(root: Path) -> pd.DataFrame:
    """Per cell x channel CFA EUI, exactly as §R1 of the Step-9 scorer computes it."""
    ann, meta = read_agg(root)
    e = ann.groupby(["cell_tag", "channel"], as_index=False)["energy_J"].sum()
    m = meta.set_index("cell_tag")
    rows = []
    for _, r in e.iterrows():
        ch, cell = r["channel"], r["cell_tag"]
        if ch not in CHANNELS or cell not in m.index:
            continue
        area = float(m.loc[cell, f"area_{ch}_m2"])
        if area <= 0:
            continue
        rows.append(dict(cell=cell, channel=ch, area_m2=area,
                         E_GJ=float(r["energy_J"]) / 1e9,
                         eui=float(r["energy_J"]) * J_TO_KWH / area))
    return pd.DataFrame(rows)


def occupant_hours(cell_dir: Path) -> dict[str, float]:
    f = cell_dir / "channel_hourly.csv"
    if not f.exists():
        return {}
    df = pd.read_csv(f)
    return {ch: float(df[f"{ch}_people"].sum())
            for ch in CHANNELS if f"{ch}_people" in df.columns}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--treat-agg", required=True, help="§8E outdir for the NECB-C cells")
    ap.add_argument("--ctrl-agg", required=True, help="§8E outdir holding the matched K=1 controls")
    ap.add_argument("--treat-cells", default="", help="cell dirs, for the occupant-hour check")
    ap.add_argument("--ctrl-cells", default="", help="cell dirs, for the occupant-hour check")
    a = ap.parse_args()

    bench = load_bench()
    lo, hi = float(bench["lo"]), float(bench["hi"])
    rule = bench.get("rule", "median")
    print(f"retail band, imported from the gate module: [{lo:g}, {hi:g}] "
          f"central {bench['central']:g}, rule = {rule}")

    t, k = eui_table(Path(a.treat_agg)), eui_table(Path(a.ctrl_agg))
    df = t.merge(k, on=["cell", "channel"], suffixes=("_treat", "_ctrl"))
    if df.empty:
        raise SystemExit("[FATAL] no cell x channel pair matched between the two aggregations.")
    missing = sorted(set(t["cell"]) - set(df["cell"]))
    if missing:
        print(f"  [WARN] {len(missing)} treated cell(s) had no control row: {missing}")
    if not df["area_m2_treat"].sub(df["area_m2_ctrl"]).abs().lt(1e-6).all():
        raise SystemExit("[FATAL] channel areas differ between arms -- the edit changed geometry, "
                         "which it must not. Refusing to score.")

    df["d_eui"] = df["eui_treat"] - df["eui_ctrl"]
    df["dE_pct"] = 100.0 * (df["E_GJ_treat"] - df["E_GJ_ctrl"]) / df["E_GJ_ctrl"]

    # -- did the occupancy edit actually land? Direct, and independent of any energy number. ----
    if a.treat_cells and a.ctrl_cells:
        print("\n=== retail occupant-hours (the edit itself, not its consequence) ===")
        for c in sorted(df["cell"].unique()):
            ot = occupant_hours(Path(a.treat_cells) / c).get("retail")
            ok_ = occupant_hours(Path(a.ctrl_cells) / c).get("retail")
            if ot and ok_:
                print(f"  {c:<26} {ok_:>12,.0f} -> {ot:>12,.0f} person-h  "
                      f"({100.0 * (ot - ok_) / ok_:+.3f} %)")

    pd.set_option("display.width", 220, "display.max_columns", 40)
    print("\n=== per cell x channel (CFA basis, aggregator definition) ===")
    print(df[["cell", "channel", "area_m2_treat", "E_GJ_ctrl", "E_GJ_treat", "dE_pct",
              "eui_ctrl", "eui_treat", "d_eui"]].sort_values(["channel", "cell"]).to_string(
        index=False, float_format=lambda v: f"{v:,.4f}"))

    r = df[df["channel"] == "retail"]
    med_c, med_t = r["eui_ctrl"].median(), r["eui_treat"].median()
    d_med = med_t - med_c
    print(f"\nretail median EUI  {med_c:.4f} -> {med_t:.4f}   "
          f"delta {d_med:+.4f} kWh/m2 ({100.0 * d_med / med_c:+.3f} %)   n = {len(r)} cells")

    v = []
    n_down = int((r["d_eui"] < 0).sum())
    v.append(("P1 SIGN", n_down == len(r),
              f"retail EUI falls in {n_down}/{len(r)} cells; per-cell delta "
              f"{r['d_eui'].min():+.4f} .. {r['d_eui'].max():+.4f} kWh/m2"))

    worst = r["d_eui"].abs().max()
    v.append(("P2 MAGNITUDE", worst <= 1.5,
              f"largest |delta EUI| = {worst:.4f} kWh/m2 (bound 1.5)"))

    # -- P3, split into the half this probe CAN settle and the half it cannot -----------------
    # The campaign median is 75.4 against a floor of 80 (44/56 cells under). These four cells are
    # all Tall/MTL and all sit INSIDE the band in the control, so the probe's own median carries
    # no information about the campaign verdict: a "PASS" here would mean only that the four
    # sampled cells were never the failing ones. Scoring `gate_t == FAIL` on them would be a
    # vacuous gate of catalogue class #1 -- a check that cannot fail for the reason it claims.
    # What the probe DOES settle is the direction of the median and the size of the lever against
    # the 4.6 kWh/m2 the gate needs. That is scored; the verdict half is reported as N/A.
    CAMPAIGN_GAP = 4.6
    gate_c = "PASS" if lo <= med_c <= hi else "FAIL"
    gate_t = "PASS" if lo <= med_t <= hi else "FAIL"
    out_c = int(((r["eui_ctrl"] < lo) | (r["eui_ctrl"] > hi)).sum())
    out_t = int(((r["eui_treat"] < lo) | (r["eui_treat"] > hi)).sum())
    frac = 100.0 * abs(d_med) / CAMPAIGN_GAP
    # STRICTLY negative, not `<= 0`. The first cut used `<= 0`, and the null-edit falsifier
    # (control differenced against itself) PASSED it -- a prediction that "the median moves down"
    # must not be satisfied by the median not moving at all. That is catalogue class #1, and it
    # was caught only because the falsifier was actually run.
    v.append(("P3 DIRECTION", d_med < 0,
              f"median {med_c:.4f} -> {med_t:.4f} ({d_med:+.4f} kWh/m2); the lever is "
              f"{frac:.1f} % of the {CAMPAIGN_GAP:g} kWh/m2 the campaign gate needs, and points "
              f"{'DOWN, away from the floor' if d_med < 0 else ('NOWHERE -- the median did not move' if d_med == 0 else 'UP, toward the floor')}"))
    geos = sorted({c.split('__')[1] for c in r['cell'] if '__' in c})
    cities = sorted({c.split('__')[2] for c in r['cell'] if c.count('__') >= 2})
    print(f"\n  [N/A ] P3 VERDICT    not scorable here: {len(r)} cell(s), geometry "
          f"{'/'.join(geos) or 'n/a'}, city {'/'.join(cities) or 'n/a'}; "
          f"{len(r) - out_c} of {len(r)} sit INSIDE [{lo:g},{hi:g}] in the control "
          f"(median {med_c:.4f} -> {gate_c}). The campaign median is 75.4 with 44/56 under the "
          f"floor. Treated: median {med_t:.4f} -> {gate_t}, cells outside band "
          f"{out_c} -> {out_t}. The gate verdict is V2-E5's to score, on the full grid.")

    o = df[df["channel"] != "retail"]
    p4_worst = o["dE_pct"].abs().max()
    row = o.loc[o["dE_pct"].abs().idxmax()]
    v.append(("P4 CONTROL", p4_worst < 0.05,
              f"largest |dE| off-channel = {p4_worst:.4f} % on {row['channel']}/{row['cell']} "
              f"(bound 0.05 %)"))

    print("\n=== pre-registered predictions ===")
    for name, ok_, why in v:
        print(f"  [{'PASS' if ok_ else 'FAIL'}] {name:<13} {why}")
    npass = sum(1 for _, ok_, _ in v if ok_)
    print(f"\n  {npass}P / {len(v) - npass}F")
    print(f"\n  NOTE: scored on {len(r)} retail cell(s) ({'/'.join(geos) or 'n/a'}), not the "
          f"56-cell campaign.\n  This settles the DIRECTION and the SIZE of the lever; the "
          f"campaign median is scored by\n  the Step-9 scorer itself, and only after WP-E re-runs "
          f"the full grid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
