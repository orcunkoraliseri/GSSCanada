#!/usr/bin/env python3
"""
04E_cop_rescue_test.py — Test COP inference modifications on G4 checkpoint

Three tests on a subset of respondents (default 5000):
  1. Seed Variance:      10 seeds, greedy COP -> is COP gap systematic?
  2. Threshold Sweep:    cop_feedback_threshold in {0.3, 0.4, 0.5, 0.6, 0.7}
  3. Multi-Sample Best:  K=10 Bernoulli COP samples/respondent, select best

Usage:
  python 04E_cop_rescue_test.py \
    --checkpoint outputs_step4_G4/checkpoints/best_model.pt \
    --data_dir outputs_step4_G1 \
    --subset 5000

Output: JSON at outputs_step4_G4/cop_rescue_test.json + console report
"""
import argparse
import importlib
import json
import os
import sys
import time
from collections import Counter

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

model_mod = importlib.import_module("04B_model")
ConditionalTransformer = model_mod.ConditionalTransformer

N_SLOTS = 48
COP_NAMES = [
    "Alone", "Spouse", "OwnChild_under5", "OwnChild_5to13",
    "OwnChild_14to17", "OtherHH", "OtherNonHH", "Coworker", "Colleagues",
]


def parse_args():
    p = argparse.ArgumentParser(description="COP rescue test on G4")
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--data_dir", required=True)
    p.add_argument("--subset", type=int, default=5000)
    p.add_argument("--output_json", default=None)
    p.add_argument("--K", type=int, default=10,
                   help="Samples per respondent for Test 3")
    return p.parse_args()


def load_data(data_dir):
    splits = {}
    for split in ["train", "val", "test"]:
        path = os.path.join(data_dir, f"step4_{split}.pt")
        splits[split] = torch.load(path, map_location="cpu", weights_only=False)
    combined = {}
    for k in list(splits["train"].keys()):
        combined[k] = torch.cat(
            [splits[sp][k] for sp in ["train", "val", "test"]], dim=0
        )
    return combined


# ── Modified generate with configurable COP feedback ────────────────────────

def generate_modified(model, act_seq, aux_seq, cond_vec, cycle_idx,
                      tgt_strata, device, temperature=0.8,
                      home_threshold=0.5, cop_threshold=0.5,
                      cop_mode="greedy"):
    """
    cop_mode="greedy": cop_tok = (cop_probs > cop_threshold)
    cop_mode="sample": cop_tok = Bernoulli(cop_probs)

    Returns: gen_act (B,48), gen_home (B,48), gen_cop_probs (B,48,9)
    """
    B = act_seq.shape[0]

    with torch.no_grad():
        memory = model.encode(act_seq, aux_seq, cond_vec, cycle_idx)
        cond_vec_g, cycle_emb_g, strata_oh_g = model._build_dec_cond(
            cond_vec, cycle_idx, tgt_strata
        )

        gen_acts, gen_homes, gen_cop_probs = [], [], []

        bos_tok = (
            model.bos_token.expand(B, 1, model.d_model)
            + model.dec_pos_enc[:, :1, :]
        )
        dec_tokens = [bos_tok]

        for t in range(model.n_slots):
            dec_seq = torch.cat(dec_tokens, dim=1)
            causal_mask = nn.Transformer.generate_square_subsequent_mask(
                dec_seq.shape[1], device=device
            )
            dec_out, _ = model.decoder(
                dec_seq, memory,
                cond_vec_g, cycle_emb_g, strata_oh_g, causal_mask,
            )
            out_t = dec_out[:, -1, :]

            act_logits = model.act_head(out_t)
            if temperature > 0:
                act_probs = F.softmax(act_logits / temperature, dim=-1)
                act_tok = torch.multinomial(act_probs, 1).squeeze(-1)
            else:
                act_tok = act_logits.argmax(dim=-1)

            home_tok = (
                torch.sigmoid(model.home_head(out_t).squeeze(-1))
                > home_threshold
            ).float()

            cop_probs = torch.sigmoid(model.cop_head(out_t))
            if cop_mode == "greedy":
                cop_tok = (cop_probs > cop_threshold).float()
            else:
                cop_tok = torch.bernoulli(cop_probs)

            gen_acts.append(act_tok)
            gen_homes.append(home_tok)
            gen_cop_probs.append(cop_probs)

            if t < model.n_slots - 1:
                aux_t = torch.cat(
                    [home_tok.unsqueeze(-1), cop_tok], dim=-1
                )
                act_emb = model.act_embedding(act_tok)
                slot_in = torch.cat([act_emb, aux_t], dim=-1)
                slot_out = model.slot_linear(slot_in).unsqueeze(1)
                slot_out = slot_out + model.dec_pos_enc[:, t + 1 : t + 2, :]
                dec_tokens.append(slot_out)

    return (
        torch.stack(gen_acts, dim=1),
        torch.stack(gen_homes, dim=1),
        torch.stack(gen_cop_probs, dim=1),
    )


