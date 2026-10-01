# -*- coding: utf-8 -*-
"""5J Step 5 part E (GPU, before the trainings): the winner's reload check again with the NEW code, all new flags off (flags-off
reproduction, val 4.3). READ-ONLY: it never writes to train/winner/pinned/ or to any checkpoint. Recomputes the validation loss of
the pinned winner (S3) on the fixed 20,000 draws and compares with the value stored in the checkpoint and in winner.json to 4 decimals."""
import glob, hashlib, json, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, "/speed-scratch/o_iseri/5J/train")
import torch
import s5_data as sd
import s5_models as sm
import s5_train as st

T = "/speed-scratch/o_iseri/5J/train/"
W = json.load(open(T + "winner/winner.json"))
pin = T + "winner/pinned/best.pt"
m = hashlib.md5(open(pin, "rb").read()).hexdigest()
print("PINNED md5 now=%s winner.json=%s file=%s" % (m, W["ckpt_md5"], open(T + "winner/pinned/best.pt.md5").read().split()[0]), flush=True)
for p in sorted(glob.glob(T + "s5_*.py")) + [T + "s5_grid.json"]:
    print("CODE_MD5 %s %s" % (os.path.basename(p), hashlib.md5(open(p, "rb").read()).hexdigest()), flush=True)
ck = torch.load(pin, map_location="cuda", weights_only=False)
cfg = ck["config"]
st.seed_all(cfg["seed"])
dv = sd.Data("validation", "cuda", stats=ck["static_stats"])
model = sm.build_model(cfg, dv.n_dyn, dv.S).to("cuda")
model.load_state_dict(ck["state_dict"])
draws = sd.validation_draws(len(dv.pa), cfg["val_draws"], cfg["val_seed"])
vl, vp = st.evaluate(model, dv, draws)
print("RELOAD_NEWCODE_FLAGS_OFF S%d: stored val_sum=%.6f (level %.6f pair %.6f) recomputed val_sum=%.6f (level %.6f pair %.6f) winner.json=%.6f" %
      (W["config_index"], ck["val_sum"], ck["val_level"], ck["val_pair"], vl + vp, vl, vp, W["validation_loss"]), flush=True)


def same4(a, b):
    return abs(a - b) < 5e-5


print("CHECK reload_planted_shift_1e-3_FAILS (seen failing) %s" % ("PASS" if not same4(vl + vp + 1e-3, ck["val_sum"]) else "FAIL"), flush=True)
ok = same4(vl + vp, ck["val_sum"]) and same4(vl + vp, W["validation_loss"]) and m == W["ckpt_md5"]
print("CHECK reload_newcode_flags_off_equal_4dp_and_md5 %s" % ("PASS" if ok else "FAIL"), flush=True)
sys.exit(0 if ok else 3)
