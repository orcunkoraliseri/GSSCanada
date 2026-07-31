#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3J Leg-3 -- Step 8D : verify a finished campaign against its ARTEFACTS, not its status lines.

Standing rule on this project: re-derive, do not believe. A campaign's own summary ("56/56 ok")
reports what the harness thinks it did; this reads what it actually wrote. The 2026-07-30 run
returned exit 0 with empty stdout, and the 2026-07-31 defect set (gas meters reporting zero,
unmultiplied channel series) lived entirely inside manifests that looked perfect.

Every check below is one this campaign could plausibly fail.
"""
from __future__ import annotations
import json, os, sys, csv
from collections import Counter, defaultdict

CH = ["office", "retail", "hotel", "residential", "residential_common", "service_MEP"]


def _expect_fn():
    """Return scenario -> frozenset(expected channels), read from the campaign cell table itself."""
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location(
        "_cells_mod", os.path.join(here, "3rdJ_08D_campaign_cells.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod._expected_channels


EXPECT = _expect_fn()


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "campaign_local_v2/campaign_cf69d508"
    cells = sorted(d for d in os.listdir(root)
                   if os.path.isdir(os.path.join(root, d)) and "_STALE_" not in d
                   and os.path.isfile(os.path.join(root, d, "manifest.json")))
    print(f"=== verifying {len(cells)} cell(s) in {root} ===\n")
    fails, mans, planned = [], {}, []
    for c in cells:
        with open(os.path.join(root, c, "manifest.json"), encoding="utf-8") as f:
            m = json.load(f)
        mans[c] = m

        def bad(msg):
            fails.append(f"{c}: {msg}")

        if m.get("ep_return_code") != 0:
            bad(f"ep_return_code = {m.get('ep_return_code')}")
        for k in [k for k in m if k.endswith("_exception")]:
            bad(f"exception key {k}: {m[k]}")
        for key in ("hourly_meters_csv", "channel_hourly_csv", "dhw_hourly_csv"):
            info = m.get(key, {})
            if info.get("rows") != 8760:
                bad(f"{key} rows = {info.get('rows')}, expected 8760")
            if not info.get("path") or not os.path.isfile(info["path"]):
                bad(f"{key} file missing on disk")
        fc = m.get("fuel_closure") or {}
        if fc.get("absent_meters"):
            bad(f"absent meters: {fc['absent_meters']}")
        for fuel in ("Electricity", "NaturalGas"):
            r = fc.get(fuel, {})
            if not r.get("closed"):
                bad(f"fuel closure {fuel} FAILED (residual {r.get('residual_rel')})")
        for metric, r in (m.get("channel_closure") or {}).items():
            if not r.get("closed"):
                bad(f"channel closure {metric} FAILED (residual {r.get('residual_rel')})")
        if m.get("dhw_unresolved_equipment"):
            bad(f"unresolved DHW equipment: {m['dhw_unresolved_equipment']}")
        inj = m.get("inject_mixed_use_result", {})
        res = inj.get("residential", {})
        scen = m.get("scenario", "")
        expected = EXPECT(scen)
        # A fallback is a FINDING only when the scenario was supposed to carry that channel.
        # DELIBERATE_CHANNEL_EXCEPTIONS in 3rdJ_08D_campaign_cells.py is the single source of
        # truth for which omissions are intended; consulting it here rather than keeping a second
        # copy is what stops this verifier drifting away from the design it is checking. Planned
        # omissions are still PRINTED -- "documented" must not become "invisible".
        for chan in (inj.get("fallback") or []):
            if chan in expected:
                bad(f"UNPLANNED fallback to NECB baseline: {chan}")
            else:
                planned.append((c, scen, chan))
        if "residential" in expected:
            if res.get("n_spaces", 0) <= 0 or res.get("n_spaces") != res.get("n_households_drawn"):
                bad(f"residential n_spaces={res.get('n_spaces')} "
                    f"n_households_drawn={res.get('n_households_drawn')}")
        elif res.get("n_spaces", 0) > 0:
            bad(f"residential injected ({res.get('n_spaces')} Spaces) into scenario '{scen}' "
                f"which is declared to carry no residential channel")
        if inj.get("ambiguous"):
            bad(f"ambiguous Tag-2 dispatch: {inj['ambiguous']}")
        unplanned_banner = [b for b in (m.get("banner_lines") or [])
                            if not any(f"FALLBACK: {ch}" in b
                                       for ch in (set(inj.get("fallback") or []) - expected))]
        if unplanned_banner:
            bad(f"unexplained banner line(s): {unplanned_banner[:2]}")

    def col(key):
        return Counter(m.get(key) for m in mans.values())

    print("PROVENANCE")
    for label, c in (("PLATFORM", col("PLATFORM")), ("INJ_HASH", col("INJ_HASH")),
                     ("OUTPUT_SCHEMA_HASH", col("OUTPUT_SCHEMA_HASH")),
                     ("energyplus_build", col("energyplus_build")),
                     ("driver_md5", col("driver_md5"))):
        print(f"  {label:<20} {dict(c)}")
    print(f"  {'INPUTS_HASH':<20} {len(col('INPUTS_HASH'))} distinct "
          f"(expected: one per scenario product set, NOT one overall)")
    print(f"  {'residential Spaces':<20} {dict(Counter(m['inject_mixed_use_result']['residential']['n_spaces'] for m in mans.values()))}")

    # Scenario axes must be alive on the columns the BEM loader actually READS -- differing md5s
    # prove nothing (a diagnostic column can vary while the consumed one is identical).
    print("\nSCENARIO AXES, ON THE CONSUMED COLUMNS")
    byscen = defaultdict(set)
    for c, m in mans.items():
        for d in m.get("INPUTS_HASH_DETAIL", []):
            byscen[d["channel"]].add(d["csv_md5"])
    for chan, s in sorted(byscen.items()):
        print(f"  {chan:<14} {len(s)} distinct product file(s) across the campaign")

    print("\nENERGY, RE-DERIVED FROM hourly_meters.csv")
    tot = {}
    for c in sorted(mans):
        p = os.path.join(root, c, "hourly_meters.csv")
        with open(p) as f:
            rd = csv.DictReader(f)
            e = g = 0.0
            n = 0
            for row in rd:
                e += float(row["Electricity:Facility"]); g += float(row["NaturalGas:Facility"]); n += 1
        tot[c] = (e / 1e9, g / 1e9, n)
    zero_gas = [c for c, (e, g, n) in tot.items() if g <= 0]
    print(f"  cells with ZERO natural gas: {len(zero_gas)} {zero_gas[:3]}")
    ge = sorted(tot.items(), key=lambda kv: kv[1][0])
    print(f"  Electricity:Facility  min {ge[0][1][0]:.1f} GJ ({ge[0][0]})  "
          f"max {ge[-1][1][0]:.1f} GJ ({ge[-1][0]})")
    gg = sorted(tot.items(), key=lambda kv: kv[1][1])
    print(f"  NaturalGas:Facility   min {gg[0][1][1]:.1f} GJ ({gg[0][0]})  "
          f"max {gg[-1][1][1]:.1f} GJ ({gg[-1][0]})")
    if len({n for _, _, n in tot.values()}) != 1:
        fails.append(f"row counts differ across cells: {Counter(n for _, _, n in tot.values())}")

    if planned:
        by = defaultdict(set)
        for cell, sc, ch in planned:
            by[(sc, ch)].add(cell)
        print("\nPLANNED CHANNEL OMISSIONS (DELIBERATE_CHANNEL_EXCEPTIONS -- documented, not defects)")
        for (sc, ch), cs in sorted(by.items()):
            print(f"  {sc:<16} carries NO '{ch}' channel, in {len(cs)} cell(s)")
        print("  These are legitimate, but they are NOT nothing: any axis built from these")
        print("  scenarios carries no signal at all for the omitted channel, and Step 9 must")
        print("  report that as ABSENT rather than as a flat result. A documented omission that")
        print("  stops being printed is how a gap becomes a finding in someone else's review.")

    print(f"\n=== {len(cells) - len({f.split(':')[0] for f in fails})}/{len(cells)} cells clean ===")
    if fails:
        print(f"[FINDINGS] {len(fails)}:")
        for f in fails[:60]:
            print(f"  {f}")
        sys.exit(1)
    print("no finding: every cell closes on both fuels and all three channel metrics, 8760 rows "
          "in all three CSVs, no ambiguous Tag-2 dispatch, and every channel omission is one the "
          "campaign table declares in advance.")


if __name__ == "__main__":
    main()
