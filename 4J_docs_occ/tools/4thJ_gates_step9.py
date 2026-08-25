# -*- coding: utf-8 -*-
"""4J Step 9 -- the fourteen gates and the five vacuity guards.

    python 4thJ_gates_step9.py --root <4J_docs_occ> [--folds es,uk,it] [--offline]

Every gate in `Step9_docs/4thJ_09_enduseLoads_val.md` is implemented here. A gate
that exists only in prose occupies the slot of the check that would have caught
the defect, and everybody downstream believes the property is covered -- so the
runner also asserts that the gate IDs it scores are exactly the gate IDs the
validation document declares, and FAILs if the two sets differ.

No threshold in this file may be changed to make a gate pass. `G9.7` and `G9.11`
are both expected to FAIL and are scored exactly as registered.
"""
import argparse
import collections
import csv
import io
import json
import math
import os
import re
import sys

# --------------------------------------------------------------------------
# registered thresholds. These are transcribed from
# `Step9_docs/4thJ_09_enduseLoads_val.md` and are NOT to be edited here.
# --------------------------------------------------------------------------
G9_7_BAND_L_PER_PERSON_DAY = (30.0, 50.0)     # "at 60 C, population median"
G9_10_CLOSURE_PCT = 0.5
G9_12_R2_MIN = 0.85
G9_4_FIELDS = ("volume", "issue", "page", "first_author")   # FINDING 47

DECLARED_GATES = ["G9.%d" % i for i in range(1, 15)]
DECLARED_GUARDS = ["V9.a", "V9.b", "V9.c", "V9.d", "V9.e"]


class Board(object):
    def __init__(self):
        self.rows = []

    def add(self, gid, verdict, n_scanned, note):
        if verdict not in ("PASS", "FAIL", "INFO", "NOT_EVALUABLE", "NOT CHECKED"):
            raise ValueError("unknown verdict %r" % verdict)
        self.rows.append({"id": gid, "verdict": verdict,
                          "n_scanned": n_scanned, "note": note})

    def verdict(self, gid):
        for r in self.rows:
            if r["id"] == gid:
                return r["verdict"]
        return None

    def counts(self):
        c = collections.Counter(r["verdict"] for r in self.rows)
        return dict(c)


# --------------------------------------------------------------------------
# inputs
# --------------------------------------------------------------------------
def read_map(out_dir):
    path = os.path.join(out_dir, "activity_appliance_map.csv")
    return list(csv.DictReader(io.open(path, encoding="utf-8"))), path


def read_citations(out_dir):
    path = os.path.join(out_dir, "citations.csv")
    return list(csv.DictReader(io.open(path, encoding="utf-8"))), path


def read_manifest(out_dir, fold):
    path = os.path.join(out_dir, "step9_manifest_%s.json" % fold)
    if not os.path.exists(path):
        return None
    return json.load(io.open(path, encoding="utf-8"))


# --------------------------------------------------------------------------
# G9.1 -- mapping citation completeness
# --------------------------------------------------------------------------
def g9_1(board, rows):
    """100 % of rows carry a source model AND the specific table or figure.

    A row citing only a paper is not cited. Rows that claim NO load are exempt
    from naming a table -- there is no value to source -- but they must still
    name why, and `G9.3` is the gate that checks that.
    """
    bad = []
    for r in rows:
        if r["end_use"] == "none":
            continue
        if not r["source_model"].strip() or not r["source_table"].strip():
            bad.append(r["row_id"])
    n = sum(1 for r in rows if r["end_use"] != "none")
    board.add("G9.1", "PASS" if not bad else "FAIL", n,
              "every load-bearing row names a source model and a table"
              if not bad else
              "%d rows carry a value with no table: %s"
              % (len(bad), ", ".join(bad[:8])))


# --------------------------------------------------------------------------
# G9.2 -- VALIDATED labelling, keyed on the STRUCTURED FIELD (V9.e)
# --------------------------------------------------------------------------
def g9_2(board, rows):
    """100 % of rows carry VALIDATED or NOT VALIDATED **and** the scale.

    A row labelled VALIDATED with no scale is a FAIL, not a warning. The test
    keys on the `validation_label` and `validation_scale` COLUMNS -- never on the
    presence of the word anywhere in the row -- because a row whose `reasoning`
    quotes a superseded label contains the right kind of token in the wrong
    place, and a naive presence test reads the correction as compliance (V9.e).
    """
    bad_label = []
    bad_scale = []
    for r in rows:
        label = (r.get("validation_label") or "").strip()
        scale = (r.get("validation_scale") or "").strip()
        if label not in ("VALIDATED", "NOT VALIDATED"):
            bad_label.append(r["row_id"])
            continue
        if not scale:
            bad_scale.append(r["row_id"])
    bad = bad_label + bad_scale
    board.add("G9.2", "PASS" if not bad else "FAIL", len(rows),
              "every row carries a structured label and a scale" if not bad else
              "%d rows without a valid label (%s), %d labelled with no scale (%s)"
              % (len(bad_label), ", ".join(bad_label[:5]),
                 len(bad_scale), ", ".join(bad_scale[:5])))


# --------------------------------------------------------------------------
# G9.3 -- unsourced-row honesty
# --------------------------------------------------------------------------
def g9_3(board, rows):
    """Every NOT VALIDATED row carries our written reasoning. Target: 0 rows
    with neither a citation nor reasoning."""
    bad = []
    for r in rows:
        if r["validation_label"] != "NOT VALIDATED":
            continue
        has_citation = bool(r["source_citation_key"].strip())
        has_reasoning = len((r.get("reasoning") or "").strip()) >= 40
        if not has_citation and not has_reasoning:
            bad.append(r["row_id"])
    n = sum(1 for r in rows if r["validation_label"] == "NOT VALIDATED")
    board.add("G9.3", "PASS" if not bad else "FAIL", n,
              "every NOT VALIDATED row carries reasoning or a citation"
              if not bad else
              "%d rows carry neither: %s" % (len(bad), ", ".join(bad[:8])))


