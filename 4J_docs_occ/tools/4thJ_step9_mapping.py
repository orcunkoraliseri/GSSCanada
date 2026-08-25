# -*- coding: utf-8 -*-
"""4J Step 9, work item 9.1 -- build the activity-to-appliance mapping table.

    python 4thJ_step9_mapping.py --root <4J_docs_occ>

Writes `outputs_step9/activity_appliance_map.csv`, `outputs_step9/citations.csv`
and `outputs_step9/mapping_provenance.md`.

WHAT THIS TOOL IS ALLOWED TO DO, AND WHAT IT IS NOT
---------------------------------------------------
`RL13`'s instruction, which the step document repeats in bold, is *do not invent
the mapping*.  Everything numeric in the output is therefore copied out of a
primary artefact that is vendored beside it under `outputs_step9/sources/` and
stamped with its md5:

  * the appliance parameters -- ownership, cycles per year, cycle length, rated
    power, standby power, restart delay, occupancy dependence, activity profile
    index and activity probability -- come from CREST, as distributed in the
    `richardsonpy` re-implementation's `inputs/Appliances.csv`;
  * the activity-profile code list (0 watching TV .. 8 CUSTOM) comes from that
    same re-implementation's `classes/appliance.py` docstring;
  * the domestic-hot-water parameters come from Table 1 of Jordan & Vajen's
    IEA-SHC Task 26 report, read from the report itself.

The ONE thing this tool contributes is the join key: which HETUS ACL code
corresponds to which CREST activity state.  That join is NOT taken from any
published source, because no published model consumes HETUS -- and it is
therefore held OUTSIDE this file, in `outputs_step9/acl_to_crest_activity.csv`,
so that an author ruling edits data and never code.  Rows whose join is not a
name-for-name correspondence carry `D-S9-2 item ...` in that file and are
labelled `NOT VALIDATED` here.

The coverage set is read from the GENERATED DIARIES, never from a constant:
`V9.a` is about what the corpus actually contains.
"""
import argparse
import codecs
import collections
import csv
import hashlib
import io
import json
import os
import sys


class MappingError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# the citation register.  Every bibliographic field here was resolved against
# the CrossRef API before it was written down; `G9.4` re-resolves them.
# `FINDING 47` is why volume, issue, pages AND first author are all carried.
# --------------------------------------------------------------------------
CITATIONS = [
    {
        "key": "CREST-2010",
        "model": "CREST",
        "authors": "Richardson, I.; Thomson, M.; Infield, D.; Clifford, C.",
        "first_author_family": "Richardson",
        "year": "2010",
        "title": "Domestic electricity use: A high-resolution energy demand model",
        "container": "Energy and Buildings",
        "volume": "42",
        "issue": "10",
        "page": "1878-1887",
        "doi": "10.1016/j.enbuild.2010.05.023",
        "artefact": "sources/crest_appliances_richardsonpy.csv",
        "artefact_origin": (
            "https://raw.githubusercontent.com/RWTH-EBC/richardsonpy/master/"
            "richardsonpy/inputs/Appliances.csv"),
        "artefact_licence": "GPL-3.0 (the richardsonpy repository)",
        "table": "Table 1 (33 appliances), as distributed in richardsonpy inputs/Appliances.csv",
        "note": (
            "The VALUES are CREST's published appliance parameters. They were read "
            "from the open re-implementation, NOT from the paywalled table in the "
            "paper. The 33-appliance count reported by RL25 B1 as UNVERIFIED is "
            "confirmed by this artefact: it carries exactly 33 appliance rows."),
    },
    {
        "key": "CREST-ACTIVITY-CODES",
        "model": "CREST",
        "authors": "Richardson, I.; Thomson, M.; Infield, D.; Clifford, C.",
        "first_author_family": "Richardson",
        "year": "2010",
        "title": "Domestic electricity use: A high-resolution energy demand model",
        "container": "Energy and Buildings",
        "volume": "42",
        "issue": "10",
        "page": "1878-1887",
        "doi": "10.1016/j.enbuild.2010.05.023",
        "artefact": "sources/crest_activity_codes.txt",
        "artefact_origin": (
            "https://raw.githubusercontent.com/RWTH-EBC/richardsonpy/master/"
            "richardsonpy/classes/appliance.py"),
        "artefact_licence": "GPL-3.0 (the richardsonpy repository)",
        "table": "activity-profile code list, docstring of classes/appliance.py",
        "note": (
            "Nine profile indices, of which SIX are named activities. This is the "
            "measurement behind G9.11: CREST resolves activity at six states, so no "
            "mapping adapted from it can resolve at three HETUS digits."),
    },
    {
        "key": "JORDAN-VAJEN-2001",
        "model": "Jordan & Vajen (IEA-SHC Task 26)",
        "authors": "Jordan, U.; Vajen, K.",
        "first_author_family": "Jordan",
        "year": "2001",
        "title": "Realistic Domestic Hot-Water Profiles in Different Time Scales",
        "container": "IEA-SHC Task 26: Solar Combisystems (report, V2.0, May 2001)",
        "volume": "",
        "issue": "",
        "page": "",
        "doi": "",
        "artefact": "sources/jordan_vajen_iea_task26_v2.0_2001.pdf",
        "artefact_origin": (
            "https://sel.me.wisc.edu/trnsys/trnlib/iea-shc-task26/"
            "iea-shc-task26-load-profiles-description-jordan.pdf"),
        "artefact_licence": "report distributed by the authors; not re-licensed here",
        "table": "Table 1, 'Assumptions and derived quantities for the load profile'",
        "note": (
            "A REPORT, NOT A JOURNAL ARTICLE: it carries no DOI. G9.4 therefore "
            "requires it to carry a retrievable artefact and an md5 instead, which "
            "is a stricter test than the DOI clause, not a waiver of it."),
    },
]

