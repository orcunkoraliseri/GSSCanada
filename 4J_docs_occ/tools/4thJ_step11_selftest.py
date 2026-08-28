# -*- coding: utf-8 -*-
"""`V11.a` for work item 11.1 -- the mutation battery for the carry-over audit.

    python 4thJ_step11_selftest.py --root <4J_docs_occ>

Every gate that PASSES at baseline is made to fall by a named mutation, and the
null perturbation moves nothing. Offline throughout: no gate here needs the
network, and `G11.4`'s registered mutation is one that must be caught WITHOUT
a resolver.

WHY THIS BATTERY EXISTS IN THE FORM IT DOES
-------------------------------------------
Work item 11.1 re-scores a mapping that is declared NOT re-authored, with code
imported from Step 9, against thresholds Step 9 registered. The obvious reading
is that it cannot fail, and a check that cannot fail is worth nothing. Two of
the seven cases below exist to settle that in the open:

  * `drop_rows_to_20` leaves every gate's OWN verdict at PASS -- twenty rows
    that all name a table satisfy `G11.1` exactly as 192 rows do -- and the
    audit still FAILS, on the inherited COUNT. That is the case that shows the
    audit detects mapping drift and not merely mapping badness.
  * `duplicate_gate_id` mutates the DECLARING DOCUMENT rather than the data,
    and the runner must refuse to score anything at all. This is `FINDING 168`
    made into a registered detector: `G11.15` really did head two gate-table
    rows on 2026-08-27, and a set comparison cannot see a duplicate.

`ALREADY_FAILING_AT_BASELINE` (`V11.b`) is reported, never counted as a hit.
`G11.4` is `NOT CHECKED` offline at baseline, which is neither a pass nor a
failure, so its row is reported `NOT_COMPARABLE_AT_BASELINE` unless its
mutation is one the offline path can still catch -- and the registered one is.
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

CSV_MAP = "activity_appliance_map.csv"
CSV_CIT = "citations.csv"


def load_runner(root):
    path = os.path.join(root, "tools", "4thJ_gates_step11.py")
    spec = importlib.util.spec_from_file_location("gates_step11", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.join(root, "tools"))
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------
# mutations. Each takes the scratch output directory and edits it in place.
# --------------------------------------------------------------------------
def _rewrite(path, rows, fields):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _read(path):
    with io.open(path, encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        return list(rd), rd.fieldnames


def m_null(out9, val_doc):
    return val_doc


def m_blank_source_table(out9, val_doc):
    p = os.path.join(out9, CSV_MAP)
    rows, f = _read(p)
    for r in rows:
        if r["end_use"] != "none" and r["source_table"].strip():
            r["source_table"] = ""
            break
    _rewrite(p, rows, f)
    return val_doc


def m_strip_validation_scale(out9, val_doc):
    p = os.path.join(out9, CSV_MAP)
    rows, f = _read(p)
    for r in rows:
        if r["validation_label"] == "VALIDATED":
            r["validation_scale"] = ""
            break
    _rewrite(p, rows, f)
    return val_doc


def m_strip_reasoning_and_citation(out9, val_doc):
    p = os.path.join(out9, CSV_MAP)
    rows, f = _read(p)
    for r in rows:
        if r["validation_label"] == "NOT VALIDATED":
            r["source_citation_key"] = ""
            r["reasoning"] = ""
            break
    _rewrite(p, rows, f)
    return val_doc


def m_citation_lose_artefact(out9, val_doc):
    """The DOI-less row loses its retrievable artefact.

    `G9.4` does not wave a report through for having no DOI -- it demands a
    file on disk and a recorded md5 instead. That arm runs offline, so this is
    the one citation mutation the battery can register without a resolver.
    """
    p = os.path.join(out9, CSV_CIT)
    rows, f = _read(p)
    for r in rows:
        if not (r.get("doi") or "").strip():
            r["artefact"] = "sources/this_file_does_not_exist.pdf"
            break
    _rewrite(p, rows, f)
    return val_doc


def m_drop_rows_to_20(out9, val_doc):
    """Silent mapping drift. Every surviving row is still well-formed."""
    p = os.path.join(out9, CSV_MAP)
    rows, f = _read(p)
    _rewrite(p, rows[:20], f)
    return val_doc


def m_duplicate_gate_id(out9, val_doc):
    """`FINDING 168` as a registered detector: give `G11.1` a second row."""
    text = io.open(val_doc, encoding="utf-8", newline="").read()
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("| **`G11.3`**"):
            lines[i] = ln.replace("| **`G11.3`**", "| **`G11.1`**", 1)
            break
    else:
        raise RuntimeError("could not find the G11.3 row to duplicate onto")
    copy = os.path.join(out9, "_selftest_val_doc.md")
    io.open(copy, "w", encoding="utf-8", newline="").write("\n".join(lines))
    return copy


# case name, mutation, gate that MUST fall, gates that must stay clean
CASES = [
    ("null", m_null, None, ["G11.1", "G11.2", "G11.3"]),
    ("blank_source_table", m_blank_source_table, "G11.1", ["G11.2", "G11.3"]),
    ("strip_validation_scale", m_strip_validation_scale, "G11.2",
     ["G11.1", "G11.3"]),
    ("strip_reasoning_and_citation", m_strip_reasoning_and_citation, "G11.3",
     ["G11.1", "G11.2"]),
    # G11.4 is NOT CHECKED offline at baseline. It is listed as the gate that
    # must fall because this mutation is caught by the arm that runs offline --
    # the artefact-and-md5 clause - so the row is a genuine hit, not a vacuous
    # one. It is the ONLY G11.4 mutation this battery may register offline.
    ("citation_lose_artefact", m_citation_lose_artefact, "G11.4",
     ["G11.1", "G11.2", "G11.3"]),
    # The anti-tautology case: nothing is malformed, the count moved.
    ("drop_rows_to_20", m_drop_rows_to_20, "G11.1", []),
    # Mutates the DOCUMENT. The runner must refuse to score at all.
    ("duplicate_gate_id", m_duplicate_gate_id, "REFUSE", []),
]


def run_case(mod, root, work, val_doc_src, out9_src, name, mutate):
    out9 = os.path.join(work, name)
    if os.path.exists(out9):
        shutil.rmtree(out9)
    os.makedirs(out9)
    for fn in (CSV_MAP, CSV_CIT):
        shutil.copy2(os.path.join(out9_src, fn), os.path.join(out9, fn))
    src_sources = os.path.join(out9_src, "sources")
    if os.path.isdir(src_sources):
        shutil.copytree(src_sources, os.path.join(out9, "sources"))
    val_doc = mutate(out9, val_doc_src)
    try:
        res = mod.run(root, offline=True, out_dir9=out9, quiet=True,
                      val_doc=val_doc)
    except SystemExit as exc:
        return {"refused": True, "why": str(exc)}
    return {"refused": False, "res": res}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--work", default=None)
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)
    root = args.root
    work = args.work or os.path.join(root, "Step11_docs", "_selftest_work")
    if not os.path.exists(work):
        os.makedirs(work)
    out9_src = os.path.join(root, "Step9_docs", "outputs_step9")
    val_doc_src = os.path.join(root, "Step11_docs",
                               "4thJ_11_stockEndUseLoads_val.md")

    mod = load_runner(root)
    t0 = time.time()

    base = run_case(mod, root, work, val_doc_src, out9_src, "_baseline", m_null)
    assert not base["refused"], base
    baseline = dict((r["id"], r["verdict"]) for r in base["res"]["board"]
                    if r["verdict"] != "NOT RUN")

    hits, misses, vacuous, rows = 0, 0, 0, []
    for name, mutate, must_fall, must_stay in CASES:
        out = run_case(mod, root, work, val_doc_src, out9_src, name, mutate)

        if must_fall == "REFUSE":
            ok = out["refused"]
            rows.append((name, "-", "HIT" if ok else "MISS",
                         "the runner refused to score: %s"
                         % out["why"].split(".")[0] if ok else
                         "THE RUNNER SCORED A DOCUMENT DECLARING ONE ID TWICE"))
            hits += 1 if ok else 0
            misses += 0 if ok else 1
            continue

        if out["refused"]:
            rows.append((name, must_fall or "-", "MISS",
                         "the runner refused unexpectedly: %s" % out["why"]))
            misses += 1
            continue

        got = dict((r["id"], r["verdict"]) for r in out["res"]["board"]
                   if r["verdict"] != "NOT RUN")

        if must_fall is None:                       # the null perturbation
            moved = sorted(g for g in baseline if got.get(g) != baseline[g])
            ok = not moved
            rows.append((name, "-", "HIT" if ok else "MISS",
                         "nothing moved" if ok
                         else "the null perturbation MOVED %s" % moved))
            hits += 1 if ok else 0
            misses += 0 if ok else 1
            continue

        if baseline.get(must_fall) == "FAIL":
            vacuous += 1
            rows.append((name, must_fall, "ALREADY_FAILING_AT_BASELINE",
                         "V11.b: a mutation cannot be seen felling a gate that "
                         "is already down"))
            continue

        fell = got.get(must_fall) == "FAIL"
        dirty = sorted(g for g in must_stay if got.get(g) != baseline.get(g))
        ok = fell and not dirty
        why = []
        if not fell:
            why.append("%s did NOT fall (%s)" % (must_fall, got.get(must_fall)))
        if dirty:
            why.append("collateral movement on %s" % dirty)
        if ok:
            why.append("%s fell and its clean set stayed clean" % must_fall)
        rows.append((name, must_fall, "HIT" if ok else "MISS", "; ".join(why)))
        hits += 1 if ok else 0
        misses += 0 if ok else 1

    dt = time.time() - t0
    print("%-30s %-8s %-28s %s" % ("case", "gate", "result", "note"))
    print("-" * 118)
    for r in rows:
        print("%-30s %-8s %-28s %s" % r)
    print("-" * 118)
    print("hits %d / misses %d / already-failing %d   (%.1f s)"
          % (hits, misses, vacuous, dt))
    print("baseline: %s" % json.dumps(baseline, sort_keys=True))
    clause = ("PASS" if misses == 0 else "FAIL")
    print("COVERAGE CLAUSE: %s -- every gate this battery registers as "
          "falling was seen falling, and the null perturbation moved nothing."
          % clause)
    print("V11.b: G11.4 is NOT CHECKED offline at baseline; the mutation "
          "registered for it is caught by the artefact-and-md5 arm, which "
          "runs without a resolver, so its row is not vacuous.")
    if args.json:
        io.open(args.json, "w", encoding="utf-8", newline="").write(
            json.dumps({"rows": [list(r) for r in rows], "hits": hits,
                        "misses": misses, "already_failing": vacuous,
                        "baseline": baseline, "seconds": round(dt, 1),
                        "coverage_clause": clause}, indent=2, sort_keys=True))
    return 0 if misses == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
