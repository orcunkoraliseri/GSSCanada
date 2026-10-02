import json, io, csv, sys, collections, os
HERE=os.path.dirname(os.path.abspath(__file__)); OUTD=os.path.dirname(HERE)
EU="C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/IT-BOL-GALVANI2_win_2026-10-05"
res=json.load(io.open(OUTD+"/bol5_check_results.json",encoding="utf-8"))
reason={}
for ln in io.open(EU+"/changed_stems.txt",encoding="utf-8"):
    p=ln.rstrip("\r\n").split("\t"); reason[p[0]]=p[1]
md5new={}
for ln in io.open(EU+"/md5_2026-10-05.txt",encoding="utf-8"):
    p=ln.split()
    if p: md5new[p[-1][:-4]]=p[0]
print("n",len(res),"reasons",collections.Counter(reason.values()), "stems in changed not in md5", len(set(reason)-set(md5new)), "md5 not in changed", len(set(md5new)-set(reason)))
print("md5 own == md5 file:", sum(1 for r in res if r["md5_new"]==md5new[r["stem"]]), "of", len(res), "; bytes equal old/new:", sum(r["bytes_equal"] for r in res))
g=collections.defaultdict(list)
for r in res: g[reason[r["stem"]]].append(r)
for k,rs in g.items():
    print("=== group",k,len(rs))
    print(" exact_shift_all_vertices:",sum(r["exact_shift_all_vertices"] for r in rs),"of",len(rs))
    print(" obj_aligned:",sum(r["obj_aligned"] for r in rs))
    print(" max dx,dy,dz over aligned stems:",max(r["shift_max_dx"] for r in rs if r["obj_aligned"]) if any(r["obj_aligned"] for r in rs) else None, max(r["shift_max_dy"] for r in rs if r["obj_aligned"]) if any(r["obj_aligned"] for r in rs) else None, max(r["shift_max_dz"] for r in rs if r["obj_aligned"]) if any(r["obj_aligned"] for r in rs) else None)
    print(" noncoord field diffs total (aligned):",sum(r["noncoord_field_diffs"] for r in rs if r["obj_aligned"]))
    print(" any_diff_noncoord stems:",sum(r["any_diff_noncoord"] for r in rs))
    print(" shading: stems with shade_shift_bad>0:",sum(1 for r in rs if r["shade_shift_bad"]>0),"; stems shade_old!=shade_new:",sum(1 for r in rs if r["shade_old"]!=r["shade_new"]),"; common sum",sum(r["shade_common"] for r in rs),"; old",sum(r["shade_old"] for r in rs),"new",sum(r["shade_new"] for r in rs))
    print(" bbox dev xy max:",max(r["bbox_dev_xy"] for r in rs),"; bbox dev z max:",max(r["bbox_dev_z"] for r in rs))
    print(" surfaces same name",sum(r["surf_same_name"] for r in rs),"exact shift",sum(r["surf_same_name_exact_shift"] for r in rs))
    print(" bld same",sum(r["bld_same"] for r in rs),"zone origin all zero new",sum(r["zone_origin_all_zero_new"] for r in rs))
    bk=collections.Counter()
    for r in rs:
        for kk,v in r["big_kinds_new"].items(): bk[kk]+=1
    print(" stems with a numeric field >50000 in NEW, by object kind:",dict(bk))
    print(" new min/max x,y:",min(r["new_min_x"] for r in rs),max(r["new_max_x"] for r in rs),min(r["new_min_y"] for r in rs),max(r["new_max_y"] for r in rs))