# --------------------------------------------------------------------------
# Jordan & Vajen Table 1, transcribed from the vendored report.
# Vdot l/min | duration min | incidences/day | sigma | vol/load l | vol/day l | portion
# --------------------------------------------------------------------------
DHW_EVENTS = [
    ("A", "short load (washing hands, etc.)", 1.0, 1, 28.0, 2.0, 1.0, 28.0, 0.14),
    ("B", "medium load (dish-washer, etc.)", 6.0, 1, 12.0, 2.0, 6.0, 72.0, 0.36),
    ("C", "bath", 14.0, 10, 0.143, 2.0, 140.0, 20.0, 0.10),
    ("D", "shower", 8.0, 5, 2.0, 2.0, 40.0, 80.0, 0.40),
]
DHW_REFERENCE_L_PER_DAY = 200.0      # "a mean load volume of 200 litres per day
#                                      was chosen for a single family house"
DHW_DELTA_T_K = 35.0                 # the report's own worked example: 35 K rise

# Which ACL codes drive which DHW category. THIS JOIN IS OURS: Jordan & Vajen
# distribute draws by a probability function over year/weekday/day, NOT by a
# time-use code. Every row below is therefore NOT VALIDATED by construction.
DHW_DRIVERS = {
    "A": ["031", "039", "312"],
    "B": ["312", "311"],
    "C": ["031"],
    "D": ["031"],
}

VALIDATION_SCALE_CREST = (
    "stock/aggregate scale (the source model's own validation). NOT re-verified "
    "here: the paper is paywalled and reconstructing a paywalled table is "
    "forbidden. RL13 and RL25 report the lineage as validated at 100-500 "
    "dwellings with R2 above 0.90; that figure is UNVERIFIED and is not quoted "
    "as ours."
)
VALIDATION_SCALE_JV = (
    "single-family-house scale, 200 l/day reference load. The report's own basis; "
    "not re-verified beyond reading Table 1 in the vendored artefact."
)


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