# ── Helpers ──────────────────────────────────────────────────────────────────

def build_syn_pairs(data, indices):
    obs_strata = data["obs_strata"][indices].numpy()
    syn_idx, syn_tgt = [], []
    for j, idx in enumerate(indices):
        s_obs = int(obs_strata[j])
        for s in [1, 2, 3]:
            if s != s_obs:
                syn_idx.append(int(idx))
                syn_tgt.append(s)
    return syn_idx, syn_tgt


def run_inference_batch(model, data, syn_idx, syn_tgt, device,
                        batch_size=256, **gen_kwargs):
    all_cops = []
    N = len(syn_idx)
    for start in range(0, N, batch_size):
        end = min(start + batch_size, N)
        bi = syn_idx[start:end]
        bt = syn_tgt[start:end]

        act_t = data["act_seq"][bi].to(device)
        aux_t = data["aux_seq"][bi].to(device)
        cond_t = data["cond_vec"][bi].to(device)
        cidx_t = data["cycle_idx"][bi].to(device)
        strat = torch.tensor(bt, dtype=torch.long, device=device)

        _, _, cop_probs = generate_modified(
            model, act_t, aux_t, cond_t, cidx_t, strat, device, **gen_kwargs
        )
        all_cops.append(cop_probs.cpu().numpy())

    return np.concatenate(all_cops, axis=0)


