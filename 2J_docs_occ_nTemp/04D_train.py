"""
04D_train.py — Step 4D: Conditional Transformer Training Loop

Teacher-forcing training with:
  - Loss: λ_act(1.0)*CE + λ_home(0.5)*BCE + λ_cop(0.3)*BCE(masked)
  - Co-presence BCE masked by per-slot availability (from target respondent)
  - Colleagues BCE additionally zeroed for CYCLE_YEAR < 2015 (defense-in-depth)
  - AdamW optimizer, linear warm-up (2000 steps) → cosine decay
  - Early stopping: patience=10 on validation Jensen-Shannon divergence
  - Gradient clipping at max_norm=1.0
  - FP16 via AMP when --fp16 is set
  - 1-of-K neighbor resampled each epoch for stochastic diversity

Usage (HPC):
    python 04D_train.py --data_dir outputs_step4 --output_dir outputs_step4 \\
        --checkpoint_dir outputs_step4/checkpoints \\
        --batch_size 256 --max_epochs 100 --patience 10 --lr 1e-4 \\
        --d_model 256 --n_heads 8 --n_enc_layers 6 --n_dec_layers 6 --fp16

Usage (local sample test):
    python 04D_train.py --sample
    (overrides to d_model=64, 2 layers, batch=16, 5 epochs, no FP16)
"""

import argparse
import csv
import importlib
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Import model via importlib (filename starts with digit)
sys.path.insert(0, SCRIPT_DIR)
model_mod = importlib.import_module("04B_model")
ConditionalTransformer = model_mod.ConditionalTransformer

LAMBDA_ACT  = 1.0
LAMBDA_HOME = 0.5
LAMBDA_COP  = 0.3


# ── Dataset ──────────────────────────────────────────────────────────────────

class Step4Dataset(Dataset):
    """
    Wraps a single split's tensor dict + training pairs.
    Resamples one of K neighbors per epoch.
    """

    def __init__(self, data: dict, pairs: dict):
        self.data  = data
        self.pairs = pairs
        self._sampled_tgt = None
        self.resample()

    def resample(self):
        """Draw one of K neighbors for each pair — called once per epoch."""
        n_pairs = len(self.pairs["src_idx"])
        K = self.pairs["tgt_k_indices"].shape[1]
        k_choice = torch.randint(0, K, (n_pairs,))
        self._sampled_tgt = self.pairs["tgt_k_indices"][
            torch.arange(n_pairs), k_choice
        ]

    def __len__(self):
        return len(self.pairs["src_idx"])

    def __getitem__(self, i):
        s = self.pairs["src_idx"][i].item()
        t = self._sampled_tgt[i].item()
        return {
            # Encoder: observed diary of source respondent
            "act_seq":    self.data["act_seq"][s],
            "aux_seq":    self.data["aux_seq"][s],
            "cond_vec":   self.data["cond_vec"][s],
            "cycle_idx":  self.data["cycle_idx"][s],
            "cycle_year": self.data["cycle_year"][s],
            "obs_strata": self.data["obs_strata"][s],
            # Decoder target: neighbor's diary
            "dec_act_seq":    self.data["act_seq"][t],
            "dec_aux_seq":    self.data["aux_seq"][t],
            "dec_cop_avail":  self.data["cop_avail"][t],
            # Target stratum is the neighbor's observed stratum
            "tgt_strata": self.data["obs_strata"][t],
        }


# ── Loss ─────────────────────────────────────────────────────────────────────

