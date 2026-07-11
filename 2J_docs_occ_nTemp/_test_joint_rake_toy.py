"""
_test_joint_rake_toy.py — Task B (Improvement 1) synthetic unit test.

Standalone toy-data test for the --joint categorical/hom-conditional rake
added to 05_postlink_rake.py on 2026-07-09. Builds small in-memory toy
DataFrames (NOT the real 21CEN22GSS_aug_Full_Schedules.csv — this test never
touches real data) and asserts the three properties required before any real
run (per step4_improvements_implementation.md, Task B Step 2):

  1. The act30 marginal for a toy cell hits the observed target EXACTLY after
     _rake_categorical_slot.
  2. No record is moved twice within the same slot in one call.
  3. Zero home-activity codes appear in cells with hom30=0 after the move
     (and vice versa: zero non-home codes under hom30=1 when the observed
     subset was pure) -- i.e. home-activities never cross into away-records.

Also includes two bonus smoke tests (not required by the spec, cheap to add):
  4. _run_act30_conditional_rake end-to-end through the LFTAG/stratum wrapper.
  5. _run_cop_rake's NaN-target skip behaviour (colleagues-style missing ref).

Run: py _test_joint_rake_toy.py
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("postlink_rake_toytest", str(_HERE / "05_postlink_rake.py"))
plr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plr)

N_SLOTS = plr.N_SLOTS
ACT_COLS = plr.ACT_COLS
HOM_COLS = plr.HOM_COLS
ACT_CATEGORIES = plr.ACT_CATEGORIES
HOME_ACTS = plr.HOME_ACTS

FAILURES = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {name}" + (f" -- {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


# ═══════════════════════════════════════════════════════════════════════════
print("=" * 72)
print("TEST 1 — _rake_categorical_slot: marginal exact + no double-move")
print("=" * 72)

# Toy cell: 40 synthetic records at one focal slot, currently {1:15, 2:10, 3:15}.
# Observed target for the same cell: {1:5, 2:5, 3:30} -- forces 15 total moves
# (10 surplus from cat1, 5 surplus from cat2, all into cat3's 15-unit deficit).
cur_vals = np.array([1] * 15 + [2] * 10 + [3] * 15, dtype=float)
target_full = {c: 0 for c in ACT_CATEGORIES}
target_full.update({1: 5, 2: 5, 3: 30})
left_vals = np.full(len(cur_vals), np.nan)
right_vals = np.full(len(cur_vals), np.nan)
rng = np.random.default_rng(42)

new_vals, n_moved = plr._rake_categorical_slot(
    cur_vals, target_full, ACT_CATEGORIES, left_vals, right_vals, rng
)

post_counts = {c: int(np.sum(new_vals == c)) for c in ACT_CATEGORIES}
check("marginal hits target exactly for every category",
      all(post_counts[c] == target_full[c] for c in ACT_CATEGORIES),
      f"post={ {c: post_counts[c] for c in [1,2,3]} } target={ {c: target_full[c] for c in [1,2,3]} }")
check("expected move count (15) reached", n_moved == 15, f"n_moved={n_moved}")
check("no double-move: #changed positions == n_moved (a double-move would "
      "inflate n_moved above the #changed-positions count)",
      int(np.sum(cur_vals != new_vals)) == n_moved,
      f"changed={int(np.sum(cur_vals != new_vals))} n_moved={n_moved}")
check("original array not mutated (function returns a copy)",
      np.array_equal(cur_vals, np.array([1] * 15 + [2] * 10 + [3] * 15, dtype=float)))


# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("TEST 2 — _rake_categorical_slot: boundary-preference contention, still no double-move")
print("=" * 72)

# 20 records, deficit in 2 categories at once (cat4 needs +6, cat5 needs +4),
# surplus spread across 3 categories (cat1:-4, cat2:-3, cat3:-3) -- exercises
# the multi-deficit while-loop with overlapping candidate pools.
cur_vals2 = np.array([1] * 6 + [2] * 5 + [3] * 5 + [4] * 2 + [5] * 2, dtype=float)
target2 = {c: 0 for c in ACT_CATEGORIES}
target2.update({1: 2, 2: 2, 3: 2, 4: 8, 5: 6})
# Give some records a "matching" neighbour to bias selection -- shouldn't
# change correctness, only selection order.
left2 = np.where(np.arange(20) % 3 == 0, 4.0, np.nan)
right2 = np.full(20, np.nan)
rng2 = np.random.default_rng(42)

new_vals2, n_moved2 = plr._rake_categorical_slot(
    cur_vals2, target2, ACT_CATEGORIES, left2, right2, rng2
)
post_counts2 = {c: int(np.sum(new_vals2 == c)) for c in ACT_CATEGORIES}
check("marginal hits target exactly (multi-deficit case)",
      all(post_counts2[c] == target2[c] for c in ACT_CATEGORIES),
      f"post={ {c: post_counts2[c] for c in [1,2,3,4,5]} }")
expected_moves2 = 4 + 3 + 3   # total surplus == total deficit
check("expected move count reached", n_moved2 == expected_moves2, f"n_moved={n_moved2}")
check("no double-move under contention",
      int(np.sum(cur_vals2 != new_vals2)) == n_moved2,
      f"changed={int(np.sum(cur_vals2 != new_vals2))} n_moved={n_moved2}")


# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("TEST 3 — _rake_act_group: hom30=0/1 crossing prevention (one toy "
      "DDAY_STRATA×slot×LFTAG cell)")
print("=" * 72)

FOCAL_T = 17          # 0-indexed slot -> column suffix "018"
N_SYN, N_OBS = 40, 50
HOME_CODE, AWAY_CODE, FILLER_CODE = 2, 1, 9   # 2 in HOME_ACTS; 1 and 9 are not

def _blank_frame(n_rows, start_idx=0):
    df = pd.DataFrame(index=range(start_idx, start_idx + n_rows))
    for c in ACT_COLS:
        df[c] = float(FILLER_CODE)
    for c in HOM_COLS:
        df[c] = 0.0
    return df

syn_df = _blank_frame(N_SYN, start_idx=0)
obs_df = _blank_frame(N_OBS, start_idx=100_000)   # non-colliding index range

act_focal = ACT_COLS[FOCAL_T]
hom_focal = HOM_COLS[FOCAL_T]

# Synthetic (pre-rake): half hom=1 / half hom=0 at the focal slot, both still
# holding the filler (away-neutral) code -- these need to move.
syn_df.loc[syn_df.index[:20], hom_focal] = 1.0
syn_df.loc[syn_df.index[20:], hom_focal] = 0.0
syn_df[act_focal] = float(FILLER_CODE)

# Observed target at the focal slot: hom=1 subset is 100% HOME_CODE,
# hom=0 subset is 100% AWAY_CODE -- a clean, pure target.
obs_df.loc[obs_df.index[:25], hom_focal] = 1.0
obs_df.loc[obs_df.index[:25], act_focal] = float(HOME_CODE)
obs_df.loc[obs_df.index[25:], hom_focal] = 0.0
obs_df.loc[obs_df.index[25:], act_focal] = float(AWAY_CODE)

combined = pd.concat([syn_df, obs_df], axis=0)
syn_idx = syn_df.index.tolist()
obs_idx = obs_df.index.tolist()

rng3 = np.random.default_rng(42)
n_moved3 = plr._rake_act_group(combined, syn_idx, obs_idx, ACT_COLS, HOM_COLS, rng3)

result = combined.loc[syn_idx]
h1 = result[result[hom_focal] == 1.0]
h0 = result[result[hom_focal] == 0.0]

check("hom30=1 subset (n=20) -> 100% moved to the pure observed home code",
      len(h1) == 20 and (h1[act_focal] == float(HOME_CODE)).all(),
      f"n={len(h1)} unique_acts={h1[act_focal].unique().tolist()}")
check("hom30=0 subset (n=20) -> 100% moved to the pure observed away code",
      len(h0) == 20 and (h0[act_focal] == float(AWAY_CODE)).all(),
      f"n={len(h0)} unique_acts={h0[act_focal].unique().tolist()}")
check("zero home-activity codes under hom30=0 after the move",
      int(h0[act_focal].isin(list(HOME_ACTS)).sum()) == 0)
check("zero non-home codes under hom30=1 after the move (vice-versa, "
      "since the observed hom=1 subset was pure-home)",
      int((~h1[act_focal].isin(list(HOME_ACTS))).sum()) == 0)
check("act30 stays in [1,14] after the move",
      float(result[ACT_COLS].values.min()) >= plr.ACT_MIN and
      float(result[ACT_COLS].values.max()) <= plr.ACT_MAX)
check("hom30 itself untouched by the act30 rake (read-only invariant)",
      (combined.loc[syn_idx, HOM_COLS].values == syn_df[HOM_COLS].values).all())


# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("TEST 4 (bonus) — _run_act30_conditional_rake end-to-end "
      "(DDAY_STRATA×LFTAG wrapper, single non-sparse cell)")
print("=" * 72)

syn_df4 = _blank_frame(N_SYN, start_idx=0)
obs_df4 = _blank_frame(N_OBS, start_idx=100_000)
syn_df4.loc[syn_df4.index[:20], hom_focal] = 1.0
syn_df4.loc[syn_df4.index[20:], hom_focal] = 0.0
syn_df4[act_focal] = float(FILLER_CODE)
obs_df4.loc[obs_df4.index[:25], hom_focal] = 1.0
obs_df4.loc[obs_df4.index[:25], act_focal] = float(HOME_CODE)
obs_df4.loc[obs_df4.index[25:], hom_focal] = 0.0
obs_df4.loc[obs_df4.index[25:], act_focal] = float(AWAY_CODE)
syn_df4["DDAY_STRATA"] = 1
obs_df4["DDAY_STRATA"] = 1
syn_df4["LFTAG"] = 1
obs_df4["LFTAG"] = 1   # 50 obs rows >= MIN_OBS_FOR_LFTAG(30) -> "ok" branch, not sparsity-pooled
syn_df4["IS_SYNTHETIC"] = 1
obs_df4["IS_SYNTHETIC"] = 0

combined4 = pd.concat([syn_df4, obs_df4], axis=0)
obs_mask4 = combined4["IS_SYNTHETIC"] == 0
syn_mask4 = combined4["IS_SYNTHETIC"] == 1
rng4 = np.random.default_rng(42)

total_moves4, diag4 = plr._run_act30_conditional_rake(
    combined4, ACT_COLS, HOM_COLS, obs_mask4, syn_mask4, rng4
)
result4 = combined4.loc[combined4.index.isin(syn_df4.index)]
h1_4 = result4[result4[hom_focal] == 1.0]
h0_4 = result4[result4[hom_focal] == 0.0]
check("end-to-end wrapper: hom=1 subset converges to pure home code",
      (h1_4[act_focal] == float(HOME_CODE)).all())
check("end-to-end wrapper: hom=0 subset converges to pure away code",
      (h0_4[act_focal] == float(AWAY_CODE)).all())
check("end-to-end wrapper: LFTAG not sparsity-dropped (50 obs >= 30)",
      len(diag4["lftag_dropped"]) == 0, f"lftag_dropped={diag4['lftag_dropped']}")


# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("TEST 5 (bonus) — _run_cop_rake: NaN-target channel/cell is skipped, not raked")
print("=" * 72)

N_SYN5, N_OBS5 = 20, 20
cols_spouse = [f"Spouse30_{t:03d}" for t in range(1, N_SLOTS + 1)]
cols_colleagues = [f"colleagues30_{t:03d}" for t in range(1, N_SLOTS + 1)]

syn5 = pd.DataFrame(index=range(N_SYN5))
obs5 = pd.DataFrame(index=range(200, 200 + N_OBS5))
for df5 in (syn5, obs5):
    for c in cols_spouse + cols_colleagues:
        df5[c] = 0.3   # soft prob for syn; will be treated as an obs 0/1-ish value too
obs5[cols_spouse] = 1.0                 # observed Spouse: 100% present -> real target
obs5[cols_colleagues] = np.nan          # observed colleagues: all-NaN, mimics 2005/2010 (no reference)
syn5["DDAY_STRATA"] = 1
obs5["DDAY_STRATA"] = 1
syn5["IS_SYNTHETIC"] = 1
obs5["IS_SYNTHETIC"] = 0

combined5 = pd.concat([syn5, obs5], axis=0)
obs_mask5 = combined5["IS_SYNTHETIC"] == 0
syn_mask5 = combined5["IS_SYNTHETIC"] == 1
rng5 = np.random.default_rng(42)

total_flips5, cop_diag5 = plr._run_cop_rake(combined5, obs_mask5, syn_mask5, rng5)
syn_result5 = combined5.loc[combined5.index.isin(syn5.index)]
check("Spouse (real observed target) raked to 100% present",
      (syn_result5[cols_spouse].values == 1.0).all())
check("colleagues (NaN observed target) left untouched (binarized-at-0.5 "
      "baseline, i.e. 0.0, since soft prob 0.3 < 0.5 -- NOT raked toward any target)",
      (syn_result5[cols_colleagues].values == 0.0).all())
check("colleagues channel logged with 0 flips (all slots skipped for NaN target)",
      cop_diag5["channels"].get("colleagues", None) == 0,
      f"channels={cop_diag5['channels']}")


# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
if FAILURES:
    print(f"RESULT: FAIL -- {len(FAILURES)} check(s) failed: {FAILURES}")
    print("=" * 72)
    sys.exit(1)
else:
    print("RESULT: ALL CHECKS PASSED")
    print("=" * 72)
    sys.exit(0)
