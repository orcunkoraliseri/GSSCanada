# -*- coding: utf-8 -*-
"""
3rdJ_04D_mdlm_train_2split.py — Step 4D-MDLM (Leg-2): Masked Diffusion Training.

Trains the MDLMOcc2Split model (3rdJ_04B_mdlm_2split.py) on the 10% ablation
data split (outputs_step4_s10/) produced by 3rdJ_04Q_make_s10_sample.py.

Training objective:
  MDLM masked-diffusion loss (cross-entropy on masked positions only, MDLM-
  weighted by 1/mask_ratio so that all mask ratios contribute equally in
  expectation).  The mask ratio r is sampled uniformly from (0, 1) per batch.

Multi-task losses (IDENTICAL weights/structure to the AR baseline 04D):
  act:   MDLM masked-diffusion CE (masked positions only)
  home:  BCEWithLogits on clean-pass home_logits
  work:  BCEWithLogits on clean-pass work_logits (masked by dec_work_avail)
  cop:   BCEWithLogits on clean-pass cop_logits (masked by dec_cop_avail)

Loss weighting, PCGrad, diversity loss, UncertaintyWeighting, SLAWWeighting:
  ALL inherited verbatim from 04D (same TASKS list, same env-var knobs).
  Loss weights are NOT tuned to isolate the structural effect of the MDLM
  backbone (per report §5 protocol: hold weights identical to AR baseline).

Masking schedule (MDLM):
  At each training step, sample r ~ Uniform(0, 1).  Independently mask each
  activity token in dec_act_seq with probability r.  The resulting noisy
  sequence is passed to the model's noisy encoder.  Unmasked positions in
  dec_act_seq are also fed (as the clean encoder input) so the binary heads
  receive a clean encoding regardless of the masking applied to the noisy pass.

CLI (mirrors 04D where sensible):
  --data_dir, --output_dir, --checkpoint_dir
  --d_model, --n_enc_layers (no n_dec_layers: MDLM has no decoder)
  --lr, --patience, --fp16, --batch_size, --max_epochs, --resume, --sample
  MDLM-specific:
  --mdlm_mask_schedule {linear, cosine}  (default cosine)
  --mdlm_denoise_steps int               (default 16, inference only — no effect on training)

Checkpoint contract (checkpoints_mdlm/best_model.pt):
  {epoch, model_state, model_config, val_js, home_gap, work_gap, val_score}
  model_type key will be "MDLM" to distinguish from AR checkpoints.

Usage:
    py -3 -X utf8 3rdJ_04D_mdlm_train_2split.py --sample
    py -3 -X utf8 3rdJ_04D_mdlm_train_2split.py --fp16   (cluster GPU, full mode)
"""

from __future__ import annotations

import argparse
import csv
import importlib
import json
import math
import os
import platform
import sys
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
mdlm_mod = importlib.import_module("3rdJ_04B_mdlm_2split")
MDLMOcc2Split = mdlm_mod.MDLMOcc2Split
MASK_TOKEN    = mdlm_mod.MASK_TOKEN
VOCAB_SIZE    = mdlm_mod.VOCAB_SIZE

# Re-use the non-model machinery from the AR training script.
ar_train_mod = importlib.import_module("3rdJ_04D_train_2split")
UncertaintyWeighting = ar_train_mod.UncertaintyWeighting
SLAWWeighting        = ar_train_mod.SLAWWeighting
EqualWeighting       = ar_train_mod.EqualWeighting
PCGrad               = ar_train_mod.PCGrad
diversity_loss       = ar_train_mod.diversity_loss
js_divergence        = ar_train_mod.js_divergence

# ── Platform-detection path block ─────────────────────────────────────────────
_SYSTEM = platform.system()
if _SYSTEM == "Windows":
    _LEG2_BASE = os.path.normpath(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split"
    )
elif os.path.isdir("/speed-scratch/o_iseri"):
    _LEG2_BASE = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split"
else:
    _LEG2_BASE = os.path.join(
        os.path.expanduser("~"),
        "GSSCanada", "GSSCanada-main", "3J_docs_occ_nTemp", "Leg2_2-split",
    )
