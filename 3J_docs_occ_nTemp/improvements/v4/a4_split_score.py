# -*- coding: utf-8 -*-
"""V4-A4 -- score S9-EUI-* per geometry, under the split authorised by V4-A1.

DESK WORK ONLY. Reads one CSV, writes one NEW artefact. It does not touch
step9_gates.json, it changes no band value, it runs no simulation and it does
not contact the cluster.

SOURCE OF TRUTH = outputs_step9_deliverable/, the FROZEN DELIVERABLE named in
improvements/v2/V2-G1_FROZEN_DELIVERABLE.md.  The sibling directory
outputs_step9/ is a 2026-07-31 run that PREDATES the v2 decisions and the
deliverable rebuild; it is read here only to document the divergence that the
pre-registered predictions were made on.

Each channel is scored under ITS OWN rule in force, taken from the deliverable
gate text, not under a uniform rule:
    office -> all_cells   (V2 wave)
    retail -> median      (V2-B3, 2026-08-05)
    hotel  -> all_cells   (V2-B2 record)
"""
import csv, io, json, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
S9 = os.path.join(ROOT, "Leg3_4-split", "Step9_docs")

DELIVERABLE = os.path.join(S9, "outputs_step9_deliverable", "step9_eui_by_channel.csv")
STALE = os.path.join(S9, "outputs_step9", "step9_eui_by_channel.csv")  # FROZEN-INPUT-OK: read ON PURPOSE, and never scored -- re-running the same scoring on the superseded file is what converted "my prediction failed" into "my input was wrong" (see V4-A4 §2)

RULE = {"office": "all_cells", "retail": "median", "hotel": "all_cells"}

# Written down BEFORE the V4-A1 decision was taken. Not edited after seeing the
# result -- the whole point of the pre-registration is that this line is fixed.
PREREGISTERED = {"Tall": "PASS", "SuperTall": "FAIL"}


def load(path):
    with io.open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def score(cells, lo, hi, rule):
    """Return (verdict, stats) for one group of cells under one rule."""
    v = sorted(float(c["eui_CFA_kWh_m2"] ) for c in cells)
    below = sum(1 for x in v if x < lo)
    above = sum(1 for x in v if x > hi)
    med = st.median(v)
    if rule == "all_cells":
        verdict = "PASS" if below == 0 and above == 0 else "FAIL"
    elif rule == "median":
        verdict = "PASS" if lo <= med <= hi else "FAIL"
    else:
        raise ValueError(rule)
    return verdict, {
        "n": len(v), "median": round(med, 2),
        "min": round(min(v), 2), "max": round(max(v), 2),
        "in_band": len(v) - below - above, "below_floor": below, "above_ceiling": above,
        "band_lo": lo, "band_hi": hi, "rule": rule,
    }


def report(rows, label):
    out = {}
    for ch, rule in RULE.items():
        r = [x for x in rows if x["channel"] == ch]
        lo, hi = float(r[0]["band_lo"]), float(r[0]["band_hi"])
        pooled_v, pooled_s = score(r, lo, hi, rule)
        groups = {}
        for g in sorted(set(x["building"] for x in r)):
            gv, gs = score([x for x in r if x["building"] == g], lo, hi, rule)
            gs["verdict"] = gv
            groups[g] = gs
        pooled_s["verdict"] = pooled_v
        out[ch] = {"pooled": pooled_s, "per_geometry": groups}
    return {"basis": label, "channels": out}


def fmt(d):
    L = []
    for ch, blk in d["channels"].items():
        p = blk["pooled"]
        L.append("### %s  (rule in force = %s, band [%g, %g])" % (ch, p["rule"], p["band_lo"], p["band_hi"]))
        L.append("")
        L.append("| unit | n | median | range | in band | below floor | above ceiling | verdict |")
        L.append("|---|--:|--:|---|--:|--:|--:|---|")
        L.append("| **pooled (as shipped)** | %d | %.2f | %.2f-%.2f | %d | %d | %d | **%s** |" % (
            p["n"], p["median"], p["min"], p["max"], p["in_band"], p["below_floor"], p["above_ceiling"], p["verdict"]))
        for g, s in blk["per_geometry"].items():
            L.append("| %s | %d | %.2f | %.2f-%.2f | %d | %d | %d | **%s** |" % (
                g, s["n"], s["median"], s["min"], s["max"], s["in_band"], s["below_floor"],
                s["above_ceiling"], s["verdict"]))
        L.append("")
    return "\n".join(L)


def main():
    deliv = report(load(DELIVERABLE), "outputs_step9_deliverable (FROZEN DELIVERABLE)")
    stale = report(load(STALE), "outputs_step9 (2026-07-31, superseded)")

    hotel = deliv["channels"]["hotel"]["per_geometry"]
    measured = {g: s["verdict"] for g, s in hotel.items()}
    agree = {g: (measured[g] == PREREGISTERED[g]) for g in PREREGISTERED}
    keeps_a_fail = any(s["verdict"] == "FAIL" for s in hotel.values())

    # the empty gap, measured rather than asserted
    hv = sorted(float(c["eui_CFA_kWh_m2"]) for c in load(DELIVERABLE) if c["channel"] == "hotel")
    gaps = [(hv[i + 1] - hv[i], hv[i], hv[i + 1]) for i in range(len(hv) - 1)]
    gap, glo, ghi = max(gaps)
    lo, hi = 180.0, 300.0

    verdict_block = {
        "preregistered": PREREGISTERED,
        "measured": measured,
        "agreement": agree,
        "all_predictions_held": all(agree.values()),
        "R1_at_least_one_hotel_subgate_still_FAILs": keeps_a_fail,
        "largest_empty_gap_kWh_m2": round(gap, 2),
        "gap_between": [round(glo, 2), round(ghi, 2)],
        "gap_pct_of_band_width": round(100 * gap / (hi - lo), 1),
        "ceiling_300_inside_the_gap": bool(glo < hi < ghi),
        "pooled_median_describes_no_cell": bool(glo < deliv["channels"]["hotel"]["pooled"]["median"] < ghi),
    }

    payload = {"task": "V4-A4", "date": "2026-08-06",
               "source_of_truth": DELIVERABLE.replace("\\", "/"),
               "superseded_comparison": STALE.replace("\\", "/"),
               "deliverable": deliv, "superseded": stale,
               "preregistration_check": verdict_block}

    with io.open(os.path.join(HERE, "v4_a4_split_scorecard.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, indent=1, ensure_ascii=False))

    print("=== SCORED ON THE FROZEN DELIVERABLE ===\n")
    print(fmt(deliv))
    print("=== the same scoring on the SUPERSEDED outputs_step9/ (why the predictions were inverted) ===\n")
    print(fmt(stale))
    print("=== PRE-REGISTRATION CHECK ===")
    print(json.dumps(verdict_block, indent=1))


if __name__ == "__main__":
    main()
