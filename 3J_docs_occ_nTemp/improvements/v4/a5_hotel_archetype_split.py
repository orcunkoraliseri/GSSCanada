# -*- coding: utf-8 -*-
"""V4-A5 -- what actually separates the two hotel clusters, and what the
uninjected control is failing on.

Desk work. Reads ONLY the frozen deliverable's Step-8 end-use table:
    Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/
No simulation, nothing written outside improvements/v4/.

The question A4 left open: `S9-EUI-hotel` FAILs on `Tall` (28/28 over the 300
ceiling) and PASSes on `SuperTall`, with an empty gap of 84.64 kWh/m2 between the
two clusters -- and the UNINJECTED control (`Default_NECB`, stock schedules, no
occupancy model at all) is ALREADY over the ceiling. So the gate is not failing on
occupancy. This decomposes both buildings by end use to name what it IS failing on.

Two claims are tested, both falsifiable here:
  C1  the separation is carried by one end use, not spread across the load
  C2  that end use does not respond to occupancy -- if it moves across the 14
      scenarios by more than the gap, C1 is not an archetype story at all
"""
import io, json, os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
AGG = os.path.join(ROOT, "Leg3_4-split", "Step8_docs", "outputs_step8", "agg_deliverable")

CEILING = 300.0
DIRECT = ["interior_lighting", "interior_equipment", "dhw"]   # occupancy-scheduled


def main():
    d = pd.read_csv(os.path.join(AGG, "agg_annual.csv"), low_memory=False)
    c = pd.read_csv(os.path.join(AGG, "agg_annual_by_channel.csv"), low_memory=False)

    hc = c[c.channel == "hotel"].drop_duplicates("cell_tag")
    area = dict(zip(hc.cell_tag, hc.area_m2))
    published = dict(zip(hc.cell_tag, hc.eui_CFA_kWh_m2))

    h = d[d.channel == "hotel"].copy()
    h["kwh"] = h.energy_J / 3.6e6
    h["area_m2"] = h.cell_tag.map(area)
    h["eui"] = h.kwh / h.area_m2

    p = h.pivot_table(index=["building", "city", "scenario"], columns="end_use",
                      values="eui", aggfunc="sum").fillna(0.0)
    p["TOTAL"] = p.sum(axis=1)

    # the decomposition must reconstruct the SCORED number, or it is not the same quantity
    recon = max(abs(p.loc[(b, ct, s), "TOTAL"] - published["%s__%s__%s" % (s, b, ct)])
                for (b, ct, s) in p.index)
    print("reconstruction vs the scored eui_CFA_kWh_m2: max |delta| = %.2e" % recon)
    assert recon < 1e-6, "the decomposition is not the scored quantity -- stop here"

    tall, sup = p.loc["Tall"], p.loc["SuperTall"]
    gap = tall.TOTAL.min() - sup.TOTAL.max()
    print("\nSuperTall  %.2f - %.2f   (n=%d)" % (sup.TOTAL.min(), sup.TOTAL.max(), len(sup)))
    print("Tall       %.2f - %.2f   (n=%d)" % (tall.TOTAL.min(), tall.TOTAL.max(), len(tall)))
    print("empty gap between the clusters: %.2f kWh/m2   (ceiling %.0f is inside it: %s)"
          % (gap, CEILING, sup.TOTAL.max() < CEILING < tall.TOTAL.min()))

    # ---- C1: which end use carries the separation --------------------------
    print("\n-- C1: per-end-use separation (Tall mean minus SuperTall mean) --")
    uses = [u for u in p.columns if u != "TOTAL"]
    sep = pd.DataFrame({"SuperTall": sup[uses].mean(), "Tall": tall[uses].mean()})
    sep["separation"] = sep.Tall - sep.SuperTall
    sep["pct_of_gap"] = 100 * sep.separation / gap
    print(sep.sort_values("separation", ascending=False).round(2).to_string())

    # ---- C2: how much does each end use answer to occupancy? ---------------
    print("\n-- C2: movement across the 14 scenarios, per city (max - min) --")
    swing = p.groupby(level=[0, 1]).apply(lambda g: g[uses].max() - g[uses].min())
    print(swing.round(2).to_string())

    # ---- the uninjected control --------------------------------------------
    print("\n-- the uninjected control (Default_NECB: stock schedules, no occupancy model) --")
    ctl = p.xs("Default_NECB", level="scenario")[["TOTAL"] + DIRECT]
    ctl["over_ceiling"] = ctl.TOTAL > CEILING
    print(ctl.round(2).to_string())

    # ---- does the load scale with the hotel floor area? --------------------
    print("\n-- does the separating load scale with hotel floor area? --")
    top = sep.separation.idxmax()
    abs_kwh = h[h.end_use == top].groupby("building").kwh.mean()
    areas = h.groupby("building").area_m2.first()
    print("end use: %s" % top)
    print("hotel floor area   SuperTall %10.1f   Tall %10.1f   ratio %.3f"
          % (areas["SuperTall"], areas["Tall"], areas["SuperTall"] / areas["Tall"]))
    print("absolute %-9s SuperTall %10.0f   Tall %10.0f   ratio %.3f"
          % (top + " kWh", abs_kwh["SuperTall"], abs_kwh["Tall"],
             abs_kwh["SuperTall"] / abs_kwh["Tall"]))
    print("=> halving the hotel floor area removes only %.1f %% of this load."
          % (100 * (1 - abs_kwh["Tall"] / abs_kwh["SuperTall"])))

    out = {
        "task": "V4-A5", "date": "2026-08-06",
        "source": "Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable (frozen deliverable)",
        "ceiling": CEILING,
        "supertall_range": [round(sup.TOTAL.min(), 2), round(sup.TOTAL.max(), 2)],
        "tall_range": [round(tall.TOTAL.min(), 2), round(tall.TOTAL.max(), 2)],
        "empty_gap": round(gap, 2),
        "separating_end_use": top,
        "separation_kwh_m2": round(sep.separation.max(), 2),
        "separation_pct_of_gap": round(100 * sep.separation.max() / gap, 1),
        "occupancy_swing_max_kwh_m2": round(float(swing.max().max()), 2),
        "control_over_ceiling": {"%s__%s" % k: bool(v) for k, v in ctl.over_ceiling.items()},
        "area_ratio": round(float(areas["SuperTall"] / areas["Tall"]), 3),
        "separating_load_abs_ratio": round(float(abs_kwh["SuperTall"] / abs_kwh["Tall"]), 3),
    }
    with io.open(os.path.join(HERE, "v4_a5_hotel_split.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
