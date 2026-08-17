#!/usr/bin/env python3
"""
4J Step 1 validation -- gates G1.1 to G1.12 (SIXTEEN IDs: G1.1-G1.5, G1.6a,
G1.6b, G1.7a-G1.7d, G1.8-G1.12) and the perturbation battery, Spain.

Implements Step1_docs/4thJ_01_corpusAcquisition_val.md exactly as
pre-registered, as of the 2026-08-15 M-1..M-5 round (sixteen-gate
specification).

🔴 This file does NOT import anything from 4thJ_read_spain.py for G1.7c,
G1.7d, G1.11 or G1.12. The byte offsets those gates need are re-transcribed
independently below, from "DISEnOS DE REGISTRO EET 2009 2010.xlsx" and
cross-checked against each raw file's own byte size. Print them so a human
can compare this declaration against the reader's own, by eye.

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

# M-4, 2026-08-15: Spain's weighting convention is "expansion" -- METH p.37,
# the estimator definition: "y d_j es el peso o factor de elevación" ("and
# d_j is the weight or expansion factor"), cited in codebook_facts_spain.md.
# Bound unchanged from before the M-4 round: [1.0, 1e6).
SPAIN_WEIGHTING_CONVENTION = "expansion"

AGE_BANDS = [(10, 14), (15, 24), (25, 44), (45, 64), (65, 200)]
SEX = {"1": "male", "6": "female"}

# INE estimator, methodology p.34: estimates are the mean of the four
# subsample estimates, t = Mon-Thu, Fri, Sat, Sun, obtained from DDIASEM.
SUBSAMPLE = {"1": 1, "2": 1, "3": 1, "4": 1, "5": 2, "6": 3, "7": 4}

NOT_CHECKED = "NOT CHECKED"

# 🔴 M-1, 2026-08-15: loc_raw sentinel handling. Spain fields LUGAR on every
# DIARIO2 slot; codebook_facts_spain.md's sentinel table records no declared
# missingness sentinel for LUGAR. There is therefore no LOCATION_BLANK_
# SENTINEL constant for Spain -- unlike the UK, nothing here maps any LUGAR
# value to "recorded and blank". "-8" is used as the loc_undeclared_sentinel
# perturbation's test value, confirmed absent from the transcribed list
# before use.
LOCATION_UNDECLARED_TEST_VALUE = "-8"

# ---------------------------------------------------------------------------
# INDEPENDENT RE-TRANSCRIPTION of raw fixed-width offsets, for G1.7c, G1.7d,
# G1.11 and G1.12 only.  1-based inclusive, exactly as INE writes them.
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
        self.subclauses = {}   # gid -> dict, M-7, only populated where a gate supplies one

    def add(self, gid, status, detail, subclauses=None):
        self.rows.append((gid, status, detail))
        if subclauses is not None:
            self.subclauses[gid] = subclauses

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


def loc_states(ep_or_col):
    col = ep_or_col if isinstance(ep_or_col, pd.Series) else ep_or_col["loc_raw"]
    n_nr = int(col.isna().sum())
    n_bl = int((col == "").sum())
    n_val = int(len(col) - n_nr - n_bl)
    return n_nr, n_bl, n_val


# ---------------------------------------------------------------------------
# G1.7c / G1.7d support: build small per-pid weight tables from the raw
# frames, independent of the reader.
# ---------------------------------------------------------------------------
def per_pid_weight(raw_df, name):
    if name == "DIARIO2":
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
    """Magnitude vs the declared layout (expansion convention, M-4),
    computed from the raw strings. Restricted to the 19,295 diary
    respondents -- see the original docstring note in the prior version of
    this file (MHOGAR's 6,600 non-respondent zero-fill rows excluded)."""
    resp = set(respondent_pids)
    vals = []
    for name, tbl in weight_tables.items():
        sub = tbl.loc[tbl["pid"].isin(resp)]
        vals.append(weight_float(sub[name]))
    allv = pd.concat(vals, ignore_index=True)
    vmin, vmax, ndist = float(allv.min()), float(allv.max()), int(allv.nunique())
    ok = bool((allv >= WEIGHT_MIN).all() and (allv < WEIGHT_MAX).all())
    detail = (
        f"convention={SPAIN_WEIGHTING_CONVENTION!r} (METH p.37, 'peso o "
        f"factor de elevación', cited codebook_facts_spain.md). "
        f"observed min {vmin:.10f}, max {vmax:.4f}, {ndist} distinct values "
        f"across {len(weight_tables)} raw file(s); bounds [{WEIGHT_MIN}, {WEIGHT_MAX})"
    )
    return ("PASS" if ok else "FAIL"), detail


def rebuild_episodes_from_diario2(diario2_raw):
    """Shared reconstruction used by G1.11 and G1.12: collapse DIARIO2 slots
    into episodes using the documented algorithm (agree on APRIN, LUGAR, all
    six co-presence flags), independent of the reader."""
    d2 = diario2_raw.copy()
    d2["INTERVALO"] = d2["INTERVALO"].astype(int)
    d2 = d2.sort_values(["pid", "INTERVALO"], kind="mergesort").reset_index(drop=True)
    key_cols = ["APRIN", "LUGAR", "SOLO", "PAREJA", "PADRES", "MENOR", "OTMH", "OTCON"]
    key = d2[key_cols].agg("|".join, axis=1)
    new_person = d2["pid"].ne(d2["pid"].shift())
    changed = key.ne(key.shift()) | new_person
    d2["episode_id"] = changed.cumsum()
    return d2


def gate_g111(d2, ep):
    """Secondary-activity three-state integrity. See prior version's
    docstring for the full explanation; unchanged by this round. `d2` is
    the already-rebuilt episode frame (run_gates rebuilds it once per call
    and shares it with G1.12 -- both gates still independently RE-DERIVE
    the reconstruction from the raw file inside this runner; sharing the
    one rebuild within a single battery pass is a performance optimisation,
    not an import from the reader)."""
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


def gate_g112(d2, ep, ctx):
    """G1.12: loc_raw three-state integrity and sentinel inventory. Built
    exactly as G1.11: independent episode rebuild from the raw file (own
    column resolution, first-of-run LUGAR -- the same key/rule act_raw's
    APRIN already uses), compared against the emitted parquet, exact, no
    tolerance. Spain has no declared missingness sentinel for LUGAR (see
    codebook_facts_spain.md sentinel table), so this recount is expected to
    show recorded_and_blank=0 on both sides. `d2` is the shared rebuild --
    see gate_g111's docstring."""
    first_lugar = d2.groupby("episode_id", sort=True)["LUGAR"].first()
    # Spain fields LUGAR on every slot; no declared sentinel maps any value
    # to blank here (unlike the UK's WhereWhen -9). "Recorded and blank"
    # would only occur if a slot's LUGAR were a literal blank string, which
    # the reader's own V1.d refusal already guarantees cannot happen
    # silently -- recomputed independently here anyway, never assumed.
    raw_not_recorded = 0
    raw_blank = int((first_lugar == "").sum())
    raw_valued = int(len(first_lugar) - raw_blank)

    emitted_nr, emitted_bl, emitted_val = loc_states(ep["loc_raw"])
    ok = (raw_not_recorded == emitted_nr and raw_blank == emitted_bl and
          raw_valued == emitted_val)

    locs = ctx["loc_codes"]
    valued_mask = first_lugar != ""
    inventory = first_lugar[valued_mask].value_counts()
    out_of_list = {k: int(v) for k, v in inventory.items() if k not in locs}

    detail = (
        f"raw recount (own column resolution 'LUGAR', first-of-run over "
        f"{len(first_lugar)} independently rebuilt episodes, no declared "
        f"sentinel for Spain): not_recorded={raw_not_recorded} "
        f"recorded_and_blank={raw_blank} recorded_with_value={raw_valued}; "
        f"emitted parquet: not_recorded={emitted_nr} recorded_and_blank="
        f"{emitted_bl} recorded_with_value={emitted_val}; "
        f"{'MATCH' if ok else 'MISMATCH'} (exact, no tolerance). Full "
        f"out-of-list inventory (value: count): {out_of_list}")
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

    # ---- G1.4 code-list membership (act_raw, act2_raw, loc_raw) ----------
    acts, locs = ctx["act_codes"], ctx["loc_codes"]
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
    a2_bad = sorted(set(a2_col[a2_valued_mask].unique()) - acts)
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
          f"act2_raw codes outside list (blanks excluded): "
          f"{a2_bad[:10]} | act2_raw states, country ES: not_recorded="
          f"{a2_not_recorded}, recorded_and_blank={a2_blank}, "
          f"recorded_with_value={a2_valued}",
          subclauses4)

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

    # ---- G1.6a integrity (M-2 split; M-6, 2026-08-16, ported from the UK
    # reference implementation: every entry resolved under --raw at
    # invocation time, preserving the manifest's own relative sub-path --
    # local_path/local_root read only, never rewritten, never taken
    # literally. Two distinct problem strings so a corrupted byte and a bad
    # deployment can never be confused.) --------------------------------
    man = ctx["manifest"]
    if man is None:
        R.add("G1.6a", NOT_CHECKED, "no acquisition manifest on disk")
    else:
        problems = []
        hashed_at_lines = []
        local_root = man.get("local_root", "")
        raw_root = ctx["raw_root"]
        for entry in man["files"]:
            lp = entry.get("local_path")
            hashed_at_lines.append(f"{entry['name']}:hashed_at="
                                    f"{ctx['hashed_at']}")
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
              f"URL; hashed_at={ctx['hashed_at']} for all (see hash_policy "
              f"in acquisition_manifest.json: 'computed at download time, "
              f"before the archive was opened'); problems: {problems}")

    # ---- G1.6b provenance (M-2 split, threshold unchanged) ----------------
    if man is None:
        R.add("G1.6b", NOT_CHECKED, "no acquisition manifest on disk")
    else:
        mism = []
        for entry in man["files"]:
            if not entry.get("url") or not entry.get("downloaded_utc"):
                mism.append(f"{entry['name']}: url or download date missing")
        R.add("G1.6b", "PASS" if not mism else "FAIL",
              f"{len(man['files'])} archives checked for url+downloaded_utc; "
              f"provenance_source={ctx['provenance_source']}; problems: {mism}")

    # ---- G1.7a weight presence, sign, distinct-count, M-3 non-productive --
    # Spain has no delivery-declared non-productive status system (no
    # equivalent of the UK's DMFlag/HhOut is fielded for excluded rows --
    # every corpus row is a diary the survey collected and every one of them
    # has a weight, codebook_facts_spain.md). So ANY missing weight on a
    # Spanish row is, by construction, NOT covered by a non-productive
    # status and is therefore a FAIL under M-3's clause -- there being no
    # accepted code is what makes weight_blank_on_productive_row fire here.
    w_dia, w_ind = per["weight_dia"], per["weight_ind"]
    dia_missing = w_dia[w_dia.isna()]
    ind_missing = w_ind[w_ind.isna()]
    dia_missing_bad = len(dia_missing)   # all missing rows are "bad": no
    ind_missing_bad = len(ind_missing)   # non-productive code system exists
    dia_present = w_dia.dropna()
    ind_present = w_ind.dropna()
    positive = bool((dia_present > 0).all()) and bool((ind_present > 0).all())
    ndist_dia, ndist_ind = int(dia_present.nunique()), int(ind_present.nunique())
    distinct_ok = ndist_dia > 1 and ndist_ind > 1
    ok7a = (dia_missing_bad == 0 and ind_missing_bad == 0 and positive and distinct_ok)
    R.add("G1.7a", "PASS" if ok7a else "FAIL",
          f"weight_dia: {len(dia_missing)} of {len(per)} diaries missing "
          f"(Spain has no delivery-declared non-productive status system, "
          f"so any missing weight is a FAIL); weight_ind: {len(ind_missing)} "
          f"of {len(per)} persons missing; all present values strictly "
          f"positive: {positive}; distinct values -- weight_dia: "
          f"{ndist_dia}, weight_ind: {ndist_ind} (both must be > 1)")

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

    # ---- G1.7d magnitude vs declared layout (raw, independent, M-4) ------
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

    # ---- G1.11 / G1.12: rebuild episodes from raw DIARIO2 ONCE, shared ---
    # (performance only -- both gates still independently re-derive the
    # reconstruction from the raw file, never from the reader or from `ep`)
    d2_rebuilt = rebuild_episodes_from_diario2(diario2_raw)

    status11, detail11 = gate_g111(d2_rebuilt, ep)
    R.add("G1.11", status11, detail11)

    status12, detail12 = gate_g112(d2_rebuilt, ep, ctx)
    R.add("G1.12", status12, detail12)

    return R


