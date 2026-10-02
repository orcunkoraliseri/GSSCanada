# -*- coding: utf-8 -*-
"""Step 9p item 7: the Bologna COPY of the campaign runner (staged under /speed-scratch/o_iseri/5J/modelA/campaign_bol5/, never the live campaign).
Starts from the local tools/speed/a9_campaign_task.py (md5 4bef1d82... = the live file) and changes exactly these spots (each must match once):
 1 LIVE_CAMP  -> campaign_bol5 (data root; A9_CAMP still overrides)
 2 VINT       -> win_2026-10-05
 3 ZMAP       -> inputs/zone_map_bol5.csv, ZMAP_MD5 = md5 of the local zone map `2026-10-01_wp9c_zone_map_bol5.csv`
 4 prep loop  -> builds the B0 household for `it` and skips `es` (the Madrid B0 is not needed here)
Compiles the result (compile(), no run)."""
import io, os, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); OUTD = os.path.dirname(HERE); IMP = os.path.dirname(OUTD)
SRC = os.path.normpath(os.path.join(IMP, "..", "..", "tools", "speed", "a9_campaign_task.py"))
DST = os.path.join(OUTD, "campaign_bol5_code", "5J_docs_occ", "tools", "a9_campaign_task.py")
zm = hashlib.md5(io.open(os.path.join(IMP, "2026-10-01_wp9c_zone_map_bol5.csv"), "rb").read()).hexdigest()
t = io.open(SRC, encoding="utf-8", newline="").read()
E = [
    ("1_camp", 'LIVE_CAMP = "/speed-scratch/o_iseri/5J/modelA/campaign"\n',
     '# Step 9p COPY (staged in campaign_bol5, never the live campaign): data root, base vintage and zone map point at the Bologna 10-05 delivery.\n'
     'LIVE_CAMP = "/speed-scratch/o_iseri/5J/modelA/campaign_bol5"\n'),
    ("2_vint", 'VINT = "win_2026-10-03"\n', 'VINT = "win_2026-10-05"\n'),
    ("3_zmap", 'ZMAP = CAMP + "/inputs/zone_map_win3.csv"\nZMAP_MD5 = "1c48d2e5240962a88ca16279dd089d50"\n',
     'ZMAP = CAMP + "/inputs/zone_map_bol5.csv"\nZMAP_MD5 = "%s"\n' % zm),
    ("4_prep_loop", '        if c == "it":\n            continue                                   # Bologna waits for _win_2026-10-04; its B0 is built when it is run\n',
     '        if c == "es":\n            continue                                   # Step 9p Bologna copy: only the Italian B0 is built here (the Madrid B0 lives in the Madrid campaign)\n'),
]
for name, old, new in E:
    n = t.count(old)
    if n != 1:
        sys.exit("STOP: edit %s matches %d times" % (name, n))
    t = t.replace(old, new)
compile(t, DST, "exec")
io.open(DST, "w", encoding="utf-8", newline="").write(t)
for name, _, _ in E:
    print("PATCH a9_campaign_task.py(bol5 copy) %s OK" % name)
print("zone map md5 written into the copy:", zm)
print("copy md5:", hashlib.md5(t.encode("utf-8")).hexdigest(), "source md5:", hashlib.md5(io.open(SRC, "rb").read()).hexdigest())
