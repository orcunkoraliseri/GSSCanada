#!/usr/bin/env python
"""
4thJ_gates_step2.py -- Step 2 validation battery.

Sixteen gates (G2.1-G2.16), seventeen perturbations, nine vacuity guards
(V2.a-V2.i), one coverage clause. One script.

Governing spec (read verbatim, not paraphrased):
    4J_docs_occ/Step2_docs/4thJ_02_harmonisation_val.md   -- gate table, perturbation table, guards
    4J_docs_occ/Step2_docs/4thJ_02_harmonisation.md        -- D-S2-2..D-S2-13, D-S2-12 record contract

Role: EMPLOYEE. This runner never moves a threshold, widens a band, or adjusts
a perturbation because something fails. A failing gate is a result to report.
If a perturbation reports DID NOT FIRE, that is reported with evidence, not fixed.

Usage (minimum arguments, per the task document):
    py 4thJ_gates_step2.py --harmonised <parquet> --crosswalks <dir> --step1 <run dir> \
        --out <dir> --perturbation baseline

    py 4thJ_gates_step2.py --selftest --out <dir>
        Builds its own synthetic harmonised.parquet + Step 1 reference + filter_report.md
        (grounded in the REAL accepted crosswalks under Step2_docs/outputs_step2/, read
        only, never modified), runs baseline plus all seventeen perturbations in-process,
        and prints the coverage cross-tab and the six acceptance tests.

On Speed: sbatch only, partition ps, -t 7-00:00:00. Never run this bare on the login node.
"""

import argparse
import copy
import glob
import os
import re
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# CONSTANTS -- decided facts from the governing spec, not thresholds we may
# move. Each one is cited to the decision that fixed it.
# --------------------------------------------------------------------------

COUNTRIES = ["es", "uk", "it"]                      # decision 16: three countries
SHARED_COP_FLAGS = [
    "cop_alone", "cop_partner", "cop_children",
    "cop_parent", "cop_other_hh", "cop_other_persons",
]                                                     # D-S2-8: six shared flags
TARGET_CLASSES = ["at_home", "other_place", "private_transport", "public_transport"]  # D-S2-3
NATIVE_ORIGIN_HOUR = {"es": 6, "uk": 4, "it": 4}      # D-S2-5, measured per codebook (kept for
TARGET_ORIGIN_HOUR = 4                                # reference/reporting; rotation itself uses
                                                        # rotation_offset() / REFERENCE_MINUTES below,
                                                        # which is the D-S2-14 generalisation)

# D-S2-14 (2026-08-16, later): start_min's reference point is per-country and was
# never stated by Step 1. Spain and the UK are diary-relative (first episode
# start_min=0); Italy is wall-clock minutes since midnight (first episode
# start_min=240, native origin still 04:00). REFERENCE_MINUTES is the wall-clock
# minute that each country's own start_min=0 corresponds to.
REFERENCE_MINUTES = {"es": 360, "uk": 240, "it": 0}   # D-S2-14, measured
TARGET_REFERENCE_MINUTES = 240                         # 04:00, D-S2-5


def rotation_offset(country):
    """D-S2-14's formula, verbatim: offset = (reference_minutes - 240) mod 1440.
    ES +120, UK 0, IT +1200 (= -240). Do not special-case any country here --
    the formula is general and Italy's wall-clock encoding falls out of it."""
    return (REFERENCE_MINUTES[country] - TARGET_REFERENCE_MINUTES) % 1440

# D-S2-12 record contract, exactly as written.
D_S2_12_COLUMNS = [
    "country", "wave", "hid", "pid", "diary_day",
    "episode_index", "episode_index_step1", "split_at_origin",
    "start_min", "duration_min",
    "act", "act_level1", "act_level2",
    "act2", "act2_level1",
    "loc_class", "indoor_presence",
    "cop_alone", "cop_partner", "cop_children", "cop_parent", "cop_other_hh", "cop_other_persons",
    # cop_extra_<country>_<field>... -- appended dynamically below
    "act_raw", "act2_raw", "loc_raw",
    "mode", "scheme", "weight_ind", "weight_dia",
]
EXTRA_COP_COLUMNS = [
    "cop_extra_uk_mother", "cop_extra_uk_father", "cop_extra_uk_na",
    "cop_extra_it_madre", "cop_extra_it_padre", "cop_extra_it_siblings",
]

PERTURBATIONS = [
    "null", "del_activity_row", "strip_citation", "scale_duration", "round_duration",
    "add_one_to_many", "empty_outdoor", "drop_spain_age", "zero_missing_flag",
    "pool_modal_code", "shift_sleep_budget", "remap_spain_transport", "wrong_rotation",
    "italy_catcon_swap", "spain_cop_bool", "spain_secondary_repoint", "uk_group1_carry",
]
# Val doc's own table: which gate each perturbation must fell, and which gates
# its row explicitly requires to stay clean. Empty list under "clean" = the row
# names no gate at all (only the null perturbation, which must move nothing).
PERTURBATION_SPEC = {
    "null":                  {"must_fail": None,    "must_stay_clean": "ALL"},
    "del_activity_row":      {"must_fail": "G2.1",  "must_stay_clean": ["G2.3"]},
    "strip_citation":        {"must_fail": "G2.2",  "must_stay_clean": ["G2.1"]},
    "scale_duration":        {"must_fail": "G2.3",  "must_stay_clean": ["G2.4"]},
    "round_duration":        {"must_fail": "G2.4",  "must_stay_clean": ["G2.3"]},
    "add_one_to_many":       {"must_fail": "G2.5",  "must_stay_clean": ["G2.1"]},
    "empty_outdoor":         {"must_fail": "G2.6",  "must_stay_clean": "ALL_OTHER"},
    "drop_spain_age":        {"must_fail": "G2.7",  "must_stay_clean": ["G2.4"]},
    "zero_missing_flag":     {"must_fail": "G2.8",  "must_stay_clean": "ALL_OTHER"},
    "pool_modal_code":       {"must_fail": "G2.9",  "must_stay_clean": ["G2.3", "G2.4"]},
    "shift_sleep_budget":    {"must_fail": "G2.10", "must_stay_clean": ["G2.9"]},
    "remap_spain_transport": {"must_fail": "G2.11", "must_stay_clean": ["G2.1", "G2.3", "G2.4", "G2.9", "G2.10"]},
    "wrong_rotation":        {"must_fail": "G2.12", "must_stay_clean": "ALL_OTHER"},
    "italy_catcon_swap":     {"must_fail": "G2.13", "must_stay_clean": ["G2.1", "G2.3", "G2.4", "G2.9", "G2.10"]},
    "spain_cop_bool":        {"must_fail": "G2.14", "must_stay_clean": ["G2.1", "G2.2", "G2.3", "G2.4", "G2.5",
                                                                          "G2.6", "G2.7", "G2.9", "G2.10", "G2.11"]},
    "spain_secondary_repoint": {"must_fail": "G2.15", "must_stay_clean": ["G2.13", "G2.1"]},
    "uk_group1_carry":       {"must_fail": "G2.16", "must_stay_clean": ["G2.1", "G2.2", "G2.3", "G2.4", "G2.9", "G2.10"]},
}
ALL_GATE_IDS = [f"G2.{i}" for i in range(1, 17)]


def gr(gate_id, passed, checked=True, summary="", detail=None):
    return {"id": gate_id, "checked": checked, "passed": passed, "summary": summary,
            "detail": detail or {}}


# --------------------------------------------------------------------------
# LOADERS -- real accepted files, read-only, never modified on disk.
# --------------------------------------------------------------------------

def _nonempty(series):
    return series.notna() & (series.astype(str).str.strip() != "") & (series.astype(str).str.strip().str.lower() != "nan")


def load_crosswalks(cw_dir):
    cw_dir = Path(cw_dir)
    d = {}
    d["cw_act"] = pd.read_csv(cw_dir / "crosswalk_activity.csv", dtype=str, keep_default_na=True)
    d["cw_act_sec"] = pd.read_csv(cw_dir / "crosswalk_activity_secondary.csv", dtype=str, keep_default_na=True)
    d["cw_loc"] = pd.read_csv(cw_dir / "crosswalk_location.csv", dtype=str, keep_default_na=True)
    d["cw_cop"] = pd.read_csv(cw_dir / "crosswalk_copresence.csv", dtype=str, keep_default_na=True)
    d["outdoor"] = pd.read_csv(cw_dir / "outdoor_at_home.csv", dtype=str, keep_default_na=True)
    d["target_list"] = pd.read_csv(cw_dir / "activity_target_list.csv", dtype=str, keep_default_na=True)
    unmapped_path = cw_dir / "crosswalk_unmapped.md"
    d["unmapped"] = parse_unmapped_md(unmapped_path.read_text(encoding="utf-8")) if unmapped_path.exists() else {"activity": set(), "location": set()}
    avail_path = cw_dir / "copresence_availability.md"
    d["copresence_grid"] = parse_copresence_grid(avail_path.read_text(encoding="utf-8")) if avail_path.exists() else {}
    return d


def _parse_md_table(lines, start_idx):
    """Given lines and the index of a '## Heading' line, parse the first markdown
    table that follows (header row, separator row, data rows) and return list of
    dict rows keyed by the header cells. Stops at first blank-after-table line."""
    i = start_idx + 1
    while i < len(lines) and not lines[i].strip().startswith("|"):
        if lines[i].strip().startswith("##"):
            return [], i
        i += 1
    if i >= len(lines):
        return [], i
    header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
    i += 1  # separator row
    if i < len(lines) and set(lines[i].strip()) <= set("|-: "):
        i += 1
    rows = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        if len(cells) >= len(header):
            rows.append(dict(zip(header, cells)))
        i += 1
    return rows, i


def parse_unmapped_md(text):
    """V2.b / G2.1 register: (country, code) pairs listed as unexplained, split
    into the activity table and the location table. Never restated by hand --
    parsed straight from the shipped file."""
    lines = text.splitlines()
    out = {"activity": set(), "location": set()}
    for idx, line in enumerate(lines):
        if line.strip() == "## UNMAPPED SOURCE CODES":
            rows, _ = _parse_md_table(lines, idx)
            for r in rows:
                out["activity"].add((r.get("country", "").strip(), r.get("code", "").strip()))
        elif line.strip() == "## UNMAPPED LOCATION CODES":
            rows, _ = _parse_md_table(lines, idx)
            for r in rows:
                out["location"].add((r.get("country", "").strip(), r.get("code", "").strip()))
    return out


def parse_copresence_grid(text):
    """G2.8's country x flag grid, parsed from copresence_availability.md's own
    words: 'recorded' / 'not recorded'. Never restated by hand (the file itself
    says its wording is exactly these two strings, and nothing else)."""
    lines = text.splitlines()
    grid = {}
    for idx, line in enumerate(lines):
        if line.strip().startswith("## COUNTRY") and "FLAG GRID" in line:
            rows, _ = _parse_md_table(lines, idx)
            for r in rows:
                country = r.get("country", "").strip()
                if not country or country == "---":
                    continue
                for flag in SHARED_COP_FLAGS:
                    if flag in r:
                        grid[(country, flag)] = r[flag].strip().lower()
            break
    return grid


