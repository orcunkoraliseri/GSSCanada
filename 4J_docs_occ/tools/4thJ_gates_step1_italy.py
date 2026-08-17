#!/usr/bin/env python3
"""
4J Step 1 validation -- gates G1.1 to G1.12 (SIXTEEN IDs: G1.1-G1.5, G1.6a,
G1.6b, G1.7a-G1.7d, G1.8-G1.12) and the perturbation battery, Italy.

Implements Step1_docs/4thJ_01_corpusAcquisition_val.md exactly as
pre-registered, as of the 2026-08-15 M-1..M-5 round (sixteen-gate
specification), adapted to an Italian, tab-delimited, native-episode
delivery.

🔴 This file does NOT import 4thJ_read_italy.py. Column names for G1.7d,
G1.11 and G1.12 are re-transcribed independently below, from ISTAT's own
Tracciato HTML files, read again from scratch here rather than reused as a
Python object from the reader. The reader's own column list is printed
alongside this file's own column list so a human can compare them by eye.

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

# M-4, 2026-08-15: Italy's weighting convention is "expansion" -- established
# from ISTAT's own text (Nota_metodologica-2013.pdf p.10, section 5, NOT
# inferred from the observed magnitudes and NOT copied from Spain, per the
# work order's explicit instruction): "Questo principio viene realizzato
# attribuendo a ogni unità campionaria un peso che indica il numero di unità
# della popolazione rappresentate dall'unità medesima. Se, per esempio, a
# un'unità campionaria viene attribuito un peso pari a 30, allora questa
# unità rappresenta se stessa e altre 29 unità della popolazione che non
# sono state incluse nel campione." ("...a weight that indicates the number
# of population units represented by that unit... a weight of 30 means this
# unit represents itself and another 29 population units not in the
# sample.") -- the textbook definition of an expansion weight, cited in
# codebook_facts_italy.md.
ITALY_WEIGHTING_CONVENTION = "expansion"

# 🔴 M-1, 2026-08-15: loc_raw sentinel handling. Italy fields cluogo on every
# DiarioGiornaliero row (catpri/cluogo never blank, F-IT-5); codebook_facts_
# italy.md's sentinel table records no declared missingness sentinel for
# cluogo. "-8" is used as the loc_undeclared_sentinel perturbation's test
# value, confirmed absent from the transcribed list before use.
LOCATION_UNDECLARED_TEST_VALUE = "-8"

# ---------------------------------------------------------------------------
# INDEPENDENT column re-transcription, for G1.7d, G1.11 and G1.12 only.
# Transcribed a second time, in this file, directly from
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


def resolve_manifest_path(local_path, local_root, raw_root):
    """M-6, 2026-08-16, ported verbatim from 4thJ_gates_step1_uk.py: resolve
    a manifest-recorded archive to its actual on-disk location under --raw
    (the country's raw dir at invocation time), using the RELATIVE sub-path
    the manifest itself records (local_path relative to local_root) -- never
    local_path taken literally, which is a workstation-specific provenance
    record and was never portable. local_path/local_root are read ONLY
    here, never rewritten -- they stay in the manifest as provenance."""
    rel = os.path.relpath(local_path, local_root)
    return os.path.normpath(os.path.join(raw_root, rel))


def act2_nonblank_count(ep):
    col = ep["act2_raw"]
    return int((col.notna() & (col != "")).sum())


def loc_states(col):
    n_nr = int(col.isna().sum())
    n_bl = int((col == "").sum())
    n_val = int(len(col) - n_nr - n_bl)
    return n_nr, n_bl, n_val


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
    a blank coefi2 (not a weight the diary design ever produced for them).
    M-4: convention cited (expansion, METH p.10)."""
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
    detail = (f"convention={ITALY_WEIGHTING_CONVENTION!r} (METH p.10 section 5, "
              f"'un peso che indica il numero di unità della popolazione "
              f"rappresentate dall'unità medesima', cited "
              f"codebook_facts_italy.md, established from ISTAT's own text, "
              f"not inferred from magnitudes and not copied from Spain). "
              f"observed min {vmin:.4f}, max {vmax:.4f}, {ndist} distinct values "
              f"(coefin+coefi2 pooled, raw Individui.txt); bounds [{WEIGHT_MIN}, {WEIGHT_MAX})")
    return ("PASS" if ok else "FAIL"), detail


def gate_g111(raw_diario, ep):
    """Secondary-activity three-state integrity. Italy ships native
    episodes -- no slot-to-episode collapsing occurs, so the independent
    recount is a direct count of non-blank catcon in the raw file (right/
    left-stripped, the SAME blank convention as the reader: a run of spaces
    strips to ""), compared against what is actually stored as non-blank
    act2_raw in the emitted table."""
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


def gate_g112(raw_diario, ep, ctx):
    """G1.12: loc_raw three-state integrity and sentinel inventory. Built
    exactly as G1.11: Italy ships native episodes, so the independent recount
    is a direct count from the raw file's own cluogo column (own column
    resolution, right/left-stripped -- same blank convention as the reader),
    compared against the emitted parquet, exact, no tolerance. Italy has no
    declared missingness sentinel for cluogo (catpri/cluogo never blank,
    F-IT-5), so this recount is expected to show recorded_and_blank=0 on
    both sides. Also prints the full out-of-list-value inventory."""
    cluogo_stripped = raw_diario["cluogo"].str.strip()
    raw_not_recorded = 0   # cluogo is fielded on every episode (F-IT-5)
    raw_blank = int((cluogo_stripped == "").sum())
    raw_valued = int(len(cluogo_stripped) - raw_blank)

    emitted_nr, emitted_bl, emitted_val = loc_states(ep["loc_raw"])
    ok = (raw_not_recorded == emitted_nr and raw_blank == emitted_bl and
          raw_valued == emitted_val)

    locs = ctx["loc_codes"]
    valued_mask = cluogo_stripped != ""
    inventory = cluogo_stripped[valued_mask].value_counts()
    out_of_list = {k: int(v) for k, v in inventory.items() if k not in locs}

    detail = (
        f"raw recount (own column resolution 'cluogo', stripped, no "
        f"reconstruction needed, no declared sentinel for Italy): "
        f"not_recorded={raw_not_recorded} recorded_and_blank={raw_blank} "
        f"recorded_with_value={raw_valued}; emitted parquet: not_recorded="
        f"{emitted_nr} recorded_and_blank={emitted_bl} recorded_with_value="
        f"{emitted_val}; {'MATCH' if ok else 'MISMATCH'} (exact, no "
        f"tolerance). Full out-of-list inventory (value: count): "
        f"{out_of_list}")
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
    loc_col = ep["loc_raw"]
    loc_nr, loc_bl, loc_val = loc_states(loc_col)
    loc_valued_mask = loc_col.notna() & (loc_col != "")
    l_bad = sorted(set(loc_col[loc_valued_mask].unique()) - locs)
    a2_col = ep["act2_raw"]
    a2_not_recorded = int(a2_col.isna().sum())
    a2_blank = int((a2_col == "").sum())
    a2_valued_mask = a2_col.notna() & (a2_col != "")
    a2_valued = int(a2_valued_mask.sum())
    a2_bad = sorted(set(a2_col[a2_valued_mask].unique()) - acts2)
    ok4 = not a_bad and not l_bad and not a2_bad
    # 🔴 M-7, 2026-08-16, ported from the UK reference implementation:
    # per-field codes_outside_list, so the perturbation loop can compare
    # baseline vs perturbed at sub-clause level if G1.4 ever FAILs at
    # baseline for an unrelated, pre-registered reason. Additive only --
    # never turns a FAIL into a PASS.
    subclauses4 = {
        "act_raw_codes_outside_list": a_bad,
        "loc_raw_codes_outside_list": l_bad,
        "act2_raw_codes_outside_list": a2_bad,
    }
    R.add("G1.4", "PASS" if ok4 else "FAIL",
          f"act_raw codes outside list: {a_bad[:10]}; loc_raw: "
          f"not_recorded={loc_nr} recorded_and_blank={loc_bl} "
          f"recorded_with_value={loc_val} codes_outside_list={l_bad[:10]}; "
          f"act2_raw codes outside catcon's OWN list (blanks "
          f"excluded): {a2_bad[:10]} | act2_raw states, country IT: "
          f"not_recorded={a2_not_recorded}, recorded_and_blank={a2_blank}, "
          f"recorded_with_value={a2_valued}",
          subclauses4)

    # ---- G1.5 parse completeness ------------------------------------------
    pr = ctx["parse_report"]
    if pr is None:
        R.add("G1.5", NOT_CHECKED, "no parse report on disk")
    else:
        claims_zero = "unexplained drops : 0" in pr
        R.add("G1.5", "PASS" if (claims_zero and n_ep == ISTAT_DIARIO_RECORDS) else "FAIL",
              f"parse report states zero unexplained drops: {claims_zero}; "
              f"{n_ep} episodes represented against {ISTAT_DIARIO_RECORDS} delivered")

    # ---- G1.6a integrity (M-2 split; M-6, 2026-08-16, ported from the UK
    # reference implementation: every entry resolved under --raw at
    # invocation time, preserving the manifest's own relative sub-path --
    # local_path/local_root read only, never rewritten, never taken
    # literally. Two distinct problem strings so a corrupted byte and a bad
    # deployment can never be confused.) --------------------------------
    man = ctx["manifest"]
    if man is None:
        R.add("G1.6a", NOT_CHECKED, "no acquisition manifest fragment on disk")
    else:
        problems = []
        hashed_at_lines = []
        local_root = man.get("local_root", "")
        raw_root = ctx["raw_root"]
        for entry in man["files"]:
            lp = entry.get("local_path")
            hashed_at_lines.append(f"{entry['name']}:hashed_at="
                                    f"{entry.get('hashed_at', 'NOT FOUND')}")
            if not lp:
                problems.append(f"{entry['name']}: recorded location not "
                                 f"resolvable under --raw (no local_path "
                                 f"recorded)")
                continue
            resolved = resolve_manifest_path(lp, local_root, raw_root)
            if not os.path.exists(resolved):
                problems.append(f"{entry['name']}: recorded location not "
                                 f"resolvable under --raw (resolved to "
                                 f"{resolved})")
                continue
            if md5_of(resolved) != entry["md5"]:
                problems.append(f"{entry['name']}: md5 mismatch (at {resolved})")
        R.add("G1.6a", "PASS" if not problems else "FAIL",
              f"{len(man['files'])} archives checked, resolved under "
              f"--raw={raw_root} (M-6, never local_path taken literally), "
              f"md5 recomputed from disk vs recorded, independent of any "
              f"URL; {' | '.join(hashed_at_lines)}; problems: {problems}")

    # ---- G1.6b provenance (M-2 split, threshold unchanged) -----------------
    if man is None:
        R.add("G1.6b", NOT_CHECKED, "no acquisition manifest fragment on disk")
    else:
        problems = []
        prov_lines = []
        for entry in man["files"]:
            url_ok = bool(entry.get("url")) and entry.get("url") != "NOT FOUND (see entry_point_note)"
            prov_lines.append(f"{entry['name']}:provenance_source="
                               f"{entry.get('provenance_source', 'NOT FOUND')}")
            if not url_ok:
                problems.append(f"{entry['name']}: url NOT FOUND in the manifest "
                                 f"(no per-file source URL was ever printed by this "
                                 f"delivery -- see codebook_facts_italy.md / manifest "
                                 f"entry_point_note; not fabricated)")
        R.add("G1.6b", "PASS" if not problems else "FAIL",
              f"{len(man['files'])} archives checked for url; "
              f"{' | '.join(prov_lines)}; problems: {problems}")

    # ---- G1.7a weight presence, sign, distinct-count, M-3 non-productive --
    # Italy has no delivery-declared non-productive status system, exactly
    # like Spain (there is no equivalent of the UK's DMFlag/HhOut). Measured
    # at baseline (F-IT-13): 0 respondents with a missing diary weight among
    # the 41,229 diary respondents. So ANY missing weight, at baseline or
    # under perturbation, is a FAIL under M-3's clause.
    w_dia, w_ind = per["weight_dia"], per["weight_ind"]
    w_dia_missing = w_dia[w_dia.isna()]
    w_ind_missing = w_ind[w_ind.isna()]
    w_dia_ok = w_dia.dropna()
    w_ind_ok = w_ind.dropna()
    positive = bool((w_dia_ok > 0).all()) and bool((w_ind_ok > 0).all())
    finite = bool(np.isfinite(w_dia_ok).all()) and bool(np.isfinite(w_ind_ok).all())
    ndist_dia, ndist_ind = int(w_dia_ok.nunique()), int(w_ind_ok.nunique())
    distinct_ok = ndist_dia > 1 and ndist_ind > 1
    ok7a = (len(w_dia_missing) == 0 and len(w_ind_missing) == 0
            and positive and finite and distinct_ok)
    R.add("G1.7a", "PASS" if ok7a else "FAIL",
          f"weight_dia: {len(w_dia_missing)} of {len(per)} respondents missing "
          f"(Italy has no delivery-declared non-productive status system, so "
          f"any missing weight is a FAIL); weight_ind: {len(w_ind_missing)} "
          f"of {len(per)} missing; all present values strictly positive: "
          f"{positive}, finite: {finite}; distinct values -- weight_dia: "
          f"{ndist_dia}, weight_ind: {ndist_ind} (both must be > 1)")

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

    # ---- G1.7d magnitude vs declared layout (raw, independent, M-4) --------
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

    # ---- G1.12 loc_raw three-state integrity + sentinel inventory (NEW) ----
    status12, detail12 = gate_g112(raw_diario, ep, ctx)
    R.add("G1.12", status12, detail12)

    return R


# ---------------------------------------------------------------------------
# perturbations
# ---------------------------------------------------------------------------
def perturb(name, ep, raw_diario, raw_ind, ctx):
    ep = ep.copy()
    raw_diario = raw_diario  # copied only when a case below touches it
    raw_ind = raw_ind
    ctx = dict(ctx)

    if name == "null":
        pass

    elif name == "drop_last_5pct_rows":
        ep = ep.iloc[: int(len(ep) * 0.95)].copy()

    elif name == "delete_one_episode":
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

    elif name == "loc_undeclared_sentinel":
        # 🔴 NEW, M-1's OWN AUDIT. Set one loc_raw to an out-of-list value
        # that is NOT a declared sentinel (Italy has none). Must fell G1.4
        # alone.
        i = ep.index[ep["loc_raw"].notna() & (ep["loc_raw"] != "")][0]
        ep.loc[i, "loc_raw"] = ctx["loc_undeclared_value"]

    elif name == "loc_sentinel_to_code":
        # N/A for Italy -- no declared sentinel exists to rewrite (state 2
        # count is 0), so this perturbation is a no-op by construction.
        pass

    elif name == "reader_skips_silently":
        ctx["parse_report"] = (ctx["parse_report"] or "").replace(
            "unexplained drops : 0", "unexplained drops : 1")

    elif name == "corrupt_archive_byte":
        man = json.loads(json.dumps(ctx["manifest"]))
        man["files"][0]["md5"] = "0" * 32
        ctx["manifest"] = man

    elif name == "strip_url_from_manifest":
        # G1.6b already FAILs at baseline for Italy (no per-file URL is ever
        # printed in this hand-delivered archive -- expected, correct, and
        # unchanged by this round). This perturbation cannot demonstrate
        # anything for the same reason corrupt_archive_byte could not
        # demonstrate anything against the old, unsplit G1.6: there is
        # nowhere for it to fall from. Applied anyway, for parity with the
        # other two countries and because the work order says the full set
        # runs on all three.
        man = json.loads(json.dumps(ctx["manifest"]))
        man["files"][0]["url"] = None
        ctx["manifest"] = man

    elif name == "weight_negative_one":
        i = ep.index[0]
        ep.loc[i, "weight_dia"] = -1.0

    elif name == "weight_constant":
        ep["weight_dia"] = 1234.5

    elif name == "weight_blank_on_productive_row":
        # 🔴 NEW, M-3, THE AUDIT PERTURBATION. Italy has no non-productive
        # status system, so any row's blanked weight is automatically
        # uncovered and must fell G1.7a alone.
        pid0 = ep["pid"].iloc[0]
        ep.loc[ep["pid"] == pid0, "weight_dia"] = np.nan

    elif name == "weight_scale_10x_normalised":
        # N/A for Italy -- expansion convention, not normalised.
        pass

    elif name == "weight_divide_1e4":
        pid0 = raw_ind["pid"].iloc[0]
        raw_ind = raw_ind.copy()
        idx = raw_ind.index[raw_ind["pid"] == pid0]
        for col in ("coefin", "coefi2"):
            raw = raw_ind.loc[idx[0], col]
            if raw.strip() != "":
                new_int = int(raw) // 10_000
                raw_ind.loc[idx[0], col] = f"{new_int:012d}"

    elif name == "drop_over_65":
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
    ("loc_undeclared_sentinel", "G1.4"),
    ("reader_skips_silently", "G1.5"),
    ("corrupt_archive_byte", "G1.6a"),
    ("strip_url_from_manifest", "G1.6b (already FAILs at baseline -- see detail)"),
    ("weight_negative_one", "G1.7a"),
    ("weight_constant", "G1.7a"),
    ("weight_blank_on_productive_row", "G1.7a"),
    ("weight_divide_1e4", "G1.7d"),
    ("weight_scale_10x_normalised", "N/A (Italy is expansion-convention, not normalised)"),
    ("drop_over_65", "G1.8 (NOT CHECKED for Italy -- see detail)"),
    ("declare_italy_2_days", "G1.9"),
    ("second_mode_value", "G1.10"),
    ("act2_rewrite_nonblank_to_blank", "G1.11"),
    ("loc_sentinel_to_code", "N/A (Italy has no declared loc_raw sentinel)"),
]

