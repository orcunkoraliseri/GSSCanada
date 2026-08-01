#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3J Leg-3 -- Step 9X : envelope-exposure mechanism test (T9-3 / S9D-3).

READ-ONLY. Never edits, re-simulates, or re-aggregates anything. Iterates the 56 finished
campaign cells ONE AT A TIME -- opens a fresh sqlite3 connection per cell and closes it before
moving on, never holds more than one cell's small metadata tables in memory. The campaign tree
is ~22 GB on a machine that cannot be rebooted remotely (see CLAUDE.md); this script only reads
`injected.idf` (via eppy, for the Tag-2 zone classification) and the small `Zones` / `Surfaces` /
`TabularDataWithStrings` tables of each `run/eplusout.sql` -- never the hourly `ReportData`
series, never more than one cell's SQL file open at a time.

WHY THIS SCRIPT EXISTS
----------------------
Step 9 found 3 FAIL: the measured EUI of the office/retail/hotel channels of this mixed tower
sits BELOW the floor of each channel's "freestanding prototype" band (office 71.1 vs [100,200],
retail 75.4 vs [80,155], hotel 178.3 vs [180,300], all CFA basis, base = as-modelled).
S9D-1 proposes to retire that band from the PASS/FAIL role for these three channels because they
are STACKED FLOORS inside one tower: almost all of their envelope faces other conditioned
volumes (interior partitions), not real exterior wall/roof/slab-on-grade. S9D-3 refuses to accept
that story on say-so -- "an ordering noticed only after the fact is not evidence" -- and demands
a falsifiable, independently measured test: if the "stacked channel" explanation is physically
real, the channel with the LEAST envelope exposure per m2 of floor should show the LARGEST
negative gap to its band floor, and the channel with the MOST exposure should show the smallest
gap. This script measures `exposure_ratio` per channel per cell so that ordering can actually be
checked instead of assumed. It does not write the `S9-EUI-EXPOSURE` gate itself -- that belongs
in `3rdJ_09_activityDrivenLoads_4split.py`, out of scope for this task -- it produces the
measurement the gate would consume, plus the correlation check the task asked for directly.

PREDICTION -- written 2026-07-31, BEFORE this script was ever executed
-----------------------------------------------------------------------
The already-observed (after-the-fact, V2) ordering of the *relative gap to the band floor* is:
    office -29 %  <  retail -6 %  <  hotel -1 %          (most negative -> least negative)
The stacked-channel explanation makes an INDEPENDENT, previously unmeasured claim about a
DIFFERENT quantity -- envelope exposure -- and predicts that its ordering across these same three
channels reproduces the same rank:
    exposure_ratio(office)  <  exposure_ratio(retail)  <  exposure_ratio(hotel)
i.e. office is the most deeply buried channel of the three band-carrying channels (repeating
open-plan floors stacked between other office floors, almost no true facade per m2 of CFA),
hotel is the least buried of the three (guest-room floors carry perimeter glazing on most of
their exterior wall and this stock's hotel floors sit nearer the building envelope's actual
extremities), retail in between. Consequently the Spearman rank correlation between
`exposure_ratio` and the SIGNED relative gap to the band floor, computed per cell across these
three channels, is predicted POSITIVE, and its sign is predicted to be consistent across the
SuperTall/Tall x CLG/MTL 2x2 grid of building x city.

This paragraph is not edited after the run to match whatever the numbers turn out to be. If the
measured order or the correlation sign comes out differently, THAT is the result -- see the
"VERDICT" block printed at the end of this script's run, and the repo's Defaut-1-style rule
against post-hoc "expected" orderings (an order noticed only after the fact proves nothing).

