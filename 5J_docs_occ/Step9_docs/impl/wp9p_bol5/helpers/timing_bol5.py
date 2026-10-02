"""Step 9p item 6/7: Madrid per-run wall time from the live array 1409235 (sacct Elapsed of COMPLETED tasks, read-only capture speed_caps/sacct_1409235.txt) joined to the live plan
(task id = row number, 1-based, of plan_ES-MAD-BERRUGUETE.csv = copy `wp9o_win5/plan_live_copy.csv`). Fits seconds = a + b * n_flats per mode. This is Madrid's timing (1 CPU per task), not Bologna's."""
import csv, io, os, collections, statistics
HERE = os.path.dirname(os.path.abspath(__file__)); OUTD = os.path.dirname(HERE); IMP = os.path.dirname(OUTD)
plan = list(csv.DictReader(io.open(IMP + "/wp9o_win5/plan_live_copy.csv", encoding="utf-8", newline="")))
def secs(s):
    h, m, x = s.split(":"); return int(h) * 3600 + int(m) * 60 + int(x)
rows = []
for ln in io.open(OUTD + "/speed_caps/sacct_1409235.txt", encoding="utf-8"):
    p = ln.rstrip("\n").split("|")
    if len(p) < 3 or p[1] != "COMPLETED" or "_" not in p[0] or "[" in p[0]: continue
    i = int(p[0].split("_")[1]); r = plan[i - 1]
    rows.append((i, r["mode"], r["pool"], int(r["n_flats"]), secs(p[2]), r["stem"]))
print("completed tasks read", len(rows), "| task ids", min(r[0] for r in rows), "to", max(r[0] for r in rows))
tot = sum(r[4] for r in rows); nf = sum(r[3] for r in rows)
print("total elapsed %.1f CPU-h over %d runs: mean %.0f s per run, median %.0f s; flats in these runs: mean %.1f, median %d" % (tot / 3600, len(rows), tot / len(rows), statistics.median(r[4] for r in rows), nf / len(rows), statistics.median(r[3] for r in rows)))
def fit(sel):
    x = [r[3] for r in sel]; y = [r[4] for r in sel]; n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / max(sum((a - mx) ** 2 for a in x), 1e-9)
    return my - b * mx, b
for mode in ("occupancy", "default"):
    sel = [r for r in rows if r[1] == mode]
    if len(sel) > 5:
        a, b = fit(sel)
        big = [r for r in sel if r[3] >= 30]
        print("mode", mode, "runs", len(sel), "fit seconds = %.0f + %.2f x n_flats" % (a, b), "| max n_flats seen", max(r[3] for r in sel), "| runs with >=30 flats:", len(big), "mean s per flat there: %.1f" % (sum(r[4] for r in big) / max(sum(r[3] for r in big), 1) if big else 0))
# by flat band
for lo, hi in ((1, 1), (2, 8), (9, 24), (25, 60), (61, 200)):
    sel = [r for r in rows if lo <= r[3] <= hi]
    if sel: print("n_flats %d-%d: runs %d mean %.0f s median %.0f s max %.0f s | mean s/flat %.1f" % (lo, hi, len(sel), sum(r[4] for r in sel) / len(sel), statistics.median(r[4] for r in sel), max(r[4] for r in sel), sum(r[4] for r in sel) / sum(r[3] for r in sel)))
top = sorted(rows, key=lambda r: -r[3])[:5]
print("largest completed:", [(r[5], r[1], r[3], r[4]) for r in top])
a, b = fit([r for r in rows if r[1] == "occupancy"])
# Bologna plan
bp = list(csv.DictReader(io.open(OUTD + "/plan_IT-BOL-GALVANI2_win5.csv", encoding="utf-8", newline="")))
est = sum(a + b * int(r["n_flats"]) for r in bp if r["mode"] == "occupancy")
dflt = [r for r in bp if r["mode"] == "default"]
# default-mode: separate fit
sel = [r for r in rows if r[1] == "default"]
ad, bd = fit(sel) if len(sel) > 5 else (a, b)
est_d = sum(ad + bd * int(r["n_flats"]) for r in dflt)
print("BOLOGNA plan rows", len(bp), "by mode", dict(collections.Counter(r["mode"] for r in bp)), "| total flats over runs", sum(int(r["n_flats"]) for r in bp))
print("LINEAR extrapolation of Madrid's fit (a + b * n_flats): occupancy rows %.0f CPU-h, default rows %.0f CPU-h, total %.0f CPU-h (Madrid's per-flat cost; EnergyPlus time may not stay linear in zones: UNMEASURED beyond 79 flats)" % (est / 3600, est_d / 3600, (est + est_d) / 3600))
sizes = collections.Counter()
for r in bp:
    n = int(r["n_flats"]); sizes["1-24" if n < 25 else "25-79" if n <= 79 else "80-199" if n < 200 else "200+"] += 1
print("Bologna rows by building size:", dict(sizes), "| rows above Madrid's largest completed run (%d flats):" % max(r[3] for r in rows), sum(1 for r in bp if int(r["n_flats"]) > max(r[3] for r in rows)))
