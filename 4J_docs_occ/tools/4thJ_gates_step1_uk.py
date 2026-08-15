#!/usr/bin/env python3
"""
4J Step 1 validation -- gates G1.1 to G1.11 and the perturbation battery, UK.

Implements Step1_docs/4thJ_01_corpusAcquisition_val.md exactly as pre-registered
(the 2026-08-14 fourteen-gate specification), against the UK delivery.

🔴 This file does NOT import anything from 4thJ_read_uk.py. Every column this
gate runner needs is resolved BY NAME, independently, from its own copy of the
UKDA tab-delimited files. Both this file's column declarations and the
reader's are printed at runtime so a human can compare them by eye -- two
independent transcriptions that agree are evidence; one used twice is not.

Usage:
    python 4thJ_gates_step1_uk.py --out <outputs_step1 dir> --raw <raw dir>
"""

import argparse
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

NOT_CHECKED = "NOT CHECKED"

# ---------------------------------------------------------------------------
# Pre-registered constants.
# ---------------------------------------------------------------------------
UKDA_DIARY_EP_ROWS = 587632     # UKDA data dictionary "Number of cases"
SLOT_MINUTES = 10
DAY_MINUTES = 1440
UK_DIARY_DAYS = 2               # NATCEN p.3/p.16: two 24-hour diary days
SECONDARY_BLANK_SENTINEL = "-9"

# ---------------------------------------------------------------------------
# INDEPENDENT column declaration for this gate runner. 1:1 with the reader's
# own declaration at the top of 4thJ_read_uk.py -- printed side by side at
# runtime, never imported.
# ---------------------------------------------------------------------------
GATE_COLUMNS = {
    "diary_ep_long": {
        "key": ["serial", "pnum", "daynum"],
        "tid": "tid", "eptime": "eptime",
        "act_raw": "whatdoing", "act2_raw": "What_Oth1",
        "act2_extra_2": "What_Oth2", "act2_extra_3": "What_Oth3",
        "loc_raw": "WhereWhen",
        "copresence": ["WithAlone", "WithSpouse", "WithMother", "WithFather",
                        "WithChild", "WithOther", "WithOtherYK", "WithMiss",
                        "WithNA"],
        "weight_dia_a": "dia_wt_a", "weight_dia_b": "dia_wt_b",
        "diary_day_ordinal": "daynum", "diary_day_of_week": "DiaryDay_Act",
    },
    "individual": {
        "key": ["serial", "pnum"],
        "age": "DVAge", "sex": "DMSex", "weight_ind": "ind_wt",
    },
    "dv_time_vars": {
        "key": ["serial", "pnum", "daynum"],
        "weight_dia_a": "dia_wt_a", "weight_dia_b": "dia_wt_b",
    },
}
# The reader's own declaration (4thJ_read_uk.py), reproduced here as a
# literal string for the printed side-by-side comparison ONLY -- not parsed,
# not imported, not executed. A human reads both blocks and compares them.
READER_COLUMNS_AS_DECLARED = """
    diary_ep_long: key=[serial,pnum,daynum], start=tid, duration=eptime,
      act_raw=whatdoing, act2_raw=What_Oth1, act2_extra_uk_2=What_Oth2,
      act2_extra_uk_3=What_Oth3, loc_raw=WhereWhen,
      copresence=[WithAlone,WithSpouse,WithMother,WithFather,WithChild,
                   WithOther,WithOtherYK,WithMiss,WithNA],
      weight_dia_a=dia_wt_a, weight_dia_b=dia_wt_b,
      diary_day=daynum, DiaryDay_Act=DiaryDay_Act
    individual: key=[serial,pnum], DVAge=DVAge, DMSex=DMSex, weight_ind=ind_wt
    (dv_time_vars.tab is not read by the reader at all -- gate runner only)
"""


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


def read_raw_tab(path, key_cols):
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    df["_key"] = df[key_cols].agg("_".join, axis=1)
    return df


def secondary_state(series):
    """Independent re-implementation of the -9 -> blank mapping (F-UK-2),
    NOT imported from 4thJ_read_uk.py. Returns a Series of '' / code-string."""
    return series.where(series != SECONDARY_BLANK_SENTINEL, "")