METHOD
------
Per cell, per channel:
    ext_area_m2    = sum of NET `Area` (opaque walls/roofs/floors AND windows, uniformly -- the
                     `Area` column is already net of sub-surface openings, so summing it across
                     ALL surface classes gives the true non-double-counting total; the `GrossArea`
                     column embeds the window footprint a second time and must NOT also have
                     window `Area` added on top of it -- verified empirically below) x the
                     zone's `Multiplier`, restricted to `ExtBoundCond == 0` (EnergyPlus's
                     "ExternalEnvironment" / Outdoors code).
    ground_area_m2 = same, restricted to `ExtBoundCond < 0` (EnergyPlus's negative special
                     codes -- Ground, GroundFCfactorMethod/OtherSideConditionsModel, etc. --
                     confirmed empirically per V-below to be exactly {-1, -5} in this campaign's
                     EnergyPlus build, and none of them collide with the positive self- or
                     adjacent-surface-index codes used for Adiabatic/interior partitions).
    cfa_m2         = channel Conditioned Floor Area, via the imported, UN-modified
                     `parse_channel_areas()` from Step 8E (single source of truth for the
                     zone -> channel map and the CFA convention; not reimplemented here).
    exposure_ratio = (ext_area_m2 + ground_area_m2) / cfa_m2

Zone -> channel classification reuses Step 8E's `FINE_TO_AGG` table and
`eSim_bem_utils.commercial_integration.classify_tag2()` UNCHANGED, imported via
`importlib.util.spec_from_file_location` (the filename `3rdJ_08E_aggregate_4split.py` is not a
valid Python module name). The only code NOT imported from 08E is the ~10-line loop that walks
`SPACE` objects to build a `zone_name -> channel` dict from `Tag_2` -- 08E does not expose that
mapping as its own function, only bundled inside `parse_channel_areas()` -- so this script
repeats that small piece of GLUE using the imported table and classifier, never re-deriving the
Tag-2 classification itself. This is the "one source of truth" rule from the Step-8 defect list.

