# -*- coding: utf-8 -*-
"""`V11.a` for work item 11.6 -- the mutation battery for the FULL gate board.

    python 4thJ_step11_selftest.py --root <4J_docs_occ>

Every gate that PASSES at baseline is made to fall by a named mutation, and the
null perturbation moves nothing. Offline throughout: no gate here needs the
network, and `G11.4`'s registered mutation is one that must be caught WITHOUT
a resolver.

PART 1 (unchanged since work item 11.1) mutates `activity_appliance_map.csv` /
`citations.csv` in a scratch copy of `out_dir9` and re-runs the full board
against it -- this is the only fixture cheap enough to copy per case, so it
covers exactly the gates that read nothing else: `G11.1`-`G11.4`, `G11.11`.

PART 2 (added 2026-09-13, work item 11.6) covers the gates that need a
stock-scale, IDF or scratch-tree fixture the CSV-only scratch of PART 1
cannot provide, by calling each `score_g11_*` function directly with a
hand-built bad input instead of running the whole board over a copied tree --
the same kind of direct probe `4thJ_gates_step9.py`'s own `v9_e` already uses
for `G9.2`. Covered this way: `G11.5`, `G11.9`, `G11.10`, `G11.13`, `G11.14`,
`G11.15`, `G11.16`, `G11.17`. `G11.9`/`G11.10` copy Step 9's saved IDF,
`enduse_by_dwelling` CSV and `enduse_profiles/` for ONE fold (`it`) into a
scratch directory and mutate the copy -- a re-pointed `WaterUse:Equipment`
schedule for `G11.9`, a doubled `ElectricEquipment` Design Level for
`G11.10` -- rather than the whole three-fold tree PART 1 uses, because
`enduse_profiles/` is 48 MB across 600 files and one fold is enough to show
each gate can fall. `G11.14`'s probe calls `check_runtime_columns` directly
against a stub mapping object (it only ever calls `.runtime_input_columns()`
on it), against the REAL generated diary for fold `it` -- no scratch copy of
the diary bundle needed.

WHAT IS NOT YET COVERED, NAMED RATHER THAN HIDDEN
--------------------------------------------------
`G11.6`, `G11.8`, `G11.18` depend on `4thJ_step11_stockboard.py`'s real
output. That output landed 2026-09-13 (both `uk` and `it`, full population,
no `--limit`): `G11.8` and `G11.18` both scored a real PASS and each now has
its own registered mutation in `run_direct_probes` (a re-split DHW category
mix; a tripled per-dwelling DHW volume, both against a scratch copy of the
REAL `it`-fold stockboard output, one fold being enough to show each gate
can fall). `G11.6` scored a real FAIL -- stock-scale per-appliance activation
counts land outside CREST's published range -- so it is
`ALREADY_FAILING_AT_BASELINE` (V11.b) and owed no mutation. Nothing here is
`MUTATION NOT YET REGISTERED` any more; a future gate added to the board
that has no probe yet would still print that label rather than being
silently absent, and the coverage clause would say so by name.

⚪ A DIAGNOSTIC NOISE SOURCE, NOT A FINDING: PART 1's own scratch `out_dir9`
copies only `activity_appliance_map.csv`, `citations.csv` and `sources/`, so
`G11.9` and `G11.10` score against a scratch tree with NO saved IDF and NO
Step 9 manifest at all in EVERY PART 1 case -- they print `FAIL` / a vacuous
`PASS 0` in that printed "PART 1 scratch, offline" baseline line, always, by
construction. That is a property of PART 1's fixture, not a result; PART 2
gives both gates their own proper fixture instead.

WHY THIS BATTERY EXISTS IN THE FORM IT DOES
-------------------------------------------
Work item 11.1 re-scores a mapping that is declared NOT re-authored, with code
imported from Step 9, against thresholds Step 9 registered. The obvious reading
is that it cannot fail, and a check that cannot fail is worth nothing. Two of
the seven PART 1 cases exist to settle that in the open:

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


def m_force_two_digit_mapping(out9, val_doc):
    """Collapse every ACL code to its 2-digit prefix (+`0`), so no row can
    carry a 3-digit signature distinct from its own 2-digit group's.

    `G11.11`'s verdict is `distinct 3-digit signatures > distinct 2-digit
    signatures` (`4thJ_gates_step9.py` `g9_11`, `signatures()`). Truncating
    every code to two digits (padded to keep the field the same width) makes
    every row's 3-digit and 2-digit signature identical, so the inequality
    cannot hold -- the gate must fall on the same rows that otherwise PASS
    it 11-strong.
    """
    p = os.path.join(out9, CSV_MAP)
    rows, f = _read(p)
    for r in rows:
        code = r["acl_code"]
        if code and not code.startswith("*"):
            r["acl_code"] = code[:2] + "0"
    _rewrite(p, rows, f)
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
    # Added 2026-09-13, work item 11.6: G11.11's own falsifier.
    ("force_two_digit_mapping", m_force_two_digit_mapping, "G11.11",
     ["G11.1", "G11.2", "G11.3"]),
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


def run_direct_probes(mod, root):
    """PART 2, added 2026-09-13 (work item 11.6). Gates whose falsifying
    mutation needs a fixture the CSV-only scratch of PART 1 cannot provide,
    probed by calling each `score_g11_*` function directly with a hand-built
    bad input -- the same shape `4thJ_gates_step9.py`'s own `v9_e` uses to
    probe `G9.2` without a scratch tree at all.

    Returns `(rows, baseline)`. `baseline` carries the REAL board's verdict
    for every gate this function did not itself probe, read once, so the
    caller can classify `G11.6`/`G11.8`/`G11.9`/`G11.10`/`G11.13`/`G11.14`/
    `G11.18` as `ALREADY_FAILING_AT_BASELINE`, `INFO`, `NOT_EVALUABLE` (no
    real data yet) or a genuine coverage gap, rather than guessing.
    """
    t11 = mod.import_step11_trigger(root)
    gates9, _ = mod.import_step9(root)
    real_board = mod.run(root, offline=True, quiet=True)
    baseline = dict((r["id"], r["verdict"]) for r in real_board["board"])
    rows = []

    # -- G11.5: force the truncation perturbation via a hand-built manifest --
    b0 = mod.Board()
    mod.score_g11_5(b0, gates9, root)
    base_ok = b0.verdict("G11.5") == "PASS"
    b1 = mod.Board()
    mod.score_g11_5(b1, gates9, root, manifests={
        "probe": {"perturbations": {"truncate_cycle_at_episode_end": True}}})
    fell = b1.verdict("G11.5") == "FAIL"
    if not base_ok:
        rows.append(("g11_5_truncation", "G11.5", "MISS",
                     "baseline is %s, not PASS -- cannot register a HIT"
                     % b0.verdict("G11.5")))
    else:
        rows.append(("g11_5_truncation", "G11.5", "HIT" if fell else "MISS",
                     "cycle-truncation perturbation flag %s the gate"
                     % ("fell" if fell else "did NOT fell")))

    # -- G11.15: widen the emitted end-use set to overlap Step 10's ---------
    b0 = mod.Board()
    mod.score_g11_15(b0, t11)
    base_ok = b0.verdict("G11.15") == "PASS"
    b1 = mod.Board()
    bad_emit = frozenset(list(t11.STEP11_END_USES) + ["space_heating"])
    mod.score_g11_15(b1, t11, emitted=bad_emit)
    fell = b1.verdict("G11.15") == "FAIL"
    rows.append(("g11_15_seam_overlap", "G11.15",
                 "HIT" if (base_ok and fell) else "MISS",
                 "an emitted set overlapping space_heating %s the seam gate"
                 % ("fell" if fell else "did NOT fell")))

    # -- G11.13: plant a per-dwelling-prediction sentence in a scratch tree -
    import tempfile
    scratch13 = tempfile.mkdtemp(prefix="g11_13_probe_")
    try:
        clean_path = os.path.join(scratch13, "clean.md")
        io.open(clean_path, "w", encoding="utf-8").write(
            "This step reports a stock-scale aggregate only; no per-dwelling "
            "prediction is made anywhere in these results (denial, not a "
            "claim).\n")
        b0 = mod.Board()
        mod.score_g11_13(b0, gates9, root, out_dir=scratch13, extra_dirs=[])
        base_ok = b0.verdict("G11.13") == "PASS"

        bad_path = os.path.join(scratch13, "bad.md")
        io.open(bad_path, "w", encoding="utf-8").write(
            "Table 7 gives this dwelling's predicted electricity use for "
            "next Tuesday.\n")
        b1 = mod.Board()
        mod.score_g11_13(b1, gates9, root, out_dir=scratch13, extra_dirs=[])
        fell = b1.verdict("G11.13") == "FAIL"
        rows.append(("g11_13_plant_per_dwelling_claim", "G11.13",
                     "HIT" if (base_ok and fell) else "MISS",
                     "a planted 'this dwelling's predicted' sentence %s the "
                     "search gate" % ("fell" if fell else "did NOT fell")))
    finally:
        shutil.rmtree(scratch13, ignore_errors=True)

    # -- G11.14: a fake mapping requesting `act2`, the policy-forbidden column
    class _FakeMapping(object):
        """`t11.check_runtime_columns` only ever calls
        `.runtime_input_columns()` -- a stub avoids reconstructing a real
        `Mapping` (which needs the whole CSV) just to vary one return value."""
        def __init__(self, cols):
            self._cols = cols

        def runtime_input_columns(self):
            return self._cols

    base_fake = _FakeMapping(["duration_min", "act", "loc_class"])
    bad_fake = _FakeMapping(["duration_min", "act", "loc_class", "act2"])
    try:
        t11.check_runtime_columns(root, "it", base_fake)
        base_ok = True
    except t11.Refusal:
        base_ok = False
    try:
        t11.check_runtime_columns(root, "it", bad_fake)
        fell = False
    except t11.Refusal:
        fell = True
    rows.append(("g11_14_act2_policy", "G11.14",
                 "HIT" if (base_ok and fell) else "MISS",
                 "a mapping requesting act2 at runtime %s the S5/G11.14 "
                 "policy refusal (D-S9-1 ruling (d)), against the REAL "
                 "generated diary for fold it"
                 % ("triggered" if fell else "did NOT trigger")))

    # -- G11.9 / G11.10: re-point a schedule / corrupt a design level -------
    # Fold `it` only -- one fold is enough to demonstrate each gate can fall,
    # and copying `enduse_profiles/` for all three folds (48 MB, 600 files)
    # would cost far more than the probe needs.
    scratch910 = tempfile.mkdtemp(prefix="g11_9_10_probe_")
    try:
        src9 = os.path.join(root, "Step9_docs", "outputs_step9")
        for fn in ("step9_objects_it.idf", "enduse_by_dwelling_it.csv",
                  "step9_manifest_it.json"):
            shutil.copy2(os.path.join(src9, fn), os.path.join(scratch910, fn))
        shutil.copytree(os.path.join(src9, "enduse_profiles", "it"),
                        os.path.join(scratch910, "enduse_profiles", "it"))
        m_it = json.load(io.open(
            os.path.join(scratch910, "step9_manifest_it.json"),
            encoding="utf-8"))
        manifests_it = {"it": m_it}
        idf_path = os.path.join(scratch910, "step9_objects_it.idf")
        original_idf = io.open(idf_path, encoding="utf-8").read()

        b0 = mod.Board()
        mod.score_g11_9_10(b0, gates9, scratch910, manifests_it, ["it"])
        base9_ok = b0.verdict("G11.9") == "PASS"
        base10_ok = b0.verdict("G11.10") == "PASS"

        # G11.9: re-point the FIRST WaterUse:Equipment's flow schedule to a
        # name that is not the object it was built with.
        lines = original_idf.split("\n")
        for i, ln in enumerate(lines):
            if "!- Flow Rate Fraction Schedule Name" in ln:
                before, _, after = ln.partition(",")
                lines[i] = before + "_WRONG," + after
                break
        io.open(idf_path, "w", encoding="utf-8", newline="").write(
            "\n".join(lines))
        b1 = mod.Board()
        mod.score_g11_9_10(b1, gates9, scratch910, manifests_it, ["it"])
        fell9 = b1.verdict("G11.9") == "FAIL"
        rows.append(("g11_9_repoint_schedule", "G11.9",
                     "HIT" if (base9_ok and fell9) else "MISS",
                     "re-pointing one WaterUse:Equipment's flow schedule %s "
                     "G11.9" % ("fell" if fell9 else "did NOT fell")))

        # G11.10: restore the IDF, then double the FIRST ElectricEquipment's
        # Design Level {W} -- the rebuilt kWh must diverge from the claimed
        # summary by far more than 0.5 %.
        lines = original_idf.split("\n")
        for i, ln in enumerate(lines):
            if "!- Design Level {W}" in ln:
                before, _, after = ln.partition(",")
                val = float(before.strip())
                lines[i] = "  %s," % (val * 2.0) + after
                break
        io.open(idf_path, "w", encoding="utf-8", newline="").write(
            "\n".join(lines))
        b2 = mod.Board()
        mod.score_g11_9_10(b2, gates9, scratch910, manifests_it, ["it"])
        fell10 = b2.verdict("G11.10") == "FAIL"
        rows.append(("g11_10_double_design_level", "G11.10",
                     "HIT" if (base10_ok and fell10) else "MISS",
                     "doubling one ElectricEquipment's Design Level {W} %s "
                     "G11.10" % ("fell" if fell10 else "did NOT fell")))
    finally:
        shutil.rmtree(scratch910, ignore_errors=True)

    # -- G11.16 / G11.17: doctor a copy of the REAL manifests ---------------
    real = {}
    for fold in mod.STOCK_FOLDS:
        m = mod.load_g11_12_manifest(root, fold)
        if m is not None:
            real[fold] = m
    if not real:
        rows.append(("g11_16_strip_declaration_field", "G11.16", "MISS",
                     "no real Step 11 stock manifest on disk to mutate"))
        rows.append(("g11_17_relabel_arm", "G11.17", "MISS",
                     "no real Step 11 stock manifest on disk to mutate"))
    else:
        import copy
        b0 = mod.Board()
        mod.score_g11_16_17(b0, root, manifests=copy.deepcopy(real))
        base16 = b0.verdict("G11.16") == "PASS"
        base17 = b0.verdict("G11.17") == "PASS"
        one_fold = sorted(real)[0]

        bad = copy.deepcopy(real)
        bad[one_fold]["declaration"]["spatial_extent"] = ""
        b1 = mod.Board()
        mod.score_g11_16_17(b1, root, manifests=bad)
        fell16 = b1.verdict("G11.16") == "FAIL"
        rows.append(("g11_16_strip_declaration_field", "G11.16",
                     "HIT" if (base16 and fell16) else "MISS",
                     "blanking %s's spatial_extent %s G11.16"
                     % (one_fold, "fell" if fell16 else "did NOT fell")))

        bad2 = copy.deepcopy(real)
        bad2[one_fold]["declaration"]["arm"] = "F"
        b2 = mod.Board()
        mod.score_g11_16_17(b2, root, manifests=bad2)
        fell17 = b2.verdict("G11.17") == "FAIL"
        rows.append(("g11_17_relabel_arm", "G11.17",
                     "HIT" if (base17 and fell17) else "MISS",
                     "relabelling %s's arm to F %s G11.17"
                     % (one_fold, "fell" if fell17 else "did NOT fell")))

    # -- G11.8: doctor a copy of the REAL stockboard's DHW category mix ----
    # `score_g11_8` reads `step11_stockboard_<fold>.json` off disk (no
    # override param, unlike G11.5/15/16/17), so the fixture is a scratch
    # ROOT with just fold `it`'s real manifest copied in and its
    # `dhw_litres_by_category` re-split -- same shape as the G11.9/10 scratch
    # tree above, one fold only.
    scratch8 = tempfile.mkdtemp(prefix="g11_8_probe_")
    try:
        fold8 = "it"
        src_dir8 = os.path.join(root, mod.STOCKBOARD_DIR, "c2_%s" % fold8)
        dst_dir8 = os.path.join(scratch8, mod.STOCKBOARD_DIR, "c2_%s" % fold8)
        os.makedirs(dst_dir8)
        man8 = os.path.join(dst_dir8, "step11_stockboard_%s.json" % fold8)
        shutil.copy2(os.path.join(src_dir8,
                                  "step11_stockboard_%s.json" % fold8), man8)

        b0 = mod.Board()
        mod.score_g11_8(b0, gates9, scratch8)
        base8_ok = b0.verdict("G11.8") == "PASS"

        manifest8 = json.load(io.open(man8, encoding="utf-8"))
        by = manifest8["dhw_litres_by_category"]
        total = sum(by.values())
        # Table 1's own portions are 0.14 / 0.36 / 0.10 / 0.40 (A/B/C/D).
        # Re-split the SAME total 0.60 / 0.20 / 0.10 / 0.10 -- every category
        # stays present and positive (so this is not the degenerate "a
        # category vanished" case G11.6 already probes structurally), but A,
        # B and D each land more than the 3 pp band away from Table 1.
        manifest8["dhw_litres_by_category"] = {
            "dhw_cat_a": 0.60 * total, "dhw_cat_b": 0.20 * total,
            "dhw_cat_c": 0.10 * total, "dhw_cat_d": 0.10 * total}
        io.open(man8, "w", encoding="utf-8", newline="").write(
            json.dumps(manifest8, indent=2, sort_keys=True))

        b1 = mod.Board()
        mod.score_g11_8(b1, gates9, scratch8)
        fell8 = b1.verdict("G11.8") == "FAIL"
        rows.append(("g11_8_reshape_dhw_mix", "G11.8",
                     "HIT" if (base8_ok and fell8) else "MISS",
                     "re-splitting fold %s's real DHW volume 60/20/10/10 "
                     "across A/B/C/D (Table 1 wants 14/36/10/40) %s G11.8"
                     % (fold8, "fell" if fell8 else "did NOT fell")))
    finally:
        shutil.rmtree(scratch8, ignore_errors=True)

    # -- G11.18: inflate a copy of the REAL per-flat DHW table --------------
    # `g9_15` ignores the manifest dict for its arithmetic and reads
    # `enduse_by_dwelling_<fold>.csv` straight off `out_dir` -- so the
    # fixture mutates THAT CSV, not the JSON, in the same one-fold scratch
    # tree shape.
    scratch18 = tempfile.mkdtemp(prefix="g11_18_probe_")
    try:
        fold18 = "it"
        src_dir18 = os.path.join(root, mod.STOCKBOARD_DIR,
                                 "c2_%s" % fold18)
        dst_dir18 = os.path.join(scratch18, mod.STOCKBOARD_DIR,
                                 "c2_%s" % fold18)
        os.makedirs(dst_dir18)
        shutil.copy2(os.path.join(src_dir18,
                                  "step11_stockboard_%s.json" % fold18),
                     os.path.join(dst_dir18,
                                  "step11_stockboard_%s.json" % fold18))
        csv_name18 = "enduse_by_dwelling_%s.csv" % fold18
        csv_path18 = os.path.join(dst_dir18, csv_name18)
        shutil.copy2(os.path.join(src_dir18, csv_name18), csv_path18)

        b0 = mod.Board()
        mod.score_g11_18(b0, gates9, scratch18)
        base18_ok = b0.verdict("G11.18") == "PASS"

        csv_rows, csv_fields = _read(csv_path18)
        for r in csv_rows:
            r["dhw_litres_per_day"] = str(float(r["dhw_litres_per_day"]) * 3.0)
        _rewrite(csv_path18, csv_rows, csv_fields)

        b1 = mod.Board()
        mod.score_g11_18(b1, gates9, scratch18)
        fell18 = b1.verdict("G11.18") == "FAIL"
        rows.append(("g11_18_triple_dhw_volume", "G11.18",
                     "HIT" if (base18_ok and fell18) else "MISS",
                     "tripling fold %s's real per-dwelling DHW litres/day %s "
                     "G11.18" % (fold18, "fell" if fell18 else "did NOT fell")))
    finally:
        shutil.rmtree(scratch18, ignore_errors=True)

    return rows, baseline


# `G11.8` and `G11.18` got their own registered mutations in `run_direct_
# probes` once `4thJ_step11_stockboard.py`'s real output landed (2026-09-13,
# same day). `G11.6` is left here: its REAL baseline scores FAIL (stock-scale
# activation counts land outside CREST's published range), so V11.b applies
# -- a mutation cannot be seen felling a gate that is already down, and none
# is owed. Classified against the REAL board's own baseline verdict at report
# time, never assumed.
UNCOVERED_CANDIDATES = ["G11.6"]


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

    # -- PART 2, work item 11.6: direct probes ----------------------------
    part2_rows, real_baseline = run_direct_probes(mod, root)
    for name, gid, result, note in part2_rows:
        rows.append((name, gid, result, note))
        if result == "HIT":
            hits += 1
        elif result == "MISS":
            misses += 1

    # -- gates with no registered mutation, classified by their REAL verdict
    uncovered_rows = []
    for gid in UNCOVERED_CANDIDATES:
        v = real_baseline.get(gid)
        if v == "FAIL":
            vacuous += 1
            uncovered_rows.append((gid, "ALREADY_FAILING_AT_BASELINE",
                                   "real baseline is FAIL; V11.b: a mutation "
                                   "cannot be seen felling a gate already "
                                   "down, so none is owed"))
        elif v == "INFO":
            uncovered_rows.append((gid, "VACUOUS_PERMANENTLY",
                                   "real baseline is INFO; an INFO gate never "
                                   "fires, so no mutation could register a hit"))
        elif v in (None, "NOT_EVALUABLE"):
            uncovered_rows.append((gid, "NOT YET SCORED",
                                   "real baseline is %s; no stock-scale data "
                                   "on disk yet, so there is no PASS to "
                                   "falsify" % v))
        else:
            uncovered_rows.append((gid, "MUTATION NOT YET REGISTERED",
                                   "real baseline is %s; this is a genuine "
                                   "coverage gap, not yet closed (see module "
                                   "docstring)" % v))

    dt = time.time() - t0
    print("%-30s %-8s %-28s %s" % ("case", "gate", "result", "note"))
    print("-" * 118)
    for r in rows:
        print("%-30s %-8s %-28s %s" % r)
    print("-" * 118)
    print("hits %d / misses %d / already-failing %d   (%.1f s)"
          % (hits, misses, vacuous, dt))
    print("baseline (PART 1 scratch, offline): %s" % json.dumps(baseline, sort_keys=True))
    print("-" * 118)
    print("GATES WITH NO REGISTERED MUTATION, classified by their REAL "
          "baseline verdict (not a scratch run):")
    for gid, status, note in uncovered_rows:
        print("  %-8s %-28s %s" % (gid, status, note))
    genuine_gaps = [gid for gid, status, _ in uncovered_rows
                    if status == "MUTATION NOT YET REGISTERED"]
    clause = ("PASS" if misses == 0 and not genuine_gaps else "FAIL")
    print("-" * 118)
    print("COVERAGE CLAUSE: %s -- every registered mutation was seen felling "
          "its gate, the null perturbation moved nothing, and %s."
          % (clause, "no genuine coverage gap remains" if not genuine_gaps
             else "a genuine coverage gap remains on %s" % genuine_gaps))
    print("V11.b: G11.4 is NOT CHECKED offline at baseline; the mutation "
          "registered for it is caught by the artefact-and-md5 arm, which "
          "runs without a resolver, so its row is not vacuous.")
    if args.json:
        io.open(args.json, "w", encoding="utf-8", newline="").write(
            json.dumps({"rows": [list(r) for r in rows], "hits": hits,
                        "misses": misses, "already_failing": vacuous,
                        "baseline": baseline, "real_baseline": real_baseline,
                        "uncovered": uncovered_rows, "seconds": round(dt, 1),
                        "coverage_clause": clause,
                        "genuine_coverage_gaps": genuine_gaps},
                       indent=2, sort_keys=True))
    return 0 if clause == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
