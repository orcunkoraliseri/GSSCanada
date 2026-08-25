# -*- coding: utf-8 -*-
"""4J Step 9 -- the registered perturbation battery, with a coverage clause.

    python 4thJ_step9_selftest.py --root <4J_docs_occ> [--households 25]

Every perturbation in `Step9_docs/4thJ_09_enduseLoads_val.md`'s "EVERY GATE MUST
BE SEEN FAILING" table is run here, against a baseline built the same way.

Three rules this file is built around, all of them learned the hard way:

  * **A gate that already FAILs at baseline cannot be demonstrated by a
    perturbation aimed at it.** Those cases are reported as
    `ALREADY_FAILING_AT_BASELINE`, never as a hit. Counting them would describe
    the battery as larger than it is.
  * **The coverage clause is not optional.** Every gate that PASSes at baseline
    is cross-tabbed against every perturbation, and the probe FAILs if any of
    them was never made to fall. A probe that checks only the gate each
    perturbation was named for reports on a subset it chose itself.
  * **The null perturbation must change nothing.** A gate that fails on
    unperturbed data is a gate nobody can read.

The battery runs on a REDUCED dwelling count by default: it is about gate
mechanics, not about the campaign, and the baseline it compares against is built
at the same reduced count so the comparison is like for like. The count used is
printed and stamped into the report.
"""
import argparse
import csv
import importlib.util
import io
import json
import os
import shutil
import sys
import time


def _load(root, name, mod):
    spec = importlib.util.spec_from_file_location(
        mod, os.path.join(root, "tools", name))
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.join(root, "tools"))
    spec.loader.exec_module(m)
    return m


