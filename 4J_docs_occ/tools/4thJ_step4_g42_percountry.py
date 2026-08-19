import json,sys
from collections import defaultdict
n=defaultdict(int); e=defaultdict(int); empty=defaultdict(int); tot=defaultdict(int)
for line in open(sys.argv[1],encoding="utf-8"):
    r=json.loads(line); c=r["country"]; b=r["text"].split("|",1)[1]
    b=b[:-5] if b.endswith("<eor>") else b
    eps=[x for x in b.split(";") if x]
    n[c]+=1; e[c]+=len(eps)
    for ep in eps:
        f=ep.split(",")
        if len(f)==5:
            tot[c]+=1
            if f[2]=="": empty[c]+=1
for c in sorted(n):
    print("%s records %6d  episodes/record %.2f  act2-empty %.4f" % (c,n[c],e[c]/n[c],empty[c]/tot[c]))
uk_it_rec=n["uk"]+n["it"]; uk_it_eps=e["uk"]+e["it"]
print("uk+it: %d records, %.2f episodes/record" % (uk_it_rec, uk_it_eps/uk_it_rec))
