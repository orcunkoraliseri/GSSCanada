#!/usr/bin/env python3
"""
4J Step 1 validation -- gates G1.1 to G1.11 (fourteen IDs, G1.7 split into
a/b/c/d) and the perturbation battery, Italy.

Implements Step1_docs/4thJ_01_corpusAcquisition_val.md exactly as
pre-registered, adapted to an Italian, tab-delimited, native-episode
delivery per Prompts/4thJ_employee_step1_italy_2026-08-14.md.

🔴 This file does NOT import 4thJ_read_italy.py. Column names for
G1.7d and G1.11 are re-transcribed independently below, from ISTAT's own
Tracciato HTML files, read again from scratch here rather than reused as a
Python object from the reader. The reader's own column list is printed
alongside this file's own column list so a human can compare them by eye
(TASK 3.0's requirement, translated from Spain's byte-offset re-transcription
to a delimited file's name-based equivalent).

Usage:
    python 4thJ_gates_step1_italy.py --out <outputs_step1 dir> --raw <unpacked dir>
"""

import argparse
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

NOT_CHECKED = "NOT CHECKED"

# ---- pre-registered constants, from codebook_facts_italy.md -------------
ISTAT_DIARIO_RECORDS = 1077657      # !Leggimi.html, "Totale record"
DAY_MINUTES = 1440
SLOT_MINUTES = 10
ITALY_DIARY_DAYS = 1                 # codebook_facts_italy.md: measured and asserted
WEIGHT_MAX = 10 ** 8                 # 12-digit field, 4 implied decimals -> 8 integer digits
WEIGHT_MIN = 1.0

# ---------------------------------------------------------------------------
# INDEPENDENT column re-transcription, for G1.7d and G1.11 only. Transcribed
# a second time, in this file, directly from
# METADATI\uso_tempo_Tracciato_Anno 2013_DiarioGiornaliero.html (rows 1-26)
# and METADATI\uso_tempo_Tracciato_Anno 2013_Individui.html (rows 1-2, 18-19),
# NOT copied from 4thJ_read_italy.py's DIARIO_COLS / INDIVIDUI_KEY_COLS
# constants as a Python object.
# ---------------------------------------------------------------------------
GATE_DIARIO_COLS = [
    "rilev", "anno", "meseri", "profam", "proind", "gsett", "ordepi",
    "oraini", "minini", "orafin", "minfin", "catpri", "catcon", "cluogo",
    "daso", "cmadre", "cpadre", "cconiu", "cfigli", "cfrate", "afacon",
    "aperco", "causi", "bestus", "pc_internet1", "pc_internet2",
]
GATE_INDIVIDUI_KEY_COLS = ["profam", "proind", "coefin", "coefi2"]
GATE_COPRESENCE = ["daso", "cmadre", "cpadre", "cconiu", "cfigli", "cfrate", "afacon", "aperco"]


class Result:
    def __init__(self):
        self.rows = []

    def add(self, gid, status, detail):
        self.rows.append((gid, status, detail))

    def ids(self):
        return [g for g, _, _ in self.rows]


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_raw_diario(raw_dir):
    """Re-read DiarioGiornaliero.txt independently, by this file's own
    column list, never via 4thJ_read_italy.py."""
    path = os.path.join(raw_dir, "MICRODATI",
                         "uso_tempo_Microdati_Anno_2013_DiarioGiornaliero.txt")
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="cp1252")
    got = list(df.columns)
    if got != GATE_DIARIO_COLS:
        raise SystemExit(f"gate runner's own transcription of DiarioGiornaliero's "
                          f"header does not match what is on disk: got {got}")
    df["pid"] = df["profam"] + "_" + df["proind"]
    return df


def read_raw_individui_weights(raw_dir):
    path = os.path.join(raw_dir, "MICRODATI",
                         "uso_tempo_Microdati_Anno_2013_Individui.txt")
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False,
                      encoding="cp1252", usecols=GATE_INDIVIDUI_KEY_COLS)
    df["pid"] = df["profam"] + "_" + df["proind"]
    return df[["pid", "coefin", "coefi2"]]


