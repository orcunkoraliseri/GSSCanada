#!/usr/bin/env python3
"""
4J Step 1, work item 1.3 -- reader, United Kingdom (UKTUS 2014-2015, UKDA SN 8128).

Reads the UKDA tab-delimited delivery and emits the common intermediate record
defined in Step1_docs/4thJ_01_corpusAcquisition.md.

Design rules this file is written under, from the step specification:

  * it itemises everything it could not parse, and it FAILS on it;
  * it never infers a value it did not read;
  * an unrecognised code, unit or column value is printed and refused,
    never silently treated as benign (vacuity guard V1.d).

🔴 The UK ships native episodes (start slot + duration), not fixed 10-minute
slots. Nothing is reconstructed here -- this is the opposite of the Spanish
reader, which rebuilds episodes from 144 slots per diary.

Every fact this file assumes (eptime is minutes, tid is the start slot, the
weight defaulting, the three-state secondary-activity handling) is established
and cited in outputs_step1/codebook_facts_uk.md; nothing here is asserted
without a citation there.

Usage:
    python 4thJ_read_uk.py --raw <dir with the unpacked UKDA-8128-tab tree> \
                            --out <outputs_step1 dir>
"""

import argparse
import hashlib
import json
import os
import sys

import pandas as pd

# ---------------------------------------------------------------------------
# Constants, all cited in codebook_facts_uk.md.
# ---------------------------------------------------------------------------
COUNTRY = "UK"          # not "GB" -- codebook_facts_uk.md records the choice
WAVE = "2014-2015"
MODE = "paper_self_completion"     # the diary's mode; codebook_facts_uk.md
SCHEME = "UKTUS_2014_2015"

SLOT_MINUTES = 10
SLOTS_PER_DIARY = 144
ORIGIN_HOUR = 4          # tid=1 is 04:00-04:10 (F-UK-5)
DAY_MINUTES = 1440

# UKDA's own "Number of cases" header in each data dictionary (G1.1 reference)
UKDA_STATED = {
    "diary_ep_long": 587632,
    "individual": 11421,
}

# The only negative sentinel observed for What_Oth1/2/3 in the delivered file
# (F-UK-2): "-9" = "No answer/refused" per the data dictionary's own value
# label for What_Oth1. Mapped to state 2, "recorded and blank" (""). Any other
# negative value appearing in these columns is refused, not assumed benign
# (V1.d) -- it would be a code this reader was not told about.
SECONDARY_BLANK_SENTINEL = "-9"

# 🔴 M-1, 2026-08-15 (contract change, codebook_facts_uk.md sentinel table):
# WhereWhen (location) fields the SAME "-9" = "No answer/refused" sentinel
# (DD's own value label for WhereWhen), on 7,117 of 587,632 episodes
# (1.211 %, F-UK-15). loc_raw is now a three-state field on the same terms as
# act2_raw -- "-9" maps to state 2 ("recorded and blank", ""). This is the
# ONLY value treated as a sentinel here; there is no rule that negative
# values in general are sentinels and none is invented. In particular
# "4276" (F-UK-9, one episode) is NOT this sentinel and is passed through
# unchanged as a value -- it must keep failing G1.4, exactly as before M-1.
LOCATION_BLANK_SENTINEL = "-9"

# Co-presence flags, in the order the dictionary declares them (positions
# 40-48 of uktus15_diary_ep_long). WithMiss and WithNA are missingness /
# concordance flags, not people-present categories (F-UK-4), but per the
# Spanish precedent every recorded flag is emitted as its own named column,
# none folded into another.
COPRESENCE = ["WithAlone", "WithSpouse", "WithMother", "WithFather",
              "WithChild", "WithOther", "WithOtherYK", "WithMiss", "WithNA"]
COP_DOMAIN = {"0", "1"}

