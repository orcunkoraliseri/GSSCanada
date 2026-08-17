"""
Step 2, work item 2.4 -- build harmonised.parquet for one country.

Governing spec: 4J_docs_occ/Step2_docs/4thJ_02_harmonisation.md, D-S2-2 .. D-S2-13,
work item 2.4, and the OUTPUTS AND INTERFACES table. D-S2-12 is the record contract,
D-S2-13 is the age floor. Both are binding.

Usage (one country per job):
    python 4thJ_harmonise_step2.py --in <run dir> --crosswalks <dir> --out <dir> \
        --country <es|it|uk> --age-floor <int>

--age-floor has NO default on purpose (D-S2-13): a floor that lives in a default is a
floor nobody can see being changed.
"""

import argparse
import sys
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Data tables, not comments. Discovered in TASK 0 (schema_dump.txt / schema_dump2.txt)
# against outputs_step1/run_20260816-2210/episodes_{spain,uk,italy}.parquet.
# ---------------------------------------------------------------------------

COUNTRY_FILE = {"es": "episodes_spain.parquet", "uk": "episodes_uk.parquet", "it": "episodes_italy.parquet"}
COUNTRY_CODEBOOK = {"es": "codebook_facts_spain.md", "uk": "codebook_facts_uk.md", "it": "codebook_facts_italy.md"}
COUNTRY_CROSSWALK_TAG = {"es": "es", "uk": "uk", "it": "it"}

# D-S2-5: measured native origins, asserted against codebook_facts_<country>.md.
NATIVE_ORIGIN_HOUR = {"es": 6, "uk": 4, "it": 4}

# D-S2-14 (2026-08-16, manager ruling): Step 1's record contract names start_min but never says
# what minute zero denotes on the wall clock -- an unwritten convention that happened to be
# diary-relative (== the diary's own stated origin) for Spain and the UK, and wall-clock-since-
# midnight for Italy. reference_minutes makes that convention an explicit, checkable property:
# it is the wall-clock time that start_min == 0 denotes, per country, as delivered by Step 1.
# Measured directly (TASK 0 follow-up investigation, jobs 1252921/1252930): Spain's and the UK's
# first episode of every diary is at start_min=0, which is exactly their own native origin hour --
# so reference_minutes == native_origin_hour*60 for them. Italy's first episode of every diary is
# at start_min=240 (four hours after its own wall-clock 00:00 reference), never 0, so Italy's
# reference_minutes is 0 (midnight), not 240 (its stated native origin hour).
REFERENCE_MINUTES = {"es": 360, "uk": 240, "it": 0}

# D-S2-13: Italy's eleven age bands, (code, lower, upper). METADATI var20.html.
ITALY_AGE_BANDS = [
    ("01", 0, 2), ("02", 3, 5), ("03", 6, 10), ("04", 11, 14), ("05", 15, 24),
    ("06", 25, 34), ("07", 35, 44), ("08", 45, 54), ("09", 55, 64), ("10", 65, 74),
    ("11", 75, 200),
]

# TASK 0 finding: the raw co-presence column names Step 1 actually wrote do not
# follow one uniform naming rule (Spain's PADRES is the exception: it is named
# cop_extra_es_padres in the parquet even though it maps to the shared cop_parent
# flag, a holdover from the superseded D-S2-2 naming). Recorded here as data,
# discovered, not assumed, and asserted against the live dataframe at runtime.
RAW_COP_COLUMN = {
    "es": {
        "SOLO": "cop_solo", "PAREJA": "cop_pareja", "PADRES": "cop_extra_es_padres",
        "MENOR": "cop_menor", "OTMH": "cop_otmh", "OTCON": "cop_otcon",
    },
    "uk": {
        "WithAlone": "cop_extra_uk_WithAlone", "WithSpouse": "cop_extra_uk_WithSpouse",
        "WithMother": "cop_extra_uk_WithMother", "WithFather": "cop_extra_uk_WithFather",
        "WithChild": "cop_extra_uk_WithChild", "WithOther": "cop_extra_uk_WithOther",
        "WithOtherYK": "cop_extra_uk_WithOtherYK", "WithMiss": "cop_extra_uk_WithMiss",
        "WithNA": "cop_extra_uk_WithNA",
    },
    "it": {
        "daso": "cop_extra_it_daso", "cmadre": "cop_extra_it_cmadre", "cpadre": "cop_extra_it_cpadre",
        "cconiu": "cop_extra_it_cconiu", "cfigli": "cop_extra_it_cfigli", "cfrate": "cop_extra_it_cfrate",
        "afacon": "cop_extra_it_afacon", "aperco": "cop_extra_it_aperco",
    },
}

