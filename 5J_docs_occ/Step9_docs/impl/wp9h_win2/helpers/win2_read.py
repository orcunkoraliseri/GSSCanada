import csv, glob, os, re, sqlite3, sys
W = sys.argv[1]
STEMS = ["0275c53572b2ff9f", "7307694dddf93fb6", "504fa19567bbc2b7", "b3f8d90890ff6314"]
exp = {}
for r in csv.DictReader(open(W + "/expected_azimuth.csv")):
    exp.setdefault(r["stem"], []).append(r)
def cdiff(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)
for stem in STEMS:
    run = W + "/runs/" + stem
    print("=== %s" % stem)
    err = run + "/eplusout.err"
    if not os.path.exists(err):
        print("NO eplusout.err (run did not start or failed)"); continue
    t = open(err, errors="replace").read()
    print("eplusout.err: upside down warnings %d; Severe %d; Fatal %d; last line: %s" % (
        len(re.findall(r"upside down", t, re.I)), len(re.findall(r"\*\* Severe", t)), len(re.findall(r"\*\* Fatal", t)), t.strip().splitlines()[-1][:160]))
    print("warning lines mentioning 'upside': " + str([l.strip()[:140] for l in t.splitlines() if re.search(r"upside", l, re.I)][:3]))
    # E+ azimuth from the SQL Surfaces table (delivered output option)
    az = {}
    sql = run + "/eplusout.sql"
    if os.path.exists(sql):
        c = sqlite3.connect(sql)
        cols = [r[1] for r in c.execute("PRAGMA table_info(Surfaces)")]
        print("Surfaces columns:", cols)
        q = "SELECT SurfaceName, ClassName, ExtBoundCond, Azimuth, SurfaceIndex FROM Surfaces ORDER BY SurfaceIndex"
        for n, cl, eb, a, i in c.execute(q):
            az[n.upper()] = (cl, eb, a, i)
        print("sql surfaces read:", len(az))
    # eplustbl.csv Opaque Exterior azimuth
    tbl = {}
    tp = run + "/eplustbl.csv"
    if os.path.exists(tp):
        rows = list(csv.reader(open(tp, errors="replace")))
        for k, r in enumerate(rows):
            if r and r[0].strip() == "Opaque Exterior":
                hdr = rows[k + 1]
                ia = [j for j, h in enumerate(hdr) if h.strip().startswith("Azimuth")]
                for r2 in rows[k + 2:]:
                    if not r2 or len([x for x in r2 if x.strip()]) < 3:
                        break
                    if ia and len(r2) > ia[0]:
                        try:
                            tbl[(r2[1] if not r2[0].strip() else r2[0]).strip().upper()] = float(r2[ia[0]])
                        except ValueError:
                            pass
                break
        print("eplustbl Opaque Exterior rows read:", len(tbl))
    else:
        print("NO eplustbl.csv")
    rows_e = exp[stem]
    first = rows_e[0]
    nm = first["wall_name"].upper()
    print("FIRST outdoor wall %s: geometric outward azimuth %s ; EnergyPlus sql azimuth %s ; EnergyPlus eplustbl azimuth %s" % (first["wall_name"], first["geom_outward_az"], az.get(nm, ("", "", "n/a"))[2], tbl.get(nm, "n/a")))
    for label, src in (("sql", {k: v[2] for k, v in az.items()}), ("eplustbl", tbl)):
        n = ag = dis = miss = und = 0
        worst = []
        for r in rows_e:
            n += 1
            if not r["geom_outward_az"]:
                und += 1; continue
            v = src.get(r["wall_name"].upper())
            if v is None:
                miss += 1; continue
            d = cdiff(v, float(r["geom_outward_az"]))
            if d <= 1.0: ag += 1
            else:
                dis += 1; worst.append((r["wall_name"][-28:], round(d, 1), r["point_class"], r["edge_class"]))
        print("COMPARE %s: outdoor walls %d, geometry-undecided %d, not found in E+ %d, agree within 1 deg %d, disagree %d %s" % (label, n, und, miss, ag, dis, worst[:5]))
