"""Step 9o side check: files the campaign reads that the per-run md5 key does NOT cover: schedules/<stem>/* (default-mode runs), windows.csv rows, prepared_buildings.csv rows, weather. 10-03 vs 10-05, per stem, one folder at a time."""
import os, io, csv, hashlib, collections
from multiprocessing import Pool
EU11 = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11"
OLD = EU11 + "/ES-MAD-BERRUGUETE_win_2026-10-03"; NEW = EU11 + "/ES-MAD-BERRUGUETE_win_2026-10-05"
ch = dict(l.rstrip("\r\n").split("\t") for l in open(NEW + "/changed_stems.txt"))
def md5(p):
    h = hashlib.md5(); h.update(open(p, "rb").read()); return h.hexdigest()
def work(stem):
    r = {}
    for tag, root in (("o", OLD), ("n", NEW)):
        d = root + "/schedules/" + stem
        r[tag] = {e.name: md5(e.path) for e in os.scandir(d) if e.is_file()} if os.path.isdir(d) else None
    return stem, r["o"], r["n"]
if __name__ == "__main__":
    stems = [l.strip().split()[-1][:-4] for l in io.open(NEW + "/md5_2026-10-05.txt", encoding="utf-8") if l.strip()]
    with Pool(10) as p: res = p.map(work, stems, chunksize=8)
    eq = collections.Counter(); bad = []
    for s, o, n in res:
        g = ch.get(s, "unchanged")
        if o is None or n is None: eq[(g, "folder missing: old=%s new=%s" % (o is not None, n is not None))] += 1; bad.append(s); continue
        if o == n: eq[(g, "schedules identical (names + md5)")] += 1
        else:
            eq[(g, "schedules differ (files %d -> %d; changed md5 %d, only old %d, only new %d)" % (len(o), len(n), sum(1 for k in o if k in n and o[k] != n[k]), len(set(o) - set(n)), len(set(n) - set(o))))] += 1; bad.append(s)
    print("SCHEDULES per group:")
    for k, v in sorted(eq.items()): print("  ", k, v)
    print("  unchanged stems with any schedules difference:", [s for s in bad if s not in ch])
    def rows(root, name, key):
        with io.open(root + "/" + name, encoding="utf-8", newline="") as fh: return {r[key]: r for r in csv.DictReader(fh)}, 
    for name, key in (("windows.csv", "stem"), ("prepared_buildings.csv", "stem")):
        o = rows(OLD, name, key)[0]; n = rows(NEW, name, key)[0]
        d = [s for s in o if s in n and o[s] != n[s]]
        cols = collections.Counter(c for s in d for c in o[s] if o[s][c] != n[s].get(c))
        print(name, "rows old", len(o), "new", len(n), "differing rows", len(d), "of which unchanged-group stems", sum(1 for s in d if s not in ch), "| stems only old/new:", len(set(o) - set(n)), len(set(n) - set(o)), "| columns:", dict(cols))
    print("weather epw md5 equal:", md5(OLD + "/weather/es_madrid_2009_2010_y2010.epw") == md5(NEW + "/weather/es_madrid_2009_2010_y2010.epw"))
