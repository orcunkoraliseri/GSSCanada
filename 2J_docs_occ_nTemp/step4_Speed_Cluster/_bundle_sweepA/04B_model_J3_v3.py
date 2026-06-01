"""
04B_model_J3_v3.py — J3 + Per-Slot Demographic Broadcast (regularized) = PSB-Lite.

Phase 2, Arm 2 of `04_augmentationGSS_IMP.md` (post-J3-PSB-shelving plan,
2026-05-22).

J3-PSB (v2) regressed all 4 gates on Speed job 934720 — composite 0.6355 → 0.8463,
act_JS 0.019 → 0.052, AT_HOME RMS 4.57 → 6.89 pp. Diagnosis (see Progress Log
entry in IMP doc): per-slot static demographic broadcast added ~d_cond × n_slots
features per sample (~4,320 with d_cond=90), and the encoder satisfied training
loss by down-weighting slot position and up-weighting the static feature. Time
signal collapsed; alone × at_home Cramer's V exploded (obs 0.067 → syn 0.272).

This file (v3) keeps the *idea* of per-slot demographic broadcast but adds two
regularizations that target the failure mode:

  (1) Project cond_vec (d_cond ≈ 90) → cond_proj (d_proj = 8) via a learnable
      `Linear(d_cond, d_proj)` BEFORE broadcast. Reduces per-slot extra capacity
      from ~4,320 to 384 features/sample (~11× smaller). The projection learns
      the most relevant demographic axes; the rest gets compressed out.

  (2) Per-slot Bernoulli cond-dropout (p_cond_drop = 0.5) at training only.
      Each slot's projected demographic vector is randomly zeroed independently
      across the 48 positions, so the encoder cannot rely on demographics being
      present at every step — it must keep using slot position. At inference the
      projection is applied directly with no dropout (standard PyTorch dropout
      semantics).

Preserved from J3 (load-bearing — never modify):
  - `arm2_act_proj = Linear(14, d_model)` projection of soft activity probs
    into Arm-2 fusion. J3's 4/4-gate result depends on it.
  - Arm-1 / Arm-2 detach barrier (removing it cost AT_HOME 4.57 → 5.88 pp in
    J5_X1b — see §3.5 of IMP doc).
  - All heads, the AR decoder, the loss formulation.

Filename begins with a digit — import via importlib only.
"""

import importlib
import os
import sys

import torch
import torch.nn as nn
import torch.nn.functional as F

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

_base = importlib.import_module("04B_model")
JSeriesHybrid = _base.JSeriesHybrid


class JSeriesHybridV3(JSeriesHybrid):
    """J3 + regularized per-slot demographic broadcast (PSB-Lite).

    Two regularizations vs v2 (raw PSB):
      - cond_vec projected to d_proj before broadcast (default d_proj = 8).
      - Per-slot Bernoulli cond-dropout at training only (default p = 0.5).

    Config keys consumed (with defaults):
      d_psb_proj      : int, default 8   — projected dim of broadcast cond_vec
      p_psb_drop      : float, default 0.5 — per-slot cond-dropout during training
    """

    def __init__(self, config: dict):
        # Build the parent as J3 so arm2_act_proj, detach barrier, Tanh heads,
        # and Arm-1 are wired identically to J3 production. We only modify the
        # encoder slot-token path.
        config_for_parent = dict(config)
        config_for_parent["model_type"] = "J3"
        super().__init__(config_for_parent)

        self._mtype = "J3_v3"

        d_act    = config.get("d_act", 32)
        n_cop    = config.get("n_copresence", 9)
        d_cond   = config["d_cond"]
        d_model  = config["d_model"]
        d_proj   = config.get("d_psb_proj", 8)
        p_drop   = config.get("p_psb_drop", 0.5)

        self.d_psb_proj = int(d_proj)
        self.p_psb_drop = float(p_drop)

        # Projection: d_cond → d_psb_proj (default 8). Xavier-init, zero bias.
        self.psb_proj = nn.Linear(d_cond, self.d_psb_proj)
        nn.init.xavier_uniform_(self.psb_proj.weight)
        nn.init.zeros_(self.psb_proj.bias)

        # Widen the encoder slot projection input by d_psb_proj.
        # Old: d_act + 1 + n_cop. New: d_act + 1 + n_cop + d_psb_proj.
        self.slot_linear = nn.Linear(
            d_act + 1 + n_cop + self.d_psb_proj, d_model
        )
        nn.init.xavier_uniform_(self.slot_linear.weight)
        nn.init.zeros_(self.slot_linear.bias)

    def _encode(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata=None):
        """J3 encoder with regularized per-slot demographic broadcast.

        Slot input grows from (d_act + 10) to (d_act + 10 + d_psb_proj).
        cond_vec is projected once (B, d_cond → B, d_proj), broadcast to all
        48 slots, then per-slot Bernoulli-masked at training only.
        CLS token construction unchanged from J3.
        """
        T = act_seq.shape[1]

        act_emb = self.act_embedding(act_seq)                              # (B, T, d_act)

        # Project + broadcast demographics
        cond_proj = self.psb_proj(cond_vec)                                # (B, d_psb_proj)
        cond_b    = cond_proj.unsqueeze(1).expand(-1, T, -1)               # (B, T, d_psb_proj)

        # Per-slot cond-dropout: zero entire d_psb_proj vector at random slots.
        # Independent Bernoulli per (batch, slot). Inverted-dropout scaling
        # matches PyTorch convention so inference scale is unchanged.
        if self.training and self.p_psb_drop > 0.0:
            keep = 1.0 - self.p_psb_drop
            mask = torch.empty(
                cond_b.shape[0], cond_b.shape[1], 1,
                device=cond_b.device, dtype=cond_b.dtype,
            ).bernoulli_(keep) / keep
            cond_b = cond_b * mask                                          # (B, T, d_psb_proj)

        slot_in  = torch.cat([act_emb, aux_seq, cond_b], dim=-1)            # (B, T, d_act + 10 + d_proj)
        slot_emb = self.slot_linear(slot_in)                                # (B, T, d_model)
        slot_emb = slot_emb + self.enc_pos_enc[:, 1:, :]

        cycle_emb = self.cycle_embedding(cycle_idx)
        cls_tok   = self.cls_mlp(
            torch.cat([cond_vec, cycle_emb], dim=-1)
        ).unsqueeze(1)
        cls_tok = cls_tok + self.enc_pos_enc[:, :1, :]

        return self.encoder(torch.cat([cls_tok, slot_emb], dim=1))          # (B, 49, d_model)
