import json, io, csv, os, collections
HERE=os.path.dirname(os.path.abspath(__file__)); OUTD=os.path.dirname(HERE)
res={r["stem"]:r for r in json.load(io.open(OUTD+"/bol5_check_results.json",encoding="utf-8"))}
rows=list(csv.DictReader(io.open(OUTD+"/bol5_check_per_stem.csv",encoding="utf-8",newline="")))
fc=[r for r in rows if r["reason"]!="origin_shift"]
print("aligned among flat_count:",[(r["stem"],r["flats_old"],r["flats_new"],r["theirs_old"],r["theirs_new"],res[r["stem"]]["noncoord_diff_kinds"]) for r in fc if res[r["stem"]]["obj_aligned"]])
print("flats equal (ours) in flat_count:",[(r["stem"],r["flats_old"],r["flats_new"],r["theirs_old"],r["theirs_new"],r["reason_old"],r["reason_new"]) for r in fc if r["flats_old"]==r["flats_new"]])
print("cons differ:",[(r["stem"],sorted(res[r["stem"]]["flats_list_old"])[:0]) for r in fc if r["cons_same"]=="0"])
# bbox xy dev > 1e-6
bx=[(r["stem"],r["bbox_dev_xy"]) for r in fc if float(r["bbox_dev_xy"])>1e-6]
print("bbox xy dev stems",len(bx),"values",sorted(set(v for _,v in bx))[:10],"max",max(float(v) for _,v in bx))
bz=[(r["stem"],r["bbox_dev_z"],r["floors_old"],r["floors_new"]) for r in fc if float(r["bbox_dev_z"])>1e-6]
print("bbox z dev stems",len(bz),"; values",collections.Counter(v for _,v,_,_ in bz).most_common(12))
print("  of those with floors_old==floors_new:",sum(1 for _,_,a,b in bz if a==b),"; floors changed but z dev==0:",sum(1 for r in fc if r["floors_old"]!=r["floors_new"] and float(r["bbox_dev_z"])<=1e-6))
# footprint (ground floor) and roof area relative change per stem
def rel(r,k): 
    o=float(r[k+"_old"]); n=float(r[k+"_new"]); return (n-o)/o if o>0 else (0 if n==0 else 9)
for k in ("ground","roof","outwall","warea"):
    v=[rel(r,k) for r in fc]
    print(k,"stems with |rel change|>0.1%:",sum(1 for x in v if abs(x)>1e-3),">1%:",sum(1 for x in v if abs(x)>1e-2),">5%:",sum(1 for x in v if abs(x)>5e-2),"max",max(v),"min",min(v))
# wall/ roof flagged
big=sorted(fc,key=lambda r:-abs(rel(r,"ground")))[:6]
print("largest ground-floor area change:",[(r["stem"],r["ground_old"],r["ground_new"],r["floors_old"],r["floors_new"]) for r in big])
# flats stats
import statistics
print("new flats per building (all stems, ours, usable only): median",statistics.median(int(r["flats_new"]) for r in rows if int(r["flats_new"])>0),"max",max(int(r["flats_new"]) for r in rows))
print("old flats per building median",statistics.median(int(r["flats_old"]) for r in rows if int(r["flats_old"])>0))
print("buildings with >=100 new flats:",sum(1 for r in rows if int(r["flats_new"])>=100),"; >=25:",sum(1 for r in rows if int(r["flats_new"])>=25))