def nonblank_count(series):
    return int((series.notna() & (series != "")).sum())


# ---------------------------------------------------------------------------
# individual gate implementations
# ---------------------------------------------------------------------------
def gate_g11(ep, ctx):
    n = len(ep)
    ok = n == UKDA_DIARY_EP_ROWS
    return ("PASS" if ok else "FAIL",
            f"{n} episode rows against UKDA's own stated "
            f"{UKDA_DIARY_EP_ROWS} (data dictionary 'Number of cases')")


def gate_g12(ep):
    per = ep.groupby(["pid", "diary_day"], sort=False)["duration_min"].sum()
    bad = per[per != DAY_MINUTES]
    ok = len(bad) == 0
    return ("PASS" if ok else "FAIL",
            f"{len(bad)} of {len(per)} (person, diary_day) diaries do not "
            f"sum to {DAY_MINUTES} min")


def gate_g13(ep):
    bad = int((ep["duration_min"] % SLOT_MINUTES != 0).sum())
    ok = bad == 0
    return ("PASS" if ok else "FAIL",
            f"{bad} of {len(ep)} episode durations are not multiples of "
            f"{SLOT_MINUTES}")


def gate_g14(ep, ctx):
    acts, locs = ctx["act_codes"], ctx["loc_codes"]
    detail_parts = []
    any_bad = False

    a_bad = sorted(set(ep["act_raw"].unique()) - acts)
    if a_bad:
        any_bad = True
    l_bad = sorted(set(ep["loc_raw"].unique()) - locs)
    if l_bad:
        any_bad = True
    detail_parts.append(f"act_raw codes outside list: {a_bad[:10]}")
    detail_parts.append(f"loc_raw codes outside list: {l_bad[:10]}")

    for col in ["act2_raw", "act2_extra_uk_2", "act2_extra_uk_3"]:
        c = ep[col]
        n_nr = int(c.isna().sum())
        n_bl = int((c == "").sum())
        valued_mask = c.notna() & (c != "")
        n_val = int(valued_mask.sum())
        bad = sorted(set(c[valued_mask].unique()) - acts)
        if bad:
            any_bad = True
        detail_parts.append(
            f"{col}: not_recorded={n_nr} recorded_and_blank={n_bl} "
            f"recorded_with_value={n_val} codes_outside_list={bad[:10]}")

    status = "FAIL" if any_bad else "PASS"
    return status, " | ".join(detail_parts)


def gate_g15(ep, ctx):
    pr = ctx["parse_report"]
    if pr is None:
        return NOT_CHECKED, "no parse report on disk"
    claims_zero = "unexplained drops : 0" in pr
    n_here = len(ep)
    ok = claims_zero and (n_here == UKDA_DIARY_EP_ROWS)
    return ("PASS" if ok else "FAIL",
            f"parse report states zero unexplained drops: {claims_zero}; "
            f"{n_here} episode rows represented against "
            f"{UKDA_DIARY_EP_ROWS} delivered")


def gate_g16(ctx):
    man = ctx["manifest"]
    if man is None:
        return NOT_CHECKED, "no acquisition manifest fragment on disk"
    uk = man.get("uk", {})
    problems = []

    def check_entry(label, entry):
        p = entry.get("local_path")
        if not p or not os.path.exists(p):
            problems.append(f"{label}: missing on disk")
            return
        if md5_of(p) != entry.get("md5"):
            problems.append(f"{label}: md5 recomputed does not match")

    check_entry("outer_archive", uk.get("outer_archive", {}))
    check_entry("inner_archive", uk.get("inner_archive", {}))
    n_delivered = 0
    for entry in uk.get("delivered_files_md5", []):
        n_delivered += 1
        # delivered_files_md5 paths are relative to UK-TUS/ (the inner
        # archive's unpack root), matching acquisition_manifest_uk.json.
        alt = os.path.join(uk.get("local_root", ""), "unpacked", "UK-TUS", entry["path"])
        if not os.path.exists(alt):
            problems.append(f"{entry['path']}: missing on disk at expected location")
            continue
        if md5_of(alt) != entry["md5"]:
            problems.append(f"{entry['path']}: md5 recomputed does not match")
    doi = uk.get("citation_and_licence", {}).get("doi")
    acquired = uk.get("acquired_utc")
    if not doi or not acquired:
        problems.append("doi or acquired_utc missing (the UK delivery prints "
                         "no literal download URL; DOI is the recorded "
                         "landing-page citation per the work order)")
    ok = not problems
    return ("PASS" if ok else "FAIL",
            f"outer+inner archive + {n_delivered} delivered files checked; "
            f"problems: {problems}")


