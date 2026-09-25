"""V3a static pre-check against the P10R arm (local, NO simulation), 2026-09-25.

    py -3 v3a_precheck_P10R.py <out_json_dir> <work_dir> <building> <city>

For one building-city cell, rebuilds with the patched V3 chain (v3_lib, P10R products, standby floor ON)
and compares object-for-object (v3_static.compare) with the P10R cell's injected_resized.idf:
  GATE      Y2022 seed 42            vs P10R Y2022      -> must be 0/0
  GATE      B_central seed 42        vs P10R B_central  -> must be 0/0
  CONTROL   Y2022 seed 101           vs P10R Y2022 (s42) -> must NOT be 0/0 (the check can fail: draw)
  CONTROL   Y2022 seed 42, floor OFF vs P10R Y2022      -> must NOT be 0/0 (the check can fail: wiring)
Also compares the live code md5s with the P10R manifest's P10R_CODE_MD5.
Exit 0 = gates 0/0 and both controls fired; 1 = a gate differs; 2 = a control did not fire;
3 = crashed (not a verdict).
"""
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v3_lib as L      # noqa: E402
import v3_static as S   # noqa: E402


def main():
    out, work, b, c = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    os.makedirs(out, exist_ok=True)
    os.makedirs(work, exist_ok=True)
    jpath = os.path.join(out, "precheck_P10R_%s_%s.json" % (b, c))
    T = L.Tools()
    res = {"building": b, "city": c, "code_md5": T.code_md5, "steps": {}}
    ref_man = json.load(open(os.path.join(L.P10R_CAMPAIGN, L.cell_tag("Y2022", b, c), "manifest.json"),
                             encoding="utf-8"))
    pc = ref_man["P10R_CODE_MD5"]
    res["code_md5_vs_P10R"] = {k: {"live": T.code_md5[k], "P10R": pc[k], "same": T.code_md5[k] == pc[k]}
                               for k in T.code_md5 if k in pc}
    print("[precheck] code md5 vs P10R:", {k: v["same"] for k, v in res["code_md5_vs_P10R"].items()})

    def step(name, scen, seed, floor, kind):
        t = time.time()
        chans = L.product_channels(scen, c, seed)
        tag = "%s__s%d__floor%d" % (L.cell_tag(scen, b, c), seed, int(floor))
        f, info = L.build_injected(T, b, c, chans, L.cell_tag(scen, b, c), os.path.join(work, tag),
                                   standby_floor=floor)
        ref = L.p10r_idf(scen, b, c)
        r = S.compare(f, ref)
        r["seconds"] = round(time.time() - t, 1)
        r["kind"], r["scenario"], r["seed"], r["standby_floor"] = kind, scen, seed, floor
        r["ref_md5"] = L.md5_file(ref)
        r["rebuilt_md5"] = L.md5_file(f)
        zero = r["n_only_a"] == 0 and r["n_only_b"] == 0
        r["outcome"] = ("PASS 0/0" if zero else "FAIL") if kind == "gate" else \
                       ("FIRED" if not zero else "RAN_NOT_FIRED")
        res["steps"][name] = r
        print("=== %s: only_a=%d only_b=%d -> %s (%.0fs)" % (name, r["n_only_a"], r["n_only_b"], r["outcome"],
                                                         r["seconds"]))
        print(r["report"][:2500])
        json.dump(res, open(jpath, "w"), indent=2, default=str)

    step("gate_Y2022_s42_vs_P10R", "Y2022", 42, True, "gate")
    step("gate_Bcentral_s42_vs_P10R", "B_central", 42, True, "gate")
    step("control_Y2022_s101_vs_P10R_s42", "Y2022", 101, True, "control")
    step("control_Y2022_s42_floorOFF_vs_P10R", "Y2022", 42, False, "control")
    st = res["steps"]
    gates_ok = all(v["outcome"] == "PASS 0/0" for v in st.values() if v["kind"] == "gate")
    ctrl_ok = all(v["outcome"] == "FIRED" for v in st.values() if v["kind"] == "control")
    res["verdict"] = "PASS" if gates_ok and ctrl_ok else ("FAIL" if not gates_ok else "NOT_EVALUABLE (control did not fire)")
    json.dump(res, open(jpath, "w"), indent=2, default=str)
    print("[precheck] %s %s VERDICT %s" % (b, c, res["verdict"]))
    return 0 if res["verdict"] == "PASS" else (1 if not gates_ok else 2)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        print("PRECHECK CRASHED -> exit 3 (not a verdict)")
        sys.exit(3)
