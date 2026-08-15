#!/usr/bin/env python3
"""
4J Step 1, work item 1.3 -- reader, Italy (ISTAT Uso del Tempo 2013-2014).

Reads ISTAT's tab-delimited public-use delivery and emits the common
intermediate record defined in Step1_docs/4thJ_01_corpusAcquisition.md.

Design rules this file is written under, from the step specification and the
Italy employee task doc (Prompts/4thJ_employee_step1_italy_2026-08-14.md):

  * it itemises everything it could not parse, and it FAILS on it;
  * it never infers a value it did not read;
  * an unrecognised code, unit or column value is printed and refused,
    never silently treated as benign (vacuity guard V1.d);
  * Italy ships NATIVE EPISODES with explicit clock start/end times, not
    fixed slots -- there is no reconstruction step here, unlike Spain;
  * the diary day wraps at 04:00: exactly one episode per diary ends after
    midnight, and its naive (end - start) is negative until +1440 is added;
  * catcon (secondary activity) is a genuinely separate, coarser
    classification from catpri (primary activity) -- validated by G1.4
    against catcon's OWN list, never catpri's;
  * blank is a real, recorded state (literal ASCII spaces matching the
    field's declared width), not "missing" -- read with keep_default_na=False
    and dtype=str so pandas cannot turn a blank field into NaN before this
    reader ever sees it.

Every column name and every domain check below is transcribed independently
from ISTAT's own Tracciato HTML files and the raw delivered files themselves
-- see Step1_docs/outputs_step1/codebook_facts_italy.md for the citations.

Usage:
    python 4thJ_read_italy.py --raw <dir with unpacked MICRODATI/METADATI> \
                               --out <outputs_step1 dir>
"""

import argparse
import hashlib
import json
import os
import sys

import pandas as pd

# --------------------------------------------------------------------------
# Column names, transcribed from METADATI\uso_tempo_Tracciato_Anno 2013_*.html
# (codebook_facts_italy.md cites the exact rows). Italy is tab-delimited with
# a header row, so these are NAMES, not byte offsets -- resolved by name,
# never by position (TASK 3.0's requirement, honoured here too so the reader
# and the gate runner can be compared by eye).
# --------------------------------------------------------------------------
DIARIO_COLS = [
    "rilev", "anno", "meseri", "profam", "proind", "gsett", "ordepi",
    "oraini", "minini", "orafin", "minfin", "catpri", "catcon", "cluogo",
    "daso", "cmadre", "cpadre", "cconiu", "cfigli", "cfrate", "afacon",
    "aperco", "causi", "bestus", "pc_internet1", "pc_internet2",
]
INDIVIDUI_KEY_COLS = ["profam", "proind", "coefin", "coefi2", "sesso", "claseta2"]

COPRESENCE = ["daso", "cmadre", "cpadre", "cconiu", "cfigli", "cfrate", "afacon", "aperco"]
# Each co-presence field's own fixed ordinal (its position in the header),
# measured directly from the delivered file: every field takes exactly two
# values across all 1,077,657 rows -- a blank, or this string. See
# codebook_facts_italy.md finding F-IT-4.
COPRESENCE_OWN_CODE = {
    "daso": "1", "cmadre": "2", "cpadre": "3", "cconiu": "4",
    "cfigli": "5", "cfrate": "6", "afacon": "7", "aperco": "8",
}

# ISTAT's own stated record counts, README (!Leggimi.html), "Totale record"
# column. This is the reference for G1.1 -- see codebook_facts_italy.md,
# finding F-IT-7. Not a number this reader computed; a number ISTAT printed.
ISTAT_STATED_RECORDS = {
    "DiarioGiornaliero": 1077657,
    "Individui": 44866,
}

# Constant prefix fields for this country, carried from Step 1 so that no
# later step has to guess them (Step 3B). Taken from codebook_facts_italy.md,
# not from Spain's values.
MODE = "paper_papi_self_or_parent_proxy_age3to10"
SCHEME = "UsoDelTempo_2013_2014"

# Wave: the file's own `anno` column is a constant "2013" (fieldwork START
# year only; METH p.9 states fieldwork ran 1 Nov 2013 - 31 Oct 2014). The
# methodology's own stated reference period, and the pre-registered corpus
# decision (RL17 / decision 6), is "2013-2014". Both are recorded; 2013-2014
# is what is emitted, because it is the period ISTAT's own methodology names
# and the survey spans, not merely the calendar year fieldwork started in.
WAVE_EMITTED = "2013-2014"

