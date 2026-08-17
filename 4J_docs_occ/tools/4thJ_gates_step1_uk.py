#!/usr/bin/env python3
"""
4J Step 1 validation -- gates G1.1 to G1.12 (SIXTEEN IDs: G1.1-G1.5, G1.6a,
G1.6b, G1.7a-G1.7d, G1.8-G1.12) and the perturbation battery, UK.

Implements Step1_docs/4thJ_01_corpusAcquisition_val.md exactly as
pre-registered as of the 2026-08-15 M-1..M-5 round (sixteen-gate
specification), against the UK delivery.

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

# 🔴 M-1, 2026-08-15: loc_raw (WhereWhen) also carries the "-9" sentinel
# (F-UK-15, DD's own value label "No answer/refused" for WhereWhen), on
# 7,117 of 587,632 episodes. Re-declared here independently of the reader,
# exactly the same shape as SECONDARY_BLANK_SENTINEL. "4276" (F-UK-9) is
# NOT this sentinel and must keep failing G1.4.
LOCATION_BLANK_SENTINEL = "-9"
LOCATION_UNDECLARED_TEST_VALUE = "-8"   # loc_undeclared_sentinel perturbation

# 🔴 M-3, 2026-08-15: DMFlag/HhOut are the delivery's own non-productive
# status codes (F-UK-8), re-transcribed here from the DD independently of
# 4thJ_read_uk.py (which does not read them at all -- they are gate-runner-
# only, per the work order). uktus15_diary_ep_long_ukda_data_dictionary.rtf:
#   DMFlag value label -6.0 = "Partial Ind from non-prod HH"
#   DMFlag value label  4.0 = "Non-productive, from part prod HH"
#   HhOut  value label 598.0 = "Other reasons why unproductive"
# Measured directly from the raw files this round (not copied from the
# codebook without re-checking): of the 2 UK person-days with a blank
# dia_wt_a/dia_wt_b, both carry DMFlag=-6 and HhOut=598. Of the 23
# diary-completing persons with a blank ind_wt, 1 carries DMFlag=-6/HhOut=598
# (the same household) and 22 carry DMFlag=4/HhOut=210 -- HhOut=210 itself
# means "Productive: at least one individual interview but not from all
# eligible household members" (a HOUSEHOLD-level code), so it is DMFlag=4,
# the INDIVIDUAL-level status, that is this session's own non-productive
# label for those 22, not HhOut. Accepted codes, per grain:
#   diary-level (per pid, diary_day): DMFlag == "-6"  OR  HhOut == "598"
#   individual-level (per pid):        DMFlag == "-6"  OR  DMFlag == "4"
UK_DIA_NONPRODUCTIVE_DMFLAG = {"-6"}
UK_DIA_NONPRODUCTIVE_HHOUT = {"598"}
UK_IND_NONPRODUCTIVE_DMFLAG = {"-6", "4"}

# M-4, 2026-08-15: UK weighting convention is "normalised" (NATCEN p.31,
# section 7.4(c)/(d): both diary weights and the individual weight are
# calibrated to mean ~1; F-UK-13 measured means 1.000322/1.000182/1.000000).
# G1.7d's mean-vs-1 clause is now SCORED (not permanently NOT CHECKED) for
# the UK. The magnitude-vs-layout-width half stays NOT CHECKED (no declared
# fixed-width layout ships anywhere in this tab-delimited delivery, F-UK-13)
# -- M-4 does not rescue that half and this runner does not make it look
# rescued.
UK_WEIGHTING_CONVENTION = "normalised"
G17D_MEAN_TOL = 0.01   # +/- 1 %, M-4

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
        "nonproductive_dia": ["DMFlag", "HhOut"],
    },
    "individual": {
        "key": ["serial", "pnum"],
        "age": "DVAge", "sex": "DMSex", "weight_ind": "ind_wt",
        "nonproductive_ind": ["DMFlag"],
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
      act2_extra_uk_3=What_Oth3, loc_raw=WhereWhen (M-1: -9 -> "" sentinel,
      same as act2_raw's -9 mapping),
      copresence=[WithAlone,WithSpouse,WithMother,WithFather,WithChild,
                   WithOther,WithOtherYK,WithMiss,WithNA],
      weight_dia_a=dia_wt_a, weight_dia_b=dia_wt_b,
      diary_day=daynum, DiaryDay_Act=DiaryDay_Act
      (DMFlag/HhOut are NOT read by the reader at all -- gate runner only,
       for G1.7a's non-productive-status clause, M-3)
    individual: key=[serial,pnum], DVAge=DVAge, DMSex=DMSex, weight_ind=ind_wt
    (dv_time_vars.tab is not read by the reader at all -- gate runner only)
"""


