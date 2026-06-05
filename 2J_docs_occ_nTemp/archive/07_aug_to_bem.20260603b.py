"""07_aug_to_bem.py — OP4 + Step 9: calibrated aug occupancy -> EnergyPlus BEM_Schedules_<year>.csv.
17-col hourly-household format eSim_bem_utils_2J/integration.py consumes.  BEM is 2-day-type
(Weekday/Weekend) per integration.py: DDAY_STRATA {1,2,3} -> {Weekday, Weekend=Sat+Sun}.
New Step-9 columns (additive, backward-compatible): Equipment_Fraction, Lighting_Fraction,
Equip_Design_W, Light_Design_W.  Predecessor archived at archive/07_aug_to_bem.20260603.py.
Run-from-anywhere, seed=42, reversible.  Usage:  py 07_aug_to_bem.py --year 2022 | --year 2030

ARCHIVE NOTE: this is the v1 Step-9 version (SingleD-only SHEU calibration targets).
Superseded by the per-DTYPE version; archived 2026-06-03 before apartment-target addition.
"""
import os, sys, argparse, shutil
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # ensure activity_loads importable
import activity_loads as _al
BASE = HERE.parent                         # GSSCanada-main/
AUG  = BASE/"0_Occupancy"/"Outputs_21CEN22GSS"/"aug_pipeline"/"21CEN22GSS_aug_Full_Aggregated_excl.csv"
D2030= BASE/"0_Occupancy"/"Outputs_21CEN22GSS"/"forecast_2030"/"2030_synthetic_diaries.csv"
BEMS = BASE/"BEM_Setup"

ACT = [f"act30_{i:03d}" for i in range(1,49)]
HOM = [f"hom30_{i:03d}" for i in range(1,49)]
STAT = ["HHSIZE","DTYPE","BEDRM","CONDO","ROOM","REPAIR","PR","MATCH_TIER"]
OUT_COLS = ["SIM_HH_ID","Day_Type","Hour","HHSIZE","DTYPE","BEDRM","CONDO","ROOM",
            "REPAIR","PR","MATCH_TIER","Occupancy_Schedule","Metabolic_Rate",
            "Equipment_Fraction","Lighting_Fraction","Equip_Design_W","Light_Design_W"]
# act code -> watts/person (BEMConverter.metabolic_map in 21CEN22GSS_occToBEM.py); unknown->100
MET = {0:0,1:125,2:175,3:190,4:195,5:70,6:105,7:170,8:110,9:90,10:85,11:245,12:105,13:140,14:135}
PR_LBL = {10:"Atlantic",11:"Atlantic",12:"Atlantic",13:"Atlantic",24:"Quebec",35:"Ontario",
          46:"Prairies",47:"Prairies",48:"Alberta",59:"BC",70:"Northern Canada"}
DAYTYPE = {1:"Weekday",2:"Weekend",3:"Weekend"}

def dtype_label(code, bedrm):
    if int(code)==2:                       # Apartment -> HighRise/MidRise by BEDRM (BEMConverter proxy)
        try: b=int(float(bedrm))
        except (ValueError,TypeError): b=2
        return "HighRise" if b<=1 else "MidRise"
    return {1:"SingleD",3:"OtherDwelling"}.get(int(code), str(int(code)))   # 8 -> "8" (matches classic)

def _compute_hh_activity_fracs(df):
    """Step 9: compute per-HH activity-driven fractions (Equipment + Lighting).

    Returns
    -------
    dict keyed by (hh_id, day_type) ->
        {'equip_frac': arr24, 'light_frac': arr24,
         'equip_design_W': float, 'light_design_W': float}
    df must already have SIM_HH_ID and Day_Type columns.
    """
    needed = ACT + HOM + ["SIM_HH_ID", "Day_Type"]
    sub = df[needed].copy()
    n_hh = sub["SIM_HH_ID"].nunique()
    print(f"  Step 9: computing activity fractions for {n_hh:,} HHs...", flush=True)
    result = {}
    for i, (hh_id, hh_df) in enumerate(sub.groupby("SIM_HH_ID")):
        if i % 10000 == 0:
            print(f"    {i:,}/{n_hh:,}", flush=True, end="\r")
        by_dt = {}
        for dt in ("Weekday", "Weekend"):
            rows = hh_df[hh_df["Day_Type"] == dt].to_dict("records")
            if rows:
                by_dt[dt] = rows
        if "Weekday" not in by_dt and "Weekend" in by_dt:
            by_dt["Weekday"] = by_dt["Weekend"]
        elif "Weekend" not in by_dt and "Weekday" in by_dt:
            by_dt["Weekend"] = by_dt["Weekday"]
        elif not by_dt:
            continue
        raw = _al.compute_48slot_loads(by_dt)
        cal = _al.calibrate_schedules(raw)
        for dt in ("Weekday", "Weekend"):
            frac_key = "equip_frac_wd" if dt == "Weekday" else "equip_frac_we"
            lfrac_key = "light_frac_wd" if dt == "Weekday" else "light_frac_we"
            result[(hh_id, dt)] = {
                "equip_frac":     cal[frac_key],
                "light_frac":     cal[lfrac_key],
                "equip_design_W": cal["equip_design_W"],
                "light_design_W": cal["light_design_W"],
            }
    print(f"    {n_hh:,}/{n_hh:,} done.", flush=True)
    return result


