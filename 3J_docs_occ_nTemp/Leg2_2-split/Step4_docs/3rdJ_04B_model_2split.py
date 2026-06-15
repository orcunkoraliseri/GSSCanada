# -*- coding: utf-8 -*-
"""
3rdJ_04B_model_2split.py — Step 4B (Leg-2): Two-Channel J3 Hybrid AR-Encoder.

Clean port of the 2nd-Journal production J3 model (JSeriesHybrid with the J3
arm2_act_proj fix) from:
    2J_docs_occ_nTemp/step4_Speed_Cluster/archive/04B_model_J3.py

LEG-2 DELTA (the only architectural change):
    A second binary occupancy head `work_head` (AT_WORK) is added to Arm 2,
    mirroring `home_head` exactly (Linear -> Tanh -> Linear -> 1 logit).
    The encoder slot embedding now consumes the width-11 aux token
    [AT_HOME | AT_WORK | 9 co-presence]: slot_linear = Linear(d_act + 11, d_model).
    The AR loop (Arm 1, activity) is byte-identical to J3.
    The DETACH BARRIER (softmax(act_logits.detach())) is preserved exactly.

Architecture (J3 faithful):
  Trunk:  shared 6-layer TransformerEncoder (sinusoidal PE, CLS demographic token).
  Arm 1:  6-layer CrossAttnDecoder, activity-only AR loop (no aux feedback).
  DETACH: act_probs = softmax(act_logits.detach(), dim=-1) before Arm 2.
  Arm 2:  per-slot NAT fusion -> Tanh-gated binary heads:
            home_head -> (B,48)        AT_HOME
            work_head -> (B,48)        AT_WORK   [LEG-2 NEW]
            cop_head  -> (B,48,9)      co-presence
          J3 detail: arm2_act_proj projects soft act probs (n_act -> d_model)
          before the Arm-2 concat.

forward(batch) -> {act_logits, home_logits, work_logits, cop_logits}.
Sigmoid is applied externally (loss / inference); heads emit raw logits.

IMPORTANT: filename starts with a digit -> import via importlib:
    model_mod = importlib.import_module("3rdJ_04B_model_2split")
    JSeriesHybrid2Split = model_mod.JSeriesHybrid2Split

This file is imported, NOT run directly.
"""

import math
import os

import torch
import torch.nn as nn
import torch.nn.functional as F

N_AUX = 11  # [AT_HOME | AT_WORK | 9 co-presence]


# ── Positional encoding ──────────────────────────────────────────────────────

def sinusoidal_pos_enc(max_len: int, d_model: int) -> torch.Tensor:
    """Standard sinusoidal positional encoding. Returns (1, max_len, d_model)."""
    pe = torch.zeros(1, max_len, d_model)
    pos = torch.arange(max_len, dtype=torch.float).unsqueeze(1)
    div = torch.exp(
        torch.arange(0, d_model, 2, dtype=torch.float) * (-math.log(10000.0) / d_model)
    )
    pe[0, :, 0::2] = torch.sin(pos * div)
    pe[0, :, 1::2] = torch.cos(pos * div)
    return pe


# ── Default / test hyperparameter configs (J3 production) ────────────────────

DEFAULT_CONFIG = {
    "model_type":          "J3",
    "d_model":             256,
    "n_heads":             8,
    "d_ff":                1024,
    "N_enc":               6,
    "N_dec":               6,
    "d_act":               32,
    "d_cycle":             32,
    "dropout":             0.1,
    "n_activity_classes":  14,
    "n_copresence":        9,
    "n_slots":             48,
    "d_cond":              None,  # set from step4_feature_config.json at runtime
}

TEST_CONFIG = {
    "model_type":          "J3",
    "d_model":             64,
    "n_heads":             2,
    "d_ff":                256,
    "N_enc":               2,
    "N_dec":               2,
    "d_act":               16,
    "d_cycle":             16,
    "dropout":             0.1,
    "n_activity_classes":  14,
    "n_copresence":        9,
    "n_slots":             48,
    "d_cond":              None,
}


# ── Cross-attention conditioning decoder (J3 Arm-1) ──────────────────────────

