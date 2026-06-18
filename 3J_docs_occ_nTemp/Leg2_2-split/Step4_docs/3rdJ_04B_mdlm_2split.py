# -*- coding: utf-8 -*-
"""
3rdJ_04B_mdlm_2split.py — Step 4B-MDLM (Leg-2): Masked Diffusion Language Model.

ABLATION BACKBONE vs. the AR baseline (3rdJ_04B_model_2split.py).
Implements MDLM (Sahoo et al. 2024, arXiv:2403.17983) with an absorbing-state
(masked-token) masking scheme for the 14-class activity sequence.

Design decisions (per dr_S4-03_architecture_choice_REPORT.md §5):
  1. BIDIRECTIONAL Transformer trunk — no causal mask.  The same conditioning
     covariates (demographics / cycle / strata) are injected as prefix tokens,
     identical to the AR baseline.
  2. VOCABULARY: the 14 activity classes (0-indexed) plus one MASK/absorbing
     token at index 14  → vocab_size = 15.  The mask token is NEVER present in
     the clean encoder input or in the final generated output.
  3. CLEAN-PASS FOR BINARY HEADS:
     During training and inference the binary heads (AT_HOME, AT_WORK,
     co-presence) are computed from a SEPARATE clean encoder pass on the
     UNMASKED activity sequence (teacher-forced ground truth at train time;
     denoised hard tokens at infer time).  This isolates the binary arms from
     masking noise (per report §3/§5).  The DETACH barrier is preserved: the
     soft activity probs fed into Arm-2 are detached from the MDLM denoising
     graph, same as the AR baseline.
  4. SAME d_model / n_heads / depth as AR DEFAULT_CONFIG for a fair ablation.
  5. Binary head structure identical to JSeriesHybrid2Split:
       home_head / work_head: Linear -> Tanh -> Linear -> 1 logit  (B,48)
       cop_head:              Linear -> Tanh -> Linear -> 9 logits (B,48,9)

Architecture:
  Trunk encoder:    shared 6-layer BiTransformerEncoder (sinusoidal PE,
                    demographic CLS token, NO causal mask)
  Noisy pass:       masked activity tokens → noisy_encoder → act_head (B,48,15)
                    → cross-entropy loss on masked positions only (MDLM objective)
  Clean pass:       unmasked activity tokens → clean_encoder → detach
                    → Arm-2 binary heads (home/work/cop)

Checkpoint compatibility: this model is NOT interchangeable with the AR model;
checkpoints are separate (outputs_step4/sweep/MDLM_s10/checkpoints/).

IMPORT:
    mdlm_mod = importlib.import_module("3rdJ_04B_mdlm_2split")
    MDLMOcc2Split = mdlm_mod.MDLMOcc2Split
    MASK_TOKEN = mdlm_mod.MASK_TOKEN

This file is imported, NOT run directly.
"""

from __future__ import annotations

import math
import os

import torch
import torch.nn as nn
import torch.nn.functional as F

# ── Constants ────────────────────────────────────────────────────────────────
N_AUX          = 11        # [AT_HOME | AT_WORK | 9 co-presence]
N_ACT_CLASSES  = 14        # real activity classes (0-indexed)
MASK_TOKEN     = 14        # absorbing / mask token index  → vocab_size = 15
VOCAB_SIZE     = N_ACT_CLASSES + 1   # 15

# ── Default / test configs (mirror AR baseline) ────────────────────────────────

DEFAULT_CONFIG = {
    "model_type":          "MDLM",
    "d_model":             256,
    "n_heads":             8,
    "d_ff":                1024,
    "N_enc":               6,
    "d_act":               32,
    "d_cycle":             32,
    "dropout":             0.1,
    "n_activity_classes":  14,
    "n_copresence":        9,
    "n_slots":             48,
    "d_cond":              None,   # set from step4_feature_config.json at runtime
}

TEST_CONFIG = {
    "model_type":          "MDLM",
    "d_model":             64,
    "n_heads":             2,
    "d_ff":                256,
    "N_enc":               2,
    "d_act":               16,
    "d_cycle":             16,
    "dropout":             0.1,
    "n_activity_classes":  14,
    "n_copresence":        9,
    "n_slots":             48,
    "d_cond":              None,
}


# ── Positional encoding ────────────────────────────────────────────────────────

