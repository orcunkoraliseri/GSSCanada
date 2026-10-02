# -*- coding: utf-8 -*-
"""5J Step 9g: Model A extractor. One OpenUBEM-style run folder -> per flat (= zone `<stem>_F<k>_dwelling_<n>`) 8,760 hourly values.

extract_run(run_dir, zone_rows) -> (result, meta)
  result: {"zones": [zone names in zone-map order], "heating_kwh", "cooling_kwh", "equipment_kwh", "total_elec_kwh": float64 [n, 8760],
           "extra": {name: float64 [n, 8760]}}
  total_elec_kwh = equipment + (heating + cooling) / 3.0 (E6; COP 3.0 assumed).
  heating = Zone Ideal Loads Supply Air Total Heating Energy, cooling = ... Total Cooling Energy (J -> kWh, as mzp_extract.py:18-21);
  equipment = Electric Equipment Electricity Energy; ONLY when the run has no ElectricEquipment column at all (default-schedule
  run, no household) it is Zone Other Equipment Electricity Energy of the zone (the 3 W/m2 lump); `meta["equipment_source"]` says which.
  extras = the pilot's other outputs (names and units as tools/speed/mzp_extract.py:18-39, VARS) where present, plus the two ventilation
  variables and the other-equipment variable the writer added.
Checks (meta): status from eplusout.end (Completed Successfully and 0 Severe), every zone of the map found for the 3 core variables
(exactly once), 8,760 rows, first and last Date/Time, annual = sum of hourly by an INDEPENDENT reader (csv module + math.fsum), and
(INFO) building totals against the eplustbl.csv End Uses table when it can be parsed.
Command line:  a9_extract.py <manifest.csv> <zone_map.csv> <out_dir>   (manifest columns: run_id, district, stem, mode, run_dir)
  writes <out_dir>/<run_id>.npz and <run_id>.json ; exit 0 if every run is OK, 1 otherwise. Run status read, never assumed.
"""
import sys, os, io, re, csv, json, math, time
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import a9_common as c

J_PER_KWH = 3.6e6
# (EnergyPlus variable, name, kind) ; sumJ = Joules -> kWh ; raw = as is   (pilot VARS, mzp_extract.py:18-39, plus the writer's three)
VARS = [
    ("Zone Ideal Loads Supply Air Total Heating Energy", "heating_kwh", "sumJ"),
    ("Zone Ideal Loads Supply Air Total Cooling Energy", "cooling_kwh", "sumJ"),
    ("Electric Equipment Electricity Energy", "equipment_kwh", "sumJ"),
    ("Zone Ideal Loads Supply Air Sensible Heating Energy", "heating_sens_kwh", "sumJ"),
    ("Zone Ideal Loads Supply Air Latent Heating Energy", "heating_lat_kwh", "sumJ"),
    ("Zone Ideal Loads Supply Air Sensible Cooling Energy", "cooling_sens_kwh", "sumJ"),
    ("Zone Ideal Loads Supply Air Latent Cooling Energy", "cooling_lat_kwh", "sumJ"),
    ("Zone Ideal Loads Zone Total Heating Energy", "zoneside_heating_kwh", "sumJ"),
    ("Zone Ideal Loads Zone Total Cooling Energy", "zoneside_cooling_kwh", "sumJ"),
    ("People Total Heating Energy", "people_heat_kwh", "sumJ"),
    ("Zone Infiltration Sensible Heat Gain Energy", "infil_gain_kwh", "sumJ"),
    ("Zone Infiltration Sensible Heat Loss Energy", "infil_loss_kwh", "sumJ"),
    ("Zone Windows Total Heat Gain Energy", "win_gain_kwh", "sumJ"),
    ("Zone Windows Total Heat Loss Energy", "win_loss_kwh", "sumJ"),
    ("Zone Windows Total Transmitted Solar Radiation Energy", "win_solar_kwh", "sumJ"),
    ("Zone Heating Setpoint Not Met Time", "unmet_heat_zone_h", "raw"),
    ("Zone Cooling Setpoint Not Met Time", "unmet_cool_zone_h", "raw"),
    ("Zone Mean Air Temperature", "t_air_c", "raw"),
    ("Zone Operative Temperature", "t_op_c", "raw"),
    ("Zone Air Relative Humidity", "rh_pct", "raw"),
    ("Zone Ventilation Sensible Heat Loss Energy", "vent_loss_kwh", "sumJ"),
    ("Zone Ventilation Sensible Heat Gain Energy", "vent_gain_kwh", "sumJ"),
    ("Zone Other Equipment Electricity Energy", "other_equip_kwh", "sumJ"),
]
VMAP = {v[0]: v for v in VARS}
COLRE = re.compile(r"^(.*?):(.+?) \[([^\]]*)\]\(Hourly\)\s*$")
ZTOKEN = re.compile(r"([0-9A-F]{16}_F\d+_DWELLING_\d+)")
CORE = ("heating_kwh", "cooling_kwh", "equipment_kwh")