def convert(df):
    df = df.rename(columns={"HH_ID":"SIM_HH_ID"}).copy()
    df["Day_Type"] = df["DDAY_STRATA"].map(DAYTYPE)
    keys = ["SIM_HH_ID","Day_Type"]
    occ48 = df.groupby(keys, sort=True)[HOM].mean()                          # (G,48) fraction home
    wdf = df[keys].copy()
    for c in ACT: wdf[c] = df[c].map(MET).fillna(100.0)
    met48 = wdf.groupby(keys, sort=True)[ACT].mean().reindex(occ48.index)    # (G,48) watts
    stat  = df.groupby(keys, sort=True)[STAT].first().reindex(occ48.index)
    G = len(occ48.index)
    occ24 = occ48.values.reshape(G,24,2).mean(axis=2)                        # hour h = slots (2h,2h+1)
    met24 = met48.values.reshape(G,24,2).mean(axis=2)
    out = pd.DataFrame({
        "SIM_HH_ID": occ48.index.get_level_values("SIM_HH_ID").repeat(24),
        "Day_Type" : occ48.index.get_level_values("Day_Type").repeat(24),
        "Hour"     : np.tile(np.arange(24), G),
        "Occupancy_Schedule": np.round(occ24.reshape(-1),3),
        "Metabolic_Rate"    : np.round(met24.reshape(-1),1),
    })
    for col in ["HHSIZE","BEDRM","CONDO","ROOM","REPAIR","MATCH_TIER"]:
        out[col] = np.repeat(stat[col].values, 24)
    dt = np.repeat(stat["DTYPE"].values,24); bd = np.repeat(stat["BEDRM"].values,24)
    out["DTYPE"] = [dtype_label(c,b) for c,b in zip(dt,bd)]
    pr = np.repeat(stat["PR"].values,24)
    out["PR"] = [PR_LBL.get(int(p), str(int(p))) for p in pr]

    # Step 9: activity-driven Equipment_Fraction + Lighting_Fraction
    frac_map = _compute_hh_activity_fracs(df)
    eq_col, lt_col, eq_dw_col, lt_dw_col = [], [], [], []
    for hh, dt in zip(occ48.index.get_level_values("SIM_HH_ID"),
                      occ48.index.get_level_values("Day_Type")):
        fracs = frac_map.get((hh, dt))
        if fracs is not None:
            eq_col.extend(fracs["equip_frac"].tolist())
            lt_col.extend(fracs["light_frac"].tolist())
            eq_dw_col.extend([fracs["equip_design_W"]] * 24)
            lt_dw_col.extend([fracs["light_design_W"]] * 24)
        else:
            eq_col.extend([0.0] * 24)
            lt_col.extend([0.0] * 24)
            eq_dw_col.extend([0.0] * 24)
            lt_dw_col.extend([0.0] * 24)
    out["Equipment_Fraction"] = np.round(eq_col, 4)
    out["Lighting_Fraction"]  = np.round(lt_col,  4)
    out["Equip_Design_W"]     = np.round(eq_dw_col, 2)
    out["Light_Design_W"]     = np.round(lt_dw_col,  2)

    return out[OUT_COLS]

