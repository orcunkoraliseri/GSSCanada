"""3rdJ_07_aug_to_bem_4split.py -- Step 7: Four-Channel BEM/UBEM Integration (3J Leg-3 4-split).

Four asymmetric products:
  Product 1 -- Residential (REPLACE):   per-SIM_HH_ID x Day_Type x Hour occupancy schedules.
  Product 2 -- Office      (MODULATE):  AT_WORK_fraction per archetype x Day_Type x Hour.
  Product 3 -- Retail      (MODULATE):  0.95 x peak-normalized shape, per Day_Type x PR x slot.
  Product 4 -- Hotel       (MODULATE):  s(t) x monthly_rate, per PR x MONTH x Day_Type x slot.

Design docs : Step7_docs/3rdJ_07_bemIntegration_4split.md (+ _val.md)
Port bases  : Leg2_2-split/Step7_docs/3rdJ_07_aug_to_bem_2split.py (post-2026-07-18, _C-hardened)
              Leg2_2-split/Step8_docs/eSim_bem_utils_3J/integration.py (md5 6a92268b..., multizone-fix
                pattern referenced for commercial_integration.py's per-Space replication)
              Leg2_2-split/Step8_docs/office_integration.py (post-2026-07-02)

Locked decisions ported from Leg-2 (OD-7A..7E) + new Leg-3 decisions:
  OD-7A -- Residential occupancy = mean(hom30) over HH members (NOT HH_hom30/max).
  OD-7B -- AT_WORK_fraction is primary column (raw absolute fraction); multiplier = peak-normalized.
  OD-7C -- Office denominator = employed is_office persons, unweighted. EMPLOYED_LFTAG = {1,2}
           (Leg-3 2030 pool also carries LFTAG=3, treated as NOT employed -- documented assumption,
           2026-07-23: no Leg-3 codebook found defining LFTAG=3; conservative exclusion).
  OD-7D -- No Step-9 Equipment/Lighting columns (deferred to Step 9).
  OD-7E -- Residential 2030 = per-bundle band files; office 2030 = one file with BAND column.
  dr_L3-06 -- Retail: multiplier(t) = 0.95 x [at_retail_fraction(t) / max_t(at_retail_fraction(t))],
              peak-normalized per (Day_Type, PR); 0.95 = NECB 2017/2020 retail/sales peak fraction.
  dr_L3-05 -- Hotel guest-room s(t): clock-native (00:00-origin), NO +4h roll applied.

  FLAGGED OPEN ITEM (2026-07-23, staff_shoulder_flag / NECB retail baseline):
    No hour-by-hour NECB Table A-8.4.3.2.(1)-A retail occupancy table exists anywhere in this
    repo (confirmed by repo-wide search). The "baseline <= 0.10" test for staff_shoulder_flag
    (H3 / R5) is therefore computed against a PROVISIONAL PROXY baseline reconstructed from the
    real "RetailStandalone BLDG_OCC_SCH_2010" Schedule:Day:Interval objects found in
    BEM_Setup/Buildings/CAN_MTL/TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v221.idf (an
    ASHRAE 90.1-2019/DOE-PNNL retail-standalone prototype, raw peak 0.80), rescaled x(0.95/0.80)
    so its peak matches the dr_L3-06 0.95 assumption. This is NOT the literal NECB table and
    MUST be reconciled against whichever real mixed-use IDF Step 8 eventually selects (the
    W-section wiring-audit is PENDING for exactly this reason -- see val report). See
    necb_retail_baseline_proxy() below.

  FLAGGED OPEN ITEM (2026-07-23, 2022 retail PR split):
    The Leg-3 Step-5 2022 stock's PR column is region-remapped 1-6 (Prairies=4 merges AB/MB/SK);
    raw province codes are not retained anywhere in the Step-5 outputs. The 2022 retail product
    therefore uses PR=2 (Quebec, exact) for "QC" and PR=4 (Prairies, AB+MB+SK) as a documented
    PROXY for "AB". The 2030 retail lever files do NOT have this problem (their source diary
    pool retains raw GSS province codes, confirmed PR_GROUP=QC/AB split directly).

  FLAGGED OPEN ITEM (2026-07-23, 2022 hotel AB Q4 gap):
    0_Occupancy/processed/hotel_multiplier_lookup.csv has AB 2022 rows for months 1-9 only
    (months 10-12 missing -- a genuine upstream data gap, QC 2022 is complete). Filled via
    carry-forward from the last available month (September); flagged distinctly in the H4 gate.

Usage (run-from-anywhere):
  py 3rdJ_07_aug_to_bem_4split.py --audit
  py 3rdJ_07_aug_to_bem_4split.py --year 2022
  py 3rdJ_07_aug_to_bem_4split.py --year 2030 --bundle {cons,central,opt}
  py 3rdJ_07_aug_to_bem_4split.py --year 2030 --bundle central --sens {office,retail,hotel}

seed=42 throughout. Deps: pandas, numpy (existing env). No new packages.
2026-07-23 built.
"""
import os
import sys
import hashlib
import argparse
import shutil
import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths (all resolved relative to this script's location, run-from-anywhere)
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent                   # Step7_docs/
LEG3 = HERE.parent                                        # Leg3_4-split/
J3   = LEG3.parent                                        # 3J_docs_occ_nTemp/
BASE = J3.parent                                          # GSSCanada-main/

AUG = (LEG3 / "Step5_docs" / "outputs_step5"
       / "3rdJ_25CEN_aug_Full_Aggregated_excl.csv")

D2030 = (LEG3 / "Step6_docs" / "outputs_step6"
         # H6: the "_C" file is the ONLY valid 2030 source (Leg-2 hard-learned lesson) --
         # hard-fail below (assert_d2030_is_c) on any non-_C default.
         / "2030_synthetic_diaries_4split_calibrated_mindwell_C.csv")
D2030_EXPECTED_MD5 = "7c105ef331b37107d5b605c95028c3ba"

LOOKUP_OFFICE = BASE / "0_Occupancy" / "processed" / "office_archetype_lookup.csv"

RETAIL_LEVER_DIR = LEG3 / "Step6_docs" / "outputs_step6"
RETAIL_LEVER_FILES = {
    "shift":       RETAIL_LEVER_DIR / "at_retail_fraction_2030_shift.csv",        # cons  (0.90)
    "plateau":     RETAIL_LEVER_DIR / "at_retail_fraction_2030_plateau.csv",      # central (0.97)
    "renaissance": RETAIL_LEVER_DIR / "at_retail_fraction_2030_renaissance.csv",  # opt   (1.05)
}

HOTEL_FORECAST = BASE / "0_Occupancy" / "forecasts" / "hotel_multiplier_2030.csv"
HOTEL_LOOKUP   = BASE / "0_Occupancy" / "processed" / "hotel_multiplier_lookup.csv"
HOTEL_ST       = BASE / "0_Occupancy" / "processed" / "hotel_diurnal_shape_st.csv"

OUT_DIR = HERE / "outputs_step7"

MIN_2030_ROWS = 111_024   # 3 bands x 37,008 (matches Leg-2 pattern, confirmed by --audit)

# ---------------------------------------------------------------------------
# Column groups
# ---------------------------------------------------------------------------
ACT = [f"act30_{i:03d}" for i in range(1, 49)]
HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
WRK = [f"wrk30_{i:03d}" for i in range(1, 49)]
RET = [f"ret30_{i:03d}" for i in range(1, 49)]
STAT = ["HHSIZE", "DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR", "PR", "MATCH_TIER"]
OUT_COLS = [
    "SIM_HH_ID", "Day_Type", "Hour",
    "HHSIZE", "DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR", "PR", "MATCH_TIER",
    "Occupancy_Schedule", "Metabolic_Rate",
]
RETAIL_OUT_COLS = ["Day_Type", "PR", "slot", "Hour", "at_retail_fraction",
                    "shape", "multiplier", "staff_shoulder_flag", "n_persons"]
HOTEL_OUT_COLS = ["PR", "MONTH", "Day_Type", "slot", "s_t", "monthly_rate",
                   "multiplier", "rate_filled"]

# ---------------------------------------------------------------------------
# Constants (verbatim from 2J/Leg-2 07_aug_to_bem.py where shared)
# ---------------------------------------------------------------------------
MET = {
    0: 0, 1: 125, 2: 175, 3: 190, 4: 195, 5: 70, 6: 105,
    7: 170, 8: 110, 9: 90, 10: 85, 11: 245, 12: 105, 13: 140, 14: 135,
}
PR_LBL = {
    # Leg-3 Step-5 remaps province codes to region codes 1-6 (same convention as Leg-2).
    1: "Atlantic", 2: "Quebec", 3: "Ontario",
    4: "Prairies",  # AB/MB/SK merged -- see FLAGGED OPEN ITEM above re: retail PR proxy
    5: "BC", 6: "Northern Canada",
}
DAYTYPE = {1: "Weekday", 2: "Weekend", 3: "Weekend"}          # residential/office: Sat+Sun -> Weekend
DAYTYPE3 = {1: "Weekday", 2: "Saturday", 3: "Sunday"}          # retail: 3 distinct day-types (load-bearing Sunday)

EMPLOYED_LFTAG = {1, 2}   # OD-7C; LFTAG=3 (Leg-3 2030 pool only) treated as not-employed (documented)

OFFICE_ARCHETYPES = {"Office_Knowledge", "Office_Public", "Office_Sales"}
BANDS = ["conservative", "hybrid", "fullyhybrid"]

# Bundle -> per-channel axis-state mapping (the "3 aligned diagonal points", user-decided 2026-07-23)
BUNDLE_MAP = {
    "cons":    {"office_band": "conservative", "retail_scenario": "shift",       "hotel_band": "low"},
    "central": {"office_band": "hybrid",       "retail_scenario": "plateau",     "hotel_band": "central"},
    "opt":     {"office_band": "fullyhybrid",  "retail_scenario": "renaissance", "hotel_band": "high"},
}
RETAIL_LEVER_VALUE = {"shift": 0.90, "plateau": 0.97, "renaissance": 1.05}  # H5/H7 exactness check

# ---------------------------------------------------------------------------
# NECB retail baseline PROXY (see FLAGGED OPEN ITEM at top of file)
# ---------------------------------------------------------------------------
_NECB_RETAIL_RAW_PEAK = 0.80
_NECB_RETAIL_TARGET_PEAK = 0.95
_RESCALE = _NECB_RETAIL_TARGET_PEAK / _NECB_RETAIL_RAW_PEAK

# (time_until_hour, value) step tables, verbatim from RetailStandalone BLDG_OCC_SCH_2010
# Schedule:Day:Interval objects, BEM_Setup/Buildings/CAN_MTL/TallBuilding_90.1-2019_..._v221.idf
_WD_STEPS  = [(7, 0.0), (8, 0.1), (9, 0.2), (11, 0.5), (15, 0.7), (16, 0.8),
              (17, 0.7), (19, 0.5), (21, 0.3), (24, 0.0)]
_SAT_STEPS = [(7, 0.0), (8, 0.1), (9, 0.2), (10, 0.5), (11, 0.6), (17, 0.8),
              (18, 0.6), (21, 0.2), (22, 0.1), (24, 0.0)]
_SUN_STEPS = [(9, 0.0), (10, 0.1), (12, 0.2), (17, 0.4), (18, 0.2), (19, 0.1), (24, 0.0)]


def _steps_to_hourly(steps):
    vals = np.zeros(24)
    prev_t = 0
    for (t_until, v) in steps:
        vals[prev_t:t_until] = v
        prev_t = t_until
    return vals


_NECB_RETAIL_BASELINE_HOURLY = {
    "Weekday":  _steps_to_hourly(_WD_STEPS) * _RESCALE,
    "Saturday": _steps_to_hourly(_SAT_STEPS) * _RESCALE,
    "Sunday":   _steps_to_hourly(_SUN_STEPS) * _RESCALE,
}


def necb_retail_baseline_proxy(day_type: str, hour: int) -> float:
    """PROVISIONAL proxy NECB-vintage retail occupancy baseline value at clock hour `hour`
    (0-23) for the given Day_Type. See FLAGGED OPEN ITEM at top of file."""
    return float(_NECB_RETAIL_BASELINE_HOURLY[day_type][hour])


# ---------------------------------------------------------------------------
# H6: _C-only hard gate
# ---------------------------------------------------------------------------
def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_d2030_is_c(path: Path) -> None:
    """H6 hard gate: the 2030 deliverable MUST be the '_C' file with the exact expected MD5."""
    assert "_C" in path.stem or path.stem.endswith("_C"), (
        f"H6 VIOLATION: 2030 deliverable is not the '_C' file: {path.name}"
    )
    if not path.exists():
        return  # existence handled by caller (tolerant PENDING path)
    actual = _md5(path)
    assert actual == D2030_EXPECTED_MD5, (
        f"H6 VIOLATION: 2030 '_C' file MD5 mismatch: expected {D2030_EXPECTED_MD5}, got {actual} "
        f"({path})"
    )
    print(f"  [H6 PASS] 2030 _C file MD5 verified: {actual}", flush=True)


# ---------------------------------------------------------------------------
# H8: input-mutex hard gate (the Leg-2 mutex-bug lesson)
# ---------------------------------------------------------------------------
def check_mutex(df: pd.DataFrame, label: str) -> None:
    """H8: 0 slots with > 1 of {hom30, wrk30, ret30} = 1, per row. FAIL aborts the build."""
    hom = df[HOM].to_numpy(dtype=float)
    wrk = df[WRK].to_numpy(dtype=float)
    ret = df[RET].to_numpy(dtype=float)
    n_active = (hom == 1).astype(np.int8) + (wrk == 1).astype(np.int8) + (ret == 1).astype(np.int8)
    n_conflicts = int((n_active > 1).sum())
    assert n_conflicts == 0, (
        f"H8 MUTEX VIOLATION [{label}]: {n_conflicts:,} slots with > 1 of "
        f"{{hom30,wrk30,ret30}} = 1 -- ABORTING BUILD (Leg-2's Step-7 validator had no mutex "
        f"check; this is exactly the hole that let 4,280 impossible cells cascade into a "
        f"72-task re-sim)."
    )
    print(f"  [H8 PASS] Mutex check [{label}]: 0 conflicts across {len(df):,} rows x 48 slots", flush=True)


# ---------------------------------------------------------------------------
# Helper: dtype_label (verbatim from Leg-2 07_aug_to_bem.py)
# ---------------------------------------------------------------------------
def dtype_label(code, bedrm):
    if int(code) == 2:
        try:
            b = int(float(bedrm))
        except (ValueError, TypeError):
            b = 2
        return "HighRise" if b <= 1 else "MidRise"
    return {1: "SingleD", 3: "OtherDwelling"}.get(int(code), str(int(code)))


# ---------------------------------------------------------------------------
# convert(df) -- residential REPLACE (ported verbatim from Leg-2, OD-7A/D)
# ---------------------------------------------------------------------------
def convert(df):
    df = df.copy()
    df["Day_Type"] = df["DDAY_STRATA"].map(DAYTYPE)
    keys = ["SIM_HH_ID", "Day_Type"]

    occ48 = df.groupby(keys, sort=True)[HOM].mean()
    wdf = df[keys].copy()
    for c in ACT:
        wdf[c] = df[c].map(MET).fillna(100.0)
    met48 = wdf.groupby(keys, sort=True)[ACT].mean().reindex(occ48.index)
    stat = df.groupby(keys, sort=True)[STAT].first().reindex(occ48.index)

    _hh_canon = stat.groupby(level="SIM_HH_ID").first()
    for _col in STAT:
        stat[_col] = stat.index.get_level_values("SIM_HH_ID").map(_hh_canon[_col])

    G = len(occ48.index)
    occ24 = occ48.values.reshape(G, 24, 2).mean(axis=2)
    met24 = met48.values.reshape(G, 24, 2).mean(axis=2)

    # Slot-origin discipline: GSS diary slots are 04:00-origin -- roll +4h to clock time.
    occ24 = np.roll(occ24, 4, axis=1)
    met24 = np.roll(met24, 4, axis=1)

    out = pd.DataFrame({
        "SIM_HH_ID":          occ48.index.get_level_values("SIM_HH_ID").repeat(24),
        "Day_Type":            occ48.index.get_level_values("Day_Type").repeat(24),
        "Hour":                np.tile(np.arange(24), G),
        "Occupancy_Schedule":  np.round(occ24.reshape(-1), 3),
        "Metabolic_Rate":      np.round(met24.reshape(-1), 1),
    })
    for col in ["HHSIZE", "BEDRM", "CONDO", "ROOM", "REPAIR", "MATCH_TIER"]:
        out[col] = np.repeat(stat[col].values, 24)
    dt = np.repeat(stat["DTYPE"].values, 24)
    bd = np.repeat(stat["BEDRM"].values, 24)
    out["DTYPE"] = [dtype_label(c, b) for c, b in zip(dt, bd)]
    pr = np.repeat(stat["PR"].values, 24)
    out["PR"] = [PR_LBL.get(int(p), str(int(p))) for p in pr]

    return out[OUT_COLS]


# ---------------------------------------------------------------------------
# complete_day_types(df) -- ported verbatim from Leg-2, extends DRAW_COLS with ret30
# ---------------------------------------------------------------------------
def complete_day_types(df):
    rng = np.random.default_rng(42)
    hh_strata = df.groupby("SIM_HH_ID")["DDAY_STRATA"].apply(lambda s: frozenset(s.unique()))
    wd_only = set(hh_strata.index[hh_strata.apply(lambda s: (1 in s) and not (2 in s or 3 in s))])
    we_only = set(hh_strata.index[hh_strata.apply(lambda s: (2 in s or 3 in s) and (1 not in s))])

    wd_pool = df[df["DDAY_STRATA"] == 1]
    we_pool = df[df["DDAY_STRATA"].isin([2, 3])]

    DRAW_COLS = ACT + HOM + WRK + RET  # 4-split extends 2-split to include RET
    extra = []
    if wd_only:
        sub = df[df["SIM_HH_ID"].isin(wd_only)].copy()
        pick = rng.integers(0, len(we_pool), size=len(sub))
        sub[DRAW_COLS] = we_pool.iloc[pick][DRAW_COLS].values
        sub["DDAY_STRATA"] = 2
        _hh_stat_wd = df[df["SIM_HH_ID"].isin(wd_only)].groupby("SIM_HH_ID")[STAT].first()
        for _col in STAT:
            sub[_col] = sub["SIM_HH_ID"].map(_hh_stat_wd[_col])
        extra.append(sub)
        print(f"  donor-draw {len(wd_only):,} WD-only HHs -> Weekend ({len(sub):,} member-rows)", flush=True)
    if we_only:
        sub = df[df["SIM_HH_ID"].isin(we_only)].copy()
        pick = rng.integers(0, len(wd_pool), size=len(sub))
        sub[DRAW_COLS] = wd_pool.iloc[pick][DRAW_COLS].values
        sub["DDAY_STRATA"] = 1
        _hh_stat_we = df[df["SIM_HH_ID"].isin(we_only)].groupby("SIM_HH_ID")[STAT].first()
        for _col in STAT:
            sub[_col] = sub["SIM_HH_ID"].map(_hh_stat_we[_col])
        extra.append(sub)
        print(f"  donor-draw {len(we_only):,} WE-only HHs -> Weekday ({len(sub):,} member-rows)", flush=True)
    if not extra:
        print("  No day-type completion needed (all HHs already have both day-types).", flush=True)
    return pd.concat([df] + extra, ignore_index=True) if extra else df


# ---------------------------------------------------------------------------
# assemble_2030(office_band) -- ported from Leg-2, keyed off the office/WFH BAND axis only
# ---------------------------------------------------------------------------
def assemble_2030(office_band, d2030_path=None):
    rng = np.random.default_rng(42)
    stock = pd.read_csv(AUG, low_memory=False)
    _d2030 = Path(d2030_path) if d2030_path is not None else D2030
    d30 = pd.read_csv(_d2030, low_memory=False)
    band_d30 = d30[d30["BAND"] == office_band].copy()
    print(f"  assemble_2030({office_band}): stock {len(stock):,} rows; 2030-band pool {len(band_d30):,} rows",
          flush=True)

    out = stock.copy()
    DRAW_COLS = ACT + HOM + WRK + RET
    for k in (1, 2, 3):
        smask = (stock["DDAY_STRATA"].values == k)
        pool = band_d30[band_d30["DDAY_STRATA"] == k]
        if len(pool) == 0:
            print(f"  WARNING: no 2030 rows for BAND={office_band}, DDAY_STRATA={k}", flush=True)
            continue
        pick = rng.integers(0, len(pool), size=int(smask.sum()))
        out.loc[smask, DRAW_COLS] = pool.iloc[pick][DRAW_COLS].values
    return out


# ---------------------------------------------------------------------------
# build_office_multiplier(df, band_label, lookup_df) -- ported verbatim from Leg-2
# ---------------------------------------------------------------------------
def build_office_multiplier(df, band_label, lookup_df):
    is_office_nocs = lookup_df[lookup_df["is_office"] == True]["NOCS"].tolist()
    nocs_to_arch = lookup_df.set_index("NOCS")["archetype_label"].to_dict()

    df = df.copy()
    df["office_archetype"] = df["NOCS"].map(nocs_to_arch).fillna("Unknown_NOCS")
    df["Day_Type"] = df["DDAY_STRATA"].map(DAYTYPE)

    mask_office = df["NOCS"].isin(is_office_nocs)
    mask_employed = df["LFTAG"].isin(EMPLOYED_LFTAG)
    office_df = df[mask_office & mask_employed].copy()

    print(f"  Office [{band_label}]: {len(office_df):,} employed is_office persons "
          f"(of {len(df):,} total rows); archetypes: {sorted(office_df['office_archetype'].unique())}",
          flush=True)

    rows = []
    for arch in sorted(OFFICE_ARCHETYPES):
        for day_type in ["Weekday", "Weekend"]:
            sub = office_df[(office_df["office_archetype"] == arch) & (office_df["Day_Type"] == day_type)]
            n = len(sub)
            if n == 0:
                print(f"  WARNING: no rows for {arch} x {day_type} [{band_label}] -- filling with zeros", flush=True)
                for h in range(24):
                    rows.append({
                        "office_archetype": arch, "BAND": band_label, "Day_Type": day_type,
                        "Hour": h, "AT_WORK_fraction": 0.0, "multiplier": 0.0, "n_persons": 0,
                    })
                continue
            wrk48 = sub[WRK].mean().values
            wrk24 = wrk48.reshape(24, 2).mean(axis=1)
            wrk24 = np.roll(wrk24, 4)
            for h in range(24):
                rows.append({
                    "office_archetype": arch, "BAND": band_label, "Day_Type": day_type,
                    "Hour": h, "AT_WORK_fraction": float(wrk24[h]), "n_persons": n,
                })

    result = pd.DataFrame(rows)
    wd_mask = result["Day_Type"] == "Weekday"
    wd_peak = result[wd_mask].groupby("office_archetype")["AT_WORK_fraction"].max()
    result["wd_peak"] = result["office_archetype"].map(wd_peak)
    result["multiplier"] = np.where(
        result["wd_peak"] > 0, result["AT_WORK_fraction"] / result["wd_peak"], 0.0,
    )
    result.drop(columns=["wd_peak"], inplace=True)
    result["AT_WORK_fraction"] = result["AT_WORK_fraction"].round(4)
    result["multiplier"] = result["multiplier"].round(4)

    return result[["office_archetype", "BAND", "Day_Type", "Hour",
                   "AT_WORK_fraction", "multiplier", "n_persons"]]


# ---------------------------------------------------------------------------
# build_retail_product -- NEW (Leg-3), dr_L3-06 normalization
# ---------------------------------------------------------------------------
def _retail_rows_from_slotarray(day_type, pr, arr_clock48, n_persons):
    """arr_clock48: length-48 float array, CLOCK-origin (already +4h-rolled). Returns row dicts."""
    peak = float(arr_clock48.max())
    shape = arr_clock48 / peak if peak > 0 else np.zeros(48)
    multiplier_raw = 0.95 * shape
    rows = []
    for i in range(48):
        hour = i // 2
        baseline = necb_retail_baseline_proxy(day_type, hour)
        flag = 1 if baseline <= 0.10 else 0
        mult_final = baseline if flag else float(multiplier_raw[i])
        rows.append({
            "Day_Type": day_type, "PR": pr, "slot": i + 1, "Hour": hour,
            "at_retail_fraction": round(float(arr_clock48[i]), 6),
            "shape": round(float(shape[i]), 6),
            "multiplier": round(mult_final, 6),
            "staff_shoulder_flag": flag,
            "n_persons": n_persons,
        })
    return rows


def build_retail_product_2030(retail_scenario):
    """retail_scenario in {'shift','plateau','renaissance'}. Reads the Step-6 lever file directly
    (Step-6B amplitude drift already baked into *_levered before this normalization, dr_L3-06)."""
    path = RETAIL_LEVER_FILES[retail_scenario]
    df = pd.read_csv(path)
    df = df[df["PR_GROUP"].isin(["QC", "AB"])].copy()
    day_map = {"weekday": "Weekday", "saturday": "Saturday", "sunday": "Sunday"}
    df["Day_Type"] = df["day_type"].map(day_map)

    rows = []
    for (dt, pr), g in df.groupby(["Day_Type", "PR_GROUP"]):
        g = g.sort_values("slot")
        assert len(g) == 48, f"retail lever [{retail_scenario}/{dt}/{pr}]: expected 48 slots, got {len(g)}"
        arr = g["at_retail_fraction_2030_levered"].to_numpy(dtype=float)   # GSS diary-origin (slot1=04:00)
        arr_clock = np.roll(arr, 8)   # +4h roll = 8 half-hour slots (slot-origin discipline)
        rows.extend(_retail_rows_from_slotarray(dt, pr, arr_clock, n_persons=None))
    out = pd.DataFrame(rows)[RETAIL_OUT_COLS]
    print(f"  Retail [{retail_scenario}]: {len(out):,} rows (3 Day_Type x 2 PR x 48 slots = 288)", flush=True)
    return out


def build_retail_product_2022(stock):
    """PR proxy: QC = region 2 (exact); AB = region 4 (Prairies, AB+MB+SK) -- documented open item."""
    stock = stock.copy()
    stock["Day_Type3"] = stock["DDAY_STRATA"].map(DAYTYPE3)
    rows = []
    for pr_label, region_code in [("QC", 2), ("AB", 4)]:
        sub_pr = stock[stock["PR"] == region_code]
        for dt in ["Weekday", "Saturday", "Sunday"]:
            sub = sub_pr[sub_pr["Day_Type3"] == dt]
            if len(sub) == 0:
                print(f"  WARNING: no 2022 rows for PR={pr_label}/{dt} -- skipping", flush=True)
                continue
            ret48 = sub[RET].mean().to_numpy(dtype=float)
            ret48_clock = np.roll(ret48, 8)
            rows.extend(_retail_rows_from_slotarray(dt, pr_label, ret48_clock, n_persons=len(sub)))
    out = pd.DataFrame(rows)[RETAIL_OUT_COLS]
    print(f"  Retail [2022]: {len(out):,} rows", flush=True)
    return out


# ---------------------------------------------------------------------------
# build_hotel_product -- NEW (Leg-3), dr_L3-05 s(t) x monthly_rate
# ---------------------------------------------------------------------------
def build_hotel_product(monthly_rate_df, scenario_label):
    """monthly_rate_df: columns PR, MONTH, occupancy_rate, [rate_filled] (0/1)."""
    st = pd.read_csv(HOTEL_ST)
    day_map = {"weekday": "Weekday", "weekend": "Weekend"}

    # H1/M3 clock-origin assertion: hotel s(t) is clock-native -- assert overnight plateau at 22:00-06:00.
    wd = st[st["day_type"] == "weekday"].sort_values("slot_index")
    s_by_hour = wd.groupby(wd["slot_index"] // 2)["s_value"].mean()
    plateau_hours_ok = all(s_by_hour.get(h, 0) >= 0.99 for h in [22, 23, 0, 1, 2, 3, 4, 5])
    assert plateau_hours_ok, (
        f"H9/M3 VIOLATION: hotel s(t) overnight plateau not at 22:00-06:00 clock time "
        f"(mis-roll risk) -- s_by_hour={s_by_hour.to_dict()}"
    )
    print("  [H9/M3 PASS] Hotel s(t) is clock-native; overnight plateau confirmed at 22:00-06:00 "
          "(NO roll applied, per dr_L3-05)", flush=True)

    rate_lookup = monthly_rate_df.set_index(["PR", "MONTH"])
    rows = []
    for pr in ["QC", "AB"]:
        for month in range(1, 13):
            key = (pr, month)
            if key in rate_lookup.index:
                rec = rate_lookup.loc[key]
                rate = float(rec["occupancy_rate"]) if not hasattr(rec, "iloc") else float(rec["occupancy_rate"].iloc[0] if hasattr(rec["occupancy_rate"], "iloc") else rec["occupancy_rate"])
                filled = int(rec.get("rate_filled", 0)) if hasattr(rec, "get") else 0
            else:
                rate, filled = float("nan"), 1
            for day_raw, day_lbl in [("weekday", "Weekday"), ("weekend", "Weekend")]:
                sub = st[st["day_type"] == day_raw].sort_values("slot_index")
                for _, r in sub.iterrows():
                    s_t = float(r["s_value"])
                    mult = s_t * rate if rate == rate else float("nan")  # NaN-safe
                    rows.append({
                        "PR": pr, "MONTH": month, "Day_Type": day_lbl,
                        "slot": int(r["slot_index"]) + 1, "s_t": s_t,
                        "monthly_rate": round(rate, 4) if rate == rate else rate,
                        "multiplier": round(mult, 6) if mult == mult else mult,
                        "rate_filled": filled,
                    })
    out = pd.DataFrame(rows)[HOTEL_OUT_COLS]
    n_nan = int(out["multiplier"].isna().sum())
    if n_nan:
        print(f"  WARNING [{scenario_label}]: {n_nan} hotel rows with no monthly_rate (NaN multiplier)", flush=True)
    print(f"  Hotel [{scenario_label}]: {len(out):,} rows (2 PR x 12 mo x 2 DT x 48 slots = 2304)", flush=True)
    return out


def _resolve_hotel_2022_rates():
    """2022 monthly_rate from the historical lookup; carry-forward fill AB's missing Q4 months
    (documented FLAGGED OPEN ITEM -- AB 2022 lookup rows only cover months 1-9)."""
    lk = pd.read_csv(HOTEL_LOOKUP)
    lk22 = lk[lk["YEAR"] == 2022][["PR", "MONTH", "occupancy_rate"]].copy()
    full_idx = pd.MultiIndex.from_product([["QC", "AB"], range(1, 13)], names=["PR", "MONTH"])
    lk22 = lk22.set_index(["PR", "MONTH"]).reindex(full_idx).reset_index()
    lk22["rate_filled"] = lk22["occupancy_rate"].isna().astype(int)
    lk22 = lk22.sort_values(["PR", "MONTH"])
    lk22["occupancy_rate"] = lk22.groupby("PR")["occupancy_rate"].ffill().bfill()
    n_filled = int(lk22["rate_filled"].sum())
    if n_filled:
        print(f"  [FLAGGED] 2022 hotel monthly_rate: {n_filled} (PR,MONTH) cells carry-forward-filled "
              f"(AB Q4 2022 gap in {HOTEL_LOOKUP.name}) -- see FLAGGED OPEN ITEM in file header", flush=True)
    return lk22


def _resolve_hotel_2030_rates(hotel_band):
    fc = pd.read_csv(HOTEL_FORECAST)
    sub = fc[fc["BAND"] == hotel_band][["PR", "MONTH", "occupancy_rate"]].copy()
    sub["rate_filled"] = 0
    return sub


# ---------------------------------------------------------------------------
# Acceptance gates -- residential/office (ported)
# ---------------------------------------------------------------------------
def run_residential_gates(bem, label=""):
    tag = f" [{label}]" if label else ""
    assert set(bem["Day_Type"].unique()) <= {"Weekday", "Weekend"}, f"Day_Type domain violation{tag}"
    assert bem["Hour"].between(0, 23).all(), f"Hour out of [0,23]{tag}"
    occ_ok = bem["Occupancy_Schedule"].between(0, 1).all()
    assert occ_ok, f"Occupancy_Schedule out of [0,1]{tag}"
    assert (bem["Metabolic_Rate"] >= 0).all(), f"Metabolic_Rate negative{tag}"
    cov = bem.groupby("SIM_HH_ID")["Day_Type"].nunique()
    bad = int((cov < 2).sum())
    assert bad == 0, f"{bad} HHs missing a day-type{tag}"
    print(f"  [GATE PASS] Residential{tag}: Day_Type domain, Hour range, Occupancy [0,1], "
          f"Metabolic >=0, day-type coverage -- ALL 5 PASS", flush=True)


def run_office_gates(off, is_2030=False, label=""):
    tag = f" [{label}]" if label else ""
    archs = set(off["office_archetype"].unique())
    assert archs <= OFFICE_ARCHETYPES, f"Office archetype domain violation{tag}"
    assert off["AT_WORK_fraction"].between(0, 1).all(), f"AT_WORK_fraction out of [0,1]{tag}"

    bands_to_check = BANDS if is_2030 else ["observed"]
    for arch in OFFICE_ARCHETYPES:
        for dt in ["Weekday", "Weekend"]:
            for band in bands_to_check:
                sub = off[(off["office_archetype"] == arch) & (off["Day_Type"] == dt) & (off["BAND"] == band)]
                assert len(sub) == 24, f"Incomplete grid{tag}: {arch} x {dt} x {band}: {len(sub)} rows"

    print(f"  [GATE PASS] Office{tag}: archetype domain, AT_WORK_fraction [0,1], grid completeness -- PASS",
          flush=True)


def run_retail_gates(ret, label=""):
    """H1/H2/H3 product-side gates."""
    tag = f" [{label}]" if label else ""
    assert set(ret["Day_Type"].unique()) <= {"Weekday", "Saturday", "Sunday"}, f"Retail Day_Type domain{tag}"
    assert set(ret["PR"].unique()) <= {"QC", "AB"}, f"Retail PR domain{tag}"
    assert ret["Hour"].between(0, 23).all(), f"Retail Hour out of [0,23]{tag}"
    assert ret["multiplier"].between(0, 0.95 + 1e-9).all(), (
        f"Retail multiplier out of [0,0.95]{tag}: max={ret['multiplier'].max():.4f}"
    )
    for (dt, pr), g in ret.groupby(["Day_Type", "PR"]):
        peak = g["multiplier"].max()
        assert abs(peak - 0.95) < 1e-6 or (g["shape"] == 0).all(), (
            f"H2/R1 peak != 0.95 exactly{tag} [{dt}/{pr}]: {peak:.6f}"
        )
        sh = g[g["staff_shoulder_flag"] == 1]
        for _, r in sh.iterrows():
            base = necb_retail_baseline_proxy(dt, int(r["Hour"]))
            assert abs(r["multiplier"] - base) < 1e-6, f"H3 staff-shoulder multiplier mismatch{tag}"
    print(f"  [GATE PASS] Retail{tag}: Day_Type/PR domain, Hour range, multiplier [0,0.95], "
          f"peak=0.95 exact, staff-shoulder preserved -- ALL PASS", flush=True)


def run_hotel_gates(hot, label=""):
    tag = f" [{label}]" if label else ""
    assert set(hot["Day_Type"].unique()) <= {"Weekday", "Weekend"}, f"Hotel Day_Type domain{tag}"
    assert set(hot["PR"].unique()) <= {"QC", "AB"}, f"Hotel PR domain{tag}"
    assert hot["MONTH"].between(1, 12).all(), f"Hotel MONTH out of [1,12]{tag}"
    valid_mult = hot["multiplier"].dropna()
    assert (valid_mult > 0).all() and (valid_mult <= 1.0 + 1e-9).all(), (
        f"Hotel multiplier out of (0,1]{tag}: min={valid_mult.min():.4f}, max={valid_mult.max():.4f}"
    )
    n_months = hot.groupby("PR")["MONTH"].apply(lambda s: s.nunique())
    assert (n_months == 12).all(), f"Hotel missing months{tag}: {n_months.to_dict()}"
    print(f"  [GATE PASS] Hotel{tag}: Day_Type/PR domain, MONTH [1,12], multiplier (0,1], "
          f"12 months per PR -- ALL PASS", flush=True)


# ---------------------------------------------------------------------------
# Atomic write helper (H7)
# ---------------------------------------------------------------------------
def atomic_write(df, path, float_format):
    path = Path(path)
    today = datetime.date.today().isoformat()
    if path.exists():
        bak = path.parent / f"{path.stem}_BAK_{today}{path.suffix}"
        if not bak.exists():
            shutil.copy2(path, bak)
            print(f"  Backed up -> {bak.name}", flush=True)
    tmp = str(path) + ".tmp"
    df.to_csv(tmp, index=False, float_format=float_format)
    os.replace(tmp, str(path))
    print(f"  WROTE {path.name}: {len(df):,} rows", flush=True)


# ---------------------------------------------------------------------------
# --audit
# ---------------------------------------------------------------------------
def cmd_audit():
    print("=" * 64, flush=True)
    print("STEP 7 (4-split) -- INPUT AUDIT (read-only)", flush=True)
    print("=" * 64, flush=True)

    print("\n[1] 2022 stock:", flush=True)
    print(f"    {AUG}", flush=True)
    if not AUG.exists():
        print("    STATUS: MISSING -- cannot proceed", flush=True); sys.exit(1)
    stock = pd.read_csv(AUG, low_memory=False)
    print(f"    Rows: {len(stock):,}  |  Unique HH: {stock['SIM_HH_ID'].nunique():,}", flush=True)
    for grp, cols in [("act30", ACT), ("hom30", HOM), ("wrk30", WRK), ("ret30", RET)]:
        missing = [c for c in cols if c not in stock.columns]
        print(f"    {grp}: {'MISSING ' + str(missing[:3]) if missing else 'PRESENT (NaN=' + str(int(stock[cols].isna().sum().sum())) + ')'}",
              flush=True)
    check_mutex(stock, "2022 stock")
    print("    STATUS: OK", flush=True)

    print("\n[2] 2030 deliverable:", flush=True)
    print(f"    {D2030}", flush=True)
    if not D2030.exists():
        print("    STATUS: 2030 deliverable not synced -- PENDING", flush=True)
    else:
        assert_d2030_is_c(D2030)
        d30 = pd.read_csv(D2030, low_memory=False)
        print(f"    Rows: {len(d30):,}", flush=True)
        bands = sorted(d30["BAND"].unique()) if "BAND" in d30.columns else []
        print(f"    BAND values: {bands} (expected {BANDS})", flush=True)
        check_mutex(d30, "2030 _C")
        print("    STATUS: OK", flush=True)

    print("\n[3] Office archetype lookup:", flush=True)
    print(f"    {LOOKUP_OFFICE}: {'OK' if LOOKUP_OFFICE.exists() else 'MISSING'}", flush=True)

    print("\n[4] Retail lever files:", flush=True)
    for k, p in RETAIL_LEVER_FILES.items():
        print(f"    {k}: {p.name} -- {'OK' if p.exists() else 'MISSING'}", flush=True)
    qc_dereg = RETAIL_LEVER_DIR / "at_retail_fraction_2030_renaissance_qcSundayDereg.csv"
    print(f"    qcSundayDereg (renaissance only, optional variant, NOT built by default): "
          f"{'present' if qc_dereg.exists() else 'absent'}", flush=True)

    print("\n[5] Hotel inputs:", flush=True)
    for p in [HOTEL_FORECAST, HOTEL_LOOKUP, HOTEL_ST]:
        print(f"    {p.name}: {'OK' if p.exists() else 'MISSING'}", flush=True)

    print("\n[6] Historical-cycle retail fractions (2005/2010/2015):", flush=True)
    print("    NOT PRESENT locally -- deferred to Step-8A-style generation (out of Step-7's "
          "execution order; Leg-2 precedent generates historical residential/office at Step 8A, "
          "not Step 7). FLAGGED per runbook permission to flag rather than fabricate.", flush=True)

    print("\n[7] IDFs for W-section dry-run injection (HighriseApartment tower + mixed-use "
          "commercial prototype):", flush=True)
    print("    Searched 0_BEM_Setup/ (HPXML templates only, no IDFs), BEM_Setup/Buildings/ "
          "(TallBuilding/SuperTallBuilding 90.1-2019 office + SF/Detached house prototypes only; "
          "v221, not v242), 2J_docs_occ_nTemp/BEM_setup/ (ApartmentHighRise/MidRise only, no "
          "retail/hotel/mixed-use zones). NO Tag-2-routable mixed-use prototype IDF (with "
          "HighriseApartment+Office+Retail+LargeHotel spaces in one building) exists anywhere "
          "in this repo. STATUS: W-section PENDING -- flagged.", flush=True)

    print("\n" + "=" * 64, flush=True)
    print("AUDIT COMPLETE", flush=True)
    print("=" * 64, flush=True)


# ---------------------------------------------------------------------------
# --year 2022
# ---------------------------------------------------------------------------
def cmd_year_2022():
    print("=" * 64, flush=True)
    print("STEP 7 (4-split) -- YEAR 2022", flush=True)
    print("=" * 64, flush=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lookup = pd.read_csv(LOOKUP_OFFICE)

    print("\n[LOAD] 2022 stock:", flush=True)
    stock = pd.read_csv(AUG, low_memory=False)
    print(f"  Rows: {len(stock):,}  |  Unique HH: {stock['SIM_HH_ID'].nunique():,}", flush=True)
    check_mutex(stock, "2022 stock (pre-build)")

    # ---- Residential ----
    print("\n[Residential] complete_day_types + convert", flush=True)
    df_complete = complete_day_types(stock)
    bem = convert(df_complete)
    print(f"  Converted: {len(bem):,} rows, {bem['SIM_HH_ID'].nunique():,} unique HH", flush=True)
    run_residential_gates(bem, label="2022")
    out_res = OUT_DIR / "BEM_Schedules_4split_2022.csv"
    atomic_write(bem, out_res, "%.3f")

    # ---- Office ----
    print("\n[Office] build_office_multiplier (2022, BAND=observed)", flush=True)
    office_out = build_office_multiplier(stock, "observed", lookup)
    run_office_gates(office_out, is_2030=False, label="2022")
    out_off = OUT_DIR / "office_presence_multiplier_2022.csv"
    atomic_write(office_out, out_off, "%.4f")

    # ---- Retail ----
    print("\n[Retail] build_retail_product_2022 (PR proxy: AB=Prairies region 4)", flush=True)
    retail_out = build_retail_product_2022(stock)
    run_retail_gates(retail_out, label="2022")
    out_ret = OUT_DIR / "retail_presence_multiplier_2022.csv"
    atomic_write(retail_out, out_ret, "%.6f")

    # ---- Hotel ----
    print("\n[Hotel] build_hotel_product (2022, carry-forward-filled AB Q4 gap)", flush=True)
    rates22 = _resolve_hotel_2022_rates()
    hotel_out = build_hotel_product(rates22, "2022")
    run_hotel_gates(hotel_out, label="2022")
    out_hot = OUT_DIR / "hotel_schedule_multiplier_2022.csv"
    atomic_write(hotel_out, out_hot, "%.6f")

    print("\n" + "=" * 64, flush=True)
    print("YEAR 2022 COMPLETE", flush=True)
    for p in [out_res, out_off, out_ret, out_hot]:
        print(f"  -> {p}", flush=True)
    print("=" * 64, flush=True)


# ---------------------------------------------------------------------------
# --year 2030 --bundle {cons,central,opt} [--sens {office,retail,hotel}]
# ---------------------------------------------------------------------------
def cmd_year_2030(bundle, sens=None, deliverable=None):
    print("=" * 64, flush=True)
    print(f"STEP 7 (4-split) -- YEAR 2030  bundle={bundle}  sens={sens}", flush=True)
    print("=" * 64, flush=True)

    _d2030 = Path(deliverable) if deliverable is not None else D2030
    if not _d2030.exists():
        print("\n  2030 deliverable not synced -- PENDING", flush=True)
        return
    assert_d2030_is_c(_d2030)

    with open(_d2030, encoding="utf-8") as fh:
        row_count = sum(1 for _ in fh) - 1
    if row_count < MIN_2030_ROWS:
        print(f"\n  2030 deliverable not synced -- PENDING (local file has {row_count} rows; "
              f"need >= {MIN_2030_ROWS:,})", flush=True)
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lookup = pd.read_csv(LOOKUP_OFFICE)
    d30 = pd.read_csv(_d2030, low_memory=False)
    check_mutex(d30, "2030 _C (pre-build)")

    cfg = BUNDLE_MAP[bundle]
    written = []

    # channels to (re)build this invocation
    if sens is None:
        chans = {"residential_office", "retail", "hotel"}
        office_states = [(bundle, cfg["office_band"])]
        retail_states = [(bundle, cfg["retail_scenario"])]
        hotel_states = [(bundle, cfg["hotel_band"])]
    else:
        # --sens <channel>: build ONLY the two off-central states for that channel
        off_central = {"cons": BUNDLE_MAP["cons"], "opt": BUNDLE_MAP["opt"]}
        if sens == "office":
            chans = {"residential_office"}
            office_states = [(b, off_central[b]["office_band"]) for b in ("cons", "opt")]
            retail_states, hotel_states = [], []
        elif sens == "retail":
            chans = {"retail"}
            retail_states = [(b, off_central[b]["retail_scenario"]) for b in ("cons", "opt")]
            office_states, hotel_states = [], []
        elif sens == "hotel":
            chans = {"hotel"}
            hotel_states = [(b, off_central[b]["hotel_band"]) for b in ("cons", "opt")]
            office_states, retail_states = [], []
        else:
            raise ValueError(f"unknown --sens {sens}")

    # ---- Residential + Office (share the office/WFH BAND axis) ----
    if "residential_office" in chans:
        for blabel, office_band in office_states:
            print(f"\n[Residential+Office] bundle={blabel} office_band={office_band}", flush=True)
            df_band = assemble_2030(office_band, d2030_path=_d2030)
            check_mutex(df_band, f"2030 assembled ({office_band})")
            df_complete = complete_day_types(df_band)
            bem = convert(df_complete)
            run_residential_gates(bem, label=f"2030/{blabel}")
            out_res = OUT_DIR / f"BEM_Schedules_4split_2030_{blabel}.csv"
            atomic_write(bem, out_res, "%.3f"); written.append(out_res)

        # Office: rebuild the SINGLE all-bands file whenever any office state changes
        # (idempotent; office does not depend on retail/hotel axes).
        office_parts = []
        for band in BANDS:
            band_slice = d30[d30["BAND"] == band].copy()
            part = build_office_multiplier(band_slice, band, lookup)
            office_parts.append(part)
        office_out = pd.concat(office_parts, ignore_index=True)
        run_office_gates(office_out, is_2030=True, label="2030")
        out_off = OUT_DIR / "office_presence_multiplier_2030.csv"
        atomic_write(office_out, out_off, "%.4f"); written.append(out_off)

    # ---- Retail ----
    if "retail" in chans:
        for blabel, scenario in retail_states:
            print(f"\n[Retail] bundle={blabel} scenario={scenario}", flush=True)
            retail_out = build_retail_product_2030(scenario)
            run_retail_gates(retail_out, label=f"2030/{blabel}")
            out_ret = OUT_DIR / f"retail_presence_multiplier_2030_{blabel}.csv"
            atomic_write(retail_out, out_ret, "%.6f"); written.append(out_ret)

    # ---- Hotel ----
    if "hotel" in chans:
        for blabel, hotel_band in hotel_states:
            print(f"\n[Hotel] bundle={blabel} hotel_band={hotel_band}", flush=True)
            rates = _resolve_hotel_2030_rates(hotel_band)
            hotel_out = build_hotel_product(rates, f"2030/{blabel}")
            run_hotel_gates(hotel_out, label=f"2030/{blabel}")
            out_hot = OUT_DIR / f"hotel_schedule_multiplier_2030_{blabel}.csv"
            atomic_write(hotel_out, out_hot, "%.6f"); written.append(out_hot)

    # ---- H5 band-monotonicity cross-check (only meaningful once all 3 bundle files exist) ----
    _check_h5_monotonicity()

    print("\n" + "=" * 64, flush=True)
    print(f"YEAR 2030 [{bundle}{'/' + sens if sens else ''}] COMPLETE", flush=True)
    for p in written:
        print(f"  -> {p}", flush=True)
    print("=" * 64, flush=True)


def _check_h5_monotonicity():
    """H5: office cons>hyb>fully (presence); retail 0.90<0.97<1.05 exact; hotel low<central<high.
    Reports INFO if not all 3 band files exist yet (partial build)."""
    res_files = {b: OUT_DIR / f"BEM_Schedules_4split_2030_{b}.csv" for b in ("cons", "central", "opt")}
    if all(p.exists() for p in res_files.values()):
        means = {}
        for b, p in res_files.items():
            df = pd.read_csv(p, usecols=["Day_Type", "Hour", "Occupancy_Schedule"])
            wd_biz = df[(df["Day_Type"] == "Weekday") & (df["Hour"].between(9, 17))]
            means[b] = float(wd_biz["Occupancy_Schedule"].mean())
        mono = means["cons"] < means["central"] < means["opt"]
        print(f"  [H5 {'PASS' if mono else 'WARN'}] Residential band ordering (WD 9-17h home occ): "
              f"cons={means['cons']:.4f} {'<' if means['cons']<means['central'] else '>='} "
              f"central={means['central']:.4f} {'<' if means['central']<means['opt'] else '>='} "
              f"opt={means['opt']:.4f}", flush=True)
    ret_files = {b: OUT_DIR / f"retail_presence_multiplier_2030_{b}.csv" for b in ("cons", "central", "opt")}
    if all(p.exists() for p in ret_files.values()):
        levers = {b: RETAIL_LEVER_VALUE[BUNDLE_MAP[b]["retail_scenario"]] for b in ("cons", "central", "opt")}
        mono = levers["cons"] < levers["central"] < levers["opt"]
        print(f"  [H5 {'PASS' if mono else 'WARN'}] Retail lever ordering: "
              f"cons={levers['cons']} < central={levers['central']} < opt={levers['opt']}: {mono}", flush=True)
    hot_files = {b: OUT_DIR / f"hotel_schedule_multiplier_2030_{b}.csv" for b in ("cons", "central", "opt")}
    if all(p.exists() for p in hot_files.values()):
        means = {}
        for b, p in hot_files.items():
            df = pd.read_csv(p, usecols=["monthly_rate"])
            means[b] = float(df["monthly_rate"].mean())
        mono = means["cons"] < means["central"] < means["opt"]
        print(f"  [H5 {'PASS' if mono else 'WARN'}] Hotel band ordering (mean monthly_rate): "
              f"cons={means['cons']:.4f} < central={means['central']:.4f} < opt={means['opt']:.4f}: {mono}",
              flush=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="Step 7 BEM Integration -- 3J Leg-3 four-channel 4-split "
                    "(residential REPLACE + office/retail/hotel MODULATE)."
    )
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--audit", action="store_true")
    grp.add_argument("--year", choices=["2022", "2030"])
    ap.add_argument("--bundle", choices=["cons", "central", "opt"], default=None)
    ap.add_argument("--sens", choices=["office", "retail", "hotel"], default=None)
    ap.add_argument("--deliverable", default=None, metavar="PATH")
    args = ap.parse_args()

    if args.audit:
        cmd_audit()
    elif args.year == "2022":
        cmd_year_2022()
    elif args.year == "2030":
        if args.bundle is None:
            ap.error("--year 2030 requires --bundle {cons,central,opt}")
        if args.sens is not None and args.bundle != "central":
            ap.error("--sens should be run with --bundle central (per runbook execution order)")
        cmd_year_2030(bundle=args.bundle, sens=args.sens, deliverable=args.deliverable)


if __name__ == "__main__":
    main()