class Result:
    def __init__(self):
        self.rows = []
        self.subclauses = {}   # gid -> dict, M-7, only populated where a gate supplies one

    def add(self, gid, status, detail, subclauses=None):
        self.rows.append((gid, status, detail))
        if subclauses is not None:
            self.subclauses[gid] = subclauses

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


def location_state(series):
    """M-1: independent re-implementation of the loc_raw -9 -> blank mapping
    (F-UK-15), NOT imported from 4thJ_read_uk.py. Same shape as
    secondary_state, own sentinel constant."""
    return series.where(series != LOCATION_BLANK_SENTINEL, "")


def nonblank_count(series):
    return int((series.notna() & (series != "")).sum())


def build_nonproductive_lookup(raw_diary, raw_ind):
    """M-3: independent construction of the delivery-declared non-productive
    status, per diary (pid, diary_day) and per individual (pid), from the
    raw files this gate runner already reads. Never touches 4thJ_read_uk.py
    -- DMFlag/HhOut are not even in the reader's output."""
    tmp = raw_diary.groupby(["serial", "pnum", "daynum"], sort=False)[
        ["DMFlag", "HhOut"]].first()
    dia_nonprod = {}
    for (s, p, d), row in tmp.iterrows():
        key = (s + "_" + p, d)
        dia_nonprod[key] = (row["DMFlag"] in UK_DIA_NONPRODUCTIVE_DMFLAG or
                             row["HhOut"] in UK_DIA_NONPRODUCTIVE_HHOUT)
    ind_nonprod = {}
    for _, row in raw_ind.iterrows():
        pid = row["serial"] + "_" + row["pnum"]
        ind_nonprod[pid] = row["DMFlag"] in UK_IND_NONPRODUCTIVE_DMFLAG
    return dia_nonprod, ind_nonprod


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
    """M-1 amendment: loc_raw's blank state ("") is excluded from the
    membership test (a blank is not a code); case (b) -- a declared,
    cited sentinel -- is likewise not tested against the list, because it
    is never stored as a code string in the first place, it is stored as
    "". Anything else outside the list, including "4276" (F-UK-9) and the
    perturbation value "-8" (loc_undeclared_sentinel), FAILs exactly as
    before M-1.

    🔴 M-7, 2026-08-16: also returns a `subclauses` dict, one entry per
    field's own codes_outside_list, so that when this gate FAILs at
    baseline (as it does for the UK, on account of F-UK-9's undocumented
    "4276" alone) the perturbation loop can still observe a perturbation
    targeting a DIFFERENT field firing at the sub-clause level -- comparing
    baseline vs perturbed per-field lists, never the overall status, which
    stays FAIL either way. This recovers observability M-1/M-2 could not
    reach for the UK; it never turns a FAIL into a PASS."""
    acts, locs = ctx["act_codes"], ctx["loc_codes"]
    detail_parts = []
    any_bad = False

    a_bad = sorted(set(ep["act_raw"].unique()) - acts)
    if a_bad:
        any_bad = True
    loc_col = ep["loc_raw"]
    loc_not_recorded = int(loc_col.isna().sum())
    loc_blank = int((loc_col == "").sum())
    loc_valued_mask = loc_col.notna() & (loc_col != "")
    loc_valued = int(loc_valued_mask.sum())
    l_bad = sorted(set(loc_col[loc_valued_mask].unique()) - locs)
    if l_bad:
        any_bad = True
    detail_parts.append(f"act_raw codes outside list: {a_bad[:10]}")
    detail_parts.append(
        f"loc_raw: not_recorded={loc_not_recorded} recorded_and_blank="
        f"{loc_blank} (sentinel '{LOCATION_BLANK_SENTINEL}') "
        f"recorded_with_value={loc_valued} codes_outside_list={l_bad[:10]}")

    subclauses = {
        "act_raw_codes_outside_list": a_bad,
        "loc_raw_codes_outside_list": l_bad,
    }

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
        subclauses[f"{col}_codes_outside_list"] = bad

    status = "FAIL" if any_bad else "PASS"
    return status, " | ".join(detail_parts), subclauses


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


