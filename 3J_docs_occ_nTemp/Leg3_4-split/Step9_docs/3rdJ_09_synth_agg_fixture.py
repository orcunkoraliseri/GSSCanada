"""Synthetic §8E-shaped tables so the Step-9 script's builders/gates/figures/HTML are exercised
end-to-end before the real aggregation exists. Values are plausible, NOT meaningful."""
import numpy as np, pandas as pd, os, sys, importlib.util
R = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main"
sys.path.insert(0, R)
s = importlib.util.spec_from_file_location("c", os.path.join(R, r"3J_docs_occ_nTemp\Leg3_4-split\Step8_docs\3rdJ_08D_campaign_cells.py"))
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
CELLS = m.build_campaign_cells(R)
CH = ["office","retail","hotel","residential","residential_common","service_MEP"]
AREA = {"office":25485.6,"retail":3159.0,"hotel":14215.4,"residential":12786.5,
        "residential_common":1428.9,"service_MEP":15547.7}
TOT = sum(AREA.values())
EUI_T = {"office":135.,"retail":110.,"hotel":240.,"residential":140.,
         "residential_common":90.,"service_MEP":60.}
LEV = {"cons":-3.0,"central":0.0,"opt":2.5}
rng = np.random.default_rng(7)
ann, peak, diur, meta = [], [], [], []
END = [("interior_lighting","Electricity"),("interior_equipment","Electricity"),
       ("interior_equipment","NaturalGas"),("dhw","Electricity"),("dhw","NaturalGas"),
       ("cooling","Electricity"),("heating","Electricity"),("heating","NaturalGas"),
       ("fans","Electricity"),("pumps","Electricity"),("heat_rejection","Electricity"),
       ("heat_recovery","Electricity")]
SHAPE = {"office":[.02,.02,.02,.02,.03,.08,.35,.75,.95,1.,1.,.98,.9,.95,1.,.98,.9,.6,.25,.1,.05,.03,.02,.02],
         "retail":[.01,.01,.01,.01,.02,.05,.15,.4,.7,.9,1.,1.,1.,.98,.95,.9,.85,.7,.45,.2,.05,.02,.01,.01],
         "hotel":[1.,1.,1.,1.,1.,.95,.75,.5,.3,.22,.2,.2,.2,.2,.2,.25,.45,.7,.85,.95,1.,1.,1.,1.],
         "residential":[.9,.9,.9,.9,.9,.85,.7,.5,.35,.3,.3,.32,.35,.35,.4,.5,.7,.9,1.,1.,1.,.98,.95,.92]}
