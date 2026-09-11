import sys, math, csv, re
from collections import defaultdict

def parse(path):
    blds = {}
    cur = None
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        if line.startswith("###BUILDING|"):
            cur = line.split("|",1)[1].strip()
            blds[cur] = {"pairs": [], "surf": {}, "counts": {}, "np": [], "za": []}
        elif line.startswith("###PAIR|"):
            p = line.split("|")
            blds[cur]["pairs"].append((p[1].strip(), p[2].strip(), int(p[3]), int(p[4])))
        elif line.startswith("###COUNTS|"):
            for kv in line.split("|")[1:]:
                k,v = kv.split("="); blds[cur]["counts"][k]=int(v)
        elif line.startswith("###NP|"): blds[cur]["np"].append(line)
        elif line.startswith("###ZA|"): blds[cur]["za"].append(line)
        elif line.startswith("###SURF|"):
            f = line.split("|")[1:]
            name = f[0]
            # locate the coordinate tail: last k fields that are all numeric, k % 3 == 0
            nums = []
            i = len(f)-1
            while i >= 0:
                try: float(f[i])
                except ValueError: break
                nums.append(f[i]); i -= 1
            nums = list(reversed(nums))
            # drop leading numeric header fields (view factor / nverts) so len % 3 == 0
            while len(nums) % 3: nums = nums[1:]
            verts = [(float(nums[j]), float(nums[j+1]), float(nums[j+2])) for j in range(0,len(nums),3)]
            head = f[:len(f)-len(nums)]
            blds[cur]["surf"][name.upper()] = {"name":name, "head":head, "v":verts}
    return blds

def edges(v):
    return [math.dist(v[i], v[(i+1)%len(v)]) for i in range(len(v))]

def canon(v, tol=1e-6):
    q = [tuple(round(c/tol)*tol for c in p) for p in v]
    return sorted(q)

def same_set(a,b,tol=1e-6):
    if len(a)!=len(b): return False
    ca, cb = canon(a,tol), canon(b,tol)
    return all(math.dist(x,y) <= 1e-4 for x,y in zip(ca,cb))

def zone_of(head):
    # head = [name, surface_type, construction, zone, space?, obc, obc_object, ...]
    return head[3] if len(head)>3 else ""

def main():
 rows=[]
 for path,dist in ((sys.argv[1],"ES"),(sys.argv[2],"IT")):
     B = parse(path)
     for bid, d in B.items():
         pairs = d["pairs"]
         if not pairs:
             rows.append(dict(district=dist,building=bid,verdict="NO_VM_PAIRS",**d["counts"]))
             continue
         seen=set(); res=[]
         for base,other,nr,mr in pairs:
             key=tuple(sorted([base.upper(),other.upper()]))
             if key in seen: continue
             seen.add(key)
             sb=d["surf"].get(base.upper()); so=d["surf"].get(other.upper())
             if not sb or not so: res.append(("NOSURF",None)); continue
             vb,vo=sb["v"],so["v"]
             eb,eo=edges(vb),edges(vo)
             sb10=sum(1 for e in eb if e<0.010); so10=sum(1 for e in eo if e<0.010)
             ident = same_set(vb,vo)
             arith = (nr == len(vb)-sb10) and (mr == len(vo)-so10)
             res.append((("IDENT" if ident else "DIFFER"), dict(
                 nwb=len(vb), nwo=len(vo), nrb=nr, nro=mr,
                 short_b=sb10, short_o=so10, minb=min(eb), mino=min(eo),
                 arith=arith, zb=zone_of(sb["head"]), zo=zone_of(so["head"]),
                 cb=sb["head"][2] if len(sb["head"])>2 else "", co=so["head"][2] if len(so["head"])>2 else "")))
         kinds=[r[0] for r in res]
         det=[r[1] for r in res if r[1]]
         verdict = "ALL_IDENTICAL" if kinds and all(k=="IDENT" for k in kinds) else \
                   "ALL_DIFFER" if kinds and all(k=="DIFFER" for k in kinds) else "MIXED" if kinds else "NOSURF"
         arith_ok = all(x["arith"] for x in det) if det else None
         rows.append(dict(district=dist,building=bid,verdict=verdict,n_pairs=len(seen),
                          arith_all_ok=arith_ok,
                          min_edge=min([min(x["minb"],x["mino"]) for x in det]) if det else None,
                          short_edges=sum(x["short_b"]+x["short_o"] for x in det) if det else 0,
                          **d["counts"]))
 w=csv.DictWriter(sys.stdout, fieldnames=["district","building","verdict","n_pairs","arith_all_ok","min_edge","short_edges","vm","np","za","cn","cc","co"], extrasaction="ignore")
 w.writeheader()
 for r in rows: w.writerow(r)
 

if __name__=='__main__':
    main()