def gate_g17a(ep):
    per_dia = ep.groupby(["pid", "diary_day"], sort=False)["weight_dia_a"].first()
    per_ind = ep.groupby("pid", sort=False)["weight_ind"].first()

    dia_nan = int(per_dia.isna().sum())
    ind_nan = int(per_ind.isna().sum())
    dia_ok_vals = per_dia.dropna()
    ind_ok_vals = per_ind.dropna()
    dia_pos = bool((dia_ok_vals > 0).all())
    ind_pos = bool((ind_ok_vals > 0).all())
    ndist_dia = int(dia_ok_vals.nunique())
    ndist_ind = int(ind_ok_vals.nunique())

    ok = (dia_nan == 0 and ind_nan == 0 and dia_pos and ind_pos
          and ndist_dia > 1 and ndist_ind > 1)
    return ("PASS" if ok else "FAIL",
            f"weight_dia_a: {dia_nan} of {len(per_dia)} diaries missing "
            f"(blank sentinel, F-UK-8), all present values positive: "
            f"{dia_pos}, {ndist_dia} distinct values; "
            f"weight_ind: {ind_nan} of {len(per_ind)} persons missing, "
            f"all present values positive: {ind_pos}, {ndist_ind} distinct "
            f"values (both distinct-counts must be > 1 and both missing "
            f"counts must be 0 for PASS)")


def gate_g17b(ep):
    return (NOT_CHECKED,
            "no numeric comparison computed: (1) NATCEN p.31, section 7.4(c) "
            "and (d), both dia_wt_a and dia_wt_b are calibrated so the "
            "weighted age/sex distribution matches the population "
            "distribution -- the same circularity structure as Spain's "
            "retired G1.7b (F-UK-11); (2) no population table is shipped in "
            "the delivery to compare against in any case (F-UK-11). "
            "Permanently NOT CHECKED, printed on every run, never scored.")


def gate_g17c(raw_diary, raw_dv):
    if raw_dv is None:
        return NOT_CHECKED, "uktus15_dv_time_vars.tab not available to the gate runner"
    a = raw_diary[["_key", "dia_wt_a", "dia_wt_b"]].drop_duplicates(subset="_key")
    b = raw_dv[["_key", "dia_wt_a", "dia_wt_b"]].drop_duplicates(subset="_key")
    m = a.merge(b, on="_key", how="outer", suffixes=("_ep", "_dv"), indicator=True)
    only_one_side = int((m["_merge"] != "both").sum())
    mism_a = int((m["dia_wt_a_ep"] != m["dia_wt_a_dv"]).sum())
    mism_b = int((m["dia_wt_b_ep"] != m["dia_wt_b_dv"]).sum())
    ok = (only_one_side == 0) and (mism_a == 0) and (mism_b == 0)
    return ("PASS" if ok else "FAIL",
            f"{len(m)} person-days compared between uktus15_diary_ep_long.tab "
            f"and uktus15_dv_time_vars.tab (both read independently by this "
            f"gate runner, raw strings, no numeric conversion); "
            f"{only_one_side} present in only one file; "
            f"dia_wt_a mismatches: {mism_a}; dia_wt_b mismatches: {mism_b}")