def act2_nonblank_count(ep):
    col = ep["act2_raw"]
    return int((col.notna() & (col != "")).sum())


def weighted_person_table(ep):
    per = ep.groupby("pid", sort=False).agg(
        diary_day=("diary_day", "first"),
        weight_ind=("weight_ind", "first"),
        weight_dia=("weight_dia", "first"),
        total_min=("duration_min", "sum"),
    ).reset_index()
    return per


def gate_g17d(raw_ind, respondent_pids):
    """Magnitude vs the declared layout (12 digits, 4 implied decimals),
    computed from the RAW strings in Individui.txt, independent of the
    reader. Restricted to the diary-respondent population (the same one
    G1.9/G1.1 use), because the 3,637 non-respondent rows in Individui carry
    a blank coefi2 (not a weight the diary design ever produced for them)."""
    resp = set(respondent_pids)
    sub = raw_ind.loc[raw_ind["pid"].isin(resp)]
    vals = []
    for col in ("coefin", "coefi2"):
        s = sub[col].str.strip()
        s = s[s != ""]
        if len(s):
            vals.append(s.astype("int64") / 1e4)
    if not vals:
        return NOT_CHECKED, "no weight values found in the raw file for the respondent population"
    allv = pd.concat(vals, ignore_index=True)
    vmin, vmax, ndist = float(allv.min()), float(allv.max()), int(allv.nunique())
    ok = bool((allv >= WEIGHT_MIN).all() and (allv < WEIGHT_MAX).all())
    detail = (f"observed min {vmin:.4f}, max {vmax:.4f}, {ndist} distinct values "
              f"(coefin+coefi2 pooled, raw Individui.txt); bounds [{WEIGHT_MIN}, {WEIGHT_MAX})")
    return ("PASS" if ok else "FAIL"), detail


def gate_g111(raw_diario, ep):
    """Secondary-activity three-state integrity. Italy ships native
    episodes -- no slot-to-episode collapsing occurs, so the independent
    recount is a direct count of non-blank catcon in the raw file (right/
    left-stripped, the SAME blank convention as the reader: a run of spaces
    strips to ""), compared against what is actually stored as non-blank
    act2_raw in the emitted table. No aggregation, no first-of-run rule --
    that is Spain's problem, not Italy's, because Italy's raw grain IS the
    episode grain."""
    catcon_stripped = raw_diario["catcon"].str.strip()
    raw_recount = int((catcon_stripped != "").sum())
    emitted_count = act2_nonblank_count(ep)
    ok = (raw_recount == emitted_count)
    detail = (f"independent recount from raw DiarioGiornaliero.txt (own column "
              f"resolution, blank convention = strip to \"\", same as the reader; "
              f"no episode reconstruction needed -- Italy ships native episodes): "
              f"{raw_recount} non-blank catcon rows; emitted episode table: "
              f"{emitted_count} non-blank act2_raw episodes.")
    return ("PASS" if ok else "FAIL"), detail


