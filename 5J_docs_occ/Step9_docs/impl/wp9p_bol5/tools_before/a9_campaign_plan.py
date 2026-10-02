# -*- coding: utf-8 -*-
"""5J Step 9l: Model A campaign plan (manifest), one district. Runs LOCALLY (desktop, `py`), writes a csv that is then scp'd to Speed.

    py a9_campaign_plan.py <district> --out <plan.csv> [--smoke-out <smoke.csv>] [--no-md5]
    py a9_campaign_plan.py --selftest

Input: sealed building lists Step9_docs/impl/buildsplit_win3/<D>_{dev,val,test}.csv (read by full name) minus
Step9_docs/impl/heldout_tinyflats_win3.csv (district, stem).  Runs per building exactly as rules R2:
  dev building : dev 1-3, val 1-2, test 1-2, b0, def = 9
  val building : dev 1-2, val 1-2, b0, def = 6
  test building: dev 1-2, test 1-2, b0, def = 6
run_id = <D>_<stem>_<pool>_<r>   (b0 and def: r = 0).   seed = run_seed_of(run_id) of the household builder (copied rule, checked
against the builder module when it can be imported).
Columns: run_id, district, stem, building_split, pool, r, mode, n_flats, seed, src_idf, src_idf_md5
Checks printed (CHECK name PASS|FAIL ...): rows, buildings per split, no held-out stem left, every stem once per split,
n_flats > 0, unique run_id, expected rows per building, plan md5.
Step 9o (additive): `--vintage win_2026-10-05` (Madrid only): FLEET paths and src md5 read from the `_win_2026-10-05` folders; building lists = the
SEALED `buildsplit_win3` lists (rule R1 a: a building keeps its sealed split), hold-out = `heldout_tinyflats_win5.csv` (rule R1 b; `--heldout win3` keeps
the 10-03 hold-out), n_flats from `2026-10-01_wp9c_wall_table_win5.csv`; sealed stems whose zone map is unusable on 10-05 (no `_dwelling_<n>` zones) are
dropped and printed. Without `--vintage` the script behaves exactly as before (10-03).
UK licence: only the two district names are accepted; the base IDF md5 is read from the two district folders of _win_2026-10-03 by
the full file name of each stem (no listing, no wildcard).
"""
import csv, hashlib, io, os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
IMPL = os.path.normpath(os.path.join(HERE, "..", "..", "Step9_docs", "impl"))
EU11 = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11"
VINT = "win_2026-10-03"
FLEET = "/speed-scratch/o_iseri/fleets"
DISTRICTS = ("ES-MAD-BERRUGUETE", "IT-BOL-GALVANI2")
EXPECT = {"ES-MAD-BERRUGUETE": {"rows": 9201, "dev": 795, "val": 172, "test": 169}}   # rules R2 (Bologna waits for _win_2026-10-04)
POOLS = {"dev": [("dev", 3), ("val", 2), ("test", 2)], "val": [("dev", 2), ("val", 2)], "test": [("dev", 2), ("test", 2)]}
# step 9o: expected counts for `_win_2026-10-05` = sealed lists 816 / 176 / 173 minus the 10-05 hold-out by SEALED split (dev 6, val 2) minus the
# 2 sealed stems with no dwelling zones on 10-05 (both dev: bb4d3f44d4fbe5b1, bf1fa61d6ffd3b54); rows = 9 x dev + 6 x val + 6 x test
EXPECT_WIN5 = {"ES-MAD-BERRUGUETE": {"rows": 9 * 808 + 6 * 174 + 6 * 173, "dev": 808, "val": 174, "test": 173}}
COLS = ["run_id", "district", "stem", "building_split", "pool", "r", "mode", "n_flats", "seed", "src_idf", "src_idf_md5"]


def run_seed_of(run_id):
    """Same rule as tools/5thJ_modelA_households.py run_seed_of (md5 of the id, first 8 hex, mod 2147483647)."""
    return int(hashlib.md5(run_id.encode()).hexdigest()[:8], 16) % 2147483647