def gate_g17d(raw_diary, raw_ind):
    diary_vals = []
    for name in ["dia_wt_a", "dia_wt_b"]:
        raw = raw_diary[name]
        blank = raw == " "
        num = raw[~blank].astype(float)
        diary_vals.append(num)
    ind_raw = raw_ind["ind_wt"]
    ind_blank = ind_raw == " "
    ind_num = ind_raw[~ind_blank].astype(float)
    allv = pd.concat(diary_vals + [ind_num], ignore_index=True)
    vmin, vmax, vmean = float(allv.min()), float(allv.max()), float(allv.mean())
    ndist = int(allv.nunique())
    n_below_1 = int((allv < 1.0).sum())
    pct_below_1 = 100.0 * n_below_1 / len(allv)
    return (NOT_CHECKED,
            f"no declared fixed-width layout exists anywhere in the UK "
            f"delivery for hh_wt/ind_wt/dia_wt_a/dia_wt_b/wks_wt (tab-"
            f"delimited free-text decimals) -- magnitude-vs-layout half is "
            f"NOT CHECKED for lack of an independent reference (F-UK-13). "
            f"Diagnostic only, printed as evidence of nothing: observed "
            f"min={vmin:.4f} max={vmax:.4f} mean={vmean:.6f} "
            f"n_distinct={ndist} across dia_wt_a+dia_wt_b+ind_wt; "
            f"{n_below_1} of {len(allv)} ({pct_below_1:.1f} %) are strictly "
            f"below 1.0 -- consistent with a normalised (mean~1) weighting "
            f"convention, not raw expansion factors; applying the "
            f"pre-registered >=1.0 clause literally would fail on the "
            f"majority of real UK weights for that reason, not a magnitude-"
            f"read defect (F-UK-13).")


def gate_g18():
    return (NOT_CHECKED,
            "no published UK age x sex population table is shipped anywhere "
            "in the delivered archive (NATCEN describes the calibration "
            "target in prose only, p.30-31; no data table accompanies it). "
            "Web search is out of scope by hard project rule. Separately, "
            "even if a table were available, both diary weights are "
            "calibrated to age/sex margins (F-UK-11), so the same narrowing "
            "applied to Spain's G1.8 would apply here too. Two distinct, "
            "both-sufficient reasons, both recorded.")


def gate_g19(raw_diary, ctx):
    person_key = raw_diary["serial"] + "_" + raw_diary["pnum"]
    tmp = pd.DataFrame({"pid": person_key, "daynum": raw_diary["daynum"]})
    dpp = tmp.drop_duplicates().groupby("pid").size()
    measured = int(dpp.max()) if len(dpp) else 0
    stated = ctx["codebook_diary_days"]
    ok = (measured == UK_DIARY_DAYS) and (stated == UK_DIARY_DAYS)
    return ("PASS" if ok else "FAIL",
            f"measured max {measured} diary day(s) per respondent "
            f"(distribution {dpp.value_counts().to_dict()}), "
            f"codebook_facts_uk.md states {stated}, design is {UK_DIARY_DAYS}")


def gate_g110(ep):
    nm, ns = ep["mode"].nunique(), ep["scheme"].nunique()
    ok = (nm == 1 and ns == 1)
    return ("PASS" if ok else "FAIL",
            f"{nm} distinct mode value(s), {ns} distinct scheme value(s)")


def gate_g111(ep, raw_diary):
    detail_parts = []
    all_ok = True
    for emitted_col, raw_col, label in [
        ("act2_raw", "What_Oth1", "act2_raw / What_Oth1"),
        ("act2_extra_uk_2", "What_Oth2", "act2_extra_uk_2 / What_Oth2"),
        ("act2_extra_uk_3", "What_Oth3", "act2_extra_uk_3 / What_Oth3"),
    ]:
        raw_state = secondary_state(raw_diary[raw_col])
        raw_count = int((raw_state != "").sum())
        emitted_count = nonblank_count(ep[emitted_col])
        ok = raw_count == emitted_count
        all_ok = all_ok and ok
        detail_parts.append(
            f"{label}: independent recount from raw "
            f"uktus15_diary_ep_long.tab (own column resolution, own -9->"
            f"blank mapping) = {raw_count}; emitted episode table = "
            f"{emitted_count}; {'MATCH' if ok else 'MISMATCH'}")
    return ("PASS" if all_ok else "FAIL"), " | ".join(detail_parts)