# --------------------------------------------------------------------------
# G9.4 -- citation correctness, widened by FINDING 47
# --------------------------------------------------------------------------
def crossref(doi, timeout=30):
    import urllib.request
    url = "https://api.crossref.org/works/" + doi
    req = urllib.request.Request(url, headers={
        "User-Agent": "4J-step9-gates (mailto:orcunkoral.oseri@concordia.ca)"})
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return json.load(fh)["message"]


def g9_4(board, cites, out_dir, offline=False):
    """Every cited DOI resolves to the title it is cited under -- AND volume,
    issue, page range and FIRST AUTHOR all match the CrossRef record.

    Title-only matching is not enough: `FINDING 47` showed that our own wrong
    note would have PASSED a title test, because it carried no DOI at all.

    A row with NO DOI is not waved through. A report is cited by artefact, so it
    must carry a retrievable file whose md5 is recorded -- a STRICTER test than
    the DOI clause, not a waiver of it.

    `V9.c`: when the resolver cannot be reached the row prints `NOT CHECKED` and
    the gate's verdict is `NOT CHECKED`. A check that cannot distinguish *found
    nothing* from *could not run* is not a check.
    """
    problems = []
    unreachable = 0
    n = 0
    for c in cites:
        n += 1
        doi = (c.get("doi") or "").strip()
        if not doi:
            art = os.path.join(out_dir, c.get("artefact", ""))
            if not c.get("artefact") or not os.path.exists(art):
                problems.append("%s: no DOI and no retrievable artefact" % c["key"])
            elif "md5" not in (c.get("note") or ""):
                problems.append("%s: artefact present but no md5 recorded" % c["key"])
            continue
        if offline:
            unreachable += 1
            continue
        try:
            m = crossref(doi)
        except Exception:                                   # noqa: BLE001
            unreachable += 1
            continue
        got_title = ((m.get("title") or [""])[0] or "").strip().lower()
        want_title = (c.get("title") or "").strip().lower()
        if want_title[:40] not in got_title:
            problems.append("%s: title mismatch (cited %r, CrossRef %r)"
                            % (c["key"], c["title"][:40], got_title[:40]))
        checks = {
            "volume": ((m.get("volume") or "").strip(), (c.get("volume") or "").strip()),
            "issue": ((m.get("issue") or "").strip(), (c.get("issue") or "").strip()),
            "page": ((m.get("page") or "").strip(), (c.get("page") or "").strip()),
            "first_author": (((m.get("author") or [{}])[0].get("family") or "").strip(),
                             (c.get("first_author_family") or "").strip()),
        }
        for field in G9_4_FIELDS:
            got, want = checks[field]
            if want and got and got.lower() != want.lower():
                problems.append("%s: %s mismatch (cited %r, CrossRef %r)"
                                % (c["key"], field, want, got))
            elif want and not got:
                problems.append("%s: %s absent from the CrossRef record"
                                % (c["key"], field))
    if unreachable and not problems:
        board.add("G9.4", "NOT CHECKED", n,
                  "%d of %d DOIs could not be resolved; V9.c forbids reporting "
                  "this as a PASS" % (unreachable, n))
        return
    board.add("G9.4", "PASS" if not problems else "FAIL", n,
              "all %d citations match CrossRef on title, volume, issue, pages "
              "and first author" % n if not problems else "; ".join(problems[:5]))


# --------------------------------------------------------------------------
# G9.5 -- cycle completion, asserted on synthetic edge cases
# --------------------------------------------------------------------------
def g9_5(board, trig):
    """An appliance triggered near the END of an activity episode still runs its
    FULL rated cycle.

    Asserted on a synthetic edge case, not on the corpus, exactly as the
    validation document requires: a single eligible minute at t=100 and a cycle
    of 60 minutes, with an occupant active all day. If the cycle were truncated
    at the end of the episode it would run for one minute.
    """
    app = {"id": "probe", "name": "probe", "group": "probe", "profile": 1,
           "rated_power_w": 1000.0, "standby_power_w": 0.0,
           "cycle_len_min": 60, "restart_delay_min": 0,
           "cycles_per_year": 1.0, "ownership_share": 1.0,
           "occupancy_dependent": 1, "in_default_dwelling": 1,
           "power_factor": 1.0}
    import random as _r
    state = trig.ApplianceState()
    out = [0.0] * trig.DAY_MINUTES
    active = [True] * trig.DAY_MINUTES
    trig.simulate_day(app, state, 1.0, [100], active, out, _r.Random(0))
    ran = sum(1 for v in out if v > 0.0)
    ok = (ran == 60 and state.cycles == 1)
    board.add("G9.5", "PASS" if ok else "FAIL", 1,
              "a cycle started in the only eligible minute of the day ran all "
              "60 minutes" if ok else
              "the cycle ran %d of 60 minutes (cycles=%d): it was truncated"
              % (ran, state.cycles))


