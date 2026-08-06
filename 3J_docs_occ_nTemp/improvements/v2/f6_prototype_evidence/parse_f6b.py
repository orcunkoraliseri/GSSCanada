"""V2-F6b. Correct End Uses parse: drop the non-energy Water [m3] column, keep fuel columns only.
Then compare against RV05's claimed Large Hotel end-use block."""
import re, html, os

FILES = {"6A Rochester": "ASHRAE901_HotelLarge_STD2019_Rochester.table.htm",
         "7 International Falls": "ASHRAE901_HotelLarge_STD2019_InternationalFalls.table.htm"}

# RV05's claimed Large Hotel 6A block: (label, GJ, share%, EUI kWh/m2) as tabled in RV05
RV05_6A = [("Heating", 174.43, 1.50, 4.27), ("Cooling", 198.87, 1.71, None),
           ("Interior Lighting", 152.06, 1.31, None), ("Exterior Lighting", 54.07, 0.47, None),
           ("Interior Equipment", 631.08, 5.43, 15.45), ("Exterior Equipment", 178.81, 1.54, None),
           ("Fans", 158.16, 1.36, None), ("Pumps", 21.82, 0.19, None),
           ("Heat Recovery", 32.93, 0.28, None), ("Water Systems", 346.90, 2.99, None),
           ("Refrigeration", 12.28, 0.11, None)]

def tables(txt):
    for m in re.finditer(r"<table[^>]*>(.*?)</table>", txt, re.S | re.I):
        head = re.sub(r"<[^>]+>", " ", txt[max(0, m.start()-900):m.start()])
        head = html.unescape(re.sub(r"\s+", " ", head)).strip()
        rows = []
        for r in re.finditer(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S | re.I):
            cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                     for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r.group(1), re.S | re.I)]
            if cells:
                rows.append(cells)
        yield head, rows

for zone, fn in FILES.items():
    txt = open(fn, encoding="utf-8", errors="replace").read()
    area = site_mj = None
    hdr = None; body = []
    for head, rows in tables(txt):
        tail = head[-260:]
        if "Site and Source Energy" in tail and site_mj is None:
            for row in rows:
                if row[0].startswith("Total Site Energy") and len(row) > 2:
                    site_mj = float(row[2])
        if "Building Area" in tail and area is None:
            for row in rows:
                if row[0].strip().lower().startswith("net conditioned building area"):
                    area = float(row[1])
        if "End Uses" in tail and hdr is None and len(rows) > 3:
            hdr = rows[0]; body = rows[1:]

    keep = [i for i, h in enumerate(hdr[1:], start=1) if "[m3]" not in h.lower()]
    print(f"\n=== {zone} ===   area {area} m2   Total Site Energy {site_mj} MJ/m2 "
          f"= {site_mj/3.6:.2f} kWh/m2.yr")
    print(f"    End Uses columns kept: {[hdr[i] for i in keep]}")
    tot = None; rowsum = 0.0; got = {}
    for row in body:
        vals = []
        for i in keep:
            try: vals.append(float(row[i]))
            except (ValueError, IndexError): vals.append(0.0)
        s = sum(vals)
        nm = row[0].strip()
        if nm == "Total End Uses": tot = s
        elif nm and s: rowsum += s; got[nm] = s
    print(f"    sum of end uses {rowsum:,.2f} GJ | 'Total End Uses' {tot:,.2f} GJ"
          f" | site total from EUI {site_mj*area/1000:,.2f} GJ")
    print(f"    coverage vs Total End Uses = {100*rowsum/tot:.2f} %"
          f" | vs site total = {100*rowsum/(site_mj*area/1000):.2f} %")
    if zone.startswith("6A"):
        print(f"\n    {'end use':<22}{'REAL GJ':>12}{'RV05 GJ':>12}{'ratio':>9}"
              f"{'REAL kWh/m2':>13}")
        for nm, gj, sh, eui in RV05_6A:
            r = got.get(nm)
            if r is None: continue
            print(f"    {nm:<22}{r:>12,.2f}{gj:>12,.2f}{r/gj:>9.2f}"
                  f"{r/3.6*1000/area:>13.2f}")
        print(f"    {'TOTAL':<22}{rowsum:>12,.2f}{sum(g for _,g,_,_ in RV05_6A):>12,.2f}"
              f"{rowsum/sum(g for _,g,_,_ in RV05_6A):>9.2f}")
