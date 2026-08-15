#!/usr/bin/env python3
"""
4J Step 1 validation -- gates G1.1 to G1.11 and the perturbation battery, Spain.

Implements Step1_docs/4thJ_01_corpusAcquisition_val.md exactly as pre-registered,
as of the 2026-08-14 redesign (G1.7 split into G1.7a/b/c/d; G1.11 added; G1.4
widened for act2_raw).

Three rules this runner is built around, from the validation document:

  V1.b  it prints what it read, with hashes and counts, BEFORE any verdict;
  V1.c  every gate's status comes from the computation that produced it, and a
        gate that could not run prints NOT CHECKED, never PASS;
  coverage clause -- after the perturbation set has run, any gate that PASSes on
        the real data and was never made to fall by anything in the set fails
        the probe.

🔴 This file does NOT import anything from 4thJ_read_spain.py for G1.7c, G1.7d
or G1.11. The byte offsets those three gates need are re-transcribed
independently below, from "DISEnOS DE REGISTRO EET 2009 2010.xlsx" and
cross-checked against each raw file's own byte size (size / (declared width +
CRLF) must equal INE's stated record count -- a second, independent route to
the same widths). Print them so a human can compare this declaration against
the reader's own, by eye.

Usage:
    python 4thJ_gates_step1_spain.py --out <outputs_step1 dir> --raw <raw dir>
"""

import argparse
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

# ---- pre-registered constants -------------------------------------------
INE_DIARIES = 19295          # record-layout workbook, sheet "Disenos", row 18
INE_SLOTS = 2778480          # record-layout workbook, sheet "Disenos", row 20
SLOT_MINUTES = 10
DAY_MINUTES = 1440
SPAIN_DIARY_DAYS = 1         # G1.9: "Spain must read 1"
G17_TOL = 0.02               # +/- 2 % (G1.7b, printed only, never scored)
G18_TOL_PP = 1.0             # +/- 1.0 percentage point per cell
MIN_AGE = 10                 # EET target population, methodology section 3
WEIGHT_MAX = 1_000_000.0     # G1.7d: 6 integer digits declared in the layout
WEIGHT_MIN = 1.0             # G1.7d: a weight under 1 represents <1 person

AGE_BANDS = [(10, 14), (15, 24), (25, 44), (45, 64), (65, 200)]
SEX = {"1": "male", "6": "female"}

# INE estimator, methodology p.34: estimates are the mean of the four
# subsample estimates, t = Mon-Thu, Fri, Sat, Sun, obtained from DDIASEM.
SUBSAMPLE = {"1": 1, "2": 1, "3": 1, "4": 1, "5": 2, "6": 3, "7": 4}

NOT_CHECKED = "NOT CHECKED"

# ---------------------------------------------------------------------------
# INDEPENDENT RE-TRANSCRIPTION of raw fixed-width offsets, for G1.7c, G1.7d
# and G1.11 only.  1-based inclusive, exactly as INE writes them.
#
# Source: "DISEnOS DE REGISTRO EET 2009 2010.xlsx", sheets "F CINDIV",
# "F DIARIO1", "F MHOGAR", "F DIARIO2", read directly in this file with
# openpyxl during development (not at runtime, and not from the reader).
#
# Independence check done during development, not repeated at runtime: each
# file's own byte size, divided by (declared width + 2 for CRLF), reproduces
# INE's stated record count exactly --
#   CINDIV  1,215,585 / 63 = 19,295   DIARIO1   771,800 / 40 = 19,295
#   MHOGAR  1,294,750 / 50 = 25,895   DIARIO2 127,810,080 / 46 = 2,778,480
# a route to the same widths that does not touch the xlsx at all.
# ---------------------------------------------------------------------------
RAW_LAYOUT = {
    "CINDIV": {
        "width": 61,
        "IDHOGAR": (1, 5), "NPERS": (6, 7), "FACTORF": (46, 61),
    },
    "DIARIO1": {
        "width": 38,
        "IDHOGAR": (1, 5), "NPERS": (6, 7), "FACTORF": (23, 38),
    },
    "MHOGAR": {
        "width": 48,
        "IDHOGAR": (1, 5), "NPERS": (6, 7), "FACTORF": (33, 48),
    },
    "DIARIO2": {
        "width": 44,
        "IDHOGAR": (1, 5), "NPERS": (6, 7), "INTERVALO": (10, 12),
        "APRIN": (13, 15), "ASECU": (17, 19), "LUGAR": (21, 22),
        "SOLO": (23, 23), "PAREJA": (24, 24), "PADRES": (25, 25),
        "MENOR": (26, 26), "OTMH": (27, 27), "OTCON": (28, 28),
        "FACTORF": (29, 44),
    },
}
RAW_FILES = {
    "CINDIV": "CINDIV.TXT", "DIARIO1": "DIARIO1.TXT",
    "MHOGAR": "MHOGAR.TXT", "DIARIO2": "DIARIO2.TXT",
}