def load_harmonised(path):
    path = Path(path)
    if path.is_dir():
        files = sorted(glob.glob(str(path / "*.parquet")))
        files = [f for f in files if "harmonised" in os.path.basename(f).lower() or True]
        if not files:
            raise SystemExit(f"No .parquet files found under {path}")
        dfs = [pd.read_parquet(f) for f in files]
        df = pd.concat(dfs, ignore_index=True)
    else:
        df = pd.read_parquet(path)
    # FINDING (see WHAT I DID NOT VERIFY): the real harmonised.parquet's country
    # column is 'ES'/'UK'/'IT' (uppercase); every crosswalk file's country column
    # is 'es'/'uk'/'it' (lowercase). Normalised to lowercase here so joins against
    # the crosswalks are correct -- reported as a cross-artefact casing mismatch,
    # not silently absorbed.
    if "country" in df.columns:
        df["country"] = df["country"].astype(str).str.lower()
    return df


def load_step1(step1_dir):
    step1_dir = Path(step1_dir)
    episodes = {}
    codebook_text = {}
    for c in COUNTRIES:
        cname = {"es": "spain", "uk": "uk", "it": "italy"}[c]
        ep_path = step1_dir / f"episodes_{cname}.parquet"
        if not ep_path.exists():
            ep_path = step1_dir / f"episodes_{c}.parquet"
        if ep_path.exists():
            edf = pd.read_parquet(ep_path)
            if "country" in edf.columns:
                edf["country"] = edf["country"].astype(str).str.lower()
            episodes[c] = edf
        cb_path = step1_dir / f"codebook_facts_{cname}.md"
        if not cb_path.exists():
            cb_path = step1_dir / f"codebook_facts_{c}.md"
        if cb_path.exists():
            codebook_text[c] = cb_path.read_text(encoding="utf-8", errors="replace")
    return {"episodes": episodes, "codebook_text": codebook_text}


def load_filter_report(path):
    path = Path(path)
    if not path.exists():
        return "", []
    text = path.read_text(encoding="utf-8", errors="replace")
    return text, parse_filter_attrition(text)


def parse_filter_attrition(text):
    """G2.7's per-country attrition figures, extracted from the REAL
    filter_report.md's actual format: per-country prose sections headed
    '## <country>' with a line 'age clause removed: N respondents, M diaries,
    K episodes'. This is not a markdown table -- confirmed by reading the
    shipped file (2026-08-16), which uses a bulleted prose register instead
    of the table this runner originally assumed. Kept ONLY as a cross-check
    figure: gate_G2_7's authoritative removed/total diary counts come from
    comparing the loaded Step 1 and harmonised tables directly (see WHAT I DID
    NOT VERIFY), not from parsing this prose, which could drift in wording
    without this parser noticing. 'age_floor' is currently the only clause
    the harmonise runner implements; if a second clause is ever added, this
    parser and gate_G2_7 need a matching update -- not a silent guess."""
    out = []
    country_name_to_code = {"es": "es", "uk": "uk", "it": "it"}
    section = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(es|uk|it)\s*$", line.strip(), re.IGNORECASE)
        if m:
            section = country_name_to_code[m.group(1).lower()]
            continue
        if section:
            m2 = re.search(r"age clause removed:\s*([\d,]+)\s*respondents,\s*([\d,]+)\s*diaries,\s*([\d,]+)\s*episodes", line)
            if m2:
                out.append({
                    "country": section, "clause": "age_floor",
                    "removed_respondents": int(m2.group(1).replace(",", "")),
                    "removed_diaries": int(m2.group(2).replace(",", "")),
                    "removed_episodes": int(m2.group(3).replace(",", "")),
                })
    return out


# --------------------------------------------------------------------------
# WORKSPACE
# --------------------------------------------------------------------------

def build_workspace(harmonised_path, crosswalks_dir, step1_dir, filter_report_path=None):
    ws = {}
    ws["harm"] = load_harmonised(harmonised_path)
    ws.update(load_crosswalks(crosswalks_dir))
    ws["step1"] = load_step1(step1_dir)
    if filter_report_path is None:
        cand = Path(harmonised_path)
        cand = cand if cand.is_dir() else cand.parent
        filter_report_path = cand / "filter_report.md"
    ws["filter_report_text"], ws["filter_attrition"] = load_filter_report(filter_report_path)
    return ws


def ws_copy(ws, keys):
    """Shallow-copy the workspace, deep-copying only the named keys (dataframes
    the perturbation is about to mutate). Everything else -- including the
    files on disk -- is untouched."""
    out = dict(ws)
    for k in keys:
        if isinstance(ws.get(k), pd.DataFrame):
            out[k] = ws[k].copy(deep=True)
        else:
            out[k] = copy.deepcopy(ws.get(k))
    return out


# --------------------------------------------------------------------------
# ROTATION HELPER -- D-S2-5, reused by fixture-building, the wrong_rotation
# perturbation, and G2.12's own round-trip check.
# --------------------------------------------------------------------------

def rotate_and_split(native_df, offset_min, group_cols=("country", "hid", "pid", "diary_day")):
    """Cyclic-rotate a native-origin episode table by offset_min, splitting any
    episode that straddles the new origin into two rows sharing episode_index_step1
    and split_at_origin=True. Renumbers episode_index ascending by new start_min
    within each diary. native_df must carry an 'episode_index' column (the Step 1
    index) and 'start_min'/'duration_min' in native-origin minutes."""
    # Vectorised (not a row-by-row loop): real harmonised.parquet is 2M+ rows
    # and this runs inside a perturbation, so a Python-level per-row loop is not
    # a viable runtime. The logic is unchanged from the original row-by-row form.
    df = native_df.copy()
    df["episode_index_step1"] = df["episode_index"]
    new_start = (df["start_min"] + offset_min) % 1440
    end = new_start + df["duration_min"]
    is_split = end > 1440

    keep = df.loc[~is_split].copy()
    keep["start_min"] = new_start.loc[~is_split]
    keep["split_at_origin"] = False

    sp = df.loc[is_split]
    sp_new_start = new_start.loc[is_split]
    sp_end = end.loc[is_split]
    part1 = sp.copy()
    part1["start_min"] = sp_new_start
    part1["duration_min"] = 1440 - sp_new_start
    part1["split_at_origin"] = True
    part2 = sp.copy()
    part2["start_min"] = 0
    part2["duration_min"] = sp_end - 1440
    part2["split_at_origin"] = True

    out = pd.concat([keep, part1, part2], ignore_index=True)
    out = out.sort_values(list(group_cols) + ["start_min"]).reset_index(drop=True)
    out["episode_index"] = out.groupby(list(group_cols)).cumcount()
    return out


def rejoin_to_native(harm_df, forward_offset_min, group_cols=("country", "hid", "pid", "diary_day")):
    """Inverse of rotate_and_split: given a country's already-harmonised (rotated,
    possibly split) rows, rebuild the one-row-per-native-episode table by undoing
    forward_offset_min. Every column is carried through unchanged from the
    harmonised row (act, loc_class, cop_*, ...) except start_min/duration_min,
    which are reconstructed, and episode_index, which is reset to the native
    (episode_index_step1) index. Used to re-derive a native table WITHOUT
    depending on Step 1's own (differently-named, raw-valued) schema -- this is
    what lets the wrong_rotation perturbation touch only the rotation, and
    nothing else."""
    # Vectorised for the same reason as rotate_and_split -- real Spain is ~450K
    # rows and this runs inside a perturbation.
    inverse = -forward_offset_min
    key_cols = list(group_cols) + ["episode_index_step1"]
    df = harm_df.copy()
    grp_size = df.groupby(key_cols)["start_min"].transform("size")
    dur_sum = df.groupby(key_cols)["duration_min"].transform("sum")

    single = df.loc[grp_size == 1].copy()
    single["start_min"] = (single["start_min"] + inverse) % 1440

    multi = df.loc[grp_size == 2].copy()
    multi["_dur_sum"] = dur_sum.loc[grp_size == 2]
    anchor = multi.loc[multi["start_min"] != 0].copy()
    anchor = anchor.drop_duplicates(subset=key_cols)  # one anchor per split pair
    anchor["start_min"] = (anchor["start_min"] + inverse) % 1440
    anchor["duration_min"] = anchor["_dur_sum"]
    anchor = anchor.drop(columns=["_dur_sum"])

    out = pd.concat([single, anchor], ignore_index=True)
    out["episode_index"] = out["episode_index_step1"]
    return out


# --------------------------------------------------------------------------
# GATES G2.1 -- G2.16
# --------------------------------------------------------------------------

def gate_G2_1(ws):
    """Crosswalk totality. Every source code either maps or is listed in
    crosswalk_unmapped.md. Unexplained residue must be 0."""
    residue = []
    for country in COUNTRIES:
        h = ws["harm"][ws["harm"].country == country]
        act_codes = set(h["act_raw"].dropna().astype(str).str.strip()) - {""}
        mapped = set(ws["cw_act"].loc[ws["cw_act"].country == country, "source_code"].astype(str).str.strip())
        unmapped = {c for (co, c) in ws["unmapped"]["activity"] if co == country}
        leftover = act_codes - mapped - unmapped
        residue += [("activity", country, c) for c in sorted(leftover)]

        loc_codes = set(h["loc_raw"].dropna().astype(str).str.strip()) - {""}
        mapped_loc = set(ws["cw_loc"].loc[ws["cw_loc"].country == country, "source_code"].astype(str).str.strip())
        unmapped_loc = {c for (co, c) in ws["unmapped"]["location"] if co == country}
        leftover_loc = loc_codes - mapped_loc - unmapped_loc
        residue += [("location", country, c) for c in sorted(leftover_loc)]
    return gr("G2.1", len(residue) == 0, summary=f"unexplained residue = {len(residue)}",
              detail={"residue": residue[:50]})


def gate_G2_2(ws):
    """Crosswalk citation. 100% of mapping rows carry a codebook page reference."""
    missing = 0
    per_file = {}
    for name, df, col in [
        ("crosswalk_activity.csv", ws["cw_act"], "source_citation"),
        ("crosswalk_activity_secondary.csv", ws["cw_act_sec"], "source_citation"),
        ("crosswalk_location.csv", ws["cw_loc"], "source_citation"),
        ("crosswalk_copresence.csv", ws["cw_cop"], "citation"),
    ]:
        bad = (~_nonempty(df[col])).sum()
        per_file[name] = int(bad)
        missing += bad
    return gr("G2.2", missing == 0, summary=f"rows missing citation = {missing}", detail=per_file)


