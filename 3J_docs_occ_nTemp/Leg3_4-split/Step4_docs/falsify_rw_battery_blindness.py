#!/usr/bin/env python
"""V3-J2 -- rebuild of the lost V2-E1 demonstration, plus the proof RW9 closes it.

WHAT WAS LOST
-------------
V2-E1 (2026-08-05) established the audit's central retail finding: all ten
RW/RETM gates report IDENTICAL statuses on a pool whose retail vectors have been
permuted between people within a cell -- the named retail battery measures
marginals, not person-level skill.  The scripts that showed it
(_e1_perturb.py / _e1_score.py / _e1_summary.py) lived in a session scratchpad
and NO LONGER EXIST, in the repo or anywhere else.  A finding whose only
demonstration has evaporated is a finding on trust.

WHAT THIS DOES
--------------
Four runs of the REAL validator, on four pools:

    A  control              the shipped pool
    B  shuffle(control)     retail vectors permuted between people, within cell
    C  copy                 every synthetic retail vector := that person's own observed
    D  shuffle(copy)        C, then the same within-cell permutation

A vs B  reproduces E1: the RW battery must be BYTE-IDENTICAL while RW9's number
        moves.  On this pool RW9 already FAILs, so the verdict cannot flip --
        stated rather than dressed up.
C vs D  is the pair that shows RW9 does what the battery cannot: identical
        marginals, identical RW battery, and RW9 flips PASS -> FAIL.

A permutation preserves every marginal EXACTLY, which is what makes "the battery
did not move" evidence rather than coincidence.

WHY THE PERTURBATION IS TEXT-LEVEL
----------------------------------
The perturbed pools are written by streaming the source file and swapping only
the 48 ret30 fields, carrying every other byte through unchanged.  Round-tripping
644 columns through a dataframe would reformat numbers, and then a gate that
moved would be impossible to attribute -- the same trap V2-E1's own global
shuffle fell into.  A PERTURBATION THAT CHANGES MORE THAN ONE THING CANNOT
ATTRIBUTE WHAT IT BREAKS.

Usage:  python falsify_rw_battery_blindness.py <pool.csv> <workdir>
Exit 1 if any required condition is unmet.  Writes ~1.3 GB of transient pools
into <workdir> and deletes them at the end unless --keep is given.
"""

import csv
import os
import re
import shutil
import subprocess
import sys

import numpy as np

VALIDATOR = "3rdJ_04_augmentationGSS_4split_val.py"
KEYS = ("occID", "CYCLE_YEAR", "DDAY_STRATA", "PR", "IS_SYNTHETIC")
BATTERY = ("RW1", "RW2", "RW3", "RW4", "RW5", "RW6", "RW7", "RW8", "RETM")
ALL_CHANNELS = ("act30", "hom30", "wrk30", "ret30", "Alone30", "Spouse30",
                "Children30", "parents30", "otherInFAMs30", "otherHHs30",
                "friends30", "colleagues30", "others30")


