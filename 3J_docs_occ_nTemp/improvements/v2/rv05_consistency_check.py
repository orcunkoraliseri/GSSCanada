"""RV05 internal-consistency falsifier. No external access; arithmetic + local CSV only."""
import csv, os

CSV = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup\Reference-Validation\DOE_non-residential_simulation_results_canadian.csv"

# ---------- CHECK 1: are RV05's "90.1-2004 anchor" rows just our own CSV? ----------
rv05_2004 = {  # (building, zone) -> RV05 kWh/m2 value
    ("Large Office", "6A"): 172.56, ("Large Office", "7"): 176.34,
    ("Medium Office", "6A"): 170.03, ("Medium Office", "7"): 172.87,
    ("Large Hotel", "6A"): 286.44, ("Large Hotel", "7"): 302.21,
    ("Small Hotel", "6A"): 230.92, ("Small Hotel", "7"): 244.80,
    ("Stand-Alone Retail", "6A"): 109.78, ("Stand-Alone Retail", "7"): 110.73,
    ("Strip Mall", "6A"): 147.00, ("Strip Mall", "7"): 153.00,
}
rows = {}
with open(CSV, newline="") as f:
    r = csv.reader(f)
    hdr = next(r)
    i6a = hdr.index("Minneapolis - Montreal (6A)")
    i7 = hdr.index("Duluth - Calgary (7)")
    for line in r:
        if line:
            rows[line[0]] = (float(line[i6a]), float(line[i7]))

print("CHECK 1 -- RV05 'Deru 2011 Table 5-2' rows vs OUR OWN local CSV")
print(f"{'prototype':<20}{'zone':<5}{'RV05':>9}{'local CSV':>13}{'delta':>10}   back-conv kBtu")
n_exact = 0
for (b, z), v in rv05_2004.items():
    local = rows[b][0 if z == "6A" else 1]
    d = v - round(local, 2)
    if abs(d) < 0.005:
        n_exact += 1
    print(f"{b:<20}{z:<5}{v:>9.2f}{local:>13.6f}{d:>10.2f}   {local/3.15459:>8.4f}")
print(f"--> {n_exact}/12 RV05 values are our local CSV rounded to 2 dp\n")

# ---------- CHECK 2: does the end-use table sum to the stated site total? ----------
# (prototype, zone) -> [(enduse, GJ, share_pct, eui)], plus stated total site EUI
EU = {
 ("Large Office","6A"): ([68.37,113.32,168.39,24.18,1003.45,130.54,157.90,23.18,35.59,102.31,2.82,19.40],
                          [0.23,0.38,0.57,0.08,3.40,0.44,0.53,0.08,0.12,0.35,0.01,0.07], 1003.45, 6.02, 177.01),
 ("Large Office","7"):  ([69.52,94.08,168.53,24.43,1003.45,130.54,158.13,22.49,28.91,116.52,3.23,20.26],
                          [0.24,0.32,0.57,0.08,3.41,0.44,0.54,0.08,0.10,0.40,0.01,0.07], 1003.45, 6.02, 176.53),
 ("Medium Office","6A"):([330.18,95.60,147.87,32.59,448.42,7.43,58.31,0.09,30.24],
                          [15.15,4.39,6.78,1.50,20.57,0.34,2.68,0.00,1.39], 448.42, 25.00, 121.53),
 ("Medium Office","7"): ([282.52,70.04,148.07,32.93,448.42,7.43,55.94,0.09,13.53,31.19],
                          [14.95,3.71,7.84,1.74,23.73,0.39,2.96,0.00,0.72,1.65], 448.42, 25.00, 105.36),
 ("Large Hotel","6A"):  ([174.43,198.87,152.06,54.07,631.08,178.81,158.16,21.82,32.93,346.90,12.28],
                          [1.50,1.71,1.31,0.47,5.43,1.54,1.36,0.19,0.28,2.99,0.11], 631.08, 15.45, 284.44),
 ("Large Hotel","7"):   ([234.85,155.68,151.98,54.00,631.08,178.81,156.68,24.90,34.72,358.08,12.25],
                          [1.92,1.27,1.24,0.44,5.16,1.46,1.28,0.20,0.28,2.93,0.10], 631.08, 15.45, 299.28),
 ("Small Hotel","6A"):  ([315.33,155.39,138.47,41.11,460.79,196.99,0.20,288.83],
                          [10.13,4.99,4.45,1.32,14.80,6.33,0.01,9.27], 460.79, 34.36, 232.24),
 ("Small Hotel","7"):   ([373.07,133.36,138.59,41.06,460.79,193.40,0.20,300.05],
                          [11.56,4.13,4.29,1.27,14.28,5.99,0.01,9.30], 460.79, 34.36, 240.69),
 ("Stand-Alone Retail","6A"):([437.70,116.78,363.61,60.39,268.24,198.29,46.58],
                          [24.95,6.66,20.72,3.44,15.29,11.30,2.65], 268.24, 32.48, 212.45),
 ("Stand-Alone Retail","7"):([323.13,75.51,359.90,60.51,268.24,196.41,26.11,47.59],
                          [21.55,5.04,24.01,4.04,17.89,13.10,1.74,3.17], 268.24, 32.48, 181.54),
 ("Strip Mall","6A"):   ([502.09,113.44,555.54,91.29,194.16,160.76,100.18],
                          [28.36,6.41,31.38,5.16,10.97,9.08,5.66], 194.16, 25.80, 235.26),
 ("Strip Mall","7"):    ([549.52,71.82,555.54,91.48,194.16,161.67,8.15,101.94],
                          [29.84,3.90,30.17,4.97,10.54,8.78,0.44,5.54], 194.16, 25.80, 244.73),
}
print("CHECK 2 -- EnergyPlus end-use tables MUST sum to total site energy")
print(f"{'prototype':<21}{'zn':<4}{'sum GJ':>9}{'shares%':>9}{'implied area m2':>17}{'total GJ from EUI':>19}{'coverage%':>11}")
for (b, z), (gj, sh, eq_gj, eq_eui, tot_eui) in EU.items():
    area = (eq_gj / 3.6 * 1000) / eq_eui
    tot_gj = tot_eui * area / 1000 * 3.6
    print(f"{b:<21}{z:<4}{sum(gj):>9.1f}{sum(sh):>9.2f}{area:>17.0f}{tot_gj:>19.1f}{100*sum(gj)/tot_gj:>11.2f}")

