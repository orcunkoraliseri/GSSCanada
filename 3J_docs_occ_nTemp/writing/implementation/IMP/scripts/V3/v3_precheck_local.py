"""Local STATIC pre-check (no simulation): does the current toolchain rebuild the frozen IDFs, and does
the code-schedule injection reproduce the hand-rule reference R object-for-object?"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import v3_lib as L, v3_static as S, v3_build_R as R
out = sys.argv[1]; b = sys.argv[2] if len(sys.argv) > 2 else "Tall"; c = sys.argv[3] if len(sys.argv) > 3 else "MTL"
os.makedirs(out, exist_ok=True)
T = L.Tools(); res = {"building": b, "city": c, "code_md5": T.code_md5}
def step(name, fn):
    t = time.time(); r = fn(); r["seconds"] = round(time.time() - t, 1); res[name] = r
    print("=== %s: only_a=%d only_b=%d  (%.0fs)" % (name, r["n_only_a"], r["n_only_b"], r["seconds"]))
    print(r["report"][:3000]); json.dump(res, open(os.path.join(out, "precheck_%s_%s.json" % (b, c)), "w"), indent=2, default=str)
def rebuild(scen, chans, tag):
    f, info = L.build_injected(T, b, c, chans, tag, os.path.join(out, tag))
    return f
Rp = os.path.join(out, "R_%s_%s.idf" % (b, c)); R.build(L.frozen_idf("Default_NECB", b, c), Rp, 2)
U = L.frozen_idf("Default_NECB", b, c)
step("B_rebuild_vs_frozen_U", lambda: S.compare(rebuild("Default_NECB", {}, L.cell_tag("Default_NECB", b, c)), U))
step("N_vs_R", lambda: S.compare(rebuild("V3N", L.fixture_channels(c), "V3N__%s__%s" % (b, c)), Rp))
step("X_vs_R", lambda: S.compare(rebuild("V3X", L.fixture_channels(c, negative=True), "V3X__%s__%s" % (b, c)), Rp))
step("Y2022s42_vs_frozen", lambda: S.compare(rebuild("Y2022", L.product_channels("Y2022", c, 42), L.cell_tag("Y2022", b, c)), L.frozen_idf("Y2022", b, c)))
step("Bcentral_s42_vs_frozen", lambda: S.compare(rebuild("B_central", L.product_channels("B_central", c, 42), L.cell_tag("B_central", b, c)), L.frozen_idf("B_central", b, c)))