def sinusoidal_pos_enc(max_len: int, d_model: int) -> torch.Tensor:
    """Standard sinusoidal positional encoding. Returns (1, max_len, d_model)."""
    pe  = torch.zeros(1, max_len, d_model)
    pos = torch.arange(max_len, dtype=torch.float).unsqueeze(1)
    div = torch.exp(
        torch.arange(0, d_model, 2, dtype=torch.float) * (-math.log(10000.0) / d_model)
    )
    pe[0, :, 0::2] = torch.sin(pos * div)
    pe[0, :, 1::2] = torch.cos(pos * div)
    return pe


# ── Bidirectional Transformer encoder ─────────────────────────────────────────

class BidirectionalEncoder(nn.Module):
    """
    Shared bidirectional encoder used for BOTH the noisy pass and the clean pass.
    No causal mask is applied — every slot can attend to every other slot.

    Parameters
    ----------
    d_model, n_heads, n_layers, d_ff, d_cond, d_cycle, dropout: standard
    vocab_size: activity vocabulary size (15 = 14 classes + mask token)
    d_act: activity embedding dimension before projection
    n_slots: sequence length (48)
    n_aux: auxiliary channel width injected alongside activity in the clean pass
           (not used in the noisy pass, where aux is zeroed to avoid data leakage)
    """

    def __init__(self, d_model, n_heads, n_layers, d_ff,
                 d_cond, d_cycle, dropout, vocab_size,
                 d_act, n_slots, n_aux):
        super().__init__()
        self.d_model  = d_model
        self.n_slots  = n_slots
        self.n_aux    = n_aux

        # Activity token embedding (shared between noisy and clean calls).
        # vocab_size = 15 so the mask token (idx 14) has its own row.
        self.act_embedding = nn.Embedding(vocab_size, d_act)

        # Noisy-pass slot projection: activity embedding only (aux is masked/absent)
        self.slot_linear_noisy = nn.Linear(d_act, d_model)

        # Clean-pass slot projection: activity embedding + aux channels (width=n_aux)
        # Mirrors the AR baseline's slot_linear = Linear(d_act + n_aux, d_model).
        self.slot_linear_clean = nn.Linear(d_act + n_aux, d_model)

        # CLS token: cycle + demographic conditioning
        self.cycle_embedding = nn.Embedding(4, d_cycle)
        self.cls_mlp = nn.Sequential(
            nn.Linear(d_cond + d_cycle, 256),
            nn.GELU(),
            nn.Linear(256, d_model),
        )

        # Conditioning tokens injected as prefix: demo / cycle / strata
        # (same 3 tokens as the AR CrossAttnDecoder conditioning)
        self.proj_demo   = nn.Linear(d_cond, d_model)
        self.proj_cycle  = nn.Linear(d_cycle, d_model)
        self.proj_strata = nn.Linear(3, d_model)

        # Positional encodings: +1 slot for the CLS token; +3 for the cond prefix
        # Layout: [CLS | cond_demo | cond_cycle | cond_strata | slot_1 .. slot_48]
        self.register_buffer(
            "pos_enc", sinusoidal_pos_enc(n_slots + 4, d_model)
        )

        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_ff,
            dropout=dropout, activation="gelu", batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            enc_layer, num_layers=n_layers, norm=nn.LayerNorm(d_model)
        )

    def _build_prefix(self, cond_vec, cycle_idx, tgt_strata):
        """Build the 4 prefix tokens: [CLS, demo, cycle, strata]."""
        cycle_emb = self.cycle_embedding(cycle_idx)           # (B, d_cycle)
        cls_tok   = self.cls_mlp(
            torch.cat([cond_vec, cycle_emb], dim=-1)
        ).unsqueeze(1)                                        # (B, 1, d_model)

        strata_oh = F.one_hot(
            (tgt_strata - 1).clamp(0, 2), num_classes=3
        ).float()                                             # (B, 3)

        demo_tok   = self.proj_demo(cond_vec).unsqueeze(1)   # (B, 1, d_model)
        cycle_tok  = self.proj_cycle(cycle_emb).unsqueeze(1) # (B, 1, d_model)
        strata_tok = self.proj_strata(strata_oh).unsqueeze(1)# (B, 1, d_model)

        # Stack and add positional encodings for positions 0..3
        prefix = torch.cat([cls_tok, demo_tok, cycle_tok, strata_tok], dim=1)  # (B,4,d_model)
        prefix = prefix + self.pos_enc[:, :4, :]
        return prefix

    def forward_noisy(self, noisy_act_seq, cond_vec, cycle_idx, tgt_strata):
        """
        Noisy-pass forward (for the MDLM denoising objective).

        noisy_act_seq: (B, 48) int64 — some positions replaced by MASK_TOKEN (14).
        Returns memory (B, 52, d_model) — prefix(4) + slots(48).
        The slot embedding uses act_embedding + slot_linear_NOISY (no aux channels).
        """
        act_emb  = self.act_embedding(noisy_act_seq)         # (B,48,d_act)
        slot_emb = self.slot_linear_noisy(act_emb)           # (B,48,d_model)
        slot_emb = slot_emb + self.pos_enc[:, 4:4 + self.n_slots, :]

        prefix = self._build_prefix(cond_vec, cycle_idx, tgt_strata)
        seq    = torch.cat([prefix, slot_emb], dim=1)        # (B,52,d_model)
        return self.encoder(seq)

    def forward_clean(self, clean_act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata):
        """
        Clean-pass forward (for binary heads; no masking noise).

        clean_act_seq: (B, 48) int64 — original (unmasked) activity tokens.
        aux_seq:       (B, 48, 11) float32 — [AT_HOME | AT_WORK | co-presence].
        Returns memory (B, 52, d_model).
        The slot embedding uses act_embedding + slot_linear_CLEAN (with aux).
        """
        act_emb  = self.act_embedding(clean_act_seq)         # (B,48,d_act)
        slot_emb = self.slot_linear_clean(
            torch.cat([act_emb, aux_seq], dim=-1)
        )                                                     # (B,48,d_model)
        slot_emb = slot_emb + self.pos_enc[:, 4:4 + self.n_slots, :]

        prefix = self._build_prefix(cond_vec, cycle_idx, tgt_strata)
        seq    = torch.cat([prefix, slot_emb], dim=1)        # (B,52,d_model)
        return self.encoder(seq)


