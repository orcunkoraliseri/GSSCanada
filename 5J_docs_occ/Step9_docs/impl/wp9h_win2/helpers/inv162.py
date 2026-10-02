import sys,importlib,math,csv
sys.path.insert(0,"C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/tools")
W=importlib.import_module("5thJ_modelA_win2_check"); M=W.M
d="ES-MAD-BERRUGUETE"
rows=list(csv.DictReader(open(W.OUT+"/win2_check_per_building.csv",encoding="utf-8")))
hdr=rows[0].keys()
bad=[r["stem"] for r in rows if r["district"]==d and int(r["wall_out_in"])>0]
print("buildings with inward walls (new):",len(bad), "sum",sum(int(r["wall_out_in"]) for r in rows if r["district"]==d))
kept=0;tot=0;ex=[]
for stem in bad:
    tn=M.read_text(W.folder(d,W.NEW)+"/idfs/"+stem+".idf"); to=M.read_text(W.folder(d,W.OLD)+"/idfs/"+stem+".idf")
    on={o["fields"][0]:M.surface_of(o) for o in M.objects(tn) if o["kw"]=="BUILDINGSURFACE:DETAILED"}
    oo={o["fields"][0]:M.surface_of(o) for o in M.objects(to) if o["kw"]=="BUILDINGSURFACE:DETAILED"}
    floors={}
    for s in on.values():
        if s["type"]=="floor": floors.setdefault(s["zone"],[]).append(s["verts"])
    for n,s in on.items():
        if s["type"]=="wall" and s["bc"]=="outdoors":
            nr=W.newell(s["verts"]); nn=math.hypot(nr[0],nr[1])
            wx=sum(v[0] for v in s["verts"])/len(s["verts"]); wy=sum(v[1] for v in s["verts"])/len(s["verts"])
            res=[]
            for dist in (0.05,0.2,0.5):
                pi=any(W.inside((wx+dist*nr[0]/nn,wy+dist*nr[1]/nn),pl) for pl in floors[s["zone"]])
                mi=any(W.inside((wx-dist*nr[0]/nn,wy-dist*nr[1]/nn),pl) for pl in floors[s["zone"]])
                res.append("in" if pi and not mi else "out" if mi and not pi else "unc")
            if res[0]=="in":
                tot+=1
                same=[(round(a,6)) for v in s["verts"] for a in v]==[(round(a,6)) for v in oo[n]["verts"] for a in v]
                kept+=same
                if len(ex)<6: ex.append((stem,n,res,same,len(s["verts"]),M.classify_wall(s["verts"])))
print("inward walls inspected",tot,"of them same vertex sequence as old base (kept):",kept)
for e in ex: print(e)
