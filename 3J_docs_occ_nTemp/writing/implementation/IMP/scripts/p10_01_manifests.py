"""P10 step 1: which Step-7 product (by md5) did every frozen deliverable cell inject?
Read-only. Prints scenario x channel -> file name + md5, and maps md5 to the files on disk now."""
import json, hashlib, glob, os
from pathlib import Path
from collections import defaultdict

J3 = Path(__file__).resolve().parents[4]
CELLS = J3 / "Leg3_4-split/Step8_docs/campaign_local_deliverable"
S7 = J3 / "Leg3_4-split/Step7_docs/outputs_step7"

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

disk = defaultdict(list)
for p in list(S7.glob("*.csv")) + list(S7.glob("archive_pre_20260730/*.csv")):
    disk[md5(p)].append(p.relative_to(S7).as_posix())

rows = defaultdict(set)
for m in sorted(CELLS.glob("*/manifest.json")):
    j = json.load(open(m, encoding="utf-8"))
    scen = j.get("scenario")
    for d in j.get("INPUTS_HASH_DETAIL", []) or []:
        rows[(scen, d["channel"])].add((Path(d["csv_path"]).name, d["csv_md5"]))
    ch = j.get("channels_requested", {})
    extra = {k: (v.get("band"), v.get("archetype"), v.get("pr"), v.get("seed")) for k, v in ch.items()}
    rows[(scen, "_meta")].add((str(sorted(extra.items())), j.get("INJ_HASH"), j.get("INPUTS_HASH")))

for k in sorted(rows):
    for v in sorted(rows[k]):
        onDisk = disk.get(v[1], ["NOT ON DISK"]) if k[1] != "_meta" else ""
        print(k, v, onDisk)
