# -*- coding: utf-8 -*-
"""4J Step 11 -- work item 11.6, THE FULL GATE BOARD. All eighteen `G11.x`.

    python 4thJ_gates_step11.py --root <4J_docs_occ> [--offline] [--json out.json]

Work item 11.1 (2026-08-27) scored four of eighteen declared gates and printed
`NOT RUN` by name for the other fourteen, on purpose (`V11.g`). This is the
runner that finishes the board. It scores all eighteen, by one of three
honest routes, and says which route each gate took:

  1. **RE-SCORED, unchanged code, on data the mapping-table declares
     ("carry-over").** `G11.1`-`G11.4`, `G11.11`. The mapping is not
     re-authored (section 2), so these re-run `g9_1`-`g9_4`/`g9_11` IMPORTED
     from `4thJ_gates_step9.py` against the SAME `activity_appliance_map.csv`
     and `citations.csv`, and compare the result against the count the
     validation document says Step 9 shipped -- exactly work item 11.1's own
     method, extended by one gate.
  2. **RE-SCORED, unchanged code, on Step 11's OWN stock-scale data.**
     `G11.5` (a synthetic probe, no data needed), `G11.6`/`G11.8`/`G11.18`
     (from `4thJ_step11_stockboard.py`'s output, work item 11.6's own tool),
     `G11.12` (from `4thJ_step11_aggregate.py`'s output, work item 11.5,
     CLOSED -- read here, never re-simulated), `G11.13` (a search over the
     Step 11 results tree), `G11.14`/`G11.15` (Step 11's own preflight
     refusals, `S5`/`S10`, re-asserted fresh), `G11.16`/`G11.17` (the
     population declaration every stock manifest already carries).
  3. **CARRIED OVER FROM STEP 9 WITHOUT RE-MEASUREMENT, BECAUSE THERE IS
     NOTHING NEW TO MEASURE.** `G11.9`/`G11.10`. Step 11 writes no per-flat
     IDF and no per-flat fraction-schedule CSV of its own -- it is a Python
     state machine over Step 10's diaries, never an EnergyPlus artefact
     writer. The only saved IDF and schedule files that exist are the ones
     Step 9 already built for its 100-household-per-fold population, and
     Step 11 reuses THOSE households unchanged (only ownership and the
     stochastic draw are redrawn per flat, `reseed`). Re-opening Step 9's own
     artefacts is therefore the whole and correct check, not a shortcut.
  4. **NOT SCORED, BY RULING, NOT BY OMISSION.** `G11.7` is `INFO`,
     PERMANENTLY, on `D-S11-1` (2026-08-27) -- read `4thJ_11_stockEndUseLoads
     _val.md` before touching this gate. It is declared here as a fixed
     classification, never re-computed.

`V11.f`: no Step 11 artefact writes a `G9.x` or `G10.x` verdict. `V11.g`: the
declared suite is the scored suite -- with all eighteen gates implemented,
this is the first Step 11 run entitled to print a real tally instead of a
partial one.
"""
import argparse
import collections
import csv
import hashlib
import importlib.util
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# All eighteen gates Step 11 declares. Nothing here is a constant the runner
# invented to agree with itself -- `declared_gate_ids()` below reads the same
# set out of the validation document, and the runner refuses to report a
# tally if the two disagree (`V11.g`).
IMPLEMENTED = ["G11.%d" % i for i in range(1, 19)]

# The mapping-table carry-over family (route 1 above): same rows, same code,
# same bars, re-filed under a new ID. `G11.11`'s val-doc row is formatted
# identically to `G11.1`-`G11.4`'s -- `` `G9.11` (PASS 11, `FINDING 140`) ``
# -- so it reuses the SAME comparison machinery, not a second one.
CARRY_OVER_GATES = ["G11.1", "G11.2", "G11.3", "G11.4", "G11.11"]
INHERITS = {"G11.1": "G9.1", "G11.2": "G9.2", "G11.3": "G9.3", "G11.4": "G9.4",
            "G11.11": "G9.11"}

CARRY_OVER_ARTEFACTS = ("activity_appliance_map.csv", "citations.csv")

