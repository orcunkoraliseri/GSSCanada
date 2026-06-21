# -*- coding: utf-8 -*-
"""
3rdJ_04D_train_2split.py — Step 4D (Leg-2): Two-Channel J3 Training Loop.

Ports the J-series training branch from 2J_docs_occ_nTemp/04D_train.py and adds
the mandatory multi-head training machinery for the new AT_WORK head:

  1. COMPONENT LOSSES (4 tasks: act, home, work, cop)
       act  = cross_entropy(act_logits, dec_act_seq) with optional inverse-sqrt-
              frequency class weights from act_class_freqs.
       home = BCEWithLogits(home_logits, dec_aux[...,0]) with home_pos_weight.
       work = BCEWithLogits(work_logits, dec_aux[...,1]) with work_pos_weight,
              MASKED by dec_work_avail.                       [Leg-2 NEW]
       cop  = BCEWithLogits(cop_logits, dec_aux[...,2:11]) MASKED by dec_cop_avail,
              colleagues channel (idx 8) zeroed for CYCLE_YEAR < 2015.

  2. DYNAMIC LOSS WEIGHTING (WEIGHT_MODE, default 'uw')
       'uw'    homoscedastic uncertainty weighting (Kendall & Gal 2018) — one
               learnable log_var per task; total = Σ exp(-lv_t)*L_t + lv_t.
       'slaw'  scaled-loss-average-weighting (running-average loss scaling).
       'equal' fixed equal weights (fallback).

  3. PCGRAD gradient surgery (USE_PCGRAD=1 default) — per-task grads, project
       away conflicting (negative-cosine) components pairwise in random order.
       Applied on the UW-weighted per-task losses (kept simple & documented).

  4. DIVERSITY loss (LAMBDA_DIV default 0.1) — per-(cycle x stratum) marginal
       matching on predicted per-slot presence curves for BOTH home and work.

Checkpoint contract (checkpoints/best_model.pt):
    {epoch, model_state, model_config, val_js, home_gap, work_gap, val_score}
    val_score = val_js + 0.5 * (home_gap + work_gap) / 2
last_checkpoint.pt also saved each epoch (with optimizer state) for resume.

Usage:
    py -3 -X utf8 3rdJ_04D_train_2split.py --sample
    py -3 -X utf8 3rdJ_04D_train_2split.py --fp16   (cluster GPU, full mode)
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
model_mod = importlib.import_module("3rdJ_04B_model_2split")
JSeriesHybrid2Split = model_mod.JSeriesHybrid2Split

# ── Platform-detection path block (mirrors Step3 / 04A / 04C) ─────────────────
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
OUTPUT_DIR = os.path.join(_LEG2_BASE, "Step4_docs", "outputs_step4")

# ── Multi-head machinery toggles (all ON by default; each behind env var) ─────
WEIGHT_MODE  = os.environ.get("WEIGHT_MODE", "uw").lower()   # 'uw' | 'slaw' | 'equal'
USE_PCGRAD   = os.environ.get("USE_PCGRAD", "1") == "1"
LAMBDA_DIV   = float(os.environ.get("LAMBDA_DIV", "0.1"))
SLAW_BETA    = float(os.environ.get("SLAW_BETA", "0.9"))     # running-avg decay
ACTIVITY_BOOSTS = os.environ.get("ACTIVITY_BOOSTS", "1") != "0"
# HPT sweep overrides (None / 0 → keep baseline behaviour from config) ─────────
WORK_POS_WEIGHT = os.environ.get("WORK_POS_WEIGHT")          # None → use config value
COP_POS_WEIGHT  = float(os.environ.get("COP_POS_WEIGHT", "0"))  # 0 → off (Leg-1 default)

TASKS = ["act", "home", "work", "cop"]
COLLEAGUES_IDX = 8

# CYCLE_YEAR -> index (matches 04A CYCLE_MAP)
CYCLE_MAP = {2005: 0, 2010: 1, 2015: 2, 2022: 3}

# ── R11: per-person latent flags (default OFF — does NOT alter existing behaviour) ──
# These come from argparse (--r11_person_latent / --r11_latent_dim / --r11_mono_weight).
# When all are at defaults (False / 8 / 0.0), R7 and earlier variants are unaffected:
#   no r11_latent key in batch, model config r11_person_latent=False, mono_weight=0.
_R11_PERSON_LATENT = False   # overridden by parse_args() before train() is called
_R11_LATENT_DIM    = 8
_R11_MONO_WEIGHT   = 0.0


# ── Dataset ──────────────────────────────────────────────────────────────────

class Step4Dataset2Split(Dataset):
    """
    Per training pair: encoder = source respondent's tensors (observed day);
    decoder target = a sampled 1-of-K neighbour's tensors (resampled each epoch).
    Provides dec_act_seq, dec_aux_seq, dec_cop_avail, dec_work_avail, tgt_strata.

    R11 mode (r11_person_latent=True): a pre-sampled per-person latent is stored in
    self._r11_latents (n, d_latent) and added to every __getitem__ under key
    'r11_latent'. Latents are re-drawn from N(0,1) each epoch in resample().
    When r11_person_latent=False (default), self._r11_latents is None and no key
    is added — the batch dict is byte-identical to the pre-R11 case.
    """

    def __init__(self, data: dict, pairs: dict, r11_person_latent: bool = False,
                 r11_latent_dim: int = 8):
        self.data = data
        self.pairs = pairs
        self.r11_person_latent = r11_person_latent
        self.r11_latent_dim    = r11_latent_dim
        self._sampled_tgt   = None
        self._r11_latents   = None
        self.resample()

    def resample(self):
        n_pairs = len(self.pairs["src_idx"])
        K = self.pairs["tgt_k_indices"].shape[1]
        k_choice = torch.randint(0, K, (n_pairs,))
        self._sampled_tgt = self.pairs["tgt_k_indices"][torch.arange(n_pairs), k_choice]

        # R11: draw fresh per-pair latents from N(0,1) each epoch.
        # One latent per SOURCE respondent (occ-level coupling): two pairs with the
        # same src get the same latent regardless of which tgt stratum is sampled.
        # We store one latent per PAIR (not per unique src_idx) — simpler indexing,
        # since pairs with the same src will naturally receive the same work-level
        # signal via the encoder's memory representation, and the latent adds a
        # stochastic EXTRA signal that is shared for the same pair this epoch.
        if self.r11_person_latent:
            self._r11_latents = torch.randn(n_pairs, self.r11_latent_dim)
        else:
            self._r11_latents = None

    def __len__(self):
        return len(self.pairs["src_idx"])

    def __getitem__(self, i):
        s = self.pairs["src_idx"][i].item()
        t = self._sampled_tgt[i].item()
        item = {
            # Encoder: observed diary of source respondent
            "act_seq":    self.data["act_seq"][s],
            "aux_seq":    self.data["aux_seq"][s],
            "cond_vec":   self.data["cond_vec"][s],
            "cycle_idx":  self.data["cycle_idx"][s],
            "cycle_year": self.data["cycle_year"][s],
            "obs_strata": self.data["obs_strata"][s],
            # Decoder target: sampled neighbour's diary (act + aux + masks)
            "dec_act_seq":   self.data["act_seq"][t],
            "dec_aux_seq":   self.data["aux_seq"][t],
            "dec_cop_avail": self.data["cop_avail"][t],
            "dec_work_avail": self.data["work_avail"][t],
            "tgt_strata":    self.data["obs_strata"][t],
        }
        # R11: add per-pair latent when enabled; absent otherwise (pre-R11 compat)
        if self._r11_latents is not None:
            item["r11_latent"] = self._r11_latents[i]
        return item


# ── Component losses (4 tasks) ────────────────────────────────────────────────

def component_losses(output: dict, batch: dict,
                     act_weights=None, home_pos_weight=None,
                     work_pos_weight=None, cop_pos_weight=None) -> dict:
    """Returns dict task -> scalar loss tensor (act, home, work, cop)."""
    act_logits  = output["act_logits"]   # (B,48,14)
    home_logits = output["home_logits"]  # (B,48)
    work_logits = output["work_logits"]  # (B,48)
    cop_logits  = output["cop_logits"]   # (B,48,9)

    act_tgt  = batch["dec_act_seq"]                       # (B,48)
    home_tgt = batch["dec_aux_seq"][:, :, 0].float()     # (B,48)
    work_tgt = batch["dec_aux_seq"][:, :, 1].float()     # (B,48)  [Leg-2]
    cop_tgt  = batch["dec_aux_seq"][:, :, 2:]            # (B,48,9)

    B, T, C = act_logits.shape

    # Activity: weighted cross-entropy
    act_loss = F.cross_entropy(
        act_logits.reshape(B * T, C), act_tgt.reshape(B * T), weight=act_weights,
    )

    # AT_HOME: BCE (always available)
    home_loss = F.binary_cross_entropy_with_logits(
        home_logits, home_tgt, pos_weight=home_pos_weight,
    )

    # AT_WORK: BCE masked by work_avail  [Leg-2 NEW]
    work_avail = batch["dec_work_avail"].float()         # (B,48)
    work_raw = F.binary_cross_entropy_with_logits(
        work_logits, work_tgt, pos_weight=work_pos_weight, reduction="none",
    )
    work_loss = (work_raw * work_avail).sum() / work_avail.sum().clamp(min=1.0)

    # Co-presence: BCE masked by availability; colleagues zeroed pre-2015
    if cop_pos_weight is not None:
        cop_raw = F.binary_cross_entropy_with_logits(
            cop_logits, cop_tgt, pos_weight=cop_pos_weight.view(1, 1, -1), reduction="none",
        )
    else:
        cop_raw = F.binary_cross_entropy_with_logits(cop_logits, cop_tgt, reduction="none")
    cop_avail = batch["dec_cop_avail"].float()           # (B,48,9)
    colleagues_mask = (batch["cycle_year"] >= 2015).float()  # (B,)
    cop_masked = cop_raw * cop_avail
    cop_masked[:, :, COLLEAGUES_IDX] = cop_masked[:, :, COLLEAGUES_IDX] * colleagues_mask.unsqueeze(-1)
    cop_loss = cop_masked.sum() / cop_avail.sum().clamp(min=1.0)

    return {"act": act_loss, "home": home_loss, "work": work_loss, "cop": cop_loss}


def diversity_loss(output: dict, batch: dict) -> torch.Tensor:
    """
    Per-(cycle x stratum) marginal matching on predicted per-slot presence curves
    for BOTH home and work. MSE between batch-mean predicted sigmoid curve and
    batch-mean target curve, computed within each (cycle, stratum) group present.
    """
    home_p = torch.sigmoid(output["home_logits"])        # (B,48)
    work_p = torch.sigmoid(output["work_logits"])        # (B,48)
    home_t = batch["dec_aux_seq"][:, :, 0].float()
    work_t = batch["dec_aux_seq"][:, :, 1].float()
    work_avail = batch["dec_work_avail"].float()

    key = batch["tgt_strata"].long() * 4 + batch["cycle_idx"].long()  # (B,)
    losses = []
    for g in key.unique():
        m = key == g
        # home: simple group-mean curve match
        losses.append(F.mse_loss(home_p[m].mean(0), home_t[m].mean(0)))
        # work: availability-weighted group-mean curve match
        wa = work_avail[m]
        denom = wa.sum(0).clamp(min=1.0)
        wp = (work_p[m] * wa).sum(0) / denom
        wt = (work_t[m] * wa).sum(0) / denom
        losses.append(F.mse_loss(wp, wt))
    if not losses:
        return torch.tensor(0.0, device=home_p.device)
    return torch.stack(losses).mean()


def r11_monotonic_penalty(model, batch: dict, device, cap: int = 32) -> torch.Tensor:
    """
    R11 soft monotonic ordering penalty: per-person weekday work-rate >= Sat >= Sun.

    Strategy: teacher-forced (not AR rollout) so cost is O(1) forward passes.
    For each of the 3 strata in {1=wkdy, 2=Sat, 3=Sun}, run Arm-1 teacher-forced
    decode on the SAME (src, r11_latent, cond) but with the strata one-hot forced
    to that target value. Compute mean sigmoid(work_logit) over slots -> wrate_s.
    Penalty = relu(wrate_Sat - wrate_wkdy) + relu(wrate_Sun - wrate_Sat).

    This is computed on the CURRENT batch (teacher-forcing on tgt seq is fine here
    because we only need a work-intensity signal, not a calibrated probability).
    When batch["r11_latent"] is absent (r11_person_latent=False), this function
    must never be called (guard in train loop).

    NOTE: only Arm-1 (activity) logits are used here; the work_logit from Arm-2
    is then derived from the detached activity probs — but for the ordering penalty
    we want the direct work signal from the ACTIVITY head (work category = class 0):
    wrate = mean probability that the model assigns to activity class 0 (Work).
    This is cleaner (no Arm-2 rollout) and directly reflects the work-ordering intent.
    """
    # MEMORY (2026-06-18 OOM fix): this penalty retains THREE teacher-forced decode
    # graphs at once (one per day-type) on top of the live main-forward graph (it is
    # computed before backward), plus a re-encode. At full batch that OOM'd the 15 GiB
    # pg card (969261, exit 13). We bound it two ways: (1) sub-batch to `cap` rows —
    # the ordering signal is a population mean, so a representative slice gives the
    # same gradient direction at a fraction of the memory; (2) compute the shared
    # encoder under no_grad — the penalty is meant to shape the per-person latent +
    # decoder day-type expression, not the shared feature extractor.
    full_B = batch["dec_act_seq"].shape[0]
    B = min(int(cap), full_B)
    sl = slice(0, B)
    dec_act_seq = batch["dec_act_seq"][sl]
    act_seq     = batch["act_seq"][sl]
    aux_seq     = batch["aux_seq"][sl]
    cond_vec    = batch["cond_vec"][sl]
    cycle_idx   = batch["cycle_idx"][sl]
    r11_latent  = batch.get("r11_latent", None)
    if r11_latent is not None:
        r11_latent = r11_latent[sl]

    # Build strata one-hot tensors for the 3 day-types, broadcast to the sub-batch.
    strata_vals = [
        torch.ones(B, dtype=torch.long, device=device),   # 1 = weekday
        torch.full((B,), 2, dtype=torch.long, device=device),  # 2 = Saturday
        torch.full((B,), 3, dtype=torch.long, device=device),  # 3 = Sunday
    ]

    with torch.no_grad():
        memory = model._encode(act_seq, aux_seq, cond_vec, cycle_idx)

    wrates = []
    for s_tensor in strata_vals:
        act_logits = model._arm1_decode_tf(
            dec_act_seq, s_tensor,
            memory, cond_vec, cycle_idx,
            r11_latent=r11_latent,
        )  # (B, 48, n_act)
        # Work probability: softmax -> class 0 -> mean over slots and batch
        work_probs = torch.softmax(act_logits, dim=-1)[:, :, 0]   # (B, 48)
        wrates.append(work_probs.mean())   # scalar

    wrate_wkdy, wrate_sat, wrate_sun = wrates
    penalty = (
        torch.relu(wrate_sat  - wrate_wkdy) +
        torch.relu(wrate_sun  - wrate_sat)
    )
    return penalty


# ── Loss weighting strategies ─────────────────────────────────────────────────

class UncertaintyWeighting(nn.Module):
    """Homoscedastic uncertainty weighting (Kendall & Gal 2018)."""
    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks
        self.log_var = nn.ParameterDict(
            {t: nn.Parameter(torch.zeros(())) for t in tasks}
        )

    def weighted(self, comp: dict):
        """Returns (total, per_task_weighted_dict). total = Σ exp(-lv)*L + lv."""
        per_task = {}
        total = 0.0
        for t in self.tasks:
            lv = self.log_var[t]
            per_task[t] = torch.exp(-lv) * comp[t] + lv
            total = total + per_task[t]
        return total, per_task

    def sigmas(self):
        return {t: float(torch.exp(0.5 * self.log_var[t]).item()) for t in self.tasks}


class SLAWWeighting:
    """Scaled Loss Average Weighting — running-average loss scaling (no params)."""
    def __init__(self, tasks, beta=0.9):
        self.tasks = tasks
        self.beta = beta
        self.run = {t: None for t in tasks}

    def weighted(self, comp: dict):
        per_task = {}
        total = 0.0
        for t in self.tasks:
            lv = float(comp[t].detach().item())
            self.run[t] = lv if self.run[t] is None else self.beta * self.run[t] + (1 - self.beta) * lv
            scale = 1.0 / max(self.run[t], 1e-6)
            per_task[t] = scale * comp[t]
            total = total + per_task[t]
        return total, per_task

    def sigmas(self):
        # report 1/scale-equivalent sigma analog for logging continuity
        return {t: float(self.run[t]) if self.run[t] is not None else 1.0 for t in self.tasks}


class EqualWeighting:
    def __init__(self, tasks):
        self.tasks = tasks

    def weighted(self, comp: dict):
        per_task = {t: comp[t] for t in self.tasks}
        total = sum(per_task.values())
        return total, per_task

    def sigmas(self):
        return {t: 1.0 for t in self.tasks}


# ── PCGrad gradient surgery ───────────────────────────────────────────────────

class PCGrad:
    """
    Projecting-Conflicting-Gradients (Yu et al. 2020).

    Given a list of per-task scalar losses, compute each task's gradient over the
    shared parameters, then for each task project away components that conflict
    (negative cosine) with other tasks' gradients, in random pairwise order.
    The de-conflicted gradients are summed and written to each param's .grad.
    Applied here on the (UW-weighted) per-task losses.
    """

    def __init__(self, params):
        self.params = [p for p in params if p.requires_grad]

    def _flat_grad(self, loss, retain):
        grads = torch.autograd.grad(loss, self.params, retain_graph=retain,
                                    allow_unused=True)
        flat, shapes = [], []
        for g, p in zip(grads, self.params):
            if g is None:
                g = torch.zeros_like(p)
            shapes.append(g.shape)
            flat.append(g.reshape(-1))
        return torch.cat(flat), shapes

    def _unflatten(self, flat, shapes):
        out, idx = [], 0
        for sh in shapes:
            n = int(np.prod(sh)) if len(sh) else 1
            out.append(flat[idx:idx + n].reshape(sh))
            idx += n
        return out

    def backward(self, task_losses: list, retain_all: bool = False):
        grads, shapes = [], None
        for i, loss in enumerate(task_losses):
            retain = retain_all or (i < len(task_losses) - 1)
            g, shapes = self._flat_grad(loss, retain=retain)
            grads.append(g)

        # Project away conflicts, pairwise, in random order per task.
        proj = [g.clone() for g in grads]
        n = len(grads)
        for i in range(n):
            order = list(range(n))
            np.random.shuffle(order)
            for j in order:
                if i == j:
                    continue
                gj = grads[j]
                dot = torch.dot(proj[i], gj)
                if dot < 0:
                    proj[i] = proj[i] - (dot / (gj.norm() ** 2 + 1e-12)) * gj
        merged = torch.stack(proj, dim=0).sum(dim=0)

        # Write into .grad
        chunks = self._unflatten(merged, shapes)
        for p, g in zip(self.params, chunks):
            p.grad = g.detach().clone()


# ── Validation ───────────────────────────────────────────────────────────────

def js_divergence(p, q):
    p = np.clip(p / (p.sum() + 1e-12), 1e-12, None)
    q = np.clip(q / (q.sum() + 1e-12), 1e-12, None)
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m)))


@torch.no_grad()
def validate(model, val_data, device, n_sample=2000):
    """Argmax generation on a sample; per-stratum activity JS + home/work gaps."""
    model.eval()
    n_val = len(val_data["act_seq"])
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
            ref_work[(int(cy), int(s))] = (
                float((work_np[mask] * wa).sum() / max(wa.sum(), 1.0))
            )

    rng = np.random.default_rng(42)
    src_idx = rng.choice(n_val, size=n_sample, replace=False)

    gen_act_by  = {s: [] for s in [1, 2, 3]}
    gen_home_by = {s: [] for s in [1, 2, 3]}
    gen_work_by = {s: [] for s in [1, 2, 3]}
    gen_cy_by   = {s: [] for s in [1, 2, 3]}

    batch_sz = 256
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

        g_act, g_home, g_work, _, _ = model.generate(
            act_t, aux_t, cond_t, cidx_t, strat, temperature=0.0
        )
        g_act = g_act.cpu().numpy(); g_home = g_home.cpu().numpy(); g_work = g_work.cpu().numpy()
        for k, (s_tgt, cy) in enumerate(zip(syn_strata, syn_cy)):
            gen_act_by[s_tgt].append(g_act[k])
            gen_home_by[s_tgt].append(g_home[k])
            gen_work_by[s_tgt].append(g_work[k])
            gen_cy_by[s_tgt].append(cy)

    js_vals, home_gaps, work_gaps = [], [], []
    for s_tgt in [1, 2, 3]:
        if not gen_act_by[s_tgt]:
            continue
        acts = np.array(gen_act_by[s_tgt]); homes = np.array(gen_home_by[s_tgt])
        works = np.array(gen_work_by[s_tgt]); cys = np.array(gen_cy_by[s_tgt])
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

    # ── Config ───────────────────────────────────────────────────────────
    with open(os.path.join(args.data_dir, "step4_feature_config.json")) as f:
        feat_cfg = json.load(f)
    d_cond = feat_cfg["d_cond"]

    # R11 flags (from module-level vars, set by parse_args before train() call)
    r11_on         = args.r11_person_latent
    r11_latent_dim = args.r11_latent_dim
    r11_mono_w     = args.r11_mono_weight

    if args.sample:
        model_config = {
            "model_type": "J3", "d_model": 64, "n_heads": 2, "d_ff": 256,
            "N_enc": 2, "N_dec": 2, "d_act": 16, "d_cycle": 16, "dropout": 0.1,
            "n_activity_classes": 14, "n_copresence": 9, "n_slots": 48,
            "n_aux": feat_cfg.get("n_aux", 11), "d_cond": d_cond,
            # R11 (carried through even in sample mode so the flag is persisted in ckpt)
            "r11_person_latent": r11_on,
            "r11_latent_dim":    r11_latent_dim,
        }
        args.batch_size = 16
        args.max_epochs = 5
        args.patience = 5
        args.warmup_epochs = 1
        args.fp16 = False
    else:
        model_config = {
            "model_type": "J3", "d_model": args.d_model, "n_heads": args.n_heads,
            "d_ff": 1024 if args.d_model == 256 else args.d_model * 4,
            "N_enc": args.n_enc_layers, "N_dec": args.n_dec_layers,
            "d_act": 32, "d_cycle": 32, "dropout": 0.1,
            "n_activity_classes": 14, "n_copresence": 9, "n_slots": 48,
            "n_aux": feat_cfg.get("n_aux", 11), "d_cond": d_cond,
            # R11
            "r11_person_latent": r11_on,
            "r11_latent_dim":    r11_latent_dim,
        }

    # ── Device ───────────────────────────────────────────────────────────
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"  Device: {device}  WEIGHT_MODE={WEIGHT_MODE}  USE_PCGRAD={USE_PCGRAD}  "
          f"LAMBDA_DIV={LAMBDA_DIV}")
    if r11_on:
        print(f"  R11: person_latent=ON  latent_dim={r11_latent_dim}  mono_weight={r11_mono_w}")

    # ── Data ─────────────────────────────────────────────────────────────
    print("[1/4] Loading datasets and pairs...")
    train_data  = torch.load(os.path.join(args.data_dir, "step4_train.pt"), map_location="cpu", weights_only=False)
    val_data    = torch.load(os.path.join(args.data_dir, "step4_val.pt"), map_location="cpu", weights_only=False)
    train_pairs = torch.load(os.path.join(args.data_dir, "training_pairs.pt"), map_location="cpu", weights_only=False)

    train_dataset = Step4Dataset2Split(
        train_data, train_pairs,
        r11_person_latent=r11_on,
        r11_latent_dim=r11_latent_dim,
    )
    print(f"  Train pairs: {len(train_dataset)} | Val respondents: {len(val_data['act_seq'])}")

    # Activity CE class weights (inverse-sqrt-frequency from act_class_freqs)
    freqs = np.array(feat_cfg.get("act_class_freqs", [1.0] * 14), dtype=float)
    freqs = np.maximum(freqs, 1e-6)
    cw = 1.0 / np.sqrt(freqs)
    cw = cw / cw.mean()
    if ACTIVITY_BOOSTS:
        cw[0] *= 5.0    # Work
        cw[12] *= 3.0   # Transit
        cw[8] *= 2.0    # Social
    act_class_weights = torch.tensor(cw, dtype=torch.float32, device=device)

    home_pw = torch.tensor([feat_cfg.get("home_pos_weight", 1.0)], dtype=torch.float32, device=device)
    _wpw = float(WORK_POS_WEIGHT) if WORK_POS_WEIGHT else feat_cfg.get("work_pos_weight", 1.0)
    work_pw = torch.tensor([_wpw], dtype=torch.float32, device=device)
    print(f"  home_pos_weight={home_pw.item():.4f}  work_pos_weight={work_pw.item():.4f}"
          f"{'  [WORK_POS_WEIGHT override]' if WORK_POS_WEIGHT else ''}")
    # Co-presence pos_weight: off by default (Leg-1 COP_POS_WEIGHT=0). When >0, apply the
    # per-channel cop_pos_weights from config (in cop_col_names order) scaled by this
    # factor — up-weights rare co-presence positives to fight head collapse (gate G3).
    if COP_POS_WEIGHT > 0:
        _names = feat_cfg.get("cop_col_names", [])
        _cpw   = feat_cfg.get("cop_pos_weights", {})
        _vec   = [float(_cpw.get(n, 1.0)) * COP_POS_WEIGHT for n in _names]
        cop_pos_weight = torch.tensor(_vec, dtype=torch.float32, device=device)
        print(f"  COP_POS_WEIGHT={COP_POS_WEIGHT}: cop pos_weights ON {[round(v, 2) for v in _vec]}")
    else:
        cop_pos_weight = None

    # WeightedRandomSampler by source stratum inverse-frequency
    src_strata = train_data["obs_strata"][train_pairs["src_idx"]].numpy()
    strata_counts = np.bincount(src_strata, minlength=4)
    sample_weights = np.array([1.0 / max(strata_counts[s], 1) for s in src_strata], dtype=np.float32)
    sampler = WeightedRandomSampler(weights=sample_weights, num_samples=len(train_dataset), replacement=True)
    train_loader = DataLoader(
        train_dataset, batch_size=args.batch_size, sampler=sampler,
        num_workers=0, pin_memory=(device.type == "cuda"),
    )

    # ── Model ────────────────────────────────────────────────────────────
    print("[2/4] Building model...")
    model = JSeriesHybrid2Split(model_config).to(device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"  Parameters: {total_params:,}")

    # ── Loss weighting strategy ──────────────────────────────────────────
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
    scaler = torch.amp.GradScaler("cuda") if (args.fp16 and device.type == "cuda") else None

    # PCGrad operates over shared model params only (not the UW log_vars).
    pcgrad = PCGrad(model.parameters()) if USE_PCGRAD else None

    # ── Resume ───────────────────────────────────────────────────────────
    start_epoch = 0
    best_val_score = float("inf")
    patience_counter = 0
    if args.resume and os.path.isfile(args.resume):
        ck = torch.load(args.resume, map_location=device, weights_only=False)
        model.load_state_dict(ck["model_state"])
        optimizer.load_state_dict(ck["optimizer_state"])
        if WEIGHT_MODE == "uw" and ck.get("weighter_state") is not None:
            weighter.load_state_dict(ck["weighter_state"])
        start_epoch = ck["epoch"] + 1
        best_val_score = ck.get("best_val_score", float("inf"))
        print(f"  Resumed from epoch {start_epoch}, best_val_score={best_val_score:.4f}")

    # ── Training log ─────────────────────────────────────────────────────
    log_path = os.path.join(out_dir, "step4_training_log.csv")
    log_fields = ["epoch", "train_loss", "act_loss", "home_loss", "work_loss",
                  "cop_loss", "div_loss", "mono_loss",
                  "sigma_act", "sigma_home", "sigma_work",
                  "sigma_cop", "val_js", "home_gap", "work_gap", "val_score",
                  "lr", "grad_norm", "elapsed_s"]
    if start_epoch == 0:
        with open(log_path, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=log_fields).writeheader()

    clip_norm = 25.0
    print("[3/4] Training...")

    for epoch in range(start_epoch, args.max_epochs):
        model.train()
        if WEIGHT_MODE == "uw":
            weighter.train()
        t0 = time.time()
        train_dataset.resample()

        accum = {k: 0.0 for k in ["total", "act", "home", "work", "cop", "div", "mono"]}
        grad_norms = []

        for batch in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            optimizer.zero_grad()

            if scaler is not None:
                with torch.amp.autocast("cuda"):
                    out = model(batch)
                    comp = component_losses(out, batch, act_class_weights, home_pw, work_pw, cop_pos_weight)
                    div = diversity_loss(out, batch)
                    total_w, per_task = weighter.weighted(comp)
                    # R11 monotonic penalty (AMP path)
                    if r11_on and r11_mono_w > 0.0 and "r11_latent" in batch:
                        mono = r11_monotonic_penalty(model, batch, device)
                    else:
                        mono = torch.tensor(0.0, device=device)
                    total = total_w + LAMBDA_DIV * div + r11_mono_w * mono
                scaler.scale(total).backward()
                scaler.unscale_(optimizer)
                grad_norm = nn.utils.clip_grad_norm_(model.parameters(), clip_norm).item()
                scaler.step(optimizer)
                scaler.update()
            else:
                out = model(batch)
                comp = component_losses(out, batch, act_class_weights, home_pw, work_pw, cop_pos_weight)
                div = diversity_loss(out, batch)
                total_w, per_task = weighter.weighted(comp)
                # R11 monotonic penalty (non-AMP path)
                if r11_on and r11_mono_w > 0.0 and "r11_latent" in batch:
                    mono = r11_monotonic_penalty(model, batch, device)
                else:
                    mono = torch.tensor(0.0, device=device)
                total = total_w + LAMBDA_DIV * div + r11_mono_w * mono

                if pcgrad is not None:
                    # De-conflict the 4 UW-weighted per-task grads on shared params,
                    # then add the diversity-loss grad and R11 mono-penalty grad on top.
                    # Retain the graph so the diversity + UW-log_var grads can still
                    # be computed below.
                    pcgrad.backward([per_task[t] for t in TASKS], retain_all=True)
                    extra = LAMBDA_DIV * div + r11_mono_w * mono
                    div_grads = torch.autograd.grad(
                        extra, pcgrad.params, allow_unused=True, retain_graph=bool(weight_params),
                    )
                    for p, dg in zip(pcgrad.params, div_grads):
                        if dg is not None:
                            p.grad = (p.grad if p.grad is not None else torch.zeros_like(p)) + dg
                    # UW log_var params get their grad from the plain total (frees graph).
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
            accum["mono"]  += float(mono.item())
            accum["cop"]   += float(comp["cop"].item())
            accum["div"]   += float(div.item())
            grad_norms.append(grad_norm)

        nb = len(train_loader)
        avg = {k: v / nb for k, v in accum.items()}
        sig = weighter.sigmas()
        cur_lr = optimizer.param_groups[0]["lr"]

        val = validate(model, val_data, device)
        in_warmup = (epoch + 1) <= args.warmup_epochs
        # Don't let the degenerate-phase val_score rise drive the LR down before
        # real training has begun; start the plateau scheduler after warmup.
        if not in_warmup:
            plateau.step(val["val_score"] if not math.isnan(val["val_score"]) else avg["total"])
        elapsed = time.time() - t0

        _mono_str = f" mono={avg['mono']:.4f}" if r11_on else ""
        print(f"Epoch {epoch+1:3d}/{args.max_epochs}: loss={avg['total']:.4f}  "
              f"act={avg['act']:.4f} home={avg['home']:.4f} work={avg['work']:.4f} "
              f"cop={avg['cop']:.4f} div={avg['div']:.4f}{_mono_str} | "
              f"sig(a/h/w/c)={sig['act']:.2f}/{sig['home']:.2f}/{sig['work']:.2f}/{sig['cop']:.2f} | "
              f"val_JS={val['val_js']:.4f} home_gap={val['home_gap']:.4f} "
              f"work_gap={val['work_gap']:.4f} score={val['val_score']:.4f} "
              f"({elapsed:.0f}s)")

        with open(log_path, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=log_fields).writerow({
                "epoch": epoch + 1, "train_loss": round(avg["total"], 6),
                "act_loss": round(avg["act"], 6), "home_loss": round(avg["home"], 6),
                "work_loss": round(avg["work"], 6), "cop_loss": round(avg["cop"], 6),
                "div_loss": round(avg["div"], 6), "mono_loss": round(avg["mono"], 6),
                "sigma_act": round(sig["act"], 6), "sigma_home": round(sig["home"], 6),
                "sigma_work": round(sig["work"], 6), "sigma_cop": round(sig["cop"], 6),
                "val_js": round(val["val_js"], 6), "home_gap": round(val["home_gap"], 6),
                "work_gap": round(val["work_gap"], 6), "val_score": round(val["val_score"], 6),
                "lr": round(cur_lr, 8), "grad_norm": round(float(np.mean(grad_norms)), 4),
                "elapsed_s": round(elapsed, 1),
            })

        # last_checkpoint.pt (resume)
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
            # Keep best_model.pt pointed at the latest warmup epoch so a checkpoint
            # always exists, but DON'T lock best_val_score or count patience —
            # otherwise the degenerate epoch-1 'predict-the-marginal' solution wins
            # selection and early-stops the run while it is still converging.
            torch.save({
                "epoch": epoch, "model_state": model.state_dict(),
                "model_config": model_config,
                "val_js": val["val_js"], "home_gap": val["home_gap"],
                "work_gap": val["work_gap"], "val_score": val["val_score"],
            }, os.path.join(ckpt_dir, "best_model.pt"))
            print(f"  [warmup {epoch+1}/{args.warmup_epochs}] best-tracking + early-stop deferred")
        elif score < best_val_score:
            best_val_score = score
            patience_counter = 0
            torch.save({
                "epoch": epoch, "model_state": model.state_dict(),
                "model_config": model_config,
                "val_js": val["val_js"], "home_gap": val["home_gap"],
                "work_gap": val["work_gap"], "val_score": val["val_score"],
            }, os.path.join(ckpt_dir, "best_model.pt"))
            print(f"  NEW BEST (score={best_val_score:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= args.patience:
                print(f"  Early stopping at epoch {epoch+1}")
                break

    print(f"\n[4/4] Training complete. Best val_score={best_val_score:.4f}")
    print(f"  Best checkpoint: {os.path.join(ckpt_dir, 'best_model.pt')}")
    print(f"  Training log:    {log_path}")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", default=None)
    p.add_argument("--output_dir", default=None)
    p.add_argument("--checkpoint_dir", default=None)
    p.add_argument("--batch_size", type=int, default=256)
    p.add_argument("--max_epochs", type=int, default=100)
    p.add_argument("--patience", type=int, default=15)
    p.add_argument("--warmup-epochs", dest="warmup_epochs", type=int, default=20,
                   help="Defer best-checkpoint tracking, early-stop, and LR-plateau "
                        "until past this epoch. The first ~10-20 epochs sit at a "
                        "degenerate 'predict-the-marginal' solution whose val_score "
                        "is artificially low; without this guard it is selected as "
                        "best and triggers premature early stopping.")
    p.add_argument("--lr", type=float, default=5e-5)
    p.add_argument("--d_model", type=int, default=256)
    p.add_argument("--n_heads", type=int, default=8)
    p.add_argument("--n_enc_layers", type=int, default=6)
    p.add_argument("--n_dec_layers", type=int, default=6)
    p.add_argument("--fp16", action="store_true")
    p.add_argument("--resume", default=None)
    p.add_argument("--sample", action="store_true")
    # ── R11: per-person work-intensity latent (default OFF — preserves pre-R11 behaviour) ──
    p.add_argument("--r11_person_latent", action="store_true", default=False,
                   help="Enable R11 per-person work-intensity latent coupling across day-types.")
    p.add_argument("--r11_latent_dim", type=int, default=8,
                   help="Dimensionality of the R11 per-person latent (default 8).")
    p.add_argument("--r11_mono_weight", type=float, default=0.0,
                   help="Weight for R11 soft monotonic ordering penalty wkdy>=Sat>=Sun "
                        "(default 0.0 = disabled). Only active when --r11_person_latent is set.")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.data_dir is None:
        args.data_dir = OUTPUT_DIR
    if args.output_dir is None:
        args.output_dir = OUTPUT_DIR
    if args.checkpoint_dir is None:
        args.checkpoint_dir = os.path.join(OUTPUT_DIR, "checkpoints")

    print("=" * 60)
    print(f"Step 4D (Leg-2) — Training  {'[SAMPLE MODE]' if args.sample else ''}")
    print("=" * 60)
    print(f"  data_dir:       {args.data_dir}")
    print(f"  output_dir:     {args.output_dir}")
    print(f"  checkpoint_dir: {args.checkpoint_dir}")
    print(f"  batch_size={args.batch_size} max_epochs={args.max_epochs} "
          f"warmup={args.warmup_epochs} patience={args.patience} lr={args.lr} fp16={args.fp16}")
    train(args)
