#!/usr/bin/env python
"""V3-H2 -- attack the claim that X-3 cannot fire while ISR-final passes.

THE CLAIM UNDER TEST
--------------------
V3-H2 rests on a three-line reading of
`3rdJ_04_augmentationGSS_4split_val.py:1448-1452`:

    n_hw = nansum((h == 1) & (w == 1))          -> X-3, pair hom/wrk
    n_hr = nansum((h == 1) & (r == 1))          -> X-3, pair hom/ret
    n_wr = nansum((w == 1) & (r == 1))          -> X-3, pair wrk/ret
    n_any_gt1 = nansum((h==1) + (w==1) + (r==1) > 1)   -> ISR-final

from which "a slot with two channels active is a pairwise conflict, and a
pairwise conflict is a slot with two channels active" -- so X-3 > 0 IFF
ISR-final > 0, and ISR-final FAILs above 1e-9 (`:496`).  If that holds, the
FAIL-vs-WARN question for X-3 has no detection consequence.

A CLAIM ABOUT AN IMPOSSIBILITY MUST BE ATTACKED, NOT ASSERTED.  Reading the
source is how the claim was formed; it cannot also be the evidence for it.  So
this runs the REAL validator on perturbed pools and tries to produce the
forbidden state: X-3 non-zero while ISR-final passes.

THE ARMS
--------
    A  control        the shipped pool, hard-linked (never copied, never written)
    B  hw k=1         one slot forced to hom=1 wrk=1 ret=0
    C  hr k=1         one slot forced to hom=1 ret=1 wrk=0
    D  wr k=1         one slot forced to wrk=1 ret=1 hom=0
    E  out-of-range   one slot forced to hom=1 ret=2 -- an attack from outside
                      the {0,1} domain both counters assume
    F  hw k=1000      enough conflicts to be real, few enough to sit under
                      X-3's own 1.0 % PASS bar

B/C/D are the positive controls: without them, "X-3 read zero" is
indistinguishable from "X-3 is broken".  E and F are the attacks.

EXACTNESS
---------
The control pool has ZERO conflicts, so forcing k slots to a chosen pair with
the third channel explicitly zeroed injects EXACTLY k conflicts of EXACTLY that
pair -- the expected X-3 census is known before the validator runs, per pair,
to the cell.

Only the three targeted fields of the targeted rows are rewritten; every other
byte of the 418 MB pool is streamed through untouched, so a gate that moves
cannot have moved because of reformatting.

Usage:  python falsify_x3_isr_relation.py <pool.csv> <workdir> [--arms A_control,...]
        python falsify_x3_isr_relation.py <pool.csv> <workdir> --arms none   # score
Exit 1 if any required condition is unmet.
"""

import os
import re
import shutil
import subprocess
import sys

VALIDATOR = "3rdJ_04_augmentationGSS_4split_val.py"
SLOT = 24                     # midday, arbitrary but fixed
X3_PASS_PCT = 1.0             # `thr["x3_pass_pct"]` -- read, not assumed (checked below)

# arm -> (list of (column, value) forced at SLOT, k rows)
ARMS = {
    "A_control":  (None, 0),
    "B_hw_k1":    ((("hom30", "1"), ("wrk30", "1"), ("ret30", "0")), 1),
    "C_hr_k1":    ((("hom30", "1"), ("ret30", "1"), ("wrk30", "0")), 1),
    "D_wr_k1":    ((("wrk30", "1"), ("ret30", "1"), ("hom30", "0")), 1),
    "E_oor":      ((("hom30", "1"), ("ret30", "2"), ("wrk30", "0")), 1),
    "F_hw_k1000": ((("hom30", "1"), ("wrk30", "1"), ("ret30", "0")), 1000),
}


