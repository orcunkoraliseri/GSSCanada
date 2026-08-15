#!/usr/bin/env python3
"""
4J Step 1, work item 1.3 -- shape-agnostic reader, Spain (INE EET 2009-2010).

Reads the INE fixed-width ASCII delivery and emits the common intermediate
record defined in Step1_docs/4thJ_01_corpusAcquisition.md.

Design rules this file is written under, from the step specification:

  * it itemises everything it could not parse, and it FAILS on it;
  * it never infers a value it did not read;
  * an unrecognised code, unit or column value is printed and refused,
    never silently treated as benign (vacuity guard V1.d).

Every column position below is cited to a sheet and row of
"DISEnOS DE REGISTRO EET 2009 2010.xlsx", which ships inside
disreg_emptiem0910.zip.  No position is guessed and none comes from a
deep-research report.

Usage:
    python 4thJ_read_spain.py --raw <dir with the unpacked .TXT files> \
                              --out <outputs_step1 dir>
"""

import argparse
import hashlib
import json
import os
import sys
from collections import Counter

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Record layouts.  Positions are 1-based inclusive, exactly as INE writes them.
# (name, first, last, kind)   kind: "s" keep as string, "i" integer, "w" weight
# --------------------------------------------------------------------------

# Sheet "F DIARIO2", rows 7-63.  Record width 44.
DIARIO2 = [
    ("IDHOGAR",   1,  5, "s"),
    ("NPERS",     6,  7, "s"),
    ("TRIM",      8,  8, "s"),
    ("DDIASEM",   9,  9, "s"),
    ("INTERVALO", 10, 12, "i"),
    ("APRIN",     13, 15, "s"),
    ("AP_INT",    16, 16, "s"),
    ("ASECU",     17, 19, "s"),
    ("AS_INT",    20, 20, "s"),
    ("LUGAR",     21, 22, "s"),
    ("SOLO",      23, 23, "s"),
    ("PAREJA",    24, 24, "s"),
    ("PADRES",    25, 25, "s"),
    ("MENOR",     26, 26, "s"),
    ("OTMH",      27, 27, "s"),
    ("OTCON",     28, 28, "s"),
    ("FACTORF",   29, 44, "w"),
]

# Sheet "F DIARIO1", rows 7-30.  Record width 38.
DIARIO1 = [
    ("IDHOGAR",    1,  5, "s"),
    ("NPERS",      6,  7, "s"),
    ("POSPO",      8,  8, "s"),
    ("D_CUMPLI",   9,  9, "s"),
    ("D_CUMPLI_D", 10, 11, "s"),
    ("D_TIPODIA",  12, 12, "s"),
    ("D_AGOB",     13, 13, "s"),
    ("D_ENFER",    14, 14, "s"),
    ("D_LIBRE",    15, 15, "s"),
    ("D_OTMOT",    16, 16, "s"),
    ("D_VIAJE",    17, 17, "s"),
    ("D_VIAJE_KM", 18, 21, "s"),
    ("D_HTR",      22, 22, "s"),
    ("FACTORF",    23, 38, "w"),
]

# Sheet "F MHOGAR", rows 7-45.  Record width 48.
MHOGAR = [
    ("IDHOGAR",   1,  5, "s"),
    ("NPERS",     6,  7, "s"),
    ("SEXO",      8,  8, "s"),
    ("NACIMES",   9, 10, "s"),
    ("NACIANNO", 11, 14, "s"),
    ("EDAD",     15, 17, "i"),
    ("HRELACTIV", 18, 18, "s"),
    ("MATRIZ",   19, 32, "s"),
    ("FACTORF",  33, 48, "w"),
]

# Sheet "F CINDIV", rows 7 onward.  Record width 61.
CINDIV = [
    ("IDHOGAR",  1,  5, "s"),
    ("NPERS",    6,  7, "s"),
    ("FACTORF", 46, 61, "w"),
]

# Sheet "F DHOGAR", rows 7-70.  Record width 37.
DHOGAR = [
    ("IDHOGAR",      1,  5, "s"),
    ("CAUT",         6,  7, "s"),
    ("TAMUN",        8,  8, "s"),
    ("TIPOHOG",      9,  9, "s"),
    ("NMH",         10, 11, "i"),
    ("NMH10",       12, 13, "i"),
    ("FACTOR_hogar", 22, 37, "w"),
]

