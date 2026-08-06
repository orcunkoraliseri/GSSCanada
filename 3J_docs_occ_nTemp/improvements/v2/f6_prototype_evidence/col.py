import re, html
txt=open("ASHRAE901_HotelLarge_STD2019_Rochester.table.htm",encoding="utf-8",errors="replace").read()
for m in re.finditer(r"<table[^>]*>(.*?)</table>", txt, re.S|re.I):
    head=re.sub(r"<[^>]+>"," ",txt[max(0,m.start()-900):m.start()])
    head=html.unescape(re.sub(r"\s+"," ",head)).strip()
    if "End Uses" not in head[-260:]: continue
    rows=[]
    for r in re.finditer(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S|re.I):
        c=[html.unescape(re.sub(r"<[^>]+>","",x)).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r.group(1), re.S|re.I)]
        if c: rows.append(c)
    if len(rows)<4: continue
    hdr=rows[0]; ie=hdr.index("Electricity [GJ]"); ng=hdr.index("Natural Gas [GJ]")
    RV={"Heating":174.43,"Cooling":198.87,"Interior Lighting":152.06,"Exterior Lighting":54.07,
        "Interior Equipment":631.08,"Exterior Equipment":178.81,"Fans":158.16,"Pumps":21.82,
        "Heat Recovery":32.93,"Water Systems":346.90,"Refrigeration":12.28}
    print(f"{'end use':<20}{'Elec GJ':>10}{'Gas GJ':>10}{'RV05':>10}{'Elec/RV05':>11}")
    te=0
    for r in rows[1:]:
        n=r[0].strip()
        if n not in RV: continue
        e=float(r[ie] or 0); g=float(r[ng] or 0); te+=e
        print(f"{n:<20}{e:>10.2f}{g:>10.2f}{RV[n]:>10.2f}{e/RV[n]:>11.4f}")
    print(f"{'TOTAL ELEC':<20}{te:>10.2f}{'':>10}{sum(RV.values()):>10.2f}{te/sum(RV.values()):>11.4f}")
    break