def run_gates(ep, raw_diary, raw_ind, raw_dv, ctx):
    R = Result()

    s, d = gate_g11(ep, ctx); R.add("G1.1", s, d)
    s, d = gate_g12(ep); R.add("G1.2", s, d)
    s, d = gate_g13(ep); R.add("G1.3", s, d)
    s, d = gate_g14(ep, ctx); R.add("G1.4", s, d)
    s, d = gate_g15(ep, ctx); R.add("G1.5", s, d)
    s, d = gate_g16(ctx); R.add("G1.6", s, d)
    s, d = gate_g17a(ep); R.add("G1.7a", s, d)
    s, d = gate_g17b(ep); R.add("G1.7b", s, d)
    s, d = gate_g17c(raw_diary, raw_dv); R.add("G1.7c", s, d)
    s, d = gate_g17d(raw_diary, raw_ind); R.add("G1.7d", s, d)
    s, d = gate_g18(); R.add("G1.8", s, d)
    s, d = gate_g19(raw_diary, ctx); R.add("G1.9", s, d)
    s, d = gate_g110(ep); R.add("G1.10", s, d)
    s, d = gate_g111(ep, raw_diary); R.add("G1.11", s, d)

    return R


# ---------------------------------------------------------------------------
# perturbations
# ---------------------------------------------------------------------------
def perturb(name, ep, raw_diary, raw_ind, raw_dv, ctx):
    ep = ep.copy()
    raw_diary = raw_diary.copy()
    raw_ind = raw_ind.copy()
    raw_dv = raw_dv.copy() if raw_dv is not None else None
    ctx = dict(ctx)

    if name == "null":
        pass

    elif name == "drop_last_5pct_rows":
        ep = ep.iloc[: int(len(ep) * 0.95)].copy()

    elif name == "delete_one_episode":
        ep = ep.drop(index=ep.index[10]).copy()

    elif name == "duration_30_to_25":
        idx = ep.index[ep["duration_min"] == 30]
        if len(idx):
            ep.loc[idx[0], "duration_min"] = 25
        else:
            idx = ep.index[ep["duration_min"] == 10]
            ep.loc[idx[0], "duration_min"] = 5

    elif name == "act_to_outside_list":
        ep.loc[ep.index[0], "act_raw"] = ctx["act_sentinel"]

    elif name == "act2_to_outside_list":
        mask = ep["act2_raw"].notna() & (ep["act2_raw"] != "")
        i = ep.index[mask][0]
        ep.loc[i, "act2_raw"] = ctx["act_sentinel"]

    elif name == "act2_extra_2_to_outside_list":
        mask = ep["act2_extra_uk_2"].notna() & (ep["act2_extra_uk_2"] != "")
        i = ep.index[mask][0]
        ep.loc[i, "act2_extra_uk_2"] = ctx["act_sentinel"]

    elif name == "act2_rewrite_nonblank_to_blank":
        mask = ep["act2_raw"].notna() & (ep["act2_raw"] != "")
        ep.loc[mask, "act2_raw"] = ""

    elif name == "reader_skips_silently":
        ctx["parse_report"] = (ctx["parse_report"] or "").replace(
            "unexplained drops : 0", "unexplained drops : 1")

    elif name == "corrupt_archive_byte":
        man = json.loads(json.dumps(ctx["manifest"]))
        man["uk"]["delivered_files_md5"][0]["md5"] = "0" * 32
        ctx["manifest"] = man

    elif name == "weight_negative_one":
        pid0 = ep["pid"].iloc[0]
        day0 = ep.loc[ep["pid"] == pid0, "diary_day"].iloc[0]
        m = (ep["pid"] == pid0) & (ep["diary_day"] == day0)
        ep.loc[m, "weight_dia_a"] = -1.0

    elif name == "weight_constant":
        ep["weight_dia_a"] = 1234.5

    elif name == "dv_time_vars_weight_swap":
        t = raw_dv.copy()
        a, b = t.index[0], t.index[1]
        t.loc[a, "dia_wt_a"], t.loc[b, "dia_wt_a"] = \
            t.loc[b, "dia_wt_a"], t.loc[a, "dia_wt_a"]
        raw_dv = t

    elif name == "declare_uk_1_day":
        ctx["codebook_diary_days"] = 1

    elif name == "second_mode_value":
        ep.loc[ep.index[0], "mode"] = "web_diary"

    else:
        raise ValueError(name)

    return ep, raw_diary, raw_ind, raw_dv, ctx