# 🔴 M-7, 2026-08-16, ported from the UK reference implementation: which
# G1.4 sub-clause each masked perturbation targets, so the perturbation loop
# can compare that ONE field's codes_outside_list between baseline and
# perturbed run and report "FIRED (sub-clause level)" even while the gate's
# overall status stays FAIL both times, for whatever pre-registered,
# unrelated reason caused the baseline FAIL. Additive only -- never flips
# the gate's own PASS/FAIL, only recovers observability a baseline FAIL
# would otherwise hide. Italy's G1.4 is not known to FAIL at baseline (no
# UK-4276-equivalent defect measured), so this mapping is not expected to
# engage this round; ported for shape parity with the UK file and so a
# future baseline defect is not masked silently.
SUBCLAUSE_FIELD_FOR_PERTURBATION = {
    "act_to_99Z": "act_raw_codes_outside_list",
    "act2_to_99Z": "act2_raw_codes_outside_list",
    "loc_undeclared_sentinel": "loc_raw_codes_outside_list",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw", required=True,
                     help="M-6, 2026-08-16: Italy's COUNTRY-ROOT raw dir "
                          "(e.g. .../4J/raw/italy), containing the archives "
                          "the manifest records (uso_tempo_2013_IT.zip, "
                          "Nota_metodologica*.pdf, ...) plus "
                          "unpacked/MICRODATI, unpacked/METADATI -- NOT the "
                          "unpacked/ dir directly. This is what G1.6a "
                          "resolves manifest-recorded archives under.")
    args = ap.parse_args()
    out = args.out
    # M-6: the deep dir the reader's own --raw always meant (kept unchanged
    # for the reader itself); derived HERE, internally, from the new
    # country-root --raw, only for this gate runner's own raw re-reads.
    unpacked_dir = os.path.join(args.raw, "unpacked")
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
        "manifest fragment": os.path.join(out, "acquisition_manifest.json"),
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

    if LOCATION_UNDECLARED_TEST_VALUE in set(locs["code"]):
        raise SystemExit(f"chosen sentinel {LOCATION_UNDECLARED_TEST_VALUE} "
                          f"IS a real Italian location code -- "
                          f"loc_undeclared_sentinel cannot fire")

    parse_report = None
    if os.path.exists(inputs["parse report"]):
        with open(inputs["parse report"], encoding="utf-8") as fh:
            parse_report = fh.read()
    manifest = None
    if os.path.exists(inputs["manifest fragment"]):
        with open(inputs["manifest fragment"], encoding="utf-8") as fh:
            manifest_root = json.load(fh)
        # M-6/round-3, 2026-08-16: acquisition_manifest.json is now the
        # root-keyed union of all three countries -- index into "it",
        # never fall back to reading the file flat.
        if "it" not in manifest_root:
            raise SystemExit(f"acquisition_manifest.json has no 'it' key -- "
                              f"cannot locate Italy's entry in the union "
                              f"manifest")
        manifest = manifest_root["it"]

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

    raw_diario = read_raw_diario(unpacked_dir)
    raw_ind = read_raw_individui_weights(unpacked_dir)
    say(f"  read DiarioGiornaliero.txt  {len(raw_diario):>9d} rows, own column list")
    say(f"  read Individui.txt (subset) {len(raw_ind):>9d} rows, own column list")
    say()

    # ---- sentinel check: "99Z" genuinely outside BOTH lists -----------------
    say("=" * 78)
    say("SENTINEL CHECK (perturbations act_to_99Z / act2_to_99Z / "
        "loc_undeclared_sentinel)")
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
    say(f"  chosen out-of-list, non-declared location sentinel: "
        f"'{LOCATION_UNDECLARED_TEST_VALUE}' (confirmed absent from the "
        f"transcribed cluogo list above)")
    say()

    ctx = {
        "act_codes": set(acts["code"]),
        "act2_codes": set(acts2["code"]),
        "loc_codes": set(locs["code"]),
        "parse_report": parse_report,
        "manifest": manifest,
        "codebook_diary_days": 1,   # from codebook_facts_italy.md
        "loc_undeclared_value": LOCATION_UNDECLARED_TEST_VALUE,
        "raw_root": args.raw,   # M-6: G1.6a resolves archives under this
    }

    say(f"  episodes loaded          : {len(ep)} rows, {ep['pid'].nunique()} diary respondents")
    say(f"  catpri codes loaded      : {len(ctx['act_codes'])}")
    say(f"  catcon codes loaded      : {len(ctx['act2_codes'])}")
    say(f"  cluogo codes loaded      : {len(ctx['loc_codes'])}")
    say()

    # ---- V1.a is scored once per round (4thJ_vacuity_step1.py), not here --
    say("=" * 78)
    say("VACUITY GUARDS")
    say("=" * 78)
    say("  V1.a  scored once per round in vacuity_report_step1.txt; deliberately not computed here.")
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
        for g in (failed - baseline_failures):
            fell[g].append(name)
        if name == "null":
            ok = (failed == baseline_failures)
            verdict = "as pre-registered (failing set unchanged)" if ok else \
                      f"🔴 NULL PERTURBATION MOVED A GATE: {sorted(failed - baseline_failures)} newly failed, {sorted(baseline_failures - failed)} newly cleared"
        elif expected.startswith("N/A"):
            verdict = f"N/A for Italy (see note); newly moved: {sorted(failed - baseline_failures)}"
            ok = True
        else:
            newly = failed - baseline_failures
            expected_id = expected.split(" ")[0]
            ok = (expected_id in newly)
            extra = [g for g in newly if g != expected_id]
            if expected.startswith("G1.8") or expected.startswith("G1.6b"):
                verdict = f"{expected_id} already/expected FAIL at baseline for Italy; case kept for parity, newly moved: {sorted(newly)}"
            else:
                verdict = ("as pre-registered" if ok and not extra else
                           "attributes cleanly" if ok else "DID NOT FIRE")
                if ok and extra:
                    verdict = f"fired, and also newly moved {extra}"

            # 🔴 M-7, 2026-08-16: additive sub-clause attribution, ported
            # from the UK reference implementation. Only engages when the
            # standard attribution says DID NOT FIRE AND this perturbation
            # is known to target one sub-clause of a gate that already
            # FAILs at baseline for an unrelated, pre-registered reason.
            # Compares the gate's OWN computed per-field detail between
            # baseline and perturbed run -- never the overall status.
            # Additive only: may never turn a FAIL into a PASS, never
            # feeds `fell`.
            if verdict == "DID NOT FIRE" and name in SUBCLAUSE_FIELD_FOR_PERTURBATION:
                field = SUBCLAUSE_FIELD_FOR_PERTURBATION[name]
                base_sc = base.subclauses.get(expected_id, {}).get(field)
                pert_sc = res.subclauses.get(expected_id, {}).get(field)
                if base_sc is not None and pert_sc is not None and base_sc != pert_sc:
                    verdict = (f"FIRED (sub-clause level, M-7): {expected_id}."
                               f"{field} went {base_sc} -> {pert_sc}. Overall "
                               f"gate status unchanged ({base_status.get(expected_id)} "
                               f"both times) -- recovers observability the "
                               f"baseline FAIL hides; does not flip the gate.")

        say(f"  {name:32s} expected {expected:55s} newly-failed {sorted(failed - baseline_failures)}")
        say(f"  {'':32s} -> {verdict}")
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

    txt = "\n".join(log) + "\n"
    with open(os.path.join(out, "gate_report_step1_italy.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(txt)
    sys.stdout.buffer.write(txt.encode("ascii", errors="replace"))


if __name__ == "__main__":
    main()