def run_gates(ep, raw_diario, raw_ind, ctx):
    R = Result()
    per = weighted_person_table(ep)

    # ---- G1.1 row-count reconciliation (ISTAT's own !Leggimi.html count) --
    n_ep = len(ep)
    R.add("G1.1", "PASS" if n_ep == ISTAT_DIARIO_RECORDS else "FAIL",
          f"{n_ep} episodes against ISTAT's stated {ISTAT_DIARIO_RECORDS} "
          f"(!Leggimi.html, 'Totale record')")

    # ---- G1.2 duration closure ------------------------------------------
    bad = per.loc[per["total_min"] != DAY_MINUTES]
    R.add("G1.2", "PASS" if len(bad) == 0 else "FAIL",
          f"{len(bad)} of {len(per)} diaries do not sum to {DAY_MINUTES} min")

    # ---- G1.3 quantisation ----------------------------------------------
    nonq = int((ep["duration_min"] % SLOT_MINUTES != 0).sum())
    R.add("G1.3", "PASS" if nonq == 0 else "FAIL",
          f"{nonq} of {len(ep)} episode durations are not multiples of {SLOT_MINUTES}")

    # ---- G1.4 code-list membership ---------------------------------------
    acts, acts2, locs = ctx["act_codes"], ctx["act2_codes"], ctx["loc_codes"]
    a_bad = sorted(set(ep["act_raw"].unique()) - acts)
    l_bad = sorted(set(ep["loc_raw"].unique()) - locs)
    a2_col = ep["act2_raw"]
    a2_not_recorded = int(a2_col.isna().sum())
    a2_blank = int((a2_col == "").sum())
    a2_valued_mask = a2_col.notna() & (a2_col != "")
    a2_valued = int(a2_valued_mask.sum())
    a2_bad = sorted(set(a2_col[a2_valued_mask].unique()) - acts2)
    ok4 = not a_bad and not l_bad and not a2_bad
    R.add("G1.4", "PASS" if ok4 else "FAIL",
          f"act_raw codes outside list: {a_bad[:10]}; loc_raw codes outside: "
          f"{l_bad[:10]}; act2_raw codes outside catcon's OWN list (blanks "
          f"excluded): {a2_bad[:10]} | act2_raw states, country IT: "
          f"not_recorded={a2_not_recorded}, recorded_and_blank={a2_blank}, "
          f"recorded_with_value={a2_valued}")

    # ---- G1.5 parse completeness ------------------------------------------
    pr = ctx["parse_report"]
    if pr is None:
        R.add("G1.5", NOT_CHECKED, "no parse report on disk")
    else:
        claims_zero = "unexplained drops : 0" in pr
        R.add("G1.5", "PASS" if (claims_zero and n_ep == ISTAT_DIARIO_RECORDS) else "FAIL",
              f"parse report states zero unexplained drops: {claims_zero}; "
              f"{n_ep} episodes represented against {ISTAT_DIARIO_RECORDS} delivered")

    # ---- G1.6 provenance ---------------------------------------------------
    man = ctx["manifest"]
    if man is None:
        R.add("G1.6", NOT_CHECKED, "no acquisition manifest fragment on disk")
    else:
        problems = []
        for entry in man["files"]:
            p = entry["local_path"]
            if not os.path.exists(p):
                problems.append(f"{entry['name']}: missing on disk")
            elif md5_of(p) != entry["md5"]:
                problems.append(f"{entry['name']}: md5 recomputed does not match")
            url_ok = bool(entry.get("url")) and entry.get("url") != "NOT FOUND (see entry_point_note)"
            if not url_ok:
                problems.append(f"{entry['name']}: url NOT FOUND in the manifest "
                                 f"(no per-file source URL was ever printed by this "
                                 f"delivery -- see codebook_facts_italy.md / manifest "
                                 f"entry_point_note; not fabricated)")
        R.add("G1.6", "PASS" if not problems else "FAIL",
              f"{len(man['files'])} archives checked; problems: {problems}")

    # ---- G1.7a weight presence, sign and distinct-count --------------------
    w_dia, w_ind = per["weight_dia"], per["weight_ind"]
    w_dia_ok = w_dia.dropna()
    w_ind_ok = w_ind.dropna()
    positive = bool((w_dia_ok > 0).all()) and bool((w_ind_ok > 0).all())
    finite = bool(np.isfinite(w_dia_ok).all()) and bool(np.isfinite(w_ind_ok).all())
    ndist_dia, ndist_ind = int(w_dia_ok.nunique()), int(w_ind_ok.nunique())
    distinct_ok = ndist_dia > 1 and ndist_ind > 1
    n_missing = int(w_dia.isna().sum())
    R.add("G1.7a", "PASS" if (positive and finite and distinct_ok) else "FAIL",
          f"all present diary/individual weights strictly positive: {positive}, "
          f"finite: {finite}; distinct values -- weight_dia: {ndist_dia}, "
          f"weight_ind: {ndist_ind} (both must be > 1); {n_missing} respondents "
          f"with no diary weight (see codebook F-IT-13, measured 0 on real data)")

    # ---- G1.7b RETIRED. Permanently NOT CHECKED, never scored. -------------
    R.add("G1.7b", NOT_CHECKED,
          "NOT CHECKED, permanently -- Nota_metodologica-2013.pdf p.12 (section 5) "
          "calibrates sample weights to 32 known regional totals, 18 of which are "
          "the population by sex x nine age classes; summing those cells reproduces "
          "the national population total, so any weighted total compared against a "
          "population figure consistent with that same calibration cannot fail. No "
          "independent population reference is loaded for this comparison in any "
          "case (see G1.8 and codebook finding F-IT-10). Printed as evidence of "
          "nothing, kept visible so the hole it retired does not get re-invented.")

    # ---- G1.7c cross-file weight identity -----------------------------------
    R.add("G1.7c", NOT_CHECKED,
          "NOT CHECKED -- coefin/coefi2 exist only in Individui.txt. "
          "DiarioGiornaliero.txt and DiarioSettimanale.txt carry no weight "
          "column at all (measured: neither file's header contains coefin or "
          "coefi2, or any other weight-shaped field). There is no cross-file "
          "restatement to check bit-identity against; this is the delivery's "
          "own shape, not a threshold moved to avoid running the check "
          "(codebook finding F-IT-8).")

    # ---- G1.7d magnitude vs declared layout (raw, independent) -------------
    respondent_pids = ep["pid"].drop_duplicates()
    status7d, detail7d = gate_g17d(raw_ind, respondent_pids)
    R.add("G1.7d", status7d, detail7d)

    # ---- G1.8 demographic marginals -----------------------------------------
    R.add("G1.8", NOT_CHECKED,
          "NOT CHECKED, for two distinct and independently sufficient reasons "
          "(codebook findings F-IT-9 and F-IT-10). (1) Same calibration "
          "circularity as G1.7b: ISTAT's weights are calibrated to sex x nine "
          "age classes regionally (Nota_metodologica-2013.pdf p.12), which is "
          "exactly what this gate would test, so even a working reference could "
          "only detect a subsample presented as the full file, never a wrong "
          "weight -- the same narrowing Spain's G1.8 required. (2) No published "
          "Italian age x sex population table for the 2013-2014 wave exists "
          "anywhere in this delivery to use as that (already-narrowed) "
          "reference: Nota_metodologica-2013.pdf's own page numbers jump from "
          "printed p.26 to printed p.95 (pp.27-94 absent from this delivery), "
          "and the tables present after the jump (Prospetti 6.A-7.D) are "
          "unweighted sample counts, not weighted population figures. Not "
          "searched for online, per hard project rule.")

    # ---- G1.9 diary days per respondent -------------------------------------
    dpp_series = ep.groupby("pid")["diary_day"].nunique()
    measured = int(dpp_series.max()) if len(dpp_series) else 0
    measured_min = int(dpp_series.min()) if len(dpp_series) else 0
    stated = ctx["codebook_diary_days"]
    ok9 = (measured == ITALY_DIARY_DAYS and measured_min == ITALY_DIARY_DAYS
           and stated == ITALY_DIARY_DAYS)
    R.add("G1.9", "PASS" if ok9 else "FAIL",
          f"measured {measured_min}-{measured} diary day(s) per respondent, "
          f"codebook_facts states {stated}, Italy must read {ITALY_DIARY_DAYS}")

    # ---- G1.10 constant-field invariance -------------------------------------
    nm, ns = ep["mode"].nunique(), ep["scheme"].nunique()
    R.add("G1.10", "PASS" if (nm == 1 and ns == 1) else "FAIL",
          f"{nm} distinct mode value(s), {ns} distinct scheme value(s)")

    # ---- G1.11 secondary-activity three-state integrity (raw, independent) --
    status11, detail11 = gate_g111(raw_diario, ep)
    R.add("G1.11", status11, detail11)

    return R


