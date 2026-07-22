import json, sys, csv, os
from collections import defaultdict, Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(__file__)
rows = json.load(open(os.path.join(BASE, "parsed_rows.json"), encoding="utf-8"))

KEEP_GEO = {"Calgary", "Edmonton", "AlbertaResorts", "AlbertaExclResorts"}
rows = [r for r in rows if r["GEO"] in KEEP_GEO]

groups = defaultdict(list)
for r in rows:
    groups[(r["YEAR"], r["MONTH"], r["GEO"], r["metric"])].append(r)

resolved = {}
conflict_log = []
for key, v in groups.items():
    # round for stable comparison
    def rnd(x):
        return round(x, 4)
    vals = [rnd(r["value"]) for r in v]
    cnt = Counter(vals)
    top_val, top_n = cnt.most_common(1)[0]
    if len(cnt) > 1:
        conflict_log.append((key, dict(cnt), [ (r["PROVENANCE"], rnd(r["value"])) for r in v ]))
    # pick most recent provenance among rows carrying the majority value
    def prov_sort_key(r):
        fn = r["PROVENANCE"]
        # AB_MM_YYYY_MM.pdf
        parts = fn.replace(".pdf", "").split("_")
        return (int(parts[2]), int(parts[3]))
    candidates = [r for r in v if rnd(r["value"]) == top_val]
    candidates.sort(key=prov_sort_key)
    best = candidates[-1]
    resolved[key] = {
        "YEAR": key[0], "MONTH": key[1], "GEO": key[2], "metric": key[3],
        "value": top_val, "SOURCE": "ABMKTMONITOR", "PROVENANCE": best["PROVENANCE"],
        "STATUS": "OK",
    }

# Build full grid: years 2011-2022, months 1-12, GEO x metric present in data at all
geo_metric_combos = sorted(set((k[2], k[3]) for k in groups.keys()))
out_rows = []
for year in range(2011, 2023):
    for month in range(1, 13):
        for geo, metric in geo_metric_combos:
            key = (year, month, geo, metric)
            if key in resolved:
                out_rows.append(resolved[key])
            else:
                out_rows.append({
                    "YEAR": year, "MONTH": month, "GEO": geo, "metric": metric,
                    "value": "", "SOURCE": "ABMKTMONITOR", "PROVENANCE": "",
                    "STATUS": "GAP",
                })

out_path = os.path.join(BASE, "hotel_ab_monthly_2012_2022.csv")
with open(out_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["YEAR","MONTH","GEO","metric","value","SOURCE","PROVENANCE","STATUS"])
    w.writeheader()
    for r in out_rows:
        w.writerow(r)

json.dump(conflict_log, open(os.path.join(BASE, "conflict_log.json"), "w", encoding="utf-8"), indent=1)

print("rows written:", len(out_rows))
print("conflicts (resolved by majority):", len(conflict_log))
print("wrote:", out_path)

# quick coverage summary
from collections import defaultdict as dd
cov = dd(lambda: {"OK":0, "GAP":0, "months_ok": []})
for r in out_rows:
    k = (r["GEO"], r["metric"])
    cov[k][r["STATUS"]] += 1
    if r["STATUS"] == "OK":
        cov[k]["months_ok"].append((r["YEAR"], r["MONTH"]))
print("\nCoverage:")
for k, v in sorted(cov.items()):
    mo = sorted(v["months_ok"])
    lo = mo[0] if mo else None
    hi = mo[-1] if mo else None
    print(f"{k}: OK={v['OK']} GAP={v['GAP']} min={lo} max={hi}")
