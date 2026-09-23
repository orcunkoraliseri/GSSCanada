"""V3c negative control (static, no simulation): F (arm) must differ from U (frozen uninjected
Default_NECB) ONLY in the 4 PEOPLE objects' occupancy-schedule reference (apartment + 3 hotel guest
rooms) plus the 1 added Schedule:Compact NECB-G-Occupancy. Uses `v3_static.compare` (same tool V3b's
gate used): it expands every Schedule:Compact/:Constant a class references into its 12-month x
12-day-type x 48-half-hour content and diffs OBJECTS, so the new schedule's own definition is not
counted directly -- it shows up only where a PEOPLE object's schedule REFERENCE now resolves to
different content. That is exactly the check this control needs.

PASS condition (real F vs U): compare() reports n_only_a == n_only_b == 4, all class PEOPLE.
FAIL-must-fire condition (negative control): build F, then ALSO change one LIGHTS object's schedule
(HighriseApartment Apartment Lights) as a stand-in for "the agent also touched lights/equipment by
mistake" -- compare() must then report a 5th differing object of class LIGHTS, i.e. more than 4 total
or a non-PEOPLE class present. If it does not, this checker exits non-zero and the control has failed
to fire (see 3J CLAUDE.md "a check must be seen failing before it is trusted").

    py -3 v3c_static_check.py <frozen_Default_NECB_dir_with_4_cells> <workdir>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v3_static as S     # noqa: E402
import v3c_build_F as F   # noqa: E402

CELLS = [("Tall", "MTL"), ("Tall", "CLG"), ("SuperTall", "MTL"), ("SuperTall", "CLG")]


def frozen_u(deliverable_root, b, c):
    return os.path.join(deliverable_root, "Default_NECB__%s__%s" % (b, c), "injected_resized.idf")


def real_check(deliverable_root, work):
    """PASS iff every cell: F vs U differs in exactly 4 objects, all class PEOPLE."""
    ok = True
    report = []
    for b, c in CELLS:
        u = frozen_u(deliverable_root, b, c)
        f = os.path.join(work, "F__%s__%s.idf" % (b, c))
        rep = F.build(u, f)
        cmp_ = S.compare(f, u)
        cells_ok = (rep["objects_changed"] == 4 and rep["objects_added"] == 1
                    and cmp_["n_only_a"] == 4 and cmp_["n_only_b"] == 4
                    and cmp_["classes_only_a"] == ["PEOPLE"] and cmp_["classes_only_b"] == ["PEOPLE"])
        ok = ok and cells_ok
        report.append({"cell": "%s/%s" % (b, c), "build": rep, "compare_n_only_a": cmp_["n_only_a"],
                        "compare_n_only_b": cmp_["n_only_b"], "classes_only_a": cmp_["classes_only_a"],
                        "classes_only_b": cmp_["classes_only_b"], "pass": cells_ok})
    return ok, report


def negative_control(deliverable_root, work):
    """Must FAIL: F plus an extra, out-of-contract LIGHTS-schedule edit must show > 4 diffs / a
    non-PEOPLE class, on one cell (Tall/MTL) -- proving the check would catch an over-broad edit."""
    b, c = "Tall", "MTL"
    u = frozen_u(deliverable_root, b, c)
    f = os.path.join(work, "F_bad__%s__%s.idf" % (b, c))
    F.build(u, f)
    txt = open(f, errors="replace").read()
    # re-point one LIGHTS object's schedule to NECB-G-Occupancy too (out of contract)
    RB = F.RB
    objs = RB.objects(txt)
    edits = []
    for s, e, cls, fl in objs:
        if cls.upper() == "LIGHTS" and fl[0] == "HighriseApartment Apartment Lights":
            nf = list(fl)
            nf[2] = "NECB-G-Occupancy"
            edits.append((s, e, RB.fmt(cls, nf)))
    if not edits:
        raise SystemExit("REFUSING: could not find HighriseApartment Apartment Lights to corrupt")
    for s, e, new in sorted(edits, key=lambda x: -x[0]):
        txt = txt[:s] + new + txt[e:]
    open(f, "w").write(txt)
    cmp_ = S.compare(f, u)
    fired = (cmp_["n_only_a"] > 4 or cmp_["classes_only_a"] != ["PEOPLE"]
             or cmp_["classes_only_b"] != ["PEOPLE"])
    return fired, cmp_


def main():
    deliverable_root, work = sys.argv[1], sys.argv[2]
    os.makedirs(work, exist_ok=True)
    ok, report = real_check(deliverable_root, work)
    fired, neg_cmp = negative_control(deliverable_root, work)
    print("REAL CHECK (F vs U, 4 cells): %s" % ("PASS" if ok else "FAIL"))
    for r in report:
        print("  %s: pass=%s only_a=%d only_b=%d classes_a=%s" % (
            r["cell"], r["pass"], r["compare_n_only_a"], r["compare_n_only_b"], r["classes_only_a"]))
    print("NEGATIVE CONTROL (F + stray lights edit, Tall/MTL): %s (only_a=%d classes_a=%s)" % (
        "FIRED (correctly caught)" if fired else "DID NOT FIRE -- CONTROL BROKEN",
        neg_cmp["n_only_a"], neg_cmp["classes_only_a"]))
    overall_ok = ok and fired
    print("OVERALL: %s" % ("PASS" if overall_ok else "FAIL"))
    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