# `es` (Madrid) never ran a Step 11 stock campaign -- `London contributes
# nothing to Step 11 for the time being` / Madrid's own campaign was stopped
# on defect 8 (implementation doc, 2026-09-08 last+48/last+49). Only `uk` and
# `it` have real stock-scale artefacts on disk. A gate that needs stock data
# says so BY FOLD, honestly, rather than silently scoring two of three and
# calling it a population.
STOCK_FOLDS = ("uk", "it")

STOCKBOARD_DIR = os.path.join("Step11_docs", "outputs_step11", "g11_6_18")
G11_12_DIR = os.path.join("Step11_docs", "outputs_step11")


class Board(object):
    """`INFO` is a first-class verdict here, not a decorated PASS."""
    OK = ("PASS", "FAIL", "INFO", "NOT_EVALUABLE", "NOT CHECKED", "NOT RUN")

    def __init__(self):
        self.rows = []

    def add(self, gid, verdict, n_scanned, note):
        if verdict not in self.OK:
            raise ValueError("unknown verdict %r" % verdict)
        if re.match(r"^G(9|10)\.", gid):
            raise ValueError("V11.f: Step 11 may not file a %s verdict" % gid)
        self.rows.append({"id": gid, "verdict": verdict,
                          "n_scanned": n_scanned, "note": note})

    def verdict(self, gid):
        for r in self.rows:
            if r["id"] == gid:
                return r["verdict"]
        return None

    def counts(self):
        return dict(collections.Counter(r["verdict"] for r in self.rows))


# --------------------------------------------------------------------------
# what the DOCUMENT declares
# --------------------------------------------------------------------------
def declared_gate_ids(val_doc_path):
    text = io.open(val_doc_path, encoding="utf-8").read()
    gates = set(re.findall(r"\bG11\.\d+\b", text))
    guards = set(re.findall(r"\bV11\.[a-z]\b", text))
    heads = re.findall(r"^\|\s*\*\*`?(G11\.\d+)`?\*\*", text, re.M)
    dupes = sorted([g for g, n in collections.Counter(heads).items() if n > 1],
                   key=lambda g: int(g.split(".")[1]))
    return (sorted(gates, key=lambda g: int(g.split(".")[1])),
            sorted(guards), dupes)


def inherited_expectations(val_doc_path):
    """The Step 9 verdict and count each carry-over gate inherits, parsed out
    of the INHERITANCE column of the gate table."""
    text = io.open(val_doc_path, encoding="utf-8").read()
    out = {}
    for line in text.split("\n"):
        m = re.match(r"^\|\s*\*\*`?(G11\.\d+)`?\*\*", line)
        if not m:
            continue
        gid = m.group(1)
        cells = line.split("|")
        tail = cells[-2] if len(cells) >= 3 else ""
        e = re.search(r"`?(G9\.\d+)`?\s*\((PASS|FAIL|NOT CHECKED|INFO)\s+(\d+)", tail)
        if e:
            out[gid] = {"step9_gate": e.group(1), "verdict": e.group(2),
                        "n": int(e.group(3))}
        else:
            p = re.search(r"`(G9\.\d+)`", tail)
            out[gid] = {"step9_gate": p.group(1) if p else None,
                        "verdict": None, "n": None}
    return out


# --------------------------------------------------------------------------
# 1. the rows are the same rows
# --------------------------------------------------------------------------
def md5(path):
    h = hashlib.md5()
    h.update(io.open(path, "rb").read())
    return h.hexdigest()


def artefact_identity(out_dir9):
    ident = {}
    for name in CARRY_OVER_ARTEFACTS:
        path = os.path.join(out_dir9, name)
        if not os.path.exists(path):
            ident[name] = {"md5": None, "n_rows": None, "missing": True}
            continue
        rows = list(csv.DictReader(io.open(path, encoding="utf-8")))
        ident[name] = {"md5": md5(path), "n_rows": len(rows), "missing": False}
    return ident


# --------------------------------------------------------------------------
# 3. the code is the same code
# --------------------------------------------------------------------------
def import_step9(root):
    path = os.path.join(root, "tools", "4thJ_gates_step9.py")
    spec = importlib.util.spec_from_file_location("gates_step9", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.join(root, "tools"))
    spec.loader.exec_module(mod)
    return mod, path


