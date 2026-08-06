import re,html,glob,os
def site(fn):
    txt=open(fn,encoding="utf-8",errors="replace").read()
    for m in re.finditer(r"<table[^>]*>(.*?)</table>", txt, re.S|re.I):
        h=re.sub(r"<[^>]+>"," ",txt[max(0,m.start()-900):m.start()])
        h=html.unescape(re.sub(r"\s+"," ",h)).strip()
        if "Site and Source Energy" not in h[-260:]: continue
        for r in re.finditer(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S|re.I):
            c=[html.unescape(re.sub(r"<[^>]+>","",x)).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r.group(1), re.S|re.I)]
            if c and c[0].startswith("Total Site Energy") and len(c)>2: return float(c[2])
RV05={"OfficeMedium_STD2019":(121.53,105.36),"RetailStandalone_STD2019":(212.45,181.54)}
print(f"{'prototype':<26}{'6A Roch':>10}{'7 IntFls':>10}{'CZ7-6A':>9}   RV05 6A / 7      delta%")
for d,(ra,rb) in RV05.items():
    a=site(glob.glob(os.path.join(d,"*Rochester.table.htm"))[0])/3.6
    b=site(glob.glob(os.path.join(d,"*InternationalFalls.table.htm"))[0])/3.6
    print(f"{d:<26}{a:>10.2f}{b:>10.2f}{100*(b-a)/a:>8.1f}%   {ra:.2f} / {rb:.2f}   "
          f"{100*(ra-a)/a:+.1f}% / {100*(rb-b)/b:+.1f}%")
