"""
04B_model_J3_v2.py — J3 + Per-Slot Demographic Broadcast (J3-PSB).

Phase 1 of 2J_docs_occ_nTemp/04_augmentationGSS_IMP.md.

Single architectural change vs J3 (baseline 0.6355): concat the per-respondent
demographic vector (`cond_vec`) onto every one of the 48 encoder slot tokens
BEFORE `slot_linear`, so the encoder sees demographics at every timestep
instead of only at the CLS + 3 cross-attention conditioning tokens.

Targets the root cause documented in
`step4_Speed-Cluster_docs/investigations/investigation_oldTransformer_vs_J3.md §6.1`:
binary heads (AT_HOME, co-presence) lack an AR fallback, so they suffer the
most when the encoder fails to route demographic information from CLS to
slot t. Per-slot broadcast removes that routing dependency.

Preserved from J3 (load-bearing):
  - `arm2_act_proj = Linear(14, d_model)` projection of soft activity probs
    into Arm-2 fusion (J3's 4/4-gate result depends on it).
  - Arm-1 / Arm-2 detach barrier (J5_X1b removed it → AT_HOME 4.57 → 5.88 pp).
  - All heads (act/home/cop), the AR decoder, all losses.

Filename begins with a digit — import via importlib only.
"""

import importlib
import os
import sys

import torch
import torch.nn as nn

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

_base = importlib.import_module("04B_model")
JSeriesHybrid = _base.JSeriesHybrid


class JSeriesHybridV2(JSeriesHybrid):
    """J3 + per-slot demographic broadcast on encoder slot tokens."""

    def __init__(self, config: dict):
        # Build the parent as J3 so arm2_act_proj, detach barrier, Tanh heads,
        # and Arm-1 are all wired identically to the J3 production baseline.
        config_for_parent = dict(config)
        config_for_parent["model_type"] = "J3"
        super().__init__(config_for_parent)

        # Re-tag for diagnostics. Forward/infer dispatch in the parent class
        # uses the "standard" J-series branch (not J_old / J5_F / J5_X1 / J5_C),
        # which is what we want — J3_v2 follows J3's Arm-1 → Arm-2 (detached) path.
        self._mtype = "J3_v2"

        # Widen the encoder slot projection input by d_cond. Old: d_act + 1 + n_cop.
        # New: d_act + 1 + n_cop + d_cond. Decoder slot inputs (arm1_slot_proj,
        # arm2_act_proj) and cls_mlp are unchanged.
        d_act   = config.get("d_act", 32)
        n_cop   = config.get("n_copresence", 9)
        d_cond  = config["d_cond"]
        d_model = config["d_model"]
        self.slot_linear = nn.Linear(d_act + 1 + n_cop + d_cond, d_model)
        nn.init.xavier_uniform_(self.slot_linear.weight)
        nn.init.zeros_(self.slot_linear.bias)

    def _encode(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata=None):
        """J3 encoder with per-slot demographic broadcast on slot tokens.

        Slot input grows from [act_emb | aux_seq] (d_act + 10) to
        [act_emb | aux_seq | cond_vec_broadcast] (d_act + 10 + d_cond).
        CLS token construction unchanged from J3.
        """
        T = act_seq.shape[1]

        act_emb  = self.act_embedding(act_seq)                       # (B, T, d_act)
        cond_b   = cond_vec.unsqueeze(1).expand(-1, T, -1)            # (B, T, d_cond) — PSB
        slot_in  = torch.cat([act_emb, aux_seq, cond_b], dim=-1)      # (B, T, d_act + 10 + d_cond)
        slot_emb = self.slot_linear(slot_in)                          # (B, T, d_model)
        slot_emb = slot_emb + self.enc_pos_enc[:, 1:, :]

        cycle_emb = self.cycle_embedding(cycle_idx)
        cls_tok   = self.cls_mlp(
            torch.cat([cond_vec, cycle_emb], dim=-1)
        ).unsqueeze(1)
        cls_tok = cls_tok + self.enc_pos_enc[:, :1, :]

        return self.encoder(torch.cat([cls_tok, slot_emb], dim=1))    # (B, 49, d_model)
