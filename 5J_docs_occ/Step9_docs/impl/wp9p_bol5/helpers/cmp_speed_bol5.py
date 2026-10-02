"""Step 9p item 3: compare the Speed fleet copy (ls captures in ../speed_caps) with the local delivered Bologna 10-05 folder (names + byte sizes + md5 of single named files). One folder at a time locally."""
import os, re, io, sys, hashlib
NEW = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/IT-BOL-GALVANI2_win_2026-10-05"
HERE = os.path.dirname(os.path.abspath(__file__)); W = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), "speed_caps")
stems = [ln.strip().split()[-1][:-4] for ln in io.open(NEW + "/md5_2026-10-05.txt", encoding="utf-8") if ln.strip()]
R = re.compile(r"^-\S+\s+\d+\s+\S+\s+\S+\s+(\d+)\s+\w+\s+\d+\s+[\d:]+\s+(.+)$")
sp = {}
for ln in io.open(W + "/speed_idfs.txt", encoding="utf-8"):
    m = R.match(ln.rstrip("\n"))
    if m: sp[m.group(2)] = int(m.group(1))
loc = {s + ".idf": os.path.getsize(NEW + "/idfs/%s.idf" % s) for s in stems}
miss = [n for n in loc if n not in sp]; extra = [n for n in sp if n not in loc]
diff = [n for n in loc if n in sp and sp[n] != loc[n]]
print("IDFS local", len(loc), "speed", len(sp), "missing on speed", len(miss), "extra on speed", len(extra), "size differs", len(diff), diff[:5], "bytes local", sum(loc.values()))
cur = None; ssp = {}
for ln in io.open(W + "/speed_sched.txt", encoding="utf-8"):
    ln = ln.rstrip("\n")
    if ln.endswith(":"):
        cur = ln[:-1].rsplit("/", 1)[-1]
        if cur == "schedules": cur = None
        continue
    m = R.match(ln)
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
# md5 of single named files, local vs speed
def md5(p):
    h = hashlib.md5(); h.update(io.open(p, "rb").read()); return h.hexdigest()
for ln in io.open(W + "/speed_md5_files.txt", encoding="utf-8"):
    h, p = ln.split()
    rel = p.split("IT-BOL-GALVANI2_win_2026-10-05/")[1]
    lm = md5(NEW + "/" + rel)
    print("MD5", rel, "speed", h[:8], "local", lm[:8], "EQUAL" if lm == h else "DIFFERENT")
if os.path.exists(W + "/speed_md5_idfs.txt"):
    m5 = {}
    for ln in io.open(NEW + "/md5_2026-10-05.txt", encoding="utf-8"):
        p = ln.split()
        if p: m5[p[-1]] = p[0]
    ok = bad = 0
    for ln in io.open(W + "/speed_md5_idfs.txt", encoding="utf-8"):
        h, p = ln.split()
        if m5[os.path.basename(p)] == h: ok += 1
        else: bad += 1
    print("MD5 of named IDFs on Speed vs md5_2026-10-05.txt: equal", ok, "different", bad)
