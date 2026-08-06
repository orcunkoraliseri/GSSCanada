#!/usr/bin/env python3
"""V2-D10 checks for the per-object DHW resize: byte-level regression + the guards, seen failing.

TWO JOBS, and the first one matters more than the feature.

R -- REGRESSION. `resize_idf()` grew a per-object path. Eight arms have been differenced against
files the SCALAR path wrote, so the scalar path must still emit those files byte-for-byte. This is
checked against artefacts already on disk (`_local_K16/K1`, `_local_K16/K6`), not against a
freshly-computed expectation, because an expectation recomputed by the code under test is the class
of gate whose reference comes from the same source it audits.

S -- THE FEATURE. With `Laundry Service Water Use 30.6gpm 180F=7`, exactly one heater moves and it
is the one on the dedicated `Laundry Service Water Loop`. The other five (Tall) / ten (SuperTall)
capacity fields must be byte-identical to arm H's.

F -- THE GUARDS, RUN. Refusals that are never triggered are decoration. Each is executed here and
must raise: a substring matching nothing, a substring matching several, a heater name that no object
carries, and -- the one that is easy to forget -- two spec entries landing on the same loop with
different factors.

    python 3rdJ_09H_resize_spec_check.py <armH_cells_dir> <local_K16_dir>
"""
import os
import re
import shutil
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from importlib.machinery import SourceFileLoader
import importlib.util


