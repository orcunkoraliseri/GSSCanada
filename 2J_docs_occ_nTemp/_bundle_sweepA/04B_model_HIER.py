"""
04B_model_HIER.py — Phase 6 Stage A Trial 6: Hierarchical coarse → refine.

Two-level decoder. Coarse head predicts a single activity per 12-slot block
(N_BLOCKS=4 blocks × 12 slots/block = 48 slots; matches plan "4-8 schedule
blocks"). Refine head takes coarse block prediction + position-in-block as
input and outputs the per-slot activity. The coarse → refine factorisation
commits to a block-level activity early, biasing the model toward longer
runs of the same activity — the target failure mode (transition rate 157×).

Filename begins with a digit — import via importlib.
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

N_BLOCKS = 4                       # 4 blocks × 12 slots = 48
BLOCK_SIZE = 12


class HIERHybrid(JSeriesHybrid):
    """J3 encoder + Arm-2 binaries; new Arm-1 = coarse block → refine."""

    def __init__(self, config: dict):
        cfg = dict(config)
        cfg["model_type"] = "J3"
        super().__init__(cfg)
        self._mtype = "HIER"

        d_model = config["d_model"]
        n_act   = config.get("n_activity_classes", 14)
        self.n_blocks   = N_BLOCKS
        self.block_size = BLOCK_SIZE

        # Coarse head: pool 12 slot tokens → one block representation → n_act logits.
        self.coarse_pool = nn.Sequential(
            nn.Linear(d_model, d_model), nn.GELU(),
            nn.Linear(d_model, n_act),
        )

        # Refine head: per-slot embedding fused with one-hot block prediction
        # (n_act) and within-block position (BLOCK_SIZE).
        self.refine_proj = nn.Linear(d_model + n_act + BLOCK_SIZE, d_model)
        self.refine_head = nn.Linear(d_model, n_act)

        for m in [self.refine_proj, self.refine_head, self.coarse_pool[0], self.coarse_pool[2]]:
            nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                nn.init.zeros_(m.bias)

    # ── Coarse → refine ──────────────────────────────────────────────────────

    def _coarse_logits(self, memory: torch.Tensor) -> torch.Tensor:
        """memory: (B, 49, d_model) → (B, N_BLOCKS, n_act)."""
        slots = memory[:, 1:, :]                                # (B, 48, d_model)
        B, T, D = slots.shape
        # Reshape (B, 48, D) → (B, 4, 12, D), mean-pool over slot dim.
        pooled = slots.reshape(B, N_BLOCKS, BLOCK_SIZE, D).mean(dim=2)  # (B, 4, D)
        return self.coarse_pool(pooled)                                  # (B, 4, n_act)

    def _refine_logits(self, memory: torch.Tensor, coarse_logits: torch.Tensor) -> torch.Tensor:
        """memory: (B, 49, d_model); coarse: (B, N_BLOCKS, n_act). Returns (B, 48, n_act)."""
        slots = memory[:, 1:, :]                                # (B, 48, d_model)
        B, T, D = slots.shape
        # Broadcast coarse predictions to each slot in their block.
        coarse_soft = F.softmax(coarse_logits.detach(), dim=-1)  # (B, 4, n_act)
        coarse_per_slot = coarse_soft.unsqueeze(2).expand(-1, -1, BLOCK_SIZE, -1)  # (B, 4, 12, n_act)
        coarse_per_slot = coarse_per_slot.reshape(B, T, -1)      # (B, 48, n_act)
        # Within-block position one-hot
        pos_idx = torch.arange(T, device=slots.device) % BLOCK_SIZE   # (T,)
        pos_oh  = F.one_hot(pos_idx, num_classes=BLOCK_SIZE).float()   # (T, 12)
        pos_oh  = pos_oh.unsqueeze(0).expand(B, -1, -1)                # (B, T, 12)

        fused   = torch.cat([slots, coarse_per_slot, pos_oh], dim=-1)
        refined = self.refine_proj(fused)
        return self.refine_head(refined)                          # (B, 48, n_act)

    # ── Forward ─────────────────────────────────────────────────────────────

    def forward(self, batch: dict) -> dict:
        memory = self._encode(
            batch["act_seq"], batch["aux_seq"],
            batch["cond_vec"], batch["cycle_idx"],
            tgt_strata=batch.get("tgt_strata"),
        )

        coarse_logits = self._coarse_logits(memory)                # (B, 4, n_act)
        act_logits    = self._refine_logits(memory, coarse_logits) # (B, 48, n_act)

        # Arm-2 binary heads from clean act probs (J3 path)
        act_probs = F.softmax(act_logits.detach(), dim=-1)
        arm2_feat = self._arm2_fuse(
            memory, act_probs, batch["cond_vec"],
            batch["cycle_idx"], batch["tgt_strata"],
        )
        home_logits = self.home_head(arm2_feat).squeeze(-1)
        cop_logits  = self.cop_head(arm2_feat)

        return {
            "act_logits":    act_logits,
            "home_logits":   home_logits,
            "cop_logits":    cop_logits,
            "aux_logits":    None,
            "coarse_logits": coarse_logits,
        }

    # ── Inference ───────────────────────────────────────────────────────────

    @torch.no_grad()
    def infer(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata,
              apply_safety: bool = True):
        memory = self._encode(act_seq, aux_seq, cond_vec, cycle_idx,
                              tgt_strata=tgt_strata)
        coarse_logits = self._coarse_logits(memory)
        act_logits    = self._refine_logits(memory, coarse_logits)
        gen_act = act_logits.argmax(dim=-1)

        act_probs = F.one_hot(gen_act, num_classes=self.n_act).float()
        arm2_feat = self._arm2_fuse(memory, act_probs, cond_vec, cycle_idx, tgt_strata)
        home_logits = self.home_head(arm2_feat).squeeze(-1)
        gen_home = (torch.sigmoid(home_logits) > 0.5).float()
        cop_prob = torch.sigmoid(self.cop_head(arm2_feat))

        if apply_safety:
            cop_prob = cop_prob.clone()
            cop_prob[:, :, self.SPOUSE_IDX] *= gen_home

        return gen_act, gen_home, cop_prob