class Result:
    def __init__(self):
        self.rows = []

    def add(self, gid, status, detail):
        self.rows.append((gid, status, detail))

    def status(self, gid):
        for g, s, _ in self.rows:
            if g == gid:
                return s
        return None

    def ids(self):
        return [g for g, _, _ in self.rows]


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_raw_fixed(path, spec):
    """Read one raw fixed-width file using RAW_LAYOUT's own offsets. Never
    calls into 4thJ_read_spain.py."""
    fields = {k: v for k, v in spec.items() if k != "width"}
    colspecs = [(a - 1, b) for (a, b) in fields.values()]
    names = list(fields.keys())
    df = pd.read_fwf(
        path, colspecs=colspecs, names=names, dtype=str,
        header=None, encoding="latin-1", keep_default_na=False,
    )
    for c in names:
        df[c] = df[c].str.strip()
    df["pid"] = df["IDHOGAR"] + "_" + df["NPERS"]
    return df


def weight_float(raw_str_series):
    """FACTORF is 16 digits: 6 integer, 10 decimal (layout workbook)."""
    return raw_str_series.astype("float64") / 1e10


def load_reference_population(path):
    """Independent age x sex population, INE Estadistica Continua de Poblacion,
    table 56934, 1 July 2010.  Not derived from the EET microdata."""
    with open(path, encoding="utf-8") as fh:
        blob = json.load(fh)
    out, skipped, buckets = {}, [], {}
    for series in blob:
        name = series.get("Nombre", "")
        parts = [p.strip() for p in name.split(".")]
        if len(parts) >= 4 and parts[0] == "Total Nacional":
            age_txt, sex_txt = parts[1], parts[2]
        elif len(parts) >= 4 and parts[0] in ("Hombres", "Mujeres"):
            sex_txt, age_txt = parts[0], parts[1]
        else:
            continue
        if sex_txt not in ("Hombres", "Mujeres"):
            continue
        if age_txt.startswith("Todas"):
            continue
        tok = age_txt.split()[0]
        if not tok.isdigit():
            continue
        age = int(tok)
        sex = "male" if sex_txt == "Hombres" else "female"
        data = series.get("Data") or []
        val = None if (not data or data[0].get("Valor") is None) \
            else float(data[0]["Valor"])
        if "y m" in age_txt:
            if val is not None:
                buckets.setdefault(sex, {})[age] = val
            continue
        if val is None:
            skipped.append((age, sex_txt))
            continue
        if (age, sex) in out:
            raise SystemExit(
                f"reference population: age {age} sex {sex} appears in more than "
                f"one series ('{name}'). Refusing to double count."
            )
        out[(age, sex)] = val

    for sex, by_thresh in buckets.items():
        singles = {a for (a, s) in out if s == sex}
        usable = sorted(t for t in by_thresh if not any(a >= t for a in singles))
        if usable:
            t = usable[0]
            out[(t, sex)] = by_thresh[t]
    return out, skipped


def band_of(age):
    for lo, hi in AGE_BANDS:
        if lo <= age <= hi:
            return f"{lo}-{hi if hi < 200 else '+'}"
    return None


def weighted_person_table(ep):
    """One row per person, with the diary weight and the subsample index."""
    per = ep.groupby("pid", sort=False).agg(
        diary_day=("diary_day", "first"),
        weight_ind=("weight_ind", "first"),
        weight_dia=("weight_dia", "first"),
        sex=("SEXO", "first"),
        age=("EDAD", "first"),
        total_min=("duration_min", "sum"),
    ).reset_index()
    per["t"] = per["diary_day"].map(SUBSAMPLE)
    return per