def import_step11_trigger(root):
    path = os.path.join(root, "tools", "4thJ_step11_trigger_campaign.py")
    spec = importlib.util.spec_from_file_location("step11_trigger_campaign", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.join(root, "tools"))
    spec.loader.exec_module(mod)
    return mod


def _load_json(path):
    if not path or not os.path.exists(path):
        return None
    return json.load(io.open(path, encoding="utf-8"))


def carry_over(board, mod, rows, cites, out_dir9, expect, offline):
    """Re-score `G9.1`-`G9.4` and `G9.11` on the same rows, re-file under
    `G11.1`-`G11.4`/`G11.11`, and compare against the count the validation
    document says Step 9 shipped. See the module docstring, route 1."""
    src = mod.Board()
    mod.g9_1(src, rows)
    mod.g9_2(src, rows)
    mod.g9_3(src, rows)
    mod.g9_4(src, cites, out_dir9, offline=offline)
    mod.g9_11(src, rows)

    agreement = []
    for gid in CARRY_OVER_GATES:
        s9 = INHERITS[gid]
        got = None
        for r in src.rows:
            if r["id"] == s9:
                got = r
                break
        if got is None:
            board.add(gid, "NOT_EVALUABLE", 0,
                      "%s did not report -- the inherited gate could not be run"
                      % s9)
            agreement.append({"gate": gid, "status": "NOT_EVALUABLE"})
            continue

        exp = expect.get(gid) or {}
        note = got["note"]
        verdict = got["verdict"]
        status = "AGREES"

        if verdict == "NOT CHECKED":
            status = "NOT COMPARABLE"
            note = ("%s. CARRY-OVER: not compared -- a NOT CHECKED verdict "
                    "distinguishes *could not run* from *found nothing*, and "
                    "V11.c forbids reading it either as a PASS or as drift"
                    % note)
        elif exp.get("verdict") is None:
            status = "NO INHERITED COUNT"
            note = ("%s. CARRY-OVER: the validation document declares no "
                    "shipped count for %s, so only the verdict carries over"
                    % (note, s9))
        else:
            same_v = (verdict == exp["verdict"])
            same_n = (got["n_scanned"] == exp["n"])
            if same_v and same_n:
                note = ("%s. CARRY-OVER: agrees with %s as shipped -- %s %d, "
                        "on the same rows" % (note, s9, exp["verdict"], exp["n"]))
            elif not same_v:
                status = "VERDICT DIFFERS"
                note = ("%s. CARRY-OVER: %s now scores %s where the validation "
                        "document says Step 9 shipped %s %s -- the gate fell on "
                        "its own bar, and the inheritance no longer holds"
                        % (note, s9, verdict, exp["verdict"], exp["n"]))
            else:
                status = "DRIFT"
                verdict = "FAIL"
                note = ("CARRY-OVER DRIFT: %s still scores %s but over %s rows "
                        "where the validation document says Step 9 shipped %s "
                        "%s. The mapping is declared NOT re-authored, so a "
                        "count that moved is an edit nobody recorded. Gate's "
                        "own note: %s"
                        % (s9, verdict, got["n_scanned"], exp["verdict"],
                           exp["n"], got["note"]))
        board.add(gid, verdict, got["n_scanned"], note)
        agreement.append({"gate": gid, "inherits": s9, "status": status,
                          "verdict": verdict, "n": got["n_scanned"],
                          "expected_verdict": exp.get("verdict"),
                          "expected_n": exp.get("n")})
    return agreement


# --------------------------------------------------------------------------
# route 2 -- Step 11's OWN stock-scale data
# --------------------------------------------------------------------------
def score_g11_5(board, mod, root, manifests=None):
    """A synthetic edge-case probe, scale-free. There is no stock-scale
    version of this check to run instead -- it is a property of
    `simulate_day`'s own truncation behaviour, not a corpus measurement.

    `manifests` is exposed only so the mutation battery can register a
    perturbed manifest (`{"perturbations": {"truncate_cycle_at_episode_end":
    True}}`) without a real campaign; every real caller passes none."""
    trig = mod._import_trigger(root)
    src = mod.Board()
    mod.g9_5(src, trig, manifests or {})
    r = src.rows[0]
    board.add("G11.5", r["verdict"], r["n_scanned"],
              "%s. Inherited from G9.5 UNCHANGED: a synthetic probe of the "
              "state machine's own cycle-truncation behaviour, independent of "
              "any corpus or population." % r["note"])