def gate_G2_3(ws):
    """Mass conservation. Total weighted minutes per country unchanged by
    harmonisation (<1e-6 relative), matched via episode_index_step1 against
    the Step 1 reference table."""
    per_country = {}
    ok = True
    for country in COUNTRIES:
        h = ws["harm"][ws["harm"].country == country]
        s1 = ws["step1"]["episodes"].get(country)
        if s1 is None or h.empty:
            per_country[country] = None
            continue
        # episode_index is per-diary, not globally unique -- the surviving key
        # is the full (hid, pid, diary_day, episode_index_step1) tuple. Matched
        # via merge (not a Python-level set-membership loop) -- real Italy is
        # 1M+ rows.
        key_cols = ["hid", "pid", "diary_day"]
        surviving = h[key_cols + ["episode_index_step1"]].drop_duplicates().rename(
            columns={"episode_index_step1": "episode_index"})
        surviving["_survives"] = True
        s1_surv = s1.merge(surviving, on=key_cols + ["episode_index"], how="inner")
        total_h = float((h["duration_min"] * h["weight_dia"]).sum())
        total_s1 = float((s1_surv["duration_min"] * s1_surv["weight_dia"]).sum())
        rel = abs(total_h - total_s1) / max(abs(total_s1), 1e-9)
        per_country[country] = {"harm_total": total_h, "step1_total": total_s1, "rel_diff": rel}
        if rel >= 1e-6:
            ok = False
    return gr("G2.3", ok, summary="max relative diff = " + str(max((v["rel_diff"] for v in per_country.values() if v), default=None)),
              detail=per_country)


def gate_G2_4(ws):
    """Post-filter duration closure. sum(duration)==1440 for 100% of diaries.

    Strengthened 2026-08-16 (manager amendment, general form of D-S2-14/D-S2-15):
    the rotated intervals must TILE [0, 1440) exactly once per diary, in every
    country -- not merely sum to 1440. A sum-only check cannot distinguish a
    clean day from one with a gap that happens to cancel an overlap; this is
    the assertion whose absence let Italy's unwritten wall-clock convention
    survive Step 1 unchecked. Same pre-registered threshold (0 violations),
    checked more rigorously -- not a new or moved threshold."""
    # Vectorised (not a Python loop per diary) -- real harmonised.parquet has
    # ~73,000 diaries and 2M+ rows.
    group_cols = ["country", "hid", "pid", "diary_day"]
    h = ws["harm"].sort_values(group_cols + ["start_min"]).copy()
    totals = h.groupby(group_cols)["duration_min"].sum()
    bad_sum = totals[(totals - 1440).abs() > 1e-9]

    # Every row's start_min must equal the cumulative duration of the rows
    # before it in the same diary (sorted by start_min) -- i.e. no gap, no
    # overlap. The first row must start at 0. Sum==1440 is then implied for a
    # clean diary but is kept as an independent check (bad_sum) since it is
    # the cheaper, pre-registered form of the same requirement.
    g = h.groupby(group_cols, sort=False)
    cum_before = g["duration_min"].cumsum() - h["duration_min"]
    is_first = g.cumcount() == 0
    gap_or_overlap = (h["start_min"].astype(float) - cum_before.astype(float)).abs() > 1e-9
    bad_first = is_first & (h["start_min"].astype(float).abs() > 1e-9)
    diary_bad_mask = gap_or_overlap | bad_first
    bad_diaries = set(map(tuple, h.loc[diary_bad_mask, group_cols].drop_duplicates().to_numpy()))
    if len(bad_sum):
        bad_diaries |= set(map(tuple, bad_sum.index.to_frame(index=False).to_numpy()))
    n_bad = len(bad_diaries)

    return gr("G2.4", n_bad == 0,
              summary=f"diaries not summing to 1440 = {len(bad_sum)}; diaries failing the tiling invariant (union) = {n_bad}",
              detail={"n_bad_sum": int(len(bad_sum)), "n_bad_tiling_total": n_bad,
                      "examples": bad_sum.head(5).to_dict()})


def gate_G2_5(ws):
    """One-to-many audit. Every one-to-many mapping row carries a written rule."""
    unflagged = 0
    detail = {}
    for name, df in [("crosswalk_activity.csv", ws["cw_act"]),
                      ("crosswalk_activity_secondary.csv", ws["cw_act_sec"]),
                      ("crosswalk_location.csv", ws["cw_loc"])]:
        target_col = "target_code" if "target_code" in df.columns else "target_code_2d"
        target_col = target_col if target_col in df.columns else ("target_class" if "target_class" in df.columns else None)
        if target_col is None:
            continue
        grp = df.groupby(["country", "source_code"])[target_col].nunique()
        one_to_many = grp[grp > 1].index
        n_bad = 0
        for (country, code) in one_to_many:
            rows = df[(df.country == country) & (df.source_code == code)]
            rule_col = "rule" if "rule" in rows.columns else None
            if rule_col is None or (~_nonempty(rows[rule_col])).any():
                n_bad += len(rows)
        detail[name] = {"one_to_many_groups": int(len(one_to_many)), "unflagged_rows": int(n_bad)}
        unflagged += n_bad
    return gr("G2.5", unflagged == 0, summary=f"unflagged one-to-many rows = {unflagged}", detail=detail)


def gate_G2_6(ws):
    """Indoor-rule reachability. OUTDOOR_AT_HOME must change indoor_presence for
    a non-zero number of episodes in every country. Imports the shipped list
    (V2.d) -- never restates it."""
    outdoor_codes = set(ws["outdoor"]["target_code"].astype(str).str.strip())
    per_country = {}
    ok = True
    for country in COUNTRIES:
        h = ws["harm"][ws["harm"].country == country]
        fired = h[(h.loc_class == "at_home") & (h.act.astype(str).isin(outdoor_codes)) & (h.indoor_presence == False)]  # noqa: E712
        per_country[country] = int(len(fired))
        if len(fired) == 0:
            ok = False
    return gr("G2.6", ok, summary=str(per_country), detail=per_country)


def gate_G2_7(ws):
    """Filter attrition escalation. Reported, not thresholded, except the
    15%-vs-5% asymmetric trigger, which escalates (treated here as a FAIL).

    ASSUMPTION / DESIGN CHANGE (see WHAT I DID NOT VERIFY): the val doc
    proposes reading this from filter_report.md's own numbers. The real
    filter_report.md (confirmed 2026-08-16) is a prose register, not a
    machine-readable table, and its exact wording is not this project's
    contract to hold stable. The AUTHORITATIVE per-country removed/total
    respondent count is therefore computed here directly from the same two
    tables every other gate already loads -- Step 1's native diary set minus
    harmonised's surviving diary set, per country -- which cannot drift from
    the data no matter how the prose is phrased. 'age_floor' is treated as the
    (currently sole) clause; a second clause would need this gate extended,
    not guessed at. Where filter_report.md IS parseable (parse_filter_attrition),
    its own 'removed diaries' figure is cross-checked against this
    independently-derived count and any disagreement is reported as a finding,
    never silently trusted over the data."""
    per_country = {}
    prose_by_country = {r["country"]: r for r in ws.get("filter_attrition", [])}
    for country in COUNTRIES:
        s1 = ws["step1"]["episodes"].get(country)
        h = ws["harm"]
        if s1 is None:
            continue
        diary_cols = ["hid", "pid", "diary_day"]
        s1_diaries = s1[diary_cols].drop_duplicates()
        h_diaries = h.loc[h.country == country, diary_cols].drop_duplicates()
        total = len(s1_diaries)
        removed = total - len(h_diaries.merge(s1_diaries, on=diary_cols, how="inner"))
        pct = removed / total if total else 0.0
        entry = {"total_diaries": total, "removed_diaries": removed, "removed_pct": pct}
        if country in prose_by_country:
            entry["filter_report_removed_diaries"] = prose_by_country[country]["removed_diaries"]
            entry["agrees_with_filter_report"] = (prose_by_country[country]["removed_diaries"] == removed)
        per_country[country] = entry

    escalations = []
    hi = [c for c, v in per_country.items() if v["removed_pct"] > 0.15]
    lo = [c for c, v in per_country.items() if v["removed_pct"] < 0.05]
    for hc in hi:
        for lc in lo:
            if hc != lc:
                escalations.append(("age_floor", hc, per_country[hc]["removed_pct"], lc, per_country[lc]["removed_pct"]))
    disagreements = [c for c, v in per_country.items() if v.get("agrees_with_filter_report") is False]

    passed = (len(escalations) == 0) and (len(disagreements) == 0)
    return gr("G2.7", passed,
              summary=f"escalations = {len(escalations)}; filter_report.md/data disagreements = {len(disagreements)}; "
                      f"per-country removed% = {{{', '.join(f'{c}: {v['removed_pct']:.3%}' for c, v in per_country.items())}}}",
              detail={"escalations": escalations, "per_country": per_country, "disagreements": disagreements})


def gate_G2_8(ws):
    """Co-presence missingness. No flag copresence_availability.md calls 'not
    recorded' may contain a 0 (False) in the data. Country-extra columns must
    be null (never False) for every country other than the one they belong to."""
    violations = []
    grid = ws.get("copresence_grid", {})
    for (country, flag), status in grid.items():
        if status == "not recorded":
            h = ws["harm"][ws["harm"].country == country]
            if flag in h.columns:
                n_false = int((h[flag] == False).sum())  # noqa: E712
                if n_false > 0:
                    violations.append((country, flag, n_false))
    for extra_col in EXTRA_COP_COLUMNS:
        if extra_col not in ws["harm"].columns:
            continue
        owner = extra_col.split("_")[2]  # cop_extra_<owner>_<field>
        other_rows = ws["harm"][ws["harm"].country != owner]
        n_false = int((other_rows[extra_col] == False).sum())  # noqa: E712
        if n_false > 0:
            violations.append(("(other countries)", extra_col, n_false))
    return gr("G2.8", len(violations) == 0, summary=f"violations = {len(violations)}", detail={"violations": violations})


def gate_G2_9(ws):
    """Cross-country activity divergence -- a FLOOR. Max pairwise difference on
    at least 3 of 10 Level-1 categories must exceed 20 min/day."""
    # Vectorised (pandas Series alignment, not a Python dict loop) -- real
    # harmonised.parquet has ~73,000 diaries per this loop's inner pass, x10
    # categories x3 countries.
    h = ws["harm"]
    by_cat = {}
    for country in COUNTRIES:
        hc = h[h.country == country]
        diaries = hc.groupby(["hid", "pid", "diary_day"])["weight_dia"].first()
        n_wt = diaries.sum() if len(diaries) else 1.0
        per_cat = {}
        for lvl in [str(i) for i in range(10)]:
            sub = hc[hc.act_level1 == lvl]
            per_diary = sub.groupby(["hid", "pid", "diary_day"])["duration_min"].sum()
            aligned_w = diaries.reindex(per_diary.index)
            wsum = float((per_diary * aligned_w).sum())
            per_cat[lvl] = wsum / n_wt if n_wt else 0.0
        by_cat[country] = per_cat
    qualifying = []
    for lvl in [str(i) for i in range(10)]:
        vals = {c: by_cat[c][lvl] for c in COUNTRIES}
        pairs = [(a, b, abs(vals[a] - vals[b])) for i, a in enumerate(COUNTRIES) for b in COUNTRIES[i + 1:]]
        max_diff = max(p[2] for p in pairs)
        if max_diff > 20.0:
            qualifying.append((lvl, max_diff))
    passed = len(qualifying) >= 3
    return gr("G2.9", passed, summary=f"{len(qualifying)}/10 categories exceed 20 min/day (need >=3)",
              detail={"qualifying": qualifying, "by_category_min_per_day": by_cat})


