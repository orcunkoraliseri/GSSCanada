"""Re-serialise the production C-VAE models (saved by keras 3.13.2) so that keras 3.10 on Speed can load them.

Why: smoke job 1401430 failed loading 0_Occupancy/saved_models_cvae/*.keras under keras 3.10
("Unrecognized keyword arguments passed to Dense: {'quantization_config': None}").
What: config.json keys written by 3.13 but absent from a model saved by 3.10 on Speed (smoke model, compared key by key
per layer class) are removed, ONLY if they hold their default value:
    Dense.quantization_config None, InputLayer.optional False, Sampling.activity_regularizer None, Sampling.autocast True.
model.weights.h5 and metadata.json are copied byte for byte. The originals are not touched.
Check: the fingerprint (md5 of each weight's bytes + outputs on a fixed input) of the ORIGINAL models under keras 3.13 is written to
prod_fingerprint_k313.json; the converted copies must give the same fingerprint here (3.13) and on Speed (3.10, probe job).
Usage (locally): py convert_prod_models_k310.py
"""
import json
import os
import sys
import zipfile

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(REPO, "0_Occupancy", "saved_models_cvae")
DST = os.path.join(HERE, "prod_models_k310")
DROP = {"Dense": {"quantization_config": None}, "InputLayer": {"optional": False},
        "Sampling": {"activity_regularizer": None, "autocast": True}}

removed = []


def strip(o):
    if isinstance(o, dict):
        cls, cfg = o.get("class_name"), o.get("config")
        if cls in DROP and isinstance(cfg, dict):
            for k, default in DROP[cls].items():
                if k in cfg:
                    assert cfg[k] == default, f"{cls}.{k} = {cfg[k]!r}, not the default {default!r}: refuse to drop"
                    del cfg[k]
                    removed.append(f"{cls}.{k}")
        for v in o.values():
            strip(v)
    elif isinstance(o, list):
        for v in o:
            strip(v)


os.makedirs(DST, exist_ok=True)
for part in ["encoder", "decoder"]:
    src, dst = os.path.join(SRC, f"cvae_{part}.keras"), os.path.join(DST, f"cvae_{part}.keras")
    zi = zipfile.ZipFile(src)
    cfg = json.loads(zi.read("config.json"))
    strip(cfg)
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_STORED) as zo:
        for name in zi.namelist():
            zo.writestr(name, json.dumps(cfg) if name == "config.json" else zi.read(name))
    zc = zipfile.ZipFile(dst)
    for name in ["model.weights.h5", "metadata.json"]:
        assert zc.read(name) == zi.read(name), f"{part} {name} not byte-identical"
    left = json.dumps(json.loads(zc.read("config.json")))
    for cls, keys in DROP.items():
        for k in keys:
            assert f'"{k}":' not in left or cls == "Sampling" and k == "autocast" and '"autocast":' not in left, f"{k} still in {part}"
    print(f"{part}: weights + metadata byte-identical; config keys removed so far: {len(removed)}")
from collections import Counter
print("REMOVED:", dict(Counter(removed)))

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "eSim", "eSim_occ_utils", "25CEN22GSS_classification"))
os.environ["WP4_MH_DIR"] = sys.path[0]
import wp4_hindcast as w  # noqa: E402

enc0, dec0 = w.load_models(SRC)
fp0 = w.model_fingerprint(enc0, dec0)
json.dump(fp0, open(os.path.join(HERE, "prod_fingerprint_k313.json"), "w"))
enc1, dec1 = w.load_models(DST)
f = w.compare_fingerprints(w.model_fingerprint(enc1, dec1), fp0)
bad = json.loads(json.dumps(fp0)); k0 = sorted(bad["dec_w"])[-1]; bad["dec_w"][k0] = "0" + bad["dec_w"][k0][1:]
assert w.compare_fingerprints(fp0, bad), "fingerprint check failed to fail on a nudged copy"
print("fingerprint check seen failing on a nudged copy:", w.compare_fingerprints(fp0, bad))
print(f"converted copies under keras 3.13: {'SAME MODEL' if not f else 'DIFFERENT ' + str(f)}")
assert not f
print(f"written {DST} and prod_fingerprint_k313.json (encoder {len(fp0["enc_w"])} + decoder {len(fp0["dec_w"])} variables, keyed by path)")