def _load(name, path):
    spec = importlib.util.spec_from_loader(name, SourceFileLoader(name, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


probe = _load("resize_probe", os.path.join(_HERE, "3rdJ_09H_plant_resize_probe.py"))
topo = _load("dhw_plant_topology", os.path.join(_HERE, "3rdJ_09H_dhw_plant_topology.py"))
cell = _load("resize_campaign_cell", os.path.join(_HERE, "3rdJ_09H_resize_campaign_cell.py"))

CAP_RE = re.compile(r"([0-9.eE+-]+),\s*!- Heater Maximum Capacity\b")
LAUNDRY_EQUIP = "Laundry Service Water Use 30.6gpm 180F"

RES = []


def check(tag, ok, detail=""):
    RES.append((tag, bool(ok)))
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", tag, ("  -- " + detail) if detail else ""))
    return ok


def refuses(tag, fn, detail=""):
    """The guard must raise. Passing quietly is the failure being tested for."""
    try:
        fn()
    except SystemExit as e:
        return check(tag, True, str(e)[:110])
    except Exception as e:                                  # noqa: BLE001 - any refusal counts
        return check(tag, True, "%s: %s" % (type(e).__name__, str(e)[:90]))
    return check(tag, False, "DID NOT REFUSE" + ((" -- " + detail) if detail else ""))


def caps(path):
    with open(path, errors="replace") as f:
        return [m.group(1) for m in CAP_RE.finditer(f.read())]


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: %s <armH_cells_dir> <local_K16_dir>" % sys.argv[0])
    armh, k16 = sys.argv[1], sys.argv[2]
    tmp = tempfile.mkdtemp(prefix="d10_")
    try:
        print("=" * 92)
        print("V2-D10  per-object resize: regression, feature, guards")
        print("=" * 92)

        # ---- R: scalar mode still writes the exact bytes eight arms were differenced against ----
        for K, arm in ((1.0, "K1"), (6.0, "K6")):
            for geo in ("B_central__Tall__MTL", "B_central__SuperTall__MTL"):
                src = os.path.join(armh, geo, "injected.idf")
                ref = os.path.join(k16, arm, geo, "injected_resized.idf")
                if not (os.path.isfile(src) and os.path.isfile(ref)):
                    check("R %s %s" % (arm, geo), False, "artefact missing -- cannot regress")
                    continue
                dst = os.path.join(tmp, "r_%s_%s.idf" % (arm, geo))
                probe.resize_idf(src, dst, K)
                a, b = open(dst, "rb").read(), open(ref, "rb").read()
                check("R  scalar K=%.0f reproduces %s/%s byte-for-byte" % (K, arm, geo), a == b,
                      "" if a == b else "%d vs %d bytes" % (len(a), len(b)))

        # ---- S: the feature ----------------------------------------------------------------
        for geo, n_heat in (("B_central__Tall__MTL", 6), ("B_central__SuperTall__MTL", 11)):
            src = os.path.join(armh, geo, "injected.idf")
            if not os.path.isfile(src):
                check("S %s" % geo, False, "arm-H IDF missing")
                continue
            per, report = cell.resolve_equip_spec("%s=7" % LAUNDRY_EQUIP, src, topo)
            check("S  %s: LAUNDRY resolves to exactly 1 heater" % geo, len(per) == 1, str(list(per)))
            check("S  %s: on the dedicated Laundry loop" % geo,
                  bool(report) and report[0][1].lower().startswith("laundry"),
                  report[0][1] if report else "")
            dst = os.path.join(tmp, "s_%s.idf" % geo)
            probe.resize_idf(src, dst, 1.0, per)
            base, new = caps(src), caps(dst)
            check("S  %s: %d capacity fields in, %d out" % (geo, n_heat, len(new)),
                  len(base) == n_heat and len(new) == n_heat)

            # The comparison is on the RATIO, not on equality, and the reason is a real property of
            # the writer found by this check on 2026-08-05: `resize_idf()` re-formats every capacity
            # to "%.6f" whatever the factor, so at K = 1 the field goes
            # 87921.3210516667 -> 87921.321052 -- a 3.3e-7 W, 3.8e-12 relative change. Equality
            # therefore reports ALL fields as moved, and the "every OTHER field is equal" companion
            # then quantifies over an empty set and passes vacuously. That pairing is what caught it.
            # The behaviour is NOT being changed: eight arms were written through this formatter and
            # the byte-regression above exists to keep them reproducible.
            ratios = [float(n) / float(b) for b, n in zip(base, new)]
            reformat = max(abs(r - 1.0) for i, r in enumerate(ratios) if abs(r - 7.0) > 1e-9)
            check("S  %s: the reformat is below 1e-9 relative, so the tolerance hides nothing" % geo,
                  reformat < 1e-9, "worst unselected drift %.3e relative" % reformat)
            up = [i for i, r in enumerate(ratios) if abs(r - 7.0) < 1e-9]
            check("S  %s: exactly 1 capacity field scaled by 7" % geo, len(up) == 1, str(up))
            flat = [i for i, r in enumerate(ratios) if abs(r - 1.0) < 1e-9]
            check("S  %s: the other %d are unchanged to 1e-9" % (geo, n_heat - 1),
                  len(flat) == n_heat - 1 and len(up) + len(flat) == n_heat,
                  "%d scaled, %d flat, %d fields" % (len(up), len(flat), n_heat))
            tot_b, tot_n = sum(map(float, base)) / 1000, sum(map(float, new)) / 1000
            print("        installed %.2f kW -> %.2f kW (a global K=7 would give %.2f kW)"
                  % (tot_b, tot_n, tot_b * 7))

        # ---- F: the guards, executed ---------------------------------------------------------
        src = os.path.join(armh, "B_central__Tall__MTL", "injected.idf")
        refuses("F1 substring matching NO equipment refuses",
                lambda: cell.resolve_equip_spec("no_such_equipment_xyz=7", src, topo))
        refuses("F2 substring matching MANY equipment refuses",
                lambda: cell.resolve_equip_spec("service water use=7", src, topo))
        refuses("F3 per_object naming a nonexistent heater refuses",
                lambda: probe.resize_idf(src, os.path.join(tmp, "f3.idf"), 1.0,
                                         {"no such water heater": 7.0}))
        # F4 REACHES THE BRANCH IT NAMES. The first version passed on
        # "...=7,Laundry Service Water Use=3" -- but that refused at the earlier
        # matched-2-objects guard and never touched the same-loop conflict at all. A guard that
        # passes because a DIFFERENT guard fired is not evidence about itself. So the two
        # equipment names are now found from the topology: two distinct objects that genuinely
        # share one loop, given different factors.
        _h, _loops, _equip, _e2l = topo.build(topo.load(src))
        _pair = None
        for _lp, _inf in _loops.items():
            _members = [e for e, v in _e2l.items() if v["loop"] == _lp]
            if len(_members) >= 2:
                _pair = (_members[0], _members[1], _lp)
                break
        if _pair:
            refuses("F4 two spec entries on the SAME loop, different factors, refuses",
                    lambda: cell.resolve_equip_spec("%s=7,%s=3" % (_pair[0], _pair[1]), src, topo),
                    "loop %s" % _pair[2])
        else:
            check("F4 two spec entries on the SAME loop, different factors, refuses", False,
                  "no loop carries 2 equipment objects -- the branch is unreachable and untested")
        refuses("F5 malformed spec item refuses",
                lambda: cell.resolve_equip_spec("laundry", src, topo))

        # F6 is the CONTROL for the refusals: the correct spec must NOT refuse. Without it, a
        # resolve_equip_spec() that raised unconditionally would score 5/5 above.
        try:
            cell.resolve_equip_spec("%s=7" % LAUNDRY_EQUIP, src, topo)
            check("F6 CONTROL: the correct spec does not refuse", True)
        except BaseException as e:                          # noqa: BLE001
            check("F6 CONTROL: the correct spec does not refuse", False, str(e)[:110])

        print("")
        n_ok = sum(1 for _, ok in RES if ok)
        print("  %d/%d checks passed" % (n_ok, len(RES)))
        sys.exit(0 if n_ok == len(RES) else 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