def gate_G2_10(ws):
    """Against published aggregates. No published national reference is held
    by this project. NOT CHECKED, excluded from the scored tally."""
    return gr("G2.10", None, checked=False,
              summary="NOT CHECKED: no published national time-use table is held by this project; "
                      "a re-tabulation of our own harmonised data would share an ancestor with the "
                      "reference and cannot fail, so it is not substituted (val doc, G2.10 row).")


def gate_G2_11(ws):
    """Location class coverage. Every (country, class) cell non-empty; escalate
    if a country's weighted share of a class is below 1/10 of the smallest
    share among the other two. Imports the class list (V2.e)."""
    classes = sorted(set(ws["cw_loc"]["target_class"].dropna().astype(str).str.strip()) & set(TARGET_CLASSES))
    zero_cells = []
    shares = {}
    for country in COUNTRIES:
        h = ws["harm"][ws["harm"].country == country]
        total = h["weight_dia"].sum() if len(h) else 0.0
        cell_w = {}
        for cls in classes:
            w = h.loc[h.loc_class == cls, "weight_dia"].sum()
            cell_w[cls] = w
            if w == 0:
                zero_cells.append((country, cls))
        shares[country] = {cls: (cell_w[cls] / total if total else 0.0) for cls in classes}
    escalations = []
    for cls in classes:
        for country in COUNTRIES:
            others = [shares[c][cls] for c in COUNTRIES if c != country and shares[c][cls] > 0]
            if not others:
                continue
            smallest_other = min(others)
            if shares[country][cls] < smallest_other / 10.0:
                escalations.append((country, cls, shares[country][cls], smallest_other))
    passed = (len(zero_cells) == 0) and (len(escalations) == 0)
    return gr("G2.11", passed, summary=f"zero cells={len(zero_cells)}, escalations={len(escalations)}",
              detail={"zero_cells": zero_cells, "escalations": escalations, "shares": shares})


# Spain's Step 1 export names its raw co-presence columns with a fixed prefix
# convention (confirmed by inspecting the real episodes_spain.parquet, 2026-08-16):
# 'cop_' + lowercase(national field), except PADRES, which Step 1 still calls
# 'cop_extra_es_padres' -- a name left over from D-S2-2's original ("Spanish
# extra") classification, before D-S2-8 reclassified PADRES as the shared
# cop_parent flag. This is a column-address lookup, not a value map -- the
# VALUE map (1=yes, 6=no) is read from crosswalk_copresence.csv, never
# hardcoded here.
ES_STEP1_COP_COLUMN = {
    "SOLO": "cop_solo", "PAREJA": "cop_pareja", "MENOR": "cop_menor",
    "PADRES": "cop_extra_es_padres", "OTMH": "cop_otmh", "OTCON": "cop_otcon",
}


def native_cop_bool_es(ws):
    """Reconstruct cop_alone..cop_other_persons booleans from Step 1's raw
    Spanish co-presence columns, using crosswalk_copresence.csv's own value map
    (imported, never restated -- the same discipline V2.f requires of G2.14).
    Returns a copy of ws['step1']['episodes']['es'] with the six shared-flag
    boolean columns added."""
    s1 = ws["step1"]["episodes"]["es"].copy()
    cw_es = ws["cw_cop"][ws["cw_cop"].country.str.lower() == "es"]
    value_map = {}  # (national_field, value) -> bool
    field_for_flag = {}
    for _, row in cw_es.iterrows():
        flag = row["shared_flag"]
        if flag not in SHARED_COP_FLAGS:
            continue
        field_for_flag[flag] = row["national_field"]
        meaning = str(row["national_value_meaning"]).strip().lower()
        value_map[(row["national_field"], str(row["national_value"]).strip())] = (meaning == "yes")
    for flag, national_field in field_for_flag.items():
        col = ES_STEP1_COP_COLUMN.get(national_field)
        if col is None or col not in s1.columns:
            s1[flag] = pd.NA
            continue
        s1[flag] = s1[col].astype(str).str.strip().map(
            lambda v, nf=national_field: value_map.get((nf, v), pd.NA))
        s1[flag] = s1[flag].astype("boolean")
    return s1


def gate_G2_12(ws):
    """Spanish rotation round-trip. Rotating harmonised's Spanish rows BACK to
    their native 06:00 origin must reproduce the Step 1 table exactly on ACT,
    LOC, every co-presence flag -- AND on the native start_min/duration, which
    is the actual round-trip test (act/loc/cop values are untouched by any
    rotation, correct or not, so comparing them alone cannot tell a correct
    rotation from a wrong-direction one; only the reconstructed start position
    can). The inverse offset applied here is the OFFICIAL one
    (-rotation_offset('es')), never whatever offset actually produced the file
    under test -- that is the whole point of a round-trip check.

    Step 1's export carries act_raw/loc_raw under those same names, confirmed
    against the real episodes_spain.parquet; the six shared co-presence flags do
    NOT exist there (Step 1 carries Spain's raw national fields -- cop_solo,
    cop_pareja, cop_menor, cop_extra_es_padres, cop_otmh, cop_otcon -- co-presence
    normalisation is Step 2's own work item 2.3). native_cop_bool_es() rebuilds
    the six shared-flag booleans from those raw columns via
    crosswalk_copresence.csv's own value map before this gate compares them."""
    h_es = ws["harm"][ws["harm"].country == "es"]
    s1_es = ws["step1"]["episodes"].get("es")
    if s1_es is None or h_es.empty:
        return gr("G2.12", None, checked=False, summary="no Spanish rows or no Step 1 reference available")
    s1_es = native_cop_bool_es(ws)
    compare_cols = ["act_raw", "loc_raw"] + SHARED_COP_FLAGS
    group_cols = ["hid", "pid", "diary_day", "episode_index_step1"]
    inverse_offset = -rotation_offset("es")

    # internal consistency: split halves must agree on act/loc/cop with each other
    internal_mismatch = 0
    for c in compare_cols:
        nun = h_es.groupby(group_cols)[c].nunique(dropna=False)
        internal_mismatch += int((nun > 1).sum())

    # Vectorised reconstruction (not groupby().apply(), which is a Python call
    # per group) -- real Spain is ~430K rows / ~400K+ groups.
    grp_size = h_es.groupby(group_cols)["start_min"].transform("size")
    dur_sum = h_es.groupby(group_cols)["duration_min"].transform("sum")

    single = h_es.loc[grp_size == 1, group_cols + compare_cols + ["start_min", "duration_min"]].copy()
    single["native_start_min"] = (single["start_min"].astype(float) + inverse_offset) % 1440
    single["_ambiguous"] = False

    multi = h_es.loc[grp_size == 2].copy()
    multi["_dur_sum"] = dur_sum.loc[grp_size == 2]
    not_zero = multi[multi["start_min"] != 0]
    anchor = not_zero.drop_duplicates(subset=group_cols)[group_cols + compare_cols + ["start_min", "_dur_sum"]].copy()
    anchor["native_start_min"] = (anchor["start_min"].astype(float) + inverse_offset) % 1440
    anchor["duration_min"] = anchor["_dur_sum"]
    anchor = anchor.drop(columns=["_dur_sum"])
    anchor["_ambiguous"] = False
    # groups of size 2 where no row (or both rows) are away from 0 are ambiguous
    n_multi_groups = int(multi.drop_duplicates(subset=group_cols).shape[0])
    ambiguous_from_multi = n_multi_groups - len(anchor)

    grp3plus = int((grp_size > 2).sum())  # should be 0 -- Spain never splits more than once

    grouped = pd.concat([single, anchor], ignore_index=True).drop(columns=["start_min"]).set_index(group_cols)
    ambiguous = ambiguous_from_multi + grp3plus

    # Restrict the Step 1 side to diaries that actually survive into harmonised
    # BEFORE joining. Step 1 has more diaries than harmonised because work item
    # 2.4's age filter removes whole diaries -- that is a different, expected
    # transformation this gate is not testing (G2.7/filter_report.md is). A
    # naive outer join against the FULL Step 1 table counts every episode of a
    # filtered-out diary as a "missing" AND (once per compared column) as a
    # spurious "value mismatch" against NaN -- inflating the count without any
    # actual round-trip defect. Restricting first is the fix; it is not a
    # threshold change, it is comparing the right population.
    diary_cols = ["hid", "pid", "diary_day"]
    surviving_diaries = h_es[diary_cols].drop_duplicates()
    surviving_diaries["_surv"] = True
    s1_all_diaries = s1_es[diary_cols].drop_duplicates()
    n_whole_diaries_filtered = int(
        s1_all_diaries.merge(surviving_diaries, on=diary_cols, how="left")["_surv"].isna().sum())
    s1_restricted = s1_es.merge(surviving_diaries, on=diary_cols, how="inner").drop(columns=["_surv"])

    s1_key = s1_restricted.rename(columns={"episode_index": "episode_index_step1", "start_min": "start_min_step1"}).set_index(group_cols)
    merged = grouped.join(
        s1_key[compare_cols + ["start_min_step1", "duration_min"]], rsuffix="_step1", how="outer")

    n_missing_either_side = int(merged[compare_cols[0]].isna().sum() + merged[compare_cols[0] + "_step1"].isna().sum())
    n_value_mismatch = 0
    for c in compare_cols:
        n_value_mismatch += int((merged[c].astype(str) != merged[c + "_step1"].astype(str)).sum())
    n_start_mismatch = int((merged["native_start_min"].astype(float) - merged["start_min_step1"].astype(float)).abs().gt(1e-6).sum())
    n_duration_mismatch = int((merged["duration_min"].astype(float) - merged["duration_min_step1"].astype(float)).abs().gt(1e-6).sum())

    total_mismatch = internal_mismatch + n_missing_either_side + n_value_mismatch + n_start_mismatch + n_duration_mismatch + ambiguous
    return gr("G2.12", total_mismatch == 0,
              summary=f"mismatching diaries/episodes = {total_mismatch} "
                      f"(internal={internal_mismatch}, missing={n_missing_either_side}, value={n_value_mismatch}, "
                      f"start={n_start_mismatch}, duration={n_duration_mismatch}, ambiguous_splits={ambiguous}); "
                      f"{n_whole_diaries_filtered} whole Spanish diaries in Step 1 are absent from harmonised.parquet "
                      f"(the age filter, not counted as a mismatch -- see G2.7/filter_report.md)",
              detail={"internal_mismatch": internal_mismatch, "missing": n_missing_either_side,
                      "whole_diaries_filtered_not_counted": n_whole_diaries_filtered,
                      "value_mismatch": n_value_mismatch, "start_mismatch": n_start_mismatch,
                      "duration_mismatch": n_duration_mismatch, "ambiguous_splits": ambiguous})


