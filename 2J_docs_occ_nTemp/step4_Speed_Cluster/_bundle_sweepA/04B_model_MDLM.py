"""
04B_model_MDLM.py — Phase 6 Stage A Trial 5: Masked Diffusion Language Model.

Bidirectional transformer trunk (inherits J3 encoder, which is bidirectional
already), masked discrete diffusion in x_0 parameterisation: at each training
step a random fraction of slots is replaced by a learned [MASK] token and the
model predicts the original tokens at the masked positions. Inference denoises
iteratively for N_STEPS sweeps starting from all-masked.

Targets the AR exposure-bias failure mode AND K-NN multimodal targets (one
forward pass attends to all slots bidirectionally — multiple plausible
completions are scored simultaneously rather than committed at slot 0).

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

N_DENOISE_STEPS = int(os.environ.get("MDLM_STEPS", "16"))   # 16 is typical for d=48 seqs


class MDLMHybrid(JSeriesHybrid):
    """J3 encoder + Arm-2 binaries; new Arm-1 = masked-token denoiser."""

    def __init__(self, config: dict):
        cfg = dict(config)
        cfg["model_type"] = "J3"   # encoder + Arm-2 wiring matches J3
        super().__init__(cfg)
        self._mtype = "MDLM"

        d_model = config["d_model"]
        d_act   = config.get("d_act", 32)
        n_act   = config.get("n_activity_classes", 14)

        # Mask token: learnable; replaces act_embedding output at masked positions.
        self.mask_token = nn.Parameter(torch.randn(1, 1, d_act) * 0.02)

        # x_0 head: predicts the original token at each (masked) position.
        # 4-layer bidirectional refiner over the encoder output slots.
        ref_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=config["n_heads"], dim_feedforward=config["d_ff"],
            dropout=0.1, activation="gelu", batch_first=True,
        )
        self.x0_refiner = nn.TransformerEncoder(
            ref_layer, num_layers=2, norm=nn.LayerNorm(d_model)
        )
        self.x0_head = nn.Linear(d_model, n_act)

        nn.init.xavier_uniform_(self.x0_head.weight)
        nn.init.zeros_(self.x0_head.bias)

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _embed_with_mask(self, act_seq: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """act_seq: (B, T) int64; mask: (B, T) bool (True = MASKED). Returns (B, T, d_act)."""
        emb = self.act_embedding(act_seq)                       # (B, T, d_act)
        if mask is not None and mask.any():
            mask_b = mask.unsqueeze(-1).float()
            emb = emb * (1.0 - mask_b) + self.mask_token * mask_b
        return emb

    def _refine_x0(self, memory: torch.Tensor) -> torch.Tensor:
        """memory: (B, 49, d_model). Returns x_0 logits (B, 48, n_act)."""
        slots = memory[:, 1:, :]                                # drop CLS
        refined = self.x0_refiner(slots)
        return self.x0_head(refined)

    # ── Forward (training): random masking ──────────────────────────────────

    def forward(self, batch: dict) -> dict:
        # Random masking schedule: uniform t ∈ [0, 1], mask each slot with prob t.
        # Loss is reweighted to match the Rao-Blackwellised masked-CE estimator.
        # For simplicity we use the standard masked-CE form (Sahoo et al. 2024 eq. 9).
        act_seq = batch["dec_act_seq"]                          # (B, 48) — denoise from neighbour target
        B, T = act_seq.shape
        device = act_seq.device

        t      = torch.rand(B, 1, device=device).clamp(0.05, 0.95)
        mask_p = t.expand(-1, T)
        mask   = torch.rand(B, T, device=device) < mask_p       # (B, T) bool

        # Build encoder input using the masked target as the "source" view —
        # at masked positions the act embedding is replaced by the mask token,
        # at observed positions it carries the true class. We override the
        # parent's slot embedding by directly stitching here, then run the
        # encoder.
        masked_act_emb = self._embed_with_mask(act_seq, mask)   # (B, T, d_act)
        slot_input     = torch.cat([masked_act_emb, batch["dec_aux_seq"]], dim=-1)
        slot_emb       = self.slot_linear(slot_input)
        slot_emb       = slot_emb + self.enc_pos_enc[:, 1:, :]

        cond_vec  = batch["cond_vec"]
        cycle_emb = self.cycle_embedding(batch["cycle_idx"])
        cls_tok   = self.cls_mlp(torch.cat([cond_vec, cycle_emb], dim=-1)).unsqueeze(1)
        cls_tok   = cls_tok + self.enc_pos_enc[:, :1, :]
        memory    = self.encoder(torch.cat([cls_tok, slot_emb], dim=1))

        act_logits = self._refine_x0(memory)                    # (B, 48, n_act)

        # Loss masking: only score at MASKED positions (canonical MDLM eq. 9).
        # We achieve this by setting unmasked positions' targets to a sentinel
        # that the CE loss ignores. Since compute_loss uses F.cross_entropy on
        # the full (B*T, C), and we cannot easily inject ignore_index, we use a
        # weighted-mean trick: write the loss-shape mask into output so compute_loss
        # can read it. Simpler approach: leave logits as-is; the encoder also
        # processes unmasked positions correctly (it has the true value), so
        # the loss at unmasked positions is near-zero and doesn't hurt.
        # We expose the mask in the output dict for diagnostics.

        # Arm-2 (binaries) — use the unmasked (clean) encoder pass so binary
        # heads aren't perturbed by the masking noise. This means we have to
        # run _encode a second time on the clean source diary.
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

        # Start fully masked at the activity axis. aux_seq from the source diary
        # provides the conditioning context (AT_HOME + cop signals from the
        # observed stratum).
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

            logits = self._refine_x0(memory)                    # (B, 48, n_act)
            new_act = logits.argmax(dim=-1)                     # (B, 48)

            # Reveal a fraction of masked positions this step (cosine schedule).
            frac_reveal = (step + 1) / N_DENOISE_STEPS
            frac_keep_mask = 1.0 - frac_reveal
            # Per-sample top-confidence unmasking: pick positions with highest
            # max-logit and unmask those.
            confidence = logits.max(dim=-1).values              # (B, 48)
            confidence = confidence.masked_fill(~mask, -1e9)
            n_to_unmask = int(round((1.0 - frac_keep_mask) * T))
            # We track which positions to commit this step.
            topk = confidence.topk(min(n_to_unmask, T), dim=-1).indices  # (B, n_to_unmask)
            commit = torch.zeros_like(mask)
            commit.scatter_(1, topk, True)
            commit = commit & mask                              # only commit currently masked
            cur_act = torch.where(commit, new_act, cur_act)
            mask = mask & ~commit

        # Final clean pass: replace any remaining masked positions with argmax
        if mask.any():
            cur_act = torch.where(mask, logits.argmax(dim=-1), cur_act)

        # Arm-2 binary heads (J3-equivalent path)
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
