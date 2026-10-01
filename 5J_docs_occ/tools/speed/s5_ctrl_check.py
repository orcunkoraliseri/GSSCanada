# -*- coding: utf-8 -*-
"""5J Step 5 part E, code checks (CPU job, runs BEFORE any training; Spain + Italy; development / validation only).
Every check prints `CHECK <name> PASS|FAIL`; planted-fault checks are marked (seen failing). Exit 1 if any FAIL.
 1. config diff: C's config vs the winner's = only blind:true -> PASS; a config with one more difference -> FAIL (planted).
 2. blind donors (rules R8): none from the same run (0), none from another country (0); 3 donors re-derived with an independent loop from
    the md5 rule; planted donor from the same run -> caught by donor_violations; a blind window = donor's household + neighbour channels,
    own weather / calendar / static / target.
 3. one-country filter (rules R9): only that country; targets and pairs follow the filter; static mean from that country's rows only;
    climate columns dropped; static column count before / after.
 4. flags off: the new Data class equals the archived original (old_s5_data.py copy) on every tensor of the validation split."""
import argparse, hashlib, importlib.util, json, os, random, sys
sys.dont_write_bytecode = True
sys.path.insert(0, "/speed-scratch/o_iseri/5J/train")
import numpy as np
import pandas as pd
import torch
import s5_common as c
import s5_data as sd
import s5_train as st

T = c.TRAIN
fails = []