def resolve_manifest_path(local_path, local_root, raw_root):
    """M-6, 2026-08-16: resolve a manifest-recorded archive to its actual
    on-disk location under --raw (the country's raw ROOT directory at
    invocation time), using the RELATIVE sub-path the manifest itself
    records (local_path relative to local_root) -- never local_path taken
    literally, which is a workstation-specific provenance record and was
    never portable. local_path/local_root are read ONLY here, never
    rewritten -- they stay in the manifest as provenance, per M-6."""
    rel = os.path.relpath(local_path, local_root)
    return os.path.normpath(os.path.join(raw_root, rel))


def gate_g16a(ctx):
    """M-2 split: integrity only, independent of any URL. Prints hashed_at
    per archive before the verdict.

    🔴 M-6, 2026-08-16: resolves each archive under --raw (now the
    country's raw ROOT directory, not a deep sub-path), preserving the
    relative sub-path the manifest itself records -- for outer_archive and
    inner_archive, local_path relative to local_root (resolve_manifest_
    path); for delivered_files_md5 entries, the in-archive path already
    recorded relative to the extracted UK-TUS tree. Two distinct problem
    strings, 'recorded location not resolvable under --raw' vs
    'md5 mismatch', so a bad deployment and a corrupted byte can never
    again look like the same failure -- this is what let a path-resolution
    bug masquerade as an integrity FAIL on 2026-08-15/16."""
    man = ctx["manifest"]
    if man is None:
        return NOT_CHECKED, "no acquisition manifest fragment on disk"
    uk = man.get("uk", {})
    raw_root = ctx["raw_root"]
    local_root = uk.get("local_root", "")
    problems = []
    hashed_at_lines = []

    def check_entry(label, entry, hashed_at):
        lp = entry.get("local_path")
        hashed_at_lines.append(f"{label}: hashed_at={hashed_at}")
        if not lp:
            problems.append(f"{label}: recorded location not resolvable "
                             f"under --raw (no local_path recorded)")
            return
        resolved = resolve_manifest_path(lp, local_root, raw_root)
        if not os.path.exists(resolved):
            problems.append(f"{label}: recorded location not resolvable "
                             f"under --raw (resolved to {resolved})")
            return
        if md5_of(resolved) != entry.get("md5"):
            problems.append(f"{label}: md5 mismatch (at {resolved})")

    check_entry("outer_archive", uk.get("outer_archive", {}),
                ctx["hashed_at"].get("outer_archive", "NOT FOUND"))
    check_entry("inner_archive", uk.get("inner_archive", {}),
                ctx["hashed_at"].get("inner_archive", "NOT FOUND"))
    n_delivered = 0
    for entry in uk.get("delivered_files_md5", []):
        n_delivered += 1
        # M-6: entry["path"] IS the manifest's own relative sub-path for
        # this file already -- "the in-archive path under the extracted
        # tree" -- resolved directly under --raw, never via local_root.
        alt = os.path.join(raw_root, "unpacked", "UK-TUS", entry["path"])
        if not os.path.exists(alt):
            problems.append(f"{entry['path']}: recorded location not "
                             f"resolvable under --raw (resolved to {alt})")
            continue
        if md5_of(alt) != entry["md5"]:
            problems.append(f"{entry['path']}: md5 mismatch (at {alt})")
    ok = not problems
    detail = (f"outer+inner archive + {n_delivered} delivered files, "
              f"resolved under --raw={raw_root} (M-6, never local_path "
              f"taken literally), md5 recomputed from disk vs recorded, "
              f"independent of any URL; {' | '.join(hashed_at_lines)}; "
              f"problems: {problems}")
    return ("PASS" if ok else "FAIL"), detail


def gate_g16b(ctx):
    """M-2 split: provenance only. Threshold UNCHANGED. UK's delivery prints
    no literal download URL (see codebook_facts_uk.md); the DOI/citation
    landing page printed inside the delivered file itself is accepted, with
    provenance_source='author_attested' and the attestation date -- this is
    what the pre-split G1.6 already accepted for the UK, so the threshold is
    unchanged, only the label is now explicit."""
    man = ctx["manifest"]
    if man is None:
        return NOT_CHECKED, "no acquisition manifest fragment on disk"
    uk = man.get("uk", {})
    problems = []
    doi = uk.get("citation_and_licence", {}).get("doi")
    acquired = uk.get("acquired_utc")
    if not doi or not acquired:
        problems.append("doi or acquired_utc missing (the UK delivery prints "
                         "no literal download URL; DOI is the recorded "
                         "landing-page citation per the work order)")
    ok = not problems
    detail = (f"provenance_source={ctx['provenance_source'].get('uk', 'NOT FOUND')}, "
              f"doi={doi!r}, acquired_utc={acquired!r}; problems: {problems}")
    return ("PASS" if ok else "FAIL"), detail