def _scan(src, channels=("ret30",)):
    """One pass: field positions, per-row keys, and the raw ret30 text blocks."""
    # The pool carries no quoted fields (checked), so a plain split is both safe
    # and several times faster than the csv module over 644 columns.
    with open(src, encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split(",")
        spans = []
        for ch in channels:
            at = [i for i, c in enumerate(header) if re.fullmatch(ch + r"_\d{3}", c)]
            assert at and at[-1] + 1 - at[0] == len(at), f"{ch} columns not contiguous"
            spans.append((at[0], at[-1] + 1))
        key_at = {k: header.index(k) for k in KEYS}
        keys, blocks = [], []
        for line in fh:
            row = line.rstrip("\n").split(",")
            keys.append(tuple(row[key_at[k]] for k in KEYS))
            blocks.append([",".join(row[a:b]) for a, b in spans])
    return header, spans, keys, blocks


def _plan(keys, mode, seed=7):
    """Row -> row whose ret30 block it should end up carrying."""
    n = len(keys)
    src_of = np.arange(n)
    occ = np.array([k[0] for k in keys])
    cyc = np.array([k[1] for k in keys])
    stratum = np.array([k[2] for k in keys])
    pr = np.array([k[3] for k in keys])
    syn = np.array([k[4] for k in keys]) == "1"

    # each person's observed row
    person = np.char.add(np.char.add(occ, "|"), cyc)
    obs_row = {}
    for i in np.flatnonzero(~syn):
        obs_row[person[i]] = i

    if mode in ("copy", "copy_shuffle"):
        for i in np.flatnonzero(syn):
            j = obs_row.get(person[i])
            if j is not None:
                src_of[i] = j
    if mode in ("shuffle", "copy_shuffle"):
        # the null's own cell: (cycle, PR, syn stratum, the person's observed stratum)
        obs_strat = np.array([stratum[obs_row[p]] if p in obs_row else "?"
                              for p in person])
        cell = np.array(["|".join(t) for t in
                         zip(cyc, pr, stratum, obs_strat)])
        rng = np.random.default_rng(seed)
        idx = np.flatnonzero(syn)
        cs = cell[idx]
        order = np.lexsort((rng.random(idx.size), cs))
        # permute the CURRENT sources within each cell
        cur = src_of[idx].copy()
        by_cell = np.argsort(cs, kind="stable")   # cell blocks, original order
        # `order` walks the SAME cell blocks in the same block order, randomised
        # inside each -- so this permutes within cells and nowhere else.
        src_of[idx[by_cell]] = cur[order]
    return src_of


def write_pool(src, dst, mode, seed=7):
    """Stream src -> dst swapping only the ret30 fields."""
    # "joint" moves the three presence channels from the same donor, which
    # preserves channel exclusivity (a retail-only permutation does not).
    # "full" moves ALL THIRTEEN channel blocks -- the entire day, activities and
    # co-presence included -- so every row stays an internally consistent day
    # and the ONLY thing destroyed is whose day it is.
    if mode.startswith("full"):
        channels = ALL_CHANNELS
    elif mode.startswith("joint"):
        channels = ("hom30", "wrk30", "ret30")
    else:
        channels = ("ret30",)
    header, spans, keys, blocks = _scan(src, channels)
    src_of = _plan(keys, mode.replace("joint_", "").replace("full_", ""), seed)
    with open(src, encoding="utf-8") as fin, \
            open(dst, "w", encoding="utf-8", newline="\n") as fout:
        fout.write(fin.readline())                     # header, byte for byte
        for n, line in enumerate(fin):
            row = line.rstrip("\n").split(",")
            donor = blocks[src_of[n]]
            for (a, b), text in zip(spans, donor):
                row[a:b] = text.split(",")
            # Every field outside the rewritten spans is carried through as its
            # own text: no reformatting, so a gate that moves can only have
            # moved because of the channel blocks.
            fout.write(",".join(row) + "\n")
    return dst


def run_validator(workdir, log):
    env = dict(os.environ)
    cmd = [sys.executable, VALIDATOR, "--step4_dir", workdir]
    with open(log, "w", encoding="utf-8") as fh:
        subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, env=env, check=False)
    lines = [l.rstrip("\n") for l in open(log, encoding="utf-8")
             if l.startswith("  [")]
    return lines


def gate_of(line):
    m = re.match(r"\s*\[\w+\]\s+([A-Za-z0-9\-\.]+)\s+\|", line)
    return m.group(1) if m else "?"


def lift_of(lines, which="PARTICIPATION"):
    for l in lines:
        if gate_of(l) == "RW9" and which in l:
            m = re.search(r"lift ([+-][\d.]+)", l)
            if m:
                return float(m.group(1))
    return None