# ---------------------------------------------------------------------------
# perturbations
# ---------------------------------------------------------------------------
def perturb(name, ep, raw_diario, raw_ind, ctx):
    ep = ep.copy()
    raw_diario = raw_diario  # not perturbed by any case below; kept for signature symmetry
    raw_ind = raw_ind
    ctx = dict(ctx)

    if name == "null":
        pass

    elif name == "drop_last_5pct_rows":
        ep = ep.iloc[: int(len(ep) * 0.95)].copy()

    elif name == "delete_one_episode":
        # delete a MID-diary episode (not the first or last of its pid) so the
        # deletion breaks duration closure rather than just shortening a run
        counts = ep.groupby("pid")["episode_index"].transform("count")
        mid_mask = (ep["episode_index"] > 0) & (ep["episode_index"] < counts - 1)
        i = ep.index[mid_mask][0]
        ep = ep.drop(index=i).copy()

    elif name == "duration_30_to_25":
        i = ep.index[(ep["duration_min"] == 30)][0]
        ep.loc[i, "duration_min"] = 25

    elif name == "act_to_99Z":
        ep.loc[ep.index[0], "act_raw"] = "99Z"

    elif name == "act2_to_99Z":
        mask = ep["act2_raw"].notna() & (ep["act2_raw"] != "")
        i = ep.index[mask][0]
        ep.loc[i, "act2_raw"] = "99Z"

    elif name == "act2_rewrite_nonblank_to_blank":
        mask = ep["act2_raw"].notna() & (ep["act2_raw"] != "")
        ep.loc[mask, "act2_raw"] = ""

    elif name == "reader_skips_silently":
        ctx["parse_report"] = (ctx["parse_report"] or "").replace(
            "unexplained drops : 0", "unexplained drops : 1")

    elif name == "corrupt_archive_byte":
        man = json.loads(json.dumps(ctx["manifest"]))
        man["files"][0]["md5"] = "0" * 32
        ctx["manifest"] = man

    elif name == "weight_negative_one":
        i = ep.index[0]
        ep.loc[i, "weight_dia"] = -1.0

    elif name == "weight_constant":
        ep["weight_dia"] = 1234.5

    elif name == "weight_divide_1e4":
        # single-file analogue of Spain's "divide by 1e4 in every file that
        # carries it" -- Italy carries the weight in one file only (G1.7c
        # NOT CHECKED), so this is applied to the raw Individui table G1.7d
        # reads independently, for exactly one respondent, in both weight
        # columns so it is visible regardless of which one G1.7d pools first.
        pid0 = raw_ind["pid"].iloc[0]
        raw_ind = raw_ind.copy()
        idx = raw_ind.index[raw_ind["pid"] == pid0]
        for col in ("coefin", "coefi2"):
            raw = raw_ind.loc[idx[0], col]
            if raw.strip() != "":
                new_int = int(raw) // 10_000
                raw_ind.loc[idx[0], col] = f"{new_int:012d}"

    elif name == "drop_over_65":
        # G1.8's pre-registered coverage case. G1.8 is NOT CHECKED for Italy
        # (F-IT-9/F-IT-10), so this case cannot "attribute" to a scored gate;
        # kept in the set per the work order ("every case in that table
        # applies") to measure what it moves regardless.
        age_lo = ep["claseta2"].isin(["10", "11"])  # 65-74, 75+
        ep = ep.loc[~age_lo].copy()

    elif name == "declare_italy_2_days":
        ctx["codebook_diary_days"] = 2

    elif name == "second_mode_value":
        ep.loc[ep.index[0], "mode"] = "web_diary"

    else:
        raise ValueError(name)

    return ep, raw_diario, raw_ind, ctx


