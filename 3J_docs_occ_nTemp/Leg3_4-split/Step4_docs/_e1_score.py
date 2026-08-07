#!/usr/bin/env python
"""V2-E1 scorer: diff the retail gate verdicts across baseline / zero / shuffle.

Scores the four pre-registered predictions. Reads the three `step4_validation_report.txt` files the
real validator wrote -- no gate logic is reimplemented here.
"""
import re
from pathlib import Path

ROOT = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\_local_runs\_e1_perturbed")
MODES = ("baseline", "zero", "shuffle", "shuffle_strat")
LINE = re.compile(r"^\[(PASS|WARN|FAIL)\]\s+([A-Za-z0-9\-]+)\s*\|\s*(.*)$")
# Every gate id the retail battery can emit. RETM is included: it is the same computation RW8
# reports, and the validator says so.
RETAIL_PREFIX = ("RW", "RETM", "ISR")


def parse(mode: str) -> dict:
    f = ROOT / mode / "step4_validation_report.txt"
    if not f.exists():
        raise SystemExit(f"[FATAL] {f} missing -- the {mode} run did not write a report.")
    out = {}
    for ln in f.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE.match(ln.strip())
        if not m:
            continue
        status, gate, detail = m.groups()
        # A gate id can appear many times (per cycle / per daytype). Key on id+detail-prefix so the
        # comparison is line-for-line rather than collapsing a 4-cycle gate into one verdict.
        key = (gate, detail.split(":")[0].strip())
        out[key] = (status, detail)
    return out


def num(detail: str, label: str):
    m = re.search(re.escape(label) + r"[^0-9\-]*(-?[0-9]*\.?[0-9]+)", detail)
    return float(m.group(1)) if m else None


def main() -> int:
    R = {m: parse(m) for m in MODES}
    for m in MODES:
        n = len(R[m])
        rt = sum(1 for (g, _) in R[m] if g.startswith(RETAIL_PREFIX))
        print(f"{m:<9} {n:>4} gate lines parsed · {rt} retail-battery lines")

    print("\n=== V2-E1 pre-registered predictions ===")
    v = []

    # ---- P1: RW1 / RW2 do not move at all -------------------------------------------------
    def rw(mode, gate):
        for (g, _), (st, det) in R[mode].items():
            if g == gate:
                return st, det
        return None, None

    p1_rows = []
    p1 = True
    for gate in ("RW1", "RW2"):
        vals = {}
        for m in MODES:
            st, det = rw(m, gate)
            vals[m] = (st, det)
        base_st, base_det = vals["baseline"]
        if base_st is None:
            p1 = False
            p1_rows.append(f"{gate}: ABSENT from the baseline report")
            continue
        same = all(vals[m][1] == base_det and vals[m][0] == base_st for m in MODES)
        p1 &= same
        p1_rows.append(f"{gate}: " + " · ".join(f"{m}={vals[m][0]}" for m in MODES) +
                       f"  [{'identical text' if same else 'CHANGED'}]  {base_det[:60]}")
    v.append(("P1 RW1/RW2 INERT", p1, "  ||  ".join(p1_rows)))

    # ---- P2: the all-zeros case is caught --------------------------------------------------
    tw_z = rw("zero", "RW-TRIPWIRE")
    tw_b = rw("baseline", "RW-TRIPWIRE")
    v.append(("P2 ZERO CAUGHT", tw_z[0] == "FAIL",
              f"RW-TRIPWIRE baseline={tw_b[0]} zero={tw_z[0]}"))

    # ---- P3: the shuffled pool passes the entire retail battery -----------------------------
    changed = []
    for key, (st, det) in R["baseline"].items():
        if not key[0].startswith(RETAIL_PREFIX):
            continue
        st2 = R["shuffle_strat"].get(key, ("MISSING", ""))[0]
        if st2 != st:
            changed.append(f"{key[0]}/{key[1][:34]}: {st}->{st2}")
    v.append(("P3 SHUFFLE INVISIBLE", not changed,
              f"retail gate lines changing status under STRATIFIED SHUFFLE: {len(changed)}"
              + ("  " + " · ".join(changed[:6]) if changed else "  (none)")))

    # ---- P4: B-3 confirmed in substance, refuted in its literal form ------------------------
    p4 = (tw_z[0] == "FAIL") and (not changed) and p1
    v.append(("P4 B-3 VERDICT", p4,
              "all-zeros IS caught (by the tripwire, not RW1/RW2); a marginal-preserving "
              "shuffle is caught by NOTHING" if p4 else "composite of P1-P3 did not hold"))

    for name, ok, why in v:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:<21} {why}")
    npass = sum(1 for _, ok, _ in v if ok)
    print(f"\n  {npass}P / {len(v) - npass}F")

    # ---- the whole-scorecard diff, so a change outside retail cannot hide -------------------
    print("\n=== every gate line whose status changed, ANY battery ===")
    for m in ("zero", "shuffle", "shuffle_strat"):
        diffs = [(k, R['baseline'][k][0], R[m].get(k, ("MISSING",))[0])
                 for k in R["baseline"] if R[m].get(k, ("MISSING",))[0] != R["baseline"][k][0]]
        print(f"  {m}: {len(diffs)} changed")
        for k, a, b in diffs[:25]:
            print(f"     {k[0]:<14} {a:>4} -> {b:<4}  {k[1][:58]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