# D-S2-12 record contract, minus the country-varying cop_extra_* block which is
# appended at runtime from crosswalk_copresence.csv.
BASE_COLUMNS_HEAD = [
    "country", "wave", "hid", "pid", "diary_day",
    "episode_index", "episode_index_step1", "split_at_origin",
    "start_min", "duration_min",
    "act", "act_level1", "act_level2",
    "act2", "act2_level1",
    "loc_class", "indoor_presence",
    "cop_alone", "cop_partner", "cop_children", "cop_parent", "cop_other_hh", "cop_other_persons",
]
BASE_COLUMNS_TAIL = [
    "act_raw", "act2_raw", "loc_raw",
    "mode", "scheme", "weight_ind", "weight_dia",
]

# Manager ruling, 2026-08-16: D-S2-12's column list is not a closed enumeration -- it already
# ends "cop_extra_<country>_<field> ...", a pattern, not a name -- and the governing principle
# ("a transform that discards its inputs cannot be audited") is the same one that keeps act_raw/
# act2_raw/loc_raw and the UK's WithMother/WithFather in the table. Dropping recorded UK fields at
# the Step 2 boundary pre-empts a decision D-S2-7 reserves for Step 3 (what is *written into the
# token stream*, not what is *kept*). These ride along unchanged, exactly like the raw fields.
COUNTRY_EXTRA_RAW_COLUMNS = {
    "es": [],
    "uk": ["act2_extra_uk_2", "act2_extra_uk_3", "weight_dia_a", "weight_dia_b"],
    "it": [],
}


def log(msg):
    print(msg, flush=True)


def fail(msg):
    raise SystemExit(f"FATAL: {msg}")


def truth_from_meaning(meaning: str, raw_value: str = None) -> bool:
    m = str(meaning).strip().lower()
    if m.startswith("yes"):
        return True
    if m.startswith("no"):
        return False
    if m == "reported":
        return True
    if m == "not reported":
        return False
    # Fallback for a field whose value label is domain-specific prose rather than a
    # yes/no statement -- the UK's WithNA ("Not reported" / "main act: work/edu/sleep").
    # Never mapped to a shared flag and never read as missing (D-S2-8, F-UK-4); it is
    # carried purely as its own raw binary 0/1 indicator, so 0/1 decide truth directly
    # when the text itself does not.
    if raw_value == "0":
        return False
    if raw_value == "1":
        return True
    fail(f"unrecognised national_value_meaning {meaning!r} (raw_value={raw_value!r}) in "
         f"crosswalk_copresence.csv -- printed and refused per G2.14, never coerced")


def compile_age_expression(country: str, floor: int):
    """Return (expr_str, italy_band_line_or_None, predicate) for the age filter.

    predicate(df) -> boolean Series, True = keeps the row's person.
    """
    if country == "es":
        expr = f"EDAD >= {floor}"
        return expr, None, (lambda df: df["EDAD"].astype(int) >= floor)
    if country == "uk":
        expr = f"DVAge >= {floor}"
        return expr, None, (lambda df: df["DVAge"].astype(int) >= floor)
    if country == "it":
        # D-S2-13: find the band containing the floor; the floor must be exactly
        # that band's lower bound, or the runner refuses to guess.
        containing = None
        for code, lo, hi in ITALY_AGE_BANDS:
            if lo <= floor <= hi:
                containing = (code, lo, hi)
                break
        if containing is None:
            fail(f"age floor {floor} does not fall inside any Italian claseta2 band "
                 f"(0-{ITALY_AGE_BANDS[-1][2]})")
        code, lo, hi = containing
        if lo != floor:
            fail(f"age floor {floor} falls STRICTLY INSIDE Italy's claseta2 band {code} "
                 f"({lo}-{hi}); it cannot be expressed exactly on Italy's banded age variable. "
                 f"Choose a floor that begins a band (D-S2-13). Refusing to silently round.")
        expr = f'claseta2 >= "{code}"'
        band_line = (f"Italy's age clause was evaluated on a BAND, not an exact age: "
                     f"claseta2 >= \"{code}\" (band {code} = {lo}-{hi}; the floor {floor} is exactly "
                     f"this band's lower bound). No exact age variable exists in Italy's delivery (F-IT-2).")
        return expr, band_line, (lambda df: df["claseta2"].astype(str) >= code)
    fail(f"unknown country {country!r}")