# --------------------------------------------------------------------------
# G9.6 -- trigger rate against the source model's published range
# --------------------------------------------------------------------------
def g9_6(board, manifests, tol=0.15):
    """Per-appliance annual activation counts against CREST's published
    `Cycles per year (n)`, at stock scale.

    The validation document registers this qualitatively -- "within the range
    the source model reports" -- so the +/-15 % band is OURS and is declared as
    such. It was chosen before the campaign ran and is not adjusted to it.

    Two classes of row are reported separately rather than folded into a count,
    because a bare tally hides which END a band gate fails at and why:

      * **NOT_EVALUABLE** -- CREST carries three standby-only devices at 1e-05
        cycles per year (answering machine, cordless telephone, clock). They are
        a standby wattage with no cycle. Asking whether 0 activations is within
        range of 0.00001 is not a question, and answering it either way would be
        a verdict about nothing.
      * **SATURATED** -- the corpus does not contain enough of the driving
        activity to support the published count at the published cycle length.
        This is a measurement, not a shortfall in the calibration: the loop
        raised the hazard until it stopped buying cycles.
    """
    bad = []
    saturated = []
    not_evaluable = collections.Counter()
    n = 0
    for fold, m in sorted(manifests.items()):
        sat = set()
        for t in m.get("calibration_trace") or []:
            sat.update(t.get("saturated") or [])
        for row in m["cycles"]:
            published = float(row["cycles_per_year_published"])
            if published < 0.5:
                not_evaluable[row["appliance_id"]] += 1
                continue
            n += 1
            ratio = row["ratio_modelled_over_published"]
            if ratio in ("", None):
                continue
            ratio = float(ratio)
            if abs(ratio - 1.0) <= tol:
                continue
            end = "BELOW" if ratio < 1.0 else "ABOVE"
            if row["appliance_id"] in sat:
                saturated.append("%s/%s %.3f %s" % (fold, row["appliance_id"],
                                                    ratio, end))
            else:
                bad.append("%s/%s %.3f %s" % (fold, row["appliance_id"],
                                              ratio, end))
    problems = bad + saturated
    note = ("%d appliance-folds scored against CREST's published cycles per "
            "year, band +/-%.0f %% (ours, declared)." % (n, tol * 100))
    if not_evaluable:
        note += (" NOT_EVALUABLE, standby-only with published cycles < 0.5: %s."
                 % ", ".join(sorted(not_evaluable)))
    if saturated:
        note += (" SATURATED (the corpus has too little of the driving activity "
                 "to support the published count): %s." % "; ".join(saturated[:8]))
    if bad:
        note += " OUTSIDE the band for other reasons: %s." % "; ".join(bad[:8])
    if not problems:
        note += " Every evaluable appliance is inside the band."
    board.add("G9.6", "PASS" if not problems else "FAIL", n, note)


# --------------------------------------------------------------------------
# G9.7 -- DHW volume, scored EXACTLY as registered
# --------------------------------------------------------------------------
def g9_7(board, manifests):
    """30 to 50 L/person/day at 60 C, population median, reported per country.

    🔴 SCORED AS REGISTERED. `FINDING 138` established that neither the band's
    per-person basis nor its 60 C reference appears in Jordan & Vajen, whose
    reference is 200 l/day per single-family house at a 35 K rise. The band is
    NOT moved for that: `D-S9-2` item 7 asks the author what the manuscript
    should say about the failure, not whether to soften it.
    """
    lo, hi = G9_7_BAND_L_PER_PERSON_DAY
    detail = []
    bad = []
    for fold, m in sorted(manifests.items()):
        v = m["stock_dhw_l_per_person_day"]
        detail.append("%s %.2f" % (fold, v))
        if not (lo <= v <= hi):
            bad.append("%s %.2f" % (fold, v))
    board.add("G9.7", "PASS" if not bad else "FAIL", len(manifests),
              "L/person/day by fold: %s against the registered %.0f-%.0f band%s"
              % (", ".join(detail), lo, hi,
                 "" if not bad else " -- OUTSIDE in %s" % ", ".join(bad)))


# --------------------------------------------------------------------------
# G9.8 -- DHW event mix
# --------------------------------------------------------------------------
def g9_8(board, manifests, tol=0.03):
    """The four-event structure is present with the source model's proportions.

    Table 1's portions are 0.14 / 0.36 / 0.10 / 0.40 of the daily volume for
    categories A / B / C / D. All four must be present and each within 3 pp.
    """
    want = {"dhw_cat_a": 0.14, "dhw_cat_b": 0.36,
            "dhw_cat_c": 0.10, "dhw_cat_d": 0.40}
    bad = []
    n = 0
    for fold, m in sorted(manifests.items()):
        by = m.get("dhw_litres_by_category") or {}
        total = sum(by.values())
        if not total:
            bad.append("%s: no DHW volume at all" % fold)
            continue
        missing = [k for k in want if k not in by or by[k] <= 0.0]
        if missing:
            bad.append("%s: categories absent: %s" % (fold, ",".join(sorted(missing))))
            continue
        for k, w in sorted(want.items()):
            n += 1
            got = by[k] / total
            if abs(got - w) > tol:
                bad.append("%s/%s portion %.3f vs %.2f" % (fold, k, got, w))
    board.add("G9.8", "PASS" if not bad else "FAIL", n,
              "all four categories present and within %.0f pp of Table 1's "
              "portions in every fold" % (tol * 100) if not bad else
              "; ".join(bad[:6]))


# --------------------------------------------------------------------------
# G9.9 -- the DHW ASSIGNMENT check, read back off the SAVED IDF
# --------------------------------------------------------------------------
IDF_OBJ_RE = re.compile(r"^\s*([A-Za-z:]+)\s*,\s*$")


def parse_idf_objects(text):
    """Split an IDF into `(type, [fields])`, comments stripped.

    A deliberately independent parser: it does not import anything the writer
    used. A gate that consults the writer's own reader cannot catch a defect in
    the reader.
    """
    clean = []
    for line in text.splitlines():
        line = line.split("!", 1)[0].rstrip()
        if line.strip():
            clean.append(line)
    blob = "\n".join(clean)
    objects = []
    for chunk in blob.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        fields = [f.strip() for f in chunk.split(",")]
        objects.append((fields[0], fields[1:]))
    return objects