def compute_cop_metrics(syn_cops, obs_prev):
    syn_prev = np.nanmean(syn_cops, axis=(0, 1))
    gap_pp = (syn_prev - obs_prev) * 100.0
    max_gap = float(np.abs(gap_pp).max())
    max_ch = COP_NAMES[int(np.abs(gap_pp).argmax())]
    return max_gap, max_ch, gap_pp, syn_prev


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("=" * 60)
    print("COP Rescue Test -- G4 Inference Modifications")
    print("=" * 60)
    print(f"  checkpoint: {args.checkpoint}")
    print(f"  data_dir:   {args.data_dir}")
    print(f"  subset:     {args.subset}")
    print(f"  K:          {args.K}")
    print(f"  device:     {device}")

    # ── Load data ──
    print("\n[1/5] Loading data...")
    data = load_data(args.data_dir)
    n = len(data["act_seq"])
    print(f"  Total respondents: {n}")

    np.random.seed(0)
    subset = np.sort(
        np.random.choice(n, size=min(args.subset, n), replace=False)
    )
    print(f"  Subset: {len(subset)} respondents")

    obs_cop = data["aux_seq"][subset].numpy()[:, :, 1:]
    obs_prev = np.nanmean(obs_cop, axis=(0, 1))
    print("\n  Observed COP prevalence (%):")
    for i, name in enumerate(COP_NAMES):
        print(f"    {name:20s}: {obs_prev[i]*100:.2f}%")

    syn_idx, syn_tgt = build_syn_pairs(data, subset)
    N_syn = len(syn_idx)
    print(f"\n  Synthetic pairs: {N_syn}")

    # ── Load model ──
    print("\n[2/5] Loading G4 checkpoint...")
    ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model = ConditionalTransformer(ckpt["model_config"]).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"  Loaded from epoch {ckpt.get('epoch', '?')}")

    results = {}

    # ═══════════════════════════════════════════════════════════════════
    # TEST 1: Seed Variance
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("[3/5] TEST 1: Seed Variance (10 seeds, greedy COP)")
    print("=" * 60)

    test1 = {}
    for seed in range(1, 11):
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        t0 = time.time()
        cops = run_inference_batch(
            model, data, syn_idx, syn_tgt, device,
            temperature=0.8, cop_threshold=0.5, cop_mode="greedy",
        )
        mg, mc, gaps, _ = compute_cop_metrics(cops, obs_prev)
        dt = time.time() - t0
        test1[seed] = {"max_gap": mg, "channel": mc, "gaps": gaps.tolist()}
        print(f"  Seed {seed:2d}: max gap = {mg:6.2f} pp ({mc:20s}) [{dt:.1f}s]")

    all_gaps = [v["max_gap"] for v in test1.values()]
    print(f"\n  Summary: min={min(all_gaps):.2f}, max={max(all_gaps):.2f}, "
          f"mean={np.mean(all_gaps):.2f}, std={np.std(all_gaps):.2f}")

    if min(all_gaps) < 5.0:
        verdict1 = "PASS_SOME_SEEDS"
    elif np.std(all_gaps) > 3.0:
        verdict1 = "HIGH_VARIANCE"
    else:
        verdict1 = "SYSTEMATIC_BIAS"
    print(f"  Verdict: {verdict1}")

    results["test1_seed_variance"] = {
        "seeds": {str(k): v for k, v in test1.items()},
        "min": min(all_gaps), "max": max(all_gaps),
        "mean": float(np.mean(all_gaps)), "std": float(np.std(all_gaps)),
        "verdict": verdict1,
    }

    # ═══════════════════════════════════════════════════════════════════
    # TEST 2: COP Threshold Sweep
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("[4/5] TEST 2: COP Feedback Threshold Sweep")
    print("=" * 60)

    test2 = {}
    for thresh in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]:
        torch.manual_seed(42)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(42)
        t0 = time.time()
        cops = run_inference_batch(
            model, data, syn_idx, syn_tgt, device,
            temperature=0.8, cop_threshold=thresh, cop_mode="greedy",
        )
        mg, mc, gaps, sp = compute_cop_metrics(cops, obs_prev)
        dt = time.time() - t0
        test2[thresh] = {
            "max_gap": mg, "channel": mc,
            "gaps": gaps.tolist(), "syn_prev": sp.tolist(),
        }
        print(f"  Thresh {thresh:.2f}: max gap = {mg:6.2f} pp ({mc:20s}) [{dt:.1f}s]")
        for i, name in enumerate(COP_NAMES):
            marker = " <<<" if abs(gaps[i]) >= mg - 0.01 else ""
            print(f"    {name:20s}: {gaps[i]:+7.2f} pp{marker}")

    all_gaps2 = {t: v["max_gap"] for t, v in test2.items()}
    best_thresh = min(all_gaps2, key=all_gaps2.get)
    print(f"\n  Best threshold: {best_thresh:.2f} -> "
          f"COP max gap = {all_gaps2[best_thresh]:.2f} pp")

    results["test2_threshold_sweep"] = {
        "thresholds": {f"{k:.2f}": v for k, v in test2.items()},
        "best_threshold": best_thresh,
        "best_max_gap": all_gaps2[best_thresh],
    }

    # ═══════════════════════════════════════════════════════════════════
    # TEST 3: Per-Respondent Multi-Sample Selection
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print(f"[5/5] TEST 3: Per-Respondent Multi-Sample (K={args.K})")
    print("=" * 60)

    K = args.K
    all_k_cops = np.zeros((K, N_syn, N_SLOTS, 9), dtype=np.float32)

    per_k_gaps = []
    for k in range(K):
        torch.manual_seed(200 + k)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(200 + k)
        t0 = time.time()
        cops = run_inference_batch(
            model, data, syn_idx, syn_tgt, device,
            temperature=0.8, cop_threshold=0.5, cop_mode="sample",
        )
        all_k_cops[k] = cops
        dt = time.time() - t0
        mg_k, mc_k, _, _ = compute_cop_metrics(cops, obs_prev)
        per_k_gaps.append({"k": k, "max_gap": mg_k, "channel": mc_k})
        print(f"  Sample {k+1:2d}/{K}: max gap = {mg_k:6.2f} pp ({mc_k}) [{dt:.1f}s]")

    # Selection: per synthetic pair, pick sample closest to obs prevalence
    # per-pair COP prevalence across 48 slots: (K, N_syn, 9)
    sample_cop_prev = np.mean(all_k_cops, axis=2)

    dist = np.sqrt(
        np.sum((sample_cop_prev - obs_prev[None, None, :]) ** 2, axis=-1)
    )  # (K, N_syn)
    best_k = np.argmin(dist, axis=0)  # (N_syn,)

    selected_cops = np.zeros((N_syn, N_SLOTS, 9), dtype=np.float32)
    for i in range(N_syn):
        selected_cops[i] = all_k_cops[best_k[i], i]

    mg_sel, mc_sel, gaps_sel, _ = compute_cop_metrics(selected_cops, obs_prev)

    # Best individual seed from Test 1 for comparison
    best_seed1_gap = min(all_gaps)

    print(f"\n  Best single seed (Test 1):    {best_seed1_gap:.2f} pp")
    print(f"  Best single Bernoulli sample: "
          f"{min(g['max_gap'] for g in per_k_gaps):.2f} pp")
    print(f"  Per-respondent selected:      {mg_sel:.2f} pp ({mc_sel})")

    k_counts = Counter(best_k.tolist())
    print(f"  Selection distribution: {dict(sorted(k_counts.items()))}")

    results["test3_multisample"] = {
        "K": K,
        "per_sample_gaps": per_k_gaps,
        "selected_max_gap": mg_sel,
        "selected_channel": mc_sel,
        "selected_gaps": gaps_sel.tolist(),
        "best_single_bernoulli": min(g["max_gap"] for g in per_k_gaps),
    }

    # ═══════════════════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"  Gate threshold:           5.0 pp")
    print(f"  J3 reference:             ~2.03 pp")
    print(f"  G4 baseline (seed=42):    ~20.55 pp")
    print(f"  ----")
    print(f"  Test 1 (seed variance):   {verdict1}  "
          f"[{min(all_gaps):.2f} - {max(all_gaps):.2f} pp]")
    print(f"  Test 2 (threshold sweep): best={best_thresh:.2f} -> "
          f"{all_gaps2[best_thresh]:.2f} pp")
    print(f"  Test 3 (multi-sample):    {mg_sel:.2f} pp")

    best_overall = min(min(all_gaps), all_gaps2[best_thresh], mg_sel)
    if best_overall < 5.0:
        print(f"\n  >>> COP GATE PASSED ({best_overall:.2f} pp) <<<")
        print("  >>> G4 RESCUE VIABLE -- proceed to full inference <<<")
    elif best_overall < 10.0:
        print(f"\n  >>> PARTIAL IMPROVEMENT ({best_overall:.2f} pp vs 20.55 baseline)")
        print("  >>> Consider combining approaches or Phase B retraining <<<")
    else:
        print(f"\n  >>> MINIMAL IMPROVEMENT ({best_overall:.2f} pp)")
        print("  >>> COP bias is structural -- Phase B retraining needed <<<")

    # Save JSON
    out_path = args.output_json
    if out_path is None:
        out_dir = os.path.dirname(args.checkpoint)
        if out_dir.endswith("checkpoints"):
            out_dir = os.path.dirname(out_dir)
        out_path = os.path.join(out_dir, "cop_rescue_test.json")

    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to: {out_path}")


if __name__ == "__main__":
    main()
