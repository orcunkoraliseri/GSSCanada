# 5J multi-zone re-pilot, job 3 (Speed, Spain only): extract per-DWELLING hourly series from each run's eplusout.csv.
# Output per run: R/extracted/<run_id>.csv.gz (long format: 8,760 rows per dwelling; header comments start with '#')
#                 R/extracted/<run_id>.dwellings.csv (side table: hid, floor index, position, floor area, zones)
# Per dwelling = sum over its zones (energy) ; area-weighted mean over its zones (temperature, humidity).
# Targets: heating_kwh, cooling_kwh, equipment_kwh, total_elec_kwh = equipment + heating/COP_H + cooling/COP_C.
# COP_H = COP_C = 3.0 is ASSUMED (manager, pending the author's numbers) and written in every file header.
import csv, gzip, io, json, os, re, sys, platform
import numpy as np
import pandas as pd

R = "/speed-scratch/o_iseri/5J/mz_pilot/"
J_PER_KWH = 3.6e6
COP_H = 3.0
COP_C = 3.0
print("python", sys.version.split()[0], "pandas", pd.__version__, "numpy", np.__version__, "host", platform.node())

# variable name -> (column name, kind) ; kind: sum | wmean
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
    ("Zone Heating Setpoint Not Met Time", "unmet_heat_zone_h", "sum"),
    ("Zone Cooling Setpoint Not Met Time", "unmet_cool_zone_h", "sum"),
    ("Zone Mean Air Temperature", "t_air_c", "wmean"),
    ("Zone Operative Temperature", "t_op_c", "wmean"),
    ("Zone Air Relative Humidity", "rh_pct", "wmean"),
]
VMAP = {v[0]: v for v in VARS}
COLRE = re.compile(r"^(.*?):(.+?) \[([^\]]*)\]\(Hourly\)\s*$")
ZRE = re.compile(r"(Z_F\d\d_D\d\d)$")

man = list(csv.DictReader(io.open(R + "run_manifest.csv", encoding="utf-8")))
os.makedirs(R + "extracted", exist_ok=True)
nbad = 0
for m in man:
    rid = m["run_id"]
    rd = R + "runs/%s/" % rid
    meta = json.load(io.open(rd + "meta.json", encoding="utf-8"))
    csvp = rd + "eplus_out/eplusout.csv"
    if not os.path.exists(csvp):
        print("EXTRACT %s ERROR no eplusout.csv" % rid)
        nbad += 1
        continue
    df = pd.read_csv(csvp)
    n = len(df)
    zone_dw = meta["zone_dwelling"]
    zarea = meta["zone_floor_areas"]
    dws = sorted(set(zone_dw.values()))
    acc = {j: {} for j in dws}          # j -> col -> array
    wsum = {j: sum(zarea[z] for z in zone_dw if zone_dw[z] == j) for j in dws}
    found = {}
    for c in df.columns[1:]:
        mm = COLRE.match(c)
        if not mm:
            continue
        key, var, unit = mm.groups()
        if var not in VMAP:
            continue
        zm = ZRE.search(key)
        if not zm:
            continue
        z = zm.group(1)
        j = zone_dw[z]
        _, name, kind = VMAP[var]
        v = df[c].to_numpy(dtype=float)
        if kind == "sumJ":
            v = v / J_PER_KWH
        elif kind == "wmean":
            v = v * (zarea[z] / wsum[j])
        acc[j][name] = acc[j].get(name, 0.0) + v
        found[name] = found.get(name, 0) + 1
    hdr = ["# 5J multi-zone re-pilot, run %s, building %s, extracted by mzp_extract.py" % (rid, m["building_id"]),
           "# units: *_kwh = kWh per hour of that dwelling (sum of its zones); t_air_c, t_op_c degC and rh_pct %% are "
           "floor-area-weighted means over the dwelling's zones; unmet_*_zone_h = sum over zones of hours",
           "# total_elec_kwh = equipment_kwh + heating_kwh / %.1f + cooling_kwh / %.1f ; COP_H = COP_C = 3.0 ASSUMED "
           "(manager, pending the author's numbers)" % (COP_H, COP_C),
           "# heating_kwh / cooling_kwh = Zone Ideal Loads Supply Air Total Heating / Cooling Energy ; "
           "equipment_kwh = Electric Equipment Electricity Energy ; no Lights object exists, so no lighting column",
           "# hour = 1..%d of the year, hour 1 ends at 01:00 on 1 January (clock origin midnight)" % n]
    frames = []
    for j in dws:
        a = acc[j]
        d = {"dwelling": np.full(n, j, dtype=int), "hour": np.arange(1, n + 1)}
        d["heating_kwh"] = a["heating_kwh"]
        d["cooling_kwh"] = a["cooling_kwh"]
        d["equipment_kwh"] = a["equipment_kwh"]
        d["total_elec_kwh"] = a["equipment_kwh"] + a["heating_kwh"] / COP_H + a["cooling_kwh"] / COP_C
        for _, name, _k in VARS[3:]:
            if name in a:
                d[name] = a[name]
        frames.append(pd.DataFrame(d))
    out = pd.concat(frames, ignore_index=True)
    p = R + "extracted/%s.csv.gz" % rid
    with gzip.open(p, "wt", encoding="utf-8") as fh:
        fh.write("\n".join(hdr) + "\n")
        out.to_csv(fh, index=False, float_format="%.8g")
    # side table
    k = int(meta["k"])
    F = int(meta["floors"])
    spans = (m["class"] in ("SFH", "TH"))
    with io.open(R + "extracted/%s.dwellings.csv" % rid, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["dwelling", "hid", "floor_min", "floor_max", "position", "col", "end_dwelling", "floor_area_m2", "n_zones", "zones"])
        plc = {int(x.split(":")[0]): x.split(":")[1] for x in m["placement"].split(";")}
        for j in dws:
            zs = sorted(z for z in zone_dw if zone_dw[z] == j)
            fl = sorted(int(z[3:5]) for z in zs)
            if spans:
                pos_, col, endd = "all", 0, 1
            else:
                f = fl[0]
                pos_ = "ground" if f == 0 else ("top" if f == F - 1 else "middle")
                col = j - f * k
                endd = 1 if (col == 0 or col == k - 1) else 0
            w.writerow([j, plc[j], fl[0], fl[-1], pos_, col, endd, "%.4f" % wsum[j], len(zs), ";".join(zs)])
    sz = os.path.getsize(p)
    print("EXTRACT %s rows=%d dwellings=%d rows_written=%d bytes_gz=%d vars_found=%s"
          % (rid, n, len(dws), len(out), sz, json.dumps(found, sort_keys=True)))
    if n != 8760 or len(out) != 8760 * len(dws):
        nbad += 1
print("EXTRACT_DONE runs=%d bad=%d" % (len(man), nbad))
sys.exit(1 if nbad else 0)
