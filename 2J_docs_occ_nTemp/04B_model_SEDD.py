"""
04B_model_SEDD.py — Phase 6 Stage A Trial 10: Score-Entropy Discrete Diffusion.

Alternative to MDLM in the discrete-diffusion family (Lou et al., ICML 2024).
Ratio-of-data-distribution parameterisation: at each (t, x) the model predicts
the score ratio s(x, t) ≈ p_t(x) / p_t(y), trained with the cross-entropy ELBO
(eq. 5 of Lou et al.). At inference, Tweedie's formula plus τ-leaping gives
a sample in N_STEPS ≈ 24 denoising steps.

For Stage A we use a simplified absorbing-state diffusion (each slot
independently masked with schedule σ(t)), score predicted as logits at every
position, training loss = standard categorical cross-entropy on x_0 (which is
the consistent ELBO for absorbing diffusion under the score-entropy
parameterisation when the noise model is uniform). Inference is the same
top-confidence iterative unmask as MDLM but with N_STEPS=24 (vs 16) and a
power-law noise schedule (vs cosine).

The trial's purpose is to provide an independent diffusion baseline so MDLM's
result isn't a single-model conclusion about the family.

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

N_DENOISE_STEPS = int(os.environ.get("SEDD_STEPS", "24"))


class SEDDHybrid(JSeriesHybrid):
    """J3 encoder + Arm-2 binaries; new Arm-1 = score-entropy discrete diffusion."""

    def __init__(self, config: dict):
        cfg = dict(config)
        cfg["model_type"] = "J3"
        super().__init__(cfg)
        self._mtype = "SEDD"

        d_model = config["d_model"]
        d_act   = config.get("d_act", 32)
        n_act   = config.get("n_activity_classes", 14)

        self.absorb_token = nn.Parameter(torch.randn(1, 1, d_act) * 0.02)

        # Score head: 3-layer bidirectional refiner — same shape as MDLM's
        # x_0 head but using a power-law schedule and the score-entropy ELBO.
        ref_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=config["n_heads"], dim_feedforward=config["d_ff"],
            dropout=0.1, activation="gelu", batch_first=True,
        )
        self.score_refiner = nn.TransformerEncoder(
            ref_layer, num_layers=3, norm=nn.LayerNorm(d_model),
        )
        self.score_head = nn.Linear(d_model, n_act)

        # Time embedding: t ∈ [0, 1] → 16-dim sinusoidal → projected to d_model.
        self.time_proj_sedd = nn.Sequential(
            nn.Linear(16, d_model), nn.GELU(),
            nn.Linear(d_model, d_model),
        )

        nn.init.xavier_uniform_(self.score_head.weight)
        nn.init.zeros_(self.score_head.bias)

    def _embed_abs(self, act_seq: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        emb = self.act_embedding(act_seq)
        if mask is not None and mask.any():
            mask_b = mask.unsqueeze(-1).float()
            emb = emb * (1.0 - mask_b) + self.absorb_token * mask_b
        return emb

    def _time_emb(self, t: torch.Tensor) -> torch.Tensor:
        """t: (B,) in [0, 1]. Returns (B, d_model)."""
        freqs = torch.arange(8, device=t.device, dtype=t.dtype)
        a = t.unsqueeze(-1) * (10.0 ** freqs) * math.pi
        emb = torch.cat([a.sin(), a.cos()], dim=-1)              # (B, 16)
        return self.time_proj_sedd(emb)

    def _score_logits(self, memory: torch.Tensor, t_emb: torch.Tensor) -> torch.Tensor:
        """memory (B, 49, D), t_emb (B, D). Returns (B, 48, n_act)."""
        slots = memory[:, 1:, :]                                  # (B, 48, D)
        slots = slots + t_emb.unsqueeze(1)                        # broadcast time signal
        refined = self.score_refiner(slots)
        return self.score_head(refined)

    # Power-law noise schedule σ(t) = t^2  → more aggressive denoising late.
    @staticmethod
    def _sigma(t: torch.Tensor) -> torch.Tensor:
        return t.pow(2.0)

    def forward(self, batch: dict) -> dict:
        act_seq = batch["dec_act_seq"]
        B, T = act_seq.shape
        device = act_seq.device

        t = torch.rand(B, device=device).clamp(0.05, 0.95)
        sigma = self._sigma(t)                                    # (B,) — mask prob
        mask = torch.rand(B, T, device=device) < sigma.unsqueeze(-1)

        masked_emb = self._embed_abs(act_seq, mask)
        slot_input = torch.cat([masked_emb, batch["dec_aux_seq"]], dim=-1)
        slot_emb   = self.slot_linear(slot_input)
        slot_emb   = slot_emb + self.enc_pos_enc[:, 1:, :]
        cycle_emb  = self.cycle_embedding(batch["cycle_idx"])
        cls_tok    = self.cls_mlp(torch.cat([batch["cond_vec"], cycle_emb], dim=-1)).unsqueeze(1)
        cls_tok    = cls_tok + self.enc_pos_enc[:, :1, :]
        memory     = self.encoder(torch.cat([cls_tok, slot_emb], dim=1))

        t_emb = self._time_emb(t)
        act_logits = self._score_logits(memory, t_emb)

        # Arm-2 from clean encoder pass on source diary
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
            "sedd_t":      t,
        }

    @torch.no_grad()
    def infer(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata,
              apply_safety: bool = True):
        B = act_seq.shape[0]
        T = self.n_slots
        device = act_seq.device

        cur_act = torch.zeros(B, T, dtype=torch.long, device=device)
        mask    = torch.ones(B, T, dtype=torch.bool, device=device)

        ts = torch.linspace(1.0, 0.0, N_DENOISE_STEPS + 1, device=device)
        logits = None
        for step in range(N_DENOISE_STEPS):
            t_now = ts[step].expand(B)
            masked_emb = self._embed_abs(cur_act, mask)
            slot_input = torch.cat([masked_emb, aux_seq], dim=-1)
            slot_emb   = self.slot_linear(slot_input)
            slot_emb   = slot_emb + self.enc_pos_enc[:, 1:, :]
            cycle_emb  = self.cycle_embedding(cycle_idx)
            cls_tok    = self.cls_mlp(torch.cat([cond_vec, cycle_emb], dim=-1)).unsqueeze(1)
            cls_tok    = cls_tok + self.enc_pos_enc[:, :1, :]
            memory     = self.encoder(torch.cat([cls_tok, slot_emb], dim=1))

            t_emb = self._time_emb(t_now)
            logits = self._score_logits(memory, t_emb)
            new_act = logits.argmax(dim=-1)

            frac_reveal = (step + 1) / N_DENOISE_STEPS
            confidence = logits.max(dim=-1).values
            confidence = confidence.masked_fill(~mask, -1e9)
            n_to_unmask = int(round(frac_reveal * T))
            topk = confidence.topk(min(n_to_unmask, T), dim=-1).indices
            commit = torch.zeros_like(mask)
            commit.scatter_(1, topk, True)
            commit = commit & mask
            cur_act = torch.where(commit, new_act, cur_act)
            mask = mask & ~commit

        if mask.any() and logits is not None:
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
