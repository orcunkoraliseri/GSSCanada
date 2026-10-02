"""Step 9p item 4: which of the two origins carries the rounding? Floor area of the stem with the largest old/new difference, computed three ways:
(a) as our parser does it (absolute coordinates, 10-03 UTM text), (b) as our parser does it on the 10-05 local text, (c) exact: each polygon moved to its own first vertex
before the cross products (no large numbers, 10-03 text). Expectation: (b) = (c) to 1e-9, (a) off by up to a few mm2 per polygon."""
import os, sys, io
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "tools"))
sys.path.insert(0, TOOLS); os.environ["MODELA_VINTAGE"] = "win_2026-10-03"
import importlib
M = importlib.import_module("5thJ_modelA_idf")
E = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/IT-BOL-GALVANI2_win_2026-10-0"
stem = "b03c667dc84a337f"
def areas(path, local_first_vertex):
    t = M.read_text(path); tot = 0.0; n = 0
    for o in M.objects(t):
        if o["kw"] == "BUILDINGSURFACE:DETAILED" and o["fields"][1].lower() == "floor":
            s = M.surface_of(o); v = s["verts"]
            if local_first_vertex:
                v = [(x - v[0][0], y - v[0][1], z - v[0][2]) for x, y, z in v]
            tot += M.area3(v); n += 1
    return tot, n
a = areas(E + "3/idfs/%s.idf" % stem, False); b = areas(E + "5/idfs/%s.idf" % stem, False); c = areas(E + "3/idfs/%s.idf" % stem, True); d = areas(E + "5/idfs/%s.idf" % stem, True)
print("floor surfaces", a[1], "| (a) 10-03 absolute %.9f | (b) 10-05 absolute %.9f | (c) 10-03 each polygon moved to its first vertex %.9f | (d) 10-05 same %.9f" % (a[0], b[0], c[0], d[0]))
print("(a)-(c) = %.6f m2 | (b)-(c) = %.9f m2 | (b)-(d) = %.9f" % (a[0] - c[0], b[0] - c[0], b[0] - d[0]))