ORIGIN_HOUR = 4  # QUEST-DG p.2: "Il diario inizia alle 4.00 del mattino"
DAY_MINUTES = 1440


class ParseFailure(Exception):
    pass


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_delimited(path, required_cols, report, exact=False):
    """Read one ISTAT tab-delimited file. Header row is checked by name, not
    assumed. Blanks are read literally (keep_default_na=False, dtype=str) so
    the three-state rule cannot be violated before this function returns.

    `exact=True` requires the header to equal `required_cols` exactly, in
    order (used for DiarioGiornaliero, whose full 26-column layout this
    reader transcribed and consumes in full). `exact=False` only requires
    `required_cols` to be a subset, by name (used for Individui, which has
    267 columns and this reader only consumes a handful of them by name --
    still resolved by name, never by position, but not required to
    transcribe columns this reader never reads)."""
    if not os.path.exists(path):
        raise ParseFailure(f"missing input file {path}")
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        head = fh.read(4096)
    try:
        head.decode("cp1252")
    except UnicodeDecodeError as exc:
        raise ParseFailure(f"{path}: does not decode as cp1252: {exc}")

    df = pd.read_csv(
        path, sep="\t", dtype=str, keep_default_na=False,
        encoding="cp1252",
    )
    got_cols = list(df.columns)
    if exact:
        if got_cols != required_cols:
            missing = [c for c in required_cols if c not in got_cols]
            extra = [c for c in got_cols if c not in required_cols]
            raise ParseFailure(
                f"{path}: header does not match the transcribed Tracciato "
                f"column list. missing={missing} extra={extra}"
            )
    else:
        missing = [c for c in required_cols if c not in got_cols]
        if missing:
            raise ParseFailure(
                f"{path}: required columns not found by name: {missing} "
                f"(header has {len(got_cols)} columns)"
            )
    report.append(f"  {os.path.basename(path):55s} {size:>12d} bytes  "
                   f"md5 {md5_of(path)}  {len(df)} data rows, {len(got_cols)} columns")
    return df


