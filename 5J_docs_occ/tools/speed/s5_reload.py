# -*- coding: utf-8 -*-
"""5J Step 5 part D, step E (GPU): fresh-process reload check of the winner (R7.4, val 4.3): recompute the validation loss on the fixed
20,000 draws with the reloaded best.pt, compare with the logged value to 4 decimals; if PASS copy the checkpoint to train/winner/pinned/
with an md5 file, chmod 444. Validation split only."""
import hashlib, json, os, shutil, sys
sys.dont_write_bytecode = True
sys.path.insert(0, "/speed-scratch/o_iseri/5J/train")
import torch
import s5_data as sd
import s5_models as sm
import s5_train as st

T = "/speed-scratch/o_iseri/5J/train/"
W = json.load(open(T + "winner/winner.json"))
ck = torch.load(W["ckpt"], map_location="cuda", weights_only=False)
cfg = ck["config"]
st.seed_all(cfg["seed"])
dv = sd.Data("validation", "cuda", stats=ck["static_stats"])
model = sm.build_model(cfg, dv.n_dyn, dv.S).to("cuda")
model.load_state_dict(ck["state_dict"])
draws = sd.validation_draws(len(dv.pa), cfg["val_draws"], cfg["val_seed"])
vl, vp = st.evaluate(model, dv, draws)
print("RELOAD S%d: logged val_sum=%.6f (level %.6f pair %.6f)  recomputed val_sum=%.6f (level %.6f pair %.6f)" %
      (W["config_index"], ck["val_sum"], ck["val_level"], ck["val_pair"], vl + vp, vl, vp))
# manager fix 2026-10-01 00:30: winner.json holds the loss as logged in train_log.tsv (6 dp), so the old "< 1e-9" test against
# the checkpoint float failed on equal values (job 1404811: 0.125884 = 0.125884); "equal to 4 dp" is |diff| < 5e-5.
def same4(a, b):
    return abs(a - b) < 5e-5
d_re, d_js = abs((vl + vp) - ck["val_sum"]), abs(ck["val_sum"] - W["validation_loss"])
print("RELOAD_DIFF recomputed-vs-ckpt %.3e ; ckpt-vs-winner.json %.3e (json is 6 dp)" % (d_re, d_js))
print("CHECK reload_planted_shift_1e-3_FAILS (seen failing) %s" % ("PASS" if not same4(vl + vp + 1e-3, ck["val_sum"]) else "FAIL"))
ok = same4(vl + vp, ck["val_sum"]) and d_js < 5e-7
print("CHECK reload_val_loss_equal_4dp (R7.4, val 4.3) %s" % ("PASS" if ok else "FAIL"))
if not ok:
    sys.exit(3)
d = T + "winner/pinned/"
os.makedirs(d, exist_ok=True)
dst = d + "best.pt"
if os.path.exists(dst):
    os.chmod(dst, 0o644)
shutil.copyfile(W["ckpt"], dst)
m = hashlib.md5(open(dst, "rb").read()).hexdigest()
open(d + "best.pt.md5", "w").write("%s  best.pt\n" % m)
os.chmod(dst, 0o444)
os.chmod(d + "best.pt.md5", 0o444)
print("CHECK pinned_md5_equals_winner_json %s  md5=%s" % ("PASS" if m == W["ckpt_md5"] else "FAIL", m))
if m != W["ckpt_md5"]:
    sys.exit(3)
print("PINNED %s mode=%s" % (dst, oct(os.stat(dst).st_mode & 0o777)))
print("RELOAD_DONE")
