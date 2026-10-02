import os,sys,io,csv,collections,math
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); OUTD=os.path.dirname(HERE); IMP=os.path.dirname(OUTD)
sys.path.insert(0,os.path.join(IMP,"wp9k","helpers"))
from degen_lib import read_surfaces, degenerate
NEW="C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/IT-BOL-GALVANI2_win_2026-10-05"
reason={}
for ln in io.open(NEW+"/changed_stems.txt",encoding="utf-8"):
    p=ln.rstrip("\r\n").split("\t"); reason[p[0]]=p[1]
rows=list(csv.DictReader(io.open(OUTD+"/degenerate_bol5.csv",encoding="utf-8",newline="")))
kinds=collections.Counter(); bc=collections.Counter(); grp=collections.Counter(); area=[]; ext=[]
ref=set(r["stem"] for r in csv.DictReader(io.open(IMP+"/wp9k/degenerate_win3.csv",encoding="utf-8",newline="")) if r["district"]=="IT-BOL-GALVANI2")
for r in rows:
    grp[(reason[r["stem"]], r["stem"] in ref)]+=1
    s=read_surfaces(NEW+"/idfs/%s.idf"%r["stem"])
    names=set(r["names"].split(";"))
    for k,n,t,b,v in s:
        if degenerate(v,0.01,0.01) and n in names:
            kinds[(k[:5],t)]+=1; bc[b]+=1
            # extent: max pairwise vertex distance; area via newell
            sx=sy=sz=0.0
            for i in range(len(v)):
                x1,y1,z1=v[i];x2,y2,z2=v[(i+1)%len(v)]
                sx+=y1*z2-z1*y2; sy+=z1*x2-x1*z2; sz+=x1*y2-y1*x2
            a=0.5*math.sqrt(sx*sx+sy*sy+sz*sz); area.append(a)
            ext.append(max(math.dist(p,q) for p in v for q in v))
print("groups (reason, in old list):",dict(grp))
print("surface kinds:",dict(kinds)); print("boundary:",dict(bc))
print("n surfaces",len(area),"area max %.5f median %.6f"%(max(area),sorted(area)[len(area)//2]),"; extent (max vertex distance) max %.4f median %.4f min %.5f"%(max(ext),sorted(ext)[len(ext)//2],min(ext)))
print("surfaces with extent<0.0127:",sum(1 for e in ext if e<0.0127),"; >=0.0127:",sum(1 for e in ext if e>=0.0127))
print("per-stem n:",collections.Counter(int(r["n_degenerate"]) for r in rows))
print("windows flagged:",sum(1 for r in rows if "window" in r["boundary_types"]))