# --------------------------------------------------------------------------
# inputs
# --------------------------------------------------------------------------
def load_crest_appliances(path):
    """Parse richardsonpy's semicolon CSV into typed appliance records."""
    rows = []
    group = ""
    with io.open(path, encoding="utf-8") as fh:
        header = fh.readline()
        if "Activity use profile" not in header:
            raise MappingError(
                "%s is not the CREST appliance table: its header does not name "
                "'Activity use profile'." % path)
        for line in fh:
            line = line.rstrip("\r\n")
            if not line.strip():
                continue
            f = line.split(";")
            # Thirteen, not twelve: the first two columns are the appliance
            # GROUP and the appliance NAME, and the group is blank on every row
            # but the first of its block. Asserted rather than assumed, because a
            # silent off-by-one here would read the activity index out of the
            # restart-delay column and every gate downstream would still pass.
            if len(f) != 13:
                raise MappingError(
                    "CREST appliance row has %d fields, expected 13: %r"
                    % (len(f), line))
            if f[0].strip():
                group = f[0].strip()
            rows.append({
                "group": group,
                "name": f[1].strip(),
                "in_default_dwelling": int(f[2]),
                "ownership_share": float(f[3]),
                "cycles_per_year": float(f[4]),
                "mean_cycle_length_min": int(f[5]),
                "rated_power_w": int(f[6]),
                "standby_power_w": int(f[7]),
                "restart_delay_min": int(f[8]),
                "occupancy_dependent": int(f[9]),
                "activity_index": int(f[10]),
                "activity_probability": float(f[11]),
                "power_factor": float(f[12]),
            })
    if len(rows) != 33:
        raise MappingError(
            "expected CREST's 33 appliances, found %d. RL25 B1 reported 33 and "
            "that count is load-bearing." % len(rows))
    return rows


def load_crosswalk(path):
    rows = list(csv.DictReader(io.open(path, encoding="utf-8")))
    if not rows:
        raise MappingError("%s is empty. A mapping over an empty join is V9.b's "
                           "'passes for the wrong reason'." % path)
    seen = collections.Counter(r["acl_code"] for r in rows)
    dupes = [c for c, n in seen.items() if n > 1]
    if dupes:
        raise MappingError(
            "an ACL code appears twice in the crosswalk, so one activity would "
            "fire two states: %s" % sorted(dupes))
    return rows


def load_acl_labels(path):
    out = {}
    for r in csv.DictReader(io.open(path, encoding="utf-8")):
        out[r["target_code"]] = r["target_label_en"]
    return out


def acl_codes_present(root, folds, decoder_dir):
    """Distinct ACL codes in the GENERATED diaries, with their time share.

    Read from the files themselves. `V9.a` is a claim about the corpus, and a
    schema constant is written by the same hand as the mapping.
    """
    sys.path.insert(0, decoder_dir)
    import decoder as dec                       # noqa: PLC0415
    from encoder import load_bit_positions      # noqa: PLC0415

    bitpos = load_bit_positions(os.path.join(
        root, "Step2_docs", "outputs_step2", "crosswalk_copresence.csv"))
    minutes = collections.Counter()
    episodes = collections.Counter()
    total = 0
    files = []
    for fold in folds:
        path = os.path.join(root, "Step7_docs", "outputs_step7",
                            "generated_leg5_%s_constrained.jsonl" % fold)
        files.append(os.path.basename(path))
        with io.open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                d = dec.decode_record(json.loads(line)["text"], bitpos)
                for e in d["episodes"]:
                    # `D-S7-1(c)`: the decoder returns None for ACT_NULL_CODE,
                    # which is the `000` state -- a duration with no activity.
                    # It is a state, not a gap, so it is counted and it gets its
                    # own explicit no-load row rather than vanishing here.
                    act = e["act"] if e["act"] is not None else "000"
                    minutes[act] += e["duration_min"]
                    episodes[act] += 1
                    total += e["duration_min"]
    return minutes, episodes, total, files