WIDTHS = {"DIARIO2": 44, "DIARIO1": 38, "MHOGAR": 48, "CINDIV": 61, "DHOGAR": 37}

# Counts INE states for its own delivery, sheet "Disenos de registro" rows 12-20.
# These are the reference for gate G1.1 and they come from the provider's
# documentation, not from any value we computed.
INE_STATED = {
    "DHOGAR": 9541,
    "MHOGAR": 25895,
    "CINDIV": 19295,
    "DIARIO1": 19295,
    "DIARIO2": 2778480,
}

# Valid-value sets that the layout workbook states explicitly.  Anything
# outside these is refused, not coerced.
YESNO = {"1", "6"}
COPRESENCE = ["SOLO", "PAREJA", "PADRES", "MENOR", "OTMH", "OTCON"]

# Constant prefix fields for this country, carried from Step 1 so that no
# later step has to guess them (Step 3B).
MODE = "paper_self_completion"
SCHEME = "EET_2009_2010"

SLOT_MINUTES = 10          # sheet "F DIARIO2" row 27
SLOTS_PER_DIARY = 144      # sheet "F DIARIO2" row 65
ORIGIN_HOUR = 6            # sheet "F DIARIO2" rows 28-31: interval 1 is 06:00-06:10


class ParseFailure(Exception):
    pass


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_fixed(path, layout, name, report):
    """Read one INE fixed-width file.  Refuse anything that does not fit."""
    width = WIDTHS[name]
    size = os.path.getsize(path)

    with open(path, "rb") as fh:
        head = fh.read(4096)
    if b"\r\n" in head:
        term, tlen = "crlf", 2
    elif b"\n" in head:
        term, tlen = "lf", 1
    else:
        raise ParseFailure(f"{name}: no line terminator found in the first 4096 bytes")

    stride = width + tlen
    if size % stride != 0:
        raise ParseFailure(
            f"{name}: file size {size} is not a whole multiple of the record "
            f"stride {stride} (declared width {width} + {term}). "
            f"The layout and the file disagree; nothing was parsed."
        )
    n_expected = size // stride
    report.append(
        f"{name}: {size} bytes, terminator {term}, declared width {width}, "
        f"stride {stride}, so {n_expected} records"
    )

    colspecs = [(a - 1, b) for (_, a, b, _) in layout]
    names = [c[0] for c in layout]
    df = pd.read_fwf(
        path, colspecs=colspecs, names=names, dtype=str,
        header=None, encoding="latin-1", keep_default_na=False,
    )
    if len(df) != n_expected:
        raise ParseFailure(
            f"{name}: pandas returned {len(df)} rows against {n_expected} "
            f"implied by the file size. Refusing to continue."
        )

    for (col, a, b, kind) in layout:
        if kind == "i":
            raw = df[col].str.strip()
            bad = raw[~raw.str.fullmatch(r"\d+")]
            if len(bad):
                raise ParseFailure(
                    f"{name}.{col}: {len(bad)} values are not integers, "
                    f"examples {list(bad.unique()[:5])}"
                )
            df[col] = raw.astype("int64")
        elif kind == "w":
            raw = df[col].str.strip()
            bad = raw[~raw.str.fullmatch(r"\d{16}")]
            if len(bad):
                raise ParseFailure(
                    f"{name}.{col}: {len(bad)} weight values are not 16 digits, "
                    f"examples {list(bad.unique()[:5])}"
                )
            # 6 integer digits and 10 decimals, sheet "F DIARIO2" row 63.
            df[col] = raw.astype("float64") / 1e10
        else:
            df[col] = df[col].str.strip()

    return df, n_expected, term


