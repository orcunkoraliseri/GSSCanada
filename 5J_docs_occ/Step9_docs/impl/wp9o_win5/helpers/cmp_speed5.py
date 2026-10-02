"""Step 9o item 3: compare the Speed copy (ls -l captures in /tmp/w5) with the local delivered folder (names + byte sizes). One folder at a time locally."""
import os, re, io, sys, hashlib
NEW = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/ES-MAD-BERRUGUETE_win_2026-10-05"
FL = "/speed-scratch/o_iseri/fleets/EU11_ES-MAD-BERRUGUETE_win_2026-10-05"
W = "/tmp/w5" if len(sys.argv) < 2 else sys.argv[1]
stems = [ln.strip().split()[-1][:-4] for ln in io.open(NEW + "/md5_2026-10-05.txt", encoding="utf-8") if ln.strip()]
# idfs
sp = {}
for ln in io.open(W + "/speed_idfs.txt", encoding="utf-8"):
    m = re.match(r"^-\S+\s+\d+\s+\S+\s+\S+\s+(\d+)\s+\w+\s+\d+\s+[\d:]+\s+(.+)$", ln.rstrip("\n"))
    if m: sp[m.group(2)] = int(m.group(1))
loc = {s + ".idf": os.path.getsize(NEW + "/idfs/%s.idf" % s) for s in stems}
miss = [n for n in loc if n not in sp]; extra = [n for n in sp if n not in loc]
diff = [n for n in loc if n in sp and sp[n] != loc[n]]
print("IDFS local", len(loc), "speed", len(sp), "missing on speed", len(miss), "extra on speed", len(extra), "size differs", len(diff), diff[:5])
# schedules
cur = None; ssp = {}
for ln in io.open(W + "/speed_sched.txt", encoding="utf-8"):
    ln = ln.rstrip("\n")
    if ln.endswith(":"):
        cur = ln[:-1].rsplit("/", 1)[-1]
        if cur == "schedules": cur = None
        continue
    m = re.match(r"^-\S+\s+\d+\s+\S+\s+\S+\s+(\d+)\s+\w+\s+\d+\s+[\d:]+\s+(.+)$", ln)
    if m and cur: ssp[(cur, m.group(2))] = int(m.group(1))
sloc = {}; ndir = 0
for s in stems:
    d = NEW + "/schedules/" + s
    if os.path.isdir(d):
        ndir += 1
        for e in os.scandir(d):
            if e.is_file(): sloc[(s, e.name)] = e.stat().st_size
miss = [k for k in sloc if k not in ssp]; extra = [k for k in ssp if k not in sloc]
diff = [k for k in sloc if k in ssp and ssp[k] != sloc[k]]
print("SCHEDULES local folders", ndir, "files", len(sloc), "speed files", len(ssp), "missing on speed", len(miss), "extra on speed", len(extra), "size differs", len(diff), "bytes local", sum(sloc.values()), "speed", sum(ssp.values()))
print("  examples missing", miss[:3], "extra", extra[:3], "diff", diff[:3])
