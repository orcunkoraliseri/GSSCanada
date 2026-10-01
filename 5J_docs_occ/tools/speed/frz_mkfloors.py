# 5J Step 4 fix 1, R4: planted HIGH floors file (val 5.2). Same layout as out/floors.json, every floor = 1.0e6 kWh. Speed job only; never overwrites.
import json, io, os, hashlib
F = "/speed-scratch/o_iseri/5J/freeze/out/"
src = json.load(io.open(F + "floors.json", encoding="utf-8"))
dst = F + "floors_PLANTED_HIGH.json"
assert not os.path.exists(dst), "additive only"
n = 0
for c in src["floor"]:
    for t in src["floor"][c]:
        src["floor"][c][t] = 1.0e6; n += 1
src["note"] = "PLANTED HIGH FLOOR for val 5.2: every floor 1.0e6 kWh (not a measurement)"
json.dump(src, io.open(dst, "w", encoding="utf-8"), indent=1)
print("WROTE", dst, "floors set", n, "keys", sorted(src.keys()))
print("MD5", hashlib.md5(open(dst, "rb").read()).hexdigest())
print(open(dst).read()[:600])