def write_pool(src, dst, forced, k):
    """Stream src -> dst, forcing `forced` at SLOT on the first k synthetic rows."""
    with open(src, encoding="utf-8") as fin, \
            open(dst, "w", encoding="utf-8", newline="\n") as fout:
        head = fin.readline()
        header = head.rstrip("\n").split(",")
        fout.write(head)
        at = {ch: header.index(f"{ch}_{SLOT:03d}") for ch, _ in forced}
        syn_at = header.index("IS_SYNTHETIC")
        done = 0
        for line in fin:
            if done < k:
                row = line.rstrip("\n").split(",")
                if row[syn_at] == "1":
                    for ch, val in forced:
                        row[at[ch]] = val
                    done += 1
                    fout.write(",".join(row) + "\n")
                    continue
            fout.write(line)
    assert done == k, f"only {done} of {k} synthetic rows found"
    return dst


def run_validator(workdir, log):
    cmd = [sys.executable, VALIDATOR, "--step4_dir", workdir]
    with open(log, "w", encoding="utf-8") as fh:
        subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, check=False)
    return [l.rstrip("\n") for l in open(log, encoding="utf-8") if l.startswith("  [")]


def _rec(line):
    m = re.match(r"\s*\[(\w+)\]\s+([A-Za-z0-9\-\.]+)\s+\|\s*(.*)$", line)
    return (m.group(1), m.group(2), m.group(3)) if m else (None, None, None)


def read_isr(lines):
    """-> (level, pct) for the recomputed ISR-final line (not the cross-check).

    HARDENED after the first run: the "cannot recompute" variant of this line
    must be read too.  Without it arm E parsed to level=None, and the
    impossibility check below -- "no arm has ISR-final PASS while X-3 > 0" --
    would have been satisfied for arm E by a PARSE MISS rather than by the
    claim holding.  A check that a silent reader failure can satisfy is the
    vacuous-reading failure this project catalogues; it is not allowed to sit
    inside the one condition that carries the argument.
    """
    for l in lines:
        lvl, gate, msg = _rec(l)
        if gate == "ISR-final" and "Final (post-projection)" in msg:
            m = re.search(r":\s*([\d.]+)%", msg)
            return lvl, (float(m.group(1)) if m else None)
    for l in lines:                       # the refusal variant (:1478)
        lvl, gate, msg = _rec(l)
        if gate == "ISR-final" and "cannot recompute" in msg:
            return lvl, "refused"
    return None, None


def read_x3(lines):
    """-> {pair: (level, count)} from the three X-3 lines."""
    out = {}
    for l in lines:
        lvl, gate, msg = _rec(l)
        if gate == "X-3":
            m = re.match(r"Pairwise exclusivity \(([^)]+)\):\s*([\d,]+) cells", msg)
            if m:
                out[m.group(1)] = (lvl, int(m.group(2).replace(",", "")))
    return out


PAIR = {"B_hw_k1": "hom AND wrk", "C_hr_k1": "hom AND ret",
        "D_wr_k1": "wrk AND ret", "F_hw_k1000": "hom AND wrk"}