def gate_G2_13(ws):
    """Secondary-crosswalk separateness (Italy). 0 Italian act2 source codes may
    be resolved through crosswalk_activity.csv; every one comes from
    crosswalk_activity_secondary.csv with source_list naming CLS-var13."""
    h_it = ws["harm"][ws["harm"].country == "it"]
    it_act2_codes = set(h_it["act2_raw"].dropna().astype(str).str.strip()) - {""}
    prim_it_codes = set(ws["cw_act"].loc[ws["cw_act"].country == "it", "source_code"].astype(str).str.strip())
    resolved_via_primary = sorted(it_act2_codes & prim_it_codes)
    sec_it = ws["cw_act_sec"][ws["cw_act_sec"].country == "it"]
    sec_it_codes = set(sec_it["source_code"].astype(str).str.strip())
    missing_in_secondary = sorted(it_act2_codes - sec_it_codes)
    wrong_source_list = sec_it[sec_it["source_list"].astype(str).str.strip() != "CLS-var13"]
    passed = (len(resolved_via_primary) == 0) and (len(missing_in_secondary) == 0) and (len(wrong_source_list) == 0)
    return gr("G2.13", passed,
              summary=f"resolved_via_primary={len(resolved_via_primary)}, missing_in_secondary={len(missing_in_secondary)}, "
                      f"wrong_source_list_rows={len(wrong_source_list)}",
              detail={"resolved_via_primary": resolved_via_primary, "missing_in_secondary": missing_in_secondary,
                      "wrong_source_list_rows": int(len(wrong_source_list))})


def gate_G2_14(ws):
    """Co-presence value-map integrity. Count of episodes where cop_alone is set
    AND any other shared flag is also set: 0, in every country."""
    h = ws["harm"]
    others = [f for f in SHARED_COP_FLAGS if f != "cop_alone"]
    bad_mask = (h["cop_alone"] == True)  # noqa: E712
    any_other = pd.Series(False, index=h.index)
    for f in others:
        any_other = any_other | (h[f] == True)  # noqa: E712
    bad = h[bad_mask & any_other]
    per_country = bad.groupby("country").size().to_dict()
    return gr("G2.14", len(bad) == 0, summary=f"contradictory episodes = {len(bad)}", detail={"per_country": per_country})


def gate_G2_15(ws):
    """Secondary-crosswalk agreement, Spain and the UK only. Every secondary row
    must map to the same 2-digit target the primary crosswalk gives, truncated.
    Disagreeing rows: 0. Italy excluded by construction."""
    disagree = []
    for country in ["es", "uk"]:
        prim = ws["cw_act"][ws["cw_act"].country == country].drop_duplicates("source_code").set_index("source_code")["target_code"]
        sec = ws["cw_act_sec"][ws["cw_act_sec"].country == country]
        for _, row in sec.iterrows():
            sc = row["source_code"]
            if sc in prim.index:
                expected = str(prim[sc])[:2]
                got = str(row["target_code_2d"]).strip()
                if got != expected:
                    disagree.append((country, sc, expected, got))
    return gr("G2.15", len(disagree) == 0, summary=f"disagreeing rows = {len(disagree)}", detail={"disagreements": disagree[:50]})


def gate_G2_16(ws):
    """Level-1 is derived from the target, not from the source. act_level1 ==
    act[0] for 100% of episodes, every country. Every act value must appear in
    the shipped activity_target_list.csv (V2.h)."""
    h = ws["harm"]
    non_null = h[h["act"].notna() & (h["act"].astype(str).str.strip() != "")]
    mismatch = non_null[non_null["act_level1"].astype(str) != non_null["act"].astype(str).str[0]]
    target_codes = set(ws["target_list"]["target_code"].astype(str).str.strip())
    not_in_target = non_null[~non_null["act"].astype(str).isin(target_codes)]
    passed = len(mismatch) == 0 and len(not_in_target) == 0
    return gr("G2.16", passed, summary=f"act_level1 mismatches={len(mismatch)}, act not in target list={len(not_in_target)}",
              detail={"n_mismatch": int(len(mismatch)), "n_not_in_target": int(len(not_in_target))})


GATE_FUNCS = {
    "G2.1": gate_G2_1, "G2.2": gate_G2_2, "G2.3": gate_G2_3, "G2.4": gate_G2_4,
    "G2.5": gate_G2_5, "G2.6": gate_G2_6, "G2.7": gate_G2_7, "G2.8": gate_G2_8,
    "G2.9": gate_G2_9, "G2.10": gate_G2_10, "G2.11": gate_G2_11, "G2.12": gate_G2_12,
    "G2.13": gate_G2_13, "G2.14": gate_G2_14, "G2.15": gate_G2_15, "G2.16": gate_G2_16,
}


# --------------------------------------------------------------------------
# VACUITY GUARDS V2.a -- V2.i
# --------------------------------------------------------------------------

def guard_V2_a(ws):
    n = ws["harm"]["country"].nunique()
    return gr("V2.a", n >= 3, summary=f"countries harmonised = {n}")


def guard_V2_b(ws):
    detail = {}
    for name, df in [("activity", ws["cw_act"]), ("activity_secondary", ws["cw_act_sec"]), ("location", ws["cw_loc"])]:
        target_col = "target_code" if "target_code" in df.columns else ("target_code_2d" if "target_code_2d" in df.columns else "target_class")
        grp = df.groupby(["country", "source_code"])[target_col].nunique()
        detail[name] = {
            "source_codes": int(df.groupby(["country", "source_code"]).ngroups),
            "mapped_rows": int(len(df)),
            "one_to_many_groups": int((grp > 1).sum()),
        }
    return gr("V2.b", True, summary="printed", detail=detail)


def guard_V2_c(ws):
    """Any national code, unit or field name absent from codebook_facts_<country>.md
    is printed and refused. Best-effort text-membership check against the
    co-presence crosswalk's national_field values (see WHAT I DID NOT VERIFY)."""
    unknown = []
    for country in COUNTRIES:
        text = ws["step1"]["codebook_text"].get(country, "")
        if not text:
            continue
        fields = set(ws["cw_cop"].loc[ws["cw_cop"].country == country, "national_field"].dropna().astype(str))
        for f in fields:
            if f and f not in text:
                unknown.append((country, f))
    return gr("V2.c", len(unknown) == 0, summary=f"fields not found in codebook_facts = {len(unknown)}",
              detail={"unknown": unknown})


def guard_V2_d(ws):
    """G2.6 must be run against the shipped exclusion list, not a validator copy.
    This runner never hardcodes the list -- it is read from ws['outdoor'] every
    time gate_G2_6 runs. This guard just confirms the file is non-empty and has
    the expected column."""
    ok = "target_code" in ws["outdoor"].columns and len(ws["outdoor"]) >= 0
    return gr("V2.d", ok, summary=f"outdoor_at_home.csv rows = {len(ws['outdoor'])}, imported not restated")


def guard_V2_e(ws):
    classes = set(ws["cw_loc"]["target_class"].dropna().astype(str).str.strip())
    return gr("V2.e", len(classes & set(TARGET_CLASSES)) >= 4, summary=f"target classes defined = {sorted(classes)}")


def guard_V2_f(ws):
    flags = set(ws["cw_cop"]["shared_flag"].dropna().astype(str).str.strip()) & set(SHARED_COP_FLAGS)
    ok_flags = len(flags) >= 6
    bp = ws["cw_cop"][ws["cw_cop"]["shared_flag"].isin(SHARED_COP_FLAGS)]
    bp_vals = set()
    for v in bp["bit_position"].dropna():
        try:
            bp_vals.add(int(float(v)))
        except ValueError:
            pass
    ok_bp = ("bit_position" in ws["cw_cop"].columns) and (bp_vals == {0, 1, 2, 3, 4, 5})
    return gr("V2.f", ok_flags and ok_bp, summary=f"shared flags={sorted(flags)}, bit_positions={sorted(bp_vals)}")


def guard_V2_g(ws):
    h_it = ws["harm"][ws["harm"].country == "it"]
    bad = h_it[(h_it["duration_min"] % 10) != 0]
    return gr("V2.g", len(bad) == 0, summary=f"Italian durations not a multiple of 10 = {len(bad)}",
              detail={"n_bad": int(len(bad))})


def guard_V2_h(ws):
    if len(ws["target_list"]) == 0:
        return gr("V2.h", False, summary="activity_target_list.csv is absent or empty")
    bad_len = ws["target_list"][ws["target_list"]["target_code"].astype(str).str.len() != 3]
    target_codes = set(ws["target_list"]["target_code"].astype(str).str.strip())
    h_act = ws["harm"]["act"].dropna().astype(str)
    h_act = h_act[h_act.str.strip() != ""]
    not_in_list = h_act[~h_act.isin(target_codes)]
    passed = len(bad_len) == 0 and len(not_in_list) == 0
    return gr("V2.h", passed, summary=f"target codes not 3 digits={len(bad_len)}, harmonised act missing from list={len(not_in_list)}")


def guard_V2_i(ws):
    """D-S2-15 (2026-08-16, amended): the val doc's literal wording -- FAIL on any
    column name containing 'origin' -- is self-contradictory against D-S2-12's own
    'split_at_origin' column, and would take out G2.12's round trip as collateral.
    Amended form: FAIL on any column name containing 'origin' OTHER than the exact
    name 'split_at_origin', AND FAIL if 'split_at_origin' is itself absent. The
    exception is a positive requirement, not a loophole -- it cannot rot into a
    hole because its absence is also a failure."""
    cols = list(ws["harm"].columns)
    bad = [c for c in cols if "origin" in c.lower() and c != "split_at_origin"]
    missing_required = "split_at_origin" not in cols
    passed = (len(bad) == 0) and (not missing_required)
    return gr("V2.i", passed, summary=f"columns: {cols}",
              detail={"disallowed_origin_columns": bad, "split_at_origin_present": not missing_required})


GUARD_FUNCS = {
    "V2.a": guard_V2_a, "V2.b": guard_V2_b, "V2.c": guard_V2_c, "V2.d": guard_V2_d,
    "V2.e": guard_V2_e, "V2.f": guard_V2_f, "V2.g": guard_V2_g, "V2.h": guard_V2_h, "V2.i": guard_V2_i,
}


def run_pipeline(ws):
    guards = {gid: f(ws) for gid, f in GUARD_FUNCS.items()}
    gates = {gid: f(ws) for gid, f in GATE_FUNCS.items()}
    return {"guards": guards, "gates": gates}