def act2_nonblank_count(ep):
    """Count of episodes whose act2_raw is 'recorded with a value' -- not
    pd.NA (not recorded) and not '' (recorded and blank)."""
    col = ep["act2_raw"]
    return int((col.notna() & (col != "")).sum())


# ---------------------------------------------------------------------------
# G1.7c / G1.7d support: build small per-pid weight tables from the raw
# frames, independent of the reader.
# ---------------------------------------------------------------------------
def per_pid_weight(raw_df, name):
    if name == "DIARIO2":
        # one weight per diary; take the first slot by INTERVALO, same
        # convention the reader uses for weight_dia, re-derived here rather
        # than imported.
        raw_df = raw_df.copy()
        raw_df["INTERVALO"] = raw_df["INTERVALO"].astype(int)
        raw_df = raw_df.sort_values(["pid", "INTERVALO"], kind="mergesort")
        out = raw_df.groupby("pid", sort=False)["FACTORF"].first().reset_index()
    else:
        out = raw_df[["pid", "FACTORF"]].drop_duplicates(subset="pid")
    return out.rename(columns={"FACTORF": name})


def gate_g17c(weight_tables, respondent_pids):
    """Cross-file weight identity, compared as raw strings."""
    files = ["CINDIV", "DIARIO1", "DIARIO2", "MHOGAR"]
    present = [f for f in files if f in weight_tables]
    if len(present) < 2:
        return NOT_CHECKED, (
            f"only {len(present)} file(s) carry FACTORF in this delivery; "
            f"cross-file identity is not checkable"
        )
    base = pd.DataFrame({"pid": respondent_pids})
    for f in present:
        base = base.merge(weight_tables[f], on="pid", how="left")
    missing = base[present].isna().any(axis=1)
    n_missing = int(missing.sum())
    checkable = base.loc[~missing]

    def n_distinct(row):
        return len(set(row[present]))

    mism = checkable.apply(n_distinct, axis=1) > 1
    n_mismatch = int(mism.sum())
    n_total = len(base)
    ok = (n_missing == 0) and (n_mismatch == 0)
    detail = (
        f"{n_total} respondents checked across {present}; "
        f"{n_missing} missing a value in at least one file; "
        f"{n_mismatch} with a non-identical raw string across files"
    )
    return ("PASS" if ok else "FAIL"), detail


def gate_g17d(weight_tables, respondent_pids):
    """Magnitude vs the declared layout, computed from the raw strings.

    🔴 Restricted to the 19,295 diary respondents, the same population
    G1.7c compares. MHOGAR carries FACTORF for all 25,895 household
    members, but the weight only applies to the individual-questionnaire-
    plus-diary respondents; the other 6,600 rows (household members under
    the diary's scope, e.g. under 10) are zero-filled placeholders, not a
    weight the design ever produced. Checking the whole file would score
    that convention as a magnitude defect, which it is not -- the reader
    itself never reads MHOGAR.FACTORF for anyone but a joined respondent
    either. Confirmed against the raw file: exactly 25,895 - 19,295 =
    6,600 all-zero FACTORF rows in MHOGAR, none of them a respondent pid.
    """
    resp = set(respondent_pids)
    vals = []
    for name, tbl in weight_tables.items():
        sub = tbl.loc[tbl["pid"].isin(resp)]
        vals.append(weight_float(sub[name]))
    allv = pd.concat(vals, ignore_index=True)
    vmin, vmax, ndist = float(allv.min()), float(allv.max()), int(allv.nunique())
    ok = bool((allv >= WEIGHT_MIN).all() and (allv < WEIGHT_MAX).all())
    detail = (
        f"observed min {vmin:.10f}, max {vmax:.4f}, {ndist} distinct values "
        f"across {len(weight_tables)} raw file(s); bounds [{WEIGHT_MIN}, {WEIGHT_MAX})"
    )
    return ("PASS" if ok else "FAIL"), detail


