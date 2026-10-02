"""Step 9p item 7: queue arithmetic at 32 CPUs from the live Madrid array 1409235 (read-only sacct capture speed_caps/sacct_1409235_b.txt taken 2026-10-01 23:15 EDT) and the plans.
Madrid per-run seconds by building size (surfaces of the 10-03 IDF, binned) from the COMPLETED tasks; remaining Madrid rows = live plan rows not COMPLETED, minus the 72 deferred buildings (not in the array);
the 1,458 resubmission rows and the Bologna rows use the same bin means (bins with no Madrid data use the smoke point 1,400 s = 77 flats / 675 surfaces, which is the only measured large run).
Everything here is Madrid's per-run time at 1 CPU on shared nodes; Bologna's big buildings are not covered."""
import csv, io, os, statistics, collections
HERE = os.path.dirname(os.path.abspath(__file__)); OUTD = os.path.dirname(HERE); IMP = os.path.dirname(OUTD)
plan = list(csv.DictReader(io.open(IMP + "/wp9o_win5/plan_live_copy.csv", encoding="utf-8", newline="")))
surf_m = {r["stem"]: int(r["surf_old"]) for r in csv.DictReader(io.open(IMP + "/wp9o_win5/win5_check_per_stem.csv", encoding="utf-8", newline=""))}
surf_b = {r["stem"]: int(r["surf_new"]) for r in csv.DictReader(io.open(OUTD + "/bol5_check_per_stem.csv", encoding="utf-8", newline=""))}
def secs(s):
    h, m, x = s.split(":"); return int(h) * 3600 + int(m) * 60 + int(x)
done = {}; state = collections.Counter(); first = None; last = None
for ln in io.open(OUTD + "/speed_caps/sacct_1409235_b.txt", encoding="utf-8"):
    p = ln.rstrip("\n").split("|")
    if len(p) < 6 or "_" not in p[0]: continue
    if "[" in p[0]:
        state["PENDING_line"] += 1; continue
    state[p[1]] += 1
    if p[1] == "COMPLETED":
        done[int(p[0].split("_")[1])] = secs(p[2])
        first = min(first or p[3], p[3]); last = max(last or p[4], p[4])
print("array 1409235: COMPLETED", len(done), "| running", state["RUNNING"], "| first start", first, "| last end", last)
def band(s): return 0 if s < 100 else 1 if s < 300 else 2 if s < 500 else 3
by = collections.defaultdict(list)
for i, e in done.items(): by[band(surf_m[plan[i - 1]["stem"]])].append(e)
SMOKE = 1400.0
mean = {b: (sum(v) / len(v) if len(v) >= 5 else None) for b, v in by.items()}
print("Madrid bin means (surfaces <100 / 100-299 / 300-499 / 500+):", [("%.0f s (n=%d)" % (mean[b], len(by[b])) if mean.get(b) else "no data (n=%d)" % len(by.get(b, []))) for b in range(4)], "| all mean %.0f s" % (sum(sum(v) for v in by.values()) / sum(len(v) for v in by.values())))
def t_of(surf): 
    m = mean.get(band(surf)); return m if m else SMOKE
allmean = sum(sum(v) for v in by.values()) / sum(len(v) for v in by.values())
# deferred stems = the 72 degenerate buildings (rows not in the array): rows of plan whose index is neither done nor running nor pending in the array is unknown here, so use the manager's count: array = 8,616 rows
tot_array = 8616
rem = tot_array - len(done) - state["RUNNING"]
print("array rows: total 8,616 (live plan minus the 72 deferred buildings), done %d, running %d, not started %d" % (len(done), state["RUNNING"], rem))
# not-started rows estimate: the plan rows beyond the done ones; use all live-plan rows with index not done as proxy for sizes (includes the 585 deferred rows: scaled to 8,616)
undone = [r for i, r in enumerate(plan, 1) if i not in done]
est_mean_bin = sum(t_of(surf_m[r["stem"]]) for r in undone) / len(undone)
est_mean_flat = allmean
print("not-started rows: mean seconds by size bins %.0f s | by plain mean of the done rows %.0f s" % (est_mean_bin, est_mean_flat))
mad_rem_low = rem * est_mean_flat / 3600.0; mad_rem_hi = rem * est_mean_bin / 3600.0
print("MADRID remaining array: %.0f to %.0f CPU-h -> at 31 CPUs %.1f to %.1f h" % (mad_rem_low, mad_rem_hi, mad_rem_low / 31, mad_rem_hi / 31))
res = list(csv.DictReader(io.open(IMP + "/wp9o_win5/resub_ES-MAD-BERRUGUETE_win5.csv", encoding="utf-8", newline="")))
rs_low = len(res) * est_mean_flat / 3600.0
sm = {r["stem"]: int(r["surf_new"]) for r in csv.DictReader(io.open(IMP + "/wp9o_win5/win5_check_per_stem.csv", encoding="utf-8", newline=""))}
rs_hi = sum(t_of(sm[r["stem"]]) for r in res) / 3600.0
print("MADRID resubmission 1,458 rows: %.0f to %.0f CPU-h -> at 32 CPUs %.1f to %.1f h" % (rs_low, rs_hi, rs_low / 32, rs_hi / 32))
bp = list(csv.DictReader(io.open(OUTD + "/plan_IT-BOL-GALVANI2_win5.csv", encoding="utf-8", newline="")))
b_low = len(bp) * est_mean_flat / 3600.0
b_hi = sum(t_of(surf_b[r["stem"]]) for r in bp) / 3600.0
nobig = [r for r in bp if surf_b[r["stem"]] < 500]
print("BOLOGNA 9,435 rows: %.0f CPU-h (plain Madrid mean) to %.0f CPU-h (bins; 500+ surfaces priced at the one measured large run, 1,400 s) -> at 32 CPUs %.1f to %.1f h = %.1f to %.1f days" % (b_low, b_hi, b_low / 32, b_hi / 32, b_low / 32 / 24, b_hi / 32 / 24))
print("  rows with a building under 500 surfaces: %d (%.0f CPU-h at the plain mean); rows at 500+ surfaces: %d (of which 1,000+: %d, 2,000+: %d, 5,000+: %d) = outside Madrid's data" % (len(nobig), len(nobig) * est_mean_flat / 3600, len(bp) - len(nobig), sum(1 for r in bp if surf_b[r["stem"]] >= 1000), sum(1 for r in bp if surf_b[r["stem"]] >= 2000), sum(1 for r in bp if surf_b[r["stem"]] >= 5000)))
for name, parts in (("Madrid rest, then Madrid resubmission, then Bologna", [mad_rem_low, rs_low, b_low]), ("same, high estimate", [mad_rem_hi, rs_hi, b_hi])):
    tot = sum(parts); print("TOTAL (%s): %.0f CPU-h = %.1f h at 32 CPUs = %.1f days" % (name, tot, tot / 32, tot / 32 / 24))
# row ranges of the biggest buildings in the Bologna plan (rows are grouped by stem; 1-based index = array task id)
idx = collections.defaultdict(list)
for i, r in enumerate(bp, 1): idx[r["stem"]].append(i)
big = sorted(idx, key=lambda s: -surf_b[s])[:6]
for s in big:
    print("  big building", s, "flats", bp[idx[s][0] - 1]["n_flats"], "surfaces", surf_b[s], "split", bp[idx[s][0] - 1]["building_split"], "rows", idx[s][0], "to", idx[s][-1], "(%d rows, consecutive: %s)" % (len(idx[s]), idx[s][-1] - idx[s][0] + 1 == len(idx[s])))
