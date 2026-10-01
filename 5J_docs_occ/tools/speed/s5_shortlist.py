# -*- coding: utf-8 -*-
"""5J Step 5 part D, step A (CPU): shortlist = the 3 lowest validation sums (level + pair) per family, from the 16 grid logs.
Reads train/ckpt/S/<i>/{train_log.tsv, run_info.json, config.json, best.pt (existence only)} for i = 0..15 (NEVER ckpt/S_void_*).
Writes train/winner/shortlist.json. Exit 1 if any config has no log. Rules R7.1."""
import csv, json, os, sys
T = "/speed-scratch/o_iseri/5J/train/"
rows, missing = [], []
for i in range(16):
    d = T + "ckpt/S/%d/" % i
    try:
        cfg = json.load(open(d + "config.json"))
        log = list(csv.DictReader(open(d + "train_log.tsv"), delimiter="\t"))
        assert len(log) > 0
    except Exception as e:
        missing.append((i, repr(e)[:100]))
        continue
    best = min(log, key=lambda r: float(r["val_sum"]))
    try:
        info = json.load(open(d + "run_info.json"))
        stop = info["stop"]
    except Exception:
        info, stop = None, "NO_run_info (not finished)"
    rows.append({"idx": i, "id": cfg.get("id"), "family": cfg["family"], "width": cfg["width"], "depth": cfg["depth"],
                 "lam": cfg["lam"], "best_epoch": int(best["epoch"]), "val_level": float(best["val_level"]),
                 "val_pair": float(best["val_pair"]), "val_sum": float(best["val_sum"]), "epochs_logged": len(log),
                 "finished": info is not None, "stop": stop, "has_best_pt": os.path.exists(d + "best.pt"),
                 "ckpt": d.rstrip("/")})
print("%-3s %-12s %-5s %-6s %-3s %-5s %-9s %-9s %-9s %-4s %s" % ("idx", "family", "width", "depth", "lam", "bestE", "level", "pair", "sum", "ep", "stop"))
for r in rows:
    print("%-3d %-12s %-5d %-6s %-3g %-5d %-9.5f %-9.5f %-9.5f %-4d %s%s" % (r["idx"], r["family"], r["width"], r["depth"], r["lam"], r["best_epoch"],
          r["val_level"], r["val_pair"], r["val_sum"], r["epochs_logged"], r["stop"], "" if r["has_best_pt"] else " NO_best.pt"))
if missing or len(rows) != 16:
    print("SHORTLIST FAIL: configs without a log: %s" % missing)
    sys.exit(1)
if any(not r["has_best_pt"] for r in rows):
    print("SHORTLIST FAIL: a config has no best.pt")
    sys.exit(1)
fams = sorted(set(r["family"] for r in rows))
print("families:", fams)
sel = []
for f in fams:
    fr = sorted([r for r in rows if r["family"] == f], key=lambda r: (r["val_sum"], r["idx"]))
    assert len(fr) == 8, (f, len(fr))
    sel += fr[:3]
for t, r in enumerate(sel):
    r["task"] = t
os.makedirs(T + "winner", exist_ok=True)
json.dump({"shortlist": sel, "all16": rows}, open(T + "winner/shortlist.json", "w"), indent=1)
print("SHORTLIST (6), array task -> config:")
for r in sel:
    print("task %d  S%d  %s w%d %s lam=%g  best_epoch=%d  val_sum=%.5f (level %.5f + pair %.5f)  stop=%s" % (r["task"], r["idx"], r["family"], r["width"],
          r["depth"], r["lam"], r["best_epoch"], r["val_sum"], r["val_level"], r["val_pair"], r["stop"]))
print("SHORTLIST_DONE")