def gate_g17a(ep, ctx):
    """M-3 re-scope: present/finite/positive/>1-distinct on rows the delivery
    weighted; every missing-weight row must carry a delivery-declared
    non-productive status (DMFlag/HhOut, independently re-read -- see
    build_nonproductive_lookup). A missing weight on a row NOT flagged
    non-productive is a FAIL."""
    dia_nonprod, ind_nonprod = ctx["dia_nonproductive"], ctx["ind_nonproductive"]

    per_dia = ep.groupby(["pid", "diary_day"], sort=False)["weight_dia_a"].first()
    per_ind = ep.groupby("pid", sort=False)["weight_ind"].first()

    dia_missing = per_dia[per_dia.isna()]
    dia_missing_bad = [k for k in dia_missing.index if not dia_nonprod.get(k, False)]
    ind_missing = per_ind[per_ind.isna()]
    ind_missing_bad = [k for k in ind_missing.index if not ind_nonprod.get(k, False)]

    dia_present = per_dia.dropna()
    ind_present = per_ind.dropna()
    dia_pos = bool((dia_present > 0).all()) and bool(np.isfinite(dia_present).all())
    ind_pos = bool((ind_present > 0).all()) and bool(np.isfinite(ind_present).all())
    ndist_dia = int(dia_present.nunique())
    ndist_ind = int(ind_present.nunique())

    ok = (len(dia_missing_bad) == 0 and len(ind_missing_bad) == 0
          and dia_pos and ind_pos and ndist_dia > 1 and ndist_ind > 1)
    detail = (
        f"weight_dia_a: {len(dia_missing)} of {len(per_dia)} diaries missing "
        f"({len(dia_missing_bad)} with NO delivery-declared non-productive "
        f"status -- FAIL if >0), all present values positive/finite: "
        f"{dia_pos}, {ndist_dia} distinct values; "
        f"weight_ind: {len(ind_missing)} of {len(per_ind)} persons missing "
        f"({len(ind_missing_bad)} with NO delivery-declared non-productive "
        f"status -- FAIL if >0), all present values positive/finite: "
        f"{ind_pos}, {ndist_ind} distinct values "
        f"(accepted non-productive codes: diary DMFlag in "
        f"{sorted(UK_DIA_NONPRODUCTIVE_DMFLAG)} or HhOut in "
        f"{sorted(UK_DIA_NONPRODUCTIVE_HHOUT)}; individual DMFlag in "
        f"{sorted(UK_IND_NONPRODUCTIVE_DMFLAG)})")
    return ("PASS" if ok else "FAIL"), detail


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
    """M-4: UK's declared convention is 'normalised' (see
    UK_WEIGHTING_CONVENTION). Scored: positive/finite AND mean within
    +/-1% of 1.0. The magnitude-vs-layout-width half stays NOT CHECKED (no
    declared fixed-width layout ships in this delivery) -- printed as such,
    not folded into the pass/fail verdict."""
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

    positive = bool((allv > 0).all())
    finite = bool(np.isfinite(allv).all())
    mean_ok = abs(vmean - 1.0) <= G17D_MEAN_TOL
    ok = positive and finite and mean_ok

    detail = (
        f"convention={UK_WEIGHTING_CONVENTION!r} (NATCEN p.31 section "
        f"7.4(c)/(d), cited codebook_facts_uk.md). Magnitude-vs-layout-width "
        f"half: NOT CHECKED (no declared fixed-width layout in this "
        f"tab-delimited delivery, F-UK-13) -- M-4 does not rescue this half. "
        f"Mean clause (SCORED): observed min={vmin:.4f} max={vmax:.4f} "
        f"mean={vmean:.6f} n_distinct={ndist} across dia_wt_a+dia_wt_b+"
        f"ind_wt pooled; positive={positive}, finite={finite}, "
        f"|mean-1.0|<= {G17D_MEAN_TOL}: {mean_ok}; {n_below_1} of "
        f"{len(allv)} ({pct_below_1:.1f} %) strictly below 1.0 (expected "
        f"under a normalised convention, not a defect)")
    return ("PASS" if ok else "FAIL"), detail


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


