# -*- coding: utf-8 -*-
"""5J Step 7 part A shared code (Speed job only; Spain only; never a UK file).
Everything Step 7 writes lives under D = /speed-scratch/o_iseri/5J/district/ . Steps 2-6 outputs are read only.
install_twins() makes camp_common (the campaign machinery, unchanged) see the district twin building rows (es_T001..) next to the
campaign building rows; nothing in camp_common is edited."""
import hashlib, io, csv, os, sys, time, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

FIVE = "/speed-scratch/o_iseri/5J/"
D = FIVE + "district/"
IN = D + "in/"
HH = D + "hh/"
POOL = HH + "pool/"               # household folders es_<hid>/ : symlinks to the 60 campaign folders + the new ones
CAMP_IN = FIVE + "campaign/in/"
CLIMATE = "es_madrid_2010"
TWINS_CSV = IN + "twins_es.csv"
SEED_SAMPLE = 20261001
SEED_TWIN = 20261002
SEED_DRAWS = 20261003
SEED_HH = 6
N_SAMPLE = 100
MIN_PER_CLASS = 5
CLASSES = ["SFH", "TH", "MFH", "AB"]
STORE = D + "store/"


def stamp(s):
    print("[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), s), flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_csv(p, **kw):
    return list(csv.DictReader(io.open(p, encoding="utf-8")))


def write_csv(path, header, rows):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def seal(path):
    """Append '<md5>  <file>' to SEALS.md5 (append only). Refuses to seal a file that is already sealed with another md5."""
    sp = IN + "SEALS.md5"
    m = md5(path)
    name = os.path.basename(path)
    old = {}
    if os.path.exists(sp):
        for ln in io.open(sp, encoding="utf-8"):
            q = ln.split()
            if len(q) == 2:
                old[q[1]] = q[0]
    if name in old:
        if old[name] != m:
            raise RuntimeError("SEAL REFUSED: %s is sealed with md5 %s but is now %s" % (name, old[name], m))
        print("SEAL already present and equal: %s %s" % (m, name))
        return m
    with io.open(sp, "a", encoding="utf-8") as fh:
        fh.write("%s  %s\n" % (m, name))
    print("SEAL %s %s" % (m, name))
    return m


def install_twins():
    """Patch camp_common.static so the building table also holds the twin rows of TWINS_CSV (if the file exists)."""
    import camp_common as cc
    orig = cc.static

    def static():
        st = orig()
        if not st.get("_twins_added"):
            if os.path.exists(TWINS_CSV):
                for r in read_csv(TWINS_CSV):
                    assert r["country"] == "es" and r["building_id"].startswith("es_T"), r
                    st["bt"][r["building_id"]] = r
            st["_twins_added"] = True
        return st
    cc.static = static
    return cc


def hid_tokens(placement):
    out = {}
    for item in placement.split(";"):
        j, t = item.split(":", 1)
        out[int(j)] = t
    return out
