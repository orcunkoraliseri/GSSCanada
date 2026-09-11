"""Read-only re-classification of C2 failing buildings from the built IDF + eplusout.err.
Nothing is retried, patched, moved or scored. Input is the output of ring_extract.sh."""
import sys, math, csv
from analyze_rings import parse, edges, same_set

E_COINCIDENT = 0.010     # EnergyPlus coincident-vertex scale (S18.23)
E_COLLINEAR  = 0.0127    # EnergyPlus collinear-vertex removal tolerance

def perp(a,b,c):
    ac = math.dist(a,c)
    if ac == 0: return 0.0
    ab=[b[i]-a[i] for i in range(3)]; av=[c[i]-a[i] for i in range(3)]
    cr=[ab[1]*av[2]-ab[2]*av[1], ab[2]*av[0]-ab[0]*av[2], ab[0]*av[1]-ab[1]*av[0]]
    return math.sqrt(sum(x*x for x in cr))/ac

def degen(v):
    e = edges(v)
    short = sum(1 for x in e if x < E_COINCIDENT)
    coll  = sum(1 for i in range(len(v)) if perp(v[i-1], v[i], v[(i+1)%len(v)]) < E_COLLINEAR)
    return short, coll, min(e)

def rows_for(path, dist):
    B = parse(path); out=[]
    for bid, d in B.items():
        c = d["counts"]; seen=set(); P=[]
        for base,other,nr,mr in d["pairs"]:
            k=tuple(sorted([base.upper(),other.upper()]))
            if k in seen: continue
            seen.add(k)
            sb=d["surf"].get(base.upper()); so=d["surf"].get(other.upper())
            if not sb or not so: continue
            vb,vo=sb["v"],so["v"]
            shb,cob,mnb = degen(vb); sho,coo,mno = degen(vo)
            P.append(dict(ident=same_set(vb,vo), W=len(vb), Wo=len(vo), nr=nr, mr=mr,
                          short=shb, coll=cob, mn=min(mnb,mno),
                          degen_ok=(shb+cob)>0, delta=abs(nr-mr)))
        if not P:
            if c.get("cn",0) > 0: fam = "C_OUR_CONSTRUCTION"
            elif c.get("cc",0) > 0 and c.get("co",0) > 0: fam = "A_COINCIDENT_DELETION"
            elif c.get("za",0) > 0: fam = "E_ZERO_AREA"
            else: fam = "UNEXPLAINED_NO_PAIRS"
            out.append(dict(district=dist, building=bid, family=fam, n_pairs=0,
                            pairs_rings_identical=0, pairs_rings_differ=0,
                            pairs_with_degenerate_vertices=0, all_delta_one="",
                            min_edge_m="", vm=c.get("vm"), np=c.get("np"), za=c.get("za"),
                            cn=c.get("cn"), cc=c.get("cc"), co=c.get("co")))
            continue
        ident = sum(1 for p in P if p["ident"]); differ = len(P)-ident
        dgn   = sum(1 for p in P if p["degen_ok"])
        d1    = all(p["delta"]==1 for p in P)
        if differ == 0 and dgn == len(P):
            fam = "B_DEGENERATE_VERTEX_ASYMMETRIC_READ"
        elif differ > 0:
            fam = "D_RINGS_DIFFER_CONTAMINATION"
        else:
            fam = "UNEXPLAINED_VM"
        out.append(dict(district=dist, building=bid, family=fam, n_pairs=len(P),
                        pairs_rings_identical=ident, pairs_rings_differ=differ,
                        pairs_with_degenerate_vertices=dgn, all_delta_one=d1,
                        min_edge_m="%.9f"%min(p["mn"] for p in P),
                        vm=c.get("vm"), np=c.get("np"), za=c.get("za"),
                        cn=c.get("cn"), cc=c.get("cc"), co=c.get("co")))
    return out

if __name__=="__main__":
    R = rows_for(sys.argv[1],"ES") + rows_for(sys.argv[2],"IT")
    fn=list(R[0].keys())
    w=csv.DictWriter(open(sys.argv[3],"w",newline="",encoding="utf-8"),fieldnames=fn); w.writeheader()
    for r in R: w.writerow(r)
    from collections import Counter
    print("=== family x district ===")
    for k,v in sorted(Counter((r["district"],r["family"]) for r in R).items()):
        print("  %-3s %-40s %d bldgs, %d cells"%(k[0],k[1],v,v*10))
    print("=== delta==1 on every pair? ===")
    print(" ", Counter(r["all_delta_one"] for r in R if r["n_pairs"]))
