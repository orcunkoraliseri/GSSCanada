import json, io, csv, sys, collections, os, statistics
HERE=os.path.dirname(os.path.abspath(__file__)); OUTD=os.path.dirname(HERE)
EU="C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/IT-BOL-GALVANI2_win_2026-10-05"
res={r["stem"]:r for r in json.load(io.open(OUTD+"/bol5_check_results.json",encoding="utf-8"))}
reason={}
for ln in io.open(EU+"/changed_stems.txt",encoding="utf-8"):
    p=ln.rstrip("\r\n").split("\t"); reason[p[0]]=p[1]
prep=list(csv.DictReader(io.open(EU+"/prepared_buildings.csv",encoding="utf-8",newline="")))
bid={r["stem"]:r["building_id"] for r in prep}
print("prepared rows",len(prep),"unique stems",len(set(bid)),"unique bid",len(set(bid.values())))
dc={r["building_id"]:r for r in csv.DictReader(io.open(EU+"/dwelling_counts_2026-10-05.csv",encoding="utf-8",newline=""))}
print("dwelling rows",len(dc),"sources",collections.Counter(r["dwellings_source"] for r in dc.values()))
so=sum(int(r["old_count"]) for r in dc.values()); sn=sum(int(r["new_count"]) for r in dc.values())
print("their sums old",so,"new",sn)
rows=[]
for st,r in res.items():
    d=dc[bid[st]]
    rows.append(dict(stem=st,reason=reason[st],building_id=bid[st],theirs_old=int(d["old_count"]),theirs_new=int(d["new_count"]),src=d["dwellings_source"],
      flats_old=r["flats_old"],flats_new=r["flats_new"],floors_old=r["floors_old"],floors_new=r["floors_new"],zones_old=r["zones_old"],zones_new=r["zones_new"],
      reason_old=r["zone_reason_old"],reason_new=r["zone_reason_new"],surf_old=r["surf_old"],surf_new=r["surf_new"],area_old=round(r["area_old"],3),area_new=round(r["area_new"],3),
      win_old=r["win_old"],win_new=r["win_new"],warea_old=round(r["warea_old"],3),warea_new=round(r["warea_new"],3),
      outwall_old=round(r["out_wall_old"],3),outwall_new=round(r["out_wall_new"],3),roof_old=round(r["roof_old"],3),roof_new=round(r["roof_new"],3),ground_old=round(r["ground_old"],3),ground_new=round(r["ground_new"],3),
      cons_same=r["cons_same"],bbox_dev_xy=round(r["bbox_dev_xy"],6),bbox_dev_z=round(r["bbox_dev_z"],3),shade_ok=int(r["shade_shift_bad"]==0 and r["shade_old"]==r["shade_new"]),
      surf_same_name=r["surf_same_name"],surf_same_exact=r["surf_same_name_exact_shift"],exact_shift_all=r["exact_shift_all_vertices"]))
with io.open(OUTD+"/bol5_check_per_stem.csv","w",encoding="utf-8",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0]),lineterminator="\n"); w.writeheader(); w.writerows(rows)
S=lambda rs,k: sum(x[k] for x in rs)
for g in ("origin_shift","flat_count+origin_shift"):
    rs=[x for x in rows if x["reason"]==g]
    print("=====",g,len(rs))
    print(" their old->new:",S(rs,"theirs_old"),S(rs,"theirs_new"),"; theirs old!=new stems:",sum(1 for x in rs if x["theirs_old"]!=x["theirs_new"]))
    print(" OUR flats (conditioned zones read by our zone map) old->new:",S(rs,"flats_old"),S(rs,"flats_new"),"; stems flats changed:",sum(1 for x in rs if x["flats_old"]!=x["flats_new"]),"up",sum(1 for x in rs if x["flats_new"]>x["flats_old"]),"down",sum(1 for x in rs if x["flats_new"]<x["flats_old"]))
    print(" zones (incl non-cond) old->new:",S(rs,"zones_old"),S(rs,"zones_new"))
    print(" floors(sum of per-building floor counts) old->new:",S(rs,"floors_old"),S(rs,"floors_new"),"; stems floors changed",sum(1 for x in rs if x["floors_old"]!=x["floors_new"]))
    print(" zone_reason old nonempty:",sum(1 for x in rs if x["reason_old"]),"new nonempty:",sum(1 for x in rs if x["reason_new"]))
    print(" our flats_old != their old_count:",sum(1 for x in rs if x["flats_old"]!=x["theirs_old"]),"; our flats_new != their new_count:",sum(1 for x in rs if x["flats_new"]!=x["theirs_new"]))
    print(" surfaces",S(rs,"surf_old"),S(rs,"surf_new"),"; area sum",round(S(rs,"area_old"),2),round(S(rs,"area_new"),2),"; windows",S(rs,"win_old"),S(rs,"win_new"),"; window area",round(S(rs,"warea_old"),2),round(S(rs,"warea_new"),2))
    print(" outdoor wall m2",round(S(rs,"outwall_old"),2),round(S(rs,"outwall_new"),2),"; roof",round(S(rs,"roof_old"),2),round(S(rs,"roof_new"),2),"; ground floor",round(S(rs,"ground_old"),2),round(S(rs,"ground_new"),2))
    print(" constructions same:",S(rs,"cons_same"),"of",len(rs))
    print(" bbox xy dev>1e-6:",sum(1 for x in rs if x["bbox_dev_xy"]>1e-6),"max",max(x["bbox_dev_xy"] for x in rs),"; bbox z dev>1e-6:",sum(1 for x in rs if x["bbox_dev_z"]>1e-6),"max",max(x["bbox_dev_z"] for x in rs),"; shade not ok:",sum(1 for x in rs if not x["shade_ok"]))
    print(" exact shift on all vertices:",S(rs,"exact_shift_all"))
    print(" same-name surfaces",S(rs,"surf_same_name"),"exact shift",S(rs,"surf_same_exact"))
allf=[x for x in rows if x["reason"]!="origin_shift"]
print("per-stem flats new-old: min",min(x["flats_new"]-x["flats_old"] for x in allf),"max",max(x["flats_new"]-x["flats_old"] for x in allf),"median",statistics.median(x["flats_new"]-x["flats_old"] for x in allf))
print("largest building new flats:",max(allf,key=lambda x:x["flats_new"])["stem"],max(x["flats_new"] for x in allf))
print("total all stems OUR flats old->new",S(rows,"flats_old"),S(rows,"flats_new"),"theirs",S(rows,"theirs_old"),S(rows,"theirs_new"))
print("stems whose zone_reason_new nonempty:",[ (x["stem"],x["zones_new"],x["flats_new"]) for x in rows if x["reason_new"]][:20], "count",sum(1 for x in rows if x["reason_new"]))
print("stems whose zone_reason_old nonempty:",sum(1 for x in rows if x["reason_old"]))
mism=[x for x in rows if x["flats_new"]!=x["theirs_new"]]
print("mismatch our-new vs their-new",len(mismatch:=mism), [ (x["stem"],x["flats_new"],x["theirs_new"],x["reason_new"]) for x in mism][:15])
mism=[x for x in rows if x["flats_old"]!=x["theirs_old"]]
print("mismatch our-old vs their-old",len(mism), [ (x["stem"],x["flats_old"],x["theirs_old"],x["reason_old"]) for x in mism][:15])