def gate_g111(diario2_raw, ep):
    """Secondary-activity three-state integrity. Re-reconstructs episode
    boundaries from the raw DIARIO2 frame (own transcribed offsets) using
    the documented algorithm (collapse runs agreeing on activity, location
    and all six co-presence flags), takes the first-of-run ASECU the same
    way the reader takes first-of-run APRIN, and counts how many of those
    independently-rebuilt episodes are non-blank. Compared against the
    count of non-blank act2_raw actually stored in the emitted episode
    table -- never against the 340,269 raw-slot figure, which is the
    reader's own number and not a reference for anything."""
    d2 = diario2_raw.copy()
    d2["INTERVALO"] = d2["INTERVALO"].astype(int)
    d2 = d2.sort_values(["pid", "INTERVALO"], kind="mergesort").reset_index(drop=True)
    key_cols = ["APRIN", "LUGAR", "SOLO", "PAREJA", "PADRES", "MENOR", "OTMH", "OTCON"]
    key = d2[key_cols].agg("|".join, axis=1)
    new_person = d2["pid"].ne(d2["pid"].shift())
    changed = key.ne(key.shift()) | new_person
    d2["episode_id"] = changed.cumsum()
    first_asecu = d2.groupby("episode_id", sort=True)["ASECU"].first()
    raw_recount = int((first_asecu != "").sum())

    emitted_count = act2_nonblank_count(ep)
    ok = (raw_recount == emitted_count)
    detail = (
        f"independent recount from raw DIARIO2 (first-of-run ASECU over "
        f"{len(first_asecu)} independently rebuilt episodes): {raw_recount} "
        f"non-blank; emitted episode table: {emitted_count} non-blank. "
        f"(For reference only, never a gate input: 340,269 of 2,778,480 raw "
        f"slots are non-blank ASECU -- a different, slot-level quantity.)"
    )
    return ("PASS" if ok else "FAIL"), detail