class CondCrossAttnDecoderLayer(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, dropout=0.0):
        super().__init__()
        self.self_attn  = nn.MultiheadAttention(d_model, n_heads, dropout=dropout, batch_first=True)
        self.cross_mem  = nn.MultiheadAttention(d_model, n_heads, dropout=dropout, batch_first=True)
        self.cross_cond = nn.MultiheadAttention(d_model, n_heads, dropout=dropout, batch_first=True)
        self.ffn = nn.Sequential(nn.Linear(d_model, d_ff), nn.GELU(), nn.Linear(d_ff, d_model))
        self.ln1, self.ln2, self.ln3, self.ln4 = (nn.LayerNorm(d_model) for _ in range(4))
        self.drop = nn.Dropout(dropout)

    def forward(self, x, memory, cond_tokens, tgt_mask):
        x = x + self.drop(self.self_attn(self.ln1(x), self.ln1(x), self.ln1(x), attn_mask=tgt_mask, need_weights=False)[0])
        x = x + self.drop(self.cross_mem(self.ln2(x), memory, memory, need_weights=False)[0])
        x = x + self.drop(self.cross_cond(self.ln3(x), cond_tokens, cond_tokens, need_weights=False)[0])
        x = x + self.drop(self.ffn(self.ln4(x)))
        return x


class CrossAttnDecoder(nn.Module):
    def __init__(self, d_model, n_heads, n_layers, d_ff, d_cond, d_cycle, dropout=0.1):
        super().__init__()
        self.proj_demo   = nn.Linear(d_cond,  d_model)
        self.proj_cycle  = nn.Linear(d_cycle, d_model)
        self.proj_strata = nn.Linear(3,       d_model)
        self.layers = nn.ModuleList([
            CondCrossAttnDecoderLayer(d_model, n_heads, d_ff, dropout) for _ in range(n_layers)
        ])
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x, memory, cond_vec, cycle_emb, strata_oh, tgt_mask):
        cond_tokens = torch.stack([
            self.proj_demo(cond_vec),
            self.proj_cycle(cycle_emb),
            self.proj_strata(strata_oh),
        ], dim=1)                                    # (B, 3, d_model)
        for layer in self.layers:
            x = layer(x, memory, cond_tokens, tgt_mask)
        return self.norm(x)


# ── J3 Hybrid AR-Encoder (two-channel) ───────────────────────────────────────