def refuse_unknown(series, allowed, label, report):
    seen = set(series.unique())
    unknown = sorted(seen - set(allowed))
    if unknown:
        raise ParseFailure(
            f"{label}: unrecognised values {unknown[:20]} "
            f"(allowed {sorted(allowed)}). Refused rather than assumed harmless."
        )
    report.append(f"  {label}: all values inside {sorted(allowed)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True,
                     help="dir containing MICRODATI/ and METADATI/ (the unpacked zip)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    report = []
    facts = {}

    diario_path = os.path.join(args.raw, "MICRODATI",
                                "uso_tempo_Microdati_Anno_2013_DiarioGiornaliero.txt")
    indiv_path = os.path.join(args.raw, "MICRODATI",
                               "uso_tempo_Microdati_Anno_2013_Individui.txt")

    report.append("=" * 78)
    report.append("INPUTS READ (hashes computed from disk at parse time)")
    report.append("=" * 78)
    d2 = read_delimited(diario_path, DIARIO_COLS, report, exact=True)
    ind = read_delimited(indiv_path, INDIVIDUI_KEY_COLS, report, exact=False)
    report.append("")

    # ---- G1.1 reference: ISTAT's own stated record counts (README) --------
    report.append("=" * 78)
    report.append("RECORD-COUNT RECONCILIATION AGAINST ISTAT'S OWN STATED COUNTS")
    report.append("(!Leggimi.html, 'Totale record' -- see codebook finding F-IT-7)")
    report.append("=" * 78)
    for name, df, key in [("DiarioGiornaliero", d2, "DiarioGiornaliero"),
                           ("Individui", ind, "Individui")]:
        stated = ISTAT_STATED_RECORDS[key]
        n = len(df)
        mark = "MATCH" if n == stated else "MISMATCH"
        report.append(f"  {name}: {n} records against ISTAT's stated {stated} -> {mark}")
        if n != stated:
            raise ParseFailure(
                f"{name}: record count {n} does not equal the {stated} ISTAT "
                f"states in !Leggimi.html. This is a truncated or partial "
                f"delivery; nothing downstream may be trusted."
            )
    report.append("")

    # ---- structural refusals (V1.d) ---------------------------------------
    report.append("=" * 78)
    report.append("VALUE-DOMAIN REFUSAL (V1.d)")
    report.append("=" * 78)
    refuse_unknown(d2["rilev"], {"13"}, "DiarioGiornaliero.rilev", report)
    refuse_unknown(d2["anno"], {"2013"}, "DiarioGiornaliero.anno", report)
    refuse_unknown(d2["meseri"], {"1", "2", "3", "4"}, "DiarioGiornaliero.meseri", report)
    refuse_unknown(d2["gsett"], {"1", "2", "3"}, "DiarioGiornaliero.gsett", report)
    refuse_unknown(d2["oraini"], {f"{h:02d}" for h in range(24)},
                    "DiarioGiornaliero.oraini", report)
    refuse_unknown(d2["orafin"], {f"{h:02d}" for h in range(24)},
                    "DiarioGiornaliero.orafin", report)
    refuse_unknown(d2["minini"], {f"{m:02d}" for m in range(0, 60, 10)},
                    "DiarioGiornaliero.minini", report)
    refuse_unknown(d2["minfin"], {f"{m:02d}" for m in range(0, 60, 10)},
                    "DiarioGiornaliero.minfin", report)
    for c in COPRESENCE:
        allowed = {" ", COPRESENCE_OWN_CODE[c]}
        refuse_unknown(d2[c], allowed, f"DiarioGiornaliero.{c}", report)

    bad_catpri = d2.loc[d2["catpri"].str.strip() == ""]
    if len(bad_catpri):
        raise ParseFailure(f"catpri: {len(bad_catpri)} episodes have a blank "
                            f"primary activity; the codebook establishes this "
                            f"never happens (0 observed)")
    bad_cluogo = d2.loc[d2["cluogo"].str.strip() == ""]
    if len(bad_cluogo):
        raise ParseFailure(f"cluogo: {len(bad_cluogo)} episodes have a blank "
                            f"location; the codebook establishes this never "
                            f"happens (0 observed)")
    report.append("  catpri, cluogo: never blank, as codebook_facts_italy.md establishes")
    report.append("")

    # ---- structural checks: profam/proind format ---------------------------
    bad_profam = d2.loc[~d2["profam"].str.fullmatch(r"\d{6}")]
    if len(bad_profam):
        raise ParseFailure(f"profam: {len(bad_profam)} values are not 6-digit "
                            f"zero-padded strings")
    bad_proind = d2.loc[~d2["proind"].str.fullmatch(r"\d{2}")]
    if len(bad_proind):
        raise ParseFailure(f"proind: {len(bad_proind)} values are not 2-digit "
                            f"zero-padded strings")
    bad_ordepi = d2.loc[~d2["ordepi"].str.fullmatch(r"\d{3}")]
    if len(bad_ordepi):
        raise ParseFailure(f"ordepi: {len(bad_ordepi)} values are not 3-digit "
                            f"zero-padded strings")

    d2 = d2.copy()
    d2["hid"] = d2["profam"]
    d2["pid"] = d2["profam"] + "_" + d2["proind"]

    # ---- episode ordering: ordepi must run 1..N with no gaps, per pid -----
    d2["ordepi_i"] = d2["ordepi"].astype(int)
    d2 = d2.sort_values(["pid", "ordepi_i"], kind="mergesort").reset_index(drop=True)
    first_ep = d2.groupby("pid", sort=False)["ordepi_i"].first()
    if not (first_ep == 1).all():
        offenders = first_ep[first_ep != 1]
        raise ParseFailure(f"{len(offenders)} diaries do not start at ordepi=1, "
                            f"examples {offenders.head().to_dict()}")
    cnt = d2.groupby("pid", sort=False).size()
    last_ep = d2.groupby("pid", sort=False)["ordepi_i"].last()
    if not (last_ep == cnt).all():
        offenders = cnt[last_ep != cnt]
        raise ParseFailure(f"{len(offenders)} diaries have gaps or duplicates "
                            f"in ordepi numbering")
    report.append(f"  {len(cnt)} diary respondents, ordepi runs 1..N with no "
                   f"gaps for every one")

    # ---- diary days per respondent (G1.9) ----------------------------------
    days_per_person = d2.groupby("pid", sort=False)["gsett"].nunique()
    dpp = int(days_per_person.max())
    if dpp != 1 or int(days_per_person.min()) != 1:
        raise ParseFailure(f"diary days per respondent is not uniformly 1: "
                            f"min {days_per_person.min()} max {dpp}")
    report.append(f"  diary days per respondent: {dpp} (uniform, codebook states 1)")
    facts["diary_days_per_respondent"] = dpp
    report.append("")

    # ---- start/duration with the 04:00 wrap --------------------------------
    report.append("=" * 78)
    report.append("DURATION COMPUTATION (native episodes; 04:00 diary-day wrap)")
    report.append("=" * 78)
    oh = d2["oraini"].astype(int)
    om = d2["minini"].astype(int)
    eh = d2["orafin"].astype(int)
    em = d2["minfin"].astype(int)
    start_clock = oh * 60 + om
    end_clock = eh * 60 + em
    raw_diff = end_clock - start_clock
    n_zero = int((raw_diff == 0).sum())
    if n_zero:
        raise ParseFailure(f"{n_zero} episodes have identical start and end "
                            f"clock times; a zero/1440-minute episode cannot "
                            f"be disambiguated without inference, which this "
                            f"reader refuses to do")
    n_wrap = int((raw_diff < 0).sum())
    duration_min = raw_diff.where(raw_diff > 0, raw_diff + DAY_MINUTES)
    d2["start_min"] = start_clock
    d2["duration_min"] = duration_min
    report.append(f"  {n_wrap} episodes wrap past midnight (end clock time < "
                   f"start clock time); +{DAY_MINUTES} min applied to those only")
    report.append(f"  duration range after wrap: min {int(duration_min.min())}, "
                   f"max {int(duration_min.max())}")
    report.append("")

    # ---- three-state act2_raw (catcon) -------------------------------------
    report.append("=" * 78)
    report.append("THREE-STATE act2_raw (catcon)")
    report.append("=" * 78)
    catcon_stripped = d2["catcon"].str.strip()
    # Italy fields catcon on every row (it is in the layout for every
    # episode), so no Italian episode is ever "not recorded" (pd.NA) --
    # only "recorded and blank" ("") or "recorded with a value" (the code).
    act2 = catcon_stripped.astype("string")
    d2["act2_raw"] = act2
    n_not_recorded = int(act2.isna().sum())
    n_blank = int((act2 == "").sum())
    n_valued = int(len(act2) - n_not_recorded - n_blank)
    report.append(f"  not recorded: {n_not_recorded}")
    report.append(f"  recorded and blank: {n_blank}")
    report.append(f"  recorded with a value: {n_valued}")
    report.append(f"  (of {len(act2)} episodes)")
    report.append("")

    # ---- act_raw (catpri, right-stripped -- see codebook finding F-IT-5) --
    d2["act_raw"] = d2["catpri"].str.rstrip()
    d2["loc_raw"] = d2["cluogo"].str.strip()

    # ---- co-presence: every field its own named column, none folded -------
    # None of Italy's 8 fields maps unambiguously onto Spain's 5-slot
    # cop_raw[5] scheme without a harmonisation decision this reader does
    # not make (see codebook finding F-IT-4). All 8 are emitted as
    # cop_extra_it_<field>, following the Spanish precedent of never
    # discarding a recorded field.
    for c in COPRESENCE:
        d2[f"cop_extra_it_{c}"] = d2[c].str.strip()

    d2["episode_index"] = d2.groupby("pid", sort=False).cumcount()
    d2["diary_day"] = d2["gsett"]
    d2["country"] = "IT"
    d2["wave"] = WAVE_EMITTED
    d2["wave_file_anno"] = d2["anno"]  # both recorded, per TASK 2 instruction
    d2["mode"] = MODE
    d2["scheme"] = SCHEME

    # ---- join person-level facts (weights, sex, age band) ------------------
    report.append("=" * 78)
    report.append("JOIN AGAINST Individui (weights, sex, age band)")
    report.append("=" * 78)
    ind2 = ind.copy()
    ind2["pid"] = ind2["profam"] + "_" + ind2["proind"]
    ind2 = ind2[["pid", "coefin", "coefi2", "sesso", "claseta2"]].rename(
        columns={"coefin": "weight_ind_raw", "coefi2": "weight_dia_raw"})
    if ind2["pid"].duplicated().any():
        ndupe = int(ind2["pid"].duplicated().sum())
        raise ParseFailure(f"Individui.txt has {ndupe} duplicate profam+proind "
                            f"keys; person identity is not unique")

    before = len(d2)
    ep = d2.merge(ind2, on="pid", how="left")
    if len(ep) != before:
        raise ParseFailure("the join against Individui changed the episode count")

    unmatched_mask = ep["weight_dia_raw"].isna() | (ep["weight_dia_raw"].str.strip() == "")
    n_unmatched = int(unmatched_mask.sum())
    n_unmatched_pids = int(ep.loc[unmatched_mask, "pid"].nunique())
    report.append(f"  episodes with no matching non-blank diary weight in "
                   f"Individui: {n_unmatched} ({n_unmatched_pids} distinct "
                   f"respondents). Rows are NOT dropped for this reason; "
                   f"weight_ind/weight_dia are left unset (NaN) for them, "
                   f"and this count is a finding, not silently absorbed.")
    facts["episodes_unmatched_to_individui_weight"] = n_unmatched
    facts["respondents_unmatched_to_individui_weight"] = n_unmatched_pids

    def to_weight(series):
        s = series.str.strip()
        out = pd.Series(float("nan"), index=s.index, dtype="float64")
        valid = s != ""
        bad = valid & ~s.str.fullmatch(r"\d{12}")
        if bad.any():
            raise ParseFailure(
                f"{int(bad.sum())} weight values are not 12-digit strings, "
                f"examples {list(s[bad].unique()[:5])}"
            )
        out.loc[valid] = s.loc[valid].astype("int64") / 1e4
        return out

    ep["weight_ind"] = to_weight(ep["weight_ind_raw"])
    ep["weight_dia"] = to_weight(ep["weight_dia_raw"])
    report.append("")

    cols = [
        "country", "wave", "wave_file_anno", "hid", "pid", "diary_day", "episode_index",
        "start_min", "duration_min", "act_raw", "act2_raw", "loc_raw",
        "cop_extra_it_daso", "cop_extra_it_cmadre", "cop_extra_it_cpadre",
        "cop_extra_it_cconiu", "cop_extra_it_cfigli", "cop_extra_it_cfrate",
        "cop_extra_it_afacon", "cop_extra_it_aperco",
        "mode", "scheme", "weight_ind", "weight_dia",
        "sesso", "claseta2", "meseri",
    ]
    ep = ep[cols]

    out_parquet = os.path.join(args.out, "episodes_italy.parquet")
    ep.to_parquet(out_parquet, index=False)
    report.append(f"  WROTE {out_parquet}  ({len(ep)} rows, {len(cols)} columns)")

    # ---- parse completeness (G1.5) -----------------------------------------
    report.append("")
    report.append("=" * 78)
    report.append("PARSE COMPLETENESS (gate G1.5)")
    report.append("=" * 78)
    report.append(f"  episode rows read from DiarioGiornaliero.txt : {len(d2)}")
    report.append(f"  episode rows represented in the emitted table : {len(ep)}")
    report.append("  rows dropped for any reason : 0")
    report.append("  rows unparsed : 0")
    report.append("  unexplained drops : 0")
    report.append("  Any condition above that could not hold raises ParseFailure and")
    report.append("  this file is not written at all. There is no silent path.")

    facts.update({
        "n_respondents": int(len(cnt)),
        "n_episodes": int(len(ep)),
        "origin_hour": ORIGIN_HOUR,
        "mode": MODE,
        "scheme": SCHEME,
        "wave_emitted": WAVE_EMITTED,
        "wave_file_anno": "2013",
        "act2_raw_episode_states": {
            "not_recorded": n_not_recorded,
            "recorded_and_blank": n_blank,
            "recorded_with_value": n_valued,
        },
        "copresence_fields": COPRESENCE,
        "istat_stated_records": ISTAT_STATED_RECORDS,
    })
    with open(os.path.join(args.out, "italy_reader_facts.json"), "w",
              encoding="utf-8") as fh:
        json.dump(facts, fh, indent=2)

    txt = "\n".join(report) + "\n"
    with open(os.path.join(args.out, "parse_report_italy.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(txt)
    print(txt)


if __name__ == "__main__":
    try:
        main()
    except ParseFailure as exc:
        print("PARSE FAILURE (nothing was emitted):", exc, file=sys.stderr)
        sys.exit(2)