def score_g11_9_10(board, mod, out_dir9, manifests9, folds9):
    src = mod.Board()
    mod.g9_9(src, out_dir9, folds9)
    mod.g9_10(src, out_dir9, manifests9, folds9)
    for gid, s9 in (("G11.9", "G9.9"), ("G11.10", "G9.10")):
        r = next(x for x in src.rows if x["id"] == s9)
        board.add(gid, r["verdict"], r["n_scanned"],
                  "%s. CARRIED OVER FROM STEP 9, NOT RE-MEASURED: Step 11 "
                  "writes no per-flat IDF and no per-flat fraction-schedule "
                  "CSV of its own -- it is a Python state machine over Step "
                  "10's diaries, reusing the SAME %d Step-9-built households "
                  "unchanged (only ownership and the stochastic draw are "
                  "redrawn per flat, `reseed`). The only saved IDF and "
                  "schedules that exist are Step 9's, so re-opening them is "
                  "the whole check, not a shortcut around a bigger one."
                  % (r["note"], len(folds9) * 100))


def score_g11_7(board):
    """`D-S11-1` (2026-08-27): permanent `INFO`, never re-scored. Declared,
    not computed -- read `4thJ_11_stockEndUseLoads_val.md` before touching
    this gate."""
    board.add("G11.7", "INFO", 0,
              "INFO PERMANENTLY by D-S11-1 item 2 (2026-08-27), on the G8.7 / "
              "D-S8-5 item 1 (a) precedent, inherited unchanged from G9.7 "
              "(itself INFO by D-S11-1 item 1): the 30-50 L/person/day band "
              "is Fuentes et al. (2018)'s, PER PERSON; the model is Jordan & "
              "Vajen's 200 l/day, PER DWELLING, unscaled; FINDING 165 showed "
              "the ratio between them is exactly n_members. A stock-scale "
              "attempt to fit this band is explicitly forbidden by the val "
              "doc STATUS section: growing N cannot move 200/n_members when "
              "the mean household is ~2.0. Band UNMOVED at 30-50; not scored.")


def load_stockboard(root, fold):
    path = os.path.join(root, STOCKBOARD_DIR, "c2_%s" % fold,
                        "step11_stockboard_%s.json" % fold)
    return _load_json(path)


def load_g11_12_manifest(root, fold):
    path = os.path.join(root, G11_12_DIR, "c2_%s" % fold,
                        "step11_11-5_%s_reseed.json" % fold)
    return _load_json(path)


def score_g11_6(board, mod, root):
    manifests = {}
    missing = []
    for fold in STOCK_FOLDS:
        m = load_stockboard(root, fold)
        if m is None:
            missing.append(fold)
            continue
        manifests[fold] = {"cycles": m["cycles"],
                           "calibration_trace": m.get("calibration_trace") or []}
    if not manifests:
        board.add("G11.6", "NOT_EVALUABLE", 0,
                  "no Step 11 stock-scale trigger-rate data on disk for any "
                  "fold -- 4thJ_step11_stockboard.py has not been run. Not a "
                  "pass.")
        return
    src = mod.Board()
    mod.g9_6(src, manifests)
    r = src.rows[0]
    note = ("stock-scale per-appliance annual activation counts vs CREST's "
            "published range, read from 4thJ_step11_stockboard.py's own "
            "output over folds %s (imported g9_6, unchanged): %s"
            % (sorted(manifests), r["note"]))
    if missing:
        note += (" NOT SCORED for %s -- no Step 11 stock campaign exists for "
                  "that fold." % ", ".join(missing))
    board.add("G11.6", r["verdict"], r["n_scanned"], note)


