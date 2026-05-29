"""
04B_model_B2.py — G4_NAT_COP Hybrid: G4 AR decoder (activity + AT_HOME) + NAT branch (COP).

Phase 8B-2 architecture. Combines:
  - G4's CrossAttn AR decoder for activity + AT_HOME (home stays in AR where G4 excels)
  - J3-style NAT parallel branch for copresence only (eliminates 7-channel cascading)

Key differences from G4:
  - AR feedback is act_emb + home_tok (d_act + 1), NOT act_emb + home_tok + cop_tok (d_act + 10)
  - cop_head removed from AR decoder, moved to NAT branch
  - NAT branch: encoder_slots || act_proj || home_proj || cond || cycle || strata → cop_head

Key differences from J3:
  - AR decoder predicts activity AND home (J3 AR predicts activity only)
  - NAT branch predicts COP only (J3 NAT predicts home + COP)
  - Home predictions fed into NAT as additional input for COP conditioning
"""

import math
import os
import torch
import torch.nn as nn
import torch.nn.functional as F


def sinusoidal_pos_enc(max_len: int, d_model: int) -> torch.Tensor:
    pe = torch.zeros(1, max_len, d_model)
    pos = torch.arange(max_len, dtype=torch.float).unsqueeze(1)
    div = torch.exp(
        torch.arange(0, d_model, 2, dtype=torch.float) * (-math.log(10000.0) / d_model)
    )
    pe[0, :, 0::2] = torch.sin(pos * div)
    pe[0, :, 1::2] = torch.cos(pos * div)
    return pe


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
    def __init__(self, d_model, n_heads, n_layers, d_ff, d_cond, d_cycle):
        super().__init__()
        self.proj_demo   = nn.Linear(d_cond,  d_model)
        self.proj_cycle  = nn.Linear(d_cycle, d_model)
        self.proj_strata = nn.Linear(3,       d_model)
        self.layers = nn.ModuleList([
            CondCrossAttnDecoderLayer(d_model, n_heads, d_ff) for _ in range(n_layers)
        ])
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x, memory, cond_vec, cycle_emb, strata_oh, tgt_mask):
        cond_tokens = torch.stack([
            self.proj_demo(cond_vec),
            self.proj_cycle(cycle_emb),
            self.proj_strata(strata_oh),
        ], dim=1)
        for layer in self.layers:
            x = layer(x, memory, cond_tokens, tgt_mask)
        return self.norm(x)


