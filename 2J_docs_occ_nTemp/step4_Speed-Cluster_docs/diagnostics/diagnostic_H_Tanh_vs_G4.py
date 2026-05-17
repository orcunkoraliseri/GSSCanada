"""
diagnostic_H_Tanh_vs_G4.py — H-Tier-1.5 inference-only logit/loss dump.

Tests the Tanh-bounding hypothesis: H_Tanh home/cop heads wrapped with
nn.Tanh() may cluster predicted probabilities around 0.5–0.7 vs G4's
bimodal 0.05/0.95, raising BCE even when the binarized AT_HOME gate holds.

Runs teacher-forcing self-reconstruction on the val set: each respondent's
observed diary is used as both encoder source and decoder target, capturing
the raw pre-sigmoid home logits under ideal (ground-truth-fed) conditions.

Usage (on cluster via job_diag_H_Tanh_vs_G4.sh):
    python diagnostic_H_Tanh_vs_G4.py \\
        --checkpoint /speed-scratch/.../outputs_step4_G4/checkpoints/best_model.pt \\
        --data_dir   /speed-scratch/.../outputs_step4_G1 \\
        --output_dir /speed-scratch/.../diagnostics_H_Tanh_vs_G4 \\
        --tag G4 --tanh_heads 0

Outputs (all in output_dir):
    {tag}_home_logits.npy      — (N, 48) pre-sigmoid home head outputs
    {tag}_home_probs.npy       — (N, 48) sigmoid(logits)
    {tag}_home_bce.npy         — (N, 48) per-sample per-slot BCE
    {tag}_per_slot_bce.csv     — (48 rows) slot, mean_bce
    {tag}_per_epoch_home.csv   — (E rows) epoch, home  (from training log)
"""

import argparse
import importlib
import os
import sys

import numpy as np
import pandas as pd
import torch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.dirname(SCRIPT_DIR)   # one up: occModeling/ where 04B_model.py lives
sys.path.insert(0, MODEL_DIR)
model_mod = importlib.import_module("04B_model")
ConditionalTransformer = model_mod.ConditionalTransformer


def parse_args():
    p = argparse.ArgumentParser(description="H-Tier-1.5 logit/loss diagnostic")
    p.add_argument("--checkpoint",  required=True,
                   help="Path to best_model.pt for this tag")
    p.add_argument("--data_dir",    required=True,
                   help="Data dir containing step4_val.pt and step4_feature_config.json")
    p.add_argument("--output_dir",  required=True,
                   help="Directory for output artefacts (created if absent)")
    p.add_argument("--tag",         required=True,
                   help="Label used in output filenames (e.g. G4, H_Tanh)")
    p.add_argument("--tanh_heads",  type=int, required=True,
                   help="0 = plain Linear heads (G4); 1 = Tanh-wrapped heads (H_Tanh). "
                        "Must match the head architecture in the checkpoint.")
    return p.parse_args()


