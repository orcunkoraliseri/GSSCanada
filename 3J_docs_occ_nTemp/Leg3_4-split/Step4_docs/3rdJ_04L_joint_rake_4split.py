# -*- coding: utf-8 -*-
"""
3rdJ_04L_joint_rake_4split.py — Step 4L (Leg-3, four-channel split): Joint
AT_HOME + AT_WORK + AT_RETAIL Post-Hoc Raking (Delta H of
3rdJ_04_augmentationGSS_4split.md, FROZEN).

Ports 3rdJ_04L_joint_rake_2split.py (Leg-2) and generalizes the greedy joint
rake from TWO channels {home, work} to THREE channels {home, work, retail}.
Leg-2 file is READ-ONLY / template only — not imported, not modified.
3rdJ_04B_model_4split.py is ALSO READ-ONLY — not modified here either.

Method (mirrors the Leg-2 04L method, extended):
  1. Load tensors + winning seed checkpoint; run
     generate(apply_safety=False, return_hw_probs=True, return_retail_probs=True)
     to get per-slot raw sigmoid probs for the home, work AND retail heads
     (8-tuple contract per 3rdJ_04B_model_4split.py's generate() docstring).
  2. Retail probs are put through the SAME −ln(pos_weight) calibration shift
     04E applies at inference (Delta C/F#3: p_cal = p / (p + k*(1-p)), k =
     retail_pos_weight from step4_feature_config.json, default 49.0) BEFORE
     raking — dr_L3-08: "rake after logit shift". Home/work probs are used
     raw (unchanged from the Leg-2 template — those heads carry no comparable
     class-imbalance re-weighting).
  3. From observed rows (IS_SYNTHETIC==0) in the source augmented_diaries.csv,
     compute per-(cy x stratum x slot) AT_HOME / AT_WORK / AT_RETAIL rates
     UNWEIGHTED (np.nanmean over binary 0/1 values) — the rake targets.
  4. For each (cy x stratum x slot) cell, assign the N_syn person-slots to
     {home=1, work=1, retail=1, neither} via greedy global-confidence joint
     raking: sort ALL (person, channel) triples by descending sigmoid
     probability (3N action list, not 2N); greedily assign each person to
     their highest-confidence eligible channel until that channel's quota is
     met. Guarantees: sum(home)==n_home, sum(work)==n_work,
     sum(retail)==n_retail, and no person has more than one of
     {home=1, work=1, retail=1} (exclusivity across ALL THREE channels).
  5. Write raked augmented_diaries.csv to a NEW sweep/<BASE>_raked3/ dir
     (never overwrites the source dir). Activity (act30_*) and co-presence
     columns are carried forward untouched — the source's G3 co-presence
     threshold block (retail-unaffected) is already applied there.

[Leg-3 NEW, non-obvious 2->3 generalization] --floating_aware priority tiers:
  Retail has NO floating-state subtlety analogous to TELEWORK (there is no
  "physical channel ambiguity" for shopping the way there is for a
  work-activity slot being either the home office or the physical
  workplace) — so retail is NOT given a forced-priority tier. It competes
  in the SAME global greedy pass as everyone else, at raw calibrated
  confidence (tier +0.0), and can only claim a person the forced home/work
  tiers (+1.0/+2.0) have not already claimed. This can rarely let a
  work-activity person who lost BOTH the home and work quota race (the
  irreducible floating case) pick up retail instead of ending up fully
  unassigned; this is measured (not silently dumped) as
  "work_act_retail_conflicts" in the provenance, mirroring the template's
  existing "measure, don't dump" residual-floating philosophy.

Usage (cluster):
    sbatch 3rdJ_s4_4split_rake.sh

Usage (local):
    python 3rdJ_04L_joint_rake_4split.py
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import platform
import shutil
import sys

import numpy as np
import pandas as pd
import torch

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
model_mod = importlib.import_module("3rdJ_04B_model_4split")
JSeriesHybrid4Split = model_mod.JSeriesHybrid4Split

# ── Platform detection (mirrors 04A/04E) ──────────────────────────────────────
_SYSTEM = platform.system()
if _SYSTEM == "Windows":
    _LEG3_BASE = os.path.normpath(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split"
    )
elif os.path.isdir("/speed-scratch/o_iseri"):
    _LEG3_BASE = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split"
else:
    _LEG3_BASE = os.path.join(
        os.path.expanduser("~"),
        "GSSCanada", "GSSCanada-main", "3J_docs_occ_nTemp", "Leg3_4-split",
    )

_STEP4_SHARED = os.path.join(_LEG3_BASE, "Step4_docs", "outputs_step4")
# Default source: seed 3's winning checkpoint dir (per-seed isolation, see
# 3rdJ_s4_4split_joint.sh's SEED_OUT convention). Override with --r5_dir for
# any other seed_N / sweep variant.
_SEED3_DIR = os.path.join(_STEP4_SHARED, "seed_3")

N_SLOTS    = 48
TEMPERATURE = 0.7   # matches 04E's Delta F#1 AR-activity temperature default
BATCH_SIZE  = 256
RETAIL_POS_WEIGHT_DEFAULT = 49.0   # matches 04E's --retail_pos_weight default
CYCLES  = [2005, 2010, 2015, 2022]
STRATA  = [1, 2, 3]
HOM_COLS = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
WRK_COLS = [f"wrk30_{s:03d}" for s in range(1, N_SLOTS + 1)]
# CONTRACT (per 3rdJ_04_augmentationGSS_4split.md): lowercase ret30_*,
# distinct from the Step-3 tiler's RETL30_* namespace.
RET_COLS = [f"ret30_{s:03d}" for s in range(1, N_SLOTS + 1)]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir",   default=None,
                   help="Dir with step4_{train,val,test}.pt + step4_feature_config.json "
                        "(defaults to the shared outputs_step4/)")
    p.add_argument("--r5_dir",     default=None,
                   help="Variant dir containing checkpoints/ + augmented_diaries.csv "
                        "(default: outputs_step4/seed_3/, the winning seed). Named "
                        "--r5_dir to keep the Leg-2 CLI contract; 'R5' has no special "
                        "meaning in Leg-3.")
    p.add_argument("--output_dir", default=None,
                   help="Output dir for the raked augmented_diaries.csv (default: "
                        "outputs_step4/sweep/<basename(r5_dir)>_raked3/). Never the "
                        "same dir as --r5_dir — the source is never overwritten.")
    p.add_argument("--checkpoint", default=None,
                   help="Override model checkpoint path. Default: <r5_dir>/checkpoints/"
                        "best_model.pt. Use this when --r5_dir holds a re-inferred "
                        "augmented_diaries.csv but the checkpoint lives elsewhere.")
    p.add_argument("--temperature", type=float, default=TEMPERATURE,
                   help="Generation temperature for the rake's model.generate "
                        "(should match the 04E temperature used to make the diaries; "
                        f"default {TEMPERATURE}).")
    p.add_argument("--telework_aware", action="store_true", default=False,
                   help="[OPT-IN] Enforce work-slot coherence before raking: "
                        "FLOATING (act==1 & wrk30=0 & hom30=0 & ret30=0) is forbidden. "
                        "Telework (TELEWORK==1) slots -> hom30=1, wrk30=0, ret30=0; "
                        "non-telework work slots -> wrk30=1, hom30=0, ret30=0. "
                        "Default OFF -> byte-identical to classic rake behaviour.")
    p.add_argument("--floating_aware", action="store_true", default=False,
                   help="[OPT-IN, root-cause fix] Floating-aware joint rake. Instead "
                        "of the --telework_aware ADDITIVE post-rake fixup (which dumps "
                        "every floating work-slot into hom30=1 ON TOP of the satisfied "
                        "home quota -> AT_HOME inflation), this routes work-activity "
                        "slots into the EXISTING per-slot home/work quota by PRIORITY: "
                        "each work-act slot person is given first claim on their "
                        "physical channel (TELEWORK==1 -> home, else -> work), then "
                        "non-work-act persons fill whatever quota remains. Retail gets "
                        "NO forced tier (no floating-state subtlety for retail; see "
                        "module docstring) — it competes at raw confidence only. "
                        "Marginals (n_home/n_work/n_retail) stay EXACT; floating "
                        "collapses to only the irreducible activity-vs-occupancy excess "
                        "(reported per cell in provenance, never dumped to home). "
                        "Mutually exclusive with --telework_aware; do not combine. "
                        "Default OFF -> byte-identical to classic rake behaviour.")
    return p.parse_args()


# ── Telework-aware coherence enforcement ─────────────────────────────────────

def _apply_telework_coherence(aug: pd.DataFrame) -> pd.DataFrame:
    """
    Enforce work-slot occupancy coherence on SYNTHETIC rows (block-wise).
    Ported from Leg-2's 04L, extended to also zero AT_RETAIL on the same
    work-activity episodes (a work episode can never simultaneously be a
    retail episode — retail's exclusivity with home/work is unconditional,
    per Delta G's OD-1 gated OR-rule; there is no telework-style dual
    interpretation for retail to preserve).

    BLOCK-WISE RESOLUTION: contiguous runs of work-activity slots
    (act30 == WORK_CAT) within a respondent-day get ONE coherent label:
      - TELEWORK==1  -> hom30=1, wrk30=0, ret30=0  for every slot in the run
      - TELEWORK==0  -> wrk30=1, hom30=0, ret30=0  for every slot in the run

    Observed rows (IS_SYNTHETIC==0) are never touched. TELEWORK is a scalar
    demographic column; NaN is treated as 0.

    NOTE: This function only SEEDS the state (home vs work vs retail=0) for
    work-act slots. The downstream rake is free to adjust ALL slots
    (including work-act slots) to hit the per-stratum marginals — a
    post-rake fixup (_post_rake_floating_fixup, telework_aware mode only)
    resolves any resulting incoherence.
    """
    ACT_WORK = 1
    syn_mask = aug["IS_SYNTHETIC"] == 1
    if not syn_mask.any():
        return aug

    act_cols = [f"act30_{j:03d}" for j in range(1, N_SLOTS + 1)
                if f"act30_{j:03d}" in aug.columns]
    hom_cols_48 = [f"hom30_{j:03d}" for j in range(1, N_SLOTS + 1)
                   if f"hom30_{j:03d}" in aug.columns]
    wrk_cols_48 = [f"wrk30_{j:03d}" for j in range(1, N_SLOTS + 1)
                   if f"wrk30_{j:03d}" in aug.columns]
    ret_cols_48 = [f"ret30_{j:03d}" for j in range(1, N_SLOTS + 1)
                   if f"ret30_{j:03d}" in aug.columns]
    n_slots_present = len(act_cols)

    if "TELEWORK" in aug.columns:
        tele_flag = (aug["TELEWORK"].fillna(0) == 1).values  # (N,) bool
    else:
        tele_flag = np.zeros(len(aug), dtype=bool)

    syn_idx = np.where(syn_mask.values)[0]

    act_mat = aug[act_cols].to_numpy(dtype=float)
    hom_mat = aug[hom_cols_48].to_numpy(dtype=float)
    wrk_mat = aug[wrk_cols_48].to_numpy(dtype=float)
    ret_mat = aug[ret_cols_48].to_numpy(dtype=float)

    for i in syn_idx:
        act_row = act_mat[i]
        is_tele = tele_flag[i]

        j = 0
        while j < n_slots_present:
            if act_row[j] == ACT_WORK:
                ep_start = j
                while j < n_slots_present and act_row[j] == ACT_WORK:
                    j += 1
                ep_end = j  # exclusive

                if is_tele:
                    hom_mat[i, ep_start:ep_end] = 1.0
                    wrk_mat[i, ep_start:ep_end] = 0.0
                else:
                    wrk_mat[i, ep_start:ep_end] = 1.0
                    hom_mat[i, ep_start:ep_end] = 0.0
                ret_mat[i, ep_start:ep_end] = 0.0   # [Leg-3 NEW] never retail during work
            else:
                j += 1

    aug[hom_cols_48] = hom_mat
    aug[wrk_cols_48] = wrk_mat
    aug[ret_cols_48] = ret_mat

    return aug


def _post_rake_floating_fixup(
    new_hom_mat: np.ndarray,
    new_wrk_mat: np.ndarray,
    new_ret_mat: np.ndarray,
    act_mat: np.ndarray,
) -> tuple:
    """
    Post-rake fixup (telework_aware mode only), extended to 3 channels.

    After the joint rake writes new_hom_mat / new_wrk_mat / new_ret_mat for a
    (cy x s) cell, some work-activity slots may have ended up with
    wrk30=0 AND hom30=0 AND ret30=0 (classic FLOATING) because the rake
    treated work-act slots as free (not locked). This forces hom30=1 on
    those slots (the safer physical fallback, as in Leg-2).

    [Leg-3 NEW] A work-activity slot can also end up with ret30=1 (the rake
    has no knowledge of act30 when assigning the retail quota) — a person
    cannot be shopping during a work episode. This is NOT classic floating
    (a channel WAS assigned) but is an equally real activity-vs-occupancy
    incoherence, so it gets the SAME home-fallback treatment: ret30 -> 0,
    hom30 -> 1. Both branches are counted and returned so the caller can
    report them (this fixup is already documented as ADDITIVE / marginal-
    inflating in telework_aware mode — see --floating_aware's docstring for
    the exact-marginal alternative, which measures instead of fixing).

    Inputs (n_syn, 48):
        new_hom_mat, new_wrk_mat, new_ret_mat — rake output (float32, 0/1)
        act_mat                               — pre-rake activity matrix
                                                  (float, ==1 for work)
    Returns:
        (new_hom_mat, new_wrk_mat, new_ret_mat, n_floating_fixed, n_work_retail_fixed)
    """
    ACT_WORK = 1.0
    floating = ((act_mat == ACT_WORK) & (new_wrk_mat == 0)
                & (new_hom_mat == 0) & (new_ret_mat == 0))
    n_floating_fixed = int(floating.sum())
    new_hom_mat[floating] = 1.0   # FLOATING -> home fallback

    work_retail_conflict = (act_mat == ACT_WORK) & (new_ret_mat == 1)
    n_work_retail_fixed = int(work_retail_conflict.sum())
    new_hom_mat[work_retail_conflict] = 1.0    # home fallback (mutually exclusive
    new_ret_mat[work_retail_conflict] = 0.0    # with new_wrk_mat by rake construction)

    return new_hom_mat, new_wrk_mat, new_ret_mat, n_floating_fixed, n_work_retail_fixed


def load_all_data(data_dir: str):
    """Concatenate train/val/test tensor dicts (mirrors 04E)."""
    splits = {}
    for split in ["train", "val", "test"]:
        splits[split] = torch.load(
            os.path.join(data_dir, f"step4_{split}.pt"), map_location="cpu", weights_only=False
        )
    keys = list(splits["train"].keys())
    return {k: torch.cat([splits[s][k] for s in ["train", "val", "test"]], dim=0) for k in keys}


# ── Delta C/F#3: retail calibration (-ln k logit shift, prob-space identity) ──
# Copied verbatim from 3rdJ_04E_inference_4split.py (that script is read-only
# and not imported for non-model helpers, per its own module docstring
# convention) so this file stays self-contained.

def calibrate_retail_prob(p: np.ndarray, pos_weight: float) -> np.ndarray:
    """sigmoid(logit(p) - ln k) == p / (p + k*(1-p)) — avoids re-exposing raw
    logits through generate(). Applied ONLY here (post-hoc rake) and in 04E
    (inference); never in 04D (training)."""
    k = float(pos_weight)
    return p / (p + k * (1.0 - p) + 1e-12)


def collect_channel_probs(model, data, device, retail_pos_weight: float):
    """
    Run generate(apply_safety=False, return_hw_probs=True,
    return_retail_probs=True) over all respondents x their 2 synthetic
    strata (8-tuple contract, see 3rdJ_04B_model_4split.py's generate()
    docstring). Retail probs are calibrated (-ln k shift) before storage —
    Delta H: "rake after logit shift" (dr_L3-08).

    Returns dict keyed by (occ_id, cycle_year, s_tgt) ->
        {"p_home": np.ndarray(48,), "p_work": np.ndarray(48,),
         "p_retail": np.ndarray(48,)}
    p_home/p_work are the raw sigmoid outputs (apply_safety=False, unchanged
    from the Leg-2 template); p_retail is the CALIBRATED sigmoid.
    """
    model.eval()
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    n = len(data["act_seq"])
    obs_strata_all = data["obs_strata"].numpy()
    cycle_year_all = data["cycle_year"].numpy()
    occ_ids_all    = data["occ_ids"].numpy()

    ch_probs = {}
    for start in range(0, n, BATCH_SIZE):
        end = min(start + BATCH_SIZE, n)
        chunk = list(range(start, end))

        syn_idx, syn_strata = [], []
        for i in chunk:
            s_obs = int(obs_strata_all[i])
            for s_tgt in [1, 2, 3]:
                if s_tgt != s_obs:
                    syn_idx.append(i)
                    syn_strata.append(s_tgt)

        if syn_idx:
            act_t  = data["act_seq"][syn_idx].to(device)
            aux_t  = data["aux_seq"][syn_idx].to(device)
            cond_t = data["cond_vec"][syn_idx].to(device)
            cidx_t = data["cycle_idx"][syn_idx].to(device)
            strat  = torch.tensor(syn_strata, dtype=torch.long, device=device)

            with torch.no_grad():
                (_, _, _, _, _,
                 g_home_probs, g_work_probs, g_retail_probs) = model.generate(
                    act_t, aux_t, cond_t, cidx_t, strat,
                    temperature=TEMPERATURE,
                    apply_safety=False,
                    return_hw_probs=True,
                    return_retail_probs=True,
                )
            g_hp = g_home_probs.cpu().numpy()     # (B_syn, 48)
            g_wp = g_work_probs.cpu().numpy()     # (B_syn, 48)
            g_rp_raw = g_retail_probs.cpu().numpy()  # (B_syn, 48) — RAW, pre-calibration
            g_rp = calibrate_retail_prob(g_rp_raw, retail_pos_weight)

            for k, (i, s_tgt) in enumerate(zip(syn_idx, syn_strata)):
                key = (int(occ_ids_all[i]), int(cycle_year_all[i]), int(s_tgt))
                ch_probs[key] = {"p_home": g_hp[k], "p_work": g_wp[k], "p_retail": g_rp[k]}

        print(f"  Collected {end}/{n} respondents ({100.0 * end / n:.1f}%)", flush=True)

    return ch_probs


def _joint_rake_slot(p_home, p_work, p_retail, n_home, n_work, n_retail,
                     force_home=None, force_work=None):
    """
    Greedy global-confidence joint assignment for one (cell x slot),
    generalized from the Leg-2 template's 2-channel {home, work} version to
    3 channels {home, work, retail}.

    Inputs:
        p_home, p_work, p_retail — (N,) float32 probabilities per person
                                    (p_retail already CALIBRATED)
        n_home, n_work, n_retail — integer target counts to assign (1s)
        force_home  — (N,) bool, optional. Persons whose physical channel at
                      this slot is HOME (work-activity AND telework). Given
                      top priority for the home quota, then second priority
                      for the work quota. [--floating_aware]
        force_work  — (N,) bool, optional. Persons whose physical channel is
                      WORK (work-activity AND non-telework). Top priority for
                      the work quota, second for home. [--floating_aware]
                      NOTE: there is intentionally NO force_retail parameter
                      — see module docstring ("no floating-state subtlety
                      for retail"). Retail always competes at tier +0.0.

    Outputs:
        new_home, new_work, new_retail — (N,) float32 binary arrays

    Guarantees:
        sum(new_home) == n_home
        sum(new_work) == n_work
        sum(new_retail) == n_retail
        no person has more than one of {new_home==1, new_work==1, new_retail==1}
        (mutual exclusivity across ALL THREE channels — the `assigned` state
        machine below tracks a single owner per person regardless of which
        of the 3N actions reaches them first)

    Floating-aware behaviour (force_* given): the assignment ORDER is tiered
    so work-activity persons claim the home/work quota BEFORE non-work-act
    persons, minimising leftover FLOATING (work-act person assigned neither)
    WITHOUT changing the quota counts — so the per-slot marginals stay exact.
    Residual floating can only occur when n_home + n_work < (#work-act
    persons), i.e. the irreducible activity-vs-occupancy excess; that is
    reported by the caller, never dumped to home. Because forced home/work
    actions are boosted to >=1.0 while retail's raw probability is <=1.0,
    a forced person's home/work action is always processed before their own
    retail action UNLESS both the home and work quotas are already exhausted
    when the sort reaches them — in that (rare, irreducible) case they may
    fall through to retail if that quota still has room. The caller measures
    this as "work_act_retail_conflicts" (see module docstring).
    """
    N = len(p_home)
    n_home   = max(0, min(int(n_home),   N))
    n_work   = max(0, min(int(n_work),   N))
    n_retail = max(0, min(int(n_retail), N))

    # Feasibility guard: n_home + n_work + n_retail must not exceed N persons.
    total_n = n_home + n_work + n_retail
    if total_n > N:
        scale    = N / total_n
        n_home   = int(round(n_home * scale))
        n_work   = int(round(n_work * scale))
        n_retail = max(0, N - n_home - n_work)

    new_home   = np.zeros(N, dtype=np.float32)
    new_work   = np.zeros(N, dtype=np.float32)
    new_retail = np.zeros(N, dtype=np.float32)
    if n_home == 0 and n_work == 0 and n_retail == 0:
        return new_home, new_work, new_retail

    # Build global sorted action list: 3N entries, one per (person, channel).
    actions_prob    = np.empty(3 * N, dtype=np.float32)
    actions_channel = np.empty(3 * N, dtype=np.uint8)
    actions_idx     = np.empty(3 * N, dtype=np.int32)
    actions_prob[:N]        = p_home.astype(np.float32)
    actions_channel[:N]     = 0           # 0 = home
    actions_idx[:N]         = np.arange(N, dtype=np.int32)
    actions_prob[N:2 * N]   = p_work.astype(np.float32)
    actions_channel[N:2*N]  = 1           # 1 = work
    actions_idx[N:2 * N]    = np.arange(N, dtype=np.int32)
    actions_prob[2*N:3*N]   = p_retail.astype(np.float32)
    actions_channel[2*N:3*N] = 2          # 2 = retail
    actions_idx[2*N:3*N]    = np.arange(N, dtype=np.int32)

    # Floating-aware priority tiers (home/work only — retail is NEVER forced;
    # see docstring). +2.0 / +1.0 offsets cleanly separate tiers since sigmoid
    # probs are in [0,1] and retail's own tier stays at +0.0.
    if force_home is not None or force_work is not None:
        sort_key = actions_prob.copy()
        if force_home is not None:
            fh = np.asarray(force_home, dtype=bool)
            sort_key[:N][fh] += 2.0        # home channel  (preferred)
            sort_key[N:2*N][fh] += 1.0     # work channel  (fallback)
        if force_work is not None:
            fw = np.asarray(force_work, dtype=bool)
            sort_key[N:2*N][fw] += 2.0     # work channel  (preferred)
            sort_key[:N][fw] += 1.0        # home channel  (fallback)
        order = np.argsort(-sort_key, kind="stable")
    else:
        order = np.argsort(-actions_prob, kind="stable")

    assigned = np.zeros(N, dtype=np.uint8)   # 0=unassigned, 1=home, 2=work, 3=retail
    rem_home, rem_work, rem_retail = n_home, n_work, n_retail

    for k in order:
        if rem_home == 0 and rem_work == 0 and rem_retail == 0:
            break
        ch = int(actions_channel[k])
        i  = int(actions_idx[k])
        if assigned[i] != 0:
            continue
        if ch == 0 and rem_home > 0:
            new_home[i] = 1.0
            assigned[i] = 1
            rem_home   -= 1
        elif ch == 1 and rem_work > 0:
            new_work[i] = 1.0
            assigned[i] = 2
            rem_work   -= 1
        elif ch == 2 and rem_retail > 0:
            new_retail[i] = 1.0
            assigned[i]   = 3
            rem_retail   -= 1

    return new_home, new_work, new_retail


def main():
    global TEMPERATURE
    args = parse_args()
    TEMPERATURE = args.temperature   # rake's generate() reads the module global at call time
    data_dir   = args.data_dir   or _STEP4_SHARED
    r5_dir     = args.r5_dir     or _SEED3_DIR
    if args.output_dir:
        output_dir = args.output_dir
    else:
        base = os.path.basename(os.path.normpath(r5_dir))
        output_dir = os.path.join(_STEP4_SHARED, "sweep", f"{base}_raked3")
    ckpt_path  = args.checkpoint or os.path.join(r5_dir, "checkpoints", "best_model.pt")
    aug_src    = os.path.join(r5_dir, "augmented_diaries.csv")
    raked_path = os.path.join(output_dir, "augmented_diaries.csv")
    prov_path  = os.path.join(output_dir, "rake3ch_provenance.json")
    telework_aware = args.telework_aware
    floating_aware = args.floating_aware
    if floating_aware and telework_aware:
        raise SystemExit("[ERROR] --floating_aware and --telework_aware are mutually "
                         "exclusive (they are two different floating treatments). "
                         "Pass only one.")

    # Never overwrite the source dir (explicit guard; the <BASE>_raked3
    # default naming convention already avoids this, but --output_dir is
    # user-settable so we check).
    if os.path.abspath(output_dir) == os.path.abspath(r5_dir):
        raise SystemExit(
            f"[ERROR] --output_dir must not equal --r5_dir ({r5_dir}) — "
            f"the rake never overwrites its source augmented_diaries.csv."
        )

    print("=" * 64)
    print("3rdJ Step 4L (Leg-3, 4-split) — Joint AT_HOME + AT_WORK + AT_RETAIL Raking")
    print("=" * 64)
    print(f"  data_dir:   {data_dir}")
    print(f"  r5_dir:     {r5_dir}")
    print(f"  output_dir: {output_dir}")
    print(f"  checkpoint: {ckpt_path}")
    print(f"  aug source: {aug_src}")
    print(f"  temperature: {TEMPERATURE}")
    print(f"  telework_aware: {telework_aware}")
    print(f"  floating_aware: {floating_aware}")

    os.makedirs(output_dir, exist_ok=True)

    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"  device:     {device}")

    # ── Step 1: Load tensors + retail calibration weight ─────────────────────
    print("\n[1/5] Loading tensor datasets...")
    data = load_all_data(data_dir)
    n = len(data["act_seq"])
    print(f"  Total respondents: {n}")

    feat_cfg_path = os.path.join(data_dir, "step4_feature_config.json")
    retail_pos_weight = RETAIL_POS_WEIGHT_DEFAULT
    if os.path.isfile(feat_cfg_path):
        with open(feat_cfg_path, encoding="utf-8") as f:
            feat_cfg = json.load(f)
        retail_pos_weight = float(feat_cfg.get("retail_pos_weight", RETAIL_POS_WEIGHT_DEFAULT))
    print(f"  retail_pos_weight (calibration k): {retail_pos_weight}")

    # ── Step 2: Load model checkpoint ────────────────────────────────────────
    print("\n[2/5] Loading model checkpoint...")
    if not os.path.isfile(ckpt_path):
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")
    ckpt  = torch.load(ckpt_path, map_location=device, weights_only=False)
    model = JSeriesHybrid4Split(ckpt["model_config"]).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"  Loaded epoch {ckpt.get('epoch','?')}  val_JS={ckpt.get('val_js','?')}  "
          f"work_gap={ckpt.get('work_gap','?')}  retail_gap={ckpt.get('retail_gap','?')}")

    # ── Step 3: Collect raw/calibrated sigmoid probs ─────────────────────────
    print("\n[3/5] Running generate(return_hw_probs=True, return_retail_probs=True)...")
    ch_probs = collect_channel_probs(model, data, device, retail_pos_weight)
    print(f"  Collected {len(ch_probs):,} (occ_id, cy, s_tgt) entries")

    # ── Step 4: Load source aug CSV and apply per-(cy x s x slot) joint rake ─
    print("\n[4/5] Loading source augmented_diaries.csv and applying joint rake...")
    if not os.path.isfile(aug_src):
        raise FileNotFoundError(f"augmented_diaries.csv not found: {aug_src}")
    aug = pd.read_csv(aug_src, low_memory=False)
    print(f"  Loaded: {aug.shape}  "
          f"(IS_SYN=0: {(aug['IS_SYNTHETIC']==0).sum():,}, "
          f"IS_SYN=1: {(aug['IS_SYNTHETIC']==1).sum():,})")

    for col in (HOM_COLS[:1] + WRK_COLS[:1] + RET_COLS[:1]
                + ["occID", "CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC"]):
        if col not in aug.columns:
            raise ValueError(f"Missing required column in aug CSV: {col}")

    # ── Telework-aware coherence pass (OPT-IN: --telework_aware) ─────────────
    if telework_aware:
        print("\n[4a/5] Applying telework-aware coherence enforcement...")
        aug = _apply_telework_coherence(aug)
        floating_after = 0
        work_slots_after = 0
        for j in range(1, N_SLOTS + 1):
            ss = f"{j:03d}"
            syn_m = (aug["IS_SYNTHETIC"] == 1).values
            act_v = aug[f"act30_{ss}"].values
            hom_v = aug[f"hom30_{ss}"].values
            wrk_v = aug[f"wrk30_{ss}"].values
            ret_v = aug[f"ret30_{ss}"].values
            work_mask = syn_m & (act_v == 1)
            work_slots_after += int(work_mask.sum())
            floating_after += int((work_mask & (wrk_v == 0) & (hom_v == 0) & (ret_v == 0)).sum())
        print(f"  Post-coherence FLOATING: {floating_after}/{work_slots_after} "
              f"work-slots ({100*floating_after/max(work_slots_after,1):.2f}%) — expect 0")
        if floating_after > 0:
            print(f"  WARNING: {floating_after} FLOATING slots remain after coherence pass "
                  f"(slots not matching act30_* schema?)")
    else:
        print("\n  [telework_aware=OFF — coherence pass skipped; classic rake unchanged]")

    provenance   = {}
    total_cells  = len(CYCLES) * len(STRATA)
    cell_count   = 0

    for cy in CYCLES:
        for s in STRATA:
            cell_count += 1
            obs_mask = ((aug["CYCLE_YEAR"] == cy) & (aug["DDAY_STRATA"] == s)
                        & (aug["IS_SYNTHETIC"] == 0))
            syn_mask = ((aug["CYCLE_YEAR"] == cy) & (aug["DDAY_STRATA"] == s)
                        & (aug["IS_SYNTHETIC"] == 1))
            osub = aug[obs_mask]
            ssub = aug[syn_mask]
            n_syn = len(ssub)
            n_obs = len(osub)

            if n_syn == 0:
                print(f"  [{cell_count}/{total_cells}] cy={cy} s={s}: no synthetic rows — skip")
                continue

            print(f"  [{cell_count}/{total_cells}] cy={cy} s={s}: {n_obs} obs, {n_syn} syn",
                  flush=True)

            ssub_idx = ssub.index
            ssub_occ = ssub["occID"].to_numpy(dtype=int)

            # Build (n_syn, 48) probability matrices
            p_home_mat   = np.zeros((n_syn, N_SLOTS), dtype=np.float32)
            p_work_mat   = np.zeros((n_syn, N_SLOTS), dtype=np.float32)
            p_retail_mat = np.zeros((n_syn, N_SLOTS), dtype=np.float32)
            n_missing = 0
            for k, occ_id in enumerate(ssub_occ):
                key = (int(occ_id), int(cy), int(s))
                if key in ch_probs:
                    p_home_mat[k]   = ch_probs[key]["p_home"]
                    p_work_mat[k]   = ch_probs[key]["p_work"]
                    p_retail_mat[k] = ch_probs[key]["p_retail"]
                else:
                    p_home_mat[k]   = 0.5   # no-preference fallback (matches Leg-2 template)
                    p_work_mat[k]   = 0.5
                    p_retail_mat[k] = 0.5
                    n_missing += 1
            if n_missing > 0:
                print(f"    WARNING: {n_missing}/{n_syn} syn rows had no channel-probs key "
                      f"— used 0.5 fallback")

            # Observed per-slot rates (used as rake targets)
            obs_hom_arr = (osub[HOM_COLS].to_numpy(dtype=float)
                           if n_obs > 0 else np.full((0, N_SLOTS), np.nan))
            obs_wrk_arr = (osub[WRK_COLS].to_numpy(dtype=float)
                           if n_obs > 0 else np.full((0, N_SLOTS), np.nan))
            obs_ret_arr = (osub[RET_COLS].to_numpy(dtype=float)
                           if n_obs > 0 else np.full((0, N_SLOTS), np.nan))

            # Pre-rake aggregate rates (for provenance)
            before_home   = float(np.nanmean(aug.loc[syn_mask, HOM_COLS].to_numpy(dtype=float))) * 100
            before_work   = float(np.nanmean(aug.loc[syn_mask, WRK_COLS].to_numpy(dtype=float))) * 100
            before_retail = float(np.nanmean(aug.loc[syn_mask, RET_COLS].to_numpy(dtype=float))) * 100
            obs_home_agg   = float(np.nanmean(obs_hom_arr)) * 100 if n_obs > 0 else float("nan")
            obs_work_agg   = float(np.nanmean(obs_wrk_arr)) * 100 if n_obs > 0 else float("nan")
            obs_retail_agg = float(np.nanmean(obs_ret_arr)) * 100 if n_obs > 0 else float("nan")

            # telework_aware / floating_aware: activity + telework context for this cell
            if telework_aware or floating_aware:
                act_cols_48 = [f"act30_{ss2:03d}" for ss2 in range(1, N_SLOTS + 1)]
                pre_act_mat = aug.loc[ssub_idx, act_cols_48].to_numpy(dtype=float)
            else:
                pre_act_mat = None

            if floating_aware:
                if "TELEWORK" in aug.columns:
                    tele_vec = (aug.loc[ssub_idx, "TELEWORK"].fillna(0) == 1).to_numpy()
                else:
                    tele_vec = np.zeros(n_syn, dtype=bool)
            else:
                tele_vec = None

            new_hom_mat = np.zeros((n_syn, N_SLOTS), dtype=np.float32)
            new_wrk_mat = np.zeros((n_syn, N_SLOTS), dtype=np.float32)
            new_ret_mat = np.zeros((n_syn, N_SLOTS), dtype=np.float32)
            slot_prov = []
            for j in range(N_SLOTS):
                obs_r_hom = float(np.nanmean(obs_hom_arr[:, j])) if n_obs > 0 else 0.0
                obs_r_wrk = float(np.nanmean(obs_wrk_arr[:, j])) if n_obs > 0 else 0.0
                obs_r_ret = float(np.nanmean(obs_ret_arr[:, j])) if n_obs > 0 else 0.0
                n_home   = int(round(obs_r_hom * n_syn))
                n_work   = int(round(obs_r_wrk * n_syn))
                n_retail = int(round(obs_r_ret * n_syn))

                # Full rake over ALL persons (no locking). floating_aware: route
                # work-act persons into the home/work quota by priority
                # (telework->home, non-tele->work); retail is NEVER forced.
                if floating_aware:
                    aw_j = pre_act_mat[:, j] == 1          # work-activity at slot j
                    fh_j = aw_j & tele_vec                 # -> prefer home
                    fw_j = aw_j & (~tele_vec)               # -> prefer work
                    new_h, new_w, new_r = _joint_rake_slot(
                        p_home_mat[:, j], p_work_mat[:, j], p_retail_mat[:, j],
                        n_home, n_work, n_retail,
                        force_home=fh_j, force_work=fw_j)
                else:
                    new_h, new_w, new_r = _joint_rake_slot(
                        p_home_mat[:, j], p_work_mat[:, j], p_retail_mat[:, j],
                        n_home, n_work, n_retail)
                new_hom_mat[:, j] = new_h
                new_wrk_mat[:, j] = new_w
                new_ret_mat[:, j] = new_r

                slot_prov.append({
                    "slot":           j + 1,
                    "obs_home_pct":   round(obs_r_hom * 100, 3),
                    "obs_work_pct":   round(obs_r_wrk * 100, 3),
                    "obs_retail_pct": round(obs_r_ret * 100, 3),
                    "n_home":         n_home,
                    "n_work":         n_work,
                    "n_retail":       n_retail,
                    "ach_home_pct":   round(float(new_h.mean()) * 100, 3),
                    "ach_work_pct":   round(float(new_w.mean()) * 100, 3),
                    "ach_retail_pct": round(float(new_r.mean()) * 100, 3),
                })

            # telework_aware post-rake fixup: resolves classic FLOATING
            # (wrk=hom=ret=0 on a work-act slot -> hom=1) AND work/retail
            # activity-coherence conflicts (ret=1 on a work-act slot -> hom=1,
            # ret=0). Both are ADDITIVE (inflate home beyond quota) — the
            # documented telework_aware trade-off; --floating_aware avoids it.
            n_floating_fixed = 0
            n_work_retail_fixed = 0
            if telework_aware and pre_act_mat is not None:
                (new_hom_mat, new_wrk_mat, new_ret_mat,
                 n_floating_fixed, n_work_retail_fixed) = _post_rake_floating_fixup(
                    new_hom_mat, new_wrk_mat, new_ret_mat, pre_act_mat
                )

            # floating_aware: measure (do NOT dump) residual floating AND
            # work/retail conflicts — the irreducible activity-vs-occupancy
            # excess, left as-is so ALL THREE marginals stay exact.
            cell_float = 0
            cell_work_retail_conflict = 0
            cell_work_slots = 0
            if floating_aware and pre_act_mat is not None:
                aw_mat = pre_act_mat == 1
                cell_work_slots = int(aw_mat.sum())
                cell_float = int((aw_mat & (new_hom_mat == 0)
                                  & (new_wrk_mat == 0) & (new_ret_mat == 0)).sum())
                cell_work_retail_conflict = int((aw_mat & (new_ret_mat == 1)).sum())

            # Write raked values back into aug DataFrame
            aug.loc[ssub_idx, HOM_COLS] = new_hom_mat.astype(float)
            aug.loc[ssub_idx, WRK_COLS] = new_wrk_mat.astype(float)
            aug.loc[ssub_idx, RET_COLS] = new_ret_mat.astype(float)

            after_home   = float(np.nanmean(new_hom_mat)) * 100
            after_work   = float(np.nanmean(new_wrk_mat)) * 100
            after_retail = float(np.nanmean(new_ret_mat)) * 100
            hw_viol = int(np.sum((new_hom_mat == 1) & (new_wrk_mat == 1)))
            hr_viol = int(np.sum((new_hom_mat == 1) & (new_ret_mat == 1)))
            wr_viol = int(np.sum((new_wrk_mat == 1) & (new_ret_mat == 1)))

            provenance[f"cy{cy}_s{s}"] = {
                "n_obs":            n_obs,
                "n_syn":            n_syn,
                "n_missing_keys":   n_missing,
                "obs_home_agg_pct":   round(obs_home_agg, 3),
                "obs_work_agg_pct":   round(obs_work_agg, 3),
                "obs_retail_agg_pct": round(obs_retail_agg, 3),
                "before_home_pct":    round(before_home, 3),
                "before_work_pct":    round(before_work, 3),
                "before_retail_pct":  round(before_retail, 3),
                "after_home_pct":     round(after_home, 3),
                "after_work_pct":     round(after_work, 3),
                "after_retail_pct":   round(after_retail, 3),
                "mutual_excl_viol_home_work":   hw_viol,
                "mutual_excl_viol_home_retail": hr_viol,
                "mutual_excl_viol_work_retail": wr_viol,
                "telework_fixup_floating_fixed":     n_floating_fixed,
                "telework_fixup_work_retail_fixed":  n_work_retail_fixed,
                "residual_floating":              cell_float,
                "work_act_retail_conflicts":      cell_work_retail_conflict,
                "work_act_slots":                 cell_work_slots,
                "residual_floating_pct":  round(100.0 * cell_float / max(cell_work_slots, 1), 3),
                "slots": slot_prov,
            }
            _resid_str = (f"  resid_float: {cell_float}/{cell_work_slots} "
                          f"({100.0*cell_float/max(cell_work_slots,1):.2f}%)  "
                          f"work/ret conflicts: {cell_work_retail_conflict}"
                          if floating_aware else "")
            print(f"    home: {before_home:.1f}% -> {after_home:.1f}% (obs {obs_home_agg:.1f}%)  "
                  f"work: {before_work:.1f}% -> {after_work:.1f}% (obs {obs_work_agg:.1f}%)  "
                  f"retail: {before_retail:.1f}% -> {after_retail:.1f}% (obs {obs_retail_agg:.1f}%)  "
                  f"viol(hw/hr/wr)={hw_viol}/{hr_viol}/{wr_viol}{_resid_str}", flush=True)

    # ── Step 5: Atomic write ──────────────────────────────────────────────────
    print("\n[5/5] Writing raked CSV + provenance JSON...")

    # Global mutual-exclusion spot-check across all rows (all 3 pairs + triple)
    total_hw = total_hr = total_wr = total_triple = 0
    for j in range(1, N_SLOTS + 1):
        h = aug[f"hom30_{j:03d}"]
        w = aug[f"wrk30_{j:03d}"]
        r = aug[f"ret30_{j:03d}"]
        total_hw     += int(((h == 1) & (w == 1)).sum())
        total_hr     += int(((h == 1) & (r == 1)).sum())
        total_wr     += int(((w == 1) & (r == 1)).sum())
        total_triple += int(((h == 1) & (w == 1) & (r == 1)).sum())
    print(f"  Global mutual-exclusion violations after rake: "
          f"home&work={total_hw}  home&retail={total_hr}  work&retail={total_wr}  "
          f"all-three={total_triple} (expect 0 for all)")

    # Global FLOATING + work/retail-conflict tally on synthetic work-activity
    # slots (floating_aware report)
    if floating_aware:
        syn_m = (aug["IS_SYNTHETIC"] == 1).values
        g_float = 0
        g_conflict = 0
        g_work = 0
        for j in range(1, N_SLOTS + 1):
            ss = f"{j:03d}"
            if f"act30_{ss}" not in aug.columns:
                continue
            aw = syn_m & (aug[f"act30_{ss}"].values == 1)
            hv = aug[f"hom30_{ss}"].values
            wv = aug[f"wrk30_{ss}"].values
            rv = aug[f"ret30_{ss}"].values
            g_work    += int(aw.sum())
            g_float   += int((aw & (hv == 0) & (wv == 0) & (rv == 0)).sum())
            g_conflict += int((aw & (rv == 1)).sum())
        print(f"  Global residual FLOATING (work-act, syn): {g_float}/{g_work} "
              f"({100.0*g_float/max(g_work,1):.2f}%) — irreducible activity-vs-occupancy "
              f"excess; NOT dumped to home (all 3 marginals preserved)")
        print(f"  Global work-act/retail conflicts (syn): {g_conflict}/{g_work} "
              f"({100.0*g_conflict/max(g_work,1):.2f}%) — retail has no forced tier "
              f"(see module docstring); NOT dumped, measured only")

    # Atomic write: .tmp + os.replace
    tmp_path = raked_path + ".tmp"
    aug.to_csv(tmp_path, index=False)
    n_written = sum(1 for _ in open(tmp_path, encoding="utf-8")) - 1   # exclude header
    if n_written != len(aug):
        raise RuntimeError(
            f"Row count mismatch writing {tmp_path}: "
            f"wrote {n_written}, expected {len(aug)}"
        )
    os.replace(tmp_path, raked_path)
    print(f"  Wrote {len(aug):,} rows -> {raked_path}")

    # Copy G3 co-presence thresholds provenance from source (co-presence
    # columns are unaffected by the retail rake)
    g3_src = os.path.join(r5_dir, "g3_copresence_thresholds.json")
    if os.path.isfile(g3_src):
        shutil.copy2(g3_src, os.path.join(output_dir, "g3_copresence_thresholds.json"))
        print(f"  Copied G3 thresholds JSON from source -> {output_dir}")

    provenance["_meta"] = {
        "telework_aware": telework_aware,
        "floating_aware": floating_aware,
        "temperature": TEMPERATURE,
        "retail_pos_weight": retail_pos_weight,
    }
    with open(prov_path, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2)
    print(f"  Wrote rake provenance -> {prov_path}")

    print(f"\nOK 04L (Leg-3, 4-split) complete.")
    print(f"  Raked dir:  {output_dir}")
    print(f"  Next step (Delta H chain): 3rdJ_04M_mindwell_4split.py on this dir, "
          f"then 3rdJ_04T_act_rake_4split.py, then the final validator run.")


if __name__ == "__main__":
    main()