# Default to 10% sample data dir for ablation
OUTPUT_DIR = os.path.join(_LEG2_BASE, "Step4_docs", "outputs_step4_s10")

# ── Multi-head machinery toggles (identical env vars to 04D) ─────────────────
WEIGHT_MODE  = os.environ.get("WEIGHT_MODE", "uw").lower()
USE_PCGRAD   = os.environ.get("USE_PCGRAD", "1") == "1"
LAMBDA_DIV   = float(os.environ.get("LAMBDA_DIV", "0.1"))
SLAW_BETA    = float(os.environ.get("SLAW_BETA", "0.9"))
ACTIVITY_BOOSTS = os.environ.get("ACTIVITY_BOOSTS", "1") != "0"
WORK_POS_WEIGHT = os.environ.get("WORK_POS_WEIGHT")
COP_POS_WEIGHT  = float(os.environ.get("COP_POS_WEIGHT", "0"))

TASKS = ["act", "home", "work", "cop"]
COLLEAGUES_IDX = 8
CYCLE_MAP = {2005: 0, 2010: 1, 2015: 2, 2022: 3}


# ── Dataset (identical to AR Step4Dataset2Split) ───────────────────────────────

class Step4DatasetMDLM(Dataset):
    """
    Per training pair: encoder = source respondent's tensors (observed day);
    decoder target = a sampled 1-of-K neighbour (resampled each epoch).

    Compared to the AR dataset, no r11 latent is added (R11 is AR-specific).
    """

    def __init__(self, data: dict, pairs: dict):
        self.data  = data
        self.pairs = pairs
        self._sampled_tgt = None
        self.resample()

    def resample(self):
        n_pairs = len(self.pairs["src_idx"])
        K       = self.pairs["tgt_k_indices"].shape[1]
        k_choice = torch.randint(0, K, (n_pairs,))
        self._sampled_tgt = self.pairs["tgt_k_indices"][torch.arange(n_pairs), k_choice]

    def __len__(self):
        return len(self.pairs["src_idx"])

    def __getitem__(self, i):
        s = self.pairs["src_idx"][i].item()
        t = self._sampled_tgt[i].item()
        return {
            "act_seq":       self.data["act_seq"][s],
            "aux_seq":       self.data["aux_seq"][s],
            "cond_vec":      self.data["cond_vec"][s],
            "cycle_idx":     self.data["cycle_idx"][s],
            "cycle_year":    self.data["cycle_year"][s],
            "obs_strata":    self.data["obs_strata"][s],
            "dec_act_seq":   self.data["act_seq"][t],
            "dec_aux_seq":   self.data["aux_seq"][t],
            "dec_cop_avail": self.data["cop_avail"][t],
            "dec_work_avail": self.data["work_avail"][t],
            "tgt_strata":    self.data["obs_strata"][t],
        }


# ── Masking (MDLM absorbing-state) ────────────────────────────────────────────

