# -*- coding: utf-8 -*-
"""
3rdJ_04D_train_4split.py — Step 4D (Leg-3, four-channel split): Three-GSS-Head
Training Loop — FIXED-ALPHA scalarization + PCGrad + two-phase warm-start
schedule (Deltas C/D/E of 3rdJ_04_augmentationGSS_4split.md, FROZEN).

Ports the J-series training branch from Leg-2's 3rdJ_04D_train_2split.py and
grafts on the AT_RETAIL head training machinery. Leg-2 file is READ-ONLY /
template only — not imported, not modified.

KEY CHANGE vs Leg-2 (Delta D): the Leg-2 dynamic loss weighter (WEIGHT_MODE=
uw/slaw/equal) is REMOVED. Replaced with WEIGHT_MODE=fixed: unitary
scalarization alpha_resid:alpha_work:alpha_retail = 1.0:0.5:0.3 (cop folded
under the resid group, as in Leg-2) + PCGrad pairwise gradient-conflict
projection across the 3-task set + the diversity-preserving loss retained
from Leg-2 (home+work group-mean matching, unchanged / not extended to
retail). Never SLAW / UW / GradNorm / DWA / CAGrad (dr_L3-13).

TWO-PHASE SCHEDULE (Delta E, FROZEN):
    Phase 1 (--phase warmup): 5 epochs, ONLY retail_head trainable (encoder +
        heads 1-2 + cop head frozen), AdamW lr=1e-3, no PCGrad (nothing else
        is being trained), no exclusivity loss.
    Phase 2 (--phase joint):  15 epochs, ALL params trainable, AdamW lr=1e-4,
        PCGrad ON, fixed alpha, exclusivity loss ON (lambda_excl), early
        stopping on the gate-set proxy (patience 10) — NEVER on train loss.

WARM-START: --warm_start <ckpt.pt> loads a checkpoint's weights by NAME+SHAPE
match only (strict=False, manual filtering) — this is intentionally more
defensive than a naive `model.load_state_dict(sd, strict=False)`, because
d_cond/n_aux can legitimately differ between the checkpoint and the current
Leg-3 run (retail is a new aux plane; see the Progress Log ESCALATE note on
2026-07-19 re: the specific Leg-2 checkpoint found at build time). Every
loaded / shape-mismatched / missing key is printed so a human can verify
"only retail_head is new" holds (or see exactly what else diverged).

Loss detail (Delta C):
    retail = BCEWithLogitsLoss(pos_weight=retail_pos_weight), masked by
             dec_retail_avail. NO retail-diary oversampling (double-corrects
             the -ln49 shift, which is INFERENCE-ONLY, never applied here).
    excl   = soft penalty on P(home)+P(work)+P(retail) > 1, masked by
             dec_work_avail & dec_retail_avail. OFF (weight 0) in phase 1,
             ON (--lambda_excl, default 0.05) in phase 2.

Regularization (Delta E): dropout 0.1 lives ONLY in the TransformerEncoder /
CondCrossAttnDecoderLayer sub-modules (self_attn/cross_attn/ffn) per 04B's
existing construction — never wraps the output-head Sequential blocks
(home_head/work_head/retail_head/cop_head/act_head); weight_decay=1e-4
(AdamW); label_smoothing=0 (F.cross_entropy default); no diary augmentation;
scheduled sampling dropped (Arm-1 is teacher-forced during training, as J3
always was — no code change needed for either of these).

Usage:
    py -3 -X utf8 3rdJ_04D_train_4split.py --phase warmup --warm_start <leg2_ckpt> --smoke
    py -3 -X utf8 3rdJ_04D_train_4split.py --phase joint  --warm_start <warmup_ckpt> --smoke
    py -3 -X utf8 3rdJ_04D_train_4split.py --phase warmup --warm_start <leg2_ckpt> --fp16   (cluster GPU)
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
    from sklearn.metrics import average_precision_score, f1_score
except Exception:  # pragma: no cover
    average_precision_score = None
    f1_score = None

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
model_mod = importlib.import_module("3rdJ_04B_model_4split")
JSeriesHybrid4Split = model_mod.JSeriesHybrid4Split

# ── Platform-detection path block (mirrors Leg-3 04A/04C) ────────────────────
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
OUTPUT_DIR = os.path.join(_LEG3_BASE, "Step4_docs", "outputs_step4")

TASK_GROUPS = ["resid", "work", "retail"]   # Delta D: fixed-alpha 3-task set
LAMBDA_DIV = float(os.environ.get("LAMBDA_DIV", "0.1"))   # diversity loss (home+work), retained from Leg-2
COLLEAGUES_IDX = 8   # relative index WITHIN the 9-column cop block (unaffected by retail's insertion)
CYCLE_MAP = {2005: 0, 2010: 1, 2015: 2, 2022: 3}


# ── Dataset ──────────────────────────────────────────────────────────────────

class Step4Dataset4Split(Dataset):
    """
    Per training pair: encoder = source respondent's tensors (observed day);
    decoder target = a sampled 1-of-K neighbour's tensors (resampled each epoch).
    Adds dec_retail_avail (mirrors dec_work_avail) and src_wght_per (the
    per-respondent GSS survey weight, used inside the loss per Delta E).
    """

    def __init__(self, data: dict, pairs: dict):
        self.data = data
        self.pairs = pairs
        self._sampled_tgt = None
        self.resample()

    def resample(self):
        n_pairs = len(self.pairs["src_idx"])
        K = self.pairs["tgt_k_indices"].shape[1]
        k_choice = torch.randint(0, K, (n_pairs,))
        self._sampled_tgt = self.pairs["tgt_k_indices"][torch.arange(n_pairs), k_choice]

    def __len__(self):
        return len(self.pairs["src_idx"])

    def __getitem__(self, i):
        s = self.pairs["src_idx"][i].item()
        t = self._sampled_tgt[i].item()
        return {
            # Encoder: observed diary of source respondent
            "act_seq":       self.data["act_seq"][s],
            "aux_seq":       self.data["aux_seq"][s],
            "cond_vec":      self.data["cond_vec"][s],
            "cycle_idx":     self.data["cycle_idx"][s],
            "cycle_year":    self.data["cycle_year"][s],
            "obs_strata":    self.data["obs_strata"][s],
            "src_wght_per":  self.data["wght_per"][s],
            # Decoder target: sampled neighbour's diary (act + aux + masks)
            "dec_act_seq":     self.data["act_seq"][t],
            "dec_aux_seq":     self.data["aux_seq"][t],
            "dec_cop_avail":   self.data["cop_avail"][t],
            "dec_work_avail":  self.data["work_avail"][t],
            "dec_retail_avail": self.data["retail_avail"][t],
            "tgt_strata":      self.data["obs_strata"][t],
        }


# ── Component losses (5 raw components: act, home, work, retail, cop) ────────

def component_losses(output: dict, batch: dict,
                     act_weights=None, home_pos_weight=None,
                     work_pos_weight=None, retail_pos_weight=None,
                     cop_pos_weight=None, wght_per=None) -> dict:
    """Returns dict task -> scalar loss tensor (act, home, work, retail, cop).
    Every component is weighted per-sample by `wght_per` (B,) — the clipped
    GSS survey weight (Delta E: "WGHT_PER inside the loss, clipped at p99")."""
    act_logits    = output["act_logits"]     # (B,48,14)
    home_logits   = output["home_logits"]    # (B,48)
    work_logits   = output["work_logits"]    # (B,48)
    retail_logits = output["retail_logits"]  # (B,48)  [Leg-3 NEW]
    cop_logits    = output["cop_logits"]     # (B,48,9)

    act_tgt    = batch["dec_act_seq"]                     # (B,48)
    home_tgt   = batch["dec_aux_seq"][:, :, 0].float()   # (B,48)
    work_tgt   = batch["dec_aux_seq"][:, :, 1].float()   # (B,48)
    retail_tgt = batch["dec_aux_seq"][:, :, 2].float()   # (B,48)  [Leg-3 NEW]
    cop_tgt    = batch["dec_aux_seq"][:, :, 3:]          # (B,48,9) — shifted by retail's insertion

    B, T, C = act_logits.shape
    if wght_per is None:
        wght_per = torch.ones(B, device=act_logits.device)
    w1 = wght_per.view(B, 1)             # broadcast over (B,T)
    w2 = wght_per.view(B, 1, 1)          # broadcast over (B,T,9)

    # Activity: weighted CE (inverse-sqrt-frequency class weights), per-sample WGHT_PER
    act_raw = F.cross_entropy(
        act_logits.reshape(B * T, C), act_tgt.reshape(B * T),
        weight=act_weights, reduction="none",
    ).reshape(B, T)
    act_loss = (act_raw * w1).sum() / w1.expand(B, T).sum().clamp(min=1e-6)

    # AT_HOME: BCE (always available), WGHT_PER weighted
    home_raw = F.binary_cross_entropy_with_logits(
        home_logits, home_tgt, pos_weight=home_pos_weight, reduction="none",
    )
    home_loss = (home_raw * w1).sum() / w1.expand(B, T).sum().clamp(min=1e-6)

    # AT_WORK: BCE masked by work_avail, WGHT_PER weighted
    work_avail = batch["dec_work_avail"].float()
    work_raw = F.binary_cross_entropy_with_logits(
        work_logits, work_tgt, pos_weight=work_pos_weight, reduction="none",
    )
    work_denom = (work_avail * w1).sum().clamp(min=1e-6)
    work_loss = (work_raw * work_avail * w1).sum() / work_denom

    # AT_RETAIL: BCE masked by retail_avail, WGHT_PER weighted  [Leg-3 NEW, Delta C]
    # pos_weight=retail_pos_weight (~49-50); NO oversampling anywhere in this pipeline;
    # NO -ln49 shift here — that correction is inference-only (04E).
    retail_avail = batch["dec_retail_avail"].float()
    retail_raw = F.binary_cross_entropy_with_logits(
        retail_logits, retail_tgt, pos_weight=retail_pos_weight, reduction="none",
    )
    retail_denom = (retail_avail * w1).sum().clamp(min=1e-6)
    retail_loss = (retail_raw * retail_avail * w1).sum() / retail_denom

    # Co-presence: BCE masked by availability; colleagues zeroed pre-2015; WGHT_PER weighted
    if cop_pos_weight is not None:
        cop_raw = F.binary_cross_entropy_with_logits(
            cop_logits, cop_tgt, pos_weight=cop_pos_weight.view(1, 1, -1), reduction="none",
        )
    else:
        cop_raw = F.binary_cross_entropy_with_logits(cop_logits, cop_tgt, reduction="none")
    cop_avail = batch["dec_cop_avail"].float()
    colleagues_mask = (batch["cycle_year"] >= 2015).float()
    cop_masked = cop_raw * cop_avail
    cop_masked[:, :, COLLEAGUES_IDX] = cop_masked[:, :, COLLEAGUES_IDX] * colleagues_mask.unsqueeze(-1)
    cop_denom = (cop_avail * w2).sum().clamp(min=1e-6)
    cop_loss = (cop_masked * w2).sum() / cop_denom

    return {"act": act_loss, "home": home_loss, "work": work_loss,
            "retail": retail_loss, "cop": cop_loss}


def diversity_loss(output: dict, batch: dict) -> torch.Tensor:
    """
    Per-(cycle x stratum) marginal matching on predicted per-slot presence
    curves for home AND work — RETAINED FROM LEG-2 UNCHANGED (Delta D: "the
    diversity-preserving loss retained from Leg 2"). NOT extended to retail.
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
        losses.append(F.mse_loss(home_p[m].mean(0), home_t[m].mean(0)))
        wa = work_avail[m]
        denom = wa.sum(0).clamp(min=1.0)
        wp = (work_p[m] * wa).sum(0) / denom
        wt = (work_t[m] * wa).sum(0) / denom
        losses.append(F.mse_loss(wp, wt))
    if not losses:
        return torch.tensor(0.0, device=home_p.device)
    return torch.stack(losses).mean()


def exclusivity_loss(output: dict, batch: dict) -> torch.Tensor:
    """
    [Leg-3 NEW, Delta C/G training-side support] Soft penalty on
    P(home)+P(work)+P(retail) > 1, masked by slots where BOTH work and retail
    are available (home is always available). OFF (weight 0) in phase 1,
    ON (weight=--lambda_excl, default 0.05) in phase 2. Training never sees a
    hard constraint — this only nudges marginals; the exact projection is a
    decode-time-only operation (Delta G, in 04E).
    """
    p_home   = torch.sigmoid(output["home_logits"])
    p_work   = torch.sigmoid(output["work_logits"])
    p_retail = torch.sigmoid(output["retail_logits"])
    excess = F.relu(p_home + p_work + p_retail - 1.0)
    avail = batch["dec_work_avail"].float() * batch["dec_retail_avail"].float()
    denom = avail.sum().clamp(min=1.0)
    return (excess * avail).sum() / denom


# ── PCGrad gradient surgery (ported verbatim from Leg-2; task-agnostic) ──────

class PCGrad:
    """
    Projecting-Conflicting-Gradients (Yu et al. 2020).

    Given a list of per-task scalar losses, compute each task's gradient over
    the given params, then for each task project away components that
    conflict (negative cosine) with other tasks' gradients, pairwise, in
    random order. The de-conflicted gradients are summed and written to each
    param's .grad. Applied here on the ALPHA-weighted per-task losses (the
    fixed-alpha analog of Leg-2's UW-weighted per-task losses).
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

        chunks = self._unflatten(merged, shapes)
        for p, g in zip(self.params, chunks):
            p.grad = g.detach().clone()


# ── Validation (gate-set proxy metrics) ───────────────────────────────────────

def js_divergence(p, q):
    p = np.clip(p / (p.sum() + 1e-12), 1e-12, None)
    q = np.clip(q / (q.sum() + 1e-12), 1e-12, None)
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m)))


@torch.no_grad()
def validate(model, val_data, device, n_sample=2000):
    """
    AR-generation JS/home/work/retail gaps (argmax rollout on a val sample) +
    a teacher-forced retail PR-AUC/F1 (real held-out labels, self-
    reconstruction on the OBSERVED day-type) + a raw (pre-projection, 0.5-
    threshold) ISR training-time diagnostic.

    NOTE: val_score is retained ONLY as a logging curiosity / early-stop
    control signal here (Delta E: "never on training loss") — it is NOT the
    gate-first -> lexicographic selection criterion (that happens later,
    across the 5-seed sweep, in a separate checkpoint-selection step).

    *** CORRECTED 2026-08-06 (V3-H1). THE PARAGRAPH ABOVE IS WRONG AND IS KEPT
    ONLY SO THE CORRECTION HAS SOMETHING TO POINT AT. ***
      (a) val_score is NOT only a logging curiosity here: line 881 selects
          best_model.pt on it (`if score < best_val_score`), and best_model.pt
          is what 04E loads. It IS the selection criterion in this file.
      (b) The "separate checkpoint-selection step ... across the 5-seed sweep"
          DOES NOT EXIST. grep for seed_0 / range(5) / 'for SEED' across
          Step4_docs/*.py and *.sh returns zero hits. Nothing ever compared the
          five seeds under the documented rule.
      (c) The documented rule (3rdJ_04_augmentationGSS_4split.md, "Checkpoint
          selection -- gate-first -> lexicographic") was in any case not
          implementable from this file: two of its five hard-gate families
          (midday error, transitions) are POOL-level and appear in none of the
          21 training-log columns, so its first clause needs inference + rake +
          validator per epoch.
    The shipped pool therefore deviates from the documented rule. That
    deviation, its cost (+0.0218 retail F1 = 0.16 sd), the reason it was not
    re-selected, and the three conditions that reopen it are recorded in the
    doc's own "Checkpoint selection" section -- NOT here, because a comment is
    not a decision record. Comment-only edit: no behaviour change, no
    checkpoint moves, no artefact regenerated.
    """
    model.eval()
    n_val = len(val_data["act_seq"])
    n_sample = min(n_sample, n_val)

    act_np    = val_data["act_seq"].cpu().numpy()
    strata_np = val_data["obs_strata"].cpu().numpy()
    cycle_np  = val_data["cycle_year"].cpu().numpy()
    home_np   = val_data["aux_seq"][:, :, 0].cpu().numpy()
    work_np   = val_data["aux_seq"][:, :, 1].cpu().numpy()
    retail_np = val_data["aux_seq"][:, :, 2].cpu().numpy()
    wavail_np = val_data["work_avail"].cpu().numpy().astype(float)
    ravail_np = val_data["retail_avail"].cpu().numpy().astype(float)

    ref_dists, ref_home, ref_work, ref_retail = {}, {}, {}, {}
    for cy in np.unique(cycle_np):
        for s in [1, 2, 3]:
            mask = (cycle_np == cy) & (strata_np == s)
            if mask.sum() == 0:
                continue
            dist = np.bincount(act_np[mask].flatten(), minlength=14).astype(float)
            ref_dists[(int(cy), int(s))] = dist
            ref_home[(int(cy), int(s))] = float(home_np[mask].mean())
            wa = wavail_np[mask]
            ref_work[(int(cy), int(s))] = float((work_np[mask] * wa).sum() / max(wa.sum(), 1.0))
            ra = ravail_np[mask]
            ref_retail[(int(cy), int(s))] = float((retail_np[mask] * ra).sum() / max(ra.sum(), 1.0))

    rng = np.random.default_rng(42)
    src_idx = rng.choice(n_val, size=n_sample, replace=False)

    gen_act_by    = {s: [] for s in [1, 2, 3]}
    gen_home_by   = {s: [] for s in [1, 2, 3]}
    gen_work_by   = {s: [] for s in [1, 2, 3]}
    gen_retail_by = {s: [] for s in [1, 2, 3]}
    gen_cy_by     = {s: [] for s in [1, 2, 3]}
    isr_flags = []

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

        g_act, g_home, g_work, _, _, retail_sigmoid = model.generate(
            act_t, aux_t, cond_t, cidx_t, strat, temperature=0.0,
            return_retail_probs=True,
        )
        g_act_np = g_act.cpu().numpy(); g_home_np = g_home.cpu().numpy(); g_work_np = g_work.cpu().numpy()
        retail_prob_np = retail_sigmoid.cpu().numpy()
        g_retail_np = (retail_prob_np > 0.5).astype(np.float32)

        # Raw (pre-projection) ISR diagnostic — plain 0.5 threshold on all 3 heads.
        active_count = ((g_home_np > 0.5).astype(int) + (g_work_np > 0.5).astype(int)
                         + (g_retail_np > 0.5).astype(int))
        isr_flags.append((active_count > 1).astype(np.float32).ravel())

        for k, (s_tgt, cy) in enumerate(zip(syn_strata, syn_cy)):
            gen_act_by[s_tgt].append(g_act_np[k])
            gen_home_by[s_tgt].append(g_home_np[k])
            gen_work_by[s_tgt].append(g_work_np[k])
            gen_retail_by[s_tgt].append(g_retail_np[k])
            gen_cy_by[s_tgt].append(cy)

    js_vals, home_gaps, work_gaps, retail_gaps = [], [], [], []
    for s_tgt in [1, 2, 3]:
        if not gen_act_by[s_tgt]:
            continue
        acts = np.array(gen_act_by[s_tgt]); homes = np.array(gen_home_by[s_tgt])
        works = np.array(gen_work_by[s_tgt]); retails = np.array(gen_retail_by[s_tgt])
        cys = np.array(gen_cy_by[s_tgt])
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
            rr = ref_retail.get((int(cy), s_tgt))
            if rr is not None:
                retail_gaps.append(abs(float(retails[mg].mean()) - rr))

    mean_js     = float(np.mean(js_vals))     if js_vals     else float("nan")
    mean_home   = float(np.mean(home_gaps))   if home_gaps   else float("nan")
    mean_work   = float(np.mean(work_gaps))   if work_gaps   else float("nan")
    mean_retail = float(np.mean(retail_gaps)) if retail_gaps else float("nan")
    isr_raw     = float(np.mean(np.concatenate(isr_flags))) if isr_flags else float("nan")

    # Teacher-forced retail PR-AUC/F1 (real held-out labels; self-reconstruction
    # on the OBSERVED day-type — the only place ground truth exists for retail).
    pr_auc, f1 = float("nan"), float("nan")
    if average_precision_score is not None:
        tf_bs = 512
        probs_all, tgt_all, avail_all = [], [], []
        for start in range(0, n_val, tf_bs):
            end = min(start + tf_bs, n_val)
            idx = list(range(start, end))
            batch_tf = {
                "act_seq":    val_data["act_seq"][idx].to(device),
                "aux_seq":    val_data["aux_seq"][idx].to(device),
                "cond_vec":   val_data["cond_vec"][idx].to(device),
                "cycle_idx":  val_data["cycle_idx"][idx].to(device),
                "cycle_year": val_data["cycle_year"][idx].to(device),
                "dec_act_seq": val_data["act_seq"][idx].to(device),
                "tgt_strata":  val_data["obs_strata"][idx].to(device),
            }
            out_tf = model(batch_tf)
            probs_all.append(torch.sigmoid(out_tf["retail_logits"]).cpu().numpy().reshape(-1))
            tgt_all.append(val_data["aux_seq"][idx][:, :, 2].numpy().reshape(-1))
            avail_all.append(val_data["retail_avail"][idx].numpy().reshape(-1))
        probs_all = np.concatenate(probs_all); tgt_all = np.concatenate(tgt_all)
        avail_all = np.concatenate(avail_all).astype(bool)
        if avail_all.sum() > 0 and tgt_all[avail_all].sum() > 0:
            p = probs_all[avail_all]; t = tgt_all[avail_all]
            pr_auc = float(average_precision_score(t, p))
            f1 = float(f1_score(t, (p > 0.5).astype(int)))

    val_score = mean_js + 0.5 * (mean_home + mean_work + mean_retail) / 3.0
    return {"val_js": mean_js, "home_gap": mean_home, "work_gap": mean_work,
            "retail_gap": mean_retail, "isr_raw": isr_raw,
            "pr_auc": pr_auc, "f1": f1, "val_score": val_score}


# ── Sampler weights: 50/25/25 day-type composition + inverse-cycle-frequency ──

def build_sampler_weights(train_data: dict, pairs: dict) -> np.ndarray:
    """Delta E: 'Stratified batch composition (50% weekday / 25% Sat / 25% Sun)
    + inverse-cycle-frequency weighting during joint training (2022 has the
    fewest diaries).' Combines two independent per-pair corrections:
      1. day-type (tgt_strata) reweighted to the fixed 50/25/25 target share.
      2. cycle_year (of the SOURCE respondent) reweighted to an equal share
         across the cycles present (boosts 2022, the sparsest cycle)."""
    tgt_strata = pairs["tgt_strata"].numpy()
    src_idx = pairs["src_idx"].numpy()
    cycle_year = train_data["cycle_year"][src_idx].numpy()

    target_share = {1: 0.50, 2: 0.25, 3: 0.25}
    strata_counts = np.bincount(tgt_strata, minlength=4)[1:4]
    strata_freq = strata_counts / max(strata_counts.sum(), 1)
    daytype_w = np.array([
        target_share[s] / max(strata_freq[s - 1], 1e-9) for s in tgt_strata
    ], dtype=np.float64)

    cycles = np.unique(cycle_year)
    cycle_counts = {int(cy): float((cycle_year == cy).sum()) for cy in cycles}
    n_total = len(cycle_year)
    target_cycle_share = 1.0 / max(len(cycles), 1)
    cycle_w = np.array([
        target_cycle_share / max(cycle_counts[int(cy)] / n_total, 1e-9) for cy in cycle_year
    ], dtype=np.float64)

    w = daytype_w * cycle_w
    return (w / w.mean()).astype(np.float32)


# ── Main training ─────────────────────────────────────────────────────────────

def train(args):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    out_dir  = args.output_dir
    ckpt_dir = args.checkpoint_dir
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(ckpt_dir, exist_ok=True)

    # ── Config ───────────────────────────────────────────────────────────
    with open(os.path.join(args.data_dir, "step4_feature_config.json")) as f:
        feat_cfg = json.load(f)
    d_cond = feat_cfg["d_cond"]
    n_aux  = feat_cfg.get("n_aux", 12)

    alphas = dict(zip(TASK_GROUPS, [float(x) for x in args.alphas.split(",")]))

    # retail_pos_weight resolution: config value (measured, ~50) wins unless the
    # user explicitly overrides --retail_pos_weight away from its documented
    # default of 49 (Delta C: "read from config ~50, expose flag default 49").
    if abs(args.retail_pos_weight - 49.0) < 1e-9:
        retail_pw_val = feat_cfg.get("retail_pos_weight", args.retail_pos_weight)
    else:
        retail_pw_val = args.retail_pos_weight

    # ── Device ───────────────────────────────────────────────────────────
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    default_lr     = 1e-3 if args.phase == "warmup" else 1e-4
    default_epochs = 5    if args.phase == "warmup" else 15
    lr         = args.lr if args.lr is not None else default_lr
    max_epochs = args.max_epochs if args.max_epochs is not None else default_epochs
    if args.smoke and args.max_epochs is None:
        max_epochs = 2   # enough to observe the loss decreasing; still tiny on CPU

    print(f"  Device: {device}  PHASE={args.phase}  WEIGHT_MODE=fixed  alphas={alphas}  "
          f"PCGrad={'ON' if args.phase == 'joint' else 'OFF (single trainable task)'}  "
          f"lambda_excl={args.lambda_excl if args.phase == 'joint' else 0.0}  "
          f"lr={lr}  max_epochs={max_epochs}")

    # ── Data ─────────────────────────────────────────────────────────────
    print("[1/4] Loading datasets and pairs...")
    train_data  = torch.load(os.path.join(args.data_dir, "step4_train.pt"), map_location="cpu", weights_only=False)
    val_data    = torch.load(os.path.join(args.data_dir, "step4_val.pt"), map_location="cpu", weights_only=False)
    train_pairs = torch.load(os.path.join(args.data_dir, "training_pairs.pt"), map_location="cpu", weights_only=False)

    if args.smoke:
        # CPU smoke: trim to a small deterministic slice for speed. Real
        # tensors are already full-scale (44,843 train rows) — this is a
        # LOCAL-ONLY convenience, not part of any frozen delta.
        n_smoke_pairs = min(400, len(train_pairs["src_idx"]))
        g = torch.Generator().manual_seed(args.seed)
        keep = torch.randperm(len(train_pairs["src_idx"]), generator=g)[:n_smoke_pairs]
        train_pairs = {k: v[keep] for k, v in train_pairs.items()}
        n_val_smoke = min(300, len(val_data["act_seq"]))
        val_data = {k: (v[:n_val_smoke] if torch.is_tensor(v) and v.shape[0] == len(val_data["act_seq"]) else v)
                    for k, v in val_data.items()}

    train_dataset = Step4Dataset4Split(train_data, train_pairs)
    print(f"  Train pairs: {len(train_dataset)} | Val respondents: {len(val_data['act_seq'])}")

    # Activity CE class weights (inverse-sqrt-frequency from act_class_freqs)
    freqs = np.array(feat_cfg.get("act_class_freqs", [1.0] * 14), dtype=float)
    freqs = np.maximum(freqs, 1e-6)
    cw = 1.0 / np.sqrt(freqs)
    cw = cw / cw.mean()
    act_class_weights = torch.tensor(cw, dtype=torch.float32, device=device)

    home_pw   = torch.tensor([feat_cfg.get("home_pos_weight", 1.0)], dtype=torch.float32, device=device)
    work_pw   = torch.tensor([feat_cfg.get("work_pos_weight", 1.0)], dtype=torch.float32, device=device)
    retail_pw = torch.tensor([retail_pw_val], dtype=torch.float32, device=device)
    print(f"  home_pos_weight={home_pw.item():.4f}  work_pos_weight={work_pw.item():.4f}  "
          f"retail_pos_weight={retail_pw.item():.4f}"
          f"{'  [config value]' if abs(args.retail_pos_weight - 49.0) < 1e-9 else '  [CLI override]'}")
    cop_pos_weight = None   # off by default (Leg-1/Leg-2 default); not part of Leg-3 frozen deltas

    # WGHT_PER: per-respondent survey weight, clipped at the 99th percentile (Delta E)
    wght_p99 = float(np.percentile(train_data["wght_per"].numpy(), 99))
    print(f"  WGHT_PER p99 clip = {wght_p99:.4f}")

    # Sampler: 50/25/25 day-type composition + inverse-cycle-frequency (Delta E)
    sampler_weights = build_sampler_weights(train_data, train_pairs)
    sampler = WeightedRandomSampler(weights=sampler_weights, num_samples=len(train_dataset), replacement=True)
    train_loader = DataLoader(
        train_dataset, batch_size=args.batch_size, sampler=sampler,
        num_workers=0, pin_memory=(device.type == "cuda"),
    )

    # ── Model architecture (Leg-3 base; overridden below by warm-start's
    #    stored model_config for the arch-family fields — d_cond/n_aux always
    #    pinned to the CURRENT run's feature config, since those are forced
    #    by the data actually being trained on). ─────────────────────────
    if args.smoke:
        model_config = {"d_model": 64, "n_heads": 2, "d_ff": 256, "N_enc": 2, "N_dec": 2,
                         "d_act": 16, "d_cycle": 16, "dropout": 0.1}
    else:
        model_config = {"d_model": args.d_model, "n_heads": args.n_heads,
                         "d_ff": 1024 if args.d_model == 256 else args.d_model * 4,
                         "N_enc": args.n_enc_layers, "N_dec": args.n_dec_layers,
                         "d_act": 32, "d_cycle": 32, "dropout": 0.1}
    model_config.update({
        "model_type": "J3", "n_activity_classes": 14, "n_copresence": 9,
        "n_slots": 48, "n_aux": n_aux, "d_cond": d_cond,
    })

    # ── Warm-start resolution ────────────────────────────────────────────
    ws_path = args.warm_start or ""
    if not ws_path and args.phase == "joint":
        _default_ws = os.path.join(ckpt_dir, "warmup_checkpoint.pt")
        if os.path.isfile(_default_ws):
            ws_path = _default_ws
            print(f"  [WARM-START] --warm_start not given; defaulting to phase-1 output: {ws_path}")
    if not ws_path:
        raise ValueError(
            f"--warm_start is required for --phase {args.phase} (Delta E: both phases warm-start "
            f"from a prior checkpoint — phase 'warmup' from the Leg-2 base model, phase 'joint' "
            f"from phase 1's own output checkpoint)."
        )
    if not os.path.isfile(ws_path):
        raise FileNotFoundError(f"--warm_start checkpoint not found: {ws_path}")

    print(f"[2/4] Building model + warm-starting from {ws_path} ...")
    ck_ws = torch.load(ws_path, map_location="cpu", weights_only=False)
    ws_cfg = ck_ws.get("model_config", {}) or {}
    for k in ["d_model", "n_heads", "d_ff", "N_enc", "N_dec", "d_act", "d_cycle", "dropout"]:
        if k in ws_cfg:
            model_config[k] = ws_cfg[k]
    if ws_cfg.get("d_cond") not in (None, d_cond):
        print(f"  [WARM-START] WARNING: checkpoint d_cond={ws_cfg.get('d_cond')} != current data "
              f"d_cond={d_cond} — conditioning is NOT byte-identical between the checkpoint and this "
              f"Leg-3 run (see Progress Log ESCALATE note, 2026-07-19). Any layer whose shape depends "
              f"on d_cond (proj_demo, cls_mlp.0) will show up below as a shape-mismatch and be "
              f"random-initialized — this is IN ADDITION to retail_head.")
    if ws_cfg.get("n_aux") not in (None, n_aux):
        print(f"  [WARM-START] NOTE: checkpoint n_aux={ws_cfg.get('n_aux')} vs current n_aux={n_aux} "
              f"(expected — retail is a new aux plane); slot_linear will be random-init.")

    model = JSeriesHybrid4Split(model_config).to(device)
    new_sd = model.state_dict()
    ck_sd = ck_ws["model_state"]
    ws_report = {"loaded": [], "shape_mismatch": [], "missing_in_ckpt": [], "unused_in_ckpt": []}
    load_sd = {}
    for k, v in ck_sd.items():
        if k not in new_sd:
            ws_report["unused_in_ckpt"].append(k)
            continue
        if tuple(v.shape) == tuple(new_sd[k].shape):
            load_sd[k] = v
            ws_report["loaded"].append(k)
        else:
            ws_report["shape_mismatch"].append((k, tuple(v.shape), tuple(new_sd[k].shape)))
    for k in new_sd:
        if k not in ck_sd:
            ws_report["missing_in_ckpt"].append(k)
    model.load_state_dict(load_sd, strict=False)

    print(f"  [WARM-START] loaded {len(ws_report['loaded'])}/{len(new_sd)} tensors by name+shape match")
    if ws_report["shape_mismatch"]:
        print(f"  [WARM-START] SHAPE-MISMATCH -> random-init ({len(ws_report['shape_mismatch'])}):")
        for k, old_s, new_s in ws_report["shape_mismatch"]:
            print(f"      {k}: ckpt{old_s} -> model{new_s}")
    if ws_report["missing_in_ckpt"]:
        print(f"  [WARM-START] MISSING-IN-CKPT -> random-init ({len(ws_report['missing_in_ckpt'])}): "
              f"{ws_report['missing_in_ckpt']}")
    if ws_report["unused_in_ckpt"]:
        print(f"  [WARM-START] UNUSED-IN-CKPT (present in checkpoint, absent in model) "
              f"({len(ws_report['unused_in_ckpt'])}): {ws_report['unused_in_ckpt']}")
    retail_only = (
        all(k.startswith("retail_head.") for k in ws_report["missing_in_ckpt"])
        and not ws_report["shape_mismatch"]
    )
    print(f"  [WARM-START] retail_head-ONLY-new confirmed: {retail_only}")

    total_params = sum(p.numel() for p in model.parameters())
    print(f"  Parameters: {total_params:,}")

    # ── Phase freezing (Delta E) ─────────────────────────────────────────
    if args.phase == "warmup":
        for name, p in model.named_parameters():
            p.requires_grad = name.startswith("retail_head.")
    else:
        for p in model.parameters():
            p.requires_grad = True
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    n_trainable = sum(p.numel() for p in trainable_params)
    n_frozen_tensors = sum(1 for p in model.parameters() if not p.requires_grad)
    n_trainable_tensors = sum(1 for p in model.parameters() if p.requires_grad)
    print(f"  [PHASE={args.phase}] trainable tensors={n_trainable_tensors} "
          f"({n_trainable:,} params) | frozen tensors={n_frozen_tensors}")
    if args.phase == "warmup":
        only_retail_trainable = all(
            name.startswith("retail_head.") for name, p in model.named_parameters() if p.requires_grad
        )
        print(f"  [PHASE=warmup] ONLY retail_head trainable confirmed: {only_retail_trainable}")

    optimizer = torch.optim.AdamW(trainable_params, lr=lr, weight_decay=1e-4)
    pcgrad = PCGrad(trainable_params) if args.phase == "joint" else None

    # ── Resume (rare; mirrors Leg-2) ─────────────────────────────────────
    start_epoch = 0
    best_val_score = float("inf")
    patience_counter = 0
    if args.resume and os.path.isfile(args.resume):
        ck = torch.load(args.resume, map_location=device, weights_only=False)
        model.load_state_dict(ck["model_state"])
        optimizer.load_state_dict(ck["optimizer_state"])
        start_epoch = ck["epoch"] + 1
        best_val_score = ck.get("best_val_score", float("inf"))
        print(f"  Resumed from epoch {start_epoch}, best_val_score={best_val_score:.4f}")

    # ── Training log ─────────────────────────────────────────────────────
    log_path = os.path.join(out_dir, f"step4_training_log_{args.phase}.csv")
    log_fields = ["epoch", "phase", "train_loss", "act_loss", "home_loss", "work_loss",
                  "retail_loss", "cop_loss", "div_loss", "excl_loss",
                  "val_js", "home_gap", "work_gap", "retail_gap", "isr_raw",
                  "pr_auc", "f1", "val_score", "lr", "grad_norm", "elapsed_s"]
    if start_epoch == 0:
        with open(log_path, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=log_fields).writeheader()

    clip_norm = 25.0
    print("[3/4] Training...")

    for epoch in range(start_epoch, max_epochs):
        model.train()
        t0 = time.time()
        train_dataset.resample()

        lambda_excl = args.lambda_excl if args.phase == "joint" else 0.0
        accum = {k: 0.0 for k in ["total", "act", "home", "work", "retail", "cop", "div", "excl"]}
        grad_norms = []

        for batch in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            optimizer.zero_grad()
            wght_per = batch["src_wght_per"].clamp(max=wght_p99)

            out = model(batch)
            comp = component_losses(out, batch, act_class_weights, home_pw, work_pw,
                                     retail_pw, cop_pos_weight, wght_per=wght_per)
            div = diversity_loss(out, batch)
            excl = exclusivity_loss(out, batch) if lambda_excl > 0 else torch.tensor(0.0, device=device)

            L_resid  = comp["act"] + comp["home"] + comp["cop"]
            L_work   = comp["work"]
            L_retail = comp["retail"]

            if args.phase == "warmup":
                # Only retail_head is trainable; the other groups produce zero
                # gradient into it anyway, so train on the plain retail BCE.
                total = L_retail
                total.backward()
                grad_norm = nn.utils.clip_grad_norm_(trainable_params, clip_norm).item()
                optimizer.step()
            else:
                task_w = {
                    "resid":  alphas["resid"]  * L_resid,
                    "work":   alphas["work"]   * L_work,
                    "retail": alphas["retail"] * L_retail,
                }
                extra = LAMBDA_DIV * div + lambda_excl * excl
                if pcgrad is not None:
                    pcgrad.backward([task_w[t] for t in TASK_GROUPS], retain_all=True)
                    extra_grads = torch.autograd.grad(extra, pcgrad.params, allow_unused=True)
                    for p, eg in zip(pcgrad.params, extra_grads):
                        if eg is not None:
                            p.grad = (p.grad if p.grad is not None else torch.zeros_like(p)) + eg
                    total = sum(task_w.values()) + extra   # logging only — PCGrad already wrote .grad
                else:
                    total = sum(task_w.values()) + extra
                    total.backward()
                grad_norm = nn.utils.clip_grad_norm_(trainable_params, clip_norm).item()
                optimizer.step()

            accum["total"]  += float(total.item())
            accum["act"]    += float(comp["act"].item())
            accum["home"]   += float(comp["home"].item())
            accum["work"]   += float(comp["work"].item())
            accum["retail"] += float(comp["retail"].item())
            accum["cop"]    += float(comp["cop"].item())
            accum["div"]    += float(div.item())
            accum["excl"]   += float(excl.item())
            grad_norms.append(grad_norm)

        nb = max(len(train_loader), 1)
        avg = {k: v / nb for k, v in accum.items()}
        cur_lr = optimizer.param_groups[0]["lr"]

        val = validate(model, val_data, device, n_sample=(100 if args.smoke else 2000))
        elapsed = time.time() - t0

        print(f"Epoch {epoch+1:3d}/{max_epochs} [{args.phase}]: loss={avg['total']:.4f}  "
              f"act={avg['act']:.4f} home={avg['home']:.4f} work={avg['work']:.4f} "
              f"retail={avg['retail']:.4f} cop={avg['cop']:.4f} div={avg['div']:.4f} "
              f"excl={avg['excl']:.4f} | val_JS={val['val_js']:.4f} home_gap={val['home_gap']:.4f} "
              f"work_gap={val['work_gap']:.4f} retail_gap={val['retail_gap']:.4f} "
              f"isr_raw={val['isr_raw']:.4f} pr_auc={val['pr_auc']:.4f} f1={val['f1']:.4f} "
              f"score={val['val_score']:.4f} ({elapsed:.0f}s)")

        with open(log_path, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=log_fields).writerow({
                "epoch": epoch + 1, "phase": args.phase, "train_loss": round(avg["total"], 6),
                "act_loss": round(avg["act"], 6), "home_loss": round(avg["home"], 6),
                "work_loss": round(avg["work"], 6), "retail_loss": round(avg["retail"], 6),
                "cop_loss": round(avg["cop"], 6), "div_loss": round(avg["div"], 6),
                "excl_loss": round(avg["excl"], 6),
                "val_js": round(val["val_js"], 6), "home_gap": round(val["home_gap"], 6),
                "work_gap": round(val["work_gap"], 6), "retail_gap": round(val["retail_gap"], 6),
                "isr_raw": round(val["isr_raw"], 6),
                "pr_auc": round(val["pr_auc"], 6) if not math.isnan(val["pr_auc"]) else "",
                "f1": round(val["f1"], 6) if not math.isnan(val["f1"]) else "",
                "val_score": round(val["val_score"], 6),
                "lr": round(cur_lr, 8), "grad_norm": round(float(np.mean(grad_norms)), 4),
                "elapsed_s": round(elapsed, 1),
            })

        ckpt_payload = {
            "epoch": epoch, "model_state": model.state_dict(), "model_config": model_config,
            "phase": args.phase, "alphas": alphas,
            "val_js": val["val_js"], "home_gap": val["home_gap"], "work_gap": val["work_gap"],
            "retail_gap": val["retail_gap"], "isr_raw": val["isr_raw"],
            "pr_auc": val["pr_auc"], "f1": val["f1"], "val_score": val["val_score"],
        }

        if args.phase == "warmup":
            # No early-stop concept in phase 1 (fixed 5 epochs); always save
            # the latest as the phase-1 output checkpoint (input to phase 2).
            torch.save(ckpt_payload, os.path.join(ckpt_dir, "warmup_checkpoint.pt"))
            print(f"  [warmup {epoch+1}/{max_epochs}] saved warmup_checkpoint.pt")
        else:
            torch.save({**ckpt_payload, "optimizer_state": optimizer.state_dict(),
                        "best_val_score": best_val_score}, os.path.join(ckpt_dir, "last_checkpoint.pt"))
            score = val["val_score"]
            if math.isnan(score):
                score = avg["total"]
            if score < best_val_score:
                best_val_score = score
                patience_counter = 0
                torch.save(ckpt_payload, os.path.join(ckpt_dir, "best_model.pt"))
                print(f"  NEW BEST (score={best_val_score:.4f})")
            else:
                patience_counter += 1
                if patience_counter >= args.patience:
                    print(f"  Early stopping at epoch {epoch+1} (gate-set proxy score, patience={args.patience})")
                    break

    print(f"\n[4/4] Training complete ({args.phase}).")
    if args.phase == "warmup":
        print(f"  Phase-1 checkpoint: {os.path.join(ckpt_dir, 'warmup_checkpoint.pt')}")
    else:
        print(f"  Best checkpoint: {os.path.join(ckpt_dir, 'best_model.pt')}  best_val_score={best_val_score:.4f}")
    print(f"  Training log:    {log_path}")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", default=None)
    p.add_argument("--output_dir", default=None)
    p.add_argument("--checkpoint_dir", default=None)
    p.add_argument("--batch_size", type=int, default=256)
    p.add_argument("--max_epochs", type=int, default=None,
                   help="override phase default (warmup=5, joint=15); --smoke forces 1")
    p.add_argument("--patience", type=int, default=10)
    p.add_argument("--lr", type=float, default=None,
                   help="override phase default (warmup=1e-3, joint=1e-4)")
    p.add_argument("--d_model", type=int, default=256)
    p.add_argument("--n_heads", type=int, default=8)
    p.add_argument("--n_enc_layers", type=int, default=6)
    p.add_argument("--n_dec_layers", type=int, default=6)
    p.add_argument("--fp16", action="store_true")
    p.add_argument("--resume", default=None)
    p.add_argument("--smoke", action="store_true",
                   help="tiny CPU smoke slice: TEST_CONFIG-scale model, 1 epoch, 400 train pairs")
    p.add_argument("--phase", choices=["warmup", "joint"], required=True,
                   help="warmup: 5ep/1e-3/retail_head-only. joint: 15ep/1e-4/all-params/PCGrad.")
    p.add_argument("--alphas", type=str, default="1.0,0.5,0.3",
                   help="fixed scalarization weights, order resid,work,retail (Delta D)")
    p.add_argument("--retail_pos_weight", type=float, default=49.0,
                   help="BCE pos_weight for the retail head; config value (~50) wins unless "
                        "this is set away from the documented default of 49 (Delta C)")
    p.add_argument("--warm_start", type=str, default="",
                   help="checkpoint to warm-start from (required both phases: Leg-2 base for "
                        "--phase warmup, phase-1 output for --phase joint)")
    p.add_argument("--lambda_excl", type=float, default=0.05,
                   help="exclusivity soft-penalty weight; OFF (0) in phase warmup regardless of "
                        "this value, ON in phase joint (Delta C/E)")
    p.add_argument("--seed", type=int, default=42)
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
    print(f"Step 4D (Leg-3, 4-split) — Training  phase={args.phase}"
          f"{'  [SMOKE]' if args.smoke else ''}")
    print("=" * 60)
    print(f"  data_dir:       {args.data_dir}")
    print(f"  output_dir:     {args.output_dir}")
    print(f"  checkpoint_dir: {args.checkpoint_dir}")
    print(f"  batch_size={args.batch_size} patience={args.patience} fp16={args.fp16}")
    train(args)