# M-8 / D-S2-18 / D-S2-19: the four remaining conditioning-strata sources.
# dhhtype and deconact live in uktus15_individual.tab (DD:individual pos.588,
# 598) -- NOT in uktus15_household.tab, which stays unread (F-UK-14 stands).
# ddayw and dmonth live in uktus15_diary_ep_long.tab (DD:diary_ep_long
# pos.19, 17). codebook_facts_uk_strata.md cites all four.
DHHTYPE_DOMAIN = {str(i) for i in range(1, 9)}          # 1..8
DECONACT_DOMAIN = {"1", "2", "3", "5", "6", "7", "8", "9", "10", "11", "13"}
DECONACT_SENTINELS = {"-9", "-8", "-7", "-1"}
DDAYW_DOMAIN = {"1", "2", "3"}
DMONTH_DOMAIN = {str(i) for i in range(1, 13)}           # 1..12


class ParseFailure(Exception):
    pass


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tab(path, name, report):
    """Read one UKDA .tab file. keep_default_na=False and dtype=str so that
    pandas cannot silently turn an empty field into NaN or a sentinel into an
    int before we ever get to look at it (the work order's warning about
    pandas defaults destroying the three-state distinction)."""
    if not os.path.exists(path):
        raise ParseFailure(f"missing input file {path}")
    size = os.path.getsize(path)
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False,
                      encoding="utf-8")
    report.append(f"  {name:16s} {size:>12d} bytes  md5 {md5_of(path)}  "
                   f"{len(df)} data rows, {len(df.columns)} columns")
    return df


def refuse_unknown(series, allowed, label, report, allow_blank=False):
    seen = set(series.unique())
    ok = set(allowed) | ({""} if allow_blank else set())
    unknown = sorted(seen - ok)
    if unknown:
        raise ParseFailure(
            f"{label}: unrecognised values {unknown[:20]} "
            f"(allowed {sorted(ok)}). Refused rather than assumed harmless."
        )


def three_state_from_uk_secondary(series):
    """Map a raw What_OthN column (dtype str, blanks preserved) to the
    project's three-state convention:
      not recorded (pd.NA)      -- not applicable here: the UK fields
                                    What_Oth1/2/3 on every episode row, so
                                    this column is never 'not recorded' for
                                    the UK (unlike a country that does not
                                    field it at all).
      recorded and blank ("")   -- raw value is the SECONDARY_BLANK_SENTINEL
                                    "-9" ("No answer/refused", F-UK-2).
      recorded with a value     -- any other value, kept as the code string.
    Anything else (a value that is neither the sentinel nor a code we can
    read as a plain integer string) is refused, not coerced.
    """
    out = series.copy()
    is_sentinel = out == SECONDARY_BLANK_SENTINEL
    out = out.where(~is_sentinel, "")
    # everything remaining must be a plain non-negative integer code string,
    # or already blanked above. UKDA .tab floats like "4276" have no decimal
    # point in this column (verified: source is integer-valued in the file).
    remaining = out[out != ""]
    bad = remaining[~remaining.str.fullmatch(r"\d+")]
    if len(bad):
        raise ParseFailure(
            f"secondary activity column: {len(bad)} values are neither the "
            f"blank sentinel '{SECONDARY_BLANK_SENTINEL}' nor a plain "
            f"integer code, examples {list(bad.unique()[:10])}. Refused "
            f"rather than assumed harmless (V1.d)."
        )
    return out.astype("string")