class G4NATCopHybrid(nn.Module):
    """
    Phase 8B-2: G4 encoder + AR decoder (activity + AT_HOME) + NAT branch (COP).

    Training: AR decoder with teacher forcing for activity + home.
              NAT branch gets detached act_probs + home_probs → predicts COP in parallel.
    Inference: AR loop generates activity + home (no COP feedback).
               NAT branch predicts all COP slots in one shot.
    """

    SPOUSE_IDX = 1

    def __init__(self, config: dict):
        super().__init__()

        d_model = config["d_model"]
        n_heads = config["n_heads"]
        d_ff    = config["d_ff"]
        N_enc   = config["N_enc"]
        N_dec   = config["N_dec"]
        d_act   = config.get("d_act",   32)
        d_cycle = config.get("d_cycle", 32)
        dropout = config.get("dropout", 0.1)
        n_act   = config.get("n_activity_classes", 14)
        n_cop   = config.get("n_copresence", 9)
        n_slots = config.get("n_slots", 48)
        d_cond  = config["d_cond"]

        self.d_model = d_model
        self.n_slots = n_slots
        self.n_act   = n_act
        self.n_cop   = n_cop

        # ── Encoder slot embedding: act + AT_HOME + 9 COP (full context) ────
        self.act_embedding   = nn.Embedding(n_act, d_act)
        self.enc_slot_linear = nn.Linear(d_act + 1 + n_cop, d_model)

        # ── Decoder slot embedding: act + AT_HOME only (NO COP feedback) ────
        self.dec_slot_linear = nn.Linear(d_act + 1, d_model)

        # ── CLS token ────────────────────────────────────────────────────────
        self.cycle_embedding = nn.Embedding(4, d_cycle)
        self.cls_mlp = nn.Sequential(
            nn.Linear(d_cond + d_cycle, 256),
            nn.GELU(),
            nn.Linear(256, d_model),
        )

        # ── BOS token ────────────────────────────────────────────────────────
        self.bos_token = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)

        # ── Positional encodings ─────────────────────────────────────────────
        self.register_buffer("enc_pos_enc", sinusoidal_pos_enc(n_slots + 1, d_model))
        self.register_buffer("dec_pos_enc", sinusoidal_pos_enc(n_slots,     d_model))

        # ── Transformer encoder ──────────────────────────────────────────────
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_ff,
            dropout=dropout, activation="gelu", batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            enc_layer, num_layers=N_enc, norm=nn.LayerNorm(d_model)
        )

        # ── CrossAttn decoder (activity + AT_HOME) ───────────────────────────
        self.decoder = CrossAttnDecoder(
            d_model=d_model, n_heads=n_heads, n_layers=N_dec,
            d_ff=d_ff, d_cond=d_cond, d_cycle=d_cycle,
        )

        # ── AR heads (activity + home) ───────────────────────────────────────
        self.act_head  = nn.Linear(d_model, n_act)
        self.home_head = nn.Linear(d_model, 1)

        # ── NAT Arm-2: COP branch ───────────────────────────────────────────
        self.arm2_act_proj  = nn.Linear(n_act, d_model)
        self.arm2_home_proj = nn.Linear(1, d_model)
        d_arm2_in = d_model + d_model + d_model + d_cond + d_cycle + 3
        self.arm2_proj = nn.Linear(d_arm2_in, d_model)
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

    # ── Encoder ──────────────────────────────────────────────────────────────

    def encode(self, act_seq, aux_seq, cond_vec, cycle_idx):
        act_emb  = self.act_embedding(act_seq)
        slot_emb = self.enc_slot_linear(torch.cat([act_emb, aux_seq], dim=-1))
        slot_emb = slot_emb + self.enc_pos_enc[:, 1:, :]

        cycle_emb = self.cycle_embedding(cycle_idx)
        cls_tok   = self.cls_mlp(
            torch.cat([cond_vec, cycle_emb], dim=-1)
        ).unsqueeze(1)
        cls_tok   = cls_tok + self.enc_pos_enc[:, :1, :]

        return self.encoder(torch.cat([cls_tok, slot_emb], dim=1))

    # ── Decoder conditioning ─────────────────────────────────────────────────

    def _build_dec_cond(self, cond_vec, cycle_idx, tgt_strata):
        cycle_emb = self.cycle_embedding(cycle_idx)
        strata_oh = F.one_hot((tgt_strata - 1).clamp(0, 2), num_classes=3).float()
        return cond_vec, cycle_emb, strata_oh

    # ── AR decode (teacher-forcing): activity + AT_HOME ──────────────────────

    def decode(self, dec_act_seq, dec_home_seq, tgt_strata, memory, cond_vec, cycle_idx):
        """
        Teacher-forcing decode for activity + AT_HOME.

        dec_act_seq  : (B, 48) int64 — target activity
        dec_home_seq : (B, 48) float — target AT_HOME binary
        Returns: act_logits (B,48,14), home_logits (B,48)
        """
        B, T = dec_act_seq.shape

        act_emb = self.act_embedding(dec_act_seq)
        dec_input_raw = torch.cat([act_emb, dec_home_seq.unsqueeze(-1)], dim=-1)
        tgt_emb = self.dec_slot_linear(dec_input_raw)

        bos = self.bos_token.expand(B, 1, -1)
        dec_input = torch.cat([bos, tgt_emb[:, :-1, :]], dim=1)
        dec_input = dec_input + self.dec_pos_enc[:, :T, :]

        cond_vec_d, cycle_emb_d, strata_oh_d = self._build_dec_cond(cond_vec, cycle_idx, tgt_strata)

        causal_mask = nn.Transformer.generate_square_subsequent_mask(T, device=dec_input.device)
        dec_output = self.decoder(dec_input, memory, cond_vec_d, cycle_emb_d, strata_oh_d, causal_mask)

        return (
            self.act_head(dec_output),
            self.home_head(dec_output).squeeze(-1),
        )

    # ── NAT Arm-2: COP fusion ───────────────────────────────────────────────

    def _arm2_fuse(self, memory, act_probs, home_probs, cond_vec, cycle_idx, tgt_strata):
        """
        Per-slot NAT fusion for COP prediction.

        memory:     (B, 49, d_model)
        act_probs:  (B, 48, n_act) — detached soft probs (train) or one-hot (infer)
        home_probs: (B, 48) — detached sigmoid output (train) or binary (infer)
        Returns:    (B, 48, d_model)
        """
        T = self.n_slots
        slots_mem = memory[:, 1:, :]

        cycle_emb = self.cycle_embedding(cycle_idx)
        strata_oh = F.one_hot((tgt_strata - 1).clamp(0, 2), num_classes=3).float()

        cond_b   = cond_vec.unsqueeze(1).expand(-1, T, -1)
        cycle_b  = cycle_emb.unsqueeze(1).expand(-1, T, -1)
        strata_b = strata_oh.unsqueeze(1).expand(-1, T, -1)

        act_emb  = self.arm2_act_proj(act_probs)
        home_emb = self.arm2_home_proj(home_probs.unsqueeze(-1))

        fused = torch.cat([slots_mem, act_emb, home_emb, cond_b, cycle_b, strata_b], dim=-1)
        return self.arm2_proj(fused)

    # ── Forward (teacher-forcing, training) ──────────────────────────────────

    def forward(self, batch: dict) -> dict:
        memory = self.encode(
            batch["act_seq"], batch["aux_seq"],
            batch["cond_vec"], batch["cycle_idx"],
        )

        dec_home_seq = batch["dec_aux_seq"][:, :, 0]

        act_logits, home_logits = self.decode(
            batch["dec_act_seq"], dec_home_seq,
            batch["tgt_strata"], memory,
            batch["cond_vec"], batch["cycle_idx"],
        )

        act_probs  = F.softmax(act_logits.detach(), dim=-1)
        home_probs = torch.sigmoid(home_logits.detach())

        arm2_feat  = self._arm2_fuse(
            memory, act_probs, home_probs,
            batch["cond_vec"], batch["cycle_idx"], batch["tgt_strata"],
        )
        cop_logits = self.cop_head(arm2_feat)

        return {
            "act_logits":  act_logits,
            "home_logits": home_logits,
            "cop_logits":  cop_logits,
            "aux_logits":  None,
        }

    # ── Inference ────────────────────────────────────────────────────────────

    @torch.no_grad()
    def infer(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata,
              apply_safety: bool = True):
        """
        AR loop for activity + AT_HOME, then NAT for COP.
        Returns (gen_act [B,48] int64, gen_home [B,48] float, cop_prob [B,48,9] float).
        """
        device = act_seq.device
        B = act_seq.shape[0]

        memory = self.encode(act_seq, aux_seq, cond_vec, cycle_idx)
        cond_vec_g, cycle_emb_g, strata_oh_g = self._build_dec_cond(cond_vec, cycle_idx, tgt_strata)

        gen_acts  = []
        gen_homes = []

        bos_tok = self.bos_token.expand(B, 1, -1) + self.dec_pos_enc[:, :1, :]
        dec_tokens = [bos_tok]

        for t in range(self.n_slots):
            dec_seq = torch.cat(dec_tokens, dim=1)
            causal_mask = nn.Transformer.generate_square_subsequent_mask(
                dec_seq.shape[1], device=device
            )
            dec_out = self.decoder(
                dec_seq, memory, cond_vec_g, cycle_emb_g, strata_oh_g, causal_mask
            )
            out_t = dec_out[:, -1, :]

            act_logits = self.act_head(out_t)
            act_tok = act_logits.argmax(dim=-1)

            home_tok = (torch.sigmoid(self.home_head(out_t).squeeze(-1)) > 0.5).float()

            gen_acts.append(act_tok)
            gen_homes.append(home_tok)

            if t < self.n_slots - 1:
                act_emb_t = self.act_embedding(act_tok)
                slot_in = torch.cat([act_emb_t, home_tok.unsqueeze(-1)], dim=-1)
                slot_out = self.dec_slot_linear(slot_in).unsqueeze(1)
                slot_out = slot_out + self.dec_pos_enc[:, t + 1:t + 2, :]
                dec_tokens.append(slot_out)

        gen_act  = torch.stack(gen_acts, dim=1)
        gen_home = torch.stack(gen_homes, dim=1)

        act_probs = F.one_hot(gen_act, num_classes=self.n_act).float()
        arm2_feat = self._arm2_fuse(memory, act_probs, gen_home, cond_vec, cycle_idx, tgt_strata)
        cop_prob  = torch.sigmoid(self.cop_head(arm2_feat))

        if apply_safety:
            cop_prob = cop_prob.clone()
            cop_prob[:, :, self.SPOUSE_IDX] *= gen_home

        return gen_act, gen_home, cop_prob