def main():
    pool = sys.argv[1]
    work = sys.argv[2]
    keep = "--keep" in sys.argv
    os.makedirs(work, exist_ok=True)

    arms = {"A_control": None, "B_shuffle": "shuffle",
            "C_copy": "copy", "D_copy_shuffle": "copy_shuffle",
            "E_joint_shuffle": "joint_shuffle",
            "F_full_shuffle": "full_shuffle"}

    # --arms lets each arm run as its own foreground job; the scoring pass then
    # runs with --arms none once all four logs exist.  Four validator runs plus
    # three 418 MB rewrites do not fit in one interactive slot.
    sel = None
    for i, a in enumerate(sys.argv):
        if a == "--arms" and i + 1 < len(sys.argv):
            sel = [x for x in sys.argv[i + 1].split(",") if x and x != "none"]

    gates = {}
    for name, mode in arms.items():
        d = os.path.join(work, name)
        log = os.path.join(work, f"{name}.log")
        if sel is None or name in sel:
            os.makedirs(d, exist_ok=True)
            target = os.path.join(d, "augmented_diaries.csv")
            if not os.path.exists(target):
                if mode is None:
                    try:
                        os.link(pool, target)      # no second copy on disk
                    except OSError:
                        shutil.copy(pool, target)
                else:
                    print(f"  writing {name} ...", flush=True)
                    write_pool(pool, target, mode)
            print(f"  validating {name} ...", flush=True)
            gates[name] = run_validator(d, log)
        elif os.path.exists(log):
            gates[name] = [l.rstrip("\n") for l in open(log, encoding="utf-8")
                           if l.startswith("  [")]
        else:
            print(f"  {name}: no log yet -- run it with --arms {name}")
            return 2
    if sel:
        print(f"\narms {','.join(sel)} done; run the rest, then score with "
              f"--arms none")
        return 0

    def battery(lines):
        return [l for l in lines if gate_of(l) in BATTERY]

    checks = []
    a, b, c, d = (gates[k] for k in ("A_control", "B_shuffle",
                                     "C_copy", "D_copy_shuffle"))

    checks.append(("E1 reproduced: RW/RETM battery byte-identical under a "
                   "person shuffle (A vs B)", battery(a) == battery(b)))
    la, lb = lift_of(a), lift_of(b)
    checks.append((f"RW9's number moves under the same shuffle "
                   f"({la:+.4f} -> {lb:+.4f})",
                   la is not None and lb is not None and la > 3 * max(lb, 1e-9)))
    checks.append(("battery byte-identical between C and D too",
                   battery(c) == battery(d)))
    lc, ld = lift_of(c), lift_of(d)
    checks.append((f"RW9 FLIPS on the pair the battery cannot see "
                   f"({lc:+.4f} PASS -> {ld:+.4f} FAIL)",
                   any(gate_of(l) == "RW9" and "[PASS]" in l for l in c)
                   and any(gate_of(l) == "RW9" and "[FAIL]" in l for l in d)))

    # Arms E and F were added after the first run: arm B's retail-only shuffle
    # ALSO breaks channel exclusivity (ISR-final 0.000000 % -> 1.421611 %), so
    # it cannot attribute what it breaks -- the exact defect V2-E1 warned about,
    # present in V2-E1's own arms.  E moves the three presence channels together
    # (exclusivity safe, but activities left behind).  F moves the WHOLE DAY.
    e = gates.get("E_joint_shuffle")
    f = gates.get("F_full_shuffle")
    if e:
        def line_of(lines, gate):
            return [l for l in lines if gate_of(l) == gate]
        checks.append(("arm E: the exclusivity confound in arm B is GONE "
                       "(ISR-final and X-3 unchanged)",
                       line_of(a, "ISR-final") == line_of(e, "ISR-final")
                       and line_of(a, "X-3") == line_of(e, "X-3")))
    if f:
        moved = [gate_of(x) for x, y in zip(a, f) if x != y]
        person_gates = {"RW9", "OW5", "OW5-REG"}
        checks.append((f"arm F: with EVERY generated day reassigned to another "
                       f"person, only {len(moved)} of {len(a)} validator lines "
                       f"move, and all are person-reading gates "
                       f"({', '.join(sorted(set(moved)))})",
                       bool(moved) and set(moved) <= person_gates))

    print("\n" + "=" * 72)
    for name, good in checks:
        print(f"  [{'PASS' if good else 'FAIL'}] {name}")
    print(f"\n{sum(g for _, g in checks)}/{len(checks)} required conditions met")

    n_batt = len(battery(a))
    print(f"\nbattery lines compared: {n_batt} per arm "
          f"({', '.join(sorted(set(gate_of(l) for l in battery(a))))})")
    print("NOTE, stated rather than dressed up: between A and B, RW9's VERDICT "
          "does not flip -- the shipped pool already FAILs it, so there is no "
          "headroom to lose.  The C/D pair is what shows the flip.")

    if not keep:
        for name in arms:
            shutil.rmtree(os.path.join(work, name), ignore_errors=True)
        print("transient pools deleted (logs kept)")

    return 0 if all(g for _, g in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
