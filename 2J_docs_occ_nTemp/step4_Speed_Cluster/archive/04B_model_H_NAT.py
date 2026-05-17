"""
04B_model.py — Conditional Transformer Encoder-Decoder architecture for Step 4.

Defines the ConditionalTransformer class that takes an observed 48-slot diary
(one DDAY_STRATA) and generates synthetic diaries for the other two strata,
conditioned on the respondent's demographic profile.

IMPORTANT: Because this filename begins with a digit, it cannot be imported
with a plain `import` statement.  Other scripts must use importlib:

    import importlib, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    model_mod = importlib.import_module("04B_model")
    ConditionalTransformer = model_mod.ConditionalTransformer

This file is imported, NOT run directly.
"""

import math
import os
import torch
import torch.nn as nn
import torch.nn.functional as F

H_TIME_PE = int(os.environ.get("H_TIME_PE", "0"))


# ── Positional encoding ──────────────────────────────────────────────────────

def sinusoidal_pos_enc(max_len: int, d_model: int) -> torch.Tensor:
    """Standard sinusoidal positional encoding.

    Returns shape (1, max_len, d_model) — broadcast-ready over batch.
    All diaries start at 4:00 AM, so position encodes time-of-day implicitly.
    """
    pe = torch.zeros(1, max_len, d_model)
    pos = torch.arange(max_len, dtype=torch.float).unsqueeze(1)
    div = torch.exp(
        torch.arange(0, d_model, 2, dtype=torch.float) * (-math.log(10000.0) / d_model)
    )
    pe[0, :, 0::2] = torch.sin(pos * div)
    pe[0, :, 1::2] = torch.cos(pos * div)
    return pe


# ── Default hyperparameter config (HPC production settings) ─────────────────

DEFAULT_CONFIG = {
    "d_model":             256,
    "n_heads":             8,
    "d_ff":                1024,
    "N_enc":               6,
    "N_dec":               6,
    "d_act":               32,    # activity category embedding dim
    "d_cycle":             32,    # CYCLE_YEAR learned embedding dim
    "dropout":             0.1,
    "n_activity_classes":  14,
    "n_copresence":        9,
    "n_slots":             48,
    "d_cond":              None,  # set from step4_feature_config.json at runtime
}

# Local-test override: smaller model for CPU speed
TEST_CONFIG = {
    "d_model":             64,
    "n_heads":             4,
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


# ── Cross-attention conditioning decoder (G3) ────────────────────────────────

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
        ], dim=1)                                    # (B, 3, d_model)
        layer0_hidden = None
        for i, layer in enumerate(self.layers):
            x = layer(x, memory, cond_tokens, tgt_mask)
            if i == 0:
                layer0_hidden = x
        return self.norm(x), layer0_hidden


# ── Model ────────────────────────────────────────────────────────────────────

