"""Step 9p item 6/7: cost driver. Madrid elapsed per COMPLETED live task (sacct) against the surface count of the 10-03 IDF it ran (wp9o_win5/win5_check_per_stem.csv, surf_old),
then applied to the Bologna plan rows with the 10-05 surface counts (bol5_check_per_stem.csv, surf_new). Madrid's timing, 1 CPU per task, nodes shared with other jobs."""
import csv, io, os, math, statistics, collections
HERE = os.path.dirname(os.path.abspath(__file__)); OUTD = os.path.dirname(HERE); IMP = os.path.dirname(OUTD)
plan = list(csv.DictReader(io.open(IMP + "/wp9o_win5/plan_live_copy.csv", encoding="utf-8", newline="")))
surf_m = {r["stem"]: int(r["surf_old"]) for r in csv.DictReader(io.open(IMP + "/wp9o_win5/win5_check_per_stem.csv", encoding="utf-8", newline=""))}
surf_b = {r["stem"]: int(r["surf_new"]) for r in csv.DictReader(io.open(OUTD + "/bol5_check_per_stem.csv", encoding="utf-8", newline=""))}
def secs(s):
    h, m, x = s.split(":"); return int(h) * 3600 + int(m) * 60 + int(x)
rows = []
for ln in io.open(OUTD + "/speed_caps/sacct_1409235.txt", encoding="utf-8"):
    p = ln.rstrip("\n").split("|")
    if len(p) < 3 or p[1] != "COMPLETED" or "[" in p[0]: continue
    r = plan[int(p[0].split("_")[1]) - 1]
    rows.append((r["mode"], int(r["n_flats"]), surf_m[r["stem"]], secs(p[2])))
def linfit(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sum((a - mx) ** 2 for a in x); a0 = my - b * mx
    ss = sum((c - (a0 + b * a)) ** 2 for a, c in zip(x, y)); st = sum((c - my) ** 2 for c in y)
    return a0, b, 1 - ss / st
print("Madrid completed tasks", len(rows), "| surfaces per building: min %d median %d max %d" % (min(r[2] for r in rows), statistics.median(r[2] for r in rows), max(r[2] for r in rows)))
bp = list(csv.DictReader(io.open(OUTD + "/plan_IT-BOL-GALVANI2_win5.csv", encoding="utf-8", newline="")))
sb = [surf_b[r["stem"]] for r in bp]
print("Bologna plan rows", len(bp), "| surfaces per building: median %d max %d (stem %s) | rows above Madrid's largest completed (%d surfaces): %d" % (statistics.median(sb), max(sb), max(bp, key=lambda r: surf_b[r["stem"]])["stem"], max(r[2] for r in rows), sum(1 for s in sb if s > max(r[2] for r in rows))))
tot = {}
for mode, name in (("occupancy", "occupancy+b0"), ("default", "default")):
    sel = [r for r in rows if r[0] == mode]
    x = [r[2] for r in sel]; y = [r[3] for r in sel]
    a0, b, r2 = linfit(x, y)
    # power law t = c * s^k in log-log
    lx = [math.log(v) for v in x]; ly = [math.log(v) for v in y]
    la, lb, r2l = linfit(lx, ly)
    rr = [r for r in bp if r["mode"] == mode]
    est_lin = sum(max(a0 + b * surf_b[r["stem"]], 60) for r in rr)
    est_pow = sum(math.exp(la) * surf_b[r["stem"]] ** lb for r in rr)
    tot[mode] = (est_lin, est_pow)
    print("%s: runs %d | linear fit s = %.0f + %.3f x surfaces (R2 %.2f) | power fit s = %.1f x surfaces^%.2f (R2 log %.2f) | Bologna %d rows: linear %.0f CPU-h, power %.0f CPU-h" % (name, len(sel), a0, b, r2, math.exp(la), lb, r2l, len(rr), est_lin / 3600, est_pow / 3600))
print("TOTAL Bologna estimate on Madrid's per-surface cost: linear %.0f CPU-h, power law %.0f CPU-h (UNMEASURED above %d surfaces; the largest Bologna buildings are far outside Madrid's range)" % (sum(v[0] for v in tot.values()) / 3600, sum(v[1] for v in tot.values()) / 3600, max(r[2] for r in rows)))
# rows by surface bands and the CPU-h share from the biggest buildings (linear fit)
bands = collections.OrderedDict((("<500", 0), ("500-2000", 0), ("2000-5000", 0), ("5000+", 0)))
for r in bp:
    s = surf_b[r["stem"]]; bands["<500" if s < 500 else "500-2000" if s < 2000 else "2000-5000" if s < 5000 else "5000+"] += 1
print("Bologna rows by surface count of the building:", dict(bands))
big = [(r["stem"], r["n_flats"], surf_b[r["stem"]]) for r in bp if r["mode"] == "occupancy" and r["pool"] == "dev" and r["r"] == "1"]
big = sorted(set(big), key=lambda t: -t[2])[:5]
print("five largest Bologna buildings (stem, flats, surfaces):", big)