def compute_loss(output: dict, batch: dict, device,
                 act_weights: torch.Tensor = None) -> dict:
    """
    Computes the three-component loss.

    Co-presence BCE is masked by:
      1. per-slot availability from the TARGET respondent (cop_avail)
      2. explicit zero for colleagues (index 8) when CYCLE_YEAR < 2015
    act_weights: optional (14,) float tensor of per-class CE weights.
    """
    act_logits  = output["act_logits"]   # (B, 48, 14)
    home_logits = output["home_logits"]  # (B, 48)
    cop_logits  = output["cop_logits"]   # (B, 48, 9)

    # Activity targets: 0-indexed int64
    act_tgt  = batch["dec_act_seq"]              # (B, 48)
    home_tgt = batch["dec_aux_seq"][:, :, 0]    # (B, 48) — AT_HOME is feature 0
    cop_tgt  = batch["dec_aux_seq"][:, :, 1:]   # (B, 48, 9) — features 1..9

    # Activity: cross-entropy over 14 classes (inverse-sqrt-frequency weighted)
    B, T, C = act_logits.shape
    act_loss = F.cross_entropy(
        act_logits.reshape(B * T, C),
        act_tgt.reshape(B * T),
        weight=act_weights,
    )

    # AT_HOME: binary cross-entropy
    home_loss = F.binary_cross_entropy_with_logits(home_logits, home_tgt)

    # Co-presence: BCE with per-slot availability masking
    cop_loss_raw = F.binary_cross_entropy_with_logits(
        cop_logits, cop_tgt, reduction="none"
    )  # (B, 48, 9)

    cop_avail = batch["dec_cop_avail"].float()   # (B, 48, 9)
    cop_loss_masked = cop_loss_raw * cop_avail

    # Defense-in-depth: also zero out colleagues (index 8) for 2005/2010 rows
    # cycle_year is from the source respondent, but within-cycle matching ensures
    # source and target share the same CYCLE_YEAR
    colleagues_mask = (batch["cycle_year"] >= 2015).float()  # (B,)
    cop_loss_masked[:, :, 8] *= colleagues_mask.unsqueeze(-1)

    # Verify colleagues loss is ~0 for 2005/2010 (print check in train loop)
    denom    = cop_avail.sum().clamp(min=1.0)
    cop_loss = cop_loss_masked.sum() / denom

    total = LAMBDA_ACT * act_loss + LAMBDA_HOME * home_loss + LAMBDA_COP * cop_loss

    return {
        "total_loss": total,
        "act_loss":   act_loss.item(),
        "home_loss":  home_loss.item(),
        "cop_loss":   cop_loss.item(),
    }


# ── LR schedule ──────────────────────────────────────────────────────────────

def get_lr(step: int, d_model: int, warmup_steps: int = 2000) -> float:
    """Linear warm-up then cosine decay (Transformer-style)."""
    if step == 0:
        step = 1
    if step < warmup_steps:
        return step / warmup_steps
    # Cosine decay from warm-up peak to a small floor
    progress = (step - warmup_steps) / max(1, warmup_steps * 50 - warmup_steps)
    return max(0.1, 0.5 * (1.0 + math.cos(math.pi * min(progress, 1.0))))


# ── Validation ───────────────────────────────────────────────────────────────

def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """Jensen-Shannon divergence between two distributions."""
    p = np.clip(p / (p.sum() + 1e-12), 1e-12, None)
    q = np.clip(q / (q.sum() + 1e-12), 1e-12, None)
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m)))


