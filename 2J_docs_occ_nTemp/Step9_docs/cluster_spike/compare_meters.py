#!/usr/bin/env python3
"""
compare_meters.py — local vs container hourly_meters.csv diff.

Runs LOCALLY after downloading hourly_meters_container.csv from Speed.

Usage:
    python compare_meters.py <local_hourly_meters.csv> <container_hourly_meters.csv>

Gate: PASS if all significant end-uses (annual > 0.1 kWh) differ < 0.5%.
      FAIL if any exceed 0.5%. Exit 1 on FAIL.
"""
import csv
import sys


def load_csv(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    meters = [c for c in fieldnames if c != "hour"]
    data = {}
    for m in meters:
        vals = []
        for r in rows:
            v = r.get(m, "")
            vals.append(float(v) if v else 0.0)
        data[m] = vals
    return data


def main():
    if len(sys.argv) != 3:
        print("Usage: compare_meters.py <local.csv> <container.csv>", file=sys.stderr)
        sys.exit(1)

    local = load_csv(sys.argv[1])
    cont = load_csv(sys.argv[2])

    all_meters = sorted(set(local) | set(cont))
    J_per_kWh = 3_600_000

    print(f"\n{'Meter':<45} {'Local kWh':>12} {'Cont kWh':>12} {'Diff%':>9} {'MaxHrly J':>11}")
    print("-" * 97)

    gate_ok = True
    for m in all_meters:
        lv = local.get(m, [])
        cv = cont.get(m, [])
        l_ann = sum(lv) / J_per_kWh
        c_ann = sum(cv) / J_per_kWh
        denom = max(abs(l_ann), 1e-6)
        pct = abs(l_ann - c_ann) / denom * 100
        n = min(len(lv), len(cv))
        max_h = max(abs(lv[i] - cv[i]) for i in range(n)) if n > 0 else 0.0
        # Gate only on meangingful end-uses (>0.1 kWh/yr)
        significant = l_ann > 0.1 or c_ann > 0.1
        flag = "  <<FAIL" if (pct > 0.5 and significant) else ""
        if flag:
            gate_ok = False
        missing = " [local only]" if m not in cont else (" [container only]" if m not in local else "")
        print(f"  {m:<43} {l_ann:>12.1f} {c_ann:>12.1f} {pct:>9.4f}%{flag}{missing}  maxH={max_h:.0f}")

    print()
    nrows_local = max((len(v) for v in local.values()), default=0)
    nrows_cont = max((len(v) for v in cont.values()), default=0)
    print(f"  Rows: local={nrows_local}, container={nrows_cont}")

    print()
    if gate_ok:
        print("GATE: PASS — all significant end-uses within 0.5%")
        sys.exit(0)
    else:
        print("GATE: FAIL — one or more end-uses exceed 0.5%")
        sys.exit(1)


if __name__ == "__main__":
    main()