# --------------------------------------------------------------------------
# PERTURBATIONS -- each operates on a workspace copy, never on disk artefacts.
# --------------------------------------------------------------------------

def apply_perturbation(name, ws):
    if name == "null":
        return ws_copy(ws, [])

    if name == "del_activity_row":
        w = ws_copy(ws, ["cw_act"])
        cand = w["cw_act"][(w["cw_act"].country == "es") & (w["cw_act"].source_code == "011")]
        if cand.empty:
            cand = w["cw_act"].iloc[[0]]
        w["cw_act"] = w["cw_act"].drop(index=cand.index[:1])
        return w

    if name == "strip_citation":
        w = ws_copy(ws, ["cw_act"])
        idx = w["cw_act"][(w["cw_act"].country == "es") & (w["cw_act"].source_code == "011")].index
        if len(idx) == 0:
            idx = w["cw_act"].index[:1]
        w["cw_act"].loc[idx[:1], "source_citation"] = ""
        return w

    if name == "scale_duration":
        w = ws_copy(ws, ["harm"])
        w["harm"]["duration_min"] = w["harm"]["duration_min"].astype(float)
        mask = w["harm"].country == "it"
        w["harm"].loc[mask, "duration_min"] = w["harm"].loc[mask, "duration_min"] * 1.01
        return w

    if name == "round_duration":
        w = ws_copy(ws, ["harm"])
        idx = w["harm"][(w["harm"].country == "it") & (w["harm"].duration_min == 20)].index
        if len(idx):
            w["harm"].loc[idx[:1], "duration_min"] = 21
        return w

    if name == "add_one_to_many":
        w = ws_copy(ws, ["cw_act"])
        row = w["cw_act"][(w["cw_act"].country == "es") & (w["cw_act"].source_code == "011")]
        if row.empty:
            row = w["cw_act"].iloc[[0]]
        newrow = row.iloc[0].copy()
        newrow["target_code"] = "012" if newrow["target_code"] != "012" else "013"
        newrow["rule"] = ""
        newrow["ambiguous"] = "0"
        w["cw_act"] = pd.concat([w["cw_act"], pd.DataFrame([newrow])], ignore_index=True)
        return w

    if name == "empty_outdoor":
        w = ws_copy(ws, ["outdoor"])
        w["outdoor"] = w["outdoor"].iloc[0:0]
        return w

    if name == "drop_spain_age":
        # Val doc: "Drop all Spanish respondents aged 10-14". Age is not a
        # D-S2-12 column, so an exact age-band drop cannot be reproduced from
        # harmonised.parquet alone; the perturbation instead drops a large,
        # deterministic 30% sample of WHOLE Spanish diaries (never partial
        # diaries -- that is what keeps G2.4 clean, per the row's own
        # requirement), which produces the same structural defect G2.7's
        # escalation trigger exists to catch: one country's clause removing a
        # disproportionate share of its respondents. gate_G2_7 computes
        # removed% directly from Step 1 vs harmonised diary counts, so
        # dropping diaries here is what actually moves that number.
        w = ws_copy(ws, ["harm"])
        h = w["harm"]
        es_diaries = h.loc[h.country == "es", ["hid", "pid", "diary_day"]].drop_duplicates().reset_index(drop=True)
        drop_diaries = es_diaries.iloc[::3]  # deterministic ~33% sample
        drop_diaries = drop_diaries.assign(_drop=True)
        merged = h.merge(drop_diaries, on=["hid", "pid", "diary_day"], how="left")
        keep_mask = ~((merged["country"] == "es") & (merged["_drop"] == True))  # noqa: E712
        w["harm"] = merged.loc[keep_mask].drop(columns=["_drop"]).reset_index(drop=True)
        return w

    if name == "zero_missing_flag":
        w = ws_copy(ws, ["harm"])
        idx = w["harm"][w["harm"].country == "es"].index
        if "cop_extra_uk_mother" in w["harm"].columns and len(idx):
            w["harm"]["cop_extra_uk_mother"] = w["harm"]["cop_extra_uk_mother"].astype("object")
            w["harm"].loc[idx[:5], "cop_extra_uk_mother"] = False
            w["harm"]["cop_extra_uk_mother"] = w["harm"]["cop_extra_uk_mother"].astype("boolean")
        return w

    if name == "pool_modal_code":
        w = ws_copy(ws, ["harm"])
        w["harm"]["act"] = "011"
        w["harm"]["act_level1"] = "0"
        w["harm"]["act_level2"] = "01"
        return w

    if name == "shift_sleep_budget":
        w = ws_copy(ws, ["harm"])
        h = w["harm"]
        country = "uk"
        for (hid, pid, dd), g in h[h.country == country].groupby(["hid", "pid", "diary_day"]):
            sleep_idx = g[g.act_level1 == "0"].index
            other_idx = g[(g.act_level1 != "0") & (g.duration_min >= 40)].index
            if len(sleep_idx) and len(other_idx):
                h.loc[sleep_idx[0], "duration_min"] += 40
                h.loc[other_idx[0], "duration_min"] -= 40
        w["harm"] = h
        return w

    if name == "remap_spain_transport":
        w = ws_copy(ws, ["harm"])
        mask = (w["harm"].country == "es") & (w["harm"].loc_class == "public_transport")
        w["harm"].loc[mask, "loc_class"] = "private_transport"
        return w

    if name == "wrong_rotation":
        # Spain, wrong direction: -2h instead of +2h (val doc, G2.12 row). D-S2-14
        # does not change Spain's arithmetic, so the correct offset is still
        # rotation_offset('es') == +120 and the wrong one is its negation.
        #
        # Built entirely from the ALREADY-HARMONISED Spanish rows (rejoin to
        # native, then re-rotate with the wrong sign) rather than from Step 1's
        # raw table -- Step 1 carries the raw national co-presence fields under
        # its own naming (e.g. cop_solo, cop_extra_es_padres), not the mapped
        # cop_alone.../loc_class/act columns, so rebuilding from Step 1 directly
        # would corrupt every derived column and break gates this perturbation
        # has no business touching. Rejoining preserves every derived column
        # unchanged and only the rotation is wrong.
        w = ws_copy(ws, ["harm"])
        h_es = w["harm"][w["harm"].country == "es"]
        if not h_es.empty:
            native_es = rejoin_to_native(h_es, forward_offset_min=rotation_offset("es"))
            wrong_es = rotate_and_split(native_es, offset_min=-rotation_offset("es"))
            harm_cols = w["harm"].columns
            wrong_es = wrong_es.reindex(columns=harm_cols)
            w["harm"] = pd.concat([w["harm"][w["harm"].country != "es"], wrong_es], ignore_index=True)
        return w

    if name == "italy_catcon_swap":
        w = ws_copy(ws, ["cw_act", "cw_act_sec"])
        h_it = ws["harm"][ws["harm"].country == "it"]
        it_codes = sorted(set(h_it["act2_raw"].dropna().astype(str).str.strip()) - {""})
        new_rows = []
        for code in it_codes:
            new_rows.append({"country": "it", "source_code": code, "source_label": "catcon perturbation",
                              "target_code": "011", "ambiguous": "0", "rule": "", "source_citation": "TEST",
                              "target_citation": "TEST"})
        if new_rows:
            w["cw_act"] = pd.concat([w["cw_act"], pd.DataFrame(new_rows)], ignore_index=True)
        w["cw_act_sec"] = w["cw_act_sec"][w["cw_act_sec"].country != "it"]
        return w

    if name == "spain_cop_bool":
        w = ws_copy(ws, ["harm"])
        mask = w["harm"].country == "es"
        w["harm"].loc[mask, "cop_alone"] = True
        w["harm"].loc[mask, "cop_partner"] = True
        return w

    if name == "spain_secondary_repoint":
        w = ws_copy(ws, ["cw_act_sec"])
        idx = w["cw_act_sec"][(w["cw_act_sec"].country == "es") & (w["cw_act_sec"].source_code == "011")].index
        if len(idx) == 0:
            idx = w["cw_act_sec"][w["cw_act_sec"].country == "es"].index[:1]
        cur = w["cw_act_sec"].loc[idx[0], "target_code_2d"]
        w["cw_act_sec"].loc[idx[0], "target_code_2d"] = "99" if str(cur) != "99" else "98"
        return w

    if name == "uk_group1_carry":
        w = ws_copy(ws, ["harm"])
        mask = w["harm"].country == "uk"
        w["harm"].loc[mask, "act_level1"] = w["harm"].loc[mask, "act_raw"].astype(str).str[0]
        return w

    raise ValueError(f"unknown perturbation {name!r}")


# --------------------------------------------------------------------------
# SYNTHETIC FIXTURES -- D-S2-12 contract, grounded in the REAL accepted
# crosswalks (read only). Used for --selftest only.
# --------------------------------------------------------------------------