@torch.no_grad()
def validate(model, val_data: dict, val_pairs: dict, device, config: dict,
             n_sample: int = 2000) -> dict:
    """
    Validation pass: argmax decoding on a sample of val respondents.
    Computes per-stratum JS divergence between predicted and observed
    activity distributions within the val set.

    Uses batched generation (same approach as 04E) for speed.
    n_sample=2000 gives stable JS estimates; old n=200 was too noisy.
    """
    model.eval()
    n_val = len(val_data["act_seq"])
    n_sample = min(n_sample, n_val)

    # Pre-compute reference activity distributions per (CYCLE_YEAR, DDAY_STRATA)
    act_np    = val_data["act_seq"].cpu().numpy()           # (n_val, 48)
    strata_np = val_data["obs_strata"].cpu().numpy()        # (n_val,)
    cycle_np  = val_data["cycle_year"].cpu().numpy()        # (n_val,)
    ref_dists = {}
    for cy in np.unique(cycle_np):
        for s in [1, 2, 3]:
            mask = (cycle_np == cy) & (strata_np == s)
            if mask.sum() == 0:
                continue
            acts = act_np[mask].flatten()                   # 0-indexed
            dist = np.bincount(acts, minlength=14).astype(float)
            ref_dists[(int(cy), int(s))] = dist

    # Sample val respondents (fixed seed for reproducibility across epochs)
    rng     = np.random.default_rng(42)
    src_idx = rng.choice(n_val, size=n_sample, replace=False)

    generated  = {s: [] for s in [1, 2, 3]}
    gen_cycles = {s: [] for s in [1, 2, 3]}

    # Batched generation: collect all (respondent, s_tgt) pairs per chunk
    batch_sz = 256
    for start in range(0, n_sample, batch_sz):
        end   = min(start + batch_sz, n_sample)
        chunk = src_idx[start:end]

        syn_idx    = []
        syn_strata = []
        syn_cycles = []
        for i in chunk:
            s_obs = int(strata_np[i])
            cy    = int(cycle_np[i])
            for s_tgt in [1, 2, 3]:
                if s_tgt != s_obs:
                    syn_idx.append(int(i))
                    syn_strata.append(s_tgt)
                    syn_cycles.append(cy)

        if not syn_idx:
            continue

        act_t  = val_data["act_seq"][syn_idx].to(device)
        aux_t  = val_data["aux_seq"][syn_idx].to(device)
        cond_t = val_data["cond_vec"][syn_idx].to(device)
        cidx_t = val_data["cycle_idx"][syn_idx].to(device)
        strat  = torch.tensor(syn_strata, dtype=torch.long, device=device)

        gen_act, _, _ = model.generate(act_t, aux_t, cond_t, cidx_t, strat, temperature=0)
        gen_act = gen_act.cpu().numpy()   # (K, 48) 0-indexed

        for k, (s_tgt, cy) in enumerate(zip(syn_strata, syn_cycles)):
            generated[s_tgt].append(gen_act[k])
            gen_cycles[s_tgt].append(cy)

    js_vals = []
    for s_tgt in [1, 2, 3]:
        acts_gen = np.array(generated[s_tgt]) if generated[s_tgt] else np.array([]).reshape(0, 48)
        cys_gen  = np.array(gen_cycles[s_tgt]) if gen_cycles[s_tgt] else np.array([])
        if len(acts_gen) == 0:
            continue
        for cy in np.unique(cys_gen):
            ref = ref_dists.get((int(cy), s_tgt))
            if ref is None:
                continue
            mask_g   = cys_gen == cy
            gen_dist = np.bincount(acts_gen[mask_g].flatten(), minlength=14).astype(float)
            js_vals.append(js_divergence(ref, gen_dist))

    mean_js = float(np.mean(js_vals)) if js_vals else float("nan")
    return {"val_js": mean_js}


# ── Main training function ────────────────────────────────────────────────────