def md5_file(p):
    h = hashlib.md5()
    with io.open(p, "rb") as fh:
        for ch in iter(lambda: fh.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def read_csv(p):
    with io.open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def check(name, ok, msg=""):
    print("CHECK %s %s %s" % (name, "PASS" if ok else "FAIL", msg), flush=True)
    return ok


def build_rows(district, lists, heldout_stems, md5_of=None):
    """lists: split -> rows (stem, n_flats ...). Returns (rows, kept_buildings per split)."""
    rows, kept = [], {}
    for sp in ("dev", "val", "test"):
        kept[sp] = []
        for b in lists[sp]:
            if b["stem"] in heldout_stems:
                continue
            kept[sp].append(b)
            src = "%s/EU11_%s_%s/idfs/%s.idf" % (FLEET, district, VINT, b["stem"])
            m5 = md5_of(b["stem"]) if md5_of else ""
            plan = [(p, r, "occupancy") for p, n in POOLS[sp] for r in range(1, n + 1)]
            plan += [("b0", 0, "occupancy"), ("def", 0, "default")]
            for pool, r, mode in plan:
                rid = "%s_%s_%s_%d" % (district, b["stem"], pool, r)
                rows.append(dict(run_id=rid, district=district, stem=b["stem"], building_split=sp, pool=pool, r=r, mode=mode,
                                 n_flats=b["n_flats"], seed=run_seed_of(rid), src_idf=src, src_idf_md5=m5))
    return rows, kept


def run_checks(district, rows, kept, lists, heldout_stems, expect):
    ok = True
    n = dict((sp, len(kept[sp])) for sp in kept)
    ok &= check("rows_%s" % district, len(rows) == expect["rows"], "rows=%d expected=%d" % (len(rows), expect["rows"]))
    ok &= check("buildings_per_split", all(n[sp] == expect[sp] for sp in ("dev", "val", "test")),
                "dev=%d val=%d test=%d expected %d/%d/%d" % (n["dev"], n["val"], n["test"], expect["dev"], expect["val"], expect["test"]))
    left = [r["stem"] for r in rows if r["stem"] in heldout_stems]
    ok &= check("no_heldout_stem_in_plan", not left, "left=%d" % len(left))
    allst = [b["stem"] for sp in kept for b in kept[sp]]
    ok &= check("each_stem_once", len(allst) == len(set(allst)), "stems=%d unique=%d" % (len(allst), len(set(allst))))
    ok &= check("run_id_unique", len(set(r["run_id"] for r in rows)) == len(rows))
    ok &= check("n_flats_positive", all(int(r["n_flats"]) > 0 for r in rows))
    per = {}
    for r in rows:
        per[r["stem"]] = per.get(r["stem"], 0) + 1
    want = {"dev": 9, "val": 6, "test": 6}
    sp_of = dict((b["stem"], sp) for sp in kept for b in kept[sp])
    ok &= check("runs_per_building_9_6_6", all(per[s] == want[sp_of[s]] for s in per), "buildings=%d" % len(per))
    return ok


def selftest(district="ES-MAD-BERRUGUETE"):
    lists = dict((sp, read_csv("%s/buildsplit_win3/%s_%s.csv" % (IMPL, district, sp))) for sp in ("dev", "val", "test"))
    held = set(r["stem"] for r in read_csv(IMPL + "/heldout_tinyflats_win3.csv") if r["district"] == district)
    rows, kept = build_rows(district, lists, held)
    good = run_checks(district, rows, kept, lists, held, EXPECT[district])
    # planted: ONE held-out stem is left in the list (not removed): the count check must FAIL
    plant = sorted(held)[0]
    rows2, kept2 = build_rows(district, lists, held - set([plant]))
    print("--- planted fault: held-out stem %s left in the plan ---" % plant)
    bad = run_checks(district, rows2, kept2, lists, held, EXPECT[district])
    print("CONTROL planted_heldout_left_in_list %s (the checks above must show FAIL)" % ("FIRED" if (good and not bad) else "DID_NOT_FIRE"))
    return 0 if (good and not bad) else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "--selftest":
        return selftest()
    district = argv[1]
    if district not in DISTRICTS:
        sys.exit("STOP: district %r not allowed" % district)
    global VINT
    out = argv[argv.index("--out") + 1]
    if "--vintage" in argv:
        VINT = argv[argv.index("--vintage") + 1]
        if VINT not in ("win_2026-10-03", "win_2026-10-05"):
            sys.exit("STOP: vintage %r not allowed" % VINT)
    win5 = (VINT == "win_2026-10-05")
    if win5 and district != "ES-MAD-BERRUGUETE":
        sys.exit("STOP: win_2026-10-05 is delivered for Madrid only")
    lists = dict((sp, read_csv("%s/buildsplit_win3/%s_%s.csv" % (IMPL, district, sp))) for sp in ("dev", "val", "test"))
    hsrc = argv[argv.index("--heldout") + 1] if "--heldout" in argv else ("win5" if win5 else "win3")
    held = set(r["stem"] for r in read_csv(IMPL + "/heldout_tinyflats_%s.csv" % hsrc) if r["district"] == district)
    print("vintage %s; building lists = sealed buildsplit_win3; hold-out source = heldout_tinyflats_%s.csv; heldout stems of %s: %d" % (VINT, hsrc, district, len(held)))
    expect = EXPECT.get(district, {"rows": -1, "dev": -1, "val": -1, "test": -1})
    if win5:
        nf5 = {}
        for r in read_csv(IMPL + "/2026-10-01_wp9c_wall_table_win5.csv"):
            if r["district"] == district and not r["zone_map_reason"].strip():
                nf5[r["stem"]] = r["n_flats"]
        dropped = []
        for sp in ("dev", "val", "test"):
            keep = []
            for b in lists[sp]:
                if b["stem"] not in nf5:
                    dropped.append((b["stem"], sp, b["n_flats"]))
                    continue
                keep.append(dict(b, n_flats=nf5[b["stem"]]))
            lists[sp] = keep
        print("DROPPED sealed stems with no dwelling zones on 10-05 (not in the plan, hold-out or not): %s" % dropped)
        expect = EXPECT_WIN5[district]
    cache = {}

    def md5_of(stem):
        if "--no-md5" in argv:
            return ""
        if stem not in cache:
            cache[stem] = md5_file("%s/%s_%s/idfs/%s.idf" % (EU11, district, VINT, stem))
        return cache[stem]

    rows, kept = build_rows(district, lists, held, md5_of)
    ok = run_checks(district, rows, kept, lists, held, expect)
    with io.open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print("PLAN %s rows=%d md5=%s" % (out, len(rows), md5_file(out)))
    if "--smoke-out" in argv:
        # smoke: small dev (fewest flats, >=2), large dev (most flats), one val, one test (nearest 6 flats), triangle building if present
        def pick(sp, key):
            c = sorted(kept[sp], key=key)
            return c[0]["stem"]
        flats = lambda b: (int(b["n_flats"]), b["stem"])
        small = pick("dev", lambda b: (int(b["n_flats"]) < 2, int(b["n_flats"]), b["stem"]))
        large = sorted(kept["dev"], key=lambda b: (-int(b["n_flats"]), b["stem"]))[0]["stem"]
        val = pick("val", lambda b: (abs(int(b["n_flats"]) - 6), b["stem"]))
        test = pick("test", lambda b: (abs(int(b["n_flats"]) - 6), b["stem"]))
        stems = [small, large, val, test]
        tri = "1271cddbf6bd1e8a"
        in_plan = [b for sp in kept for b in kept[sp] if b["stem"] == tri]
        if in_plan and tri not in stems:
            stems.append(tri)
        sm = [r for r in rows if r["stem"] in stems]
        so = argv[argv.index("--smoke-out") + 1]
        with io.open(so, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
            w.writeheader()
            w.writerows(sm)
        nf = dict((b["stem"], b["n_flats"]) for sp in kept for b in kept[sp])
        print("SMOKE %s rows=%d stems=%s flats=%s triangle_in_plan=%s md5=%s" % (so, len(sm), stems, [nf[s] for s in stems], bool(in_plan), md5_file(so)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