def load_crosswalks(xw_dir, country_tag):
    act = pd.read_csv(f"{xw_dir}/crosswalk_activity.csv", dtype=str, keep_default_na=False)
    act2 = pd.read_csv(f"{xw_dir}/crosswalk_activity_secondary.csv", dtype=str, keep_default_na=False)
    loc = pd.read_csv(f"{xw_dir}/crosswalk_location.csv", dtype=str, keep_default_na=False)
    cop = pd.read_csv(f"{xw_dir}/crosswalk_copresence.csv", dtype=str, keep_default_na=False)
    outdoor = pd.read_csv(f"{xw_dir}/outdoor_at_home.csv", dtype=str, keep_default_na=False)
    target = pd.read_csv(f"{xw_dir}/activity_target_list.csv", dtype=str, keep_default_na=False)

    act_c = act[act["country"] == country_tag][["source_code", "target_code"]].drop_duplicates()
    if act_c["source_code"].duplicated().any():
        fail(f"crosswalk_activity.csv has duplicate source_code rows for country={country_tag}")
    act2_c = act2[act2["country"] == country_tag][["source_code", "target_code_2d"]].drop_duplicates()
    if act2_c["source_code"].duplicated().any():
        fail(f"crosswalk_activity_secondary.csv has duplicate source_code rows for country={country_tag}")
    loc_c = loc[loc["country"] == country_tag][["source_code", "target_class"]].drop_duplicates()
    if loc_c["source_code"].duplicated().any():
        fail(f"crosswalk_location.csv has duplicate source_code rows for country={country_tag}")
    cop_c = cop[cop["country"] == country_tag].copy()

    return {
        "act": act_c, "act2": act2_c, "loc": loc_c, "cop": cop_c,
        "outdoor_codes": set(outdoor["target_code"].tolist()),
        "target_codes": set(target["target_code"].tolist()),
    }