def refuse_unknown(df, col, allowed, name, allow_blank=False):
    seen = set(df[col].unique())
    ok = set(allowed) | ({""} if allow_blank else set())
    unknown = sorted(seen - ok)
    if unknown:
        raise ParseFailure(
            f"{name}.{col}: unrecognised values {unknown[:20]} "
            f"(allowed {sorted(ok)}). Refused rather than assumed harmless."
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    report = []
    facts = {}

    # ---- V1.b: print what was read, with hashes, BEFORE any verdict ---------
    files = {
        "DIARIO2": "DIARIO2.TXT",
        "DIARIO1": "DIARIO1.TXT",
        "MHOGAR": "MHOGAR.TXT",
        "CINDIV": "CINDIV.TXT",
        "DHOGAR": "DHOGAR.TXT",
    }
    report.append("=" * 74)
    report.append("INPUTS READ (hashes computed from disk at parse time)")
    report.append("=" * 74)
    for key, fn in files.items():
        p = os.path.join(args.raw, fn)
        if not os.path.exists(p):
            raise ParseFailure(f"missing input file {p}")
        report.append(f"  {fn:14s} {os.path.getsize(p):>12d} bytes  md5 {md5_of(p)}")
    report.append("")

    frames = {}
    for key, fn in files.items():
        layout = {"DIARIO2": DIARIO2, "DIARIO1": DIARIO1, "MHOGAR": MHOGAR,
                  "CINDIV": CINDIV, "DHOGAR": DHOGAR}[key]
        df, n, term = read_fixed(os.path.join(args.raw, fn), layout, key, report)
        frames[key] = df
        stated = INE_STATED[key]
        mark = "MATCH" if n == stated else "MISMATCH"
        report.append(f"  {key}: {n} records against INE's stated {stated} -> {mark}")
        if n != stated:
            raise ParseFailure(
                f"{key}: record count {n} does not equal the {stated} INE states "
                f"in its own record-layout workbook. This is a truncated or "
                f"partial delivery; nothing downstream may be trusted."
            )
    report.append("")

    d2 = frames["DIARIO2"]

    # ---- refuse unrecognised values (V1.d) ---------------------------------
    report.append("=" * 74)
    report.append("VALUE-DOMAIN REFUSAL (V1.d)")
    report.append("=" * 74)
    refuse_unknown(d2, "TRIM", {"1", "2", "3", "4"}, "DIARIO2")
    refuse_unknown(d2, "DDIASEM", {str(i) for i in range(1, 8)}, "DIARIO2")
    refuse_unknown(d2, "AP_INT", YESNO, "DIARIO2", allow_blank=True)
    refuse_unknown(d2, "AS_INT", YESNO, "DIARIO2", allow_blank=True)
    for c in COPRESENCE:
        refuse_unknown(d2, c, YESNO, "DIARIO2", allow_blank=True)
    report.append("  TRIM, DDIASEM, AP_INT, AS_INT and the six co-presence flags")
    report.append("  are all inside the domains the layout workbook declares.")

    bad_int = d2.loc[(d2["INTERVALO"] < 1) | (d2["INTERVALO"] > SLOTS_PER_DIARY)]
    if len(bad_int):
        raise ParseFailure(f"DIARIO2.INTERVALO: {len(bad_int)} values outside 1..144")
    report.append("  INTERVALO is inside 1..144 on every row.")

    # APRIN and LUGAR are declared only as "Lista EET" in the workbook, so the
    # reader cannot refuse against a list it does not hold.  It reports the
    # observed alphabet instead, and Step 1 gate G1.4 stays NOT CHECKED until
    # the list itself is in hand.
    act_seen = sorted(d2["APRIN"].unique())
    sec_seen = sorted(d2["ASECU"].unique())
    loc_seen = sorted(d2["LUGAR"].unique())
    report.append("")
    report.append(f"  APRIN observed alphabet: {len(act_seen)} distinct codes")
    report.append(f"  ASECU observed alphabet: {len(sec_seen)} distinct codes "
                  f"(blank counted: {(d2['ASECU'] == '').sum()} rows)")
    report.append(f"  LUGAR observed alphabet: {len(loc_seen)} distinct codes -> {loc_seen}")
    facts["act_codes_observed"] = act_seen
    facts["loc_codes_observed"] = loc_seen

    # ---- diary structure ---------------------------------------------------
    report.append("")
    report.append("=" * 74)
    report.append("DIARY STRUCTURE")
    report.append("=" * 74)
    d2["hid"] = d2["IDHOGAR"]
    d2["pid"] = d2["IDHOGAR"] + "_" + d2["NPERS"]

    per_diary = d2.groupby("pid", sort=False).size()
    if not (per_diary == SLOTS_PER_DIARY).all():
        offenders = per_diary[per_diary != SLOTS_PER_DIARY]
        raise ParseFailure(
            f"{len(offenders)} diaries do not have exactly {SLOTS_PER_DIARY} slots, "
            f"examples {offenders.head().to_dict()}"
        )
    n_diaries = len(per_diary)
    report.append(f"  {n_diaries} diaries, every one with exactly {SLOTS_PER_DIARY} slots")

    # diary days per respondent: how many distinct diary days each person filed
    days_per_person = d2.groupby("pid", sort=False)["DDIASEM"].nunique()
    dpp = int(days_per_person.max())
    report.append(f"  diary days per respondent: max {dpp}, "
                  f"distribution {dict(Counter(days_per_person))}")
    facts["diary_days_per_respondent"] = dpp

    # constant fields
    report.append(f"  mode   = {MODE}   (one value, by construction of this wave)")
    report.append(f"  scheme = {SCHEME}")

    # ---- build episodes ----------------------------------------------------
    report.append("")
    report.append("=" * 74)
    report.append("EPISODE RECONSTRUCTION")
    report.append("=" * 74)
    report.append("  INE ships 144 fixed 10-minute slots per diary, not native")
    report.append("  START/DURATION.  Episodes are built by collapsing runs of")
    report.append("  consecutive slots that agree on primary activity, location and")
    report.append("  all six co-presence flags.  No other field is used to break a run.")

    d2 = d2.sort_values(["pid", "INTERVALO"], kind="mergesort").reset_index(drop=True)

    key_cols = ["APRIN", "LUGAR"] + COPRESENCE
    key = d2[key_cols].agg("|".join, axis=1)
    new_person = d2["pid"].ne(d2["pid"].shift())
    changed = key.ne(key.shift()) | new_person
    d2["episode_id"] = changed.cumsum()

    grp = d2.groupby("episode_id", sort=True)
    ep = grp.agg(
        hid=("hid", "first"),
        pid=("pid", "first"),
        diary_day=("DDIASEM", "first"),
        trim=("TRIM", "first"),
        first_slot=("INTERVALO", "first"),
        n_slots=("INTERVALO", "size"),
        act_raw=("APRIN", "first"),
        act2_raw=("ASECU", "first"),
        loc_raw=("LUGAR", "first"),
        cop_solo=("SOLO", "first"),
        cop_pareja=("PAREJA", "first"),
        cop_extra_es_padres=("PADRES", "first"),
        cop_menor=("MENOR", "first"),
        cop_otmh=("OTMH", "first"),
        cop_otcon=("OTCON", "first"),
        weight_dia=("FACTORF", "first"),
    ).reset_index(drop=True)

    # act2_raw (secondary activity, F-ES-6): aggregated the same way act_raw
    # is aggregated -- "first" of the run -- but kept in a nullable pandas
    # "string" dtype so that pd.NA (not recorded) and "" (recorded, blank)
    # cannot collapse into each other going into parquet. Spain fields ASECU
    # on every row, so no Spanish episode is ever pd.NA; the dtype supports
    # it now so the column does not need widening for the other three
    # countries later.
    ep["act2_raw"] = ep["act2_raw"].astype("string")

    # a run must be contiguous in INTERVALO; assert it rather than assume it
    ep["last_slot"] = ep["first_slot"] + ep["n_slots"] - 1
    check = d2.groupby("episode_id", sort=True)["INTERVALO"].max().values
    if not np.array_equal(check, ep["last_slot"].values):
        raise ParseFailure("episode runs are not contiguous in INTERVALO")

    ep["episode_index"] = ep.groupby("pid", sort=False).cumcount()
    ep["start_min"] = (ep["first_slot"] - 1) * SLOT_MINUTES
    ep["duration_min"] = ep["n_slots"] * SLOT_MINUTES
    ep["country"] = "ES"
    ep["wave"] = "2009-2010"
    ep["mode"] = MODE
    ep["scheme"] = SCHEME

    report.append(f"  {len(ep)} episodes from {len(d2)} slots "
                  f"({len(ep) / n_diaries:.2f} episodes per diary)")

    # act2_raw (secondary activity, F-ES-6): carried now, three states kept
    # separable. Spain fields ASECU on every DIARIO2 row, so no episode can
    # be "not recorded" (pd.NA) for this country; the other two states are
    # measured at episode level, the same level act2_raw itself lives at.
    n_not_recorded = int(ep["act2_raw"].isna().sum())
    n_blank = int((ep["act2_raw"] == "").sum())
    n_valued = int(len(ep) - n_not_recorded - n_blank)
    sec_nonblank_slots = int((d2["ASECU"] != "").sum())
    report.append(f"  CARRIED: act2_raw (secondary activity, from ASECU). Episode-level "
                  f"states -- not recorded: {n_not_recorded}, recorded and blank: "
                  f"{n_blank}, recorded with a value: {n_valued} (of {len(ep)} episodes).")
    report.append(f"  For reference only, at slot level (not the emitted grain): ASECU is "
                  f"non-blank on {sec_nonblank_slots} of {len(d2)} DIARIO2 slots "
                  f"({100.0 * sec_nonblank_slots / len(d2):.1f} %). Episode-level "
                  f"act2_raw is a first-of-run summary of the slot-level field, the same "
                  f"way act_raw itself summarises its run; the two counts are not the "
                  f"same quantity and are not expected to agree.")

    # ---- join person-level facts ------------------------------------------
    mh = frames["MHOGAR"].copy()
    mh["pid"] = mh["IDHOGAR"] + "_" + mh["NPERS"]
    mh = mh[["pid", "SEXO", "EDAD", "HRELACTIV"]]
    ci = frames["CINDIV"].copy()
    ci["pid"] = ci["IDHOGAR"] + "_" + ci["NPERS"]
    ci = ci[["pid", "FACTORF"]].rename(columns={"FACTORF": "weight_ind"})

    before = len(ep)
    ep = ep.merge(mh, on="pid", how="left").merge(ci, on="pid", how="left")
    if len(ep) != before:
        raise ParseFailure("a join changed the episode count")
    miss_dem = int(ep["EDAD"].isna().sum())
    miss_w = int(ep["weight_ind"].isna().sum())
    if miss_dem or miss_w:
        raise ParseFailure(
            f"{miss_dem} episodes have no MHOGAR demographic row and "
            f"{miss_w} have no CINDIV weight row. Refusing to emit a table with "
            f"unexplained gaps."
        )
    report.append(f"  demographics and individual weights joined on pid, "
                  f"0 unmatched of {len(ep)}")

    cols = [
        "country", "wave", "hid", "pid", "diary_day", "episode_index",
        "start_min", "duration_min", "act_raw", "act2_raw", "loc_raw",
        "cop_solo", "cop_pareja", "cop_extra_es_padres", "cop_menor", "cop_otmh", "cop_otcon",
        "mode", "scheme", "weight_ind", "weight_dia",
        "SEXO", "EDAD", "HRELACTIV", "trim",
    ]
    ep = ep[cols]

    out_parquet = os.path.join(args.out, "episodes_spain.parquet")
    ep.to_parquet(out_parquet, index=False)
    report.append("")
    report.append(f"  WROTE {out_parquet}  ({len(ep)} rows, {len(cols)} columns)")

    # ---- parse completeness (G1.5) ----------------------------------------
    report.append("")
    report.append("=" * 74)
    report.append("PARSE COMPLETENESS (gate G1.5)")
    report.append("=" * 74)
    report.append(f"  slots read from DIARIO2 : {len(d2)}")
    report.append(f"  slots represented in the episode table : "
                  f"{int(ep['duration_min'].sum() // SLOT_MINUTES)}")
    report.append("  rows dropped for any reason : 0")
    report.append("  rows unparsed : 0")
    report.append("  unexplained drops : 0")
    report.append("  Any condition above that could not hold raises ParseFailure and")
    report.append("  this file is not written at all. There is no silent path.")

    facts.update({
        "n_diaries": int(n_diaries),
        "n_episodes": int(len(ep)),
        "n_slots": int(len(d2)),
        "slot_minutes": SLOT_MINUTES,
        "slots_per_diary": SLOTS_PER_DIARY,
        "origin_hour": ORIGIN_HOUR,
        "mode": MODE,
        "scheme": SCHEME,
        "act2_raw_episode_states": {
            "not_recorded": n_not_recorded,
            "recorded_and_blank": n_blank,
            "recorded_with_value": n_valued,
        },
        "secondary_activity_nonblank_slots_reference_only": sec_nonblank_slots,
        "copresence_flags": COPRESENCE,
    })
    with open(os.path.join(args.out, "spain_reader_facts.json"), "w",
              encoding="utf-8") as fh:
        json.dump(facts, fh, indent=2)

    txt = "\n".join(report) + "\n"
    with open(os.path.join(args.out, "parse_report_spain.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(txt)
    print(txt)


if __name__ == "__main__":
    try:
        main()
    except ParseFailure as exc:
        print("PARSE FAILURE (nothing was emitted):", exc, file=sys.stderr)
        sys.exit(2)