# --------------------------------------------------------------------------
# output
# --------------------------------------------------------------------------
FIELDS = [
    "row_id", "acl_code", "acl_label", "crest_activity_index",
    "crest_activity_name", "appliance_id", "appliance_name", "appliance_group",
    "end_use", "p_appliance_given_activity", "rated_power_w", "standby_power_w",
    "mean_cycle_length_min", "restart_delay_min", "cycles_per_year",
    "ownership_share", "occupancy_dependent", "power_factor",
    "in_default_dwelling", "dhw_flow_l_per_min", "dhw_duration_min",
    "dhw_inc_per_day", "dhw_sigma", "dhw_vol_per_load_l",
    "source_model", "source_citation_key", "source_table", "source_doi",
    "source_artefact", "source_artefact_md5", "validation_label",
    "validation_scale", "reasoning",
]


def appliance_id(name):
    keep = []
    for ch in name.lower():
        keep.append(ch if ch.isalnum() else "_")
    out = "".join(keep)
    while "__" in out:
        out = out.replace("__", "_")
    return out.strip("_")


def build(root, folds):
    out_dir = os.path.join(root, "Step9_docs", "outputs_step9")
    src_dir = os.path.join(out_dir, "sources")
    crest_path = os.path.join(src_dir, "crest_appliances_richardsonpy.csv")
    jv_path = os.path.join(src_dir, "jordan_vajen_iea_task26_v2.0_2001.pdf")
    codes_path = os.path.join(src_dir, "crest_activity_codes.txt")

    appliances = load_crest_appliances(crest_path)
    crosswalk = load_crosswalk(os.path.join(out_dir, "acl_to_crest_activity.csv"))
    labels = load_acl_labels(os.path.join(
        root, "Step2_docs", "outputs_step2", "activity_target_list.csv"))
    minutes, episodes, total_min, gen_files = acl_codes_present(
        root, folds, os.path.join(root, "tools"))

    cite = dict((c["key"], c) for c in CITATIONS)
    crest_md5 = md5_of(crest_path)
    jv_md5 = md5_of(jv_path)
    codes_md5 = md5_of(codes_path) if os.path.exists(codes_path) else ""

    by_index = collections.defaultdict(list)
    for a in appliances:
        by_index[a["activity_index"]].append(a)

    rows = []
    n = 0

    def emit(**kw):
        nonlocal n
        n += 1
        rec = dict((f, "") for f in FIELDS)
        rec["row_id"] = "R%04d" % n
        rec.update(kw)
        missing = set(rec) - set(FIELDS)
        if missing:
            raise MappingError("row carries unknown fields: %s" % sorted(missing))
        rows.append(rec)

    # --- 1. CREST appliance rows, one per (ACL code x appliance) -------------
    for cw in crosswalk:
        idx = int(cw["crest_activity_index"])
        code = cw["acl_code"]
        label = labels.get(code, cw["crest_activity_name"]
                           if code.startswith("*") else "")
        if code.startswith("*"):
            label = "(dwelling state, not an ACL code)"
        elif code not in labels:
            raise MappingError(
                "crosswalk names ACL code %r, which is not in "
                "activity_target_list.csv. A join key that does not exist in the "
                "corpus is FINDING 42's shape." % code)
        provisional = cw["decision_status"] != "unambiguous"
        for a in by_index.get(idx, []):
            emit(
                acl_code=code,
                acl_label=label,
                crest_activity_index=idx,
                crest_activity_name=cw["crest_activity_name"],
                appliance_id=appliance_id(a["name"]),
                appliance_name=a["name"],
                appliance_group=a["group"],
                end_use="electricity",
                p_appliance_given_activity="%.4f" % a["activity_probability"],
                rated_power_w=a["rated_power_w"],
                standby_power_w=a["standby_power_w"],
                mean_cycle_length_min=a["mean_cycle_length_min"],
                restart_delay_min=a["restart_delay_min"],
                cycles_per_year="%.5f" % a["cycles_per_year"],
                ownership_share="%.3f" % a["ownership_share"],
                occupancy_dependent=a["occupancy_dependent"],
                power_factor="%.1f" % a["power_factor"],
                in_default_dwelling=a["in_default_dwelling"],
                source_model="CREST",
                source_citation_key="CREST-2010",
                source_table=cite["CREST-2010"]["table"],
                source_doi=cite["CREST-2010"]["doi"],
                source_artefact="sources/crest_appliances_richardsonpy.csv",
                source_artefact_md5=crest_md5,
                validation_label="NOT VALIDATED" if provisional else "VALIDATED",
                validation_scale=VALIDATION_SCALE_CREST,
                reasoning=(
                    ("The appliance parameters are CREST's. The ACL join is "
                     "PROVISIONAL and awaits %s: %s"
                     % (cw["decision_status"], cw["reasoning"]))
                    if provisional else
                    ("The appliance parameters are CREST's. The ACL join is a "
                     "name-for-name correspondence between two published code "
                     "lists: %s" % cw["reasoning"])),
            )

    # --- 2. Jordan & Vajen DHW rows -----------------------------------------
    for cat, name, vdot, dur, inc, sigma, vol_load, _vol_day, _portion in DHW_EVENTS:
        for code in DHW_DRIVERS[cat]:
            emit(
                acl_code=code,
                acl_label=labels.get(code, ""),
                crest_activity_index="",
                crest_activity_name="",
                appliance_id="dhw_cat_%s" % cat.lower(),
                appliance_name="DHW draw-off category %s: %s" % (cat, name),
                appliance_group="Domestic hot water",
                end_use="dhw",
                p_appliance_given_activity="",
                dhw_flow_l_per_min="%.1f" % vdot,
                dhw_duration_min=dur,
                dhw_inc_per_day="%.3f" % inc,
                dhw_sigma="%.1f" % sigma,
                dhw_vol_per_load_l="%.1f" % vol_load,
                source_model="Jordan & Vajen (IEA-SHC Task 26)",
                source_citation_key="JORDAN-VAJEN-2001",
                source_table=cite["JORDAN-VAJEN-2001"]["table"],
                source_doi="",
                source_artefact="sources/jordan_vajen_iea_task26_v2.0_2001.pdf",
                source_artefact_md5=jv_md5,
                validation_label="NOT VALIDATED",
                validation_scale=VALIDATION_SCALE_JV,
                reasoning=(
                    "The four categories and every number in this row -- flow "
                    "rate, duration, incidences per day, sigma and volume per "
                    "load -- are Table 1's. The ACL DRIVER IS OURS AND IS NOT "
                    "PUBLISHED: Jordan & Vajen distribute draw-offs by a "
                    "probability function over year, weekday and day, not by a "
                    "time-use code, so no published source assigns category %s to "
                    "ACL %s. Labelled NOT VALIDATED for that reason and for no "
                    "other. See D-S9-2 item 4." % (cat, code)),
            )

    # --- 3. every remaining ACL code present in the corpus -------------------
    mapped = set(r["acl_code"] for r in rows)
    for code in sorted(minutes):
        if code in mapped:
            continue
        emit(
            acl_code=code,
            acl_label=labels.get(
                code, "(null activity state, D-S7-1(c))" if code == "000"
                else "(not in activity_target_list.csv)"),
            appliance_id="NONE",
            appliance_name="(no appliance)",
            appliance_group="(none)",
            end_use="none",
            source_model="(none -- examined and not found)",
            source_citation_key="",
            source_table="",
            source_doi="",
            source_artefact="",
            source_artefact_md5="",
            validation_label="NOT VALIDATED",
            validation_scale="not applicable: no load is claimed for this code",
            reasoning=(
                ("The `000` null state carries a duration and no activity "
                 "(D-S7-1(c)), so under D-S9-1's ruling (d) -- the trigger fires "
                 "from the primary code alone -- there is nothing to fire from. "
                 "No load is claimed. This state is %.4f %% of modelled time."
                 % (100.0 * minutes[code] / total_min))
                if code == "000" else
                ("No published activity-to-appliance model assigns a load to "
                 "this activity. CREST resolves six activity states and this is "
                 "not one of them; Widen resolves nine to ten and publishes no "
                 "HETUS join; LoadProfileGenerator uses a bespoke ontology with "
                 "zero TUS codes; RAMP has no activity mapping at all. Inventing "
                 "a plausible number here is the one thing RL13 forbids, so the "
                 "row claims nothing. This code is %.4f %% of modelled time."
                 % (100.0 * minutes[code] / total_min))),
        )

    # --- write ---------------------------------------------------------------
    map_path = os.path.join(out_dir, "activity_appliance_map.csv")
    with io.open(map_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    cit_path = os.path.join(out_dir, "citations.csv")
    cit_fields = ["key", "model", "authors", "first_author_family", "year",
                  "title", "container", "volume", "issue", "page", "doi",
                  "artefact", "artefact_origin", "artefact_licence", "table",
                  "note"]
    with io.open(cit_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cit_fields, lineterminator="\n")
        w.writeheader()
        for c in CITATIONS:
            row = dict(c)
            if row["key"] == "CREST-2010":
                row["note"] += " md5 %s." % crest_md5
            elif row["key"] == "JORDAN-VAJEN-2001":
                row["note"] += " md5 %s." % jv_md5
            elif row["key"] == "CREST-ACTIVITY-CODES" and codes_md5:
                row["note"] += " md5 %s." % codes_md5
            w.writerow(row)

    stats = {
        "n_rows": len(rows),
        "n_acl_codes_in_corpus": len(minutes),
        "n_acl_codes_covered_by_a_load": len(
            set(r["acl_code"] for r in rows
                if r["appliance_id"] not in ("NONE", "")
                and not r["acl_code"].startswith("*"))),
        "n_appliance_rows": sum(1 for r in rows if r["end_use"] == "electricity"),
        "n_dhw_rows": sum(1 for r in rows if r["end_use"] == "dhw"),
        "n_no_load_rows": sum(1 for r in rows if r["end_use"] == "none"),
        "n_validated": sum(1 for r in rows if r["validation_label"] == "VALIDATED"),
        "n_not_validated": sum(1 for r in rows
                               if r["validation_label"] == "NOT VALIDATED"),
        "generated_files": gen_files,
        "total_modelled_minutes": total_min,
        "crest_md5": crest_md5,
        "jv_md5": jv_md5,
        "map_md5": md5_of(map_path),
    }
    write_provenance(out_dir, rows, stats, minutes, total_min, crosswalk)
    return stats


def write_provenance(out_dir, rows, stats, minutes, total_min, crosswalk):
    path = os.path.join(out_dir, "mapping_provenance.md")
    covered_time = sum(
        minutes[c] for c in set(
            r["acl_code"] for r in rows
            if r["end_use"] == "electricity" and not r["acl_code"].startswith("*")))
    L = []
    A = L.append
    A("# Step 9, item 9.1 -- provenance of `activity_appliance_map.csv`")
    A("")
    A("Generated by `tools/4thJ_step9_mapping.py`. Every number in the map is "
      "copied from a")
    A("primary artefact vendored under `outputs_step9/sources/` and stamped with "
      "its md5.")
    A("")
    A("## What was adapted, and from where")
    A("")
    A("| model | publishes a mapping table? | used here | why |")
    A("|---|---|---|---|")
    A("| **CREST** (Richardson et al. 2010) | yes -- Table 1, 33 appliances | "
      "**YES, in full** | the only source of the four quantities the trigger "
      "needs (activity state, activity probability, rated power, cycle length) "
      "in one artefact |")
    A("| **Widen** et al. 2009 / 2010 | yes -- 2009 Tables 1-2, 2010 Table 1 | "
      "**no** | the papers are paywalled and reconstructing a paywalled table is "
      "forbidden. No open artefact reproduces the tables |")
    A("| **LoadProfileGenerator** (Pflugradt 2016) | no -- the mapping lives "
      "inside `profilegenerator.db3` | **no** | a bespoke *Affordance* ontology "
      "with **zero** TUS codes, so nothing joins to an ACL code |")
    A("| **RAMP** (Lombardi et al. 2020) | **no mapping at all** | **no** | "
      "user-defined time-of-use windows; `RL25` reported a clean NOT FOUND and "
      "that is what it is |")
    A("| **Jordan & Vajen** (IEA-SHC Task 26, 2001) | yes -- Table 1, four "
      "draw-off categories | **YES, for DHW** | the model the step document "
      "names; the report is open and was read |")
    A("")
    A("## The one thing in this file that is ours")
    A("")
    A("🔴 **The join key.** No published model consumes HETUS, so which ACL code "
      "corresponds to")
    A("which CREST activity state is **our** correspondence and cannot be cited "
      "to anyone. It is")
    A("held in `acl_to_crest_activity.csv` so an author ruling edits DATA, never "
      "code. Rows whose")
    A("join is a name-for-name correspondence between two published code lists "
      "are labelled")
    A("`VALIDATED`; rows whose join required a judgement are labelled "
      "`NOT VALIDATED` and name the")
    A("decision item that owns them.")
    A("")
    A("| ACL | CREST state | status |")
    A("|---|---|---|")
    for cw in crosswalk:
        A("| `%s` | %d %s | %s |" % (cw["acl_code"],
                                     int(cw["crest_activity_index"]),
                                     cw["crest_activity_name"],
                                     cw["decision_status"]))
    A("")
    A("🔴 **Every DHW row is `NOT VALIDATED` by construction**, and not because "
      "its numbers are")
    A("doubtful: Jordan & Vajen distribute draw-offs by a probability function "
      "over year, weekday")
    A("and day, **not by a time-use code**. The parameters are theirs; the "
      "activity driver is ours.")
    A("")
    A("## Counts")
    A("")
    A("| quantity | value |")
    A("|---|---:|")
    A("| rows in the map | %d |" % stats["n_rows"])
    A("| distinct ACL codes present in the generated corpus | %d |"
      % stats["n_acl_codes_in_corpus"])
    A("| ACL codes carrying at least one electricity load | %d |"
      % stats["n_acl_codes_covered_by_a_load"])
    A("| share of modelled time under an ACL code that drives a load | %.3f %% |"
      % (100.0 * covered_time / total_min))
    A("| electricity rows | %d |" % stats["n_appliance_rows"])
    A("| DHW rows | %d |" % stats["n_dhw_rows"])
    A("| explicit no-load rows | %d |" % stats["n_no_load_rows"])
    A("| rows labelled VALIDATED | %d |" % stats["n_validated"])
    A("| rows labelled NOT VALIDATED | %d |" % stats["n_not_validated"])
    A("")
    A("## Artefacts")
    A("")
    A("| file | md5 |")
    A("|---|---|")
    A("| `sources/crest_appliances_richardsonpy.csv` | `%s` |" % stats["crest_md5"])
    A("| `sources/jordan_vajen_iea_task26_v2.0_2001.pdf` | `%s` |" % stats["jv_md5"])
    A("| `activity_appliance_map.csv` | `%s` |" % stats["map_md5"])
    A("")
    A("Corpus read: %s (%d modelled minutes)."
      % (", ".join("`%s`" % f for f in stats["generated_files"]), total_min))
    A("")
    io.open(path, "w", encoding="utf-8", newline="").write("\n".join(L))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--folds", default="es,uk,it")
    args = ap.parse_args(argv)
    stats = build(args.root, [f for f in args.folds.split(",") if f])
    for k in ("n_rows", "n_acl_codes_in_corpus", "n_acl_codes_covered_by_a_load",
              "n_appliance_rows", "n_dhw_rows", "n_no_load_rows",
              "n_validated", "n_not_validated"):
        print("%-38s %s" % (k, stats[k]))
    print("%-38s %s" % ("map md5", stats["map_md5"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