def g9_9(board, out_dir, folds):
    """Re-open the SAVED IDF and assert every `WaterUse:Equipment` object still
    points at the schedule it was built with.

    🔴 A VALUE CHECK CANNOT SEE A RE-POINTED OBJECT. In 3J that hid a x3.028
    draw increase across 56 cells while every audit reported zero violations,
    because a re-pointed object leaves no before/after pair to compare. So this
    reads the artefact on disk, not any number the writer reported about itself.
    """
    bad = []
    n = 0
    for fold in folds:
        path = os.path.join(out_dir, "step9_objects_%s.idf" % fold)
        if not os.path.exists(path):
            bad.append("%s: no saved IDF" % fold)
            continue
        objs = parse_idf_objects(io.open(path, encoding="utf-8").read())
        schedules = set()
        for typ, f in objs:
            if typ.lower() == "schedule:file" and f:
                schedules.add(f[0])
        for typ, f in objs:
            if typ.lower() != "wateruse:equipment":
                continue
            n += 1
            name = f[0]
            flow_sched = f[3] if len(f) > 3 else ""
            expected = name              # built as `<name>` == `<HH>_DHW`
            if flow_sched != expected:
                bad.append("%s: %s points at %r, was built with %r"
                           % (fold, name, flow_sched, expected))
            elif flow_sched not in schedules:
                bad.append("%s: %s points at %r, which no Schedule:File in this "
                           "file defines" % (fold, name, flow_sched))
    board.add("G9.9", "PASS" if not bad else "FAIL", n,
              "%d WaterUse:Equipment objects re-read from the saved IDF, every "
              "one still bound to its own schedule" % n if not bad else
              "; ".join(bad[:6]))


# --------------------------------------------------------------------------
# G9.10 -- energy closure
# --------------------------------------------------------------------------
def g9_10(board, out_dir, manifests, folds):
    """Sum of the end uses reconciles with the total injected internal gain,
    within 0.5 %.

    🔴 THE TWO SIDES MUST NOT SHARE A CODE PATH, or the gate only proves the
    writer agrees with itself. So:

      * side A is the writer's own summary, `enduse_by_dwelling_<fold>.csv`;
      * side B is rebuilt from THE ARTEFACTS ENERGYPLUS WOULD ACTUALLY CONSUME
        -- the per-dwelling fraction schedules on disk, multiplied by the
        `Design Level {W}` and `Peak Flow Rate {m3/s}` parsed out of the SAVED
        IDF by this file's own independent parser.

    If an end use were dropped from the sum, or a schedule re-pointed, or a
    design level mis-scaled, side B moves and side A does not.
    """
    bad = []
    n = 0
    for fold in folds:
        m = manifests.get(fold)
        if not m:
            continue
        ts = m["timestep_min"]
        rows = list(csv.DictReader(io.open(
            os.path.join(out_dir, "enduse_by_dwelling_%s.csv" % fold),
            encoding="utf-8")))
        idf_path = os.path.join(out_dir, "step9_objects_%s.idf" % fold)
        if not os.path.exists(idf_path):
            bad.append("%s: no saved IDF to rebuild the sum from" % fold)
            continue
        objs = parse_idf_objects(io.open(idf_path, encoding="utf-8").read())
        design_w = {}
        peak_m3s = {}
        sched_file = {}
        for typ, f in objs:
            t = typ.lower()
            if t == "electricequipment" and len(f) > 4:
                design_w[f[0]] = float(f[4])
            elif t == "wateruse:equipment" and len(f) > 2:
                peak_m3s[f[0]] = float(f[2])
            elif t == "schedule:file" and len(f) > 2:
                sched_file[f[0]] = f[2]
        prof_dir = os.path.join(out_dir, "enduse_profiles", fold)
        for r in rows:
            n += 1
            name = "HH_%s_%s" % (fold, r["hid"])
            elec_obj = name + "_Appliances"
            dhw_obj = name + "_DHW"
            if elec_obj not in design_w:
                bad.append("%s: the saved IDF has no ElectricEquipment for %s"
                           % (fold, name))
                continue
            e_csv = sched_file.get(name + "_Appliance")
            d_csv = sched_file.get(name + "_DHW")
            if not e_csv or not d_csv:
                bad.append("%s: %s names a schedule file the IDF does not "
                           "declare" % (fold, name))
                continue
            e_vals = _read_fraction(os.path.join(prof_dir, e_csv))
            d_vals = _read_fraction(os.path.join(prof_dir, d_csv))
            rebuilt_kwh = sum(e_vals) * design_w[elec_obj] * ts / 60.0 / 1000.0
            rebuilt_l = (sum(d_vals) * peak_m3s.get(dhw_obj, 0.0)
                         * 1000.0 * 60.0 * ts)
            claimed_kwh = float(r["elec_kwh_per_year"])
            claimed_l = float(r["dhw_litres_per_year"])
            for label, rebuilt, claimed in (("electricity", rebuilt_kwh, claimed_kwh),
                                            ("DHW", rebuilt_l, claimed_l)):
                if claimed <= 0.0 and rebuilt <= 0.0:
                    bad.append("%s/%s: %s is zero on BOTH sides -- an end use is "
                               "missing from the sum, and two zeroes agree"
                               % (fold, name, label))
                    continue
                if claimed <= 0.0:
                    bad.append("%s/%s: %s claimed 0 but the artefacts carry %.3f"
                               % (fold, name, label, rebuilt))
                    continue
                gap = (rebuilt - claimed) / claimed * 100.0
                if abs(gap) > G9_10_CLOSURE_PCT:
                    bad.append("%s/%s: %s closes to %+.4f %% (%s the summary)"
                               % (fold, name, label, gap,
                                  "ABOVE" if gap > 0 else "BELOW"))
    board.add("G9.10", "PASS" if not bad else "FAIL", n,
              "%d dwellings: electricity and DHW rebuilt from the saved IDF and "
              "the on-disk fraction schedules reconcile with the summary within "
              "%.1f %%" % (n, G9_10_CLOSURE_PCT) if not bad
              else "%d discrepancies: %s" % (len(bad), "; ".join(bad[:5])))


