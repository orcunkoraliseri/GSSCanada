"""List P10R campaign cells whose stored INPUTS_HASH no longer matches the current Step-7 products
(hotel_obs switch 2026-09-25). The local driver's cell_ok() does not look at INPUTS_HASH, so these
cells must be moved out of campaign_local_P10R before the driver is re-run, or it skips them."""
import importlib.util, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LEG3 = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "Leg3_4-split"))
S8 = os.path.join(LEG3, "Step8_docs")
REPO = os.path.normpath(os.path.join(LEG3, "..", ".."))
sys.path.insert(0, S8); sys.path.insert(0, os.path.join(REPO, "eSim"))
def load(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cells_mod = load(os.path.join(S8, "3rdJ_08D_campaign_cells.py"), "cells")
probe = load(os.path.join(S8, "3rdJ_08P_probe_driver.py"), "probe")
cells = cells_mod.build_campaign_cells(REPO, step7_out=os.path.join(LEG3, "Step7_docs", "outputs_step7_P10R"))
stale, same, nomani = [], [], []
for c in cells:
    h, _ = probe._compute_inputs_hash(c["channels"])
    mp = os.path.join(S8, "campaign_local_P10R", c["tag"], "manifest.json")
    if not os.path.isfile(mp):
        nomani.append(c["tag"]); continue
    old = json.load(open(mp, encoding="utf-8")).get("INPUTS_HASH")
    (same if old == h else stale).append(c["tag"])
print("cells=%d stale=%d unchanged=%d no_manifest=%d" % (len(cells), len(stale), len(same), len(nomani)))
for t in stale: print("STALE", t)
for t in nomani: print("NO_MANIFEST", t)