VALIDATION OF THE PARSING METHOD (empirical, done before writing this docstring's final form)
-----------------------------------------------------------------------------------------------
On cell `B_central__SuperTall__CLG`:
  * `ExtBoundCond == 0` reproduces EnergyPlus's own per-zone "Exterior Gross Wall Area" and
    "Exterior Window Area" (`eplusout.eio`, `Zone Information` lines) exactly, 0 mismatches
    across all 256 zones.
  * `ExtBoundCond` values {-1, -5} exactly match the IDF's own count of surfaces whose
    `Outside Boundary Condition` text is `Ground` (7) and `GroundFCfactorMethod` (18)
    respectively; every other surface (partitions, Adiabatic) carries a POSITIVE ExtBoundCond
    (a self- or adjacent-surface-index reference), never negative and never 0.
  * Summing `Area x Multiplier` over `ExtBoundCond IN (0,-1,-5)` across ALL surface classes
    (opaque + windows, uniformly) reproduces EnergyPlus's own independently-computed
    `EnvelopeSummary / Opaque Exterior / Gross Area` column total (which already embeds each
    wall's window footprint) to 0.0003 % -- confirming both the boundary-condition decode and
    the zone-Multiplier convention (areas in `Surfaces`/`Zones` are per-instance, not
    pre-multiplied, exactly like `Zones.FloorArea` in Step 8E).

USAGE
-----
    py -3 3rdJ_09X_envelope_exposure.py [--campaign-dir <dir>] [--outdir <dir>]
                                        [--eplus-idd <path>]
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sqlite3
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
LEG3_DIR = os.path.abspath(os.path.join(HERE, ".."))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DEFAULT_CAMPAIGN_DIR = os.path.join(
    LEG3_DIR, "Step8_docs", "campaign_local_v2", "campaign_cf69d508")
DEFAULT_OUTDIR = os.path.join(HERE, "outputs_step9")
DEFAULT_EPLUS_IDD = r"C:\EnergyPlusV24-2-0\Energy+.idd"
EIGHT_E_PATH = os.path.join(LEG3_DIR, "Step8_docs", "3rdJ_08E_aggregate_4split.py")
EUI_BY_CHANNEL_CSV = os.path.join(DEFAULT_OUTDIR, "step9_eui_by_channel.csv")

BANDED_CHANNELS = ["office", "retail", "hotel"]           # carry a freestanding-prototype band
CONTEXT_CHANNEL = "residential"                            # SHEU context only, no as-modelled band


def _load_08e_module():
    """Import 3rdJ_08E_aggregate_4split.py by path (its name is not a valid module identifier)."""
    spec = importlib.util.spec_from_file_location("step8e_aggregate_4split", EIGHT_E_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _zone_to_channel(injected_idf: str, eplus_idd: str, fine_to_agg: dict, classify_tag2) -> dict:
    """Zone name (upper) -> aggregate channel, via Step 8E's imported table/classifier ONLY.

    Mirrors the SPACE-walking loop inside `parse_channel_areas()` (08E does not expose it as a
    standalone function) so this script can also attribute Surfaces-table rows to a channel.
    The classification itself (`fine_to_agg`, `classify_tag2`) is imported, never reimplemented.
    """
    from eppy.modeleditor import IDF

    IDF.setiddname(eplus_idd)  # no-op if already set to this same path (eppy contract)
    idf = IDF(injected_idf)
    zone_to_channel = {}
    for sp in idf.idfobjects.get("SPACE", []):
        tag2 = ""
        for f in ("Tag_2", "Space_Type_Name", "Space_Type", "Name"):
            v = str(getattr(sp, f, "") or "").strip()
            if v:
                tag2 = v
                break
        agg = fine_to_agg.get(classify_tag2(tag2))
        zn = str(getattr(sp, "Zone_Name", "") or "").strip().upper()
        if agg and zn:
            zone_to_channel[zn] = agg
    del idf
    return zone_to_channel


def _read_surfaces_and_zones(sql_path: str) -> pd.DataFrame:
    """Small metadata tables ONLY -- never the hourly ReportData series."""
    conn = sqlite3.connect(f"file:{sql_path}?mode=ro", uri=True)
    try:
        surf = pd.read_sql_query(
            "SELECT SurfaceName, ClassName, ExtBoundCond, ZoneIndex, Area "
            "FROM Surfaces WHERE ClassName != 'Internal Mass'", conn)
        zone = pd.read_sql_query(
            "SELECT ZoneIndex, ZoneName, Multiplier FROM Zones", conn)
    finally:
        conn.close()
    surf = surf.merge(zone, on="ZoneIndex", how="left")
    surf["ZONE_KEY"] = surf["ZoneName"].astype(str).str.strip().str.upper()
    surf["area_total"] = surf["Area"].astype(float) * surf["Multiplier"].astype(float)
    return surf


def _read_envelope_summary_total(sql_path: str) -> float | None:
    """Independent, EnergyPlus-computed total exterior+ground envelope area (control #2).

    `EnvelopeSummary / Opaque Exterior / Gross Area`, summed over all real surfaces (the
    "Total or Average" / "North Total or Average" / "Non-North Total or Average" rows are
    EXCLUDED -- they are E+'s own subtotal rows and summing them in would triple-count, which is
    exactly the bug this script's author hit and fixed while validating the method above).
    `Gross Area` for a wall already includes any window cut into it, so this single column is
    the correct non-double-counting total; `Exterior Fenestration` must NOT be added on top.
    """
    conn = sqlite3.connect(f"file:{sql_path}?mode=ro", uri=True)
    try:
        env = pd.read_sql_query(
            "SELECT RowName, Value FROM TabularDataWithStrings "
            "WHERE ReportName='EnvelopeSummary' AND TableName='Opaque Exterior' "
            "AND ColumnName='Gross Area'", conn)
    except Exception:
        return None
    finally:
        conn.close()
    if env.empty:
        return None
    env = env[~env["RowName"].str.contains("Total|Average", case=False, na=False)]
    return float(pd.to_numeric(env["Value"], errors="coerce").fillna(0.0).sum())


def process_cell(cell_dir: str, mod, classify_tag2, eplus_idd: str) -> tuple[list[dict], dict]:
    """One cell, read-only, connection opened and closed within this call. Returns
    (list of per-channel row dicts, control-check dict)."""
    name = os.path.basename(cell_dir.rstrip("\\/"))
    idf_path = os.path.join(cell_dir, "injected.idf")
    sql_path = os.path.join(cell_dir, "run", "eplusout.sql")
    if not (os.path.isfile(idf_path) and os.path.isfile(sql_path)):
        print(f"  [skip] {name}: missing injected.idf or run/eplusout.sql")
        return [], {"cell_tag": name, "status": "skipped"}

    zone_to_channel = _zone_to_channel(idf_path, eplus_idd, mod.FINE_TO_AGG, classify_tag2)
    cfa = mod.parse_channel_areas(idf_path, sql_path, eplus_idd)

    surf = _read_surfaces_and_zones(sql_path)
    surf["channel"] = surf["ZONE_KEY"].map(zone_to_channel)

    ext = surf[surf["ExtBoundCond"] == 0]
    grd = surf[surf["ExtBoundCond"] < 0]

    ext_by_chan = ext.groupby("channel")["area_total"].sum()
    grd_by_chan = grd.groupby("channel")["area_total"].sum()

    rows = []
    for c in mod.CHANNELS:
        e = float(ext_by_chan.get(c, 0.0))
        g = float(grd_by_chan.get(c, 0.0))
        cfa_c = float(cfa.get(c, 0.0))
        ratio = (e + g) / cfa_c if cfa_c > 0 else float("nan")
        rows.append({
            "cell_tag": name, "channel": c,
            "ext_area_m2": e, "ground_area_m2": g,
            "cfa_m2": cfa_c, "exposure_ratio": ratio,
        })

    unclassified_area = float(surf.loc[surf["channel"].isna(), "area_total"].sum())
    total_mine = float(ext["area_total"].sum() + grd["area_total"].sum())
    env_total = _read_envelope_summary_total(sql_path)
    if env_total and env_total > 0:
        pct_diff = (total_mine - env_total) / env_total * 100.0
    else:
        pct_diff = None

    control = {
        "cell_tag": name, "status": "ok",
        "total_mine_m2": total_mine, "env_total_m2": env_total,
        "pct_diff": pct_diff, "unclassified_area_m2": unclassified_area,
    }
    flag = "" if (pct_diff is None or abs(pct_diff) <= 1.0) else "  <<< CONTROL FAIL (>1%)"
    print(f"  [{name}] total(mine)={total_mine:,.1f} m2  total(EnvelopeSummary)="
          f"{env_total if env_total is not None else float('nan'):,.1f} m2  "
          f"diff={pct_diff if pct_diff is not None else float('nan'):+.4f} %{flag}")
    return rows, control


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign-dir", default=DEFAULT_CAMPAIGN_DIR)
    ap.add_argument("--outdir", default=DEFAULT_OUTDIR)
    ap.add_argument("--eplus-idd", default=DEFAULT_EPLUS_IDD)
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    out_csv = os.path.join(args.outdir, "step9_envelope_exposure.csv")

    mod = _load_08e_module()
    from eSim_bem_utils.commercial_integration import classify_tag2  # same source 08E uses

    cell_names = sorted(
        d for d in os.listdir(args.campaign_dir)
        if os.path.isdir(os.path.join(args.campaign_dir, d)))
    print(f"3rdJ_09X_envelope_exposure -- {len(cell_names)} cells found under {args.campaign_dir}")

    all_rows: list[dict] = []
    controls: list[dict] = []
    for name in cell_names:
        cell_dir = os.path.join(args.campaign_dir, name)
        rows, control = process_cell(cell_dir, mod, classify_tag2, args.eplus_idd)
        all_rows.extend(rows)
        controls.append(control)

    df = pd.DataFrame(all_rows, columns=[
        "cell_tag", "channel", "ext_area_m2", "ground_area_m2", "cfa_m2", "exposure_ratio"])
    df.to_csv(out_csv, index=False)
    print(f"\nWrote {out_csv} ({len(df)} rows, {df['cell_tag'].nunique()} cells)")

    # ------------------------------------------------------------------ control #2 summary
    ctrl_df = pd.DataFrame(controls)
    ok = ctrl_df[ctrl_df["status"] == "ok"]
    print("\n=== CONTROL #2 -- independent total-envelope cross-check ===")
    if len(ok) and ok["pct_diff"].notna().any():
        print(f"  cells checked        : {len(ok)} / {len(cell_names)}")
        print(f"  max |pct diff|       : {ok['pct_diff'].abs().max():.4f} %")
        print(f"  median |pct diff|    : {ok['pct_diff'].abs().median():.4f} %")
        worst = ok.loc[ok["pct_diff"].abs().idxmax()]
        print(f"  worst cell           : {worst['cell_tag']} ({worst['pct_diff']:+.4f} %)")
    else:
        print("  NO cell produced a usable EnvelopeSummary total -- control could not run.")

    # ------------------------------------------------------------------ items 1 & 2 : medians
    print("\n=== exposure_ratio -- median across 56 cells, by channel ===")
    med_exp = df.groupby("channel")["exposure_ratio"].median().reindex(
        ["office", "retail", "hotel", "residential", "residential_common", "service_MEP"])
    print(med_exp.to_string())

    if not os.path.isfile(EUI_BY_CHANNEL_CSV):
        print(f"\n[WARN] {EUI_BY_CHANNEL_CSV} not found -- cannot compute band-floor gap or "
              f"correlation (items 2/3 of the deliverable). Exposure CSV is still written.")
        return

    eui = pd.read_csv(EUI_BY_CHANNEL_CSV)
    eui["floor"] = eui["band_lo"]
    resid_mask = eui["channel"] == CONTEXT_CHANNEL
    eui.loc[resid_mask, "floor"] = eui.loc[resid_mask, "info_lo"]  # SHEU context floor, labeled
    eui["gap_pct"] = (eui["eui_CFA_kWh_m2"] - eui["floor"]) / eui["floor"] * 100.0

    merged = df.merge(
        eui[["cell_tag", "channel", "building", "city", "eui_CFA_kWh_m2", "floor", "gap_pct"]],
        on=["cell_tag", "channel"], how="inner")

    print("\n=== gap-to-floor (%) -- median across 56 cells, by channel ===")
    print(merged.groupby("channel")["gap_pct"].median().reindex(
        ["office", "retail", "hotel", "residential"]).to_string())
    print("  (residential's 'floor' is the SHEU-2019 context band lower bound, info_lo -- it "
          "has no as-modelled prototype band; reported for context only, per the task.)")

    # ------------------------------------------------------------------ item 3 : correlation
    def per_cell_rho(sub: pd.DataFrame) -> float:
        sub = sub.dropna(subset=["exposure_ratio", "gap_pct"])
        if len(sub) < 3 or sub["exposure_ratio"].nunique() < 2 or sub["gap_pct"].nunique() < 2:
            return float("nan")
        rho, _ = spearmanr(sub["exposure_ratio"], sub["gap_pct"])
        return rho

    banded = merged[merged["channel"].isin(BANDED_CHANNELS)]
    rho_3 = banded.groupby("cell_tag").apply(per_cell_rho, include_groups=False)
    with_ctx = merged[merged["channel"].isin(BANDED_CHANNELS + [CONTEXT_CHANNEL])]
    rho_4 = with_ctx.groupby("cell_tag").apply(per_cell_rho, include_groups=False)

    print("\n=== CORRELATION VERDICT (Spearman, exposure_ratio vs signed gap-to-floor) ===")
    for label, rho_series in (("3 banded channels (office/retail/hotel)", rho_3),
                               ("+ residential as context point (4 pts)", rho_4)):
        valid = rho_series.dropna()
        frac_pos = float((valid > 0).mean()) if len(valid) else float("nan")
        print(f"  -- {label} --")
        print(f"     n cells with a defined rho : {len(valid)} / {rho_series.shape[0]}")
        print(f"     median rho                 : {valid.median() if len(valid) else float('nan'):.3f}")
        print(f"     fraction of cells rho > 0  : {frac_pos * 100:.1f} %")

    print("\n  -- sign consistency across the 4 building x city pairs (pooled per pair) --")
    pair_signs = {}
    for (building, city), sub in with_ctx.groupby(["building", "city"]):
        sub2 = sub.dropna(subset=["exposure_ratio", "gap_pct"])
        if len(sub2) >= 3 and sub2["exposure_ratio"].nunique() > 1 and sub2["gap_pct"].nunique() > 1:
            rho, _ = spearmanr(sub2["exposure_ratio"], sub2["gap_pct"])
        else:
            rho = float("nan")
        pair_signs[(building, city)] = rho
        print(f"     {building:>10s} x {city:<4s}: pooled rho = {rho:+.3f}  (n={len(sub2)})")
    signs = [np.sign(v) for v in pair_signs.values() if not np.isnan(v)]
    n_pos = sum(1 for s in signs if s > 0)
    print(f"     sign-consistent across all 4 pairs (all positive)?  "
          f"{'YES' if n_pos == 4 else f'NO ({n_pos}/4 positive)'}")

    print(f"\nRun completed {datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()
