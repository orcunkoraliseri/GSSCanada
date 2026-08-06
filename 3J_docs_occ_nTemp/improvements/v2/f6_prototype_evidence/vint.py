import re,html,glob,os
def site(fn):
    txt=open(fn,encoding="utf-8",errors="replace").read()
    for m in re.finditer(r"<table[^>]*>(.*?)</table>", txt, re.S|re.I):
        head=re.sub(r"<[^>]+>"," ",txt[max(0,m.start()-900):m.start()])
        head=html.unescape(re.sub(r"\s+"," ",head)).strip()
        if "Site and Source Energy" not in head[-260:]: continue
        for r in re.finditer(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S|re.I):
            c=[html.unescape(re.sub(r"<[^>]+>","",x)).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r.group(1), re.S|re.I)]
            if c and c[0].startswith("Total Site Energy") and len(c)>2: return float(c[2])
    return None
RV05={"2013":(310.74,332.16),"2016":(306.73,328.09),"2019":(284.44,299.28)}
print(f"{'vintage':<9}{'6A Rochester':>15}{'7 IntFalls':>13}{'CZ7-CZ6A':>11}   RV05 6A / 7        delta%")
for v in ["2013","2016","2019"]:
    d="HotelLarge_STD"+v if v!="2019" else "."
    r=glob.glob(os.path.join(d,"*Rochester.table.htm"))[0]
    i=glob.glob(os.path.join(d,"*InternationalFalls.table.htm"))[0]
    a,b=site(r)/3.6, site(i)/3.6
    ra,rb=RV05[v]
    print(f"{v:<9}{a:>15.2f}{b:>13.2f}{100*(b-a)/a:>10.1f}%   {ra:.2f} / {rb:.2f}   "
          f"{100*(ra-a)/a:+.2f}% / {100*(rb-b)/b:+.2f}%")