def build_copresence_plan(cop_c: pd.DataFrame, country: str):
    """Return (targets, missing_trigger) from crosswalk_copresence.csv rows for one country.

    targets: dict target_col -> list of (raw_col, value_bool_map) contributing to it.
             target_col is either a shared cop_* name or an EXTRA:-stripped cop_extra_* name.
    missing_trigger: None, or (raw_col, trigger_raw_value) -- when raw_col == trigger_raw_value,
                      the six shared flags are overridden to null (D-S2-8, UK's WithMiss).
    """
    targets = {}
    missing_trigger = None
    raw_col_map = RAW_COP_COLUMN[country]

    for national_field, rows in cop_c.groupby("national_field"):
        if national_field not in raw_col_map:
            fail(f"crosswalk_copresence.csv names national_field={national_field!r} for country={country} "
                 f"but no raw column mapping is known for it -- discovered-vs-declared discrepancy, "
                 f"reported rather than guessed")
        raw_col = raw_col_map[national_field]

        # Build the raw-value -> bool map once, from the row(s)' national_value/meaning.
        value_bool_map = {}
        for _, row in rows.iterrows():
            raw_value = row["national_value"]
            matcher = "" if raw_value == "(blank)" else raw_value
            if row["shared_flag"] == "NOT_A_PRESENCE_FLAG":
                if "no co-presence" in row["national_value_meaning"].strip().lower():
                    missing_trigger = (raw_col, matcher)
                continue
            truth = truth_from_meaning(row["national_value_meaning"], matcher)
            if matcher in value_bool_map and value_bool_map[matcher] != truth:
                fail(f"crosswalk_copresence.csv gives inconsistent truth values for "
                     f"country={country} field={national_field} value={raw_value!r}")
            value_bool_map[matcher] = truth

        for _, row in rows.iterrows():
            sf = row["shared_flag"]
            if sf == "NOT_A_PRESENCE_FLAG":
                continue
            target_col = sf[len("EXTRA:"):] if sf.startswith("EXTRA:") else sf
            targets.setdefault(target_col, [])
            if not any(rc == raw_col for rc, _ in targets[target_col]):
                targets[target_col].append((raw_col, value_bool_map))

    return targets, missing_trigger


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_dir", required=True)
    ap.add_argument("--crosswalks", dest="xw_dir", required=True)
    ap.add_argument("--out", dest="out_dir", required=True)
    ap.add_argument("--country", required=True, choices=["es", "it", "uk"])
    ap.add_argument("--age-floor", dest="age_floor", type=int, required=True,
                     help="No default (D-S2-13): a floor nobody can see being changed is a bug.")
    args = ap.parse_args()

    country = args.country
    floor = args.age_floor
    log(f"=== Step 2 harmonisation, country={country}, age_floor={floor} ===")

    # ---- load ----
    in_path = f"{args.in_dir}/{COUNTRY_FILE[country]}"
    df = pd.read_parquet(in_path)
    n_input_episodes = len(df)
    n_input_respondents = df[["hid", "pid"]].drop_duplicates().shape[0]
    n_input_diaries = df[["hid", "pid", "diary_day"]].drop_duplicates().shape[0]
    log(f"input: {in_path}, {n_input_episodes} episodes, {n_input_respondents} respondents, "
        f"{n_input_diaries} diaries")

    xw = load_crosswalks(args.xw_dir, COUNTRY_CROSSWALK_TAG[country])

    report = {"country": country, "age_floor": floor}

    # ---- assert native origin (D-S2-5) ----
    codebook_path = f"{args.in_dir}/{COUNTRY_CODEBOOK[country]}"
    try:
        with open(codebook_path, encoding="utf-8") as fh:
            codebook_text = fh.read()
    except FileNotFoundError:
        fail(f"codebook_facts file not found: {codebook_path}")
    expected_origin = NATIVE_ORIGIN_HOUR[country]
    import re
    origin_line = None
    for line in codebook_text.splitlines():
        if "Diary origin hour" in line:
            origin_line = line
            break
    if origin_line is None:
        fail(f"{COUNTRY_CODEBOOK[country]} has no 'Diary origin hour' line -- native origin must be "
             f"re-measured, not assumed")
    m = re.search(r"(\d{2}):00", origin_line)
    if not m:
        fail(f"could not parse an HH:00 origin value out of the 'Diary origin hour' line in "
             f"{COUNTRY_CODEBOOK[country]}: {origin_line!r}")
    measured_origin = int(m.group(1))
    if measured_origin != expected_origin:
        fail(f"{COUNTRY_CODEBOOK[country]} states native origin {measured_origin:02d}:00, expected "
             f"{expected_origin:02d}:00 -- stopping rather than assuming")
    log(f"native origin asserted: {country} = {expected_origin:02d}:00 (matches codebook_facts)")
    report["native_origin_hour"] = expected_origin

    # ---- TASK 1, step 1: age filter (D-S2-13) ----
    expr, band_line, keep_predicate = compile_age_expression(country, floor)
    log(f"compiled age expression: {expr}")
    report["age_expr"] = expr
    report["italy_band_line"] = band_line

    keep_person_mask = keep_predicate(df)
    df["_age_keep"] = keep_person_mask
    removed_persons = df.loc[~df["_age_keep"], ["hid", "pid"]].drop_duplicates().shape[0]
    removed_diaries = df.loc[~df["_age_keep"], ["hid", "pid", "diary_day"]].drop_duplicates().shape[0]
    removed_episodes = int((~df["_age_keep"]).sum())
    df = df[df["_age_keep"]].drop(columns=["_age_keep"]).reset_index(drop=True)
    report["age_removed"] = {
        "respondents": removed_persons, "diaries": removed_diaries, "episodes": removed_episodes,
    }
    log(f"age filter removed: {removed_persons} respondents, {removed_diaries} diaries, "
        f"{removed_episodes} episodes")

    if len(df) == 0:
        fail(f"age filter removed every episode for country={country} -- refusing to emit an empty table")

    # ---- TASK 1, step 2: rotate to 04:00 origin, cyclic (D-S2-5, corrected by D-S2-14) ----
    # D-S2-14: start_min's own contract never said what minute zero denotes on the wall clock.
    # reference_minutes makes that an explicit, checkable property instead of an assumed one.
    reference_minutes = REFERENCE_MINUTES[country]
    offset = (reference_minutes - 240) % 1440
    log(f"reference_minutes for {country}: {reference_minutes} (wall-clock time that start_min==0 "
        f"denotes); rotation offset: {offset} min")
    report["reference_minutes"] = reference_minutes

    # D-S2-14 assertion (1): every diary's first episode (Step 1's own episode_index == 0) starts
    # at the declared reference-consistent value -- derived as (native_origin_hour*60 -
    # reference_minutes) mod 1440, i.e. the diary's own wall-clock start expressed in this
    # country's own start_min encoding. Stop rather than assume if this ever breaks.
    expected_first_start = (expected_origin * 60 - reference_minutes) % 1440
    first_eps = df[df["episode_index"] == 0]
    bad_first = first_eps[first_eps["start_min"] != expected_first_start]
    if len(bad_first) > 0:
        fail(f"{len(bad_first)} diar(y/ies) for country={country} have their episode_index==0 "
             f"episode NOT at the declared first-episode start_min {expected_first_start} "
             f"(reference_minutes={reference_minutes}). Example keys:\n"
             f"{bad_first[['hid','pid','diary_day','start_min']].head(3).to_string()}")
    log(f"first-episode start_min assertion passed for {country}: all {len(first_eps)} diaries "
        f"start at {expected_first_start}")

    df = df.rename(columns={"episode_index": "episode_index_step1"})
    df["_new_start"] = (df["start_min"] + offset) % 1440
    df["_end"] = df["_new_start"] + df["duration_min"]
    split_mask = df["_end"] > 1440

    part1 = df.copy()
    part1["start_min"] = part1["_new_start"]
    part1["duration_min"] = np.where(split_mask, 1440 - part1["_new_start"], part1["duration_min"])
    part1["split_at_origin"] = split_mask

    part2 = df.loc[split_mask].copy()
    part2["start_min"] = 0
    part2["duration_min"] = part2["_end"] - 1440
    part2["split_at_origin"] = True

    combined = pd.concat([part1, part2], ignore_index=True)
    combined = combined.drop(columns=["_new_start", "_end"])

    n_splits = int(split_mask.sum())
    report["splits"] = n_splits
    log(f"splits at origin for {country}: {n_splits}")
    if country == "es":
        if n_splits == 0:
            fail("Spain produced zero splits at the 04:00 rotation -- expected non-zero (D-S2-5)")
    else:
        if n_splits != 0:
            fail(f"{country} produced {n_splits} split(s) at the 04:00 rotation -- only Spain should "
                 f"split (offset=0 for uk/it); this is a defect, stopping rather than absorbing it")

    combined = combined.sort_values(["country", "hid", "pid", "diary_day", "start_min"]).reset_index(drop=True)
    combined["episode_index"] = combined.groupby(["country", "hid", "pid", "diary_day"]).cumcount()

    df = combined

    # ---- TASK 1, step 3: assert the 10-minute grid, never coerce ----
    bad_start = df["start_min"] % 10 != 0
    bad_dur = df["duration_min"] % 10 != 0
    if bad_start.any() or bad_dur.any():
        examples = df.loc[bad_start | bad_dur, ["country", "hid", "pid", "diary_day"]].head(3)
        fail(f"grid violation after rotation: {int(bad_start.sum())} bad start_min, "
             f"{int(bad_dur.sum())} bad duration_min. Example keys:\n{examples.to_string()}")

    day_sums = df.groupby(["country", "hid", "pid", "diary_day"])["duration_min"].sum()
    bad_days = day_sums[day_sums != 1440]
    if len(bad_days) > 0:
        fail(f"{len(bad_days)} diaries do not sum to 1440 after rotation. Example keys:\n"
             f"{bad_days.head(3).to_string()}")
    log(f"grid assertions passed: {len(df)} episodes, {len(day_sums)} diaries, all sum to 1440, "
        f"no coercion applied")

    # D-S2-14 assertion (2): the rotated intervals tile [0, 1440) exactly once per diary -- the
    # general form of the by-hand check that caught Italy's reference-minutes defect. df is
    # already sorted by start_min within each diary (done just above). A diary tiles correctly
    # iff each interval's start equals the running sum of durations before it (first interval at
    # 0, no gaps, no overlaps); combined with day_sums == 1440 above, this rules out both a
    # short/overlapping cover and a long one.
    diary_key = ["country", "hid", "pid", "diary_day"]
    running_end = df.groupby(diary_key)["duration_min"].cumsum()
    expected_start = running_end - df["duration_min"]
    tiling_bad = df["start_min"] != expected_start
    if tiling_bad.any():
        examples = df.loc[tiling_bad, diary_key + ["start_min", "duration_min"]].head(3)
        fail(f"{int(tiling_bad.sum())} interval(s) do not tile [0, 1440) exactly once per diary "
             f"(gap or overlap detected) for country={country}. Example rows:\n{examples.to_string()}")
    log(f"tiling assertion passed for {country}: every diary's rotated intervals partition "
        f"[0, 1440) exactly once, no gaps, no overlaps")

    # ---- TASK 1, step 4: activity -> act, act_level1, act_level2 ----
    df = df.merge(xw["act"].rename(columns={"source_code": "act_raw", "target_code": "act"}),
                   on="act_raw", how="left")
    n_act_null = int(df["act"].isna().sum())
    report["act_unmapped"] = n_act_null
    df["act_level1"] = df["act"].where(df["act"].isna(), df["act"].str[0])
    df["act_level2"] = df["act"].where(df["act"].isna(), df["act"].str[:2])

    non_null_act = set(df["act"].dropna().unique())
    missing_from_target = non_null_act - xw["target_codes"]
    if missing_from_target:
        fail(f"{len(missing_from_target)} emitted act code(s) are not in activity_target_list.csv: "
             f"{sorted(missing_from_target)[:10]}")
    bad_l1 = df.loc[df["act"].notna() & (df["act_level1"] != df["act"].str[0])]
    bad_l2 = df.loc[df["act"].notna() & (df["act_level2"] != df["act"].str[:2])]
    if len(bad_l1) or len(bad_l2):
        fail(f"act_level1/act_level2 not sliced from the emitted act code on {len(bad_l1)}/{len(bad_l2)} rows")
    log(f"activity mapped: {n_act_null} unmapped (act=null) of {len(df)} episodes")

    # ---- TASK 1, step 5: secondary activity -> act2, act2_level1 ----
    # act2_raw's three states: null=not recorded, ""=recorded and blank, else=recorded with a value.
    # blank is never looked up in the crosswalk; only non-blank, non-null codes are joined.
    is_null_a2 = df["act2_raw"].isna()
    is_blank_a2 = (~is_null_a2) & (df["act2_raw"] == "")
    is_value_a2 = (~is_null_a2) & (~is_blank_a2)

    report["act2_states"] = {
        "not_recorded_null": int(is_null_a2.sum()),
        "recorded_blank": int(is_blank_a2.sum()),
        "recorded_with_value": int(is_value_a2.sum()),
    }
    log(f"act2_raw three states for {country}: not_recorded(null)={int(is_null_a2.sum())}, "
        f"recorded_and_blank('')={int(is_blank_a2.sum())}, recorded_with_value={int(is_value_a2.sum())}")

    act2_map = xw["act2"].rename(columns={"source_code": "act2_raw", "target_code_2d": "_act2_mapped"})
    df = df.merge(act2_map, on="act2_raw", how="left")
    df["act2"] = np.where(is_null_a2, None, np.where(is_blank_a2, "", df["_act2_mapped"]))
    df = df.drop(columns=["_act2_mapped"])
    n_act2_unmapped_values = int(is_value_a2.sum() - df.loc[is_value_a2, "act2"].notna().sum())
    report["act2_unmapped_values"] = n_act2_unmapped_values

    df["act2_level1"] = None
    has_act2 = df["act2"].notna()
    nonblank_act2 = has_act2 & (df["act2"] != "")
    df.loc[has_act2 & ~nonblank_act2, "act2_level1"] = ""
    df.loc[nonblank_act2, "act2_level1"] = df.loc[nonblank_act2, "act2"].str[0]

    # ---- TASK 1, step 6: location -> loc_class ----
    df = df.merge(xw["loc"].rename(columns={"source_code": "loc_raw", "target_class": "loc_class"}),
                   on="loc_raw", how="left")
    is_blank_loc = df["loc_raw"] == ""
    n_loc_blank = int(is_blank_loc.sum())
    n_loc_unmapped = int(df["loc_class"].isna().sum() - n_loc_blank)  # unmapped non-blank codes
    report["loc_unmapped"] = n_loc_unmapped
    report["loc_blank"] = n_loc_blank
    log(f"location mapped: {n_loc_unmapped} unmapped non-blank code(s), {n_loc_blank} recorded-and-blank "
        f"episode(s) of {len(df)}")

    # ---- TASK 1, step 7: indoor_presence ----
    # null wherever loc_raw is recorded-and-blank, or (as this runner's own extension, since the
    # spec only names the blank case explicitly) wherever loc_class is otherwise unmapped/unknown --
    # "we don't know" is never allowed to collapse into False. See progress log fragment.
    outdoor_codes = xw["outdoor_codes"]
    at_home = df["loc_class"] == "at_home"
    not_outdoor = ~df["act"].isin(outdoor_codes)
    loc_unknown = df["loc_class"].isna()
    act_unknown = df["act"].isna()
    indoor = at_home & not_outdoor
    df["indoor_presence"] = indoor.astype("boolean")
    # null wherever we cannot know the answer: loc_class itself unknown (covers both loc_raw's
    # recorded-and-blank state and any genuinely unmapped non-blank location code -- an extension
    # of the spec's explicit blank-state rule, since "unknown" must never collapse into False);
    # or loc_class=='at_home' but act is unmapped, so the outdoor-at-home exclusion cannot be
    # evaluated even though we do know the person is at home.
    df.loc[loc_unknown, "indoor_presence"] = pd.NA
    df.loc[at_home & act_unknown, "indoor_presence"] = pd.NA

    # ---- TASK 1, step 8: co-presence ----
    targets, missing_trigger = build_copresence_plan(xw["cop"], country)
    SHARED = ["cop_alone", "cop_partner", "cop_children", "cop_parent", "cop_other_hh", "cop_other_persons"]
    for col in SHARED:
        if col not in targets:
            fail(f"crosswalk_copresence.csv does not map any national field to shared flag {col} "
                 f"for country={country}")

    for target_col, sources in targets.items():
        acc = None
        for raw_col, value_map in sources:
            if raw_col not in df.columns:
                fail(f"expected raw co-presence column {raw_col!r} not found in input for country={country}")
            mapped = df[raw_col].astype(str).map(value_map)
            unrecognised = df[raw_col].astype(str)[mapped.isna() & df[raw_col].notna()]
            if len(unrecognised) > 0:
                fail(f"{len(unrecognised)} unrecognised raw value(s) for {raw_col} in country={country}: "
                     f"{sorted(unrecognised.unique())[:10]} -- printed and refused, never coerced (G2.14)")
            mapped_bool = mapped.astype("boolean")
            acc = mapped_bool if acc is None else (acc | mapped_bool)
        df[target_col] = acc

    if missing_trigger is not None:
        raw_col, trigger_val = missing_trigger
        miss_mask = df[raw_col].astype(str) == trigger_val
        n_miss = int(miss_mask.sum())
        report["cop_missing_flag_rows"] = n_miss
        log(f"{country}: {n_miss} episode(s) have {raw_col}=={trigger_val!r} "
            f"(D-S2-8 missingness) -- the six shared cop_* flags are set to null on these rows")
        df.loc[miss_mask, SHARED] = pd.NA
    else:
        report["cop_missing_flag_rows"] = 0

    cop_extra_cols = sorted(c for c in targets if c not in SHARED)
    extra_raw_cols = COUNTRY_EXTRA_RAW_COLUMNS.get(country, [])
    missing_extra_raw = [c for c in extra_raw_cols if c not in df.columns]
    if missing_extra_raw:
        fail(f"expected extra raw column(s) {missing_extra_raw} not found in input for country={country}")

    # ---- TASK 1, step 9: emit ----
    columns = list(BASE_COLUMNS_HEAD) + cop_extra_cols + list(BASE_COLUMNS_TAIL) + extra_raw_cols
    for c in ["act", "act2", "act2_level1", "loc_class"]:
        df[c] = df[c].astype("string")
    for c in ["act_level1", "act_level2"]:
        df[c] = df[c].astype("string")

    # V2.i (see the val doc) forbids a per-country origin_hour-style column reaching Step 3.
    # Its literal text says "any column name containing origin", but D-S2-12 itself requires
    # split_at_origin as a column, which trips that literal reading -- an apparent contradiction
    # in the governing spec, noted here and in the progress log fragment rather than silently
    # resolved. This self-check targets the actual leak the rule exists to stop (an origin_hour
    # value column) and allows the required split_at_origin flag; V2.i itself is implemented by
    # a separate validator (tools/4thJ_gates_step2.py, a different work item) and gets the final say.
    bad_origin_cols = [c for c in columns if "origin" in c.lower() and c != "split_at_origin"]
    if bad_origin_cols:
        fail(f"column name(s) containing 'origin' about to be written: {bad_origin_cols} -- V2.i forbids this")

    missing_cols = [c for c in columns if c not in df.columns]
    if missing_cols:
        fail(f"about to write harmonised table but these D-S2-12 columns are missing: {missing_cols}")

    out_df = df[columns].copy()
    n_output_episodes = len(out_df)
    report["output_episodes"] = n_output_episodes
    report["input_episodes"] = n_input_episodes

    reconciled = n_input_episodes - removed_episodes + n_splits == n_output_episodes
    report["reconciles"] = reconciled
    log(f"reconciliation: input {n_input_episodes} - age_removed {removed_episodes} + splits {n_splits} "
        f"= {n_input_episodes - removed_episodes + n_splits}, output = {n_output_episodes}, "
        f"{'OK' if reconciled else 'MISMATCH'}")
    if not reconciled:
        fail("episode count does not reconcile: input - filtered + splits != output")

    import os
    os.makedirs(args.out_dir, exist_ok=True)
    out_path = f"{args.out_dir}/harmonised_{country}.parquet"
    out_df.to_parquet(out_path, index=False, engine="pyarrow")

    # attach file-level metadata with the native origin (D-S2-5, D-S2-12: never a row/column)
    import pyarrow.parquet as pq
    import pyarrow as pa
    table = pq.read_table(out_path)
    meta = dict(table.schema.metadata or {})
    meta[b"native_origin_hour"] = str(expected_origin).encode()
    meta[b"country"] = country.encode()
    meta[b"age_floor"] = str(floor).encode()
    table = table.replace_schema_metadata(meta)
    pq.write_table(table, out_path)
    log(f"wrote {out_path} ({n_output_episodes} episodes, native_origin_hour={expected_origin} in file metadata)")

    # ---- per-country filter_report fragment ----
    frag_path = f"{args.out_dir}/filter_report_{country}.md"
    with open(frag_path, "w", encoding="utf-8") as fh:
        fh.write(f"## {country}\n\n")
        fh.write(f"- age floor used: {floor}\n")
        fh.write(f"- compiled age expression: `{expr}`\n")
        if band_line:
            fh.write(f"- {band_line}\n")
        fh.write(f"- age clause removed: {removed_persons} respondents, {removed_diaries} diaries, "
                  f"{removed_episodes} episodes\n")
        fh.write(f"- native origin hour: {expected_origin:02d}:00 (asserted against {COUNTRY_CODEBOOK[country]})\n")
        fh.write(f"- reference_minutes (D-S2-14): {reference_minutes} (wall-clock time that "
                  f"start_min==0 denotes)\n")
        fh.write(f"- rotation offset applied: {offset} min\n")
        fh.write(f"- first-episode start_min assertion: PASS, all diaries start at {expected_first_start}\n")
        fh.write(f"- tiling assertion: PASS, every diary's rotated intervals partition [0,1440) "
                  f"exactly once\n")
        fh.write(f"- split_at_origin count: {n_splits}\n")
        fh.write(f"- act2_raw three states: not_recorded(null)={report['act2_states']['not_recorded_null']}, "
                  f"recorded_and_blank('')={report['act2_states']['recorded_blank']}, "
                  f"recorded_with_value={report['act2_states']['recorded_with_value']}\n")
        fh.write(f"- act2 unmapped-with-value codes (act2=null despite a raw value): {n_act2_unmapped_values}\n")
        n_act2_null_total = int(out_df["act2"].isna().sum())
        fh.write(f"- act2=null overload: D-S2-12 says null means 'not recorded', but in this delivery "
                  f"act2=null ALWAYS means 'the recorded act2_raw code did not map' ({n_act2_null_total} "
                  f"episode(s) here) -- the literal 'not recorded' state never occurs for any country "
                  f"(act2_raw three states above: not_recorded(null)=0 everywhere). Resolve downstream via "
                  f"act2_raw: a non-empty, non-null act2_raw paired with act2 IS NULL is the unmapped case; "
                  f"act2_raw=='' always pairs with act2=='' (recorded-and-blank), never with act2=null.\n")
        fh.write(f"- act unmapped (act=null): {n_act_null}\n")
        fh.write(f"- loc_class unmapped, non-blank raw (loc_class=null): {n_loc_unmapped}\n")
        fh.write(f"- loc_raw recorded-and-blank episodes: {n_loc_blank}\n")
        n_indoor_null = int(out_df["indoor_presence"].isna().sum())
        fh.write(f"- indoor_presence null count: {n_indoor_null} (null, never False, wherever we cannot "
                  f"evaluate the rule: loc_class unknown -- loc_raw recorded-and-blank or an unmapped "
                  f"code -- or loc_class=='at_home' but act is unmapped so the outdoor-at-home exclusion "
                  f"cannot be checked; 'we don't know' is never collapsed into False)\n")
        fh.write(f"- co-presence missingness-flagged episodes (six shared flags set null): "
                  f"{report['cop_missing_flag_rows']}\n")
        fh.write(f"- input episodes: {n_input_episodes}\n")
        fh.write(f"- output episodes: {n_output_episodes}\n")
        fh.write(f"- reconciliation: {n_input_episodes} - {removed_episodes} + {n_splits} = "
                  f"{n_input_episodes - removed_episodes + n_splits} (output {n_output_episodes}), "
                  f"{'OK' if reconciled else 'MISMATCH'}\n")
        if country == "es":
            share_alone = out_df["cop_alone"].mean(skipna=True)
            fh.write(f"- Spain cop_alone share True (of non-null): {share_alone:.4f} "
                     f"(sanity check against D-S2-8's 1=yes/6=no truthy-cast bug)\n")
        for col in ["cop_alone", "cop_partner", "cop_children", "cop_parent", "cop_other_hh",
                    "cop_other_persons"] + cop_extra_cols:
            n_null = int(out_df[col].isna().sum())
            n_true = int((out_df[col] == True).sum())
            n_false = int((out_df[col] == False).sum())
            fh.write(f"  - {col}: null={n_null}, True={n_true}, False={n_false}\n")

    log(f"wrote {frag_path}")
    log(f"=== DONE country={country} ===")


if __name__ == "__main__":
    main()