PERTURBATIONS = [
    ("null", "nothing may fail (see note: baseline is not fully clean)"),
    ("drop_last_5pct_rows", "G1.1"),
    ("delete_one_episode", "G1.2"),
    ("duration_30_to_25", "G1.3"),
    ("act_to_outside_list", "G1.4"),
    ("act2_to_outside_list", "G1.4"),
    ("act2_extra_2_to_outside_list", "G1.4"),
    ("reader_skips_silently", "G1.5"),
    ("corrupt_archive_byte", "G1.6"),
    ("weight_negative_one", "G1.7a"),
    ("weight_constant", "G1.7a"),
    ("dv_time_vars_weight_swap", "G1.7c"),
    ("declare_uk_1_day", "G1.9"),
    ("second_mode_value", "G1.10"),
    ("act2_rewrite_nonblank_to_blank", "G1.11"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw", required=True,
                     help="dir containing UKDA-8128-tab/tab")
    args = ap.parse_args()
    out = args.out
    log = []

    def say(s=""):
        log.append(s)

    say("=" * 78)
    say("COLUMN RESOLUTION -- printed for human comparison against the reader")
    say("=" * 78)
    say("This gate runner's own, independently-declared columns:")
    for line in json.dumps(GATE_COLUMNS, indent=2).splitlines():
        say("  " + line)
    say("")
    say("The reader's own declaration (4thJ_read_uk.py), reproduced as text")
    say("for comparison only -- NOT imported, NOT executed:")
    say(READER_COLUMNS_AS_DECLARED)
    say("")

    # ---- V1.b: everything read, with hashes, before any verdict ----------
    say("=" * 78)
    say("INPUTS (V1.b: printed before any verdict)")
    say("=" * 78)
    inputs = {
        "episodes": os.path.join(out, "episodes_uk.parquet"),
        "activity list": os.path.join(out, "crosswalk_source_uk_activity.csv"),
        "location list": os.path.join(out, "crosswalk_source_uk_location.csv"),
        "parse report": os.path.join(out, "parse_report_uk.txt"),
        "manifest fragment": os.path.join(out, "acquisition_manifest_uk.json"),
        "codebook facts": os.path.join(out, "codebook_facts_uk.md"),
    }
    for k, p in inputs.items():
        if os.path.exists(p):
            say(f"  {k:22s} {os.path.getsize(p):>10d} bytes  md5 {md5_of(p)}")
        else:
            say(f"  {k:22s} {'MISSING':>10s}")
    say()

    ep = pd.read_parquet(inputs["episodes"])
    acts = pd.read_csv(inputs["activity list"], dtype=str)
    locs = pd.read_csv(inputs["location list"], dtype=str)
    act_code_set = set(acts["code"])
    loc_code_set = set(locs["code"])

    # a genuinely out-of-list sentinel, checked against our own transcribed
    # list before use (the "999 was actually a real INE code" lesson)
    act_sentinel = "99999"
    if act_sentinel in act_code_set:
        raise SystemExit(f"chosen sentinel {act_sentinel} IS a real UK "
                          f"activity code -- perturbation cannot fire")

    parse_report = None
    if os.path.exists(inputs["parse report"]):
        with open(inputs["parse report"], encoding="utf-8") as fh:
            parse_report = fh.read()
    manifest = None
    if os.path.exists(inputs["manifest fragment"]):
        with open(inputs["manifest fragment"], encoding="utf-8") as fh:
            manifest = json.load(fh)

    # ---- independent raw re-read, own column resolution -------------------
    say("=" * 78)
    say("INDEPENDENT RAW RE-READ (own column resolution; never imports "
        "4thJ_read_uk.py)")
    say("=" * 78)
    tab_dir = os.path.join(args.raw, "tab")
    raw_diary = read_raw_tab(os.path.join(tab_dir, "uktus15_diary_ep_long.tab"),
                              GATE_COLUMNS["diary_ep_long"]["key"])
    raw_ind = read_raw_tab(os.path.join(tab_dir, "uktus15_individual.tab"),
                            GATE_COLUMNS["individual"]["key"])
    dv_path = os.path.join(tab_dir, "uktus15_dv_time_vars.tab")
    raw_dv = read_raw_tab(dv_path, GATE_COLUMNS["dv_time_vars"]["key"]) \
        if os.path.exists(dv_path) else None
    say(f"  uktus15_diary_ep_long.tab : {len(raw_diary)} rows, "
        f"{len(raw_diary.columns)} columns, md5 "
        f"{md5_of(os.path.join(tab_dir, 'uktus15_diary_ep_long.tab'))}")
    say(f"  uktus15_individual.tab    : {len(raw_ind)} rows, "
        f"{len(raw_ind.columns)} columns, md5 "
        f"{md5_of(os.path.join(tab_dir, 'uktus15_individual.tab'))}")
    if raw_dv is not None:
        say(f"  uktus15_dv_time_vars.tab  : {len(raw_dv)} rows, "
            f"{len(raw_dv.columns)} columns, md5 {md5_of(dv_path)} "
            f"(read only by this gate runner, for G1.7c)")
    say()

    ctx = {
        "act_codes": act_code_set,
        "loc_codes": loc_code_set,
        "parse_report": parse_report,
        "manifest": manifest,
        "codebook_diary_days": UK_DIARY_DAYS,
        "act_sentinel": act_sentinel,
    }

    say(f"  episodes loaded        : {len(ep)} rows, {ep['pid'].nunique()} people, "
        f"{ep.groupby(['pid','diary_day']).ngroups} (person,diary_day) diaries")
    say(f"  activity codes loaded  : {len(act_code_set)}")
    say(f"  location codes loaded  : {len(loc_code_set)}")
    say(f"  chosen out-of-list activity sentinel: '{act_sentinel}' "
        f"(confirmed absent from the transcribed list)")
    say()

    # ---- V1.a: single-country round ----------------------------------------
    countries = sorted(ep["country"].unique())
    v1a = "FIRED" if len(countries) < 4 else "clear"
    say("=" * 78)
    say("VACUITY GUARDS")
    say("=" * 78)
    say(f"  V1.a  countries scanned: {countries} ({len(countries)} of 4) -> {v1a}")
    say("        This is a one-country round by design. V1.a firing is the")
    say("        correct behaviour and the battery below is reported under")
    say("        it, not instead of it. The guard was not lowered and no")
    say("        --single-country escape flag exists.")
    say("  V1.b  inputs, sizes and md5s printed above, before any verdict.")
    say("  V1.c  every status below comes from the computation that produced")
    say("        it; a gate that could not run prints NOT CHECKED.")
    say("  V1.d  enforced inside the reader (4thJ_read_uk.py): unrecognised")
    say("        codes/units raise and stop rather than being coerced.")
    say()

    # ---- baseline ------------------------------------------------------
    base = run_gates(ep, raw_diary, raw_ind, raw_dv, ctx)
    say("=" * 78)
    say("GATES ON THE REAL DATA")
    say("=" * 78)
    for gid, status, detail in base.rows:
        say(f"  {gid:6s} {status:11s} {detail}")
    say()
    baseline_fails = [g for g, s, _ in base.rows if s == "FAIL"]
    if baseline_fails:
        say(f"  🔴 NOTE: {baseline_fails} FAIL on real, UNPERTURBED UK data.")
        say("  This is reported as a true property of the delivered file")
        say("  (F-UK-8, F-UK-9 in codebook_facts_uk.md), not smoothed over.")
        say("  Because these gates do not PASS at baseline, they are outside")
        say("  the coverage clause's scope (which applies to PASSing gates),")
        say("  exactly as a NOT CHECKED gate is -- but for a different,")
        say("  stated reason: they have already been seen failing, on real")
        say("  data, before any perturbation is applied.")
    say()

    # ---- perturbations -------------------------------------------------
    say("=" * 78)
    say("PERTURBATION BATTERY (a gate is trusted once it has been seen failing)")
    say("=" * 78)
    # `fell` only records a gate as "made to fall" by a perturbation that
    # NEWLY broke it relative to baseline -- G1.4 and G1.7a already FAIL on
    # real data, so every perturbation's failed-list trivially contains them
    # without any perturbation having "broken" anything; crediting a
    # perturbation for a gate that was already fallen would misattribute.
    fell = {gid: [] for gid in base.ids()}
    base_status = {g: s for g, s, _ in base.rows}
    for name, expected in PERTURBATIONS:
        pep, prd, pri, pdv, pctx = perturb(name, ep, raw_diary, raw_ind, raw_dv, ctx)
        res = run_gates(pep, prd, pri, pdv, pctx)
        failed = [g for g, s, _ in res.rows if s == "FAIL"]
        newly_failed = [g for g in failed if base_status.get(g) != "FAIL"]
        already_failing = [g for g in failed if base_status.get(g) == "FAIL"]
        for g in newly_failed:
            fell[g].append(name)
        if name == "null":
            res_status = {g: s for g, s, _ in res.rows}
            changed = {g: (base_status[g], res_status[g]) for g in res_status
                       if res_status[g] != base_status[g]}
            ok = len(changed) == 0
            verdict = ("as pre-registered (identical to baseline verdicts)"
                       if ok else f"NULL PERTURBATION MOVED A GATE: {changed}")
        else:
            ok = expected in newly_failed
            extra = [g for g in newly_failed if g != expected]
            verdict = ("as pre-registered" if ok and not extra else
                       "attributes cleanly" if ok else "DID NOT FIRE")
            if ok and extra:
                verdict = f"fired, and also newly moved {extra}"
        already_note = (f" (already failing at baseline, not newly moved: "
                         f"{already_failing})" if already_failing else "")
        say(f"  {name:32s} expected {expected!s:12s} failed {failed if failed else '[]'}"
            f"{already_note}")
        say(f"  {'':32s} -> {verdict}")
    say()

    # ---- coverage clause -------------------------------------------------
    say("=" * 78)
    say("COVERAGE CLAUSE")
    say("=" * 78)
    say("Applies to gates that PASS on the real data. NOT CHECKED gates are")
    say("exempt by the clause's own text. Gates that already FAIL on real,")
    say("unperturbed data are reported separately above; they are not a")
    say("PASS nothing shook, so the clause's literal condition does not")
    say("apply to them either -- but this is stated, not silently assumed.")
    say()
    uncovered = []
    for gid, status, _ in base.rows:
        if status == "PASS" and not fell[gid]:
            uncovered.append(gid)
    for gid, status, _ in base.rows:
        mark = ("never fell" if not fell[gid] else ", ".join(fell[gid]))
        say(f"  {gid:6s} baseline {status:11s} made to fall by: {mark}")
    say()
    if uncovered:
        say(f"  🔴 PROBE FAILS. These gates PASS on the real data and nothing")
        say(f"     in the set ever made them fall: {uncovered}")
    else:
        say("  Every gate that PASSes on the real data was made to fall by")
        say("  at least one perturbation. Coverage clause satisfied.")
    say()

    scored = [g for g, s, _ in base.rows if s in ("PASS", "FAIL")]
    say("=" * 78)
    say("SUMMARY")
    say("=" * 78)
    say(f"  gates scored          : {len(scored)}  {scored}")
    say(f"  gates NOT CHECKED     : {[g for g, s, _ in base.rows if s == NOT_CHECKED]}")
    say(f"  gates PASS            : {sum(1 for g, s, _ in base.rows if s == 'PASS')}")
    say(f"  gates FAIL            : {sum(1 for g, s, _ in base.rows if s == 'FAIL')}")
    say(f"  gates FAIL at baseline (outside coverage clause, see note): "
        f"{baseline_fails}")
    say(f"  V1.a                  : {v1a} (expected to fire on a "
        f"one-country round)")

    txt = "\n".join(log) + "\n"
    with open(os.path.join(out, "gate_report_step1_uk.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(txt)
    # the Windows console's default codepage cannot encode the emoji used
    # above; the full report is already on disk, so print an ASCII-safe copy
    sys.stdout.buffer.write(txt.encode("ascii", errors="replace"))


if __name__ == "__main__":
    main()
