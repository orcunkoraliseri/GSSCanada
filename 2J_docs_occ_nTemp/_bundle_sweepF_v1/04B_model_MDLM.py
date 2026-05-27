"""
04B_model_MDLM.py — Phase 6 Stage F: MDLM with configurable intrinsic parameters.

Backward-compatible with MDLM_C when no extra env vars are set.
New env-var knobs for Stage F HPT:
  MDLM_STEPS          — denoise steps at inference (default 16)
  MDLM_MASK_SCHEDULE  — "uniform" (default), "cosine", "linear"
  MDLM_MASK_LO        — mask clamp lower bound (default 0.05)
  MDLM_MASK_HI        — mask clamp upper bound (default 0.95)
  MDLM_REFINER_LAYERS — x0_refiner transformer layers (default 2)
"""

import importlib
import math
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

N_DENOISE_STEPS    = int(os.environ.get("MDLM_STEPS", "16"))
MASK_SCHEDULE      = os.environ.get("MDLM_MASK_SCHEDULE", "uniform")
MASK_LO            = float(os.environ.get("MDLM_MASK_LO", "0.05"))
MASK_HI            = float(os.environ.get("MDLM_MASK_HI", "0.95"))
REFINER_LAYERS     = int(os.environ.get("MDLM_REFINER_LAYERS", "2"))


def _sample_mask_t(B: int, device: torch.device) -> torch.Tensor:
    """Sample masking ratio t per sample according to the configured schedule."""
    if MASK_SCHEDULE == "uniform":
        return torch.rand(B, 1, device=device).clamp(MASK_LO, MASK_HI)
    elif MASK_SCHEDULE == "cosine":
        u = torch.rand(B, 1, device=device)
        t = 0.5 * (1.0 - torch.cos(math.pi * u))
        return t.clamp(MASK_LO, MASK_HI)
    elif MASK_SCHEDULE == "linear":
        return torch.rand(B, 1, device=device).clamp(MASK_LO, MASK_HI)
    else:
        raise ValueError(f"Unknown MDLM_MASK_SCHEDULE: {MASK_SCHEDULE}")