class ConditionalTransformer(nn.Module):
    """
    Conditional Transformer Encoder-Decoder for diary augmentation.

    Encoder processes the observed 48-slot diary (with demographic CLS token).
    Decoder generates the target-stratum diary via cross-attention over the
    encoder output.  Three output heads predict:
      - activity (14 categories, cross-entropy)
      - AT_HOME (binary, BCE)
      - co-presence (9 binary columns, BCE with availability mask)

    Args:
        config: dict with keys from DEFAULT_CONFIG.  d_cond must be set.
    """

    def __init__(self, config: dict):
        super().__init__()

        d_model  = config["d_model"]
        n_heads  = config["n_heads"]
        d_ff     = config["d_ff"]
        N_enc    = config["N_enc"]
        N_dec    = config["N_dec"]
        d_act    = config.get("d_act",   32)
        d_cycle  = config.get("d_cycle", 32)
        dropout  = config.get("dropout", 0.1)
        n_act    = config.get("n_activity_classes", 14)
        n_cop    = config.get("n_copresence", 9)
        n_slots  = config.get("n_slots", 48)
        d_cond   = config["d_cond"]   # pre-computed conditioning vector dim

        self.d_model  = d_model
        self.n_slots  = n_slots
        self.n_act    = n_act
        self.n_cop    = n_cop

        # ── Shared slot embedding (encoder & decoder) ────────────────────
        # occACT → Embedding(14, d_act), then concat with [AT_HOME + 9 co-pres]
        self.act_embedding = nn.Embedding(n_act, d_act)
        self.slot_linear   = nn.Linear(d_act + 1 + n_cop, d_model)  # +1 for AT_HOME

        # ── Encoder: CLS token (demographic conditioning) ────────────────
        # CYCLE_YEAR → learned embedding, concatenated with pre-computed cond_vec
        self.cycle_embedding = nn.Embedding(4, d_cycle)
        # MLP: (d_cond + d_cycle) → 256 → d_model
        self.cls_mlp = nn.Sequential(
            nn.Linear(d_cond + d_cycle, 256),
            nn.GELU(),
            nn.Linear(256, d_model),
        )

        # ── Decoder: BOS token ───────────────────────────────────────────
        # Learnable BOS token (start-of-sequence for decoder)
        self.bos_token = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)

        # ── Sinusoidal positional encodings ──────────────────────────────
        # Encoder: 49 positions (1 CLS + 48 slots)
        # Decoder: 48 positions (BOS=pos 0 + 47 shifted GT slots)
        self.register_buffer("enc_pos_enc", sinusoidal_pos_enc(n_slots + 1, d_model))
        self.register_buffer("dec_pos_enc", sinusoidal_pos_enc(n_slots,     d_model))

        if H_TIME_PE:
            self.learnable_pe = nn.Parameter(torch.randn(1, n_slots, d_model) * 0.02)
            t_idx = torch.arange(n_slots, dtype=torch.float)
            cyc = torch.stack([
                torch.sin(2 * math.pi * t_idx / n_slots),
                torch.cos(2 * math.pi * t_idx / n_slots),
            ], dim=-1).unsqueeze(0)  # (1, 48, 2)
            self.register_buffer("cyclical_time", cyc)
            self.time_proj = nn.Linear(d_model + 2, d_model)

        # ── Transformer encoder ──────────────────────────────────────────
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_ff,
            dropout=dropout, activation="gelu", batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            enc_layer, num_layers=N_enc, norm=nn.LayerNorm(d_model)
        )

        # ── Transformer decoder (cross-attention conditioning, G3) ───────
        # CrossAttnDecoder: self-attn → cross-attn(memory) → cross-attn(3
        # conditioning tokens: demo, cycle, strata) → FFN, per layer.
        self.decoder = CrossAttnDecoder(
            d_model=d_model, n_heads=n_heads, n_layers=N_dec,
            d_ff=d_ff, d_cond=d_cond, d_cycle=d_cycle,
        )

        # ── Output heads ─────────────────────────────────────────────────
        # H_TANH_HEADS=1: wrap home/cop heads with Tanh pre-activation (H_Tanh trial).
        # H_TANH_HEADS=0 (default): plain Linear — identical to G4.
        _h_tanh = os.environ.get("H_TANH_HEADS", "0") == "1"
        self.act_head  = nn.Linear(d_model, n_act)  # → 14 activity logits
        self.home_head = (nn.Sequential(nn.Tanh(), nn.Linear(d_model, 1))
                          if _h_tanh else nn.Linear(d_model, 1))
        self.cop_head  = (nn.Sequential(nn.Tanh(), nn.Linear(d_model, n_cop))
                          if _h_tanh else nn.Linear(d_model, n_cop))

        # Optional auxiliary head: predicts target DDAY_STRATA (3-way CE) from
        # decoder layer-0 hidden mean-pool. Gated by config["aux_stratum_head"].
        if config.get("aux_stratum_head", False):
            self.aux_strata_head = nn.Sequential(
                nn.Linear(d_model, 64),
                nn.GELU(),
                nn.Linear(64, 3),
            )
        else:
            self.aux_strata_head = None

        self._init_weights()

    def _init_weights(self):
        """Xavier init for linear layers; normal for embeddings."""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.02)

    # ── Slot embedding (shared) ──────────────────────────────────────────────

    def _embed_slots(self, act_seq: torch.Tensor, aux_seq: torch.Tensor) -> torch.Tensor:
        """
        Embed 48 multivariate slot tokens.

        act_seq : (B, T)      — int64, 0-indexed activity categories
        aux_seq : (B, T, 10)  — float32, [AT_HOME | 9 co-presence]
        Returns : (B, T, d_model)
        """
        act_emb    = self.act_embedding(act_seq)          # (B, T, d_act)
        slot_input = torch.cat([act_emb, aux_seq], dim=-1)  # (B, T, d_act+10)
        return self.slot_linear(slot_input)                 # (B, T, d_model)

    # ── Encoder ─────────────────────────────────────────────────────────────

    def encode(self, act_seq, aux_seq, cond_vec, cycle_idx) -> torch.Tensor:
        """
        Encode observed diary + demographic CLS token.

        Returns memory: (B, 49, d_model) — 1 CLS + 48 slot states.
        """
        B = act_seq.shape[0]

        # Slot embeddings with positional encoding at positions 1..48
        slot_emb = self._embed_slots(act_seq, aux_seq)         # (B, 48, d_model)
        slot_emb = slot_emb + self.enc_pos_enc[:, 1:, :]

        # CLS token: demographics + cycle year embedding, projected to d_model
        cycle_emb  = self.cycle_embedding(cycle_idx)            # (B, d_cycle)
        cls_input  = torch.cat([cond_vec, cycle_emb], dim=-1)   # (B, d_cond+d_cycle)
        cls_tok    = self.cls_mlp(cls_input).unsqueeze(1)        # (B, 1, d_model)
        cls_tok    = cls_tok + self.enc_pos_enc[:, :1, :]        # position 0

        enc_input = torch.cat([cls_tok, slot_emb], dim=1)       # (B, 49, d_model)
        return self.encoder(enc_input)                           # (B, 49, d_model)

    # ── Decoder (teacher-forcing mode) ──────────────────────────────────────

    def _build_dec_cond(self, cond_vec, cycle_idx, tgt_strata):
        """Returns (cond_vec, cycle_emb, strata_oh) for CrossAttnDecoder."""
        cycle_emb = self.cycle_embedding(cycle_idx)
        strata_oh = F.one_hot((tgt_strata - 1).clamp(0, 2), num_classes=3).float()
        return cond_vec, cycle_emb, strata_oh

    def decode(self, dec_act_seq, dec_aux_seq, tgt_strata, memory,
               cond_vec, cycle_idx):
        """
        Teacher-forcing decode: predicts target slots given ground-truth shifted input.

        dec_act_seq : (B, 48) — int64, target activity sequence
        dec_aux_seq : (B, 48, 10) — target [AT_HOME | co-pres]
        tgt_strata  : (B,) — int64, target DDAY_STRATA (1,2,3)
        memory      : (B, 49, d_model) — encoder output
        cond_vec    : (B, d_cond)
        cycle_idx   : (B,) — int64

        Returns act_logits (B,48,14), home_logits (B,48), cop_logits (B,48,9)
        """
        B, T = dec_act_seq.shape

        # Embed target slots
        tgt_emb = self._embed_slots(dec_act_seq, dec_aux_seq)   # (B, T, d_model)

        # Shift right: [BOS, slot_0, ..., slot_{T-2}]
        bos       = self.bos_token.expand(B, 1, -1)
        dec_input = torch.cat([bos, tgt_emb[:, :-1, :]], dim=1) # (B, T, d_model)

        # Positional encoding (positions 0..T-1)
        if H_TIME_PE:
            cyc = self.cyclical_time.expand(B, -1, -1)[:, :T, :]
            dec_input = self.time_proj(torch.cat([dec_input, cyc], dim=-1))
            dec_input = dec_input + self.learnable_pe[:, :T, :]
        else:
            dec_input = dec_input + self.dec_pos_enc[:, :T, :]

        # Cross-attention conditioning tensors
        cond_vec_d, cycle_emb_d, strata_oh_d = self._build_dec_cond(cond_vec, cycle_idx, tgt_strata)

        # Causal mask: each position attends only to itself and earlier positions
        causal_mask = nn.Transformer.generate_square_subsequent_mask(
            T, device=dec_input.device
        )
        dec_output, layer0_hidden = self.decoder(
            dec_input, memory, cond_vec_d, cycle_emb_d, strata_oh_d, causal_mask
        )  # dec_output: (B, T, d_model); layer0_hidden: (B, T, d_model)

        aux_logits = None
        if self.aux_strata_head is not None and layer0_hidden is not None:
            aux_logits = self.aux_strata_head(layer0_hidden.mean(dim=1))  # (B, 3)

        return (
            self.act_head(dec_output),               # (B, T, 14)
            self.home_head(dec_output).squeeze(-1),  # (B, T)
            self.cop_head(dec_output),               # (B, T, 9)
            aux_logits,                              # (B, 3) or None
        )

    # ── Forward (teacher-forcing, called during training) ────────────────────

    def forward(self, batch: dict) -> dict:
        """
        Full forward pass with teacher forcing.

        Expects batch keys:
          act_seq, aux_seq, cond_vec, cycle_idx  — encoder (observed diary)
          dec_act_seq, dec_aux_seq               — decoder targets (neighbor)
          tgt_strata                              — target DDAY_STRATA (1,2,3)
        """
        memory = self.encode(
            batch["act_seq"], batch["aux_seq"],
            batch["cond_vec"], batch["cycle_idx"],
        )
        act_logits, home_logits, cop_logits, aux_logits = self.decode(
            batch["dec_act_seq"], batch["dec_aux_seq"],
            batch["tgt_strata"], memory,
            batch["cond_vec"], batch["cycle_idx"],
        )
        return {
            "act_logits":  act_logits,
            "home_logits": home_logits,
            "cop_logits":  cop_logits,
            "aux_logits":  aux_logits,
        }

    # ── Inference (autoregressive generation) ────────────────────────────────

    @torch.no_grad()
    def generate(
        self,
        act_seq:   torch.Tensor,
        aux_seq:   torch.Tensor,
        cond_vec:  torch.Tensor,
        cycle_idx: torch.Tensor,
        tgt_strata: torch.Tensor,
        temperature: float = 0.8,
        home_threshold: float = 0.5,
    ):
        """
        Autoregressive generation for one or more respondents.

        act_seq    : (B, 48) — observed diary (encoder input)
        aux_seq    : (B, 48, 10) — observed aux sequence (encoder input)
        cond_vec   : (B, d_cond)
        cycle_idx  : (B,)
        tgt_strata : (B,) — target DDAY_STRATA (1,2,3)
        temperature: >0 → multinomial sampling; 0 → argmax (deterministic)
        home_threshold: sigmoid cutoff for AT_HOME decision (default 0.5).
                        Raising it reduces AT_HOME=1 predictions; because
                        home_tok is fed back into the decoder's aux input at
                        the next step, the choice cascades through the diary.

        Returns:
            gen_act  (B, 48) int64 — 0-indexed generated activity
            gen_home (B, 48) float32 — binary AT_HOME
            gen_cop  (B, 48, 9) float32 — binary co-presence
        """
        device = act_seq.device
        B      = act_seq.shape[0]

        memory = self.encode(act_seq, aux_seq, cond_vec, cycle_idx)

        # Cross-attn conditioning tensors (fixed for all decoder steps)
        cond_vec_g, cycle_emb_g, strata_oh_g = self._build_dec_cond(cond_vec, cycle_idx, tgt_strata)

        gen_acts       = []
        gen_homes      = []
        gen_cops       = []
        gen_cop_probs  = []

        # Decoder sequence starts with the BOS token at position 0
        bos_tok = self.bos_token.expand(B, 1, self.d_model)
        if not H_TIME_PE:
            bos_tok = bos_tok + self.dec_pos_enc[:, :1, :]
        dec_tokens = [bos_tok]

        for t in range(self.n_slots):
            dec_seq = torch.cat(dec_tokens, dim=1)           # (B, t+1, d_model)
            if H_TIME_PE:
                _sz = dec_seq.size(1)
                cyc = self.cyclical_time.expand(B, -1, -1)[:, :_sz, :]
                dec_seq = self.time_proj(torch.cat([dec_seq, cyc], dim=-1))
                dec_seq = dec_seq + self.learnable_pe[:, :_sz, :]
            causal_mask = nn.Transformer.generate_square_subsequent_mask(
                dec_seq.shape[1], device=device
            )
            dec_out, _ = self.decoder(dec_seq, memory,
                                      cond_vec_g, cycle_emb_g, strata_oh_g, causal_mask)
            out_t = dec_out[:, -1, :]                             # (B, d_model)

            # Activity head
            act_logits = self.act_head(out_t)                     # (B, 14)
            if temperature > 0:
                act_probs = F.softmax(act_logits / temperature, dim=-1)
                act_tok   = torch.multinomial(act_probs, 1).squeeze(-1)  # (B,)
            else:
                act_tok = act_logits.argmax(dim=-1)

            # AT_HOME head
            home_tok = (torch.sigmoid(self.home_head(out_t).squeeze(-1)) > home_threshold).float()

            # Co-presence head — raw σ for output, binary for AR feedback
            cop_probs = torch.sigmoid(self.cop_head(out_t))        # (B, 9) float in [0,1]
            cop_tok   = (cop_probs > 0.5).float()                  # (B, 9) binary — matches training

            gen_acts.append(act_tok)
            gen_homes.append(home_tok)
            gen_cops.append(cop_tok)
            gen_cop_probs.append(cop_probs)

            # Embed the just-generated slot to feed as next decoder input
            # Position t+1 in the decoder sequence (BOS was position 0)
            if t < self.n_slots - 1:
                aux_t    = torch.cat([home_tok.unsqueeze(-1), cop_tok], dim=-1)  # (B, 10)
                act_emb  = self.act_embedding(act_tok)                            # (B, d_act)
                slot_in  = torch.cat([act_emb, aux_t], dim=-1)                   # (B, d_act+10)
                slot_out = self.slot_linear(slot_in).unsqueeze(1)                 # (B, 1, d_model)
                if not H_TIME_PE:
                    slot_out = slot_out + self.dec_pos_enc[:, t + 1:t + 2, :]
                dec_tokens.append(slot_out)

        return (
            torch.stack(gen_acts,      dim=1),      # (B, 48) int64
            torch.stack(gen_homes,     dim=1),      # (B, 48) float32
            torch.stack(gen_cops,      dim=1),      # (B, 48, 9) float32 binary
            torch.stack(gen_cop_probs, dim=1),      # (B, 48, 9) float32 raw σ
        )