# ── Arm-2 fusion (shared with AR baseline structure) ─────────────────────────

class Arm2Fusion(nn.Module):
    """
    Per-slot NAT fusion block.  Mirrors JSeriesHybrid2Split._arm2_fuse + heads.
    Input:  clean memory slot tokens (B,48,d_model) + detached clean act_probs
            (B,48,n_act) + conditioning scalars.
    Output: arm2_feat (B,48,d_model) before binary heads.

    Binary heads (identical structure to AR baseline):
      home_head / work_head: Linear -> Tanh -> Linear -> 1 logit
      cop_head:              Linear -> Tanh -> Linear -> 9 logits
    """

    def __init__(self, d_model, d_cond, d_cycle, n_act, n_cop):
        super().__init__()
        self.cycle_embedding = None   # re-uses the shared one from BidirectionalEncoder
        self._d_cycle = d_cycle
        self._n_act   = n_act

        self.arm2_act_proj = nn.Linear(n_act, d_model)
        d_arm2_in = d_model + d_model + d_cond + d_cycle + 3
        self.arm2_proj = nn.Linear(d_arm2_in, d_model)

        self.home_head = nn.Sequential(
            nn.Linear(d_model, d_model), nn.Tanh(), nn.Linear(d_model, 1)
        )
        self.work_head = nn.Sequential(
            nn.Linear(d_model, d_model), nn.Tanh(), nn.Linear(d_model, 1)
        )
        self.cop_head = nn.Sequential(
            nn.Linear(d_model, d_model), nn.Tanh(), nn.Linear(d_model, n_cop)
        )

    def forward(self, clean_memory, act_probs, cond_vec, cycle_emb, tgt_strata):
        """
        clean_memory: (B, 52, d_model) — clean-pass encoder output
        act_probs:    (B, 48, n_act)   — detached soft activity probs (CLEAN pass)
        cycle_emb:    (B, d_cycle)
        tgt_strata:   (B,) long
        """
        T        = act_probs.shape[1]  # 48
        slots_mem = clean_memory[:, 4:, :]  # skip prefix tokens → (B,48,d_model)

        strata_oh = F.one_hot(
            (tgt_strata - 1).clamp(0, 2), num_classes=3
        ).float()  # (B,3)

        cond_b   = cond_vec.unsqueeze(1).expand(-1, T, -1)
        cycle_b  = cycle_emb.unsqueeze(1).expand(-1, T, -1)
        strata_b = strata_oh.unsqueeze(1).expand(-1, T, -1)

        act_emb  = self.arm2_act_proj(act_probs)   # (B,48,d_model)
        fused    = torch.cat([slots_mem, act_emb, cond_b, cycle_b, strata_b], dim=-1)
        return self.arm2_proj(fused)                # (B,48,d_model)


