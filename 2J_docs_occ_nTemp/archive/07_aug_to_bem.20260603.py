"""07_aug_to_bem.py — OP4: calibrated aug occupancy -> EnergyPlus BEM_Schedules_<year>.csv.
13-col hourly-household format eSim_bem_utils/main.py consumes. BEM is 2-day-type
(Weekday/Weekend) per integration.py: DDAY_STRATA {1,2,3} -> {Weekday, Weekend=Sat+Sun}.
Run-from-anywhere, seed=42, reversible.  Usage:  py 07_aug_to_bem.py --year 2022 | --year 2030
"""
import os, sys, argparse, shutil
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
BASE = HERE.parent                         # GSSCanada-main/
AUG  = BASE/"0_Occupancy"/"Outputs_21CEN22GSS"/"aug_pipeline"/"21CEN22GSS_aug_Full_Aggregated_excl.csv"
D2030= BASE/"0_Occupancy"/"Outputs_21CEN22GSS"/"forecast_2030"/"2030_synthetic_diaries.csv"
BEMS = BASE/"BEM_Setup"

ACT = [f"act30_{i:03d}" for i in range(1,49)]
HOM = [f"hom30_{i:03d}" for i in range(1,49)]
STAT = ["HHSIZE","DTYPE","BEDRM","CONDO","ROOM","REPAIR","PR","MATCH_TIER"]
OUT_COLS = ["SIM_HH_ID","Day_Type","Hour","HHSIZE","DTYPE","BEDRM","CONDO","ROOM",
            "REPAIR","PR","MATCH_TIER","Occupancy_Schedule","Metabolic_Rate"]
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