# ── Encoder-only (H_NAT) ─────────────────────────────────────────────────────

class EncoderOnlyOccupancyModel(nn.Module):
    """
    Encoder-only (non-AR) architecture for diary generation (H_NAT trial).

    Encodes the observed 48-slot diary with a CLS conditioning token, then
    refines with a 2-layer bidirectional TransformerEncoder.  Parallel heads
    predict all 48 target slots simultaneously in a single forward pass.

    No AR loop, no BOS token, no causal mask.
    Post-hoc safety net (in infer()): Spouse channel zeroed when AT_HOME=0.
    H-Tier-1.6 AR-cascade diagnostic modes A/B/C do not apply to this model.
    """

    SPOUSE_IDX = 1  # index in 9-channel cop tensor

    def __init__(self, config: dict):
        super().__init__()

        d_model = config["d_model"]
        n_heads = config["n_heads"]
        d_ff    = config["d_ff"]
        N_enc   = config["N_enc"]
        N_ref   = config.get("refinement_layers", 2)
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

        # Slot embedding (same as ConditionalTransformer)
        self.act_embedding = nn.Embedding(n_act, d_act)
        self.slot_linear   = nn.Linear(d_act + 1 + n_cop, d_model)

        # CLS token for encoder (same as ConditionalTransformer)
        self.cycle_embedding = nn.Embedding(4, d_cycle)
        self.cls_mlp = nn.Sequential(
            nn.Linear(d_cond + d_cycle, 256),
            nn.GELU(),
            nn.Linear(256, d_model),
        )

        # Sinusoidal PE: 49 positions (1 CLS + 48 slots)
        self.register_buffer("enc_pos_enc", sinusoidal_pos_enc(n_slots + 1, d_model))

        # 6-layer transformer encoder (same depth as G4)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_ff,
            dropout=dropout, activation="gelu", batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            enc_layer, num_layers=N_enc, norm=nn.LayerNorm(d_model)
        )

        # Target stratum conditioning token prepended to refinement input
        self.strata_proj = nn.Linear(3, d_model)

        # 2-layer bidirectional refinement (no causal mask)
        ref_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_ff,
            dropout=dropout, activation="gelu", batch_first=True,
        )
        self.refinement = nn.TransformerEncoder(
            ref_layer, num_layers=N_ref, norm=nn.LayerNorm(d_model)
        )

        # Parallel output heads
        self.act_head  = nn.Linear(d_model, n_act)
        self.home_head = nn.Linear(d_model, 1)
        self.cop_head  = nn.Linear(d_model, n_cop)

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.02)

    def _embed_slots(self, act_seq, aux_seq):
        act_emb    = self.act_embedding(act_seq)
        slot_input = torch.cat([act_emb, aux_seq], dim=-1)
        return self.slot_linear(slot_input)

    def _encode(self, act_seq, aux_seq, cond_vec, cycle_idx):
        slot_emb  = self._embed_slots(act_seq, aux_seq)
        slot_emb  = slot_emb + self.enc_pos_enc[:, 1:, :]
        cycle_emb = self.cycle_embedding(cycle_idx)
        cls_tok   = self.cls_mlp(torch.cat([cond_vec, cycle_emb], dim=-1)).unsqueeze(1)
        cls_tok   = cls_tok + self.enc_pos_enc[:, :1, :]
        return self.encoder(torch.cat([cls_tok, slot_emb], dim=1))  # (B, 49, d_model)

    def _refine(self, memory, tgt_strata):
        """Prepend target-stratum token, run bidirectional refinement, return slot outputs."""
        slots      = memory[:, 1:, :]  # (B, 48, d_model)
        strata_oh  = F.one_hot((tgt_strata - 1).clamp(0, 2), num_classes=3).float()
        cond_token = self.strata_proj(strata_oh).unsqueeze(1)     # (B, 1, d_model)
        refined    = self.refinement(torch.cat([cond_token, slots], dim=1))  # (B, 49, d_model)
        return refined[:, 1:, :]  # (B, 48, d_model) — drop strata token

    def forward(self, batch: dict) -> dict:
        """Teacher-forcing forward for training. Encodes source diary, refines to target."""
        memory = self._encode(batch["act_seq"], batch["aux_seq"],
                              batch["cond_vec"], batch["cycle_idx"])
        slots  = self._refine(memory, batch["tgt_strata"])
        return {
            "act_logits":  self.act_head(slots),               # (B, 48, 14)
            "home_logits": self.home_head(slots).squeeze(-1),  # (B, 48)
            "cop_logits":  self.cop_head(slots),               # (B, 48, 9)
            "aux_logits":  None,
        }

    @torch.no_grad()
    def infer(self, act_seq, aux_seq, cond_vec, cycle_idx, tgt_strata,
              apply_safety: bool = True):
        """
        Single-pass inference. Returns (gen_act, gen_home, gen_cop_probs).
        Post-hoc safety net: Spouse probability zeroed when AT_HOME=0 (apply_safety=True).
        gen_act is 0-indexed (compatible with validate() and 04J metrics pipeline).
        """
        memory = self._encode(act_seq, aux_seq, cond_vec, cycle_idx)
        slots  = self._refine(memory, tgt_strata)

        gen_act  = self.act_head(slots).argmax(dim=-1)                     # (B, 48) 0-indexed
        gen_home = (torch.sigmoid(self.home_head(slots).squeeze(-1)) > 0.5).float()  # (B, 48)
        cop_prob = torch.sigmoid(self.cop_head(slots))                     # (B, 48, 9)

        if apply_safety:
            # Zero Spouse when person is not home (post-hoc logical constraint)
            cop_prob = cop_prob.clone()
            cop_prob[:, :, self.SPOUSE_IDX] = (
                cop_prob[:, :, self.SPOUSE_IDX] * gen_home
            )

        return gen_act, gen_home, cop_prob