def train(args):
    # Reproducibility seeds (see Phase1_ready.md: HPC runs must match on rerun)
    torch.manual_seed(42)
    np.random.seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    out_dir   = args.output_dir
    ckpt_dir  = args.checkpoint_dir
    os.makedirs(out_dir,  exist_ok=True)
    os.makedirs(ckpt_dir, exist_ok=True)
    print(f"  checkpoint_dir (absolute): {os.path.abspath(ckpt_dir)}")

    # ── Config ───────────────────────────────────────────────────────────
    cfg_path = os.path.join(args.data_dir, "step4_feature_config.json")
    with open(cfg_path) as f:
        feat_cfg = json.load(f)
    d_cond = feat_cfg["d_cond"]

    if args.sample:
        # Local test config (CPU-friendly, fast)
        model_config = {
            "d_model": 64, "n_heads": 4, "d_ff": 256,
            "N_enc": 2, "N_dec": 2,
            "d_act": 16, "d_cycle": 16,
            "dropout": 0.1, "n_activity_classes": 14,
            "n_copresence": 9, "n_slots": 48, "d_cond": d_cond,
        }
        args.batch_size = 16
        args.max_epochs = 5
        args.patience   = 3
        args.fp16       = False
    else:
        model_config = {
            "d_model": args.d_model, "n_heads": args.n_heads,
            "d_ff": 1024 if args.d_model == 256 else args.d_model * 4,
            "N_enc": args.n_enc_layers, "N_dec": args.n_dec_layers,
            "d_act": 32, "d_cycle": 32,
            "dropout": 0.1, "n_activity_classes": 14,
            "n_copresence": 9, "n_slots": 48, "d_cond": d_cond,
        }

    # ── Device ───────────────────────────────────────────────────────────
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"  Device: {device}")

    # ── Data ─────────────────────────────────────────────────────────────
    print("[1/4] Loading datasets and pairs...")
    train_data  = torch.load(os.path.join(args.data_dir, "step4_train.pt"),
                             map_location="cpu", weights_only=False)
    val_data    = torch.load(os.path.join(args.data_dir, "step4_val.pt"),
                             map_location="cpu", weights_only=False)
    train_pairs = torch.load(os.path.join(args.data_dir, "training_pairs.pt"),
                             map_location="cpu", weights_only=False)
    val_pairs   = torch.load(os.path.join(args.data_dir, "val_pairs.pt"),
                             map_location="cpu", weights_only=False)

    train_dataset = Step4Dataset(train_data, train_pairs)
    print(f"  Train pairs: {len(train_dataset)} | Val respondents: "
          f"{len(val_data['act_seq'])}")

    # Inverse-sqrt-frequency class weights for activity CE loss.
    # Downweights Sleep/Recreation dominance; boosts Work, Transit, Shopping gradients.
    act_flat = train_data["act_seq"].numpy().flatten()
    class_counts = np.bincount(act_flat, minlength=14).astype(float)
    class_weights_np = 1.0 / np.sqrt(np.maximum(class_counts, 1.0))
    class_weights_np = class_weights_np / class_weights_np.mean()  # normalize: mean=1
    act_class_weights = torch.tensor(class_weights_np, dtype=torch.float32, device=device)
    print("  Activity class weights (inv-sqrt-freq, mean-normalized):")
    for i, w in enumerate(class_weights_np):
        print(f"    class {i:2d}: {w:.3f}")

    # Inverse-frequency weighting for DDAY_STRATA imbalance
    src_strata = train_data["obs_strata"][train_pairs["src_idx"]].numpy()
    strata_counts = np.bincount(src_strata, minlength=4)
    sample_weights = np.array([
        1.0 / max(strata_counts[s], 1) for s in src_strata
    ], dtype=np.float32)
    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(train_dataset),
        replacement=True,
    )
    train_loader = DataLoader(
        train_dataset, batch_size=args.batch_size,
        sampler=sampler, num_workers=0, pin_memory=(device.type == "cuda"),
    )

    # ── Model ────────────────────────────────────────────────────────────
    print("[2/4] Building model...")
    model = ConditionalTransformer(model_config).to(device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"  Parameters: {total_params:,}")
    print(model)

    # ── Optimizer & schedule ─────────────────────────────────────────────
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-2)
    warmup_steps = 2000 if not args.sample else 50
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer,
        lr_lambda=lambda step: get_lr(step, model_config["d_model"], warmup_steps),
    )
    scaler = torch.amp.GradScaler("cuda") if (args.fp16 and device.type == "cuda") else None

    # Resume from checkpoint if requested
    start_epoch = 0
    best_val_js = float("inf")
    patience_counter = 0

    if args.resume:
        if not os.path.isfile(args.resume):
            raise FileNotFoundError(
                f"--resume path does not exist: {os.path.abspath(args.resume)}"
            )
        print(f"  Resuming from {os.path.abspath(args.resume)} "
              f"({os.path.getsize(args.resume) / 1e6:.1f} MB)")
        try:
            ckpt = torch.load(args.resume, map_location=device, weights_only=False)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Failed to load --resume checkpoint: {e}")
        model.load_state_dict(ckpt["model_state"])
        optimizer.load_state_dict(ckpt["optimizer_state"])
        scheduler.load_state_dict(ckpt["scheduler_state"])
        start_epoch     = ckpt["epoch"] + 1
        best_val_js     = ckpt.get("best_val_js", float("inf"))
        patience_counter = 0  # reset on resume — prior patience was from buggy warmup run
        print(f"  Resumed from epoch {start_epoch}, best_val_js={best_val_js:.4f}")

    # ── Training log CSV ─────────────────────────────────────────────────
    log_path = os.path.join(out_dir, "step4_training_log.csv")
    log_fields = ["epoch", "train_loss", "act_loss", "home_loss", "cop_loss",
                  "val_js", "lr", "grad_norm", "elapsed_s"]
    if start_epoch == 0:
        with open(log_path, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=log_fields).writeheader()

    # ── Training loop ────────────────────────────────────────────────────
    print("[3/4] Training...")
    global_step = start_epoch * len(train_loader)

    for epoch in range(start_epoch, args.max_epochs):
        model.train()
        epoch_start = time.time()

        # Resample 1-of-K neighbors for this epoch
        train_dataset.resample()

        epoch_losses = {"total": 0.0, "act": 0.0, "home": 0.0, "cop": 0.0}
        grad_norms   = []

        for batch in train_loader:
            # Move to device
            batch = {k: v.to(device) for k, v in batch.items()}
            optimizer.zero_grad()

            if scaler is not None:
                with torch.amp.autocast("cuda"):
                    out   = model(batch)
                    losses = compute_loss(out, batch, device, act_weights=act_class_weights)
                scaler.scale(losses["total_loss"]).backward()
                scaler.unscale_(optimizer)
                grad_norm = nn.utils.clip_grad_norm_(model.parameters(), 1.0).item()
                scaler.step(optimizer)
                scaler.update()
            else:
                out    = model(batch)
                losses = compute_loss(out, batch, device, act_weights=act_class_weights)
                losses["total_loss"].backward()
                grad_norm = nn.utils.clip_grad_norm_(model.parameters(), 1.0).item()
                optimizer.step()

            scheduler.step()
            global_step += 1

            epoch_losses["total"] += losses["total_loss"].item()
            epoch_losses["act"]   += losses["act_loss"]
            epoch_losses["home"]  += losses["home_loss"]
            epoch_losses["cop"]   += losses["cop_loss"]
            grad_norms.append(grad_norm)

            # Gradient health check: first backward pass of first epoch
            if epoch == start_epoch and global_step == 1:
                n_zero = sum(
                    1 for p in model.parameters()
                    if p.grad is not None and p.grad.norm().item() == 0
                )
                n_nan  = sum(
                    1 for p in model.parameters()
                    if p.grad is not None and torch.isnan(p.grad).any()
                )
                if n_zero > 0:
                    print(f"  WARN: {n_zero} params have zero gradient")
                if n_nan > 0:
                    print(f"  FAIL: {n_nan} params have NaN gradient")

        n_batches = len(train_loader)
        avg_loss  = epoch_losses["total"] / n_batches
        avg_act   = epoch_losses["act"]   / n_batches
        avg_home  = epoch_losses["home"]  / n_batches
        avg_cop   = epoch_losses["cop"]   / n_batches
        avg_gnorm = float(np.mean(grad_norms))
        cur_lr    = scheduler.get_last_lr()[0]

        # Validation pass
        val_result = validate(model, val_data, val_pairs, device, model_config)
        val_js     = val_result["val_js"]
        elapsed    = time.time() - epoch_start

        print(f"Epoch {epoch+1:3d}/{args.max_epochs}: "
              f"train_loss={avg_loss:.4f}  act={avg_act:.4f}  home={avg_home:.4f}  "
              f"cop={avg_cop:.4f}  |  val_JS={val_js:.4f}  "
              f"lr={cur_lr:.2e}  grad_norm={avg_gnorm:.3f}  "
              f"({elapsed:.0f}s)")

        # Append to training log
        with open(log_path, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=log_fields).writerow({
                "epoch": epoch + 1, "train_loss": round(avg_loss, 6),
                "act_loss": round(avg_act, 6), "home_loss": round(avg_home, 6),
                "cop_loss": round(avg_cop, 6), "val_js": round(val_js, 6),
                "lr": round(cur_lr, 8), "grad_norm": round(avg_gnorm, 4),
                "elapsed_s": round(elapsed, 1),
            })

        # Save last checkpoint (for resume on timeout)
        last_ckpt = os.path.join(ckpt_dir, "last_checkpoint.pt")
        torch.save({
            "epoch": epoch, "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "scheduler_state": scheduler.state_dict(),
            "best_val_js": best_val_js, "patience_counter": patience_counter,
            "model_config": model_config,
        }, last_ckpt)

        # Save best checkpoint
        if val_js < best_val_js:
            best_val_js      = val_js
            patience_counter = 0
            best_ckpt = os.path.join(ckpt_dir, "best_model.pt")
            torch.save({
                "epoch": epoch, "model_state": model.state_dict(),
                "model_config": model_config,
                "val_js": val_js,
            }, best_ckpt)
            print(f"  ✓ New best model saved (val_JS={val_js:.4f})")
        else:
            patience_counter += 1
            warmup_epochs = math.ceil(warmup_steps / max(1, len(train_loader)))
            if patience_counter >= args.patience and (epoch + 1) > warmup_epochs:
                print(f"  Early stopping at epoch {epoch+1} "
                      f"(no improvement for {args.patience} epochs)")
                break

    print(f"\n[4/4] Training complete. Best val_JS={best_val_js:.4f}")
    print(f"  Best checkpoint: {os.path.join(ckpt_dir, 'best_model.pt')}")
    print(f"  Training log:    {log_path}")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir",       default=None)
    p.add_argument("--output_dir",     default=None)
    p.add_argument("--checkpoint_dir", default=None)
    p.add_argument("--batch_size",     type=int,   default=256)
    p.add_argument("--max_epochs",     type=int,   default=100)
    p.add_argument("--patience",       type=int,   default=10)
    p.add_argument("--lr",             type=float, default=1e-4)
    p.add_argument("--d_model",        type=int,   default=256)
    p.add_argument("--n_heads",        type=int,   default=8)
    p.add_argument("--n_enc_layers",   type=int,   default=6)
    p.add_argument("--n_dec_layers",   type=int,   default=6)
    p.add_argument("--fp16",           action="store_true")
    p.add_argument("--resume",         default=None)
    p.add_argument("--sample",         action="store_true",
                   help="Use sample data and small model for local testing")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Resolve data / output dirs (auto-detect sample vs full)
    base_dir = os.path.join(SCRIPT_DIR, "outputs_step4_test" if args.sample else "outputs_step4")
    if args.data_dir is None:
        args.data_dir = base_dir
    if args.output_dir is None:
        args.output_dir = base_dir
    if args.checkpoint_dir is None:
        args.checkpoint_dir = os.path.join(base_dir, "checkpoints")

    print("=" * 60)
    print(f"Step 4D — Training  {'[SAMPLE MODE]' if args.sample else ''}")
    print("=" * 60)
    print(f"  data_dir:       {args.data_dir}")
    print(f"  output_dir:     {args.output_dir}")
    print(f"  checkpoint_dir: {args.checkpoint_dir}")
    print(f"  batch_size={args.batch_size}  max_epochs={args.max_epochs}  "
          f"patience={args.patience}  lr={args.lr}  fp16={args.fp16}")

    train(args)