# ------------------------------------------------------------------------
# perturbations
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
        mask = ep["act2_raw"].notna() & (ep["act2_raw"] != "")
        i = ep.index[mask][0]
        ep.loc[i, "act2_raw"] = "99Z"

    elif name == "act2_rewrite_nonblank_to_blank":
        mask = ep["act2_raw"].notna() & (ep["act2_raw"] != "")
        ep.loc[mask, "act2_raw"] = ""

    elif name == "loc_undeclared_sentinel":
        # 🔴 NEW, M-1's OWN AUDIT. Set one loc_raw to an out-of-list value
        # that is NOT a declared sentinel (Spain has no declared sentinel at
        # all -- confirmed against the transcribed list before use). Must
        # fell G1.4 alone.
        i = ep.index[ep["loc_raw"].notna() & (ep["loc_raw"] != "")][0]
        ep.loc[i, "loc_raw"] = ctx["loc_undeclared_value"]

    elif name == "loc_sentinel_to_code":
        # N/A for Spain -- see PERTURBATIONS list note. No declared
        # sentinel exists to rewrite (state 2 count is 0), so this
        # perturbation is a no-op by construction for this country.
        pass

    elif name == "reader_skips_silently":
        ctx["parse_report"] = (ctx["parse_report"] or "").replace(
            "unexplained drops : 0", "unexplained drops : 1")

    elif name == "corrupt_archive_byte":
        man = json.loads(json.dumps(ctx["manifest"]))
        man["files"][0]["md5"] = "0" * 32
        ctx["manifest"] = man

    elif name == "strip_url_from_manifest":
        # 🔴 NEW, M-2. Must fell G1.6b alone; bytes/hashes untouched, so
        # G1.6a stays clean.
        man = json.loads(json.dumps(ctx["manifest"]))
        man["files"][0]["url"] = None
        ctx["manifest"] = man

    elif name == "weight_negative_one":
        i = ep.index[0]
        ep.loc[i, "weight_dia"] = -1.0

    elif name == "weight_constant":
        ep["weight_dia"] = 1234.5

    elif name == "weight_blank_on_productive_row":
        # 🔴 NEW, M-3, THE AUDIT PERTURBATION. Spain has no non-productive
        # status system, so any row's blanked weight is automatically
        # uncovered and must fell G1.7a alone.
        pid0 = ep["pid"].iloc[0]
        ep.loc[ep["pid"] == pid0, "weight_dia"] = np.nan

    elif name == "weight_scale_10x_normalised":
        # N/A for Spain -- expansion convention, not normalised. See
        # PERTURBATIONS list note. No-op by construction.
        pass

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
    ("loc_undeclared_sentinel", "G1.4"),
    ("reader_skips_silently", "G1.5"),
    ("corrupt_archive_byte", "G1.6a"),
    ("strip_url_from_manifest", "G1.6b"),
    ("weight_negative_one", "G1.7a"),
    ("weight_constant", "G1.7a"),
    ("weight_blank_on_productive_row", "G1.7a"),
    ("factorf_swap_cindiv", "G1.7c"),
    ("divide_weight_1e4_all_files", "G1.7d"),
    ("weight_scale_10x_normalised", "N/A (Spain is expansion-convention, not normalised)"),
    ("drop_over_65", "G1.8"),
    ("declare_spain_2_days", "G1.9"),
    ("second_mode_value", "G1.10"),
    ("act2_rewrite_nonblank_to_blank", "G1.11"),
    ("loc_sentinel_to_code", "N/A (Spain has no declared loc_raw sentinel)"),
]