SHAPE["residential_common"]=[.6]*24; SHAPE["service_MEP"]=[.7]*24
for c in CELLS:
    tag, sc = c["tag"], c["scenario"]
    f = 1.0
    for k, v in LEV.items():
        if sc.endswith("_"+k) or sc == "B_"+k: f = 1 + v/100
    if sc.startswith("Y"):  f = 1 + (int(sc[1:])-2015)/2000
    if sc == "Default_NECB": f = 1.06
    tot_ch = {}
    for ch in CH:
        base = EUI_T[ch]*AREA[ch]/ (1/3.6e6) / 1e0  # kWh -> J
        base = EUI_T[ch]*AREA[ch]*3.6e6
        ff = f if (("sens_"+ch) in sc or sc.startswith("B_") or sc.startswith("Y") or sc=="Default_NECB") else 1.0
        if sc.startswith("sens_") and not sc.startswith("sens_"+ch): ff = 1.0
        tot = base*ff*(1+rng.normal(0,.004))
        tot_ch[ch] = tot
        w = np.array([.20,.24,.06,.03,.07,.14,.06,.09,.05,.03,.02,.01]); w = w/w.sum()
        for (eu,fu),ww in zip(END,w):
            ann.append(dict(channel=ch,end_use=eu,fuel=fu,energy_J=tot*ww,
                            peak_W=tot*ww/3600/2000,allocation="direct" if eu.startswith("interior") else "hvac",
                            cell_tag=tag,scenario=sc,building=c["building"],city=c["city"],cz=c["cz"],
                            energy_GJ=tot*ww/1e9))
    ann.append(dict(channel="core_exterior",end_use="exterior_lighting",fuel="Electricity",
                    energy_J=682.88e9,peak_W=1e5,allocation="unallocated",cell_tag=tag,scenario=sc,
                    building=c["building"],city=c["city"],cz=c["cz"],energy_GJ=682.88))
    sop = 0.0
    for ch in CH:
        mw = tot_ch[ch]/8760/3600
        for season in ("winter","summer","shoulder","all"):
            for dt in ("WD","WE"):
                sh = np.array(SHAPE[ch]); sh = sh/sh.mean()
                if dt=="WE" and ch=="office": sh = sh*.35
                for h in range(24):
                    diur.append(dict(season=season,daytype=dt,hour=h,W=mw*sh[h]*(1.1 if season=="winter" else 1.0),
                                     channel=ch,metric="energy_W",cell_tag=tag))
        # occupancy series: same shape family, but residential is evening-dominant only when
        # injected -- Default_NECB keeps a midday-dominant code schedule (measured: ratio 0.22).
        osh = np.array(SHAPE[ch], dtype=float)
        if ch == "residential" and sc == "Default_NECB":
            osh = np.array([.2,.2,.2,.2,.25,.4,.6,.8,.95,1.,1.,1.,1.,.95,.9,.8,.6,.4,.3,.25,.22,.2,.2,.2])
        for season in ("winter","summer","shoulder","all"):
            for dt in ("WD","WE"):
                for h in range(24):
                    diur.append(dict(season=season,daytype=dt,hour=h,W=osh[h]*100,
                                     channel=ch,metric="people",cell_tag=tag))
        for dt in ("WD","WE","all"):
            peak.append(dict(channel=ch,daytype=dt,metric="people",peak_W=float(osh.max()*100),
                             peak_hour_argmax=int(np.argmax(osh)),
                             peak_hour_circular=float(np.argmax(osh))+0.3,mean_W=float(osh.mean()*100),
                             sum_of_channel_peaks_W=0,coincidence_factor=0,cell_tag=tag))
        pk = mw*max(SHAPE[ch])/np.mean(SHAPE[ch])*1.6; sop += pk
        prof = np.array(SHAPE[ch])
        for dt in ("WD","WE","all"):
            peak.append(dict(channel=ch,daytype=dt,metric="energy_W",peak_W=pk,
                             peak_hour_argmax=int(np.argmax(prof)),
                             peak_hour_circular=float(np.argmax(prof))+0.3,mean_W=mw,
                             sum_of_channel_peaks_W=0,coincidence_factor=0,cell_tag=tag))
    for r in peak:
        if r["cell_tag"]==tag:
            r["sum_of_channel_peaks_W"]=sop; r["coincidence_factor"]=0.78
    peak.append(dict(channel="_BUILDING",daytype="all",metric="energy_W",peak_W=sop*.78,peak_hour_argmax=-1,
                     peak_hour_circular=14.,mean_W=sum(tot_ch.values())/8760/3600,
                     sum_of_channel_peaks_W=sop,coincidence_factor=0.78,cell_tag=tag))
    mt = dict(cell_tag=tag,scenario=sc,building=c["building"],city=c["city"],cz=c["cz"],
              PLATFORM="win32",INJ_HASH="cf69d508",INPUTS_HASH="85773432",OUTPUT_SCHEMA_HASH="db4e729f",
              energyplus_version="24.2.0",site_energy_GJ=sum(tot_ch.values())/1e9,
              attributed_GJ=sum(tot_ch.values())/1e9,attribution_residual_rel=0.0,attribution_closed=True,
              total_building_area_m2=TOT,excluded_plenum_area_m2=70611.6,unclassified_area_m2=0.0,
              fallback_hours_cool=120,fallback_hours_heat=300,fallback_hours_hvac=40,fallback_hours_dhw=0)
    for ch in CH:
        mt[f"area_{ch}_m2"]=AREA[ch]; mt[f"share_{ch}_pct_gross"]=100*AREA[ch]/TOT
    meta.append(mt)
os.makedirs("fake_agg", exist_ok=True)
pd.DataFrame(ann).to_csv("fake_agg/agg_annual.csv",index=False)
pd.DataFrame(peak).to_csv("fake_agg/agg_peak.csv",index=False)
pd.DataFrame(diur).to_csv("fake_agg/agg_diurnal.csv",index=False)
pd.DataFrame(meta).to_csv("fake_agg/agg_meta.csv",index=False)
print("cells",len(CELLS),"| annual",len(ann),"| diurnal",len(diur),"| peak",len(peak))
