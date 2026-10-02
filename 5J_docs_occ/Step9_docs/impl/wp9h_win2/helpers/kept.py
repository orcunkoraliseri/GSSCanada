import sys,importlib,math,collections
sys.path.insert(0,"C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/tools")
W=importlib.import_module("5thJ_modelA_win2_check"); M=W.M
import csv
for d in W.DISTRICTS:
    stems=[r["stem"] for r in W.read_rows(W.folder(d,W.NEW)+"/prepared_buildings.csv")]
    cnt=collections.Counter(); area=collections.Counter(); tot=0; totarea=0.0; bld=set(); flats=set()
    keptbuild=collections.Counter()
    for stem in stems:
        tn=M.read_text(W.folder(d,W.NEW)+"/idfs/"+stem+".idf"); to=M.read_text(W.folder(d,W.OLD)+"/idfs/"+stem+".idf")
        objs=M.objects(tn)
        on={o["fields"][0]:M.surface_of(o) for o in M.objects(to) if o["kw"]=="BUILDINGSURFACE:DETAILED"}
        S={};floors={};fed={};fup={}
        for o in objs:
            if o["kw"]=="BUILDINGSURFACE:DETAILED":
                s=M.surface_of(o);S[s["name"]]=s
                if s["type"]=="floor":
                    floors.setdefault(s["zone"],[]).append(s["verts"]); vv=s["verts"]
                    fup[s["zone"]]=fup.get(s["zone"],0) or (W.newell(vv)[2]>0)
                    for i in range(len(vv)): fed.setdefault(s["zone"],set()).add((W._k(vv[i]),W._k(vv[(i+1)%len(vv)])))
        for n,s in S.items():
            if s["type"]=="wall" and s["bc"]=="outdoors":
                tot+=1; a=W.area3(s["verts"]); totarea+=a
                same=[W._k(v) for v in s["verts"]]==[W._k(v) for v in on[n]["verts"]]
                nr=W.newell(s["verts"]);nn=math.hypot(nr[0],nr[1])
                wx=sum(v[0] for v in s["verts"])/len(s["verts"]);wy=sum(v[1] for v in s["verts"])/len(s["verts"])
                pi=any(W.inside((wx+0.05*nr[0]/nn,wy+0.05*nr[1]/nn),pl) for pl in floors.get(s["zone"],[]))
                mi=any(W.inside((wx-0.05*nr[0]/nn,wy-0.05*nr[1]/nn),pl) for pl in floors.get(s["zone"],[]))
                pc="in" if pi and not mi else "out" if mi and not pi else "unc"
                ec=W.edge_class(s,fed,fup)
                if same:
                    cnt[("kept",pc,ec)]+=1; area[("kept",pc,ec)]+=a; bld.add(stem)
                else:
                    cnt[("rev",pc,ec)]+=1
    print(d,"outdoor walls",tot,"area %.0f"%totarea)
    kept=sum(v for k,v in cnt.items() if k[0]=="kept"); ka=sum(v for k,v in area.items())
    print(" kept (same vertex sequence as old base):",kept,"area %.0f m2 = %.2f %% of outdoor wall area"%(ka,100*ka/totarea),"in",len(bld),"buildings")
    for k in sorted(cnt): print("  ",k,cnt[k],"area %.0f"%area.get(k,0))