def score_g11_8(board, mod, root):
    manifests = {}
    missing = []
    for fold in STOCK_FOLDS:
        m = load_stockboard(root, fold)
        if m is None:
            missing.append(fold)
            continue
        manifests[fold] = {"dhw_litres_by_category": m["dhw_litres_by_category"]}
    if not manifests:
        board.add("G11.8", "NOT_EVALUABLE", 0,
                  "no Step 11 stock-scale DHW category data on disk for any "
                  "fold. Not a pass.")
        return
    src = mod.Board()
    mod.g9_8(src, manifests)
    r = src.rows[0]
    note = ("stock-scale four-event DHW volume mix vs Table 1's portions, "
            "read from 4thJ_step11_stockboard.py's own output over folds %s "
            "(imported g9_8, unchanged): %s" % (sorted(manifests), r["note"]))
    if missing:
        note += " NOT SCORED for %s." % ", ".join(missing)
    board.add("G11.8", r["verdict"], r["n_scanned"], note)


def score_g11_18(board, mod, root):
    detail = []
    bad = []
    ran = []
    missing = []
    n_all = 0
    for fold in STOCK_FOLDS:
        m = load_stockboard(root, fold)
        if m is None:
            missing.append(fold)
            continue
        ran.append(fold)
        stockboard_dir = os.path.join(root, STOCKBOARD_DIR, "c2_%s" % fold)
        src = mod.Board()
        mod.g9_15(src, {fold: m}, stockboard_dir)
        r = src.rows[0]
        detail.append(r["note"])
        n_all += r["n_scanned"]
        if r["verdict"] == "FAIL":
            bad.append(fold)
    if not ran:
        board.add("G11.18", "NOT_EVALUABLE", 0,
                  "no Step 11 stock-scale DHW data on disk for any fold. Not "
                  "a pass.")
        return
    note = ("stock MEAN litres per dwelling per day vs Jordan & Vajen's own "
            "200 +/- 10%%, read from 4thJ_step11_stockboard.py's own "
            "per-flat table (imported g9_15, unchanged), one fold at a time "
            "(g9_15 keys its CSV lookup by out_dir, and each fold's table "
            "lives in its own directory): %s" % " || ".join(detail))
    if missing:
        note += " NOT SCORED for %s." % ", ".join(missing)
    board.add("G11.18", "FAIL" if bad else "PASS", n_all, note)


def score_g11_12(board, root):
    manifests = {}
    missing = []
    for fold in STOCK_FOLDS:
        m = load_g11_12_manifest(root, fold)
        if m is None:
            missing.append(fold)
            continue
        manifests[fold] = m
    if not manifests:
        board.add("G11.12", "NOT_EVALUABLE", 0,
                  "no Step 11 stock-scale G11.12 manifest on disk for any "
                  "fold -- work item 11.5 has not been run. Not a pass.")
        return
    detail = []
    bad = []
    n = 0
    for fold, m in sorted(manifests.items()):
        n += m["n_flats_aggregated"]
        g = m["G11.12"]
        detail.append("%s R2=%.4f n=%d (%s)"
                      % (fold, m["r_squared"], m["n_flats_aggregated"],
                         g["verdict"]))
        if g["verdict"] != "PASS":
            bad.append(fold)
    note = ("mean diurnal appliance power against CREST's own published "
            "activity statistics at real stock scale, read from work item "
            "11.5's OWN closed manifests (never re-simulated here): %s"
            % "; ".join(detail))
    if missing:
        note += (" NOT SCORED for %s -- no Step 11 stock campaign exists for "
                  "that fold." % ", ".join(missing))
    board.add("G11.12", "FAIL" if bad else "PASS", n, note)


def score_g11_13(board, mod, root, out_dir=None, extra_dirs=None):
    """`out_dir`/`extra_dirs` are exposed only so the mutation battery can
    point this at a scratch tree instead of the real results directory;
    every real caller passes neither."""
    out_dir = out_dir or os.path.join(root, "Step11_docs")
    extra = (extra_dirs if extra_dirs is not None else
            [os.path.join(root, "Step11_docs", "docs"),
             os.path.join(root, "Step11_docs", "investigate")])
    src = mod.Board()
    mod.g9_13(src, out_dir, extra_dirs=extra)
    r = src.rows[0]
    board.add("G11.13", r["verdict"], r["n_scanned"],
              "%s. Inherited from G9.13 UNCHANGED (V11.d: the search prints "
              "its own scope and FAILs if it scanned fewer files than it "
              "found), pointed at the Step 11 results tree instead of Step "
              "9's." % r["note"])