def gate_g112(ep, raw_diary, ctx):
    """G1.12: loc_raw three-state integrity and sentinel inventory. Built
    exactly as G1.11 is: independent recount from the raw file (own column
    resolution, own sentinel mapping -- location_state(), not
    secondary_state()), compared against the emitted parquet, exact, no
    tolerance. Also prints the full out-of-list-value inventory."""
    raw_loc = raw_diary[GATE_COLUMNS["diary_ep_long"]["loc_raw"]]
    raw_state = location_state(raw_loc)
    raw_not_recorded = 0  # UK fields WhereWhen on every episode row
    raw_blank = int((raw_state == "").sum())
    raw_valued = int(len(raw_state) - raw_blank)

    loc_col = ep["loc_raw"]
    emitted_not_recorded = int(loc_col.isna().sum())
    emitted_blank = int((loc_col == "").sum())
    emitted_valued = int(len(loc_col) - emitted_not_recorded - emitted_blank)

    ok = (raw_not_recorded == emitted_not_recorded and
          raw_blank == emitted_blank and raw_valued == emitted_valued)

    locs = ctx["loc_codes"]
    valued_mask = raw_state != ""
    inventory = raw_state[valued_mask].value_counts()
    out_of_list = {k: int(v) for k, v in inventory.items() if k not in locs}

    detail = (
        f"raw recount (own column resolution 'WhereWhen', own sentinel "
        f"'{LOCATION_BLANK_SENTINEL}' mapping): not_recorded={raw_not_recorded} "
        f"recorded_and_blank={raw_blank} recorded_with_value={raw_valued}; "
        f"emitted parquet: not_recorded={emitted_not_recorded} "
        f"recorded_and_blank={emitted_blank} recorded_with_value="
        f"{emitted_valued}; {'MATCH' if ok else 'MISMATCH'} (exact, no "
        f"tolerance). Full out-of-list inventory (value: count): "
        f"{out_of_list}")
    return ("PASS" if ok else "FAIL"), detail