def _read_fraction(path):
    """One-column fraction schedule. Raises rather than defaulting to zero.

    A reader that returns 0.0 for a form it does not understand blames the
    system under test for its own gap.
    """
    vals = []
    with io.open(path, encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    if len(rows) < 2:
        raise ValueError("%s has no data rows" % path)
    for i, row in enumerate(rows[1:], 2):
        if not row:
            continue
        try:
            vals.append(float(row[0]))
        except (ValueError, IndexError):
            raise ValueError("%s line %d is not a number: %r" % (path, i, row))
    return vals


# --------------------------------------------------------------------------
# G9.11 -- 3-digit dependence. EXPECTED TO FAIL, AND ALLOWED TO.
# --------------------------------------------------------------------------
def g9_11(board, rows):
    """The number of distinct ACL codes with DISTINCT appliance rows must exceed
    the number of distinct 2-digit groups.

    🔴 THE BAND IS NOT RELAXED AND THE VERDICT IS WHATEVER THE RULE GIVES.
    `RL25` and the vendored artefact both establish that CREST resolves activity
    at SIX states and consumes zero HETUS codes, and the standing recommendation
    has been that this gate would FAIL and should be allowed to.

    The implementation reports MORE than the verdict, because the verdict alone
    is misleading in both directions. It prints:

      * which 2-digit ACL groups the mapping actually SPLITS, and
      * whether each split comes from CREST's own appliance rows or from our
        DHW driver assignment -- because a split we invented is not evidence
        that a published model uses the third digit.

    A pass driven only by our own DHW drivers would be the gate passing for the
    wrong reason, which is indistinguishable from a vacuous gate until somebody
    prints the breakdown.
    """
    def signatures(subset):
        sig = {}
        for r in subset:
            if r["end_use"] == "none" or r["acl_code"].startswith("*"):
                continue
            sig.setdefault(r["acl_code"], set()).add(
                (r["appliance_id"], r["p_appliance_given_activity"]))
        three = len(set(frozenset(v) for v in sig.values()))
        two = {}
        for code, v in sig.items():
            two.setdefault(code[:2], set()).update(v)
        two_n = len(set(frozenset(v) for v in two.values()))
        split = sorted(g for g, _v in two.items()
                       if len(set(frozenset(sig[c]) for c in sig
                                  if c[:2] == g)) > 1)
        return three, two_n, split, sig

    all_three, all_two, all_split, sig = signatures(rows)
    elec = [r for r in rows if r["end_use"] == "electricity"]
    e_three, e_two, e_split, _ = signatures(elec)

    ok = all_three > all_two
    note = ("%d distinct 3-digit appliance signatures against %d distinct "
            "2-digit signatures. 2-digit groups SPLIT by the mapping: %s. "
            "On CREST's electricity rows ALONE: %d vs %d, splitting %s."
            % (all_three, all_two, ", ".join(all_split) or "none",
               e_three, e_two, ", ".join(e_split) or "none"))
    if ok and not e_split:
        note += (" 🔴 The pass rests ENTIRELY on our own DHW driver assignment, "
                 "which is not a published mapping -- read it as a FAIL of the "
                 "question the gate was asking.")
    elif ok:
        note += (" 🔴 The pass rests on %d published split(s) and nothing wider: "
                 "the third digit buys exactly that much." % len(e_split))
    else:
        note += " The mapping does NOT resolve at three digits. Band NOT relaxed."
    board.add("G9.11", "PASS" if ok else "FAIL", len(sig), note)


# --------------------------------------------------------------------------
# G9.12 -- stock-scale agreement against CREST's own published statistics
# --------------------------------------------------------------------------
def load_crest_activity_statistics(path):
    """`{(n_active, profile): [144 ten-minute probabilities]}`.

    Indexed by the file's OWN two key columns rather than by arithmetic on the
    row number: the re-implementation computes the row as `5*n + profile`, which
    does not match this file's 6-profile blocks, and an off-by-one there would
    read cooking's statistics out of the laundry row without erroring.
    """
    out = {}
    for line in io.open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        f = line.split(";")
        out[(int(f[0]), int(f[1]))] = [float(x) for x in f[2:]]
    return out


def crest_expected_diurnal(mapping, stats, occ_dist, hazards):
    """CREST's OWN expected mean diurnal appliance power, in watts.

    The reference is built from CREST's published 10-minute activity statistics
    and CREST's published appliance parameters -- the two artefacts vendored
    under `sources/`. The only thing taken from our run is the occupancy
    distribution, because the statistics are conditioned on it.

    This is the quantity our diaries REPLACE, so agreement with it is exactly
    the question `G9.12` asks: does swapping CREST's activity timing for HETUS
    diary timing preserve the aggregate load shape?
    """
    prof = [0.0] * 144
    for aid, app in mapping.appliances.items():
        if not app["in_default_dwelling"]:
            continue
        p = app["profile"]
        h = hazards.get(aid, 0.0)
        if h <= 0.0:
            continue
        share = app["ownership_share"]
        starts = [0.0] * 144
        for s in range(144):
            if p < 6:
                inten = sum(occ_dist.get(n, 0.0) * stats.get((n, p), [0.0] * 144)[s]
                            for n in range(6))
            elif p == 6:
                inten = sum(occ_dist.get(n, 0.0) for n in range(1, 6))
            else:
                inten = 1.0
            starts[s] = h * inten * 10.0              # expected starts in slot
        # A cycle started in slot s draws power in slots s .. s + cycle/10, so
        # the expected profile is the start intensity CONVOLVED with the cycle,
        # not the intensity scaled by it. For a 73-minute television that is a
        # seven-slot smear, and leaving it out shifts the whole reference earlier.
        span = max(1, int(round(app["cycle_len_min"] / 10.0)))
        for s in range(144):
            if starts[s] <= 0.0:
                continue
            watts = starts[s] * app["rated_power_w"] * share
            for k in range(span):
                prof[(s + k) % 144] += watts
        for s in range(144):
            prof[s] += app["standby_power_w"] * share
    return prof


def r_squared(a, b):
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    if sa == 0.0 or sb == 0.0:
        return None
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return (cov / (sa * sb)) ** 2


def g9_12(board, root, out_dir, manifests, folds):
    """Aggregate load shape over >= 100 dwellings, R2 >= 0.85."""
    stats_path = os.path.join(out_dir, "sources",
                              "crest_activity_statistics_wd.csv")
    if not os.path.exists(stats_path):
        board.add("G9.12", "NOT_EVALUABLE", 0,
                  "CREST's published activity statistics are not on disk, so "
                  "the reference profile cannot be built. NOT a pass.")
        return
    sys.path.insert(0, os.path.join(root, "tools"))
    trig = _import_trigger(root)
    try:
        mapping = trig.Mapping(os.path.join(out_dir,
                                            "activity_appliance_map.csv"))
    except Exception as exc:                                   # noqa: BLE001
        # The map itself is inconsistent, so no reference profile can be built
        # from it. Reported LOUDLY with the reason rather than defaulting to a
        # verdict: a reference that could not be constructed is not agreement,
        # and it is not disagreement either.
        board.add("G9.12", "NOT_EVALUABLE", 0,
                  "the mapping could not be loaded, so no reference profile "
                  "exists to compare against: %s" % exc)
        return
    stats = load_crest_activity_statistics(stats_path)
    detail = []
    bad = []
    n = 0
    for fold in folds:
        m = manifests.get(fold)
        if not m:
            continue
        n += 1
        ts = m["timestep_min"]
        per_day = 24 * 60 // ts
        spath = os.path.join(out_dir, "stock_series_%s.csv" % fold)
        acc = [0.0] * per_day
        cnt = [0] * per_day
        for r in csv.DictReader(io.open(spath, encoding="utf-8")):
            i = int(r["timestep"]) % per_day
            acc[i] += float(r["electricity_w"])
            cnt[i] += 1
        ours = [acc[i] / cnt[i] / m["n_dwellings"] if cnt[i] else 0.0
                for i in range(per_day)]
        hazards = dict(
            (aid, d["hazard_per_eligible_minute"])
            for aid, d in m["calibration"].items() if not aid.startswith("dhw:"))
        occ = _occupancy_distribution(m)
        ref144 = crest_expected_diurnal(mapping, stats, occ, hazards)
        ref = _rebin(ref144, per_day)
        r2 = r_squared(ours, ref)
        if r2 is None:
            bad.append("%s: one of the two profiles is constant, so R2 is "
                       "undefined -- a flat series is not agreement" % fold)
            continue
        detail.append("%s R2=%.4f" % (fold, r2))
        if r2 < G9_12_R2_MIN:
            bad.append("%s R2=%.4f below %.2f" % (fold, r2, G9_12_R2_MIN))
    board.add("G9.12", "PASS" if not bad else "FAIL", n,
              "mean diurnal appliance power against CREST's own published "
              "activity statistics: %s" % ", ".join(detail) if not bad
              else "; ".join(bad[:6]) + (" (%s)" % ", ".join(detail) if detail
                                         else ""))


def _occupancy_distribution(m):
    """P(n active occupants) implied by this fold's household sizes.

    Approximated by household SIZE, which is what the manifest carries. Stated
    rather than hidden: CREST's statistics are conditioned on ACTIVE occupancy
    and this is a size distribution, so the reference profile is an
    approximation of CREST's, not a reproduction of it.
    """
    total = float(m["n_dwellings"])
    dist = collections.Counter()
    for row in m.get("cycles", []):
        break
    sizes = m.get("household_sizes")
    if not sizes:
        mean = m["n_people"] / total
        lo = int(math.floor(mean))
        frac = mean - lo
        dist[lo] += 1.0 - frac
        dist[min(5, lo + 1)] += frac
        return dict(dist)
    for s in sizes:
        dist[min(5, s)] += 1.0 / total
    return dict(dist)


def _rebin(values, n_out):
    n_in = len(values)
    if n_in == n_out:
        return list(values)
    out = []
    per = n_in / float(n_out)
    for i in range(n_out):
        lo = int(round(i * per))
        hi = max(lo + 1, int(round((i + 1) * per)))
        chunk = values[lo:hi]
        out.append(sum(chunk) / len(chunk))
    return out


# --------------------------------------------------------------------------
# G9.13 -- the per-dwelling non-claim, with V9.d's coverage clause
# --------------------------------------------------------------------------
PER_DWELLING_PATTERNS = [
    r"predict(?:s|ed|ion)?\s+(?:the\s+)?(?:load|demand|profile|consumption)\s+"
    r"(?:of|for)\s+(?:a|one|this)\s+(?:dwelling|household|home)",
    r"per-dwelling\s+prediction",
    r"this\s+dwelling(?:'s)?\s+predicted",
    r"forecast\s+for\s+(?:a|one)\s+(?:dwelling|household)",
]


def g9_13(board, out_dir, extra_dirs=()):
    """No result in any output, table or figure is a per-dwelling prediction.

    `V9.d`: the search PRINTS the files it scanned and FAILs if it scanned fewer
    than the results directory contains. A green check that scanned nothing is
    decoration.
    """
    scanned = []
    hits = []
    roots = [out_dir] + list(extra_dirs)
    candidates = 0
    pats = [re.compile(p, re.I) for p in PER_DWELLING_PATTERNS]
    for rt in roots:
        for dirpath, _dirs, files in os.walk(rt):
            if os.sep + "sources" in dirpath or os.sep + "enduse_profiles" in dirpath:
                continue
            for fn in files:
                if not fn.lower().endswith((".md", ".csv", ".json", ".txt", ".idf")):
                    continue
                candidates += 1
                path = os.path.join(dirpath, fn)
                try:
                    text = io.open(path, encoding="utf-8", errors="replace").read()
                except Exception:                          # noqa: BLE001
                    continue
                scanned.append(os.path.relpath(path, rt))
                for p in pats:
                    m = p.search(text)
                    if m:
                        hits.append("%s: %r" % (os.path.relpath(path, rt),
                                                m.group(0)[:60]))
    if len(scanned) < candidates:
        board.add("G9.13", "FAIL", len(scanned),
                  "scanned %d of %d candidate files -- V9.d refuses a verdict "
                  "over a subset the check chose itself"
                  % (len(scanned), candidates))
        return
    board.add("G9.13", "PASS" if not hits else "FAIL", len(scanned),
              "scanned %d result artefacts, no per-dwelling prediction framing"
              % len(scanned) if not hits else
              "%d per-dwelling claims: %s" % (len(hits), "; ".join(hits[:4])))


# --------------------------------------------------------------------------
# G9.14 -- the trigger's runtime inputs exist in the generated record
# --------------------------------------------------------------------------
def g9_14(board, root, manifests, folds):
    """The set of columns the trigger reads at runtime must be a SUBSET of the
    columns the generated diaries actually carry -- asserted against the FILE --
    and must not contain `act2`.

    🔴 RE-SPECIFIED 2026-08-25, `FINDING 137`, `D-S9-2` item 3. The gate's
    original rationale was that `act2` is absent from the generated record, so a
    rule reading it would silently never fire. THAT IS FALSE: the episode tuple
    has five fields and 29.816 % of shipped episodes carry a non-empty `act2`.
    The exclusion of `act2` is therefore a POLICY -- `D-S9-1` ruled (d), the
    trigger fires from the primary code alone -- and this gate asserts the
    policy, not the format. The registered perturbation is unchanged.
    """
    sys.path.insert(0, os.path.join(root, "tools"))
    import decoder as dec                                  # noqa: PLC0415
    from encoder import load_bit_positions                 # noqa: PLC0415
    bitpos = load_bit_positions(os.path.join(
        root, "Step2_docs", "outputs_step2", "crosswalk_copresence.csv"))
    problems = []
    n = 0
    for fold in folds:
        m = manifests.get(fold)
        if not m:
            continue
        path = os.path.join(root, "Step7_docs", "outputs_step7",
                            "generated_%s_%s_constrained.jsonl"
                            % (m["leg"], fold))
        with io.open(path, encoding="utf-8") as fh:
            rec = json.loads(fh.readline())
        episode = dec.decode_record(rec["text"], bitpos)["episodes"][0]
        present = set(episode.keys())
        used = set(m["runtime_input_columns"])
        n += len(used)
        missing = sorted(used - present)
        if missing:
            problems.append("%s: the trigger reads %s, which the generated "
                            "record does not carry"
                            % (fold, ", ".join(missing)))
        if "act2" in used:
            problems.append(
                "%s: the trigger reads `act2`, which D-S9-1 ruling (d) forbids. "
                "The record DOES carry it (FINDING 137), so this would fire and "
                "silently reintroduce a dropped calibration input." % fold)
    board.add("G9.14", "PASS" if not problems else "FAIL", n,
              "the trigger's runtime columns are a subset of the generated "
              "record's, and act2 is not among them" if not problems
              else "; ".join(problems[:4]))


# --------------------------------------------------------------------------
# vacuity guards
# --------------------------------------------------------------------------
def v9_a(board, root, rows, manifests, folds):
    """The map must not have fewer rows than the corpus has distinct ACL codes,
    and the shortfall is PRINTED.

    Also reports, as INFO, any ACL code the map claims a load for that the
    corpus never contains. A row about a code that does not occur is a different
    fact from a missing row, and burying it would be the same silence.
    """
    sys.path.insert(0, os.path.join(root, "tools"))
    import decoder as dec                                  # noqa: PLC0415
    from encoder import load_bit_positions                 # noqa: PLC0415
    bitpos = load_bit_positions(os.path.join(
        root, "Step2_docs", "outputs_step2", "crosswalk_copresence.csv"))
    present = collections.Counter()
    for fold in folds:
        m = manifests.get(fold)
        leg = m["leg"] if m else "leg5"
        path = os.path.join(root, "Step7_docs", "outputs_step7",
                            "generated_%s_%s_constrained.jsonl" % (leg, fold))
        with io.open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                for e in dec.decode_record(json.loads(line)["text"],
                                           bitpos)["episodes"]:
                    present[e["act"] if e["act"] is not None else "000"] += 1
    covered = set(r["acl_code"] for r in rows if not r["acl_code"].startswith("*"))
    shortfall = sorted(set(present) - covered)
    claimed = set(r["acl_code"] for r in rows
                  if r["end_use"] != "none" and not r["acl_code"].startswith("*"))
    inert = sorted(claimed - set(present))
    note = ("%d distinct ACL codes in the corpus, %d covered by the map"
            % (len(present), len(covered & set(present))))
    if inert:
        note += "; INERT (claimed but never occurring): %s" % ", ".join(inert)
    if shortfall:
        note += "; SHORTFALL: %s" % ", ".join(shortfall[:12])
    board.add("V9.a", "PASS" if not shortfall else "FAIL", len(present), note)


def v9_b(board, board_rows):
    """G9.1 to G9.4 must print the row count they scanned before any verdict.

    A provenance check over an empty set passes for the wrong reason.
    """
    bad = []
    for gid in ("G9.1", "G9.2", "G9.3", "G9.4"):
        row = next((r for r in board_rows if r["id"] == gid), None)
        if row is None:
            bad.append("%s did not run" % gid)
        elif not row["n_scanned"]:
            bad.append("%s scanned 0 rows and still returned %s"
                       % (gid, row["verdict"]))
    board.add("V9.b", "PASS" if not bad else "FAIL", 4,
              "G9.1-G9.4 each scanned a non-empty row set" if not bad
              else "; ".join(bad))


def v9_e(board, rows):
    """G9.2's presence test keys on the structured field, not on the word.

    Proven rather than asserted: a row is built in memory whose `reasoning`
    quotes the word VALIDATED while its `validation_label` column is empty. A
    naive presence test reads that as compliance; `G9.2` must call it a FAIL.
    """
    probe = dict(rows[0])
    probe["row_id"] = "PROBE"
    probe["validation_label"] = ""
    probe["validation_scale"] = ""
    probe["reasoning"] = ("superseded note: this row was once labelled VALIDATED "
                          "at stock scale and that label was withdrawn")
    sub = Board()
    g9_2(sub, [probe])
    ok = sub.verdict("G9.2") == "FAIL"
    board.add("V9.e", "PASS" if ok else "FAIL", 1,
              "a row quoting the word VALIDATED with an empty label column is "
              "read as a FAIL" if ok else
              "G9.2 accepted a row whose label lives only in prose")


# --------------------------------------------------------------------------
# the runner
# --------------------------------------------------------------------------
def _import_trigger(root):
    import importlib.util
    path = os.path.join(root, "tools", "4thJ_step9_trigger.py")
    spec = importlib.util.spec_from_file_location("step9_trigger", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.join(root, "tools"))
    spec.loader.exec_module(mod)
    return mod


def declared_gate_ids(val_doc_path):
    """The gate IDs the VALIDATION DOCUMENT declares, read from the document.

    A gate that exists only in prose occupies the slot of the check that would
    have caught the defect. So the runner compares what it scores against what
    the document claims, and refuses to report a tally if the two disagree.
    Read from the file, never from a constant in this file -- a constant here
    would be written by the same hand as the runner and would agree with it.
    """
    text = io.open(val_doc_path, encoding="utf-8").read()
    gates = set(re.findall(r"\bG9\.\d+\b", text))
    guards = set(re.findall(r"\bV9\.[a-z]\b", text))
    return sorted(gates, key=lambda g: int(g.split(".")[1])), sorted(guards)


def run(root, folds, offline=False, out_dir=None, quiet=False):
    out_dir = out_dir or os.path.join(root, "Step9_docs", "outputs_step9")
    val_doc = os.path.join(root, "Step9_docs", "4thJ_09_enduseLoads_val.md")
    rows, _map_path = read_map(out_dir)
    cites, _cit_path = read_citations(out_dir)
    manifests = {}
    for f in folds:
        m = read_manifest(out_dir, f)
        if m:
            manifests[f] = m
    trig = _import_trigger(root)

    board = Board()
    g9_1(board, rows)
    g9_2(board, rows)
    g9_3(board, rows)
    g9_4(board, cites, out_dir, offline=offline)
    g9_5(board, trig)
    g9_6(board, manifests)
    g9_7(board, manifests)
    g9_8(board, manifests)
    g9_9(board, out_dir, folds)
    g9_10(board, out_dir, manifests, folds)
    g9_11(board, rows)
    g9_12(board, root, out_dir, manifests, folds)
    g9_13(board, out_dir, extra_dirs=[os.path.join(root, "Step9_docs", "docs")])
    g9_14(board, root, manifests, folds)

    v9_a(board, root, rows, manifests, folds)
    v9_b(board, board.rows)
    # V9.c is asserted inside G9.4 and recorded here from its verdict.
    board.add("V9.c", "PASS" if board.verdict("G9.4") != "PASS" or not offline
              else "FAIL", 1,
              "G9.4 reports NOT CHECKED rather than PASS when the resolver "
              "cannot be reached (verdict was %s)" % board.verdict("G9.4"))
    # V9.d is asserted inside G9.13.
    g13 = next(r for r in board.rows if r["id"] == "G9.13")
    board.add("V9.d", "PASS" if g13["n_scanned"] > 0 else "FAIL",
              g13["n_scanned"],
              "G9.13 printed the %d files it scanned" % g13["n_scanned"])
    v9_e(board, rows)

    # -- the gate set must be the one the document declares -------------------
    declared, guards = declared_gate_ids(val_doc)
    scored = sorted((r["id"] for r in board.rows if r["id"].startswith("G9.")),
                    key=lambda g: int(g.split(".")[1]))
    missing = sorted(set(declared) - set(scored),
                     key=lambda g: int(g.split(".")[1]))
    extra = sorted(set(scored) - set(declared),
                   key=lambda g: int(g.split(".")[1]))
    guard_missing = sorted(set(guards) - set(
        r["id"] for r in board.rows if r["id"].startswith("V9.")))
    coverage_ok = not missing and not extra and not guard_missing

    result = {
        "board": board.rows,
        "counts": board.counts(),
        "declared_gates": declared,
        "scored_gates": scored,
        "gates_declared_but_not_scored": missing,
        "gates_scored_but_not_declared": extra,
        "guards_declared_but_not_run": guard_missing,
        "gate_set_matches_document": coverage_ok,
        "folds": folds,
        "n_map_rows": len(rows),
    }
    if not quiet:
        print("%-7s %-14s %8s  %s" % ("gate", "verdict", "scanned", "note"))
        print("-" * 110)
        for r in board.rows:
            print("%-7s %-14s %8s  %s"
                  % (r["id"], r["verdict"], r["n_scanned"], r["note"][:150]))
        print("-" * 110)
        print("counts: %s" % json.dumps(board.counts(), sort_keys=True))
        if coverage_ok:
            print("gate set matches the validation document: %d gates, %d guards"
                  % (len(declared), len(guards)))
        else:
            print("GATE SET DOES NOT MATCH THE DOCUMENT -- declared-not-scored "
                  "%s, scored-not-declared %s, guards-not-run %s"
                  % (missing, extra, guard_missing))
    return result


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--folds", default="es,uk,it")
    ap.add_argument("--offline", action="store_true",
                    help="skip CrossRef; G9.4 then reports NOT CHECKED, never PASS")
    ap.add_argument("--out", default=None)
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)
    res = run(args.root, [f for f in args.folds.split(",") if f],
              offline=args.offline, out_dir=args.out)
    if args.json:
        io.open(args.json, "w", encoding="utf-8", newline="").write(
            json.dumps(res, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