class JSeriesHybrid2Split(nn.Module):
    """
    J3 Hybrid AR-Encoder with a second AT_WORK occupancy head (Leg-2).

    Trunk:  6-layer TransformerEncoder (shared); slot token absorbs width-11 aux.
    Arm 1:  CrossAttnDecoder, activity-only AR loop (no aux feedback) — J3 verbatim.
    Arm 2:  per-slot NAT fusion over detached soft activity probs -> 3 Tanh-gated
            heads: home_logits, work_logits (NEW), cop_logits.
    """

    SPOUSE_IDX     = 1
    COLLEAGUES_IDX = 8

    def __init__(self, config: dict):
        super().__init__()

        d_model = config["d_model"]
        n_heads = config["n_heads"]
        d_ff    = config["d_ff"]
        N_enc   = config["N_enc"]
        N_dec   = config.get("N_dec", 6)
        d_act   = config.get("d_act",   32)
        d_cycle = config.get("d_cycle", 32)
        dropout = config.get("dropout", 0.1)
        n_act   = config.get("n_activity_classes", 14)
        n_cop   = config.get("n_copresence", 9)
        n_slots = config.get("n_slots", 48)
        n_aux   = config.get("n_aux", N_AUX)
        d_cond  = config["d_cond"]

        self.d_model = d_model
        self.n_slots = n_slots
        self.n_act   = n_act
        self.n_cop   = n_cop
        self.n_aux   = n_aux

        # ── Encoder: source-diary slot embedding (act + width-11 aux) ────
        self.act_embedding = nn.Embedding(n_act, d_act)
        self.slot_linear   = nn.Linear(d_act + n_aux, d_model)   # [Leg-2] aux width = 11

        # ── CLS token: cycle + demographic conditioning ──────────────────
        self.cycle_embedding = nn.Embedding(4, d_cycle)
        self.cls_mlp = nn.Sequential(
            nn.Linear(d_cond + d_cycle, 256),
            nn.GELU(),
            nn.Linear(256, d_model),
        )

        # ── Arm 1: BOS token, sinusoidal PE, activity-only slot proj ────
        self.bos_token      = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)
        self.arm1_slot_proj = nn.Linear(d_act, d_model)  # activity-only, no aux
        self.register_buffer("enc_pos_enc", sinusoidal_pos_enc(n_slots + 1, d_model))
        self.register_buffer("dec_pos_enc", sinusoidal_pos_enc(n_slots,     d_model))

        # ── Trunk: 6-layer TransformerEncoder ───────────────────────────
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_ff,
            dropout=dropout, activation="gelu", batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            enc_layer, num_layers=N_enc, norm=nn.LayerNorm(d_model)
        )

        # ── Arm 1: CrossAttnDecoder ──────────────────────────────────────
        self.arm1_decoder = CrossAttnDecoder(
            d_model=d_model, n_heads=n_heads, n_layers=N_dec,
            d_ff=d_ff, d_cond=d_cond, d_cycle=d_cycle, dropout=dropout,
        )
        self.act_head = nn.Linear(d_model, n_act)

        # ── Arm 2: per-slot fusion projection (J3 arm2_act_proj) ─────────
        self.arm2_act_proj = nn.Linear(n_act, d_model)
        d_arm2_in = d_model + d_model + d_cond + d_cycle + 3
        self.arm2_proj = nn.Linear(d_arm2_in, d_model)

        # ── Arm 2 heads: Tanh-gated (J3). Each Linear->Tanh->Linear. ─────
        self.home_head = nn.Sequential(
            nn.Linear(d_model, d_model), nn.Tanh(), nn.Linear(d_model, 1)
        )
        # [Leg-2 NEW] AT_WORK head mirrors home_head exactly.
        self.work_head = nn.Sequential(
            nn.Linear(d_model, d_model), nn.Tanh(), nn.Linear(d_model, 1)
        )
        self.cop_head = nn.Sequential(
            nn.Linear(d_model, d_model), nn.Tanh(), nn.Linear(d_model, n_cop)
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

    # ── Encoder ─────────────────────────────────────────────────────────────

    def _encode(self, act_seq, aux_seq, cond_vec, cycle_idx):
        """Encode observed source diary. Returns memory (B, 49, d_model)."""
        act_emb  = self.act_embedding(act_seq)
        slot_emb = self.slot_linear(torch.cat([act_emb, aux_seq], dim=-1))
        slot_emb = slot_emb + self.enc_pos_enc[:, 1:, :]

        cycle_emb = self.cycle_embedding(cycle_idx)
        cls_tok   = self.cls_mlp(torch.cat([cond_vec, cycle_emb], dim=-1)).unsqueeze(1)
        cls_tok   = cls_tok + self.enc_pos_enc[:, :1, :]

        return self.encoder(torch.cat([cls_tok, slot_emb], dim=1))

    # ── Arm 1 helpers ────────────────────────────────────────────────────────

    def _build_arm1_cond(self, cond_vec, cycle_idx, tgt_strata):
        cycle_emb = self.cycle_embedding(cycle_idx)
        strata_oh = F.one_hot((tgt_strata - 1).clamp(0, 2), num_classes=3).float()
        return cond_vec, cycle_emb, strata_oh

    def _arm1_decode_tf(self, dec_act_seq, tgt_strata, memory, cond_vec, cycle_idx):
        """Teacher-forced Arm-1 decode (activity-only inputs). Returns (B,48,n_act)."""
        B, T = dec_act_seq.shape
        act_emb = self.act_embedding(dec_act_seq)
        tgt_emb = self.arm1_slot_proj(act_emb)

        bos = self.bos_token.expand(B, 1, -1)
        dec_input = torch.cat([bos, tgt_emb[:, :-1, :]], dim=1)
        dec_input = dec_input + self.dec_pos_enc[:, :T, :]

        cond_vec_d, cycle_emb_d, strata_oh_d = self._build_arm1_cond(cond_vec, cycle_idx, tgt_strata)
        causal_mask = nn.Transformer.generate_square_subsequent_mask(T, device=dec_input.device)
        dec_out = self.arm1_decoder(dec_input, memory, cond_vec_d, cycle_emb_d, strata_oh_d, causal_mask)
        return self.act_head(dec_out)

    def _arm1_generate(self, memory, cond_vec, cycle_idx, tgt_strata, temperature: float = 0.0):
        """AR activity generation (no aux feedback). Returns (B,48) int64 0-indexed."""
        B = memory.shape[0]
        device = memory.device
        cond_vec_d, cycle_emb_d, strata_oh_d = self._build_arm1_cond(cond_vec, cycle_idx, tgt_strata)

        bos_tok = self.bos_token.expand(B, 1, -1) + self.dec_pos_enc[:, :1, :]
        dec_tokens = [bos_tok]
        act_tokens = []

        for t in range(self.n_slots):
            dec_seq = torch.cat(dec_tokens, dim=1)
            causal_mask = nn.Transformer.generate_square_subsequent_mask(dec_seq.shape[1], device=device)
            dec_out = self.arm1_decoder(dec_seq, memory, cond_vec_d, cycle_emb_d, strata_oh_d, causal_mask)
            out_t   = dec_out[:, -1, :]
            logits  = self.act_head(out_t)
            if temperature and temperature > 0:
                probs   = F.softmax(logits / temperature, dim=-1)
                act_tok = torch.multinomial(probs, 1).squeeze(-1)
            else:
                act_tok = logits.argmax(-1)
            act_tokens.append(act_tok)

            if t < self.n_slots - 1:
                act_emb_t = self.act_embedding(act_tok)
                slot_next = (self.arm1_slot_proj(act_emb_t).unsqueeze(1)
                             + self.dec_pos_enc[:, t + 1:t + 2, :])
                dec_tokens.append(slot_next)

        return torch.stack(act_tokens, dim=1)

    # ── Arm 2 fusion ───────────────────────────────────────────────────────

    def _arm2_fuse(self, memory, act_probs, cond_vec, cycle_idx, tgt_strata):
        """Per-slot NAT fusion. act_probs already projected by arm2_act_proj. (B,48,d_model)."""
        T         = self.n_slots
        slots_mem = memory[:, 1:, :]                                         # (B,48,d_model)

        cycle_emb = self.cycle_embedding(cycle_idx)
        strata_oh = F.one_hot((tgt_strata - 1).clamp(0, 2), num_classes=3).float()

        cond_b   = cond_vec.unsqueeze(1).expand(-1, T, -1)
        cycle_b  = cycle_emb.unsqueeze(1).expand(-1, T, -1)
        strata_b = strata_oh.unsqueeze(1).expand(-1, T, -1)

        act_emb = self.arm2_act_proj(act_probs)                             # (B,48,d_model)

        fused = torch.cat([slots_mem, act_emb, cond_b, cycle_b, strata_b], dim=-1)
        return self.arm2_proj(fused)

    # ── Forward (teacher-forcing, training) ──────────────────────────────────

    def forward(self, batch: dict) -> dict:
        """Full forward with teacher forcing. Arm 1 -> detach -> Arm 2."""
        memory = self._encode(
            batch["act_seq"], batch["aux_seq"],
            batch["cond_vec"], batch["cycle_idx"],
        )
        act_logits = self._arm1_decode_tf(
            batch["dec_act_seq"], batch["tgt_strata"],
            memory, batch["cond_vec"], batch["cycle_idx"],
        )  # (B, 48, n_act)

        # DETACH BARRIER — preserved exactly.
        act_probs = F.softmax(act_logits.detach(), dim=-1)
        arm2_feat = self._arm2_fuse(
            memory, act_probs, batch["cond_vec"],
            batch["cycle_idx"], batch["tgt_strata"],
        )

        return {
            "act_logits":  act_logits,
            "home_logits": self.home_head(arm2_feat).squeeze(-1),  # (B, 48)
            "work_logits": self.work_head(arm2_feat).squeeze(-1),  # (B, 48) [Leg-2 NEW]
            "cop_logits":  self.cop_head(arm2_feat),               # (B, 48, 9)
        }

    # ── Inference (AR Arm 1 -> NAT Arm 2) ────────────────────────────────────

    @torch.no_grad()
    def generate(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata,
                 temperature: float = 0.8,
                 home_threshold: float = 0.5,
                 work_threshold: float = 0.5,
                 apply_safety: bool = True):
        """
        AR activity (Arm 1) then NAT binary heads (Arm 2).

        Returns:
            gen_act       (B,48) int64   — 0-indexed generated activity
            gen_home      (B,48) float32 — binary AT_HOME
            gen_work      (B,48) float32 — binary AT_WORK [Leg-2 NEW]
            gen_cop       (B,48,9) float32 — binary co-presence (AR-feedback style)
            gen_cop_probs (B,48,9) float32 — raw sigmoid co-presence
        apply_safety: Spouse cop_prob *= (home_pred > 0.5) clip when not home.
        """
        memory = self._encode(act_seq, aux_seq, cond_vec, cycle_idx)
        act_tokens = self._arm1_generate(memory, cond_vec, cycle_idx, tgt_strata,
                                         temperature=temperature)

        act_probs = F.one_hot(act_tokens, num_classes=self.n_act).float()  # hard at infer
        arm2_feat = self._arm2_fuse(memory, act_probs, cond_vec, cycle_idx, tgt_strata)

        gen_home = (torch.sigmoid(self.home_head(arm2_feat).squeeze(-1)) > home_threshold).float()
        gen_work = (torch.sigmoid(self.work_head(arm2_feat).squeeze(-1)) > work_threshold).float()
        cop_probs = torch.sigmoid(self.cop_head(arm2_feat))                 # (B,48,9)
        cop_bin   = (cop_probs > 0.5).float()

        if apply_safety:
            cop_probs = cop_probs.clone()
            cop_probs[:, :, self.SPOUSE_IDX] *= gen_home

        return act_tokens, gen_home, gen_work, cop_bin, cop_probs