PERTURBATIONS = [
    ("null", "nothing may fail"),
    ("drop_last_5pct_rows", "G1.1"),
    ("delete_one_episode", "G1.2"),
    ("duration_30_to_25", "G1.3"),
    ("act_to_99Z", "G1.4"),
    ("act2_to_99Z", "G1.4"),
    ("reader_skips_silently", "G1.5"),
    ("corrupt_archive_byte", "G1.6"),
    ("weight_negative_one", "G1.7a"),
    ("weight_constant", "G1.7a"),
    ("weight_divide_1e4", "G1.7d"),
    ("drop_over_65", "G1.8 (NOT CHECKED for Italy -- see detail)"),
    ("declare_italy_2_days", "G1.9"),
    ("second_mode_value", "G1.10"),
    ("act2_rewrite_nonblank_to_blank", "G1.11"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw", required=True,
                     help="dir containing MICRODATI/ and METADATI/ (the unpacked zip)")
    args = ap.parse_args()
    out = args.out
    log = []

    def say(s=""):
        log.append(s)

    # ---- V1.b: everything read, with hashes, before any verdict ------------
    say("=" * 78)
    say("INPUTS (V1.b: printed before any verdict)")
    say("=" * 78)
    inputs = {
        "episodes": os.path.join(out, "episodes_italy.parquet"),
        "activity list (catpri)": os.path.join(out, "crosswalk_source_italy_activity.csv"),
        "activity2 list (catcon)": os.path.join(out, "crosswalk_source_italy_activity2.csv"),
        "location list (cluogo)": os.path.join(out, "crosswalk_source_italy_location.csv"),
        "parse report": os.path.join(out, "parse_report_italy.txt"),
        "manifest fragment": os.path.join(out, "acquisition_manifest_italy.json"),
        "codebook facts": os.path.join(out, "codebook_facts_italy.md"),
    }
    for k, p in inputs.items():
        if os.path.exists(p):
            say(f"  {k:26s} {os.path.getsize(p):>10d} bytes  md5 {md5_of(p)}")
        else:
            say(f"  {k:26s} {'MISSING':>10s}")
    say()

    ep = pd.read_parquet(inputs["episodes"])
    acts = pd.read_csv(inputs["activity list (catpri)"], dtype=str)
    acts2 = pd.read_csv(inputs["activity2 list (catcon)"], dtype=str)
    locs = pd.read_csv(inputs["location list (cluogo)"], dtype=str)

    parse_report = None
    if os.path.exists(inputs["parse report"]):
        with open(inputs["parse report"], encoding="utf-8") as fh:
            parse_report = fh.read()
    manifest = None
    if os.path.exists(inputs["manifest fragment"]):
        with open(inputs["manifest fragment"], encoding="utf-8") as fh:
            manifest = json.load(fh)

    say("=" * 78)
    say("INDEPENDENT COLUMN RE-TRANSCRIPTION (this file's own, re-declared from")
    say("the Tracciato HTML files; 4thJ_read_italy.py is not imported anywhere below)")
    say("=" * 78)
    say(f"  DiarioGiornaliero, this file's own list ({len(GATE_DIARIO_COLS)} cols):")
    say(f"    {GATE_DIARIO_COLS}")
    say(f"  Individui, this file's own key-column list ({len(GATE_INDIVIDUI_KEY_COLS)} cols):")
    say(f"    {GATE_INDIVIDUI_KEY_COLS}")
    say("  Compare this against the column lists declared independently at the top")
    say("  of 4thJ_read_italy.py (DIARIO_COLS, INDIVIDUI_KEY_COLS), by eye.")
    say()

    raw_diario = read_raw_diario(args.raw)
    raw_ind = read_raw_individui_weights(args.raw)
    say(f"  read DiarioGiornaliero.txt  {len(raw_diario):>9d} rows, own column list")
    say(f"  read Individui.txt (subset) {len(raw_ind):>9d} rows, own column list")
    say()

    # ---- sentinel check: "99Z" genuinely outside BOTH lists -----------------
    say("=" * 78)
    say("SENTINEL CHECK (perturbations act_to_99Z / act2_to_99Z)")
    say("=" * 78)
    sentinel = "99Z"
    in_catpri = sentinel in set(acts["code"])
    in_catcon = sentinel in set(acts2["code"])
    say(f"  sentinel chosen: {sentinel!r}")
    say(f"  present in catpri's transcribed list (146 codes)? {in_catpri}")
    say(f"  present in catcon's transcribed list (34 codes)?  {in_catcon}")
    if in_catpri or in_catcon:
        raise SystemExit("chosen sentinel is a real code in at least one list; "
                          "perturbation cannot fire as designed, refusing to run")
    say("  Confirmed absent from both lists -- catpri and catcon are different")
    say("  classifications (codebook finding F-IT-3) and each was checked on its own.")
    say()

    ctx = {
        "act_codes": set(acts["code"]),
        "act2_codes": set(acts2["code"]),
        "loc_codes": set(locs["code"]),
        "parse_report": parse_report,
        "manifest": manifest,
        "codebook_diary_days": 1,   # from codebook_facts_italy.md
    }

    say(f"  episodes loaded          : {len(ep)} rows, {ep['pid'].nunique()} diary respondents")
    say(f"  catpri codes loaded      : {len(ctx['act_codes'])}")
    say(f"  catcon codes loaded      : {len(ctx['act2_codes'])}")
    say(f"  cluogo codes loaded      : {len(ctx['loc_codes'])}")
    say()

    # ---- V1.a: the battery must know how many countries it scanned ---------
    countries = sorted(ep["country"].unique())
    v1a = "FIRED" if len(countries) < 4 else "clear"
    say("=" * 78)
    say("VACUITY GUARDS")
    say("=" * 78)
    say(f"  V1.a  countries scanned: {countries} ({len(countries)} of 4) -> {v1a}")
    say("        This is a one-country round by design (Italy only, per the work")
    say("        order). V1.a firing is correct behaviour and is reported, not")
    say("        escaped with a single-country flag.")
    say("  V1.b  inputs, sizes and md5s printed above, before any verdict.")
    say("  V1.c  every status below comes from the computation that produced it;")
    say("        a gate that could not run prints NOT CHECKED.")
    say("  V1.d  enforced inside the reader (4thJ_read_italy.py): unrecognised")
    say("        codes and out-of-domain co-presence values raise and stop.")
    say()

    # ---- baseline ------------------------------------------------------------
    base = run_gates(ep, raw_diario, raw_ind, ctx)
    say("=" * 78)
    say("GATES ON THE REAL DATA")
    say("=" * 78)
    for gid, status, detail in base.rows:
        say(f"  {gid:6s} {status:11s} {detail}")
    say()
    base_status = {gid: status for gid, status, _ in base.rows}
    baseline_failures = {gid for gid, status, _ in base.rows if status == "FAIL"}
    if baseline_failures:
        say(f"  🔴 BASELINE ALREADY CONTAINS A FAIL: {sorted(baseline_failures)}.")
        say("     This is not a perturbation artefact; see the gate detail above and")
        say("     codebook_facts_italy.md / the manifest fragment's entry_point_note.")
        say()

    # ---- perturbations ---------------------------------------------------------
    say("=" * 78)
    say("PERTURBATION BATTERY (a gate is trusted once it has been seen failing)")
    say("=" * 78)
    fell = {gid: [] for gid in base.ids()}
    for name, expected in PERTURBATIONS:
        pep, praw_diario, praw_ind, pctx = perturb(name, ep, raw_diario, raw_ind, ctx)
        res = run_gates(pep, praw_diario, praw_ind, pctx)
        failed = {g for g, s, _ in res.rows if s == "FAIL"}
        # Only count a gate as "made to fall by" a perturbation if the
        # perturbation is what newly broke it -- a gate already FAILing at
        # baseline (G1.6, here) trivially shows up in `failed` under every
        # perturbation, which would otherwise credit unrelated perturbations
        # with shaking a gate that was never PASSing to begin with.
        for g in (failed - baseline_failures):
            fell[g].append(name)
        if name == "null":
            # A gate that already FAILs on real data is not "moved" by a
            # perturbation that changes nothing; the correct null-case check
            # is that the FAILing set is UNCHANGED from baseline, which is
            # the general form of "nothing may fail" and coincides with it
            # whenever the baseline itself is clean (as it was for Spain).
            ok = (failed == baseline_failures)
            verdict = "as pre-registered (failing set unchanged)" if ok else \
                      f"🔴 NULL PERTURBATION MOVED A GATE: {sorted(failed - baseline_failures)} newly failed, {sorted(baseline_failures - failed)} newly cleared"
        else:
            newly = failed - baseline_failures
            ok = (expected in newly) if not expected.startswith("G1.8") else False
            extra = [g for g in newly if g != expected]
            if expected.startswith("G1.8"):
                verdict = f"G1.8 is NOT CHECKED; case kept for parity, moved: {sorted(newly)}"
            else:
                verdict = ("as pre-registered" if ok and not extra else
                           "attributes cleanly" if ok else "DID NOT FIRE")
                if ok and extra:
                    verdict = f"fired, and also newly moved {extra}"
        say(f"  {name:32s} expected {expected:40s} newly-failed {sorted(failed - baseline_failures)}")
        say(f"  {'':32s} -> {verdict}")
        if name == "corrupt_archive_byte" and not ok:
            say(f"  {'':32s}    NOTE: G1.6 already FAILs at baseline (missing url), so this")
            say(f"  {'':32s}    perturbation cannot demonstrate anything -- it is not exempt")
            say(f"  {'':32s}    from the clause because it PASSES nowhere to be shaken from.")
    say()

    # ---- coverage clause ---------------------------------------------------------
    say("=" * 78)
    say("COVERAGE CLAUSE")
    say("=" * 78)
    uncovered = []
    for gid, status, _ in base.rows:
        if status == "PASS" and not fell[gid]:
            uncovered.append(gid)
    for gid, status, _ in base.rows:
        mark = ("never fell" if not fell[gid] else ", ".join(fell[gid]))
        say(f"  {gid:6s} baseline {status:11s} made to fall by: {mark}")
    say()
    if uncovered:
        say(f"  🔴 PROBE FAILS. These gates PASS on the real data and nothing in")
        say(f"     the set ever made them fall: {uncovered}")
    else:
        say("  Every gate that PASSes on the real data was made to fall by at")
        say("  least one perturbation. Coverage clause satisfied.")
        say("  (Gates already FAILing at baseline -- see above -- and NOT CHECKED")
        say("   gates are outside the clause by construction: the clause only")
        say("   binds gates that PASS on the real data.)")
    say()

    seen = sum(1 for g in base.ids() if fell[g])
    scored = [g for g, s, _ in base.rows if s in ("PASS", "FAIL")]
    say("=" * 78)
    say("SUMMARY")
    say("=" * 78)
    say(f"  gates scored          : {len(scored)}  {scored}")
    say(f"  gates NOT CHECKED     : {[g for g, s, _ in base.rows if s == NOT_CHECKED]}")
    say(f"  gates PASS            : {sum(1 for g, s, _ in base.rows if s == 'PASS')}")
    say(f"  gates FAIL            : {sum(1 for g, s, _ in base.rows if s == 'FAIL')}")
    say(f"  gates seen failing    : {seen} of {len(scored)}")
    say(f"  V1.a                  : {v1a} (expected to fire on a one-country round)")

    txt = "\n".join(log) + "\n"
    with open(os.path.join(out, "gate_report_step1_italy.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(txt)
    try:
        print(txt)
    except UnicodeEncodeError:
        print(txt.encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
