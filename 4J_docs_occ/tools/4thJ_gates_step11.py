# -*- coding: utf-8 -*-
"""4J Step 11 -- work item 11.1, THE CARRY-OVER AUDIT. `G11.1`-`G11.4` only.

    python 4thJ_gates_step11.py --root <4J_docs_occ> [--offline] [--json out.json]

Step 11 declares eighteen gates. FOUR of them are implemented here, and the
runner says so in those words rather than printing a suite tally -- `V11.g`:
the declared suite is the scored suite, and a partial run that prints a tally
reads as a complete one.

WHAT THIS AUDIT ACTUALLY ESTABLISHES, AND WHAT IT DOES NOT
----------------------------------------------------------
`Step11_docs/4thJ_11_stockEndUseLoads.md` section 2: *the mapping is not
re-authored*. `G11.1`-`G11.4` re-score THE SAME ROWS against THE SAME BARS.
Read carelessly that is a tautology -- same file, same code, same answer -- and
a gate that cannot fail is worth nothing. It is not a tautology, because the
audit asserts three things it could find false:

  1. THE ROWS ARE THE SAME ROWS. `activity_appliance_map.csv` and
     `citations.csv` are hashed and their md5s printed. A mapping edited
     between Step 9 and Step 11 is exactly the silent drift this audit exists
     to catch, and `citations.csv` HAS already changed once -- `D-S11-1`
     directive 1 added `FUENTES-2018` on 2026-08-27.
  2. THE BARS ARE THE SAME BARS. The expected verdict and count are read out
     of the INHERITANCE COLUMN of `Step11_docs/4thJ_11_stockEndUseLoads_val.md`
     -- from the document, never from a constant in this file, which would be
     written by the same hand as the runner and would agree with it. A re-score
     that disagrees with the inherited count is a FAIL, whatever the gate's own
     verdict says.
  3. THE CODE IS THE SAME CODE. `g9_1`-`g9_4` are IMPORTED from
     `4thJ_gates_step9.py` and re-filed under `G11.x` IDs, so a change to the
     Step 9 gate bodies moves this audit too. Re-implementing them here would
     have produced a second opinion, and a second opinion is not an inheritance.

It does NOT establish anything at stock scale. Nothing here is aggregated, no
building is simulated, and no Step 10 artefact is read. The four gates score a
mapping table, which is scale-free -- that is why 11.1 is the one Step 11 item
that can run before a cell is simulated.

`V11.f`: no Step 11 artefact writes a `G9.x` or `G10.x` verdict. Asserted on
the board AND on the serialised JSON before it is written.
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

# The four gates work item 11.1 covers. Everything else Step 11 declares is
# reported NOT RUN by name -- an unimplemented gate must be visible, not absent.
IMPLEMENTED = ["G11.1", "G11.2", "G11.3", "G11.4"]

# Which Step 9 gate each one inherits. The MAPPING is the inheritance; the
# THRESHOLD is read from the validation document, not from here.
INHERITS = {"G11.1": "G9.1", "G11.2": "G9.2", "G11.3": "G9.3", "G11.4": "G9.4"}

CARRY_OVER_ARTEFACTS = ("activity_appliance_map.csv", "citations.csv")


class Board(object):
    """`INFO` is a first-class verdict here, not a decorated PASS.

    `D-S11-1` made `G11.7` permanently `INFO` and `V11.b` was amended to say
    an `INFO` gate never fires at all. A board that folded `INFO` into `PASS`
    would report a gate that cannot fail as a gate that passed.
    """
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
    """Gate and guard IDs, read from the validation document.

    Returns (gates, guards, duplicate_rows). `duplicate_rows` is the repair for
    `FINDING 168`: on 2026-08-27 `G11.15` headed TWO gate-table rows at once --
    section D's pre-registered double-count gate and, for a few hours, the DHW
    arm `D-S11-2` added. A SET does not count a duplicate twice, so `V11.g`
    would have compared 17 declared against 17 scored and reported a match
    while one of the two gates went unscored forever. The census below is what
    the set comparison cannot see, and it runs before anything is scored.
    """
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
    of the INHERITANCE column of the gate table.

    `| **`G11.1`** ... | `G9.1` (PASS 61) |` -> ("PASS", 61).

    Read from the document on purpose. A constant in this file would be a
    number the runner's own author chose, and it would agree with the runner
    for that reason and no other.
    """
    text = io.open(val_doc_path, encoding="utf-8").read()
    out = {}
    for line in text.split("\n"):
        m = re.match(r"^\|\s*\*\*`?(G11\.\d+)`?\*\*", line)
        if not m:
            continue
        gid = m.group(1)
        cells = line.split("|")
        tail = cells[-2] if len(cells) >= 3 else ""
        e = re.search(r"`?(G9\.\d+)`?\s*\((PASS|FAIL|NOT CHECKED|INFO)\s+(\d+)\)", tail)
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


