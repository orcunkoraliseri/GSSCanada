import json, io, csv, os, collections
HERE=os.path.dirname(os.path.abspath(__file__)); OUTD=os.path.dirname(HERE)
res={r["stem"]:r for r in json.load(io.open(OUTD+"/bol5_check_results.json",encoding="utf-8"))}
rows=[r for r in csv.DictReader(io.open(OUTD+"/bol5_check_per_stem.csv",encoding="utf-8",newline="")) if r["reason"]!="origin_shift"]
def f(x): return float(x)
# height: new max z - old max z needs bbox; recompute from json? we only have dev. use floors dev sign via outwall? read z from json not stored; use roof z? skip -> use floors_new-floors_old sign among z-dev stems
zd=[r for r in rows if f(r["bbox_dev_z"])>1e-6]
print("z-dev stems",len(zd),"floors_new>old",sum(1 for r in zd if int(r["floors_new"])>int(r["floors_old"])),"floors_new<old",sum(1 for r in zd if int(r["floors_new"])<int(r["floors_old"])),"equal",sum(1 for r in zd if r["floors_new"]==r["floors_old"]),"whole(0 floors) new/old",sum(1 for r in zd if int(r["floors_new"])==0),sum(1 for r in zd if int(r["floors_old"])==0))
nz=[r for r in rows if f(r["bbox_dev_z"])<=1e-6]
def rel(r,k):
    o=f(r[k+"_old"]); n=f(r[k+"_new"]); return (n-o)/o if o>0 else (0 if n==0 else float("inf"))
print("z-dev==0 stems:",len(nz),"; with outwall change >1%:",sum(1 for r in nz if abs(rel(r,"outwall"))>0.01),">5%:",sum(1 for r in nz if abs(rel(r,"outwall"))>0.05))
print("z-dev>0 stems with outwall change >1%:",sum(1 for r in zd if abs(rel(r,"outwall"))>0.01),"of",len(zd))
print("outwall old==0 & new>0:",[ (r["stem"],r["outwall_new"]) for r in rows if f(r["outwall_old"])==0 and f(r["outwall_new"])>0][:10], "old>0 & new==0:",[(r["stem"],r["outwall_old"]) for r in rows if f(r["outwall_old"])>0 and f(r["outwall_new"])==0][:10])
# direction among z-dev==0 with outwall change >5%
up=sum(1 for r in nz if rel(r,"outwall")>0.05); dn=sum(1 for r in nz if rel(r,"outwall")<-0.05)
print("z-dev==0: outwall up >5%:",up,"down >5%:",dn)
# window share
print("window area / outwall: old",round(sum(f(r["warea_old"]) for r in rows)/sum(f(r["outwall_old"]) for r in rows),4),"new",round(sum(f(r["warea_new"]) for r in rows)/sum(f(r["outwall_new"]) for r in rows),4))
# floors: conditioned floor area (ground only) etc. not here
ex=[r for r in nz if abs(rel(r,"outwall"))>0.2][:5]
print("examples z-dev==0, outwall change >20%:",[(r["stem"],r["outwall_old"],r["outwall_new"],r["floors_old"],r["floors_new"],r["flats_old"],r["flats_new"],r["surf_old"],r["surf_new"]) for r in ex])
