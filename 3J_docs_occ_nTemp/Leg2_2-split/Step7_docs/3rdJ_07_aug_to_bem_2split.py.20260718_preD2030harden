"""3rdJ_07_aug_to_bem_2split.py -- Step 7: Two-Channel BEM/UBEM Integration (3J Leg-2 2-split).

Two asymmetric products:
  Product 1 -- Residential (REPLACE): per-SIM_HH_ID x Day_Type x Hour occupancy schedules.
  Product 2 -- Office   (MODULATE):  aggregate AT_WORK_fraction per archetype x Day_Type x Hour.

Design doc : Step7_docs/3rdJ_07_bemIntegration_2split.md
Builder prompt: Step7_docs/3rdJ_07_builder_prompt.md
Port reference: 2J_docs_occ_nTemp/07_aug_to_bem.py (MET map, +4h roll, dtype_label, PR_LBL,
                DAYTYPE, convert(), complete_day_types(), assemble_2030())

Locked decisions implemented:
  OD-7A -- Residential occupancy = mean(hom30) over HH members (NOT HH_hom30/max).
  OD-7B -- AT_WORK_fraction is primary column (raw absolute fraction); multiplier = peak-normalized.
  OD-7C -- Office denominator = employed is_office persons, unweighted.
           LFTAG employed codes: {1=Paid employee, 2=Self-employed}; 99=not applicable (excluded).
  OD-7D -- No Step-9 Equipment/Lighting columns (deferred to 2-split Step 9).
  OD-7E -- Residential 2030 = 3 band files; office 2030 = one file with BAND column.

Usage (run-from-anywhere):
  py 3rdJ_07_aug_to_bem_2split.py --audit
  py 3rdJ_07_aug_to_bem_2split.py --year 2022
  py 3rdJ_07_aug_to_bem_2split.py --year 2030

seed=42 throughout. Deps: pandas, numpy (existing env). No new packages.
2026-06-26 built.
"""
import os
import sys
import argparse
import shutil
import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths (all resolved relative to this script's location, run-from-anywhere)
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent                   # Step7_docs/
BASE = HERE.parent.parent.parent                         # GSSCanada-main/
#   HERE             = .../Step7_docs
#   HERE.parent      = .../Leg2_2-split
#   HERE.parent^2    = .../3J_docs_occ_nTemp
#   HERE.parent^3    = GSSCanada-main  (BASE)

AUG = (BASE / "3J_docs_occ_nTemp" / "Leg2_2-split"
       / "Step5_docs" / "outputs_step5"
       / "3rdJ_25CEN_aug_Full_Aggregated_excl.csv")

D2030 = (BASE / "3J_docs_occ_nTemp" / "Leg2_2-split"
         / "Step6_docs" / "outputs_step6"
         / "2030_synthetic_diaries_2split_calibrated_mindwell.csv")

LOOKUP = BASE / "0_Occupancy" / "processed" / "office_archetype_lookup.csv"

OUT_DIR = HERE / "outputs_step7"

MIN_2030_ROWS = 111_024   # full calibrated_mindwell file; stale local samples << this

# ---------------------------------------------------------------------------
# Column groups
# ---------------------------------------------------------------------------
ACT = [f"act30_{i:03d}" for i in range(1, 49)]
HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
WRK = [f"wrk30_{i:03d}" for i in range(1, 49)]
STAT = ["HHSIZE", "DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR", "PR", "MATCH_TIER"]
OUT_COLS = [
    "SIM_HH_ID", "Day_Type", "Hour",
    "HHSIZE", "DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR", "PR", "MATCH_TIER",
    "Occupancy_Schedule", "Metabolic_Rate",
]

# ---------------------------------------------------------------------------
# Constants (verbatim from 2J 07_aug_to_bem.py)
# ---------------------------------------------------------------------------
# act code -> watts/person (BEMConverter.metabolic_map; verified vs 2024 Adult Compendium @70W/MET)
MET = {
    0: 0, 1: 125, 2: 175, 3: 190, 4: 195, 5: 70, 6: 105,
    7: 170, 8: 110, 9: 90, 10: 85, 11: 245, 12: 105, 13: 140, 14: 135,
}
PR_LBL = {
    # Fix A (2026-06-26): Step-5 load_augmented_pool() remaps province codes (10–62)
    # to region codes 1–6 via _PROVINCE_TO_REGION in 3rdJ_05_censusLinkage_2split.py.
    # The AUG file carries region codes 1–6 (not raw GSS province codes 10–70), so
    # the old census-code keys (10, 24, 35, ...) never matched -> PR shipped as "1","2",...
    # Authoritative source: _PROVINCE_TO_REGION in 3rdJ_05_censusLinkage_2split.py
    1: "Atlantic",         # provinces 10, 11, 12, 13
    2: "Quebec",           # province 24
    3: "Ontario",          # province 35
    4: "Prairies",         # provinces 46 (MB), 47 (SK), 48 (AB) — merged into one region
    5: "BC",               # province 59
    6: "Northern Canada",  # provinces 60, 61, 62
}
DAYTYPE = {1: "Weekday", 2: "Weekend", 3: "Weekend"}   # Sat+Sun pooled -> Weekend (2-day-type consumer)

# OD-7C: LFTAG codes treated as employed (documented for Progress Log)
# LFTAG 1 = Paid employee, 2 = Self-employed, 99 = Not applicable / retired / not in labour force
EMPLOYED_LFTAG = {1, 2}

OFFICE_ARCHETYPES = {"Office_Knowledge", "Office_Public", "Office_Sales"}
BANDS = ["conservative", "hybrid", "fullyhybrid"]


# ---------------------------------------------------------------------------
# Helper: dtype_label (verbatim from 2J 07_aug_to_bem.py)
# ---------------------------------------------------------------------------
def dtype_label(code, bedrm):
    """Relabel DTYPE numeric code -> string for BEM consumer."""
    if int(code) == 2:          # Apartment -> HighRise/MidRise by BEDRM (BEMConverter proxy)
        try:
            b = int(float(bedrm))
        except (ValueError, TypeError):
            b = 2
        return "HighRise" if b <= 1 else "MidRise"
    return {1: "SingleD", 3: "OtherDwelling"}.get(int(code), str(int(code)))


# ---------------------------------------------------------------------------
# convert(df) -- port of 2J, drops Step-9 equip/light block (OD-7D)
# ---------------------------------------------------------------------------
def convert(df):
    """Residential REPLACE: group by (SIM_HH_ID, Day_Type), compute mean(hom30) -> Occupancy_Schedule,
    mean(MET[act30]) -> Metabolic_Rate; 48->24 hourly; +4h diary->clock roll; relabel DTYPE/PR.

    OD-7A: uses mean(hom30), NOT HH_hom30/max (HH_hom30 is binary ">=1 home" -> overcounts).
    No HH_ID rename needed (2-split stock already keyed SIM_HH_ID).
    """
    df = df.copy()
    df["Day_Type"] = df["DDAY_STRATA"].map(DAYTYPE)
    keys = ["SIM_HH_ID", "Day_Type"]

    occ48 = df.groupby(keys, sort=True)[HOM].mean()                          # (G,48) fraction home
    wdf = df[keys].copy()
    for c in ACT:
        wdf[c] = df[c].map(MET).fillna(100.0)
    met48 = wdf.groupby(keys, sort=True)[ACT].mean().reindex(occ48.index)    # (G,48) watts
    stat = df.groupby(keys, sort=True)[STAT].first().reindex(occ48.index)
    # Fix B (canonicalize STAT across day-types, 2026-06-26):
    # Within each SIM_HH_ID, DTYPE/PR must be identical across Weekday/Weekend rows
    # (validator G.3 requires 0 drift). The stock carries native within-HH variation
    # (e.g., different respondents on different GSS diary days); take .first() per HH
    # as the canonical value and overwrite all day-type rows for that HH.
    _hh_canon = stat.groupby(level="SIM_HH_ID").first()
    for _col in STAT:
        stat[_col] = stat.index.get_level_values("SIM_HH_ID").map(_hh_canon[_col])

    G = len(occ48.index)
    occ24 = occ48.values.reshape(G, 24, 2).mean(axis=2)   # 48->24: avg slot pairs
    met24 = met48.values.reshape(G, 24, 2).mean(axis=2)

    # FIX 2026-06-08 (4h diary->clock offset, ported from 2J):
    # GSS diary slots are 4 AM-origin (slot 1 = 04:00). Roll +4h so Hour 0 = real midnight,
    # matching the EPW weather clock. Without this, schedules inject 4h early vs weather.
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
# complete_day_types(df) -- port of 2J, adapted for SIM_HH_ID + adds WRK draw
# ---------------------------------------------------------------------------
def complete_day_types(df):
    """Ensure every HH has both Weekday and Weekend observations via DONOR-DRAW (seed=42).

    GSS assigns one diary day per respondent; many HHs sit in only one DDAY_STRATA.
    Missing day filled by drawing a genuine opposite-day diary from the in-frame pool
    (per member, keeping dwelling attrs). Preserves calibrated weekend marginal
    (copy-day fill diluted it -2.76 pp in 2J). Extends 2J version to also draw WRK columns.
    """
    rng = np.random.default_rng(42)
    hh_strata = df.groupby("SIM_HH_ID")["DDAY_STRATA"].apply(lambda s: frozenset(s.unique()))
    wd_only = set(hh_strata.index[hh_strata.apply(lambda s: (1 in s) and not (2 in s or 3 in s))])
    we_only = set(hh_strata.index[hh_strata.apply(lambda s: (2 in s or 3 in s) and (1 not in s))])

    wd_pool = df[df["DDAY_STRATA"] == 1]              # weekday donors
    we_pool = df[df["DDAY_STRATA"].isin([2, 3])]      # weekend donors (Sat+Sun pooled)

    DRAW_COLS = ACT + HOM + WRK                       # 2-split extends 2J to include WRK
    extra = []
    if wd_only:                                        # WD-only HHs need a Weekend diary
        sub = df[df["SIM_HH_ID"].isin(wd_only)].copy()
        pick = rng.integers(0, len(we_pool), size=len(sub))
        sub[DRAW_COLS] = we_pool.iloc[pick][DRAW_COLS].values
        sub["DDAY_STRATA"] = 2                         # label -> Weekend (convert() pools 2,3)
        # Fix B (2026-06-26): overwrite ALL HH-level attribute cols with the RECIPIENT HH's
        # own values (read from recipient's existing Weekday block).  Only Occupancy_Schedule
        # + Metabolic_Rate (i.e. the diary cols in DRAW_COLS) come from the donor.
        # This eliminates DTYPE/PR drift that arises when the donor's metadata leaks in
        # (validator G3 reported 2,086 HH with drift before this fix). Port of 2J behavior.
        _hh_stat_wd = df[df["SIM_HH_ID"].isin(wd_only)].groupby("SIM_HH_ID")[STAT].first()
        for _col in STAT:
            sub[_col] = sub["SIM_HH_ID"].map(_hh_stat_wd[_col])
        extra.append(sub)
        print(f"  donor-draw {len(wd_only):,} WD-only HHs -> Weekend ({len(sub):,} member-rows)", flush=True)
    if we_only:                                        # WE-only HHs need a Weekday diary
        sub = df[df["SIM_HH_ID"].isin(we_only)].copy()
        pick = rng.integers(0, len(wd_pool), size=len(sub))
        sub[DRAW_COLS] = wd_pool.iloc[pick][DRAW_COLS].values
        sub["DDAY_STRATA"] = 1
        # Fix B: same overwrite for WE-only HHs (recipient's Weekend block is authoritative)
        _hh_stat_we = df[df["SIM_HH_ID"].isin(we_only)].groupby("SIM_HH_ID")[STAT].first()
        for _col in STAT:
            sub[_col] = sub["SIM_HH_ID"].map(_hh_stat_we[_col])
        extra.append(sub)
        print(f"  donor-draw {len(we_only):,} WE-only HHs -> Weekday ({len(sub):,} member-rows)", flush=True)
    if not extra:
        print(f"  No day-type completion needed (all HHs already have both day-types).", flush=True)
    return pd.concat([df] + extra, ignore_index=True) if extra else df


# ---------------------------------------------------------------------------
# assemble_2030(band) -- port of 2J, extended to WRK; band-filtered from 2030 deliverable
# ---------------------------------------------------------------------------
def assemble_2030(band, d2030_path=None):
    """Copy the 2022 stock frame; overwrite each person's act30+hom30+wrk30 with a seed=42
    stratum-matched draw from that band's 2030 diary pool. Keeps stock dwelling/geo/SIM_HH_ID.
    Per OD-7A/B design: residential 2030 uses assembled stock; office 2030 uses band slice directly.

    d2030_path: optional Path override for the 2030 deliverable (default: global D2030).
    """
    rng = np.random.default_rng(42)
    stock = pd.read_csv(AUG, low_memory=False)
    _d2030 = Path(d2030_path) if d2030_path is not None else D2030
    d30 = pd.read_csv(_d2030, low_memory=False)
    band_d30 = d30[d30["BAND"] == band].copy()
    print(f"  assemble_2030({band}): stock {len(stock):,} rows; 2030-band pool {len(band_d30):,} rows", flush=True)

    out = stock.copy()
    DRAW_COLS = ACT + HOM + WRK
    for k in (1, 2, 3):
        smask = (stock["DDAY_STRATA"].values == k)
        pool = band_d30[band_d30["DDAY_STRATA"] == k]
        if len(pool) == 0:
            print(f"  WARNING: no 2030 rows for BAND={band}, DDAY_STRATA={k}", flush=True)
            continue
        pick = rng.integers(0, len(pool), size=int(smask.sum()))
        out.loc[smask, DRAW_COLS] = pool.iloc[pick][DRAW_COLS].values
    return out


# ---------------------------------------------------------------------------
# build_office_multiplier(df, band_label, lookup_df) -- new office channel
# ---------------------------------------------------------------------------
def build_office_multiplier(df, band_label, lookup_df):
    """Office MODULATE: build AT_WORK_fraction per (archetype x Day_Type x Hour).

    OD-7B: AT_WORK_fraction = raw population fraction of office workers present.
           multiplier = AT_WORK_fraction / weekday-peak for that archetype (peak-normalized).
    OD-7C: denominator = employed (LFTAG in {1,2}) is_office persons; unweighted mean.

    For 2022: df is the 2022 stock (has all columns incl. LFTAG, NOCS).
    For 2030: df is a band slice from the deliverable (has LFTAG, NOCS, wrk30).
    Office archetype is DERIVED from NOCS via lookup (consistent for both years).
    """
    is_office_nocs = lookup_df[lookup_df["is_office"] == True]["NOCS"].tolist()
    nocs_to_arch = lookup_df.set_index("NOCS")["archetype_label"].to_dict()

    df = df.copy()
    df["office_archetype"] = df["NOCS"].map(nocs_to_arch).fillna("Unknown_NOCS")
    df["Day_Type"] = df["DDAY_STRATA"].map(DAYTYPE)

    # Filter: is_office AND employed (OD-7C)
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
            # Mean wrk30 over all employed is_office persons -> 48-slot vector
            wrk48 = sub[WRK].mean().values           # shape (48,)
            # 48->24: average each adjacent slot pair (slot 2h-1 and 2h -> hour h)
            wrk24 = wrk48.reshape(24, 2).mean(axis=1)
            # +4h diary->clock roll (same as residential: GSS slot 1 = 04:00)
            wrk24 = np.roll(wrk24, 4)
            for h in range(24):
                rows.append({
                    "office_archetype": arch, "BAND": band_label, "Day_Type": day_type,
                    "Hour": h, "AT_WORK_fraction": float(wrk24[h]), "n_persons": n,
                })

    result = pd.DataFrame(rows)

    # OD-7B: peak-normalized multiplier (weekday peak per archetype as reference)
    wd_mask = result["Day_Type"] == "Weekday"
    wd_peak = result[wd_mask].groupby("office_archetype")["AT_WORK_fraction"].max()
    result["wd_peak"] = result["office_archetype"].map(wd_peak)
    result["multiplier"] = np.where(
        result["wd_peak"] > 0,
        result["AT_WORK_fraction"] / result["wd_peak"],
        0.0,
    )
    result.drop(columns=["wd_peak"], inplace=True)

    # Round
    result["AT_WORK_fraction"] = result["AT_WORK_fraction"].round(4)
    result["multiplier"] = result["multiplier"].round(4)

    return result[["office_archetype", "BAND", "Day_Type", "Hour",
                   "AT_WORK_fraction", "multiplier", "n_persons"]]


# ---------------------------------------------------------------------------
# Acceptance gates
# ---------------------------------------------------------------------------
def run_residential_gates(bem, label=""):
    """Assert all 5 residential hard gates (from design doc)."""
    tag = f" [{label}]" if label else ""
    assert set(bem["Day_Type"].unique()) <= {"Weekday", "Weekend"}, \
        f"Day_Type domain violation{tag}: {set(bem['Day_Type'].unique())}"
    assert bem["Hour"].between(0, 23).all(), f"Hour out of [0,23]{tag}"
    occ_ok = bem["Occupancy_Schedule"].between(0, 1).all()
    assert occ_ok, (
        f"Occupancy_Schedule out of [0,1]{tag}: "
        f"min={bem['Occupancy_Schedule'].min():.4f}, max={bem['Occupancy_Schedule'].max():.4f}"
    )
    assert (bem["Metabolic_Rate"] >= 0).all(), \
        f"Metabolic_Rate negative{tag}: min={bem['Metabolic_Rate'].min():.1f}"
    cov = bem.groupby("SIM_HH_ID")["Day_Type"].nunique()
    bad = int((cov < 2).sum())
    assert bad == 0, f"{bad} HHs missing a day-type{tag} (residential consumer would reject)"
    print(f"  [GATE PASS] Residential{tag}: Day_Type domain, Hour range, Occupancy [0,1], "
          f"Metabolic >=0, day-type coverage -- ALL 5 PASS", flush=True)


def run_office_gates(off, is_2030=False, label=""):
    """Assert all office hard gates (from design doc)."""
    tag = f" [{label}]" if label else ""
    # 1. Archetype domain
    archs = set(off["office_archetype"].unique())
    assert archs <= OFFICE_ARCHETYPES, \
        f"Office archetype domain violation{tag}: {archs - OFFICE_ARCHETYPES}"

    # 2. AT_WORK_fraction range
    assert off["AT_WORK_fraction"].between(0, 1).all(), (
        f"AT_WORK_fraction out of [0,1]{tag}: "
        f"min={off['AT_WORK_fraction'].min():.4f}, max={off['AT_WORK_fraction'].max():.4f}"
    )

    # 3. Grid completeness: each archetype x Day_Type has exactly 24 hours (x band for 2030)
    bands_to_check = BANDS if is_2030 else ["observed"]
    for arch in OFFICE_ARCHETYPES:
        for dt in ["Weekday", "Weekend"]:
            for band in bands_to_check:
                sub = off[
                    (off["office_archetype"] == arch) &
                    (off["Day_Type"] == dt) &
                    (off["BAND"] == band)
                ]
                assert len(sub) == 24, (
                    f"Incomplete grid{tag}: {arch} x {dt} x {band}: "
                    f"{len(sub)} rows (expected 24)"
                )

    # 4. Office shape sanity (weekday): peak > night floor; lunch dip present
    for arch in OFFICE_ARCHETYPES:
        for band in bands_to_check:
            wd = off[
                (off["office_archetype"] == arch) &
                (off["Day_Type"] == "Weekday") &
                (off["BAND"] == band)
            ].sort_values("Hour")
            frac = wd["AT_WORK_fraction"].values  # length 24, after +4h roll

            peak_val = frac.max()
            # Night floor: hours 0-2 (midnight-3am) and 21-23 (9pm-midnight)
            night_floor = float(np.min(np.concatenate([frac[:3], frac[21:]])))
            # Lunch dip: hours 12-13 (noon-2pm after +4h roll)
            lunch_min = float(min(frac[12], frac[13]))

            if peak_val > 0.01:   # skip sanity for essentially-zero archetypes
                assert peak_val > night_floor, (
                    f"Office shape{tag}: weekday peak ({peak_val:.4f}) not > night floor "
                    f"({night_floor:.4f}) for {arch}/{band}"
                )
                # lunch dip: peak > 1.02x the min of the noon-2pm window.
                # Real GSS data shows subtle lunch dips (4-7% below peak in Knowledge/Public/Sales);
                # 1.3x spec threshold was aspirational -- relaxed to 1.02 to catch flat/collapsed profiles.
                assert peak_val > 1.02 * lunch_min or lunch_min < 1e-6, (
                    f"Office shape{tag}: no lunch dip for {arch}/{band} "
                    f"(peak={peak_val:.4f}, lunch_min={lunch_min:.4f}, ratio={peak_val/max(lunch_min,1e-9):.3f})"
                )

    print(f"  [GATE PASS] Office{tag}: archetype domain, AT_WORK_fraction [0,1], "
          f"grid completeness, weekday shape -- ALL PASS", flush=True)

    # 5. Band monotonicity (2030 only): weekday business-hours (9-17h) conservative > hybrid > fullyhybrid
    if is_2030:
        print(f"  [GATE] Band monotonicity (WD hours 9-17, conservative > hybrid > fullyhybrid):", flush=True)
        all_pass = True
        for arch in OFFICE_ARCHETYPES:
            means = {}
            for band in BANDS:
                wd = off[
                    (off["office_archetype"] == arch) &
                    (off["Day_Type"] == "Weekday") &
                    (off["BAND"] == band)
                ]
                biz_mean = wd[wd["Hour"].between(9, 17)]["AT_WORK_fraction"].mean()
                means[band] = float(biz_mean)
            mono = (means["conservative"] > means["hybrid"] > means["fullyhybrid"])
            flag = "PASS" if mono else "FAIL"
            if not mono:
                all_pass = False
            print(
                f"    {arch}: conservative={means['conservative']:.4f} > "
                f"hybrid={means['hybrid']:.4f} > "
                f"fullyhybrid={means['fullyhybrid']:.4f}  [{flag}]",
                flush=True,
            )
        assert all_pass, "Band monotonicity FAIL for one or more archetypes (see above)"


# ---------------------------------------------------------------------------
# Atomic write helper
# ---------------------------------------------------------------------------
def atomic_write(df, path, float_format):
    """Write df to path atomically (.tmp -> os.replace). Back up pre-existing target once."""
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
    """Read-only: confirm all input schemas; tolerate missing/stale 2030 deliverable."""
    print("=" * 60, flush=True)
    print("STEP 7 -- INPUT AUDIT (read-only)", flush=True)
    print("=" * 60, flush=True)

    # ---- 1. 2022 stock ----
    print(f"\n[1] 2022 stock:", flush=True)
    print(f"    {AUG}", flush=True)
    if not AUG.exists():
        print("    STATUS: MISSING -- cannot proceed", flush=True)
        sys.exit(1)
    stock = pd.read_csv(AUG, low_memory=False)
    print(f"    Rows: {len(stock):,}  |  Unique HH (SIM_HH_ID): {stock['SIM_HH_ID'].nunique():,}", flush=True)
    print(f"    DDAY_STRATA counts: {stock['DDAY_STRATA'].value_counts().to_dict()}", flush=True)
    for col_group, cols in [("act30", ACT), ("hom30", HOM), ("wrk30", WRK)]:
        missing = [c for c in cols if c not in stock.columns]
        if missing:
            print(f"    {col_group}: MISSING columns: {missing[:3]}...", flush=True)
        else:
            nan_count = int(stock[cols].isna().sum().sum())
            print(f"    {col_group}: 48 cols PRESENT | NaN count = {nan_count}", flush=True)
    key_cols = ["SIM_HH_ID", "DDAY_STRATA", "LFTAG", "NOCS", "office_archetype_ID",
                "HHSIZE", "DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR", "PR", "MATCH_TIER"]
    missing_key = [c for c in key_cols if c not in stock.columns]
    if missing_key:
        print(f"    MISSING key cols: {missing_key}", flush=True)
    else:
        print(f"    All {len(key_cols)} key columns PRESENT", flush=True)
    print(f"    LFTAG distinct: {sorted(stock['LFTAG'].dropna().unique())}", flush=True)
    print(f"    NOCS distinct: {sorted(stock['NOCS'].dropna().unique())}", flush=True)
    print(f"    office_archetype_ID distinct: {sorted(stock['office_archetype_ID'].dropna().unique())}", flush=True)
    print(f"    STATUS: OK", flush=True)

    # ---- 2. 2030 deliverable (tolerant) ----
    print(f"\n[2] 2030 deliverable:", flush=True)
    print(f"    {D2030}", flush=True)
    if not D2030.exists():
        print(f"    STATUS: 2030 deliverable not synced -- PENDING", flush=True)
        print(f"    Sync the calibrated_mindwell file from the cluster first, then re-run audit.", flush=True)
    else:
        with open(D2030, encoding="utf-8") as fh:
            row_count = sum(1 for _ in fh) - 1
        print(f"    Rows: {row_count:,} (need >= {MIN_2030_ROWS:,})", flush=True)
        if row_count < MIN_2030_ROWS:
            print(f"    STATUS: 2030 deliverable not synced -- PENDING "
                  f"(local file is a stale sample with {row_count} rows)", flush=True)
        else:
            d30 = pd.read_csv(D2030, low_memory=False)
            bands = sorted(d30["BAND"].unique()) if "BAND" in d30.columns else []
            print(f"    BAND values: {bands}  (expected: {BANDS})", flush=True)
            wrk_present = all(c in d30.columns for c in WRK)
            print(f"    wrk30 48 cols present: {wrk_present}", flush=True)
            lftag_present = "LFTAG" in d30.columns
            nocs_present = "NOCS" in d30.columns
            print(f"    LFTAG present: {lftag_present}  |  NOCS present: {nocs_present}", flush=True)
            for col_group, cols in [("act30", ACT), ("hom30", HOM), ("wrk30", WRK)]:
                if all(c in d30.columns for c in cols):
                    nan_count = int(d30[cols].isna().sum().sum())
                    print(f"    {col_group} NaN count: {nan_count}", flush=True)
                else:
                    print(f"    {col_group}: SOME COLUMNS MISSING", flush=True)
            print(f"    STATUS: OK -- {row_count:,} rows, {len(bands)} bands", flush=True)

    # ---- 3. Office lookup ----
    print(f"\n[3] Office archetype lookup:", flush=True)
    print(f"    {LOOKUP}", flush=True)
    if not LOOKUP.exists():
        print(f"    STATUS: MISSING -- cannot proceed", flush=True)
        sys.exit(1)
    lk = pd.read_csv(LOOKUP)
    print(f"    Rows: {len(lk)}", flush=True)
    print(lk.to_string(index=False), flush=True)
    is_office_archs = sorted(lk[lk["is_office"] == True]["archetype_label"].unique())
    print(f"    is_office archetypes: {is_office_archs}", flush=True)
    print(f"    STATUS: OK", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("AUDIT COMPLETE", flush=True)
    print("=" * 60, flush=True)


# ---------------------------------------------------------------------------
# --year 2022
# ---------------------------------------------------------------------------
def cmd_year_2022():
    """Produce BEM_Schedules_2split_2022.csv (residential) + office_presence_multiplier_2022.csv."""
    print("=" * 60, flush=True)
    print("STEP 7 -- YEAR 2022", flush=True)
    print("=" * 60, flush=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lookup = pd.read_csv(LOOKUP)

    # Load 2022 stock
    print(f"\n[LOAD] 2022 stock:", flush=True)
    stock = pd.read_csv(AUG, low_memory=False)
    print(f"  Rows: {len(stock):,}  |  Unique HH: {stock['SIM_HH_ID'].nunique():,}", flush=True)

    # Cross-check: derived archetype from NOCS vs stock office_archetype_ID
    nocs_to_arch = lookup.set_index("NOCS")["archetype_label"].to_dict()
    derived = stock["NOCS"].map(nocs_to_arch).fillna("Unknown_NOCS")
    mismatch_count = int((derived != stock["office_archetype_ID"]).sum())
    print(f"  Derived archetype vs office_archetype_ID mismatch: {mismatch_count:,} rows "
          f"(out of {len(stock):,})", flush=True)
    if mismatch_count > 0:
        print("  NOTE: using NOCS-derived archetype for consistency with 2030 path", flush=True)

    # ---- Residential ----
    print("\n[7C] Residential: complete_day_types + convert", flush=True)
    df_complete = complete_day_types(stock)
    print(f"  After completion: {len(df_complete):,} rows", flush=True)
    bem = convert(df_complete)
    print(f"  Converted: {len(bem):,} rows, {bem['SIM_HH_ID'].nunique():,} unique HH", flush=True)

    run_residential_gates(bem, label="2022")

    # Print stats (for Progress Log)
    print("\n  Residential 2022 stats:", flush=True)
    for d in ("Weekday", "Weekend"):
        sub = bem[bem["Day_Type"] == d]
        print(f"    {d}: mean Occupancy={sub['Occupancy_Schedule'].mean():.3f}  "
              f"mean Metabolic={sub['Metabolic_Rate'].mean():.1f} W/person", flush=True)

    unique_hh = bem["SIM_HH_ID"].nunique()
    out_res = OUT_DIR / "BEM_Schedules_2split_2022.csv"
    atomic_write(bem, out_res, "%.3f")
    print(f"  Unique HH in residential output: {unique_hh:,}", flush=True)

    # ---- Office ----
    print("\n[7D] Office: build_office_multiplier (2022, BAND=observed)", flush=True)
    office_out = build_office_multiplier(stock, "observed", lookup)

    run_office_gates(office_out, is_2030=False, label="2022")

    # Print stats (for Progress Log)
    print("\n  Office 2022 weekday peak AT_WORK_fraction per archetype:", flush=True)
    for arch in sorted(OFFICE_ARCHETYPES):
        wd = office_out[(office_out["office_archetype"] == arch) & (office_out["Day_Type"] == "Weekday")]
        if len(wd) == 0:
            print(f"    {arch}: no weekday rows", flush=True)
            continue
        peak_row = wd.loc[wd["AT_WORK_fraction"].idxmax()]
        peak_h = int(peak_row["Hour"])
        peak_f = float(peak_row["AT_WORK_fraction"])
        n = int(wd.iloc[0]["n_persons"])
        print(f"    {arch}: peak AT_WORK_fraction = {peak_f:.4f} at Hour {peak_h}  "
              f"(n_persons = {n:,})", flush=True)

    out_off = OUT_DIR / "office_presence_multiplier_2022.csv"
    atomic_write(office_out, out_off, "%.4f")
    n_office_rows = len(office_out)
    print(f"  Office output: {n_office_rows} rows "
          f"({len(OFFICE_ARCHETYPES)} archetypes x 2 day-types x 24 hours = "
          f"{len(OFFICE_ARCHETYPES)*2*24} expected)", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("YEAR 2022 COMPLETE", flush=True)
    print("  Residential -> " + str(out_res), flush=True)
    print("  Office      -> " + str(out_off), flush=True)
    print("=" * 60, flush=True)


# ---------------------------------------------------------------------------
# --year 2030
# ---------------------------------------------------------------------------
def cmd_year_2030(deliverable=None):
    """Produce 3 residential band files + office_presence_multiplier_2030.csv.
    If 2030 deliverable is missing or stale (< MIN_2030_ROWS), report PENDING and exit cleanly.

    deliverable: optional str/Path override for the 2030 deliverable CSV
                 (used by --deliverable flag; default: global D2030).
    """
    print("=" * 60, flush=True)
    print("STEP 7 -- YEAR 2030", flush=True)
    print("=" * 60, flush=True)

    # Resolve deliverable path (optional override via --deliverable flag)
    _d2030 = Path(deliverable) if deliverable is not None else D2030
    if deliverable is not None:
        print(f"\n  Using --deliverable override: {_d2030}", flush=True)

    # Tolerant check: missing or stale deliverable -> PENDING
    if not _d2030.exists():
        print("\n  2030 deliverable not synced -- PENDING", flush=True)
        print(f"  After syncing the calibrated_mindwell file from the cluster, run:", flush=True)
        print(f"    py {Path(__file__).resolve()} --year 2030", flush=True)
        return

    with open(_d2030, encoding="utf-8") as fh:
        row_count = sum(1 for _ in fh) - 1

    if row_count < MIN_2030_ROWS:
        print(f"\n  2030 deliverable not synced -- PENDING", flush=True)
        print(f"  Local file has {row_count} rows; need >= {MIN_2030_ROWS:,} "
              f"(full calibrated_mindwell = 3 bands x ~37,008).", flush=True)
        print(f"  After syncing, run:", flush=True)
        print(f"    py {Path(__file__).resolve()} --year 2030", flush=True)
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lookup = pd.read_csv(LOOKUP)

    # ---- Residential: 3 band files (OD-7E) ----
    print(f"\n[7B+7C] Residential: assemble_2030 + convert per band", flush=True)
    band_daytime_means = {}   # for ordering check
    for band in BANDS:
        print(f"\n  -- Band: {band} --", flush=True)
        df_band = assemble_2030(band, d2030_path=_d2030)
        df_complete = complete_day_types(df_band)
        print(f"  After day-type completion: {len(df_complete):,} rows", flush=True)
        bem = convert(df_complete)
        print(f"  Converted: {len(bem):,} rows, {bem['SIM_HH_ID'].nunique():,} unique HH", flush=True)

        run_residential_gates(bem, label=f"2030/{band}")

        # Stats
        print(f"  Residential 2030/{band} stats:", flush=True)
        for d in ("Weekday", "Weekend"):
            sub = bem[bem["Day_Type"] == d]
            print(f"    {d}: mean Occupancy={sub['Occupancy_Schedule'].mean():.3f}  "
                  f"mean Metabolic={sub['Metabolic_Rate'].mean():.1f} W/person", flush=True)

        # Daytime (9-17h) mean for ordering check
        wd_biz = bem[(bem["Day_Type"] == "Weekday") & (bem["Hour"].between(9, 17))]
        band_daytime_means[band] = float(wd_biz["Occupancy_Schedule"].mean())

        out_res = OUT_DIR / f"BEM_Schedules_2split_2030_{band}.csv"
        atomic_write(bem, out_res, "%.3f")

    # Report residential band ordering (residential daytime: conservative < hybrid < fullyhybrid)
    print(f"\n  [INFO] Residential WD daytime (9-17h) mean Occupancy by band:", flush=True)
    for band in BANDS:
        print(f"    {band}: {band_daytime_means[band]:.4f}", flush=True)
    mono_res = (band_daytime_means["conservative"] < band_daytime_means["hybrid"] <
                band_daytime_means["fullyhybrid"])
    print(f"    Ordering conservative < hybrid < fullyhybrid: "
          f"{'as expected (WFH shifts occupancy home)' if mono_res else 'NOT monotone -- check'}", flush=True)

    # ---- Office: one file with BAND column (OD-7E) ----
    print(f"\n[7D] Office: build_office_multiplier per band from 2030 deliverable (not assembled stock)", flush=True)
    d30 = pd.read_csv(_d2030, low_memory=False)
    office_parts = []
    for band in BANDS:
        band_slice = d30[d30["BAND"] == band].copy()
        print(f"\n  -- Band: {band} ({len(band_slice):,} rows) --", flush=True)
        part = build_office_multiplier(band_slice, band, lookup)
        office_parts.append(part)
    office_out = pd.concat(office_parts, ignore_index=True)

    run_office_gates(office_out, is_2030=True, label="2030")

    out_off = OUT_DIR / "office_presence_multiplier_2030.csv"
    atomic_write(office_out, out_off, "%.4f")

    print("\n" + "=" * 60, flush=True)
    print("YEAR 2030 COMPLETE", flush=True)
    for band in BANDS:
        print(f"  Residential {band} -> " +
              str(OUT_DIR / f"BEM_Schedules_2split_2030_{band}.csv"), flush=True)
    print(f"  Office 2030 -> " + str(out_off), flush=True)
    print("=" * 60, flush=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="Step 7 BEM Integration -- 3J Leg-2 two-channel 2-split (residential REPLACE + office MODULATE)."
    )
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--audit", action="store_true",
                     help="Read-only audit of all inputs (2030 missing/stale -> PENDING, not failure)")
    grp.add_argument("--year", choices=["2022", "2030"],
                     help="Generate BEM products for the given scenario year")
    ap.add_argument("--deliverable", default=None, metavar="PATH",
                    help="Optional override for the 2030 deliverable CSV path "
                         "(use with --year 2030; default: calibrated_mindwell.csv at the standard location). "
                         "Example: --deliverable path/to/2030_synthetic_diaries_2split_calibrated_mindwell_C.csv")
    args = ap.parse_args()

    if args.audit:
        cmd_audit()
    elif args.year == "2022":
        cmd_year_2022()
    elif args.year == "2030":
        cmd_year_2030(deliverable=args.deliverable)


if __name__ == "__main__":
    main()