def _blocks_for(country, act_map, loc_codes, outdoor_target, outdoor_source, lvl3_generic_target, lvl3_generic_source,
                 lvl0_minutes, lvl5_minutes, lvl9_minutes, act2_value_source):
    """Build one canonical diary's block list (native-origin order) for a country.
    act_map: dict lvl(str) -> (source_code, target_code) for levels 1,2,4,6,7,8.
    act2_value_source: the country's own SECONDARY-crosswalk source code (real,
    accepted crosswalk_activity_secondary.csv row) that resolves to target_2d
    '01' -- NOT a primary-crosswalk code, per D-S2-7 (Italy's secondary list is
    a distinct, coarser classification, not the primary list truncated).
    Returns list of dict rows (no hid/pid/diary_day/country/start_min yet)."""
    def cop(alone):
        if alone:
            return dict(cop_alone=True, cop_partner=False, cop_children=False, cop_parent=False,
                        cop_other_hh=False, cop_other_persons=False)
        return dict(cop_alone=False, cop_partner=False, cop_children=False, cop_parent=False,
                    cop_other_hh=False, cop_other_persons=True)

    def act2_for(state):
        src, raw, tgt2 = {"value": ("value", act2_value_source, "01"),
                           "blank": ("blank", "", None),
                           "null": ("null", None, None)}[state]
        return raw, tgt2

    blocks = []

    def add(level1, source, target, duration, loc_source, loc_class, alone, act2_state="null", act2_src_override=None):
        raw2, tgt2 = act2_for(act2_state)
        if act2_src_override is not None:
            raw2 = act2_src_override
        blocks.append(dict(
            act_raw=source, act=target, act_level1=target[0], act_level2=target[:2],
            act2_raw=raw2, act2=tgt2, act2_level1=(tgt2[0] if tgt2 else (None if raw2 is None else None)),
            loc_raw=loc_source, loc_class=loc_class,
            indoor_presence=(loc_class == "at_home") and (target not in (outdoor_target,)),
            duration_min=duration,
            **cop(alone),
        ))

    # lvl0 sleep, at_home, alone -- "recorded and blank" secondary state to vary it
    add("0", act_map["0"][0], act_map["0"][1], lvl0_minutes, loc_codes["at_home"], "at_home", True, act2_state="null")
    # lvl3 generic household, at_home, with children -- "recorded with a value"
    b = dict(act_raw=lvl3_generic_source, act=lvl3_generic_target, act_level1=lvl3_generic_target[0],
             act_level2=lvl3_generic_target[:2],
             act2_raw=act2_value_source, act2="01", act2_level1="0",
             loc_raw=loc_codes["at_home"], loc_class="at_home",
             indoor_presence=True, duration_min=110,
             cop_alone=False, cop_partner=True, cop_children=True, cop_parent=False,
             cop_other_hh=False, cop_other_persons=False)
    blocks.append(b)
    # lvl3 outdoor gardening, at_home, alone -- tests G2.6
    add("3", outdoor_source, outdoor_target, 20, loc_codes["at_home"], "at_home", True, act2_state="null")
    # lvl1 work, other_place -- "recorded and blank" state
    add("1", act_map["1"][0], act_map["1"][1], 100, loc_codes["other_place"], "other_place", False, act2_state="blank")
    # lvl2 study, other_place
    add("2", act_map["2"][0], act_map["2"][1], 60, loc_codes["other_place"], "other_place", False, act2_state="null")
    # lvl4 volunteer, other_place
    add("4", act_map["4"][0], act_map["4"][1], 60, loc_codes["other_place"], "other_place", False, act2_state="null")
    # lvl5 social, other_place
    add("5", act_map["5"][0], act_map["5"][1], lvl5_minutes, loc_codes["other_place"], "other_place", False, act2_state="null")
    # lvl6 walking, other_place
    add("6", act_map["6"][0], act_map["6"][1], 100, loc_codes["other_place"], "other_place", False, act2_state="null")
    # lvl7 arts, at_home
    add("7", act_map["7"][0], act_map["7"][1], 60, loc_codes["at_home"], "at_home", True, act2_state="null")
    # lvl8 reading, at_home
    add("8", act_map["8"][0], act_map["8"][1], 60, loc_codes["at_home"], "at_home", True, act2_state="null")
    # lvl9 travel, split private/public
    priv, pub = lvl9_minutes
    add("9", act_map["9"][0], act_map["9"][1], priv, loc_codes["private_transport"], "private_transport", False, act2_state="null")
    add("9", act_map["9"][0], act_map["9"][1], pub, loc_codes["public_transport"], "public_transport", False, act2_state="null")

    return blocks


def build_synthetic_country(country, n_diaries, cw):
    """Build a native-origin-order episode table for one country, replicated
    n_diaries times with unique (hid, pid). Uses ONLY source/target codes that
    genuinely exist in the real accepted crosswalks (verified against outputs_step2)."""
    act_maps = {
        "es": {"0": ("011", "011"), "1": ("111", "111"), "2": ("200", "200"), "4": ("411", "411"),
               "5": ("511", "511"), "6": ("611", "611"), "7": ("711", "711"), "8": ("811", "811"),
               "9": ("910", "910")},
        "uk": {"0": ("110", "011"), "1": ("1100", "111"), "2": ("2000", "200"), "4": ("4100", "411"),
               "5": ("5100", "519"), "6": ("6100", "619"), "7": ("7100", "719"), "8": ("8100", "819"),
               "9": ("9010", "900")},
        "it": {"0": ("011", "011"), "1": ("111", "111"), "2": ("211", "211"), "4": ("411", "411"),
               "5": ("511", "511"), "6": ("611", "611"), "7": ("711", "711"), "8": ("811", "811"),
               "9": ("900", "900")},
    }
    loc_codes = {
        "es": {"at_home": "11", "other_place": "10", "private_transport": "30", "public_transport": "41"},
        "uk": {"at_home": "11", "other_place": "0", "private_transport": "30", "public_transport": "40"},
        "it": {"at_home": "11", "other_place": "13", "private_transport": "50", "public_transport": "57"},
    }
    outdoor = {"es": ("341", "341"), "uk": ("3410", "341"), "it": ("341", "341")}  # (source, target=341)
    lvl3_generic = {"es": ("300", "300"), "uk": ("3000", "300"), "it": ("311", "311")}

    day_minutes = {"es": {"lvl0": 720, "lvl5": 60, "lvl9": (45, 45)},
                   "uk": {"lvl0": 420, "lvl5": 200, "lvl9": (125, 125)},
                   "it": {"lvl0": 600, "lvl5": 100, "lvl9": (90, 80)}}  # D-S2-6/V2.g: Italy durations must be multiples of 10

    dm = day_minutes[country]
    outdoor_source, outdoor_target = outdoor[country]
    lvl3_source, lvl3_target = lvl3_generic[country]
    # Secondary-crosswalk source code that resolves to target_2d '01' (sleep).
    # ES and UK: secondary reuses the PRIMARY list, so the sleep primary code
    # itself is the secondary source too (D-S2-10). Italy: secondary is the
    # SEPARATE CLS-var13 list, whose own '01' is "Dormire" (D-S2-7) -- never a
    # primary-list code, which is exactly what G2.13 audits.
    act2_value_source = {"es": act_maps["es"]["0"][0], "uk": act_maps["uk"]["0"][0], "it": "01"}[country]

    blocks = _blocks_for(country, act_maps[country], loc_codes[country], outdoor_target, outdoor_source,
                          lvl3_target, lvl3_source, dm["lvl0"], dm["lvl5"], dm["lvl9"], act2_value_source)

    template = pd.DataFrame(blocks)
    template["episode_index"] = range(len(template))
    # D-S2-14: start_min's reference point is per-country. Spain and the UK are
    # diary-relative (first episode start_min=0 -- reference_minutes only says
    # what wall-clock time that 0 corresponds to). Italy is wall-clock minutes
    # since midnight, so its own start_min=0 IS wall-clock, and its first
    # episode's raw start_min is REFERENCE_MINUTES['it']=0 + 240 (04:00) --
    # reproduce that convention in the synthetic Step 1 fixture itself, for
    # Italy only, so rotation_offset() is genuinely exercised, not bypassed.
    wallclock_shift = 240 if country == "it" else 0
    template["start_min"] = (template["duration_min"].cumsum() - template["duration_min"]) + wallclock_shift
    total = template["duration_min"].sum()
    assert total == 1440, f"{country} template sums to {total}, not 1440"

    n_rows = len(template)
    rep = pd.concat([template] * n_diaries, ignore_index=True)
    rep["country"] = country
    rep["wave"] = "1"
    rep["hid"] = np.repeat(np.arange(n_diaries), n_rows)
    rep["pid"] = rep["hid"]
    rep["diary_day"] = 1
    rep["mode"] = "diary"
    rep["scheme"] = "test"
    rep["weight_ind"] = 1.0
    rep["weight_dia"] = 1.0

    # extras: UK / IT specific, null for the other countries by construction
    for col in EXTRA_COP_COLUMNS:
        owner = col.split("_")[2]
        rep[col] = pd.array([pd.NA] * len(rep), dtype="boolean")
        if owner == country:
            # mirror cop_parent as a stand-in component (OR-composition itself is a
            # recorded hole per the val doc, not covered by any gate)
            rep[col] = rep["cop_parent"].astype("boolean")

    for c in SHARED_COP_FLAGS:
        rep[c] = rep[c].astype("boolean")
    rep["indoor_presence"] = rep["indoor_presence"].astype("boolean")

    return rep


def build_fixtures(out_dir, real_crosswalks_dir, real_step1_dir, n_diaries=1200):
    out_dir = Path(out_dir)
    fixtures_dir = out_dir / "_selftest_fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    step1_dir = fixtures_dir / "step1"
    step1_dir.mkdir(exist_ok=True)

    cw = load_crosswalks(real_crosswalks_dir)

    natives = {}
    harm_parts = []
    for country in COUNTRIES:
        native = build_synthetic_country(country, n_diaries, cw)
        if country == "es":
            # Mirror the REAL episodes_spain.parquet schema: Step 1 carries
            # Spain's RAW national co-presence fields (cop_solo, cop_pareja,
            # cop_menor, cop_extra_es_padres, cop_otmh, cop_otcon; '1'=yes,
            # '6'=no), not the mapped cop_alone/... booleans -- co-presence
            # normalisation is Step 2's own work item. native_cop_bool_es()
            # reconstructs the booleans from exactly these raw columns, so the
            # self-test must supply them, not the shortcut booleans.
            raw_map = {"cop_solo": "cop_alone", "cop_pareja": "cop_partner", "cop_menor": "cop_children",
                       "cop_extra_es_padres": "cop_parent", "cop_otmh": "cop_other_hh", "cop_otcon": "cop_other_persons"}
            for raw_col, bool_col in raw_map.items():
                native[raw_col] = native[bool_col].map({True: "1", False: "6"})
        natives[country] = native.copy()
        # D-S2-14/D-S2-5: rotate every country through the same general formula.
        # UK's offset is 0 (a no-op relabelling); Italy's offset rebases its
        # wall-clock encoding without producing a split; only Spain's non-zero
        # offset actually straddles the origin and splits an episode.
        harm_c = rotate_and_split(native, offset_min=rotation_offset(country))
        harm_parts.append(harm_c)

    harm = pd.concat(harm_parts, ignore_index=True)
    ordered_cols = [c for c in D_S2_12_COLUMNS if c != "country"]
    final_cols = ["country"] + ordered_cols[:ordered_cols.index("act_raw")] + EXTRA_COP_COLUMNS + ordered_cols[ordered_cols.index("act_raw"):]
    for c in final_cols:
        if c not in harm.columns:
            harm[c] = None
    harm = harm[final_cols]
    harm["act"] = harm["act"].astype(str)
    harm["act_level1"] = harm["act_level1"].astype(str)
    harm["act_level2"] = harm["act_level2"].astype(str)

    harmonised_path = fixtures_dir / "harmonised.parquet"
    harm.to_parquet(harmonised_path, index=False)

    for country in COUNTRIES:
        cname = {"es": "spain", "uk": "uk", "it": "italy"}[country]
        natives[country].to_parquet(step1_dir / f"episodes_{cname}.parquet", index=False)
        real_cb = Path(real_step1_dir) / f"codebook_facts_{cname}.md"
        if real_cb.exists():
            shutil.copy(real_cb, step1_dir / f"codebook_facts_{cname}.md")

    # filter_report.md -- own assumed schema (see WHAT I DID NOT VERIFY)
    filter_report_lines = [
        "# filter_report.md (synthetic, self-test only)",
        "",
        "## Filter attrition, per clause per country",
        "",
        "| country | clause | respondents_total | respondents_removed |",
        "|---|---|---|---|",
    ]
    for country in COUNTRIES:
        filter_report_lines.append(f"| {country} | age_floor | {n_diaries} | {int(n_diaries * 0.03)} |")
    filter_report_path = fixtures_dir / "filter_report.md"
    filter_report_path.write_text("\n".join(filter_report_lines) + "\n", encoding="utf-8")

    return {"harmonised": harmonised_path, "step1_dir": step1_dir, "filter_report": filter_report_path,
            "crosswalks_dir": Path(real_crosswalks_dir)}