def complete_day_types(df):
    """Ensure every HH has both Weekday and Weekend observations.
    GSS assigns one diary day per respondent, so many HHs appear in only one DDAY_STRATA.
    Missing day is filled by DONOR-DRAW (seed=42): draw a *genuine* opposite-day diary
    from the in-frame pool (same target day-type), per member, keeping the HH's own
    dwelling/HH attrs. Preserves the calibrated weekend marginal (copy-day biased it
    -2.76 pp). Same mechanism as assemble_2030; for 2030 the pool is the assembled 2030
    frame so donors carry 2030 occupancy. Limitation: imputed day's within-HH co-presence
    and WD/WE correlation are synthetic, but BEM consumes only the occupancy fraction +
    metabolic (not pairwise COP), so harmless.
    """
    rng = np.random.default_rng(42)
    hh_strata = df.groupby('HH_ID')['DDAY_STRATA'].apply(lambda s: frozenset(s.unique()))
    wd_only = set(hh_strata.index[hh_strata.apply(lambda s: (1 in s) and not (2 in s or 3 in s))])
    we_only = set(hh_strata.index[hh_strata.apply(lambda s: (2 in s or 3 in s) and (1 not in s))])
    wd_pool = df[df['DDAY_STRATA'] == 1]                 # weekday donors
    we_pool = df[df['DDAY_STRATA'].isin([2, 3])]         # weekend donors (Sat+Sun pooled -> matches WE marginal)
    extra = []
    if wd_only:                                          # WD-only HHs need a Weekend
        sub = df[df['HH_ID'].isin(wd_only)].copy()
        pick = rng.integers(0, len(we_pool), size=len(sub))
        sub[ACT + HOM] = we_pool.iloc[pick][ACT + HOM].values
        sub['DDAY_STRATA'] = 2                           # label -> Weekend (convert() pools 2,3)
        extra.append(sub)
        print(f"  donor-draw {len(wd_only):,} WD-only HHs -> Weekend ({len(sub):,} member-rows)", flush=True)
    if we_only:                                          # WE-only HHs need a Weekday
        sub = df[df['HH_ID'].isin(we_only)].copy()
        pick = rng.integers(0, len(wd_pool), size=len(sub))
        sub[ACT + HOM] = wd_pool.iloc[pick][ACT + HOM].values
        sub['DDAY_STRATA'] = 1
        extra.append(sub)
        print(f"  donor-draw {len(we_only):,} WE-only HHs -> Weekday ({len(sub):,} member-rows)", flush=True)
    return pd.concat([df] + extra, ignore_index=True) if extra else df

def assemble_2030():
    rng = np.random.default_rng(42)
    stock = pd.read_csv(AUG, low_memory=False)          # frozen 2022 _excl persons
    d30   = pd.read_csv(D2030, low_memory=False)         # calibrated 2030 diaries
    out = stock.copy()
    for k in (1,2,3):
        smask = (stock["DDAY_STRATA"].values==k)
        pool  = d30[d30["DDAY_STRATA"]==k]
        pick  = rng.integers(0, len(pool), size=int(smask.sum()))
        out.loc[smask, ACT+HOM] = pool.iloc[pick][ACT+HOM].values
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--year",choices=["2022","2030"],required=True)
    yr=ap.parse_args().year
    df = pd.read_csv(AUG, low_memory=False) if yr=="2022" else assemble_2030()
    df = complete_day_types(df)
    bem = convert(df)
    # acceptance gates
    assert set(bem["Day_Type"].unique()) <= {"Weekday","Weekend"}
    assert bem["Hour"].between(0,23).all()
    assert bem["Occupancy_Schedule"].between(0,1).all()
    assert (bem["Metabolic_Rate"]>=0).all()
    cov = bem.groupby("SIM_HH_ID")["Day_Type"].nunique()
    assert (cov==2).all(), f"{int((cov<2).sum())} HHs missing a day-type (integration.py would reject)"
    # Step 9 gates
    assert bem["Equipment_Fraction"].between(0,1).all(), "Equipment_Fraction out of [0,1]"
    assert bem["Lighting_Fraction"].between(0,1).all(),  "Lighting_Fraction out of [0,1]"
    assert (bem["Equip_Design_W"]>=0).all(),             "Equip_Design_W negative"
    assert (bem["Light_Design_W"]>=0).all(),             "Light_Design_W negative"
    target = BEMS/f"BEM_Schedules_{yr}.csv"
    if target.exists():
        bak = BEMS/f"BEM_Schedules_{yr}_CLASSIC_BAK_2026-05-31.csv"
        if not bak.exists(): shutil.copy2(target,bak); print("backed up ->",bak.name, flush=True)
    tmp=str(target)+".tmp"; bem.to_csv(tmp,index=False,float_format="%.3f"); os.replace(tmp,str(target))
    nhh=bem["SIM_HH_ID"].nunique()
    print(f"WROTE {target.name}: {len(bem):,} rows, {nhh:,} HH", flush=True)
    print("  DTYPE:", sorted(bem['DTYPE'].astype(str).unique()), flush=True)
    print("  PR:", sorted(bem['PR'].astype(str).unique()), flush=True)
    for d in ("Weekday","Weekend"):
        sub=bem[bem.Day_Type==d]; print(f"  {d}: mean Occupancy {sub.Occupancy_Schedule.mean():.3f}, mean Metabolic {sub.Metabolic_Rate.mean():.1f}", flush=True)

if __name__=="__main__": main()