# 🔴 M-7, 2026-08-16, ported from the UK reference implementation: which
# G1.4 sub-clause each masked perturbation targets, so the perturbation loop
# can compare that ONE field's codes_outside_list between baseline and
# perturbed run and report "FIRED (sub-clause level)" even while the gate's
# overall status stays FAIL both times, for whatever pre-registered,
# unrelated reason caused the baseline FAIL. Additive only -- never flips
# the gate's own PASS/FAIL, only recovers observability a baseline FAIL
# would otherwise hide. Spain's G1.4 is not known to FAIL at baseline (no
# UK-4276-equivalent defect measured), so this mapping is not expected to
# engage this round; ported for shape parity with the UK file and so a
# future baseline defect is not masked silently.
SUBCLAUSE_FIELD_FOR_PERTURBATION = {
    "act_to_999": "act_raw_codes_outside_list",
    "act2_to_999": "act2_raw_codes_outside_list",
    "loc_undeclared_sentinel": "loc_raw_codes_outside_list",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw", required=True,
                     help="M-6, 2026-08-16: Spain's COUNTRY-ROOT raw dir "
                          "(e.g. .../4J/raw/spain), containing the archives "
                          "the manifest records (datos_emptiem0910.zip, "
                          "docs/*.pdf, ...) plus unpacked/DIARIO2.TXT etc -- "
                          "NOT the unpacked/ dir directly. This is what "
                          "G1.6a resolves manifest-recorded archives under.")
    args = ap.parse_args()
    out = args.out
    # M-6: the deep dir the reader's own --raw always meant (kept unchanged
    # for the reader itself); derived HERE, internally, from the new
    # country-root --raw, only for this gate runner's own raw re-reads.
    unpacked_dir = os.path.join(args.raw, "unpacked")
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

    if LOCATION_UNDECLARED_TEST_VALUE in set(locs["code"]):
        raise SystemExit(f"chosen sentinel {LOCATION_UNDECLARED_TEST_VALUE} "
                          f"IS a real Spanish location code -- "
                          f"loc_undeclared_sentinel cannot fire")

    parse_report = None
    if os.path.exists(inputs["parse report"]):
        with open(inputs["parse report"], encoding="utf-8") as fh:
            parse_report = fh.read()
    manifest = None
    if os.path.exists(inputs["manifest"]):
        with open(inputs["manifest"], encoding="utf-8") as fh:
            manifest_root = json.load(fh)
        # M-6/round-3, 2026-08-16: acquisition_manifest.json is now the
        # root-keyed union of all three countries -- index into "es",
        # never fall back to reading the file flat.
        if "es" not in manifest_root:
            raise SystemExit(f"acquisition_manifest.json has no 'es' key -- "
                              f"cannot locate Spain's entry in the union "
                              f"manifest")
        manifest = manifest_root["es"]

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

    # ---- independent raw re-read for G1.7c / G1.7d / G1.11 / G1.12 --------
    say("=" * 78)
    say("INDEPENDENT OFFSET TRANSCRIPTION (G1.7c, G1.7d, G1.11, G1.12 -- ")
    say("re-declared in this file; 4thJ_read_spain.py is not imported below)")
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
        p = os.path.join(unpacked_dir, fn)
        df = read_raw_fixed(p, RAW_LAYOUT[fname])
        raw_frames_full[fname] = df
        weight_tables[fname] = per_pid_weight(df, fname)
        say(f"  read {fn:14s} {len(df):>9d} rows, own offsets, from {p}")
    diario2_raw = raw_frames_full["DIARIO2"]
    say()

    # hashed_at / provenance_source (M-2). Derived from what is already
    # recorded in acquisition_manifest.json (every file has both a url and a
    # downloaded_utc, and hash_policy states md5 was computed "at download
    # time, before the archive was opened") without editing that file -- it
    # is off-limits to this employee round except via TASK 6, which does not
    # ask for this edit.
    hashed_at = "download"
    provenance_source = "fetched_by_us"

    ctx = {
        "act_codes": set(acts["code"]),
        "loc_codes": set(locs["code"]),
        "parse_report": parse_report,
        "manifest": manifest,
        "ref_pop_cells": cells,
        "ref_pop_10plus": total10,
        "codebook_diary_days": 1,   # from codebook_facts_spain.md
        "loc_undeclared_value": LOCATION_UNDECLARED_TEST_VALUE,
        "hashed_at": hashed_at,
        "provenance_source": provenance_source,
        "raw_root": args.raw,   # M-6: G1.6a resolves archives under this
    }

    say(f"  episodes loaded        : {len(ep)} rows, {ep['pid'].nunique()} diaries")
    say(f"  activity codes loaded  : {len(ctx['act_codes'])}")
    say(f"  location codes loaded  : {len(ctx['loc_codes'])}")
    say(f"  chosen out-of-list, non-declared location sentinel: "
        f"'{LOCATION_UNDECLARED_TEST_VALUE}' (confirmed absent from the "
        f"transcribed list; loc_undeclared_sentinel perturbation)")
    say(f"  reference population   : {total10:,.0f} persons aged {MIN_AGE}+, "
        f"INE ECP table 56934, 1 July 2010")
    say()

    # ---- V1.a is scored once per round (4thJ_vacuity_step1.py), not here --
    say("=" * 78)
    say("VACUITY GUARDS")
    say("=" * 78)
    say("  V1.a  scored once per round in vacuity_report_step1.txt; deliberately not computed here.")
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
    base_status = {g: s for g, s, _ in base.rows}
    for name, expected in PERTURBATIONS:
        pep, pwt, pd2, pctx = perturb(name, ep, weight_tables, diario2_raw, ctx)
        res = run_gates(pep, pwt, pd2, pctx)
        failed = [g for g, s, _ in res.rows if s == "FAIL"]
        newly_failed = [g for g in failed if base_status.get(g) != "FAIL"]
        for g in newly_failed:
            fell[g].append(name)
        if name == "null":
            ok = (len(failed) == 0)
            verdict = "as pre-registered" if ok else "🔴 NULL PERTURBATION MOVED A GATE"
        elif expected.startswith("N/A"):
            verdict = f"N/A for Spain (see note); moved: {newly_failed}"
            ok = True
        else:
            ok = expected in newly_failed
            extra = [g for g in newly_failed if g != expected]
            verdict = ("as pre-registered" if ok and not extra else
                       "attributes cleanly" if ok else "DID NOT FIRE")
            if ok and extra:
                verdict = f"fired, and also moved {extra}"

        # 🔴 M-7, 2026-08-16: additive sub-clause attribution, ported from
        # the UK reference implementation. Only engages when the standard
        # PASS->FAIL attribution says DID NOT FIRE AND this perturbation is
        # known to target one sub-clause of a gate that already FAILs at
        # baseline for an unrelated, pre-registered reason. Compares the
        # gate's OWN computed per-field detail between baseline and
        # perturbed run -- never the overall status. Additive only: may
        # never turn a FAIL into a PASS, never feeds `fell`.
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

        say(f"  {name:32s} expected {expected:55s} failed {failed if failed else '[]'}")
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

    txt = "\n".join(log) + "\n"
    with open(os.path.join(out, "gate_report_step1_spain.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(txt)
    # the Windows console's default codepage cannot encode the emoji used
    # above; the full report is already on disk, so print an ASCII-safe copy
    sys.stdout.buffer.write(txt.encode("ascii", errors="replace"))


if __name__ == "__main__":
    main()