def apply_mask(act_seq: torch.Tensor, mask_ratio: float) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Independently mask each token in act_seq with probability mask_ratio.

    Parameters
    ----------
    act_seq   : (B, T) int64 — clean activity tokens (0..13)
    mask_ratio: float in (0, 1) — fraction to mask (sampled per batch in train)

    Returns
    -------
    noisy_seq : (B, T) int64 — with masked positions replaced by MASK_TOKEN (14)
    mask_pos  : (B, T) bool  — True where token was masked
    """
    mask_pos  = torch.bernoulli(
        torch.full(act_seq.shape, mask_ratio, device=act_seq.device)
    ).bool()
    noisy_seq = torch.where(mask_pos, torch.full_like(act_seq, MASK_TOKEN), act_seq)
    return noisy_seq, mask_pos


# ── Component losses ───────────────────────────────────────────────────────────

def component_losses_mdlm(output: dict, batch: dict,
                           act_weights=None, home_pos_weight=None,
                           work_pos_weight=None, cop_pos_weight=None) -> dict:
    """
    Component losses for MDLM.

    Activity loss: MDLM masked-diffusion CE.
      - Cross-entropy only on MASKED positions (mask_pos == True).
      - Weighted by 1/mask_ratio so all mask ratios contribute equally in
        expectation (standard MDLM weighting, Sahoo et al. 2024 eq. 5).
      - class weights (ACTIVITY_BOOSTS) applied identically to the AR baseline.

    Binary losses (home, work, cop): identical to AR 04D — computed on the
    clean-pass logits (binary heads are not masked-pass dependent).
    """
    act_logits  = output["act_logits"]   # (B,48,15)
    home_logits = output["home_logits"]  # (B,48)
    work_logits = output["work_logits"]  # (B,48)
    cop_logits  = output["cop_logits"]   # (B,48,9)
    mask_pos    = output["mask_pos"]     # (B,48) bool

    act_tgt  = batch["dec_act_seq"]                     # (B,48) long, values 0..13
    home_tgt = batch["dec_aux_seq"][:, :, 0].float()   # (B,48)
    work_tgt = batch["dec_aux_seq"][:, :, 1].float()   # (B,48)
    cop_tgt  = batch["dec_aux_seq"][:, :, 2:]          # (B,48,9)

    B, T, C = act_logits.shape  # C = VOCAB_SIZE = 15

    # ── Activity: MDLM masked CE ────────────────────────────────────────────
    n_masked = mask_pos.sum().float().clamp(min=1.0)
    mask_ratio = (n_masked / (B * T)).clamp(min=1e-6)

    if mask_pos.any():
        # Flatten and select only masked positions
        act_logits_f = act_logits.reshape(B * T, C)
        act_tgt_f    = act_tgt.reshape(B * T)
        mask_flat    = mask_pos.reshape(B * T)

        act_loss_raw = F.cross_entropy(
            act_logits_f[mask_flat],
            act_tgt_f[mask_flat],
            weight=act_weights,
            reduction="mean",
        )
        # MDLM weighting: 1 / mask_ratio
        act_loss = act_loss_raw / mask_ratio
    else:
        # Edge case: no positions masked (extremely rare with r ~ U(0,1))
        act_loss = torch.tensor(0.0, device=act_logits.device, requires_grad=True)

    # ── AT_HOME: BCE (always available) ─────────────────────────────────────
    home_loss = F.binary_cross_entropy_with_logits(
        home_logits, home_tgt, pos_weight=home_pos_weight,
    )

    # ── AT_WORK: BCE masked by work_avail ────────────────────────────────────
    work_avail = batch["dec_work_avail"].float()
    work_raw   = F.binary_cross_entropy_with_logits(
        work_logits, work_tgt, pos_weight=work_pos_weight, reduction="none",
    )
    work_loss = (work_raw * work_avail).sum() / work_avail.sum().clamp(min=1.0)

    # ── Co-presence: BCE masked + colleagues zeroed pre-2015 ─────────────────
    if cop_pos_weight is not None:
        cop_raw = F.binary_cross_entropy_with_logits(
            cop_logits, cop_tgt, pos_weight=cop_pos_weight.view(1, 1, -1), reduction="none",
        )
    else:
        cop_raw = F.binary_cross_entropy_with_logits(cop_logits, cop_tgt, reduction="none")
    cop_avail = batch["dec_cop_avail"].float()
    colleagues_mask = (batch["cycle_year"] >= 2015).float()
    cop_masked = cop_raw * cop_avail
    cop_masked[:, :, COLLEAGUES_IDX] = (
        cop_masked[:, :, COLLEAGUES_IDX] * colleagues_mask.unsqueeze(-1)
    )
    cop_loss = cop_masked.sum() / cop_avail.sum().clamp(min=1.0)

    return {"act": act_loss, "home": home_loss, "work": work_loss, "cop": cop_loss}


# ── Validation (mirrors 04D validate(), adapted for MDLM denoise) ─────────────

@torch.no_grad()
def validate(model, val_data, device, n_steps: int = 16,
             schedule: str = "cosine", n_sample: int = 2000):
    """Denoised generation on a sample; per-stratum JS + home/work gaps."""
    model.eval()
    n_val    = len(val_data["act_seq"])
    n_sample = min(n_sample, n_val)

    act_np    = val_data["act_seq"].cpu().numpy()
    strata_np = val_data["obs_strata"].cpu().numpy()
    cycle_np  = val_data["cycle_year"].cpu().numpy()
    home_np   = val_data["aux_seq"][:, :, 0].cpu().numpy()
    work_np   = val_data["aux_seq"][:, :, 1].cpu().numpy()
    wavail_np = val_data["work_avail"].cpu().numpy().astype(float)

    ref_dists, ref_home, ref_work = {}, {}, {}
    for cy in np.unique(cycle_np):
        for s in [1, 2, 3]:
            mask = (cycle_np == cy) & (strata_np == s)
            if mask.sum() == 0:
                continue
            dist = np.bincount(act_np[mask].flatten(), minlength=14).astype(float)
            ref_dists[(int(cy), int(s))] = dist
            ref_home[(int(cy), int(s))] = float(home_np[mask].mean())
            wa = wavail_np[mask]
            ref_work[(int(cy), int(s))] = float(
                (work_np[mask] * wa).sum() / max(wa.sum(), 1.0)
            )

    rng = np.random.default_rng(42)
    src_idx = rng.choice(n_val, size=n_sample, replace=False)

    gen_act_by  = {s: [] for s in [1, 2, 3]}
    gen_home_by = {s: [] for s in [1, 2, 3]}
    gen_work_by = {s: [] for s in [1, 2, 3]}
    gen_cy_by   = {s: [] for s in [1, 2, 3]}

    batch_sz = 128
    for start in range(0, n_sample, batch_sz):
        chunk = src_idx[start:start + batch_sz]
        syn_idx, syn_strata, syn_cy = [], [], []
        for i in chunk:
            s_obs = int(strata_np[i]); cy = int(cycle_np[i])
            for s_tgt in [1, 2, 3]:
                if s_tgt != s_obs:
                    syn_idx.append(int(i)); syn_strata.append(s_tgt); syn_cy.append(cy)
        if not syn_idx:
            continue

        act_t  = val_data["act_seq"][syn_idx].to(device)
        aux_t  = val_data["aux_seq"][syn_idx].to(device)
        cond_t = val_data["cond_vec"][syn_idx].to(device)
        cidx_t = val_data["cycle_idx"][syn_idx].to(device)
        strat  = torch.tensor(syn_strata, dtype=torch.long, device=device)

        g_act, g_home, g_work, _, _ = model.denoise(
            act_t, aux_t, cond_t, cidx_t, strat,
            n_steps=n_steps, schedule=schedule, temperature=0.0
        )
        g_act  = g_act.cpu().numpy()
        g_home = g_home.cpu().numpy()
        g_work = g_work.cpu().numpy()

        for k, (s_tgt, cy) in enumerate(zip(syn_strata, syn_cy)):
            gen_act_by[s_tgt].append(g_act[k])
            gen_home_by[s_tgt].append(g_home[k])
            gen_work_by[s_tgt].append(g_work[k])
            gen_cy_by[s_tgt].append(cy)

    js_vals, home_gaps, work_gaps = [], [], []
    for s_tgt in [1, 2, 3]:
        if not gen_act_by[s_tgt]:
            continue
        acts  = np.array(gen_act_by[s_tgt])
        homes = np.array(gen_home_by[s_tgt])
        works = np.array(gen_work_by[s_tgt])
        cys   = np.array(gen_cy_by[s_tgt])
        for cy in np.unique(cys):
            ref = ref_dists.get((int(cy), s_tgt))
            if ref is None:
                continue
            mg = cys == cy
            gen_dist = np.bincount(acts[mg].flatten(), minlength=14).astype(float)
            js_vals.append(js_divergence(ref, gen_dist))
            rh = ref_home.get((int(cy), s_tgt))
            if rh is not None:
                home_gaps.append(abs(float(homes[mg].mean()) - rh))
            rw = ref_work.get((int(cy), s_tgt))
            if rw is not None:
                work_gaps.append(abs(float(works[mg].mean()) - rw))

    mean_js   = float(np.mean(js_vals))   if js_vals   else float("nan")
    mean_home = float(np.mean(home_gaps)) if home_gaps else float("nan")
    mean_work = float(np.mean(work_gaps)) if work_gaps else float("nan")
    val_score = mean_js + 0.5 * (mean_home + mean_work) / 2.0
    return {"val_js": mean_js, "home_gap": mean_home,
            "work_gap": mean_work, "val_score": val_score}


# ── Main training ─────────────────────────────────────────────────────────────

def train(args):
    torch.manual_seed(42)
    np.random.seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    out_dir  = args.output_dir
    ckpt_dir = args.checkpoint_dir
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(ckpt_dir, exist_ok=True)

    with open(os.path.join(args.data_dir, "step4_feature_config.json")) as f:
        feat_cfg = json.load(f)
    d_cond = feat_cfg["d_cond"]

    if args.sample:
        model_config = {
            "model_type": "MDLM", "d_model": 64, "n_heads": 2, "d_ff": 256,
            "N_enc": 2, "d_act": 16, "d_cycle": 16, "dropout": 0.1,
            "n_activity_classes": 14, "n_copresence": 9, "n_slots": 48,
            "n_aux": feat_cfg.get("n_aux", 11), "d_cond": d_cond,
            "mdlm_mask_schedule": args.mdlm_mask_schedule,
            "mdlm_denoise_steps": args.mdlm_denoise_steps,
        }
        args.batch_size  = 16
        args.max_epochs  = 5
        args.patience    = 5
        args.warmup_epochs = 1
        args.fp16        = False
    else:
        model_config = {
            "model_type": "MDLM",
            "d_model":    args.d_model,
            "n_heads":    8 if args.d_model == 256 else max(2, args.d_model // 32),
            "d_ff":       1024 if args.d_model == 256 else args.d_model * 4,
            "N_enc":      args.n_enc_layers,
            "d_act":      32, "d_cycle": 32, "dropout": 0.1,
            "n_activity_classes": 14, "n_copresence": 9, "n_slots": 48,
            "n_aux": feat_cfg.get("n_aux", 11), "d_cond": d_cond,
            "mdlm_mask_schedule": args.mdlm_mask_schedule,
            "mdlm_denoise_steps": args.mdlm_denoise_steps,
        }

    # ── Device ───────────────────────────────────────────────────────────
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"  Device: {device}  WEIGHT_MODE={WEIGHT_MODE}  USE_PCGRAD={USE_PCGRAD}  "
          f"LAMBDA_DIV={LAMBDA_DIV}  mask_schedule={args.mdlm_mask_schedule}  "
          f"denoise_steps={args.mdlm_denoise_steps}")

    # ── Data ─────────────────────────────────────────────────────────────
    print("[1/4] Loading datasets and pairs...")
    train_data  = torch.load(os.path.join(args.data_dir, "step4_train.pt"),  map_location="cpu", weights_only=False)
    val_data    = torch.load(os.path.join(args.data_dir, "step4_val.pt"),    map_location="cpu", weights_only=False)
    train_pairs = torch.load(os.path.join(args.data_dir, "training_pairs.pt"), map_location="cpu", weights_only=False)

    train_dataset = Step4DatasetMDLM(train_data, train_pairs)
    print(f"  Train pairs: {len(train_dataset)} | Val respondents: {len(val_data['act_seq'])}")

    # Activity CE class weights (inverse-sqrt-frequency, same boosts as 04D)
    freqs = np.array(feat_cfg.get("act_class_freqs", [1.0] * 14), dtype=float)
    freqs = np.maximum(freqs, 1e-6)
    cw = 1.0 / np.sqrt(freqs); cw = cw / cw.mean()
    if ACTIVITY_BOOSTS:
        cw[0] *= 5.0; cw[12] *= 3.0; cw[8] *= 2.0
    act_class_weights = torch.tensor(cw, dtype=torch.float32, device=device)

    home_pw = torch.tensor([feat_cfg.get("home_pos_weight", 1.0)], dtype=torch.float32, device=device)
    _wpw    = float(WORK_POS_WEIGHT) if WORK_POS_WEIGHT else feat_cfg.get("work_pos_weight", 1.0)
    work_pw = torch.tensor([_wpw], dtype=torch.float32, device=device)

    if COP_POS_WEIGHT > 0:
        _names = feat_cfg.get("cop_col_names", [])
        _cpw   = feat_cfg.get("cop_pos_weights", {})
        _vec   = [float(_cpw.get(n, 1.0)) * COP_POS_WEIGHT for n in _names]
        cop_pos_weight = torch.tensor(_vec, dtype=torch.float32, device=device)
    else:
        cop_pos_weight = None

    src_strata     = train_data["obs_strata"][train_pairs["src_idx"]].numpy()
    strata_counts  = np.bincount(src_strata, minlength=4)
    sample_weights = np.array([1.0 / max(strata_counts[s], 1) for s in src_strata], dtype=np.float32)
    sampler        = WeightedRandomSampler(weights=sample_weights, num_samples=len(train_dataset), replacement=True)
    train_loader   = DataLoader(
        train_dataset, batch_size=args.batch_size, sampler=sampler,
        num_workers=0, pin_memory=(device.type == "cuda"),
    )

    # ── Model ─────────────────────────────────────────────────────────────
    print("[2/4] Building MDLM model...")
    model = MDLMOcc2Split(model_config).to(device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"  Parameters: {total_params:,}")

    # ── Loss weighting ───────────────────────────────────────────────────
    if WEIGHT_MODE == "uw":
        weighter = UncertaintyWeighting(TASKS).to(device)
        weight_params = list(weighter.parameters())
    elif WEIGHT_MODE == "slaw":
        weighter = SLAWWeighting(TASKS, beta=SLAW_BETA)
        weight_params = []
    else:
        weighter = EqualWeighting(TASKS)
        weight_params = []

    optimizer = torch.optim.AdamW(
        list(model.parameters()) + weight_params, lr=args.lr, weight_decay=1e-2,
    )
    plateau = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.95, patience=5)
    scaler  = torch.amp.GradScaler("cuda") if (args.fp16 and device.type == "cuda") else None
    pcgrad  = PCGrad(model.parameters()) if USE_PCGRAD else None

    # ── Resume ───────────────────────────────────────────────────────────
    start_epoch    = 0
    best_val_score = float("inf")
    patience_ctr   = 0
    if args.resume and os.path.isfile(args.resume):
        ck = torch.load(args.resume, map_location=device, weights_only=False)
        model.load_state_dict(ck["model_state"])
        optimizer.load_state_dict(ck["optimizer_state"])
        if WEIGHT_MODE == "uw" and ck.get("weighter_state") is not None:
            weighter.load_state_dict(ck["weighter_state"])
        start_epoch    = ck["epoch"] + 1
        best_val_score = ck.get("best_val_score", float("inf"))
        print(f"  Resumed from epoch {start_epoch}, best_val_score={best_val_score:.4f}")

    log_path   = os.path.join(out_dir, "step4_mdlm_training_log.csv")
    log_fields = ["epoch", "train_loss", "act_loss", "home_loss", "work_loss",
                  "cop_loss", "div_loss", "sigma_act", "sigma_home", "sigma_work",
                  "sigma_cop", "val_js", "home_gap", "work_gap", "val_score",
                  "lr", "grad_norm", "elapsed_s"]
    if start_epoch == 0:
        with open(log_path, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=log_fields).writeheader()

    clip_norm = 25.0
    print("[3/4] Training MDLM...")

    for epoch in range(start_epoch, args.max_epochs):
        model.train()
        if WEIGHT_MODE == "uw":
            weighter.train()
        t0 = time.time()
        train_dataset.resample()

        accum     = {k: 0.0 for k in ["total", "act", "home", "work", "cop", "div"]}
        grad_norms = []

        for batch in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            optimizer.zero_grad()

            # ── Sample mask ratio and apply masking ─────────────────────────
            mask_ratio = float(torch.rand(1).item())
            mask_ratio = max(mask_ratio, 1e-4)   # avoid exactly zero
            noisy_seq, mask_pos = apply_mask(batch["dec_act_seq"], mask_ratio)
            batch["noisy_act_seq"] = noisy_seq
            batch["mask_pos"]      = mask_pos

            if scaler is not None:
                with torch.amp.autocast("cuda"):
                    out  = model(batch)
                    comp = component_losses_mdlm(out, batch, act_class_weights, home_pw, work_pw, cop_pos_weight)
                    div  = diversity_loss(out, batch)
                    total_w, per_task = weighter.weighted(comp)
                    total = total_w + LAMBDA_DIV * div
                scaler.scale(total).backward()
                scaler.unscale_(optimizer)
                grad_norm = nn.utils.clip_grad_norm_(model.parameters(), clip_norm).item()
                scaler.step(optimizer)
                scaler.update()
            else:
                out  = model(batch)
                comp = component_losses_mdlm(out, batch, act_class_weights, home_pw, work_pw, cop_pos_weight)
                div  = diversity_loss(out, batch)
                total_w, per_task = weighter.weighted(comp)
                total = total_w + LAMBDA_DIV * div

                if pcgrad is not None:
                    pcgrad.backward([per_task[t] for t in TASKS], retain_all=True)
                    extra = LAMBDA_DIV * div
                    div_grads = torch.autograd.grad(extra, pcgrad.params, allow_unused=True,
                                                    retain_graph=bool(weight_params))
                    for p, dg in zip(pcgrad.params, div_grads):
                        if dg is not None:
                            p.grad = (p.grad if p.grad is not None else torch.zeros_like(p)) + dg
                    if weight_params:
                        lv_grads = torch.autograd.grad(total, weight_params, allow_unused=True)
                        for p, lg in zip(weight_params, lv_grads):
                            if lg is not None:
                                p.grad = lg.detach().clone()
                else:
                    total.backward()

                grad_norm = nn.utils.clip_grad_norm_(model.parameters(), clip_norm).item()
                optimizer.step()

            accum["total"] += float(total.item())
            accum["act"]   += float(comp["act"].item())
            accum["home"]  += float(comp["home"].item())
            accum["work"]  += float(comp["work"].item())
            accum["cop"]   += float(comp["cop"].item())
            accum["div"]   += float(div.item())
            grad_norms.append(grad_norm)

        nb  = len(train_loader)
        avg = {k: v / nb for k, v in accum.items()}
        sig = weighter.sigmas()
        cur_lr = optimizer.param_groups[0]["lr"]

        val = validate(model, val_data, device,
                       n_steps=args.mdlm_denoise_steps,
                       schedule=args.mdlm_mask_schedule)
        in_warmup = (epoch + 1) <= args.warmup_epochs
        if not in_warmup:
            plateau.step(val["val_score"] if not math.isnan(val["val_score"]) else avg["total"])
        elapsed = time.time() - t0

        print(f"Epoch {epoch+1:3d}/{args.max_epochs}: loss={avg['total']:.4f}  "
              f"act={avg['act']:.4f} home={avg['home']:.4f} work={avg['work']:.4f} "
              f"cop={avg['cop']:.4f} div={avg['div']:.4f} | "
              f"sig(a/h/w/c)={sig['act']:.2f}/{sig['home']:.2f}/{sig['work']:.2f}/{sig['cop']:.2f} | "
              f"val_JS={val['val_js']:.4f} home_gap={val['home_gap']:.4f} "
              f"work_gap={val['work_gap']:.4f} score={val['val_score']:.4f} ({elapsed:.0f}s)")

        with open(log_path, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=log_fields).writerow({
                "epoch": epoch + 1, "train_loss": round(avg["total"], 6),
                "act_loss": round(avg["act"], 6), "home_loss": round(avg["home"], 6),
                "work_loss": round(avg["work"], 6), "cop_loss": round(avg["cop"], 6),
                "div_loss": round(avg["div"], 6),
                "sigma_act": round(sig["act"], 6), "sigma_home": round(sig["home"], 6),
                "sigma_work": round(sig["work"], 6), "sigma_cop": round(sig["cop"], 6),
                "val_js": round(val["val_js"], 6), "home_gap": round(val["home_gap"], 6),
                "work_gap": round(val["work_gap"], 6), "val_score": round(val["val_score"], 6),
                "lr": round(cur_lr, 8), "grad_norm": round(float(np.mean(grad_norms)), 4),
                "elapsed_s": round(elapsed, 1),
            })

        # Save last checkpoint (for resume)
        torch.save({
            "epoch": epoch, "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "weighter_state": weighter.state_dict() if WEIGHT_MODE == "uw" else None,
            "best_val_score": best_val_score, "model_config": model_config,
        }, os.path.join(ckpt_dir, "last_checkpoint.pt"))

        score = val["val_score"]
        if math.isnan(score):
            score = avg["total"]
        if in_warmup:
            torch.save({
                "epoch": epoch, "model_state": model.state_dict(),
                "model_config": model_config,
                "val_js": val["val_js"], "home_gap": val["home_gap"],
                "work_gap": val["work_gap"], "val_score": val["val_score"],
            }, os.path.join(ckpt_dir, "best_model.pt"))
            print(f"  [warmup {epoch+1}/{args.warmup_epochs}] best-tracking deferred")
        elif score < best_val_score:
            best_val_score = score
            patience_ctr   = 0
            torch.save({
                "epoch": epoch, "model_state": model.state_dict(),
                "model_config": model_config,
                "val_js": val["val_js"], "home_gap": val["home_gap"],
                "work_gap": val["work_gap"], "val_score": val["val_score"],
            }, os.path.join(ckpt_dir, "best_model.pt"))
            print(f"  NEW BEST (score={best_val_score:.4f})")
        else:
            patience_ctr += 1
            if patience_ctr >= args.patience:
                print(f"  Early stopping at epoch {epoch+1}")
                break

    print(f"\n[4/4] Training complete. Best val_score={best_val_score:.4f}")
    print(f"  Best checkpoint: {os.path.join(ckpt_dir, 'best_model.pt')}")
    print(f"  Training log:    {log_path}")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir",       default=None)
    p.add_argument("--output_dir",     default=None)
    p.add_argument("--checkpoint_dir", default=None)
    p.add_argument("--batch_size",     type=int,   default=256)
    p.add_argument("--max_epochs",     type=int,   default=100)
    p.add_argument("--patience",       type=int,   default=15)
    p.add_argument("--warmup-epochs",  dest="warmup_epochs", type=int, default=20)
    p.add_argument("--lr",             type=float, default=5e-5)
    p.add_argument("--d_model",        type=int,   default=256)
    p.add_argument("--n_enc_layers",   type=int,   default=6)
    p.add_argument("--fp16",           action="store_true")
    p.add_argument("--resume",         default=None)
    p.add_argument("--sample",         action="store_true")
    # MDLM-specific
    p.add_argument("--mdlm_mask_schedule", default="cosine",
                   choices=["linear", "cosine"],
                   help="Masking schedule for the MDLM denoise steps (default: cosine)")
    p.add_argument("--mdlm_denoise_steps", type=int, default=16,
                   help="Number of denoising steps at inference (default: 16)")
    return p.parse_args()




if __name__ == "__main__":
    args = parse_args()
    if args.data_dir is None:
        args.data_dir = OUTPUT_DIR
    if args.output_dir is None:
        args.output_dir = OUTPUT_DIR
    if args.checkpoint_dir is None:
        args.checkpoint_dir = os.path.join(OUTPUT_DIR, "checkpoints_mdlm")

    print("=" * 60)
    print(f"Step 4D-MDLM (Leg-2) — Training  {'[SAMPLE MODE]' if args.sample else ''}")
    print("=" * 60)
    print(f"  data_dir:       {args.data_dir}")
    print(f"  output_dir:     {args.output_dir}")
    print(f"  checkpoint_dir: {args.checkpoint_dir}")
    train(args)