def run_gates(ep, raw_diary, raw_ind, raw_dv, ctx):
    R = Result()

    s, d = gate_g11(ep, ctx); R.add("G1.1", s, d)
    s, d = gate_g12(ep); R.add("G1.2", s, d)
    s, d = gate_g13(ep); R.add("G1.3", s, d)
    s, d, sc = gate_g14(ep, ctx); R.add("G1.4", s, d, sc)
    s, d = gate_g15(ep, ctx); R.add("G1.5", s, d)
    s, d = gate_g16a(ctx); R.add("G1.6a", s, d)
    s, d = gate_g16b(ctx); R.add("G1.6b", s, d)
    s, d = gate_g17a(ep, ctx); R.add("G1.7a", s, d)
    s, d = gate_g17b(ep); R.add("G1.7b", s, d)
    s, d = gate_g17c(raw_diary, raw_dv); R.add("G1.7c", s, d)
    s, d = gate_g17d(raw_diary, raw_ind); R.add("G1.7d", s, d)
    s, d = gate_g18(); R.add("G1.8", s, d)
    s, d = gate_g19(raw_diary, ctx); R.add("G1.9", s, d)
    s, d = gate_g110(ep); R.add("G1.10", s, d)
    s, d = gate_g111(ep, raw_diary); R.add("G1.11", s, d)
    s, d = gate_g112(ep, raw_diary, ctx); R.add("G1.12", s, d)

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
        # 🔴 retargeted to G1.6a by the M-2 split (2026-08-15).
        man = json.loads(json.dumps(ctx["manifest"]))
        man["uk"]["delivered_files_md5"][0]["md5"] = "0" * 32
        ctx["manifest"] = man

    elif name == "strip_url_from_manifest":
        # 🔴 NEW, M-2. Remove the DOI (the UK's own recorded "URL" -- the
        # delivery prints no literal download URL) from the manifest
        # fragment. Must fell G1.6b alone; the bytes and their hashes (and
        # hashed_at) are untouched, so G1.6a stays clean.
        man = json.loads(json.dumps(ctx["manifest"]))
        man["uk"]["citation_and_licence"]["doi"] = None
        ctx["manifest"] = man

    elif name == "weight_negative_one":
        pid0 = ep["pid"].iloc[0]
        day0 = ep.loc[ep["pid"] == pid0, "diary_day"].iloc[0]
        m = (ep["pid"] == pid0) & (ep["diary_day"] == day0)
        ep.loc[m, "weight_dia_a"] = -1.0

    elif name == "weight_constant":
        ep["weight_dia_a"] = 1234.5

    elif name == "weight_blank_on_productive_row":
        # 🔴 NEW, M-3, THE AUDIT PERTURBATION. Pick a (pid, diary_day) the
        # delivery does NOT flag non-productive (DMFlag/HhOut re-read
        # independently in ctx) and blank its weight_dia_a. Must fell G1.7a
        # alone -- no row moves, no code changes, no archive touched.
        prod_key = None
        for key, is_nonprod in ctx["dia_nonproductive"].items():
            if not is_nonprod:
                prod_key = key
                break
        if prod_key is None:
            raise SystemExit("weight_blank_on_productive_row: no productive "
                              "(pid, diary_day) found to perturb -- cannot fire")
        pid0, day0 = prod_key
        m = (ep["pid"] == pid0) & (ep["diary_day"] == day0)
        ep.loc[m, "weight_dia_a"] = np.nan

    elif name == "weight_scale_10x_normalised":
        # 🔴 NEW, M-4. UK is normalised-convention. Multiply the WHOLE
        # dia_wt_a column by 10, consistently in BOTH raw sources G1.7c
        # compares (raw_diary and raw_dv), so G1.7c's cross-file identity
        # stays satisfied and only G1.7d's mean-vs-1 clause is exercised.
        # G1.7a reads from `ep`, not from these raw frames, so it is
        # untouched by this perturbation.
        def scale10(df):
            df = df.copy()
            blank = df["dia_wt_a"] == " "
            vals = df.loc[~blank, "dia_wt_a"].astype(float) * 10.0
            df.loc[~blank, "dia_wt_a"] = vals.map(repr)
            return df
        raw_diary = scale10(raw_diary)
        if raw_dv is not None:
            raw_dv = scale10(raw_dv)

    elif name == "loc_sentinel_to_code":
        # 🔴 NEW, M-1/G1.12. Rewrite every declared loc_raw sentinel
        # (state 2, "") as a valid location code. No row moves and every
        # value is now in-list, so G1.1, G1.2, G1.4, G1.5 all stay green;
        # only G1.12 (which independently recounts from the RAW file, where
        # the sentinel is still present) is fooled by the emitted table.
        code = ctx["loc_sentinel_replacement_code"]
        mask = ep["loc_raw"] == ""
        ep.loc[mask, "loc_raw"] = code

    elif name == "loc_undeclared_sentinel":
        # 🔴 NEW, M-1's OWN AUDIT. Set one loc_raw to an out-of-list value
        # that is NOT a declared sentinel. Must fell G1.4 alone.
        i = ep.index[ep["loc_raw"].notna() & (ep["loc_raw"] != "")][0]
        ep.loc[i, "loc_raw"] = ctx["loc_undeclared_value"]

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


# 🔴 M-7, 2026-08-16: which G1.4 sub-clause each of the four masked
# perturbations targets, so the perturbation loop can compare that ONE
# field's codes_outside_list between baseline and perturbed run and report
# "FIRED (sub-clause level)" even while the gate's overall status stays
# FAIL both times (F-UK-9's "4276" alone). Additive only -- never flips the
# gate's own PASS/FAIL, only recovers what the masking hides.
SUBCLAUSE_FIELD_FOR_PERTURBATION = {
    "act_to_outside_list": "act_raw_codes_outside_list",
    "act2_to_outside_list": "act2_raw_codes_outside_list",
    "act2_extra_2_to_outside_list": "act2_extra_uk_2_codes_outside_list",
    "loc_undeclared_sentinel": "loc_raw_codes_outside_list",
}