# --------------------------------------------------------------------------
# file-level mutations
# --------------------------------------------------------------------------
def _rows(path):
    with io.open(path, encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        return list(r), r.fieldnames


def _write(path, rows, fields):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def strip_table_reference(out_dir):
    path = os.path.join(out_dir, "activity_appliance_map.csv")
    rows, fields = _rows(path)
    for r in rows:
        if r["end_use"] == "electricity":
            r["source_table"] = ""
            break
    else:
        raise RuntimeError("no electricity row to strip")
    _write(path, rows, fields)


def label_validated_without_scale(out_dir):
    path = os.path.join(out_dir, "activity_appliance_map.csv")
    rows, fields = _rows(path)
    for r in rows:
        if r["validation_label"] == "VALIDATED":
            r["validation_scale"] = ""
            break
    else:
        raise RuntimeError("no VALIDATED row to strip")
    _write(path, rows, fields)


def add_row_with_number_and_no_source(out_dir):
    path = os.path.join(out_dir, "activity_appliance_map.csv")
    rows, fields = _rows(path)
    probe = dict((f, "") for f in fields)
    probe.update({
        "row_id": "PERTURB", "acl_code": "999", "acl_label": "planted",
        "appliance_id": "planted_appliance", "appliance_name": "planted",
        "appliance_group": "planted", "end_use": "electricity",
        "p_appliance_given_activity": "0.5000", "rated_power_w": "1234",
        "standby_power_w": "0", "mean_cycle_length_min": "30",
        "restart_delay_min": "0", "cycles_per_year": "100",
        "ownership_share": "1.000", "occupancy_dependent": "1",
        "power_factor": "1.0", "in_default_dwelling": "1",
        "crest_activity_index": "1", "crest_activity_name": "cooking",
        # a number, and NOTHING to source it to
        "source_model": "", "source_citation_key": "", "source_table": "",
        "source_doi": "", "source_artefact": "", "source_artefact_md5": "",
        "validation_label": "NOT VALIDATED", "validation_scale": "none",
        "reasoning": "",
    })
    rows.append(probe)
    _write(path, rows, fields)


def miscite_widen(out_dir):
    """Cite Widen 2010 as 87(3):780-789 -- the exact error `FINDING 47` is about.

    The DOI stays correct, so a title-only test would still pass. Only the
    widened volume/issue/page/first-author test can see it.
    """
    path = os.path.join(out_dir, "citations.csv")
    rows, fields = _rows(path)
    rows.append({
        "key": "WIDEN-2010-MISCITED", "model": "Widen",
        "authors": "Widen, J.; Wackelgard, E.",
        "first_author_family": "Widén", "year": "2010",
        "title": "A high-resolution stochastic model of domestic activity "
                 "patterns and electricity demand",
        "container": "Applied Energy", "volume": "87", "issue": "3",
        "page": "780-789", "doi": "10.1016/j.apenergy.2009.11.006",
        "artefact": "", "artefact_origin": "", "artefact_licence": "",
        "table": "Table 1", "note": "PERTURBATION",
    })
    _write(path, rows, fields)


def collapse_map_to_two_digits(out_dir):
    path = os.path.join(out_dir, "activity_appliance_map.csv")
    rows, fields = _rows(path)
    for r in rows:
        if not r["acl_code"].startswith("*") and len(r["acl_code"]) == 3:
            r["acl_code"] = r["acl_code"][:2] + "0"
    _write(path, rows, fields)


def repoint_wateruse(out_dir, fold):
    """Re-point ONE `WaterUse:Equipment` at another dwelling's schedule and
    leave every value untouched. The value check sees nothing, which is the
    whole point."""
    path = os.path.join(out_dir, "step9_objects_%s.idf" % fold)
    text = io.open(path, encoding="utf-8").read()
    import re as _re
    uniq = []
    for m in _re.finditer(r"^\s*(HH_[A-Za-z0-9_]+_DHW),\s*!- Name\s*$",
                          text, _re.M):
        if m.group(1) not in uniq:
            uniq.append(m.group(1))
    if len(uniq) < 2:
        raise RuntimeError("need two dwellings to re-point between")
    victim, donor = uniq[0], uniq[1]
    marker = "  %s,                  !- Flow Rate Fraction Schedule Name" % victim
    if marker not in text:
        raise RuntimeError("could not find the flow-rate schedule line for %s"
                           % victim)
    text = text.replace(
        marker,
        "  %s,                  !- Flow Rate Fraction Schedule Name" % donor, 1)
    io.open(path, "w", encoding="utf-8", newline="").write(text)


def add_per_dwelling_figure(out_dir):
    io.open(os.path.join(out_dir, "results_note_PERTURB.md"), "w",
            encoding="utf-8", newline="").write(
        "# Results note\n\nFigure 4 shows the model's predicted load for a "
        "single dwelling over one week.\nThe model predicts the demand of this "
        "dwelling to within a few per cent.\n")


def add_act2_to_runtime_columns(out_dir, folds):
    for fold in folds:
        path = os.path.join(out_dir, "step9_manifest_%s.json" % fold)
        if not os.path.exists(path):
            continue
        m = json.load(io.open(path, encoding="utf-8"))
        m["runtime_input_columns"] = sorted(set(m["runtime_input_columns"])
                                            | {"act2"})
        io.open(path, "w", encoding="utf-8", newline="").write(
            json.dumps(m, indent=2, sort_keys=True))


# --------------------------------------------------------------------------
# the registered table
# --------------------------------------------------------------------------
# name, must_fail, must_stay_clean, kind, kwargs
CASES = [
    ("strip_table_reference", "G9.1", ["G9.2"], "file", {}),
    ("label_validated_no_scale", "G9.2", ["G9.1"], "file", {}),
    ("row_with_number_no_source", "G9.3", ["G9.1"], "file", {}),
    ("miscite_widen_87_3", "G9.4", ["G9.1"], "file", {}),
    ("truncate_cycle_at_episode_end", "G9.5", ["G9.6"], "run",
     {"truncate_cycle_at_episode_end": True}),
    ("double_one_trigger_probability", "G9.6", ["G9.5"], "run",
     {"double_trigger_appliance": "vacuum"}),
    ("scale_dhw_by_2", "G9.7", ["G9.8"], "run", {"dhw_scale": 2.0}),
    ("collapse_four_events_into_one", "G9.8", ["G9.7"], "run",
     {"collapse_dhw_events": True}),
    ("repoint_one_wateruse_equipment", "G9.9", ["G9.7"], "file", {}),
    ("drop_one_end_use_from_the_sum", "G9.10", ["G9.6"], "run",
     {"drop_end_use": "dhw"}),
    ("replace_mapping_with_two_digit", "G9.11", ["G9.10"], "file", {}),
    ("add_act2_to_runtime_inputs", "G9.14", ["G9.10", "G9.6"], "file", {}),
    ("zero_load_on_20pc_of_dwellings", "G9.12", ["G9.10"], "run",
     {"zero_load_share": 0.20}),
    ("add_per_dwelling_prediction", "G9.13", None, "file", {}),
    ("null_change_nothing", None, "ALL", "run", {}),
]

FILE_MUTATORS = {
    "strip_table_reference": lambda d, f: strip_table_reference(d),
    "label_validated_no_scale": lambda d, f: label_validated_without_scale(d),
    "row_with_number_no_source": lambda d, f: add_row_with_number_and_no_source(d),
    "miscite_widen_87_3": lambda d, f: miscite_widen(d),
    "repoint_one_wateruse_equipment": lambda d, f: repoint_wateruse(d, f[0]),
    "replace_mapping_with_two_digit": lambda d, f: collapse_map_to_two_digits(d),
    "add_act2_to_runtime_inputs": lambda d, f: add_act2_to_runtime_columns(d, f),
    "add_per_dwelling_prediction": lambda d, f: add_per_dwelling_figure(d),
}


def build_campaign(trig, root, folds, work, households, calibration_passes=2,
                   **kw):
    """One campaign into `work`.

    `verify_against_step8` is OFF here and only here: the battery draws a
    REDUCED household sample, which is deliberately not the 100 the campaign
    shipped, so the byte-for-byte check against Step 8's presence schedules
    cannot apply. The campaign run keeps it ON.

    `calibration_passes` is cut to 2 for the same reason -- the battery is about
    whether a gate can fall, and the baseline it compares against is built with
    the identical setting, so the comparison stays like for like.
    """
    for fold in folds:
        trig.run_fold(root, fold, "leg5", 2017, 1, households, 60, work,
                      200.0, verify_against_step8=False,
                      calibration_passes=calibration_passes, **kw)


def seed_dir(root, work, src_dir):
    if os.path.isdir(work):
        shutil.rmtree(work)
    os.makedirs(work)
    for name in ("activity_appliance_map.csv", "citations.csv",
                 "acl_to_crest_activity.csv", "mapping_provenance.md"):
        shutil.copy2(os.path.join(src_dir, name), os.path.join(work, name))
    shutil.copytree(os.path.join(src_dir, "sources"),
                    os.path.join(work, "sources"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--folds", default="es")
    ap.add_argument("--households", type=int, default=25)
    ap.add_argument("--work", default=None)
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)
    root = args.root
    folds = [f for f in args.folds.split(",") if f]
    src = os.path.join(root, "Step9_docs", "outputs_step9")
    work_root = args.work or os.path.join(src, "_selftest")
    trig = _load(root, "4thJ_step9_trigger.py", "step9_trigger")
    gates = _load(root, "4thJ_gates_step9.py", "step9_gates")

    t0 = time.time()
    # ---- baseline, at the same reduced dwelling count ----------------------
    base_dir = os.path.join(work_root, "baseline")
    seed_dir(root, base_dir, src)
    build_campaign(trig, root, folds, base_dir, args.households)
    baseline = gates.run(root, folds, out_dir=base_dir, quiet=True)
    base_verdict = dict((r["id"], r["verdict"]) for r in baseline["board"])

    results = []
    fell = dict((gid, []) for gid, v in base_verdict.items() if v == "PASS")
    for name, must_fail, must_clean, kind, kw in CASES:
        cdir = os.path.join(work_root, name)
        seed_dir(root, cdir, src)
        if kind == "run":
            build_campaign(trig, root, folds, cdir, args.households, **kw)
        else:
            build_campaign(trig, root, folds, cdir, args.households)
            FILE_MUTATORS[name](cdir, folds)
        got = gates.run(root, folds, out_dir=cdir, quiet=True)
        gv = dict((r["id"], r["verdict"]) for r in got["board"])

        for gid, v in gv.items():
            if base_verdict.get(gid) == "PASS" and v == "FAIL":
                fell.setdefault(gid, []).append(name)

        rec = {"case": name, "target": must_fail, "verdicts": gv}
        if must_fail is None:
            changed = sorted(g for g in gv
                             if gv[g] != base_verdict.get(g))
            rec["status"] = "OK" if not changed else "NULL_PERTURBATION_MOVED"
            rec["detail"] = ("nothing moved" if not changed
                            else "these gates changed verdict: %s" % changed)
        elif base_verdict.get(must_fail) != "PASS":
            rec["status"] = "ALREADY_FAILING_AT_BASELINE"
            rec["detail"] = ("%s is %s at baseline, so this perturbation "
                             "demonstrates nothing about it"
                             % (must_fail, base_verdict.get(must_fail)))
        elif gv.get(must_fail) == "FAIL":
            dirty = []
            for g in (must_clean or []):
                if g == "ALL":
                    continue
                if gv.get(g) != base_verdict.get(g):
                    dirty.append("%s moved %s -> %s"
                                 % (g, base_verdict.get(g), gv.get(g)))
            rec["status"] = "HIT" if not dirty else "HIT_BUT_COLLATERAL"
            rec["detail"] = ("%s fell and its clean set stayed clean" % must_fail
                             if not dirty else "; ".join(dirty))
        else:
            rec["status"] = "MISS"
            rec["detail"] = ("%s stayed %s under a perturbation registered to "
                             "fell it" % (must_fail, gv.get(must_fail)))
        results.append(rec)

    never_fell = sorted(g for g, cases in fell.items() if not cases)
    report = {
        "households": args.households,
        "folds": folds,
        "baseline_verdicts": base_verdict,
        "cases": results,
        "gates_passing_at_baseline": sorted(fell),
        "gates_never_seen_failing": never_fell,
        "coverage_clause": "PASS" if not never_fell else "FAIL",
        "n_hit": sum(1 for r in results if r["status"] == "HIT"),
        "n_miss": sum(1 for r in results if r["status"] == "MISS"),
        "n_already_failing": sum(1 for r in results
                                 if r["status"] == "ALREADY_FAILING_AT_BASELINE"),
        "seconds": round(time.time() - t0, 1),
    }
    print("%-34s %-8s %-28s %s" % ("case", "target", "status", "detail"))
    print("-" * 130)
    for r in results:
        print("%-34s %-8s %-28s %s"
              % (r["case"], r["target"] or "-", r["status"], r["detail"][:60]))
    print("-" * 130)
    print("baseline: %s" % json.dumps(
        dict((k, v) for k, v in sorted(base_verdict.items())), sort_keys=True))
    print("hits %d / misses %d / already-failing %d"
          % (report["n_hit"], report["n_miss"], report["n_already_failing"]))
    print("COVERAGE CLAUSE: %s%s"
          % (report["coverage_clause"],
             "" if not never_fell else
             " -- these gates PASS at baseline and nothing ever made them "
             "fall: %s" % never_fell))
    print("%.1f s, %d households, folds %s"
          % (report["seconds"], args.households, ",".join(folds)))
    if args.json:
        io.open(args.json, "w", encoding="utf-8", newline="").write(
            json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