class MDLMHybrid(JSeriesHybrid):
    """J3 encoder + Arm-2 binaries; new Arm-1 = masked-token denoiser."""

    def __init__(self, config: dict):
        cfg = dict(config)
        cfg["model_type"] = "J3"
        super().__init__(cfg)
        self._mtype = "MDLM"

        d_model = config["d_model"]
        d_act   = config.get("d_act", 32)
        n_act   = config.get("n_activity_classes", 14)

        self.mask_token = nn.Parameter(torch.randn(1, 1, d_act) * 0.02)

        ref_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=config["n_heads"], dim_feedforward=config["d_ff"],
            dropout=0.1, activation="gelu", batch_first=True,
        )
        self.x0_refiner = nn.TransformerEncoder(
            ref_layer, num_layers=REFINER_LAYERS, norm=nn.LayerNorm(d_model)
        )
        self.x0_head = nn.Linear(d_model, n_act)

        nn.init.xavier_uniform_(self.x0_head.weight)
        nn.init.zeros_(self.x0_head.bias)

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _embed_with_mask(self, act_seq: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        emb = self.act_embedding(act_seq)
        if mask is not None and mask.any():
            mask_b = mask.unsqueeze(-1).float()
            emb = emb * (1.0 - mask_b) + self.mask_token * mask_b
        return emb

    def _refine_x0(self, memory: torch.Tensor) -> torch.Tensor:
        slots = memory[:, 1:, :]
        refined = self.x0_refiner(slots)
        return self.x0_head(refined)

    # ── Forward (training): random masking ──────────────────────────────────

    def forward(self, batch: dict) -> dict:
        act_seq = batch["dec_act_seq"]
        B, T = act_seq.shape
        device = act_seq.device

        t      = _sample_mask_t(B, device)
        mask_p = t.expand(-1, T)
        mask   = torch.rand(B, T, device=device) < mask_p

        masked_act_emb = self._embed_with_mask(act_seq, mask)
        slot_input     = torch.cat([masked_act_emb, batch["dec_aux_seq"]], dim=-1)
        slot_emb       = self.slot_linear(slot_input)
        slot_emb       = slot_emb + self.enc_pos_enc[:, 1:, :]

        cond_vec  = batch["cond_vec"]
        cycle_emb = self.cycle_embedding(batch["cycle_idx"])
        cls_tok   = self.cls_mlp(torch.cat([cond_vec, cycle_emb], dim=-1)).unsqueeze(1)
        cls_tok   = cls_tok + self.enc_pos_enc[:, :1, :]
        memory    = self.encoder(torch.cat([cls_tok, slot_emb], dim=1))

        act_logits = self._refine_x0(memory)

        clean_memory = self._encode(
            batch["act_seq"], batch["aux_seq"],
            batch["cond_vec"], batch["cycle_idx"],
            tgt_strata=batch.get("tgt_strata"),
        )
        act_probs = F.softmax(act_logits.detach(), dim=-1)
        arm2_feat = self._arm2_fuse(
            clean_memory, act_probs, batch["cond_vec"],
            batch["cycle_idx"], batch["tgt_strata"],
        )
        home_logits = self.home_head(arm2_feat).squeeze(-1)
        cop_logits  = self.cop_head(arm2_feat)

        return {
            "act_logits":  act_logits,
            "home_logits": home_logits,
            "cop_logits":  cop_logits,
            "aux_logits":  None,
            "mdlm_mask":   mask,
        }

    # ── Inference: iterative unmasking ──────────────────────────────────────

    @torch.no_grad()
    def infer(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata,
              apply_safety: bool = True):
        B = act_seq.shape[0]
        T = self.n_slots
        device = act_seq.device

        cur_act = torch.zeros(B, T, dtype=torch.long, device=device)
        mask    = torch.ones(B, T, dtype=torch.bool, device=device)

        for step in range(N_DENOISE_STEPS):
            masked_emb = self._embed_with_mask(cur_act, mask)
            slot_input = torch.cat([masked_emb, aux_seq], dim=-1)
            slot_emb   = self.slot_linear(slot_input)
            slot_emb   = slot_emb + self.enc_pos_enc[:, 1:, :]
            cycle_emb  = self.cycle_embedding(cycle_idx)
            cls_tok    = self.cls_mlp(torch.cat([cond_vec, cycle_emb], dim=-1)).unsqueeze(1)
            cls_tok    = cls_tok + self.enc_pos_enc[:, :1, :]
            memory     = self.encoder(torch.cat([cls_tok, slot_emb], dim=1))

            logits = self._refine_x0(memory)
            new_act = logits.argmax(dim=-1)

            frac_reveal = (step + 1) / N_DENOISE_STEPS
            frac_keep_mask = 1.0 - frac_reveal
            confidence = logits.max(dim=-1).values
            confidence = confidence.masked_fill(~mask, -1e9)
            n_to_unmask = int(round((1.0 - frac_keep_mask) * T))
            topk = confidence.topk(min(n_to_unmask, T), dim=-1).indices
            commit = torch.zeros_like(mask)
            commit.scatter_(1, topk, True)
            commit = commit & mask
            cur_act = torch.where(commit, new_act, cur_act)
            mask = mask & ~commit

        if mask.any():
            cur_act = torch.where(mask, logits.argmax(dim=-1), cur_act)

        clean_memory = self._encode(act_seq, aux_seq, cond_vec, cycle_idx,
                                    tgt_strata=tgt_strata)
        act_probs = F.one_hot(cur_act, num_classes=self.n_act).float()
        arm2_feat = self._arm2_fuse(clean_memory, act_probs, cond_vec, cycle_idx, tgt_strata)
        home_logits = self.home_head(arm2_feat).squeeze(-1)
        gen_home = (torch.sigmoid(home_logits) > 0.5).float()
        cop_prob = torch.sigmoid(self.cop_head(arm2_feat))

        if apply_safety:
            cop_prob = cop_prob.clone()
            cop_prob[:, :, self.SPOUSE_IDX] *= gen_home

        return cur_act, gen_home, cop_prob