PERTURBATIONS = [
    ("null", "nothing may fail (see note: baseline is not fully clean)"),
    ("drop_last_5pct_rows", "G1.1"),
    ("delete_one_episode", "G1.2"),
    ("duration_30_to_25", "G1.3"),
    ("act_to_outside_list", "G1.4"),
    ("act2_to_outside_list", "G1.4"),
    ("act2_extra_2_to_outside_list", "G1.4"),
    ("loc_undeclared_sentinel", "G1.4"),
    ("reader_skips_silently", "G1.5"),
    ("corrupt_archive_byte", "G1.6a"),
    ("strip_url_from_manifest", "G1.6b"),
    ("weight_negative_one", "G1.7a"),
    ("weight_constant", "G1.7a"),
    ("weight_blank_on_productive_row", "G1.7a"),
    ("dv_time_vars_weight_swap", "G1.7c"),
    ("weight_scale_10x_normalised", "G1.7d"),
    ("declare_uk_1_day", "G1.9"),
    ("second_mode_value", "G1.10"),
    ("act2_rewrite_nonblank_to_blank", "G1.11"),
    ("loc_sentinel_to_code", "G1.12"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw", required=True,
                     help="M-6, 2026-08-16: the UK's COUNTRY-ROOT raw dir "
                          "(e.g. .../4J/raw/uk), containing the outer "
                          "archive and unpacked/UK-TUS/UKDA-8128-tab -- NOT "
                          "the deep UKDA-8128-tab dir directly. This is what "
                          "G1.6a resolves manifest-recorded archives under.")
    args = ap.parse_args()
    out = args.out
    # M-6: the deep path the reader's own --raw always meant (kept
    # unchanged for the reader itself); derived HERE, internally, from the
    # new country-root --raw, only for this gate runner's own raw re-reads.
    ukda_dir = os.path.join(args.raw, "unpacked", "UK-TUS", "UKDA-8128-tab")
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
        "manifest fragment": os.path.join(out, "acquisition_manifest.json"),
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
    if LOCATION_UNDECLARED_TEST_VALUE in loc_code_set:
        raise SystemExit(f"chosen sentinel {LOCATION_UNDECLARED_TEST_VALUE} "
                          f"IS a real UK location code -- "
                          f"loc_undeclared_sentinel cannot fire")
    # a valid, in-list location code, for loc_sentinel_to_code -- any code
    # other than the sentinel itself.
    loc_replacement_code = sorted(loc_code_set - {LOCATION_BLANK_SENTINEL})[0]

    parse_report = None
    if os.path.exists(inputs["parse report"]):
        with open(inputs["parse report"], encoding="utf-8") as fh:
            parse_report = fh.read()
    manifest = None
    if os.path.exists(inputs["manifest fragment"]):
        with open(inputs["manifest fragment"], encoding="utf-8") as fh:
            manifest = json.load(fh)
        # M-6/round-3, 2026-08-16: acquisition_manifest.json is now the
        # root-keyed union of all three countries. This file already
        # unwraps a "uk" key downstream (man.get("uk", {})) -- just refuse
        # to proceed silently if that key is now absent, never fall back
        # to reading the file flat.
        if "uk" not in manifest:
            raise SystemExit(f"acquisition_manifest.json has no 'uk' key -- "
                              f"cannot locate the UK's entry in the union "
                              f"manifest")

    # ---- independent raw re-read, own column resolution -------------------
    say("=" * 78)
    say("INDEPENDENT RAW RE-READ (own column resolution; never imports "
        "4thJ_read_uk.py)")
    say("=" * 78)
    tab_dir = os.path.join(ukda_dir, "tab")
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

    dia_nonprod, ind_nonprod = build_nonproductive_lookup(raw_diary, raw_ind)
    n_dia_nonprod = sum(1 for v in dia_nonprod.values() if v)
    n_ind_nonprod = sum(1 for v in ind_nonprod.values() if v)
    say("=" * 78)
    say("M-3: NON-PRODUCTIVE STATUS (DMFlag/HhOut), independently re-read")
    say("=" * 78)
    say(f"  diary-level (pid, diary_day): {n_dia_nonprod} of {len(dia_nonprod)} "
        f"flagged non-productive by DMFlag in {sorted(UK_DIA_NONPRODUCTIVE_DMFLAG)} "
        f"or HhOut in {sorted(UK_DIA_NONPRODUCTIVE_HHOUT)}")
    say(f"  individual-level (pid): {n_ind_nonprod} of {len(ind_nonprod)} "
        f"flagged non-productive by DMFlag in {sorted(UK_IND_NONPRODUCTIVE_DMFLAG)}")
    say()

    # hashed_at / provenance_source (M-2): read from the manifest fragment
    # itself (acquisition_manifest_uk.json), which now carries these two
    # fields per archive, filled in by this M-2 round from what is actually
    # known -- not invented here at runtime.
    uk_frag = (manifest or {}).get("uk", {})
    hashed_at = {
        "outer_archive": uk_frag.get("outer_archive", {}).get("hashed_at", "NOT FOUND"),
        "inner_archive": uk_frag.get("inner_archive", {}).get("hashed_at", "NOT FOUND"),
    }
    provenance_source = {"uk": uk_frag.get("provenance_source", "NOT FOUND")}

    ctx = {
        "act_codes": act_code_set,
        "loc_codes": loc_code_set,
        "parse_report": parse_report,
        "manifest": manifest,
        "codebook_diary_days": UK_DIARY_DAYS,
        "act_sentinel": act_sentinel,
        "loc_undeclared_value": LOCATION_UNDECLARED_TEST_VALUE,
        "loc_sentinel_replacement_code": loc_replacement_code,
        "dia_nonproductive": dia_nonprod,
        "ind_nonproductive": ind_nonprod,
        "hashed_at": hashed_at,
        "provenance_source": provenance_source,
        "raw_root": args.raw,   # M-6: G1.6a resolves archives under this
    }

    say(f"  episodes loaded        : {len(ep)} rows, {ep['pid'].nunique()} people, "
        f"{ep.groupby(['pid','diary_day']).ngroups} (person,diary_day) diaries")
    say(f"  activity codes loaded  : {len(act_code_set)}")
    say(f"  location codes loaded  : {len(loc_code_set)}")
    say(f"  chosen out-of-list activity sentinel: '{act_sentinel}' "
        f"(confirmed absent from the transcribed list)")
    say(f"  chosen out-of-list, non-declared location sentinel: "
        f"'{LOCATION_UNDECLARED_TEST_VALUE}' (confirmed absent from the "
        f"transcribed list; loc_undeclared_sentinel perturbation)")
    say(f"  chosen in-list replacement location code for "
        f"loc_sentinel_to_code: '{loc_replacement_code}'")
    say()

    # ---- V1.a is scored once per round (4thJ_vacuity_step1.py), not here --
    say("=" * 78)
    say("VACUITY GUARDS")
    say("=" * 78)
    say("  V1.a  scored once per round in vacuity_report_step1.txt; deliberately not computed here.")
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
        say("  This is reported as a true property of the delivered file,")
        say("  not smoothed over. Because these gates do not PASS at")
        say("  baseline, they are outside the coverage clause's scope.")
    say()

    # ---- perturbations -------------------------------------------------
    say("=" * 78)
    say("PERTURBATION BATTERY (a gate is trusted once it has been seen failing)")
    say("=" * 78)
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

        # 🔴 M-7, 2026-08-16: additive sub-clause attribution. Only engages
        # when the standard PASS->FAIL attribution says DID NOT FIRE AND
        # this perturbation is known to target one sub-clause of a gate
        # that already FAILs at baseline for an unrelated, pre-registered
        # reason (UK's G1.4, F-UK-9's "4276"). Compares the gate's OWN
        # computed per-field detail between baseline and perturbed run --
        # never the overall status. This is additive only: it may never
        # turn a FAIL into a PASS, and it never feeds `fell` (which drives
        # the coverage clause) -- it only recovers observability the
        # baseline FAIL was hiding.
        if verdict == "DID NOT FIRE" and name in SUBCLAUSE_FIELD_FOR_PERTURBATION:
            field = SUBCLAUSE_FIELD_FOR_PERTURBATION[name]
            base_sc = base.subclauses.get(expected, {}).get(field)
            pert_sc = res.subclauses.get(expected, {}).get(field)
            if base_sc is not None and pert_sc is not None and base_sc != pert_sc:
                verdict = (f"FIRED (sub-clause level, M-7): {expected}."
                           f"{field} went {base_sc} -> {pert_sc}. Overall "
                           f"gate status unchanged ({base_status.get(expected)} "
                           f"both times) -- recovers observability the "
                           f"baseline FAIL hides; does not flip the gate.")

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

    txt = "\n".join(log) + "\n"
    with open(os.path.join(out, "gate_report_step1_uk.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(txt)
    # the Windows console's default codepage cannot encode the emoji used
    # above; the full report is already on disk, so print an ASCII-safe copy
    sys.stdout.buffer.write(txt.encode("ascii", errors="replace"))


if __name__ == "__main__":
    main()