def main():
    pool, work = sys.argv[1], sys.argv[2]
    keep = "--keep" in sys.argv
    os.makedirs(work, exist_ok=True)

    sel = None
    for i, a in enumerate(sys.argv):
        if a == "--arms" and i + 1 < len(sys.argv):
            sel = [x for x in sys.argv[i + 1].split(",") if x and x != "none"]

    gates = {}
    for name, (forced, k) in ARMS.items():
        d = os.path.join(work, name)
        log = os.path.join(work, f"{name}.log")
        if sel is None or name in sel:
            os.makedirs(d, exist_ok=True)
            target = os.path.join(d, "augmented_diaries.csv")
            if not os.path.exists(target):
                if forced is None:
                    try:
                        os.link(pool, target)      # control is never written
                    except OSError:
                        shutil.copy(pool, target)
                else:
                    print(f"  writing {name} ...", flush=True)
                    write_pool(pool, target, forced, k)
            print(f"  validating {name} ...", flush=True)
            gates[name] = run_validator(d, log)
        elif os.path.exists(log):
            gates[name] = [l.rstrip("\n") for l in open(log, encoding="utf-8")
                           if l.startswith("  [")]
        else:
            print(f"  {name}: no log yet -- run it with --arms {name}")
            return 2
    if sel:
        print(f"\narms {','.join(sel)} done; run the rest, then score with --arms none")
        return 0

    isr = {k: read_isr(v) for k, v in gates.items()}
    x3 = {k: read_x3(v) for k, v in gates.items()}

    print("\n%-12s %-14s %-10s %s" % ("arm", "ISR-final", "pct", "X-3 census"))
    for name in ARMS:
        lvl, pct = isr[name]
        cen = "  ".join(f"{p}={n}[{l}]" for p, (l, n) in sorted(x3[name].items()))
        print("%-12s %-14s %-10s %s" % (name, lvl, f"{pct}", cen))

    checks = []

    # 1 -- the control must read clean, or nothing below means anything
    lvl, pct = isr["A_control"]
    checks.append(("control: ISR-final PASS at 0 % and all three X-3 counts zero",
                   lvl == "PASS" and pct == 0.0
                   and all(n == 0 for _l, n in x3["A_control"].values())))

    # 2-4 -- positive controls, one per pair, with the census known in advance
    for arm in ("B_hw_k1", "C_hr_k1", "D_wr_k1"):
        lvl, _pct = isr[arm]
        want = PAIR[arm]
        got = {p: n for p, (_l, n) in x3[arm].items()}
        ok = (lvl == "FAIL" and got.get(want) == 1
              and all(v == 0 for p, v in got.items() if p != want))
        checks.append((f"{arm}: ISR-final FAILs and X-3 reports exactly 1 cell on "
                       f"'{want}' and 0 on the other two", ok))

    # 5 -- THE CLAIM.  No arm may show a non-zero X-3 while ISR-final passes.
    unread = [a for a in ARMS if isr[a][0] is None]
    broken = [a for a in ARMS
              if isr[a][0] == "PASS" and any(n > 0 for _l, n in x3[a].values())]
    checks.append(("the claim: no arm produces X-3 > 0 while ISR-final PASSes "
                   f"(attacked by E and F; breaking arms: {broken or 'none'}; "
                   f"unreadable arms, which do NOT count as holding: "
                   f"{unread or 'none'})",
                   not broken and not unread))

    # 6 -- the out-of-range attack: it does not break the claim, and what it
    #      does expose is a blind spot the two counters SHARE.
    lvl, _pct = isr["E_oor"]
    checks.append(("E: a value outside {0,1} is invisible to BOTH counters "
                   "(ISR-final PASS and X-3 all-zero on a pool that does "
                   "contain a hom/ret overlap)",
                   lvl == "PASS" and all(n == 0 for _l, n in x3["E_oor"].values())))

    # 7 -- severity is not the binding constraint: X-3 can grade PASS on a pool
    #      ISR-final has already failed, so raising X-3 to FAIL adds nothing.
    lvl, _pct = isr["F_hw_k1000"]
    got = {p: (l, n) for p, (l, n) in x3["F_hw_k1000"].items()}
    hw_lvl, hw_n = got.get("hom AND wrk", (None, None))
    checks.append((f"F: 1000 real conflicts -> ISR-final FAIL while X-3 itself "
                   f"grades {hw_lvl} (count {hw_n}, under its own "
                   f"{X3_PASS_PCT} % PASS bar)",
                   lvl == "FAIL" and hw_n == 1000 and hw_lvl == "PASS"))

    print()
    bad = 0
    for msg, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {msg}")
        bad += 0 if ok else 1
    print(f"\n{len(checks) - bad}/{len(checks)} conditions met")

    if not keep:
        for name in ARMS:
            d = os.path.join(work, name)
            t = os.path.join(d, "augmented_diaries.csv")
            if os.path.exists(t):
                os.remove(t)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