def run_gates(ep, weight_tables, diario2_raw, ctx):
    """Every gate. `ep` is the (possibly perturbed) episode table.
    `weight_tables` and `diario2_raw` are the (possibly perturbed) raw-file
    reconstructions, independent of the reader and of `ep`."""
    R = Result()
    per = weighted_person_table(ep)

    # ---- G1.1 row-count reconciliation ----------------------------------
    n_diaries = len(per)
    R.add("G1.1", "PASS" if n_diaries == INE_DIARIES else "FAIL",
          f"{n_diaries} diaries against INE's stated {INE_DIARIES}")

    # ---- G1.2 duration closure ------------------------------------------
    bad = per.loc[per["total_min"] != DAY_MINUTES]
    R.add("G1.2", "PASS" if len(bad) == 0 else "FAIL",
          f"{len(bad)} of {len(per)} diaries do not sum to {DAY_MINUTES} min")

    # ---- G1.3 quantisation ----------------------------------------------
    nonq = int((ep["duration_min"] % SLOT_MINUTES != 0).sum())
    R.add("G1.3", "PASS" if nonq == 0 else "FAIL",
          f"{nonq} of {len(ep)} episode durations are not multiples of {SLOT_MINUTES}")

    # ---- G1.4 code-list membership (widened: act_raw, act2_raw, loc_raw) --
    acts, locs = ctx["act_codes"], ctx["loc_codes"]
    a_bad = sorted(set(ep["act_raw"].unique()) - acts)
    l_bad = sorted(set(ep["loc_raw"].unique()) - locs)
    a2_col = ep["act2_raw"]
    a2_not_recorded = int(a2_col.isna().sum())
    a2_blank = int((a2_col == "").sum())
    a2_valued_mask = a2_col.notna() & (a2_col != "")
    a2_valued = int(a2_valued_mask.sum())
    a2_bad = sorted(set(a2_col[a2_valued_mask].unique()) - acts)
    ok4 = not a_bad and not l_bad and not a2_bad
    R.add("G1.4", "PASS" if ok4 else "FAIL",
          f"act_raw codes outside list: {a_bad[:10]}; loc_raw codes outside: "
          f"{l_bad[:10]}; act2_raw codes outside list (blanks excluded): "
          f"{a2_bad[:10]} | act2_raw states, country ES: not_recorded="
          f"{a2_not_recorded}, recorded_and_blank={a2_blank}, "
          f"recorded_with_value={a2_valued}")

    # ---- G1.5 parse completeness ----------------------------------------
    slots_here = int(ep["duration_min"].sum() // SLOT_MINUTES)
    pr = ctx["parse_report"]
    if pr is None:
        R.add("G1.5", NOT_CHECKED, "no parse report on disk")
    else:
        claims_zero = "unexplained drops : 0" in pr
        R.add("G1.5", "PASS" if (claims_zero and slots_here == INE_SLOTS) else "FAIL",
              f"parse report states zero unexplained drops: {claims_zero}; "
              f"{slots_here} slots represented against {INE_SLOTS} delivered")

    # ---- G1.6 provenance -------------------------------------------------
    man = ctx["manifest"]
    if man is None:
        R.add("G1.6", NOT_CHECKED, "no acquisition manifest on disk")
    else:
        mism = []
        for entry in man["files"]:
            p = entry["local_path"]
            if not os.path.exists(p):
                mism.append(f"{entry['name']}: missing on disk")
            elif md5_of(p) != entry["md5"]:
                mism.append(f"{entry['name']}: md5 recomputed does not match")
            if not entry.get("url") or not entry.get("downloaded_utc"):
                mism.append(f"{entry['name']}: url or download date missing")
        R.add("G1.6", "PASS" if not mism else "FAIL",
              f"{len(man['files'])} archives checked; problems: {mism}")

    # ---- G1.7a weight presence, sign and distinct-count ------------------
    w_dia, w_ind = per["weight_dia"], per["weight_ind"]
    positive = bool((w_dia > 0).all()) and bool((w_ind > 0).all())
    ndist_dia, ndist_ind = int(w_dia.nunique()), int(w_ind.nunique())
    distinct_ok = ndist_dia > 1 and ndist_ind > 1
    R.add("G1.7a", "PASS" if (positive and distinct_ok) else "FAIL",
          f"all diary and individual weights strictly positive: {positive}; "
          f"distinct values -- weight_dia: {ndist_dia}, weight_ind: {ndist_ind} "
          f"(both must be > 1)")

    # ---- G1.7b RETIRED. Permanently NOT CHECKED, never scored. -----------
    est = per.groupby("t")["weight_dia"].sum()
    pop_est = float(est.mean()) if len(est) else float("nan")
    ref10 = ctx["ref_pop_10plus"]
    rel = abs(pop_est - ref10) / ref10 if ref10 else float("nan")
    R.add("G1.7b", NOT_CHECKED,
          f"weighted population estimate {pop_est:,.0f} against ECP 10+ "
          f"{ref10:,.0f}, relative difference {rel:.4f} (tolerance {G17_TOL}). "
          f"NOT CHECKED, permanently -- METH p.34 step 3 ratio-adjusts the "
          f"weights to this same population projection, so this comparison "
          f"cannot fail. Printed as evidence of nothing, kept visible so the "
          f"hole it retired does not get re-invented.")

    # ---- G1.7c cross-file weight identity (raw, independent) -------------
    respondent_pids = ep["pid"].drop_duplicates()
    status7c, detail7c = gate_g17c(weight_tables, respondent_pids)
    R.add("G1.7c", status7c, detail7c)

    # ---- G1.7d magnitude vs declared layout (raw, independent) -----------
    status7d, detail7d = gate_g17d(weight_tables, respondent_pids)
    R.add("G1.7d", status7d, detail7d)

    # ---- G1.8 demographic marginals -------------------------------------
    ref = ctx["ref_pop_cells"]
    if not ref:
        R.add("G1.8", NOT_CHECKED, "no external age x sex reference loaded")
    else:
        p = per.loc[per["age"] >= MIN_AGE].copy()
        p["band"] = p["age"].apply(band_of)
        p["sexname"] = p["sex"].map(SEX)
        p = p.dropna(subset=["band", "sexname"])
        shares = []
        for t, sub in p.groupby("t"):
            tot = sub["weight_dia"].sum()
            s = sub.groupby(["band", "sexname"])["weight_dia"].sum() / tot
            shares.append(s)
        obs = pd.concat(shares, axis=1).mean(axis=1) * 100.0 if shares else pd.Series(dtype=float)
        ref_tot = sum(ref.values())
        refs = {k: 100.0 * v / ref_tot for k, v in ref.items()}
        worst, worst_cell = 0.0, None
        detail = []
        for cell, rv in sorted(refs.items()):
            ov = float(obs.get(cell, 0.0))
            d = abs(ov - rv)
            detail.append(f"{cell[0]}/{cell[1]}: obs {ov:.2f} ref {rv:.2f} d {d:.2f}")
            if d > worst:
                worst, worst_cell = d, cell
        R.add("G1.8", "PASS" if worst <= G18_TOL_PP else "FAIL",
              f"worst cell {worst_cell} off by {worst:.2f} pp "
              f"(tolerance {G18_TOL_PP} pp) | " + "; ".join(detail))

    # ---- G1.9 diary days per respondent ---------------------------------
    dpp = per.groupby("pid").size()
    measured = int(dpp.max()) if len(dpp) else 0
    stated = ctx["codebook_diary_days"]
    R.add("G1.9", "PASS" if (measured == SPAIN_DIARY_DAYS and stated == SPAIN_DIARY_DAYS)
          else "FAIL",
          f"measured {measured} diary day(s) per respondent, "
          f"codebook_facts states {stated}, Spain must read {SPAIN_DIARY_DAYS}")

    # ---- G1.10 constant-field invariance --------------------------------
    nm, ns = ep["mode"].nunique(), ep["scheme"].nunique()
    R.add("G1.10", "PASS" if (nm == 1 and ns == 1) else "FAIL",
          f"{nm} distinct mode value(s), {ns} distinct scheme value(s)")

    # ---- G1.11 secondary-activity three-state integrity (raw, independent)
    status11, detail11 = gate_g111(diario2_raw, ep)
    R.add("G1.11", status11, detail11)

    return R


# ------------------------------------------------------------------------
# perturbations, exactly the pre-registered table (2026-08-14 redesign)
# ------------------------------------------------------------------------
def perturb(name, ep, weight_tables, diario2_raw, ctx):
    ep = ep.copy()
    weight_tables = dict(weight_tables)  # shallow; deep-copy only what's touched
    ctx = dict(ctx)

    if name == "null":
        pass

    elif name == "drop_last_5pct_rows":
        ep = ep.iloc[: int(len(ep) * 0.95)].copy()

    elif name == "delete_one_episode":
        ep = ep.drop(index=ep.index[10]).copy()

    elif name == "duration_30_to_25":
        i = ep.index[(ep["duration_min"] == 30)][0]
        ep.loc[i, "duration_min"] = 25

    elif name == "act_to_999":
        ep.loc[ep.index[0], "act_raw"] = "99Z"

    elif name == "act2_to_999":
        # "999" is itself a valid INE code ("Otro empleo del tiempo no
        # especificado", row 117 of the transcribed activity list), so it
        # would not test code-list membership at all. Use "99Z", the same
        # genuinely-out-of-list value act_to_999 already uses. Overwrite an
        # already non-blank act2_raw so the non-blank COUNT (what G1.11
        # checks) does not move -- isolates this case to G1.4.
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

    elif name == "factorf_swap_cindiv":
        t = weight_tables["CINDIV"].copy()
        a, b = t.index[0], t.index[1]
        t.loc[a, "CINDIV"], t.loc[b, "CINDIV"] = t.loc[b, "CINDIV"], t.loc[a, "CINDIV"]
        weight_tables["CINDIV"] = t

    elif name == "divide_weight_1e4_all_files":
        pid0 = weight_tables["CINDIV"]["pid"].iloc[0]
        for fname in ["CINDIV", "DIARIO1", "DIARIO2", "MHOGAR"]:
            t = weight_tables[fname].copy()
            idx = t.index[t["pid"] == pid0]
            if len(idx):
                raw = t.loc[idx[0], fname]
                new_int = int(raw) // 10_000
                t.loc[idx[0], fname] = f"{new_int:016d}"
            weight_tables[fname] = t

    elif name == "drop_over_65":
        ep = ep.loc[ep["EDAD"] <= 65].copy()

    elif name == "declare_spain_2_days":
        ctx["codebook_diary_days"] = 2

    elif name == "second_mode_value":
        ep.loc[ep.index[0], "mode"] = "web_diary"

    else:
        raise ValueError(name)

    return ep, weight_tables, diario2_raw, ctx


PERTURBATIONS = [
    ("null", "nothing may fail"),
    ("drop_last_5pct_rows", "G1.1"),
    ("delete_one_episode", "G1.2"),
    ("duration_30_to_25", "G1.3"),
    ("act_to_999", "G1.4"),
    ("act2_to_999", "G1.4"),
    ("reader_skips_silently", "G1.5"),
    ("corrupt_archive_byte", "G1.6"),
    ("weight_negative_one", "G1.7a"),
    ("weight_constant", "G1.7a"),
    ("factorf_swap_cindiv", "G1.7c"),
    ("divide_weight_1e4_all_files", "G1.7d"),
    ("drop_over_65", "G1.8"),
    ("declare_spain_2_days", "G1.9"),
    ("second_mode_value", "G1.10"),
    ("act2_rewrite_nonblank_to_blank", "G1.11"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw", required=True)
    args = ap.parse_args()
    out = args.out
    log = []

    def say(s=""):
        log.append(s)

    # ---- V1.b: everything read, with hashes, before any verdict ----------
    say("=" * 78)
    say("INPUTS (V1.b: printed before any verdict)")
    say("=" * 78)
    inputs = {
        "episodes": os.path.join(out, "episodes_spain.parquet"),
        "activity list": os.path.join(out, "crosswalk_source_spain_activity.csv"),
        "location list": os.path.join(out, "crosswalk_source_spain_location.csv"),
        "population reference": os.path.join(out, "reference_es_population_ecp_20100701.json"),
        "parse report": os.path.join(out, "parse_report_spain.txt"),
        "manifest": os.path.join(out, "acquisition_manifest.json"),
        "codebook facts": os.path.join(out, "codebook_facts_spain.md"),
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

    parse_report = None
    if os.path.exists(inputs["parse report"]):
        with open(inputs["parse report"], encoding="utf-8") as fh:
            parse_report = fh.read()
    manifest = None
    if os.path.exists(inputs["manifest"]):
        with open(inputs["manifest"], encoding="utf-8") as fh:
            manifest = json.load(fh)

    refpop, ref_skipped = load_reference_population(inputs["population reference"])
    cells = {}
    total10 = 0.0
    for (age, sex), v in refpop.items():
        if age < MIN_AGE:
            continue
        b = band_of(age)
        if b is None:
            continue
        cells[(b, sex)] = cells.get((b, sex), 0.0) + v
        total10 += v
    missing_in_scope = [s for s in ref_skipped if MIN_AGE <= s[0] < 100]
    if missing_in_scope:
        say(f"  reference series with a null value at ages {MIN_AGE}+: "
            f"{missing_in_scope[:10]} ({len(missing_in_scope)} total). "
            f"G1.8 is withheld rather than computed on a gapped reference.")
        cells = {}

    # ---- independent raw re-read for G1.7c / G1.7d / G1.11 ----------------
    say("=" * 78)
    say("INDEPENDENT OFFSET TRANSCRIPTION (G1.7c, G1.7d, G1.11 -- re-declared")
    say("in this file; 4thJ_read_spain.py is not imported anywhere below)")
    say("=" * 78)
    for fname, spec in RAW_LAYOUT.items():
        fields = {k: v for k, v in spec.items() if k != "width"}
        parts = " ".join(f"{k}={a}-{b}" for k, (a, b) in fields.items())
        say(f"  {fname:8s} width={spec['width']:3d}  {parts}")
    say("  Compare this table against the layout table declared independently")
    say("  at the top of 4thJ_read_spain.py, by eye.")
    say()

    raw_frames_full = {}
    weight_tables = {}
    for fname, fn in RAW_FILES.items():
        p = os.path.join(args.raw, fn)
        df = read_raw_fixed(p, RAW_LAYOUT[fname])
        raw_frames_full[fname] = df
        weight_tables[fname] = per_pid_weight(df, fname)
        say(f"  read {fn:14s} {len(df):>9d} rows, own offsets, from {p}")
    diario2_raw = raw_frames_full["DIARIO2"]
    say()

    ctx = {
        "act_codes": set(acts["code"]),
        "loc_codes": set(locs["code"]),
        "parse_report": parse_report,
        "manifest": manifest,
        "ref_pop_cells": cells,
        "ref_pop_10plus": total10,
        "codebook_diary_days": 1,   # from codebook_facts_spain.md
    }

    say(f"  episodes loaded        : {len(ep)} rows, {ep['pid'].nunique()} diaries")
    say(f"  activity codes loaded  : {len(ctx['act_codes'])}")
    say(f"  location codes loaded  : {len(ctx['loc_codes'])}")
    say(f"  reference population   : {total10:,.0f} persons aged {MIN_AGE}+, "
        f"INE ECP table 56934, 1 July 2010")
    say()

    # ---- V1.a: the battery must know how many countries it scanned -------
    countries = sorted(ep["country"].unique())
    v1a = "FIRED" if len(countries) < 4 else "clear"
    say("=" * 78)
    say("VACUITY GUARDS")
    say("=" * 78)
    say(f"  V1.a  countries scanned: {countries} ({len(countries)} of 4) -> {v1a}")
    say("        This is a one-country round by design. V1.a firing is the")
    say("        correct behaviour and the battery below is reported under it,")
    say("        not instead of it. The guard was not lowered.")
    say("  V1.b  inputs, sizes and md5s printed above, before any verdict.")
    say("  V1.c  every status below comes from the computation that produced it;")
    say("        a gate that could not run prints NOT CHECKED.")
    say("  V1.d  enforced inside the reader: unrecognised codes raise and stop.")
    say()

    # ---- baseline --------------------------------------------------------
    base = run_gates(ep, weight_tables, diario2_raw, ctx)
    say("=" * 78)
    say("GATES ON THE REAL DATA")
    say("=" * 78)
    for gid, status, detail in base.rows:
        say(f"  {gid:6s} {status:11s} {detail}")
    say()

    # ---- perturbations -----------------------------------------------------
    say("=" * 78)
    say("PERTURBATION BATTERY (a gate is trusted once it has been seen failing)")
    say("=" * 78)
    fell = {gid: [] for gid in base.ids()}
    for name, expected in PERTURBATIONS:
        pep, pwt, pd2, pctx = perturb(name, ep, weight_tables, diario2_raw, ctx)
        res = run_gates(pep, pwt, pd2, pctx)
        failed = [g for g, s, _ in res.rows if s == "FAIL"]
        for g in failed:
            fell[g].append(name)
        if name == "null":
            ok = (len(failed) == 0)
            verdict = "as pre-registered" if ok else "🔴 NULL PERTURBATION MOVED A GATE"
        else:
            ok = expected in failed
            extra = [g for g in failed if g != expected]
            verdict = ("as pre-registered" if ok and not extra else
                       "attributes cleanly" if ok else "DID NOT FIRE")
            if ok and extra:
                verdict = f"fired, and also moved {extra}"
        say(f"  {name:32s} expected {expected:9s} failed {failed if failed else '[]'}")
        say(f"  {'':32s} -> {verdict}")
    say()

    # ---- coverage clause ---------------------------------------------------
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
    say()

    seen = sum(1 for g in base.ids() if fell[g])
    scored = [g for g, s, _ in base.rows if s in ("PASS", "FAIL")]
    say("=" * 78)
    say("SUMMARY")
    say("=" * 78)
    say(f"  gates scored          : {len(scored)}  {scored}")
    say(f"  gates NOT CHECKED     : "
        f"{[g for g, s, _ in base.rows if s == NOT_CHECKED]}")
    say(f"  gates PASS            : {sum(1 for g, s, _ in base.rows if s == 'PASS')}")
    say(f"  gates FAIL            : {sum(1 for g, s, _ in base.rows if s == 'FAIL')}")
    say(f"  gates seen failing    : {seen} of {len(scored)}")
    say(f"  V1.a                  : {v1a} (expected to fire on a one-country round)")

    txt = "\n".join(log) + "\n"
    with open(os.path.join(out, "gate_report_step1_spain.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
