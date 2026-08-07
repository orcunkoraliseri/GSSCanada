#!/usr/bin/env python
"""Per-gate-ID verdict table across the four arms.

The line-level diff keys on the detail string, which for RW7 embeds the numbers it is comparing --
so a changed number reads as a MISSING key rather than as a status change. This collapses to the
GATE ID and reports the worst status per id, which is what "did this gate fire" actually means.
"""
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\_local_runs\_e1_perturbed")
MODES = ("baseline", "zero", "shuffle", "shuffle_strat")
LINE = re.compile(r"^\[(PASS|WARN|FAIL)\]\s+([A-Za-z0-9\-]+)\s*\|\s*(.*)$")
RANK = {"PASS": 0, "WARN": 1, "FAIL": 2}
RETAIL = ("RW", "RETM", "ISR", "X-3")


def worst(mode):
    out = defaultdict(lambda: "PASS")
    seen = set()
    for ln in (ROOT / mode / "step4_validation_report.txt").read_text(
            encoding="utf-8", errors="replace").splitlines():
        m = LINE.match(ln.strip())
        if not m:
            continue
        st, gate, _ = m.groups()
        seen.add(gate)
        if RANK[st] > RANK[out[gate]]:
            out[gate] = st
    return {g: out[g] for g in seen}


W = {m: worst(m) for m in MODES}
ids = sorted({g for m in MODES for g in W[m]},
             key=lambda g: (not g.startswith(RETAIL), g))

print(f"{'gate':<16}{'baseline':>10}{'zero':>8}{'shuffle':>10}{'strat':>8}   verdict")
print("-" * 76)
n_blind = n_catch = 0
for g in ids:
    row = [W[m].get(g, "-") for m in MODES]
    if not g.startswith(RETAIL):
        continue
    base, z, sh, ss = row
    if ss == base and z == base:
        tag = "BLIND to both"
    elif ss == base:
        tag = "blind to the stratified shuffle"
    else:
        tag = "*** CATCHES the person-level shuffle ***"
    if g.startswith(("RW", "RETM")):
        n_blind += (ss == base)
        n_catch += (ss != base)
    print(f"{g:<16}{base:>10}{z:>8}{sh:>10}{ss:>8}   {tag}")

print("-" * 76)
print(f"RW/RETM gates blind to the stratified shuffle: {n_blind} of {n_blind + n_catch}")
print("\nnon-retail gates that changed under the stratified shuffle:")
for g in ids:
    if g.startswith(RETAIL):
        continue
    if W["shuffle_strat"].get(g) != W["baseline"].get(g):
        print(f"  {g}: {W['baseline'].get(g)} -> {W['shuffle_strat'].get(g)}")