def zone_key(key):
    """EnergyPlus upper-cases object names. Ideal loads keys are '<ZONE> IDEAL LOADS AIR SYSTEM', equipment 'EQ_<ZONE>', people 'PE_<ZONE>',
    zone variables '<ZONE>'. Returns the upper-case zone name or None (a name that is not a zone of the map is simply not matched)."""
    k = key.strip().upper()
    if k.endswith(" IDEAL LOADS AIR SYSTEM"):
        k = k[:-len(" IDEAL LOADS AIR SYSTEM")]
    for pre in ("EQ_", "PE_"):
        if k.startswith(pre):
            k = k[len(pre):]
    return k


def read_status(run_dir):
    """(completed, severe, text) from eplusout.end ('EnergyPlus Completed Successfully-- n Warning; m Severe Errors; ...')."""
    p = os.path.join(run_dir, "eplusout.end")
    if not os.path.exists(p):
        return False, None, "no eplusout.end"
    t = io.open(p, encoding="utf-8", errors="replace").read().strip()
    m = re.search(r"(\d+)\s+Severe Errors", t)
    return ("EnergyPlus Completed Successfully" in t), (int(m.group(1)) if m else None), t[:200]


def table_end_use(run_dir):
    """INFO only: building totals in kWh from the End Uses table of eplustbl.csv: {'equipment': x, 'heating': y, 'cooling': z} or {} ."""
    p = os.path.join(run_dir, "eplustbl.csv")
    out = {}
    try:
        rows = list(csv.reader(io.open(p, newline="", encoding="utf-8", errors="replace")))
        for i, r in enumerate(rows):
            if r and r[0] == "End Uses":
                hdr = rows[i + 1]
                for r2 in rows[i + 2:i + 40]:
                    if not r2 or not r2[0].strip():
                        break
                    nm = r2[0].strip()
                    for key, rowname, colpre in (("equipment", "Interior Equipment", "Electricity"), ("heating", "Heating", "District Heating"),
                                                 ("cooling", "Cooling", "District Cooling")):
                        if nm == rowname:
                            for j, h in enumerate(hdr):
                                if h.startswith(colpre):
                                    f = 277.7777778 if "[GJ]" in h else (1.0 if "[kWh]" in h else None)
                                    if f is not None and r2[j].strip() != "":
                                        out[key] = out.get(key, 0.0) + float(r2[j]) * f
                break
    except Exception:
        return {}
    return out