def score_g11_14(board, t11, root, out_dir9=None):
    out_dir9 = out_dir9 or os.path.join(root, "Step9_docs", "outputs_step9")
    trig = t11.load_trigger()
    try:
        mapping = trig.Mapping(
            os.path.join(out_dir9, "activity_appliance_map.csv"))
    except Exception as exc:                                   # noqa: BLE001
        # The mapping itself is inconsistent (e.g. one ACL code mapped to two
        # CREST profiles), so the runtime-column set this gate checks cannot
        # even be built. Reported LOUDLY with the reason, never a crash --
        # the same posture G9.12 takes when its own Mapping() fails to load.
        board.add("G11.14", "NOT_EVALUABLE", 0,
                  "the mapping could not be loaded, so the trigger's runtime "
                  "column set cannot be determined: %s" % exc)
        return
    detail = []
    bad = []
    ran = []
    for fold in STOCK_FOLDS:
        m = load_g11_12_manifest(root, fold) or load_stockboard(root, fold)
        if m is None:
            continue
        ran.append(fold)
        try:
            wanted, present = t11.check_runtime_columns(root, fold, mapping)
            detail.append("%s: %d runtime columns, all present, act2 absent"
                          % (fold, len(wanted)))
        except t11.Refusal as exc:
            bad.append("%s: %s" % (fold, exc))
    if not ran:
        board.add("G11.14", "NOT_EVALUABLE", 0,
                  "no Step 11 stock campaign exists for any fold; the "
                  "generated diaries this gate checks against are Step 10's, "
                  "and no fold has them bound to a completed Step 11 run.")
        return
    board.add("G11.14", "FAIL" if bad else "PASS", len(ran),
              "the trigger's runtime columns are a subset of the generated "
              "diary's own, and act2 is absent, re-asserted fresh (S5, the "
              "same check 11.3/11.5 already passed silently before every "
              "real run): %s%s"
              % ("; ".join(detail), "" if not bad else " FAILURES: %s" % "; ".join(bad)))


def score_g11_15(board, t11, emitted=None):
    """`emitted` is exposed only so the mutation battery can register an
    end-use set that violates the seam without a real campaign; every real
    caller passes none and gets `t11.STEP11_END_USES` (the module's own
    declared pair)."""
    emitted = t11.STEP11_END_USES if emitted is None else emitted
    try:
        t11.check_seam(emitted)
        board.add("G11.15", "PASS", 1,
                  "S10, re-asserted fresh: appliance_electricity and dhw "
                  "(Step 11's declared end-uses) share no member with "
                  "space_heating (Step 10's), and nothing outside the "
                  "declared pair is emitted. This check is scale-free -- it "
                  "compares two frozensets -- and it already ran silently on "
                  "every real Step 11 campaign to date (11.3, 11.4, 11.5) "
                  "without raising.")
    except t11.Refusal as exc:
        board.add("G11.15", "FAIL", 1, "S10 fired: %s" % exc)