def three_state_from_uk_location(series):
    """M-1: independent mapping for WhereWhen (loc_raw), exactly the same
    shape as three_state_from_uk_secondary but with its OWN sentinel
    (LOCATION_BLANK_SENTINEL) and NO membership check against a code list --
    that is G1.4's job, deliberately kept out of the reader. Any value other
    than the sentinel is passed through unchanged as 'recorded with a value',
    including out-of-list values like '4276' (F-UK-9), which is not this
    sentinel and must keep failing G1.4 after this change exactly as before
    it. The UK fields WhereWhen on every episode row, so 'not recorded'
    (pd.NA) never occurs for this country -- only "" (the sentinel) or a
    code, in a nullable 'string' dtype so the parquet round-trip cannot
    merge pd.NA and "" (exactly act2_raw's treatment)."""
    out = series.copy()
    is_sentinel = out == LOCATION_BLANK_SENTINEL
    out = out.where(~is_sentinel, "")
    return out.astype("string")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True,
                     help="dir containing UKDA-8128-tab/tab and UKDA-8128-tab/mrdoc")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    report = []
    facts = {}

    tab_dir = os.path.join(args.raw, "tab")

    # ---- V1.b: print what was read, with hashes, BEFORE any verdict --------
    report.append("=" * 78)
    report.append("INPUTS READ (hashes computed from disk at parse time)")
    report.append("=" * 78)
    ep_path = os.path.join(tab_dir, "uktus15_diary_ep_long.tab")
    ind_path = os.path.join(tab_dir, "uktus15_individual.tab")

    ep = read_tab(ep_path, "diary_ep_long", report)
    ind = read_tab(ind_path, "individual", report)
    report.append("")
    report.append("  NOT READ (see codebook_facts_uk.md, F-UK-14): "
                   "uktus15_household.tab, uktus15_diary_wide.tab, "
                   "uktus15_dv_time_vars.tab (gate runner only, for G1.7c), "
                   "uktus15_wksched.tab")
    report.append("")

    # ---- G1.1 reference: UKDA's own stated "Number of cases" ---------------
    for key, n_stated in UKDA_STATED.items():
        n_here = {"diary_ep_long": len(ep), "individual": len(ind)}[key]
        mark = "MATCH" if n_here == n_stated else "MISMATCH"
        report.append(f"  {key}: {n_here} rows against UKDA-stated "
                       f"{n_stated} -> {mark}")
        if n_here != n_stated:
            raise ParseFailure(
                f"{key}: row count {n_here} does not equal the {n_stated} "
                f"UKDA states in its own data dictionary 'Number of cases'. "
                f"This is a truncated or partial delivery; nothing "
                f"downstream may be trusted."
            )
    report.append("")

    # ---- V1.d: refuse anything the dictionary did not declare --------------
    report.append("=" * 78)
    report.append("VALUE-DOMAIN REFUSAL (V1.d)")
    report.append("=" * 78)
    for c in COPRESENCE:
        refuse_unknown(ep[c], COP_DOMAIN, f"diary_ep_long.{c}", report)
    report.append("  All nine co-presence flags are inside {0,1}.")

    # M-8 / D-S2-18 / D-S2-19: day-type and season strata sources.
    refuse_unknown(ep["ddayw"], DDAYW_DOMAIN, "diary_ep_long.ddayw", report)
    refuse_unknown(ep["dmonth"], DMONTH_DOMAIN, "diary_ep_long.dmonth", report)
    report.append("  ddayw (day-type stratum) and dmonth (season stratum) are "
                   "inside the domains the data dictionary declares.")

    tid_i = ep["tid"].astype(int)
    bad_tid = ep.loc[(tid_i < 1) | (tid_i > SLOTS_PER_DIARY)]
    if len(bad_tid):
        raise ParseFailure(f"tid: {len(bad_tid)} values outside 1..144")
    report.append("  tid is inside 1..144 on every row.")

    ept = ep["eptime"].astype(float)
    bad_ept = ep.loc[(ept % SLOT_MINUTES != 0) | (ept <= 0)]
    if len(bad_ept):
        raise ParseFailure(
            f"eptime: {len(bad_ept)} values are not a positive multiple of "
            f"{SLOT_MINUTES}"
        )
    report.append(f"  eptime is a positive multiple of {SLOT_MINUTES} on "
                   f"every row (min {ept.min():.0f}, max {ept.max():.0f}).")

    # whatdoing (primary activity): no negative sentinel observed anywhere in
    # the delivered file (codebook_facts_uk.md, required-facts table). Report
    # the observed alphabet; membership against the transcribed list is G1.4,
    # scored independently by the gate runner, not here.
    act_seen = sorted(ep["whatdoing"].unique(), key=lambda s: int(s))
    loc_seen = sorted(ep["WhereWhen"].unique(), key=lambda s: int(s))
    report.append("")
    report.append(f"  whatdoing observed alphabet: {len(act_seen)} distinct codes")
    report.append(f"  WhereWhen observed alphabet: {len(loc_seen)} distinct codes")
    bad_what = ep.loc[ep["whatdoing"].astype(float) < 0]
    if len(bad_what):
        raise ParseFailure(
            f"whatdoing: {len(bad_what)} negative values observed; this "
            f"reader was told (codebook_facts_uk.md) that the primary "
            f"activity column carries no negative sentinel in this "
            f"delivery. Refusing rather than assuming what a negative code "
            f"here would mean."
        )
    facts["act_codes_observed"] = act_seen
    facts["loc_codes_observed"] = loc_seen

    # ---- diary structure -----------------------------------------------
    report.append("")
    report.append("=" * 78)
    report.append("DIARY STRUCTURE")
    report.append("=" * 78)
    ep["hid"] = ep["serial"]
    ep["pid"] = ep["serial"] + "_" + ep["pnum"]
    # F-UK-6: diary_day is the survey's own 1st/2nd-day ordinal (daynum), NOT
    # DiaryDay_Act (day of week) -- 3 of 8,259 two-day respondents share the
    # same DiaryDay_Act on both their days, so only daynum is collision-free.
    ep["diary_day"] = ep["daynum"]
    ep["diary_key"] = ep["pid"] + "_" + ep["diary_day"]

    per_diary_min = ep.groupby("diary_key", sort=False)["eptime"].apply(
        lambda s: s.astype(float).sum())
    n_diary_days = len(per_diary_min)
    bad_sum = per_diary_min[per_diary_min != DAY_MINUTES]
    report.append(f"  {n_diary_days} (person, diary_day) diaries; "
                   f"{len(bad_sum)} do not sum to {DAY_MINUTES} minutes")
    if len(bad_sum):
        raise ParseFailure(
            f"{len(bad_sum)} diaries do not sum to {DAY_MINUTES} minutes, "
            f"examples {bad_sum.head().to_dict()}"
        )

    days_per_person = ep.groupby("pid", sort=False)["diary_day"].nunique()
    dpp_max = int(days_per_person.max())
    report.append(f"  diary days per respondent: max {dpp_max}, "
                   f"distribution {days_per_person.value_counts().to_dict()}")
    facts["diary_days_per_respondent_max"] = dpp_max
    facts["diary_days_per_respondent_distribution"] = {
        str(k): int(v) for k, v in days_per_person.value_counts().items()}

    report.append(f"  mode   = {MODE}   (diary instrument only; "
                   f"see codebook_facts_uk.md)")
    report.append(f"  scheme = {SCHEME}")

    # ---- build the intermediate record: episodes are already native -------
    report.append("")
    report.append("=" * 78)
    report.append("EPISODES (native -- nothing reconstructed, F-UK-1)")
    report.append("=" * 78)
    report.append("  tid = start slot (1..144, slot 1 = 04:00-04:10).")
    report.append("  eptime = duration in minutes. start_min = (tid-1)*10.")

    # Sort ep ONCE, up front, into final row order (pid, diary_day, tid).
    # Sort key uses the NUMERIC tid (a string sort would put "10" before "2").
    # Every column below is built from this single sorted frame `ep`, using
    # index-aligned Series (never a bare .values assignment against a frame
    # that has been reordered separately) -- the reader's own three-state and
    # weight columns must never be able to silently drift out of row
    # alignment with each other.
    ep = ep.assign(_tid_sort=ep["tid"].astype(int))
    ep = ep.sort_values(["pid", "diary_day", "_tid_sort"], kind="mergesort").reset_index(drop=True)
    ep = ep.drop(columns=["_tid_sort"])
    tid_i = ep["tid"].astype(int)
    ept = ep["eptime"].astype(float)

    out = pd.DataFrame({
        "country": COUNTRY,
        "wave": WAVE,
        "hid": ep["hid"],
        "pid": ep["pid"],
        "diary_day": ep["diary_day"],
        "episode_index": ep.groupby(["pid", "diary_day"], sort=False).cumcount(),
        "start_min": (tid_i - 1) * SLOT_MINUTES,
        "duration_min": ept.astype("int64"),
        "act_raw": ep["whatdoing"],
        "mode": MODE,
        "scheme": SCHEME,
    })

    # act2_raw (What_Oth1) and the two extra secondary-activity columns
    # (What_Oth2, What_Oth3, F-UK-2). Three-state rule (work order): the UK
    # fields all three on every episode row, so none is ever pd.NA here --
    # only "" (blank, the -9 sentinel) or a code, in a nullable "string" dtype
    # so the parquet round-trip cannot merge pd.NA and "".
    out["act2_raw"] = three_state_from_uk_secondary(ep["What_Oth1"])
    out["act2_extra_uk_2"] = three_state_from_uk_secondary(ep["What_Oth2"])
    out["act2_extra_uk_3"] = three_state_from_uk_secondary(ep["What_Oth3"])

    # loc_raw (M-1, 2026-08-15): three-state on the same terms as act2_raw.
    # "-9" (F-UK-15) -> state 2 (""); anything else, including "4276"
    # (F-UK-9), passed through unchanged as a value for G1.4 to judge.
    out["loc_raw"] = three_state_from_uk_location(ep["WhereWhen"])

    for c in COPRESENCE:
        out[f"cop_extra_uk_{c}"] = ep[c]

    # weights: both diary weights carried by name (F-UK-3); the contract's
    # single weight_dia is populated from dia_wt_a. 🔴 M-5, CONFIRMED: this
    # was already the reader's behaviour; this round only adds the explicit
    # citation the manager's decision asks for. dia_wt_a is the documented
    # default for diary/event-level (person-day) analysis -- NATCEN p. 31,
    # section 7.4(c)/(d): "The diary weight - day level balances the sample
    # for each month and day of the week"; CTUR p. 13's own worked example,
    # `svyset psu [pw=dia_wt_a], strata(strata)`, declares a person-day-level
    # survey design using dia_wt_a. dia_wt_b (no day-of-week adjustment,
    # NATCEN p.31 §7.4(d)) is carried alongside as weight_dia_b and never
    # silently substituted; see codebook_facts_uk.md F-UK-3 for the reopen
    # trigger (Step 5/6 moving the unit of analysis to the person).
    out["weight_dia_a"] = ep["dia_wt_a"]
    out["weight_dia_b"] = ep["dia_wt_b"]
    out["weight_dia"] = ep["dia_wt_a"]

    out["DiaryDay_Act"] = ep["DiaryDay_Act"]  # extra, F-UK-6
    out["daynum"] = ep["daynum"]              # extra, same key as diary_day

    # M-8 / D-S2-18 / D-S2-19: day-type and season strata raw carriers.
    # strat_day_type_raw is ddayw, NOT DiaryDay_Act (F-UK-17): ddayw is UKDA's
    # own pre-collapsed weekday/Saturday/Sunday field, the harmonisation
    # source; DiaryDay_Act (7-way) rides along unchanged above, as it always
    # has.
    out["strat_day_type_raw"] = ep["ddayw"]
    out["strat_season_raw"] = ep["dmonth"]

    report.append(f"  {len(out)} episodes (native, one row per delivered "
                   f"episode -- no reconstruction, no rows added or dropped)")

    # secondary-activity three-state counts, per column (parse report)
    for col_out, col_raw, label in [
        ("act2_raw", "What_Oth1", "act2_raw (What_Oth1)"),
        ("act2_extra_uk_2", "What_Oth2", "act2_extra_uk_2 (What_Oth2)"),
        ("act2_extra_uk_3", "What_Oth3", "act2_extra_uk_3 (What_Oth3)"),
    ]:
        col = out[col_out]
        n_not_recorded = int(col.isna().sum())
        n_blank = int((col == "").sum())
        n_valued = int(len(col) - n_not_recorded - n_blank)
        report.append(f"  {label}: not recorded {n_not_recorded}, recorded "
                       f"and blank {n_blank}, recorded with a value "
                       f"{n_valued} (of {len(col)} episodes)")
        facts[f"{col_out}_states"] = {
            "not_recorded": n_not_recorded,
            "recorded_and_blank": n_blank,
            "recorded_with_value": n_valued,
        }

    # loc_raw three-state count (M-1). Printed the same way act2_raw's states
    # are, so G1.12's independent recount has an emitted figure to compare
    # against.
    loc_col = out["loc_raw"]
    loc_not_recorded = int(loc_col.isna().sum())
    loc_blank = int((loc_col == "").sum())
    loc_valued = int(len(loc_col) - loc_not_recorded - loc_blank)
    report.append(f"  loc_raw (WhereWhen, M-1): not recorded {loc_not_recorded}, "
                   f"recorded and blank {loc_blank} (sentinel "
                   f"'{LOCATION_BLANK_SENTINEL}', F-UK-15), recorded with a "
                   f"value {loc_valued} (of {len(loc_col)} episodes)")
    facts["loc_raw_states"] = {
        "not_recorded": loc_not_recorded,
        "recorded_and_blank": loc_blank,
        "recorded_with_value": loc_valued,
    }

    # ---- join individual demographics and weight_ind -----------------------
    # M-8 / D-S2-18: dhhtype (household type) and deconact (economic status)
    # both live in uktus15_individual.tab -- DD:individual pos.588 and 598 --
    # not in uktus15_household.tab, which this reader still does not read
    # (F-UK-14 stands; see codebook_facts_uk_strata.md). Same join as
    # DVAge/DMSex, no second join required.
    ind2 = ind.copy()
    ind2["pid"] = ind2["serial"] + "_" + ind2["pnum"]
    ind2 = ind2[["pid", "DVAge", "DMSex", "ind_wt", "dhhtype", "deconact"]].rename(
        columns={"DVAge": "DVAge", "DMSex": "DMSex", "ind_wt": "weight_ind"})

    before = len(out)
    out = out.merge(ind2, on="pid", how="left")
    if len(out) != before:
        raise ParseFailure("the demographic join changed the episode count")
    miss_age = int((out["DVAge"].isna() | (out["DVAge"] == "")).sum())
    if miss_age:
        raise ParseFailure(
            f"{miss_age} episodes have no individual.tab DVAge match. "
            f"Refusing to emit a table with unexplained gaps."
        )
    n_matched_strata = int(out.loc[out["dhhtype"].notna(), "pid"].nunique())
    if n_matched_strata == 0:
        raise ParseFailure(
            "household-type/economic-status join (individual.tab on pid) matched "
            "ZERO distinct respondents -- a join that matches nothing must FAIL "
            "loudly, not produce nulls (D-S2-16)."
        )
    report.append(f"  demographics and individual weight joined on pid, "
                   f"0 unmatched of {len(out)}")
    report.append(f"  household-type/economic-status (dhhtype, deconact) joined on "
                   f"pid: {n_matched_strata} distinct respondents matched")

    # 🔴 CORRECTED after the raw file itself (job 1254923's FAIL): dhhtype and
    # deconact's blank sentinel is a literal single SPACE (" "), the same
    # sentinel convention already documented for the weight columns (F-UK-8),
    # not an empty string. Measured directly: dhhtype " " count = 411 (matches
    # the 3.6% codebook figure exactly); deconact " " count = 25 (matches the
    # "25 blank" component of the 722-row breakdown exactly). Normalised to ""
    # here -- the project's "recorded and blank" convention -- before the
    # domain check and before strat_hh_type_raw/strat_econ_status_raw are set,
    # so the crosswalk's declared blank->unknown row (source_value="") matches.
    out["dhhtype"] = out["dhhtype"].where(out["dhhtype"] != " ", "")
    out["deconact"] = out["deconact"].where(out["deconact"] != " ", "")

    # M-8 / D-S2-19: dhhtype and deconact domain checks. dhhtype fields blank
    # for missing (3.6 %, F-UK-18 context); deconact fields blank or one of
    # four declared sentinels (-9/-8/-7/-1, 6.3 % combined). Both allow_blank.
    refuse_unknown(out["dhhtype"], DHHTYPE_DOMAIN, "individual.dhhtype", report,
                    allow_blank=True)
    refuse_unknown(out["deconact"], DECONACT_DOMAIN | DECONACT_SENTINELS,
                    "individual.deconact", report, allow_blank=True)
    report.append("  dhhtype and deconact are inside the domains the data "
                   "dictionary declares (including declared sentinels).")

    # weight columns: convert raw strings to float64, mapping the literal
    # blank-space sentinel (F-UK-8) to NaN -- a genuine missing weight, not a
    # code and not silently coerced to 0. Anything that is neither the space
    # sentinel nor a parseable decimal is refused (V1.d), never assumed
    # harmless.
    def parse_weight_column(name):
        raw = out[name]
        blank_mask = raw == " "
        n_blank_w = int(blank_mask.sum())
        rest = raw[~blank_mask]
        bad = rest[~rest.str.fullmatch(r"-?(\d+\.?\d*|\.\d+)")]
        if len(bad):
            raise ParseFailure(
                f"{name}: {len(bad)} values are neither the blank-space "
                f"sentinel nor a parseable decimal, examples "
                f"{list(bad.unique()[:10])}. Refused rather than assumed "
                f"harmless (V1.d)."
            )
        vals = raw.where(~blank_mask, None).astype("float64")
        report.append(f"  {name}: {n_blank_w} of {len(out)} rows are the "
                       f"literal blank-space sentinel (F-UK-8), mapped to "
                       f"NaN, not a parseable number")
        facts[f"{name}_blank_sentinel_rows"] = n_blank_w
        return vals

    for wname in ["weight_dia_a", "weight_dia_b", "weight_ind"]:
        out[wname] = parse_weight_column(wname)
    out["weight_dia"] = out["weight_dia_a"]

    # M-8 / D-S2-18 / D-S2-19: the remaining conditioning-strata raw carriers.
    # National values only, no mapping, no banding, no collapsing (Step 2's
    # job -- see codebook_facts_uk_strata.md and strata_proposal.md).
    out["strat_age_band_raw"] = out["DVAge"]
    out["strat_sex_raw"] = out["DMSex"]
    out["strat_hh_type_raw"] = out["dhhtype"]
    out["strat_econ_status_raw"] = out["deconact"]
    report.append("  CARRIED (M-8/D-S2-18/D-S2-19): strat_age_band_raw (DVAge), "
                   "strat_sex_raw (DMSex), strat_hh_type_raw (dhhtype), "
                   "strat_econ_status_raw (deconact), strat_day_type_raw (ddayw, "
                   "already carried above), strat_season_raw (dmonth, already "
                   "carried above) -- six national values, unbanded.")

    cols = [
        "country", "wave", "hid", "pid", "diary_day", "episode_index",
        "start_min", "duration_min", "act_raw", "act2_raw",
        "act2_extra_uk_2", "act2_extra_uk_3", "loc_raw",
    ] + [f"cop_extra_uk_{c}" for c in COPRESENCE] + [
        "mode", "scheme", "weight_ind", "weight_dia",
        "weight_dia_a", "weight_dia_b",
        "DVAge", "DMSex", "DiaryDay_Act", "daynum",
        "dhhtype", "deconact",
        "strat_age_band_raw", "strat_sex_raw", "strat_hh_type_raw",
        "strat_econ_status_raw", "strat_day_type_raw", "strat_season_raw",
    ]
    out = out[cols]

    out_parquet = os.path.join(args.out, "episodes_uk.parquet")
    out.to_parquet(out_parquet, index=False)
    report.append("")
    report.append(f"  WROTE {out_parquet}  ({len(out)} rows, {len(cols)} columns)")

    # ---- parse completeness (G1.5) -----------------------------------------
    report.append("")
    report.append("=" * 78)
    report.append("PARSE COMPLETENESS (gate G1.5)")
    report.append("=" * 78)
    report.append(f"  episode rows read from uktus15_diary_ep_long.tab : {len(ep)}")
    report.append(f"  episode rows represented in the output table    : {len(out)}")
    report.append("  rows dropped for any reason : 0")
    report.append("  rows unparsed : 0")
    report.append("  unexplained drops : 0")
    report.append("  Any condition above that could not hold raises ParseFailure")
    report.append("  and this file is not written at all. There is no silent path.")

    facts.update({
        "n_diary_days": int(n_diary_days),
        "n_episodes": int(len(out)),
        "slot_minutes": SLOT_MINUTES,
        "slots_per_diary": SLOTS_PER_DIARY,
        "origin_hour": ORIGIN_HOUR,
        "mode": MODE,
        "scheme": SCHEME,
        "copresence_flags": COPRESENCE,
    })
    with open(os.path.join(args.out, "uk_reader_facts.json"), "w",
              encoding="utf-8") as fh:
        json.dump(facts, fh, indent=2)

    txt = "\n".join(report) + "\n"
    with open(os.path.join(args.out, "parse_report_uk.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(txt)
    print(txt)


if __name__ == "__main__":
    try:
        main()
    except ParseFailure as exc:
        print("PARSE FAILURE (nothing was emitted):", exc, file=sys.stderr)
        sys.exit(2)
