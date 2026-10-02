import csv
OPP={"N":"S","S":"N","E":"W","W":"E"}
for d in ("ES-MAD-BERRUGUETE","IT-BOL-GALVANI2"):
    a=list(csv.DictReader(open("static/flats_%s.csv"%d,encoding="utf-8")))
    b=list(csv.DictReader(open("static_win2/flats_%s.csv"%d,encoding="utf-8")))
    cols=list(a[0].keys())
    orient=[c for c in cols if c.startswith("wall_") and c[5] in "NESW" or c.startswith("win_") and c[4] in "NESW"]
    other=[c for c in cols if c not in orient]
    keyeq=[(x["stem"],x["zone"]) for x in a]==[(x["stem"],x["zone"]) for x in b] if "zone" in cols else None
    print(d,"rows old",len(a),"new",len(b),"same order of (stem,zone):",keyeq)
    print(" orientation cols:",orient)
    neq=sum(1 for x,y in zip(a,b) if any(x[c]!=y[c] for c in other))
    print(" flats with any non-orientation column different:",neq)
    ch=0;mirror=0;partial=[];nosw=0;ex=None;noorient=0
    for x,y in zip(a,b):
        if any(x[c]!=y[c] for c in orient):
            ch+=1
            ok=all(abs(float(x["wall_%s_m2"%k])-float(y["wall_%s_m2"%OPP[k]]))<1e-3 and abs(float(x["win_%s_m2"%k])-float(y["win_%s_m2"%OPP[k]]))<1e-3 for k in "NESW")
            if ok:
                mirror+=1
                if ex is None and abs(float(x["wall_N_m2"])-float(x["wall_S_m2"]))>5 and min(float(x["wall_N_m2"]),float(x["wall_S_m2"]))>0.5 :
                    ex=(x["zone"],{k:(x["wall_%s_m2"%k],y["wall_%s_m2"%k]) for k in "NS"},{k:(x["win_%s_m2"%k],y["win_%s_m2"%k]) for k in "NS"})
            else: partial.append(x["zone"])
        else: noorient+=1
    print(" flats with orientation columns changed:",ch,"of",len(a),"; of those exactly N<->S and E<->W mirrored:",mirror,"; not an exact mirror:",len(partial),partial[:3]," unchanged (no outdoor wall or symmetric):",noorient)
    print(" example N/S swapped flat (old,new):",ex)
    # totals check: sum of wall area per flat equal
    print(" wall total per flat equal old/new:",all(abs(sum(float(x["wall_%s_m2"%k]) for k in "NESW")-sum(float(y["wall_%s_m2"%k]) for k in "NESW"))<1e-3 for x,y in zip(a,b)),
          "; window total per flat equal:",all(abs(sum(float(x["win_%s_m2"%k]) for k in "NESW")-sum(float(y["win_%s_m2"%k]) for k in "NESW"))<1e-3 for x,y in zip(a,b)))
    b1=open("static/buildings_%s.csv"%d,"rb").read(); b2=open("static_win2/buildings_%s.csv"%d,"rb").read()
    print(" buildings table byte-equal:",b1==b2)