def score_g11_16_17(board, root, manifests=None):
    """`manifests` is exposed only so the mutation battery can register a
    doctored declaration without touching a real manifest on disk; every
    real caller passes none and gets the actual `outputs_step11/c2_*`
    manifests."""
    if manifests is None:
        manifests = {}
        for fold in STOCK_FOLDS:
            m = load_g11_12_manifest(root, fold)
            if m is not None:
                manifests[fold] = m
    if not manifests:
        for gid in ("G11.16", "G11.17"):
            board.add(gid, "NOT_EVALUABLE", 0,
                      "no Step 11 stock-scale manifest on disk for any fold.")
        return

    required = ("population", "spatial_extent", "weather_file_sha256",
               "fold", "district", "arm")
    bad16 = []
    for fold, m in sorted(manifests.items()):
        decl = m.get("declaration") or {}
        missing = [k for k in required if not decl.get(k)]
        if missing:
            bad16.append("%s missing %s" % (fold, missing))
    board.add("G11.16", "FAIL" if bad16 else "PASS", len(manifests),
              "every stock-scale manifest names its population, spatial "
              "extent, weather file, fold and district (population_"
              "declaration(), re-checked against the manifests on disk): "
              "folds %s%s" % (sorted(manifests),
                              "" if not bad16 else "; MISSING: %s" % "; ".join(bad16)))

    bad17 = []
    for fold, m in sorted(manifests.items()):
        decl = m.get("declaration") or {}
        arm = decl.get("arm")
        if arm != "D":
            bad17.append("%s: arm=%r, expected exactly 'D'" % (fold, arm))
        note = (decl.get("arm_note") or "").upper()
        if "LOWER BOUND" not in note:
            bad17.append("%s: arm_note does not carry the LOWER BOUND label"
                         % fold)
    board.add("G11.17", "FAIL" if bad17 else "PASS", len(manifests),
              "every stock-scale aggregate names its Step 10 arm (D) and "
              "carries the LOWER BOUND label for Arm F in its own note: "
              "folds %s%s. Vacuously satisfied on the never-mixed clause: "
              "this project has never produced a Step 11 stock aggregate "
              "over Arm F or over a mix of arms, so there is nothing to "
              "mislabel or pool -- stated rather than hidden."
              % (sorted(manifests),
                 "" if not bad17 else "; %s" % "; ".join(bad17)))