def carry_over(board, mod, rows, cites, out_dir9, expect, offline):
    """Re-score `G9.1`-`G9.4` on the same rows, re-file under `G11.1`-`G11.4`,
    and compare against the count the validation document says Step 9 shipped.

    The comparison is the audit. A gate returning PASS on a mapping that has
    silently lost half its rows is still PASS -- `G9.1` asks whether every
    load-bearing row names a table, and zero rows satisfy that vacuously. The
    inherited COUNT is what makes the drift visible, which is why a verdict
    match with a count mismatch is a FAIL here and not a footnote.
    """
    src = mod.Board()
    mod.g9_1(src, rows)
    mod.g9_2(src, rows)
    mod.g9_3(src, rows)
    mod.g9_4(src, cites, out_dir9, offline=offline)

    agreement = []
    for gid in IMPLEMENTED:
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
            # V11.c. The resolver did not run, so there is nothing to compare
            # and nothing to call a pass.
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
                # The gate fell on its OWN bar. Its own verdict stands and its
                # own note leads; the inheritance is reported as broken, not
                # substituted for the reason. Calling this "drift" would hide
                # a real gate failure behind a bookkeeping word.
                status = "VERDICT DIFFERS"
                note = ("%s. CARRY-OVER: %s now scores %s where the validation "
                        "document says Step 9 shipped %s %s -- the gate fell on "
                        "its own bar, and the inheritance no longer holds"
                        % (note, s9, verdict, exp["verdict"], exp["n"]))
            else:
                # Same verdict, different count. This is the case a verdict
                # check cannot see: twenty well-formed rows satisfy G11.1
                # exactly as 192 do, and the mapping is declared NOT
                # re-authored, so the difference is an edit nobody recorded.
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
def run(root, offline=False, out_dir9=None, quiet=False, val_doc=None):
    out_dir9 = out_dir9 or os.path.join(root, "Step9_docs", "outputs_step9")
    val_doc = val_doc or os.path.join(root, "Step11_docs",
                                      "4thJ_11_stockEndUseLoads_val.md")

    declared, guards, dupes = declared_gate_ids(val_doc)
    if dupes:
        # Refuse before scoring. A duplicate ID means the document asks for two
        # gates under one name and the set comparison below cannot see it.
        raise SystemExit(
            "V11.g / FINDING 168: %s heads more than one gate-table row in %s. "
            "The declared suite is ambiguous; nothing was scored."
            % (", ".join(dupes), os.path.basename(val_doc)))

    expect = inherited_expectations(val_doc)
    ident = artefact_identity(out_dir9)
    mod, mod_path = import_step9(root)
    rows, map_path = mod.read_map(out_dir9)
    cites, cit_path = mod.read_citations(out_dir9)

    board = Board()
    agreement = carry_over(board, mod, rows, cites, out_dir9, expect, offline)

    not_run = [g for g in declared if g not in IMPLEMENTED]
    for gid in not_run:
        board.add(gid, "NOT RUN", 0,
                  "declared, not implemented -- outside work item 11.1")

    # -- V11.f -----------------------------------------------------------
    leaked = [r["id"] for r in board.rows if re.match(r"^G(9|10)\.", r["id"])]

    # -- V11.g, stated as a PARTIAL, never as a tally ---------------------
    scored = [r["id"] for r in board.rows if r["verdict"] != "NOT RUN"]
    extra = sorted(set(scored) - set(declared),
                   key=lambda g: int(g.split(".")[1]))
    on_board = set(r["id"] for r in board.rows)
    covered = sorted(set(declared) - on_board,
                     key=lambda g: int(g.split(".")[1]))

    drift = [a for a in agreement if a.get("status") == "DRIFT"]
    broken = [a for a in agreement if a.get("status") == "VERDICT DIFFERS"]
    result = {
        "work_item": "11.1 carry-over audit",
        "scope": "G11.1-G11.4 only; Step 11 declares %d gates" % len(declared),
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
        "suite_is_partial": True,
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
        print("PARTIAL SUITE -- work item 11.1 implements %d of %d declared "
              "gates. NOT RUN: %s" % (len(IMPLEMENTED), len(declared),
                                      ", ".join(not_run)))
        print("V11.g: no tally is reported for Step 11; a partial run that "
              "prints one reads as a complete one.")
        print("V11.f gate-ID hygiene: %s" % result["v11_f_gate_id_hygiene"])
        if extra:
            print("SCORED BUT NOT DECLARED: %s" % extra)
        if drift:
            print("CARRY-OVER DRIFT on %s -- same verdict, different row "
                  "count, and the mapping is declared NOT re-authored"
                  % ", ".join(a["gate"] for a in drift))
        if broken:
            print("INHERITANCE BROKEN on %s -- the gate fell on its own bar; "
                  "the Step 9 verdict it inherits no longer holds"
                  % ", ".join(a["gate"] for a in broken))
        if not drift and not broken:
            print("CARRY-OVER: no drift; every compared gate reproduces the "
                  "count the validation document says Step 9 shipped.")
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
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
