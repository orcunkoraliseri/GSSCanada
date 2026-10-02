import sys,importlib,math,csv
sys.path.insert(0,"C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/tools")
W=importlib.import_module("5thJ_modelA_win2_check"); M=W.M; W.NEW="win_2026-10-03"  # 9j: new base
SP="C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/Step9_docs/impl/wp9j_win3"
B=[("ES-MAD-BERRUGUETE","0275c53572b2ff9f"),("ES-MAD-BERRUGUETE","7307694dddf93fb6"),("IT-BOL-GALVANI2","504fa19567bbc2b7"),("IT-BOL-GALVANI2","b3f8d90890ff6314")]
out=open(SP+"/expected_azimuth.csv","w",newline="")
w=csv.writer(out,lineterminator="\n"); w.writerow(["district","stem","wall_name","point_class","edge_class","newell_az","geom_outward_az","order_in_idf"])
for d,stem in B:
    t=M.read_text(W.folder(d,W.NEW)+"/idfs/"+stem+".idf")
    objs=M.objects(t); S=[];floors={};fed={};fup={}
    for o in objs:
        if o["kw"]=="BUILDINGSURFACE:DETAILED":
            s=M.surface_of(o);S.append(s)
            if s["type"]=="floor":
                floors.setdefault(s["zone"],[]).append(s["verts"]);vv=s["verts"]
                fup[s["zone"]]=fup.get(s["zone"],0) or (W.newell(vv)[2]>0)
                for i in range(len(vv)): fed.setdefault(s["zone"],set()).add((W._k(vv[i]),W._k(vv[(i+1)%len(vv)])))
    k=0
    for s in S:
        if s["type"]=="wall" and s["bc"]=="outdoors":
            k+=1
            nr=W.newell(s["verts"]);nn=math.hypot(nr[0],nr[1])
            az=(math.degrees(math.atan2(nr[0],nr[1])))%360
            wx=sum(v[0] for v in s["verts"])/len(s["verts"]);wy=sum(v[1] for v in s["verts"])/len(s["verts"])
            pl=floors.get(s["zone"],[])
            if nn>0 and pl:
                pi=any(W.inside((wx+0.05*nr[0]/nn,wy+0.05*nr[1]/nn),p) for p in pl);mi=any(W.inside((wx-0.05*nr[0]/nn,wy-0.05*nr[1]/nn),p) for p in pl)
                pc="in" if pi and not mi else "out" if mi and not pi else "unc"
            else: pc="unc"
            ec=W.edge_class(s,fed,fup)
            g="" 
            if pc=="out" and ec in("out","none"): g="%.4f"%az
            elif pc=="in" and ec in ("in","none"): g="%.4f"%((az+180)%360)
            elif pc=="unc" and ec=="out": g="%.4f"%az
            elif pc=="unc" and ec=="in": g="%.4f"%((az+180)%360)
            w.writerow([d,stem,s["name"],pc,ec,"%.4f"%az,g,k])
out.close()
print(open(SP+"/expected_azimuth.csv").read().count("\n"))