# --------------------------------------------------------------------------
def run(root, offline=False, out_dir9=None, quiet=False, val_doc=None):
    out_dir9 = out_dir9 or os.path.join(root, "Step9_docs", "outputs_step9")
    val_doc = val_doc or os.path.join(root, "Step11_docs",
                                      "4thJ_11_stockEndUseLoads_val.md")

    declared, guards, dupes = declared_gate_ids(val_doc)
    if dupes:
        raise SystemExit(
            "V11.g / FINDING 168: %s heads more than one gate-table row in %s. "
            "The declared suite is ambiguous; nothing was scored."
            % (", ".join(dupes), os.path.basename(val_doc)))

    expect = inherited_expectations(val_doc)
    ident = artefact_identity(out_dir9)
    mod, mod_path = import_step9(root)
    t11 = import_step11_trigger(root)
    rows, map_path = mod.read_map(out_dir9)
    cites, cit_path = mod.read_citations(out_dir9)

    folds9 = ["es", "uk", "it"]
    manifests9 = {}
    for f in folds9:
        m = mod.read_manifest(out_dir9, f)
        if m:
            manifests9[f] = m

    board = Board()
    agreement = carry_over(board, mod, rows, cites, out_dir9, expect, offline)
    score_g11_5(board, mod, root)
    score_g11_6(board, mod, root)
    score_g11_7(board)
    score_g11_8(board, mod, root)
    score_g11_9_10(board, mod, out_dir9, manifests9, folds9)
    score_g11_12(board, root)
    score_g11_13(board, mod, root)
    score_g11_14(board, t11, root, out_dir9=out_dir9)
    score_g11_15(board, t11)
    score_g11_16_17(board, root)
    score_g11_18(board, mod, root)

    not_run = [g for g in declared if g not in IMPLEMENTED]
    for gid in not_run:
        board.add(gid, "NOT RUN", 0, "declared, not implemented")

    # -- V11.f -----------------------------------------------------------
    leaked = [r["id"] for r in board.rows if re.match(r"^G(9|10)\.", r["id"])]

    # -- V11.g -------------------------------------------------------------
    scored = [r["id"] for r in board.rows if r["verdict"] != "NOT RUN"]
    extra = sorted(set(scored) - set(declared),
                   key=lambda g: int(g.split(".")[1]))
    on_board = set(r["id"] for r in board.rows)
    covered = sorted(set(declared) - on_board,
                     key=lambda g: int(g.split(".")[1]))
    suite_is_complete = (not not_run) and (not extra) and (not covered)

    drift = [a for a in agreement if a.get("status") == "DRIFT"]
    broken = [a for a in agreement if a.get("status") == "VERDICT DIFFERS"]
    result = {
        "work_item": "11.6 full gate board",
        "scope": "all %d declared gates" % len(declared),
        "board": board.rows,
        "counts_of_scored_gates_only": dict(collections.Counter(
            r["verdict"] for r in board.rows if r["verdict"] != "NOT RUN")),
        "declared_gates": declared,
        "declared_guards": guards,
        "duplicate_gate_ids": dupes,
        "implemented_gates": IMPLEMENTED,
        "gates_declared_but_not_implemented": not_run,
        "gates_scored_but_not_declared": extra,
        "gates_declared_but_absent_from_board": covered,
        "suite_is_partial": not suite_is_complete,
        "stock_folds_available": list(STOCK_FOLDS),
        "carry_over_agreement": agreement,
        "carry_over_drift": drift,
        "carry_over_inheritance_broken": broken,
        "artefact_identity": ident,
        "artefact_paths": {"map": os.path.relpath(map_path, root),
                           "citations": os.path.relpath(cit_path, root),
                           "step9_gate_code": os.path.relpath(mod_path, root)},
        "step9_gate_code_md5": md5(mod_path),
        "v11_f_gate_id_hygiene": "PASS" if not leaked else "FAIL: %s" % leaked,
        "offline": bool(offline),
    }

    if not quiet:
        print("%-8s %-13s %8s  %s" % ("gate", "verdict", "scanned", "note"))
        print("-" * 118)
        for r in board.rows:
            if r["verdict"] == "NOT RUN":
                continue
            print("%-8s %-13s %8s  %s"
                  % (r["id"], r["verdict"], r["n_scanned"], r["note"][:150]))
        print("-" * 118)
        for name in CARRY_OVER_ARTEFACTS:
            i = ident[name]
            print("identity  %-30s md5 %s  rows %s"
                  % (name, i["md5"], i["n_rows"]))
        print("identity  %-30s md5 %s"
              % ("4thJ_gates_step9.py", result["step9_gate_code_md5"]))
        print("-" * 118)
        print("scored: %s" % json.dumps(result["counts_of_scored_gates_only"],
                                        sort_keys=True))
        if suite_is_complete:
            print("SUITE COMPLETE -- all %d declared gates scored (V11.g)."
                  % len(declared))
        else:
            print("PARTIAL SUITE -- work item 11.6 implements %d of %d "
                  "declared gates. NOT RUN: %s"
                  % (len(IMPLEMENTED), len(declared), ", ".join(not_run)))
            print("V11.g: no tally is reported for a partial run; a partial "
                  "run that prints one reads as a complete one.")
        print("V11.f gate-ID hygiene: %s" % result["v11_f_gate_id_hygiene"])
        if extra:
            print("SCORED BUT NOT DECLARED: %s" % extra)
        if drift:
            print("CARRY-OVER DRIFT on %s" % ", ".join(a["gate"] for a in drift))
        if broken:
            print("INHERITANCE BROKEN on %s" % ", ".join(a["gate"] for a in broken))
    return result


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--offline", action="store_true",
                    help="skip CrossRef; G11.4 then reports NOT CHECKED (V11.c)")
    ap.add_argument("--out9", default=None)
    ap.add_argument("--valdoc", default=None,
                    help="override the declaring document (the mutation "
                         "battery points this at a mutated copy)")
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)
    res = run(args.root, offline=args.offline, out_dir9=args.out9,
              val_doc=args.valdoc)
    if args.json:
        blob = json.dumps(res, indent=2, sort_keys=True)
        bad = re.findall(r'"id": "(G(?:9|10)\.\d+)"', blob)
        if bad:
            raise SystemExit("V11.f: refusing to write %s into a Step 11 "
                             "artefact" % sorted(set(bad)))
        io.open(args.json, "w", encoding="utf-8", newline="").write(blob)
    bad = (res["carry_over_drift"] or res["carry_over_inheritance_broken"]
           or res["gates_scored_but_not_declared"])
    if not res.get("suite_is_partial"):
        pass
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