def main():
    args = parse_args()

    # Set H_TANH_HEADS before ConditionalTransformer.__init__ so head shape matches ckpt.
    os.environ["H_TANH_HEADS"] = str(args.tanh_heads)
    os.makedirs(args.output_dir, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[{args.tag}] device={device}  H_TANH_HEADS={os.environ['H_TANH_HEADS']}")
    print(f"[{args.tag}] checkpoint : {args.checkpoint}")
    print(f"[{args.tag}] data_dir   : {args.data_dir}")
    print(f"[{args.tag}] output_dir : {args.output_dir}")

    # ── Load val split ─────────────────────────────────────────────────────────
    val_path = os.path.join(args.data_dir, "step4_val.pt")
    print(f"\n[{args.tag}] loading {val_path} ...")
    val_data = torch.load(val_path, map_location="cpu", weights_only=False)
    N = len(val_data["act_seq"])
    print(f"[{args.tag}] val respondents: {N}")

    # ── Load checkpoint ────────────────────────────────────────────────────────
    print(f"[{args.tag}] loading checkpoint ...")
    if not os.path.isfile(args.checkpoint):
        raise FileNotFoundError(f"Checkpoint not found: {args.checkpoint}")
    ckpt         = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model_config = ckpt["model_config"]
    model        = ConditionalTransformer(model_config).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"[{args.tag}] loaded epoch={ckpt.get('epoch','?')}  "
          f"val_score={ckpt.get('val_score','?')}")

    # ── Teacher-forcing self-reconstruction pass ───────────────────────────────
    # Source = observed diary; decoder target = same diary; tgt_strata = obs_strata.
    # Tests whether the home head logit range is bounded by the Tanh wrap in H_Tanh
    # vs the unconstrained Linear in G4, independent of autoregressive cascading.
    batch_size   = 256
    all_logits   = []   # (N, 48)  pre-sigmoid home logits
    all_home_tgt = []   # (N, 48)  binary AT_HOME ground truth

    with torch.no_grad():
        for start in range(0, N, batch_size):
            end    = min(start + batch_size, N)
            act_t  = val_data["act_seq"][start:end].to(device)
            aux_t  = val_data["aux_seq"][start:end].to(device)
            cond_t = val_data["cond_vec"][start:end].to(device)
            cidx_t = val_data["cycle_idx"][start:end].to(device)
            strat  = val_data["obs_strata"][start:end].to(device)
            home_tgt = val_data["aux_seq"][start:end, :, 0].numpy()  # (B,48) AT_HOME

            memory = model.encode(act_t, aux_t, cond_t, cidx_t)
            _, home_logits, _, _ = model.decode(
                dec_act_seq=act_t,
                dec_aux_seq=aux_t,
                tgt_strata=strat,
                memory=memory,
                cond_vec=cond_t,
                cycle_idx=cidx_t,
            )
            # home_logits: (B, 48) — output of home_head before any sigmoid/BCE
            all_logits.append(home_logits.cpu().float().numpy())
            all_home_tgt.append(home_tgt)

            if (start // batch_size) % 5 == 0:
                print(f"  [{args.tag}] {end}/{N} respondents", flush=True)

    logits_np = np.concatenate(all_logits,   axis=0)  # (N, 48)
    tgt_np    = np.concatenate(all_home_tgt, axis=0)  # (N, 48)

    # ── (b) Save logits ────────────────────────────────────────────────────────
    np.save(os.path.join(args.output_dir, f"{args.tag}_home_logits.npy"), logits_np)
    print(f"\n[{args.tag}] home_logits: shape={logits_np.shape}  "
          f"min={logits_np.min():.3f}  max={logits_np.max():.3f}  "
          f"mean={logits_np.mean():.3f}  std={logits_np.std():.3f}")

    # ── (c) Predicted probabilities ────────────────────────────────────────────
    # Numerically stable sigmoid via numpy
    probs_np = np.where(
        logits_np >= 0,
        1.0 / (1.0 + np.exp(-logits_np)),
        np.exp(logits_np) / (1.0 + np.exp(logits_np)),
    )
    np.save(os.path.join(args.output_dir, f"{args.tag}_home_probs.npy"), probs_np)
    frac_confident = float(np.mean((probs_np < 0.1) | (probs_np > 0.9)))
    frac_mid       = float(np.mean((probs_np > 0.4) & (probs_np < 0.7)))
    print(f"[{args.tag}] home_probs : min={probs_np.min():.3f}  max={probs_np.max():.3f}  "
          f"frac<0.1or>0.9={frac_confident:.3f}  frac(0.4,0.7)={frac_mid:.3f}")

    # ── (d) Per-sample BCE ─────────────────────────────────────────────────────
    # Numerically stable BCEWithLogits: max(l,0) - y*l + log(1 + exp(-|l|))
    bce_np = (
        np.maximum(logits_np, 0)
        - tgt_np * logits_np
        + np.log1p(np.exp(-np.abs(logits_np)))
    )
    np.save(os.path.join(args.output_dir, f"{args.tag}_home_bce.npy"), bce_np)
    print(f"[{args.tag}] home_bce   : mean={bce_np.mean():.4f}  "
          f"median={np.median(bce_np):.4f}")

    # ── (e) Per-slot mean BCE ──────────────────────────────────────────────────
    per_slot = bce_np.mean(axis=0)  # (48,)
    df_slot  = pd.DataFrame({"slot": np.arange(48), "bce": per_slot})
    df_slot.to_csv(
        os.path.join(args.output_dir, f"{args.tag}_per_slot_bce.csv"), index=False
    )
    top3 = df_slot.nlargest(3, "bce")[["slot", "bce"]].values
    print(f"[{args.tag}] per_slot_bce: top-3 worst slots {top3}")

    # ── (f) Per-epoch home loss from training log ──────────────────────────────
    # Derive run_dir as the grandparent of the checkpoint (ckpt lives in checkpoints/)
    run_dir  = os.path.dirname(os.path.dirname(os.path.abspath(args.checkpoint)))
    log_path = os.path.join(run_dir, "step4_training_log.csv")
    if os.path.isfile(log_path):
        df_log   = pd.read_csv(log_path)
        df_epoch = df_log[["epoch", "home_loss"]].rename(columns={"home_loss": "home"})
        df_epoch.to_csv(
            os.path.join(args.output_dir, f"{args.tag}_per_epoch_home.csv"), index=False
        )
        final_home = float(df_epoch["home"].iloc[-1])
        print(f"[{args.tag}] per_epoch_home: {len(df_epoch)} epochs  "
              f"final_home_loss={final_home:.4f}")
    else:
        print(f"[{args.tag}] WARNING: training log not found at {log_path}  "
              f"(per_epoch_home.csv not written)")

    print(f"\n[{args.tag}] DONE — all artefacts written to {args.output_dir}")


if __name__ == "__main__":
    main()