# ── MDLM main model ────────────────────────────────────────────────────────────

class MDLMOcc2Split(nn.Module):
    """
    Masked Diffusion Language Model for two-channel occupancy generation (Leg-2).

    Two-pass forward:
      1. NOISY PASS  — masked activity tokens → BiEncoder → act_head (logits over
                       VOCAB_SIZE=15).  Only masked positions contribute to the loss.
      2. CLEAN PASS  — original (unmasked) tokens → BiEncoder → DETACH → Arm-2
                       binary heads (home / work / cop).

    Training signature (batch dict keys):
        act_seq         (B,48) int64  — SOURCE diary activity (observed)
        aux_seq         (B,48,11) f32 — SOURCE diary aux (used by clean encoder)
        cond_vec        (B, d_cond) f32
        cycle_idx       (B,) int64
        dec_act_seq     (B,48) int64  — TARGET diary activity (teacher-forcing)
        dec_aux_seq     (B,48,11) f32 — TARGET diary aux
        tgt_strata      (B,) int64    — target day-type {1,2,3}
        noisy_act_seq   (B,48) int64  — dec_act_seq with masks applied (caller-provided)
        mask_pos        (B,48) bool   — True where token was replaced by MASK_TOKEN

    Note: noisy_act_seq and mask_pos are generated by the training loop
    (3rdJ_04D_mdlm_train_2split.py) using the chosen masking schedule.

    forward() returns:
        act_logits:   (B,48,15)  — raw logits over VOCAB_SIZE (mask included)
        home_logits:  (B,48)     — raw AT_HOME logits
        work_logits:  (B,48)     — raw AT_WORK logits
        cop_logits:   (B,48,9)   — raw co-presence logits
        mask_pos:     (B,48)     — echoed back for loss computation convenience
    """

    SPOUSE_IDX     = 1
    COLLEAGUES_IDX = 8

    def __init__(self, config: dict):
        super().__init__()

        d_model = config["d_model"]
        n_heads = config["n_heads"]
        d_ff    = config["d_ff"]
        N_enc   = config["N_enc"]
        d_act   = config.get("d_act", 32)
        d_cycle = config.get("d_cycle", 32)
        dropout = config.get("dropout", 0.1)
        n_act   = config.get("n_activity_classes", N_ACT_CLASSES)
        n_cop   = config.get("n_copresence", 9)
        n_slots = config.get("n_slots", 48)
        n_aux   = config.get("n_aux", N_AUX)
        d_cond  = config["d_cond"]

        self.d_model = d_model
        self.n_slots = n_slots
        self.n_act   = n_act
        self.n_cop   = n_cop
        self.n_aux   = n_aux
        self.d_cycle = d_cycle

        # Shared bidirectional encoder (used for both passes)
        self.encoder = BidirectionalEncoder(
            d_model=d_model, n_heads=n_heads, n_layers=N_enc, d_ff=d_ff,
            d_cond=d_cond, d_cycle=d_cycle, dropout=dropout,
            vocab_size=VOCAB_SIZE,
            d_act=d_act, n_slots=n_slots, n_aux=n_aux,
        )

        # Activity prediction head (noisy pass → denoising objective)
        self.act_head = nn.Linear(d_model, VOCAB_SIZE)

        # Arm-2 cycle embedding (shared with encoder's cycle_embedding to save params)
        # Point to the same object to avoid duplicating parameters.
        self._cycle_embedding = self.encoder.cycle_embedding

        # Arm-2 fusion + binary heads
        self.arm2 = Arm2Fusion(
            d_model=d_model, d_cond=d_cond, d_cycle=d_cycle,
            n_act=n_act, n_cop=n_cop,
        )

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.02)

    # ── Forward (teacher-forcing, training) ──────────────────────────────────

    def forward(self, batch: dict) -> dict:
        """
        Two-pass forward.

        Noisy pass:
            Uses batch["noisy_act_seq"] (B,48) which has some positions replaced
            by MASK_TOKEN (14).  Conditions on TARGET strata (tgt_strata) so the
            model learns to denoise conditioned on the correct day-type.

        Clean pass:
            Uses batch["dec_act_seq"] (the ground-truth target activity, unmasked)
            and batch["dec_aux_seq"] (the target aux channels).  Also conditioned
            on tgt_strata.  Output is DETACHED before Arm-2 to preserve the
            decoupled gradient flow of the AR baseline.
        """
        noisy_act = batch["noisy_act_seq"]    # (B,48) — with mask tokens
        clean_act = batch["dec_act_seq"]      # (B,48) — unmasked ground truth
        clean_aux = batch["dec_aux_seq"]      # (B,48,11)
        cond_vec  = batch["cond_vec"]
        cycle_idx = batch["cycle_idx"]
        tgt_strata = batch["tgt_strata"]

        # ── Noisy pass ───────────────────────────────────────────────────────
        noisy_mem  = self.encoder.forward_noisy(noisy_act, cond_vec, cycle_idx, tgt_strata)
        slot_noisy = noisy_mem[:, 4:, :]      # (B,48,d_model) — skip prefix
        act_logits = self.act_head(slot_noisy) # (B,48,15)

        # ── Clean pass ───────────────────────────────────────────────────────
        clean_mem  = self.encoder.forward_clean(clean_act, clean_aux, cond_vec, cycle_idx, tgt_strata)
        slot_clean = clean_mem[:, 4:, :]      # (B,48,d_model) — skip prefix

        # Soft probs from CLEAN pass (only the 14 real classes, no mask class)
        clean_logits_14 = self.act_head(slot_clean)[..., :self.n_act]  # (B,48,14)
        act_probs_clean = F.softmax(clean_logits_14.detach(), dim=-1)  # DETACH barrier

        # Arm-2 fusion
        cycle_emb  = self._cycle_embedding(cycle_idx)
        arm2_feat  = self.arm2(clean_mem, act_probs_clean, cond_vec, cycle_emb, tgt_strata)

        return {
            "act_logits":  act_logits,                                  # (B,48,15)
            "home_logits": self.arm2.home_head(arm2_feat).squeeze(-1),  # (B,48)
            "work_logits": self.arm2.work_head(arm2_feat).squeeze(-1),  # (B,48)
            "cop_logits":  self.arm2.cop_head(arm2_feat),               # (B,48,9)
            "mask_pos":    batch["mask_pos"],                           # (B,48) bool
        }

    # ── Denoise loop (inference) ──────────────────────────────────────────────

    @torch.no_grad()
    def denoise(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata,
                n_steps: int = 16,
                schedule: str = "cosine",
                temperature: float = 0.8):
        """
        Iterative masked-diffusion denoising for activity sequence generation.

        Strategy (absorbing-state MDLM inference):
          - Start from fully masked sequence.
          - At each step t (from T down to 0) predict the clean token at each
            masked position and unmask a fraction of them.
          - The fraction unmasked per step follows the chosen schedule.
          - Binary heads are computed from the CLEAN (fully denoised) pass at
            the end (one extra forward pass with no masks).

        Parameters
        ----------
        act_seq    (B,48) int64  — SOURCE diary activity (encoder context)
        aux_seq    (B,48,11)     — SOURCE diary aux (encoder context)
        cond_vec   (B,d_cond)
        cycle_idx  (B,) int64
        tgt_strata (B,) int64
        n_steps    int           — number of denoising steps (default 16)
        schedule   str           — 'cosine' or 'linear'
        temperature float        — sampling temperature for activity tokens

        Returns
        -------
        gen_act   (B,48) int64   — final activity tokens in {0..13}
        gen_home  (B,48) float32 — binary AT_HOME
        gen_work  (B,48) float32 — binary AT_WORK
        gen_cop   (B,48,9) float32 — binary co-presence (threshold 0.5)
        gen_cop_probs (B,48,9) float32 — raw sigmoid co-presence
        """
        B      = act_seq.shape[0]
        T      = self.n_slots
        device = act_seq.device

        # ── Build unmasked-ratio schedule ─────────────────────────────────────
        # unmask_fracs[t] = fraction of STILL-MASKED positions to unmask at step t.
        # We define cumulative unmasked fraction at step s: alpha(s) in [0..1].
        # At step s we want total unmasked = alpha(s)*T tokens.
        # Per-step conditional: unmask (alpha(s) - alpha(s-1)) / (1 - alpha(s-1))
        # of the remaining masked positions.

        steps = torch.linspace(0.0, 1.0, n_steps + 1)  # shape (n_steps+1,)
        if schedule == "cosine":
            alpha = 1.0 - torch.cos(steps * math.pi / 2)  # (0..1)
        else:
            alpha = steps  # linear

        # Start from fully masked
        x = torch.full((B, T), MASK_TOKEN, dtype=torch.long, device=device)

        for s in range(1, n_steps + 1):
            # Predict clean token at all positions
            noisy_mem  = self.encoder.forward_noisy(x, cond_vec, cycle_idx, tgt_strata)
            slot_out   = noisy_mem[:, 4:, :]              # (B,48,d_model)
            logits_15  = self.act_head(slot_out)           # (B,48,15)
            # Only the 14 real classes can be sampled (mask token cannot be output)
            logits_14  = logits_15[..., :self.n_act]       # (B,48,14)

            if temperature and temperature > 0:
                probs    = F.softmax(logits_14 / temperature, dim=-1)
                # Sample independently per (batch, slot)
                probs_2d = probs.reshape(B * T, self.n_act)
                pred     = torch.multinomial(probs_2d, 1).reshape(B, T)
            else:
                pred = logits_14.argmax(-1)  # (B,48)

            # Determine which fraction to unmask this step
            # Still-masked positions (value == MASK_TOKEN)
            still_masked = (x == MASK_TOKEN)             # (B,48) bool

            a_prev = alpha[s - 1].item()
            a_curr = alpha[s].item()
            denom  = 1.0 - a_prev
            if denom < 1e-9:
                cond_frac = 1.0
            else:
                cond_frac = (a_curr - a_prev) / denom
            cond_frac = min(max(cond_frac, 0.0), 1.0)

            # At the last step force full unmask
            if s == n_steps:
                cond_frac = 1.0

            # For each batch element, randomly choose cond_frac of masked positions
            # to unmask (using uniform noise as a tie-breaker / random selection).
            noise = torch.rand(B, T, device=device)
            # Unmask positions where: still_masked AND noise < cond_frac
            to_unmask = still_masked & (noise < cond_frac)
            x = torch.where(to_unmask, pred, x)

        # ── Final cleanup: any remaining MASK_TOKEN -> argmax prediction ──────
        remaining = (x == MASK_TOKEN)
        if remaining.any():
            noisy_mem  = self.encoder.forward_noisy(x, cond_vec, cycle_idx, tgt_strata)
            slot_out   = noisy_mem[:, 4:, :]
            logits_14  = self.act_head(slot_out)[..., :self.n_act]
            x = torch.where(remaining, logits_14.argmax(-1), x)

        gen_act = x  # (B,48) in {0..13}

        # ── Clean pass for binary heads ───────────────────────────────────────
        # Use the denoised activity as the "clean" input to the encoder.
        # Aux input is zeroed here because we have no ground-truth aux at
        # inference time (the binary heads will output it themselves).
        zero_aux = torch.zeros(B, T, self.n_aux, device=device)
        clean_mem  = self.encoder.forward_clean(gen_act, zero_aux, cond_vec, cycle_idx, tgt_strata)
        slot_clean = clean_mem[:, 4:, :]
        clean_l14  = self.act_head(slot_clean)[..., :self.n_act]
        act_probs  = F.softmax(clean_l14, dim=-1)   # (B,48,14) — no detach needed at infer

        cycle_emb  = self._cycle_embedding(cycle_idx)
        arm2_feat  = self.arm2(clean_mem, act_probs, cond_vec, cycle_emb, tgt_strata)

        home_sigmoid = torch.sigmoid(self.arm2.home_head(arm2_feat).squeeze(-1))  # (B,48)
        work_sigmoid = torch.sigmoid(self.arm2.work_head(arm2_feat).squeeze(-1))  # (B,48)
        gen_home = (home_sigmoid > 0.5).float()
        gen_work = (work_sigmoid > 0.5).float()

        cop_probs = torch.sigmoid(self.arm2.cop_head(arm2_feat))  # (B,48,9)
        # Safety: Spouse co-presence suppressed when not AT_HOME
        cop_probs = cop_probs.clone()
        cop_probs[:, :, self.SPOUSE_IDX] *= gen_home
        gen_cop   = (cop_probs > 0.5).float()

        return gen_act, gen_home, gen_work, gen_cop, cop_probs
