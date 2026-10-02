# -*- coding: utf-8 -*-
"""Step 9p item 6: additive edit of tools/speed/a9_campaign_plan.py: `--vintage win_2026-10-05` is now also accepted for IT-BOL-GALVANI2 (lists = buildsplit_bol5 derived on
the new base, provisional until the manager seals them by amendment A2; hold-out = heldout_tinyflats_bol5.csv; n_flats from the `_bol5` wall table).
Madrid (10-03 and 10-05) and the --selftest path are untouched: every edit sits behind `bol5 = (VINT == win_2026-10-05 and district == IT-BOL-GALVANI2)`.
Each edit must match exactly once; one PATCH line per edit."""
import io, sys, os
P = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "tools", "speed", "a9_campaign_plan.py"))
t = io.open(P, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
E = [
    ("a_expect",
     'COLS = ["run_id",',
     '# step 9p: expected counts for Bologna on `_win_2026-10-05`, written BEFORE the run from the lists and the hold-out: buildsplit_bol5 lists 818 / 176 / 173 (md5 89686455... / b8910b92... / 577eca43...),\n'
     '# hold-out heldout_tinyflats_bol5.csv = 3 buildings (dev 1, test 2) -> 817 / 176 / 171; rows = 9 x dev + 6 x val + 6 x test\n'
     'EXPECT_BOL5 = {"IT-BOL-GALVANI2": {"rows": 9 * 817 + 6 * 176 + 6 * 171, "dev": 817, "val": 176, "test": 171}}\n'
     'COLS = ["run_id",'),
    ("b_vintage_district",
     '    win5 = (VINT == "win_2026-10-05")\n    if win5 and district != "ES-MAD-BERRUGUETE":\n        sys.exit("STOP: win_2026-10-05 is delivered for Madrid only")\n'
     '    lists = dict((sp, read_csv("%s/buildsplit_win3/%s_%s.csv" % (IMPL, district, sp))) for sp in ("dev", "val", "test"))\n'
     '    hsrc = argv[argv.index("--heldout") + 1] if "--heldout" in argv else ("win5" if win5 else "win3")\n',
     '    bol5 = (VINT == "win_2026-10-05" and district == "IT-BOL-GALVANI2")   # step 9p\n'
     '    win5 = (VINT == "win_2026-10-05") and not bol5\n'
     '    if VINT == "win_2026-10-05" and district not in ("ES-MAD-BERRUGUETE", "IT-BOL-GALVANI2"):\n        sys.exit("STOP: win_2026-10-05 is delivered for Madrid and Bologna only")\n'
     '    lists = dict((sp, read_csv("%s/%s/%s_%s.csv" % (IMPL, "buildsplit_bol5" if bol5 else "buildsplit_win3", district, sp))) for sp in ("dev", "val", "test"))\n'
     '    hsrc = argv[argv.index("--heldout") + 1] if "--heldout" in argv else ("bol5" if bol5 else ("win5" if win5 else "win3"))\n'),
    ("c_print",
     '    print("vintage %s; building lists = sealed buildsplit_win3; hold-out source = heldout_tinyflats_%s.csv; heldout stems of %s: %d" % (VINT, hsrc, district, len(held)))\n',
     '    print("vintage %s; building lists = %s; hold-out source = heldout_tinyflats_%s.csv; heldout stems of %s: %d" % (VINT, "buildsplit_bol5 (PROVISIONAL: derived on the new base, not sealed until amendment A2)" if bol5 else "sealed buildsplit_win3", hsrc, district, len(held)))\n'),
    ("d_nflats",
     '    if win5:\n        nf5 = {}\n        for r in read_csv(IMPL + "/2026-10-01_wp9c_wall_table_win5.csv"):\n',
     '    if bol5:\n'
     '        nfb = {}\n'
     '        for r in read_csv(IMPL + "/2026-10-01_wp9c_wall_table_bol5.csv"):\n'
     '            if r["district"] == district and not r["zone_map_reason"].strip():\n'
     '                nfb[r["stem"]] = r["n_flats"]\n'
     '        bad = [(sp, b["stem"]) for sp in ("dev", "val", "test") for b in lists[sp] if nfb.get(b["stem"]) != b["n_flats"]]\n'
     '        print("n_flats of the bol5 lists vs the bol5 wall table: %d lists rows, %d differ" % (sum(len(lists[sp]) for sp in lists), len(bad)))\n'
     '        if bad:\n            sys.exit("STOP: list n_flats differs from the wall table: %s" % bad[:5])\n'
     '        expect = EXPECT_BOL5[district]\n'
     '    if win5:\n        nf5 = {}\n        for r in read_csv(IMPL + "/2026-10-01_wp9c_wall_table_win5.csv"):\n'),
]
for name, old, new in E:
    old, new = old.replace("\n", nl), new.replace("\n", nl)
    n = t.count(old)
    if n != 1:
        sys.exit("STOP: edit %s matches %d times (nothing written)" % (name, n))
    t = t.replace(old, new)
io.open(P, "w", encoding="utf-8", newline="").write(t)
for name, _, _ in E:
    print("PATCH a9_campaign_plan.py %s OK" % name)
