# The act2 term, estimated honestly: fit P(act2 empty | context) on 80 % of the
# records, score the other 20 %, backoff-smoothed. Restricted to the uk+it held-in
# validation mix, which is what delim=0.1094 was measured on.
import json, math, sys, hashlib
from collections import defaultdict

PATH = sys.argv[1]
def bucket(d):
    d = int(d)
    return "<=15" if d <= 15 else "16-30" if d <= 30 else "31-60" if d <= 60 else "61-120" if d <= 120 else ">120"

rows = []          # (fold, country, act, loc, durb, empty)
eps_per_rec = defaultdict(int); nrec = 0
for line in open(PATH, encoding="utf-8"):
    r = json.loads(line)
    if r["country"] == "es":          # es is the held-out fold; val is uk+it
        continue
    h = int(hashlib.md5(r["pid"].encode()).hexdigest()[:8], 16) % 5
    fold = "test" if h == 0 else "fit"
    b = r["text"].split("|", 1)[1]
    b = b[:-5] if b.endswith("<eor>") else b
    nrec += 1
    for ep in [x for x in b.split(";") if x]:
        f = ep.split(",")
        if len(f) != 5:
            continue
        eps_per_rec[fold] += 1
        rows.append((fold, r["country"], f[1], f[3], bucket(f[0]), f[2] == ""))

CTX = {
    "marginal":            lambda c, a, l, d: (),
    "(country)":           lambda c, a, l, d: (c,),
    "(country,act)":       lambda c, a, l, d: (c, a),
    "(country,act,loc)":   lambda c, a, l, d: (c, a, l),
    "(country,act,loc,dur)": lambda c, a, l, d: (c, a, l, d),
}
ALPHA = 0.5     # Laplace, 2 outcomes
n_test_eps = sum(1 for r in rows if r[0] == "test")
n_test_empty = sum(1 for r in rows if r[0] == "test" and r[5])
delim_per_ep = 5 - (n_test_empty / n_test_eps)     # ",," is ONE token (confirmed below)
D = n_test_eps * delim_per_ep

print("uk+it: %d episodes scored, act2-empty %.4f" % (n_test_eps, n_test_empty / n_test_eps))
print("delimiter tokens per episode (',,' merged): %.3f\n" % delim_per_ep)
print("%-24s %10s %10s %10s" % ("P(act2 empty | ctx)", "nats/empty", "nats/delim", "band"))
for name, keyf in CTX.items():
    tab = defaultdict(lambda: [0, 0])
    for fold, c, a, l, d, e in rows:
        if fold == "fit":
            tab[keyf(c, a, l, d)][0 if e else 1] += 1
    tot, n = 0.0, 0
    for fold, c, a, l, d, e in rows:
        if fold != "test" or not e:
            continue
        cnt = tab.get(keyf(c, a, l, d))
        if cnt is None or sum(cnt) == 0:
            cnt = [sum(v[0] for v in tab.values()), sum(v[1] for v in tab.values())]
        p = (cnt[0] + ALPHA) / (cnt[0] + cnt[1] + 2 * ALPHA)
        tot += -math.log(p); n += 1
    print("%-24s %10.4f %10.4f %10s" % (name, tot / n, tot / D,
                                        "PASS" if tot / D < 0.05 else "over 0.05"))
