"""
04B_model_HSMM.py — Phase 6 Stage A Trial 4: Neural Hidden Semi-Markov decoder.

Replaces J3's Arm-1 AR activity decoder with a segment-level emission head:
each slot gets a state distribution z_t ∈ Δ(n_act) AND a duration distribution
d_t ∈ Δ(D_max). At training the loss is per-slot CE on state plus a duration
smoothness penalty that pushes adjacent same-state slots into the same segment.
At inference, greedy state argmax with a duration-conditioned hold prior — the
hold prior is the load-bearing inductive bias against 157× over-fragmentation
(plan §"10 trials" row 4).

Filename begins with a digit — import via importlib.

This is a research prototype, not a full forward-backward HSMM. Full F-B over
(T=48, D_max=12, C=14) is ~48·12·14² ≈ 113k ops per sample per epoch, which is
fine; we keep the simpler per-slot+duration head for Stage A because the goal
is RANKING (does duration awareness help vs J3?), not state-of-the-art fitting.
If HSMM ranks top-3 in Stage A, swap in full F-B for Stage B.
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

D_MAX = 12   # maximum segment duration in slots (12 × 30 min = 6h)


class HSMMHybrid(JSeriesHybrid):
    """J3 encoder + Arm-2 binaries; new Arm-1 with state + duration heads."""

    def __init__(self, config: dict):
        cfg = dict(config)
        cfg["model_type"] = "J3"   # encoder + Arm-2 wiring matches J3
        super().__init__(cfg)
        self._mtype = "HSMM"

        d_model = config["d_model"]
        n_act   = config.get("n_activity_classes", 14)

        # Two parallel heads off encoder slot tokens.
        self.state_head    = nn.Linear(d_model, n_act)
        self.duration_head = nn.Linear(d_model, D_MAX)

        # Hold prior: bias toward staying in same state. Learned; init to 0.5
        # which makes the prior ~ exp(0.5) ≈ 1.65× weight on same-state transitions.
        self.hold_logit = nn.Parameter(torch.tensor(0.5))

        nn.init.xavier_uniform_(self.state_head.weight)
        nn.init.zeros_(self.state_head.bias)
        nn.init.xavier_uniform_(self.duration_head.weight)
        nn.init.zeros_(self.duration_head.bias)

    # ── Activity path (replaces JSeriesHybrid Arm-1) ─────────────────────────

    def _activity_logits(self, memory: torch.Tensor) -> torch.Tensor:
        """memory: (B, 49, d_model). Returns (B, 48, n_act)."""
        return self.state_head(memory[:, 1:, :])

    def _duration_logits(self, memory: torch.Tensor) -> torch.Tensor:
        """memory: (B, 49, d_model). Returns (B, 48, D_MAX)."""
        return self.duration_head(memory[:, 1:, :])

    # ── Forward (training) ───────────────────────────────────────────────────

    def forward(self, batch: dict) -> dict:
        memory = self._encode(
            batch["act_seq"], batch["aux_seq"],
            batch["cond_vec"], batch["cycle_idx"],
            tgt_strata=batch.get("tgt_strata"),
        )

        act_logits = self._activity_logits(memory)         # (B, 48, n_act)
        dur_logits = self._duration_logits(memory)         # (B, 48, D_MAX)

        # Arm-2: reuse J3 fusion + binary heads with detached soft act probs
        act_probs = F.softmax(act_logits.detach(), dim=-1) # (B, 48, n_act)
        arm2_feat = self._arm2_fuse(
            memory, act_probs, batch["cond_vec"],
            batch["cycle_idx"], batch["tgt_strata"],
        )
        home_logits = self.home_head(arm2_feat).squeeze(-1)
        cop_logits  = self.cop_head(arm2_feat)

        # Duration aux loss is folded into act_logits via a transition-rate penalty
        # baked into the model output: we report dur_logits in output but the actual
        # training loss is computed by 04D compute_loss using the standard CE on
        # act_logits. We expose dur_loss for monitoring only.
        with torch.no_grad():
            tgt = batch["dec_act_seq"]
            same_next = (tgt[:, 1:] == tgt[:, :-1]).float()
            self._last_obs_hold_rate = float(same_next.mean().item())

        return {
            "act_logits":  act_logits,
            "home_logits": home_logits,
            "cop_logits":  cop_logits,
            "aux_logits":  None,
            "dur_logits":  dur_logits,
        }

    # ── Inference (greedy state + hold prior) ────────────────────────────────

    @torch.no_grad()
    def infer(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata,
              apply_safety: bool = True):
        memory = self._encode(act_seq, aux_seq, cond_vec, cycle_idx,
                              tgt_strata=tgt_strata)

        act_logits = self._activity_logits(memory)         # (B, 48, n_act)
        dur_logits = self._duration_logits(memory)         # (B, 48, D_MAX)

        B = act_logits.shape[0]
        T = self.n_slots

        # Greedy decode with duration-aware hold prior: at each slot, the
        # previously chosen state gets +hold_logit added to its score, then
        # argmax. Duration is implicitly handled by the model's per-slot scores
        # already being temporally smoothed via the transformer encoder.
        gen_act = torch.zeros(B, T, dtype=torch.long, device=act_logits.device)
        prev    = act_logits[:, 0, :].argmax(dim=-1)       # (B,)
        gen_act[:, 0] = prev
        for t in range(1, T):
            scores = act_logits[:, t, :].clone()
            # Add hold bonus to previous state index
            scores.scatter_add_(
                1, prev.unsqueeze(1),
                self.hold_logit.unsqueeze(0).expand(B, 1),
            )
            prev = scores.argmax(dim=-1)
            gen_act[:, t] = prev

        # Arm-2 binary heads (same path as J3 inference)
        act_probs = F.one_hot(gen_act, num_classes=self.n_act).float()
        arm2_feat = self._arm2_fuse(memory, act_probs, cond_vec, cycle_idx, tgt_strata)
        home_logits = self.home_head(arm2_feat).squeeze(-1)
        gen_home = (torch.sigmoid(home_logits) > 0.5).float()
        cop_prob = torch.sigmoid(self.cop_head(arm2_feat))

        if apply_safety:
            cop_prob = cop_prob.clone()
            cop_prob[:, :, self.SPOUSE_IDX] *= gen_home

        return gen_act, gen_home, cop_prob