def extract_run(run_dir, zone_rows):
    """See the module text. Raises RuntimeError on a structural problem (a missing zone, a wrong row count); never returns partial data."""
    meta = {"run_dir": run_dir}
    comp, sev, txt = read_status(run_dir)
    meta.update({"completed": comp, "severe": sev, "end_text": txt})
    if not comp or sev != 0:
        raise RuntimeError("run status not clean: completed=%s severe=%s (%s)" % (comp, sev, txt))
    csvp = os.path.join(run_dir, "eplusout.csv")
    if not os.path.exists(csvp):
        raise RuntimeError("no eplusout.csv in %s" % run_dir)
    df = pd.read_csv(csvp)
    n = len(df)
    meta["rows"] = n
    if n != c.H:
        raise RuntimeError("rows %d != %d" % (n, c.H))
    t0, t1 = str(df.iloc[0, 0]).strip(), str(df.iloc[-1, 0]).strip()
    meta["first_last"] = [t0, t1]
    if not (t0.startswith("01/01") and "01:00:00" in t0 and t1.startswith("12/31") and "24:00:00" in t1):
        raise RuntimeError("first / last Date/Time wrong: %r %r" % (t0, t1))
    zones = [r["zone"] for r in zone_rows]
    up = {z.upper(): i for i, z in enumerate(zones)}
    if len(up) != len(zones):
        raise RuntimeError("duplicate zone names in the zone map rows")
    acc = {}                                # name -> {zone index -> (column label, array)}
    unmatched_vars = 0
    for col in df.columns[1:]:
        m = COLRE.match(col)
        if not m:
            continue
        key, var, unit = m.groups()
        if var not in VMAP:
            continue
        zi = up.get(zone_key(key))
        if zi is None:
            zt = ZTOKEN.search(key.upper())          # fallback: the one zone token inside the key
            zi = up.get(zt.group(1)) if zt else None
        if zi is None:
            unmatched_vars += 1
            continue
        _, name, kind = VMAP[var]
        if kind == "sumJ" and unit != "J":
            raise RuntimeError("variable %s has unit %s, expected J" % (var, unit))
        v = df[col].to_numpy(dtype=float)
        if kind == "sumJ":
            v = v / J_PER_KWH
        d = acc.setdefault(name, {})
        if zi in d:
            raise RuntimeError("zone %s has two columns for %s" % (zones[zi], var))
        d[zi] = (col, v)
    meta["columns_not_matched_to_a_zone"] = unmatched_vars
    nz = len(zones)
    eq_name = "equipment_kwh"
    if "equipment_kwh" not in acc:
        if "other_equip_kwh" in acc:
            eq_name = "other_equip_kwh"
        else:
            raise RuntimeError("neither Electric Equipment nor Other Equipment electricity found")
    meta["equipment_source"] = "Electric Equipment Electricity Energy" if eq_name == "equipment_kwh" else "Zone Other Equipment Electricity Energy (no ElectricEquipment in the run)"
    need = {"heating_kwh": acc.get("heating_kwh", {}), "cooling_kwh": acc.get("cooling_kwh", {}), "equipment_kwh": acc.get(eq_name, {})}
    for nm, d in need.items():
        miss = [zones[i] for i in range(nz) if i not in d]
        if miss:
            raise RuntimeError("%s: %d of %d zones have no column, first %s" % (nm, len(miss), nz, miss[:2]))
        if len(d) != nz:
            raise RuntimeError("%s: %d columns for %d zones (a column matches a name outside the map)" % (nm, len(d), nz))
    res = {"zones": zones, "extra": {}}
    cols_used = {}
    for nm, d in need.items():
        res[nm] = np.stack([d[i][1] for i in range(nz)])
        cols_used[nm] = [d[i][0] for i in range(nz)]
    res["total_elec_kwh"] = res["equipment_kwh"] + (res["heating_kwh"] + res["cooling_kwh"]) / c.COP
    for _, name, _k in VARS:
        if name in CORE:
            continue
        d = acc.get(name)
        if d and len(d) == nz:
            res["extra"][name] = np.stack([d[i][1] for i in range(nz)])
    meta["extras_present"] = sorted(res["extra"])
    if not np.isfinite(res["total_elec_kwh"]).all():
        raise RuntimeError("non-finite values")
    # independent annual check: csv module + fsum, own column lookup by the exact label
    want = {}
    for nm, labs in cols_used.items():
        for i, lab in enumerate(labs):
            want[lab] = (nm, i)
    sums = {lab: [] for lab in want}
    with io.open(csvp, newline="", encoding="utf-8", errors="replace") as fh:
        rd = csv.reader(fh)
        head = next(rd)
        pos = {lab: head.index(lab) for lab in want}
        for row in rd:
            for lab, p in pos.items():
                sums[lab].append(float(row[p]))
    worst = 0.0
    for lab, (nm, i) in want.items():
        a_ind = math.fsum(sums[lab]) / J_PER_KWH
        a_arr = float(res[nm][i].sum())
        worst = max(worst, abs(a_ind - a_arr) / max(abs(a_ind), 1e-9) if abs(a_ind) > 1e-9 else abs(a_ind - a_arr))
    meta["annual_vs_sum_hourly_max_rel"] = worst
    if worst > 1e-9:
        raise RuntimeError("annual differs from the sum of hourly (independent reader): %.3e" % worst)
    tb = table_end_use(run_dir)
    meta["table_end_use_kwh"] = tb
    meta["table_vs_extracted_rel"] = {}
    for key, nm in (("equipment", "equipment_kwh"), ("heating", "heating_kwh"), ("cooling", "cooling_kwh")):
        tot = float(res[nm].sum())
        if key in tb and tot > 0:
            meta["table_vs_extracted_rel"][key] = abs(tb[key] - tot) / tot
    meta["annual_kwh"] = {nm: float(res[nm].sum()) for nm in CORE + ("total_elec_kwh",)}
    meta["n_zones"] = nz
    return res, meta


def main(argv):
    manifest, zmap, out_dir = argv[1:4]
    zm = c.zone_map(zmap)
    os.makedirs(out_dir, exist_ok=True)
    bad = 0
    for r in c.read_csv_rows(manifest):
        t0 = time.time()
        key = (r["district"], r["stem"])
        try:
            if key not in zm:
                raise RuntimeError("stem not in the zone map")
            res, meta = extract_run(r["run_dir"], zm[key])
            np.savez_compressed(os.path.join(out_dir, r["run_id"] + ".npz"), heating=res["heating_kwh"], cooling=res["cooling_kwh"],
                                equipment=res["equipment_kwh"], total_elec=res["total_elec_kwh"], zones=np.array(res["zones"]),
                                **{"x_" + k: v for k, v in res["extra"].items()})
            meta["status"] = "OK"
        except Exception as e:                       # a failed run is a result, written down, never skipped
            meta = {"status": "FAILED", "reason": str(e)[:300]}
            bad += 1
        meta.update({"run_id": r["run_id"], "mode": r.get("mode"), "seconds": round(time.time() - t0, 1)})
        json.dump(meta, io.open(os.path.join(out_dir, r["run_id"] + ".json"), "w", encoding="utf-8"), indent=1, default=str)
        print("EXTRACT %s %s %s" % (r["run_id"], meta["status"], meta.get("reason", "zones=%s annual_kwh=%s" % (meta.get("n_zones"), {k: round(v, 1) for k, v in meta.get("annual_kwh", {}).items()}))), flush=True)
    print("EXTRACT_DONE bad=%d" % bad, flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