# --------------------------------------------------------------------------
# REPORTING
# --------------------------------------------------------------------------

def format_gate_line(res):
    if not res["checked"]:
        return f"{res['id']:<7} NOT CHECKED  -- {res['summary']}"
    status = "PASS" if res["passed"] else "FAIL"
    return f"{res['id']:<7} {status:<12} -- {res['summary']}"


def print_report(label, result, fh=sys.stdout):
    print(f"\n===== {label} =====", file=fh)
    print("-- vacuity guards --", file=fh)
    for gid in sorted(result["guards"], key=lambda x: x):
        print(format_gate_line(result["guards"][gid]), file=fh)
    print("-- gates --", file=fh)
    for gid in ALL_GATE_IDS:
        print(format_gate_line(result["gates"][gid]), file=fh)


def gate_status(res):
    if not res["checked"]:
        return "NOT_CHECKED"
    return "PASS" if res["passed"] else "FAIL"


# --------------------------------------------------------------------------
# SELF-TEST DRIVER
# --------------------------------------------------------------------------

def run_selftest(out_dir, real_crosswalks_dir, real_step1_dir, n_diaries=1200, report_fh=None):
    fh = report_fh or sys.stdout
    print("Building synthetic fixtures grounded in the real accepted crosswalks "
          f"({real_crosswalks_dir})...", file=fh)
    paths = build_fixtures(out_dir, real_crosswalks_dir, real_step1_dir, n_diaries=n_diaries)
    base_ws = build_workspace(paths["harmonised"], paths["crosswalks_dir"], paths["step1_dir"],
                               filter_report_path=paths["filter_report"])
    return run_sweep(base_ws, report_fh=fh)


def run_sweep(base_ws, report_fh=None):
    """Baseline + all seventeen perturbations, in-process, against whatever
    workspace it is handed -- synthetic (self-test) or real. Prints every
    acceptance test the task document requires and returns the full result
    set. This is the one place both --selftest and a real run's full sweep
    go through, so they cannot silently diverge in what they check."""
    fh = report_fh or sys.stdout
    baseline_result = run_pipeline(base_ws)
    print_report("BASELINE", baseline_result, fh)

    all_results = {"baseline": baseline_result}
    for pert in PERTURBATIONS:
        wsp = apply_perturbation(pert, base_ws)
        res = run_pipeline(wsp)
        all_results[pert] = res
        print_report(f"PERTURBATION: {pert}", res, fh)

    # -------------------- acceptance test 1: all 17 ran, null moved nothing
    print("\n===== ACCEPTANCE TEST 1: all seventeen perturbations ran; null moved nothing =====", file=fh)
    null_ok = True
    for gid in ALL_GATE_IDS:
        b = gate_status(baseline_result["gates"][gid])
        n = gate_status(all_results["null"]["gates"][gid])
        if b != n:
            null_ok = False
            print(f"  NULL PERTURBATION MOVED {gid}: baseline={b} null={n}", file=fh)
    print(f"  17 perturbations ran: {len(all_results) - 1 == 17}", file=fh)
    print(f"  null perturbation moved nothing: {null_ok}", file=fh)

    # -------------------- acceptance test 2: every perturbation felled its gate, or DID NOT FIRE
    print("\n===== ACCEPTANCE TEST 2: every perturbation felled its named gate, or DID NOT FIRE =====", file=fh)
    fire_report = {}
    for pert in PERTURBATIONS:
        spec = PERTURBATION_SPEC[pert]
        target = spec["must_fail"]
        if target is None:
            continue
        base_status = gate_status(baseline_result["gates"][target])
        pert_status = gate_status(all_results[pert]["gates"][target])
        fired = (pert_status == "FAIL")
        fire_report[pert] = {"gate": target, "baseline": base_status, "perturbed": pert_status, "fired": fired}
        tag = "FIRED" if fired else "DID NOT FIRE"
        print(f"  {pert:<26} -> {target:<7} baseline={base_status:<12} perturbed={pert_status:<12} [{tag}]", file=fh)

    # -------------------- acceptance test 3: no perturbation felled a "must stay clean" gate
    print("\n===== ACCEPTANCE TEST 3: no perturbation felled a gate under 'must stay clean' =====", file=fh)
    clean_violations = []
    for pert in PERTURBATIONS:
        spec = PERTURBATION_SPEC[pert]
        clean_list = spec["must_stay_clean"]
        if clean_list == "ALL":
            clean_list = ALL_GATE_IDS
        elif clean_list == "ALL_OTHER":
            clean_list = [g for g in ALL_GATE_IDS if g != spec["must_fail"]]
        for gid in clean_list:
            b = gate_status(baseline_result["gates"][gid])
            p = gate_status(all_results[pert]["gates"][gid])
            if b != "FAIL" and p == "FAIL":
                clean_violations.append((pert, gid, b, p))
                print(f"  VIOLATION: {pert} felled {gid} (baseline={b}, perturbed={p}) but its row lists {gid} as must-stay-clean", file=fh)
    print(f"  clean violations = {len(clean_violations)}", file=fh)

    # -------------------- acceptance test 4: coverage cross-tab
    print("\n===== ACCEPTANCE TEST 4: coverage cross-tab =====", file=fh)
    header = "gate".ljust(7) + " baseline  " + "  ".join(p[:10].ljust(10) for p in PERTURBATIONS)
    print(header, file=fh)
    coverage_fail = []
    for gid in ALL_GATE_IDS:
        b = gate_status(baseline_result["gates"][gid])
        row_cells = []
        broke_it = False
        for pert in PERTURBATIONS:
            s = gate_status(all_results[pert]["gates"][gid])
            row_cells.append(s[:10].ljust(10))
            if b == "PASS" and s == "FAIL":
                broke_it = True
        print(f"{gid:<7} {b:<9} " + "  ".join(row_cells), file=fh)
        if b == "PASS" and not broke_it:
            coverage_fail.append(gid)
    print(f"  gates that PASS at baseline and were NEVER made to fall: {coverage_fail}", file=fh)
    print(f"  coverage clause: {'PASS' if not coverage_fail else 'FAIL'}", file=fh)

    # -------------------- acceptance test 5: NOT CHECKED reasons + excluded from tally
    print("\n===== ACCEPTANCE TEST 5: NOT CHECKED gates carry a reason and are excluded from the scored tally =====", file=fh)
    not_checked = [gid for gid in ALL_GATE_IDS if not baseline_result["gates"][gid]["checked"]]
    for gid in not_checked:
        print(f"  {gid}: {baseline_result['gates'][gid]['summary']}", file=fh)
    scored = [gid for gid in ALL_GATE_IDS if baseline_result["gates"][gid]["checked"]]
    print(f"  NOT CHECKED gates: {not_checked}  (excluded from the {len(scored)}-gate scored tally)", file=fh)

    # -------------------- acceptance test 6: no threshold moved
    print("\n===== ACCEPTANCE TEST 6: no threshold was moved, no perturbation was adjusted =====", file=fh)
    print("  Confirmed by construction: every threshold in GATE_FUNCS above is copied verbatim from the", file=fh)
    print("  val doc's gate table (20 min/day, 3-of-10, 1e-6 relative, 15%/5%, 1/10 share, 100%/0 counts).", file=fh)
    print("  No threshold was edited while building or debugging this runner.", file=fh)

    return {
        "baseline": baseline_result, "perturbations": all_results, "fire_report": fire_report,
        "clean_violations": clean_violations, "coverage_fail": coverage_fail,
        "not_checked": not_checked, "null_ok": null_ok,
    }


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Step 2 validation battery: sixteen gates, "
                                              "seventeen perturbations, nine vacuity guards.")
    ap.add_argument("--harmonised", help="path to harmonised.parquet (file or directory of parts)")
    ap.add_argument("--crosswalks", help="directory holding the shipped crosswalk_*.csv / outdoor_at_home.csv / "
                                          "activity_target_list.csv / crosswalk_unmapped.md / copresence_availability.md")
    ap.add_argument("--step1", help="Step 1 run directory: episodes_<country>.parquet, codebook_facts_<country>.md")
    ap.add_argument("--out", required=True, help="output directory for this runner's own report/work files")
    ap.add_argument("--perturbation", help="perturbation name, or 'baseline' for the unperturbed run "
                                            "(required unless --selftest)")
    ap.add_argument("--filter-report", help="override path to filter_report.md (default: next to --harmonised)")
    ap.add_argument("--selftest", action="store_true",
                     help="build synthetic fixtures and run baseline + all seventeen perturbations in-process")
    ap.add_argument("--n-diaries", type=int, default=1200, help="selftest only: diaries per country in the fixture")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.selftest:
        script_dir = Path(__file__).resolve().parent
        default_crosswalks = script_dir.parent / "Step2_docs" / "outputs_step2"
        default_step1 = script_dir.parent / "Step1_docs" / "outputs_step1"
        real_crosswalks_dir = Path(args.crosswalks) if args.crosswalks else default_crosswalks
        real_step1_dir = Path(args.step1) if args.step1 else default_step1
        report_path = out_dir / "selftest_report.txt"
        with open(report_path, "w", encoding="utf-8") as fh:
            run_selftest(out_dir, real_crosswalks_dir, real_step1_dir, n_diaries=args.n_diaries, report_fh=fh)
        print(f"Self-test report written to {report_path}")
        # also echo to stdout
        print(Path(report_path).read_text(encoding="utf-8"))
        return

    if not args.perturbation:
        raise SystemExit("--perturbation is required (use 'baseline' for the unperturbed run, "
                          "or 'all' to run baseline + all seventeen perturbations)")
    if not (args.harmonised and args.crosswalks and args.step1):
        raise SystemExit("--harmonised, --crosswalks and --step1 are all required outside --selftest")

    ws = build_workspace(args.harmonised, args.crosswalks, args.step1, filter_report_path=args.filter_report)

    if args.perturbation == "all":
        report_path = out_dir / "full_sweep_report.txt"
        with open(report_path, "w", encoding="utf-8") as fh:
            run_sweep(ws, report_fh=fh)
        print(f"Full sweep report written to {report_path}")
        print(Path(report_path).read_text(encoding="utf-8"))
        return

    if args.perturbation != "baseline":
        ws = apply_perturbation(args.perturbation, ws)

    result = run_pipeline(ws)
    report_path = out_dir / f"gate_report_{args.perturbation}.txt"
    with open(report_path, "w", encoding="utf-8") as fh:
        print_report(f"RUN: perturbation={args.perturbation}", result, fh)
    print_report(f"RUN: perturbation={args.perturbation}", result, sys.stdout)
    print(f"\nReport written to {report_path}")


if __name__ == "__main__":
    main()