# ---------- CHECK 3: colder zone must not use less heating / less total ----------
TOT = {
 "Large Office":      {"2004": (172.56,176.34), "2013": (197.21,198.89), "2016": (185.01,185.46), "2019": (177.01,176.53)},
 "Medium Office":     {"2004": (170.03,172.87), "2013": (133.57,125.69), "2016": (124.31,111.29), "2019": (121.53,105.36)},
 "Large Hotel":       {"2004": (286.44,302.21), "2013": (310.74,332.16), "2016": (306.73,328.09), "2019": (284.44,299.28)},
 "Small Hotel":       {"2004": (230.92,244.80), "2013": (269.56,280.56), "2016": (240.94,249.71), "2019": (232.24,240.69)},
 "Stand-Alone Retail":{"2004": (109.78,110.73), "2013": (185.02,195.75), "2016": (215.74,184.83), "2019": (212.45,181.54)},
 "Strip Mall":        {"2004": (147.00,153.00), "2013": (251.57,263.91), "2016": (237.92,246.94), "2019": (235.26,244.73)},
}
print("\nCHECK 3 -- CZ7 (International Falls / Duluth) vs CZ6A: colder should be >= ")
print(f"{'prototype':<21}" + "".join(f"{v:>12}" for v in ["2004","2013","2016","2019"]))
for b, d in TOT.items():
    cells = []
    for v in ["2004","2013","2016","2019"]:
        a, c = d[v]
        cells.append(f"{100*(c-a)/a:+.1f}%" + ("!" if c < a else " "))
    print(f"{b:<21}" + "".join(f"{c:>12}" for c in cells))

print("\nCHECK 4 -- 2004 -> 2019 change (newer code should be <= older)")
for b, d in TOT.items():
    a4, c4 = d["2004"]; a9, c9 = d["2019"]
    print(f"{b:<21}6A {a4:7.2f} -> {a9:7.2f} ({100*(a9-a4)/a4:+6.1f}%)   "
          f"7 {c4:7.2f} -> {c9:7.2f} ({100*(c9-c4)/c4:+6.1f}%)")

print("\nCHECK 5 -- heating EUI, CZ6A vs CZ7 (kWh/m2)")
heat = {"Large Office":(0.41,0.42),"Medium Office":(18.41,15.75),"Large Hotel":(4.27,5.75),
        "Small Hotel":(23.51,27.82),"Stand-Alone Retail":(53.00,39.13),"Strip Mall":(66.72,73.02)}
for b,(a,c) in heat.items():
    print(f"{b:<21}6A {a:7.2f}   7 {c:7.2f}   {'INVERTED' if c<a else 'ok'}")