def chk(name, ok, text=""):
    print("CHECK %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)
    if not ok:
        fails.append(name)


# ---------------------------------------------------------------- 1. config diff
w = json.load(open(T + "winner/winner.json"))["config"]
ns = argparse.Namespace(seed=1, blind=True, country=None, no_climate=False)
cC = st.control_flags(w, ns)
chk("config_diff_C_vs_winner_only_blind_true", st.check_control_config(cC))
cBad = dict(cC)
cBad["lam"] = 0
chk("config_diff_planted_second_difference_FAILS (seen failing)", not st.check_control_config(cBad))
cBad2 = dict(cC)
cBad2["width"] = 128
chk("config_diff_planted_width_change_FAILS (seen failing)", not st.check_control_config(cBad2))
g3 = st.load_config("3")
chk("grid_index_3_equals_winner_config", st.config_diff(w, g3) == {}, "diff=%s" % st.config_diff(w, g3))
chk("seed_flag_only_changes_seed", list(st.config_diff(w, st.control_flags(w, argparse.Namespace(seed=2, blind=False, country=None, no_climate=False))).keys()) == ["seed"])
chk("flags_off_config_unchanged", st.control_flags(w, argparse.Namespace(seed=None, blind=False, country=None, no_climate=False)) == w)

# ---------------------------------------------------------------- 4 first (old vs new, flags off)
spec = importlib.util.spec_from_file_location("old_s5_data", T + "ctrl_check/old_s5_data.py")
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
print("md5 old_s5_data.py = %s (expected 890d5c64...)" % hashlib.md5(open(T + "ctrl_check/old_s5_data.py", "rb").read()).hexdigest(), flush=True)
dn = sd.Data("validation", "cpu", load_targets=True)
do = old.Data("validation", "cpu", load_targets=True)
same = {nm: bool(torch.equal(getattr(dn, nm), getattr(do, nm))) for nm in ["static", "hh_row", "nb", "pa", "pb", "cl_idx", "cal_idx", "T", "HHT", "W", "CAL"]}
chk("flags_off_new_Data_equals_original_on_all_tensors", all(same.values()) and dn.stats == do.stats and dn.static_names == do.static_names, str(same))
rows = torch.tensor([0, 5, 100, 4000, 7000])
days = torch.tensor([0, 200, 364, 17, 90])
xn, sn, yn = dn.windows(rows, days)
xo, so, yo = do.windows(rows, days)
chk("flags_off_windows_equal", bool(torch.equal(xn, xo) and torch.equal(sn, so) and torch.equal(yn, yo)))

# ---------------------------------------------------------------- 2. blind
db = sd.Data("validation", "cpu", load_targets=True, blind=True)
fl, bi = db.flats, db.blind_info
chk("blind_no_donor_from_same_run_or_other_country", bi["donor_same_run"] == 0 and bi["donor_other_country"] == 0, str(bi))
print("INFO blind share_donor_hid_equals_own_hid = %.5f over %d rows" % (bi["share_donor_hid_equals_own_hid"], bi["n_rows"]), flush=True)
base = pd.read_parquet(sd.STORE + "flats_validation.parquet")
run_a, cty_a = base["run_id"].to_numpy(), base["country"].to_numpy()
donor = fl["donor_row"].to_numpy()
# independent re-derivation of 3 donors (plain loop, written separately from blind_donors)
ok3 = True
for i in (0, 3333, len(base) - 1):
    rng = random.Random(int(hashlib.md5(("%s|%d|blind|20260930" % (base["run_id"].iloc[i], int(base["flat"].iloc[i]))).encode()).hexdigest(), 16))
    cand = [r for r in range(len(base)) if cty_a[r] == cty_a[i]]
    while True:
        j = cand[rng.randrange(len(cand))]
        if run_a[j] != run_a[i]:
            break
    print("  donor re-derived row %d (%s flat %d) -> row %d (%s flat %d) ; table donor_row=%d" % (i, run_a[i], base["flat"].iloc[i], j, run_a[j], base["flat"].iloc[j], donor[i]), flush=True)
    ok3 = ok3 and (j == donor[i])
chk("blind_3_donors_rederived_from_md5_rule", ok3)
bad = donor.copy()
bad[10] = 10
v = sd.donor_violations(run_a, cty_a, bad)
chk("blind_planted_same_run_donor_CAUGHT (seen failing)", v[0] >= 1, "violations=%s" % (v,))
bad2 = donor.copy()
bad2[10] = int(np.flatnonzero(cty_a != cty_a[10])[0])
v2 = sd.donor_violations(run_a, cty_a, bad2)
chk("blind_planted_other_country_donor_CAUGHT (seen failing)", v2[1] >= 1, "violations=%s" % (v2,))
chk("blind_building_static_climate_unchanged", all((fl[col].to_numpy() == base[col].to_numpy()).all() for col in ["run_id", "building_id", "flat", "climate_id", "country"] + list(db.s_cols)))
chk("blind_drivers_equal_donor_row_of_original", all((fl[col].to_numpy() == base[col].to_numpy()[donor]).all() for col in sd.BLIND_COLS))
# a blind window = donor's household + neighbour channels (0..12), own weather / calendar (13..24), own static and target
ok_w = True
xb, sb, yb = db.windows(rows, days)
for k in range(len(rows)):
    i = int(rows[k]); j = int(donor[i])
    xd, _, _ = dn.windows(torch.tensor([j]), days[k:k + 1])
    xi, si, yi = dn.windows(torch.tensor([i]), days[k:k + 1])
    ok_w = ok_w and bool(torch.equal(xb[k, :, :13], xd[0, :, :13])) and bool(torch.equal(xb[k, :, 13:], xi[0, :, 13:])) and bool(torch.equal(sb[k], si[0])) and bool(torch.equal(yb[k], yi[0]))
chk("blind_window_channels_donor_household_own_weather_static_target", ok_w, "n_dyn=%d" % db.n_dyn)
chk("blind_window_differs_from_unblind_in_household_channel", not bool(torch.equal(xb[:, :, :4], xn[:, :, :4])))

# ---------------------------------------------------------------- 3. one country
for cc in ("es", "it"):
    dc = sd.Data("validation", "cpu", load_targets=True, country=cc, drop_climate=True)
    keep = np.flatnonzero((base["country"] == cc).to_numpy())
    chk("country_%s_rows_only_that_country" % cc, set(dc.flats["country"]) == {cc} and len(dc.flats) == len(keep), "rows=%d" % len(dc.flats))
    Tfull = np.load(sd.STORE + "targets_validation.npy", mmap_mode="r")
    chk("country_%s_targets_follow_filter" % cc, bool(np.array_equal(dc.T[[0, len(keep) // 2, len(keep) - 1]].numpy(), np.asarray(Tfull[[keep[0], keep[len(keep) // 2], keep[-1]]]))))
    pr = pd.read_parquet(sd.STORE + "pairs_validation.parquet")
    n_expect = int(((cty_a[pr["row_a"].to_numpy()] == cc) & (cty_a[pr["row_b"].to_numpy()] == cc)).sum())
    pa, pb = dc.pa.numpy(), dc.pb.numpy()
    same_pairs = bool((dc.flats["building_id"].to_numpy()[pa] == dc.flats["building_id"].to_numpy()[pb]).all() and (dc.flats["flat"].to_numpy()[pa] == dc.flats["flat"].to_numpy()[pb]).all()
                      and (dc.flats["run_id"].to_numpy()[pa] != dc.flats["run_id"].to_numpy()[pb]).all())
    chk("country_%s_pairs_follow_filter" % cc, len(pa) == n_expect and pa.max() < len(dc.flats) and same_pairs, "pairs=%d expected=%d" % (len(pa), n_expect))
    chk("country_%s_climate_columns_dropped" % cc, not any(nm.startswith("c_") for nm in dc.static_names) and dc.S == len(dc.s_cols), "S=%d s_cols=%d c_cols=%d" % (dc.S, len(dc.s_cols), len(dc.c_cols)))
    dd = sd.Data("development", "cpu", load_targets=False, country=cc, drop_climate=True)
    fdev = pd.read_parquet(sd.STORE + "flats_development.parquet")
    fdev = fdev[fdev["country"] == cc]
    mu = fdev[dd.s_cols].to_numpy(dtype=np.float64).mean(0)
    chk("country_%s_static_mean_from_training_country_only" % cc, np.allclose(mu, np.array(dd.stats["mean"])), "max abs diff %.3e" % np.abs(mu - np.array(dd.stats["mean"])).max())
    fall = pd.read_parquet(sd.STORE + "flats_development.parquet")
    mu_all = fall[dd.s_cols].to_numpy(dtype=np.float64).mean(0)
    chk("country_%s_static_mean_differs_from_both_countries_(planted: wrong basis would differ)" % cc, not np.allclose(mu_all, np.array(dd.stats["mean"])), "max abs diff %.3e" % np.abs(mu_all - np.array(dd.stats["mean"])).max())
    dvv = sd.Data("validation", "cpu", load_targets=False, stats=dd.stats, country=cc, drop_climate=True)
    print("INFO country=%s static columns before %d after %d ; dev rows %d val rows %d ; val clip %s" % (cc, len(dd.s_cols) + len(dd.c_cols), dd.S, len(dd.flats), len(dvv.flats), dvv.clip_info), flush=True)
    del dc, dd, dvv

print("CTRL_CHECK_DONE %s fails=%s" % ("OK" if not fails else "FAILED", fails), flush=True)
sys.exit(0 if not fails else 1)
